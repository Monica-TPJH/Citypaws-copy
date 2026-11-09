"""Key out the green screen (RGB ~0,200,80) from extracted frames.
usage: python key.py <frames_dir> <out_dir>
Writes RGBA PNGs cropped to the union bounding box (+padding) of all frames.
"""
import sys, os, glob
import numpy as np
from PIL import Image

src, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
fs = sorted(glob.glob(os.path.join(src, '*.png')))
rgbas = []
for f in fs:
    im = np.asarray(Image.open(f).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    spill = g - np.maximum(r, b)              # how "green-screen" a pixel is
    a = np.clip(1 - (spill - 25) / 60, 0, 1)  # >85 fully transparent, <25 opaque
    # despill: pull green down to the larger of r/b on semi-transparent / fringe pixels
    g2 = np.where(spill > 0, np.maximum(r, b) + np.clip(spill, 0, None) * 0.15, g)
    rgbas.append(np.dstack([r, g2, b, a * 255]).astype(np.uint8))

mask = np.zeros(rgbas[0].shape[:2], bool)
for x in rgbas:
    mask |= x[..., 3] > 20
ys, xs = np.where(mask)
PAD = 6
H, W = mask.shape
box = (max(0, xs.min() - PAD), max(0, ys.min() - PAD), min(W, xs.max() + PAD + 1), min(H, ys.max() + PAD + 1))
for i, x in enumerate(rgbas):
    Image.fromarray(x).crop(box).save(os.path.join(out, f'{i + 1:04d}.png'))
print('frames', len(rgbas), 'box', box)
