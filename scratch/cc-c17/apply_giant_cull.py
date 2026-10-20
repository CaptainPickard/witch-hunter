#!/usr/bin/env python3
"""CC-C17v2 ROW SHAPE LAW alignment (v2 brief: 'Region C tree/props rows: same
shape as the C4b giants ({ asset, x, z, rotY, scale, cullM: 140 })'). The live C
giant rows carry NO cullM (they hide at cullDistanceM 170), so the brief's own
budget premise did not hold: the full v2 set measured 2,071,776 (103.6%) on the
west plateau. This gives the 54 live (uncommented) regionC yewTree/witchwoodTree
rows cullM 140 - x/z/rotY/scale untouched. Visual: none by the CONFIG's own
FOG-CULL COHERENCE rule (show band 140 x 0.92 = 128.8 m > the 94.2 m fog-visible
reach at the thinnest C fog) - the CC-C8 outcrop precedent (cullM 120).
Rollback: delete ', cullM: 140 }   // CC-C17 shape' -> ' }' on those rows."""
import re
CFG = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
src = open(CFG).read()
i = src.index('  regionC: {'); j = src.index('  regionD: {')
blk = src[i:j]
pat = re.compile(r"(?m)^(      \{ asset: '(?:yewTree|witchwoodTree)',\s+x: [-\d.]+, z: [-\d.]+, rotY: [\d.]+, scale: [\d.]+) \},$")
blk2, n = pat.subn(r"\1, cullM: 140 },   // CC-C17 shape", blk)
assert n == 54, n
anchor = "      // king specimen giants (R-62.6 rare band 28-30): lane + Stone approach anchors\n"
assert blk2.count(anchor) == 1
blk2 = blk2.replace(anchor, "      // CC-C17 ROW SHAPE LAW: every live giant row below carries cullM 140 (the v2\n"
                    "      // brief's C4b-giant shape; hide 140 / show 128.8 m > the 94.2 m fog reach = no\n"
                    "      // visible pop). Ledger relief for the C17 set (scratch/cc-c17/apply_giant_cull.py).\n" + anchor)
open(CFG, 'w').write(src[:i] + blk2 + src[j:])
print('giant rows -> cullM 140:', n)
