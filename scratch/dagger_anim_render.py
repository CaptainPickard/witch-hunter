"""Render QA cells for the dagger anim swap (Blender headless, Workbench).

    blender -b --factory-startup --python-exit-code 1 --python scratch/dagger_anim_render.py -- \
        GLB CELLS.json OUTDIR [--cell 512]

CELLS.json = {clip: [[label, seconds], ...]}  ->  OUTDIR/<clip>_c<k>.png
Darkwood-neutral scene of the prior dagger QA (neutral grey world, dark-wood
ground at the Root z = -1), front-right 3/4 ortho camera of
scratch/blender_dagger_clips.py preview, dagger-curved proxy @ 0.35 parented
to R_Hand exactly as that preview (QC framing only - this never exports).
Default glTF import (as that preview) so R_Hand bone local +Z = blade.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
GLB, CELLS, OUT = (os.path.abspath(a) for a in argv[:3])
CELL = int(argv[argv.index('--cell') + 1]) if '--cell' in argv else 512
DAGGER_GLB = 'art-direction/3d/assets/weapons/dagger-curved-pixelated.glb'
MEASURE_JSON = 'scratch/dagger_measure.json'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
sc = bpy.context.scene
arm = bpy.data.objects['WH_Armature']
for tr in arm.animation_data.nla_tracks:
    tr.mute = True
arm.animation_data.action = None
os.makedirs(OUT, exist_ok=True)
sc.render.engine = 'BLENDER_WORKBENCH'
sc.render.resolution_x = sc.render.resolution_y = CELL
sc.render.image_settings.file_format = 'PNG'
sh = sc.display.shading
sh.light, sh.studio_light, sh.color_type = 'STUDIO', 'paint.sl', 'TEXTURE'
sh.show_shadows = sh.show_cavity = True
sh.background_type = 'WORLD'
sc.world = bpy.data.worlds.new('W')
sc.world.color = (0.3, 0.3, 0.35)
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, -1.0))
ground = bpy.context.active_object
ground.color = (0.18, 0.16, 0.14, 1)
gm = bpy.data.materials.new('ground')
gm.diffuse_color = (0.18, 0.16, 0.14, 1)
ground.data.materials.append(gm)
meas = json.load(open(MEASURE_JSON))
k = meas['weaponTargetHeight'] / meas['height_m']
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(DAGGER_GLB))
new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
assert len(new) == 1
dag = new[0]
dag.parent = None
dag.matrix_world = Matrix.Diagonal((k, k, k, 1.0)) @ Matrix.Diagonal((meas['bladeAxisY'], 1, meas['bladeAxisY'], 1))
dag.parent = arm
dag.parent_type = 'BONE'
dag.parent_bone = 'R_Hand'
dag.matrix_parent_inverse = Matrix.Translation((0, -arm.data.bones['R_Hand'].length, 0))
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 2.6
sc.collection.objects.link(cam)
sc.camera = cam
tgt = Vector((-0.05, -0.15, -0.1))
cam.location = Vector((-3.4, -6.4, 3.0))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
acts = {a.name: a for a in bpy.data.actions}
fps = sc.render.fps
cells = json.load(open(CELLS))
for name, moments in cells.items():
    act = acts[name]
    arm.animation_data.action = act
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
    for c, (label, t) in enumerate(moments):
        f = t * fps
        fi = int(math.floor(f + 1e-6))
        sc.frame_set(fi, subframe=f - fi)
        sc.render.filepath = os.path.join(OUT, f'{name}_c{c}.png')
        bpy.ops.render.render(write_still=True)
        print(f'[render] {name} c{c} {label} t={t:.3f}s frame {f:.2f}', flush=True)
