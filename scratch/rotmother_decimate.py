"""Rot Mother decimation via Blender Quad Decimate (topology-preserving).
60k stage (fs.simplify, clean) -> Blender decimate ratio -> target ~18k.
python3 scratch/rotmother_decimate.py
"""
import numpy as np

SRC = 'art-direction/3d/assets/races_regen/rotmother.glb'
OUT = '/tmp/wh_dec_18k.glb'

# 1) fs.simplify to 60k (proven clean by visual + parity)
import trimesh
import fast_simplification as fs
m = trimesh.load(SRC, force='mesh')
verts = np.asarray(m.vertices)
faces = np.asarray(m.faces)
print('input v', len(verts), 'f', len(faces))
s1v, s1f = fs.simplify(verts, faces, target_count=60000)
print('stage1 60k: v', len(s1v), 'f', len(s1f))
trimesh.Trimesh(s1v, s1f, process=False).export('/tmp/wh_stage1_60k.glb')

# 2) Blender quad decimate (shell subprocess for env isolation)
import subprocess
PY = """
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/tmp/wh_stage1_60k.glb')
obj = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = obj
n0 = len(obj.data.polygons)
md = obj.modifiers.new('dec', 'DECIMATE')
md.ratio = 0.3
bpy.ops.object.modifier_apply(modifier='dec')
n1 = len(obj.data.polygons)
bpy.ops.export_scene.gltf(filepath='/tmp/wh_dec_18k.glb', export_format='GLB')
print('BLENDER_DECIMATE', n0, '->', n1)
"""
r = subprocess.run(['/opt/blender-4.5.4-linux-x64/blender', '-b', '--python-expr', PY],
                   capture_output=True, text=True, timeout=600)
for line in r.stdout.splitlines():
    if 'BLENDER_DECIMATE' in line:
        print(line)

# 3) cc gate on the result
m2 = trimesh.load(OUT, force='mesh', process=False)
print('decimated: v', len(m2.vertices), 'f', len(m2.faces))
print('bounds', m2.bounds.round(3).tolist())