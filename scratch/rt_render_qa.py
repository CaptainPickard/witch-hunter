"""Render mid/end frames from the DELIVERED GLB, not the working Blender scene.
blender -b --python rt_render_qa.py -- BODY.mixamo.glb --clips clips.json --out DIR
"""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector, Matrix


def bounds(meshes):
    deps = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        ev = obj.evaluated_get(deps)
        me = ev.to_mesh()
        points.extend(ev.matrix_world @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    return ([min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('glb')
    p.add_argument('--clips', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    names = list(json.loads(Path(args.clips).read_text()))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    bpy.ops.import_scene.gltf(filepath=str(Path(args.glb).resolve()), bone_heuristic='BLENDER')
    arm = bpy.data.objects['WH_Armature']
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    acts = {a.name: a for a in bpy.data.actions}
    for tr in arm.animation_data.nla_tracks:
        tr.mute = True
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    rest_min, rest_max = bounds(meshes)
    ground = rest_min[2]
    # Keep one fixed camera for every pose. Floor stays at the canonical rest
    # ground; do not move either the body or floor for individual screenshots.
    aim = Vector((0, 0, (rest_min[2] + rest_max[2]) * .5))
    bpy.ops.object.camera_add(location=aim + Vector((2.8, -6.0, 1.9)))
    cam = bpy.context.object
    cam.rotation_euler = (aim - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 3.3
    scene.camera = cam
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, ground - .003))
    floor = bpy.context.object
    floor.name = 'QA_floor'
    floor.color = (.10, .13, .16, 1)
    scene.render.resolution_x = 700
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.studio_light = 'paint.sl'
    scene.display.shading.color_type = 'TEXTURE'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = 'WORLD'
    scene.world = bpy.data.worlds.new('QA_world')
    scene.world.color = (.12, .15, .18)
    report = {'glb': str(Path(args.glb).resolve()), 'ground_z': ground, 'clips': {}}
    for name in names:
        act = acts[name]
        arm.animation_data.action = act
        arm.animation_data.action_slot = act.slots[0]
        first, last = act.frame_range
        entries = []
        for tag, f in [('mid', int(round((first+last)/2))), ('end', int(round(last)))]:
            scene.frame_set(f)
            bpy.context.view_layer.update()
            lo, hi = bounds(meshes)
            path = out / (name + ('_end' if tag == 'end' else '') + '.png')
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            entries.append({'pose': tag, 'frame': f, 'png': str(path), 'bbox_min': lo,
                            'bbox_max': hi, 'ground_clearance_m': lo[2]-ground})
        report['clips'][name] = entries
        (out/'renders.json').write_text(json.dumps(report, indent=2)+'\n')
    print('QA_RENDER_PASS', len(report['clips']), flush=True)


if __name__ == '__main__':
    main()
