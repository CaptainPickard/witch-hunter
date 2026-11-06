# CC-AE1 — NIGHT RAIDS (doc 41 Family 4 raiding parties + doc 34 §6 ambush rules)

IO spec, 2026-11-06, wake 6. Round = the first BEHAVIOR round of the wilderness
layer: a night raid director on the roads of region C. Art anchors (read this
wake, law 1): concepts/concept-05-night-ambush.png (obsidian 0x0A0B10 /
indigo 0x1B1E2B / slate 0x3E424B, moonlight silver 0xC0C8D0, amber lantern
accent 0xFF8C00) and concepts/day-05-ambush.png. The warn cue = the amber
accent beat. No new concept art needed: this lane's anchor exists.

## Source law (quotes verified in docs this wake)

- doc 34 §6 table, Darkwood road patrol NIGHT row: "2-3 Bandits + 1 Rot Wolf".
- doc 34 Night/ambush rules: "Ambush spawn: night agents spawning within 18m
  of an unaware player enter with detection pre-set ... and attack from the
  player's rear arc when the rear arc is not facing them"; "the audio cue
  fires 2.00s before the ambush spawn resolves".
- doc 41 R3 LIGHT TRAFFIC: "night raids come FROM doc 34's night-ambush cap,
  not on top of it"; "1-2 concurrent parties per region".
- doc 41 Family 4: "Raiding parties at clock edges"; "Road life spawns from
  ROUTES, not random points".
- VEIL-TIDE front extension (night tables into dusk/dawn): NOT landed (no
  system exists to hook) - future round, not V1. V1 window = clock phase
  'night' exactly.
- Sight-halving at night / player awareness: NOT landed (no awareness FSM,
  sight halves live as wolf nightBoldnessMult 1.5 opposite flavor, CC-C5
  landed law) - future round, not V1.

## V1 scope (this round ONLY)

At night (phase 'night', clock FREE-RUNNING - dormant boot clock never
triggers; the dormant look IS night, so the gate reads dn.dormant === false),
in region forest_of_the_old_king, away from fires, on roads: a 3-raider party
(2 bandit + 1 wolf, inside the doc 34 night row) spawns 14-17.5 m off the
nearest road centerline, in the player's rear arc, pre-aggroed, after a
2.0 s warning HUD cue. Parties are TRANSIENT (never saved, never in
regionStates), capped at 1 alive / 2 per night, 180 s cooldown after a raid
ends. Composition/health: stock CONFIG.enemy rows, zero stat edits (doc 34
slice locks untouched).

