"""MEMO cat walks LEFT across the school plaza for 5 s, then the loop starts again.
usage: python compose-scene.py <scratch_dir> <out_dir>
  <scratch_dir>/kco/*.png   keyed walk frames (original, unmirrored: the cat naturally walks left)
  <scratch_dir>/bg15l/*.png looping background (people walking), stretched to the 5 s timeline
The cat fades in/out on the clip's still frames (feet together) so the restart is soft.
"""
import sys, glob
from PIL import Image, ImageDraw, ImageFilter

S, OUT = sys.argv[1:3]
CAT_H = 0.24                 # cat height as a fraction of frame height
X_START, X_END = 0.52, 0.14  # cat centre x (fraction of width): starts right, walks left
Y_FEET = 0.905
FADE = 4                     # frames of fade at each end (these are the still frames)

bg = [Image.open(f).convert('RGB') for f in sorted(glob.glob(S + '/bg15l/*.png'))]
W, H = bg[0].size
cat = [Image.open(f).convert('RGBA') for f in sorted(glob.glob(S + '/kco/*.png'))]
n = len(cat)

ch = int(H * CAT_H)
cw = int(cat[0].width * ch / cat[0].height)
cat = [c.resize((cw, ch), Image.LANCZOS) for c in cat]
feet = max(c.getchannel('A').point(lambda v: 255 if v > 100 else 0).getbbox()[3] for c in cat[:10])

a_, b_ = 4, n - 2            # clip frames where the feet are still
def prog(j):
    if j <= a_: return 0.0
    if j >= b_: return 1.0
    u = (j - a_) / (b_ - a_); e = 0.08
    if u < e: return (u * u / (2 * e)) / (1 - e)
    if u > 1 - e: return 1 - ((1 - u) ** 2 / (2 * e)) / (1 - e)
    return (u - e / 2) / (1 - e)

yf = Y_FEET * H
for t in range(n):
    f = bg[int(t * len(bg) / n)].convert('RGBA')          # background stretched to 5 s
    cx = (X_START + (X_END - X_START) * prog(t)) * W
    alpha = min(1.0, (t + 1) / (FADE + 1), (n - t) / (FADE + 1))
    layer = Image.new('RGBA', f.size, (0, 0, 0, 0))
    sw, sh = int(cw * 0.62), max(3, int(ch * 0.07))
    shadow = Image.new('RGBA', (sw + 16, sh + 16), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((8, 8, 8 + sw, 8 + sh), fill=(50, 35, 25, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    layer.alpha_composite(shadow, (int(cx - shadow.width / 2), int(yf - shadow.height / 2)))
    layer.alpha_composite(cat[t], (int(cx - cw / 2), int(yf - feet)))
    if alpha < 1:
        layer.putalpha(layer.getchannel('A').point(lambda v: int(v * alpha)))
    f.alpha_composite(layer)
    f.convert('RGB').save(f'{OUT}/{t:04d}.png')
print('frames', n, 'size', W, H, 'cat', cw, ch)
