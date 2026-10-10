"""Diagnostic: colour selected mesh islands and render several views.
blender -b --python cape_diag_render.py -- GLB OUTDIR ISLANDS.json [ACTION FRAME]
ISLANDS.json: {"vertex_groups": {"label": [vertex indices...]}} (glTF vertex order)
"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out, spec = argv[0], Path(argv[1]), json.loads(Path(argv[2]).read_text())
action = argv[3] if len(argv) > 3 else None
frame = int(argv[4]) if len(argv) > 4 else 0
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb, bone_heuristic='BLENDER')
arm = bpy.data.objects['WH_Armature']
body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.modifiers)
for tr in arm.animation_data.nla_tracks:
    tr.mute = True
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
if action:
    act = bpy.data.actions[action]
    arm.animation_data.action = act
    arm.animation_data.action_slot = act.slots[0]
bpy.context.scene.frame_set(frame)
# glTF importer keeps vertex order for a single primitive without merging.
me = body.data
palette = [(1, .1, .1, 1), (.1, .9, .1, 1), (.2, .4, 1, 1), (1, .9, .1, 1),
           (1, .2, 1, 1), (.1, 1, 1, 1)]
attr = me.color_attributes.new('diag', 'FLOAT_COLOR', 'POINT')
for v in attr.data:
    v.color = (.55, .55, .55, 1)
for i, (label, idx) in enumerate(spec['vertex_groups'].items()):
    for j in idx:
        attr.data[j].color = palette[i % len(palette)]
me.color_attributes.active_color = attr
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'VERTEX'
scene.render.resolution_x = scene.render.resolution_y = 700
deps = bpy.context.evaluated_depsgraph_get()
ev = body.evaluated_get(deps)
m = ev.to_mesh()
pts = [ev.matrix_world @ v.co for v in m.vertices]
ev.to_mesh_clear()
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
aim = (lo + hi) / 2
bpy.ops.object.camera_add()
cam = bpy.context.object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = max(hi - lo) * 1.15
scene.camera = cam
for tag, d in [('front', (0, -6, 0)), ('back', (0, 6, 0)), ('left', (6, 0, 0)),
               ('right', (-6, 0, 0)), ('threeq', (2.8, -6, 1.9)), ('backq', (-2.8, 6, 1.9))]:
    cam.location = aim + Vector(d)
    cam.rotation_euler = (aim - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(out / f'{tag}.png')
    bpy.ops.render.render(write_still=True)
print('DIAG_DONE', out)
