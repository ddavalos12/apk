#!/usr/bin/env python3
"""
Escena 3: "La oferta de los filisteos" (Jueces 16:5) - Escuela Dominical "Monte de Horeb"

Los príncipes de los filisteos visitan a Dalila y le ofrecen plata para que
descubra el secreto de la fuerza de Sansón.

A partir del video original (1280x720, 25 fps):
  1. Pone un banner animado "Escena 3 · La oferta de los filisteos" al inicio,
     a la derecha (Dalila está sentada a la izquierda).
  2. Sube los tramos de diálogo en vivo (sin micrófono), cada uno con limpieza
     de ruido y ecualización para la voz.
  3. Equilibra los canales y nivela todo el audio (compresión suave y -16 LUFS).
  4. Mejora la imagen: limpieza de compresión, 1920x1080, enfoque y alta calidad.

Uso:
    python3 editar_escena3.py [salida.mp4]
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import os
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE))
import comun_escenas as C  # noqa: E402

SRC = os.path.join(BASE, "original", "escena3_original.mp4")
FPS = 25

# --- banner
BANNER_START = 1.0
BANNER_DUR = 7.5
BANNER_Y = 780
BANNER_SIDE = "right"
LINE1 = "ESCENA 3"
LINE2 = "La oferta de los filisteos"

# --- audio: tramos de diálogo en vivo (los bordes caen en pausas)
# (inicio, fin, ganancia máxima en dB, reducción de ruido en dB, nombre)
# La música (13-19 s y 60-65 s) y la parte fuerte (43.5-56 s) se dejan como están.
KIDS = [
    (20.75, 26.60, 14.0, 8, "filisteos hablan con Dalila"),
    (27.45, 33.55, 22.0, 10, "diálogo en voz baja"),
    (35.05, 37.95, 14.0, 8, "diálogo"),
    (38.00, 43.30, 20.0, 12, "frase débil antes del final"),
]
KIDS_VS_REST_DB = 0.0    # 0 = los picos de la voz quedan como los del resto de la escena


def process_audio(src, tmp):
    return C.boost_regions(src, tmp, KIDS, KIDS_VS_REST_DB)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                          os.path.join(BASE, "escena3_la_oferta_de_los_filisteos.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena3_", dir=os.environ.get("TMPDIR"))
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
