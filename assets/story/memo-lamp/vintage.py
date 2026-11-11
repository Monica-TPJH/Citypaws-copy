"""Give an RGBA cutout the faded old-print look of the vintage photo.
usage: python vintage.py <cutout_rgba> <out_rgba> [strength]
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1:3]
s = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
im = np.asarray(Image.open(src).convert('RGBA')).astype(np.float64)
p, a = im[..., :3], im[..., 3:]
lum = (p * np.array([0.299, 0.587, 0.114])).sum(2, keepdims=True)
g = p * (1 - 0.3 * s) + lum * 0.3 * s                         # desaturate
g = g * (1 - 0.18 * s) + np.array([100, 70, 29]) * 0.18 * s     # lift blacks, warm
g = g * (np.array([1.0, 0.94, 0.8]) ** s)                       # yellowed paper
g = g * (1 - 0.05 * s)
rng = np.random.default_rng(3)
n = np.clip(rng.normal(0, 7 * s, p.shape[:2]) + 128, 0, 255).astype(np.uint8)
n = np.asarray(Image.fromarray(n).filter(ImageFilter.GaussianBlur(0.6))).astype(float)[..., None] - 128
g = np.clip(g + n, 0, 255)
Image.fromarray(np.concatenate([g, a], 2).astype(np.uint8)).save(out)
print('ok')
