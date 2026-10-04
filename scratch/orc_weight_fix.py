"""Orc skin-weight repair: vertices skinned to anatomically distant bones.

python3 scratch/orc_weight_fix.py CANONICAL.rigged.glb OUT.rigged.glb --report JSON

Defect: the auto-rig weighted some arm/hand/back vertices wholly to bones they
are not near (e.g. hand verts to R_Thigh, lat verts to the forearm). At the
hanging-arm rest pose these bones overlap in space, so the rest pose and the
original WH clips look fine. Mixamo clips move the arms away from the thighs,
and the stuck vertices extrude into rigid slabs.

Repair, mesh-space at the bind pose:
- Each bone is a capsule (head -> child head) with a radius measured from the
  vertices it already dominates (median distance).
- A vertex's region is the bone with the smallest distance/radius.
- Only the region bone and its hierarchy neighbours (parent, children) may keep
  weight. If they hold at least KEEP of the old weight, renormalise it.
  Otherwise the vertex goes rigidly to its region bone.

Output is byte-surgical. The canonical BIN stays a byte-identical prefix. New
JOINTS_0/WEIGHTS_0 accessors are appended, and only the primitive's two
attribute indices change. Every other JSON key, including all six original
clips, stays identical.
"""
import argparse
import copy
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse, save, accessor_bytes

KEEP = 0.5
FAR_ABS = 2.5
HIP_Y = 0.12
# (|x| >, (y0, y1)): hanging-arm slabs. Hand height, then lower forearm.
GATES = ((0.40, (-0.45, 0.15)), (0.36, (0.15, 0.33)))
FLAP_X, FLAP_Z = 0.12, 0.21
FAR = 1.5
# Jaw gate (Round B): the orc's jaw/chin hangs below the Head joint, in front
# of the neck, and sits closer to the shoulder/neck capsules than to Head's.
# Without this gate ~560 face verts were moved rigidly to R/L_Shoulder, Neck
# and Chest and the jaw stretched into a beak whenever the head turned.
# Head weight on these verts is authored; never strip it. The cape is behind
# the neck (z < 0) and the pauldrons are at |x| >= JAW_X, so both stay repaired.
JAW_X, JAW_Z = 0.15, 0.05
# Capsule radii (m, mesh space; the orc is ~2 m tall in mesh units).
CHAIN = {'Hips': 'axial', 'Spine': 'axial', 'Chest': 'axial', 'Neck': 'axial',
         'Head': 'axial', 'Root': 'axial'}
CHAIN.update({f'{s}_{b}': f'{s}_arm' for s in 'LR'
              for b in ('Shoulder', 'UpperArm', 'Forearm', 'Hand')})
CHAIN.update({f'{s}_{b}': f'{s}_leg' for s in 'LR' for b in ('Thigh', 'Shin', 'Foot')})
RADIUS = {'Hips': .22, 'Spine': .25, 'Chest': .25, 'Neck': .12,
                  'Head': .12, 'L_Shoulder': .15, 'R_Shoulder': .15,
                  'L_UpperArm': .09, 'R_UpperArm': .09, 'L_Forearm': .09,
                  'R_Forearm': .09, 'L_Hand': .09, 'R_Hand': .09,
                  'L_Thigh': .17, 'R_Thigh': .17, 'L_Shin': .14, 'R_Shin': .14,
                  'L_Foot': .16, 'R_Foot': .16}


def load(doc, blob, idx, dtype, width):
    return np.frombuffer(accessor_bytes(doc, blob, idx), dtype=dtype).reshape(-1, width)


def segments(doc, blob):
    skin = doc['skins'][0]
    names = [doc['nodes'][j]['name'] for j in skin['joints']]
    ibm = load(doc, blob, skin['inverseBindMatrices'], np.float32, 16)
    heads = np.array([np.linalg.inv(m.reshape(4, 4).T)[:3, 3] for m in ibm])
    node_to_joint = {n: i for i, n in enumerate(skin['joints'])}
    parent = {}
    for ni, node in enumerate(doc['nodes']):
        for c in node.get('children', []):
            if ni in node_to_joint and c in node_to_joint:
                parent[node_to_joint[c]] = node_to_joint[ni]
    children = {i: [c for c, p in parent.items() if p == i] for i in range(len(names))}
    tails = heads.copy()
    for i in range(len(names)):
        kids = children[i]
        if len(kids) == 1:
            tails[i] = heads[kids[0]]
        elif kids:
            # Hips/Chest branch: follow the spine child, not a limb.
            spine = [k for k in kids if names[k] in ('Spine', 'Chest', 'Neck')]
            tails[i] = heads[spine[0]] if spine else heads[kids].mean(0)
        elif i in parent:
            # Leaf (Hand/Foot/Head): extend along the parent bone direction.
            d = heads[i] - heads[parent[i]]
            tails[i] = heads[i] + d / np.linalg.norm(d) * {'Head': .18, 'L_Hand': .2,
                                                            'R_Hand': .2}.get(names[i], .12)
    return names, heads, tails, parent, children


