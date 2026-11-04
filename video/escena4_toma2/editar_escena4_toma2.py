#!/usr/bin/env python3
"""
Escena 4, toma 2 (archivo "41.mp4"): "El secreto de Sansón" (Jueces 16:17-19)
Escuela Dominical "Monte de Horeb"

Otra grabación, más larga (81 s), de la misma escena: Sansón visita a Dalila,
conversan, ella le sirve de beber, él se queda dormido y Dalila toma las tijeras.

A partir del video original (1280x720, 30 fps):
  1. Pone el banner "Escena 4 · El secreto de Sansón" al inicio, a la derecha.
  2. Sube los tramos de diálogo en vivo, cada uno según cuánto le falta.
     El último tramo (Dalila y la música final) se sube sin el filtro de voz,
     para no quitarle los graves a la música.
  3. Equilibra los canales y nivela todo el audio (compresión suave y -16 LUFS).
  4. Mejora la imagen a 1920x1080.  Se usa CRF 19 (en vez de 17) para que el
     archivo quede por debajo de los 100 MB que acepta GitHub.

Uso:
    python3 editar_escena4_toma2.py [salida.mp4]
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import os
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE))
import comun_escenas as C  # noqa: E402

SRC = os.path.join(BASE, "original", "escena4_toma2_original.mp4")
FPS = 30
CRF = 19

# --- banner
BANNER_START = 1.0
BANNER_DUR = 7.5
BANNER_Y = 780
BANNER_SIDE = "right"
LINE1 = "ESCENA 4"
LINE2 = "El secreto de Sansón"

# --- audio: tramos de diálogo en vivo (los bordes caen en pausas)
# (inicio, fin, ganancia máxima en dB, reducción de ruido en dB, nombre[, filtro])
# La música del inicio (1-14 s) y las partes fuertes (40.6-45.2 s y 60.6-66.4 s,
# cuando Sansón alza la copa) se dejan como están.
MUSIC_CHAIN = "afftdn=nr=4:nf=-60:tn=1,highpass=f=50"
KIDS = [
    (14.05, 18.30, 14.0, 10, "Sansón llega con Dalila"),
    (18.80, 20.80, 14.0, 10, "saludo"),
    (21.50, 26.30, 14.0, 10, "conversación"),
    (26.50, 34.25, 6.0, 8, "conversación 2"),
    (34.45, 39.10, 22.0, 10, "diálogo en voz baja"),
    (45.80, 48.80, 18.0, 10, "Dalila sirve la bebida"),
    (51.65, 52.45, 12.0, 10, "frase corta"),
    (54.55, 56.10, 22.0, 12, "frase en voz baja"),
    (68.45, 81.00, 8.0, 4, "Dalila y la música final", MUSIC_CHAIN),
]
KIDS_VS_REST_DB = 0.0    # 0 = los picos de la voz quedan como los del resto de la escena


def process_audio(src, tmp):
    return C.boost_regions(src, tmp, KIDS, KIDS_VS_REST_DB)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                          os.path.join(BASE, "escena4_el_secreto_de_sanson_toma2.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena4t2_", dir=os.environ.get("TMPDIR"))
    try:
        print("Banner…", flush=True)
        bn = C.render_banner(tmp, LINE1, LINE2, BANNER_DUR, FPS, BANNER_SIDE)
        bx = 0 if BANNER_SIDE == "left" else C.W - bn.cw
        print("Audio…", flush=True)
        wav = process_audio(SRC, tmp)
        print("Video…", flush=True)
        C.encode(SRC, tmp, BANNER_START, bx, BANNER_Y, wav, out, FPS, crf=CRF)
        print("Listo:", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
