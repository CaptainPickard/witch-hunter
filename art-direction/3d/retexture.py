#!/usr/bin/env python3
"""Witch Hunter register re-texture pass (from art-bible doc 24 + spike S-B3).

256px downsample -> 48-color MEDIANCUT quantize -> 5-bit posterize.
Rewrites texture images inside a GLB in place. Usage: retexture.py in.glb out.glb
"""
import sys
import numpy as np
from PIL import Image
import trimesh
import io

def pixelate(img):
    img = img.convert('RGBA')
    # 256px downsample (LANCZOS keeps painterly edges readable)
    w, h = img.size
    scale = 256.0 / max(w, h)
    if scale < 1.0:
        img = img.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
    # 48-color MEDIANCUT quantize (RGB pass; alpha re-applied after)
    alpha = img.split()[3]
    rgb = img.convert('RGB').quantize(colors=48, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    img = rgb.convert('RGBA')
    img.putalpha(alpha)
    # 5-bit posterize on RGB channels
    arr = np.array(img)
    arr[..., 0] = (arr[..., 0] >> 3) << 3
    arr[..., 1] = (arr[..., 1] >> 3) << 3
    arr[..., 2] = (arr[..., 2] >> 3) << 3
    return Image.fromarray(arr)

def main(inp, outp):
    scene = trimesh.load(inp)
    n = 0
    for name, geom in scene.geometry.items():
        vis = geom.visual
        mat = getattr(vis, 'material', None)
        uv = getattr(vis, 'uv', None)
        if mat is None:
            continue
        tex = getattr(mat, 'baseColorTexture', None)
        if tex is not None:
            new = pixelate(tex)
            mat.baseColorTexture = new
            n += 1
            if uv is not None:
                from trimesh.visual.texture import TextureVisuals
                geom.visual = TextureVisuals(uv=uv, material=mat, image=new)
        # normal maps: soften by pixelate-lite to kill photoreal detail
        nmap = getattr(mat, 'normalTexture', None)
        if nmap is not None:
            mat.normalTexture = pixelate(nmap)
    scene.export(outp)
    print(f"retextured {n} textures -> {outp}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])