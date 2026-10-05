#!/usr/bin/env python3
"""Round J: name-gated groundSink for the reach-trees (CONFIG + assets.js).
usage: roundJ_patch.py <repo root>  (idempotent; esprima-validates both)"""
import sys, esprima
from pathlib import Path
root = Path(sys.argv[1]) / 'prototype/js'

cfg = root / 'CONFIG.js'
s = cfg.read_text()
anchor = "    standInColor: 0x777777,\n"
block = anchor + """    // Round J (io/roundJ-provenance.md): the Meshy reach-trees are open-
    // bottomed shells whose root tips hang below the trunk floor, so
    // groundAlign (lowest vertex -> y=0) stood them on those tips with sky
    // under the trunk (0.27/0.80/0.39m median gap at scale 10). Extra sink
    // in GLB units (scales with every placement + scatter scale) = p75 of the
    // trunk-underside height (scratch/roundJ_underside.py). {} = old look.
    groundSink: { reachTreeA: 0.0312, reachTreeB: 0.0878, reachTreeC: 0.0500 },
"""
if 'groundSink:' not in s:
    assert s.count(anchor) == 1
    s = s.replace(anchor, block)
    cfg.write_text(s)

aj = root / 'assets.js'
s = aj.read_text()
a1 = "        cache[name] = groundAlign(root);\n"
a2 = """  // 2026-10-03 measured weapon sizing"""
fn = """  // Round J: per-asset extra sink below the groundAlign floor, gated by
  // name via CONFIG.assets.groundSink (GLB units, so it scales with the
  // holder). GROUND_META keeps the measured bounds; the sink is recorded.
  function applyGroundSink(name, root) {
    var sinks = CFG.assets && CFG.assets.groundSink;
    var sink = sinks && sinks[name];
    if (!(sink > 0)) return;
    var holder = root.parent;
    root.position.y -= sink;
    holder.updateMatrixWorld(true);
    GROUND_META[holder.uuid].groundSink = sink;
  }

"""
if 'applyGroundSink' not in s:
    assert s.count(a1) == 1 and s.count(a2) == 1
    s = s.replace(a1, a1 + "        applyGroundSink(name, root);\n")
    s = s.replace(a2, fn + a2)
    aj.write_text(s)

for f in (cfg, aj):
    esprima.parseScript(f.read_text())
    print('esprima OK', f)
