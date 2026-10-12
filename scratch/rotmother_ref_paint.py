"""Rot Mother ref-craft R1.5: region-mask paint for VISUAL verification.
Masks in Blender space (Z up, -Y front) from measured landmarks.
blender -b -P scratch/rotmother_ref_paint.py -- a1.glb out_prefix
"""
import bpy, sys, math, mathutils
import numpy as np

argv = sys.argv[sys.argv.index('--')+1:]
src, pre = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if len(meshes) > 1:
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
obj = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
me = obj.data

coords = np.empty(len(me.vertices)*3, dtype=np.float32)
me.vertices.foreach_get('co', coords)
coords = coords.reshape(-1, 3)
loop_vidx = np.empty(len(me.loops), dtype=np.int32)
me.loops.foreach_get('vertex_index', loop_vidx)
face_v = loop_vidx.reshape(-1, 3)
cent = coords[face_v].mean(axis=1)   # (F,3) Blender space
# face normals (unit)
n = np.cross(coords[face_v][:,1]-coords[face_v][:,0], coords[face_v][:,2]-coords[face_v][:,0])
nl = np.linalg.norm(n, axis=1, keepdims=True); nl[nl==0]=1
n = n/nl
X, Y, Z = cent[:,0], cent[:,1], cent[:,2]
print('CENTS F', len(cent), 'z[', round(Z.min(),3), '..', round(Z.max(),3), ']')

masks = {}
masks['crest']      = (Z > 0.86)
masks['eyes']       = (Z > 0.70) & (Z <= 0.84) & (np.abs(X) < 0.13)
masks['mouth_zone'] = (Z > 0.58) & (Z <= 0.70) & (np.abs(X) < 0.13)
masks['head_rest']  = (Z > 0.642) & (Z <= 0.86) & (np.abs(X) >= 0.13)
masks['neck']       = (Z > 0.495) & (Z <= 0.642)
masks['ribcage']    = (Z > 0.0) & (Z <= 0.495)
masks['belly']      = (Z > -0.24) & (Z <= 0.0)
masks['drips']      = (Z > -0.50) & (Z <= -0.24) & (np.abs(X) < 0.16)
masks['hips']       = (Z > -0.24) & (Z <= -0.10) & (np.abs(X) >= 0.16)
masks['legs']       = (Z <= -0.20) & (np.abs(X) >= 0.10) & (np.abs(X) < 0.26)
masks['feet']       = (Z <= -0.75) & ((np.abs(X) >= 0.26) | (np.abs(Y) > 0.2))
masks['arms_hands'] = None  # leftover: everything else
assigned = np.zeros(len(cent), dtype=bool)
for k, m in masks.items():
    if m is not None:
        assigned |= m
masks['arms_hands'] = ~assigned

# within mouth_zone: split front surface (normal -Y) vs recess floor (normal +Y)
mz = masks['mouth_zone']
masks['mouth_front'] = mz & (Y < -0.15) & (n[:,1] < -0.35)
masks['mouth_recess'] = mz & (n[:,1] > 0.35)
masks['mouth_side'] = mz & ~(masks['mouth_front'] | masks['mouth_recess'])
# eyes: recess = backward-normal in eye band
ey = masks['eyes']
masks['eye_recess'] = ey & (n[:,1] > 0.3)
del masks['eyes'], masks['mouth_zone']

for k, m in masks.items():
    print(f'MASK {k:12s} f{int(m.sum()):7d}')

cols = {
 'crest':(0.90,0.25,0.90,1),'head_rest':(0.95,0.80,0.95,1),'neck':(1.0,0.55,0.10,1),
 'ribcage':(0.20,0.85,0.90,1),'belly':(0.15,0.25,0.95,1),'drips':(0.95,0.15,0.15,1),
 'hips':(0.20,0.90,0.20,1),'legs':(0.95,0.85,0.20,1),'feet':(0.95,0.50,0.05,1),
 'arms_hands':(0.55,0.55,0.60,1),'mouth_front':(0.0,0.0,0.0,1),
 'mouth_recess':(1.0,0.0,0.0,1),'mouth_side':(0.5,0.1,0.1,1),'eye_recess':(0.5,0.0,0.5,1),
}
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and o != obj:
        bpy.data.objects.remove(o, do_unlink=True)
if len(me.materials):
    me.materials.clear()
matidx = np.full(len(me.polygons), len(cols), dtype=np.int32)
names = list(cols.keys())
for i, k in enumerate(names):
    m = masks[k]
    mat = bpy.data.materials.new(k)
    mat.diffuse_color = cols[k]
    me.materials.append(mat)
    matidx[m] = i
me.polygons.foreach_set('material_index', matidx)
me.update()

sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'MATERIAL'
sc.display.shading.show_cavity = True
sc.display.shading.show_shadows = True
sc.render.resolution_x = sc.render.resolution_y = 1024
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.08, 0.08, 0.09)
mn = mathutils.Vector(coords.min(axis=0)); mx = mathutils.Vector(coords.max(axis=0))
ctr = (mn+mx)/2; h = (mx-mn).length
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = h*1.12
for name, az in (('front', 0), ('34', 45), ('side', 90)):
    a = math.radians(az); d = h*3
    cam.location = ctr + mathutils.Vector((d*math.sin(a), -d*math.cos(a), 0))
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{pre}_mask_{name}.png'
    bpy.ops.render.render(write_still=True)
print('PAINT_DONE')