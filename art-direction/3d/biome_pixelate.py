#!/usr/bin/env python3
"""Biome library pixelation pass (v3.1 / CC-NS2: raw mesh AS-IS, WELDED
SMOOTH normals via the CC-NS1 kernel law, color pixelation only: 512px
NEAREST + 5-bit posterize). Wake-45 Autopilot amendment: the old trimesh
vertex_normals fallback is a shader bug under the CC-NS1 law (black speckles,
faceted shards); when the law kernel is absent this module REFUSES to write
(RuntimeError, marker 'CC-NS2 refuses'). The old hardcoded os.chdir is gone
(sandbox/valspec law; runs from the current working directory).

Input:  art-direction/3d/assets/biome_library/raw/<id>.glb
Output: art-direction/3d/assets/biome_library/<id>.glb (raw copy)
        art-direction/3d/assets/biome_library/<id>-pixelated.glb

Stats (valspec V-7): one JSONL row per output file at
scratch/ns2-biome-stats.jsonl (override with BP_STATS_PATH) with ns2Weld,
ts, source, verts, faces, weldedVerts, weldPairs, guardZero.

Module contract for scripts (valspec drivers): SRC, OUT, IDS are module
attributes; IDS defaults to os.listdir of SRC (pipeline-lag law V-5);
main() runs the loop; __main__ calls main() and prints 'BIOME PIXELATE
COMPLETE' then 'V3 COMPLETE' (the historical bottom-line banner).
"""
import os, io, sys, struct, json, datetime
import numpy as np
import trimesh
from PIL import Image

# -- CC-NS2 shared kernel import block (identical text in both pipelines) --#
try:  # law kernel; refuses fallback normals ever being written (CC-NS1 law)
    import add_normals_v2 as _ns2_kernel
except ImportError:  # loud-fail law: never write un-welded normals
    _ns2_kernel = None
_NS2_WELD = _ns2_kernel is not None

SRC = 'art-direction/3d/assets/biome_library/raw'
OUT = 'art-direction/3d/assets/biome_library'
IDS = None   # pipeline-lag law: derived from os.listdir(SRC) when unset
BP_STATS_PATH = 'scratch/ns2-biome-stats.jsonl'


def _effective_ids():
    ids = globals().get('IDS')
    if ids is not None:
        return list(ids)
    return sorted(f[:-4] for f in os.listdir(SRC) if f.endswith('.glb'))


def _ns2_weld_normals(verts32, faces):
    """CC-NS2 kernel-law normals; RuntimeError when the kernel is absent."""
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2 refuses to write un-welded normals: add_normals_v2 law '
            'kernel could not be imported (import add_normals_v2 first; the '
            'CC-NS1 law forbids unwelded output).')
    return _ns2_kernel.law_normals(verts32, faces)


def _ns2_ensure_normal(path):
    """CC-NS2: return kernel-law per-file stats for path, or REFUSE loudly.

    Replaces the old trimesh vertex_normals injection fallback: per the
    CC-NS1 law, un-welded per-vertex normals are a shader bug (black
    speckles, faceted shards). If the law kernel is importable, rewrites
    path with welded smooth normals (full law append, idempotent for files
    already carrying NORMAL: returns the skip marker without writing).
    """
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2 refuses un-welded fallback normals; add_normals_v2 '
            'could not be imported; no output would be written [refusing].')
    data = open(path, "rb").read()
    g, boff, _blen = _ns2_kernel.parse_glb(data)
    if _ns2_kernel.has_normal(g):
        return {'skipped': 'NORMAL present'}
    row = _ns2_kernel.process_glb(path)
    return row


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


def _log(path, source, verts, faces, welded, pairs, guard):
    """Per-file stats row (one per OUTPUT file; valspec V-7 shape)."""
    row = {'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source': source, 'verts': int(verts), 'faces': int(faces),
           'weldedVerts': int(welded), 'weldPairs': int(pairs),
           'guardZero': int(guard), 'ns2Weld': True}
    os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(row, sort_keys=True) + '\n')


