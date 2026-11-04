#!/usr/bin/env python3
"""
Intro horizontal (1920x1080, 30 fps, ~59 s) - "Sansón y Dalila"
Escuela Dominical - Iglesia Evangélica Metodista "Monte de Horeb"

Genera:
  - música original sintetizada (sin derechos de autor)
  - animación con efecto Ken Burns, textos, partículas y transiciones
y lo une todo en un MP4 compatible con el video principal (H.264 + AAC 44.1 kHz).

Uso:
    python3 generar_intro.py [salida.mp4]
Requisitos: Python 3, numpy, Pillow, ffmpeg.
"""
import math
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "img")
FONTS = os.path.join(BASE, "assets", "fonts")

W, H = 1920, 1080
FPS = 30
DURATION = 59.0
NFRAMES = int(round(DURATION * FPS))
SR = 44100

# ----------------------------------------------------------------------------
# Línea de tiempo (segundos).  Cada escena se cruza 0.8 s con la siguiente.
# ----------------------------------------------------------------------------
SCENES = [
    ("iglesia",   0.0,  6.4),
    ("escuela",   5.6, 11.4),
    ("titulo",   10.6, 17.4),
    ("nazareo",  16.6, 22.4),
    ("dalila",   21.6, 27.4),
    ("insistio", 26.6, 32.4),
    ("versiculo", 31.6, 43.4),
    ("rapado",   42.6, 48.4),
    ("clamo",    47.6, 53.9),
    ("cierre",   53.1, DURATION),
]
T_TITLE_HIT = 12.6     # aparece "y Dalila"
T_CLAMO_HIT = 48.0     # vuelve la fuerza
T_CIERRE = 53.1

# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------

def clamp01(x):
    return max(0.0, min(1.0, x))


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


F_CAPS = "Cinzel-SemiBold.ttf"
F_CAPS_BOLD = "Cinzel-ExtraBold.ttf"
F_SERIF = "Cormorant-SemiBold.ttf"
F_ITALIC = "Cormorant-SemiBoldItalic.ttf"
F_ITALIC_M = "Cormorant-MediumItalic.ttf"

GOLD_TOP = (255, 236, 176)
GOLD_BOT = (205, 148, 52)
CREAM = (250, 242, 222)


# ----------------------------------------------------------------------------
# Imágenes
# ----------------------------------------------------------------------------

def grade(img, warmth=1.0, contrast=1.08, sat=1.05, bright=1.0):
    """Corrección de color cálida y cinematográfica."""
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Brightness(img).enhance(bright)
    a = np.asarray(img).astype(np.float32) / 255.0
    a[..., 0] *= 1.0 + 0.05 * warmth
    a[..., 1] *= 1.0 + 0.01 * warmth
    a[..., 2] *= 1.0 - 0.07 * warmth
    a = a * 0.96 + 0.025 * np.array([1.0, 0.85, 0.6], np.float32)  # sombras cálidas
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def load(name, **kw):
    return grade(Image.open(os.path.join(IMG, name)).convert("RGB"), **kw)


def kenburns(src, t, r0, r1):
    """r = (cx, cy, ancho) en píxeles de la imagen fuente; alto = ancho*9/16."""
    e = ease_in_out(t)
    cx = r0[0] + (r1[0] - r0[0]) * e
    cy = r0[1] + (r1[1] - r0[1]) * e
    w = r0[2] + (r1[2] - r0[2]) * e
    h = w * H / W
    s = w / W
    out = src.transform((W, H), Image.AFFINE, (s, 0, cx - w / 2, 0, s, cy - h / 2),
                        resample=Image.BICUBIC)
    return np.asarray(out).astype(np.float32) / 255.0


