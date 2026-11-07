# CC-H5b probe v2 amendment — IO note (2026-11-07, wake 24)

The FAIL verdict's remedy items (valspec V-7 remediation, all implemented in
scratch/cc-h5b/probe_placement.py): (1) corridor-cycle analysis — 2-D band
overlap math + walker timing, printed per run; (2) the three C2 audit blocks —
no-new-lights / no-new-assets / draw-call budget (makeCard cites + pipe clone
count) all present per run; (3) B1 floors enforced at spec numbers: 2.0 m prop
edge, 6.0 m boss, 5.0 m enemy, 4.0 m land, 2.5 m walk-in, plus P1 ring-edge
1.0 m and P7 disc — every seat × every floor.

## Width finding (disclosed for the re-verdict)

The v1 probe's printed edges (6.84 / 1.81 / 1.35 / 1.16 m — the numbers in the
FAIL report) came from a width map that does not reflect engine truth. The
engine collider is colliderRadius(name, meta.width, scale) with meta.width =
Box3.setFromObject X-extent (assets.js:428-433, prepTemplate applies no
scaling; node-transform walk + per-vertex numpy both verify):
  mourningStatue 1.862, okRuinColumn 0.957, stoneSteps 1.948,
  skullPile 2.0, lanternPost 0.59, blightcap 1.692, mossBoulder 1.897.
Implied v1 widths (col 2.204, statue 4.008, steps ~5.2) are ~2.2x the runtime
truth; the v1 artifact was overwritten by the v2 draft mid-flight, so the
discrepancy is reconstructed from its printed rows.

## Layout effect at runtime truth (vents unchanged)

  vent 0 (-5.5,-864) prop edge 7.71 (okRuinColumn) — was 6.84
  vent 1 (6.5,-869)  prop edge 2.68 (okRuinColumn) — was 1.81
  vent 2 (-4.5,-899) prop edge 2.42 (mourningStatue) — was 1.35
  vent 3 (3,-897)    prop edge 2.23 (mourningStatue) — was 1.16
All seats clear; margins IMPROVE at truth. The seat amendment itself (B1 seat
2 from (-6.0,-894) to (-4.5,-899)) stays necessary at truth too: the original
seat sat 2.00 m from the statue (-6,-896) center = 1.069 m scaled edge,
still under the 2.0 m floor. Amendment direction confirmed; magnitude in the
verdict text was v1-map-inflated. Corridor P6: no vent's lethal circle overlaps
the spawn-walk band; walker is out at t=4.00 s, earliest blast t>=7.50 s.

Probe v2 re-run ×3 (incl. two post-audit runs): exit 0, byte-identical. Game
code untouched (zero diffs since the parent build; bundle sha12 ba3d56fa0045
unchanged). This note + the probe amend the artifact; the verdict belongs to
Testerbot's re-run.
