"""Round G proof stills from roundG_proof_scene.py shots: roundF_proof_render.py
with shadows OFF (contract) and no night/lantern branch use.
blender -b --python roundG_proof_render.py -- shots.json OUTDIR
Each GLB is imported once and linked-duplicated per placement. Placement =
assets.js groundAlign (min y -> 0) then the game transform (x, y, z, rotY,
per-axis scale sx/sy/sz in glTF axes). glTF (x, y, z) -> Blender (x, -z, y):
glTF X scale = Blender X, glTF Y = Blender Z, glTF Z = Blender Y. Pixelated
textures sampled Closest (NearestFilter). Night shots: dim moon + a warm
point light at the lantern socket (the emissive glass comes from the GLB).
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
            d = m.copy()
            scene.collection.objects.link(d)
            d.hide_render = False; d.hide_viewport = False
            d.parent = None
            # groundAlign lift as a matrix (setting .location then reading
            # .matrix_world in the same tick returns the STALE matrix)
            S = Matrix.Diagonal((ob['sx'], ob['sz'], ob['sy'], 1.0))
            d.matrix_world = (Matrix.Translation((ob['x'], -ob['z'], ob['y'])) @
                              Matrix.Rotation(ob['rotY'], 4, 'Z') @ S @
                              Matrix.Translation((0, 0, -zmin)) @ m.matrix_world)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    g = bpy.data.materials.new('ground'); g.use_nodes = True
    g.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.046, .042, .025, 1)  # 0x3d3a2c linear
    g.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.0
    bpy.context.object.data.materials.append(g)
    night = shot.get('night')
    sun = bpy.data.lights.new('sun', 'SUN')
    sun.energy = 0.35 if night else 2.6
    sun.color = (0.62, 0.70, 0.95) if night else (0.85, 0.88, 0.95)
    sun.use_shadow = False
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), 0, math.radians(35))
    scene.collection.objects.link(so)
    if shot.get('light'):
        L = shot['light']
        pl = bpy.data.lights.new('lantern', 'POINT'); pl.energy = L['watts']
        pl.color = (1.0, 0.69, 0.38); pl.shadow_soft_size = 0.15
        pl.use_shadow = False
        po = bpy.data.objects.new('lantern', pl); po.location = (L['x'], -L['z'], L['y'])
        scene.collection.objects.link(po)
    cx, cy, cz = shot['cam']; ax, ay, az = shot['aim']
    cam_loc = Vector((cx, -cz, cy)); aim = Vector((ax, -az, ay))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    cam.rotation_euler = (aim - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = shot['lens']; cam.data.clip_end = 500
    scene.camera = cam
    scene.world = bpy.data.worlds.new('w'); scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (.05, .06, .08, 1) if night else (.32, .35, .36, 1)
    bg.inputs['Strength'].default_value = 0.5 if night else 0.9
    r = scene.render
    r.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    r.resolution_x = 1280; r.resolution_y = 800; r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    r.filepath = str(out / (shot['stem'] + '.png'))
    bpy.ops.render.render(write_still=True)
    rec = {'png': r.filepath, 'objects': len(shot['objects']), 'aim': shot['aim'], 'cam': shot['cam'],
           'lens': shot['lens'], 'night': bool(night)}
    if shot.get('light'): rec['pointLight'] = shot['light']
    if shot.get('tree'): rec['tree'] = shot['tree']
    for k in ('host', 'eyeY', 'wallH', 'segments'):
        if k in shot: rec[k] = shot[k]
    report.append(rec)
json.dump(report, open(out / 'renders.json', 'w'), indent=1)
print('[proof]', json.dumps(report), flush=True)
