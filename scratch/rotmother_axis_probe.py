"""Definitive axis probe: paint faces by DEPTH band color (import y) at a1.
If creature front = -y_import: front surfaces (mouth recess floor, belly front)
render MAGENTA/RED; back surfaces (skull back) BLUE/GREEN.
blender -b -P scratch/rotmother_axis_probe.py -- a1.glb
"""
import bpy, sys
import numpy as np

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/tmp/wh-worldfeat/scratch/rotmother-qa/dl/a1.glb')
obj = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
me = obj.data
coords = np.empty(len(me.vertices) * 3, dtype=np.float32)
me.vertices.foreach_get('co', coords)
V = coords.reshape(-1, 3)
loop_vidx = np.empty(len(me.loops), dtype=np.int32)
me.loops.foreach_get('vertex_index', loop_vidx)
fv = loop_vidx.reshape(-1, 3)
cent = V[fv].mean(axis=1)
n = np.cross(V[fv][:, 1] - V[fv][:, 0], V[fv][:, 2] - V[fv][:, 0])
nl = np.linalg.norm(n, axis=1, keepdims=True); nl[nl == 0] = 1
nn = n / nl
X, Y, Z = cent[:, 0], cent[:, 1], cent[:, 2]

print('Y span', round(Y.min(), 3), round(Y.max(), 3))
print('Z span', round(Z.min(), 3), round(Z.max(), 3))
front_faces = (nn[:, 1] < -0.5)   # faces pointing -y_import
magenta = front_faces & (Z > 0.55) & (Z < 0.75) & (np.abs(X) < 0.16)
belly_front = front_faces & (Z > -0.30) & (Z < 0.15) & (np.abs(X) < 0.16)
print('front-y faces', int(front_faces.sum()))
print('front-y in head band', int(magenta.sum()))
print('front-y in belly band', int(belly_front.sum()))
print('sample head-band front Y-centroid', round(float(Y[magenta].mean()), 3) if magenta.any() else 'none')
print('sample belly-band front Y-centroid', round(float(Y[belly_front].mean()), 3) if belly_front.any() else 'none')

# paint: magenta = front-facing everywhere, cyan = back-facing
matA = bpy.data.materials.new('front'); matA.diffuse_color = (0.95, 0.1, 0.75, 1)
matB = bpy.data.materials.new('back'); matB.diffuse_color = (0.1, 0.35, 0.9, 1)
me.materials.clear(); me.materials.append(matA); me.materials.append(matB)
matidx = np.where(front_faces, 0, 1).astype(np.int32)
me.polygons.foreach_set('material_index', matidx)
me.update()

objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
mn = V.min(axis=0); mx = V.max(axis=0)
ctr = (mn + mx) / 2; h = float((mx - mn).max())
import mathutils
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'MATERIAL'
sc.render.resolution_x = sc.render.resolution_y = 640
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.08, 0.08, 0.09)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = h * 1.2
cam.location = ctr + mathutils.Vector((0.0, h * 3, 0.0))
cam.rotation_euler = (mathutils.Vector(ctr) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = '/tmp/wh-worldfeat/scratch/rotmother-qa2/axisprobe_frontYcam.png'
bpy.ops.render.render(write_still=True)
cam.location = ctr + mathutils.Vector((0.0, -h * 3, 0.0))
cam.rotation_euler = (mathutils.Vector(ctr) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = '/tmp/wh-worldfeat/scratch/rotmother-qa2/axisprobe_backYcam.png'
bpy.ops.render.render(write_still=True)
print('RENDER_DONE')