"""
Funciones comunes para editar las escenas de la obra de Sansón.

- Banner animado "ESCENA N · Título" (cinta azul con borde dorado, como la intro).
- Audio: limpieza de voz, nivelación final (-16 LUFS) y utilidades de medición.
- Video: limpieza del ruido de compresión, escalado a 1920x1080 y codificación.

Lo usan editar_escena1.py, editar_escena2.py, etc.
"""
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "intro_sanson", "assets", "fonts")

W, H = 1920, 1080
SR = 48000
TARGET_LUFS = -16.0
TARGET_TP = -1.5

NAVY_L = np.array([10, 28, 80], np.float32) / 255
NAVY_R = np.array([24, 58, 138], np.float32) / 255
GOLD_TOP = np.array([255, 236, 176], np.float32) / 255
GOLD_BOT = np.array([205, 148, 52], np.float32) / 255
CREAM = (250, 242, 222)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = max(0.0, min(1.0, x))
    return x ** 3


# ----------------------------------------------------------------------------
# Banner
# ----------------------------------------------------------------------------

def tracked_width(fnt, text, tracking):
    return sum(fnt.getlength(c) for c in text) + tracking * (len(text) - 1)


def draw_tracked(draw, x, y, text, fnt, tracking, fill):
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill)
        x += fnt.getlength(c) + tracking


