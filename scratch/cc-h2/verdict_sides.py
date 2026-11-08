#!/usr/bin/env python3
"""verdict_sides.py — Testerbot INDEPENDENT V-5 probe (CC-H2 garrison round).

Own probe, written per valspec sec 4 V-5 (python-fallback shape): parse the
LANDED prototype/js/CONFIG.js regionH.door + prototype/js/region-defs.js
connections[6] live with regex, replicate sideOfPlane = z > planeCoord ? 1 : -1
(the region-defs.js:314 definition), and assert the doc 66 sec 10 interior law.
NO spec constants feed the assertions -- planeCoord, sides signs, land rows all
come from the parsed landed text. Read-only over the worktree.
"""
import re
import sys

ROOT = '/tmp/wh-worldfeat'

cfg_src = open(ROOT + '/prototype/js/CONFIG.js').read()
rdefs_src = open(ROOT + '/prototype/js/region-defs.js').read()

fails = []
checks = []


def check(name, ok, detail=''):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name)
    print('%-4s %s%s' % ('PASS' if ok else 'FAIL', name,
                         ('  [' + detail + ']') if detail else ''))


def need(name, m):
    ok = m is not None
    check(name, ok)
    if not ok:
        sys.exit(1)
    assert m is not None
    return m


# ---- parse regionH door block from CONFIG.js (live) -------------------------
m_rh = need('anchor: regionH block found in CONFIG.js',
            re.search(r'\n  regionH: \{', cfg_src))
dblob = cfg_src[m_rh.start():]
m_door = need('anchor: regionH.door block found', re.search(r'door: \{', dblob))
dblk = dblob[m_door.start():m_door.start() + 2600]

m_g = need('anchor: regionG block found', re.search(r'\n  regionG: \{', cfg_src))
gblob = cfg_src[m_g.start():m_g.start() + 400]
m_gid = need('regionG id parsed', re.search(r"id: '([a-z_]+)'", gblob))
g_id = m_gid.group(1)
m_hid = need('regionH id parsed', re.search(r"id: '([a-z_]+)'", dblob[:300]))
h_id = m_hid.group(1)
check('region ids: G=%s H=%s' % (g_id, h_id),
      g_id == 'lords_hold' and h_id == 'fort_garrison')

checks.pop()  # drop the informative id line from the failure count bookkeeping
if not (g_id == 'lords_hold' and h_id == 'fort_garrison'):
    fails.append('region ids')

m_pz = need('CONFIG regionH.door.planeZ parsed',
            re.search(r'planeZ: (-?[\d.]+)', dblk))
m_dx = need('CONFIG regionH.door.doorX parsed', re.search(r'doorX: (-?[\d.]+)', dblk))
m_hw = need('CONFIG regionH.door.doorHalfWidth parsed',
            re.search(r'doorHalfWidth: (-?[\d.]+)', dblk))
m_sd = need('CONFIG regionH.door.suspendDepthM parsed',
            re.search(r'suspendDepthM: (-?[\d.]+)', dblk))
plane_z = float(m_pz.group(1))
door_x = float(m_dx.group(1))
half_w = float(m_hw.group(1))
suspend = float(m_sd.group(1))

m_land_h = need('land.fort_garrison row parsed',
                re.search(h_id + r':\s*\{ x: (-?[\d.]+), z: (-?[\d.]+), faceX: (-?[\d.]+), faceZ: (-?[\d.]+) \}', dblk))
m_land_g = need('land.lords_hold row parsed',
                re.search(g_id + r':\s*\{ x: (-?[\d.]+), z: (-?[\d.]+), faceX: (-?[\d.]+), faceZ: (-?[\d.]+) \}', dblk))
land_h_z = float(m_land_h.group(2))
land_g_z = float(m_land_g.group(2))

# ---- parse conn[6] block from region-defs.js (live) -------------------------
m_hd = need('anchor: var HD in region-defs.js',
            re.search(r'var HD = CFG\.regionH\.door;', rdefs_src))
