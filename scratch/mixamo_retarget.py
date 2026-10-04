"""Mixamo FBX -> WH 20-bone rig retarget (constraint+bake route), batch, GLB export.

Usage:
  blender --background --factory-startup --python scratch/mixamo_retarget.py -- \
      TARGET.glb OUT.glb --clips FILE.json [--log LOG.json]
"""
import bpy, os, sys, json, math

argv = sys.argv[sys.argv.index("--") + 1:]
IN_GLB, OUT_GLB = argv[0], argv[1]
CLIPS_JSON = argv[argv.index("--clips") + 1]
LOG = argv[argv.index("--log") + 1] if "--log" in argv else None

def log(*a):
    print("[rt]", *a, flush=True)

with open(CLIPS_JSON) as fh:
    CLIPS = json.load(fh)

bpy.ops.import_scene.gltf(filepath=IN_GLB)
arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
target = max(arms, key=lambda a: len(a.data.bones))
log("target:", target.name, len(target.data.bones), "bones")

existing_actions = {a.name: a for a in bpy.data.actions}
for a in existing_actions.values():
    a.use_fake_user = True
log("stashed actions:", len(existing_actions))

MAP = {
    'Root': 'Hips', 'Spine': 'Spine1', 'Chest': 'Spine2',
    'Neck': 'Neck', 'Head': 'Head',
    'L_Shoulder': 'LeftShoulder', 'R_Shoulder': 'RightShoulder',
    'L_UpperArm': 'LeftArm', 'R_UpperArm': 'RightArm',
    'L_Forearm': 'LeftForeArm', 'R_Forearm': 'RightForeArm',
    'L_Hand': 'LeftHand', 'R_Hand': 'RightHand',
    'L_Thigh': 'LeftUpLeg', 'R_Thigh': 'RightUpLeg',
    'L_Shin': 'LeftLeg', 'R_Shin': 'RightLeg',
    'L_Foot': 'LeftFoot', 'R_Foot': 'RightFoot',
}
HIPS_MAP = {'Root': 'Hips'}  # location-carrying bones

scene = bpy.context.scene
scene.render.fps = 30
report = {"clips": {}}

def cleanup(src, acts):
    names = [a.name for a in acts]
    src_children = [c for c in src.children_recursive]
    bpy.data.objects.remove(src, do_unlink=True)
    for c in src_children:
        try:
            bpy.data.objects.remove(c, do_unlink=True)
        except Exception:
            pass
    for n in names:
        a = bpy.data.actions.get(n)
        if a:
            bpy.data.actions.remove(a)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                 bpy.data.armatures, bpy.data.cameras, bpy.data.lights):
        for x in list(coll):
            if x.users == 0:
                coll.remove(x)

for wh_name, fbx_path in CLIPS.items():
    before_objs = {o.name for o in bpy.data.objects}
    before_acts = set(bpy.data.actions.keys())
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    src = None
    for o in bpy.data.objects:
        if o.name not in before_objs and o.type == 'ARMATURE':
            src = o
    new_acts = [a for a in bpy.data.actions if a.name not in before_acts]
    if not src or not new_acts:
        report["clips"][wh_name] = {"error": "import failed"}
        continue
    act = new_acts[0]
    src.animation_data_create()
    src.animation_data.action = act
    scene.frame_start = 0
    scene.frame_end = int(math.ceil(act.frame_range[1]))
    log("retarget:", wh_name, "<-", os.path.basename(fbx_path),
        "frames", scene.frame_start, "-", scene.frame_end)

    src_bones = {b.name.replace('mixamorig:', ''): b for b in src.pose.bones}
    # constraints on target pose bones
    for wh_b, mx_b in MAP.items():
        pb = target.pose.bones.get(wh_b)
        sb = src_bones.get(mx_b)
        if not pb or not sb:
            log("  miss:", wh_b, mx_b)
            continue
        c = pb.constraints.new('ARMATURE' if False else 'COPY_ROTATION')
        c.name = "rt_rot"
        c.target = src
        c.subtarget = sb.name
        pb.constraints.new('LIMIT_ROTATION')  # placeholder removed below
        pb.constraints.remove(pb.constraints["Limit Rotation"])
        if wh_b in HIPS_MAP:
            ct = pb.constraints.new('COPY_LOCATION')
            c.name = "rt_loc"
            ct.target = src
            ct.subtarget = sb.name
            ct.target_space = 'POSE'
            ct.owner_space = 'POSE'
    t_act = bpy.data.actions.new(wh_name)
    t_act.use_fake_user = True
    tmod = target.animation_data_create()
    tmod.action = t_act
    try:
        t_act.slots.new(id_type='OBJECT', name=wh_name)
    except Exception as e:
        log("  slot create failed (4.5 may auto-slot):", e)
    if t_act.slots:
        tmod.action_slot = t_act.slots[0]
    # nla.bake uses selected_editable_objects, NOT the active object alone.
    # FBX import selects the source and deselects the target on every iteration.
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.ops.nla.bake(frame_start=scene.frame_start, frame_end=scene.frame_end,
                     only_selected=False, visual_keying=True, clear_constraints=True,
                     use_current_action=True)
    baked = target.animation_data.action  # baked INTO the placeholder (no NLA push)
    baked.name = wh_name + "_baked"
    baked.use_fake_user = True
    trk = target.animation_data.nla_tracks.new()
    trk.name = "RT_" + wh_name
    strip = trk.strips.new(name=wh_name, start=0, action=baked)
    if baked.slots:
        strip.action_slot = baked.slots[0]
    target.animation_data.action = None
    report["clips"][wh_name] = {"frames": int(math.ceil(act.frame_range[1])),
                                "src": os.path.basename(fbx_path),
                                "fcurves": len(baked.fcurves)}
    log("  baked:", wh_name, "fcurves:", len(baked.fcurves))
    cleanup(src, new_acts)

target.animation_data.action = None
bpy.context.view_layer.objects.active = target
bpy.ops.export_scene.gltf(
    filepath=OUT_GLB, export_format="GLB",
    export_animation_mode="ACTIONS",
    export_skins=True, export_def_bones=False,
    export_apply=False, export_image_format="AUTO",
    export_yup=True,
    export_force_sampling=False,
    export_optimize_animation_size=False,
    export_anim_slide_to_zero=True, export_reset_pose_bones=True,
    export_extras=False, export_cameras=False, export_lights=False)
log(f"exported {OUT_GLB} ({os.path.getsize(OUT_GLB)/1e6:.2f} MB)")
if LOG:
    json.dump(report, open(LOG, 'w'), indent=1)
print("RETARGET DONE", flush=True)