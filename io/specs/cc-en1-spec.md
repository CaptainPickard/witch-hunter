# CC-EN1 — Wilderness Encounter Tables V1 (doc 51 Section 2; regionB director + both live-biome tables)

IO spec, 2026-11-08. Gate order: this spec -> Testerbot valspec -> Devbot build ->
Testerbot verdict -> IO commit+push. Worktree /tmp/wh-worldfeat (feat/world-visuals).
Children NEVER git-commit or push (NO-GIT clause). Art anchors (law 1, vision-QA'd
this wake): concept-02-moors (silhouette-first, fog-emergence, warmth scarce = camp
safety law) + concept-05-night-ambush (pack flanking, numbers hidden until close =
seat/density law). Law 2: NO browser smoke checks; validation is static + node.

## 0. Scope

Doc 51 §2 authors per-biome wilderness encounter tables. TWO live regions exist:
darkwood_edge (regionB) and forest_of_the_old_king (regionC). regionC's night road
life is ALREADY implemented (CC-AE1 night raids, js/ambush.js, serving). This round:

1. AUTHORS the §2 tables as CONFIG data for BOTH live wilderness regions
   (CONFIG.encounters.biomes.darkwood_edge + .forest_of_the_old_king), every row
   mapped onto the LIVE enemy kit (bandit / ghoul / wolf / coven). No new enemy
   types, no new combat mechanics (doc 51 scope note: it invents no mechanics).
   §2 rows naming not-yet-built machinery (barrow wights, drowned dead, hag-pool
   beasts, blockhouse garrisons, pilgrim carts) are NOT invented — they become
   table metadata notes (pending: 'x'), keeping the doc's rows visible without
   fabricating enemies.
2. IMPLEMENTS a night encounter director for darkwood_edge ONLY:
   js/encounters.js, window.WH_ENCOUNTERS. regionC keeps AE1 (its table rows are
   the data record of what AE1 already rolls; no second director there).
