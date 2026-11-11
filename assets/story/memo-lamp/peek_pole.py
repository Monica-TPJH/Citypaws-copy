"""Hide the peeking MEMO behind the lamp pole.
usage: peek_pole.py <base> <peek_rgba> <out> <edge_x> <feet_y> <height>
The drawn wall in the peek sticker is cut away; its edge sits behind the pole."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
base, src, out = sys.argv[1:4]; ex, feet, h = (int(v) for v in sys.argv[4:7])
cat = Image.open(src).convert('RGBA')
a = np.asarray(cat).copy(); a[:, :236, 3] = 0
bb = Image.fromarray(a).getbbox(); cat = Image.fromarray(a).crop((236, bb[1], bb[2], bb[3]))
k = h / cat.size[1]; cat = cat.resize((round(cat.size[0] * k), h), Image.LANCZOS)
w = cat.size[0]; x0, y0 = ex, feet - h
bg = Image.open(base).convert('RGBA'); orig = np.asarray(bg).astype(float)
# contact shadow
sh = Image.new('L', bg.size, 0)
ImageDraw.Draw(sh).ellipse((x0 - w * .05, feet - h * .03, x0 + w * .8, feet + h * .04), fill=220)
sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(h * .025))).astype(float) / 255
b = orig.copy(); b[..., :3] *= 1 - .55 * sh[..., None]
bg = Image.fromarray(b.astype(np.uint8)); bg.alpha_composite(cat, (x0, y0))
r = np.asarray(bg).astype(float)
# the pole stays in front: restore original pixels left of its right edge
m = np.zeros(r.shape[:2]); m[:, :1192] = 1; m[:, 1192:1195] = .5
r = r * (1 - m[..., None]) + orig * m[..., None]
Image.fromarray(r.astype(np.uint8)).convert('RGB').save(out, quality=92)
print('cat box', x0, y0, x0 + w, feet)
