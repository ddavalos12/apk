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

# New backdrop: deep blue radial gradient with a soft warm glow in the centre.
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.48) / (H * 0.62)) ** 2)
r = np.clip(r, 0, 1)[..., None]
center = np.array([122, 62, 38], np.float32)   # BGR  #263E7A
edge = np.array([52, 20, 10], np.float32)      # BGR  #0A1434
base = center * (1 - r ** 1.4) + edge * r ** 1.4
glow = np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - H * 0.45) / 330) ** 2))[..., None]
base += glow * np.array([30, 45, 60], np.float32)
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
        col = (90, 170, 235) if hue > 0.45 else (235, 170, 110)   # gold or light blue (BGR)
        a = 0.06 + 0.06 * (0.5 + 0.5 * np.sin(t * 0.7 + ph * 9))
        cv2.circle(small, (int(cx), int(cy)), rad, tuple(c * a for c in col), -1, cv2.LINE_AA)
    small = cv2.GaussianBlur(small, (0, 0), 3)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)

K5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
K15 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
WM_X0, WM_Y0 = 1440, 900
K_RING = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

def process(frame, t):
    f = frame.astype(np.float32)
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
    bg = bg * (1 - 0.6 * shadow)
    # Thin warm-white frame around each photo.
    ring = (cv2.dilate(filled, K_RING) - filled).astype(np.float32)
    ring = cv2.GaussianBlur(ring, (0, 0), 0.8)[..., None]
    bg = bg * (1 - 0.85 * ring) + np.array([225, 240, 250], np.float32) * 0.85 * ring

    out = f + (1 - alpha) * (bg - plate)
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
    ff.stdin.write((process(frame, t) if t < END else frame).tobytes())
    i += 1
    if i % 300 == 0:
        print('frame', i, flush=True)
ff.stdin.close(); ff.wait()
print('done', i)