3. Deliberate scope cut: DAY rows change nothing in this round — regionB's day
   stays the static CONFIG roster (doc 51: "a good player's night is the
   dangerous half"; dens Family 1 day pairs are authored-at-C data). Declared,
   not silent.

The round is ONE new module + ONE CONFIG block + 3 engine wiring lines. Art law:
no new materials, no new meshes, no new lights — spawn bodies reuse
Enemy.makeBody; the amber warn toast (inventoryUI.toast, works screen-closed) is
the round's ONE accent, same as AE1.

## 1. CONFIG.encounters block (data)

Sibling of CONFIG.raid (placed after the raid block in CONFIG.js). One global
block; the only file touched besides encounters.js/game.js/index.html is CONFIG.js.

```
window.WH_CONFIG.encounters = {
  enabled: true,
  director: {
    regionId: 'darkwood_edge',
    checkSec: 20,
    triggerChance: 0.25,
    cooldownSec: 180,
    partiesPerNightMax: 2,
    warnSec: 2.0,
    warnLine: 'Eyes open in the murk of the Darkwood.',
    nightTable: 'darkwood_edge',        // which biome table the roll reads
    seatMinPlayerDistM: 14,
    seatMinPropM: 3.0,
    seatMaxSlopeTan: 0.45,
    nearFireExclusionM: 50,
    spawnSpacingM: 2.2,                 // lateral spacing between party members
    boundaryBandM: 6,                   // keep seats >= this off the z=-25 plane
    nodeM: 2.5,                         // gather-node clearance (scatter.nodeM)
    enemyRowM: 5,                       // static-roster spawn clearance (gather.placement.enemyM)
    spawnBandR: [0.2, 0.72]             // seat radial band = fraction of playable radius
  },
  biomes: {
    darkwood_edge: {
      note: 'doc 51 §2.1 darkwood mapping. Live-kit rows only; rows naming '
          + 'not-yet-built sites are notes, not compositions.',
      pending: { 'F2-tainted-glade-wailcaster': 'gravebound caster pool awaits its kit (doc 51 1.4)' },
      day: [   // DATA ONLY this round (the director never rolls day)
        { family: 3, label: 'wayfinding bandits', comp: [{ type: 'bandit', n: 2 }], tier: 'T1' }
      ],
      night: [
        { family: 1, label: 'lair-edge wolf pack', comp: [{ type: 'wolf', n: 2 }, { type: 'wolf', n: 1 }], tier: 'T1-T2' },
        { family: 2, label: 'bound thrall watch', comp: [{ type: 'bandit', n: 2 }], tier: 'T2',
          note: 'thrall seats = bandit chassis per doc 51 1.4 humanoid-grammar law' },
        { family: 3, label: 'roadless wayfinding', comp: [{ type: 'bandit', n: 1 }], tier: 'T1' },
        { family: 5, label: 'grave ghouls', comp: [{ type: 'ghoul', n: 1 }, { type: 'ghoul', n: 2 }], tier: 'T2',
          note: 'disturbance-spawn only at C; in B the graveyard edge stands in (keepOut chapel is NOT a spawn site)' },
        { family: 8, label: 'war-scar looters', comp: [{ type: 'bandit', n: 2 }, { type: 'bandit', n: 1 }], tier: 'T2-T3' }
      ],
      weights: [0, 0.28, 0.12, 0.15, 0.25, 0.2]   // index 0 = unused slot (1-based family feel)
    },
    forest_of_the_old_king: {
      note: 'doc 51 §2.1 as LIVE in regionC: night road life already rolls via '
          + 'CC-AE1 (js/ambush.js CONFIG.raid = F4 night). These rows are the '
          + 'table record of that live behavior + the F1/F5 rows AE1 explicitly '
          + 'avoids (den mouths, notch arcs). No second director.',
      pending: { 'F1-lair-pair': 'dens are authored C sites; the den-mouth day pair stays site data (doc 41 F1)' },
      night: [
        { family: 4, label: 'night roads (LIVE via AE1)', comp: [{ type: 'bandit', n: 2 }, { type: 'wolf', n: 1 }], tier: 'T1-T2', live: 'cc-ae1' }
      ]
    }
  }
};
```

WEIGHT LAW: weights indexes correspond to the `night` array (0 = family-1 spare
slot so the array stays 1-based-aligned to family numbers); the roll sums
weights[i] for i: 0..night.length and walks cumulative bands. Weights PROPOSED,
Nicko tunes.

COMPOSITION LAW: every comp entry = one member (type, n). A party's comp entries
all spawn. Every type must be in the live kit: bandit | ghoul | wolf | coven.
No comp entry may exceed 3 members of one type (doc 34 pack grammar band).

## 2. js/encounters.js (the director)

IIFE module on the chest.js/ambush.js conventions. Only window globals read:
WH_CONFIG, WH_Enemy, WH_GROUND (optional), WH_RegionGeom (optional), WH_GAME via
game ref. Exposes window.WH_ENCOUNTERS: init(game), tick(dt), state(), pickSeat().

State machine: 'idle' -> (gates all pass + checkSec cadence + Math.random roll) ->
'warn' (warnT counts down, amber toast) -> 'live' (party spawns TRANSIENT) ->
(allDead / allIdle / anyMemberGone) -> 'idle' + cooldownT. Night leaving during
warn = cancel, no spawn, no cooldown (AE1 refund law). Night leaving during live =
raid finishes naturally (AE1 law: dawn does NOT interrupt a live raid).

GATES (all must hold to roll):
g1 dayNight.dormant === false
g2 dayNight.phase === 'night'
g3 game.player.state === 'alive'
g4 game.regionManager.logic.activeId === director.regionId
g5 player distance to every regionB banditCampfire prop row > nearFireExclusionM
g6 cooldownT === 0
g7 nightParties < partiesPerNightMax
g8 seat found (pickSeat ok)

SEAT (pickSeat; PURE law shape — Math.random calls confined to this function's
body and tick's roll only):
1. angle = Math.random()*2PI; radius r = playableR * (band[0] + rand*(band[1]-band[0])).
   playableR = CFG.world.groundRadius (90) - CFG.world.playerMargin (1.5) = 88.5
   for regionB (it reads the SHARED disc at the origin). Radial margin does not
   double-count the boundary plane — the plane is predicate p6's job, not another
   radius term.
2. candidate x,z on that polar point.
Predicates (each failure = re-roll candidate, up to 24 attempts, else not ok):
p1 keepOut: the chapel ellipse row { regionId 'darkwood_edge', x 0, z -58, rx 21,
   rz 12.5 } — ((x-x0)/rx)^2 + ((z-z0)/rz)^2 >= 1.15 (outside + margin)
p2 props: every regionB.props row with .x: dist >= seatMinPropM
p3 fires: every regionB banditCampfire row: dist > nearFireExclusionM
p4 player: dist to player.pos >= seatMinPlayerDistM
p5 slope: WH_GROUND.slopeTan(regionId, x, z) <= seatMaxSlopeTan when WH_GROUND
   has the region (else pass)
p6 boundary band: |z - CFG.boundary.z| >= boundaryBandM for A-side... B occupies
   z < boundary.z = -25? NO: CFG.boundary.z = -25, B z < -25 (spawnZ -45). The
   seat must keep |z - (-25)| >= boundaryBandM.
p7 nodes: every regionB.nodes row: dist >= nodeM
p8 roster: every regionB.enemies row: dist >= enemyRowM
p9 ground: y = WH_GROUND.heightAt when present (visual only, no clamp)

SPAWN (spawnParty at warn expiry; the AE1 grammar VERBATIM):
for each comp entry of the ROLLED night row, for n members:
  e = new WH_Enemy(type, rm.scene, regionId, x + i*spacingJitter, z + j)
  where spacingJitter per member = alternating +/- offsets along a random bearing,
  magnitude spawnSpacingM (keeps 5-member worst case inside 2 rings of p2 clearance)
  e.raidMember = true            (TRANSIENT law)
  e.setFsm('chase'); e.yaw faces player
  e.setBody(WH_Enemy.makeBody(type))
  if (e.terrainHome) e.pos.y = e.groundY()
  e.root.position.copy(e.pos); e.yawFrame.rotation.y = e.yaw
  list.push(e); rm.scene.add(e.root)
Party members recorded in S.party. Return count (0 = region list vanished ->
refund + idle).

ROLL: one night row per party. roll = Math.random(); walk cumulative weight
bands; the row whose band holds roll wins. debugForce bypasses ONLY the roll
(seats still validate). debugMute suppresses toasts.

## 3. Engine wiring (game.js + index.html) — the ONLY engine edits

game.js hooks (3 one-line edits, the AE1 pattern):
- init site: next to `if (window.WH_AMBUSH) window.WH_AMBUSH.init(game);`
  add `if (window.WH_ENCOUNTERS) window.WH_ENCOUNTERS.init(game);`
- tick site: next to `window.WH_AMBUSH.tick(dt);`
  add `window.WH_ENCOUNTERS.tick(dt);`
index.html: `<script src="js/encounters.js"></script>` immediately after the
ambush.js script tag (order: encounters.js reads CONFIG at load; WH_Enemy must
exist by tick time — enemy.js loads earlier in the tag order, verified by valspec).

## 4. Acceptance criteria (what Testerbot asserts)

A1. node --check passes on all touched files (CONFIG.js, encounters.js, game.js).
A2. game.js edit surface: exactly the 2 hook lines added; index.html exactly 1
    tag; no other engine file touched (git diff --stat pinned in the report).
A3. Tables complete: darkwood_edge carries family 1,2,3,5,8 night rows + family
    3 day row + F4/F6/F7 pending notes; forest_of_the_old_king carries the LIVE
    F4 row + F1 pending note; every comp type ∈ {bandit, ghoul, wolf, coven}.
A4. Weights: darkwood_edge weights length == night.length + 1, sum == 1.0
    (+-1e-9), weights[0] === 0.
A5. Director gates g1..g8 each provably present in encounters.js (grep anchors
    per gate comment "g1".."g8"); predicates p1..p9 present ("p1".."p9").
A6. Transient law: raidMember assigned at spawn in encounters.js; the region-
    manager dead-state guard skips raidMember rows (the line already exists —
    grep "raidMember" region-manager.js; engine untouched by this round).
A7. Art law: encounters.js contains no `new THREE.PointLight`, no
    `MeshStandardMaterial`, no new geometry constructors beyond reusing
    makeBody-driven instances (grep count 0); exactly one toast accent call.
A8. RNG law: Math.random calls confined to roll + pickSeat bodies (grep: 2
    call sites max, both inside those functions).
A9. Build: tools/build_v8.py run in the worktree produces v8-playable.html in
    which the CC-EN1 marker + encounters.js body are INLINE (build_v8 inlines
    whole files). Determinism: two runs sha-equal.
A10. Serving law held for close-out: build committed BEFORE any playable claim.

## 5. Playtest pointer (for Nicko)

Night (45min) on the Darkwood Edge, away from bandit fires (>50 m): party spawns
14 m+ behind/around with a 2 s amber cue. Worst case 2 parties x 5 members.
All numbers CONFIG-PROPOSED; he tunes CONFIG.encounters.director / table weights
live like CONFIG.raid.

## 6. IO AMENDMENTS (2026-11-08 wake 46, after Testerbot valspec defect report §2.1..§2.9)

EN1-1 (§2.1 accepted): gate greps are documentation anchors only; the valspec's
behavioral gate matrix is the proof. Build carries BOTH (comments g1..g8/p1..p9
kept for human navigation).
EN1-2 (§2.2 accepted): toast law = exactly ONE `function toast` helper; call
sites funnel through it; authorized sites = the warn cue + at most one
end-of-raid line. debugMute honored.
EN1-3 (§2.3 accepted): RNG law final form = all Math.random sites inside ONLY
{ pickSeat, spawnParty spacing-bearing, tick roll }, <= 4 sites total.
EN1-4 (§2.4 resolved): pending notes carry the FULL family story, not one key.
CONFIG.pending maps: darkwood_edge.pending keys F2/F4/F6/F7 (values name the
doc-51 row + why pending); forest_of_the_old_king.pending keys F1/F6/F7.
RegionC note text keeps 'no second director' + cc-ae1. This supersedes §1's
two-key literal.
EN1-5 (§2.5 accepted): SPAWN spacing law (replaces the malformed line in §2):
party members offset from EACH OTHER by alternating orthogonal offsets along a
single random bearing (magnitude spawnSpacingM), keeping every pairwise member
gap >= spawnSpacingM - epsilon and every p2/p3/p4/p6/p7/p8 predicate holding
per-member at the worst 5-member case.
EN1-6 (§2.6 resolved): predicate p6 FINAL FORM (supersedes §2's mid-line
self-correction): the seat must sit on B's side of the plane AND >= band off it:
`z <= CFG.boundary.z - director.boundaryBandM` (i.e. z <= -31). No A-side seats.
EN1-7 (§2.7 accepted): determinism = post-build run-A sha == post-build run-B
sha; NOT compared against HEAD's committed bundle.
EN1-8 (§2.8 accepted): engine surface = 2 game.js lines + 1 index.html tag.
EN1-9 (§2.9 accepted): CONFIG path names in §1 comments are prose; the live
paths CONFIG.scatter.clear.nodeM (2.5) and CONFIG.gather.placement.enemyM (5)
are the values of record (both match the pinned numbers).
