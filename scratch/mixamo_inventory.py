"""Inventory all Mixamo FBX clips: armature, bone count, actions, fps, key counts."""
import bpy, os, sys, json

ROOT = "/workspace/witch-hunter/scratch/mixamo-fbx"
OUT = "/workspace/witch-hunter/scratch/mixamo-inventory.json"

def fbx_inventory(path):
    # isolate
    before = set(bpy.data.actions.keys())
    before |= {o.name for o in bpy.data.objects}
    try:
        bpy.ops.import_scene.fbx(filepath=path, use_manual_orientation=False, global_scale=1.0)
    except Exception as e:
        return {"error": str(e)[:120]}
    new_actions = [a for a in bpy.data.actions.keys() if a not in before]
    arm = None
    new_objects = [o for o in bpy.data.objects if o.name not in before]
    for o in new_objects:
        if o.type == 'ARMATURE':
            arm = o
            break
    res = {"actions": len(new_actions), "action_names": new_actions[:3],
           "bones": len(arm.data.bones) if arm else 0}
    if arm and new_actions:
        bpy.context.view_layer.objects.active = arm
        for an in new_actions[:2]:
            a = bpy.data.actions[an]
            fps = a.fps if hasattr(a, 'fps') else 0
            frames = int(a.frame_range[1] - a.frame_range[0]) + 1
            res["range"] = [round(a.frame_range[0],1), round(a.frame_range[1],1)]
    # cleanup
    for o in new_objects:
        b = o
        bpy.data.objects.remove(b, do_unlink=True)
    for an in new_actions:
        bpy.data.actions.remove(bpy.data.actions[an])
    # ALSO purge other imported datablocks
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for x in list(coll):
            if x.users == 0:
                coll.remove(x)
    return res

results = {}
files = sorted(os.listdir(os.path.join(ROOT, "axepack")))[:2]  # probe 2 files first
for f in files:
    p = os.path.join(ROOT, "axepack", f)
    results[f] = fbx_inventory(p)
    print(f, "->", json.dumps(results[f]), flush=True)

json.dump(results, open(OUT, 'w'), indent=1)
print("PROBE DONE")