Rear-arc law V1 (disclosed deviation for Nicko's PROPOSED list): the doc
conditions the rear-arc attack on "when the rear arc is not facing them"
(awareness-FSM version). V1 seats the party rear-arc unconditionally at
spawn time (player body yaw P.yaw + PI, jitter ±60°). The doc's conditional
stays future work with the awareness system.

## Files (exact surface; Devbot touches NOTHING else)

1. js/CONFIG.js - ONE new top-level block `raid:` inserted after the roads
   array block closes (after the closing `],` of the C4b notch rows comment
   "Old King's Roads are once again the only roads (CC-C4a geometry intact)."
   ~line 1650, before `boundary:`). All values PROPOSED, Nicko tunes:

  raid: {
    regionId: 'forest_of_the_old_king',
    warnSec: 2.0,                 // doc 34: cue fires 2.00s before spawn resolves
    warnLine: 'Something stalks the road behind you.',
    party: { banditCount: 2, wolfCount: 1 },   // doc 34 night road row (low end)
    spawnBandM: [14, 17.5],       // lateral off road centerline (18m radii law)
    roadSeekRadiusM: 25,          // rear-anchor -> nearest road sample max distance
    rearSpreadDeg: 60,            // rear-arc bearing jitter (yaw + PI +- this)
    seatSlideM: 6,                // per-retry slide along the road when a seat fails
    seatRetries: 3,
    seatMaxSlopeTan: 0.45,        // seat rejection slope (WH_GROUND.slopeTan)
    seatMinPropM: 3.0,            // seat rejection: CONFIG prop rows clearance
    nearFireExclusionM: 50,       // one number everywhere: player-check gate AND seat gate (A-1 evidence)
    notchMouthExclusionM: 26,     // A-1: no seats within this of a branch road's terminal point IN ITS NOTCH ARC (north (0,-596) / east (240,-366) / west (-240,-366)); kingsRoad exempt
    seatMinRoadRenderedM: 14,     // AE1-A: rendered-road distance floor (SWAYED geometry, window.WH_RegionGeom.distToRoad - the road the player sees); polyline fallback only when WH_RegionGeom is absent
    minPlayerDistM: 14,           // AE1-A: seat-to-PLAYER straight-line floor (pop-in guard; worst poly-band case measured 8.96 m with player on a sway bulge)
    stoneRingExclusionR: 40,      // seat rejection radius around the Stone (0, -366)
    checkSec: 20,                 // trigger check cadence while eligible
    triggerChance: 0.25,          // per check roll (debugForce bypasses)
    partiesPerNightMax: 2,        // doc 41 R3: 1-2 concurrent per region; V1 = 2 max, 1 alive at a time
    cooldownSec: 180,             // after a raid ends (wipe or leash-out)
    debugForce: false,            // Nicko dev knob (dayNight.debugTimeScale pattern)
    debugMute: false              // dev knob: silence the state toasts below
  }

   Byte-sacred: roads rows (all), wolfPacks, regionC.enemies, regionC.props,
   enemy stat rows - all byte-identical.

2. js/ambush.js - NEW file (classic IIFE, same house style as cooking.js:
   'use strict', var CFG = window.WH_CONFIG, exposes window.WH_AMBUSH).

   window.WH_AMBUSH = {
     init(game),                 // stores { game } ref; called once by game.js after construction
     tick(dt),                   // called every frame from the game loop (after rm.updateEnemies)
     state(),                    // read-only snapshot { mode, party:n, nightParties, cooldownT } for diagnostics
     pickRaidSeat()              // PURE seat picker (see A-1); no game mutation, no DOM, no RNG misuse:
                                 //   deterministic given game state + Math.random calls made ONLY inside
   }

   Internal state machine: 'idle' -> 'warn' -> 'live' -> ('idle' via cooldown).
   - 'idle': while ELIGIBLE (all gates below), accumulate checkT; on checkSec
     roll triggerChance (or debugForce) -> reserve the party (nightParties + 1),
     pick seat ONCE (locked through the raid), fire the warn cue, mode 'warn',
     warnT = CFG.raid.warnSec.
   - 'warn': warnT -= dt; at 0 -> spawn the party at the locked seat, mode 'live'.
   - 'live': party ends when ALL members are fsm 'dead' (wipe) OR all members
     fsm 'idle' (leashed home) OR any member no longer in rm.enemies[raid.regionId]
     (region rebuild / boundary crossing -> end silently, no toast). On end ->
     cooldownT = CFG.raid.cooldownSec, mode 'idle', party = [].
   - 'idle' + cooldownT > 0: tick it down; gates below never open during cooldown.
   - Dawn (phase leaves 'night'): if mode is 'warn' -> cancel (no spawn,
     refund the party counter); nightParties = 0. A 'live' raid finishes
     naturally (leash does the work); no new spawns after dawn.

   Gates (ALL must hold to enter 'warn' from 'idle'):
     g1 dn.dormant === false
     g2 dn.phase === 'night'
     g3 game.player.state === 'alive'
     g4 rm.logic.activeId === CFG.raid.regionId
     g5 nearest CONFIG banditCampfire row distance (player) > nearFireExclusionM
     g6 cooldownT === 0
     g7 nightParties < partiesPerNightMax
     g8 pickRaidSeat() returns ok:true
     (debugForce replaces g8's RNG-dependent failure? NO: debugForce bypasses
     only the triggerChance roll at check time; seats still must pass.)

   Spawn mechanics (the runtime-spawn grammar, proven by Enemy.prototype.spawnMinion):
     - seat = pickRaidSeat() result { x, z } (player pos AT WARN TIME, locked)
     - for each of party's 3 rows in order [bandit, bandit, wolf]:
         var e = new window.WH_Enemy(type, rm.scene, CFG.raid.regionId, sx, sz);
         e.raidMember = true;
         e.setFsm('chase');            // pre-aggro: doc 34 "detection pre-set", rear arc
         e.yaw = Math.atan2(px - sx, pz - sz);   // face the player (rear approach)
         e.setBody(window.WH_Enemy.makeBody(type));
         if (e.terrainHome) e.pos.y = e.groundY();
         e.root.position.copy(e.pos); e.yawFrame.rotation.y = e.yaw;
         rm.enemies[CFG.raid.regionId].push(e);
         rm.scene.add(e.root);         // parent = scene, same level buildRegion uses
     - raiders carry NO packId and NO CONFIG row: buildPacks never adopts
       them (it reads regionCfg.enemies rows), CC-C5 pack machinery untouched.

   Warn cue: game.inventoryUI.toast(CFG.raid.warnLine, CFG.raid.warnSec + 0.6)
     at warn start (the inventoryUI toast is the HUD layer; works screen-closed).
     debugMute suppresses ALL ambush toasts (validator harness uses it).

   pickRaidSeat() contract (PURE - reads game/player/CONFIG/WH_GROUND only):
     - rear anchor = player.pos + (sin, cos) of (P.yaw + PI) at 12 m
     - seek the nearest sample point on any CONFIG.roads row of
       raid.regionId with .points (kingsRoad, northRoad, eastRoad, westRoad;
       stone rows and notch rows EXCLUDED for seats) within roadSeekRadiusM of
       the rear anchor; none -> { ok: false, why: 'no-road' }
     - seat = road sample + perpendicular-to-road offset, random side,
       magnitude uniform in spawnBandM
     - seat validation (else slide seatSlideM along the road toward the rear
       anchor's road-projection, up to seatRetries): seat not inside any
       branch road's notch-mouth exclusion arc (derived from the road's own
       terminal point, kingsRoad exempt); AE1-A rendered-road floor:
       window.WH_RegionGeom.distToRoad(bestRow, seat) >= seatMinRoadRenderedM
       (the SWAYED render geometry, imported pure - no re-implementation);
       when WH_RegionGeom is missing (harness/node), fall back to the plain
       polyline distance (the old law); AE1-A player floor: straight-line
       seat-to-player distance >= minPlayerDistM; WH_GROUND.slopeTan at seat
       <= seatMaxSlopeTan; every CONFIG.regionC.props row with .x distance >=
       seatMinPropM; distance to (0, -366) >= stoneRingExclusionR; each spawn
       row seat distance to nearest fire row >= nearFireExclusionM
     - returns { ok, x, z, bearingDeg (seat->player vs P.yaw+PI delta, for
       diagnostics), roadId, slide, why? }

3. js/game.js - TWO call sites, nothing else:
   - after the regionManager/dayNight construction is complete (same place
     other init hooks like cooking/camp wiring run): window.WH_AMBUSH.init(game);
   - frame loop, immediately after the rm.updateEnemies(...) call
     (~line 3075): window.WH_AMBUSH.tick(dt);

4. index.html - ONE script tag after the wolf-debug line, BEFORE game.js:
   <script src="js/ambush.js"></script>  (needs WH_Enemy + WH_CONFIG at load;
   uses game refs only at runtime).

5. js/region-manager.js - the ONLY engine edit, ONE guarded line in
   updateEnemies' dead-state record loop (currently:
       if (list[m].fsm === 'dead') st.enemies[m] = 'dead';
     becomes:
       // CC-AE1: raid-member corpses stay TRANSIENT - raiders are not CONFIG
       // roster rows; saving their indexes would inflate regionStates forever.
       if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead';
   Rationale verified this wake: st.enemies is INDEX-keyed against the CONFIG
   roster and restore loops read it at rebuild; appended raiders would poison
   the index space (phantom dead slots, inflated knownEnemies).

NOT touched: save.js, enemy.js (zero edits - spawn grammar used read-only),
daynight.js, wh-ground.js, any art file.

## A-1 pre-spec probe (DONE - ran this wake, evidence in scratch/cc-ae1/)

raid_probe.py + node child ran BEFORE this spec froze. Three probe
iterations, final law evidence:
- v1 (raw band): FAILS — eastRoad notch shoulder 28.5 deg, mossBoulder at
  0.4 m off westRoad, Bravo fire 45.2 m off kingsRoad.
- Amendment A (from v1): nearFireExclusionM unified at 50 (player gate AND
  seat gate); notchMouthExclusionM 26 on the three branch roads' terminal
  arcs (kingsRoad exempt).
- v2 miscounted exclusions as fails; v3 (FINAL) counts them separately:
  kingsRoad PASS 90.2% maxRun 8 / northRoad PASS 93.5% run 6 / eastRoad
  PASS 95.4% run 1 / westRoad PASS 96.3% run 6 -> OVERALL PASS.
- Lock law (validated by Testerbot, same thresholds): per road, over
  eligible seats: passPct >= 90 AND no consecutive eligible-fail run over
  16 offset-seats (2 centerline samples = 8 m; slide depth 18 m covers it).

## AE1-A amendment (2026-11-06, from Testerbot independent verdict 1: FAIL)

Testerbot V-A17 caught a REAL spec flaw (adjudicated blocking by IO):
the seat band was pinned to the raw CONFIG polyline, but roads RENDER
through whRoadLine: Catmull-Rom through .points + sway sideways
(swayAmp 7 kingsRoad / 6 branch, ramped at ends). A seat 14-17.5 m off
the POLYLINE can sit ~9-10.5 m off the road the player actually sees
(and the player can stand a sway-bulge sideways from the polyline).
IO re-measured from Testerbot's harness data: worst = 8.96 m from a
player standing on the rendered road at the arc-28 bulge. That violates
doc 34's ambush frame (rear arc, near-but-not-on-top). Fix (two new
CONFIG gates, both consumed by ambush.js):
- seatMinRoadRenderedM 14: distance-to-RENDERED-road floor via
  window.WH_RegionGeom.distToRoad (the engine's own pure renderer-geometry
  helper, region-manager.js L2139 EXACTLY what the player sees; polyline
  fallback only if WH_RegionGeom is absent in a harness).
