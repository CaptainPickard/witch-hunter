#!/usr/bin/env python3
"""CC-H2b V1 seat freeze BY DATA - garrison supply nodes + armory dressing candidates.
Law (H2/ED1 precedent): seats locked before the spec freezes; the spec cites
the scan output. Constraints (gather.placement + H2 prop-scan precedent):
  node  vs node      >= spacingM   (no regionH row yet -> use global 6m, all 10 nodes)
  node  vs enemies   >= 5.0 m raw
  node  vs props     >= 4.0 m raw  (every landed prop row incl. wall ring w/ sz 2.40)
  node  vs spawn     >= 6.0 m      (0,-955)
  node  vs door plane>= 2.5 m off the breach lane (z -948, |x|<=5 w/ pad)
  node  inside rim   rho <= 74.5   (playable 78.5 minus node-base clearance margin 4)
  node  vs light props: keep >= 3.0 m from the four warm sockets' seats
  armory dressing rows: vs everything >= 4.0, mutual >= 4.0, rho <= 74.5
Identity: no new asset ids (manifest assets only), no new node types.
"""
import math, json

# --- landed state (read straight from the worktree HEAD census) ----------------
ENEMIES = [(-10, -975), (11, -976)]
SPAWN   = (0, -955)
# every CONFIG regionH props row (asset,x,z) - dressing + wall ring
PROPS = [
    ('whTent',44,-1058), ('whCampkit',38,-1052), ('whCampkit',41,-1064),
    ('okRuinColumn',52,-1050), ('stoneSteps',-46,-1064), ('skullPile',-50,-1050),
    ('b6Bones',-42,-1076), ('rubblePile',-34,-1072), ('stoneSteps',0,-1097),
    ('torch',4,-1093), ('torch',-4,-1093), ('banditCampfire',0,-990),
    ('lanternPost',6.5,-954), ('mossBoulder',26,-1000), ('mossBoulder',-24,-1030),
    ('rubblePile',58,-992), ('okFenceStonewall',10,-968), ('okFenceStonewall',-10,-968),
    ('whWallB',10,-968), ('whWallB',-10,-968),
]
# wall ring (wall:8) sampled at its landed x,z (48 rows) - collider footprint sz 2.40
WALLS = [
    (14.99,-945.42),(24.72,-947.92),(34.06,-951.61),(42.87,-956.45),(50.99,-962.36),
    (58.32,-969.24),(64.72,-976.98),(70.1,-985.46),(74.38,-994.55),(77.49,-1004.1),
    (79.37,-1013.97),(80.0,-1024.0),(79.37,-1034.03),(77.49,-1043.9),(74.38,-1053.45),
    (70.1,-1062.54),(64.72,-1071.02),(58.32,-1078.76),(50.99,-1085.64),(42.87,-1091.55),
    (34.06,-1096.39),(24.72,-1100.08),(14.99,-1102.58),(5.02,-1103.84),
    (-5.02,-1103.84),(-14.99,-1102.58),(-24.72,-1100.08),(-34.06,-1096.39),
    (-42.87,-1091.55),(-50.99,-1085.64),(-58.32,-1078.76),(-64.72,-1071.02),
    (-70.1,-1062.54),(-74.38,-1053.45),(-77.49,-1043.9),(-79.37,-1034.03),
    (-80.0,-1024.0),(-79.37,-1013.97),(-77.49,-1004.1),(-74.38,-994.55),
    (-70.1,-985.46),(-64.72,-976.98),(-58.32,-969.24),(-50.99,-962.36),
    (-42.87,-956.45),(-34.06,-951.61),(-24.72,-947.92),(-14.99,-945.42),
]
LIGHT_SOCKETS = [(0,-990),(6.5,-954),(38,-1052),(41,-1064)]   # amber family seats

def d(ax,az,bx,bz): return math.hypot(ax-bx, az-bz)

def scan_node(t,x,z,nodes):
    fails=[]
    rho=math.hypot(x,z+1024)
    if rho>74.5: fails.append(f"rho {rho:.1f}>74.5")
    for tx,tz in ((x,z-2.4),(x,z+2.4),(x-2.4,z),(x+2.4,z),(x-1.7,z-1.7),(x+1.7,z-1.7),(x-1.7,z+1.7),(x+1.7,z+1.7)):
        if math.hypot(tx,tz+1024)>78.5: fails.append(f"4-dir+diag footprint off disc @({tx},{tz})")
    if d(x,z,*SPAWN)<6.0: fails.append(f"spawn {d(x,z,*SPAWN):.1f}<6")
    for ex,ez in ENEMIES:
        if d(x,z,ex,ez)<5.0: fails.append(f"enemy({ex},{ez}) {d(x,z,ex,ez):.1f}<5")
    for _,px,pz in PROPS:
        if d(x,z,px,pz)<4.0: fails.append(f"prop {px},{pz} {d(x,z,px,pz):.1f}<4")
    for wx,wz in WALLS:
        if d(x,z,wx,wz)<4.0: fails.append(f"wall {wx},{wz} {d(x,z,wx,wz):.1f}<4")
    # breach lane: |x|<=5 is the door corridor with pad; nodes must sit >=2.5m off it
    if abs(x)<=5 and abs(z-(-948))<7.5: fails.append("breach lane corridor")
    for lx,lz in LIGHT_SOCKETS:
        if d(x,z,lx,lz)<3.0: fails.append(f"light {lx},{lz} {d(x,z,lx,lz):.1f}<3")
    for (t_,tx,tz) in nodes:
        if (tx,tz)!=(x,z) and d(x,z,tx,tz)<6.0: fails.append(f"spacing 6 vs {tx},{tz}: {d(x,z,tx,tz):.1f}")
    return fails

