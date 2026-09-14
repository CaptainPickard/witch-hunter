#!/usr/bin/env python3
"""Noise metrics on viewer screenshots: figure-region mean |horizontal diff|, brightness."""
import sys, os, numpy as np
from PIL import Image

def metrics(path, verbose=True):
    im = np.asarray(Image.open(path).convert("L"), dtype=np.float64)
    h, w = im.shape
    # figure region: central strip excluding left/right panels (panels ~296+300px)
    x0, x1 = 320, w - 330
    y0, y1 = int(h * 0.08), int(h * 0.92)
    crop = im[y0:y1, x0:x1]
    bg = np.median(crop)  # background is the dominant tone
    # figure pixels = significantly different from bg OR bright
    fig = crop > bg + 18
    if fig.sum() < 500:
        fig = crop > 90
    ys, xs = np.where(fig)
    if len(xs) < 100:
        print(f"{path}: NO FIGURE FOUND (bg={bg})"); return None
    bx0, bx1 = xs.min(), xs.max(); by0, by1 = ys.min(), ys.max()
    # pad bbox
    bx0 = max(0, bx0 - 10); bx1 = min(crop.shape[1], bx1 + 10)
    by0 = max(0, by0 - 10); by1 = min(crop.shape[0], by1 + 10)
    figcrop = crop[by0:by1, bx0:bx1]
    hf = np.abs(np.diff(figcrop, axis=1)).mean()
    # also hf inside the actual figure mask only (texel speckle, not edge contrast)
    mask = fig[by0:by1, bx0:bx1]
    figpix = figcrop[mask]
    hf_masked = None
    if mask[:, 1:].any():
        m = mask
        hf_masked = np.abs(np.diff(np.where(m, figcrop, np.nan), axis=1))
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hf_masked = float(np.nanmean(hf_masked))
    out = dict(path=path, bg=float(bg), bbox=(int(bx0), int(by0), int(bx1), int(by1)),
               fig_mean=float(figpix.mean()), fig_p10=float(np.percentile(figpix, 10)),
               fig_p90=float(np.percentile(figpix, 90)),
               hf_all=float(hf), hf_fig=hf_masked, fig_frac=float(mask.mean()))
    if verbose:
        print(f"{os.path.basename(path)}: bg={out['bg']:.0f} fig_mean={out['fig_mean']:.1f} "
              f"p10/p90={out['fig_p10']:.0f}/{out['fig_p90']:.0f} hf_all={out['hf_all']:.2f} "
              f"hf_fig={out['hf_fig']:.2f} fig_frac={out['fig_frac']:.2f}")
    return out

if __name__ == "__main__":
    for p in sys.argv[1:]:
        metrics(p)