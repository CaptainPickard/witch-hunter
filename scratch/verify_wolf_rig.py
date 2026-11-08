#!/usr/bin/env python3
"""VERIFY GATE for the WOLF-RIG round (io/missions/2026-10-08-wolf-rig.md sec. 2/3).

Plain python + numpy on the GLB bytes (no Blender, no game): the shipped file is
what gets measured. Skinned positions = linear blend skinning of the raw
vertices with the file's own joints / IBMs / animation keys.

    python3 scratch/verify_wolf_rig.py RAW.glb RIGGED.glb [--pixelated PIX.glb] [--json OUT.json]

Asserts (all must PASS):
  mesh       13,085 verts / 20,060 tris; POSITION/NORMAL/TEXCOORD_0/indices
             vs raw (max |drift| < 1.2e-5, reported; bitwise flag reported)
  texture    embedded image bytes == raw atlas bytes (mimeType equal)
  material   raw PBR fields equal, baseColorTexture present; sampler equal
  skin       1 skin, 21 joints, exact names + parent topology, <= 4
             influences, weights sum 1, Jaw only in the mouth slab, Tail only
             behind the rump
  clips      6, exact names; channels = 21 bones x T/R/S = 63; durations
             within 5% of 3 / 1 / 0.55 / 0.7 / 0.4 / 1.1 s
  root       Root channels == Root rest on every key (no root motion)
  seamless   Idle/Walk/Run/Attack1/Hit: first-frame TRS == last-frame TRS
  stance     every clip starts at the bind stance; all but Death end there
  death      LAST frame measured prone: pelvis + chest joint height above
             ground < 35% of rest, body rolled >= 60 deg, settled (last two
             keys identical within 1 mm), mesh resting on the ground
  ground     Walk/Run lowest skinned vertex >= ground - 0.02 on every key
             (ground = raw sole height y=-0.593273; the raw is not re-based)
  cadence    Walk/Run per-leg hip-joint (UpperLeg head) height p2p > 0.02 and
             per-leg paw height p2p > 0.02
  pixelated  (optional) mesh/skin/JOINTS_0/WEIGHTS_0/IBM/animation accessor
             bytes identical to RIGGED; image = 512 NEAREST + 5-bit of the raw
             atlas, decoded pixel-exact
"""
import io
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse, accessor_bytes, COMPONENTS, WIDTHS  # noqa: E402

GROUND = -0.593273
SPEC = {"WH_Wolf_Idle": 3.0, "WH_Wolf_Walk": 1.0, "WH_Wolf_Run": 0.55,
        "WH_Wolf_Attack1": 0.7, "WH_Wolf_Hit": 0.4, "WH_Wolf_Death": 1.1}
LOOPS = ["WH_Wolf_Idle", "WH_Wolf_Walk", "WH_Wolf_Run", "WH_Wolf_Attack1", "WH_Wolf_Hit"]
PARENTS = {"Root": None, "Spine": "Root", "Chest": "Spine", "Neck": "Chest", "Head": "Neck",
           "Jaw": "Head", "Tail1": "Spine", "Tail2": "Tail1", "Tail3": "Tail2"}
for _p in ("FL", "FR", "BL", "BR"):
    PARENTS[f"{_p}_UpperLeg"] = "Chest" if _p[0] == "F" else "Spine"
    PARENTS[f"{_p}_Leg"] = f"{_p}_UpperLeg"
    PARENTS[f"{_p}_Foot"] = f"{_p}_Leg"
LEGS = ("FL", "FR", "BL", "BR")
NP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}

RESULTS = []


def check(name, ok, detail):
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)


def acc(doc, blob, i):
    a = doc['accessors'][i]
    arr = np.frombuffer(accessor_bytes(doc, blob, i), NP[a['componentType']])
    return arr.reshape(a['count'], WIDTHS[a['type']])


def image_bytes(doc, blob, i=0):
    v = doc['bufferViews'][doc['images'][i]['bufferView']]
    return blob[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]


# --------------------------------------------------------------------- math
def quat_mat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def trs(t, r, s):
    m = np.eye(4)
    m[:3, :3] = quat_mat(r) * np.asarray(s)[None, :]
    m[:3, 3] = t
    return m


