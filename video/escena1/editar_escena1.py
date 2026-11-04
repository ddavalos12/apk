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
import os
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE))
import comun_escenas as C  # noqa: E402

SRC = os.path.join(BASE, "original", "escena1_original.mp4")
FPS = 25

# --- banner
BANNER_START = 1.0      # segundo del video en que aparece
BANNER_DUR = 7.5        # cuánto dura en pantalla (incluye entrada y salida)
BANNER_Y = 780
BANNER_SIDE = "left"
LINE1 = "ESCENA 1"
LINE2 = "La revelación"

# --- audio
KIDS = (43.75, 60.5)    # parte en que hablan los niños (los bordes caen en silencio)
KIDS_VS_NARRATOR_DB = 1.0   # los niños quedan 1 dB por encima del narrador


def process_audio(src, tmp):
    raw = C.decode_audio(src, os.path.join(tmp, "raw.wav"))
    a, b = KIDS
    narr = C.loudness(raw, 14.0, 42.5)

    # 1) voz de los niños limpia y ecualizada, llevada al nivel del narrador y
    #    con un compresor que empareja sílabas y a los dos niños entre sí
    kids0 = os.path.join(tmp, "kids0.wav")
    C.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", raw,
           "-af", C.KIDS_CHAIN, "-c:a", "pcm_f32le", kids0])
    g1 = narr - C.loudness(kids0)
    kids1 = os.path.join(tmp, "kids1.wav")
    C.run(["ffmpeg", "-v", "error", "-y", "-i", kids0, "-af",
           f"volume={g1:.2f}dB,"
           f"agate=threshold=0.01:ratio=2:range=0.2:attack=10:release=250,"   # baja el ruido entre palabras
           f"acompressor=threshold=-22dB:ratio=3:attack=6:release=180:knee=6",
           "-c:a", "pcm_f32le", kids1])
    # 2) la compresión les quita volumen: se vuelve a igualar con el narrador
    g2 = narr + KIDS_VS_NARRATOR_DB - C.loudness(kids1)
    print(f"  narrador {narr:.1f} LUFS · niños antes {C.loudness(raw, a, b):.1f} LUFS · "
          f"ganancia total +{g1 + g2:.1f} dB")

    # 3) unir las tres partes; luego compresión suave para todo y -16 LUFS
    mixed = os.path.join(tmp, "mixed.wav")
    fc = (f"[0:a]highpass=f=60,asplit=2[x1][x3];"
          f"[x1]atrim=0:{a},asetpts=N/SR/TB[p1];"
          f"[1:a]volume={g2:.2f}dB[p2];"
          f"[x3]atrim={b},asetpts=N/SR/TB[p3];"
          f"[p1][p2][p3]concat=n=3:v=0:a=1[out]")
    C.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-i", kids1, "-filter_complex", fc, "-map", "[out]",
           "-c:a", "pcm_f32le", mixed])
    final = C.glue_and_normalize(mixed, tmp)
    for name, (s, e) in (("música", (0, 13.5)), ("narrador", (14, 42.5)), ("niños", KIDS), ("narrador 2", (61, 76.4))):
        print(f"  {name:10s} {C.loudness(final, s, e):6.1f} LUFS")
    return final


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "escena1_la_revelacion.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena1_", dir=os.environ.get("TMPDIR"))
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
