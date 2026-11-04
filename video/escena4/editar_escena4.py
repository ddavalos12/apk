#!/usr/bin/env python3
"""
Escena 4: "El secreto de Sansón" (Jueces 16:17-19) - Escuela Dominical "Monte de Horeb"

Sansón visita a Dalila, conversan, ella le sirve de beber, él se queda dormido
y Dalila se acerca con las tijeras.

A partir del video original (1280x720, 30 fps):
  1. Pone un banner animado "Escena 4 · El secreto de Sansón" al inicio, a la
     derecha (Dalila está a la izquierda).
  2. Sube los tramos de diálogo en vivo (sin micrófono), cada uno según cuánto le
     falta, con limpieza de ruido y ecualización para la voz.
  3. Equilibra los canales y nivela todo el audio (compresión suave y -16 LUFS).
  4. Mejora la imagen: limpieza de compresión, 1920x1080, enfoque y alta calidad.

Uso:
    python3 editar_escena4.py [salida.mp4]
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import os
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE))
import comun_escenas as C  # noqa: E402

SRC = os.path.join(BASE, "original", "escena4_original.mp4")
FPS = 30

# --- banner
BANNER_START = 1.0
BANNER_DUR = 7.5
BANNER_Y = 780
BANNER_SIDE = "right"
LINE1 = "ESCENA 4"
LINE2 = "El secreto de Sansón"

# --- audio: tramos de diálogo en vivo (los bordes caen en pausas)
# (inicio, fin, ganancia máxima en dB, reducción de ruido en dB, nombre)
# La música (1-12 s y 61.4-64.4 s) y la parte fuerte (47.6-55 s) se dejan como están.
KIDS = [
    (12.40, 22.05, 20.0, 10, "Sansón llega con Dalila"),
    (22.05, 31.70, 10.0, 8, "conversación"),
    (32.45, 36.95, 22.0, 10, "diálogo en voz baja"),
    (37.35, 41.85, 10.0, 8, "conversación 2"),
    (42.25, 45.75, 20.0, 10, "Dalila sirve la bebida"),
    (55.45, 58.15, 8.0, 8, "Sansón se duerme"),
    (59.15, 60.25, 16.0, 10, "Dalila con las tijeras"),
]
KIDS_VS_REST_DB = 0.0    # 0 = los picos de la voz quedan como los del resto de la escena


def process_audio(src, tmp):
    return C.boost_regions(src, tmp, KIDS, KIDS_VS_REST_DB)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                          os.path.join(BASE, "escena4_el_secreto_de_sanson.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena4_", dir=os.environ.get("TMPDIR"))
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
