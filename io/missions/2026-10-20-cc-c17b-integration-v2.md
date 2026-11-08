# CC-C17 v2 dispatch brief - the RE-RUN, with every blocker the first run surfaced resolved

Claude Code integration child round 1 (200-turn) returned PARTIAL rows 0:
its recon was GOOD (real asset measurements + honest blockers) but it
misread three brief lines and then stopped. This brief resolves every
blocker EXPLICITLY. The probe + repo facts from round 1's recon carry in
verbatim (asset sizes/widths, no-tree-table note, 97.5%->93.3% budget state,
cc_c8_ledger_probe.js usage: node scratch/cc_c8_ledger_probe.js <repoRoot>
LX LZ [R] - the child may run it directly).

## GROUND TRUTH CONFIRMED BY IO (2026-10-20 04:4x)
- Budget: C worst-case now 93.3% of 2M at the ring (1,866,576) WITHOUT the
  CC-C13b/16b rows counted (probe misses churchArchway etc tris: 4 assets
  unlisted: churchArchway/churchCornerButtress/stoneSteps/stoneCrossTilted
  -> count them as ~4k/2k/5k/4k = 15k in YOUR ledger).
- HEADROOM analysis (IO decision, binding): adding the full C17 set
  (~320k tris by C17 plan) would hit 98%+ near the farm/ruins pockets.
  THEREFORE the v2 set is TRIMMED:
  - Farm: cottage + well + fence kit line + lantern gate (NO barn, NO silo,
    NO haybales THIS round: barn 29.5k + silo 14.5k + haybales 7.6k =
    51.6k tris deferred to a later budget pass - they are BAKED and ready
    at art-direction/3d/assets/old_king/, just not wired).
  - Trees: ok-tree-oak x2 sentinels (57.4k) ONLY flanking the den corridor
    + ok-tree-pine x1 at the N road bend (24k). NO scatter-table mixing
    (round-1 recon was right: C's tree table is hand-placed by design).
  - Ruins: reuse the EXISTING church kit + rubble/mossBoulder rows (keep
    them seated as-is or +-3 m) and add ONLY the ok-ruin-arch + 2
    ok-ruin-column rows to the (-101,-207) cluster (the 16 m boulder
    "violation" under the 26 m centre-to-centre rule is a CLUSTER rule
    violation, not a real one: clusters are ALLOWED to be tight; the 26 m
    gate applies to the cluster's OUTER envelope vs other props - use the
    cluster centre, not per-row).
  - Spooky dressing: 2 deadTree + 2 blightcap + 1 skullPile near the den
    corridor + the 3-boulder half-swallowed ring fragment (bearing 200,
    r 238) (mossBoulder x3, scale 2.2-2.8).
  - Fence kit: farm yard = ok-fence-post x6 + ok-fence-gate x1 +
    ok-fence-stonewall x4 + ok-fence-corner-v2 x2 (the bracket IS a proper
    right-angle corner for the yard, IO QA'd the geometry as usable:
    IO's earlier steer 'do not use fence-corner' is SUPERSEDED - the v2
    bracket shape at scale 1.5 works as a stone-fence corner).
  TOTAL ADDED TRIS ~ 175k -> expected worst ~ 97.5% (the C8-trim-era state,
  acceptable; ledger must confirm <= 1,980,000 at BOTH probe centres).

## ROW SHAPE LAW
Region C tree/props rows: same shape as the C4b giants
({ asset, x, z, rotY, scale, cullM: 140 }). Tall assets (oak/pine/silo/barn
when later wired) WANT cullM 140 so they cull past the prop band. Small
props (fence posts, blightcap, skullPile): cullM follows the local scatter
cull band (120).

## THE WORK (v2 ORDER, trimmed set ~ 40 rows)
0. Read CONFIG + recon facts from round 1 (they hold).
1. MANIFEST: add 9 assets to window.WH_CONFIG.assets (assets.js):
   okFarmCottage, okFarmWell, okTreeOak, okTreePine, okFencePost,
   okFenceGate, okFenceStonewall, okFenceCornerV2, okRuinArch,
   paths art-direction/3d/assets/old_king/<name>-pixelated.glb. NOT
   bootCritical. WAIT: assets.js IS an engine file - the law says data
   rows only in CONFIG.js, ASSETS ARE DATA: OK, assets.js edits are
   SANCTIONED for the MANIFEST object only (it is the manifest table -
   CONFIG.camp comments confirm 'a one-line edit per piece (glb = an
   assets.js manifest name)'). NO other assets.js edits.
2. FARM (trimmed): cottage + well + 6 posts + 2 stonewall + gate + 2
   corner-v2 + 1 lanternPost. Site: east of the spine z<0 half, r 150-200
   from the Stone, probe: cluster-centre rule vs props >= 26, roads >= 35,
   fires >= 45, loops >= 60, NOT bearing 225 +-15, zones 48. Cottage rotY
   faces the road (door +Z convention per the C3.1c tent comment).
3. RUIN accent: arch + 2 columns ADDED to the (-101,-207) cluster (cluster
   envelope probe), NO church-kit row removals.
4. TREES: oak sentinels x2 at bearing 210/240 r 232 from the Stone (the
   den approach framing, 12-14 scale) + pine x1 at the N road bend
   (-15, -570) scale 12 (probed 26 m).
5. SPOOKY: 2 deadTree + 2 blightcap + 1 skullPile along the den corridor
   (bearing 225 band, spaced 26 m, r 200-235) + the 3-mossBoulder ring
   fragment (bearing 200 r 238, scale 2.2-2.8, probed).
6. LEDGER: write scratch/cc-c17/ledger2.py (repo-stub pattern, the 4
   missing tri rows counted 4k/2k/5k/4k + your added rows) and run it at
   BOTH centres (0,-366) + (-175,-266) R 170 - PASS = both <= 1,980,000.
7. BUILD: python3 tools/build_v8.py; node --check CONFIG.js; grep markers.
8. REPORT: scratch/cc-c17/REPORT-v2.md (rows, coords, ledger lines, size).

## HARD LAWS (unchanged from round 1)
No git. No harness/browser/server. Probes before paste. Seeds labeled.
Do not move den/tent/cook-fire/Stone. Copy law. node --check each edit.
Write scope: CONFIG.js + assets.js (MANIFEST only) + scratch/ + io/reports/.

FINISH LINE (final message, exactly):
CC-C17 INTEGRATION-V2 DONE rows-added <N> ledger PASS build <bytes>