def export(path, mesh, tex):
    """CC-NS2 export: raw mesh AS-IS + welded smooth kernel-law normals +
    pixelated-palette texture. Raises RuntimeError ('CC-NS2 refuses')
    when the law kernel is unavailable — never writes un-welded output."""
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2 refuses to write un-welded normals: add_normals_v2 law '
            'kernel could not be imported (import add_normals_v2 first; the '
            'CC-NS1 law forbids unwelded output) [before any geometry/'
            'texture handling, before any file write].')
    verts32 = np.asarray(mesh.vertices, dtype=np.float32)
    faces64 = np.asarray(mesh.faces, dtype=np.int64)
    # kernel-law NORMAL payload FIRST (no file write on fallback)
    vnorm, _nv, _wc, _pairs, _guard = _ns2_kernel.law_normals(verts32, faces64)
    nvn = vnorm.astype(np.float32)
    assert len(nvn) == len(verts32)
    # Post-CC-NS1 the raw SOURCES carry NORMAL (325-file census); trimesh
    # roundtrips that payload verbatim. Lawful mechanism (AMEND-4): seed the
    # mesh's OWN vertex_normals with the law payload BEFORE export, so the
    # GLB trimesh writes is the law payload (float32 re-pack <= 1e-6). No
    # accessor surgery, no un-law writes.
    mesh.vertex_normals = nvn
    mat = mesh.visual.material.copy() if hasattr(mesh.visual, 'material') else trimesh.visual.material.PBRMaterial()
    mat.baseColorTexture = tex
    mesh.visual = trimesh.visual.texture.TextureVisuals(
        uv=mesh.visual.uv, material=mat, image=tex)
    mesh.export(path, file_type='glb')
    # LAW-CHECK (not a blind trust): exported file's NORMAL payload must
    # equal the law payload within the float32 re-pack tolerance (AMEND-4).
    edata = open(path, 'rb').read()
    if len(edata) < 20 or edata[:4] != b'glTF':
        raise RuntimeError('CC-NS2 export produced a non-GLB file [refusing]')
    eg, eboff, _ = _ns2_kernel.parse_glb(edata)
    eprim = eg['meshes'][0]['primitives'][0]
    if 'NORMAL' not in eprim.get('attributes', {}):
        raise RuntimeError(
            'CC-NS2 refuses: exported GLB carries NO NORMAL payload after '
            'the law-seeded export [refusing unverified output].')
    eacc = eg['accessors'][eprim['attributes']['NORMAL']]
    ebv = eg['bufferViews'][eacc['bufferView']]
    epay = np.frombuffer(edata, dtype='<f4',
                         count=eacc['count'] * 3,
                         offset=eboff + ebv.get('byteOffset', 0)).reshape(-1, 3)
    if int(eacc['count']) != len(nvn):
        raise RuntimeError('CC-NS2 export: NORMAL count != source verts '
                           f'({eacc["count"]} vs {len(nvn)}) [refusing]')
    delta = np.abs(epay.astype(np.float32) - nvn).max()
    zl = np.linalg.norm(nvn, axis=1) < 1e-12
    ezero = np.linalg.norm(epay.astype(np.float32), axis=1) < 1e-12
    if not (zl == ezero).all() or delta > 1e-6:
        raise RuntimeError(
            f'CC-NS2 export: NORMAL payload diverged beyond the float32 '
            f're-pack tolerance (max delta {delta!r}) [refusing]')
    return {'verts': len(verts32), 'faces': len(faces64),
            'weldedVerts': _wc, 'weldPairs': _pairs, 'guardZero': _guard}


def main(ids=None, SRC=None, OUT=None):
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2 refuses to write un-welded normals: add_normals_v2 law '
            'kernel could not be imported (import add_normals_v2 first; the '
            'CC-NS1 law forbids unwelded output) [main pre-build check, no '
            'file writes].')
    src_root = SRC if SRC is not None else globals()['SRC']
    out_root = OUT if OUT is not None else globals()['OUT']
    if ids is not None:
        globals()['IDS'] = list(ids)
    stats_path = os.environ.get('BP_STATS_PATH', BP_STATS_PATH)
    for mid in _effective_ids():
        src = os.path.join(src_root, mid + '.glb')
        scene = trimesh.load(src)
        mesh = list(scene.geometry.values())[0]
        img = mesh.visual.material.baseColorTexture
        # raw copy (untouched TEXTURE, law-guaranteed normals via export())
        raw_out = os.path.join(out_root, mid + '.glb')
        st0 = export(raw_out, mesh, img)
        _log(stats_path, raw_out, st0['verts'], st0['faces'],
             st0['weldedVerts'], st0['weldPairs'], st0['guardZero'])
        # pixelated (posterized texture, same law normals)
        tex = posterize512(img)
        pix_out = os.path.join(out_root, mid + '-pixelated.glb')
        st1 = export(pix_out, mesh, tex)
        _log(stats_path, pix_out, st1['verts'], st1['faces'],
             st1['weldedVerts'], st1['weldPairs'], st1['guardZero'])
        print(mid, 'raw', os.path.getsize(raw_out) // 1024, 'KB, pixelated',
              os.path.getsize(pix_out) // 1024, 'KB',
              f"[{st1['weldedVerts']}w/{st1['weldPairs']}p/{st1['guardZero']}g]")
    return 0


def process(mid):
    """Backward-compatible alias."""
    main(ids=[mid])


if __name__ == '__main__':
    main()
    print('BIOME PIXELATE COMPLETE')
    print('V3 COMPLETE')
