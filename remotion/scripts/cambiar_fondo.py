"""Replace the parchment background of the BumanD album with a clean, darker backdrop.

The parchment is a static plate, so every pixel that matches the plate is background.
Output = frame + (1 - alpha) * (new_bg - plate), which also handles semi-transparent photos.
"""
import subprocess, sys
import cv2
import numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
SAMPLES = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
W, H, FPS = 1920, 1080, 30
END = 158.4  # after this the source is vertical content on black: keep as is

cap = cv2.VideoCapture(SRC)

def grab(t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    return f

# Background plate from frames whose centre is empty parchment.
plate_ts = [49.0, 49.25, 49.5, 49.75, 69.5, 69.75, 70.0, 70.25, 70.5, 70.75, 77.75, 78.0, 90.5, 102.0, 110.0, 121.75, 131.75, 149.25, 149.5]
plate = np.median(np.stack([grab(t) for t in plate_ts]), axis=0).astype(np.float32)
plate_blur = cv2.GaussianBlur(plate, (0, 0), 2)

# New backdrop: clean light neutral gradient so the photos stand out.
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.48) / (H * 0.62)) ** 2)
r = np.clip(r, 0, 1)[..., None]
center = np.array([236, 243, 247], np.float32)  # BGR  #F7F3EC
edge = np.array([190, 202, 212], np.float32)    # BGR  #D4CABE
base = center * (1 - r ** 1.4) + edge * r ** 1.4
glow = np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - H * 0.45) / 330) ** 2))[..., None]
base += glow * np.array([4, 6, 8], np.float32)
# Fine grain so the gradient doesn't band.
rng = np.random.default_rng(1)
grain = rng.normal(0, 2.0, (H, W, 1)).astype(np.float32)
base = base + grain

# Slow drifting bokeh (drawn at quarter resolution, then blurred and upscaled).
N_BOKEH = 26
bk = rng.random((N_BOKEH, 6))

