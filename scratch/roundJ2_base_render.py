"""Round J2 (from roundJ_base_render.py, ortho now honours azimuth for side views): base close-up of a reach-tree as the game grounds it.
blender -b -P roundJ_base_render.py -- <glb> <out.png> <scale> [persp|ortho] [sink] [azimuthDeg]
Mirrors assets.js groundAlign (lowest vertex -> y=0) and the CONFIG prop
scale, then frames the trunk base from 2m away at 0.5m height."""
import bpy, sys, math
from mathutils import Vector, Euler
argv = sys.argv[sys.argv.index('--') + 1:]
glb, out, scale = argv[0], argv[1], float(argv[2])
sink = float(argv[4]) if len(argv) > 4 else 0.0   # GLB units, as CONFIG.assets.groundSink
azim = math.radians(float(argv[5])) if len(argv) > 5 else 0.0  # camera azimuth about the trunk
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in objs:
    o.scale = (o.scale[0]*scale, o.scale[1]*scale, o.scale[2]*scale)
    o.location = o.location * scale
bpy.context.view_layer.update()
vs = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
zmin = min(v.z for v in vs)
for o in objs:
    o.location.z -= zmin + sink * scale   # groundAlign (+ Round J groundSink)
bpy.context.view_layer.update()
vs = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
H = max(v.z for v in vs)
band = [v for v in vs if 0.10*H < v.z < 0.25*H]
ax = sum((Vector((v.x, v.y, 0)) for v in band), Vector()) / len(band)
bpy.ops.mesh.primitive_plane_add(size=60, location=(ax.x, ax.y, 0))
g = bpy.context.object
gm = bpy.data.materials.new('ground'); gm.diffuse_color = (0.25, 0.32, 0.18, 1)
g.data.materials.append(gm)
cam = bpy.data.cameras.new('c'); cam.lens = 18
co = bpy.data.objects.new('c', cam); bpy.context.scene.collection.objects.link(co)
# trunk surface: nearest verts to the axis in the 0-3m band, on the camera side
low = [v for v in vs if v.z < 3.0]
rt = sorted((Vector((v.x, v.y, 0)) - ax).length for v in low)
rtrunk = rt[len(rt) // 10]
mode = argv[3] if len(argv) > 3 else 'persp'
sc = bpy.context.scene; sc.camera = co
if mode == 'ortho':                      # side elevation of the bottom 4m
    cam.type = 'ORTHO'; cam.ortho_scale = 24
    off = Vector((0, -40, 0)); off.rotate(Euler((0, 0, azim)))
    co.location = ax + off + Vector((0, 0, 3.0))
    co.rotation_euler = (math.radians(90), 0, azim)
    sc.render.resolution_x, sc.render.resolution_y = 1200, 300
else:
    # 2m beyond the outermost ground-level root flare, 0.5m eye height
    rflare = max((Vector((v.x, v.y, 0)) - ax).length for v in vs if v.z < 0.5)
    off = Vector((0, -(rflare + 2.0), 0)); off.rotate(Euler((0, 0, azim)))
    co.location = ax + off + Vector((0, 0, 0.5))
    d = (ax + Vector((0, 0, 1.2))) - co.location
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
sc.display.shading.show_shadows = True; sc.display.shading.show_cavity = True
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.55, 0.6, 0.7)
if mode != 'ortho': sc.render.resolution_x, sc.render.resolution_y = 900, 600
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print(f'ROUNDJ2 az={math.degrees(azim):.0f} {mode} sink={sink} rtrunk={rtrunk:.2f}m {glb} scale={scale} axis=({ax.x:.3f},{ax.y:.3f}) H={H:.3f}m')
