# ------------------------------------------------- PNG decode (stdlib only) --
def decode_png(data_url):
    """Minimal PNG reader (8-bit RGB/RGBA, non-interlaced) from a data URL."""
    raw = base64.b64decode(data_url.split(",", 1)[1])
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a png")
    pos, w, h, depth, ctype = 8, 0, 0, 0, 0
    idat = b""
    while pos < len(raw):
        ln, typ = struct.unpack(">I4s", raw[pos:pos + 8])
        body = raw[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif typ == b"IDAT":
            idat += body
        pos += 12 + ln
    if depth != 8 or ctype not in (2, 6):
        raise ValueError("unsupported png depth=%d ctype=%d" % (depth, ctype))
    bpp = 3 if ctype == 2 else 4
    stride = w * bpp
    data = zlib.decompress(idat)
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = data[p]; p += 1
        line = bytearray(data[p:p + stride]); p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride: y * stride + stride] = line
        prev = line
    # expand 4bpp down to 3ch so downstream samplers are uniform
    if bpp == 4:
        rgb = bytearray(w * h * 3)
        for i in range(w * h):
            rgb[i * 3] = out[i * 4]
            rgb[i * 3 + 1] = out[i * 4 + 1]
            rgb[i * 3 + 2] = out[i * 4 + 2]
        return w, h, bytes(rgb), 3
    return w, h, bytes(out), bpp


def luma_of(px, o, bpp):
    return 0.2126 * px[o] + 0.7152 * px[o + 1] + 0.0722 * px[o + 2]


def mean_luma(img, w, h, bpp, x0, y0, x1, y1):
    vals = []
    for y in range(max(0, int(y0)), min(h, int(y1))):
        for x in range(max(0, int(x0)), min(w, int(x1))):
            o = (y * w + x) * bpp
            vals.append(luma_of(img, o, bpp))
    if not vals:
        return {"mean": 0.0, "n": 0}
    return {"mean": sum(vals) / len(vals), "n": len(vals)}


def mean_luma_box(img, w, h, bpp, cx, cy, half=10):
    return mean_luma(img, w, h, bpp, cx - half, cy - half, cx + half, cy + half)


def mean_luma_annulus(img, w, h, bpp, cx, cy, r0, r1, exclude_half=10):
    vals = []
    for y in range(max(0, cy - int(r1)), min(h, cy + int(r1))):
        for x in range(max(0, cx - int(r1)), min(w, cx + int(r1))):
            dx, dy = x - cx, y - cy
            d2 = dx * dx + dy * dy
            if d2 < r0 * r0 or d2 > r1 * r1:
                continue
            if abs(dx) <= exclude_half and abs(dy) <= exclude_half:
                continue
            o = (y * w + x) * bpp
            vals.append(luma_of(img, o, bpp))
    if not vals:
        return {"mean": 0.0, "n": 0}
    return {"mean": sum(vals) / len(vals), "n": len(vals)}