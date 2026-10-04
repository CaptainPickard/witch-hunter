"""Mixamo -> WH visual constraint bake, isolated actions + byte-preserving append.

blender -b --factory-startup --python-exit-code 1 --python scratch/mixamo_retarget.py -- \
    TARGET.rigged.glb TARGET.mixamo.glb --clips scratch/mixamo_bandit.json --log LOG.json

Never write the imported GLB back out. Blender's temporary export supplies ONLY
new animation accessors to glb_append_clips; all original JSON/BIN data survives.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import append_clips, parse

# The actual rig has 20 bones, including Hips (omitted from the initial brief).
# Root is the ground/gameplay anchor. Driving it with pelvis rotation incorrectly
# pivots the entire character about its feet; animate Hips instead.
MAP = {'Hips': 'Hips', 'Spine': 'Spine1', 'Chest': 'Spine2', 'Neck': 'Neck',
       'Head': 'Head', 'L_Shoulder': 'LeftShoulder', 'R_Shoulder': 'RightShoulder',
       'L_UpperArm': 'LeftArm', 'R_UpperArm': 'RightArm',
       'L_Forearm': 'LeftForeArm', 'R_Forearm': 'RightForeArm',
       'L_Hand': 'LeftHand', 'R_Hand': 'RightHand',
       'L_Thigh': 'LeftUpLeg', 'R_Thigh': 'RightUpLeg',
       'L_Shin': 'LeftLeg', 'R_Shin': 'RightLeg',
       'L_Foot': 'LeftFoot', 'R_Foot': 'RightFoot'}


def log(*args):
    print('[rt]', *args, flush=True)


def mesh_floor(objects):
    deps = bpy.context.evaluated_depsgraph_get()
    floor = float('inf')
    for ob in objects:
        evaluated = ob.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        floor = min(floor, min((evaluated.matrix_world @ v.co).z for v in mesh.vertices))
        evaluated.to_mesh_clear()
    return floor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--clips', required=True)
    parser.add_argument('--log', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    inp, out = Path(args.input).resolve(), Path(args.output).resolve()
    assert inp != out and out.name.endswith('.mixamo.glb'), 'Use a separate .mixamo.glb'
    manifest_path = Path(args.clips).resolve()
    clips = json.loads(manifest_path.read_text())
    repo = Path(__file__).resolve().parent.parent
    clips = {n: str((repo / p).resolve()) for n, p in clips.items()}
    assert clips and all(Path(p).is_file() for p in clips.values())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(inp), bone_heuristic='BLENDER')
    target = bpy.data.objects['WH_Armature']
    assert set(target.pose.bones.keys()) == set(MAP) | {'Root'}
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    scene = bpy.context.scene
    originals = list(bpy.data.actions)
    for action in originals:
        action.use_fake_user = True
    original_strips = [(track, track.mute, [(s, s.action) for s in track.strips])
                       for track in target.animation_data.nla_tracks]
    for track, _, _ in original_strips:
        track.mute = True
    target.animation_data.action = None
    for pb in target.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
        pb.rotation_mode = 'QUATERNION'
    bpy.context.view_layer.update()
    floor = mesh_floor(meshes)
    report = {'input': str(inp), 'output': str(out), 'fps': 30, 'clips': {},
              'ground_z': floor, 'root_motion': 'Root fixed; Hips vertical only',
              'constraint_space': 'WORLD: FBX armature is Y-up centimeters; WH is Z-up meters'}
    for name, fbx in clips.items():
        try:
            # Drop previous active action, mute all strips, reset every pose channel.
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
            # FBX import changes scene settings: never reuse the previous clip range.
            scene.render.fps = 30
            scene.render.fps_base = 1
            scene.frame_start, scene.frame_end = start, end
            assert end > start
            source_bones = {b.name.removeprefix('mixamorig:'): b for b in source.pose.bones}
            assert set(MAP.values()) <= set(source_bones)
            # Preserve the target's bone roll while following source bone
            # directions. Direct absolute-rotation copy twists WH armor/limbs
            # because Mixamo and WH bone-local X/Z axes are not equivalent.
            # A zero-key child on each source bone adds only the calibrated
            # local-Y twist. Its inherited evaluated pose remains the driver.
            corrected_names = {}
            corrections = {}
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
                child.head = parent.head
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
                helper.location = target_hips + Vector((0, 0, (source_z - hips_rest) * ratio))
                helper.keyframe_insert('location', frame=frame)
            helper_action = helper.animation_data.action
            for wh, mx in MAP.items():
                pb = target.pose.bones[wh]
                con = pb.constraints.new('COPY_ROTATION')
                con.name = 'RT_rotation'
                con.target = source
                con.subtarget = corrected_names[wh]
                # Unlike the brief's POSE suggestion, these rigs' object spaces
                # differ by 90 degrees and 100x. WORLD explicitly reconciles both.
                con.target_space = 'WORLD'
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
            # Critical fix: active != selected. nla.bake iterates selected objects.
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
            assert all(len(fc.keyframe_points) == end-start+1 for fc in action.fcurves)
            assert all(not pb.constraints for pb in target.pose.bones)
            bpy.data.objects.remove(helper, do_unlink=True)
            bpy.data.actions.remove(helper_action)
            # Ground clamp after proportional pelvis transfer: use the actual
            # deformed mesh, not a camera/framing trick or a bone-head estimate.
            offsets = []
            for frame in range(start, end + 1):
                scene.frame_set(frame)
                bpy.context.view_layer.update()
                delta = max(0.0, floor - mesh_floor(meshes))
                offsets.append(delta)
                if delta > 1e-6:
                    pb = target.pose.bones['Hips']
                    world_delta = Vector((0, 0, delta))
                    parent_rest = target.data.bones['Root'].matrix_local
                    child_rest = target.data.bones['Hips'].matrix_local
                    # Root is identity animated, so rest-rotation inverse maps
                    # armature translation to Hips basis location channels.
                    pb.location += child_rest.to_3x3().inverted() @ world_delta
                    pb.keyframe_insert('location', frame=frame)
            for fc in action.fcurves:
                for key in fc.keyframe_points:
                    key.interpolation = 'LINEAR'
                    # glTF slide-to-zero does not shift positive-start actions
                    # in every ACTIONS path; normalize baked keys explicitly.
                    key.co.x -= start
                    key.handle_left.x -= start
                    key.handle_right.x -= start
            track = target.animation_data.nla_tracks.new()
            track.name = name
            strip = track.strips.new(name, 0, action)
            strip.action_slot = slot
            track.mute = True
            target.animation_data.action = None
            for obj in imported_objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            for act in imported_actions:
                bpy.data.actions.remove(act)
            for collection in (bpy.data.meshes, bpy.data.armatures, bpy.data.materials,
                               bpy.data.images):
                for block in list(collection):
                    if block.users == 0:
                        collection.remove(block)
            for old_track, _, strips in original_strips:
                assert [(s, s.action) for s in old_track.strips] == strips
            report['clips'][name] = {'src': fbx, 'frame_start': start, 'frame_end': end,
                'samples': end-start+1, 'duration_seconds': (end-start)/30,
                'fcurves': len(action.fcurves), 'leg_scale_ratio': ratio,
                'max_ground_correction_m': max(offsets), 'status': 'baked'}
            Path(args.log).write_text(json.dumps(report, indent=2) + '\n')
            log(name, start, end, 'fcurves', len(action.fcurves))
        except Exception as exc:
            report['clips'][name] = {'status': 'failed', 'error': str(exc), 'src': fbx}
            Path(args.log).write_text(json.dumps(report, indent=2) + '\n')
            raise
    target.animation_data.action = None
    for track, muted, _ in original_strips:
        track.mute = muted
    scene.frame_start = 0
    scene.frame_end = max(c['frame_end'] for c in report['clips'].values())
    with tempfile.TemporaryDirectory(prefix='wh-retarget-') as temp:
        export_path = str(Path(temp) / 'animations.glb')
        bpy.ops.export_scene.gltf(filepath=export_path, export_format='GLB',
            export_animation_mode='ACTIONS', export_skins=True, export_def_bones=False,
            export_apply=False, export_image_format='AUTO', export_yup=True,
            export_force_sampling=False, export_optimize_animation_size=False,
            export_optimize_animation_keep_anim_armature=True,
            export_anim_slide_to_zero=True, export_reset_pose_bones=True,
            export_frame_range=False, export_extras=False,
            export_cameras=False, export_lights=False)
        doc = append_clips(inp, export_path, out, list(clips))
        for anim in doc['animations']:
            if anim['name'] in report['clips']:
                assert len(anim['channels']) == 60
                report['clips'][anim['name']]['channels'] = len(anim['channels'])
    report['output_bytes'] = out.stat().st_size
    report['status'] = 'pass'
    Path(args.log).write_text(json.dumps(report, indent=2) + '\n')
    log('PASS', out)


if __name__ == '__main__':
    main()
