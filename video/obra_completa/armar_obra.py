#!/usr/bin/env python3
"""
Obra completa "Sansón y Dalila" (intro + escenas 1 a 5) con overlays animados.

Reconstruye el video que armó el usuario (escuela_dominical.mp4) a partir de
los masters en 1080p, con los mismos cortes:
  intro 0-60 · escena 1 hasta 76.12 s · escena 2 desde 0.75 s · un clip extra
  de 3.9 s (solo está en el video compilado) · escenas 3, 4 (toma 2) y 5.
Agrega overlays según lo que pasa en cada escena (personajes, lugares,
versículos RVR1960, luz divina, golpes, plata, sueño, tijeras, derrumbe) y
un cierre "Fin" con el golpe final de la canción de la intro.

Uso:
    python3 armar_obra.py                     # video completo
    python3 armar_obra.py --preview DIR t...  # cuadros de prueba en esos segundos
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import math
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
V = os.path.dirname(BASE)
sys.path.insert(0, V)
sys.path.insert(0, BASE)
import comun_escenas as C  # noqa: E402
import overlays as O  # noqa: E402

W, H, FPS, SR = 1920, 1080, 30, 48000
COMPILADO = os.path.join(BASE, "original", "escuela_dominical_compilado.mp4")
SONG = os.path.join(V, "intro_sanson", "assets", "audio", "con_fuerza_de_dios.mp3")
OUT = os.path.join(BASE, "sanson_y_dalila_obra_completa.mp4")
CRF = 20

UPSCALE = ("hqdn3d=3:2.5:6:5,scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int,"
           "cas=strength=0.5,eq=contrast=1.03:saturation=1.07")

# (clave, archivo, inicio en la fuente, fin en la fuente, filtro extra, fundido de entrada, de salida)
SEGMENTS = [
    ("intro", os.path.join(V, "intro_sanson_dalila.mp4"), 0.0, 60.0, None, 0.0, 0.0),
    ("e1", os.path.join(V, "escena1", "escena1_la_revelacion.mp4"), 0.0, 76.12, None, 0.35, 0.35),
    ("e2", os.path.join(V, "escena2", "escena2_la_quijada_de_asno.mp4"), 0.75, 56.70, None, 0.35, 0.0),
    ("extra", COMPILADO, 192.07, 195.97, UPSCALE, 0.0, 0.35),
    ("e3", os.path.join(V, "escena3", "escena3_la_oferta_de_los_filisteos.mp4"), 0.0, 64.83, None, 0.35, 0.35),
    ("e4", os.path.join(V, "escena4_toma2", "escena4_el_secreto_de_sanson_toma2.mp4"), 0.0, 80.96, None, 0.35, 0.35),
    ("e5", os.path.join(V, "escena5", "escena5_el_templo_de_dagon.mp4"), 0.0, 103.78, None, 0.35, 0.0),
]
OUTRO = 7.0           # segundos del cierre "Fin" (último cuadro congelado)
T_FIN_IN_OUTRO = 3.6  # "Fin" aparece con el golpe final de la canción
SONG_HIT = 57.211 + 89 * 4 * 60 / 143.0   # golpe final de la canción (mismo que en la intro)

# cuadros y comienzo de cada tramo en el video final
NFR, G0, SRC_IN = {}, {}, {}
_g = 0
for key, path, a, b, *_ in SEGMENTS:
    NFR[key] = int(round((b - a) * FPS))
    G0[key] = _g / FPS
    SRC_IN[key] = a
    _g += NFR[key]
T_OUTRO = _g / FPS
TOTAL_FRAMES = _g + int(round(OUTRO * FPS))


def L(key, t):
    """Segundo t del master de la escena -> segundo del video final."""
    return G0[key] + (t - SRC_IN[key])


# ----------------------------------------------------------------------------
# Overlays por escena (tiempos en segundos de cada master; posiciones 0-1)
# ----------------------------------------------------------------------------

def build_overlays():
    ov = []
    # --- Escena 1: La revelación
    ov += [
        O.LocationPin("ZORA", "Tribu de Dan", "JUECES 13:2", L("e1", 9.5), L("e1", 14.8)),
        O.VerseCard("Los hijos de Israel volvieron a hacer lo malo ante los ojos de Jehová; y Jehová los "
                    "entregó en mano de los filisteos por cuarenta años.", "JUECES 13:1",
                    L("e1", 15.5), L("e1", 24.8)),
        O.NameTag("LA ESPOSA DE MANOA", "era estéril y no tenía hijos", L("e1", 26.0), L("e1", 31.5),
                  (0.535, 0.41), (0.74, 0.30)),
        O.DivineLight(L("e1", 41.8), L("e1", 48.8), (0.27, 0.40), strength=0.9),
        O.NameTag("EL ÁNGEL DE JEHOVÁ", "anuncia un hijo", L("e1", 43.6), L("e1", 48.4),
                  (0.27, 0.34), (0.15, 0.15)),
        O.VerseCard("…concebirás y darás a luz un hijo; y navaja no pasará sobre su cabeza, porque el niño "
                    "será nazareo a Dios desde su nacimiento…", "JUECES 13:5", L("e1", 49.5), L("e1", 57.8)),
        O.TitleCard("Nace Sansón", "Y la mujer dio a luz un hijo, y le puso por nombre Sansón. Y el niño "
                    "creció, y Jehová lo bendijo.", "JUECES 13:24", L("e1", 64.6), L("e1", 75.6)),
    ]
    # --- Escena 2: La quijada de asno
    ov += [
        O.NameTag("SANSÓN", "nazareo de Dios", L("e2", 9.0), L("e2", 12.6), (0.515, 0.11), (0.68, 0.12)),
        O.LocationPin("LEHI", "Tierra de Judá", "JUECES 15:9-14", L("e2", 13.0), L("e2", 17.2)),
        O.NameTag("LOS FILISTEOS", "enemigos de Israel", L("e2", 17.4), L("e2", 20.8), (0.79, 0.29),
                  (0.80, 0.09)),
    ]
    for k, (t, x, y, s) in enumerate([(20.0, 0.50, 0.45, 1.0), (21.9, 0.61, 0.78, 0.8), (24.6, 0.86, 0.80, 0.8),
                                      (28.7, 0.53, 0.33, 1.0), (29.8, 0.57, 0.82, 0.8)]):
        ov.append(O.ImpactBurst(L("e2", t), (x, y), s, seed=k))
    ov += [
        O.VerseCard("Y hallando una quijada de asno fresca aún, extendió la mano y la tomó, y mató con ella a "
                    "mil hombres.", "JUECES 15:15", L("e2", 31.5), L("e2", 39.8)),
        O.VerseCard("Después de esto aconteció que se enamoró de una mujer en el valle de Sorec, la cual se "
                    "llamaba Dalila.", "JUECES 16:4", L("e2", 50.6), G0["e3"] - 0.45),
    ]
    # --- Escena 3: La oferta de los filisteos
    ov += [
        O.NameTag("DALILA", "del valle de Sorec", L("e3", 9.0), L("e3", 13.2), (0.23, 0.62), (0.42, 0.47)),
        O.LocationPin("VALLE DE SOREC", "Casa de Dalila", "JUECES 16:4", L("e3", 13.6), L("e3", 18.2)),
        O.NameTag("LOS FILISTEOS", "príncipes que visitan a Dalila", L("e3", 19.6), L("e3", 24.2),
                  (0.585, 0.15), (0.80, 0.09)),
        O.VerseCard("Engáñale e infórmate en qué consiste su gran fuerza, y cómo lo podríamos vencer… y cada "
                    "uno de nosotros te dará mil cien siclos de plata.", "JUECES 16:5",
                    L("e3", 24.6), L("e3", 33.3)),
        O.Sparkles(L("e3", 36.0), L("e3", 40.3), (0.60, 0.47), (0.05, 0.07), seed=3),
        O.Sparkles(L("e3", 40.6), L("e3", 52.5), (0.45, 0.42), (0.05, 0.06), seed=4),
        O.NameTag("MIL CIEN SICLOS", "de plata, de cada príncipe", L("e3", 43.0), L("e3", 50.0),
                  (0.44, 0.42), (0.19, 0.27)),
    ]
    # --- Escena 4: El secreto de Sansón (toma 2)
    ov += [
        O.NameTag("DALILA", "quiere saber el secreto", L("e4", 9.0), L("e4", 12.6), (0.16, 0.30), (0.34, 0.14)),
        O.NameTag("SANSÓN", "visita a Dalila", L("e4", 14.0), L("e4", 18.0), (0.70, 0.25), (0.86, 0.12)),
        O.VerseCard("Nunca a mi cabeza llegó navaja; porque soy nazareo de Dios desde el vientre de mi madre. "
                    "Si fuere rapado, mi fuerza se apartará de mí…", "JUECES 16:17",
                    L("e4", 29.8), L("e4", 38.6)),
        O.NightTint(L("e4", 66.8), L("e4", 74.3)),
        O.Zzz(L("e4", 67.4), L("e4", 73.8), (0.32, 0.50)),
        O.Glint(L("e4", 74.35), (0.715, 0.12), size=80),
        O.VignettePulse(L("e4", 74.0), G0["e5"] - 0.1),
        O.VerseCard("Y ella hizo que él se durmiese sobre sus rodillas, y llamó a un hombre, quien le rapó "
                    "las siete guedejas de su cabeza…", "JUECES 16:19", L("e4", 74.6), L("e4", 80.6)),
    ]
    # --- Escena 5: El templo de Dagón
    ov += [
        O.LocationPin("GAZA", "Templo de Dagón", "JUECES 16:21-23", L("e5", 9.5), L("e5", 14.8)),
        O.VerseCard("…se juntaron para ofrecer sacrificio a Dagón su dios y para alegrarse; y dijeron: "
                    "Nuestro dios entregó en nuestras manos a Sansón nuestro enemigo.", "JUECES 16:23",
                    L("e5", 15.2), L("e5", 24.2)),
        O.NameTag("SANSÓN", "ciego y encadenado", L("e5", 62.0), L("e5", 66.4), (0.42, 0.36), (0.42, 0.10)),
        O.VerseCard("Acércame, y hazme palpar las columnas sobre las que descansa la casa, para que me apoye "
                    "sobre ellas.", "JUECES 16:26", L("e5", 80.0), L("e5", 87.8)),
        O.VerseCard("Señor Jehová, acuérdate ahora de mí, y fortaléceme, te ruego, solamente esta vez, "
                    "oh Dios…", "JUECES 16:28", L("e5", 89.0), L("e5", 96.2)),
        O.DivineLight(L("e5", 92.4), L("e5", 99.0), (0.44, 0.38), strength=1.1, fin=1.2, fout=0.4, seed=8),
        O.Flash(L("e5", 99.1)),
        O.Dust(L("e5", 98.9), T_OUTRO + OUTRO),
        O.EndCard(T_OUTRO, T_OUTRO + OUTRO, T_OUTRO + T_FIN_IN_OUTRO,
                  "Y dijo Sansón: Muera yo con los filisteos. Entonces se inclinó con toda su fuerza, y cayó "
                  "la casa…", "JUECES 16:30"),
    ]
    return ov


def shake_amp(g):
    """Temblor durante el derrumbe (px)."""
    t = g - G0["e5"]
    if t < 95.8 or g >= T_OUTRO + 0.5:
        return 0.0
    a = 5.0 * O.smooth((t - 95.8) / 2.8)
    if t > 98.6:
        a = 5.0 * math.exp(-(t - 98.6) / 1.2) + 2.0
    if t >= 99.1:
        a += 22.0 * math.exp(-(t - 99.1) / 0.75)
    return a * (1 - O.smooth((g - (T_OUTRO - 0.6)) / 0.6))


def shake(frame, g, a):
    dx = a * (0.6 * math.sin(2 * math.pi * 11 * g) + 0.4 * math.sin(2 * math.pi * 17.3 * g + 1))
    dy = a * (0.6 * math.sin(2 * math.pi * 13.1 * g + 2) + 0.4 * math.sin(2 * math.pi * 7.7 * g))
    s = 1 + 2.6 * a / 1000 + 0.004
    c = W / 2 - (W / 2 + dx) / s
    f = H / 2 - (H / 2 + dy) / s
    im = Image.fromarray(frame).transform((W, H), Image.AFFINE, (1 / s, 0, c, 0, 1 / s, f), Image.BILINEAR)
    return np.asarray(im).copy()


def composite(frame, g, overlays):
    a = shake_amp(g)
    if a > 0.05:
        frame = shake(frame, g, a)
    if g >= T_OUTRO:   # cierre: el último cuadro se va desenfocando
        r = min(9.0, (g - T_OUTRO) * 7)
        if r > 0.3:
            frame = np.asarray(Image.fromarray(frame).filter(ImageFilter.GaussianBlur(r))).copy()
    act = [o for o in overlays if o.t0 <= g < o.t1]
    if not act:
        return frame
    if any(o.full for o in act):
        x0, y0, x1, y1 = 0, 0, W, H
    else:
        bs = [o.bbox(g) for o in act]
        x0 = max(0, min(b[0] for b in bs))
        y0 = max(0, min(b[1] for b in bs))
        x1 = min(W, max(b[2] for b in bs))
        y1 = min(H, max(b[3] for b in bs))
        if x0 >= x1 or y0 >= y1:
            return frame
    reg = frame[y0:y1, x0:x1].astype(np.float32) * (1 / 255)
    buf = O.Buf(reg, x0, y0)
    for o in sorted(act, key=lambda o: o.layer):
        o.draw(buf, g)
    np.clip(reg, 0, 1, out=reg)
    frame[y0:y1, x0:x1] = (reg * 255 + 0.5).astype(np.uint8)
    return frame


# ----------------------------------------------------------------------------
# Audio
# ----------------------------------------------------------------------------

def read_seg(path, start, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.4f}", "-t", f"{dur + 0.5:.4f}", "-i", path,
                          "-vn", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(round(dur * SR))
    if len(x) < n:
        x = np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])
    return x[:n]


def fades(x, fin, fout):
    n = len(x)
    if fin > 0:
        k = int(fin * SR)
        x[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None]
    if fout > 0:
        k = int(fout * SR)
        x[n - k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
    return x


def build_audio(path):
    parts = []
    for key, src, a, b, _, fin, fout in SEGMENTS:
        dur = NFR[key] / FPS
        x = read_seg(src, a, dur)
        # fundidos de audio cortos (sin cortar palabras); la escena 5 se apaga antes del cierre
        x = fades(x, min(fin, 0.05) if fin else 0.0, 0.9 if key == "e5" else (0.15 if fout else 0.0))
        parts.append(x)
    # cierre: la canción de la intro, que sube y termina con su golpe final al aparecer "Fin"
    s0 = SONG_HIT - T_FIN_IN_OUTRO
    song = read_seg(SONG, s0, OUTRO)
    song *= np.float32(10 ** (-3.4 / 20))
    k = int(1.6 * SR)
    song[:k] *= (np.linspace(0, 1, k, dtype=np.float32) ** 2)[:, None]
    k = int(0.8 * SR)
    song[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
    parts.append(song)
    y = np.concatenate(parts)
    peak = np.abs(y).max()
    if peak > 0.97:
        y *= 0.97 / peak
    C.write_audio(path, y)
    return path


# ----------------------------------------------------------------------------
# Video
# ----------------------------------------------------------------------------

def decoder_cmd():
    cmd = ["ffmpeg", "-v", "error"]
    seeks = {}
    for key, src, a, *_ in SEGMENTS:
        if key == "extra":
            pre = max(0.0, a - 1.0)
            cmd += ["-ss", f"{pre:.3f}"]
            seeks[key] = a - pre
        else:
            seeks[key] = a
        cmd += ["-i", src]
    fc = []
    for i, (key, src, a, b, extra, fin, fout) in enumerate(SEGMENTS):
        n = NFR[key]
        f = (f"[{i}:v]trim=start={seeks[key]:.4f}:duration={n / FPS + 0.6:.4f},setpts=PTS-STARTPTS,"
             f"fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS,setsar=1")
        if extra:
            f += "," + extra
        if fin:
            f += f",fade=t=in:st=0:d={fin}"
        if fout:
            f += f",fade=t=out:start_frame={n - int(fout * FPS)}:nb_frames={int(fout * FPS)}"
        f += f",scale=in_color_matrix=bt709:in_range=tv,format=rgb24[v{i}]"
        fc.append(f)
    fc.append("".join(f"[v{i}]" for i in range(len(SEGMENTS))) +
              f"concat=n={len(SEGMENTS)}:v=1:a=0,tpad=stop_mode=clone:stop_duration={OUTRO}[v]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return cmd


def encoder_cmd(wav, out):
    keys = ",".join(f"{G0[k]:.3f}" for k, *_ in SEGMENTS[1:] if k != "extra") + f",{T_OUTRO:.3f}"
    return ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-", "-i", wav,
            "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF), "-maxrate", "9M", "-bufsize", "18M",
            "-tune", "film", "-profile:v", "high", "-level", "4.1", "-g", "60", "-force_key_frames", keys,
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", out]


def render(out=OUT):
    tmpwav = os.path.splitext(out)[0] + "_audio.wav"
    print("Audio…", flush=True)
    build_audio(tmpwav)
    print("Overlays…", flush=True)
    ov = build_overlays()
    print(f"Video: {TOTAL_FRAMES} cuadros ({TOTAL_FRAMES / FPS:.1f} s)…", flush=True)
    dec = subprocess.Popen(decoder_cmd(), stdout=subprocess.PIPE, bufsize=0)
    enc = subprocess.Popen(encoder_cmd(tmpwav, out), stdin=subprocess.PIPE)
    fb = W * H * 3
    buf = bytearray(fb)
    mv = memoryview(buf)
    t_start = time.time()
    last = None
    for i in range(TOTAL_FRAMES):
        got = 0
        while got < fb:
            r = dec.stdout.readinto(mv[got:])
            if not r:
                break
            got += r
        if got < fb:
            if last is None:
                raise RuntimeError("el decodificador no entregó cuadros")
            frame = last.copy()          # (por seguridad) repite el último cuadro
        else:
            frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
            last = frame
        frame = composite(frame, i / FPS, ov)
        enc.stdin.write(np.ascontiguousarray(frame).data)
        if i % 600 == 0:
            el = time.time() - t_start
            print(f"  {i}/{TOTAL_FRAMES}  {el / 60:.1f} min", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    os.remove(tmpwav)
    print("Listo:", out, f"({(time.time() - t_start) / 60:.1f} min)")


def split_parts(src=OUT):
    """Una parte por escena (con -c copy, sin perder calidad), cada una < 100 MB."""
    names = {"intro": "0_intro", "e1": "1_la_revelacion", "e2": "2_la_quijada_de_asno",
             "e3": "3_la_oferta_de_los_filisteos", "e4": "4_el_secreto_de_sanson", "e5": "5_el_templo_de_dagon"}
    keys = [k for k, *_ in SEGMENTS if k != "extra"]
    starts = [G0[k] for k in keys] + [T_OUTRO + OUTRO]
    folder = os.path.join(BASE, "partes")
    os.makedirs(folder, exist_ok=True)
    for k, a, b in zip(keys, starts[:-1], starts[1:]):
        p = os.path.join(folder, f"parte_{names[k]}.mp4")
        C.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", src,
               "-c", "copy", "-movflags", "+faststart", p])
        print("  ", p)


def preview(folder, times):
    os.makedirs(folder, exist_ok=True)
    ov = build_overlays()
    for g in times:
        gg = min(g, T_OUTRO - 0.25)
        for key, src, a, b, extra, *_ in reversed(SEGMENTS):
            if gg >= G0[key]:
                break
        local = a + (gg - G0[key])
        vf = (extra + "," if extra else "") + "scale=1920:1080,format=rgb24"
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{local:.3f}", "-i", src, "-frames:v", "1",
                              "-vf", vf, "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
        frame = np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()
        frame = composite(frame, g, ov)
        Image.fromarray(frame).save(os.path.join(folder, f"p_{g:07.2f}.jpg"), quality=90)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        preview(sys.argv[2], [float(x) for x in sys.argv[3:]])
    elif len(sys.argv) > 1 and sys.argv[1] == "--partes":
        split_parts()
    else:
        render(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else OUT)
        split_parts()