def bokeh(t):
    small = np.zeros((H // 4, W // 4, 3), np.float32)
    for i, (x, y, s, sp, ph, hue) in enumerate(bk):
        cx = (x * (W // 4) + np.sin(t * 0.15 + ph * 6) * 30) % (W // 4)
        cy = (y * (H // 4) - t * (2 + sp * 4)) % (H // 4)
        rad = int(6 + s * 18)
        col = (60, 150, 215) if hue > 0.45 else (190, 120, 60)    # gold or brand blue (BGR)
        a = 0.05 + 0.05 * (0.5 + 0.5 * np.sin(t * 0.7 + ph * 9))
        cv2.circle(small, (int(cx), int(cy)), rad, tuple(c * a for c in col), -1, cv2.LINE_AA)
    small = cv2.GaussianBlur(small, (0, 0), 3)
    # On a light backdrop the bokeh tints instead of adding light.
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR) - 0.35 * cv2.resize(small.mean(axis=2, keepdims=True), (W, H))[..., None]

K5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
K15 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
WM_X0, WM_Y0 = 1440, 900
K_RING = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

BOLIVIA_GREEN = np.array([52, 121, 0], np.float32)  # BGR #007934

def fix_flags(f):
    """The source filter crushed the flag's green stripe to pure dark blue. Find dark-blue
    pixels that sit below a yellow stripe which itself sits below red, and paint them green."""
    small = cv2.resize(f, (W // 2, H // 2))
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    h, sat, v = hsv[..., 0].astype(int), hsv[..., 1], hsv[..., 2]
    red = (((h <= 8) | (h >= 170)) & (sat > 120) & (v > 120)).astype(np.uint8)
    yellow = ((h >= 12) & (h <= 34) & (sat > 100) & (v > 120)).astype(np.uint8)
    b_, g_, r_ = [small[..., i].astype(int) for i in range(3)]
    blue = ((h >= 100) & (h <= 135) & (sat > 110) & (v < 175)).astype(np.uint8)
    # Small/far flags: the stripe came out almost black and grey.
    dark = ((v < 80) & (b_ >= g_ - 2) & (b_ >= r_ - 2)).astype(np.uint8)
    if blue.sum() < 100 or yellow.sum() < 100 or red.sum() < 100:
        return f
    # "reach down": a pixel is within D px below the mask
    def reach(mask, d):
        k = np.zeros((2 * d + 1, 1), np.uint8)
        k[:d + 1] = 1  # anchor at centre: spreads the mask downwards only
        return cv2.dilate(mask, k)
    red_band = cv2.morphologyEx(red, cv2.MORPH_OPEN, K5)
    yellow_band = cv2.morphologyEx(yellow, cv2.MORPH_OPEN, K5) & reach(red_band, 90)
    cand = (blue & reach(yellow_band, 70)) | (dark & reach(yellow_band, 14))
    cand = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, K5)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cand)
    fix = np.zeros_like(cand)
    for i in range(1, n):
        x, y, w, hh, area = stats[i]
        if area >= 350 and w >= 2.2 * hh:  # a wide horizontal stripe, not a stray blob
            fix[lab == i] = 1
    if not fix.any():
        return f
    m = cv2.resize(fix.astype(np.float32), (W, H))
    m = cv2.GaussianBlur(cv2.dilate(m, K5), (0, 0), 1.0)[..., None]
    lum = np.clip(f[..., :1].astype(np.float32) / 70.0, 0.45, 1.3)
    return f * (1 - m) + BOLIVIA_GREEN * lum * m

def process(frame, t):
    f = fix_flags(frame).astype(np.float32)
    d = np.abs(cv2.GaussianBlur(f, (0, 0), 2) - plate_blur).max(axis=2)
    soft = np.clip((d - 14) / (40 - 14), 0, 1)
    strong = (d > 34).astype(np.uint8)
    strong = cv2.morphologyEx(strong, cv2.MORPH_OPEN, K5)       # drop sparkles
    strong = cv2.morphologyEx(strong, cv2.MORPH_CLOSE, K15)     # bridge gaps inside photos
    strong[WM_Y0:, WM_X0:] = 0                                  # ignore the "descript" watermark
    filled = np.zeros_like(strong)
    cnts, _ = cv2.findContours(strong, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Photos are convex frames (rectangles, hexagons): the hull fills light areas that match the parchment.
    hulls = [cv2.convexHull(c) for c in cnts if cv2.contourArea(c) > 6000]
    cv2.drawContours(filled, hulls, -1, 1, -1)
    filled = cv2.erode(filled, K5)
    alpha = np.maximum(soft * cv2.dilate(filled, K15).astype(np.float32), filled.astype(np.float32))
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)[..., None]

    bg = base + bokeh(t)
    # Soft drop shadow under the photos.
    shadow = cv2.GaussianBlur(filled.astype(np.float32), (0, 0), 18)
    shadow = np.roll(shadow, (14, 8), axis=(0, 1))[..., None]
    bg = bg * (1 - 0.45 * shadow)
    # Thin warm-white frame around each photo.
    ring = (cv2.dilate(filled, K_RING) - filled).astype(np.float32)
    ring = cv2.GaussianBlur(ring, (0, 0), 0.8)[..., None]
    bg = bg * (1 - ring) + np.array([255, 255, 255], np.float32) * ring

    # Gentle unsharp mask on the photos only.
    sharp = f + 0.6 * (f - cv2.GaussianBlur(f, (0, 0), 1.4))
    f = f * (1 - alpha) + sharp * alpha
    out = f + (1 - alpha) * (bg - plate)
    # Where there is no photo at all, use the clean backdrop (drops the old sparkles and watermark).
    w = np.clip(alpha / 0.08, 0, 1)
    out = w * out + (1 - w) * bg
    return np.clip(out, 0, 255).astype(np.uint8)

if SAMPLES:
    for t in SAMPLES:
        cv2.imwrite(f'{OUT}_{t}.jpg', cv2.resize(np.hstack([grab(t), process(grab(t), t)]), (1920, 540)))
    sys.exit()

ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-i', SRC, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                       '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', OUT], stdin=subprocess.PIPE)
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    t = i / FPS
    ff.stdin.write((process(frame, t) if t < END else fix_flags(frame).astype(np.uint8)).tobytes())
    i += 1
    if i % 300 == 0:
        print('frame', i, flush=True)
ff.stdin.close(); ff.wait()
print('done', i)
