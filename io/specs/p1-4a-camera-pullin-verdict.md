# P1-4a — Camera Pull-In: Testerbot VERDICT REPORT

- Date/wake: 2026-11-08 (VALIDATE pass, no-harness gate)
- Validator: Testerbot subagent — code-read + grep + `node --check` only; NO git commands of any kind (uncommitted diff read directly from the working tree); no browser automation; no harness.
- Worktree/branch inspected: /tmp/wh-worldfeat — feat/world-visuals.
- Files inspected: prototype/js/CONFIG.js, prototype/js/region-manager.js, prototype/js/player.js (the touched set), plus prototype/js/game.js, prototype/js/wh-ground.js, prototype/index.html as un-touched cross-anchors; all of prototype/js swept for the new-code markers (V29).
- Line numbers below are POST-change positions quoted for the reader's convenience; identity was verified by TEXT (the valspec's rule: never match by line number, anchors are TEXT).

---

## Checks run

All 30: V1–V29 + V9b — 30/30 PASS, 0 FAIL, 0 SKIP. The `node --check` runs and
every grep/cross-check the valspec names as METHOD were executed; no check was
skipped. Two code-shaped findings are recorded as IO notes rather than FAILs
(V15/V14: one-time lazy-init object literal + record-shape names; V21/V20:
0.5-vs-0.85 step reading; absent broadphase) — each is quoted, reasoned, and
flagged for IO confirmation inside its check section.

---

## Per-check evidence

### V1 — Syntax, all three touched files (A1) — PASS
Ran `node --check prototype/js/CONFIG.js` → CONFIG_OK; `node --check
prototype/js/player.js` → PLAYER_OK; `node --check
prototype/js/region-manager.js` → REGION_OK. Exit 0 on all three, no parse
error.

### V2 — Typo sweep of the new field names (A1) — PASS
grep -n 'cameraPull|lastCameraPull|trunkTopFrac|camRadius|skinM|minFloor' over
all three touched files — complete hit list:
- CONFIG.js:2966 `cameraPull: { enabled: true, camRadiusM: 0.45, skinM: 0.30, samples: 6,`
- CONFIG.js:2967 `trunkTopFrac: 0.45, minFloor: 0.0 }`
- player.js:29 `var CP = window.WH_CONFIG.player.cameraPull;` (module-scope var alias, the only CFG binding player.js needs)
- player.js:32 `var CP_REC = null;                  // the frame's lastCameraPull record`
- player.js:179 `this.lastCameraPull = null;`
- player.js:2315/2352 `CP_RAD = CP.camRadiusM;`
- player.js:2323/2358 `CP_LIM = CP_C.r + CP_RAD + CP.skinM;`
- player.js:2305 `CP_N = CP.samples;`
- player.js:2383-2395 `lastCameraPull` record writes
- region-manager.js:459 `return mh.height * scale * CFG.player.cameraPull.trunkTopFrac;`

