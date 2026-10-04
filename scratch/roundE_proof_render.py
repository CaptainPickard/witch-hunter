"""Round E proof stills from the scatter plan (roundE_proof_scene.py output).
blender -b --python roundE_proof_render.py -- shots.json OUTDIR
Each GLB is imported once and linked-duplicated per placement. Placement =
assets.js groundAlign (min y -> 0) then the game transform (x, y, z, rotY,
uniform scale). glTF (x, y, z) -> Blender (x, -z, y); rotY about glTF +Y =
rotation about Blender +Z. Pixelated textures sampled Closest (NearestFilter).
"""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

shots_p, out = sys.argv[sys.argv.index('--') + 1:][:2]
out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
shots = json.load(open(shots_p))
report = []
for shot in shots:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    templates = {}
    for glb in sorted({o['glb'] for o in shot['objects']}):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=glb)
        new = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in new if o.type == 'MESH']
        bpy.context.view_layer.update()
        zmin = min((o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box)
        for o in meshes:
            for slot in o.material_slots:
                if slot.material and slot.material.use_nodes:
                    for n in slot.material.node_tree.nodes:
                        if n.type == 'TEX_IMAGE':
                            n.interpolation = 'Closest'
        templates[glb] = (meshes, zmin)
        for o in new:
            o.hide_render = True; o.hide_viewport = True
    for ob in shot['objects']:
        meshes, zmin = templates[ob['glb']]
        for m in meshes:
            d = m.copy()                      # linked duplicate (shares mesh data)
            scene.collection.objects.link(d)
            d.hide_render = False; d.hide_viewport = False
            d.parent = None
            d.matrix_world = m.matrix_world.copy()
            d.location.z -= zmin
            s = ob['scale']
            d.matrix_world = (Matrix.Translation((ob['x'], -ob['z'], ob['y'])) @
                              Matrix.Rotation(ob['rotY'], 4, 'Z') @
                              Matrix.Scale(s, 4) @ d.matrix_world)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    g = bpy.data.materials.new('ground'); g.use_nodes = True
    g.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.046, .042, .025, 1)  # 0x3d3a2c linear
    g.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.0
    bpy.context.object.data.materials.append(g)
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 2.6; sun.color = (0.85, 0.88, 0.95)
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), 0, math.radians(35))
    scene.collection.objects.link(so)
    cx, cy, cz = shot['cam']; ax, ay, az = shot['aim']
    cam_loc = Vector((cx, -cz, cy)); aim = Vector((ax, -az, ay))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    cam.rotation_euler = (aim - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = shot['lens']; cam.data.clip_end = 500
    scene.camera = cam
    scene.world = bpy.data.worlds.new('w'); scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.32, .35, .36, 1)  # fog 0x9aa0a3
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    r = scene.render
    r.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    r.resolution_x = 1280; r.resolution_y = 800; r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    r.filepath = str(out / (shot['stem'] + '.png'))
    bpy.ops.render.render(write_still=True)
    report.append({'png': r.filepath, 'objects': len(shot['objects']), 'aim': shot['aim'], 'cam': shot['cam']})
json.dump(report, open(out / 'renders.json', 'w'), indent=1)
print('[proof]', json.dumps(report), flush=True)
