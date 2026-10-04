"""Objective slab metric: per-edge stretch (posed length / rest length) over clips.

blender -b --python scratch/orc_stretch_probe.py -- GLB OUT.npz OUT.json [CLIP ...]
Without CLIP names every action in the GLB is sampled. Slab extrusion shows up
as edges stretched far beyond rest length. Rigid limbs stay near 1.0.
The npz holds per-vertex maxima per clip, per-edge maxima as E_<clip>, and the
Blender edge list. Vertex order equals glTF order (single primitive, importer does not merge).
"""
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out_npz, out_json, clips = argv[0], argv[1], argv[2], argv[3:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb, bone_heuristic='BLENDER')
arm = bpy.data.objects['WH_Armature']
body = next(o for o in bpy.data.objects if o.type == 'MESH' and
            any(m.type == 'ARMATURE' for m in o.modifiers))
for tr in arm.animation_data.nla_tracks:
    tr.mute = True
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
scene = bpy.context.scene
me = body.data
edges = np.empty(len(me.edges) * 2, np.int64)
me.edges.foreach_get('vertices', edges)
edges = edges.reshape(-1, 2)


def coords():
    deps = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(deps)
    m = ev.to_mesh()
    co = np.empty(len(m.vertices) * 3)
    m.vertices.foreach_get('co', co)
    ev.to_mesh_clear()
    return co.reshape(-1, 3)


bpy.context.view_layer.update()
rest = coords()
rest_len = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
valid = rest_len > 1e-5
names = clips or [a.name for a in bpy.data.actions]
vmax = {}
report = {'glb': str(Path(glb).resolve()), 'edges': int(valid.sum()), 'clips': {}}
for name in names:
    act = bpy.data.actions[name]
    arm.animation_data.action = act
    arm.animation_data.action_slot = act.slots[0]
    lo, hi = map(lambda x: int(round(x)), act.frame_range)
    emax = np.ones(len(edges))
    for f in range(lo, hi + 1):
        scene.frame_set(f)
        co = coords()
        ln = np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1)
        emax = np.maximum(emax, np.where(valid, ln / np.maximum(rest_len, 1e-5), 1))
    v = np.ones(len(rest))
    np.maximum.at(v, edges[:, 0], emax)
    np.maximum.at(v, edges[:, 1], emax)
    vmax[name] = v
    vmax['E_' + name] = emax
    report['clips'][name] = {'frames': hi - lo + 1, 'max_edge_stretch': float(emax.max()),
        'edges_over_2x': int((emax > 2).sum()), 'edges_over_3x': int((emax > 3).sum()),
        'edges_over_5x': int((emax > 5).sum()), 'p999': float(np.quantile(emax, .999))}
    print('[stretch]', name, report['clips'][name], flush=True)
np.savez(out_npz, edges=edges, **vmax)
Path(out_json).write_text(json.dumps(report, indent=2) + '\n')
print('STRETCH_DONE')
