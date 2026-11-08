"""MEMO study story animation from the two ORIGINAL drawings (no redraw), transparent background.
usage: python animate-study.py <out_dir>
Beats (15 fps):
  read   0.0-2.4s  reading pose, gentle breathing/sway
  sneak  2.4-4.6s  squash-pop into the bun-eating pose, chewing bob, crumbs flying
  snap   4.6-5.0s  pop back to the reading pose (quick squash/stretch)
  proper 5.0-7.0s  sitting properly, still, two small yellow sparkles
Writes <out_dir>/0000.png ... RGBA frames on a fixed canvas.
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FPS = 15
H_OUT = 360                                   # canvas height (px)

read = Image.open('pose-read.png').convert('RGBA')
eat = Image.open('pose-eat.png').convert('RGBA')
nom = Image.open('pose-nom.png').convert('RGBA')     # mouth open (AI-edited from the eating drawing)
chew = Image.open('pose-chew.png').convert('RGBA')   # mouth closed chewing, bun lowered


def hat_span(im):
    a = np.asarray(im.getchannel('A')) > 100
    ys = np.where(a.any(1))[0]
    top = ys[0]; rows = a[top + 5: top + int(im.height * 0.08)]
    xs = np.where(rows.any(0))[0]
    return xs.max() - xs.min(), (xs.max() + xs.min()) / 2


# scale both poses so the hats are the same width -> head stays the same size across the switch
wr, _ = hat_span(read); we, _ = hat_span(eat)
k = 0.80 * H_OUT / read.height
read = read.resize((int(read.width * k), int(read.height * k)), Image.LANCZOS)
ke = k * wr / we
eat = eat.resize((int(eat.width * ke), int(eat.height * ke)), Image.LANCZOS)
_, cr = hat_span(read); _, ce = hat_span(eat)
wn, _ = hat_span(nom)
kn = k * wr / wn
nom = nom.resize((int(nom.width * kn), int(nom.height * kn)), Image.LANCZOS)
chew = chew.resize((int(chew.width * kn), int(chew.height * kn)), Image.LANCZOS)
_, cn = hat_span(nom); _, cc = hat_span(chew)

W_OUT = int(H_OUT * 0.95)
GROUND = int(H_OUT * 0.96)
CX = W_OUT // 2


def place(canvas, pose, hat_cx, sx=1.0, sy=1.0, rot=0.0, dy=0.0):
    """Draw pose with feet on the ground line, hat centre on CX; scale/rotate about the feet."""
    p = pose
    if sx != 1.0 or sy != 1.0:
        p = p.resize((max(1, int(p.width * sx)), max(1, int(p.height * sy))), Image.LANCZOS)
    cx = hat_cx * sx
    if rot:
        big = Image.new('RGBA', (p.width * 2, p.height * 2), (0, 0, 0, 0))
        big.paste(p, (p.width - int(cx), p.height - p.height), p)   # feet-centre pivot at (w, h)
        big = big.rotate(rot, resample=Image.BICUBIC, center=(p.width, p.height))
        canvas.alpha_composite(big, (int(CX - p.width), int(GROUND - p.height * 2 + p.height + dy)))
    else:
        canvas.alpha_composite(p, (int(CX - cx), int(GROUND - p.height + dy)))


def sparkle(canvas, x, y, r, alpha):
    if alpha <= 0: return
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2; rr = r if i % 2 == 0 else r * 0.32
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=(246, 204, 90, int(255 * alpha)), outline=(224, 169, 58, int(255 * alpha)))
    canvas.alpha_composite(layer)


def crumb(canvas, x, y, r, alpha):
    if alpha <= 0: return
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((x - r, y - r, x + r, y + r), fill=(240, 185, 70, int(255 * alpha)),
                                  outline=(205, 140, 50, int(255 * alpha)))
    canvas.alpha_composite(layer)


T_READ, T_SNEAK, T_SNAP, T_PROPER = 2.4, 2.2, 0.4, 2.0
N = int((T_READ + T_SNEAK + T_SNAP + T_PROPER) * FPS)
rng = np.random.default_rng(4)
# crumbs: spawn times within the sneak beat
crumbs = [(T_READ + 0.3 + rng.uniform(0, 1.6), rng.uniform(-1, 1)) for _ in range(7)]
mouth = (CX + eat.width * 0.06, GROUND - eat.height * 0.62)    # around the bun / mouth

for i in range(N):
    t = i / FPS
    c = Image.new('RGBA', (W_OUT, H_OUT), (0, 0, 0, 0))
    if t < T_READ:                                            # reading, breathing
        b = math.sin(2 * math.pi * t / 1.2)
        place(c, read, cr, sx=1 - 0.006 * b, sy=1 + 0.012 * b, rot=1.5 * math.sin(2 * math.pi * t / 2.4))
    elif t < T_READ + T_SNEAK:                                # sneak a bite
        u = t - T_READ
        if u < 0.2:                                           # squash-pop into the eating pose
            s = 1 - 0.5 * (u / 0.2)
            place(c, read if u < 0.1 else eat, cr if u < 0.1 else ce, sx=1 + 0.08 * s, sy=1 - 0.10 * s)
        else:
            # eating cycle: open mouth -> bite (bun at mouth) -> chew chew chew (mouth moves)
            v = u - 0.2
            cyc = [(nom, cn, 0.22), (eat, ce, 0.20)] + [(chew, cc, 0.16), (eat, ce, 0.12)] * 3
            acc = 0.0; pose, pc = cyc[-1][0], cyc[-1][1]
            for pp, cxp, d in cyc:
                if v < acc + d: pose, pc = pp, cxp; break
                acc += d
            else:
                pose, pc = (chew, cc) if int((v - acc) / 0.14) % 2 == 0 else (eat, ce)
            bob = 1.0 if pose is chew else 0.0
            place(c, pose, pc, sx=1 + 0.015 * bob, sy=1 - 0.03 * bob, dy=-2 * bob)
        for st, dx in crumbs:                                 # crumbs fly out and fall
            v = t - st
            if 0 <= v < 0.6:
                x = mouth[0] + dx * 40 * v / 0.6 + 30 * v
                y = mouth[1] - 50 * v + 160 * v * v
                crumb(c, x, y, 3.2, 1 - v / 0.6)
    elif t < T_READ + T_SNEAK + T_SNAP:                       # snap back to sitting properly
        u = (t - T_READ - T_SNEAK) / T_SNAP
        if u < 0.35:
            place(c, eat, ce, sx=1.08, sy=0.90)
        else:
            s = math.sin(math.pi * min(1, (u - 0.35) / 0.65))
            place(c, read, cr, sx=1 - 0.05 * s, sy=1 + 0.07 * s)
    else:                                                     # sitting properly, sparkles
        u = t - (T_READ + T_SNEAK + T_SNAP)
        place(c, read, cr)
        top = GROUND - read.height                           # sparkles beside the head
        for k_, (dx, dy_, delay) in enumerate([(-0.50, 0.16, 0.0), (0.52, 0.04, 0.25)]):
            v = u - delay
            a = min(1, v / 0.25) if v < 1.4 else max(0, 1 - (v - 1.4) / 0.4)
            r = (13 if k_ == 0 else 10) * (0.85 + 0.15 * math.sin(v * 6))
            sparkle(c, CX + dx * read.width, top + dy_ * read.height, r, a if v >= 0 else 0)
    c.save(os.path.join(OUT, f'{i:04d}.png'))
print('frames', N, 'canvas', W_OUT, H_OUT, 'read', read.size, 'eat', eat.size)
