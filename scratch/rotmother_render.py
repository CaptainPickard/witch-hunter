"""Headless Blender QA render: 3 angles (front, 3/4, side) of a GLB.
blender -b -P scratch/rotmother_render.py -- in.glb out_prefix [res]
Workbench, studio light, material/vertex colour if present (flat colour = what the GLB carries)."""
import bpy, sys, math, mathutils
argv = sys.argv[sys.argv.index('--')+1:]
src, pre = argv[0], argv[1]; res = int(argv[2]) if len(argv) > 2 else 1024
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
mn = mathutils.Vector((1e9,)*3); mx = -mn
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
ctr = (mn+mx)/2; h = max(mx-mn)
print('IMPORT_OK meshes', len(objs), 'verts', sum(len(o.data.vertices) for o in objs), 'polys', sum(len(o.data.polygons) for o in objs), 'bbox', tuple(round(v,3) for v in mn), tuple(round(v,3) for v in mx))
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'MATERIAL' if '--clay' not in argv else 'SINGLE'
sc.display.shading.show_cavity = True
sc.display.shading.show_shadows = True
sc.render.resolution_x = sc.render.resolution_y = res
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.18, 0.2, 0.22)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = h*1.15
# Blender is Z-up after glTF import; glTF front (+Z) -> Blender -Y
for name, az in (('front', 0), ('34', 45), ('side', 90)):
    a = math.radians(az); d = h*3
    cam.location = ctr + mathutils.Vector((d*math.sin(a), -d*math.cos(a), 0))
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{pre}_{name}.png'
    bpy.ops.render.render(write_still=True)
print('RENDER_DONE')
