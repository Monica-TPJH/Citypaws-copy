"""Static image: MEMO cat on the school plaza.
usage: python compose-still.py <original_photo_for_colour> [out_prefix] [--retro]
  background  school-restored-nosign.png  (restored photo, AI-added sign lettering removed)
  colour      graded to match the original old photo's per-channel mean/contrast
  cat         memo-cat-cutout.png (original art, unflipped, colours untouched)
Writes <out_prefix>.png (rounded cream frame) and <out_prefix>-plain.png.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CAT_H = 0.30          # cat height as a fraction of the photo height
CAT_X = 0.28          # cat centre x (fraction of width)
FEET_Y = 0.93         # ground line (fraction of height)
GRAIN = 5.5           # film grain strength

args = [a for a in sys.argv[1:] if a != '--retro']
RETRO = '--retro' in sys.argv          # add the vintage filter over the whole picture
ref_path = args[0]
prefix = args[1] if len(args) > 1 else 'memo-school-still'

src = np.asarray(Image.open('school-restored-nosign.png').convert('RGB')).astype(float)
H, W, _ = src.shape
ref = np.asarray(Image.open(ref_path).convert('RGB')).astype(float).reshape(-1, 3)
s = src.reshape(-1, 3)
g = np.clip((src - s.mean(0)) / s.std(0) * ref.std(0) + ref.mean(0), 0, 255)

rng = np.random.default_rng(7)
grain = rng.normal(0, GRAIN, (H, W))
grain = np.asarray(Image.fromarray((grain + 128).clip(0, 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.6))).astype(float) - 128
g = np.clip(g + grain[..., None], 0, 255)
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
g = np.clip(g * (1 - 0.06 * np.clip(d - 0.6, 0, 1))[..., None], 0, 255)
bg = Image.fromarray(g.astype(np.uint8)).convert('RGBA')

cat = Image.open('memo-cat-cutout.png').convert('RGBA')
ch = int(H * CAT_H); cw = int(cat.width * ch / cat.height)
c = cat.resize((cw, ch), Image.LANCZOS)
feet = c.getchannel('A').point(lambda v: 255 if v > 100 else 0).getbbox()[3]
yf = int(H * FEET_Y); x = int(W * CAT_X)
sw, sh = int(cw * 0.62), int(ch * 0.06)
sd = Image.new('RGBA', (sw + 40, sh + 40), (0, 0, 0, 0))
ImageDraw.Draw(sd).ellipse((20, 20, 20 + sw, 20 + sh), fill=(50, 40, 35, 85))
sd = sd.filter(ImageFilter.GaussianBlur(5))
bg.alpha_composite(sd, (x - sd.width // 2, yf - sd.height // 2))
bg.alpha_composite(c, (x - cw // 2, yf - feet))


def retro(img):
    """Vintage filter over the whole picture (photo + cat): faded blacks, warm sepia cast,
    lower saturation, softer detail, heavier grain, vignette, faint dust."""
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    lum = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    a = lum + (a - lum) * 0.72                                # desaturate a bit
    a = a * [1.04, 0.99, 0.88] + [0.02, 0.01, -0.01]          # warm sepia cast
    a = 0.10 + a * 0.84                                       # lift blacks, dim whites (faded)
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    a = np.asarray(out).astype(float)
    hh, ww = a.shape[:2]
    r2 = np.random.default_rng(11)
    gr = r2.normal(0, 9, (hh, ww))
    gr = np.asarray(Image.fromarray((gr + 128).clip(0, 255).astype(np.uint8))
                    .filter(ImageFilter.GaussianBlur(0.8))).astype(float) - 128
    a = a + gr[..., None]
    y_, x_ = np.mgrid[0:hh, 0:ww]
    dd = np.sqrt(((x_ - ww / 2) / (ww / 2)) ** 2 + ((y_ - hh / 2) / (hh / 2)) ** 2)
    a = a * (1 - 0.22 * np.clip(dd - 0.45, 0, 1) ** 1.5)[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out)                                  # a few faint dust specks
    for _ in range(40):
        px, py = r2.integers(0, ww), r2.integers(0, hh); rad = r2.uniform(0.6, 1.8)
        v = int(r2.choice([235, 60])); dr.ellipse((px - rad, py - rad, px + rad, py + rad), fill=(v, v - 8, v - 18))
    return out.convert('RGBA')


if RETRO:
    bg = retro(bg)
bg.convert('RGB').save(prefix + '-plain.png')

B = int(W * 0.014); R = int(W * 0.03)
out = Image.new('RGBA', (W + 2 * B, H + 2 * B), (0, 0, 0, 0))
fm = Image.new('L', out.size, 0)
ImageDraw.Draw(fm).rounded_rectangle((0, 0, out.width - 1, out.height - 1), R + B, fill=255)
out.paste(Image.new('RGBA', out.size, (246, 241, 231, 255)), (0, 0), fm)
pm = Image.new('L', (W, H), 0)
ImageDraw.Draw(pm).rounded_rectangle((0, 0, W - 1, H - 1), R, fill=255)
out.paste(bg, (B, B), pm)
out.save(prefix + '.png')
print('saved', prefix + '.png', out.size)
