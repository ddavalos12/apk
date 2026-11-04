#!/usr/bin/env python3
"""
Escena 5: "El templo de Dagón" (Jueces 16:23-30) - Escuela Dominical "Monte de Horeb"

Los filisteos celebran en el templo y traen a Sansón encadenado para burlarse
de él.  Sansón ora, se apoya en las columnas y derriba el templo.

A partir del video original (1280x720, 30 fps):
  1. Pone el banner "Escena 5 · El templo de Dagón" al inicio, abajo a la derecha.
  2. Sube los tramos de voces bajas y baja la parte de la segunda cámara, que
     sonaba más fuerte que el resto.
  3. Efectos de sonido originales para el derrumbe: retumbe de terremoto,
     crujidos de piedra, columnas que caen, estruendo y escombros.
  4. Equilibra los canales y nivela todo el audio (compresión suave y -16 LUFS).
  5. Mejora la imagen a 1920x1080 (CRF 20, para quedar debajo de 100 MB).

Uso:
    python3 editar_escena5.py [salida.mp4]
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

SRC = os.path.join(BASE, "original", "escena5_original.mp4")
FPS = 30
CRF = 20

# --- banner (más abajo de lo normal: así tapa pies y piso, no a los niños)
BANNER_START = 1.0
BANNER_DUR = 7.5
BANNER_Y = 830
BANNER_SIDE = "right"
LINE1 = "ESCENA 5"
LINE2 = "El templo de Dagón"

# --- audio
# (inicio, fin, ganancia máxima en dB, reducción de ruido en dB, nombre[, filtro])
KIDS = [
    (34.00, 36.65, 18.0, 10, "traen a Sansón"),
    (43.30, 56.10, 0.0, 6, "segunda cámara (más fuerte)", "highpass=f=60"),
    (61.00, 69.40, 8.0, 8, "se burlan de Sansón"),
]
KIDS_VS_REST_DB = 0.0

# --- momentos del derrumbe (segundos del video, vistos cuadro por cuadro)
T_GRIP = 95.8        # Sansón se apoya en las columnas: empieza el retumbe
CRACKS = [(96.6, 0.5), (97.3, 0.6), (97.8, 0.7), (98.2, 0.85), (98.45, 0.9), (98.55, 1.0)]
T_FALL = 98.6        # la primera columna se inclina: silbido de la caída
T_IMPACT = 99.1      # los bloques golpean el piso
IMPACTS = [(99.1, 1.0), (99.3, 0.6), (99.6, 0.5), (100.0, 0.45), (100.45, 0.35)]
T_END = 102.6        # termina el polvo

# el audio original ya es muy fuerte aquí (gritos de los niños): se baja un poco
# para que el derrumbe se oiga encima, sin taparlos
DUCK = [(96.9, 98.9, -3.0, 0.4), (98.9, 101.8, -7.0, 0.25)]


# ----------------------------------------------------------------------------
# Efectos de sonido (sintetizados; sin derechos de autor)
# ----------------------------------------------------------------------------

SR = C.SR
rng = np.random.default_rng(1630)


def band(x, lo, hi):
    """Filtro pasa-banda por FFT (x: (n,) o (n, 2))."""
    n = len(x)
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = ((f >= lo) & (f <= hi)).astype(np.float32)
    # bordes suaves para que no suene metálico
    g = np.convolve(g, np.hanning(41) / np.hanning(41).sum(), mode="same")
    if x.ndim == 2:
        g = g[:, None]
    return np.fft.irfft(X * g, n, axis=0).astype(np.float32)


def pan(mono, p):
    """p de -1 (izquierda) a 1 (derecha)."""
    a = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)], axis=1)


def place(out, sig, t0):
    i0 = int(t0 * SR)
    k = min(len(sig), len(out) - i0)
    if k > 0:
        out[i0:i0 + k] += sig[:k]


def rumble(t0, t_peak, t_end):
    n = int((t_end - t0) * SR)
    t = np.arange(n) / SR
    low = band(rng.standard_normal((n, 2)).astype(np.float32), 28, 140)
    grind = band(rng.standard_normal((n, 2)).astype(np.float32), 150, 650)
    rise = np.clip(t / (t_peak - t0), 0, 1) ** 1.6
    fall = np.where(t > (t_peak - t0), np.exp(-(t - (t_peak - t0)) / 1.3), 1.0)
    env = rise * fall
    # temblor: modulación que se acelera
    fr = 3.5 + 5.5 * np.clip(t / (t_peak - t0), 0, 1)
    trem = 1 + 0.45 * np.sin(2 * np.pi * np.cumsum(fr) / SR)
    wob = band(rng.standard_normal(n).astype(np.float32), 0.5, 6)
    wob = 1 + 0.6 * wob / (np.abs(wob).max() + 1e-9)
    low *= (env * trem * wob)[:, None] / (np.abs(low).max() + 1e-9)
    grind *= (env ** 1.5 * (1 + 0.5 * np.sin(2 * np.pi * 11 * t)))[:, None] / (np.abs(grind).max() + 1e-9)
    return low * 0.55 + grind * 0.12


def crack(size):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    snap = band(rng.standard_normal(n).astype(np.float32), 900, 9000) * np.exp(-t / 0.010)
    crunch = np.zeros(n, np.float32)
    for _ in range(int(25 * size) + 8):
        i = int(rng.exponential(0.06) * SR)
        if i < n - 200:
            crunch[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 30) * rng.uniform(0.2, 1)
    crunch = band(crunch, 1500, 8000) * np.exp(-t / 0.12)
    f0 = rng.uniform(170, 320)
    body = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.05)
    sig = snap * 1.0 + crunch * 0.5 + body * 0.35
    sig /= np.abs(sig).max() + 1e-9
    return pan(sig * size, rng.uniform(-0.6, 0.6))


def whoosh(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    lo = band(rng.standard_normal(n).astype(np.float32), 200, 900)
    hi = band(rng.standard_normal(n).astype(np.float32), 900, 3500)
    k = t / dur
    sig = lo * k + hi * (1 - k) * 0.6          # el tono baja mientras cae
    sig *= np.sin(np.pi * np.clip(k * 0.9, 0, 1)) ** 2
    sig /= np.abs(sig).max() + 1e-9
    return np.stack([sig, np.roll(sig, 240)], axis=1)


def impact(size):
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t / 0.12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    thump = np.sin(2 * np.pi * 52 * t) * np.exp(-t / 0.18)
    burst = band(rng.standard_normal(n).astype(np.float32), 80, 4000) * np.exp(-t / 0.22)
    snap = band(rng.standard_normal(n).astype(np.float32), 2000, 10000) * np.exp(-t / 0.025)
    sig = boom * 0.9 + thump * 0.6 + burst * 0.7 + snap * 0.35
    sig /= np.abs(sig).max() + 1e-9
    return pan(sig * size, rng.uniform(-0.4, 0.4))


def debris(dur):
    """Escombros: muchos golpecitos y trozos que caen, cada vez menos."""
    n = int(dur * SR)
    out = np.zeros((n, 2), np.float32)
    tt = 0.0
    while tt < dur:
        rate = 60 * np.exp(-tt / 0.7) + 4
        tt += rng.exponential(1 / rate)
        if tt >= dur:
            break
        ln = int(rng.uniform(0.004, 0.03) * SR)
        g = rng.standard_normal(ln).astype(np.float32) * np.exp(-np.arange(ln) / (ln / 4))
        amp = np.exp(-tt / 0.9) * rng.uniform(0.2, 1.0)
        place(out, pan(g * amp, rng.uniform(-0.9, 0.9)), tt)
    out = band(out, 300, 7000)
    for _ in range(9):   # trozos grandes
        tt = rng.uniform(0.0, 1.4)
        ln = int(0.35 * SR)
        ti = np.arange(ln) / SR
        th = np.sin(2 * np.pi * rng.uniform(70, 180) * ti) * np.exp(-ti / 0.07) * np.exp(-tt / 0.9)
        place(out, pan(th.astype(np.float32) * 0.8, rng.uniform(-0.7, 0.7)), tt)
    out /= np.abs(out).max() + 1e-9
    return out


def reverb(x, secs=1.1, wet=0.28):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = np.stack([band(rng.standard_normal(n).astype(np.float32), 100, 6000) * np.exp(-t * 6.9 / secs)
                   for _ in range(2)], axis=1)
    ir /= np.sqrt((ir ** 2).sum(0))[None, :]
    m = len(x) + n - 1
    nfft = 1 << (m - 1).bit_length()
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[:len(x)]
                  for c in range(2)], axis=1)
    return (x + y * wet).astype(np.float32)


def rms_db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def at_rms(x, target_db, a=0, b=None):
    """Escala x para que su nivel (RMS) entre las muestras a y b sea target_db."""
    return x * np.float32(10 ** ((target_db - rms_db(x[a:b])) / 20))


def collapse_sfx(n_samples):
    """Todos los efectos del derrumbe, alineados con el video.
    Niveles pensados para sonar por encima del audio original de ese momento
    (≈ -12 dB RMS, con gritos de los niños)."""
    out = np.zeros((n_samples, 2), np.float32)
    r = rumble(T_GRIP, T_IMPACT, T_END)
    i_peak = int((T_IMPACT - T_GRIP) * SR)
    place(out, at_rms(r, -14.0, i_peak - int(0.8 * SR), i_peak), T_GRIP)       # retumbe que crece
    for t0, size in CRACKS:                                                     # crujidos de piedra
        c = crack(1.0)
        place(out, c * np.float32(10 ** (-4 / 20) * size / (np.abs(c).max() + 1e-9)), t0)
    w = whoosh(T_IMPACT - T_FALL + 0.05)
    place(out, at_rms(w, -20.0), T_FALL)                                        # columnas cayendo
    for t0, size in IMPACTS:                                                    # golpes contra el piso
        im = impact(1.0)
        place(out, at_rms(im, -5.0, 0, int(0.4 * SR)) * np.float32(size), t0)
    d = debris(T_END - T_IMPACT)
    place(out, at_rms(d, -16.0, 0, SR), T_IMPACT + 0.05)                       # escombros y polvo
    return reverb(out)


# ----------------------------------------------------------------------------

def process_audio(src, tmp):
    n = int(round(float(C.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                              capture_output=True, text=True).stdout) * SR)) + SR
    sfx = collapse_sfx(n)
    return C.boost_regions(src, tmp, KIDS, KIDS_VS_REST_DB, sfx=sfx, duck=DUCK)


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "escena5_el_templo_de_dagon.mp4"))
    tmp = tempfile.mkdtemp(prefix="escena5_", dir=os.environ.get("TMPDIR"))
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
