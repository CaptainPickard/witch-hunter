# CC-B2 — Gate Forecourt: Iron-Fence Runs + Paired Lantern Posts
Spec owner: IO. Date: 2026-11-07. Branch: feat/world-visuals (worktree /tmp/wh-worldfeat).
Source: docs/planning/61-world-audit.md P1-3 (physical sub-lane only — crossfade /
ground-split deferred). Journal-designated lane for wake 35.

## Context (read first)
Round F (already shipped) built the world boundary: vine-stone wall ring + chord
along z=-25, b3Gate arch over the chokepoint (0,-25), 1 hung lantern under the
apex, all as a seeded pure plan (whWallPlan) rendered in buildWorld into a
persistent world group. Colliders feed both regions via whPropColliders(...
wallPlan()); light sockets feed game.js via worldSockets() -> pool handoff.

What is still missing vs doc 61 P1-3's "visible wall" ask: the arch mouth reads
naked at grade level — no iron-fence runs tying the arch into the wall line, no
lit lantern posts flanking the approach. This unit adds exactly that dressing,
world-level, additive only.

## Art anchor (Nicko law)
- art-direction/concepts/concept-01-darkwood.png (boundary mood; single amber
  accent, fog-lifted bases)
- art-direction/concepts/scene-04-toll-bridge.png (threshold grammar: fences as
  leading lines into the gate, oxidized dark iron)
- art-direction/concepts/char-07-gravedigger-undead.png (graveyard lantern mood)
Palette law: charcoal/slate base, oxidized iron, ONE amber accent family — the
existing light pool color CFG.lightPool.color (0xffc27a) and the existing
lanternPost socket params. No new glow colors. No new assets.

## Assets (on disk, both already used in shipped rounds)
- ironFenceSection (church-kit, C13b scale law: 1.35)
- ironFenceCorner (church-kit, terminus pieces)
- lanternPost (church-kit v3, existing scale 2.535; socket row exists in
  CFG.lightSockets.lanternPost)

## Changes
1. CONFIG.js — extend CFG.boundaryWall with a `forecourt` block:
   fence: { asset: 'ironFenceSection', cornerAsset: 'ironFenceCorner',
            scale: 1.35, z: -22.9, fromX: ..., toX: 20.0, overlapM: 0.05 }
   posts: [ { asset:'lanternPost', x:-6.2, z:-20.5, rotY:0, scale:2.535 },
            { asset:'lanternPost', x: 6.2, z:-20.5, rotY:0, scale:2.535 } ]
   fromX is NOT hardcoded: whWallPlan computes it at plan time as
   max(CFG.boundaryWall.chordFromX, plan.arch.halfWidth + 1.2 + clearM) with
   clearM = 0.7. (Reason: chord wall + arch geometry already occupy the plane;
   the fence must start outside the arch pillar face, never inside it.)
   All tunables in CONFIG; no magic numbers in region-manager.js.
2. region-manager.js — extend whWallPlan with ONE new seeded section:
   - stream layer 'wall:forecourt' (seed ^ hash), draws taken BEFORE any
     exclusion test (existing butt-discipline law).
   - Fence: per side (sd in [1,-1]) instances along z=-22.9, from computed
     fromX to toX, step = span/nc after nc = ceil(span/(sectionLen - overlapM));
     sectionLen derives from the loaded meta width * scale, like the chord does
     with segmentLengthUnits. rotY set so the section runs along X (the section
     length axis is its local X; mirrored side keeps the ivy/detail facing).
     Last piece on each side is the corner asset as terminus (counts reported).
   - Posts: 2 fixed placements from CONFIG, plus colliders, plus sockets.
   - plan.segments entries carry {asset,x,y:0,z,rotY,sx,sy,sz} (per-axis scale
     supported since Round F) and ride the EXISTING generic instancing loop in
     buildWorld (no new mesh-building code, no new draw path).
   - Colliders: every fence piece, corner, and post goes into plan.colliders
     via colliderRadius() (posts/fences are NOT trunk-class -> full footprint).
     whPropColliders already merges plan colliders -> no plumbing changes.
   - Sockets: post sockets { id: 'lanternPost@forecourtE/W', x,y,z, intensity:
     CFG.lightSockets.lanternPost.intensity, weight: 1 }. y computed from meta
     height * scale * CFG.lightSockets.lanternPost.heightFraction (ground-level
     base, posts sink 0.05 like others if that is the wall convention — follow
     the existing post handling in CONFIG props; ground stack math is
     computeFireSockets's for CONFIG props, but WORLD sockets carry explicit y
     per b3Gate precedent: y = height*scale*heightFraction, offset [0,0]).
   - Corridor law: fence pieces and posts are skipped when
     whMeetsCorridor(x, z, colliderR) returns true (the passable lane stays
     empty). Report skips in stats.
   - stats extensions: fenceE, fenceW, fenceCorners, posts, forecourtSkips.
     Existing stats MUST NOT CHANGE (ring/chordE/chordW/archLegs/archPlugs/
     doorGap counts identical to pre-patch values — the section is additive and
     runs after them; ring/chord/arch/door draws are untouched).
3. Marker: add 'CC-B2' marker string consistent with how CC-B1 landed its
   marker (build title stamp stays automatic via tools/build_v8.py).

## Hard limits
- NO behavior changes: door logic, enemy spawns, player, corridor width,
  colliderCorridorHalfDepth, fog, and lighting code UNTOUCHED. No asset JSON /
  GLB changes. No new assets.
- No changes outside: CONFIG.js (boundaryWall block), region-manager.js
  (whWallPlan +, if strictly needed for stats logging, nothing else), this
  spec, valspec. If buildWorld needs zero changes (it should — generic loop),
  keep it that way.
- NO-GIT clause: children NEVER push. IO commits.
- No harness runs, no headless browser smoke tests. Pure-plan verification via
  node probe (precedent: scratch/cc13b_probe.cjs stubs meta and calls the pure
  function) is CODE QA and allowed.

## Acceptance criteria
A1. node probe of WH_WallPlan (meta stubbed) shows: fence segments present on
    both sides starting at x >= archHalfWidth + 1.2 and ending at toX=20 with
    corner termini; both posts present; fence/post colliders in plan.colliders;
    2 new sockets in plan.sockets with intensity == CFG.lightSockets.lanternPost
    .intensity; no socket/collider within whMeetsCorridor footprint.
A2. Two consecutive probe runs produce byte-identical plans (pure, seeded).
A3. Pre-patch vs post-patch plan diff: ring, chordE, chordW, arch, doorArch,
    archLegs, archPlugs counts and their segment coordinates IDENTICAL
    (additivity proof).
A4. python3 tools/build_v8.py succeeds; CC-B2 marker present in
    prototype/builds/v8-playable.html.
A5. grep audit: no edits outside CONFIG.js / region-manager.js / docs.
A6. Nicko's playtest is the acceptance bar — NO automated playability claims.
