"""Mirror a sequence of keyed cat frames but keep the MEMO hat text readable, without jitter.

mirror_sequence_keep_hat(frames) -> list of RGBA images:
  each frame is flipped horizontally, then the ORIGINAL (unflipped) hat from that frame is
  pasted where the flipped hat sits.
To stop the pasted hat from wobbling frame to frame:
  * hat height is the same for every frame (median of the per-frame detections)
  * hat centre is measured only on the upper, ear-free rows, then smoothed over time (loop-aware)
  * frames whose detection fails borrow the hat shape from the nearest good frame
"""
import numpy as np
from PIL import Image

HAT_WIDEN = 1.06


def _run(row_a, cx):
    if not row_a[cx]:
        idx = np.where(row_a)[0]
        if not len(idx): return None
        cx = idx[np.argmin(np.abs(idx - cx))]
    l = cx
    while l > 0 and row_a[l - 1]: l -= 1
    r = cx
    while r < len(row_a) - 1 and row_a[r + 1]: r += 1
    return l, r


def _detect(arr):
    """Per-frame detection: top row, rows/spans of the clean (ear-free) part of the hat,
    the side lines for extrapolation, and the colour-detected bottom row."""
    a = arr[..., 3] > 100
    ys = np.where(a.any(1))[0]
    top, bot = ys[0], ys[-1]
    h = bot - top
    band = a[top:top + max(2, h // 25)]
    cx = int(np.where(band.any(0))[0].mean())
    widths, rows = [], []
    stop = None
    for y in range(top, top + int(h * 0.30)):
        run = _run(a[y], cx)
        if run is None: break
        w = run[1] - run[0]
        if len(widths) > 5:
            pi = int(np.argmax(widths)); after = widths[pi:]
            if len(after) > 3 and w > min(after) + max(3, h // 150):
                stop = y; break
        widths.append(w); rows.append((y, run))
        cx = (run[0] + run[1]) // 2
    if stop is None or len(rows) < 12:
        return None
    pi = int(np.argmax(widths)); fit = rows[pi:]
    yy = np.array([r[0] for r in fit], float)
    pl = np.polyfit(yy, [r[1][0] for r in fit], 1)
    pr = np.polyfit(yy, [r[1][1] for r in fit], 1)
    rgb = arr[..., :3].astype(float)
    furry, bottom = 0, None
    for y in range(stop, top + int(h * 0.30)):
        l = int(round(np.polyval(pl, y))); r = int(round(np.polyval(pr, y)))
        if r - l < 6: break
        mid = rgb[y, l + (r - l) // 5: r - (r - l) // 5]
        light = mid.min(axis=1) > 175
        warm = (mid[:, 0] - mid[:, 2] > 45) & (mid.min(axis=1) > 95) & ~light
        furry = furry + 1 if warm.mean() > 0.6 else 0
        if furry >= 2:
            bottom = y - 2; break
    if bottom is None:
        return None
    upper = [(r[1][0] + r[1][1]) / 2 for r in rows if top + 4 <= r[0] <= top + 30]
    return dict(top=top, rows=rows, stop=stop, pl=pl, pr=pr, bottom=bottom,
                centre=float(np.mean(upper)) if upper else None)


def _mask_from(det, a, height, top=None):
    """Hat mask: detected spans above `stop`, side-line extrapolation below, fixed height."""
    top = det['top'] if top is None else top
    dy = top - det['top']                             # vertical offset when borrowing a shape
    m = np.zeros_like(a)
    H, W = a.shape
    for y, (l, r) in det['rows']:
        yy = y + dy
        if 0 <= yy < H: m[yy, max(l, 0):min(r, W - 1) + 1] = True
    for y in range(det['stop'], det['top'] + height + 1):
        yy = y + dy
        if not 0 <= yy < H: continue
        l = int(round(np.polyval(det['pl'], y))); r = int(round(np.polyval(det['pr'], y)))
        if r - l < 6: break
        m[yy, max(l, 0):min(r, W - 1) + 1] = True
    return m & a


def _smooth_loop(v, sigma=2.0):
    n = len(v); k = np.arange(-int(3 * sigma), int(3 * sigma) + 1)
    w = np.exp(-k ** 2 / (2 * sigma ** 2)); w /= w.sum()
    return np.array([sum(w[j] * v[(i + k[j]) % n] for j in range(len(k))) for i in range(n)])


def mirror_sequence_keep_hat(frames, report=None):
    arrs = [np.asarray(f.convert('RGBA')) for f in frames]
    n = len(arrs)
    dets = [_detect(a) for a in arrs]
    good = [i for i, d in enumerate(dets) if d and d['centre'] is not None]
    height = int(np.median([dets[i]['bottom'] - dets[i]['top'] for i in good]))
    # outlier heights also count as bad
    good = [i for i in good if abs((dets[i]['bottom'] - dets[i]['top']) - height) <= 8]
    tops = np.array([np.where(a[..., 3].any(1))[0][0] for a in arrs], float)
    centres = np.array([dets[i]['centre'] if i in good else np.nan for i in range(n)])
    gi = np.array(good)
    for i in range(n):                               # fill bad frames by loop-aware interpolation
        if np.isnan(centres[i]):
            d = np.minimum(np.abs(gi - i), n - np.abs(gi - i)); j = gi[np.argmin(d)]
            centres[i] = centres[j]
    cs = _smooth_loop(centres)
    out = []
    for i, arr in enumerate(arrs):
        a = arr[..., 3] > 100
        if i in good:
            m = _mask_from(dets[i], a, height)
        else:
            d = np.minimum(np.abs(gi - i), n - np.abs(gi - i)); j = gi[np.argmin(d)]
            m = _mask_from(dets[j], a, height, top=int(tops[i]))
        W = arr.shape[1]
        shift = int(round((W - 1) - 2 * cs[i]))
        flipped = np.ascontiguousarray(arr[:, ::-1]).copy()
        hat = np.zeros_like(arr)
        src = np.where(m[..., None], arr, 0).astype(np.uint8)
        # widen the pasted hat a little around its centre so it fully hides the flipped one
        ys_m = np.where(m.any(1))[0]; y0, y1 = ys_m[0], ys_m[-1] + 1
        xs_m = np.where(m.any(0))[0]; x0, x1 = xs_m[0], xs_m[-1] + 1
        crop = Image.fromarray(src[y0:y1, x0:x1]); cw = x1 - x0
        nw = int(round(cw * HAT_WIDEN)); crop = crop.resize((nw, y1 - y0), Image.LANCZOS)
        big = np.zeros_like(src); nx0 = int(round(x0 - (nw - cw) / 2))
        lx0, lx1 = max(nx0, 0), min(nx0 + nw, W)
        big[y0:y1, lx0:lx1] = np.asarray(crop)[:, lx0 - nx0:lx1 - nx0]
        src = big
        if shift >= 0: hat[:, shift:] = src[:, :W - shift]
        else: hat[:, :W + shift] = src[:, -shift:]
        # leftover edge of the mirrored hat that the pasted hat does not cover
        P = hat[..., 3] > 100
        Mm = m[:, ::-1]
        for _ in range(3):                                  # the drawn hat edge is a bit wider than the mask
            Mm = Mm | np.roll(Mm, 1, 1) | np.roll(Mm, -1, 1)
        ghost = Mm & ~P
        if ghost.any():
            head = (flipped[..., 3] > 100) & ~Mm & ~P      # real head/ear pixels around the hat
            for y in np.where(ghost.any(1))[0]:
                hx = np.where(head[y])[0]
                for x in np.where(ghost[y])[0]:
                    if len(hx):
                        j = hx[np.argmin(np.abs(hx - x))]
                        if abs(j - x) <= 14:
                            flipped[y, x] = flipped[y, j]; continue
                    flipped[y, x] = 0                        # over background: clear it
        o = Image.fromarray(flipped); o.alpha_composite(Image.fromarray(hat.astype(np.uint8)))
        out.append(o)
    if report is not None:
        report.update(height=height, bad=[i for i in range(n) if i not in good],
                      raw_jump=float(np.nanmean(np.abs(np.diff(centres)))),
                      smooth_jump=float(np.mean(np.abs(np.diff(cs)))))
    return out