push_blk = rdefs_src[m_hd.start():m_hd.start() + 1200]
m_push = need('anchor: connections.push after var HD',
              re.search(r'connections\.push', push_blk))
m_mb = need('anchor: conn push end (}});) before sides rows',
            re.search(r'\}\);\s*\n\s*// SIDES TABLE \(CC-H2', push_blk))
side_blk = push_blk[:m_mb.start()]
m_mb2 = need('anchor: SIDES TABLE banner present', m_mb)

check('conn[6] connection keys: from: CFG.regionG.id', 'from: CFG.regionG.id' in side_blk)
check('conn[6] connection keys: to: CFG.regionH.id', 'to: CFG.regionH.id' in side_blk)
check("conn[6] connection keys: axis: 'z'", "axis: 'z'" in side_blk)
check('conn[6] connection keys: planeCoord: HD.planeZ', 'planeCoord: HD.planeZ' in side_blk)
check('conn[6] connection keys: sides: {}', 'sides: {}' in side_blk)
check('conn[6] door keys: doorX: HD.doorX', 'doorX: HD.doorX' in side_blk)
check('conn[6] door keys: doorHalfWidth: HD.doorHalfWidth', 'doorHalfWidth: HD.doorHalfWidth' in side_blk)
check('conn[6] door keys: suspendDepthM: HD.suspendDepthM', 'suspendDepthM: HD.suspendDepthM' in side_blk)
check('conn[6] door keys: wallGapPadM: HD.wallGapPadM', 'wallGapPadM: HD.wallGapPadM' in side_blk)
check('conn[6] door keys: arch: null', 'arch: null' in side_blk)
check('conn[6] door keys: gatedTo: null', 'gatedTo: null' in side_blk)
check('conn[6] door keys: land: HD.land', 'land: HD.land' in side_blk)
check('conn[6] NO walkFrom row', 'walkFrom' not in side_blk)
check('conn[6] NO interact row', 'interact' not in side_blk)

m_side_blk = rdefs_src[m_hd.start():]
m_sg = need('sides row conn[6].regionG parsed',
            re.search(r'connections\[6\]\.sides\[CFG\.regionG\.id\] = (-?\d);', m_side_blk))
m_sh = need('sides row conn[6].regionH parsed',
            re.search(r'connections\[6\]\.sides\[CFG\.regionH\.id\] = (-?\d);', m_side_blk))
side_g = int(m_sg.group(1))
side_h = int(m_sh.group(1))

# ---- replicate sideOfPlane (region-defs.js:314 definition) ------------------
def side_of_plane(z):
    return 1 if z > plane_z else -1


def side_in(region_id):
    return side_g if region_id == g_id else side_h


# ---- doc 66 sec 10 interior law, BOTH entries -------------------------------
check("sideOfPlane(conn6, -822) === 1  === sideIn(conn6, 'lords_hold')",
      side_of_plane(-822.0) == 1 == side_in(g_id),
      'sideOfPlane=%d sideIn=%d' % (side_of_plane(-822.0), side_in(g_id)))
check("sideOfPlane(conn6, -1024) === -1 === sideIn(conn6, 'fort_garrison')",
      side_of_plane(-1024.0) == -1 == side_in(h_id),
      'sideOfPlane=%d sideIn=%d' % (side_of_plane(-1024.0), side_in(h_id)))

# land rows on home sides
check('land.fort_garrison z %.1f <= planeCoord %.1f (H home side)'
      % (land_h_z, plane_z), land_h_z <= plane_z)
check('land.lords_hold z %.1f > planeCoord %.1f (G home side)'
      % (land_g_z, plane_z), land_g_z > plane_z)

