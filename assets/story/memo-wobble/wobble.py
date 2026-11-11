"""Head-wobble loop for the round MEMO: the whole head sways side to side as one piece
(tilt + slide), the paws move with it.
usage: wobble.py <frames_dir> [n_frames] [deg] [slide_px]   (uses layer-head.png / layer-paws.png)"""
import sys, os, math
from PIL import Image
out = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 24
DEG = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
SLIDE = float(sys.argv[4]) if len(sys.argv) > 4 else 14.0
os.makedirs(out, exist_ok=True)
head = Image.open('layer-head.png'); paws = Image.open('layer-paws.png')
PAD = 120; W = 1100 + 2 * PAD
def padded(im):
    c = Image.new('RGBA', (W, W), (0, 0, 0, 0)); c.paste(im, (PAD, PAD)); return c
head, paws = padded(head), padded(paws)
pivot = (PAD + 550, PAD + 940)                       # where the head sits on the paws
frames = []
for i in range(N):
    t = i / N; s = math.sin(2 * math.pi * t)
    ang = DEG * s
    dx = SLIDE * s
    dy = -5 * (1 - math.cos(4 * math.pi * t)) / 2      # tiny lift at each side
    h = head.rotate(ang, resample=Image.BICUBIC, center=pivot, translate=(dx, dy))
    p = paws.rotate(ang, resample=Image.BICUBIC, center=pivot, translate=(dx, dy))  # paws move with the head
    f = Image.new("RGBA", (W, W), (0, 0, 0, 0)); f.alpha_composite(h); f.alpha_composite(p)
    frames.append(f)
bb = None
for f in frames:
    b = f.getbbox(); bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
bb = (bb[0] - 6, bb[1] - 6, bb[2] + 6, bb[3] + 6)
for i, f in enumerate(frames): f.crop(bb).save(f'{out}/{i:04d}.png')
print('frames', N, 'crop', bb)
