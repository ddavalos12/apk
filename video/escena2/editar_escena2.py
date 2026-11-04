#!/usr/bin/env python3
"""
Escena 2: "La quijada de asno" (Jueces 15:15) - Escuela Dominical "Monte de Horeb"

A partir del video original (1280x720, 25 fps):
  1. Pone un banner animado "Escena 2 · La quijada de asno" al inicio, a la
     derecha (Sansón está a la izquierda del escenario).
  2. Sube los tramos donde los niños hablan sin micrófono, cada uno con su
     limpieza de ruido y ecualización para la voz.
  3. Equilibra los canales izquierdo/derecho y nivela todo el audio
     (compresión suave y -16 LUFS, pico máximo -1.5 dBTP).
  4. Mejora la imagen: reduce el ruido de compresión, escala a 1920x1080,
     enfoca un poco y codifica a alta calidad.

Uso:
    python3 editar_escena2.py [salida.mp4]
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import os
import shutil
import sys
import tempfile

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE))
import comun_escenas as C  # noqa: E402

SRC = os.path.join(BASE, "original", "escena2_original.mp4")
FPS = 25

# --- banner
BANNER_START = 1.0
BANNER_DUR = 7.5
BANNER_Y = 780
BANNER_SIDE = "right"
LINE1 = "ESCENA 2"
LINE2 = "La quijada de asno"

# --- audio: tramos en que los niños hablan sin micrófono
# (inicio, fin, ganancia máxima en dB, reducción de ruido en dB, nombre)
KIDS = [
    (19.00, 22.05, 16.0, 15, "pelea con los filisteos"),   # casi todo forcejeo y ruido de sala: subida moderada
    (34.25, 35.45, 28.0, 12, "Sansón habla solo"),
    (44.30, 45.75, 18.0, 8, "Sansón y la mujer"),          # voz clara
]
KIDS_VS_REST_DB = 0.0    # 0 = los picos de la voz quedan como los del resto de la escena
PAD = 0.3                # margen que se procesa alrededor de cada tramo
RAMP = 0.06              # fundido para entrar y salir de cada tramo (s)


def voice_peak(x, a=None, b=None):
    """Nivel de los picos de la voz: percentil 95 del nivel en ventanas de 50 ms (dB).
    En tramos cortos con pausas es más fiable que el promedio."""
    m = x.mean(1)
    if a is not None:
        m = m[int(a * C.SR):int(b * C.SR)]
    win = int(0.05 * C.SR)
    k = len(m) // win
    r = np.sqrt((m[:k * win].reshape(k, win) ** 2).mean(1)) + 1e-9
    return float(np.percentile(20 * np.log10(r), 95))


def process_audio(src, tmp):
    raw = C.decode_audio(src, os.path.join(tmp, "raw.wav"))
    x = C.read_audio(raw)
    n = len(x)
    t = np.arange(n) / C.SR
    ref = voice_peak(x)            # picos de la escena (casi todo es la parte con buen volumen)

    # equilibrio izquierda/derecha (el canal derecho venía 0.8 dB más bajo)
    rms = np.sqrt((x ** 2).mean(0))
    x *= (np.sqrt(rms[0] * rms[1]) / rms)[None, :]

    out = x.copy()
    for a, b, gmax, nr, name in KIDS:
        s0, s1 = max(0.0, a - PAD), b + PAD
        seg_in = os.path.join(tmp, f"k_{a:.2f}_in.wav")
        seg_cl = os.path.join(tmp, f"k_{a:.2f}_clean.wav")
        C.write_audio(seg_in, x[int(s0 * C.SR):int(s1 * C.SR)])
        C.run(["ffmpeg", "-v", "error", "-y", "-i", seg_in, "-af", C.voice_chain(nr),
               "-c:a", "pcm_f32le", seg_cl])
        before = C.loudness(seg_in, a - s0, b - s0)
        g = min(gmax, ref + KIDS_VS_REST_DB - voice_peak(C.read_audio(seg_cl), a - s0, b - s0))
        seg_g = os.path.join(tmp, f"k_{a:.2f}_gain.wav")
        C.run(["ffmpeg", "-v", "error", "-y", "-i", seg_cl, "-af",
               f"volume={g:.2f}dB,"
               f"agate=threshold=0.01:ratio=2:range=0.2:attack=10:release=250,"
               f"acompressor=threshold=-22dB:ratio=2.5:attack=6:release=180:knee=6",
               "-c:a", "pcm_f32le", seg_g])
        y = C.read_audio(seg_g)
        # el compresor baja un poco los picos: se corrige (sin pasar el tope de ganancia)
        fix = min(gmax - g, ref + KIDS_VS_REST_DB - voice_peak(y, a - s0, b - s0))
        y *= np.float32(10 ** (fix / 20))
        g += fix
        # mezcla con fundidos cortos al entrar y salir del tramo
        i0 = int(s0 * C.SR)
        y = y[: n - i0]
        tt = t[i0:i0 + len(y)]
        w = np.clip(np.minimum((tt - a) / RAMP, (b - tt) / RAMP), 0, 1)
        w = (0.5 - 0.5 * np.cos(np.pi * w))[:, None].astype(np.float32)
        out[i0:i0 + len(y)] = out[i0:i0 + len(y)] * (1 - w) + y * w
        print(f"  {name:24s} {before:6.1f} LUFS → +{g:.1f} dB")

    # graves muy bajos fuera (retumbe); la música de entrada conserva su bajo
    mixed = C.write_audio(os.path.join(tmp, "mixed_pre.wav"), out)
    mixed_hp = os.path.join(tmp, "mixed.wav")
    C.run(["ffmpeg", "-v", "error", "-y", "-i", mixed, "-af", "highpass=f=60", "-c:a", "pcm_f32le", mixed_hp])
    final = C.glue_and_normalize(mixed_hp, tmp)
    print(f"  {'escena completa':24s} {C.loudness(final):6.1f} LUFS")
    for a, b, _, _, name in KIDS:
        print(f"  {name:24s} {C.loudness(final, a, b):6.1f} LUFS (final)")
    return final


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "escena2_la_quijada_de_asno.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena2_", dir=os.environ.get("TMPDIR"))
    try:
        print("Banner…", flush=True)
        bn = C.render_banner(tmp, LINE1, LINE2, BANNER_DUR, FPS, BANNER_SIDE)
        bx = 0 if BANNER_SIDE == "left" else C.W - bn.cw
        print("Audio…", flush=True)
        wav = process_audio(SRC, tmp)
        print("Video…", flush=True)
        C.encode(SRC, tmp, BANNER_START, bx, BANNER_Y, wav, out, FPS)
        print("Listo:", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
