"""Round B capefix proof: exactly three full-size stills from the DELIVERED bandit GLB.
blender -b --factory-startup --python scratch/capefix_proof_render.py -- BODY.mixamo.glb OUTDIR

rest.png         bind pose, no action
walk_mid.png     WH_Walk_Melee at max horizontal foot separation (mid-stride)
attack_mid.png   WH_Attack_High at peak right-hand world speed (mid-swing)
Camera matches rt_render_qa.py (front three-quarter) so slabs compare 1:1 with
scratch/mixamo-fbx/qa/bandit/*.png evidence.
"""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out = Path(argv[0]).resolve(), Path(argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=str(glb), bone_heuristic='BLENDER')
arm = bpy.data.objects['WH_Armature']
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and
          any(m.type == 'ARMATURE' and m.object == arm for m in o.modifiers)]
for tr in arm.animation_data.nla_tracks:
    tr.mute = True
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()

deps = bpy.context.evaluated_depsgraph_get()
pts = []
for ob in meshes:
    ev = ob.evaluated_get(deps)
    me = ev.to_mesh()
    pts.extend(ev.matrix_world @ v.co for v in me.vertices)
    ev.to_mesh_clear()
ground = min(p.z for p in pts)
top = max(p.z for p in pts)
aim = Vector((0, 0, (ground + top) * .5))
bpy.ops.object.camera_add(location=aim + Vector((2.8, -6.0, 1.9)))
cam = bpy.context.object
cam.rotation_euler = (aim - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.0
scene.camera = cam
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, ground - .003))
bpy.context.object.color = (.10, .13, .16, 1)
scene.render.resolution_x = scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.studio_light = 'paint.sl'
scene.display.shading.color_type = 'TEXTURE'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('proof_world')
scene.world.color = (.12, .15, .18)


def bone_world(name):
    return arm.matrix_world @ arm.pose.bones[name].head


def use(action_name):
    act = bpy.data.actions[action_name]
    arm.animation_data.action = act
    arm.animation_data.action_slot = act.slots[0]
    first, last = (int(round(x)) for x in act.frame_range)
    return range(first, last + 1)


def pick(frames, metric):
    best = None
    for f in frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        value = metric(f)
        if best is None or value > best[1]:
            best = (f, value)
    return best


def render(tag, frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    scene.render.filepath = str(out / f'{tag}.png')
    bpy.ops.render.render(write_still=True)


report = {'glb': str(glb), 'renders': {}}
render('rest', 0)
report['renders']['rest'] = {'action': None, 'frame': 0}

frames = use('WH_Walk_Melee')
f, sep = pick(frames, lambda f: (bone_world('L_Foot') - bone_world('R_Foot')).xy.length)
render('walk_mid', f)
report['renders']['walk_mid'] = {'action': 'WH_Walk_Melee', 'frame': f,
                                 'foot_separation_m': sep}

frames = use('WH_Attack_High')
prev = {}
def hand_speed(f):
    p = bone_world('R_Hand').copy()
    speed = (p - prev['p']).length if 'p' in prev else 0.0
    prev['p'] = p
    return speed
f, speed = pick(frames, hand_speed)
render('attack_mid', f)
report['renders']['attack_mid'] = {'action': 'WH_Attack_High', 'frame': f,
                                   'r_hand_m_per_frame': speed}
(out / 'renders.json').write_text(json.dumps(report, indent=2) + '\n')
print('PROOF_DONE', json.dumps(report), flush=True)
