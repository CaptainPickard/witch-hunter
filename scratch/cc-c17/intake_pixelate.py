#!/usr/bin/env python3
"""CC-C17 intake: pixelate the 16 old_king raw bakes into the game asset dir.
v3 discipline: raw mesh AS-IS (except the 6 over-cap decimates), normals
injected, color pixelation 512 NEAREST + 5-bit posterize.
Outputs to art-direction/3d/assets/old_king/<id>-pixelated.glb + keeps raws.
Over-cap set (decimate first via fast_simplification, repo-proven):
  barn 35112->29500, haybale 4204->3800, fence-corner 55738->REGENERATE,
  ruin-arch 10131->7900, ruin-rubble 11097->5900, ruin-wall-corner 9285->7800,
  ruin-wall-straight 8367->7800, tree-pine 26714->24000.
"""
import os, sys, struct, json, math
import numpy as np
import trimesh
from PIL import Image

R = '/tmp/wh-worldfeat/scratch/treegen/old_king/raw'
OUT = '/tmp/wh-worldfeat/art-direction/3d/assets/old_king'
os.makedirs(OUT, exist_ok=True)
os.makedirs(R, exist_ok=True)

DECIMATE = {  # name -> target tris
    'ok-farm-barn': 29500, 'ok-farm-haybale': 3800,
    'ok-ruin-arch': 7900, 'ok-ruin-rubble': 5900,
    'ok-ruin-wall-corner': 7800, 'ok-ruin-wall-straight': 7800,
    'ok-tree-pine': 24000,
}

def posterize512(img):
    img = img.convert('RGBA')
    w, h = img.size
    scale = 512.0 / max(w, h)
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
    arr = np.array(img)
    for c in (0, 1, 2):
        arr[..., c] = (arr[..., c] >> 3) << 3
    return Image.fromarray(arr)

def count_tris(glb_path):
    with open(glb_path, 'rb') as f:
        data = f.read()
    clen = struct.unpack_from('<I', data, 12)[0]
    js = json.loads(data[20:20 + clen])
    n = 0
    for m in js.get('meshes', []):
        for p in m.get('primitives', []):
            idx = p.get('indices')
            if idx is not None:
                n += js['accessors'][idx].get('count', 0) // 3
    return n

def pixelate_scene(scene):
    """Posterize every embedded texture in the scene graph (trimesh objects)."""
    out_scene = scene
    try:
        for name, geom in out_scene.geometry.items():
            # 1) normals
            if not geom.face_normals.any():
                pass
            try:
                if hasattr(geom, 'vertex_normals') and (geom.vertex_normals is None or not len(geom.vertex_normals)):
                    geom.vertex_normals
            except Exception:
                pass
            # 2) texture posterize
            mat = getattr(geom.visual, 'material', None)
            tex = getattr(mat, 'baseColorTexture', None) if mat is not None else None
            if tex is not None:
                try:
                    small = posterize512(tex)
                    mat.baseColorTexture = small
                except Exception as e:
                    print('  texture post fail', name, e)
    except Exception as e:
        print('scene walk fail', e)
    return out_scene

def glb_save(scene, path):
    # trimesh GLB export round-trips materials/textures
    scene.export(path)
    return path

def process(name):
    raw = f'{R}/{name}-meshy.glb'
    if not os.path.exists(raw):
        print('MISSING', name); return None
    outp = f'{OUT}/{name}-pixelated.glb'
    if os.path.exists(outp):
        print('skip exists', name); return outp
    # load
    obj = trimesh.load(raw)
    if isinstance(obj, trimesh.Scene):
        s = obj
    else:
        s = trimesh.Scene({'m': obj})
    # decimate if flagged: apply per-geometry simplification
    if name in DECIMATE:
        target = DECIMATE[name]
        import fast_simplification
        total = sum(len(g.faces) for g in s.geometry.values())
        for gname, g in list(s.geometry.items()):
            share = len(g.faces) / max(1, total)
            tgt = max(200, int(len(g.faces) * target / max(1, total)))
            if len(g.faces) <= tgt:
                continue
            try:
                vn, fn = fast_simplification.simplify(np.asarray(g.vertices, dtype=np.float32),
                                                      np.asarray(g.faces, dtype=np.int64), target_count=tgt)
                s.geometry[gname] = trimesh.Trimesh(vn, fn, process=False)
            except Exception as e:
                print('  decimate fail', gname, e)
    s2 = pixelate_scene(s)
    glb_save(s2, outp)
    tri = count_tris(outp)
    print('%-24s -> %-40s tris %7d  %d KB' % (name, os.path.basename(outp), tri, os.path.getsize(outp) // 1024))
    return outp

names = [os.path.basename(p).replace('-meshy.glb', '') for p in sorted(os.listdir(R)) if p.endswith('-meshy.glb')]
res = {}
for n in names:
    try:
        res[n] = process(n)
    except Exception as e:
        print('FAIL', n, type(e).__name__, str(e)[:120])
        res[n] = None
print('---')
ok = [k for k, v in res.items() if v]
print('BAKED %d/%d' % (len(ok), len(names)))