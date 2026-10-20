# CC-C17 · MAJOR GOAL: The Old King's Forest feels SPOOKY - full asset + dressing + danger integration

## MISSION (Nicko, 2026-10-20, standing major goal)
"dispatch claude code running on max long horizon task: add ALL the new
astrabot assets to the game. Make the forest feel like a spooky place full of
danger and mystery. Reorder the locations of enemies if needed. Set this as a
major goal; dispatch as many subagents as necessary."

You are the INTEGRATION LANE. Deliver the full pass. Work in the worktree
/tmp/wh-worldfeat (branch feat/world-visuals). LEAVE ALL EDITS UNTRACKED
(IO is the sole committer). NO harness/browser/dev-server runs — IO + Nicko
validate on the live surfaces.

## WHERE THINGS ARE
- 16 pixelated asset bakes READY: art-direction/3d/assets/old_king/*-pixelated.glb
  (farm set: cottage/barn/silo/haybale/well; ruins: arch/column/rubble/
  wall-straight/wall-corner; trees: oak/pine; fence kit: post/gate/stonewall).
  (ok-fence-corner-pixelated.glb is a REJECTED bracket-shaped mesh — skip it;
  a regenerated v2 bake is incoming async: if
  /tmp/wh-worldfeat/scratch/treegen/old_king/raw/ok-fence-corner-v2-meshy.glb
  EXISTS when you reach the fence task, pixelate it yourself per
  scratch/cc-c17/intake_pixelate.py's posterize512 + use it; else wire the
  fence run with post/gate/stonewall only.)
- Concept refs (the look): art-direction/concepts/old_king/*-ref.png.
- Art law: pixelated everything (512 NEAREST + 5-bit), darkwood palette, one
  accent per frame (amber human fire / cyan magic / red pact).
- Copy law: never the word "free"; no agent names in player copy.
- THE MAP (world coords, region C = Forest of the Old King): spawn glade
  (0,-96) + lanternPost (3,-99); King's Road spine x~0..4 z -88..-332;
  stoneRing r34 around the Stone (0,-366) + gate pair + Old King's Stone
  assembly; branch roads E/W/N to notch mouths (240,-366)/(-240,-366)/(0,-596);
  den cave mouth (-163.4,-202.6) facing the map centre (do NOT move it);
  bandit camps Alpha (-60,-186 Bravo? check CONFIG) — read the CURRENT
  CONFIG for exact rows. Current densify: fires D1-D4 + wolf packs east/west/
  north/sw/se/ss/nw2 in CONFIG.enemy.wolfPacks.

## THE WORK (ORDER OF WORK — do not skip ahead)
0. READ prototype/js/CONFIG.js fully around regionC + CONFIG.assets
   (manifest), CONFIG.enemy (wolfPacks), CONFIG.cooking.stations +
   regionC.props + roads. Understand the row shape BEFORE editing.
1. MANIFEST + boot: add the 15 usable old_king assets to
   CONFIG.assets (assets.js MANIFEST object window.WH_CONFIG.assets) with
   art-direction/3d/assets/old_king/<id>-pixelated glb paths; add each to
   bootCritical ONLY if a boot build reads it (the farm/ruin/fence rows are
   region C streaming props: DO NOT add to bootCritical — the streaming late
   swap handles them; wolves/player bodies stay as-is).
2. FARM (the quest-giver site): place the farm as a distinct homestead just
   off the King's Road spine between the glade and the Stone (pick the site
   with the gen_squad4-style probe pattern you write: clearance to all
   existing props >= 26 m, roads >= 35 m, fires >= 45 m, loops >= 60 m,
   r 120..244 from the Stone, NOT inside the den approach bearing 225 +- 15
   band nor the spawn/Stone 48 m zones). Layout: cottage (front door facing
   the road), barn 8 m behind, silo beside the barn, well 6 m in front,
   haybales x2 flanking the barn (the v2 fence-corner when ready + fence
   posts enclose a small yard). Colliders = the default asset footprint
   (region-manager propColliders) - no custom collider code.
3. RUINS: replace BOTH CC-C13b church-kit stand-in cluster rows (the 9 rows
   tagged CC-C13b stone-ruin clusters) with the ok-ruin-* pieces (2 clusters:
   -101,-207 area near the old den approach + -31,-139 west of the glade),
   PLUS 2 new small ruin clusters on roads' far sides (N-1 near (30,-410),
   W-1 near (-115,-300)) - probed the same way. Keep the C13b rubble/moss
   boulder rows that still make sense (you may re-seat them +-3 m).
4. TREES: add ok-tree-oak + ok-tree-pine as scatter assets in regionC's
   scatterOverrides flora table (weight ~0.5 of yewTree, height bands 9-15 m
   oak / 8-13 m pine) so the population mixes them in; ALSO hand-place
   3 sentinel oaks flanking the den approach ( spooky framing: dead-looking,
   scale 14-16) + 4 pines on the N road bend, probed.
5. FENCE KIT: the starting world-camp's picketFence rows (regionB) STAY (a
   farm aesthetic is fine there); in region C: replace the C13b-normalized
   random picket/iron rows IF the read feels off... (they are the A/B yards,
   leave them; ONLY region C gets the new kit): build a small fence line at
   the farm yard (posts, gate, stonewall corner) + a broken stonewall run
   along the east road's first bend (48-52 m from the boulder rows), probed.
6. SPOOKY DRESSING (the mystery): on top of geometry, LIGHT + sound-of-space
   reads. Concretely (all CONFIG data rows, NO engine changes):
   - 2 deadTree + 2 blightcap + 2 b6Bones-style bone dressing rows near the
     den corridor (existing assets only, probed 26 m) - the approach feels
     haunted.
   - 1 mossBoulder ring fragment (3 boulders) half-swallowed by the ridge at
     bearing 200 r 238 (visual storytelling: the mountain eats old ruins).
   - Dusk/night lantern contrast: the region C lantern rows already exist;
     ADD 1 lanternPost at the farm gate (amber beacon = safety) so the farm
     reads SAFE at night vs the dark woods (the C6C fires already glow).
7. ENEMY REORDER (the danger): audit the CURRENT 22 bandit + 28 wolf rows
   + densify sites; then REBALANCE for pacing:
   - the glade-to-Stone spine stays MEDIUM (players learn here);
   - the den approach bearing 225 band: LIGHT at its mouth (a hunter needs
     one breathing beat before the cave), DARK dense at the SW quadrant edge;
   - 2 camp guards per NEW camp (D1-D4) stay as-is; REPOSITION the OLD
     Alpha/Bravo guards if a camp sits too close to your new farm/ruin
     placements (enemies >= 30 m from every building).
   - wolf loop adjustments ONLY IF a loop now grazes a building pad (probe).
   Every move: same probe gates, and CONFIG row comments updated.
8. LEDGER: with every prop added, write scratch/cc-c17/ledger.py mirroring
   scratch/cc13b_probe.cjs rules (props >= 26 m to props, roads >= 35,
   fires >= 45, loops >= 60, zone checks) + the C worst-case 2M tri circle
   budget copied from the C8 trim probe pattern. RUN IT after every step
   (2,3,4,5,6,7). ALL CLEAR = proceed; any violation = fix before more.
9. BUILD: python3 tools/build_v8.py; node --check every touched js; grep
   the bundle for your markers.
10. REPORT: scratch/cc-c17/REPORT.md - what moved, verdicts, ledger output,
   build size. Untracked.

## HARD LAWS (repeat)
- NO commits, NO pushes (IO).
- NO harness / no playwright / no chromium / no dev server (the live serve
  is IO's job; Nicko playtests).
- EVERY placement is probed BEFORE paste (the probe script first, paste next).
- Deterministic seeds on every generator (label them).
- Do NOT move the den (CC-C16a orientation is final), the starting tent,
  the tutorial cook fire (darkwood_edge), or the Old King's Stone assembly.
- No new engine .js files: data rows in CONFIG.js only (+ optional scratch
  tools). region-manager/enemy/camp/cooking readers already carry every
  feature this brief needs.
- Pixelate law for the v2 fence bake once it lands (posterize512 pattern).
- The map centre is (0,-366); bearing 225 = the den direction.

## FINISH
The last line of your final summary MUST be:
CC-C17 INTEGRATION <DONE|PARTIAL> rows-added <N> ledger <PASS|FAIL> build <bytes>

## MID-RUN STATE UPDATE (IO, 2026-10-20 04:39 UTC) - FENCE-CORNER RULING
The fence-corner saga is resolved: v1 (55k tris bracket) REJECTED, v2 (bracket
again) REJECTED, v3 (18860 tris from a GOOD ortho concept ref) GEOMETRY-RIGHT
but its decimated bake ok-fence-corner-v3-pixelated.glb (2500 tris) reads
abstract/glitchy in QA renders. RULING: do NOT wire ANY ok-fence-corner* into
the farm yard or fence run. Build the farm yard with ok-fence-post rows +
ok-fence-gate + ok-fence-stonewall ONLY (all QA PASS), leaving a natural gap
where a corner would sit (a stonewall end-turn works visually). IGNORE
ok-fence-corner* (v1/v2/v3) everywhere in farm + fence tasks with NO manifest
entry for any corner variant. Everything else in the brief unchanged; note
this ruling in REPORT.md. Manifest stays 15 assets: farm 5 + ruins 5 +
trees 2 + fence post/gate/stonewall 3.
