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


def process_audio(src, tmp):
    return C.boost_regions(src, tmp, KIDS, KIDS_VS_REST_DB)


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