def cover(img, blur=0, scale=1.12):
    """Imagen que cubre todo el cuadro (para fondos difuminados)."""
    iw, ih = img.size
    s = max(W / iw, H / ih) * scale
    im = img.resize((int(iw * s), int(ih * s)), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


def framed_photo(img, height, border=6, radius=18):
    """Foto vertical con borde dorado fino, esquinas redondeadas y sombra."""
    iw, ih = img.size
    w = int(iw * height / ih)
    ph = img.resize((w, height), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (w, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, height - 1), radius, fill=255)
    ph.putalpha(mask)
    pad = 60
    canvas = Image.new("RGBA", (w + 2 * pad, height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 14, pad + w, pad + height + 14), radius, fill=190)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    canvas.paste((0, 0, 0, 255), (0, 0), sh)
    gold = Image.new("RGBA", (w + 2 * border, height + 2 * border), (0, 0, 0, 0))
    ImageDraw.Draw(gold).rounded_rectangle((0, 0, w + 2 * border - 1, height + 2 * border - 1),
                                           radius + border, fill=(222, 178, 92, 255))
    canvas.alpha_composite(gold, (pad - border, pad - border))
    canvas.alpha_composite(ph, (pad, pad))
    return to_layer(canvas)


def feathered(img, size, feather=60):
    """Imagen con bordes desvanecidos (sin marco)."""
    im = img.resize(size, Image.LANCZOS).convert("RGBA")
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rectangle((feather, feather // 2, size[0] - feather, size[1] - feather // 2), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather / 2.2))
    im.putalpha(m)
    return to_layer(im)


# ----------------------------------------------------------------------------
# Capas (RGBA en float32, alfa premultiplicado)
# ----------------------------------------------------------------------------

def to_layer(im):
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255.0
    rgb = a[..., :3] * a[..., 3:4]
    return rgb, a[..., 3:4]


def blend(frame, layer, x, y, opacity=1.0, scale=None):
    if opacity <= 0.002:
        return
    rgb, al = layer
    lh, lw = al.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + lw), min(H, y + lh)
    if x0 >= x1 or y0 >= y1:
        return
    sr = rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    sa = al[y0 - y:y1 - y, x0 - x:x1 - x] * opacity
    dst = frame[y0:y1, x0:x1]
    dst *= (1.0 - sa)
    dst += sr * opacity


# ----------------------------------------------------------------------------
# Texto
# ----------------------------------------------------------------------------

def _draw_line(draw, xy, text, fnt, tracking, fill):
    x, y = xy
    if tracking == 0:
        draw.text((x, y), text, font=fnt, fill=fill)
        return
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + tracking


def _line_width(text, fnt, tracking):
    if tracking == 0:
        return fnt.getlength(text)
    return sum(fnt.getlength(c) for c in text) + tracking * (len(text) - 1)


def text_layer(lines, align="center", gold=False, shadow=0.75, glow=0.0, line_gap=1.18, scrim=0.0):
    """lines: lista de (texto, fuente, tamaño, tracking, color|None).
    color None => degradado dorado."""
    fonts = [font(f, s) for _, f, s, _, _ in lines]
    widths = [_line_width(t, fn, tr) for (t, _, _, tr, _), fn in zip(lines, fonts)]
    heights = [int(s * line_gap) for _, _, s, _, _ in lines]
    pad = 140 if scrim else 70
    lw = int(max(widths)) + 2 * pad
    lh = sum(heights) + 2 * pad
    mask_gold = Image.new("L", (lw, lh), 0)
    col = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    dg, dc = ImageDraw.Draw(mask_gold), ImageDraw.Draw(col)
    y = pad
    for (t, _, s, tr, c), fn, wdt, hh in zip(lines, fonts, widths, heights):
        if align == "center":
            x = (lw - wdt) / 2
        elif align == "left":
            x = pad
        else:
            x = lw - pad - wdt
        if c is None:
            _draw_line(dg, (x, y), t, fn, tr, 255)
        else:
            _draw_line(dc, (x, y), t, fn, tr, tuple(c) + (255,))
        y += hh
    # degradado dorado vertical, por línea
    grad = np.zeros((lh, lw, 3), np.float32)
    y = pad
    for (_, _, s, _, _), hh in zip(lines, heights):
        yy = np.arange(hh)[:, None]
        k = np.clip((yy - hh * 0.08) / (s * 1.0), 0, 1)
        top, bot = np.array(GOLD_TOP, np.float32), np.array(GOLD_BOT, np.float32)
        g = top * (1 - k[..., None]) + bot * k[..., None]
        grad[y:y + hh] = g / 255.0
        y += hh
    grad[y:] = np.array(GOLD_BOT, np.float32) / 255.0
    ga = np.asarray(mask_gold).astype(np.float32)[..., None] / 255.0
    ca = np.asarray(col).astype(np.float32) / 255.0
    rgb = grad * ga + ca[..., :3] * ca[..., 3:4]
    alpha = np.clip(ga + ca[..., 3:4], 0, 1)
    rgb = rgb / np.maximum(alpha, 1e-4)  # des-premultiplicar
    a_img = Image.fromarray((alpha[..., 0] * 255).astype(np.uint8))
    out = np.zeros((lh, lw, 4), np.float32)
    # sombra suave
    if shadow > 0:
        sh = np.asarray(a_img.filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 255.0
        sh = np.roll(sh, 5, axis=0) * shadow
        sh2 = np.asarray(a_img.filter(ImageFilter.GaussianBlur(28))).astype(np.float32) / 255.0 * shadow * 0.6
        sh = np.clip(sh + sh2, 0, 1)
        if scrim > 0:  # sombra amplia y difusa detrás del texto (legibilidad)
            sc = np.asarray(a_img.filter(ImageFilter.GaussianBlur(26))).astype(np.float32) / 255.0
            sc = Image.fromarray((np.clip(sc * 3.0, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(48))
            sc = np.asarray(sc).astype(np.float32) / 255.0
            sh = np.clip(sh + sc * scrim, 0, 1)
        out[..., 3] = sh
    if glow > 0:
        gl = np.asarray(a_img.filter(ImageFilter.GaussianBlur(18))).astype(np.float32) / 255.0 * glow
        gcol = np.array([1.0, 0.82, 0.45], np.float32)
        # glow cálido sobre la sombra
        out_rgb = gcol * gl[..., None]
        out[..., :3] = out_rgb  # premultiplicado
        out[..., 3] = np.clip(out[..., 3] + gl, 0, 1)
    prem = out[..., :3]
    a0 = out[..., 3:4]
    prem = prem * (1 - alpha) + rgb * alpha
    a_tot = a0 * (1 - alpha) + alpha
    return prem.astype(np.float32), a_tot.astype(np.float32)


class Txt:
    """Texto animado: aparece con fundido + leve subida."""

    def __init__(self, layer, cx, cy, t_in, t_out, rise=22, fade=0.7, anchor="center"):
        self.layer, self.cx, self.cy = layer, cx, cy
        self.t_in, self.t_out, self.rise, self.fade = t_in, t_out, rise, fade
        self.anchor = anchor

    def draw(self, frame, t):
        a_in = ease_out((t - self.t_in) / self.fade)
        a_out = 1 - smooth((t - (self.t_out - 1.3)) / 0.5)
        op = a_in * a_out
        if op <= 0.002:
            return
        lh, lw = self.layer[1].shape[:2]
        dy = (1 - a_in) * self.rise
        if self.anchor == "center":
            x = self.cx - lw / 2
        elif self.anchor == "left":
            x = self.cx - 70
        else:
            x = self.cx - lw + 70
        blend(frame, self.layer, x, self.cy - lh / 2 + dy, op)


def ornament(width=420, color=(226, 182, 96)):
    """Separador decorativo: línea — rombo — línea."""
    h = 40
    im = Image.new("RGBA", (width + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = (width + 40) // 2, (h + 40) // 2
    d.line((20, cy, cx - 22, cy), fill=color + (255,), width=3)
    d.line((cx + 22, cy, width + 20, cy), fill=color + (255,), width=3)
    d.polygon([(cx, cy - 11), (cx + 11, cy), (cx, cy + 11), (cx - 11, cy)], fill=color + (255,))
    d.ellipse((cx - 32, cy - 4, cx - 24, cy + 4), fill=color + (255,))
    d.ellipse((cx + 24, cy - 4, cx + 32, cy + 4), fill=color + (255,))
    return to_layer(im)


# ----------------------------------------------------------------------------
# Efectos globales
# ----------------------------------------------------------------------------

def make_vignette(strength=0.55):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r = np.sqrt(nx ** 2 * 0.8 + ny ** 2)
    v = 1 - strength * np.clip((r - 0.55) / 0.9, 0, 1) ** 1.6
    return v[..., None].astype(np.float32)


def gradient_v(top_alpha, bottom_alpha, start=0.0):
    """Capa oscura vertical (multiplicativa) para legibilidad del texto."""
    y = np.linspace(0, 1, H, dtype=np.float32)
    k = np.clip((y - start) / max(1e-3, 1 - start), 0, 1)
    a = top_alpha + (bottom_alpha - top_alpha) * k
    return (1 - a)[:, None, None]


class Particles:
    def __init__(self, n=70, seed=7):
        rng = np.random.default_rng(seed)
        self.x = rng.uniform(0, W, n)
        self.y = rng.uniform(0, H, n)
        self.v = rng.uniform(12, 45, n)
        self.amp = rng.uniform(10, 40, n)
        self.ph = rng.uniform(0, 2 * np.pi, n)
        self.fr = rng.uniform(0.1, 0.35, n)
        self.size = rng.choice([3, 4, 6, 9, 14], n, p=[0.3, 0.3, 0.2, 0.13, 0.07])
        self.bri = rng.uniform(0.25, 0.9, n)
        self.tw = rng.uniform(0.5, 1.6, n)
        self.sprites = {}
        for s in set(self.size.tolist()):
            r = s * 2.2
            n2 = int(r * 2 + 1)
            yy, xx = np.mgrid[0:n2, 0:n2].astype(np.float32) - r
            g = np.exp(-(xx ** 2 + yy ** 2) / (2 * (s * 0.55) ** 2))
            if s >= 9:  # bokeh: disco suave
                d = np.sqrt(xx ** 2 + yy ** 2)
                g = np.clip((s - d) / 2.0, 0, 1) * 0.55 + g * 0.45
            self.sprites[s] = g.astype(np.float32)
        self.col = np.array([1.0, 0.84, 0.52], np.float32)

    def draw(self, frame, t, intensity):
        if intensity <= 0.01:
            return
        for i in range(len(self.x)):
            s = int(self.size[i])
            spr = self.sprites[s]
            n2 = spr.shape[0]
            px = (self.x[i] + self.amp[i] * math.sin(self.fr[i] * t * 2 * math.pi + self.ph[i])) % (W + 60) - 30
            py = (self.y[i] - self.v[i] * t) % (H + 60) - 30
            b = self.bri[i] * (0.6 + 0.4 * math.sin(self.tw[i] * t * 2 * math.pi + self.ph[i])) * intensity
            x0, y0 = int(px - n2 / 2), int(py - n2 / 2)
            xa, ya = max(0, x0), max(0, y0)
            xb, yb = min(W, x0 + n2), min(H, y0 + n2)
            if xa >= xb or ya >= yb:
                continue
            g = spr[ya - y0:yb - y0, xa - x0:xb - x0, None] * (b * 0.55)
            frame[ya:yb, xa:xb] += g * self.col


# ----------------------------------------------------------------------------
# Escenas
# ----------------------------------------------------------------------------

class Assets:
    def __init__(self):
        self.puerta = load("1_puerta.jpg", contrast=1.06)
        self.escuela = load("2_escuela_dominical.jpg", warmth=0.6, sat=1.08)
        self.iglesia = load("3_iglesia.jpg", warmth=0.7, contrast=1.05)
        self.escenario = load("4_escenario.jpg", warmth=1.0, contrast=1.1)
        self.letras = load("5_letras_sanson.jpg", warmth=0.3, contrast=1.1, sat=1.1)
        self.letras_crop = self.letras.crop((40, 50, 1240, 440))
        self.escenario_soft = self.escenario.filter(ImageFilter.GaussianBlur(2.6))
        self.escenario_rays = self.escenario.filter(ImageFilter.GaussianBlur(1.4))

        self.vignette = make_vignette()
        self.particles = Particles()
        self.dark_low = gradient_v(0.05, 0.72, 0.35)
        self.dark_mid = gradient_v(0.35, 0.65, 0.0)

        # fondos difuminados
        def bg(img, blur, dark):
            im = cover(img, blur=blur, scale=1.15)
            a = np.asarray(im).astype(np.float32) / 255.0 * dark
            return Image.fromarray((a * 255).astype(np.uint8))

        self.bg_escuela = bg(self.escuela, 40, 0.42)
        self.bg_puerta = bg(self.puerta, 40, 0.40)
        self.bg_letras = bg(self.letras, 34, 0.30)
        self.bg_verso = bg(self.escenario, 28, 0.30)

        self.photo_escuela = framed_photo(self.escuela, 900)
        self.photo_puerta = framed_photo(self.puerta, 900)
        self.letras_layer = feathered(self.letras_crop, (1560, 507), feather=70)

        # rayos de luz (precálculo del ángulo)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.ray_ang = np.arctan2(xx - W / 2, yy + 260).astype(np.float32)
        dist = np.sqrt((xx - W / 2) ** 2 + (yy + 260) ** 2)
        self.ray_fall = (np.clip(1 - dist / 1500, 0, 1) ** 1.5).astype(np.float32)

        self.build_texts()

    # ---------------------------------------------------------------- textos
    def build_texts(self):
        G = None  # dorado
        S = SCENES_D

        self.t_iglesia = [
            Txt(text_layer([("IGLESIA EVANGÉLICA METODISTA", F_CAPS, 40, 7, CREAM)], scrim=0.5),
                W / 2, 780, 1.2, S["iglesia"][1]),
            Txt(text_layer([("Monte de Horeb", F_ITALIC, 128, 0, G)], glow=0.25, scrim=0.55),
                W / 2, 880, 1.7, S["iglesia"][1]),
        ]
        e0, e1 = S["escuela"]
        self.t_escuela = [
            Txt(text_layer([("ESCUELA DOMINICAL", F_CAPS, 60, 6, G)], glow=0.2), 1265, 395, e0 + 0.9, e1),
            Txt(ornament(460), 1265, 470, e0 + 1.3, e1, rise=0),
            Txt(text_layer([("presenta", F_ITALIC, 104, 0, CREAM)]), 1265, 560, e0 + 1.6, e1),
            Txt(text_layer([("una historia de fe, fuerza", F_SERIF, 50, 0, CREAM),
                            ("y obediencia a Dios", F_SERIF, 50, 0, CREAM)]), 1265, 710, e0 + 2.2, e1),
        ]
        c0, c1 = S["titulo"]
        self.t_titulo = [
            Txt(text_layer([("LA HISTORIA DE", F_CAPS, 50, 12, CREAM)]), W / 2, 150, c0 + 0.8, c1),
            Txt(text_layer([("y Dalila", F_ITALIC, 150, 0, G)], glow=0.45), W / 2, 870, T_TITLE_HIT, c1, rise=0),
            Txt(text_layer([("JUECES 13 – 16", F_CAPS, 34, 9, (236, 214, 170))]), W / 2, 990, T_TITLE_HIT + 0.9, c1),
        ]
        n0, n1 = S["nazareo"]
        self.t_nazareo = [
            Txt(text_layer([("Desde el vientre de su madre,", F_ITALIC, 76, 0, CREAM),
                            ("Sansón fue apartado como", F_ITALIC, 76, 0, CREAM),
                            ("nazareo de Dios", F_ITALIC, 86, 0, G)], glow=0.15, scrim=0.62), W / 2, 760, n0 + 0.9, n1),
            Txt(text_layer([("JUECES 13:5", F_CAPS, 30, 8, (232, 210, 165))], scrim=0.5), W / 2, 1000, n0 + 1.8, n1),
        ]
        d0, d1 = S["dalila"]
        self.t_dalila = [
            Txt(text_layer([("Pero Sansón amó", F_ITALIC, 82, 0, CREAM),
                            ("a una mujer llamada", F_ITALIC, 82, 0, CREAM),
                            ("Dalila", F_ITALIC, 120, 0, G)], align="center", glow=0.2), 640, 430, d0 + 0.9, d1),
            Txt(text_layer([("Los filisteos le ofrecieron plata", F_SERIF, 46, 0, (238, 228, 205)),
                            ("por el secreto de su fuerza.", F_SERIF, 46, 0, (238, 228, 205))]),
                640, 770, d0 + 1.7, d1),
            Txt(text_layer([("JUECES 16:4-5", F_CAPS, 30, 8, (232, 210, 165))]), 640, 905, d0 + 2.1, d1),
        ]
        i0, i1 = S["insistio"]
        self.t_insistio = [
            Txt(text_layer([("Tanto le insistió, cada día,", F_ITALIC, 76, 0, CREAM),
                            ("que él le descubrió", F_ITALIC, 76, 0, CREAM),
                            ("todo su corazón…", F_ITALIC, 90, 0, G)], glow=0.15, scrim=0.62), W / 2, 740, i0 + 0.9, i1),
            Txt(text_layer([("JUECES 16:16-17", F_CAPS, 30, 8, (232, 210, 165))], scrim=0.5), W / 2, 990, i0 + 1.8, i1),
        ]
        v0, v1 = S["versiculo"]
        verse = [
            ("“Y él le dijo: Nunca a mi cabeza llegó navaja;", CREAM),
            ("porque soy nazareo de Dios", CREAM),
            ("desde el vientre de mi madre.", CREAM),
            ("Si fuere rapado, mi fuerza se apartará de mí,", None),
            ("y seré debilitado y como todos los hombres.”", None),
        ]
        self.t_verso = []
        y = 320
        for k, (line, colr) in enumerate(verse):
            self.t_verso.append(Txt(text_layer([(line, F_ITALIC, 70, 0, colr)], glow=0.18 if colr is None else 0),
                                    W / 2, y, v0 + 0.9 + k * 0.85, v1, rise=16, fade=0.9))
            y += 98
        self.t_verso.append(Txt(ornament(360), W / 2, y + 22, v0 + 5.4, v1, rise=0))
        self.t_verso.append(Txt(text_layer([("JUECES 16:17 · REINA-VALERA 1960", F_CAPS, 34, 7, (236, 214, 170))]),
                                W / 2, y + 95, v0 + 5.8, v1))
        r0, r1 = S["rapado"]
        self.t_rapado = [
            Txt(text_layer([("Mientras dormía, le raparon", F_ITALIC, 76, 0, CREAM),
                            ("las siete guedejas de su cabeza…", F_ITALIC, 76, 0, CREAM)], scrim=0.35), W / 2, 690, r0 + 0.9, r1),
            Txt(text_layer([("y su fuerza se apartó de él.", F_ITALIC, 84, 0, (210, 214, 222))]),
                W / 2, 875, r0 + 2.2, r1),
            Txt(text_layer([("JUECES 16:19", F_CAPS, 30, 8, (205, 205, 210))]), W / 2, 1000, r0 + 2.8, r1),
        ]
        k0, k1 = S["clamo"]
        self.t_clamo = [
            Txt(text_layer([("Pero clamó a Jehová:", F_ITALIC, 74, 0, CREAM)], scrim=0.6), W / 2, 600, k0 + 0.5, k1),
            Txt(text_layer([("«Acuérdate ahora de mí, y fortaléceme,", F_ITALIC, 76, 0, G),
                            ("te ruego, solamente esta vez»", F_ITALIC, 76, 0, G)], glow=0.3, scrim=0.62), W / 2, 790, k0 + 1.2, k1),
            Txt(text_layer([("JUECES 16:28", F_CAPS, 30, 8, (236, 214, 170))], scrim=0.5), W / 2, 975, k0 + 1.9, k1),
        ]
        f0, f1 = S["cierre"]
        self.t_cierre = [
            Txt(text_layer([("Nuestra fuerza viene de Dios", F_ITALIC, 118, 0, G)], glow=0.35, scrim=0.55), W / 2, 760, f0 + 1.0, f1 + 5),
            Txt(ornament(520), W / 2, 862, f0 + 1.8, f1 + 5, rise=0),
            Txt(text_layer([("ESCUELA DOMINICAL · MONTE DE HOREB", F_CAPS, 40, 7, CREAM)]), W / 2, 935, f0 + 2.2, f1 + 5),
            Txt(text_layer([("IGLESIA EVANGÉLICA METODISTA", F_CAPS, 28, 7, (232, 214, 178))]), W / 2, 1000, f0 + 2.7, f1 + 5),
        ]

    # ---------------------------------------------------------------- render
    def scene(self, name, t):
        t0, t1 = SCENES_D[name]
        u = (t - t0) / (t1 - t0)
        fr = getattr(self, "s_" + name)(t, u)
        return fr

    def s_iglesia(self, t, u):
        f = kenburns(self.iglesia, u, (640, 360, 1280), (600, 320, 1030))
        f *= self.dark_low
        f *= gradient_like_bottom(self)
        for x in self.t_iglesia:
            x.draw(f, t)
        return f

    def s_escuela(self, t, u):
        f = kenburns(self.bg_escuela, u, (self.bg_escuela.width / 2, self.bg_escuela.height / 2, 1920),
                     (self.bg_escuela.width / 2, self.bg_escuela.height / 2 - 40, 1800))
        lh, lw = self.photo_escuela[1].shape[:2]
        op = ease_out((t - SCENES_D["escuela"][0] - 0.2) / 0.9)
        blend(f, self.photo_escuela, 470 - lw / 2, H / 2 - lh / 2 + (1 - op) * 40 - 8 * u, op)
        for x in self.t_escuela:
            x.draw(f, t)
        return f

    def s_titulo(self, t, u):
        bw, bh = self.bg_letras.size
        f = kenburns(self.bg_letras, u, (bw / 2, bh / 2, 1920), (bw / 2, bh / 2, 1760))
        # destello cálido al aparecer el título
        lt = t - T_TITLE_HIT
        lh, lw = self.letras_layer[1].shape[:2]
        sc_y = 500 - lh / 2 - 10 * u
        blend(f, self.letras_layer, W / 2 - lw / 2, sc_y, smooth((t - SCENES_D["titulo"][0]) / 0.8))
        if lt > -0.05:
            fl = math.exp(-max(lt, 0) / 0.35) * 0.55
            f += fl * np.array([1.0, 0.85, 0.55], np.float32) * self.ray_fall[..., None] * 0.9
        for x in self.t_titulo:
            x.draw(f, t)
        return f

    def s_nazareo(self, t, u):
        f = kenburns(self.escenario_soft, u, (500, 300, 960), (450, 270, 840))
        f *= self.dark_low
        f *= 0.9
        for x in self.t_nazareo:
            x.draw(f, t)
        return f

    def s_dalila(self, t, u):
        f = kenburns(self.bg_puerta, u, (self.bg_puerta.width / 2, self.bg_puerta.height / 2 + 60, 1920),
                     (self.bg_puerta.width / 2, self.bg_puerta.height / 2 - 20, 1800))
        lh, lw = self.photo_puerta[1].shape[:2]
        op = ease_out((t - SCENES_D["dalila"][0] - 0.2) / 0.9)
        blend(f, self.photo_puerta, 1450 - lw / 2, H / 2 - lh / 2 + (1 - op) * 40 - 8 * u, op)
        for x in self.t_dalila:
            x.draw(f, t)
        return f

    def s_insistio(self, t, u):
        f = kenburns(self.escenario_soft, u, (820, 300, 920), (860, 320, 820))
        f *= self.dark_low
        f *= 0.85
        for x in self.t_insistio:
            x.draw(f, t)
        return f

    def s_versiculo(self, t, u):
        bw, bh = self.bg_verso.size
        f = kenburns(self.bg_verso, u, (bw / 2, bh / 2, 1920), (bw / 2, bh / 2 - 20, 1700))
        # halo dorado central suave
        f += self.ray_fall[..., None] * np.array([0.10, 0.07, 0.03], np.float32) * (0.6 + 0.4 * math.sin(t * 0.9))
        for x in self.t_verso:
            x.draw(f, t)
        return f

    def s_rapado(self, t, u):
        f = kenburns(self.letras, u, (640, 281, 990), (640, 262, 840))
        # la fuerza se va: el color se apaga y la imagen se oscurece
        k = smooth((u - 0.05) / 0.6)
        gray = f @ np.array([0.299, 0.587, 0.114], np.float32)
        gray = gray[..., None] * np.array([0.92, 0.95, 1.02], np.float32)
        f = f * (1 - k) + gray * k
        f *= (1 - 0.45 * k) * 0.62
        f *= self.dark_low
        for x in self.t_rapado:
            x.draw(f, t)
        return f

    def s_clamo(self, t, u):
        f = kenburns(self.escenario_rays, u, (640, 360, 1280), (640, 340, 1080))
        f *= self.dark_mid
        f *= 0.8
        lt = t - T_CLAMO_HIT
        if lt > -0.2:
            grow = smooth((lt + 0.2) / 2.5)
            rays = (0.5 + 0.5 * np.cos(self.ray_ang * 22 + t * 0.35)) ** 6
            rays = rays * self.ray_fall * (0.35 + 0.25 * grow)
            f += rays[..., None] * np.array([1.0, 0.82, 0.45], np.float32) * (0.35 + 0.4 * grow)
            fl = math.exp(-max(lt, 0) / 0.4) * 0.5 * smooth((lt + 0.2) / 0.2)
            f += fl * np.array([1.0, 0.88, 0.6], np.float32) * self.ray_fall[..., None]
        for x in self.t_clamo:
            x.draw(f, t)
        return f

    def s_cierre(self, t, u):
        f = kenburns(self.iglesia, u, (600, 320, 1000), (640, 350, 1240))
        f *= self.dark_low
        f *= gradient_like_bottom(self)
        for x in self.t_cierre:
            x.draw(f, t)
        return f


def gradient_like_bottom(a):
    if not hasattr(a, "_g_cierre"):
        a._g_cierre = gradient_v(0.0, 0.6, 0.45)
    return a._g_cierre


SCENES_D = {n: (a, b) for n, a, b in SCENES}
_A = None


def particle_intensity(t):
    if 42.6 <= t < 47.6:
        return 0.25
    if 47.6 <= t < 53.9:
        return 1.3
    return 0.85


def render_frame(i):
    t = i / FPS
    active = [(n, a, b) for n, a, b in SCENES if a <= t < b]
    frame = None
    for n, a, b in active:
        f = _A.scene(n, t)
        if frame is None:
            frame = f
            continue
        # cruce con la escena anterior
        w = smooth((t - a) / 0.8)
        frame = frame * (1 - w) + f * w
    _A.particles.draw(frame, t, particle_intensity(t))
    frame *= _A.vignette
    fade = smooth(t / 1.0) * (1 - smooth((t - (DURATION - 1.6)) / 1.6))
    frame *= fade
    return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()


def _init():
    global _A
    _A = Assets()


# ----------------------------------------------------------------------------
# Música original (síntesis)
# ----------------------------------------------------------------------------

def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


CH = {
    "Dm": [50, 57, 62, 65, 69], "Bb": [46, 53, 58, 62, 65], "Gm": [43, 50, 55, 58, 62],
    "F": [41, 48, 53, 57, 60], "C": [48, 55, 60, 64, 67], "A": [45, 52, 57, 61, 64],
    "D": [50, 57, 62, 66, 69],
}
ROOT = {"Dm": 38, "Bb": 34, "Gm": 31, "F": 29, "C": 36, "A": 33, "D": 38}

# (inicio, fin, acorde, nivel, brillo)
PROG = [
    (0.0, 6.0, "Dm", 0.55, 2.2), (5.6, 11.0, "Bb", 0.6, 2.5), (10.6, 12.9, "Gm", 0.7, 3.0),
    (12.5, 17.0, "Dm", 0.9, 4.0), (16.6, 22.0, "Bb", 0.75, 3.2), (21.6, 27.0, "F", 0.75, 3.2),
    (26.6, 29.9, "C", 0.8, 3.6), (29.5, 32.3, "A", 0.85, 3.8), (31.9, 37.9, "Dm", 0.65, 2.6),
    (37.5, 43.0, "Bb", 0.65, 2.6), (42.6, 45.9, "Gm", 0.42, 1.4), (45.5, 48.2, "A", 0.5, 1.6),
    (47.8, 50.9, "Bb", 1.0, 4.5), (50.5, 53.4, "C", 1.0, 4.8), (53.0, 55.9, "F", 0.95, 4.2),
    (55.5, 60.0, "D", 0.9, 4.0),
]


def env_seg(n, a, r):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    if nr:
        e[-nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
    return e


def pad_voice(freq, n, bright, rng):
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros((n, 2), np.float32)
    for det, pan in ((-6, 0.15), (0, 0.5), (6, 0.85)):
        f = freq * 2 ** (det / 1200)
        vib = 1 + 0.0025 * np.sin(2 * np.pi * (4.8 + rng.uniform(-0.5, 0.5)) * t + rng.uniform(0, 6.28))
        phase = 2 * np.pi * np.cumsum(f * vib) / SR
        sig = np.zeros(n, np.float32)
        for k in range(1, 14):
            if f * k > 9000:
                break
            sig += np.sin(k * phase + rng.uniform(0, 6.28)) * (1 / k) * math.exp(-(k - 1) / bright)
        lfo = 0.8 + 0.2 * np.sin(2 * np.pi * rng.uniform(0.08, 0.25) * t + rng.uniform(0, 6.28))
        sig *= lfo
        out[:, 0] += sig * math.cos(pan * math.pi / 2)
        out[:, 1] += sig * math.sin(pan * math.pi / 2)
    return out


def drum(n_total, t0, pitch=70.0, decay=0.45, amp=1.0, noise=0.25, rng=None):
    out = np.zeros(n_total, np.float32)
    i0 = int(t0 * SR)
    n = int((decay * 6) * SR)
    n = min(n, n_total - i0)
    if n <= 0:
        return out
    t = np.arange(n, dtype=np.float32) / SR
    f = pitch * (1 + 1.2 * np.exp(-t / 0.035))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / decay)
    nz = rng.standard_normal(n).astype(np.float32)
    # ruido suavizado (pasa-bajos simple por media móvil)
    k = 24
    nz = np.convolve(nz, np.ones(k) / k, mode="same")
    nz *= np.exp(-t / 0.06) * noise * 3
    out[i0:i0 + n] = (body + nz) * amp
    return out


def bell(n_total, t0, freq, amp=0.2, decay=3.0):
    out = np.zeros(n_total, np.float32)
    i0 = int(t0 * SR)
    n = min(int(decay * 5 * SR), n_total - i0)
    t = np.arange(n, dtype=np.float32) / SR
    s = np.zeros(n, np.float32)
    for ratio, a, d in ((1, 1, 1), (2.0, 0.35, 0.6), (2.76, 0.25, 0.45), (5.4, 0.1, 0.25)):
        s += a * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / (decay * d))
    s *= np.minimum(1, t / 0.004)
    out[i0:i0 + n] = s * amp
    return out


def riser(n_total, t0, t1, amp, rng):
    out = np.zeros(n_total, np.float32)
    i0, i1 = int(t0 * SR), int(t1 * SR)
    n = i1 - i0
    nz = rng.standard_normal(n).astype(np.float32)
    x = np.linspace(0, 1, n, dtype=np.float32)
    # filtrado progresivo: mezcla de ruido suave y ruido brillante
    dark = np.convolve(nz, np.ones(60) / 60, mode="same") * 6
    mid = np.convolve(nz, np.ones(10) / 10, mode="same") * 2
    s = dark * (1 - x) + mid * x
    out[i0:i1] = s * (x ** 2.2) * amp
    return out


def fft_convolve(x, h):
    n = len(x) + len(h) - 1
    nfft = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(h, nfft), nfft)[:len(x)]
    return y.astype(np.float32)


def measure_lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    vals = [ln.split()[1] for ln in r.stderr.splitlines() if ln.strip().startswith("I:")]
    return float(vals[-1])


TARGET_LUFS = -16.0


def build_music(path):
    rng = np.random.default_rng(2026)
    N = int(DURATION * SR)
    pad = np.zeros((N, 2), np.float32)
    bass = np.zeros(N, np.float32)
    for j, (a, b, ch, lvl, br) in enumerate(PROG):
        i0, i1 = int(a * SR), min(N, int(b * SR))
        n = i1 - i0
        if n <= 0:
            continue
        # fundido de potencia constante: dura exactamente lo que se solapan los acordes
        att = PROG[j - 1][1] - a if j > 0 else 1.5
        rel = b - PROG[j + 1][0] if j + 1 < len(PROG) else 0.05
        swell = 0.86 + 0.14 * np.clip(np.arange(n, dtype=np.float32) / (1.6 * SR), 0, 1)
        e = (env_seg(n, att, rel) * swell)[:, None]
        seg = np.zeros((n, 2), np.float32)
        for m in CH[ch]:
            seg += pad_voice(midi(m), n, br, rng) * (0.9 if m < 55 else 0.7)
        pad[i0:i1] += seg * e * lvl
        t = np.arange(n, dtype=np.float32) / SR
        fb = midi(ROOT[ch])
        bs = np.sin(2 * np.pi * fb * t) + 0.3 * np.sin(4 * np.pi * fb * t) + 0.12 * np.sin(6 * np.pi * fb * t)
        bass[i0:i1] += bs * env_seg(n, att, rel) * lvl

    drums = np.zeros(N, np.float32)
    # golpes grandes
    for t0, p, d, amp in ((T_TITLE_HIT - 0.02, 48, 1.6, 1.2), (31.95, 46, 1.4, 0.7),
                          (T_CLAMO_HIT - 0.02, 46, 1.8, 1.3), (T_CIERRE - 0.02, 44, 2.0, 1.2)):
        drums += drum(N, t0, p, d, amp, 0.5, rng)
    # pulso creciente (Dalila insiste)
    beat = 0.6
    t0 = 26.6
    k = 0
    while t0 + k * beat < 31.6:
        acc = [1.0, 0.45, 0.7, 0.45][k % 4]
        ramp = 0.3 + 0.6 * (k * beat) / 5.0
        drums += drum(N, t0 + k * beat, 72, 0.32, acc * ramp * 0.95, 0.3, rng)
        k += 1
    # latido (la fuerza se va)
    for tb in (43.2, 44.5, 45.8, 47.0):
        drums += drum(N, tb, 52, 0.25, 0.35, 0.05, rng)
        drums += drum(N, tb + 0.24, 50, 0.22, 0.22, 0.05, rng)
    # tambores épicos (vuelve la fuerza)
    pat = [(0, 1.0), (0.6, 0.5), (0.9, 0.5), (1.2, 0.8), (1.8, 0.5), (2.1, 0.6), (2.25, 0.6),
           (2.4, 1.0), (3.0, 0.5), (3.3, 0.5), (3.6, 0.8), (4.05, 0.6), (4.2, 0.7), (4.35, 0.8), (4.5, 0.9)]
    for dt, acc in pat:
        tt = T_CLAMO_HIT + 0.6 + dt
        if tt < T_CIERRE - 0.1:
            drums += drum(N, tt, 64, 0.35, acc * 0.75, 0.35, rng)

    bells = np.zeros(N, np.float32)
    for t0, m, amp in ((1.3, 81, 0.18), (6.3, 77, 0.15), (T_TITLE_HIT, 86, 0.16), (13.4, 81, 0.12),
                       (32.4, 81, 0.15), (35.0, 77, 0.10), (37.6, 74, 0.12), (49.0, 86, 0.10),
                       (T_CIERRE + 0.5, 86, 0.16), (55.6, 81, 0.15), (56.4, 78, 0.12)):
        bells += bell(N, t0, midi(m), amp)

    rise = riser(N, 11.0, T_TITLE_HIT, 0.16, rng) + riser(N, 46.3, T_CLAMO_HIT, 0.2, rng) \
        + riser(N, 30.4, 31.95, 0.08, rng)

    # reverberación por convolución
    ir_n = int(2.8 * SR)
    ti = np.arange(ir_n, dtype=np.float32) / SR
    irs = []
    for s in (1, 2):
        r = np.random.default_rng(100 + s).standard_normal(ir_n).astype(np.float32)
        r = np.convolve(r, np.ones(6) / 6, mode="same")
        r *= np.exp(-ti * 6.9 / 2.4)
        r[: int(0.012 * SR)] = 0
        irs.append(r / np.sqrt(np.sum(r ** 2)))

    dry = np.zeros((N, 2), np.float32)
    dry += pad * 0.11
    dry += (bass * 0.16)[:, None]
    dry += (drums * 0.42)[:, None]
    dry += (bells * 0.5)[:, None] * np.array([0.8, 1.0], np.float32)
    dry += (rise * 0.6)[:, None]
    send = pad * 0.10 + (bells * 0.6)[:, None] + (drums * 0.12)[:, None] + (rise * 0.3)[:, None]
    wet = np.stack([fft_convolve(send[:, 0], irs[0]), fft_convolve(send[:, 1], irs[1])], axis=1)
    mix = dry + wet * 0.55

    t = np.arange(N, dtype=np.float32) / SR
    master = np.clip(t / 1.2, 0, 1) * (1 - np.clip((t - (DURATION - 2.5)) / 2.5, 0, 1)) ** 1.5
    mix *= master[:, None]
    mix /= np.max(np.abs(mix)) + 1e-9
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix *= 0.89 / (np.max(np.abs(mix)) + 1e-9)

    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


# ----------------------------------------------------------------------------

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "..", "intro_sanson_dalila.mp4")
    out = os.path.abspath(out)
    tmp_wav = os.path.splitext(out)[0] + "_musica.wav"
    print("Generando música…", flush=True)
    build_music(tmp_wav)
    gain = min(0.0, TARGET_LUFS - measure_lufs(tmp_wav))  # solo bajar: la mezcla ya tiene pico de -1 dBFS
    print(f"  ganancia de audio: {gain:+.1f} dB (objetivo {TARGET_LUFS} LUFS)", flush=True)
    print("Renderizando", NFRAMES, "cuadros…", flush=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", tmp_wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1", "-tune", "film",
           "-af", f"volume={gain:.2f}dB", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
           "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=_init) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(NFRAMES), chunksize=6)):
            proc.stdin.write(buf)
            if k % 150 == 0:
                print(f"  {k}/{NFRAMES}", flush=True)
    proc.stdin.close()
    proc.wait()
    os.remove(tmp_wav)
    print("Listo:", out)


if __name__ == "__main__":
    main()