def scan_prop(t,x,z,rows):
    fails=[]
    rho=math.hypot(x,z+1024)
    if rho>74.5: fails.append(f"rho {rho:.1f}>74.5")
    if d(x,z,*SPAWN)<6.0: fails.append(f"spawn {d(x,z,*SPAWN):.1f}<6")
    for ex,ez in ENEMIES:
        if d(x,z,ex,ez)<5.0: fails.append(f"enemy({ex},{ez}) {d(x,z,ex,ez):.1f}<5")
    for (_,px,pz) in PROPS:
        if (px,pz)!=(x,z) and d(x,z,px,pz)<4.0: fails.append(f"prop {px},{pz} {d(x,z,px,pz):.1f}<4")
    for wx,wz in WALLS:
        if d(x,z,wx,wz)<4.0: fails.append(f"wall {wx},{wz} {d(x,z,wx,wz):.1f}<4")
    for (_p,rx,rz) in props:
        if (rx,rz)!=(x,z) and d(x,z,rx,rz)<4.0: fails.append(f"mutual {rx},{rz} {d(x,z,rx,rz):.1f}<4")
    for lx,lz in LIGHT_SOCKETS:
        if (lx,lz)!=(x,z) and d(x,z,lx,lz)<3.0: fails.append(f"light {lx},{lz} {d(x,z,lx,lz):.1f}<3")
    return fails

# --- candidate seats (drafted by census, frozen by this scan) ------------------
NODE_CANDIDATES = [
    # dungeon-mouth ossuary corner (west): 3x bonePile - what the garrison ate
    ('bonePile', -56.0, -1032.0),
    ('bonePile', -63.0, -1044.0),
    ('bonePile', -50.0, -1044.0),
    # armory corner (east): 2x ironVein - quartermaster ore store (doc 42 feed)
    ('ironVein', 66.0, -1042.0),
    ('ironVein', 58.0, -1050.0),
    # mid-yard wreck rows: 3x bonePile + 2x moss/stone flavor = no; keep loot-only
    ('bonePile', 22.0, -1046.0),
    ('bonePile', -20.0, -992.0),
    # breach-approach flank pair (yard-side of the sentries, clear of mouth lane)
    ('bonePile', -13.0, -986.0),
    ('bonePile', 13.0, -986.0),
    # yard-edge ossuary tail
    ('bonePile', 44.0, -996.0),
    ('ironVein', 44.0, -1022.0),
]
# armory dressing candidates (assets from manifest only, no light sockets;
# ALL point-collider assets - whWallB WITHOUT wall: key takes ONE trunk
# collider -> ghost-ends, banned this round)
PROP_CANDIDATES = [
    ('b6Bones', 46, -1076),   # collapsed-arms clutter leaning in the armory corner
    ('rubblePile', 36, -1042),# rubble between kits and boulder
    ('okFenceStonewall', -66, -1024), # west ossuary partition (rotY pi/2 handled in spec)
    ('graveMound', -58, -1008), # ossuary mound row (manifest asset)
]

nodes=[(t,x,z) for (t,x,z) in NODE_CANDIDATES]
props=[(t,x,z) for (t,x,z) in PROP_CANDIDATES]
passed=0; failed=0; detail={}
for (t,x,z) in nodes:
    f=scan_node(t,x,z,nodes)
    detail[f"node {t} {x},{z}"]=f
    passed+= 0 if f else 1; failed+= 1 if f else 0
for (t,x,z) in props:
    f=scan_prop(t,x,z,props)
    detail[f"prop {t} {x},{z}"]=f
    passed+= 0 if f else 1; failed+= 1 if f else 0

print("=== CC-H2b SEAT SCAN (11 nodes + 4 dressing rows) ===")
for k,v in detail.items():
    print(("PASS " if not v else "FAIL ") + k + ("" if not v else "  -> " + "; ".join(v)))
print(f"TOTAL {passed} PASS / {failed} FAIL")
