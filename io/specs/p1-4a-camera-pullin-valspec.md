# P1-4a — Camera Pull-In VALIDATION SPEC (Testerbot)

Authority: io/specs/p1-4a-camera-pullin-spec.md (IO spec, wake 39, 2026-11-08).
Status at authoring: PRE-BUILD (Devbot has not implemented yet — these checks are
executed against the Devbot diff on feat/world-visuals after build).
Gate: Testerbot audits code/JSON/diff-read only — NO playtest harness, NO browser
automation of gameplay (no-harness gate), Nicko is the playtest.

## Rules for the validator

- NO git commands of any kind (children NEVER push or commit; IO is the sole
  git gatekeeper). "Byte-identical" checks below are executed as TEXT
  comparisons: read_file the post-change file at the quoted landmark and
  compare the lines to the anchor text quoted here, or grep for the exact
  quoted line. Never match by line number after Devbot's edit — Devbot's
  insertions shift every line below its edit; all anchors here are TEXT.
- All code reads are against /tmp/wh-worldfeat (branch feat/world-visuals).
- Convention checks follow IO spec "Boundaries": IIFE + window globals, var
  style, NO ES modules / import / const / let / arrow functions in js/.
- A FAIL must quote the offending line(s). A SKIP needs the gate's consent
  (state the reason in the verdict).

## Baseline (pre-change tree, verified this authoring wake)

player.js `Player.prototype.updateCamera` starts at line 2227; within it:
lock-on yaw aim 2229-2240 (LOCK = window.WH_CONFIG.lockOn, var LOCK at line 16);
`var target = this.pos.clone();` 2243; `target.y += CFG.camHeight;` 2244;
pitch cap comment 2245-2248; `var pitchCap = Math.max(CFG.camMinDistance,
CFG.camMaxDistance * (1 - CFG.camPitchDistShrink * Math.max(0,
Math.sin(this.camPitch))));` 2249-2250;
`var effDist = Math.max(CFG.camMinDistance, Math.min(pitchCap, this.camDist));`
2251; `var floorY = CFG.camGroundClearance;` 2252; `var offset = new
THREE.Vector3(Math.sin(this.camYaw) * Math.cos(this.camPitch),
Math.sin(this.camPitch), Math.cos(this.camYaw) *
Math.cos(this.camPitch)).multiplyScalar(effDist);` 2253-2257;
`var want = target.clone().add(offset);` 2258;
`if (want.y < floorY) want.y = floorY;` 2259; decoupling comment 2261-2265;
`var lerp2 = 1 - Math.exp(-CFG.camFollowLerp * dt);` 2266;
`this.camera.position.lerp(want, lerp2);` 2267;
`if (this.camera.position.y < floorY) this.camera.position.y = floorY;` 2268;
`this.camera.lookAt(target);` 2269.
Grep baseline (0 hits today, so any hit after build = new code):
'cameraPull|lastCameraPull' over prototype/ = 0 matches.
`var want` in player.js = exactly 1 match (line 2258).

