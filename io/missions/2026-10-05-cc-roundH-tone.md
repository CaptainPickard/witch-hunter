# ROUND H CONTRACT: south spawn + snare recolor + bramble free bushes + cemetery fog (IO -> Claude Code)

You are implementing IO-approved Round H in /workspace/witch-hunter. Nicko is
dialing in tone/setting against an attached dark-fantasy reference: cool
moonlit navy/charcoal palette, pale blue-grey luminous ground fog, warm amber
lantern pockets as the only warmth, gnarled dead vegetation. Follow EXACTLY.
Static probes + Blender renders + esprima only. NO harness, NO browser/game
runs, NO Meshy texture tasks beyond the ONE bramble asset budgeted below.

## 1. Player spawn: south wall, on the path, halfway to the first lantern

Current: CONFIG.regionA.spawn = { x: 0, z: 45 } and game.js boot calls
player.faceTowards(0, 0) (faces map center = north, toward the moon at
azimuth 0). KEEP the faceTowards(0, 0) call and KEEP default camYaw = PI
(looks north into region A). Only the spawn point moves.

New spawn RULE (compute in code from CONFIG, do not hardcode your guessed
numbers in the report; the report states the computed values):
- wallPoint = the south wall ring point ON the dirt path centerline:
  path = CFG.world.dirtPath (regionA, zFrom = south rim start ~86). Take
  wallR = CFG.boundaryWall.ringRadiusM (or the mirror's ring radius value)
  and the path centerline x(z) at z = wallR if wallR >= zFrom, else x at
  zFrom (the ring is at ~87.5, path zFrom ~86: use the path start).
- firstLantern = the nearest regionA lanternPost prop to wallPoint
  (regionA props list; expect the (~5, ~62) or (~-3.4, ~51) post - read the
  real rows, do not guess).
- spawn = midpoint of wallPoint and firstLantern, rounded to 0.5 m.
  Add to CONFIG as regionA.spawn values + a one-line comment
  "Round H: south wall x path, halfway to first lantern".
- Boot safety: verify the new spawn is >= 3 m from every CONFIG prop
  collider center and outside the graveyard keepOut ellipse (it should be,
  z ~ 75 > ellipse z extent 43; assert in a probe, report the check).
  If an enemy spawn sits within 12 m, nudge the spawn along the path toward
  the lantern until clear (report if you had to).
- faceTowards(0,0) unchanged: from the new spawn this faces north = the moon.
  Camera default camYaw = PI already looks north/down-path.

## 2. Snare bush COLOR PASS (vertex paint, zero credits)

Raw = art-direction/3d/assets/biome_library raw refs from Round G; the
pixelated GLB currently uses a flat bark colour (geometry-only source, no
UVs/material - documented FAILED step of Round G).

The mesh (two-tone confirmed suited by QA): canes = long thin sparse strips;
roses = dense volumetric clusters at branch termini. Implement
scratch/snare_color_roundG.py (deterministic; extend the Round G bake script
pattern):
- Classify per-vertex: k-NN local vertex density (k=12 over the decimated
  mesh, normalized) separates rose clusters (high) from canes/thorns (low);
  plus a height-floor darkening for the bottom ~15% (seats the bush).
- Two-tone palette from the reference TONE (desaturated, cool graveyard):
  canes/thorns: dark cold bark ~ #2e2a26 (charcoal brown, 5-bit);
  roses: ash-rose ~ #8d6d6a (dusty desaturated rose-grey, 5-bit);
  base darkening multiplies both toward near-black.
  Exact hex may be tuned +-15% if the render shows better separation; obey
  the pixel register (5-bit posterize per channel) and darkwood canon
  (colours desaturated, one mood).
- Write COLOR_0 attribute + material vertexColors = true on the pixelated
  GLB (reuse the Round G pipeline steps; keep 3000-tri decimation - color
  pass runs on the decimated mesh).
- QA: scratch/treeqa/roundH/ renders front+side+one closeup; vision-check
  yourself: roses must read as distinct pale-ash forms against dark canes.
  Thresholds get up to 2 tuning reruns; if classification misfires twice,
  mark FAILED with the render evidence and keep the better render.

## 3. New bramble bush asset for FREE bushes (Meshy, budget 30 credits)

Free bushes (the 20/region NOT at tree rings) swap from wh-bush-a/b to a
new larger brambled thorny bush themed with the snare bush.

Pipeline (tree-variety toolchain, serial-only submits, read script headers):
1. t2i ref (~3 cr): prompt must stay in-register: "a gnarled bramble
   thicket, dense tangled thorny canes, sparse withered dark rose blossoms,
   old graveyard plant, one single object, matte grey clay render, plain
   black background". NO trigger words (no 'thin curling fronds', no 'dew',
   no multi-object phrasing). Matte the ref like prior rounds.
