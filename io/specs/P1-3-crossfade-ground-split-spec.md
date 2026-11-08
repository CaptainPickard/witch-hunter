# P1-3 REMAINDER — Chokepoint Crossing Continuity: Fog Crossfade + Ground Split

Spec by IO (wake 37, 2026-11-08). Implements the unclosed half of doc 61 P1-3
(the physical gate/fences half landed as CC-B1/B2). Acceptance metric: M-22
(doc 61: no background pixel step > 3% per frame across a crossing).

Art law (concept-01-darkwood + scene-04-toll-bridge, viewed this wake):
cold slate/indigo fog base, single amber accent; crossing grammar = fog
thickens on approach, curtain at the threshold (the iron gate, scene-level),
reveal on the far side. The crossfade IS that grammar in realtime.

## Grounded facts (file:line, worktree /tmp/wh-worldfeat, branch feat/world-visuals)

- Cross flow: game.js:3160 rm.tickTransition -> applyCross(tr) (game.js:1004).
  applyCross: maps player, applyRegionLighting(tr.newActiveId) (game.js:1374),
  sky variant (1s own fade), banner. Lighting swap today = INSTANT step.
- Fog is re-written EVERY FRAME from day/night state: applyDayNight()
  (game.js:1627) does scene.fog.color.copy(S.fog[rid]) + density, and hemi
  fill = CFG.lighting.hemiBaseIntensity * region.ambientLightLevel
  * (rid===B ? regionBFillMult 1.15 : 1) * S.hemiFillMult (game.js:1635-1640,
  1656-1659). Then cemeteryFogTick() (game.js:1395, ticked game.js:3273)
  lerps region-A graveyard ramp on top. Any tween MUST plug in after
  applyDayNight and before cemeteryFogTick, as a per-frame override.
- Region groups: region-manager.js buildRegion (js/region-manager.js ~1841)
  builds group per regionId; prewarm builds hidden (visible=false,
  group.visible = !hidden at 2039); tickTransition cross handler
  (region-manager.js ~2135) reveals new group + DISPOSES old instantly.
- Ground: A and B share world.groundRadius 90 (CONFIG.js:133); visual radius
  = max(90, ...) (region-manager.js:299-316) => full CircleGeometry disc r90
  centered origin for BOTH regions (region-manager.js:1862-1876). Only region
  C has its own center / y-offset / terrain. A/B boundary plane at
  CFG.boundary.z = -25 (CORRECTED per Testerbot A1 — home A z>=-25 [spawn z=74],
  home B z<=-25 [spawn z=-45]; an earlier draft said 25/A-z-side and is void).
  The two discs are COPLANAR
  (doc 61 audit row 'z-fighting', region-manager.js:293-299,358) — safe today
  only because the old group is disposed at the cross. ANY simultaneous render
  overlaps them in z<=-65..65 => the split is REQUIRED for the crossfade.
- Old-region enemies hang off the old group (group.add(enemy.root),
  region-manager.js:2018); updateEnemies ticks ONLY the active region, so old
  enemies freeze (invisible harm: they sit >= 60m from the plane, fully fogged).
- Boundary wall + iron fences + lantern posts (CC-B1/B2) are added to the
  SCENE, not the region group (region-manager.js:1693) => the gate persists
  across the cross as the physical seam. Leave untouched.
- Region fog rows per phase: daynight.state.fog[rid] exists per region id
  (applyDayNight: var f = S.fog[rid]); the NIGHT row equals the CONFIG region
  constants, so lerping the two regions' rows is phase-correct at night, and
  a mid-fade day/night phase flip just moves the lerp target. Day/night clock
  is frozen while dormant (camp rest), which covers rests mid-fade.

## Design (frozen)

### 1. Chord-cut half-disc ground (A/B only)

- In buildRegion: for a region WITHOUT reg.center (A and B — the shared-disc
  family) replace the full CircleGeometry ground with a half-disc bounded by
  the region's own home half-plane. CORRECTED SIGNS (Testerbot A1, verified
  against CONFIG.js:2807-2811): CFG.boundary.z = -25; region A occupies
  z > boundary.z (A spawn z = 74), region B occupies z < boundary.z (B spawn
  z = -45). So: A-half = { x^2+z^2 <= R_vis^2, z >= CFG.boundary.z },
  B-half = { ..., z <= CFG.boundary.z }. Build via THREE.Shape + absarc +
  ShapeGeometry; half-chord xc = sqrt(R_vis^2 - plane^2) with
  R_vis = whVisualGroundRadius(regionId), plane = CFG.boundary.z (at R_vis 90:
  sqrt(90^2 - 25^2) = 86.46); read plane, R_vis and home side from CFG/
  DEFS at runtime — NEVER hard-code 25 or its sign; remember the rotX(-PI/2)
  mapping world z = -geometry y when deriving arc angles. Skirt/edge
  behavior: the flat texture material stays as-is; edge of the chord sits AT
  the plane line, hidden under the scene-level boundary wall + gate.
