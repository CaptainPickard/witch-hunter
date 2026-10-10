"""Round D proof: exactly 3 full-size stills from the DELIVERED combat-sword.glb.
blender -b --python roundD_proof_render.py -- human-hunter-male.combat-sword.glb OUTDIR
Same fixed camera/floor/shading as swordwire_proof_render.py. Impact frames are
the contract's 1-based source frames (f18 = 0.567s, f13 = 0.400s); baked keys
start at 0, so the rendered key is frame - 1.
"""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector, Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt_render_qa import bounds

glb, out = sys.argv[sys.argv.index('--') + 1:][:2]
out = Path(out).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=str(Path(glb).resolve()), bone_heuristic='BLENDER')
arm = bpy.data.objects['WH_Armature']
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and
          any(m.type == 'ARMATURE' and m.object == arm for m in o.modifiers)]
acts = {a.name: a for a in bpy.data.actions}
for tr in arm.animation_data.nla_tracks:
    tr.mute = True
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
rest_min, rest_max = bounds(meshes)
aim = Vector((0, 0, (rest_min[2] + rest_max[2]) * .5))
bpy.ops.object.camera_add(location=aim + Vector((2.8, -6.0, 1.9)))
cam = bpy.context.object
cam.rotation_euler = (aim - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.3
scene.camera = cam
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, rest_min[2] - .003))
bpy.context.object.color = (.10, .13, .16, 1)
r = scene.render
r.resolution_x = r.resolution_y = 1024
r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'
r.engine = 'BLENDER_WORKBENCH'
sh = scene.display.shading
sh.light, sh.studio_light, sh.color_type = 'STUDIO', 'paint.sl', 'TEXTURE'
sh.show_shadows = sh.show_cavity = True
sh.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('QA_world')
scene.world.color = (.12, .15, .18)


def use(name):
    act = acts[name]
    arm.animation_data.action = act
    arm.animation_data.action_slot = act.slots[0]
    return [int(round(x)) for x in act.frame_range]


shots = [('01-rest', None, 0),
         ('02-ss-slashr2l-mid', 'WH_SS_SlashR2L', 18),
         ('03-ss-overhead-mid', 'WH_SS_Overhead', 13)]
report = []
for stem, name, frame in shots:
    if name:
        key = use(name)[0] + frame - 1
    else:
        arm.animation_data.action = None
        for pb in arm.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        key = 0
    scene.frame_set(key)
    bpy.context.view_layer.update()
    lo, hi = bounds(meshes)
    r.filepath = str(out / (stem + '.png'))
    bpy.ops.render.render(write_still=True)
    report.append({'png': r.filepath, 'clip': name, 'frame': frame, 'key': key,
                   'time_s': key / 30, 'ground_clearance_m': lo[2] - rest_min[2]})
print('[proof]', json.dumps(report), flush=True)