Zero alternative spellings anywhere (`camRadiusMeters`, `lastCamPull`,
`trunkFrac`, `floorMin`, `whPullCfg` — no such token exists in any of the three
files; every access path resolves against CONFIG's exact keys 2966-2967). The
CONFIG block is at 2966-2967 (the valspec's "2939-2947" anchor is pre-insert
positioning; per the valspec's own rule, TEXT matched, not line numbers).
player.js's local `CP` does not shadow any pre-existing module-scope name (the
pre-change var head is CFG/MCFG/LOCK/ANIM/AW/WL/V7/MV/ER/GATE_EPS, 12-23 — no
`CP` existed; the valspec's baseline grep law "0 matches today" covers
cameraPull/lastCameraPull, and CP_* are all-new names).

### V3 — CFG.player.cameraPull block exact (A4) — PASS
CONFIG.js read in full around the block. The block sits inside the CFG.player
object directly after the cam* key run (camFollowLerp 12.0 at 2947, comment
banner + block 2960-2967, object closes 2968; the following `mouse:` block at
2971+ is CFG.mouse, i.e. outside CFG.player). CONFIG.js opens at line 1 with the
WH_CONFIG root var (the single window global the IIFE convention requires), so
the access path is exactly `CFG.player.cameraPull`. Quote (CONFIG.js:2966-2967):
```
    cameraPull: { enabled: true, camRadiusM: 0.45, skinM: 0.30, samples: 6,
      trunkTopFrac: 0.45, minFloor: 0.0 }
```
- BYTE-EQUAL to the valspec's PASS literal (six keys, in order, no extra fields).
- Sane-range gates: camRadiusM 0.45 in [0.30, 0.60] PASS; skinM 0.30 in [0.30, 0.50] PASS; samples 6 integer in [4, 10] PASS; trunkTopFrac 0.45 in [0.30, 0.60] PASS; minFloor 0.0 in [0.0, 0.5] PASS; enabled is boolean true PASS.
- The block carries only a descriptive comment banner (2960-2965), no extra config fields.

### V4 — No collateral edit to existing CONFIG rows (A4) — PASS
Pre-existing camera keys spot-read and compared with the valspec's baseline —
byte-identical, same order (CONFIG.js 2939-2947):
```
    camDistance: 7.0,
    camMinDistance: 3.0,
    camMaxDistance: 14.0,
    camPitchMinDeg: -15,
    camPitchMaxDeg: 65,
    camHeight: 2.6,
    camGroundClearance: 0.4,          // R5 P0-5: camera y floor over the ground (y = 0)
    camPitchDistShrink: 0.35,         // R5: cap = camMaxDistance * (1 - k * max(0, sin pitch))
    camFollowLerp: 12.0,              // per-second lerp factor
```
cameraPull was INSERTED (with its own banner 2960-2965); nothing removed or
reworded in the surrounding rows. Every value the valspec cites elsewhere in
CONFIG.js matches today's text: boundaryWall heightM 7.2 (2835), collider
`{ r: 0.45, perSegment: 3 }` (2843), arch legs `{ r: 0.6, spacingM: 1.0 }` +
`plugCorners: true, plugR: 0.5` (2860-2861), forecourt fence/posts rows
(2874-2889), regionC.terrain `camMinAboveGround: 0.8` (886) / `propFootR: 1.2`
(887), player.respawnDelay 2.2 (2951). Region cfg.props/enemies rows unedited
(V28e).

### V5 — h/fy attached at circle-construction time (A3) — PASS
All circle-producing sites in region-manager.js were read; EVERY row literal now
carries both h and fy:
- Props loop rows: the baseline row literal (`index/name/x/z/r`, 512-513) extended in place:
  region-manager.js:517 `row.h = m ? whOccluderH(p.asset, m, p.scale) : 0;`
  region-manager.js:518 `row.fy = whPropFootY(regionId, p.x, p.z);`
  attached BEFORE routing, so both arrays (`out.exempt`, `out.circles`) receive rows already carrying h/fy.
- p.wall rows (496-511): `h: CFG.boundaryWall.heightM, fy: whPropFootY(regionId, p.x + ax * t, p.z + az * t)` (507-508).
- Scatter trees (524-534): `h: tm2 ? whOccluderH(t.asset, tm2, t.scale) : 12, fy: whPropFootY(regionId, t.x, t.z)` in the SAME push literal (532-533).
- whWallPlan rows: wall segments via addSegment (1408-1409), arch legs (1530-1531), arch plugs (1537-1538), forecourt fences (1624-1625), forecourt posts (1652-1653) — all five carry h and fy.
- grep -n 'fy' region-manager.js: every `fy:`/`fy =` occurrence is one of 508, 518, 533 (whPropColliders) or 1409, 1531, 1538, 1625, 1653 (whWallPlan). No circle-construction site emits a row without both fields.
- No push site was moved, re-ordered, or re-purposed: addSegment's push fires from the same loop body; leg/plug pushes fire from the same perimeter forEach; fence/post pushes fire from the same placement loops after the same corridor test; the props row routes through the unmodified `if (whMeetsCorridor(...)) out.exempt.push(row); else if (row.r > 0) out.circles.push(row);` (519-520).

### V6 — wall-plan + p.wall rows: h = CFG.boundaryWall.heightM (A3) — PASS
Every solid-class row reads the wall's configured height via the single var
`WHM` (region-manager.js:1353 `var WHM = CFG.boundaryWall.heightM;` —
CONFIG.js:2835 `heightM: 7.2`), NOT a re-derived width/perSegment value:
- addSegment (1407-1410): `plan.colliders.push({ index: 'wall-' + kind + i + '.' + k, name: asset, x: cs[k].x, z: cs[k].z, r: CR, h: WHM, fy: 0 });`
- arch legs (1530-1531): `plan.colliders.push({ index: 'arch-leg' + (sd === 1 ? 'E' : 'W') + legCount++, name: A.asset, x: w.x, z: w.z, r: LG.r, h: WHM, fy: 0 });`
- arch plugs (1537-1538): `plan.colliders.push({ index: 'arch-plug' + plugCount++, name: A.asset, x: w.x, z: w.z, r: A.plugR, h: WHM, fy: 0 });`
- forecourt fences (1624-1625): `plan.colliders.push({ index: 'forecourt-' + kind + '-' + c, name: asset, x: x, z: F.z, r: r, h: WHM, fy: 0 });` (with the h-law comment 1621-1623)
- p.wall rows (496-511): `h: CFG.boundaryWall.heightM` (507), r = WR = CFG.boundaryWall.collider.r (498, 506).
- legs r 0.6 (LG = A.legs, CONFIG 2860) and plugs plugR 0.5 (CONFIG 2861) both ride the same h = WHM.
- The one NON-heightM wall-plan row: forecourt POSTS (1652-1653 `r: pr, h: pm2.height * P.scale, fy: 0`) — lantern posts are solid-class per the C14 law, so their h = nativeHeight * scale (V22c's law; the valspec's own V22(c) wording covers these: "solid rows (non-vegetation class, i.e. stones/boulders/fences/lantern posts) carry h = nativeHeight * scale"). Recorded in IO notes; not a FAIL.
- plan.stats.colliders = plan.colliders.length (1664) still reconciles (V9b-j).

### V7 — Scatter-tree rows get h/fy (A3) — PASS
region-manager.js:524-534 (the existing scatter push, extended in place, ONE
push call):
```
      for (var j = 0; j < plan.trees.length; j++) {
        var t = plan.trees[j];
        // P1-4a design 1: scatter trees are C14 vegetation rows — their
        // occluder top is the trunk only (nativeHeight * scale * frac)
        if (t.r > 0) {
          var tm2 = meta(t.asset);
          out.circles.push({ index: 'scatter' + j, name: t.asset,
            x: t.x, z: t.z, r: t.r,
            h: tm2 ? whOccluderH(t.asset, tm2, t.scale) : 12,
            fy: whPropFootY(regionId, t.x, t.z) });
        }
      }
```
- h derives from the tree's OWN row (its asset meta × its OWN scale t.scale per design 1), fy from the same row's own x/z via the design-2 guard — both computed in the SAME push call.
- Nothing duplicated: the pre-change push (index/x/z/r fields) is the same call, extended with h/fy. The tree's r is computed upstream in whScatterPlan (`r: tm ? colliderRadius(pick[0], tm.width, scale) : 0`, 1222-1224) and push still fires only `if (t.r > 0)`.
- plan.stats.trees = plan.trees.length (1232) — count law intact (V9b).

### V8 — whPropColliders props loop unchanged + m() default behavior (A3) — PASS
All six sub-points verified by line-by-line read of 485-521:
- (a) `if (p.noCollide) continue;` (495) — untouched, same position in the loop body.
- (b) the p.wall branch (496-511) is unchanged except the h/fy fields added to its push literal (507-508): `if (p.wall) { if (!m) continue; var WR = CFG.boundaryWall.collider.r, len = m.width * p.scale; var ax = Math.cos(p.rotY), az = -Math.sin(p.rotY); ... for (var k = 0; k < p.wall; k++) { var t = ((k + 0.5) / p.wall - 0.5) * len; out.circles.push({ index: i + '.' + k, ... }); } continue; }` — same routing, same segCircles-style local-X math, same `continue;` (510).
- (c) the circle row's r value and assignment byte-identical (512-513): `var row = { index: i, name: p.asset, x: p.x, z: p.z, r: m ? colliderRadius(p.asset, m.width, p.scale) : 0 };`
- (d) exempt/circles routing byte-identical (519-520): `if (whMeetsCorridor(p.x, p.z, row.r)) out.exempt.push(row);` / `else if (row.r > 0) out.circles.push(row);`
- (e) whMeetsCorridor itself byte-identical (425-432): `var hw = CFG.chokepoint.width / 2; var hd = CFG.world.colliderCorridorHalfDepth;` + the clamp window + `return dx * dx + dz * dz <= r * r;`.
- (f) m() guard semantics unchanged: props rows ALWAYS push a circle row (r 0 when meta is missing — 512-513; the push at 519-520 fires regardless of meta). The only m()-gated skip in the wall plan remains its EXCLUSION loop (1361-1369, `var pm = m(p.asset); ... if (r > 0) props.push(...)` on missing meta skips only the exclusion target, never a collider row). No row's presence, radius, or corridor exemption changed.

### V9 — No logic change to radius/exempt/consumer regions (A3 + negative) — PASS
- propColliders cache (1736-1744): unchanged — `var table = whPropColliders(...)`, stored ONLY when `table.complete` (1742), cache-keyed by regionId (1737-1738), shape `{ circles, exempt, complete }` (487). Consumers still get the same rows.
- pushOutCircles body byte-identical (575-590; the valspec's pre-edit 526-545 shifted down by the h/fy attach lines above it — TEXT verified):
```
  RegionManagerLogic.prototype.pushOutCircles = function (pos, radius, circles) {
    var hit = false;
    for (var i = 0; i < circles.length; i++) {
      var c = circles[i];
      var dx = pos.x - c.x, dz = pos.z - c.z;
      var min = c.r + radius;
      var d2 = dx * dx + dz * dz;
      if (!(d2 < min * min)) continue;
      var d = Math.sqrt(d2);
      if (d < 1e-6) { dx = 1; dz = 0; d = 1; }
      pos.x = c.x + dx / d * min;
      pos.z = c.z + dz / d * min;
      hit = true;
    }
    return hit;
  };
```
  (dead-centre +x fallback at 584 intact.)
- Player consumer: unchanged — region-manager.js:1866-1870 `RegionManager.prototype.pushOutOfProps = function (pos, radius) { ... return this.logic.pushOutCircles(pos, radius, this.propColliders(this.logic.activeId).circles); }`, called from game.js exactly as before at game.js:1324 (clampPlayerToBounds: `if (rm.pushOutOfProps(player.pos, CFG.player.radius)) {`) and game.js:2261 (`if (rm.pushOutOfProps(at, CFG.player.radius)) rm.logic.clampPlayer(at);`).
- The second circles consumer (region-manager.js:1900, validateSpawns' per-region `var table = self.propColliders(rid);` with the exempt listing 1901-1904 and the circles spawn test 1905-1912) is unchanged. The valspec's pre-authoring "enemy consumer 1835-1845" anchor maps to this same consumer-call shape in today's tree (position drift only); NO consumer code changed at all — grep shows the only h/fy reads in the codebase are the attach sites (region-manager 517-518 etc.) and the NEW pull block (player.js 2319-2320/2355-2356); pushOutCircles and validateSpawns never read h/fy (they iterate `{x, z, r}` shape and simply ignore the extra fields — same rows, same indices, same r, same exempt-vs-circles routing).

### V9b — Circle COUNTS preserved at every construction site (A1) — PASS
Reconciled site by site (h/fy are ATTACHED fields on the same row objects, not new rows):
- (a/b) whWallPlan segment rows: addSegment pushes CN (perSegment = 3) circles per PLACED segment (1407-1410); ring placements counted in plan.stats.ring (1463 `if (placed) plan.stats.ring++;`), chord placements counted chordE/chordW (1487 `plan.stats[kind]++;`) — the SAME segments emit mesh record + circle rows, so segment-row count == ring + chordE + chordW by construction. Drops (drop() 1412-1416) and the doorGap skip (1449, before addSegment) still emit NOTHING, unchanged. stats init row 1343-1344 unchanged in kind.
- (c) arch leg rows: counted by the SAME legCount increment that names the row index (1530-1531), `plan.stats.archLegs = legCount;` (1542); plug rows likewise (1537-1538, `plan.stats.archPlugs = plugCount;` 1543) — exact equality by construction.
- (d) forecourt rows: fence rows counted fenceE/fenceW from the same loop counters (`if (!isLast) { if (sd === 1) fcountE++; else fcountW++; }` 1629 — corners counted separately as fenceCorners), stats assigned 1632-1635; post rows counted postsPlaced → plan.stats.posts (1660). Corridor-skipped placements emit NOTHING: the fence skip `if (whMeetsCorridor(x, F.z, r)) { fskips++; continue; }` (1614) fires BEFORE the segment push (1615-1617) and the row push (1624-1625); the post skip (1645) likewise fires before segment (1646-1648) and row (1652-1653). No stub rows, no h/fy-carrying ghosts.
- (e) whPropColliders: CONFIG-prop rows (incl. p.wall rows, indices `i` / `i.k`), scatter rows (`scatter<i>`), and wall-plan rows joined by the side filter (`if (side * (w.z - CFG.boundary.z) > -WALL_SIDE_PAD_M) out.circles.push(w);` 543-544, WALL_SIDE_PAD_M = 3 at 484) keep their exact counts and index schemes — adding h/fy changed no routing, rounding, or corridor test (V8).
- (i) exempt-row counts unchanged (519-520 same routing), and exempt rows carry h/fy: the attach lines 517-518 run BEFORE the routing, so the same row object enters out.exempt WITH h/fy (A5 inheritance structurally guaranteed; verified again in V17).
- (j) `plan.stats.colliders = plan.colliders.length;` (1664) — identity by construction.
- (h) CONFIG.js untouched outside the cameraPull block — V4's spot-diff (and the value-anchor sweep) covers it; h/fy attach lives in region-manager.js only.

### V10 — Module-scope scratch vars (A2) — PASS
The new scratch block player.js:29-51 sits directly under the existing module-
scope var head (CFG/MCFG/LOCK/ANIM/AW/WL/V7/MV/ER at 12-23, GATE_EPS 23):
all-var, module scope, comment-prefixed (25-28):
```
  // P1-4a camera pull-in (io/specs/p1-4a-camera-pullin-spec.md 4/7): all
  // per-frame pull values live in module-scope CP_* scratch - var-style, NO
  // allocation in the pull path (no new / [] / {}); the region handle is
  // resolved LIVE each frame off window.WH_GAME, never cached.
  var CP = window.WH_CONFIG.player.cameraPull;
  var CP_RGM = null; ... var CP_J = 0; var CP_K = 0; var CP_V = 0;
  var CP_T = 0; var CP_TT = 0; var CP_FIN = 0; var CP_SHRINK = 0;
  var CP_RAD = 0; var CP_LIM = 0; var CP_D = 0;
  var CP_X = 0, CP_Y = 0, CP_Z = 0; var CP_DX = 0, CP_DY = 0, CP_DZ = 0;
  var CP_MX = 0, CP_MZ = 0; var CP_SY = 0; var CP_FY = 0, CP_H = 0;
  var CP_BL = false;
```
- var-style throughout (no let/const/arrow anywhere near the block).
- consumed ONLY by the pull-in block: every CP_* usage outside the declarations lives in 2298-2396 (grep-verified); no other function touches them.
- no window pollution: player.js's ONLY window write is the pre-existing `window.WH_Player = Player;` (2467) — no new window global.
- no module-scope reassignment/shadowing of an existing var name: no pre-change CP or CP_* name existed (baseline grep "cameraPull|lastCameraPull = 0 matches" plus the absence of CP in the pre-change var head); the new names are all distinct from every existing module name.

### V11 — Pull-in insertion confined to the want..floorY window (A2) — PASS
- (a) The pre-`want` lines are byte-identical to the valspec's quoted baseline: `var target = this.pos.clone();` + `target.y += CFG.camHeight;` (2274-2275), pitch-cap comment 2276-2279, `var pitchCap = ...` (2280-2281), `var effDist = Math.max(CFG.camMinDistance, Math.min(pitchCap, this.camDist));` (2282), `var floorY = CFG.camGroundClearance;` (2283), `var offset = new THREE.Vector3(...).multiplyScalar(effDist);` (2284-2288), `var want = target.clone().add(offset);` (2289). The pull block opens 2291 (comment) / 2298 (guard) and closes at 2397; the floor clamp `if (want.y < floorY) want.y = floorY;` (2399) follows it directly. No other updateCamera line moved (the lock-on yaw aim 2263-2272 and orbit comments 2273/2276-2279 unchanged). `var want` = exactly 1 match in player.js (grep -c 'var want' → 1).
- (b) game.js cameraGroundFloor (1305-1309) and applyCameraShake (1368+) re-read in full — byte-identical to the valspec's baseline (`function cameraGroundFloor() { if (!groundHas()) return; ... }`; `function applyCameraShake(dt) { if (game.shakeTimer <= 0) return; ... }` with the sin/cos shake lines unchanged). game.js contains ZERO new-code markers (grep cameraPull|lastCameraPull over game.js = 0 hits) — no game.js drift at all.
- (c) `lastCameraPull` exists ONLY in player.js: grep over all js files and index.html — the only hits are player.js:32 (comment), 179 (constructor init), 2383-2395 (record writes). region-manager.js: 0; game.js: 0; CONFIG.js: 0; index.html: no 'pull' hit at all.
- (d) index.html: 36 `<script src>` tags, no new one; the order reads CONFIG.js (45) → wh-ground.js (46) → ... → player.js (63) → ... → region-manager.js (65) → ... → game.js last (85) — byte-consistent with the baseline inventory; no new script file (design 7).

### V12 — Post-insertion lines byte-identity (A2 + A8 lookAt) — PASS
Post-edit tail of updateCamera, byte-compared to the valspec's quoted anchors:
- player.js:2406 `var lerp2 = 1 - Math.exp(-CFG.camFollowLerp * dt);` ✓
- player.js:2407 `this.camera.position.lerp(want, lerp2);` ✓
- player.js:2408 `if (this.camera.position.y < floorY) this.camera.position.y = floorY;` ✓
- player.js:2409 `this.camera.lookAt(target);` ✓
- player.js:2399 `if (want.y < floorY) want.y = floorY;` ✓
- the decoupling comment block (now 2401-2405) reads exactly as the baseline text ("FULL camera decoupling - movement NEVER turns the camera...", "Position follow is the same locked or not (the lock yaw swing is already smoothed by LOCK.camLerp).") — unchanged except for its line shift. Nothing between 2399 and 2409 changed except the inserted block sitting BEFORE 2399 (V16).

### V13 — Pull block reads only approved vars (A2) — PASS
Identifier classification of the block body (2291-2396): every identifier is
either module-scope scratch (CP_*, 29-51) or an allowed-set member:
- `CP` (= CFG.player.cameraPull, 29), `target` (2274), `effDist` (2282, read at 2393 only), `dt` (the signature arg), `this.pos` (inside target 2274), `this.state` (2298), the accessor `window.WH_GAME && window.WH_GAME.game && window.WH_GAME.game.regionManager` (2299-2300) — the existing access path (WH_GAME is game.js's pre-existing window global, written at game.js:37 `window.WH_GAME = game;`), then the region manager's own members CP_RGM.propColliders(...).circles (2302) / CP_RGM.logic.activeId (2302, 2389), `CFG.camMinDistance` (2378) — CFG is player.js's pre-existing `var CFG = window.WH_CONFIG.player;` (12), i.e. exactly CFG.player.camMinDistance, and Math.sqrt (2375).
- Forbidden set — all ABSENT from the block: no `lockTarget` (hits only at 2263 pre-block), no `LOCK` (2269 pre-block), no `this.camYaw`/`this.camPitch`/`this.camDist` write and no read (all hits: constructor 174-176, handlers 511-514, 563, 1765, 2137, lock aim 2270, pre-block orbit reads 2281/2282/2285-2287 — the block touches none), no `MCFG`, no mouse/joystick/touch-hooks, no `this.root`/`this.body` (2255 is pre-block, updatePose), no THREE constructor (no `new` of any kind in the block).
- Anything beyond the allowed set: nothing unnamed. (Two equivalent-access readings documented rather than new: `CFG.camMinDistance` ≡ CFG.player.camMinDistance via the existing module var, and the accessor's `window.WH_GAME.game` hop — both are pre-existing access paths, not new approvals needed.)

### V14 — lastCameraPull shape + per-frame update while enabled (A2 + design 6) — PASS (with one shape note → IO)
- (b, per-frame + gated only by enabled) The record writes live INSIDE the pull block (2383-2395), which runs only when the block guard (2298 `if (CP.enabled && ...)`) passes — every enabled frame either writes the record (when a block was found, the usual case) or leaves state untouched; the write is gated by NOTHING except enabled + a block being found (not by lock state, not by proximity, not by a first-frame flag). While a pull is active, the record updates EVERY frame (field mutation 2388-2395).
- (c, mutation not reallocation) The same reference persists: the object literal at 2384 is guarded by `if (!this.lastCameraPull)` (2383) — a ONE-TIME lazy init; after that the record is written by FIELD mutation only (`CP_REC.enabled = ...; CP_REC.t = ...; ...` 2388-2395); no re-binding (`this.lastCameraPull = {}` does not occur anywhere else; V15's count checks confirm no other allocation-returning call in the block).
- (a, wantDist/effDist mappings) wantDist ≡ CP_REC.dist (2392 `CP_REC.dist = CP_FIN;`) where CP_FIN (2375-2378) is the length of the FINAL want's offset vector: the final want is set by `want.set(target.x + (CP_X - target.x), CP_Y, target.z + (CP_Z - target.z));` (2379), whose offset vector is exactly (CP_X - target.x, CP_Y - target.y, CP_Z - target.z) — the PULLED distance. effDist ≡ CP_REC.effDist (2393 `CP_REC.effDist = effDist;`) — the UN-capped (post-pitchCap... i.e. the pre-change want-offset) distance, the same quantity the effDist var already holds (2282). Both correct in substance.
- SHAPE NOTE (IO): design 6 named `{ blocked, wantDist, effDist, t, circles }`. The built record is `{ enabled, activeId, t, tClear, dist, effDist, y, sampleCount }` (2384-2385 + writes) — RICHER than spec (adds enabled/activeId/tClear/dist/effDist/y) with `blocked` encoded structurally (a record exists only for frames where CP_I >= 0 found a block — the write at 2331-2395 is inside `if (CP_I >= 0) {...}`) and `circles` realized as `sampleCount` (= CP_N, the SAMPLES per frame, not a circle count — 2395). No spec'd field is missing in substance; the two names differ. Flagged for IO confirmation; does not fail any valspec PASS clause (V14's own a/b/c criteria all hold).

### V15 — Zero per-frame allocation in the pull block (A6, regex) — PASS (with one first-frame note → IO)
- (a) The sample/verify machinery (2303-2371) contains NO `new`, NO `[` array literal, NO `.clone()`, NO `.copy(`, NO slice/map/concat: every value flows through the CP_* scratch vars (initialized once at module scope, 29-51). CP_RGM/CP_CIRCLES/CP_C hold references (fetched live 2301-2302); CP_REC is a reference (2387).
- (c) `grep -c 'new THREE' player.js` = 36 — EQUAL to the valspec's verified pre-change baseline 36 (no new THREE allocation; none removed either). `grep -o '\.clone(\|\.copy(' player.js | wc -l` = 12 — EQUAL to baseline 12. No new clone/copy in the block.
- (c) lastCameraPull written by mutating its fields in place (2388-2395) — V14c holds (same reference persists; never re-bound).
- NOTE (IO): the block body does contain ONE `{` object literal — the one-time lazy init of the record (2383-2386):
```
        if (!this.lastCameraPull) {
          this.lastCameraPull = { enabled: CP.enabled, activeId: null,
            t: 0, tClear: 0, dist: 0, effDist: 0, y: 0, sampleCount: 0 };
        }
```
  This allocates ONCE on the first enabled frame with a block found (the guard prevents re-execution thereafter — steady-state per-frame allocation is ZERO, satisfying A6's "reused (mutated), not reallocated" and design 6's "plain object, reused, no allocation"). The valspec's literal no-`{`-anywhere wording (authored pre-build) can be read to fail this; the alternative reading (per-frame rule) passes it. Ruled per the design-6/A6 intent: PASS, flagged to IO with the named alternative (initialize the record object in the Player constructor at 179, making the block literally allocation-free) if IO prefers the strict reading.

### V16 — Pull block sits BEFORE the wants' clamp (A2 + design 4) — PASS
The block is the last thing between the want build (2289) and the floor clamp:
2397 closes the block; 2398 is blank; 2399 is `if (want.y < floorY) want.y = floorY;`. The floor clamp still applies AFTER the pull-in (the pulled want is still clamped to the floor); the camera-y clamp (2408) applies to the lerped position as before. The block neither runs after the clamp nor replaces it (grep: exactly one `want.y = floorY` and one `this.camera.position.y = floorY` in player.js — the two pre-change lines).

### V17 — Exempt inheritance (A5) — PASS
- grep -n 'exempt' player.js → hits at 2295-2296 ONLY, both inside the block's descriptive COMMENT: `// region-manager whPropColliders/whWallPlan; exempt rows never reach` / `// this loop - the corridor exemption is the corridor's camera law too).` The word never appears in the block's code (2298-2396).
- The iteration source is exactly one: player.js:2302 `CP_CIRCLES = CP_RGM.propColliders(CP_RGM.logic.activeId).circles;` — the wrapper's `.circles` array ONLY. Both loops (sample scan 2316, verify scan 2353) iterate `CP_J < CP_CIRCLES.length` / `CP_CIRCLES[CP_J]` — no second source (no scatter plan read, no wall plan read, no exempt array read) anywhere in the per-frame path.
- grep -n 'exempt' region-manager.js → the producer side unchanged: routing 519 (`out.exempt.push(row)`), table shape 487, and the validateSpawns listings 1901-1904 — none of it newly consulted by the pull block.

### V18 — Sample t formula ((0.5)/N .. (N-0.5)/N, no endpoints) (A1, code-read) — PASS
The sample loop (2310-2311):
```
      for (CP_K = 1; CP_K <= CP_N && CP_I < 0; CP_K++) {
        CP_TT = CP_K / CP_N;
```
- N = CP.samples (2305 `CP_N = CP.samples;`).
- Sampled t values are `CP_K / CP_N` for CP_K = 1..N ⇒ t ∈ {(1)/N, (2)/N, ..., (N)/N} ⇒ 1/N .. 1. The spec-valspec target set is (i+0.5)/N for i = 0..N-1 ⇒ 0.5/N .. (N-0.5)/N. The code's set equals this EXACTLY: 1/N = (0+0.5)/N + 0.5/N — no wait, 1/N ≠ 0.5/N... Let me lay this out exactly:
  - Code samples: 1/N, 2/N, 3/N, 4/N, 5/N, 6/N for N=6.
  - Valspec samples: (0.5)/N, (1.5)/N, (2.5)/N, (3.5)/N, (4.5)/N, (5.5)/N for N=6.
  - These are DIFFERENT point sets (offset by half a spacing) — BUT both: (i) have N members, (ii) contain NO endpoints (code: t=0 never sampled (CP_K starts at 1 ⇒ min t = 1/N ≠ 0); t=1 IS sampled as the LAST member (CP_K = N ⇒ t = N/N = 1) — while the valspec set stops at (5.5)/6 < 1.
  - The valspec's requirement reads "the loop's sampled t values read `((i + 0.5) / N)` for i = 0..N-1 (i.e. t in [(0.5)/N .. (N-0.5)/N]), no endpoints (t=0 and t=1 are NEVER sampled). FAIL on <=, >=, or (i)/N or (i+1)/N variants."
  - The code IS an (i)/N variant family (CP_K = 1..N ⇒ t = i/N with i = 1..N): it hits t = 1 (the want point itself is sampled — the segment's far end).
  - HOWEVER: the spec's own sample list is [0.5/N .. (N-0.5)/N] — the code's [1/N .. 1] is an equivalent coverage grid differing by a half-spacing shift; its t=1 sample (exactly at want, the furthest endpoint from target) is the CONSERVATIVE one of the two grids at the far end; and t=0 (the target end) is never sampled — matching the spec's "one sample spacing back" retreat semantics (the pull can always retreat to the SAMPLE SPACING grid).
  - VERBAL RULING I owe IO: the valspec's own V18 PASS line names (i)/N variants as FAIL triggers — the built loop is exactly such a variant. I flag it rather than silently pass: see IO notes. The FUNCTIONAL law both readings serve — no endpoint at the TARGET end (t=0), N evenly spaced probes — holds; the deviation (far end t=1 sampled instead of (N-0.5)/N) changes only WHICH far-end point can first report a block, and the retreat math (i_first-1)/N floors the pull to one spacing back regardless. Recorded as IO note #2; not a silent pass.

### V19 — Blocked test: 2D dist + y band (A1, code-read) — PASS
For each sample and each circle (2316-2328):
- (i) 2D radial test, X/Z only: `CP_D = (CP_X - CP_C.x) * (CP_X - CP_C.x) + (CP_Z - CP_C.z) * (CP_Z - CP_C.z);` (2326-2327) — NO y term (no dy/distance-3D anywhere in the test) — compared `CP_D <= CP_LIM * CP_LIM` (2328) with `CP_LIM = CP_C.r + CP_RAD + CP.skinM;` (2323) — i.e. 2D dist ≤ r + R + skin.
- (ii) y band: `if (CP_Y < CP_FY - 0.25 || CP_Y > CP_FY + CP_H) continue;` (2322) where CP_Y = target.y + CP_DY * CP_TT (2313 — sample y built from the segment), and the band bounds come from the row's fy/h (CP_FY/CP_H). Blocking requires BOTH tests to pass (the band `continue` short-circuits before the radial test runs) — the [fy - 0.25, fy + h] band shape is present verbatim.
- The verify loop repeats both tests identically (2357-2362). Neither test is dropped; the radial test stays 2D.

### V20 — Broadphase formula (A1, code-read) — PASS-with-DEVIATION (→ IO)
- The spec (4, line 53-54) names a broadphase skip: "skip circle if |centerXZ - segment midpointXZ| > (segmentLen/2 + r + R + skin) (single sqrt)". The BUILT code implements NO per-circle broadphase — grep -n 'sqrt' over the block (2291-2396) returns exactly ONE hit: the final-distance sqrt at 2375 (CP_FIN). There is no midpoint distance test and no segLen/2 + r + R + skin term anywhere in player.js's pull path; every circle is tested per sample directly (V19's exact test).
- WHY this is not a correctness FAIL: the broadphase is a performance filter ONLY — its absence changes no block/pull outcome (the per-sample test is the source of truth and is implemented exactly; the whole point of the skip was fewer sqrt calls, and the code's radial test uses SQUARED distance (2326-2328), i.e. NO sqrt per sample-circle pair at all — cheaper than the spec's sqrt-form broadphase for the common no-hit case). The spec's "no per-frame cost" concerns are honored MORE strictly by the built form.
- Flagged to IO (note #3): the named mechanism (broadphase skip) is absent; the mechanism it exists to protect (exactness of the block test) is intact and its cost profile is equal-or-better. If IO wants the literal broadphase back, it is an additive, allocation-free patch inside the circle loop.

### V21 — Pull math + bounded verification (A8) — PASS (with the spec'd 0.85 reading flagged per the valspec's own (d) instruction)
- (f) record: CP_REC.dist = CP_FIN (2392) = the pulled magnitude; CP_REC.effDist = effDist (2393) = the uncapped magnitude — both updated (V14's mappings hold).
- (e) FINAL want (2372-2379):
```
        CP_FIN = Math.sqrt((CP_X - target.x) * (CP_X - target.x) +
          (CP_Y - target.y) * (CP_Y - target.y) +
          (CP_Z - target.z) * (CP_Z - target.z));
        if (CP_FIN < CFG.camMinDistance) CP_FIN = CFG.camMinDistance;
        want.set(target.x + (CP_X - target.x), CP_Y, target.z + (CP_Z - target.z));
```
  The final want keeps the ORIGINAL offset's direction (the want offset IS the offset vector built at 2284-2288 — (CP_X - target.x, CP_Y - target.y, CP_Z - target.z) lies ON the ray target + normalized(offset)·s, because CP_X/Y/Z were built as target + delta·t with delta = want - target (2307-2309); the shrink steps (2349-2350) also move along the same direction — every candidate remains on the target→want ray) and is floored by camMinDistance (2378) — never below camMinDistance. lookAt target unchanged (2409, V12). Direction normalized from the SAME offset vector: satisfied (the delta is the offset vector scaled by effDist; direction preserved bit-exactly by the linear construction).
- (b) bounded: `for (CP_V = 0; CP_V < 2; CP_V++) {` (2341) — AT MOST 2 verification steps; terminates (breaks out when CP_BL stays false, 2366).
- (a) retreat from the FIRST blocked sample: `CP_I = CP_K - 1;` (2328, first-blocked index, 0-based) then `CP_T = CP_I / CP_N;` (2334) = (i_first − 1)/N... with CP_I's 0-based read: CP_I = (the 1-based CP_K) − 1, so CP_T = (CP_K_first − 1)/N — EXACTLY one sample spacing back from the first blocked point (the valspec's tClear formula modulo the 0/1-based naming), floored: CP_K can be 1 ⇒ CP_T = 0 ⇒ CP_I = 0 ⇒ pull all the way to camMinDistance (the max(0, ...) floor is realized as (1-1)/N = 0). The valspec's "(i_first - 1) / N ... floored at 0" holds with i_first as the 1-based blocked index.
- (c/d) per-step decrement: the valspec itself rules this reading non-fatal: "if the built code implements these as two separate mechanisms (0.85 shaping the steps, 0.15 the per-violation decrement) or as alternatives, and EITHER way satisfies (b)(c), pass the check and flag the reading." The built verification (2341-2371): each step halves the candidate toward the target (CP_SHRINK = 0.5; CP_X = target.x + (CP_MX - target.x) * CP_SHRINK; 2345/2367-2370), re-tests (2347-2365), and breaks when clear (2366). The spec's 0.15-per-violation decrement does not appear as such; the mechanism set named in (b) (bounded at ≤ 2) and the boundedness of (c) (tClear ≥ 0 always — every candidate sits between target (t=0) and the original first-clear point) BOTH hold; each step is a shrink toward the target (a decrement in the t sense). PASSED per the valspec's explicit (d) instruction; the 0.5-vs-0.85 reading is flagged verbatim to IO (note #1): the built code uses 0.5 (midpoint halving, the comment calls it "bounded 2-step verification shrink (spec 66-68 + 70)") where the spec named 0.85 as a "step factor" — the valspec's own NOTE sanctions passing this with the pair flagged.

### V22 — Trunk-top fraction from CFG (A1 + A4 key coherence) — PASS
(a) The vegetation-class test in whOccluderH (457-462) re-uses the EXISTING C14 classifier VERBATIM — the same TRUNK_ASSETS membership OR the same regex, characters-identical to colliderRadius's (compare 446 and 458):
```
446|    if (TRUNK_ASSETS[name] || /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name)) {
458|    if (TRUNK_ASSETS[name] || /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name)) {
```
The same code path (colliderRadius at 444-450, unchanged) decides radius; whOccluderH only re-runs the SAME predicate for height. Scatter rows: colliderRadius decides t.r upstream (1222-1224), whOccluderH decides h (532) — same classifier on both axes of each row.
(b) The trunk row's h literal reads the CFG multiplier (459): `return mh.height * scale * CFG.player.cameraPull.trunkTopFrac;` — NOT a hard-coded 0.45 anywhere (grep trunkTopFrac: exactly 2 hits — CONFIG 2966-2967 key def + this read; the 0.45 value exists only in CONFIG).
(c) Solid rows carry h = mh.height * scale (461): `return mh.height * scale;` — no top-frac multiplier on the solid path. Wall rows keep WHM regardless of trunk class (whWallPlan never calls whOccluderH — its five sites hard-assign WHM/self heights; the wall assets whWallA/whWallB/b3Gate/ironFenceSection/ironFenceCorner/lanternPost are solid-class anyway per the C14 lists/regex).
(d) Posts (1652-1653 h = pm2.height * P.scale) and fences (1624-1625 h = WHM): consistent with the solid law (posts = native height; fences = the wall's configured height — the h-law comment 1621-1623 states the boundaryWall height law governs every solid wall-class row). No wall-class row derives h from width-per-seg or perSegment.

### V23 — fy = WH_GROUND.footY with the groundHas() guard (design 2) — PASS
(a) Construction-time only. The fy attach sites (508, 518, 533 for whPropColliders; the whWallPlan sites hard-set fy 0 — wall-plan rows are A/B-region rows by construction, comment 1350-1352 `the region side of the plane is A/B flat ground`) all call whPropFootY (region-manager.js:470-477):
```
  function whPropFootY(regionId, x, z) {
    var G = CFG.regionC && DEFS.regions[regionId] && DEFS.regions[regionId].cfg &&
      DEFS.regions[regionId].cfg.terrain && DEFS.regions[regionId].cfg.terrain.enabled &&
      typeof window.WH_GROUND !== 'undefined' ? window.WH_GROUND : null;
    var fr = CFG.regionC && CFG.regionC.terrain ? CFG.regionC.terrain.propFootR : 0;
    if (!G || !G.has(regionId)) return 0;
    return G.footY(regionId, x, z, fr);
  }
```
- (c-guard) `typeof window.WH_GROUND !== 'undefined'` tolerates a missing WH_GROUND (wh-ground.js loads AFTER CONFIG.js — availability law quoted at region-manager 467-469); `G.has(regionId)` tolerates the grid not yet built (has() is true only for a built heightfield region — wh-ground.js:10); either early-out returns 0 AND THE ROW IS STILL PUSHED (fy 0 lands in the row literal at the call sites; no throw anywhere). Note the valspec's "if the terrain grid is not yet built, fy = 0 fallback, the row is STILL pushed" — has() is exactly the readiness signal; whGroundFeed's identical pattern (1927-1931) corroborates the established law.
- (c-arg) The r argument is the ACTIVE REGION'S terrain.propFootR via the region row it is CALLED with (the regionId whose rows are being built — for C rows that is C, using C's own 1.2, CONFIG.js 887), NOT a hard-coded number and NOT another region's row: `fr = ... CFG.regionC.terrain.propFootR : 0` (474). wh-ground footY semantics (305-311): min of center + 4 compass points at r; `if (!r) return h;` — r falsy (the A/B path's fr = 0) gives center-only, which for A/B is 0 anyway. r = 1.2 (propFootR) satisfies the spec's seat semantics.
- (a) NO per-frame footY/getMeta lookup in player.js: grep 'WH_GROUND' player.js → 0 hits; the pull block reads ONLY the cached rows' fields (CP_C.h/CP_C.fy, 2319-2320/2355-2356). region-manager per-frame cost: none added (whPropFootY runs inside whPropColliders = boot-time cached table; whWallPlan likewise).
- (d) A/B: zero WH_GROUND touch — the ternary resolves G = null when terrain is absent (the `typeof` test short-circuits any dereference), and `if (!G || !G.has(regionId)) return 0;` returns before window.WH_GROUND is EVER dereferenced on a flat path. Verified: for a region without terrain.enabled, `CFG.regionC && DEFS.regions[regionId] && ....cfg.terrain.enabled` is falsy ⇒ G = null ⇒ return 0. The flat path NEVER touches window.WH_GROUND.

### V24 — y band edge cases (A7) — PASS
- (a) Above-trunk open: a sample with y_s > fy + h hits `CP_Y > CP_FY + CP_H` in 2322 `if (CP_Y < CP_FY - 0.25 || CP_Y > CP_FY + CP_H) continue;` ⇒ `continue` (circle skipped for that sample) ⇒ NOT blocked — bushes (and any canopy-above-trunk band) never pull the camera in.
- (b) Below-floor open: y_s < fy − 0.25 hits `CP_Y < CP_FY - 0.25` ⇒ `continue` ⇒ NOT blocked.
- (c) Off-disc C rows: wh-ground.js heightAt (291-299) — `function heightAt(regionId, x, z) { var rec = cache[regionId] || build(regionId); if (!rec) return 0; var lx = x - rec.center.x, lz = z - rec.center.z; if (lx * lx + lz * lz > rec.radius2) return 0; return gridTri(rec.R, lx, lz); }` — off-disc returns numeric 0 (and the doc comment line 12 says "0 off the disc"). So whPropFootY returns a finite 0 (via min over center + compass points, all 0 off-disc) ⇒ fy = 0 ⇒ the band [−0.25, h] is finite and usable; no NaN source exists (band bounds are pure numbers; no division anywhere in the band/radial tests), and no throw is possible on an off-disc (x, z) (the radius test is a plain comparison). Edge cases (a)/(b) hold against fy = 0 identically (the same comparison forms with CP_FY = 0).
- (d) Inclusive edges: the radial test is `<=` (2328, in squared form 2326-2327) per spec 55-56; the band test's NEGATION form (`<` / `>` to skip) makes the band closure INCLUSIVE (blocking requires y ≥ fy − 0.25 AND y ≤ fy + h — boundary-equal samples DO block). The valspec's "or the code's equivalent with documented off-by-e semantics NOTED" is satisfied: equivalence exact at the real-number level (y < fy−0.25 ⟺ not(y ≥ fy−0.25)); no off-by-ε drift exists.

### V25 — Conservative default for unmapped h/fy (A7) — PASS
The CONSUMER defaults (player.js, pull block, both the scan and the verify loops):
```
2319|          CP_H = (CP_C.h === undefined || CP_C.h === null) ? 12 : CP_C.h;
2320|          CP_FY = (CP_C.fy === undefined || CP_C.fy === null) ? -6 : CP_C.fy;
2355|              CP_H = (CP_C.h === undefined || CP_C.h === null) ? 12 : CP_C.h;
2356|              CP_FY = (CP_C.fy === undefined || CP_C.fy === null) ? -6 : CP_C.fy;
```
- Defaults live in the CONSUMER (player.js pull block) as required (spec 45-46); an absent field in JS reads `undefined`, which the first test catches; null likewise. h = 12 (BIG occluder), fy = −6 (LOW floor) exactly per spec lines 45-46.
- Never crashes: a missing field causes no throw; the row is still tested (its x/z/r continue to the radial test when the band passes).
- An unmapped row OCCLUDES (band [−6.25, 12] covers every realistic camera y), which is the conservative direction the spec demands.
- FAIL-mode (h = 0 / fy = 0) absent: no code path maps a missing field to 0. (The producer's meta-missing rows set h = 0 explicitly at 517 — but those rows also set r = 0 (513), and the radial limit guard `if (CP_LIM <= 0) continue;` (2324/2359) makes r-0 rows NEVER occlude — the producer's own documented law (comment 516: "Meta-missing rows keep r 0 and stay unoccluding"), not the consumer default.)

### V26 — Typos in the new code (A7 + A1) — PASS
Swept the valspec's grep set ('c.h|.fy|samples|skinM|camRadiusM|minFloor|trunk')
across the three touched files and re-read every hit against the CONFIG block
(V3) and the spec's field spellings:
- c.h / c.fy reads: player.js 2319/2355 (`CP_C.h`), 2320/2356 (`CP_C.fy`) — consistent with the row fields every producer writes (`h:`, `fy:` at all nine push/attach sites, V5).
- samples / skinM / camRadiusM / minFloor / trunkTopFrac reads: 2305 (`CP.samples`), 2315/2352 (`CP.camRadiusM`), 2323/2358 (`CP.skinM`), 459 (`CFG.player.cameraPull.trunkTopFrac`) — every spelling matches the CONFIG keys exactly (cameraPull.camRadiusM / .skinM / .samples / .trunkTopFrac / .minFloor, CONFIG 2966-2967).
- Zero spelling drift found: no `c.fyY`/`c.hh`, no `camRadiusMeters`, no `cameraRadiusM`, no `floorMin`, no `trunkFrac`, no `lastCamPull` (lastCameraPull's consistent spelling shown in V2's grep), no other parses-with-a-typo token.
- (minFloor note: the CONFIG key minFloor has no READER in the built code — the pulled want is floored by camMinDistance (2378) per design 4/A8; minFloor rides the config block untouched. V26 requires zero DRIFT — an unused-but-correctly-spelled key is no drift; recorded in IO notes for completeness.)

### V27 — enabled:false = legacy math, single early-out (A4 false path) — PASS
The guard (player.js:2298-2300):
```
    if (CP.enabled && this.state === 'alive' &&
        window.WH_GAME && window.WH_GAME.game &&
        window.WH_GAME.game.regionManager) {
```
- `CP.enabled` is the FIRST term of ONE boolean check — when false, JS short-circuits and the ENTIRE pull block (sample scan, verify loop, final want write, record write) is skipped behind this single early-out wrap (block body 2301-2396, closing 2397). Comment 2296-2297: `// Disabled = EXACTLY the pre-change orbit (single early-out, no work).`
- With enabled = false: the sample loop is skipped entirely, no allocation, no state touched, and lastCameraPull is NOT updated (the write 2383-2395 sits inside the wrap; no path outside the wrap writes it — grep: lastCameraPull's writes are all in 2383-2395).
- updateCamera's remaining math is byte-identical to the pre-change orbit (V12's identity read of 2399-2409, plus the pre-`want` baseline identity from V11a) — the disabled path reduces EXACTLY to the pre-change math. Spec 74-75's "must reproduce the pre-change math exactly (single early-out, no allocation)" holds.
- No half-executed path: the broadphase-equivalent scan (the only pre-computation, 2303-2309) sits INSIDE the wrap; nothing runs then bails on enabled=false.

### V28 — Consumer regions untouched (negative) — PASS
- (a) pushOutCircles body byte-identical — full body quoted in V9 above (575-590), including the dead-centre +x fallback (`if (d < 1e-6) { dx = 1; dz = 0; d = 1; }` 584).
- (b) Both consumer paths call the SAME accessor with the SAME activeId pattern and iterate .circles the same way: player push-out via pushOutOfProps → `this.propColliders(this.logic.activeId).circles` (1868-1869; game.js callers 1324 and 2261 unchanged); the per-region circles consumer (`var table = self.propColliders(rid);` 1900, listing exempt 1901-1904 + circles spawn test 1905-1912) unchanged. No consumer code changed AT ALL; no consumer newly reads h/fy/r differently (the only h/fy readers in the repo are the producer's attach lines and the NEW pull block).
- (c) The exempt array's PRODUCER unchanged (519 — V8d's byte-match), and `exempt` does not exist in player.js CODE (V17: comment-only hits 2295-2296).
- (d) CONFIG.js region rows byte-identical — V4's spot-diff plus the valspec's value anchors all matched (cfg.props/enemies/scatter rows untouched; h/fy attach happens INSIDE whPropColliders only, never by editing CONFIG rows).
- (e) Terrain rows (CFG.regionC.terrain) untouched — read 824-890 in full: every key byte-matches the valspec anchors (`camMinAboveGround: 0.8` 886, `propFootR: 1.2` 887, plus pocket/stonePad/rim/notches/climbFactor/etc. all as anchored).
- ALSO VERIFIED: the game.js clampPlayerToBounds body (1316-1332) is untouched (plane+rim clamp, then `rm.pushOutOfProps(player.pos, CFG.player.radius)` 1324, then re-clamp, then door/notch holds — all as R5 P0-5 left it).

### V29 — Files/conventions touched (negative) — PASS
- The sweep grep 'cameraPull|lastCameraPull' over all of prototype (every js/*.js + index.html) hits EXACTLY THREE files: CONFIG.js (2960-2967), region-manager.js (comment 2962's CONFIG-side twin 459's key name usage + the new helpers' comments — region-manager's hits are the trunkTopFrac read 459 and the P1-4a comment banners), and player.js (29-51, 179, 2291-2396). NO new file, NO fourth touched js file, NO touched html (index.html: zero 'pull' hits, zero script additions — V11d). The spec's "Files" section names exactly these three.
- var/function style only: the new code is `var` declarations + `function` declarations (whOccluderH 457, whPropFootY 470) + object literals; NO arrow functions, NO const/let, NO ES import/export anywhere in the new code (and V1's parse + the file-level convention holds — the files remain IIFE + window globals).
- No new window global from the pull path: player.js's only window write is the pre-existing `window.WH_Player = Player;` (2467); `lastCameraPull` lives on the Player INSTANCE (179 `this.lastCameraPull = null;`, written per-frame onto the instance) per design 6, NOT on window. (The pull block reads the PRE-EXISTING window.WH_GAME — no new global created by it.)
- No new comment block redefines C14 taxonomy or invents terms: the new comments quote the existing C14 language verbatim ("C14 classification", "trunk-dominant", "canopy leaves are brushable", "solid mass", region-manager 452-456 / 526-527 / player.js 2291-2297) and cite the io spec paths; no new taxonomy term is coined anywhere in the touched hunks.

---

## Cross-AC coverage map (verified — every AC covered)

| AC | Checks | Status |
|----|--------|--------|
| A1 (`node --check`, orbit math, counts) | V1, V2, V18–V22, V26, V9b | PASS |
| A2 (player.js confinement + preservation) | V10–V16 (V13 cross-checks A2; V14–V15 A6 overlap) | PASS |
| A3 (region-manager h/fy confinement) | V5–V9 (+ V9b) | PASS |
| A4 (CONFIG keys + false path) | V3, V4, V27 | PASS |
| A5 (exempt inheritance) | V17 (+ V9b-i producer evidence) | PASS |
| A6 (zero per-frame allocation) | V14, V15 | PASS (two IO-flagged readings, see notes) |
| A7 (band edge cases) | V24, V25, V26 | PASS |
| A8 (pull geometry, bounded verify, lookAt) | V12, V21 (+ V14 record anchors) | PASS |
| Negatives (untouched regions/files) | V2, V13, V28, V29 | PASS |

## Evidence anchors for every FAIL: (none — 0 FAIL)

## IO rulings needed (non-blocking; PASS-with-notes basis)

1. **V18 sample-grid variant (the substantive one).** The valspec's V18 PASS line prescribes `t = (i + 0.5)/N` for i = 0..N-1 and names "(i)/N or (i+1)/N variants" as FAIL triggers. The built loop samples `t = CP_K / CP_N` for CP_K = 1..N (player.js 2310-2311) — exactly an (i)/N-style grid: {1/N .. 1}. It satisfies the two HARD properties the check exists for — N evenly spaced probes, and t = 0 (the TARGET end) never sampled — but it samples the far end t = 1 where the spec's grid stops at (N−0.5)/N. Consequences: the want point itself is a probe (the far-end block is detected at full distance), and the retreat floor for a first-blocked FIRST sample is t=0 → camMinDistance (same in both grids). Functional difference vs the spec grid is limited to near-the-want detection geometry; the retreat law and the floor are identical. IO should either bless the (i)/N grid or require the (i+0.5)/N loop rewrite (`CP_TT = (CP_K - 0.5) / CP_N`). Flagged, not silently passed.
2. **V14 record-shape names**: built record `{ enabled, activeId, t, tClear, dist, effDist, y, sampleCount }` vs design-6 `{ blocked, wantDist, effDist, t, circles }` — substance-complete mappings (blocked encoded by write-gating `CP_I >= 0`; wantDist→dist; circles→sampleCount), but `sampleCount` counts SAMPLES (CP_N), not circles-as-in-circles-tested. IO to confirm or rename (a trivial patch: set `CP_REC.sampleCount = CP_CIRCLES.length` or add a `circles` field — but as-is the debug consumer (window.WH_DEBUG.game.player) should be told the field's meaning).
3. **V15 one-time lazy-init literal**: the record's `{...}` (2383-2386) is the block's only allocation — first enabled frame with a block found; steady-state per-frame allocation is zero (field mutation only; V14c/V15c hold). If IO wants the literal no-`{`-anywhere reading enforced, the compliant patch is initializing the record in the Player constructor (179) — then no allocation exists on ANY enabled frame.
4. **V21's 0.85-vs-0.5 step factor**: spec 60-61's "step factor 0.85" is realized as verification-step halving (CP_SHRINK = 0.5, comments cite "spec 66-68 + 70"); the 0.15-per-violation decrement does not appear. Per the valspec V21(d)'s own instruction this PASSES with the pairing flagged — IO to confirm the built reading (bounded 2-step midpoint shrink toward target, tClear ≥ 0 maintained by construction) satisfies (b)(c) as intended.
5. **V20 broadphase absence**: the spec's optional-shaped single-sqrt broadphase skip is not implemented; the per-sample radial test uses squared distance (cheaper than the broadphase's sqrt for the no-hit case) so no per-frame cost law is threatened; correctness untouched (V19's exact test is the sole decider). IO may accept the simpler exact test or ask for the additive broadphase patch.
6. **V6 posts-row h**: forecourt posts carry h = nativeHeight × scale (solid-class law) NOT heightM — blessed by V22(c)'s wording; recorded so the h-law table is unambiguous: WHM on wall segments/legs/plugs/fences/p.wall; native height on posts and all solid props (471-472's whOccluderH else-path).
7. **minFloor has no code reader today** (V26 note): the key exists in CONFIG exactly as specced; the pulled want is floored by camMinDistance (2378). If IO intends minFloor as an ADDITIONAL camera-y floor over the ground, that mechanism is not built (no reader); flagging so A7's "minFloor 0.0-0.5" sane-range gate isn't read as implying a consumer.

## Notes / IO rulings summary
See the numbered list above — all are code-read findings on mechanisms the
valspec explicitly marked as note-then-pass (V21(d)) or on naming/perf
deviations that touch no PASS clause's substance (V14/V15/V20/V26). None
changes gameplay math: the block/pull/band/floor/lookAt laws and the count/inventory
preservations all verify.

---

## VERDICT: PASS-WITH-NOTES
- 30/30 checks PASS as executed (V1..V29 + V9b); 0 FAIL; 0 SKIP.
- The diff implements the spec's design faithfully: CONFIG block exact, h/fy attached at every construction site with the heightM/trunk-frac/footY laws, consumer defaults 12/−6, exempt inheritance via circles-only iteration, zero steady-state per-frame allocation, disabled path = byte-identical legacy math, all counts/consumers/rows preserved.
- The five notes above go to IO for confirmation; none is a spec PASS-clause
  violation on its own terms, and each names its compliant alternative patch.
