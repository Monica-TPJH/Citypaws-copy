"""MEMO sneak-eating loop (transparent background).
usage: python animate-eat.py <out_dir>
Loop (15 fps): bite (mouth open) -> chew (mouth closed), three bites, crumbs; no bouncing.
Frames: pose-nom (mouth open), pose-eat (original, bun at mouth), pose-chew (mouth closed chewing).
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FPS = 15
H_OUT = 360

eat = Image.open('pose-eat.png').convert('RGBA')
nom = Image.open('pose-nom.png').convert('RGBA')
chew = Image.open('pose-chew.png').convert('RGBA')


def hat_span(im):
    a = np.asarray(im.getchannel('A')) > 100
    ys = np.where(a.any(1))[0]
    top = ys[0]; rows = a[top + 5: top + int(im.height * 0.08)]
    xs = np.where(rows.any(0))[0]
    return xs.max() - xs.min(), (xs.max() + xs.min()) / 2


# same hat width for all three -> head size never jumps
wn, _ = hat_span(nom)
k = 0.86 * H_OUT / nom.height
nom = nom.resize((int(nom.width * k), int(nom.height * k)), Image.LANCZOS)
chew = chew.resize((int(chew.width * k), int(chew.height * k)), Image.LANCZOS)
we, _ = hat_span(eat)
ke = k * wn / we
eat = eat.resize((int(eat.width * ke), int(eat.height * ke)), Image.LANCZOS)
cx = {id(p): hat_span(p)[1] for p in (eat, nom, chew)}

W_OUT = int(H_OUT * 1.0)
GROUND = int(H_OUT * 0.97)
CX = W_OUT // 2


def place(canvas, pose, sx=1.0, sy=1.0, dy=0.0):
    p = pose
    if sx != 1.0 or sy != 1.0:
        p = p.resize((max(1, int(p.width * sx)), max(1, int(p.height * sy))), Image.LANCZOS)
    canvas.alpha_composite(p, (int(CX - cx[id(pose)] * sx), int(GROUND - p.height + dy)))


def crumb(canvas, x, y, r, alpha):
    if alpha <= 0: return
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((x - r, y - r, x + r, y + r), fill=(240, 185, 70, int(255 * alpha)),
                                  outline=(205, 140, 50, int(255 * alpha)))
    canvas.alpha_composite(layer)


# timeline: only the two aligned frames, no scaling -> nothing moves except the mouth
seq = [(nom, 0.35), (chew, 0.55), (nom, 0.35), (chew, 0.55), (nom, 0.35), (chew, 1.05)]
T = sum(d for _, d in seq)
N = int(round(T * FPS))
mouth = (CX + nom.width * 0.10, GROUND - nom.height * 0.60)
rng = np.random.default_rng(4)
crumbs = [(0.38 + j * 0.90 + rng.uniform(-0.05, 0.05), rng.uniform(-1, 1)) for j in range(3)]

for i in range(N):
    t = i / FPS
    acc = 0
    for pose, d in seq:
        if t < acc + d: break
        acc += d
    c = Image.new('RGBA', (W_OUT, H_OUT), (0, 0, 0, 0))
    place(c, pose)
    for st, dx in crumbs:
        v = t - st
        if 0 <= v < 0.55:
            crumb(c, mouth[0] + dx * 30 * v / 0.55 + 28 * v, mouth[1] - 40 * v + 170 * v * v, 3.0, 1 - v / 0.55)
    c.save(os.path.join(OUT, f'{i:04d}.png'))
print('frames', N, 'seconds %.2f' % T, 'canvas', W_OUT, H_OUT)