- minPlayerDistM 14: straight-line seat-to-player floor (pop-in guard,
  geometry-independent).
Testerbot verdict 1 detail: 32/34 PASS; blocking = V-A17 (this
amendment); V-A30's FAIL was an ORACLE error (asserted a strict-mode
throw that node does not produce); IO re-ran the purity law directly -
digest unchanged before/after the write attempt with the machine live -
adjudicated PASS; the report file was never written (child died at
max_iterations before write_file) so this section carries the verdict.
Ambush.js edit scope for AE1-A: the pickRaidSeat validation chain ONLY
(two reads of CFG.raid + one WH_RegionGeom call + fallback) + the valspec
addendum cases; everything else stands.

## Acceptance criteria

A-1: probe report exists (scratch/cc-ae1/) with the PASS lines above; any
     failing road segment is disclosed, and seat-slide law covers it.
A-2: code lands exactly per the file list (5 files); byte-sacred rows intact
     (diff roads/wolfPacks/regionC.enemies/props/enemy stats = empty).
A-3: node validation harness (Testerbot valspec defines the cases) green
     under node only - NO browser, NO harness runs, NO playtest claims.
A-4: python3 tools/build_v8.py exit 0 in the worktree; v8-playable.html
     carries the round marker (grep -c 'CC-AE1' > 0).
