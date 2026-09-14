#!/usr/bin/env python3
"""Regrade the baked texture atlases in race pixelated GLBs.

Diagnosis (2026-09-14): the Meshy-authored 2048px atlases are authored far
darker than the concept art (orc atlas mean 29/255; 91% below 44). At the
PSX register that value range collapses into mud. Professional verdict: the
texture generation under-baked the concept's olive-skin/brown-leather midtones.

Fix (no credits, keeps UVs + geometry): in-place atlas regrade inside each
pixelated GLB - gamma 0.42 lift, saturation 1.5x, 3x3 median denoise, then the
standard 256px/48-color pixel pass register. Model on add_normals.py surgery.

Usage: regrade_atlas.py [dir] (default art-direction/3d/assets/races)
"""
import os, sys, struct, json, io
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def regrade(path):
    data = bytearray(open(path, "rb").read())
    jl, _ = struct.unpack_from("<II", data, 12)
    g = json.loads(bytes(data[20:20+jl]))
    prim = g["meshes"][0]["primitives"][0]
    img = g["images"][0]
    ibv = g["bufferViews"][img["bufferView"]]
    binoff = 20 + jl + 8
    boff = binoff + ibv["byteOffset"]
    blen = ibv["byteLength"]

    tex = Image.open(io.BytesIO(bytes(data[boff:boff+blen]))).convert("RGB")
    # gamma lift (authoring was ~2 stops under)
    a = np.asarray(tex).astype(np.float32) / 255.0
    a = np.clip(a ** 0.42, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    # saturation boost - the concept wants olive skin + brown leather to READ
    out = ImageEnhance.Color(out).enhance(1.5)
    # gentle denoise to kill the AI high-frequency grit
    out = out.filter(ImageFilter.MedianFilter(3))
    # re-encode PNG
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    newpng = buf.getvalue()

    if len(newpng) > blen:
        # atlas grew: rebuild the GLB with a bigger bin (append-safe approach)
        # strategy: pad by relocating this bufferView to the end of the bin
        start = len(data)
        while start % 4:
            start += 1
        data += b"\x00" * (start - len(data)) if start > len(data) else b""
        new_off = len(data) - binoff  # offset relative to bin start
        data += newpng
        while len(data) % 4:
            data += b"\x00"
        ibv["byteOffset"] = new_off
        ibv["byteLength"] = len(newpng)
        g["buffers"][0]["byteLength"] = len(data) - binoff
    else:
        data[boff:boff+blen] = newpng
        ibv["byteLength"] = len(newpng)

    json_out = json.dumps(g, separators=(",", ":")).encode()
    pad = (4 - len(json_out) % 4) % 4
    json_out += b" " * pad
    bin_data = bytes(data[binoff:])
    out_glTF = b"glTF" + struct.pack("<II", 2, len(json_out) + 8 + len(bin_data)) \
               + struct.pack("<II", len(json_out), 0x4E4F534A) + json_out \
               + struct.pack("<II", len(bin_data), 0x004E4942) + bin_data
    with open(path, "wb") as fh:
        fh.write(out_glTF)
    os.chmod(path, 0o644)
    return len(newpng)


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "/workspace/witch-hunter/art-direction/3d/assets/races"
    for fn in sorted(os.listdir(d)):
        if fn.endswith("-pixelated.glb"):
            n = regrade(os.path.join(d, fn))
            print(f"regraded atlas: {fn} -> {n} bytes")