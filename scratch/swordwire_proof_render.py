"""Round C proof: exactly 3 full-size stills from the DELIVERED combat-sword.glb.
blender -b --python swordwire_proof_render.py -- human-hunter-male.combat-sword.glb OUTDIR
Same fixed camera/floor/shading as rt_render_qa.py. Walk frame = max ankle spread.
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


def ankle_spread(f):
    scene.frame_set(f)
    pl, pr = arm.pose.bones['L_Foot'], arm.pose.bones['R_Foot']
    return ((arm.matrix_world @ pl.head) - (arm.matrix_world @ pr.head)).length


shots = []
first, last = use('WH_SwordIdle')
shots.append(('01_rest_WH_SwordIdle', 'WH_SwordIdle', first))
first, last = use('WH_SwordWalk')
shots.append(('02_midstride_WH_SwordWalk', 'WH_SwordWalk',
              max(range(first, last + 1), key=ankle_spread)))
first, last = use('WH_ShieldCrouchIdle')
shots.append(('03_midblock_WH_ShieldCrouchIdle', 'WH_ShieldCrouchIdle', (first + last) // 2))
report = []
for stem, name, frame in shots:
    use(name)
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    lo, hi = bounds(meshes)
    r.filepath = str(out / (stem + '.png'))
    bpy.ops.render.render(write_still=True)
    report.append({'png': r.filepath, 'clip': name, 'frame': frame,
                   'ground_clearance_m': lo[2] - rest_min[2]})
(out / 'renders.json').write_text(json.dumps(report, indent=2) + '\n')
print('[proof]', json.dumps(report), flush=True)