def seg_dist(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)


def repair(doc, blob):
    attrs = doc['meshes'][0]['primitives'][0]['attributes']
    P = load(doc, blob, attrs['POSITION'], np.float32, 3).astype(np.float64)
    J = load(doc, blob, attrs['JOINTS_0'], np.uint8, 4).astype(np.int64)
    W = load(doc, blob, attrs['WEIGHTS_0'], np.float32, 4).astype(np.float64)
    names, heads, tails, parent, children = segments(doc, blob)
    nb = len(names)
    D = np.stack([seg_dist(P, heads[i], tails[i]) for i in range(nb)], 1)
    dense = np.zeros((len(P), nb))
    np.add.at(dense, (np.arange(len(P))[:, None], J), W)
    dom = dense.argmax(1)
    # Fixed anatomical radii. Medians over "owned" verts are unusable because
    # the misweighted verts (arm surface owned by the clavicle) inflate them.
    radius = np.array([RADIUS.get(n, np.inf) for n in names])
    # Root carries no skin and can never be a region.
    ratio = np.where(np.isfinite(radius), D / radius, np.inf)
    leg = np.array([CHAIN.get(n, '').endswith('_leg') for n in names])
    above_hip = P[:, 1] > HIP_Y
    ratio[np.ix_(above_hip, leg)] = np.inf
    region = ratio.argmin(1)
    # Hand gate: the arms hang beside the thighs. At hand height, true thigh
    # surface ends at |x| ~0.36 and hand/forearm surface starts at ~0.46, but
    # curled fingertips sit closer to the thigh capsule than to the hand's.
    # Force that slab into the same-side arm chain and pick the arm bone by fit.
    gate = np.zeros(len(P), bool)
    for gx, (y0, y1) in GATES:
        gate |= (np.abs(P[:, 0]) > gx) & (P[:, 1] > y0) & (P[:, 1] < y1)
    for side, sign in (('L', 1), ('R', -1)):
        rows = gate & (np.sign(P[:, 0]) == sign)
        cols = np.array([CHAIN.get(n) == f'{side}_arm' and n.split('_')[-1] in
                         ('UpperArm', 'Forearm', 'Hand') for n in names])
        sub = np.where(cols[None, :], ratio[rows], np.inf)
        region[rows] = sub.argmin(1)
    best = np.take_along_axis(ratio, region[:, None], 1)
    allowed = np.zeros((nb, nb), bool)
    for i in range(nb):
        allowed[i, i] = True
        if i in parent:
            allowed[i, parent[i]] = True
        allowed[i, children[i]] = True
    # Offending influence: not a hierarchy neighbour of the region bone AND
    # clearly far away (outside its own capsule by FAR and > 2x the best fit).
    offend = (~allowed[region]) & (ratio > FAR) & (ratio > 2 * best) & (dense > 0)
    # Chain rule: a limb vertex never takes weight from another limb, and a
    # forearm/hand vertex never takes torso weight. Hands hang beside the
    # thighs at rest, so the capsule test alone keeps hand verts on L_Thigh.
    chain = np.array([CHAIN.get(n, '') for n in names])
    distal = np.array([n.split('_')[-1] in ('Forearm', 'Hand') for n in names])
    limb = chain[region] != 'axial'
    cross = limb[:, None] & (chain[None, :] != 'axial') & (chain[None, :] != chain[region][:, None])
    cross |= distal[region][:, None] & (chain[None, :] == 'axial')[0:1].repeat(len(P), 0)
    offend |= cross & ~allowed[region] & (dense > 0)
    # No bone drives vertices far outside its own capsule, neighbour or not
    # (clavicle weight on the forearm surface). Leg weight never above hips.
    offend |= (ratio > FAR_ABS) & (dense > 0)
    offend |= above_hip[:, None] & leg[None, :] & (dense > 0)
    hi = names.index('Head')
    jaw = (np.abs(P[:, 0]) < JAW_X) & (P[:, 2] > heads[hi][2] + JAW_Z) & (dense[:, hi] > 0)
    offend[jaw, hi] = False
    new = np.where(offend, 0, dense)
    kept = new.sum(1)
    rigid = (kept < KEEP) & offend.any(1)
    new[rigid] = 0
    new[rigid, region[rigid]] = 1
    new /= new.sum(1, keepdims=True)
    # Loincloth flaps hang across the centreline between the legs. A hard
    # L_Thigh/R_Thigh switch at x=0 tears the cloth when the legs split, so
    # share the thigh weight with a smoothstep across the flap.
    li, ri = names.index('L_Thigh'), names.index('R_Thigh')
    flap = (np.abs(P[:, 0]) < FLAP_X) & (P[:, 1] < 0) & (np.abs(P[:, 2]) > FLAP_Z)
    flap &= (new[:, li] + new[:, ri]) > 0
    t = np.clip((P[flap, 0] + FLAP_X) / (2 * FLAP_X), 0, 1)
    share = t * t * (3 - 2 * t)
    total = new[flap, li] + new[flap, ri]
    new[flap, li], new[flap, ri] = total * share, total * (1 - share)
    # Back to 4 influences: top-4, renormalised in float32.
    top = np.argsort(-new, 1)[:, :4]
    tw = np.take_along_axis(new, top, 1)
    tw[tw < 1e-6] = 0
    top[tw == 0] = 0
    tw = (tw / tw.sum(1, keepdims=True)).astype(np.float32)
    J2, W2 = top.astype(np.uint8), tw
    changed = np.abs(np.take_along_axis(dense, top, 1) - tw).max(1) > 1e-5
    changed |= np.abs(dense.sum(1) - np.take_along_axis(dense, top, 1).sum(1)) > 1e-5
    stats = {'vertices': int(len(P)), 'changed': int(changed.sum()),
             'rigid_reassigned': int(rigid.sum()),
             'renormalised': int((changed & ~rigid).sum()),
             'keep_threshold': KEEP, 'far_ratio': FAR,
             'far_abs_ratio': FAR_ABS, 'hip_y': HIP_Y,
             'arm_gates': {'rules': GATES, 'vertices': int(gate.sum())},
             'jaw_gate': {'abs_x_lt': JAW_X, 'z_gt_head_plus': JAW_Z,
                          'vertices': int(jaw.sum())},
             'loincloth_flap': {'abs_x_lt': FLAP_X, 'abs_z_gt': FLAP_Z,
                                'vertices': int(flap.sum())},
             'capsule_radius_m': {names[i]: float(radius[i]) for i in range(nb)},
             'changed_by_old_dominant': {}, 'changed_by_new_region': {}}
    for i in range(nb):
        a, b = int((changed & (dom == i)).sum()), int((changed & (region == i)).sum())
        if a:
            stats['changed_by_old_dominant'][names[i]] = a
        if b:
            stats['changed_by_new_region'][names[i]] = b
    return J2, W2, changed, stats


