#!/usr/bin/env python3
"""v3.1 (CC-NS2): raw Meshy mesh used AS-IS, WELDED SMOOTH normals, pixelated
colors. Amended wake 45 (Autopilot) toward the CC-NS1/CC-NS2 normal law:

"Get rid of your post processing completely... Remove any post-processing
unless it's purely pixelation of the colors on the skin." (v3 charter.)

v3.1 per body:
  - raw Meshy mesh used AS-IS (no decimation, no UV changes, no hole-fill)
  - WELDED SMOOTH normals via the art-direction/3d kernel law
    (add_normals_v2.law_normals): 1e-4 weld -> area-weighted smooth normals ->
    un-weld to the original vertex order. Fallback normals are a shader bug
    (CC-NS1: black speckles / faceted-shard artifacts); if the kernel is not
    importable this module REFUSES to write un-welded output (RuntimeError,
    marker 'CC-NS2 refuses')
  - texture: color pixelation ONLY (512px nearest + 5-bit posterize, no
    smoothing, no regrade, no palette quantize beyond the bit crush)

Input:  art-direction/3d/assets/races_regen/<name>.glb  (raw Meshy, untouched)
Output: art-direction/3d/assets/races/<name>.glb (2048px tex)
        art-direction/3d/assets/races/<name>-pixelated.glb (512px, 5-bit)

Stats (valspec V-7): one JSONL row per output file at
scratch/ns2-regen-stats.jsonl (override with NS2_STATS_PATH) with ns2Weld,
ts, source, verts, faces, weldedVerts, weldPairs, guardZero.

Module contract for scripts (valspec drivers): SRC, OUT, NAMES are module
attributes; main() runs the loop for NAMES; run_one(name) runs one body; the
__main__ entry calls main() and prints V3 COMPLETE. No os.chdir anywhere.
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

SRC = 'art-direction/3d/assets/races_regen'
OUT = 'art-direction/3d/assets/races'
NAMES = ['dwarf-female','dwarf-male-smith','elf-dawn-refuser-male',
         'human-hunter-female','human-hunter-male','orc-female',
         'orc-male-warrior','undead-ghoul-male','vampire-female','vampire-male-noble']
NS2_STATS_PATH = 'scratch/ns2-regen-stats.jsonl'


def _ns2_weld_normals(verts32, faces):
    """CC-NS2 kernel-law normals; RuntimeError when the kernel is absent."""
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2 refuses to write un-welded normals: add_normals_v2 law '
            'kernel could not be imported (import add_normals_v2 first; the '
            'CC-NS1 law forbids unwelded output).')
    return _ns2_kernel.law_normals(verts32, faces)


def _ns2_log(path, source, verts, faces, welded, pairs, guard):
    """Per-file stats row (one per OUTPUT file; valspec V-7 shape)."""
    row = {'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source': source, 'verts': int(verts), 'faces': int(faces),
           'weldedVerts': int(welded), 'weldPairs': int(pairs),
           'guardZero': int(guard), 'ns2Weld': True}
    os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(row, sort_keys=True) + '\n')


def export(path, verts, faces, uv, mat, tex):
    """Export raw mesh + inject WELDED SMOOTH normals (kernel law).
    uv MUST be len==len(verts). Raises RuntimeError ('CC-NS2 refuses')
    when the CC-NS1 kernel is unavailable — never writes un-welded output."""
    verts32 = np.asarray(verts, dtype=np.float32)
    faces64 = np.asarray(faces, dtype=np.int64)
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2 refuses to write un-welded normals: add_normals_v2 law '
            'kernel could not be imported (import add_normals_v2 first; the '
            'CC-NS1 law forbids unwelded output) [before any geometry/'
            'texture handling, before any file write].')
    # kernel-law NORMAL payload FIRST (no file write happens on fallback)
    vnorm, _nv, _wc, _pairs, _guard = _ns2_kernel.law_normals(verts32, faces64)
    nvn = vnorm.astype(np.float32)
    assert len(nvn) == len(verts32), 'normal count != vertex count'
    # ---- geometry/texture handling only after the payload is law-clean ----
    m = trimesh.Trimesh(verts32, faces64, process=False)
    mat2 = mat.copy()
    mat2.baseColorTexture = tex
    m.visual = trimesh.visual.texture.TextureVisuals(uv=uv, material=mat2, image=tex)
    buf = io.BytesIO(); m.export(buf, file_type='glb')
    data = bytearray(buf.getvalue())
    jl, = struct.unpack_from('<I', data, 12)
    g = json.loads(bytes(data[20:20+jl]))
    prim = g['meshes'][0]['primitives'][0]
    attrs = prim['attributes']
    accessors = g['accessors']; bvs = g['bufferViews']
    binoff = 20 + jl + 8
    blen, = struct.unpack_from('<I', data, 20+jl)
    bin_data = bytearray(data[binoff:binoff+blen])
    while len(bin_data)%4: bin_data += b'\x00'
    start = len(bin_data)
    nv = nvn.tobytes()
    bin_data += nv
    while len(bin_data)%4: bin_data += b'\x00'
    bvs.append({'buffer':0,'byteOffset':start,'byteLength':len(nv),
                'target':34962})
    accessors.append({'bufferView':len(bvs)-1,'componentType':5126,
                      'count':int(len(nvn)),'type':'VEC3',
                      'min':[float(x) for x in vnorm.min(axis=0)],
                      'max':[float(x) for x in vnorm.max(axis=0)]})
    n_acc = len(accessors)-1
    new_attrs = {'NORMAL': n_acc, 'POSITION': attrs['POSITION'],
                 'TEXCOORD_0': attrs['TEXCOORD_0']}
    prim['attributes'] = new_attrs
    g['buffers'][0]['byteLength'] = len(bin_data)
    json_out = json.dumps(g, separators=(',',':')).encode()
    pad = (4-len(json_out)%4)%4; json_out += b' '*pad
    outb = (b'glTF' + struct.pack('<II',2,len(json_out)+8+len(bin_data))
            + struct.pack('<II',len(json_out),0x4E4F534A) + json_out
            + struct.pack('<II',len(bin_data),0x004E4942) + bytes(bin_data))
    with open(path,'wb') as fh: fh.write(outb)
    os.chmod(path, 0o644)
    return {'verts': len(verts32), 'faces': len(faces64),
            'weldedVerts': _wc, 'weldPairs': _pairs, 'guardZero': _guard,
            'normalBytes': len(nv)}


def pixelate_colors(tex):
    """Pure color pixelation: NEAREST downscale + 5-bit posterize. No blur,
    no smoothing, no palette remap - just crush texel density and color depth."""
    t = tex.convert('RGB').resize((512,512), Image.NEAREST)
    arr = np.asarray(t)
    arr = (arr >> 3) << 3
    return Image.fromarray(arr)


def run_one(name, SRC=None, OUT=None):
    """One raw Meshy body -> raw-copy GLB + pixelated GLB, kernel-law normals
    on both, per-file stats rows appended (valspec V-7). Returns the row dict
    pair."""
    src_root = SRC if SRC is not None else globals()['SRC']
    out_root = OUT if OUT is not None else globals()['OUT']
    src = os.path.join(src_root, name + '.glb')
    raw = open(src,'rb').read()
    jl, = struct.unpack_from('<I', raw, 12)
    g = json.loads(raw[20:20+jl])
    prim = g['meshes'][0]['primitives'][0]
    img = g['images'][0]; bv = g['bufferViews'][img['bufferView']]
    binoff = 20 + jl + 8
    blen, = struct.unpack_from('<I', raw, 20+jl)
    tex = Image.open(io.BytesIO(raw[binoff+bv['byteOffset']:binoff+bv['byteOffset']+bv['byteLength']])).convert('RGB')
    m = trimesh.load(src, force='mesh')
    uv = np.asarray(m.visual.uv)
    assert uv is not None and len(uv) == len(m.vertices), name
    mat = m.visual.material
    verts = np.asarray(m.vertices); faces = np.asarray(m.faces)
    stats_path = os.environ.get('NS2_STATS_PATH', NS2_STATS_PATH)
    rows = []
    # raw export: original texture, original mesh, welded smooth normals
    p = os.path.join(out_root, name + '.glb')
    st = export(p, verts, faces, uv, mat, tex)
    rows.append((p, st))
    _ns2_log(stats_path, p, st['verts'], st['faces'], st['weldedVerts'],
             st['weldPairs'], st['guardZero'])
    # pixelated: color-pixelated texture only (same law normals, byte-identical)
    p2 = os.path.join(out_root, name + '-pixelated.glb')
    st2 = export(p2, verts, faces, uv, mat, pixelate_colors(tex))
    rows.append((p2, st2))
    _ns2_log(stats_path, p2, st2['verts'], st2['faces'], st2['weldedVerts'],
             st2['weldPairs'], st2['guardZero'])
    print(f'{name}: raw mesh as-is ({len(faces)} faces), color-pixelated tex, '
          f'welded smooth normals [{st["weldedVerts"]}w/{st["weldPairs"]}p/{st["guardZero"]}g]')
    return rows


def main(names=None, SRC=None, OUT=None):
    n_src = SRC if SRC is not None else globals()['SRC']
    n_out = OUT if OUT is not None else globals()['OUT']
    body = list(names) if names is not None else list(globals()['NAMES'])
    for name in body:
        run_one(name, SRC=n_src, OUT=n_out)
    return 0


def process(name):
    """Backward-compatible alias used by some checkers."""
    run_one(name)


if __name__ == '__main__':
    main()
    print('V3 COMPLETE')
