"""Hide the placed cat behind the left stone pedestal of couples-a.png.
usage: python hide.py <base> <placed> <out>
Restores base pixels wherever the pedestal is in front, and adds a little
ambient shading on the cat right next to the pedestal edge.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
base, placed, out = sys.argv[1:4]
b = np.asarray(Image.open(base).convert('RGB')).astype(float)
p = np.asarray(Image.open(placed).convert('RGB')).astype(float)
H, W = b.shape[:2]
edge = np.full(H, -1)                 # pedestal right edge per row (x < edge is pedestal)
edge[870:945] = 1050
edge[945:1350] = 983
edge[1350:] = 1030
xs = np.arange(W)[None, :]
occ = (xs < edge[:, None]).astype(float)
occ = np.asarray(Image.fromarray((occ * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255
# ambient occlusion: darken what's just right of the pedestal edge (only where the cat changed pixels)
changed = (np.abs(p - b).sum(2) > 12).astype(float)
dist = xs - edge[:, None]
ao = np.clip(1 - dist / 40, 0, 1) * (dist >= 0) * changed * 0.35
p = p * (1 - ao[..., None])
outimg = p * (1 - occ[..., None]) + b * occ[..., None]
Image.fromarray(outimg.astype(np.uint8)).save(out, quality=93)
print('ok')