region-manager.js: `collisionRadius`/`colliderRadius` at 444-450 with the
`/tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i` regex and TRUNK_RATIO
0.25; TRUNK_ASSETS 440-443; `whMeetsCorridor` 425-431 (+ CFG.world.
colliderCorridorHalfDepth at 427); `whPropColliders(regionId, meta, plan,
wall)` 458-503: props loop 461-483 (`p.noCollide` continue 468; p.wall rows
push r=CFG.boundaryWall.collider.r circles at 475; normal row build 479-480;
exempt/circles routing 481-482), scatter-tree rows 486-490, wall-plan rows on
the region's side (WALL_SIDE_PAD_M 3) 494-501; `plan.colliders.push` in
whWallPlan at 1355-1356 (via addSegment), 1476-1477, 1482-1483, 1566-1568,
1592-1593;
m()-gating: the EXCLUSION loop (1311-1318) skips prop rows on missing meta
via m() (plan.complete -> false); the arch section is gated by
`if (gm && gm.width > 0)` 1445, the lantern by `if (lm && lm.height > 0)`
1493, door arches by `if (!dm || !(dm.width > 0)) return;` 1511, forecourt
posts by `if (!pm2) return;` 1584, and the forecourt fence sections (1559) /
posts (1587) take whMeetsCorridor skips — arch legs and plugs have NO
corridor exemption (comment 1442: "NOT whMeetsCorridor-exempt: they are the
doorway"); RegionManager.prototype.propColliders cache 1676-1684
(stores only `table.complete`); pushOutCircles body 526-545; collider
consumers: region-manager 1805-1810 (player) + 1835-1845 (enemy), game.js calls
pushOutCircles(clampPlayerToBounds ~1371-1381); wall-plan asset exclusion loop
1311-1318 (NOT to change); whWallPlan header comments 1286-1292.

CONFIG.js: player cam keys 2939-2947 (camDistance 7.0, camMinDistance 3.0,
camMaxDistance 14.0, camPitchMinDeg/MaxDeg, camHeight 2.6, camGroundClearance
0.4, camPitchDistShrink 0.35, camFollowLerp 12.0); boundaryWall 2828-2890
(heightM 7.2 at 2835; collider { r 0.45, perSegment 3 } 2843; arch legs
{ r 0.6, spacingM 1.0 } + plugR 0.5 at 2860-2861); regionC row 556-560+
(center -366 z, groundRadius 280); regionC/terrain row ~824-887 (camMinAboveGround
0.8 at 886, propFootR 1.2 at 887); player block ends ~2955
(player.respawnDelay 2951).

wh-ground.js / assets.js / game.js: WH_GROUND public API = { has, build,
heightAt, footY, mesh, slopeTan, notchNear, holdAtNotch, debugRaycast,
gridHash } (region-manager 372-377); footY(regionId, x, z, r) = min ground
under the footprint (center + 4 compass points at r; r falsy = center only)
(305-309); getMeta returns { height, width, groundMinY } (assets.js 909-920);
game.js groundHas() 1258-1260; cameraGroundFloor() 1305-1309 (uses groundYAt +
terrain.camMinAboveGround); applyCameraShake 1368; computeFireSockets 3064+
with the groundHas()-guarded footY seat at 3089-3091 (THE GUARD PATTERN the io
spec points to).

index.html script inventory (46 entries): wh-ground.js loads AFTER CONFIG.js;
player.js 63; region-manager.js 65; game.js last (85). NO new script file may
be added (spec design 7).

---

## Checks

Map: V1-V2 run syntax + typo sweeps. V3-V4 verify A4 (CONFIG keys). V5-V9 +
V9b verify A3 (region-manager h/fy) and A1's count preservation. V10-V16
verify A2 (player.js diff confinement + exact preservation) and A6 (zero
per-frame allocation). V17 verifies A5 (exempt inheritance). V18-V23 verify
A1 (orbit math) and A8 (pull result geometry). V24-V26 verify A7 (band edge
cases). V27 re-verifies A4's false path. V28-V29 are negative checks
(consumer regions + boundaries).

### V1 — Syntax, all three touched files
AC A1. METHOD: `node --check prototype/js/CONFIG.js` ; `node --check
prototype/js/player.js` ; `node --check prototype/js/region-manager.js`.
PASS: exit 0 on all three, no parse error. (Covers A1's node --check bar
literally.)

### V2 — Typo sweep (node --check cannot catch bad field names)
METHOD: grep -n 'cameraPull|lastCameraPull|trunkTopFrac|camRadius|skinM|
minFloor' prototype/js/CONFIG.js prototype/js/player.js
prototype/js/region-manager.js; code-read each hit.
PASS: every CFG.player.cameraPull key and field name in the pull block spells
the SAME way as defined at CONFIG.js 2939-2947 (cameraPull.camRadiusM,
cameraPull.skinM, cameraPull.samples, cameraPull.trunkTopFrac,
cameraPull.minFloor); zero hits read as a different spelling
(e.g. camRadiusM vs camRadiusMeters, lastCamPull vs lastCameraPull). FAIL on
ANY mismatched spelling.

### V3 — CFG.player.cameraPull block exact (A4)
METHOD: code-read CONFIG.js beside the existing cam* keys (landmark
CONFIG.js 2939-2947). Diff-read the block against the spec line 71-73.
PASS: the block exists, is added INSIDE the CFG.player object, and reads
`cameraPull: { enabled: true, camRadiusM: 0.45, skinM: 0.30, samples: 6,
trunkTopFrac: 0.45, minFloor: 0.0 }` with no extra config fields. Sane-range
gates (values, not spelling): 0.30 <= camRadiusM <= 0.60; 0.30 <= skinM <=
0.50; 4 <= samples <= 10 (integer); 0.30 <= trunkTopFrac <= 0.60; minFloor
0.0-0.5 (a small non-negative floor is allowed); enabled is boolean true.

### V4 — No collateral edit to existing CONFIG rows (A4)
METHOD: code-read CONFIG.js around the player camera keys 2939-2947 and spot-
diff the lines against the anchors quoted in the baseline section above.
PASS: every pre-existing line inside the CFG.player camera block
(camDistance..camFollowLerp, mouseSensDegPerPx, respawnDelay) is byte-identical
to the baseline text; cameraPull was INSERTED, nothing removed or reworded.
FAIL on any altered pre-existing key or repositioned cam* default.

### V5 — h/fy attached at circle-construction time (A3)
METHOD: code-read region-manager.js whPropColliders (landmark 458-503) and the
whWallPlan circle-push sites — wall-segment rows via addSegment
(1354-1357), arch legs (1476-1478), arch plugs (1482-1484), forecourt fence
rows (1566-1568), forecourt lantern-post rows (1592-1594). grep -n 'fy'
prototype/js/region-manager.js.
PASS: every circle row now carries BOTH h and fy (the row literals read in the
shape `{ index: ..., name: ..., x: ..., z: ..., r: ..., h: ..., fy: ... }`),
EVERY listed push site emits both fields, and no circle-construction site was
moved, re-ordered, or re-purposed: each
push call still fires from the same loop body as the baseline text, with the
same routing (rows routed through out.exempt/out.circles/plan.colliders
exactly as before).

### V6 — wall-plan + p.wall rows: h = CFG.boundaryWall.heightM (A3)
METHOD: code-read (i) the p.wall branch inside whPropColliders' props loop
(p.wall circles push r = CFG.boundaryWall.collider.r circles at 475) and (ii)
the wall-plan-class rows in whWallPlan (wall segments 1354-1357, arch legs
1476-1478, plugs 1482-1484, forecourt fences 1566-1568, posts 1592-1594).
PASS: every solid-CLASS row in these sites (all wall-plan rows are solid
per design 1 — segments, fence sections, lantern posts) carries h reading
CFG.boundaryWall.heightM (7.2, CONFIG.js 2835) — NOT a re-derived width-per-seg
or perSegment-derived value; arch legs (r 0.6, CONFIG 2860) and plugs (plugR
0.5, CONFIG 2861) read the same heightM. p.wall rows (CONFIG boundary segment
props in A/B cfg.props) ride the same h. FAIL if any wall-class row's h is
missing, or derived from a different CFG field.

### V7 — Scatter-tree rows get h/fy (A3)
METHOD: code-read the scatter-tree push inside whPropColliders (landmark
486-490) and grep -n 'scatter' prototype/js/region-manager.js.
PASS: each scatter-tree circle row carries h and fy computed from the same
row's own x/z/scale (h from the tree's nativeWidth/height * scale per design 1;
fy from the design-2 footY guard), in the SAME push call (the existing
plan.colliders.push call is EXTENDED, not duplicated).

