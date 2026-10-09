"""DAGGER ANIM SWAP: sword-pro Mixamo -> WH player rig, retimed dagger clips.

io/missions/2026-10-09-dagger-anim-swap.md (A1 probe, A2 bake+retime, A3 splice).
Retarget core is scratch/mixamo_retarget.py verbatim in behaviour (WORLD-space
COPY_ROTATION onto roll-calibrated helper bones, Root still, Hips carries
rotation + proportion-scaled vertical, horizontal displacement removed,
explicit deselect-all/select-target before nla.bake, keys shifted to zero) and
honours the binding corrections list in scratch/mixamo-retarget-report.md.

  # A1: retarget every candidate at its native 30 fps (no retime) -> probe GLB
  blender -b --factory-startup --python-exit-code 1 --python scratch/dagger_anim_retarget.py -- \
      probe PRISTINE.rigged.glb OUT_candidates.glb --clips CANDIDATES.json --log LOG.json
  # A2+A3: retarget the 3 selected, retime to 24 fps dagger clocks, byte-append
  blender ... -- bake PRISTINE.rigged.glb OUT.combat-dagger.glb --clips RETIME.json --log LOG.json

The PRISTINE rig is only read. Blender's temporary export supplies ONLY the new
animation accessors; scratch/glb_append_clips.append_clips writes them after the
untouched pristine JSON/BIN (Blender export can NOT preserve identity).

Retime (bake mode, per clip spec in RETIME.json):
  src_frames [a, i, b]: source window start, impact, end (30 fps source frames)
  out: total seconds; impact_out: output time of the impact frame
  strike_end_out: output time where the uniform strike rate stops (third clip
  only; after it the recover alone is stretched, smoothstep-eased so the
  follow-through HOLDS a beat then SETTLES).
  Uniform part: s(t) = i + (t - impact_out) * k, k = (i - a) / impact_out
  (source frames per output second).  Fast clips: k also == (b - i) / (out -
  impact_out), i.e. one rate end to end.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile

import bpy
from mathutils import Matrix, Vector, Quaternion

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import append_clips
from mixamo_retarget import MAP, mesh_floor

SRC_FPS = 30
OUT_FPS = 24


def log(*a):
    print('[dar]', *a, flush=True)


def setup(inp):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(inp), bone_heuristic='BLENDER')
    target = bpy.data.objects['WH_Armature']
    assert set(target.pose.bones.keys()) == set(MAP) | {'Root'}
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' and
              any(m.type == 'ARMATURE' and m.object == target for m in o.modifiers)]
    assert meshes
    for action in list(bpy.data.actions):
        action.use_fake_user = True
    for track in target.animation_data.nla_tracks:
        track.mute = True
    target.animation_data.action = None
    for pb in target.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
        pb.rotation_mode = 'QUATERNION'
    bpy.context.view_layer.update()
    return target, meshes, mesh_floor(meshes)


def retarget(target, name, fbx):
    """mixamo_retarget.py loop body: returns (action, slot, n_frames, ratio).
    Keys at source frames shifted to zero start, every bone, 200 fcurves."""
    scene = bpy.context.scene
    target.animation_data.action = None
    for track in target.animation_data.nla_tracks:
        track.mute = True
    for pb in target.pose.bones:
        assert not pb.constraints, pb.name
        pb.matrix_basis = Matrix.Identity(4)
    before_objects = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=fbx)
    imported_objects = set(bpy.data.objects) - before_objects
    imported_actions = set(bpy.data.actions) - before_actions
    sources = [o for o in imported_objects if o.type == 'ARMATURE']
    assert len(sources) == 1
    source = sources[0]
    source_action = source.animation_data.action
    assert source_action and source.animation_data.action_slot
    start, end = map(lambda x: int(round(x)), source_action.frame_range)
    scene.render.fps = SRC_FPS
    scene.render.fps_base = 1
    scene.frame_start, scene.frame_end = start, end
    assert end > start
    source_bones = {b.name.removeprefix('mixamorig:'): b for b in source.pose.bones}
    assert set(MAP.values()) <= set(source_bones)
    corrected_names, corrections = {}, {}
    for wh, mx in MAP.items():
        src_rest = source.matrix_world @ source_bones[mx].bone.matrix_local
        dst_rest = target.matrix_world @ target.data.bones[wh].matrix_local
        sq, tq = src_rest.to_quaternion(), dst_rest.to_quaternion()
        sy, ty = sq @ Vector((0, 1, 0)), tq @ Vector((0, 1, 0))
        swing = sy.rotation_difference(ty)
        corrections[wh] = (swing @ sq).inverted() @ tq
        corrected_names[wh] = 'RT_' + wh
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.mode_set(mode='EDIT')
    for wh, mx in MAP.items():
        parent = source.data.edit_bones['mixamorig:' + mx]
        child = source.data.edit_bones.new(corrected_names[wh])
        child.head = parent.head          # helper edit bones need nonzero head/tail
        child.tail = parent.tail
        child.matrix = parent.matrix @ corrections[wh].to_matrix().to_4x4()
        child.parent = parent
        child.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    source_bones = {b.name.removeprefix('mixamorig:'): b for b in source.pose.bones}
    source_scale = source.matrix_world.to_scale().x
    ratio = (sum(target.data.bones[b].length for b in ['L_Thigh', 'L_Shin']) /
             (sum(source_bones[b].bone.length for b in ['LeftUpLeg', 'LeftLeg']) * source_scale))
    hips_rest = (source.matrix_world @ source_bones['Hips'].bone.head_local).z
    target_hips = target.data.bones['Hips'].head_local.copy()
    helper = bpy.data.objects.new('RT_hips_position', None)
    scene.collection.objects.link(helper)
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        source_z = (source.matrix_world @ source_bones['Hips'].head).z
        # Root still, horizontal displacement removed, vertical proportion-scaled.
        helper.location = target_hips + Vector((0, 0, (source_z - hips_rest) * ratio))
        helper.keyframe_insert('location', frame=frame)
    helper_action = helper.animation_data.action
    for wh, mx in MAP.items():
        con = target.pose.bones[wh].constraints.new('COPY_ROTATION')
        con.name = 'RT_rotation'
        con.target = source
        con.subtarget = corrected_names[wh]
        con.target_space = 'WORLD'          # source is Y-up cm (90 deg, 0.01): WORLD reconciles
        con.owner_space = 'WORLD'
        con.mix_mode = 'REPLACE'
    con = target.pose.bones['Hips'].constraints.new('COPY_LOCATION')
    con.target = helper
    con.target_space = 'WORLD'
    con.owner_space = 'WORLD'
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    slot = action.slots.new(id_type='OBJECT', name=target.name)
    target.animation_data.action = action
    target.animation_data.action_slot = slot
    target.animation_data.action_blend_type = 'REPLACE'
    target.animation_data.action_influence = 1
    scene.frame_set(start)
    # nla.bake iterates SELECTED objects: explicit deselect-all + select-target.
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.context.view_layer.update()
    assert list(bpy.context.selected_editable_objects) == [target]
    result = bpy.ops.nla.bake(frame_start=start, frame_end=end, step=1,
        only_selected=False, visual_keying=True, clear_constraints=True,
        clear_parents=False, use_current_action=True, clean_curves=False,
        bake_types={'POSE'}, channel_types={'LOCATION', 'ROTATION', 'SCALE'})
    assert result == {'FINISHED'} and target.animation_data.action == action
    assert len(action.fcurves) == 200, (name, len(action.fcurves))
    assert all(len(fc.keyframe_points) == end - start + 1 for fc in action.fcurves)
    assert all(not pb.constraints for pb in target.pose.bones)
    bpy.data.objects.remove(helper, do_unlink=True)
    bpy.data.actions.remove(helper_action)
    for fc in action.fcurves:
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'
            key.co.x -= start              # explicit shift to zero (slide_to_zero unreliable)
            key.handle_left.x -= start
            key.handle_right.x -= start
    target.animation_data.action = None
    for obj in imported_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for act in imported_actions:
        bpy.data.actions.remove(act)
    for collection in (bpy.data.meshes, bpy.data.armatures, bpy.data.materials, bpy.data.images):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)
    finite = all(math.isfinite(k.co.y) for fc in action.fcurves for k in fc.keyframe_points)
    assert finite, name
    return action, slot, end - start + 1, ratio


def ground_clamp(target, meshes, floor, frames):
    """Raise Hips (basis location) so the SKINNED body (skinned-only
    measurement law) never dips below the rest floor - at every key AND at
    SUB sub-samples inside every key interval (fast retimed keys interpolate
    far apart): each key is raised by the worst deficit of itself and of its
    two adjacent intervals, so the linear Hips lift covers the in-betweens."""
    scene = bpy.context.scene

    def deficit(f):
        fi = int(math.floor(f + 1e-6))
        scene.frame_set(fi, subframe=f - fi)
        bpy.context.view_layer.update()
        return max(0.0, floor - mesh_floor(meshes))
    at_key = [deficit(f) for f in frames]
    SUB = 8
    mids = [max(deficit(a + (b - a) * u / SUB) for u in range(1, SUB))
            for a, b in zip(frames, frames[1:])]
    deltas = [max([at_key[j]] + mids[max(0, j - 1):j + 1]) for j in range(len(frames))]
    pb = target.pose.bones['Hips']
    child_rest = target.data.bones['Hips'].matrix_local
    for f, delta in zip(frames, deltas):
        if delta > 1e-6:
            fi = int(math.floor(f + 1e-6))
            scene.frame_set(fi, subframe=f - fi)
            bpy.context.view_layer.update()
            # Root is identity-animated: rest-rotation inverse maps armature Z to Hips basis.
            pb.location += child_rest.to_3x3().inverted() @ Vector((0, 0, delta))
            pb.keyframe_insert('location', frame=f, group='Hips')
    return max(deltas) if deltas else 0.0


def stash(target, name, action, slot):
    for fc in action.fcurves:
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'
    track = target.animation_data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 0, action)
    strip.action_slot = slot
    track.mute = True
    target.animation_data.action = None


def evaluate_pose(src, frame):
    """Evaluate every pose channel of src at a (fractional) source frame."""
    vals = {}
    for fc in src.fcurves:
        vals[(fc.data_path, fc.array_index)] = fc.evaluate(frame)
    return vals


def hips_yaw(target):
    """Hips yaw about armature +Z (forward = -Y), radians, pose relative to rest."""
    pb = target.pose.bones['Hips']
    m = (pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3()
    f = m @ Vector((0, -1, 0))
    return math.atan2(f.x, -f.y)


def despin(target, src, n, knots):
    """FLAGGED fill edit (attack (3) spin): subtract a piecewise-linear yaw ramp
    through the Hips' own unwrapped yaw at `knots` (source frames), rotating Hips
    about the vertical through its head. Yaw is zero at every knot; the natural
    turn into the cut between knots is kept. Only Hips rot/loc keys change."""
    scene = bpy.context.scene
    target.animation_data.action = src
    target.animation_data.action_slot = src.slots[0]
    yaws = []
    for f in range(n):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        y = hips_yaw(target)
        if yaws:
            while y - yaws[-1] > math.pi:
                y -= 2 * math.pi
            while y - yaws[-1] < -math.pi:
                y += 2 * math.pi
        yaws.append(y)

    def at(x):   # unwrapped yaw at fractional frame
        i = min(int(math.floor(x)), n - 2)
        return yaws[i] + (yaws[i + 1] - yaws[i]) * (x - i)
    kv = [at(k) for k in knots]

    def ramp(f):
        if f <= knots[0]:
            return kv[0]
        for (k0, v0), (k1, v1) in zip(zip(knots, kv), zip(knots[1:], kv[1:])):
            if f <= k1:
                return v0 + (v1 - v0) * (f - k0) / (k1 - k0)
        return kv[-1]
    pb = target.pose.bones['Hips']
    before, after = [], []
    for f in range(n):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        before.append(math.degrees(yaws[f] - yaws[0]))
        h = pb.head.copy()
        r = Matrix.Rotation(-ramp(f), 4, 'Z')
        pb.matrix = Matrix.Translation(h) @ r @ Matrix.Translation(-h) @ pb.matrix
        bpy.context.view_layer.update()
        pb.keyframe_insert('rotation_quaternion', frame=f, group='Hips')
        pb.keyframe_insert('location', frame=f, group='Hips')
        after.append(math.degrees(hips_yaw(target)))
    for fc in src.fcurves:      # re-inserted keys must stay LINEAR for the retime sampler
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'
    target.animation_data.action = None
    return {'knots_src_frames': knots, 'knot_yaw_deg': [round(math.degrees(v), 1) for v in kv],
            'yaw_before_deg_every4': [round(v, 1) for v in before[::4]],
            'yaw_after_deg_every4': [round(v, 1) for v in after[::4]],
            'max_abs_yaw_after_deg': round(max(abs(v) for v in after), 1)}


def source_time(spec, t):
    a, i, b = spec['src_frames']
    ti, T = spec['impact_out'], spec['out']
    k = (i - a) / ti                      # source frames per output second
    se = spec.get('strike_end_out')
    if se is None or t <= se:
        return min(b, max(a, i + (t - ti) * k))
    # third clip: stretched recover from s(se) to b, smoothstep-eased
    s0 = i + (se - ti) * k
    u = (t - se) / (T - se)
    u = u * u * (3 - 2 * u)
    return s0 + (b - s0) * u


def retime(target, name, src, spec):
    scene = bpy.context.scene
    scene.render.fps = OUT_FPS
    L = round(spec['out'] * OUT_FPS, 4)
    frames = sorted(set([float(f) for f in range(int(math.floor(L + 1e-6)) + 1)] + [L]))
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=target.name)
    target.animation_data.action = act
    target.animation_data.action_slot = slot
    prev = {}
    samples = []
    for f in frames:
        t = f / OUT_FPS
        s = source_time(spec, t)
        samples.append((round(t, 4), round(s, 4)))
        v = evaluate_pose(src, s)
        for pb in target.pose.bones:
            base = pb.path_from_id()
            q = Quaternion([v[(base + '.rotation_quaternion', c)] for c in range(4)]).normalized()
            if pb.name in prev and q.dot(prev[pb.name]) < 0:
                q.negate()
            prev[pb.name] = q.copy()
            pb.rotation_quaternion = q
            pb.location = [v[(base + '.location', c)] for c in range(3)]
            pb.scale = [v[(base + '.scale', c)] for c in range(3)]
            for prop in ('rotation_quaternion', 'location', 'scale'):
                pb.keyframe_insert(prop, frame=f, group=pb.name)
    assert len(act.fcurves) == 200 and all(len(fc.keyframe_points) == len(frames) for fc in act.fcurves)
    for fc in act.fcurves:      # LINEAR before the ground clamp evaluates in-betweens (glTF ships LINEAR)
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'
    return act, slot, frames, samples


def export_and_append(inp, out, names):
    target = bpy.data.objects['WH_Armature']
    target.animation_data.action = None
    with tempfile.TemporaryDirectory(prefix='wh-dagan-') as temp:
        export_path = str(Path(temp) / 'animations.glb')
        bpy.ops.export_scene.gltf(filepath=export_path, export_format='GLB',
            export_animation_mode='ACTIONS', export_skins=True, export_def_bones=False,
            export_apply=False, export_image_format='AUTO', export_yup=True,
            export_force_sampling=False, export_optimize_animation_size=False,
            export_optimize_animation_keep_anim_armature=True,
            export_anim_slide_to_zero=True, export_reset_pose_bones=True,
            export_frame_range=False, export_extras=False,
            export_cameras=False, export_lights=False)
        doc = append_clips(inp, export_path, out, names)
    chans = {a['name']: len(a['channels']) for a in doc['animations'] if a['name'] in names}
    assert all(c == 60 for c in chans.values()) and sorted(chans) == sorted(names), chans
    return chans


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
    target, meshes, floor = setup(inp)
    rep = {'mode': args.mode, 'input': str(inp), 'output': str(out), 'ground_z': floor, 'clips': {}}
    names = []
    for name, c in spec.items():
        fbx = c['fbx'] if isinstance(c, dict) else c
        assert Path(fbx).is_file() and 'mixamo-fbx/swordpack' in fbx, fbx
        src, slot, n, ratio = retarget(target, ('SRC_' + name) if args.mode == 'bake' else name, fbx)
        r = {'fbx': fbx, 'src_frames': n, 'src_sec': (n - 1) / SRC_FPS, 'leg_scale_ratio': ratio}
        if args.mode == 'probe':
            target.animation_data.action = src
            target.animation_data.action_slot = slot
            r['max_ground_correction_m'] = ground_clamp(target, meshes, floor, [float(f) for f in range(n)])
            stash(target, name, src, slot)
        else:
            if 'despin_knots' in c:
                r['despin'] = despin(target, src, n, c['despin_knots'])
                log(name, 'despin', json.dumps(r['despin']))
            act, aslot, frames, samples = retime(target, name, src, c)
            r['max_ground_correction_m'] = ground_clamp(target, meshes, floor, frames)
            stash(target, name, act, aslot)
            bpy.data.actions.remove(src)
            r.update({'retime': {k: c[k] for k in c if k != 'fbx'}, 'out_frames': frames[-1],
                      'out_sec': frames[-1] / OUT_FPS, 'keys': len(frames), 'samples_t_srcframe': samples})
        rep['clips'][name] = r
        names.append(name)
        log(name, json.dumps({k: v for k, v in r.items() if k != 'samples_t_srcframe'}))
    bpy.context.scene.render.fps = SRC_FPS if args.mode == 'probe' else OUT_FPS
    bpy.context.scene.frame_start = 0
    rep['channels'] = export_and_append(inp, out, names)
    rep['output_bytes'] = out.stat().st_size
    rep['nla_tracks'] = [t.name for t in target.animation_data.nla_tracks]
    rep['status'] = 'pass'
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(rep, indent=1) + '\n')
    log('PASS', out)


if __name__ == '__main__':
    main()
