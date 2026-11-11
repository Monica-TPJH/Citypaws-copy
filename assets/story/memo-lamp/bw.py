"""Turn an RGBA cutout into grainy black-and-white film. usage: bw.py <in> <out>"""
import sys, numpy as np
from PIL import Image, ImageFilter
im = np.asarray(Image.open(sys.argv[1]).convert('RGBA')).astype(np.float64)
p, a = im[..., :3], im[..., 3:]
l = (p * [0.299, 0.587, 0.114]).sum(2)
l = 128 + (l - 128) * 1.08            # a touch more film contrast
l = l * 0.84 + 18                     # lift blacks, soften whites like the print
n = np.random.default_rng(5).normal(0, 9, l.shape)
n = np.asarray(Image.fromarray(np.clip(n + 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(float) - 128
l = np.clip(l + n, 0, 255)
out = np.dstack([l, l, l, a[..., 0]]).astype(np.uint8)
Image.fromarray(out).save(sys.argv[2])
