import sys
from pathlib import Path

import numpy as np
from PIL import Image

SHOTS = Path(r"C:\Users\ACER\AppData\Local\Temp\cursor\screenshots")
OUT = Path(__file__).parent

FRAMES = {
    "screen-1-translate": ["f1-01", "f1-03", "f1-04", "f1-06"],
    "screen-2-heritage": ["f2-01", "f2-02", "f2-04", "f2-k3"],
    "screen-3-learn": ["f3-01", "f3-02", "f3-03", "f3-04"],
    "screen-4-contribute": ["f4-01", "f4-02", "f4-03", "f4-04"],
}


def load(name):
    img = np.asarray(Image.open(SHOTS / f"{name}.png").convert("RGB")).astype(np.int16)
    cols = np.where(img.mean(axis=(0, 2)) > 20)[0]
    return img[:, cols.min() : cols.max() + 1]


def best_shift(a, b, min_overlap=25):
    h = a.shape[0]
    best, best_dy = None, None
    for dy in range(1, h - min_overlap):
        diff = np.abs(a[dy:] - b[: h - dy]).mean()
        if best is None or diff < best:
            best, best_dy = diff, dy
    return best_dy, best


for out, names in FRAMES.items():
    imgs = [load(n) for n in names]
    width = min(i.shape[1] for i in imgs)
    imgs = [i[:, :width] for i in imgs]
    canvas = imgs[0]
    prev = imgs[0]
    for img in imgs[1:]:
        dy, err = best_shift(prev, img)
        print(out, "shift", dy, "err", round(float(err), 2))
        canvas = np.vstack([canvas, img[img.shape[0] - dy :]])
        prev = img
    Image.fromarray(canvas.astype(np.uint8)).save(OUT / f"{out}.png")
    print(out, canvas.shape)
sys.exit(0)
