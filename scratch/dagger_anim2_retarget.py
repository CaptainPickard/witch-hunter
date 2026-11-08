"""DAG-SWIPES (io/missions/2026-10-10-dag-swipes.md): standing swordpack swipes
-> WH_Dag* chain. Thin driver over scratch/dagger_anim_retarget.py (the round-9
engine, unchanged): retarget = mixamo_retarget WORLD-constraint core, retime =
24 fps uniform-rate window with an early impact (slot 3: same strike rate, only
the recover stretched, smoothstep hold + settle), keys LINEAR before the ground
clamp (every key + 8 sub-samples), byte-append via glb_append_clips.

Sources are scratch/dag-swipes/src/ COPIES of the read-only swordpack FBXs.

  blender -b --factory-startup --python-exit-code 1 --python scratch/dagger_anim2_retarget.py -- \
      probe|bake PRISTINE.rigged.glb OUT.glb --clips SPEC.json --log LOG.json

Also logs, per clip, the Hips head height above the rig floor (armature Z) at
every output key (bake) / native frame (probe) for the R2 no-crouch assert.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dagger_anim_retarget as D


def hips_heights(target, act, slot, frames, floor):
    scene = bpy.context.scene
    target.animation_data.action = act
    target.animation_data.action_slot = slot
    out = []
    for f in frames:
        fi = int(f)
        scene.frame_set(fi, subframe=f - fi)
        bpy.context.view_layer.update()
        out.append(round((target.matrix_world @ target.pose.bones['Hips'].head).z - floor, 5))
    target.animation_data.action = None
    return out


def fix_quat_signs(out, names):
    """The glTF exporter can hand consecutive rotation keys opposite signs (seen
    on the thighs at the 24 fps retime's ~90 deg steps). three.js slerp takes the
    short arc anyway, but nlerp evaluators (Blender fcurves = what the ground
    clamp measured, the verify FK) would swing through the long arc. Negate keys
    for dot >= 0 continuity: identical rotations, patched in place inside the
    APPENDED accessors only (JSON + pristine BIN prefix untouched)."""
    import struct
    from glb_append_clips import parse
    raw = bytearray(Path(out).read_bytes())
    doc, blob = parse(out)
    bin_at = 12 + 8 + struct.unpack_from('<I', raw, 12)[0] + 8
    assert bytes(raw[bin_at:bin_at + len(blob)]) == blob
    fixed = {}
    for an in doc['animations']:
        if an['name'] not in names:
            continue
        n = 0
        for ch in an['channels']:
            if ch['target']['path'] != 'rotation':
                continue
            acc = doc['accessors'][an['samplers'][ch['sampler']]['output']]
            view = doc['bufferViews'][acc['bufferView']]
            assert acc['componentType'] == 5126 and acc['type'] == 'VEC4' and view.get('byteStride', 16) == 16
            base = bin_at + view.get('byteOffset', 0) + acc.get('byteOffset', 0)
            prev = None
            for k in range(acc['count']):
                q = struct.unpack_from('<4f', raw, base + 16 * k)
                if prev is not None and sum(a * b for a, b in zip(q, prev)) < 0:
                    q = tuple(-c for c in q)
                    struct.pack_into('<4f', raw, base + 16 * k, *q)
                    n += 1
                prev = q
        fixed[an['name']] = n
    Path(out).write_bytes(bytes(raw))
    return fixed


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['probe', 'bake'])
    p.add_argument('input')
    p.add_argument('output')
    p.add_argument('--clips', required=True)
    p.add_argument('--log', required=True)
    args = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    inp, out = Path(args.input).resolve(), Path(args.output).resolve()
    assert inp != out and inp.name.endswith('.rigged.glb')
    spec = json.loads(Path(args.clips).read_text())
    target, meshes, floor = D.setup(inp)
    rep = {'mode': args.mode, 'input': str(inp), 'output': str(out), 'ground_z': floor, 'clips': {}}
    names = []
    for name, c in spec.items():
        fbx = c['fbx'] if isinstance(c, dict) else c
        assert Path(fbx).is_file() and 'scratch/dag-swipes/src/' in fbx, fbx
        src, slot, n, ratio = D.retarget(target, ('SRC_' + name) if args.mode == 'bake' else name, fbx)
        r = {'fbx': fbx, 'src_frames': n, 'src_sec': (n - 1) / D.SRC_FPS, 'leg_scale_ratio': ratio}
        # unclamped source Hips height on the WH rig, every native frame
        bpy.context.scene.render.fps = D.SRC_FPS
        r['src_hips_h'] = hips_heights(target, src, slot, [float(f) for f in range(n)], floor)
        if args.mode == 'probe':
            target.animation_data.action = src
            target.animation_data.action_slot = slot
            r['max_ground_correction_m'] = D.ground_clamp(target, meshes, floor, [float(f) for f in range(n)])
            D.stash(target, name, src, slot)
        else:
            act, aslot, frames, samples = D.retime(target, name, src, c)
            r['max_ground_correction_m'] = D.ground_clamp(target, meshes, floor, frames)
            r['out_hips_h'] = hips_heights(target, act, aslot, frames, floor)
            D.stash(target, name, act, aslot)
            bpy.data.actions.remove(src)
            r.update({'retime': {k: c[k] for k in c if k != 'fbx'}, 'out_frames': frames[-1],
                      'out_sec': frames[-1] / D.OUT_FPS, 'keys': len(frames), 'samples_t_srcframe': samples})
        rep['clips'][name] = r
        names.append(name)
        D.log(name, json.dumps({k: v for k, v in r.items() if k not in ('samples_t_srcframe', 'src_hips_h', 'out_hips_h')}))
    bpy.context.scene.render.fps = D.SRC_FPS if args.mode == 'probe' else D.OUT_FPS
    bpy.context.scene.frame_start = 0
    rep['channels'] = D.export_and_append(inp, out, names)
    rep['quat_sign_keys_fixed'] = fix_quat_signs(out, names)
    D.log('quat sign continuity', rep['quat_sign_keys_fixed'])
    rep['output_bytes'] = out.stat().st_size
    rep['nla_tracks'] = [t.name for t in target.animation_data.nla_tracks]
    rep['status'] = 'pass'
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(rep, indent=1) + '\n')
    D.log('PASS', out)


if __name__ == '__main__':
    main()
