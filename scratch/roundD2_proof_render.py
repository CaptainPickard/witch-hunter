"""Round D2 proof: 3 stills, each = fire-prop GLB alone + one warm PointLight
at the NEW socket (Round D2 CONFIG.lightSockets offset * scale, heightFraction * H *
scale, rotY 0) + a small emissive sphere at the light as the flame stand-in.
blender -b --python roundD2_proof_render.py -- WH_ROOT OUTDIR
glTF (x, y, z) -> Blender (x, -z, y); prop is ground-aligned like
assets.js (min y -> 0, x/z origin kept).
"""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

root, out = sys.argv[sys.argv.index('--') + 1:][:2]
out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
A = root + '/art-direction/3d/assets/'
shots = [  # stem, glb, scale, heightFraction, offset [x, z] (CONFIG Round D2), watts
    ('01-lantern-post', A + 'church-kit/lantern-post-pixelated.glb', 2.4, 0.72, (-0.18, 0.0), 120),
    ('02-waymarker', A + 'biome_library/b3-waymarker-pixelated.glb', 1.9, 0.67, (0.0, 0.35), 120),
    ('03-campfire', A + 'biome_library/m15-bandit-campfire-pixelated.glb', 1.8, 0.55, (0.0, 0.0), 60),
]
report = []
for stem, glb, s, hf, (ox, oz), watts in shots:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=glb)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    zmin = min(p.z for p in pts); zmax = max(p.z for p in pts)
    H = zmax - zmin
    for o in [o for o in bpy.data.objects if o.parent is None]:
        o.location.z -= zmin
        o.location *= s
        o.scale *= s
    bpy.context.view_layer.update()
    lx, ly, lz = ox * s, -oz * s, H * s * hf
    L = Vector((lx, ly, lz))
    ld = bpy.data.lights.new('fire', 'POINT'); ld.energy = watts
    ld.color = (1.0, 0.62, 0.3); ld.shadow_soft_size = 0.02
    ld.use_shadow = False  # game pool lights have no castShadow
    lo = bpy.data.objects.new('fire', ld); lo.location = L
    scene.collection.objects.link(lo)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035 * s, location=L)
    sph = bpy.context.object
    m = bpy.data.materials.new('flame'); m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Emission Color'].default_value = (1, .7, .3, 1)
    bs.inputs['Emission Strength'].default_value = 25
    sph.data.materials.append(m); sph.visible_shadow = False
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    g = bpy.data.materials.new('ground'); g.use_nodes = True
    g.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.25, .25, .22, 1)
    bpy.context.object.data.materials.append(g)
    top = H * s
    aim = Vector((lx, ly, top * 0.5))
    cam_loc = aim + Vector((top * 0.9, -top * 1.6, top * 0.35)) if stem != '03-campfire' \
        else aim + Vector((top * 3.5, -top * 6.0, top * 4.5))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    cam.rotation_euler = (aim - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 35
    scene.camera = cam
    scene.world = bpy.data.worlds.new('w'); scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.01, .012, .02, 1)
    r = scene.render
    r.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    r.resolution_x = r.resolution_y = 1024; r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    r.filepath = str(out / (stem + '.png'))
    bpy.ops.render.render(write_still=True)
    report.append({'png': r.filepath, 'H_local': round(H, 4), 'light_blender_xyz': [round(v, 3) for v in L]})
print('[proof]', json.dumps(report), flush=True)