2. i23d meshy-5 (15 cr): target_polycount 2000 (script MAX_TARGET guard),
   serial after the t2i returns.
3. QA: tree_gate.py + tree_ortho.py into scratch/treeqa/roundH/. If it
   fails the gate (shard storm / largest piece < 60%), ONE re-roll from a
   new ref is allowed (stays within the 30-cr budget incl refs); a second
   failure = FAILED step, report, keep the better render, do not ship a
   broken mesh (free bushes would keep wh-bush-a/b that round).
4. Decimate to <= 2500 tris (reuse scratch/decimate_roundG.py pattern,
   deterministic, log before/after), pixel-bake per register (same path as
   the E bushes).
5. Land as art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb
   (+ refs/ + raw/ per layout). assets.js MANIFEST entry 'bramble'. KEEP
   wh-bush-a/b pixelated GLBs (rollback = CONFIG key).
6. CONFIG.scatter.bushes.free assets -> [['bramble', 1, 1.4, 2.0]] (larger
   than the old bulbs ~0.7-1.3). Rings (atTreeRing) stay whBushSnare ONLY.
   Re-run scatter mirror: placements MAY shift (footprint change) - report
   per-region new counts; keepOut/clearances/no-collider law unchanged;
   two runs byte-identical.

## 4. Cemetery fog ramp (approach the graveyard -> denser, cooler fog)

Region A fog is a global FogExp2 (game.js applyRegionLighting sets color
0x9aa0a3, density 0.012). Add a position-driven ramp (game.js, cheap, in the
existing per-frame path like poolTick):
- CONFIG.regionA.cemeteryFog = { zone: reuse the graveyard keepOut ellipse
  (regionId hold_outskirts, x 0, z 10, rx 36, rz 33), density: 0.030,
  color: 0x7f8ea6, rampStart: 1.35, rampEnd: 0.55 }.
  rampStart/rampEnd = normalized ellipse distance (>1 outside shrink,
  <1 inside): weight w = smoothstep from 0 at d=rampStart to 1 at d=rampEnd.
- Per frame: scene.fog.density = lerp(regionFogDensity, cemeteryFog.density,w)
  and scene.fog.color = lerpColor(regionFogColor, cemeteryFog.color, w).
  Region switches re-apply the REGION base (applyRegionLighting unchanged);
  the ramp only runs in region A. NO new lights, NO new meshes, NO mist
  plane changes this round.
- Values are first-pass targets against the reference (pale blue-grey
  luminous fog); Nicko tunes after playtest. Report the ramp math in one
  sentence and keep it O(1) per frame.

## 5. Commits (identity CaptainPickard <pickard.nicko@gmail.com>)

Per branch (dev checkout /workspace/witch-hunter stays on dev; worktree
/tmp/wh-worldfeat on feat/world-visuals), identical messages:
- feat(assets): wh-bramble generated + snare vertex-color pass (Round H)
- feat(world): south spawn, cemetery fog ramp, bramble free bushes (Round H)
- build: v7 bundle (worktree only)
Also commit scratch/treeqa/roundH/, scratch/roundH-proof/, the two new
scratch scripts, updated provenance (io/roundH-provenance.md), mirror JSONs.
Do NOT push. Do NOT touch main, light.js, player.js, enemy.js, moveset.js,
region-defs.js, any rigged/combat GLB, never read/commit
scratch/.mixamo-credentials.txt or scratch/.mixamo-storage.json.
Meshy budget: 30 credits (balance before you start: 1255); serial-only
submits; if a submit 402/400s twice, mark that step FAILED and continue.

## 6. Proof stills (exactly 3, scratch/roundH-proof/, Round F renderer
pattern - grounded, shadows off, 1024px)

1. 01-spawn-view.png: the new spawn ground view facing north: path ribbon
   ahead, first lantern visible mid-distance, moon-side sky cool, fog base.
2. 02-cemetery-fog-approach.png: camera on the path at the graveyard fence
   mouth showing the denser cooler fog pool over the cemetery zone.
3. 03-bramble-snare-closeup.png: free-standing brambles (new asset) + a
   snare-bush ring at a young tree base nearby: two-tone roses vs dark
   canes must read.
Vision-check each yourself; re-render on mistakes (free); if a still is
wrong for a reason you cannot fix in 2 tries, report it with evidence.

## 7. Report format

Commits table (both branches), Meshy ledger (id, credits, before/after
balance), snare color-pass classification stats (% verts roses/canes),
new scatter counts per region, wall mirror + scatter mirror determinism
(both must be byte-identical), the computed spawn coordinate and its safety
checks, deviations, watch items for Nicko's playtest, FAILED steps (or
none). Keep the whole report under 150 lines.