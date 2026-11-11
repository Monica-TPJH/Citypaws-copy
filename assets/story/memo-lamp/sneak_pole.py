"""Sneaky MEMO gripping the lamp pole and peeking at the couple.
usage: sneak_pole.py <base> <cat_rgba> <out> <pole_center_x> <feet_y> <height>"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
PAW = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0  # 1 = paws in front of the pole
base, src, out = sys.argv[1:4]; px, feet, h = (int(v) for v in sys.argv[4:7])
cat = Image.open(src).convert('RGBA'); W0, H0 = cat.size; k = h / H0
cat = cat.resize((round(W0 * k), h), Image.LANCZOS); w = cat.size[0]
x0 = px - round(104 * k); y0 = feet - h
# paws (cutout coords) stay in front of the pole
pm = Image.new('L', cat.size, 0); d = ImageDraw.Draw(pm)
for cx, cy, rx, ry in ((92, 642, 92, 96), (119, 885, 99, 103)):
    d.ellipse(((cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k), fill=255)
paw = np.zeros(Image.open(base).size[::-1]); paw[y0:y0 + h, x0:x0 + w] = np.asarray(pm) / 255
bg = Image.open(base).convert('RGBA'); orig = np.asarray(bg).astype(float)
sh = Image.new('L', bg.size, 0)
ImageDraw.Draw(sh).ellipse((x0 + w * .1, feet - h * .03, x0 + w * .85, feet + h * .04), fill=220)
sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(h * .025))).astype(float) / 255
b = orig.copy(); b[..., :3] *= 1 - .55 * sh[..., None]
bg = Image.fromarray(b.astype(np.uint8)); bg.alpha_composite(cat, (x0, y0))
r = np.asarray(bg).astype(float)
m = np.zeros(r.shape[:2]); m[:, :1192] = 1; m[:, 1192:1195] = .5
m = m * (1 - paw * PAW)
r = r * (1 - m[..., None]) + orig * m[..., None]
Image.fromarray(r.astype(np.uint8)).convert('RGB').save(out, quality=92)
print('cat box', x0, y0, x0 + w, feet)