### V8 — whPropColliders props loop unchanged + m() default behavior (A3)
METHOD: code-read the props loop 459-483 line by line against the baseline
text above. grep -n 'whMeetsCorridor' prototype/js/region-manager.js.
PASS: (a) the p.noCollide continue (468) is untouched; (b) the p.wall branch
(469-478) is untouched EXCEPT where design 1/2 legitimately add h/fy; (c) the
circle row's r value and its assignment (479-480) are byte-identical; (d) the
exempt/circles routing (481-482: `if (whMeetsCorridor(...)) -> exempt; else if
(row.r > 0) -> circles`) is byte-identical; (e) whMeetsCorridor itself (the
CFG.chokepoint.width / 2 + CFG.world.colliderCorridorHalfDepth window) is
byte-identical; (f) the m()-guard semantics are unchanged: props rows ALWAYS
push a circle row (r 0 when meta is missing), only whWallPlan's EXCLUSION loop
(1311-1318) keeps `if (m && m.width > 0)`. FAIL if the props row r, noCollide,
exempt routing, or m-guard default is altered in a way that changes a circle's
presence, radius, or corridor exemption.

### V9 — No logic change to radius/exempt/consumer regions (A3 + negative)
METHOD: code-read the circle consumers downstream of the h/fy additions:
RegionManager.prototype.propColliders (1676-1684), RegionManagerLogic.
pushOutCircles (526-545), the player circle consumer (1805-1810 calls
this.propColliders(this.logic.activeId).circles), the enemy consumer
(1835-1845 iterates propColliders(rid).circles), and grep -n
'propColliders(' prototype/js/region-manager.js prototype/js/game.js.
PASS: propColliders cache semantics unchanged (rows stored only when
table.complete; the cached shape still { circles, exempt, complete }); every
existing consumer (player + enemy push-out) sees the SAME rows (same indices,
same r, same exempt vs circles routing) after the change; no consumer code
changed AT ALL; no consumer newly reads h/fy/r differently. FAIL on any
changed consumer.

