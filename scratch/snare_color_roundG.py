#!/usr/bin/env python3
"""Round H: two-tone vertex-color pass on the Round G snare bush (zero credits).

Input is the decimated, geometry-only snare mesh (biome_library/wh-bush-snare.glb,
3000 tris from scratch/decimate_roundG.py). It has no UV or texture, so the colour
goes in as glTF COLOR_0. GLTFLoader turns COLOR_0 into material.vertexColors = true.
Classification is deterministic. It uses no RNG, and ties break by vertex order:
  1. k-NN local density: mean distance to the k=12 nearest vertices. Density is
     1/meanDist, normalized to a 0..1 percentile rank. The quadric decimator keeps
     many vertices on the volumetric rose heads and few on the flat cane/thorn
     ribbons, so high density means rose.
  2. shape gate (Round H tuning rerun 2): density alone also lit the thick trunk
     (try1/try2 renders), so rose additionally needs a volumetric neighbourhood:
     isotropy = middle/largest eigenvalue of the k=24 NN covariance >= ISO_MIN.
  3. rose = rank >= ROSE_RANK and the shape gate, then MAJORITY smoothing over the same 12
     neighbours (SMOOTH passes) to clear salt-and-pepper speckle.
  4. height floor: the bottom BASE_FRAC of the bush height multiplies toward
     BASE_MIN (near-black) so the bush sits in the ground.
Palette (sRGB, 5-bit crushed per channel = pixel register): canes/thorns =
#2e2a26 dark cold bark, roses = #8d6d6a ash-rose. The base multiply is crushed
again after it is applied. COLOR_0 stores linear floats (glTF spec).

  snare_color_roundG.py [--rose-rank 0.62] [--smooth 2] [--iso-min 0.5] [--src in.glb] [--out out.glb]
Rewrites biome_library/wh-bush-snare-pixelated.glb as POSITION + NORMAL +
COLOR_0 + indices with one white factor PBR material (metallic 0, roughness
0.8). wh-bush-snare.glb (geometry) and raw/ are untouched. The run stats are
appended to scratch/treeqa/roundH/snare_color.jsonl.
Signed: Claude Code (Round H), 2026-10-05.
"""
import argparse, json, os, struct
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

OUT = 'art-direction/3d/assets/biome_library'
MID = 'wh-bush-snare'
K = 12
K_SHAPE = 24
CANE = (0x2e, 0x2a, 0x26)
ROSE = (0x8d, 0x6d, 0x6a)
BASE_FRAC, BASE_MIN = 0.15, 0.3


def crush5(c): return (np.asarray(c, dtype=np.int64) >> 3) << 3


def lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def isotropy(v, tree):
    """middle / largest eigenvalue of the K_SHAPE-NN covariance: ~0 on a thin
    cane or the long trunk, high on a volumetric rose knot."""
    _, idx = tree.query(v, k=K_SHAPE + 1)
    P = v[idx] - v[idx].mean(1, keepdims=True)
    ev = np.linalg.eigvalsh(np.einsum('nki,nkj->nij', P, P) / K_SHAPE)
    return ev[:, 1] / np.maximum(ev[:, 2], 1e-12)


def classify(v, rose_rank, smooth, iso_min):
    tree = cKDTree(v)
    d, idx = tree.query(v, k=K + 1)
    md = d[:, 1:].mean(1)
    # percentile rank of density (1/md): stable vs absolute scale; ties by index
    order = np.lexsort((np.arange(len(md)), -md))     # sparse first
    rank = np.empty(len(md)); rank[order] = np.arange(len(md)) / (len(md) - 1)
    rose = rank >= rose_rank
    if iso_min > 0:
        rose &= isotropy(v, tree) >= iso_min
    nb = idx[:, 1:]
    for _ in range(smooth):
        votes = rose[nb].sum(1) + rose            # self + 12 neighbours
        rose = votes * 2 > K + 1
    return rose, rank


