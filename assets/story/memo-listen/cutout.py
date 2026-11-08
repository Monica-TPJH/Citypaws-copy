"""Remove the white background + cream sticker border from a sticker drawing.
usage: python cutout.py <sticker> <out_rgba.png>
Flood-fills from the image edge through light pixels; dark outline (dilated) blocks the fill.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1:3]
src_im = Image.open(src).convert('RGBA')
a0 = np.asarray(src_im.getchannel('A')).astype(float) / 255   # source may already be transparent
im = Image.new('RGBA', src_im.size, (255, 255, 255, 255)); im.alpha_composite(src_im); im = im.convert('RGB')
a = np.asarray(im).astype(int)
light = (a.mean(2) >= 195) & ((a.max(2) - a.min(2)) < 70)
dark = Image.fromarray(((a.mean(2) < 170) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
passable = light & (np.asarray(dark) == 0)
reach = np.zeros_like(passable)
reach[0, :] = passable[0, :]; reach[-1, :] = passable[-1, :]
reach[:, 0] = passable[:, 0]; reach[:, -1] = passable[:, -1]
while True:
    g = reach.copy()
    g[1:] |= reach[:-1]; g[:-1] |= reach[1:]; g[:, 1:] |= reach[:, :-1]; g[:, :-1] |= reach[:, 1:]
    g &= passable
    if (g == reach).all(): break
    reach = g
# grow the background a little into the light fringe next to the outline, then soften
# close specks left by paper texture: dilate+erode the background, but never across the outline
r = Image.fromarray((reach * 255).astype(np.uint8))
closed = np.asarray(r.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))) > 0
outline = np.asarray(dark) > 0
bgm = reach | (closed & ~outline)
grow = np.asarray(Image.fromarray((bgm * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
bgm = bgm | (grow & light)
alpha = (np.where(bgm, 0, 255) * a0).astype(np.uint8)
alpha = np.asarray(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.7)))
rgba = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]))
rgba = rgba.crop(rgba.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox())
rgba.save(out)
print('saved', out, rgba.size)
