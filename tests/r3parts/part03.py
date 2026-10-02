

# ----------------------------------------- image decode + block metrics ----
def decode_image(data):
    """PNG bytes or data URL -> PIL RGB image (PIL 12.3 on the box)."""
    from PIL import Image
    import base64
    if isinstance(data, str) and data.startswith("data:"):
        data = base64.b64decode(data.split(",", 1)[1])
    return Image.open(io.BytesIO(data)).convert("RGB")


def is_degenerate(img):
    """All-zero / single-colour frame = SwiftShader degenerate (flake)."""
    ext = img.getextrema()
    return all(lo == hi for lo, hi in ext)


def _eq(a, b):
    return (abs(a[0] - b[0]) <= 2 and abs(a[1] - b[1]) <= 2
            and abs(a[2] - b[2]) <= 2)


def block_metrics(img):
    """A2: block structure on the COMPOSITED display (page.screenshot).
    Band = ground rows [0.72h,0.95h] x cols [0.30w,0.70w]. Phase (0/1)
    auto-detected once from the horizontal aligned-vs-misaligned gap and
    reused for every metric."""
    w, h = img.size
    px = img.load()
    x0, x1 = int(0.30 * w), int(0.70 * w)
    y0, y1 = int(0.72 * h), int(0.95 * h)

    def pair_h(ph):
        eq = n = 0
        for y in range(y0, y1):
            for x in range(x0 + ((ph - x0) % 2), x1 - 1, 2):
                n += 1
                eq += _eq(px[x, y], px[x + 1, y])
        return eq / max(1, n)

    def pair_v(ph):
        eq = n = 0
        for y in range(y0 + ((ph - y0) % 2), y1 - 1, 2):
            for x in range(x0, x1):
                n += 1
                eq += _eq(px[x, y], px[x, y + 1])
        return eq / max(1, n)

    p0, p1 = pair_h(0), pair_h(1)
    phase = 0 if (p0 - p1) >= (p1 - p0) else 1
    aligned_h = p0 if phase == 0 else p1
    misaligned = p1 if phase == 0 else p0
    aligned_v = pair_v(phase)
    # run lengths over 20 sampled rows (truncated first/last run dropped)
    hist = {}
    runs_total = runs_even = 0
    for k in range(20):
        y = y0 + int(k * (y1 - y0 - 1) / 19.0)
        runs = []
        start = x0
        for x in range(x0 + 1, x1):
            if not _eq(px[x, y], px[x - 1, y]):
                runs.append((start, x - start))
                start = x
        runs.append((start, x1 - start))
        for (_s, ln) in runs[1:-1]:
            runs_total += 1
            runs_even += (ln % 2 == 0)
            hist[ln] = hist.get(ln, 0) + 1
    modal = max(hist.items(), key=lambda kv: kv[1])[0] if hist else 0
    top5 = sorted(hist.items(), key=lambda kv: -kv[1])[:5]
    return {"phase": phase, "aligned_h": round(aligned_h, 4),
            "aligned_v": round(aligned_v, 4),
            "misaligned": round(misaligned, 4),
            "gap": round(aligned_h - misaligned, 4),
            # A10 primary bar (was RECORD-only): share of colour edges
            # that fall ON the block grid; bilinear/no-grid ~0.5,
            # pixel-locked -> 1.0
            "edge_on_grid": round((1 - misaligned) / max(
                1e-9, (1 - aligned_h) + (1 - misaligned)), 4),
            "even_frac": round(runs_even / max(1, runs_total), 4),
            "runs": runs_total, "modal_run": modal, "run_top5": top5,
            "band": [x0, y0, x1, y1]}


def block_bars(m):
    """Valspec AC-P1(b) bars per IO ruling A10 (6474019): aligned bars +
    even-run + modal-run unchanged; the scene-flat misaligned control-gap
    bar (0.15) is REPLACED by edge_on_grid >= 0.80 (colour-edge grid
    adjacency: pixel-locked ~1.0, bilinear/no-grid ~0.5)."""
    return (m["aligned_h"] >= 0.90 and m["aligned_v"] >= 0.90
            and m["edge_on_grid"] >= 0.80 and m["even_frac"] >= 0.90
            and m["modal_run"] >= 2)