A-5: Testerbot independent verdict PASS -> IO commit (CaptainPickard
     <pickard.nicko@gmail.com>) + push + release flip + served-bytes check.

## Validation guidance to Testerbot (valspec author)

The harness pattern that works on this box: node + globalThis.window shim +
require prototype/vendor/three.classic.js + prototype/js/CONFIG.js +
prototype/js/wh-ground.js (see scratch/cc-c5/loops_probe.js, cc-ed1 site_scan
node child). ambush.js can be LOADED in node (it only reads WH_CONFIG at
load); drive its state machine with a MOCK game object (fake dayNight with
controllable phase/dormant, fake player {pos, yaw, state}, fake regionManager
{ logic.activeId, enemies[regionId] = [] , scene: {} }, fake inventoryUI
{toast: recorder}), and fake WH_Enemy as a record-only stub for the spawn
path (this validator does NOT test Enemy physics - the stock FSM runs every
night already, it is landed code). Assert: gate matrix (dormant/region/phase/
fire/cooldown/cap each blocks alone), seat geometry laws across >= 100 seeded
player poses near each road (band 14-17.5, rear arc, fire/stone/slope/prop
clearances, road excluded rows), warn-order (cue recorded BEFORE any enemy
construct), 2.0 s delay, transient law (raidMember flag present on every
spawned stub and NEVER written to mock regionStates), dawn cancel, cooldown,
per-night cap, and CONFIG purity (deep-freeze WH_CONFIG before tick; any
mutation fails the case).

## Devbot guidance

Worktree /tmp/wh-worldfeat on feat/world-visuals. NO git commands (NO-GIT:
no add, no commit, no push - IO is the sole gatekeeper). Build check is
ALLOWED and expected: python3 tools/build_v8.py from the worktree root.
Art law: pixelated everything, darkwood palette, one accent per frame - the
amber warn toast is the round's accent; NO new materials, NO new models,
NO new light sources this round. Keep the diff at exactly the 5 files above.