def colors(v, rose):
    y = v[:, 1]
    h = (y - y.min()) / (y.max() - y.min())
    base = np.where(h < BASE_FRAC, BASE_MIN + (1 - BASE_MIN) * h / BASE_FRAC, 1.0)
    srgb = np.where(rose[:, None], crush5(ROSE)[None, :], crush5(CANE)[None, :]).astype(np.float64)
    srgb = crush5(np.round(srgb * base[:, None]))
    return srgb, base


def write_glb(path, v, n, f, col_lin):
    v = np.asarray(v, dtype='<f4'); n = np.asarray(n, dtype='<f4')
    c = np.hstack([col_lin, np.ones((len(col_lin), 1))]).astype('<f4')
    f = np.asarray(f, dtype='<u4').reshape(-1)
    blobs = [v.tobytes(), n.tobytes(), c.tobytes(), f.tobytes()]
    views, off = [], 0
    for b, tgt in zip(blobs, (34962, 34962, 34962, 34963)):
        views.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(b), 'target': tgt})
        off += len(b)
    gltf = {
        'asset': {'version': '2.0', 'generator': 'scratch/snare_color_roundG.py'},
        'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': MID}],
        'meshes': [{'name': MID, 'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1, 'COLOR_0': 2},
                                                 'indices': 3, 'material': 0}]}],
        'materials': [{'name': MID + '-vcol', 'pbrMetallicRoughness': {
            'baseColorFactor': [1.0, 1.0, 1.0, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.8}}],
        'accessors': [
            {'bufferView': 0, 'componentType': 5126, 'count': len(v), 'type': 'VEC3',
             'min': v.min(0).tolist(), 'max': v.max(0).tolist()},
            {'bufferView': 1, 'componentType': 5126, 'count': len(n), 'type': 'VEC3'},
            {'bufferView': 2, 'componentType': 5126, 'count': len(c), 'type': 'VEC4'},
            {'bufferView': 3, 'componentType': 5125, 'count': len(f), 'type': 'SCALAR'}],
        'bufferViews': views, 'buffers': [{'byteLength': off}]}
    js = json.dumps(gltf, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    bin_ = b''.join(blobs)
    bin_ += b'\x00' * ((4 - len(bin_) % 4) % 4)
    with open(path, 'wb') as fh:
        fh.write(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(bin_)))
        fh.write(struct.pack('<I4s', len(js), b'JSON') + js)
        fh.write(struct.pack('<I4s', len(bin_), b'BIN\x00') + bin_)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rose-rank', type=float, default=0.62)
    ap.add_argument('--smooth', type=int, default=2)
    ap.add_argument('--iso-min', type=float, default=0.5)
    ap.add_argument('--src', default=os.path.join(OUT, MID + '.glb'))
    ap.add_argument('--out', default=os.path.join(OUT, MID + '-pixelated.glb'))
    a = ap.parse_args()
    m = trimesh.load(a.src, force='mesh')
    v = np.asarray(m.vertices, dtype=np.float64)
    f = np.asarray(m.faces)
    n = trimesh.Trimesh(v, f, process=False).vertex_normals
    rose, _ = classify(v, a.rose_rank, a.smooth, a.iso_min)
    srgb, base = colors(v, rose)
    write_glb(a.out, v, n, f, lin(srgb))
    row = dict(signed='Claude Code (Round H) 2026-10-05', src=a.src, out=a.out, k=K,
               rose_rank=a.rose_rank, smooth=a.smooth, iso_min=a.iso_min, k_shape=K_SHAPE, verts=len(v), faces=len(f),
               rose_pct=round(100.0 * rose.mean(), 1), cane_pct=round(100.0 * (1 - rose.mean()), 1),
               base_darkened_pct=round(100.0 * (base < 1).mean(), 1),
               cane_srgb=crush5(CANE).tolist(), rose_srgb=crush5(ROSE).tolist(),
               bytes=os.path.getsize(a.out))
    print(json.dumps(row))
    log = Path(__file__).parent / 'treeqa' / 'roundH' / 'snare_color.jsonl'
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, 'a') as fh:
        fh.write(json.dumps(row) + '\n')


if __name__ == '__main__':
    main()
