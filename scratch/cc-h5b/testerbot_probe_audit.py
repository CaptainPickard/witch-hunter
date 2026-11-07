#!/usr/bin/env python3
"""CC-H5b Testerbot probe audit — source-level checks on the amended probe."""
import re
import sys

P = "/tmp/wh-worldfeat/scratch/cc-h5b/probe_placement.py"
src = open(P).read()

# PA-1 hardcode scan
hits = [l for l in src.splitlines()
        if re.search(r"-5\.5|\b6\.5|-6\.0|(?<![\d.])3\.0(?![\d.])", l)]
print("PA-1 vent-literal scan:", "CLEAN" if not hits else "HITS: %r" % hits)
adv = [l for l in src.splitlines() if re.search(r"-864|-869|-894|-897", l)]
print("PA-1 advisory z-scan hits (report-only): %d -> %s" % (len(adv), adv))

# PA-2 seat-source proof
evals = re.findall(r"readFileSync\(process\.argv\[\d\]", src)
seat_src = "K.hazards.vents" in src and "WH_CONFIG" in src
print("PA-2: two readFileSync evals found:", len(evals) == 2)
print("PA-2: seats read from WH_CONFIG K.hazards.vents:", seat_src)

# WIDTHS truth table (Testerbot-measured GLB x-extents)
truth = {"mourningStatue": 1.862, "okRuinColumn": 0.957, "stoneSteps": 1.948,
         "skullPile": 2.0, "lanternPost": 0.59, "blightcap": 1.692,
         "mossBoulder": 1.897}
m = re.search(r"WIDTHS = \{(.*?)\}", src, re.S)
tbl = dict(re.findall(r"\"(\w+)\":\s*([\d.]+)", m.group(1)))
ok = True
for k, v in sorted(tbl.items()):
    t = truth[k]
    match = abs(float(v) - t) <= 0.005
    print("WIDTHS[%s] = %s vs testerbot-measured %s: %s"
          % (k, v, t, "MATCH" if match else "MISMATCH"))
    ok &= match
print("WIDTHS map complete (7 assets):", len(tbl) == 7)
ok &= (len(tbl) == 7)

# Floors
line = next((l.strip() for l in src.splitlines()
             if l.strip().startswith("F_RING")), "")
lhs, rhs = line.split("=")
vals = [float(v) for v in rhs.split(",")]
names = [x.strip() for x in lhs.split(",")]
lines = dict(zip(names, vals))
law = {"F_RING": 1.0, "F_ENEMY": 5.0, "F_PROP": 2.0, "F_BOSS": 6.0,
       "F_LAND": 4.0, "F_WALKIN": 2.5}
for n, v in lines.items():
    good = abs(law[n] - v) < 1e-9
    print("floor %s = %s (law %s): %s" % (n, v, law[n], "MATCH" if good else "MISMATCH"))
    ok &= good

ok &= (not hits) and len(evals) == 2 and seat_src
print("AUDIT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
