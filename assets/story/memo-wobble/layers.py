"""Split the round MEMO into a head layer (paws removed, body completed by AI under the paws)
and a paws layer (original pixels). Both on the 1100x1100 canvas of wobble-green.png."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
cut = Image.open('wobble-cutout.png')
orig = Image.new('RGBA', (1100, 1100), (0, 0, 0, 0)); orig.alpha_composite(cut, (25, 58))
O = np.asarray(orig).astype(float)
ai = np.asarray(Image.open('nopaw-a.png').convert('RGB').resize((1100, 1100), Image.LANCZOS)).astype(float)
r, g, b = ai[..., 0], ai[..., 1], ai[..., 2]
key = np.clip(((g - np.maximum(r, b)) - 30) / 40, 0, 1)            # 1 = green
A = np.dstack([ai, 255 * (1 - key)])
A[..., 1] = np.where(key > 0, np.minimum(g, np.maximum(r, b)), g)  # despill
yy = np.mgrid[:1100, :1100][0]
w = np.clip((yy - 815) / 30, 0, 1)[..., None]                     # orig above 815, AI below 845
head = O * (1 - w) + A * w
Image.fromarray(head.clip(0, 255).astype(np.uint8)).save('layer-head.png')
pm = Image.new('L', (1100, 1100), 0); d = ImageDraw.Draw(pm)
for cx, cy, rx, ry in ((301, 942, 114, 102), (780, 942, 117, 102)):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
# exact paw shape: flood the paw interior from its centre, then grow by the outline width
lum = (O[..., :3] * [0.299, 0.587, 0.114]).sum(2)
inner = Image.fromarray(((lum > 150) & (O[..., 3] > 128)).astype(np.uint8) * 255).copy()
for c in ((301, 942), (780, 942)): ImageDraw.floodfill(inner, c, 128)
inner = Image.fromarray(((np.asarray(inner) == 128) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17))
pm = (np.asarray(inner).astype(float) / 255) * (np.asarray(pm).astype(float) / 255)
pm = np.asarray(Image.fromarray((pm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255
paws = O.copy(); paws[..., 3] *= pm
Image.fromarray(paws.astype(np.uint8)).save('layer-paws.png')
