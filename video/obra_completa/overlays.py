"""
Overlays animados para la obra completa "Sansón y Dalila".

Cada overlay tiene un intervalo [t0, t1) en segundos del video final y dibuja
sobre un trozo del cuadro (Buf) en coma flotante (0-1).  Estilo: el mismo de la
intro y los banners (azul marino, dorado, crema; fuentes Cinzel y Cormorant).
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "intro_sanson", "assets", "fonts")
W, H = 1920, 1080

NAVY_L = np.array([10, 28, 80], np.float32) / 255
NAVY_R = np.array([24, 58, 138], np.float32) / 255
GOLD_TOP = np.array([255, 236, 176], np.float32) / 255
GOLD_BOT = np.array([205, 148, 52], np.float32) / 255
GOLD = (226, 182, 96)
CREAM = (250, 242, 222)
LIGHT_GOLD = (236, 214, 170)

F_CAPS = "Cinzel-SemiBold.ttf"
F_CAPS_BOLD = "Cinzel-ExtraBold.ttf"
F_ITALIC = "Cormorant-SemiBoldItalic.ttf"
F_SERIF = "Cormorant-SemiBold.ttf"


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------

def clamp01(x):
    return max(0.0, min(1.0, x))


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.9):
    x = clamp01(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def fade_io(g, t0, t1, fin=0.5, fout=0.5):
    return smooth((g - t0) / fin) * (1 - smooth((g - (t1 - fout)) / fout))


_fonts = {}


def font(name, size):
    k = (name, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _fonts[k]


def text_width(text, fnt, tracking=0):
    if not tracking:
        return fnt.getlength(text)
    return sum(fnt.getlength(c) for c in text) + tracking * (len(text) - 1)


def draw_text(d, x, y, text, fnt, tracking, fill):
    if not tracking:
        d.text((x, y), text, font=fnt, fill=fill)
        return
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill)
        x += fnt.getlength(c) + tracking


def premult(img):
    """PIL RGBA -> (rgb premultiplicado (h,w,3), alfa (h,w,1)) float32."""
    a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255
    return a[..., :3] * a[..., 3:4], np.ascontiguousarray(a[..., 3:4])


def text_layer(text, fname, size, color, tracking=0, shadow=0.75, glow=0.0, pad=36):
    """Texto en una línea.  color: (r,g,b) o 'gold' (degradado dorado)."""
    fnt = font(fname, size)
    w = int(text_width(text, fnt, tracking)) + 2 * pad
    h = int(size * 1.35) + 2 * pad
    m = Image.new("L", (w, h), 0)
    draw_text(ImageDraw.Draw(m), pad, pad, text, fnt, tracking, 255)
    ma = np.asarray(m).astype(np.float32)[..., None] / 255
    if color == "gold":
        yy = np.clip((np.arange(h, dtype=np.float32)[:, None, None] - pad - size * 0.1) / (size * 1.05), 0, 1)
        col = GOLD_TOP * (1 - yy) + GOLD_BOT * yy
        col = np.broadcast_to(col, (h, w, 3))
    else:
        col = np.broadcast_to(np.array(color, np.float32) / 255, (h, w, 3))
    rgb = np.zeros((h, w, 3), np.float32)
    al = np.zeros((h, w, 1), np.float32)
    if shadow:
        s1 = np.asarray(m.filter(ImageFilter.GaussianBlur(5))).astype(np.float32)[..., None] / 255
        s2 = np.asarray(m.filter(ImageFilter.GaussianBlur(16))).astype(np.float32)[..., None] / 255
        sh = np.clip(np.roll(s1, 3, axis=0) * shadow + s2 * shadow * 0.55, 0, 1)
        al = sh
    if glow:
        gl = np.asarray(m.filter(ImageFilter.GaussianBlur(14))).astype(np.float32)[..., None] / 255 * glow
        rgb = rgb * (1 - gl) + np.array([1.0, 0.8, 0.42], np.float32) * gl
        al = al * (1 - gl) + gl
    rgb = rgb * (1 - ma) + col * ma
    al = al * (1 - ma) + ma
    return rgb.astype(np.float32), al.astype(np.float32)


def stack_layers(layers, align="center", gap=0):
    """Apila capas (rgb, a) verticalmente.  layers: lista de (capa, dy_extra)."""
    w = max(l[1].shape[1] for l, _ in layers)
    h = sum(l[1].shape[0] + dy for l, dy in layers) + gap * (len(layers) - 1)
    rgb = np.zeros((h, w, 3), np.float32)
    al = np.zeros((h, w, 1), np.float32)
    y = 0
    for (lr, la), dy in layers:
        y += dy
        lh, lw = la.shape[:2]
        x = (w - lw) // 2 if align == "center" else 0
        d = rgb[y:y + lh, x:x + lw]
        d *= (1 - la)
        d += lr
        al[y:y + lh, x:x + lw] = al[y:y + lh, x:x + lw] * (1 - la) + la
        y += lh + gap
    return rgb, al


def card_layer(w, h, radius=18, alpha=0.9, border=2.5):
    """Tarjeta azul marino con borde dorado (como los banners)."""
    ss = 2
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius * ss, fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    b = Image.new("L", (w * ss, h * ss), 0)
    db = ImageDraw.Draw(b)
    db.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius * ss, outline=255, width=int(border * ss))
    inset = 7 * ss
    db.rounded_rectangle((inset, inset, w * ss - 1 - inset, h * ss - 1 - inset), max(2, (radius - 7) * ss),
                         outline=120, width=ss)
    b = b.resize((w, h), Image.LANCZOS)
    ma = np.asarray(m).astype(np.float32)[..., None] / 255
    ba = np.asarray(b).astype(np.float32)[..., None] / 255
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    fill = NAVY_L * (1 - xx) + NAVY_R * xx + np.clip(1 - yy / 0.35, 0, 1) * 0.08
    gold = GOLD_TOP * (1 - yy) + GOLD_BOT * yy
    a_f = ma * alpha
    rgb = fill * a_f
    al = a_f
    rgb = rgb * (1 - ba) + gold * ba
    al = al * (1 - ba) + ba
    return rgb.astype(np.float32), al.astype(np.float32)


def place_on(dst, src, x, y):
    """Pega una capa sobre otra (ambas (rgb, a)), alfa sobre alfa."""
    drgb, da = dst
    srgb, sa = src
    h, w = sa.shape[:2]
    d = drgb[y:y + h, x:x + w]
    d *= (1 - sa)
    d += srgb
    da[y:y + h, x:x + w] = da[y:y + h, x:x + w] * (1 - sa) + sa


def gaussian_sprite(r, sigma=None):
    sigma = sigma or r / 2.5
    n = int(2 * r + 1)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - r
    return np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2)).astype(np.float32)


def star_sprite(r):
    """Destello de 4 puntas con centro brillante."""
    n = int(2 * r + 1)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - r
    lw = max(1.0, r / 14)
    arms = np.exp(-(yy ** 2) / (2 * lw ** 2)) * np.exp(-np.abs(xx) / (r / 3.2))
    arms += np.exp(-(xx ** 2) / (2 * lw ** 2)) * np.exp(-np.abs(yy) / (r / 3.2))
    core = np.exp(-(xx ** 2 + yy ** 2) / (2 * (r / 7) ** 2))
    return np.clip(arms * 0.8 + core, 0, 1.4).astype(np.float32)


# ----------------------------------------------------------------------------
# Buffer de dibujo
# ----------------------------------------------------------------------------

class Buf:
    """Trozo del cuadro en float (h, w, 3) cuya esquina está en (ox, oy)."""

    def __init__(self, arr, ox, oy):
        self.arr, self.ox, self.oy = arr, ox, oy
        self.h, self.w = arr.shape[:2]

    def _clip(self, x, y, lw, lh):
        x, y = int(round(x)), int(round(y))
        x0, y0 = max(x, self.ox), max(y, self.oy)
        x1, y1 = min(x + lw, self.ox + self.w), min(y + lh, self.oy + self.h)
        if x0 >= x1 or y0 >= y1:
            return None
        return x, y, x0, y0, x1, y1

    def over(self, layer, x, y, op=1.0):
        if op <= 0.003:
            return
        rgb, a = layer
        c = self._clip(x, y, a.shape[1], a.shape[0])
        if not c:
            return
        x, y, x0, y0, x1, y1 = c
        sa = a[y0 - y:y1 - y, x0 - x:x1 - x]
        sr = rgb[y0 - y:y1 - y, x0 - x:x1 - x]
        d = self.arr[y0 - self.oy:y1 - self.oy, x0 - self.ox:x1 - self.ox]
        if op != 1.0:
            sa = sa * op
            sr = sr * op
        d *= (1 - sa)
        d += sr

    def add(self, sprite, color, x, y, k=1.0):
        """Luz aditiva: sprite (h, w) o (h, w, 1) por color (3,)."""
        if k <= 0.003:
            return
        s = sprite if sprite.ndim == 3 else sprite[..., None]
        c = self._clip(x, y, s.shape[1], s.shape[0])
        if not c:
            return
        x, y, x0, y0, x1, y1 = c
        self.arr[y0 - self.oy:y1 - self.oy, x0 - self.ox:x1 - self.ox] += \
            s[y0 - y:y1 - y, x0 - x:x1 - x] * (np.asarray(color, np.float32) * k)

    def add_centered(self, sprite, color, cx, cy, k=1.0):
        self.add(sprite, color, cx - sprite.shape[1] / 2, cy - sprite.shape[0] / 2, k)


class Overlay:
    full = False     # True: necesita el cuadro entero
    layer = 1        # orden de dibujo (0 = efectos de luz, 1 = gráficos)

    def bbox(self, g):
        return (0, 0, W, H)

    def draw(self, buf, g):
        raise NotImplementedError


# ----------------------------------------------------------------------------
# Etiqueta de personaje: punto, línea y tarjeta
# ----------------------------------------------------------------------------

class NameTag(Overlay):
    def __init__(self, name, sub, t0, t1, anchor, pill):
        self.t0, self.t1 = t0, t1
        self.ax, self.ay = anchor[0] * W, anchor[1] * H
        cx, cy = pill[0] * W, pill[1] * H
        l1 = text_layer(name, F_CAPS, 34, "gold", tracking=5, shadow=0.0, pad=0)
        parts = [(l1, 0)]
        if sub:
            parts.append((text_layer(sub, F_ITALIC, 31, CREAM, shadow=0.0, pad=0), 2))
        txt = stack_layers(parts)
        tw, th = txt[1].shape[1], txt[1].shape[0]
        pw, ph = tw + 64, th + 30
        self.card = card_layer(pw, ph, radius=16)
        place_on(self.card, txt, (pw - tw) // 2, (ph - th) // 2 + 2)
        self.pw, self.ph = pw, ph
        self.px = int(np.clip(cx - pw / 2, 24, W - pw - 24))
        self.py = int(np.clip(cy - ph / 2, 24, H - ph - 24))
        cx, cy = self.px + pw / 2, self.py + ph / 2
        dx, dy = cx - self.ax, cy - self.ay
        if abs(dx) > abs(dy) * 0.9:
            self.mode = "left" if dx > 0 else "right"
            self.P = (self.px if dx > 0 else self.px + pw, cy)
        else:
            self.mode = "center"
            self.P = (cx, self.py + ph if dy < 0 else self.py)
        m = 40
        self.bx0 = int(min(self.ax, self.P[0], self.px) - m)
        self.by0 = int(min(self.ay, self.P[1], self.py) - m)
        self.bx1 = int(max(self.ax, self.P[0], self.px + pw) + m)
        self.by1 = int(max(self.ay, self.P[1], self.py + ph) + m)
        self.lx0 = int(min(self.ax, self.P[0]) - 46)
        self.ly0 = int(min(self.ay, self.P[1]) - 46)
        self.lw = int(abs(self.ax - self.P[0]) + 92)
        self.lh = int(abs(self.ay - self.P[1]) + 92)

    def bbox(self, g):
        return (self.bx0, self.by0, self.bx1, self.by1)

    def draw(self, buf, g):
        u = g - self.t0
        out = 1 - smooth((g - (self.t1 - 0.45)) / 0.45)
        if out <= 0:
            return
        # punto, anillo y línea (dibujados al doble de tamaño y reducidos: bordes suaves)
        ss = 2
        im = Image.new("RGBA", (self.lw * ss, self.lh * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        ax, ay = (self.ax - self.lx0) * ss, (self.ay - self.ly0) * ss
        Px, Py = (self.P[0] - self.lx0) * ss, (self.P[1] - self.ly0) * ss
        p = ease_out((u - 0.15) / 0.4)
        if p > 0:
            ex, ey = ax + (Px - ax) * p, ay + (Py - ay) * p
            d.line([(ax, ay), (ex, ey)], fill=(8, 18, 50, 150), width=7 * ss)
            d.line([(ax, ay), (ex, ey)], fill=GOLD + (255,), width=3 * ss)
        v = clamp01(u / 0.9)
        if v < 1:
            rr = (9 + 34 * ease_out(v)) * ss
            d.ellipse((ax - rr, ay - rr, ax + rr, ay + rr), outline=GOLD + (int(230 * (1 - v)),), width=2 * ss)
        r = 8 * ease_out_back(u / 0.3) * ss
        if r > 0:
            d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=GOLD + (255,))
            r2 = r * 0.45
            d.ellipse((ax - r2, ay - r2, ax + r2, ay + r2), fill=(255, 250, 235, 255))
        im = im.resize((self.lw, self.lh), Image.LANCZOS)
        buf.over(premult(im), self.lx0, self.ly0, out)
        # tarjeta: se despliega desde el lado de la línea
        rv = ease_out((u - 0.45) / 0.45)
        if rv <= 0:
            return
        rgb, a = self.card
        w = self.pw
        if self.mode == "left":
            c0, c1 = 0, max(1, int(w * rv))
        elif self.mode == "right":
            c0, c1 = min(w - 1, int(w * (1 - rv))), w
        else:
            c0, c1 = int(w / 2 * (1 - rv)), max(int(w / 2 * (1 + rv)), int(w / 2 * (1 - rv)) + 1)
        buf.over((rgb[:, c0:c1], a[:, c0:c1]), self.px + c0, self.py, out * smooth((u - 0.4) / 0.25))


# ----------------------------------------------------------------------------
# Lugar: alfiler de mapa con tarjeta
# ----------------------------------------------------------------------------

def pin_layer(size=64):
    ss = 3
    s = size * ss
    im = Image.new("RGBA", (s, int(s * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = s * 0.42
    cx, cy = s / 2, s * 0.45
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(226, 182, 96, 255))
    d.polygon([(cx - r * 0.82, cy + r * 0.55), (cx + r * 0.82, cy + r * 0.55), (cx, s * 1.3)], fill=(226, 182, 96, 255))
    r2 = r * 0.42
    d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=(14, 34, 92, 255))
    im = im.resize((size, int(size * 1.35)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    hh = a.shape[0]
    yy = np.linspace(0, 1, hh, dtype=np.float32)[:, None, None]
    col = GOLD_TOP * (1 - yy) + GOLD_BOT * yy
    gold_mask = (a[..., :3].sum(-1, keepdims=True) > 1.2).astype(np.float32)
    rgb = np.where(gold_mask > 0, col, a[..., :3]) * a[..., 3:4]
    return rgb.astype(np.float32), a[..., 3:4].copy()


class LocationPin(Overlay):
    def __init__(self, title, sub, ref, t0, t1, x=64, y=60):
        self.t0, self.t1, self.x, self.y = t0, t1, x, y
        lt = text_layer(title, F_CAPS_BOLD, 42, "gold", tracking=7, shadow=0.0, pad=0)
        ls = text_layer(sub, F_ITALIC, 34, CREAM, shadow=0.0, pad=0)
        lr = text_layer(ref, F_CAPS, 21, LIGHT_GOLD, tracking=5, shadow=0.0, pad=0)
        txt = stack_layers([(lt, 0), (ls, 0), (lr, 6)], align="left")
        tw, th = txt[1].shape[1], txt[1].shape[0]
        self.pin = pin_layer(58)
        pw = 58 + 40 + tw + 52
        ph = max(th, 80) + 34
        self.card = card_layer(pw, ph, radius=18)
        place_on(self.card, txt, 58 + 40 + 20, (ph - th) // 2 + 2)
        self.pw, self.ph = pw, ph
        self.pin_x = x + 30
        self.pin_y = y + (ph - self.pin[1].shape[0]) // 2
        self.tip = (self.pin_x + 29, self.pin_y + self.pin[1].shape[0] - 2)
        self.ring = gaussian_sprite(40, 12)

    def bbox(self, g):
        return (self.x - 40, self.y - 120, self.x + self.pw + 40, self.y + self.ph + 60)

    def draw(self, buf, g):
        u = g - self.t0
        out = 1 - smooth((g - (self.t1 - 0.5)) / 0.5)
        if out <= 0:
            return
        rv = ease_out((u - 0.05) / 0.6)
        rgb, a = self.card
        c1 = max(1, int(self.pw * rv))
        buf.over((rgb[:, :c1], a[:, :c1]), self.x, self.y, out)
        # el alfiler cae con un rebote
        k = clamp01((u - 0.35) / 0.55)
        if k > 0:
            b = 1 - abs(math.cos(k * math.pi * 1.5)) * (1 - k) ** 1.5
            dy = -110 * (1 - b)
            buf.over(self.pin, self.pin_x, self.pin_y + dy, out * smooth(k / 0.2))
        v = clamp01((u - 0.8) / 0.7)
        if 0 < v < 1:
            # onda en la punta del alfiler
            im = Image.new("RGBA", (200, 80), (0, 0, 0, 0))
            dr = ImageDraw.Draw(im)
            rx, ry = 12 + 70 * ease_out(v), 4 + 18 * ease_out(v)
            dr.ellipse((100 - rx, 40 - ry, 100 + rx, 40 + ry), outline=GOLD + (int(220 * (1 - v)),), width=3)
            buf.over(premult(im), self.tip[0] - 100, self.tip[1] - 40, out)


# ----------------------------------------------------------------------------
# Versículo en la parte de abajo
# ----------------------------------------------------------------------------

def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ornament_layer(width=420):
    ss = 2
    h = 30
    im = Image.new("RGBA", ((width + 40) * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = (width + 40) * ss // 2, h * ss // 2
    col = GOLD + (255,)
    d.line((20 * ss, cy, cx - 22 * ss, cy), fill=col, width=3 * ss)
    d.line((cx + 22 * ss, cy, (width + 20) * ss, cy), fill=col, width=3 * ss)
    d.polygon([(cx, cy - 10 * ss), (cx + 10 * ss, cy), (cx, cy + 10 * ss), (cx - 10 * ss, cy)], fill=col)
    for sx in (-28, 28):
        d.ellipse((cx + (sx - 4) * ss, cy - 4 * ss, cx + (sx + 4) * ss, cy + 4 * ss), fill=col)
    im = im.resize((width + 40, h), Image.LANCZOS)
    return premult(im)


class VerseCard(Overlay):
    def __init__(self, text, ref, t0, t1, size=50, maxw=1560):
        self.t0, self.t1 = t0, t1
        fnt = font(F_ITALIC, size)
        lines = wrap("“" + text + "”", fnt, maxw)
        self.lines = [text_layer(l, F_ITALIC, size, CREAM, shadow=0.8, pad=24) for l in lines]
        self.ref = text_layer(ref, F_CAPS, 27, "gold", tracking=7, shadow=0.8, pad=20)
        self.orn = ornament_layer(380)
        lh = int(size * 1.22)
        total = 34 + len(lines) * lh + 52
        self.y_bottom = H - 46
        self.y_orn = self.y_bottom - total
        self.y_lines = [self.y_orn + 34 + k * lh for k in range(len(lines))]
        self.y_ref = self.y_bottom - 46
        self.top = self.y_orn - 150
        yy = np.arange(H - self.top, dtype=np.float32)
        k = np.clip(yy / (H - self.top), 0, 1)
        self.band = (k ** 1.15 * 0.78)[:, None, None].astype(np.float32)

    def bbox(self, g):
        return (0, self.top, W, H)

    def draw(self, buf, g):
        u = g - self.t0
        out = 1 - smooth((g - (self.t1 - 0.6)) / 0.6)
        if out <= 0:
            return
        kb = smooth(u / 0.6) * out
        y0 = self.top - buf.oy
        reg = buf.arr[max(0, y0):, :]
        band = self.band[max(0, -y0):max(0, -y0) + reg.shape[0]]
        reg *= (1 - band * kb)
        # ornamento: se dibuja desde el centro hacia afuera
        p = ease_out((u - 0.15) / 0.7)
        if p > 0:
            rgb, a = self.orn
            w = a.shape[1]
            c0, c1 = int(w / 2 * (1 - p)), max(int(w / 2 * (1 + p)), int(w / 2 * (1 - p)) + 1)
            buf.over((rgb[:, c0:c1], a[:, c0:c1]), (W - w) / 2 + c0, self.y_orn, out)
        for k, (lay, y) in enumerate(zip(self.lines, self.y_lines)):
            e = ease_out((u - 0.35 - 0.22 * k) / 0.6)
            if e > 0:
                lw, lh = lay[1].shape[1], lay[1].shape[0]
                buf.over(lay, (W - lw) / 2, y - 24 + (1 - e) * 16, e * out)
        e = ease_out((u - 0.55 - 0.22 * len(self.lines)) / 0.6)
        if e > 0:
            lw = self.ref[1].shape[1]
            buf.over(self.ref, (W - lw) / 2, self.y_ref - 20, e * out)


# ----------------------------------------------------------------------------
# Tarjeta de título centrada (escenario vacío)
# ----------------------------------------------------------------------------

class TitleCard(Overlay):
    full = True

    def __init__(self, title, text, ref, t0, t1, cy=0.42):
        self.t0, self.t1 = t0, t1
        self.title = text_layer(title, F_ITALIC, 150, "gold", shadow=0.8, glow=0.4, pad=50)
        fnt = font(F_ITALIC, 52)
        self.lines = [text_layer(l, F_ITALIC, 52, CREAM, shadow=0.85, pad=24)
                      for l in wrap("“" + text + "”", fnt, 1300)]
        self.ref = text_layer(ref, F_CAPS, 28, "gold", tracking=7, shadow=0.8, pad=20)
        self.orn = ornament_layer(460)
        self.cy = cy * H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - self.cy - 60) / (H * 0.55)) ** 2)
        self.dark = (0.55 * np.clip(1.15 - r * 0.6, 0, 1) + 0.12)[..., None].astype(np.float32)
        self.dust = Particles(60, seed=13, color=(1.0, 0.85, 0.5), rise=24)

    def draw(self, buf, g):
        u = g - self.t0
        k = fade_io(g, self.t0, self.t1, 0.8, 0.7)
        if k <= 0:
            return
        buf.arr *= (1 - self.dark * k)
        self.dust.draw(buf, g, k * 0.9)
        th = self.title[1].shape[0]
        e = ease_out((u - 0.3) / 0.9)
        tw = self.title[1].shape[1]
        buf.over(self.title, (W - tw) / 2, self.cy - th / 2 - 70 + (1 - e) * 24, e * k)
        p = ease_out((u - 0.8) / 0.8)
        if p > 0:
            rgb, a = self.orn
            w = a.shape[1]
            c0, c1 = int(w / 2 * (1 - p)), max(int(w / 2 * (1 + p)), int(w / 2 * (1 - p)) + 1)
            buf.over((rgb[:, c0:c1], a[:, c0:c1]), (W - w) / 2 + c0, self.cy + 40, k)
        y = self.cy + 86
        for j, lay in enumerate(self.lines):
            e = ease_out((u - 1.2 - 0.25 * j) / 0.7)
            lw = lay[1].shape[1]
            buf.over(lay, (W - lw) / 2, y - 24 + (1 - e) * 14, e * k)
            y += 64
        e = ease_out((u - 1.5 - 0.25 * len(self.lines)) / 0.7)
        buf.over(self.ref, (W - self.ref[1].shape[1]) / 2, y - 4, e * k)


# ----------------------------------------------------------------------------
# Partículas de polvo dorado (flotan)
# ----------------------------------------------------------------------------

class Particles:
    def __init__(self, n, seed, color, rise=30, region=(0, 0, W, H)):
        rng = np.random.default_rng(seed)
        x0, y0, x1, y1 = region
        self.x = rng.uniform(x0, x1, n)
        self.y = rng.uniform(y0, y1, n)
        self.region = region
        self.v = rng.uniform(rise * 0.4, rise, n)
        self.ph = rng.uniform(0, 6.28, n)
        self.fr = rng.uniform(0.1, 0.35, n)
        self.amp = rng.uniform(8, 30, n)
        self.size = rng.choice([3, 4, 6, 9], n, p=[0.35, 0.3, 0.22, 0.13])
        self.bri = rng.uniform(0.3, 1.0, n)
        self.sprites = {s: gaussian_sprite(s * 2.2, s * 0.6) for s in set(self.size.tolist())}
        self.color = np.array(color, np.float32)

    def draw(self, buf, g, k):
        if k <= 0.01:
            return
        x0, y0, x1, y1 = self.region
        for i in range(len(self.x)):
            px = x0 + (self.x[i] - x0 + self.amp[i] * math.sin(self.fr[i] * g * 6.28 + self.ph[i])) % (x1 - x0)
            py = y0 + (self.y[i] - y0 - self.v[i] * g) % (y1 - y0)
            b = self.bri[i] * (0.6 + 0.4 * math.sin(g * 2.3 + self.ph[i])) * k * 0.6
            buf.add_centered(self.sprites[int(self.size[i])], self.color, px, py, b)


# ----------------------------------------------------------------------------
# Luz divina (rayos desde arriba) con destellos
# ----------------------------------------------------------------------------

class DivineLight(Overlay):
    full = True
    layer = 0

    def __init__(self, t0, t1, target, src=None, strength=1.0, color=(1.0, 0.86, 0.52), spread=0.42, seed=5,
                 fin=1.0, fout=1.0):
        self.t0, self.t1, self.strength, self.fin, self.fout = t0, t1, strength, fin, fout
        self.color = np.array(color, np.float32)
        tx, ty = target[0] * W, target[1] * H
        sx, sy = (src[0] * W, src[1] * H) if src else (tx, -0.35 * H)
        ys, xs = np.mgrid[0:H:2, 0:W:2].astype(np.float32)   # media resolución
        ang = np.arctan2(xs - sx, ys - sy)
        a0 = math.atan2(tx - sx, ty - sy)
        dist = np.sqrt((xs - sx) ** 2 + (ys - sy) ** 2)
        dt = math.hypot(tx - sx, ty - sy)
        cone = np.exp(-((ang - a0) / spread) ** 2)
        fall = np.clip(1 - (dist - dt) / (H * 0.8), 0, 1) ** 1.2 * np.clip(dist / (dt * 0.25), 0, 1)
        r1 = (0.5 + 0.5 * np.cos(ang * 26 + 0.7)) ** 5
        r2 = (0.5 + 0.5 * np.cos(ang * 19 + 2.1)) ** 5
        base = cone * fall
        up = lambda a: np.asarray(Image.fromarray(a.astype(np.float32), "F").resize((W, H), Image.BILINEAR))[..., None]
        self.r1 = up(r1 * base * 0.55 + base * 0.10)
        self.r2 = up(r2 * base * 0.55 + base * 0.10)
        self.glow = gaussian_sprite(260, 110)
        self.tx, self.ty = tx, ty
        rng = np.random.default_rng(seed)
        n = 26
        self.sx = tx + rng.normal(0, 120, n)
        self.sy = ty + rng.normal(10, 150, n)
        self.sper = rng.uniform(0.9, 2.0, n)
        self.sph = rng.uniform(0, 1, n)
        self.ssz = rng.choice([10, 14, 20], n)
        self.stars = {s: star_sprite(s) for s in (10, 14, 20)}

    def draw(self, buf, g):
        k = fade_io(g, self.t0, self.t1, self.fin, self.fout) * self.strength
        if k <= 0:
            return
        w = 0.5 + 0.5 * math.sin(g * 1.3)
        buf.arr += (self.r1 * w + self.r2 * (1 - w)) * (self.color * k)
        buf.add_centered(self.glow, self.color, self.tx, self.ty, 0.28 * k)
        for i in range(len(self.sx)):
            ph = ((g - self.t0) / self.sper[i] + self.sph[i]) % 1.0
            b = max(0.0, math.sin(ph * math.pi)) ** 3
            buf.add_centered(self.stars[int(self.ssz[i])], (1.0, 0.95, 0.8), self.sx[i],
                             self.sy[i] - ph * 40, b * 0.9 * k)


# ----------------------------------------------------------------------------
# Golpe (pelea con la quijada)
# ----------------------------------------------------------------------------

class ImpactBurst(Overlay):
    layer = 0

    def __init__(self, t, pos, size=1.0, seed=0):
        self.t0, self.t1 = t - 0.03, t + 0.55
        self.t = t
        self.cx, self.cy = pos[0] * W, pos[1] * H
        self.s = size
        rng = np.random.default_rng(seed)
        self.angs = rng.uniform(0, 2 * math.pi, 12)
        self.lens = rng.uniform(0.6, 1.0, 12)
        self.flash = gaussian_sprite(120, 45)
        self.R = int(300 * size)

    def bbox(self, g):
        return (int(self.cx - self.R), int(self.cy - self.R), int(self.cx + self.R), int(self.cy + self.R))

    def draw(self, buf, g):
        u = (g - self.t) / 0.5
        if u < 0:
            return
        e = ease_out(u)
        R = self.R
        ss = 2
        im = Image.new("RGBA", (2 * R * ss, 2 * R * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = R * ss
        rr = (30 + 200 * e) * self.s * ss
        a = int(255 * (1 - u) ** 1.3)
        d.ellipse((c - rr, c - rr, c + rr, c + rr), outline=(255, 226, 150, a), width=max(1, int(7 * (1 - e) * ss) + ss))
        for ang, ln in zip(self.angs, self.lens):
            r0 = (40 + 170 * e) * self.s * ss
            r1 = r0 + 70 * ln * (1 - e) * self.s * ss
            d.line((c + r0 * math.cos(ang), c + r0 * math.sin(ang), c + r1 * math.cos(ang), c + r1 * math.sin(ang)),
                   fill=(255, 240, 200, a), width=3 * ss)
        im = im.resize((2 * R, 2 * R), Image.LANCZOS)
        rgb, al = premult(im)
        buf.add(rgb, (1, 1, 1), self.cx - R, self.cy - R, 1.0)
        if u < 0.35:
            buf.add_centered(self.flash, (1.0, 0.93, 0.75), self.cx, self.cy, 0.9 * (1 - u / 0.35) * self.s)


# ----------------------------------------------------------------------------
# Destellos (plata, oro, tijeras)
# ----------------------------------------------------------------------------

class Sparkles(Overlay):
    layer = 0

    def __init__(self, t0, t1, center, radius, color=(0.92, 0.96, 1.0), n=16, seed=1, strength=1.0):
        self.t0, self.t1 = t0, t1
        self.cx, self.cy = center[0] * W, center[1] * H
        self.rx, self.ry = radius[0] * W, radius[1] * H
        rng = np.random.default_rng(seed)
        ang = rng.uniform(0, 2 * math.pi, n)
        rad = np.sqrt(rng.uniform(0, 1, n))
        self.ox = np.cos(ang) * rad * self.rx
        self.oy = np.sin(ang) * rad * self.ry
        self.per = rng.uniform(0.7, 1.5, n)
        self.ph = rng.uniform(0, 1, n)
        self.sz = rng.choice([12, 18, 26], n, p=[0.45, 0.35, 0.2])
        self.stars = {s: star_sprite(s) for s in (12, 18, 26)}
        self.color = color
        self.strength = strength
        self.glow = gaussian_sprite(int(max(self.rx, self.ry) * 1.3) + 10)

    def bbox(self, g):
        m = 140
        return (int(self.cx - self.rx - m), int(self.cy - self.ry - m), int(self.cx + self.rx + m),
                int(self.cy + self.ry + m))

    def draw(self, buf, g):
        k = fade_io(g, self.t0, self.t1, 0.4, 0.5) * self.strength
        if k <= 0:
            return
        buf.add_centered(self.glow, self.color, self.cx, self.cy, 0.18 * k)
        for i in range(len(self.ox)):
            ph = ((g - self.t0) / self.per[i] + self.ph[i]) % 1.0
            b = max(0.0, math.sin(ph * math.pi)) ** 4
            buf.add_centered(self.stars[int(self.sz[i])], self.color, self.cx + self.ox[i], self.cy + self.oy[i],
                             b * 1.1 * k)


class Glint(Overlay):
    """Un destello grande que gira (brillo de las tijeras)."""
    layer = 0

    def __init__(self, t, pos, size=70):
        self.t0, self.t1, self.t = t - 0.05, t + 0.7, t
        self.cx, self.cy = pos[0] * W, pos[1] * H
        self.size = size
        self.star = star_sprite(size)

    def bbox(self, g):
        s = self.size * 2
        return (int(self.cx - s), int(self.cy - s), int(self.cx + s), int(self.cy + s))

    def draw(self, buf, g):
        u = (g - self.t) / 0.65
        if u < 0 or u > 1:
            return
        k = math.sin(u * math.pi) ** 1.5
        ang = u * 70
        im = Image.fromarray(np.clip(self.star * 255 / 1.4, 0, 255).astype(np.uint8), "L").rotate(ang, Image.BILINEAR)
        sc = 0.6 + 0.6 * k
        n = max(3, int(im.size[0] * sc))
        im = im.resize((n, n), Image.BILINEAR)
        s = np.asarray(im).astype(np.float32) / 255 * 1.4
        buf.add_centered(s, (1.0, 0.97, 0.9), self.cx, self.cy, 1.2 * k)


# ----------------------------------------------------------------------------
# Sueño de Sansón: tono de noche y "Z z z"
# ----------------------------------------------------------------------------

class NightTint(Overlay):
    full = True
    layer = 0

    def __init__(self, t0, t1, strength=1.0):
        self.t0, self.t1, self.strength = t0, t1, strength
        self.col = np.array([0.74, 0.8, 1.02], np.float32)

    def draw(self, buf, g):
        k = fade_io(g, self.t0, self.t1, 1.0, 1.0) * self.strength
        if k <= 0:
            return
        buf.arr *= (1 + (self.col * 0.92 - 1) * k)


class Zzz(Overlay):
    def __init__(self, t0, t1, origin, every=0.75, life=2.4):
        self.t0, self.t1 = t0, t1
        self.ox, self.oy = origin[0] * W, origin[1] * H
        self.every, self.life = every, life
        self.glyphs = {s: text_layer("Z", F_CAPS_BOLD, s, (235, 240, 255), shadow=0.9, pad=18)
                       for s in (44, 56, 70, 86, 104)}

    def bbox(self, g):
        return (int(self.ox - 80), int(self.oy - 360), int(self.ox + 330), int(self.oy + 80))

    def draw(self, buf, g):
        out = 1 - smooth((g - (self.t1 - 0.6)) / 0.6)
        k = 0
        while True:
            ts = self.t0 + k * self.every
            if ts > g or ts > self.t1 - 1.0:
                break
            u = (g - ts) / self.life
            if 0 <= u < 1:
                sizes = [44, 56, 70, 86, 104]
                s = sizes[min(4, int(u * 5))]
                x = self.ox + 150 * u + 22 * math.sin(u * 7 + k)
                y = self.oy - 290 * u
                op = smooth(u / 0.15) * (1 - smooth((u - 0.6) / 0.4)) * out
                lay = self.glyphs[s]
                buf.over(lay, x - lay[1].shape[1] / 2, y - lay[1].shape[0] / 2, op)
            k += 1


# ----------------------------------------------------------------------------
# Viñeta que late (tensión: las tijeras)
# ----------------------------------------------------------------------------

class VignettePulse(Overlay):
    full = True
    layer = 0

    def __init__(self, t0, t1, bpm=72, strength=0.5, tint=(1.0, 0.86, 0.86)):
        self.t0, self.t1, self.beat, self.strength = t0, t1, 60.0 / bpm, strength
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 * 0.85 + ((yy - H / 2) / (H / 2)) ** 2)
        self.v = (np.clip((r - 0.45) / 0.9, 0, 1) ** 1.4)[..., None].astype(np.float32)
        self.tint = np.array(tint, np.float32)

    def draw(self, buf, g):
        k = fade_io(g, self.t0, self.t1, 0.8, 0.8)
        if k <= 0:
            return
        ph = ((g - self.t0) / self.beat) % 1.0
        beat = math.exp(-ph * 9) + 0.6 * math.exp(-max(0.0, ph - 0.22) * 9) * (ph > 0.22)
        a = self.strength * k * (0.7 + 0.3 * beat)
        buf.arr *= (1 - self.v * a) * (1 + (self.tint - 1) * self.v * k)


# ----------------------------------------------------------------------------
# Derrumbe: destello, polvo y escombros
# ----------------------------------------------------------------------------

class Flash(Overlay):
    full = True
    layer = 0

    def __init__(self, t, strength=0.6, decay=0.14):
        self.t0, self.t1, self.t, self.s, self.d = t, t + 0.8, t, strength, decay

    def draw(self, buf, g):
        u = g - self.t
        if u < 0:
            return
        buf.arr += np.array([1.0, 0.95, 0.85], np.float32) * (self.s * math.exp(-u / self.d))


class Dust(Overlay):
    full = True
    layer = 0

    def __init__(self, t0, t1, seed=30):
        self.t0, self.t1 = t0, t1
        rng = np.random.default_rng(seed)
        n = 160
        self.x = rng.uniform(0, W, n)
        self.y0 = rng.uniform(-H * 0.6, H * 0.2, n)
        self.vy = rng.uniform(260, 620, n)
        self.vx = rng.normal(0, 30, n)
        self.sz = rng.choice([2, 3, 4, 6], n, p=[0.3, 0.35, 0.25, 0.1])
        self.delay = rng.uniform(0, 1.2, n)
        self.specks = {s: gaussian_sprite(s * 1.8, s * 0.6) for s in (2, 3, 4, 6)}
        m = 14
        self.cx = rng.uniform(80, W - 80, m)
        self.cy = rng.uniform(H * 0.62, H * 1.02, m)
        self.cr = rng.uniform(140, 300, m)
        self.cd = rng.uniform(0, 0.6, m)
        self.cloud = {}
        for r in (160, 240, 340):
            s = gaussian_sprite(r, r / 2.4)
            self.cloud[r] = s

    def draw(self, buf, g):
        k = fade_io(g, self.t0, self.t1, 0.2, 1.5)
        if k <= 0:
            return
        u = g - self.t0
        col = np.array([0.80, 0.76, 0.70], np.float32)
        # nubes de polvo que suben del piso y se extienden
        for i in range(len(self.cx)):
            v = u - self.cd[i]
            if v <= 0:
                continue
            grow = ease_out(v / 2.5)
            r = self.cr[i] * (0.5 + 0.9 * grow)
            key = min(self.cloud, key=lambda kk: abs(kk - r))
            spr = self.cloud[key]
            a = (0.42 * smooth(v / 0.4) * (1 - smooth((v - 1.5) / 2.5))) * k
            if a <= 0.005:
                continue
            al = spr[..., None] * a
            buf.over((col * al, al), self.cx[i] - key, self.cy[i] - key - 60 * grow, 1.0)
        # partículas que caen
        for i in range(len(self.x)):
            v = u - self.delay[i]
            if v <= 0:
                continue
            y = self.y0[i] + self.vy[i] * v
            if y > H + 10:
                continue
            x = self.x[i] + self.vx[i] * v
            spr = self.specks[int(self.sz[i])]
            buf.add_centered(spr, (0.55, 0.52, 0.48), x, y, 0.9 * k)


# ----------------------------------------------------------------------------
# Final: "Fin"
# ----------------------------------------------------------------------------

class EndCard(Overlay):
    full = True

    def __init__(self, t0, t1, t_fin, quote, ref):
        self.t0, self.t1, self.t_fin = t0, t1, t_fin
        fnt = font(F_ITALIC, 50)
        self.quote = [text_layer(l, F_ITALIC, 50, CREAM, shadow=0.85, pad=24)
                      for l in wrap("“" + quote + "”", fnt, 1300)]
        self.ref = text_layer(ref, F_CAPS, 26, "gold", tracking=7, shadow=0.8, pad=20)
        self.fin = text_layer("Fin", F_ITALIC, 200, "gold", shadow=0.8, glow=0.5, pad=60)
        self.sub = text_layer("ESCUELA DOMINICAL · MONTE DE HOREB", F_CAPS, 34, CREAM, tracking=7, shadow=0.8,
                              pad=20)
        self.orn = ornament_layer(520)
        self.dust = Particles(70, seed=21, color=(1.0, 0.85, 0.5), rise=26)

    def draw(self, buf, g):
        u = g - self.t0
        k = smooth(u / 0.8)
        buf.arr *= (1 - 0.72 * k)
        self.dust.draw(buf, g, k)
        qa = ease_out((u - 0.2) / 0.8) * (1 - smooth((g - self.t_fin + 0.4) / 0.5))
        y = 300
        for lay in self.quote:
            buf.over(lay, (W - lay[1].shape[1]) / 2, y + (1 - qa) * 14, qa)
            y += 62
        buf.over(self.ref, (W - self.ref[1].shape[1]) / 2, y + 4, qa)
        e = ease_out((g - self.t_fin) / 0.9)
        if e > 0:
            fh = self.fin[1].shape[0]
            buf.over(self.fin, (W - self.fin[1].shape[1]) / 2, H / 2 - fh / 2 - 60 + (1 - e) * 26, e)
            p = ease_out((g - self.t_fin - 0.4) / 0.8)
            rgb, a = self.orn
            w = a.shape[1]
            c0, c1 = int(w / 2 * (1 - p)), max(int(w / 2 * (1 + p)), int(w / 2 * (1 - p)) + 1)
            if p > 0:
                buf.over((rgb[:, c0:c1], a[:, c0:c1]), (W - w) / 2 + c0, H / 2 + 90, 1.0)
            e2 = ease_out((g - self.t_fin - 0.7) / 0.8)
            buf.over(self.sub, (W - self.sub[1].shape[1]) / 2, H / 2 + 130, e2)
        # fundido a negro al final
        buf.arr *= (1 - smooth((g - (self.t1 - 0.9)) / 0.9))