- Regions WITH reg.center (C) keep the existing full-disc + offset path
  UNCHANGED. Ground texture, repeat, dirt path (per-region), roads, mist
  plane all keep their existing region gating.

### 2. Crossfade (fog + hemi light), 1.5 s

- New module state in game.js: regionFade = null | {
  t, dur, fromSnapshot, toId } where fromSnapshot = { fogColor: THREE.Color
  clone of scene.fog.color, fogDensity: scene.fog.density, hemiIntensity:
  game.hemiLight.intensity } captured at the cross, toId = new region id.
- Start: in applyCross, BEFORE applyRegionLighting, if the crossing is a
  GATE crossing (tr has no conn.door — den-door crosses keep their black
  dip, forceCross stays untouched), capture the snapshot from the CURRENT
  (old-region) rendered state, then start the fade and SKIP the instant
  applyRegionLighting step for fog/hemi (set them via the per-frame tick
  from the fade instead; region id bookkeeping otherwise identical).
- Per-frame: new regionFadeTick(dt) called in the tick AFTER applyDayNight()
  and BEFORE cemeteryFogTick() (game.js:3272-3273 window). When active:
  w = smoothstep(t/dur); fog.color = lerpColors(fromSnapshot.fogColor,
  S.fog[toId].color, w); fog.density = lerp(from.fogDensity, S.fog[toId]
  .density, w); hemiLight.intensity = lerp(from.hemiIntensity, fillTarget,
  w) where fillTarget = CFG.lighting.hemiBaseIntensity *
  regions[toId].ambientLightLevel * (toId===B ? regionBFillMult : 1) *
  S.hemiFillMult. t += dt; at t >= dur: clear regionFade (subsequent frames
  = the plain applyDayNight path again).
- When no fade is active: regionFadeTick is a no-op (zero code risk to
  non-crossing frames).
- A reverse cross mid-fade (B->A within 1.5 s): restart with a fresh
  snapshot of the CURRENT lerped state (snapshot at fade start is taken
  from scene.fog / hemiLight live values, so this falls out naturally).
- cemeteryFogTick stays last-write for the A-yard ramp; during a B->A fade
  the player is at the plane, ramp weight 0, no conflict.

### 3. Deferred disposal of the crossed-out region

- At the gate cross: DO NOT disposeRegion(oldId) in the tickTransition cross
  handler; keep the old group visible (it carries the old half-disc + props,
  which render fogged silhouettes under the lerping fog exactly per the
  audit's "show the neighbour" intent — note the OLD region is the one on
  screen at cross start; the pre-warmed NEW group is revealed as today).
- The pending old id is stored (a single regionFade.pendingDispose on
  game.js is fine; document the exact holder in the code comment). When
  regionFadeTick completes the fade, it calls
  game.regionManager.disposeRegion(pendingDispose) + disposeHiddenExcept(null)
  (same hygiene as today's cross handler).
- Death/respawn switchTo and forceCross (den) paths keep today's instant
  swap + dispose (explicitly out of scope; the den has its own dip fade).
- Enemy/HUD safety: old enemies are not ticked during the fade (frozen
  statues, fogged at >=60m); enemy HP bars and clamps all read the new
  active id exactly as today.

### 4. CONFIG

- CFG.sceneFade = { durationSec: 1.5 } (new small block, CONFIG.js, near the
  preWarm block CONFIG.js:2893). All magic numbers flow from it. Build marker
  (pinned by valspec A2): every round must leave the literal string
  WH_P1_3_REGIONFADE_V1 present in prototype/js/game.js AND in the built
  prototype/builds/v8-playable.html.

## Acceptance criteria (Testerbot verdict basis)

1. Pure-logic checks (node, no browser): smoothstep w curve is 0 at t=0,
   1 at t=dur, monotone; the fog lerp endpoints equal S.fog rows of both
   regions at night (row == CONFIG constants); half-chord xc = sqrt(90^2-25^2)
   = 86.46 (86.5); arc-angle math produces a shape whose winding covers the
   home half (assert via a point-in-shape spot test on constructed numbers).
2. Code-walk: applyCross gate path starts a fade with a live-state snapshot
   and does not step fog/hemi; day/night + cemetery ordering is exactly
   applyDayNight -> regionFadeTick -> cemeteryFogTick; dispose of old region
   happens only at fade completion; C, forceCross, switchTo paths untouched.
3. Budget: the added per-frame work when fade is inactive is a single null
   check; when active: one color lerp + two scalar lerps + one dispose at end.
4. No new globals beyond the documented module state; no harness; no browser.
5. Build: tools/build_v8.py runs from the worktree; v8-playable.html contains
   the new marker string agreed on dispatch (regionFade implementation must
   be in the built bundle, not an external file).

## Law reminder for children

- Worktree /tmp/wh-worldfeat, branch feat/world-visuals. Children NEVER run
  git commit/push (NO-GIT). No harness runs. No headless browser smoke tests.
  Art law: palette from concept-01/scene-04 (cold slate fog, amber accent);
  this is a mechanics pass — no new art required.
