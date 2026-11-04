#!/usr/bin/env python3
"""
Escena 1: "La revelación" - Escuela Dominical "Monte de Horeb"

A partir del video original (1280x720, 25 fps):
  1. Pone un banner animado "Escena 1 · La revelación" al inicio.
  2. Sube la voz de los niños (la parte sin micrófono, 43.75-60.5 s) hasta el
     nivel del narrador, con limpieza de ruido y ecualización para la voz.
  3. Nivela todo el audio (compresión suave y -16 LUFS, pico máximo -1.5 dBTP).
  4. Mejora la imagen: reduce el ruido de compresión, escala a 1920x1080 con
     Lanczos, enfoca un poco y codifica a alta calidad.

Uso:
    python3 editar_escena1.py [salida.mp4]
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "original", "escena1_original.mp4")
FONTS = os.path.join(BASE, "..", "intro_sanson", "assets", "fonts")

W, H = 1920, 1080
FPS = 25

# --- banner
BANNER_START = 1.0      # segundo del video en que aparece
BANNER_DUR = 7.5        # cuánto dura en pantalla (incluye entrada y salida)
BANNER_X, BANNER_Y = 0, 780
LINE1 = "ESCENA 1"
LINE2 = "La revelación"

# --- audio
KIDS = (43.75, 60.5)    # parte en que hablan los niños (los bordes caen en silencio)
KIDS_VS_NARRATOR_DB = 1.0   # los niños quedan 1 dB por encima del narrador
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
    def __init__(self):
        f1 = ImageFont.truetype(os.path.join(FONTS, "Cinzel-SemiBold.ttf"), 34)
        f2 = ImageFont.truetype(os.path.join(FONTS, "Cormorant-SemiBoldItalic.ttf"), 96)
        w1 = tracked_width(f1, LINE1, 9)
        w2 = f2.getlength(LINE2)
        self.tx = 112                                   # margen izquierdo del texto
        self.ribbon_end = int(self.tx + max(w1, w2) + 70)  # donde termina la cinta (antes de la punta)
        self.tip = 46
        self.top, self.bot = 52, 222                    # borde superior / inferior de la cinta
        self.cw = self.ribbon_end + self.tip + 60
        self.ch = 280
        cw, ch, top, bot = self.cw, self.ch, self.top, self.bot
        mid = (top + bot) / 2
        poly = [(0, top), (self.ribbon_end, top), (self.ribbon_end + self.tip, mid),
                (self.ribbon_end, bot), (0, bot)]

        # forma de la cinta
        m = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        self.mask = np.asarray(m).astype(np.float32) / 255

        # relleno azul con degradado horizontal y brillo superior
        xx = np.linspace(0, 1, cw, dtype=np.float32)[None, :, None]
        yy = np.linspace(0, 1, ch, dtype=np.float32)[:, None, None]
        fill = NAVY_L * (1 - xx) + NAVY_R * xx
        sheen = np.clip(1 - (yy - top / ch) / 0.25, 0, 1) * 0.10
        fill = fill + sheen
        self.fill = np.broadcast_to(fill, (ch, cw, 3)).astype(np.float32)

        # bordes dorados (doble línea siguiendo la forma)
        g = Image.new("L", (cw, ch), 0)
        d = ImageDraw.Draw(g)
        d.line([(0, top), (self.ribbon_end, top), (self.ribbon_end + self.tip, mid),
                (self.ribbon_end, bot), (0, bot)], fill=255, width=4, joint="curve")
        inset = 9
        d.line([(0, top + inset), (self.ribbon_end - 4, top + inset),
                (self.ribbon_end + self.tip - inset - 6, mid),
                (self.ribbon_end - 4, bot - inset), (0, bot - inset)], fill=150, width=1, joint="curve")
        # barra de acento a la izquierda del texto + rombo
        d.rectangle((70, top + 28, 75, bot - 28), fill=255)
        d.polygon([(72.5, top + 14), (80, top + 22), (72.5, top + 30), (65, top + 22)], fill=255)
        d.polygon([(72.5, bot - 30), (80, bot - 22), (72.5, bot - 14), (65, bot - 22)], fill=255)
        self.gold_a = np.asarray(g).astype(np.float32)[..., None] / 255
        grad = GOLD_TOP * (1 - yy) + GOLD_BOT * yy
        self.gold = np.broadcast_to(grad, (ch, cw, 3)).astype(np.float32)

        # sombra
        sh = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sh).polygon([(x, y + 10) for x, y in poly], fill=200)
        self.shadow = np.asarray(sh.filter(ImageFilter.GaussianBlur(16))).astype(np.float32) / 255

        # textos
        def text_layer(draw_fn):
            a = Image.new("L", (cw, ch), 0)
            draw_fn(ImageDraw.Draw(a))
            arr = np.asarray(a).astype(np.float32) / 255
            shadow = np.asarray(a.filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255
            return arr, np.roll(shadow, 3, axis=0)

        y1 = top + 20
        self.t1 = text_layer(lambda d: draw_tracked(d, self.tx, y1, LINE1, f1, 9, 255))
        y2 = top + 52
        self.t2 = text_layer(lambda d: d.text((self.tx - 4, y2), LINE2, font=f2, fill=255))
        self.t1_col = self.gold
        self.t2_col = np.broadcast_to(np.array(CREAM, np.float32) / 255, (ch, cw, 3))

        xs = np.arange(cw, dtype=np.float32)[None, :]
        ys = np.arange(ch, dtype=np.float32)[:, None]
        self.diag = xs + (ys - ch / 2) * 0.45  # para el destello diagonal

    def frame(self, tau):
        """RGBA (uint8) del banner en el instante tau (segundos desde que empieza)."""
        cw, ch = self.cw, self.ch
        # entrada: la cinta sale desde el borde izquierdo; salida: vuelve a entrar
        e_in = ease_out(tau / 0.75)
        e_out = ease_in((tau - (BANNER_DUR - 0.7)) / 0.7)
        reveal = cw * e_in * (1 - e_out)
        cut = np.clip((reveal - np.arange(cw, dtype=np.float32)) / 6.0, 0, 1)[None, :]
        shift = -50 * (1 - e_in) - 50 * e_out

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

        # textos
        t_out = 1 - ease_out((tau - (BANNER_DUR - 1.05)) / 0.35)
        for (arr, shd), col, delay in ((self.t1, self.t1_col, 0.45), (self.t2, self.t2_col, 0.6)):
            k = ease_out((tau - delay) / 0.6) * t_out
            if k <= 0:
                continue
            dy = int(round((1 - k) * 14))
            a = np.roll(arr, dy, axis=0) * k * cut[0][None, :]
            s = np.roll(shd, dy, axis=0) * k * 0.6 * cut[0][None, :]
            over(np.zeros(3, np.float32), s * self.mask)
            over(col, a)

        # destello dorado que cruza la cinta una vez
        if 1.0 < tau < 2.0:
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


def render_banner(folder):
    b = Banner()
    n = int(round(BANNER_DUR * FPS))
    for i in range(n):
        b.frame(i / FPS).save(os.path.join(folder, f"b_{i:04d}.png"), compress_level=1)
    return n


# ----------------------------------------------------------------------------
# Audio
# ----------------------------------------------------------------------------

def loudness(path, start=None, end=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start is not None:
        cmd += ["-ss", str(start), "-to", str(end)]
    cmd += ["-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    vals = [ln.split()[1] for ln in err.splitlines() if ln.strip().startswith("I:")]
    return float(vals[-1])


KIDS_CHAIN = ("afftdn=nr=10:nf=-60:tn=1,"            # quita ruido de fondo (sigue al ruido)
              "highpass=f=120,highpass=f=120,highpass=f=100,"  # corte fuerte de graves: sin pasos ni retumbe del escenario
              "equalizer=f=280:t=q:w=1.0:g=-2.5,"      # menos voz "encajonada"
              "equalizer=f=3200:t=q:w=1.2:g=4,"        # más claridad en las palabras
              "equalizer=f=7500:t=q:w=1.0:g=1.5")


def process_audio(src, tmp):
    raw = os.path.join(tmp, "raw.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le", raw])
    a, b = KIDS
    narr = loudness(raw, 14.0, 42.5)

    # 1) voz de los niños limpia y ecualizada, llevada al nivel del narrador y
    #    con un compresor que empareja sílabas y a los dos niños entre sí
    kids0 = os.path.join(tmp, "kids0.wav")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", raw,
         "-af", KIDS_CHAIN, "-c:a", "pcm_f32le", kids0])
    g1 = narr - loudness(kids0)
    kids1 = os.path.join(tmp, "kids1.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", kids0, "-af",
         f"volume={g1:.2f}dB,"
         f"agate=threshold=0.01:ratio=2:range=0.2:attack=10:release=250,"   # baja el ruido entre palabras
         f"acompressor=threshold=-22dB:ratio=3:attack=6:release=180:knee=6",
         "-c:a", "pcm_f32le", kids1])
    # 2) la compresión les quita volumen: se vuelve a igualar con el narrador
    g2 = narr + KIDS_VS_NARRATOR_DB - loudness(kids1)
    print(f"  narrador {narr:.1f} LUFS · niños antes {loudness(raw, a, b):.1f} LUFS · "
          f"ganancia total +{g1 + g2:.1f} dB")

    # 3) unir las tres partes y comprimir todo junto (así todos quedan parejos)
    mixed = os.path.join(tmp, "mixed.wav")
    fc = (f"[0:a]highpass=f=60,asplit=2[x1][x3];"
          f"[x1]atrim=0:{a},asetpts=N/SR/TB[p1];"
          f"[1:a]volume={g2:.2f}dB[p2];"
          f"[x3]atrim={b},asetpts=N/SR/TB[p3];"
          f"[p1][p2][p3]concat=n=3:v=0:a=1,"
          f"acompressor=threshold=-20dB:ratio=2.2:attack=12:release=250:knee=6,"
          f"alimiter=limit=0.85:attack=3:release=60:level=false[out]")
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-i", kids1, "-filter_complex", fc, "-map", "[out]",
         "-c:a", "pcm_f32le", mixed])

    # 3) normalización final de volumen (dos pasadas, lineal)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mixed, "-af",
                        f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=7:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    final = os.path.join(tmp, "final.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", mixed, "-af",
         f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
         f"aresample=48000", "-c:a", "pcm_f32le", final])
    for name, (s, e) in (("música", (0, 13.5)), ("narrador", (14, 42.5)), ("niños", KIDS), ("narrador 2", (61, 76.4))):
        print(f"  {name:10s} {loudness(final, s, e):6.1f} LUFS")
    return final


# ----------------------------------------------------------------------------

VIDEO_FILTER = ("hqdn3d=1.5:1.2:4:3,"                       # quita ruido y bloques de compresión
                "scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int,"
                "cas=strength=0.45,"                         # enfoque adaptativo
                "eq=contrast=1.03:saturation=1.07,"
                "format=yuv420p")


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "escena1_la_revelacion.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena1_", dir=os.environ.get("TMPDIR"))
    try:
        print("Banner…", flush=True)
        render_banner(tmp)
        print("Audio…", flush=True)
        wav = process_audio(SRC, tmp)
        print("Video…", flush=True)
        fc = (f"[0:v]{VIDEO_FILTER}[v0];"
              f"[1:v]format=rgba,setpts=PTS+{BANNER_START}/TB[bn];"
              f"[v0][bn]overlay=x={BANNER_X}:y={BANNER_Y}:eof_action=pass:format=auto,format=yuv420p[v]")
        run(["ffmpeg", "-v", "error", "-y", "-i", SRC,
             "-framerate", str(FPS), "-i", os.path.join(tmp, "b_%04d.png"),
             "-i", wav, "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
             "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "film",
             "-profile:v", "high", "-level", "4.1", "-r", str(FPS),
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
             "-shortest", "-movflags", "+faststart", out])
        print("Listo:", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
