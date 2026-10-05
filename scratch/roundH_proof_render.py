"""Round H proof stills from roundH_proof_scene.py shots: the Round F/G renderer
(matrix-chain ground lift, shadows OFF, pixelated textures Closest) plus the
game's night rig and fog, 1024 px wide:
  - moon = SUN at the CONFIG azimuth/elevation (azimuth 0 = the -z side),
    strength = moonIntensity (three directional intensity == Blender sun
    irradiance; both shade a white lambert at 1/pi);
  - hemi fill: world lighting colour sky/ground by normal up, strength
    hemiIntensity / pi (three hemi irradiance * BRDF_Lambert);
    camera rays see the sky dome gradient instead (zenith / band / glow);
  - light pool + player lantern = POINT lights, watts = candela * 4 pi;
  - fog = compositor FogExp2 on the Z pass: f = 1 - exp(-(density z)^2),
    colour mixed in linear; sky pixels (Z > 1000) stay unfogged like the
    game's fog:false dome;
  - COLOR_0 vertex colours (the snare) multiply into Base Color;
  - view transform Standard (three outputs plain sRGB, no AgX/Filmic).
blender -b --python roundH_proof_render.py -- shots.json OUTDIR
glTF (x, y, z) -> Blender (x, -z, y).
"""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

shots_p, out = sys.argv[sys.argv.index('--') + 1:][:2]
out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
shots = json.load(open(shots_p))
report = []


def lin(c):
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def wire_vertex_colors(o):
    if not o.data.color_attributes:
        return False
    name = o.data.color_attributes[0].name
    for slot in o.material_slots:
        m = slot.material
        if not (m and m.use_nodes):
            continue
        nt = m.node_tree
        bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None or bsdf.inputs['Base Color'].is_linked:
            continue
        a = nt.nodes.new('ShaderNodeVertexColor'); a.layer_name = name
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1.0
        mix.inputs[6].default_value = bsdf.inputs['Base Color'].default_value
        nt.links.new(a.outputs['Color'], mix.inputs[7])
        nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    return True


def world(scene, shot):
    w = bpy.data.worlds.new('w'); w.use_nodes = True; scene.world = w
    nt = w.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputWorld')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    # camera rays: sky dome gradient by view elevation (Generated z = dir z)
    ramp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sep.outputs['Z'], ramp.inputs[0])
    S = shot['sky']
    e = ramp.color_ramp.elements
    e[0].position = 0.0; e[0].color = lin(S['horizonGlow']) + [1]
    e[1].position = 1.0; e[1].color = lin(S['zenithColor']) + [1]
    mid = e.new(S['glowStop']); mid.color = lin(S['horizonBand']) + [1]
    skybg = nt.nodes.new('ShaderNodeBackground'); nt.links.new(ramp.outputs['Color'], skybg.inputs['Color'])
    # lighting rays: hemisphere ground->sky by direction z
    hr = nt.nodes.new('ShaderNodeMapRange'); nt.links.new(sep.outputs['Z'], hr.inputs['Value'])
    hr.inputs['From Min'].default_value = -1.0; hr.inputs['From Max'].default_value = 1.0
    hm = nt.nodes.new('ShaderNodeMix'); hm.data_type = 'RGBA'
    nt.links.new(hr.outputs['Result'], hm.inputs['Factor'])
    hm.inputs[6].default_value = lin(shot['hemi']['ground']) + [1]
    hm.inputs[7].default_value = lin(shot['hemi']['sky']) + [1]
    hemibg = nt.nodes.new('ShaderNodeBackground'); nt.links.new(hm.outputs[2], hemibg.inputs['Color'])
    hemibg.inputs['Strength'].default_value = shot['hemi']['intensity'] / math.pi
    lp = nt.nodes.new('ShaderNodeLightPath')
    mixs = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mixs.inputs['Fac'])
    nt.links.new(hemibg.outputs[0], mixs.inputs[1]); nt.links.new(skybg.outputs[0], mixs.inputs[2])
    nt.links.new(mixs.outputs[0], o.inputs['Surface'])


def fog(scene, shot):
    F = shot['fog']
    col = [a + (b - a) * F['w'] for a, b in zip(lin(F['baseColor']), lin(F['targetColor']))]
    scene.view_layers[0].use_pass_z = True
    scene.use_nodes = True
    nt = scene.node_tree; nt.nodes.clear()
    rl = nt.nodes.new('CompositorNodeRLayers')
    comp = nt.nodes.new('CompositorNodeComposite')
    def math_node(op, a=None, b=None):
        n = nt.nodes.new('CompositorNodeMath'); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    dz = math_node('MULTIPLY', rl.outputs['Depth'], F['density'])
    sq = math_node('MULTIPLY', dz, dz)
    ex = math_node('EXPONENT', math_node('MULTIPLY', sq, -1.0))
    f = math_node('SUBTRACT', 1.0, ex)
    mask = math_node('LESS_THAN', rl.outputs['Depth'], 1000.0)
    fm = math_node('MULTIPLY', f, mask)
    mix = nt.nodes.new('CompositorNodeMixRGB')
    nt.links.new(fm, mix.inputs[0]); nt.links.new(rl.outputs['Image'], mix.inputs[1])
    mix.inputs[2].default_value = col + [1]
    nt.links.new(mix.outputs[0], comp.inputs['Image'])
    return col