### V9b — Circle COUNTS preserved at every construction site (A1)
METHOD: code-read each push site post-change and compare its row-producing
count to the pre-change semantics quoted in the baseline; grep -n
'plan.stats' prototype/js/region-manager.js for the self-reported counts.
PASS (no count may drift — h/fy are ATTACHED fields, not new rows):
(f) whWallPlan rows: ring/chord segment rows == plan.stats.ring + chordE +
chordW as reported (drops/doorGap exclusions unchanged); arch leg rows ==
plan.stats.archLegs, plug rows == plan.stats.archPlugs; forecourt fence rows
== plan.stats.fenceE + fenceW (corners ride the last seat, region-manager
1563-1571), lantern-post rows == plan.stats.posts; corridor-skipped fence/post
placements (whMeetsCorridor at 1559/1587) still emit NOTHING (not rows, not
h/fy-carrying stubs); (g) whPropColliders: CONFIG-prop rows (incl. p.wall
rows), scatter-tree rows ('scatter<i>'), and wall-plan rows joined by the
WALL_SIDE_PAD filter (494-501) keep their exact counts and indices — adding
h/fy must not change routing, rounding, or the corridor exemption test;
(h) CONFIG.js untouched OUTSIDE the cameraPull block — V4's spot-diff covers
this (an added/removed cfg.props / cfg.enemies / scatterOverrides row would
surface there; h/fy attach lives in region-manager.js only);
(i) exempt-row counts unchanged (props corridor-exempt rows 481 push the SAME
row into out.exempt, now with h/fy attached — exempt rows MUST also carry
h/fy per A5's inheritance, verified again in V17);
(j) wall-plan stats.colliders (1604) still equals plan.colliders.length and
the per-kind stats still reconcile with the row totals per (f).

### V10 — Module-scope scratch vars (A2)
METHOD: code-read player.js' IIFE variable head (baseline landmarks: `var CFG
= window.WH_CONFIG.player;`, `var LOCK = window.WH_CONFIG.lockOn;` line 16,
`var MCFG = ...` line 13, `var ANIM/WL/AW` 17-18). grep -n 'var camera' or the
scratch names in player.js.
PASS: the new scratch variables (whatever names Devbot chose) are declared at
MODULE scope near the existing var block, are var-style (not let/const), and
are consumed ONLY by the pull-in block (no new window pollution, no
module-scope reassignment of an existing var name — a Devbot scratch name that
shadows or reuses an existing module-scope name FAILS).

### V11 — Pull-in insertion confined to the want..floorY window (A2)
METHOD: (a) code-read player.js updateCamera after the change; (b) grep -n
'applyCameraShake|cameraGroundFloor' prototype/js/game.js; (c) grep -n
'lastCameraPull' prototype/js/player.js; (d) compare index.html's script
inventory against the 46-entry baseline above.
PASS: (a) the pull-in block sits EXACTLY between `var want =
target.clone().add(offset);` (2258) and the first floor clamp `if (want.y <
floorY) want.y = floorY;` (2259) — no other line of updateCamera was moved; (b)
game.js cameraGroundFloor() (1305-1309) and applyCameraShake (1368) are
byte-identical to the baseline text; (c) lastCameraPull exists ONLY in
player.js (no cross-file leakage); (d) index.html gained NO new <script> tag
and its entries are byte-identical to the baseline (design 7: no new script
file). FAIL on any edit outside the player.js want..floorY window, any
game.js/CONFIG-region-manager line drift beyond the spec'd h/fy sites, or any
new file/script.

### V12 — Post-insertion lines byte-identity (A2 + A8 lookAt)
METHOD: read the lines from `var lerp2 = 1 - Math.exp(-CFG.camFollowLerp * dt);`
(2266) to `this.camera.lookAt(target);` (2269) and diff-read them against the
baseline anchor text above.
PASS: (a) the `var lerp2` line and both floor-clamp lines (2268 and 2259) are
byte-identical; (b) `this.camera.position.lerp(want, lerp2);` and
`this.camera.lookAt(target);` are byte-identical; (c) nothing between 2261
(the decoupling comment block) and 2269 changed except the inserted pull-in
block (i.e. the comment block 2261-2265 reads exactly as the baseline
above).

### V13 — Pull block reads only approved vars (A2)
METHOD: grep -n 'cameraPull|lastCameraPull' prototype/js/player.js; code-read
the inserted block (the only lines between 2258's want build and 2259's floor
clamp) and classify every identifier that appears.
PASS: the pull block references NONE of: `lockTarget`, `LOCK`, `camYaw`
mutation, `camPitch` mutation, `camDist` (wheel state) assignment, `MCFG`,
mouse/joystick handlers, touch-controls hooks, `this.root`, `this.body`, or
any THREE constructor other than (optionally) reused scratch Vector3s built at
module scope. The ALLOWED set: `CFG.player.cameraPull`, the already-local
vars `target`, `effDist`, `pitchCap`, `dt`, `this.pos`, `this.state`,
module-scope scratch vars, the region-manager accessor `window.WH_GAME &&
window.WH_GAME.regionManager` (or an equivalent existing access path the
build wires at module scope), `CFG.player.camMinDistance`. Anything else needs
an explicit verdict note naming and justifying it.

### V14 — lastCameraPull shape + per-frame update while enabled (A2 + design 6)
METHOD: code-read the lastCameraPull assignment in player.js; grep -n
'lastCameraPull' prototype/js/player.js.
PASS: (a) the player instance records `lastCameraPull = { blocked, wantDist,
effDist, t, circles }` with wantDist = the PULLED distance (the post-pull
want-offset length) and effDist = the UN-capped want distance (the pre-change
want-offset length, the same quantity the effDist variable already holds);
(b) the assignment executes inside Player.prototype.updateCamera (on the
Player instance) whenever the pull path runs with CFG.player.cameraPull.
enabled true — every frame while enabled, gated by NOTHING except enabled (not by blocked, not by lock
state, not by proximity); (c) the object is MUTATED, not reallocated per frame
(the same lastCameraPull reference persists frame-to-frame; rebinding
`this.lastCameraPull = new ...` or `{}` inside the per-frame path FAILS via
V15's regex as well).

### V15 — Zero per-frame allocation in the pull block (A6, regex)
METHOD: (a) grep -n 'new '|']|{' against the inserted pull block body in
player.js — extract the block between `var want = target.clone().add(offset);`
and `if (want.y < floorY) want.y = floorY;` and inspect it as text; (b)
code-read; (c) grep -n 'new THREE' prototype/js/player.js and compare count to
the pre-change baseline count 36 (verified this authoring wake);
PASS: (a) the pull-in block body contains NO `new `, NO `[` array literal, NO
`{` object literal, NO `.clone()`, NO `.copy(` allocation-returning call, NO
Array.prototype.slice/map/concat — any allocation inside the per-frame path
FAILS (module-scope scratch reuse is the required pattern); (b) `new THREE`
count in player.js post-change == the pre-change baseline count 36 (36 hits of
/new THREE/ in the pre-change tree, verified this authoring wake — an added
`new THREE.Vector3` in the pull path FAILS, an incidental removal elsewhere
also FAILS); likewise /\.clone\(|\.copy\(/ count == baseline 12 (no new
clone/copy in the block); scratch vars are the allowed pattern and are
initialized ONCE at module scope; (c) lastCameraPull is written by
mutating its fields in place (see V14c).

### V16 — Pull block sits BEFORE the wants' clamp (A2 + design 4)
METHOD: code-read player.js updateCamera after the change.
PASS: the pull-in block is the last thing between the want build (2258) and
the `if (want.y < floorY) want.y = floorY;` clause (2259) — i.e. the floor
clamp still applies AFTER the pull-in (the pulled want is still clamped to
the floor). FAIL if the pull block runs after the clamp or replaces it.

### V17 — Exempt inheritance (A5)
METHOD: code-read the pull block and its circle iteration target.
grep -n 'exempt|\.circles' prototype/js/player.js prototype/js/region-manager.js
with the post-change file.
PASS: the pull block iterates ONLY the active region's
`regionManagerLogic.propColliders(activeId).circles` (or the
RegionManager.prototype.propColliders wrapper's `.circles`); the word
`exempt` NEVER appears inside the pull block, and no second iteration source
(exempt array, scatter plan separately, wall plan separately) is read by the
per-frame path. Corridor-camera behavior therefore stays preserved (gate
corridor stays camera-clean). FAIL if exempt is consulted or if the iteration
source is anything other than .circles.

### V18 — Sample t formula (A1, code-read)
METHOD: code-read the sample loop in the pull block.
PASS: N = CFG.player.cameraPull.samples; the loop's sampled t values read
`((i + 0.5) / N)` for i = 0..N-1 (i.e. t in [(0.5)/N .. (N-0.5)/N]), no
endpoints (t=0 and t=1 are NEVER sampled). FAIL on <=, >=, or (i)/N or (i+1)/N
variants.

### V19 — Blocked test: 2D dist + y band (A1, code-read)
METHOD: code-read the per-sample test in the pull block.
PASS: for each circle row and each sample the test is BOTH (i) `2D dist
sample->circle center <= r + R + skin` using ONLY x/z (dz and dx on the
center), and (ii) `y_s within [fy - 0.25, fy + h]` where y_s is sample y
(target.y + offset.y * t) and the band bounds come from the row's fy/h. FAIL
if either test is dropped, if the y test has no [fy - 0.25, fy + h] band
shape, or if the radial test uses a y-distance (must stay 2D per spec line
55-56).

### V20 — Broadphase formula (A1, code-read)
METHOD: code-read the broadphase skip in the pull block.
PASS: skip reads `sqrt((c.x - midX)^2 + (c.z - midZ)^2) > (segLen/2 + c.r + R +
skin)` — a SINGLE sqrt against the segment midpoint (midX/midZ = the midpoint
of target->want) with the sum segLen/2 + circle r + camRadiusM + skinM. FAIL
on per-sample broadphase (a sqrt per circle per sample instead of once per
circle), on a missing +c.r/R/skin term, or on a midpoint built from anything
other than the current frame's segment (midpoint must be recomputed from this
frame's target/want, not cached across frames).

### V21 — Pull math + bounded verification (A8)
METHOD: code-read the retreat and verification sub-block.
PASS: (a) the retreat is `tClear = max(0, (i_first - 1) / N)` from the FIRST
blocked sample's index, i.e. exactly one sample spacing (1/N of the want
segment) back from the first blocked point, floored at 0; (b) the verification
loop is bounded at AT MOST 2 shrink steps (A8: terminates <= 2 shrinks); (c)
each still-violated step decrements tClear by 0.15 with the floor tClear >= 0;
(d) the loop applies the step factor 0.85 as written in spec lines 60-61 —
NOTE (IO ruling candidate, do NOT fail on it alone): the spec pairs "step
factor 0.85, max 2 shrink steps" with "while violated, tClear -= 0.15"; if the
built code implements these as two separate mechanisms (0.85 shaping the
steps, 0.15 the per-violation decrement) or as alternatives, and EITHER way
satisfies (b)(c), pass the check and flag the reading in the verdict for IO
confirmation; fail only if a mechanism named in (b)-(d) is missing outright;
(e) the FINAL want is `target + normalized(offset) * max(CFG.camMinDistance,
tClear * effDist)` — the direction normalized from the SAME offset vector
(built at 2253-2257), the magnitude via the max(camMinDistance, ...) clamp;
(f) lastCameraPull.wantDist = the pulled magnitude and lastCameraPull.effDist
= the uncapped magnitude are both updated per V14.

### V22 — Trunk-top fraction from CFG (A1 + A4 key coherence)
METHOD: code-read the trunk-vs-solid selection in the h attach sites
(region-manager.js) and grep -n 'trunkTopFrac' region-manager.js CONFIG.js.
PASS: (a) the vegetation-class test re-uses the EXISTING C14 classifier
verbatim (the TRUNK_ASSETS membership OR the /tree|oak|birch|sapling|bush|
bramble|fern|shrub|stump/i regex — the same code path colliderRadius already
runs at 444-450; a re-implemented or subtly different classifier FAILS); (b)
the trunk row's h literal reads `nativeWidth/height * scale *
CFG.player.cameraPull.trunkTopFrac` — NOT a hard-coded 0.45 (if 0.45 is
hard-coded, FAIL: it breaks the CONFIG key's purpose); (c) solid rows
(non-vegetation class, i.e. stones/boulders/fences/lantern posts) carry h =
nativeHeight * scale, NOT the top-frac multiplier; (d) wall-plan rows keep
V6's heightM regardless of trunk class (wall/segment/arch rows are solid mass
per design 1).

### V23 — fy = WH_GROUND.footY with the groundHas() guard (design 2)
METHOD: code-read the fy attach site in region-manager.js (props wall /
props / scatter circles) and the terrain-region dispatch. grep -n
'WH_GROUND|footY|terrain' prototype/js/region-manager.js.
PASS: (a) fy for region C terrain rows is computed at CONSTRUCTION time
(inside whPropColliders / whWallPlan, so the value RIDES the cache — no
per-frame getMeta/footY lookups in player.js at runtime); (b) the guard
repeats the computeFireSockets groundHas() pattern (game.js 1258-1260,
3089-3091): `if (<terrain active>) fy = window.WH_GROUND.footY(activeId, x,
z, <CFG.regionC.terrain.propFootR>)` — else fy = 0; the guard also tolerates
the terrain grid not being built yet (fy = 0 fallback, the row is STILL
pushed, no throw); (c) the footY r argument is the ACTIVE REGION'S
terrain.propFootR (1.2 today, CONFIG.js 887), NOT a hard-coded number and NOT
a different region's row (wh-ground footY semantics: min of center + 4
compass points at r; r falsy gives center only — so passing propFootR is
required for the spec's seat semantics); (d) A/B (no terrain row) fy = 0 with
no WH_GROUND read at all (guard short-circuits before touching
window.WH_GROUND for non-terrain regions — window.WH_GROUND must NEVER be
dereferenced on a flat-ground path).
FAIL on: an unguarded window.WH_GROUND.footY call (throw risk when the table
is not ready), a per-frame footY lookup (belongs at construction only), a
hard-coded 1.2, or an fy that ignores propFootR.

### V24 — y band edge cases (A7)
METHOD: code-read the band comparison in the pull block AND the fy fallback in
region-manager.js. Reason through the off-disc-terrain case (wh-ground.js
heightAt returns 0 off the disc, WH_GROUND doc comment lines 10-14).
PASS: (a) a sample with y_s > fy + h does NOT block (bushes never pull the
camera in — the canopy-above-trunk band is open); (b) a sample with y_s < fy
- 0.25 does NOT block; (c) a region-C row whose (x, z) falls outside the
heightfield disc gets fy = 0 from the heightAt-off-disc semantics (or from the
build fallback) and STILL gets a usable band [fy - 0.25, fy + h] — it does not
NaN or throw, and the band edge cases (a)/(b) still hold against fy = 0;
(d) the comparison is inclusive on the band edges per spec lines 55-56 (<=
r+R+skin; the y band read as fy - 0.25 <= y_s <= fy + h, or the code's
equivalent with documented off-by-e semantics NOTED in the verdict).
FAIL on any code path that lets an above-trunk or below-ground sample block,
or that NaNs/throws on an off-disc x/z.

### V25 — Conservative default for unmapped h/fy (A7)
METHOD: code-read the consumer defaults inside the pull block
(player.js). grep -n '12|-6' the pull block body.
PASS: a circle row missing h or fy (undefined / null / absent) is treated as
h = 12 (BIG occluder) and fy = -6 (LOW floor) per spec line 45-46; defaults
live in the CONSUMER (player.js pull block), not just the producer; the
defaults never crash (no throw on a missing field, the row is still tested).
FAIL if a missing h or fy yields h = 0 / fy = 0 (an unmapped row would then
NEVER occlude — backwards from conservative) or throws.

### V26 — Typos in the new code (A7 + A1)
METHOD: grep -n 'c\.h|\.fy|samples|skinM|camRadiusM|minFloor|trunk' on the
three touched files; code-read every hit against the CONFIG block (V3) and the
spec's field spellings (spec lines 44-46, 57, 64, 71-73).
PASS: zero spelling drift (e.g. c.fy/c.h vs c.fyY/c.hh; camRadiusM vs
cameraRadiusM; minFloor vs floorMin; trunkTopFrac vs trunkFrac) ANYWHERE the
new code references it. FAIL on any typo (even one that parses).

### V27 — enabled:false = legacy math, single early-out (A4 false path)
METHOD: code-read the enabled guard in the pull block (player.js).
PASS: when CFG.player.cameraPull.enabled is false the ENTIRE pull block
(body + lastCameraPull update) is skipped behind ONE boolean check (a single
`if (!CFG.player.cameraPull.enabled) return;`-style early-out or an
equivalent single `if (CFG.player.cameraPull.enabled) { ... }` wrap), and
with enabled=false the updateCamera math reduces EXACTLY to the pre-change
orbit (same sample loop skipped, same no-op, lastCameraPull NOT updated —
spec line 74-75 "must reproduce the pre-change math exactly (single early-out,
no allocation)"). No half-executed path (e.g. broadphase running then bailing,
lastCameraPull written on a disabled frame) FAILS.

### V28 — Consumer regions untouched (negative)
METHOD: code-read region-manager.js 526-545 (pushOutCircles) and
1805-1810/1835-1845 (the two circle consumers), CONFIG.js 2920-2955 + the
regionA/regionB/regionC cfg.props/enemies rows, and grep -n 'exempt'
prototype/js/region-manager.js.
PASS: (a) pushOutCircles body byte-identical (the push-out circle test,
dead-centre +x fallback at 538-539, etc.); (b) both consumers (player +
enemy AI) call the SAME propColliders accessor with the SAME activeId arg and
iterate .circles the same way; (c) the exempt array's PRODUCER (481) and its
non-existence in player.js per V17; (d) CONFIG.js region rows (props /
enemies / scatter) byte-identical to baseline (h/fy attach happens INSIDE
whPropColliders, never by editing CONFIG rows); (e) terrain rows
(CFG.regionC.terrain) untouched. FAIL on ANY of these.

### V29 — Files/conventions touched (negative)
METHOD: search_files over /tmp/wh-worldfeat/prototype for the new-code
markers (cameraPull|lastCameraPull) and read any file that shows up; check
the file inventory.
PASS: exactly THREE files carry the new code (CONFIG.js, region-manager.js,
player.js per spec "Files") — NO new file, NO fourth touched js file, NO
touched html; the new code uses var/function style only (NO arrow functions,
NO const/let, NO ES import/export); no new window global added by the pull
path (lastCameraPull lives on the Player instance per design 6, NOT on
window); the touched code adds no comment block that redefines C14 taxonomy
or invents new terms (spec "no new taxonomy" law — reuse the C14 language in
any new comments).

## Verdict (Testerbot fills after executing on the Devbot diff)

- Date / wake: ____
- Worktree/branch inspected: /tmp/wh-worldfeat feat/world-visuals
- Checks run (list, with any SKIP + reason): ____
- V-count: __/30 PASS (V1..V29 + V9b), __ FAIL
- Evidence anchors (file:line quotes for every FAIL): ____
- Cross-AC coverage: A1 [V18-V22, V9b], A2 [V10-V16], A3 [V5-V9], A4 [V3-V4,
  V27], A5 [V17], A6 [V14-V15], A7 [V24-V26], A8 [V12, V21], negatives
  [V2, V13, V28, V29]. All covered.
- Notes / IO rulings needed (e.g. V21's 0.85-vs-0.15 pairing): ____
- VERDICT: PASS / FAIL / PASS-WITH-NOTES
