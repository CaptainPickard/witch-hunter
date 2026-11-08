"""Rot Mother REF render v2: per-face MATERIAL palette (proven technique).
blender -b -P scratch/rotmother_ref_render2.py -- IN.glb OUT_PREFIX [768]
Palette: dull swamp green body / sickly pale belly / moss blotches / charcoal claws.
Dark neutral bg, single subject centered, 768px, 3 angles.
"""
import bpy, sys, math, mathutils
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
src, pre = argv[0], argv[1]
res = int(argv[2]) if len(argv) > 2 else 768

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
coords = np.empty(len(me.vertices) * 3, dtype=np.float32)
me.vertices.foreach_get('co', coords)
V = coords.reshape(-1, 3)
loop_vidx = np.empty(len(me.loops), dtype=np.int32)
me.loops.foreach_get('vertex_index', loop_vidx)
fv = loop_vidx.reshape(-1, 3)                     # (F,3) blender space
cent = V[fv].mean(axis=1)
n = np.cross(V[fv][:, 1] - V[fv][:, 0], V[fv][:, 2] - V[fv][:, 0])
nl = np.linalg.norm(n, axis=1, keepdims=True); nl[nl == 0] = 1
nn = n / nl

bx, by, bz = V[:, 0], V[:, 1], V[:, 2]        # import space: z = vertical, y = depth
cX, cY, cZ = cent[:, 0], cent[:, 1], cent[:, 2]

# ---------------- per-face masks (vertical = cZ, depth = cY) ----------------
# v2 deltas: pale island smaller (green frame at the gut rim, no frayed
# silhouette edges); moss fewer + upper-torso/head interiors only.
belly = (cZ >= -0.16) & (cZ < -0.00) & (np.abs(cX) < 0.205) & (cY >= 0.03) & (cY <= 0.17)
ribcage = (cZ >= 0.12) & (cZ < 0.79)
legs = (cZ < -0.30) & (np.abs(cX) >= 0.09) & (np.abs(cX) < 0.34)
feet = (cZ < -0.75) & (np.abs(cX) >= 0.075)
arms = ~belly & ~ribcage & ~legs & ~feet & (cZ < 0.79)
crest = (cZ >= 0.79) & (np.abs(cX) >= 0.30)
head = (cZ >= 0.79) & (np.abs(cX) < 0.30)
claw = feet & (cY < 0.12)

# moss blotches: interior upper zones only (head/crest/shoulder-top),
# sparse clustered noise, away from arm silhouette edges
rng = np.random.default_rng(71104)
g = rng.uniform(0, 1, len(cent))
coarse = (g > 0.85) & (g < 0.89)
fine = g > 0.945
upper = (cZ > 0.35) & (arms | crest | head | (ribcage & (cZ > 0.45)))
arm_front = arms & (cY < -0.10)          # avoid arm silhouette edges
moss = ((coarse | fine) & upper & ~arm_front)

# face-level palette decision (sequential precedence: base -> moss -> claw)
face_mat = np.zeros(len(cent), dtype=np.int64)     # 0 skin green
face_mat[ribcage] = 1                              # darker green ribs
face_mat[belly] = 2                                # sickly pale
face_mat[legs] = 1
face_mat[feet] = 1
face_mat[moss] = 3                                 # moss overrides listed zones
face_mat[claw] = 4                                 # charcoal claws win

names = ['skin', 'ribs', 'pale', 'moss', 'claw']
rgbs = {
    'skin': (0.168, 0.251, 0.155),   # dull swamp green
    'ribs': (0.086, 0.145, 0.086),   # darker wet green
    'pale': (0.855, 0.842, 0.700),   # sickly pale wax
    'moss': (0.235, 0.427, 0.196),   # moss green
    'claw': (0.063, 0.066, 0.055),   # charcoal
}
mats = []
for nm in names:
    mat = bpy.data.materials.new(nm)
    rgb = rgbs[nm]
    mat.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)   # Workbench reads THIS
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.42
    mats.append(mat)
me.materials.clear()
for m in mats:
    me.materials.append(m)

# per-loop material index -> per-face assignment via material_index on polys
me.polygons.foreach_set('material_index', face_mat.astype(np.int32))
me.update()
print('PAINT_DONE faces', len(cent), 'skin', int((face_mat == 0).sum()),
      'ribs', int((face_mat == 1).sum()), 'pale', int((face_mat == 2).sum()),
      'moss', int((face_mat == 3).sum()), 'claw', int((face_mat == 4).sum()))

# ---------------- render rig ----------------
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
mn = mathutils.Vector((1e9,) * 3); mx = -mn
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
ctr = (mn + mx) / 2; h = max(mx - mn)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'MATERIAL'
sc.display.shading.show_cavity = True
sc.display.shading.show_shadows = True
sc.render.resolution_x = sc.render.resolution_y = res
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.10, 0.11, 0.12)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = h * 1.15
for name, az in (('front', 0), ('34', 45), ('side', 90)):
    a = math.radians(az); d = h * 3
    cam.location = ctr + mathutils.Vector((d * math.sin(a), -d * math.cos(a), 0))
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{pre}_{name}.png'
    bpy.ops.render.render(write_still=True)
print('RENDER_DONE')