def path_mesh(scene, shot):
    pts, hw, y = shot['path'], shot['pathHalfWidth'], shot['pathY']
    verts, faces = [], []
    for i, (x, z) in enumerate(pts):
        j0, j1 = max(0, i - 1), min(len(pts) - 1, i + 1)
        tx, tz = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
        tl = math.hypot(tx, tz); nx, nz = -tz / tl, tx / tl
        for s in (-1, 1):
            gx, gz = x + nx * hw * s, z + nz * hw * s
            verts.append((gx, -gz, y))
        if i:
            a = 2 * (i - 1)
            faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new('path'); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new('dirt-path', me); scene.collection.objects.link(ob)
    m = bpy.data.materials.new('dirt'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin([0x5a / 255, 0x4a / 255, 0x33 / 255]) + [1]
    b.inputs['Roughness'].default_value = 1.0
    me.materials.append(m)


for shot in shots:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    templates = {}
    vcol = set()
    for glb in sorted({o['glb'] for o in shot['objects']}):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=glb)
        new = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in new if o.type == 'MESH']
        bpy.context.view_layer.update()
        zmin = min((o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box)
        for o in meshes:
            if wire_vertex_colors(o):
                vcol.add(Path(glb).name)
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
            S = Matrix.Diagonal((ob['sx'], ob['sz'], ob['sy'], 1.0))
            d.matrix_world = (Matrix.Translation((ob['x'], -ob['z'], ob['y'])) @
                              Matrix.Rotation(ob['rotY'], 4, 'Z') @ S @
                              Matrix.Translation((0, 0, -zmin)) @ m.matrix_world)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    g = bpy.data.materials.new('ground'); g.use_nodes = True
    g.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.046, .042, .025, 1)  # 0x3d3a2c linear
    g.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.0
    bpy.context.object.data.materials.append(g)
    path_mesh(scene, shot)
    M = shot['moon']
    sun = bpy.data.lights.new('moon', 'SUN')
    sun.energy = M['intensity']; sun.color = lin(M['color']); sun.use_shadow = False
    so = bpy.data.objects.new('moon', sun)
    az, el = math.radians(M['azDeg']), math.radians(M['elDeg'])
    # game: moon on the -z side at azimuth 0 -> Blender +Y; light travels moon -> origin
    mdir = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so.rotation_euler = (-mdir).to_track_quat('-Z', 'Y').to_euler()
    scene.collection.objects.link(so)
    for i, L in enumerate(shot['lights']):
        pl = bpy.data.lights.new(f'pool{i}', 'POINT'); pl.energy = L['cd'] * 4 * math.pi
        pl.color = lin(L['color']); pl.shadow_soft_size = 0.15; pl.use_shadow = False
        po = bpy.data.objects.new(f'pool{i}', pl); po.location = (L['x'], -L['z'], L['y'])
        scene.collection.objects.link(po)
    world(scene, shot)
    fogcol = fog(scene, shot)
    cx, cy, cz = shot['cam']; ax, ay, az_ = shot['aim']
    cam_loc = Vector((cx, -cz, cy)); aim = Vector((ax, -az_, ay))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    cam.rotation_euler = (aim - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = shot['lens']; cam.data.clip_end = 500
    scene.camera = cam
    scene.view_settings.view_transform = 'Standard'
    r = scene.render
    r.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    r.resolution_x = 1024; r.resolution_y = 640; r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    r.filepath = str(out / (shot['stem'] + '.png'))
    bpy.ops.render.render(write_still=True)
    rec = {'png': r.filepath, 'objects': len(shot['objects']), 'cam': shot['cam'], 'aim': shot['aim'],
           'lens': shot['lens'], 'player': shot['player'], 'fog': shot['fog'],
           'fogColorLinear': [round(c, 4) for c in fogcol], 'lights': len(shot['lights']),
           'vertexColorGLBs': sorted(vcol)}
    if 'host' in shot: rec['host'] = shot['host']
    report.append(rec)
json.dump(report, open(out / 'renders.json', 'w'), indent=1)
print('[proof]', json.dumps(report), flush=True)