def write_patched(base_path, out_path, J2, W2):
    doc, blob = parse(base_path)
    out = copy.deepcopy(doc)
    blob = bytearray(blob)
    prim = out['meshes'][0]['primitives'][0]['attributes']
    for key, arr, ctype in (('JOINTS_0', J2, 5121), ('WEIGHTS_0', W2, 5126)):
        blob.extend(b'\0' * (-len(blob) % 4))
        payload = np.ascontiguousarray(arr).tobytes()
        out['bufferViews'].append({'buffer': 0, 'byteOffset': len(blob),
                                   'byteLength': len(payload), 'target': 34962})
        blob.extend(payload)
        acc = copy.deepcopy(doc['accessors'][prim[key]])
        acc.update({'bufferView': len(out['bufferViews']) - 1, 'componentType': ctype})
        acc.pop('byteOffset', None)
        out['accessors'].append(acc)
        prim[key] = len(out['accessors']) - 1
    out['buffers'][0]['byteLength'] = len(blob)
    save(out_path, out, blob)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('canonical')
    ap.add_argument('out')
    ap.add_argument('--report', required=True)
    ap.add_argument('--changed-json', help='diagnostic vertex list for cape_diag_render')
    a = ap.parse_args()
    src, out = Path(a.canonical).resolve(), Path(a.out).resolve()
    assert src != out
    doc, blob = parse(src)
    J2, W2, changed, stats = repair(doc, blob)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_patched(src, out, J2, W2)
    stats.update({'canonical': str(src), 'output': str(out)})
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text(json.dumps(stats, indent=2) + '\n')
    if a.changed_json:
        Path(a.changed_json).write_text(json.dumps(
            {'vertex_groups': {'changed': np.where(changed)[0].tolist()}}))
    print(json.dumps({k: v for k, v in stats.items() if k != 'capsule_radius_m'}, indent=2))


if __name__ == '__main__':
    main()
