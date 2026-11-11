"""Place the MEMO cat cutout into the stair photo.
usage: python place.py <photo> <cat_rgba> <out> <cx> <feet_y> <height> [grade]
grade 0..1: how much the cat is pulled toward the photo's cool, soft light.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

photo, cat_p, out = sys.argv[1:4]
cx, feet, h = (int(v) for v in sys.argv[4:7])
grade = float(sys.argv[7]) if len(sys.argv) > 7 else 0.25

bg = Image.open(photo).convert('RGBA')
cat = Image.open(cat_p).convert('RGBA')
k = h / cat.size[1]
cat = cat.resize((round(cat.size[0] * k), h), Image.LANCZOS)
w = cat.size[0]
x0, y0 = cx - w // 2, feet - h

# colour grade: slight desaturation, cooler and a touch darker to sit in overcast light
a = np.asarray(cat).astype(float)
rgb = a[..., :3]
lum = rgb @ [0.299, 0.587, 0.114]
rgb = rgb * (1 - 0.35 * grade) + lum[..., None] * 0.35 * grade
rgb = rgb * (1 - 0.12 * grade) + np.array([150, 160, 170]) * 0.12 * grade
rgb = rgb * (1 - 0.08 * grade)
a[..., :3] = np.clip(rgb, 0, 255)
cat = Image.fromarray(a.astype(np.uint8))

# soft contact shadow under the feet + faint ambient occlusion
sh = Image.new('L', bg.size, 0)
from PIL import ImageDraw
d = ImageDraw.Draw(sh)
d.ellipse((cx - w * 0.42, feet - h * 0.035, cx + w * 0.46, feet + h * 0.04), fill=235)
sh = sh.filter(ImageFilter.GaussianBlur(h * 0.022))
amb = Image.new('L', bg.size, 0)
ImageDraw.Draw(amb).ellipse((cx - w * 0.6, feet - h * 0.07, cx + w * 0.7, feet + h * 0.08), fill=110)
amb = amb.filter(ImageFilter.GaussianBlur(h * 0.08))
shadow = np.maximum(np.asarray(sh), np.asarray(amb)).astype(float) / 255
b = np.asarray(bg).astype(float)
b[..., :3] *= (1 - 0.62 * shadow[..., None])
bg = Image.fromarray(b.astype(np.uint8))

bg.alpha_composite(cat, (x0, y0))
bg.convert('RGB').save(out, quality=92)
print('placed', (x0, y0, x0 + w, feet))