# generality clause: sideIn(R) == sideOfPlane(R interior) for EVERY member,
# and neither region lies ON the plane (interiors strictly off plane_z)
for rid, interior in ((g_id, -822.0), (h_id, -1024.0)):
    check('generality: sideIn(%s) == sideOfPlane(interior %.0f)' % (rid, interior),
          side_in(rid) == side_of_plane(interior))
    check('%s interior strictly OFF the plane (not ON %.0f)' % (rid, plane_z),
          interior != plane_z)

# ---- sides sign cross-check against the plane geometry ----------------------
check('sides signs match sideOfPlane at interiors',
      side_g == side_of_plane(-822.0) and side_h == side_of_plane(-1024.0),
      'G=%d H=%d' % (side_g, side_h))

# sec 10 item 2 plane-on-edge sanity: record both margins (parsed radii)
m_cz = need('regionH center parsed', re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', dblob[:600]))
m_gr = need('regionH groundRadius parsed', re.search(r'groundRadius: (-?[\d.]+)', dblob[:600]))
m_ggr = need('regionG groundRadius parsed', re.search(r'groundRadius: (-?[\d.]+)', gblob[:900]))
h_center_z = float(m_cz.group(2))
h_ground_r = float(m_gr.group(1))
g_ground_r = float(m_ggr.group(1))
# G center z (parse, don't assume)
m_gcz = need('regionG center parsed', re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', gblob[:600]))
g_center_z = float(m_gcz.group(2))
# H2 door-side rim is the NORTH rim: center + radius (z larger = toward -948)
h_rim_full = h_center_z + h_ground_r          # -1024 + 80 = -944
h_rim_play = h_center_z + (h_ground_r - 1.5)  # -945.5
margin_h_full = abs(plane_z - h_rim_full)
margin_h_play = abs(plane_z - h_rim_play)
# G door-side rim is the SOUTH rim: center - radius
g_rim_full = g_center_z - g_ground_r          # -822 - 126 = -948
g_rim_play = g_center_z - (g_ground_r - 1.5)  # -946.5
margin_g_play = abs(plane_z - g_rim_play)
check('plane inside BOTH playable rims (not at a disc center)',
      0.5 < margin_h_play < 20.0 and 0.0 < margin_g_play < 20.0,
      'H play rim %.1f margin %.2f m; G play rim %.1f margin %.1f m'
      % (h_rim_play, margin_h_play, g_rim_play, margin_g_play))
check('H full-rim margin == 4.0 m (planeZ -948 vs rim -944)',
      abs(margin_h_full - 4.0) <= 0.01, 'margin %.3f (full rim %.1f)' % (margin_h_full, h_rim_full))
check('H play-rim gap == 2.5 m (planeZ -948 vs playable rim -945.5)',
      abs(margin_h_play - 2.5) <= 0.01, 'margin %.3f' % margin_h_play)
check('G play-rim margin == 1.5 m (planeZ -948 vs playable south rim -946.5)',
      abs(margin_g_play - 1.5) <= 0.01, 'margin %.3f' % margin_g_play)
check('suspendDepthM == 4 (both-side reach, H1a trap)', suspend == 4.0,
      'suspendDepthM %.1f' % suspend)
check('suspendDepthM covers BOTH play-rim gaps (4 >= 2.5 and >= 1.5)',
      suspend >= margin_h_play and suspend >= margin_g_play,
      'suspend %.1f vs gaps %.2f/%.1f' % (suspend, margin_h_play, margin_g_play))
check('doorHalfWidth == 4.0 (the breach lane |x| <= 4)', half_w == 4.0,
      'halfWidth %.1f' % half_w)
check('doorX == 0 (breach lane rides x 0)', door_x == 0.0, 'doorX %.1f' % door_x)
check('spawn depth past plane >= suspendDepthM',
      abs(-955.0 - plane_z) >= suspend, 'depth %.1f' % abs(-955.0 - plane_z))

print('---')
print('VERDICT SIDES PROBE: %d checks, %d FAIL' % (len(checks), len(fails)))
if not fails:
    print('VERDICT PROBES: PASS (%d checks)' % len(checks))
sys.exit(0 if not fails else 1)
