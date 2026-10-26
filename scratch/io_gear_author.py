"""Author v5: hat data-space tilt (brim pierces hood = seated), satchel at belt-front-left
diagonal. Flat display-colored materials. Numeric bounds printed.
Run: blender --background --factory-startup --python wh_author5.py -- BASE OUT PREVIEW
"""
import bpy, sys, math, mathutils
from mathutils import Vector, Matrix, Euler

argv = sys.argv[sys.argv.index("--") + 1:]
BASE, OUT_GLB, PREVIEW = argv[0], argv[1], argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=BASE)

body = bpy.data.objects["WH_Body"]
arm = bpy.data.objects["WH_Armature"]

def flat_mat(name, hexcol, rough=0.85, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    r, g, b = (int(hexcol[i:i+2], 16)/255.0 for i in (0, 2, 4))
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (r, g, b, 1.0)
    return m

m_hat   = flat_mat("WHGearHatFabric", "23232a", 0.92)
m_band  = flat_mat("WHGearHatBand",   "39281a", 0.85)
m_buck  = flat_mat("WHGearSteel",     "7d838c", 0.45, metal=0.75)
m_pouch = flat_mat("WHGearLeather",   "453122", 0.88)
m_strap = flat_mat("WHGearStrapDark", "2a1e14", 0.85)

# ================= HAT =================
z_brim = 0.925    # v6: below hood widest flare -> brim slices through hood = seated
HC = Vector((0.0, -0.035, z_brim))

def shade_flat(o):
    for p in o.data.polygons: p.use_smooth = False

bpy.ops.mesh.primitive_cone_add(vertices=28, radius1=0.37, radius2=0.115,
                                depth=0.030, location=(0, -0.035, z_brim - 0.015))
brim = bpy.context.object; brim.name = "WH_HatBrim"

crown_h = 0.16
bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.16, depth=crown_h,
                                    location=(0, -0.035, z_brim + crown_h/2 - 0.02))
crown = bpy.context.object; crown.name = "WH_HatCrown"
crown.scale = (0.80, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.018,
                                 major_segments=28, minor_segments=8,
                                 location=(0, -0.035, z_brim + 0.020))
band = bpy.context.object; band.name = "WH_HatBand"
band.scale = (0.83, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, -0.035 - 0.155, z_brim + 0.020))
buck = bpy.context.object; buck.name = "WH_HatBuckle"
buck.scale = (0.028, 0.010, 0.05)
bpy.ops.object.transform_apply(scale=True)

brim.data.materials.append(m_hat)
crown.data.materials.append(m_hat)
band.data.materials.append(m_band)
buck.data.materials.append(m_buck)
for o in (brim, crown, band, buck): shade_flat(o)
for o, th in ((brim, 0.010), (crown, 0.012), (band, 0.008), (buck, 0.006)):
    mod = o.modifiers.new("sol", 'SOLIDIFY'); mod.thickness = th; mod.offset = 0.0
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="sol")

bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = brim
for o in (brim, crown, band, buck): o.select_set(True)
bpy.ops.object.join()
hat = bpy.context.active_object
hat.name = "WH_Hat"
# bake to world coords, then tilt about the hat's own center IN DATA SPACE
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
R = Matrix.Translation(HC) @ Matrix.Rotation(math.radians(8.0), 4, 'X') @ Matrix.Translation(-HC)
hat.data.transform(R)
hw = [hat.matrix_world @ Vector(c) for c in hat.bound_box]
print("HAT_BOUNDS z=[%.3f,%.3f] y=[%.3f,%.3f] x=[%.3f,%.3f]" % (
    min(p.z for p in hw), max(p.z for p in hw),
    min(p.y for p in hw), max(p.y for p in hw),
    min(p.x for p in hw), max(p.x for p in hw)))

# ================= SATCHEL: belt front-left diagonal =================
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.175, -0.205, -0.030))
pouch = bpy.context.object; pouch.name = "WH_SatchelPouch"
pouch.scale = (0.085, 0.12, 0.095)
pouch.rotation_euler = Euler((0, 0, math.radians(30)))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.175, -0.205, 0.020))
flap = bpy.context.object; flap.name = "WH_SatchelFlap"
flap.scale = (0.095, 0.135, 0.022)
flap.rotation_euler = Euler((0, 0, math.radians(30)))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# short strap up to the belt: spans flap top (~0.114) to belt (~0.175) with overlap both ends
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.198, -0.235, 0.075))
strap = bpy.context.object; strap.name = "WH_SatchelStrap"
strap.scale = (0.022, 0.024, 0.055)
strap.rotation_euler = Euler((0, 0, math.radians(30)))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# belt-loop buckle between strap and belt
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.212, -0.248, 0.125))
buckle = bpy.context.object; buckle.name = "WH_SatchelBuckle"
buckle.scale = (0.034, 0.02, 0.032)
bpy.ops.object.transform_apply(scale=True)

pouch.data.materials.append(m_pouch)
flap.data.materials.append(m_pouch)
strap.data.materials.append(m_strap)
buckle.data.materials.append(m_buck)
for o in (pouch, flap, strap, buckle): shade_flat(o)
for o, th in ((pouch, 0.008), (flap, 0.005), (strap, 0.004), (buckle, 0.005)):
    mod = o.modifiers.new("sol", 'SOLIDIFY'); mod.thickness = th; mod.offset = 0.0
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="sol")

bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = pouch
for o in (pouch, flap, strap, buckle): o.select_set(True)
bpy.ops.object.join()
sat = bpy.context.active_object
sat.name = "WH_Satchel"

# ================= weights + parenting (world coords, data = world) =================
for o, bone in ((hat, "Head"), (sat, "Hips")):
    vg = o.vertex_groups.new(name=bone)
    vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    o.parent = arm
    o.matrix_parent_inverse = arm.matrix_world.inverted()
    mod = o.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm

bpy.ops.object.select_all(action='DESELECT')
hat.select_set(True); sat.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
tris = 0
for o in (hat, sat):
    o.data.calc_loop_triangles()
    tris += len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(
    filepath=OUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_animations=False,
    export_skins=True,
    export_materials='EXPORT',
    export_yup=True,
)
print("AUTHOR5_DONE gear_tris=%d out=%s" % (tris, OUT_GLB))

scene = bpy.context.scene
wb = scene.display.shading
wb.light = 'STUDIO'; wb.color_type = 'MATERIAL'; wb.show_shadows = True
cam_data = bpy.data.cameras.new("Cam"); cam_data.lens = 60
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam); scene.camera = cam
target = Vector((0.0, 0.0, 0.3))
def look_from(pos, name):
    cam.location = pos
    d = target - pos
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = f"{PREVIEW}/{name}.png"
    bpy.ops.render.render(write_still=True)
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 720; scene.render.resolution_y = 960
look_from(Vector((0.0, -2.4, 0.55)), "v8_front")
look_from(Vector((1.8, -1.8, 0.7)), "v8_front_right_34")
look_from(Vector((-2.4, 0.0, 0.35)), "v8_left_side")
look_from(Vector((-1.9, 1.9, 0.6)), "v8_back_right_34")
look_from(Vector((0.0, 2.4, 0.6)), "v8_back")
print("PREVIEW5_DONE")