class Rig:
    """Node graph + skin + clips of one GLB; evaluates joint worlds / skinned verts."""

    def __init__(self, path):
        self.doc, self.bin = parse(path)
        d = self.doc
        self.prim = d['meshes'][0]['primitives'][0]
        at = self.prim['attributes']
        self.pos = acc(d, self.bin, at['POSITION']).astype(np.float64)
        self.idx = acc(d, self.bin, self.prim['indices']).reshape(-1, 3)
        self.uv = acc(d, self.bin, at['TEXCOORD_0']).astype(np.float64)
        self.parent = {}
        for i, n in enumerate(d['nodes']):
            for c in n.get('children', []):
                self.parent[c] = i
        self.name = {i: n.get('name') for i, n in enumerate(d['nodes'])}
        self.by_name = {v: k for k, v in self.name.items() if v}
        if 'skins' in d:
            sk = d['skins'][0]
            self.joints = sk['joints']
            self.ibm = acc(d, self.bin, sk['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1).astype(np.float64)
            self.J = acc(d, self.bin, at['JOINTS_0']).astype(int)
            self.W = acc(d, self.bin, at['WEIGHTS_0']).astype(np.float64)
            self.clips = {}
            for a in d.get('animations', []):
                ch = {}
                times = None
                for c in a['channels']:
                    s = a['samplers'][c['sampler']]
                    t = acc(d, self.bin, s['input'])[:, 0].astype(np.float64)
                    if times is None:
                        times = t
                    assert np.array_equal(times, t), f"{a['name']}: channels with different key times"
                    assert s.get('interpolation', 'LINEAR') == 'LINEAR'
                    ch[(c['target']['node'], c['target']['path'])] = acc(d, self.bin, s['output']).astype(np.float64)
                self.clips[a['name']] = (times, ch, len(a['channels']))

    def rest_trs(self, i):
        n = self.doc['nodes'][i]
        assert 'matrix' not in n or i == 0
        return (np.array(n.get('translation', [0, 0, 0]), float), np.array(n.get('rotation', [0, 0, 0, 1]), float),
                np.array(n.get('scale', [1, 1, 1]), float))

    def worlds(self, clip=None, k=0):
        ch = self.clips[clip][1] if clip else {}
        local = {}
        for i, n in enumerate(self.doc['nodes']):
            if 'matrix' in n:
                local[i] = np.array(n['matrix'], float).reshape(4, 4).T
                continue
            t, r, s = self.rest_trs(i)
            t = ch.get((i, 'translation'), [t])[k if (i, 'translation') in ch else 0]
            r = ch.get((i, 'rotation'), [r])[k if (i, 'rotation') in ch else 0]
            s = ch.get((i, 'scale'), [s])[k if (i, 'scale') in ch else 0]
            local[i] = trs(t, r / np.linalg.norm(r), s)
        world = {}

        def w(i):
            if i not in world:
                world[i] = local[i] if i not in self.parent else w(self.parent[i]) @ local[i]
            return world[i]
        for i in local:
            w(i)
        return world

    def skin(self, clip=None, k=0):
        world = self.worlds(clip, k)
        M = np.stack([world[j] @ self.ibm[n] for n, j in enumerate(self.joints)])     # (J,4,4)
        p = np.concatenate([self.pos, np.ones((len(self.pos), 1))], 1)
        out = np.zeros((len(self.pos), 3))
        for c in range(4):
            Mc = M[self.J[:, c]]                                                          # (N,4,4)
            out += self.W[:, c:c + 1] * np.einsum('nij,nj->ni', Mc, p)[:, :3]
        return out, world, M

    def joint_pos(self, world, name):
        return world[self.by_name[name]][:3, 3]


def max_quat_diff(a, b):
    return min(np.abs(a - b).max(), np.abs(a + b).max())


# --------------------------------------------------------------------- gate
def gate(raw_path, rig_path, report):
    raw_doc, raw_bin = parse(raw_path)
    R = Rig(rig_path)
    d = R.doc
    rp = raw_doc['meshes'][0]['primitives'][0]
    # ---- mesh
    nv, nt = len(R.pos), len(R.idx)
    check("mesh.counts", nv == 13085 and nt == 20060, f"{nv} verts / {nt} tris (raw 13085 / 20060)")
    drift = {}
    bitwise = True
    for attr in ("POSITION", "NORMAL", "TEXCOORD_0"):
        a = acc(raw_doc, raw_bin, rp['attributes'][attr]).astype(np.float64)
        b = acc(d, R.bin, R.prim['attributes'][attr]).astype(np.float64)
        drift[attr] = float(np.abs(a - b).max()) if a.shape == b.shape else float('inf')
        bitwise &= accessor_bytes(raw_doc, raw_bin, rp['attributes'][attr]) == accessor_bytes(d, R.bin, R.prim['attributes'][attr])
    idx_eq = accessor_bytes(raw_doc, raw_bin, rp['indices']) == accessor_bytes(d, R.bin, R.prim['indices'])
    worst = max(drift.values())
    check("mesh.drift", worst < 1.2e-5 and idx_eq,
          f"max |drift| POSITION {drift['POSITION']:.3g} NORMAL {drift['NORMAL']:.3g} TEXCOORD_0 {drift['TEXCOORD_0']:.3g}; "
          f"indices equal {idx_eq}; bitwise-identical {bitwise}")
    report['mesh'] = {"verts": nv, "tris": nt, "drift": drift, "bitwise": bool(bitwise)}
    # ---- texture / material
    report['texture_bytes'] = len(image_bytes(d, R.bin))
    if report.get('_pixelated'):
        pass
    else:
        same = image_bytes(raw_doc, raw_bin) == image_bytes(d, R.bin)
        check("texture.bytes", same and raw_doc['images'][0]['mimeType'] == d['images'][0]['mimeType'],
              f"{len(image_bytes(d, R.bin))} B {d['images'][0]['mimeType']} == raw atlas: {same}")
    mat_ok = d['materials'][0] == raw_doc['materials'][0] and 'baseColorTexture' in d['materials'][0]['pbrMetallicRoughness']
    check("material", mat_ok and d['samplers'] == raw_doc['samplers'] and d['textures'] == raw_doc['textures'],
          f"PBR {d['materials'][0]['pbrMetallicRoughness']}")
    # ---- skin
    sk = d.get('skins', [])
    names = [R.name[j] for j in R.joints] if sk else []
    topo = {n: R.name.get(R.parent.get(R.by_name[n])) for n in names}
    topo = {n: (p if p in PARENTS else None) for n, p in topo.items()}
    check("skin.topology", len(sk) == 1 and sorted(names) == sorted(PARENTS) and topo == PARENTS,
          f"{len(sk)} skin, {len(names)} joints: {sorted(names)}")
    report['joints'] = len(names)
    infl = (R.W > 0).sum(1)
    wsum = R.W.sum(1)
    check("skin.weights", infl.max() <= 4 and np.abs(wsum - 1).max() < 1e-5 and (infl >= 1).all(),
          f"influences hist {np.bincount(infl, minlength=5).tolist()}, |sum-1| max {np.abs(wsum - 1).max():.2g}")
    jn = {i: R.name[j] for i, j in enumerate(R.joints)}
    wj = {n: np.zeros(nv) for n in names}
    for c in range(4):
        for i, n in jn.items():
            wj[n] += np.where(R.J[:, c] == i, R.W[:, c], 0.0)
    x, y, z = R.pos.T
    jaw_out = int(((wj['Jaw'] > 0) & ~(z > 0.74)).sum())
    tail_out = int((((wj['Tail1'] + wj['Tail2'] + wj['Tail3']) > 0) & (z > -0.68)).sum())
    check("skin.jaw_tail_law", jaw_out == 0 and tail_out == 0,
          f"Jaw-weighted verts outside snout: {jaw_out}; Tail-weighted verts on rump/chest: {tail_out}; "
          f"Jaw verts {int((wj['Jaw'] > 0).sum())}, Tail verts {int(((wj['Tail1'] + wj['Tail2'] + wj['Tail3']) > 0).sum())}")
    # ---- clips
    cn = sorted(R.clips)
    check("clips.names", cn == sorted(SPEC), f"{cn}")
    report['clips'] = {}
    for name, spec in SPEC.items():
        times, ch, nch = R.clips[name]
        dur = float(times[-1] - times[0])
        animated = {k[0] for k in ch}
        ok = abs(dur - spec) / spec <= 0.05 and nch == len(animated) * 3 == 63 and times[0] == 0.0
        report['clips'][name] = {"duration_s": round(dur, 5), "spec_s": spec, "err_pct": round(100 * (dur - spec) / spec, 2),
                                 "channels": nch, "animated_bones": len(animated), "keys": len(times)}
        check(f"clip.{name}", ok, f"{dur:.4f}s (spec {spec}s, {100 * (dur - spec) / spec:+.2f}%), "
                                  f"{nch} channels = {len(animated)} bones x T/R/S, {len(times)} keys")
    # ---- root static + stance + seamless
    root = R.by_name['Root']
    rt = R.rest_trs(root)
    rmax = 0.0
    for name in SPEC:
        _, ch, _ = R.clips[name]
        rmax = max(rmax, np.abs(ch[(root, 'translation')] - rt[0]).max(),
                   max(max_quat_diff(q, rt[1]) for q in ch[(root, 'rotation')]),
                   np.abs(ch[(root, 'scale')] - rt[2]).max())
    check("root.static", rmax < 1e-6, f"Root max deviation from rest over all keys of all clips {rmax:.2g}")

    def frame_diff(ch, i, j):
        m = 0.0
        for (node, path), v in ch.items():
            m = max(m, max_quat_diff(v[i], v[j]) if path == 'rotation' else np.abs(v[i] - v[j]).max())
        return m

    def rest_diff(ch, i):
        m = 0.0
        for (node, path), v in ch.items():
            t, r, s = R.rest_trs(node)
            ref = {'translation': t, 'rotation': r, 'scale': s}[path]
            m = max(m, max_quat_diff(v[i], ref) if path == 'rotation' else np.abs(v[i] - ref).max())
        return m

    report['seamless'] = {}
    for name in LOOPS:
        _, ch, _ = R.clips[name]
        dfl = frame_diff(ch, 0, -1)
        report['seamless'][name] = dfl
        check(f"seamless.{name}", dfl < 1e-5, f"max |first - last| over 63 channels {dfl:.2g}")
    report['stance'] = {}
    for name in SPEC:
        _, ch, _ = R.clips[name]
        report['stance'][name] = {"start": rest_diff(ch, 0), "end": rest_diff(ch, -1)}
    st = report['stance']
    # one-shots enter/leave EXACTLY at the bind stance; Idle starts within its own
    # sway amplitude; gait loops are seamless cycles whose frame 0 is mid-stride
    st_ok = (all(st[k]['start'] < 1e-4 for k in ("WH_Wolf_Attack1", "WH_Wolf_Hit", "WH_Wolf_Death"))
             and all(st[k]['end'] < 1e-4 for k in ("WH_Wolf_Attack1", "WH_Wolf_Hit"))
             and st['WH_Wolf_Idle']['start'] < 0.08)
    check("stance.in_out", st_ok, "max TRS component deviation from bind stance start/end: " +
          ", ".join(f"{k[8:]} {v['start']:.4f}/{v['end']:.4f}" for k, v in st.items()) +
          " (Attack1/Hit/Death start + Attack1/Hit end must be < 1e-4; Idle start = its sway phase 0; "
          "Walk/Run frame 0 = mid-stride, seam-checked above; Death end = prone, checked below)")
    # ---- skinned measurements
    rest_v, rest_w, _ = R.skin()
    assert np.abs(rest_v - R.pos).max() < 1e-4, "bind pose does not reproduce the raw mesh"
    report['bind_reproduces_raw_max'] = float(np.abs(rest_v - R.pos).max())
    rest_h = {n: R.joint_pos(rest_w, n)[1] - GROUND for n in ("Spine", "Chest")}
    rest_top = rest_v[:, 1].max() - GROUND
    foot_dom = {leg: np.argmax(np.stack([wj[n] for n in names], 1), 1) == names.index(f"{leg}_Foot") for leg in LEGS}
    report['frames'] = {}
    for name in SPEC:
        times, ch, _ = R.clips[name]
        lows, hips, paws, tops, spine_h, chest_h, roll = [], {l: [] for l in LEGS}, {l: [] for l in LEGS}, [], [], [], []
        for k in range(len(times)):
            v, w, M = R.skin(name, k)
            lows.append(v[:, 1].min())
            tops.append(v[:, 1].max())
            for leg in LEGS:
                hips[leg].append(R.joint_pos(w, f"{leg}_UpperLeg")[1])
                paws[leg].append(v[foot_dom[leg], 1].min())
            spine_h.append(R.joint_pos(w, "Spine")[1] - GROUND)
            chest_h.append(R.joint_pos(w, "Chest")[1] - GROUND)
            Ms = M[names.index("Spine")][:3, :3]
            up = Ms @ np.array([0, 1.0, 0])
            roll.append(math.degrees(math.acos(max(-1, min(1, up[1] / np.linalg.norm(up))))))
        report['frames'][name] = {
            "lowest_min": float(min(lows)), "penetration_m": float(GROUND - min(lows)),
            "hip_p2p": {l: float(np.ptp(hips[l])) for l in LEGS},
            "paw_p2p": {l: float(np.ptp(paws[l])) for l in LEGS},
            "last": {"spine_h": spine_h[-1], "chest_h": chest_h[-1], "top_h": tops[-1] - GROUND,
                     "roll_deg": roll[-1], "lowest": lows[-1]},
        }
        if name in ("WH_Wolf_Walk", "WH_Wolf_Run"):
            check(f"ground.{name}", min(lows) >= GROUND - 0.02,
                  f"lowest skinned vertex {min(lows):+.4f} (ground {GROUND}, sink {GROUND - min(lows):+.4f} m, limit 0.02) over {len(times)} keys")
            hp = report['frames'][name]['hip_p2p']
            pp = report['frames'][name]['paw_p2p']
            check(f"cadence.{name}", min(hp.values()) > 0.02 and min(pp.values()) > 0.02,
                  "hip-joint height p2p " + " ".join(f"{l} {hp[l]:.3f}" for l in LEGS) +
                  " | paw height p2p " + " ".join(f"{l} {pp[l]:.3f}" for l in LEGS))
    # ---- death terminal pose (measured)
    times, ch, _ = R.clips["WH_Wolf_Death"]
    L = report['frames']["WH_Wolf_Death"]['last']
    settled = frame_diff(ch, -1, -2)
    v_last, _, _ = R.skin("WH_Wolf_Death", len(times) - 1)
    v_prev, _, _ = R.skin("WH_Wolf_Death", len(times) - 2)
    vel = float(np.abs(v_last - v_prev).max())
    ratio_s, ratio_c = L['spine_h'] / rest_h['Spine'], L['chest_h'] / rest_h['Chest']
    prone = ratio_s < 0.35 and ratio_c < 0.35 and L['roll_deg'] >= 60 and vel < 1e-3 and abs(L['lowest'] - GROUND) < 0.02
    check("death.prone", prone,
          f"last frame: pelvis {L['spine_h']:.3f} m = {100 * ratio_s:.1f}% of rest {rest_h['Spine']:.3f}; "
          f"chest {L['chest_h']:.3f} m = {100 * ratio_c:.1f}% of rest {rest_h['Chest']:.3f}; body roll {L['roll_deg']:.1f} deg; "
          f"mesh top {L['top_h']:.3f} m (rest {rest_top:.3f}); lowest vertex {L['lowest']:+.4f} (ground {GROUND}); "
          f"last-key vertex motion {vel * 1000:.3f} mm (settled)")
    report['death'] = {"pelvis_ratio": ratio_s, "chest_ratio": ratio_c, "roll_deg": L['roll_deg'], "settle_mm": vel * 1000,
                       "rest_heights": rest_h, "last": L}
    # ---- jaw (attack): open angle at windup, closed at contact (informational)
    times, ch, _ = R.clips["WH_Wolf_Attack1"]
    jaw = R.by_name['Jaw']
    r0 = R.rest_trs(jaw)[1]
    ang = [2 * math.degrees(math.acos(min(1.0, abs(float(np.dot(q / np.linalg.norm(q), r0)))))) for q in ch[(jaw, 'rotation')]]
    report['attack_jaw_deg'] = {"max": max(ang), "max_at_s": float(times[int(np.argmax(ang))]),
                                "series": [[round(float(t), 3), round(a, 1)] for t, a in zip(times, ang)]}
    print(f"[INFO] Attack1 jaw open max {max(ang):.1f} deg at {times[int(np.argmax(ang))]:.3f}s; "
          f"at contact key ~0.392s: {ang[int(np.argmin(np.abs(times - 0.392)))]:.1f} deg")
    print("[INFO] lowest skinned vertex per clip: " + ", ".join(
        f"{k[8:]} {v['lowest_min']:+.4f}" for k, v in report['frames'].items()))
    return R


def gate_pixelated(rig_path, pix_path, raw_path, report):
    from PIL import Image
    A, a_bin = parse(rig_path)
    P, p_bin = parse(pix_path)
    raw_doc, raw_bin = parse(raw_path)
    prim_a, prim_p = A['meshes'][0]['primitives'][0], P['meshes'][0]['primitives'][0]
    same = []
    for attr in ("POSITION", "NORMAL", "TEXCOORD_0", "JOINTS_0", "WEIGHTS_0"):
        same.append(accessor_bytes(A, a_bin, prim_a['attributes'][attr]) == accessor_bytes(P, p_bin, prim_p['attributes'][attr]))
    same.append(accessor_bytes(A, a_bin, prim_a['indices']) == accessor_bytes(P, p_bin, prim_p['indices']))
    same.append(accessor_bytes(A, a_bin, A['skins'][0]['inverseBindMatrices']) == accessor_bytes(P, p_bin, P['skins'][0]['inverseBindMatrices']))
    anim_same = True
    for aa, pa in zip(A['animations'], P['animations']):
        anim_same &= aa == pa
        for s in aa['samplers']:
            for f in ('input', 'output'):
                anim_same &= accessor_bytes(A, a_bin, s[f]) == accessor_bytes(P, p_bin, s[f])
    json_same = {k: A[k] == P[k] for k in A if k not in ('bufferViews', 'buffers', 'images')}
    check("pixelated.bytes", all(same) and anim_same and all(json_same.values()) and len(A['animations']) == len(P['animations']) == 6,
          f"POSITION/NORMAL/TEXCOORD_0/JOINTS_0/WEIGHTS_0/indices/IBM bytes identical {all(same)}; "
          f"6 animations + sampler accessors identical {anim_same}; JSON (minus bufferViews/buffers/images) identical {all(json_same.values())}")
    src = Image.open(io.BytesIO(image_bytes(raw_doc, raw_bin))).convert('RGB')
    want = (np.asarray(src.resize((512, 512), Image.NEAREST)) >> 3) << 3
    got = np.asarray(Image.open(io.BytesIO(image_bytes(P, p_bin))).convert('RGB'))
    check("pixelated.texture", got.shape == want.shape and np.array_equal(got, want),
          f"{P['images'][0]['mimeType']} {got.shape[1]}x{got.shape[0]}, pixel-exact v3 pixelation (512 NEAREST + 5-bit) of the raw atlas: "
          f"{np.array_equal(got, want)}; {len(image_bytes(P, p_bin))} B (raw atlas {len(image_bytes(raw_doc, raw_bin))} B)")


if __name__ == '__main__':
    args = sys.argv[1:]
    opts = {}
    pos = []
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            opts[args[i][2:]] = args[i + 1]
            i += 2
        else:
            pos.append(args[i])
            i += 1
    report = {}
    gate(pos[0], pos[1], report)
    if 'pixelated' in opts:
        prep = {"_pixelated": True}
        print(f"--- pixelated variant {opts['pixelated']}")
        gate(pos[0], opts['pixelated'], prep)
        gate_pixelated(pos[1], opts['pixelated'], pos[0], report)
    fails = [r for r in RESULTS if not r[1]]
    print(f"VERIFY GATE: {len(RESULTS) - len(fails)}/{len(RESULTS)} PASS" + (f"; FAIL: {[f[0] for f in fails]}" if fails else ""))
    if 'json' in opts:
        Path(opts['json']).write_text(json.dumps(report, indent=1, default=float))
    sys.exit(1 if fails else 0)