class Banner:
    """Cinta pegada al borde izquierdo (side="left") o derecho (side="right")."""

    def __init__(self, line1, line2, dur, side="left"):
        self.dur, self.side = dur, side
        f1 = ImageFont.truetype(os.path.join(FONTS, "Cinzel-SemiBold.ttf"), 34)
        f2 = ImageFont.truetype(os.path.join(FONTS, "Cormorant-SemiBoldItalic.ttf"), 96)
        w1 = tracked_width(f1, line1, 9)
        w2 = f2.getlength(line2)
        self.tx = 112                                       # margen del texto desde el borde de pantalla
        self.ribbon_end = int(self.tx + max(w1, w2) + 70)   # donde termina la cinta (antes de la punta)
        self.tip = 46
        self.top, self.bot = 52, 222
        self.cw = self.ribbon_end + self.tip + 60
        self.ch = 280
        cw, ch, top, bot = self.cw, self.ch, self.top, self.bot
        mid = (top + bot) / 2
        poly = [(0, top), (self.ribbon_end, top), (self.ribbon_end + self.tip, mid),
                (self.ribbon_end, bot), (0, bot)]

        # Las formas se dibujan para el lado izquierdo y se reflejan si va a la derecha.
        m = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        mask = np.asarray(m).astype(np.float32) / 255

        xx = np.linspace(0, 1, cw, dtype=np.float32)[None, :, None]
        yy = np.linspace(0, 1, ch, dtype=np.float32)[:, None, None]
        fill = NAVY_L * (1 - xx) + NAVY_R * xx
        fill = fill + np.clip(1 - (yy - top / ch) / 0.25, 0, 1) * 0.10   # brillo superior
        fill = np.broadcast_to(fill, (ch, cw, 3)).astype(np.float32)

        g = Image.new("L", (cw, ch), 0)
        d = ImageDraw.Draw(g)
        d.line([(0, top), (self.ribbon_end, top), (self.ribbon_end + self.tip, mid),
                (self.ribbon_end, bot), (0, bot)], fill=255, width=4, joint="curve")
        inset = 9
        d.line([(0, top + inset), (self.ribbon_end - 4, top + inset),
                (self.ribbon_end + self.tip - inset - 6, mid),
                (self.ribbon_end - 4, bot - inset), (0, bot - inset)], fill=150, width=1, joint="curve")
        d.rectangle((70, top + 28, 75, bot - 28), fill=255)          # barra de acento + rombos
        d.polygon([(72.5, top + 14), (80, top + 22), (72.5, top + 30), (65, top + 22)], fill=255)
        d.polygon([(72.5, bot - 30), (80, bot - 22), (72.5, bot - 14), (65, bot - 22)], fill=255)
        gold_a = np.asarray(g).astype(np.float32)[..., None] / 255

        sh = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sh).polygon([(x, y + 10) for x, y in poly], fill=200)
        shadow = np.asarray(sh.filter(ImageFilter.GaussianBlur(16))).astype(np.float32) / 255

        if side == "right":
            mask, fill, gold_a, shadow = (np.ascontiguousarray(a[:, ::-1]) for a in (mask, fill, gold_a, shadow))
        self.mask, self.fill, self.gold_a, self.shadow = mask, fill, gold_a, shadow
        grad = GOLD_TOP * (1 - yy) + GOLD_BOT * yy
        self.gold = np.broadcast_to(grad, (ch, cw, 3)).astype(np.float32)

        def text_layer(draw_fn):
            a = Image.new("L", (cw, ch), 0)
            draw_fn(ImageDraw.Draw(a))
            arr = np.asarray(a).astype(np.float32) / 255
            shd = np.asarray(a.filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255
            return arr, np.roll(shd, 3, axis=0)

        if side == "right":   # texto alineado a la derecha, junto a la barra de acento
            x1, x2 = cw - self.tx - w1, cw - self.tx - w2 + 4
        else:
            x1, x2 = self.tx, self.tx - 4
        self.t1 = text_layer(lambda dd: draw_tracked(dd, x1, top + 20, line1, f1, 9, 255))
        self.t2 = text_layer(lambda dd: dd.text((x2, top + 52), line2, font=f2, fill=255))
        self.t1_col = self.gold
        self.t2_col = np.broadcast_to(np.array(CREAM, np.float32) / 255, (ch, cw, 3))

        xs = np.arange(cw, dtype=np.float32)[None, :]
        if side == "right":
            xs = cw - 1 - xs
        ys = np.arange(ch, dtype=np.float32)[:, None]
        self.dist = xs                                   # distancia al borde de pantalla
        self.diag = xs + (ys - ch / 2) * 0.45            # para el destello diagonal

    def frame(self, tau):
        """Imagen RGBA del banner en el instante tau (segundos desde que empieza)."""
        cw, ch, dur = self.cw, self.ch, self.dur
        e_in = ease_out(tau / 0.75)
        e_out = ease_in((tau - (dur - 0.7)) / 0.7)
        reveal = cw * e_in * (1 - e_out)
        cut = np.clip((reveal - self.dist[0]) / 6.0, 0, 1)[None, :]
        shift = (50 * (1 - e_in) + 50 * e_out) * (1 if self.side == "right" else -1)

        a_rib = self.mask * cut * 0.93
        a_gold = self.gold_a[..., 0] * cut
        a_sh = self.shadow * cut * 0.55

        rgb = np.zeros((ch, cw, 3), np.float32)
        alpha = np.zeros((ch, cw), np.float32)

        def over(col, a):
            nonlocal rgb, alpha
            rgb = rgb * (1 - a[..., None]) + col * a[..., None]
            alpha = alpha * (1 - a) + a

        over(np.zeros(3, np.float32), a_sh)
        over(self.fill, a_rib)
        over(self.gold, a_gold)

        t_out = 1 - ease_out((tau - (dur - 1.05)) / 0.35)
        for (arr, shd), col, delay in ((self.t1, self.t1_col, 0.45), (self.t2, self.t2_col, 0.6)):
            k = ease_out((tau - delay) / 0.6) * t_out
            if k <= 0:
                continue
            dy = int(round((1 - k) * 14))
            a = np.roll(arr, dy, axis=0) * k * cut[0][None, :]
            s = np.roll(shd, dy, axis=0) * k * 0.6 * cut[0][None, :]
            over(np.zeros(3, np.float32), s * self.mask)
            over(col, a)

        if 1.0 < tau < 2.0:   # destello dorado que cruza la cinta una vez
            pos = (tau - 1.0) / 1.0 * (cw + 300) - 150
            streak = np.exp(-((self.diag - pos) / 38.0) ** 2) * 0.35
            rgb += np.array([1.0, 0.9, 0.65], np.float32) * (streak * (a_rib + a_gold))[..., None]

        out = np.zeros((ch, cw, 4), np.float32)
        out[..., :3] = np.clip(rgb / np.maximum(alpha[..., None], 1e-4), 0, 1)
        out[..., 3] = np.clip(alpha, 0, 1)
        img = Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")
        if shift:
            moved = Image.new("RGBA", img.size, (0, 0, 0, 0))
            moved.paste(img, (int(round(shift)), 0))
            img = moved
        return img


def render_banner(folder, line1, line2, dur, fps, side="left"):
    """Guarda los cuadros del banner como b_0000.png… y devuelve el Banner."""
    b = Banner(line1, line2, dur, side)
    for i in range(int(round(dur * fps))):
        b.frame(i / fps).save(os.path.join(folder, f"b_{i:04d}.png"), compress_level=1)
    return b


# ----------------------------------------------------------------------------
# Audio
# ----------------------------------------------------------------------------

# Limpieza para voces de niños sin micrófono (se sube mucho su volumen).
def voice_chain(nr=10):
    return (f"afftdn=nr={nr}:nf=-60:tn=1,"                     # quita ruido de fondo
            "highpass=f=120,highpass=f=120,highpass=f=100,"     # sin pasos ni retumbe del escenario
            "equalizer=f=280:t=q:w=1.0:g=-2.5,"                 # menos voz "encajonada"
            "equalizer=f=3200:t=q:w=1.2:g=4,"                   # más claridad en las palabras
            "equalizer=f=7500:t=q:w=1.0:g=1.5")


KIDS_CHAIN = voice_chain(10)
GLUE = ("acompressor=threshold=-20dB:ratio=2.2:attack=12:release=250:knee=6,"
        "alimiter=limit=0.85:attack=3:release=60:level=false")


def loudness(path, start=None, end=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start is not None:
        cmd += ["-ss", str(start), "-to", str(end)]
    cmd += ["-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    vals = [ln.split()[1] for ln in err.splitlines() if ln.strip().startswith("I:")]
    return float(vals[-1])


def decode_audio(src, dst):
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_f32le", dst])
    return dst


def read_audio(path):
    raw = run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
              capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def write_audio(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                    "-c:a", "pcm_f32le", path], input=np.ascontiguousarray(x, np.float32).tobytes(), check=True)
    return path


def voice_peak(x, a=None, b=None):
    """Nivel de los picos de la voz: percentil 95 del nivel en ventanas de 50 ms (dB).
    En tramos cortos con pausas es más fiable que el promedio."""
    m = x.mean(1)
    if a is not None:
        m = m[int(a * SR):int(b * SR)]
    win = int(0.05 * SR)
    k = len(m) // win
    r = np.sqrt((m[:k * win].reshape(k, win) ** 2).mean(1)) + 1e-9
    return float(np.percentile(20 * np.log10(r), 95))


def boost_regions(src, tmp, regions, offset_db=0.0, pad=0.3, ramp=0.06, sfx=None, duck=None):
    """Sube los tramos donde los niños hablan sin micrófono y nivela toda la escena.

    regions: lista de (inicio, fin, ganancia máxima dB, reducción de ruido dB, nombre[, filtro]).
    El filtro opcional reemplaza a voice_chain(nr), por ejemplo para un tramo con música.
    Cada tramo se limpia (voice_chain), se lleva a los picos de voz del resto de la
    escena sin pasar su ganancia máxima, se le aplica una puerta de ruido suave y un
    compresor, y se mezcla con fundidos cortos.  Al final: canales equilibrados,
    corte de graves a 60 Hz, compresión suave para todo y -16 LUFS.
    sfx: efectos de sonido opcionales (arreglo (muestras, 2) a 48 kHz, alineado con
    el video) que se suman después del corte de graves y antes de la nivelación.
    duck: lista opcional de (inicio, fin, dB, fundido) para bajar el audio original
    en ese tramo (por ejemplo, para que se oigan los efectos).
    Devuelve la ruta del WAV final."""
    raw = decode_audio(src, os.path.join(tmp, "raw.wav"))
    x = read_audio(raw)
    n = len(x)
    t = np.arange(n) / SR
    ref = voice_peak(x)                     # picos de la escena (la parte con buen volumen)

    rms = np.sqrt((x ** 2).mean(0))         # equilibrio izquierda/derecha
    x *= (np.sqrt(rms[0] * rms[1]) / rms)[None, :]

    out = x.copy()
    for reg in regions:
        a, b, gmax, nr, name = reg[:5]
        chain = reg[5] if len(reg) > 5 else voice_chain(nr)
        s0, s1 = max(0.0, a - pad), b + pad
        seg_in = os.path.join(tmp, f"k_{a:.2f}_in.wav")
        seg_cl = os.path.join(tmp, f"k_{a:.2f}_clean.wav")
        write_audio(seg_in, x[int(s0 * SR):int(s1 * SR)])
        run(["ffmpeg", "-v", "error", "-y", "-i", seg_in, "-af", chain, "-c:a", "pcm_f32le", seg_cl])
        before = loudness(seg_in, a - s0, b - s0)
        g = min(gmax, ref + offset_db - voice_peak(read_audio(seg_cl), a - s0, b - s0))
        seg_g = os.path.join(tmp, f"k_{a:.2f}_gain.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", seg_cl, "-af",
             f"volume={g:.2f}dB,"
             f"agate=threshold=0.01:ratio=2:range=0.2:attack=10:release=250,"
             f"acompressor=threshold=-22dB:ratio=2.5:attack=6:release=180:knee=6",
             "-c:a", "pcm_f32le", seg_g])
        y = read_audio(seg_g)
        # el compresor baja un poco los picos: se corrige (sin pasar la ganancia máxima)
        fix = min(gmax - g, ref + offset_db - voice_peak(y, a - s0, b - s0))
        y *= np.float32(10 ** (fix / 20))
        g += fix
        i0 = int(s0 * SR)
        y = y[: n - i0]
        tt = t[i0:i0 + len(y)]
        w = np.clip(np.minimum((tt - a) / ramp, (b - tt) / ramp), 0, 1)
        w = (0.5 - 0.5 * np.cos(np.pi * w))[:, None].astype(np.float32)
        out[i0:i0 + len(y)] = out[i0:i0 + len(y)] * (1 - w) + y * w
        print(f"  {name:26s} {before:6.1f} LUFS → +{g:.1f} dB")

    for a, b, gdb, fade in (duck or []):
        k = np.clip(np.minimum((t - a) / fade, (b + fade - t) / fade), 0, 1)
        k = 0.5 - 0.5 * np.cos(np.pi * k)
        out *= (1 + (10 ** (gdb / 20) - 1) * k).astype(np.float32)[:, None]
        print(f"  {'audio original':26s} {gdb:+.0f} dB de {a:.1f} a {b:.1f} s")

    mixed = write_audio(os.path.join(tmp, "mixed_pre.wav"), out)
    mixed_hp = os.path.join(tmp, "mixed.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", mixed, "-af", "highpass=f=60", "-c:a", "pcm_f32le", mixed_hp])
    if sfx is not None:
        y = read_audio(mixed_hp)
        k = min(len(y), len(sfx))
        y[:k] += sfx[:k]
        write_audio(mixed_hp, y)
    final = glue_and_normalize(mixed_hp, tmp)
    print(f"  {'escena completa':26s} {loudness(raw):6.1f} → {loudness(final):6.1f} LUFS")
    for reg in regions:
        a, b, name = reg[0], reg[1], reg[4]
        print(f"  {name:26s} {loudness(raw, a, b):6.1f} → {loudness(final, a, b):6.1f} LUFS")
    return final


