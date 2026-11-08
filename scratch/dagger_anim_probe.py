#!/usr/bin/env python3
"""A1 candidate measurement for the dagger anim swap (plain python + numpy FK,
Rig/LBS from scratch/verify_dagger_clips.py; no Blender, no browser).

    python3 scratch/dagger_anim_probe.py CANDIDATES.glb OUT.json

Model space (glTF): +Y up, +Z forward, +X = character's LEFT. Per candidate
(30 fps native keys, retargeted by scratch/dagger_anim_retarget.py probe):
  impact      = global max |R_Hand velocity| (swordpack_probe4 method)
  strike      = contiguous run around impact where speed >= 20 % of peak
  direction   = sign of hand dx across the strike (+ = R->L), measured in the
                Hips-yaw frame too (spin clips rotate the whole body)
  arc         = hand height at strike start/impact/end vs shoulder (flat/overhead)
  swings      = speed peaks >= 50 % of max separated by dips < 30 % (combo test)
  yaw         = unwrapped Hips yaw travel over the clip (spin test)
  sanity      = finite curves, unit quats, min skinned vertex y.
"""
import json
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from verify_dagger_clips import Rig, lbs_setup, skin_min_y

FPS = 30


def yaw_of(M):
    f = M[:3, :3] @ np.array([0.0, 0.0, 1.0])
    return np.degrees(np.arctan2(f[0], f[2]))


def measure(R, S, clip, rest_hips):
    an = R.anims[clip]
    times = sorted(set(np.round(np.concatenate([v[0] for v in an.values()]), 5)))
    finite = all(np.isfinite(v[1]).all() and np.isfinite(v[0]).all() for v in an.values())
    qn = max(float(np.abs(np.linalg.norm(v[1], axis=1) - 1).max())
             for (i, p), v in an.items() if p == 'rotation')
    hand, blade, yaw, hy = [], [], [], []
    for t in times:
        M = R.world('R_Hand', clip, t)
        H = R.world('Hips', clip, t)
        hand.append(M[:3, 3])
        blade.append(M[:3, 2])
        yaw.append(yaw_of(H @ np.linalg.inv(rest_hips)))
    hand, blade = np.array(hand), np.array(blade)
    yaw = np.unwrap(np.radians(yaw))
    yaw = np.degrees(yaw - yaw[0])
    sp = np.linalg.norm(np.diff(hand, axis=0), axis=1) * FPS
    vi = int(np.argmax(sp))
    peak = sp[vi]
    a = vi
    while a > 0 and sp[a - 1] >= 0.2 * peak:
        a -= 1
    b = vi
    while b < len(sp) - 1 and sp[b + 1] >= 0.2 * peak:
        b += 1
    s0, s1 = a, b + 1          # hand samples bracketing the strike
    # combo test: peaks >= 50 % separated by a dip < 30 %
    peaks, armed = [], True
    for k in range(1, len(sp) - 1):
        if sp[k] < 0.3 * peak:
            armed = True
        if armed and sp[k] >= 0.5 * peak and sp[k] >= sp[k - 1] and sp[k] >= sp[k + 1]:
            peaks.append(k)
            armed = False

    def local_x(k):   # hand x in the Hips-yaw frame (de-spun)
        th = np.radians(yaw[k])
        c, s = np.cos(th), np.sin(th)
        x, z = hand[k][0], hand[k][2]
        return c * x - s * z
    dx = hand[s1][0] - hand[s0][0]
    dxl = local_x(s1) - local_x(s0)
    mins = [skin_min_y(R, S, clip, t) for t in times[::2]]
    step = {}   # per-bone max rotation per native frame (verify's no-explosion reference)
    for j in R.js['skins'][0]['joints']:
        q = np.array([R.channel(clip, j, 'rotation', t) for t in times])
        d = np.abs(np.sum(q[1:] * q[:-1], axis=1)).clip(0, 1)
        step[R.nodes[j]['name']] = round(float(np.degrees(2 * np.arccos(d)).max()), 2)
    return {
        'frames': len(times), 'sec': round(times[-1], 3),
        'finite': bool(finite), 'max_quat_norm_err': qn,
        'impact_frame': vi, 'impact_sec': round(vi / FPS, 3), 'peak_speed_mps': round(float(peak), 2),
        'strike_frames': [s0, s1], 'strike_sec': round((s1 - s0) / FPS, 3),
        'hand_x_strike': [round(float(hand[s0][0]), 3), round(float(hand[s1][0]), 3)],
        'dx_world': round(float(dx), 3), 'dx_hipsframe': round(float(dxl), 3),
        'direction': 'R->L' if dxl > 0.1 else ('L->R' if dxl < -0.1 else 'none'),
        'hand_y_strike_start_imp_end': [round(float(hand[k][1]), 3) for k in (s0, vi, s1)],
        'hand_y_max': round(float(hand[:, 1].max()), 3),
        'swing_peaks': peaks, 'n_swings': len(peaks),
        'yaw_total_deg': round(float(yaw[-1]), 1), 'yaw_span_deg': round(float(yaw.max() - yaw.min()), 1),
        'yaw_during_strike_deg': round(float(yaw[s1] - yaw[s0]), 1),
        'min_skinned_y': round(float(min(mins)), 4),
        'hand_start_end_gap': round(float(np.linalg.norm(hand[0] - hand[-1])), 3),
        'bone_max_step_deg_per_frame': step,
    }


def main(glb, out):
    R = Rig(glb)
    S = lbs_setup(R)
    sh = R.world('R_UpperArm')[1, 3]
    rest_hips = R.world('Hips')
    res = {'shoulder_y': round(float(sh), 3), 'ground_y': -1.0, 'clips': {}}
    for clip in R.anims:
        if not clip.startswith('CAND_'):
            continue
        m = measure(R, S, clip, rest_hips)
        y0, yi, y1 = m['hand_y_strike_start_imp_end']
        m['arc'] = 'overhead' if (y0 > sh - 0.05 and y0 - y1 > 0.5) else 'flat/diagonal'
        res['clips'][clip] = m
        print(clip, json.dumps({k: v for k, v in m.items() if k != 'bone_max_step_deg_per_frame'}, default=float))
    json.dump(res, open(out, 'w'), indent=1, default=float)


if __name__ == '__main__':
    main(*sys.argv[1:3])