def glue_and_normalize(src, tmp):
    """Compresión suave + limitador para todo, y normalización a -16 LUFS (dos pasadas, lineal)."""
    glued = os.path.join(tmp, "glued.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", GLUE, "-c:a", "pcm_f32le", glued])
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", glued, "-af",
                        f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=7:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    final = os.path.join(tmp, "final.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", glued, "-af",
         f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
         f"aresample={SR}", "-c:a", "pcm_f32le", final])
    return final


# ----------------------------------------------------------------------------
# Video
# ----------------------------------------------------------------------------

VIDEO_FILTER = ("hqdn3d=1.5:1.2:4:3,"                       # quita ruido y bloques de compresión
                "scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int,"
                "cas=strength=0.45,"                         # enfoque adaptativo
                "eq=contrast=1.03:saturation=1.07,"
                "format=yuv420p")


def encode(src, banner_dir, banner_start, banner_x, banner_y, wav, out, fps, crf=17):
    """crf: calidad de x264 (17 = casi sin pérdida; 19-20 para videos largos, así el
    archivo queda por debajo de los 100 MB que acepta GitHub)."""
    fc = (f"[0:v]{VIDEO_FILTER}[v0];"
          f"[1:v]format=rgba,setpts=PTS+{banner_start}/TB[bn];"
          f"[v0][bn]overlay=x={banner_x}:y={banner_y}:eof_action=pass:format=auto,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", src,
         "-framerate", str(fps), "-i", os.path.join(banner_dir, "b_%04d.png"),
         "-i", wav, "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-tune", "film",
         "-profile:v", "high", "-level", "4.1", "-r", str(fps),
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:a", "aac", "-b:a", "256k", "-ar", str(SR),
         "-shortest", "-movflags", "+faststart", out])
