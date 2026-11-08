# CC-C5 · Wolves of the Old King — packs, loops, cohesion, pack aggro (R-62.7-adjacent, doc 62 §5.1)

Change-order brief, written 2026-10-08 by IO from docs/planning/62 §5.1
(wolf pack law), docs/planning/63 CC-C5, and the wolf asset lane
(intake 69fbab4 + rig rounds fc01956/1a4e13c). NO placeholder body — the
rigged wolf ships WITH this order.

## 0. STATE (verified 2026-10-08 @ 06918bc; re-verify anchors - they drift)

- TIP: 06918bc (asset-pipeline loader fix) — the magic/classes lane landed
  AFTER the wolf rig: class system (S1-S6 commits f8a75c3..9f17440),
  daggers (6b1b5b0..b31de8c), caster variant (bcbb227), loader timeouts
  (a32d5f6..06918bc). Worktree clean, origin equal (verified host-side).
- WOLF ASSET LANED AND RIGGED (do NOT use a placeholder):
  - art-direction/3d/assets/races_regen/rigged/wolf.rigged.glb (raw-color
    rigged) + wolf.rigged.pixelated.glb (512px 5-bit; texture-swap-in-place:
    mesh/skin/clips byte-identical to the rigged file).
  - 21 joints; clips EXACT names: WH_Wolf_Idle (3.0s), WH_Wolf_Walk (1.0s),
    WH_Wolf_Run (0.55s), WH_Wolf_Attack1 (0.7s), WH_Wolf_Hit (0.4s),
    WH_Wolf_Death (1.1s, ends prone).
  - The model spans raw y -0.593..+0.596; paws at y=-0.593 (the rig's
    ground line - the groundMinY pin machinery handles it, verify).
  - Facing: head toward -Z in model space (imported orientation was
    verified in the rig round: nose at negative z).
- MANIFEST: assets.js currently lacks wolfBody. CHARACTERS registry
  (assets.js ~:176): { playerBody: 43, banditBody: 6, ghoulBody: 6,
  playerDagClips: 9 }. Adding wolfBody: 6 (the six WH_Wolf_* clips).
  MANIFEST row: 'art-direction/3d/assets/races_regen/rigged/wolf.rigged
  .pixelated.glb'.
- ENEMY MACHINERY (the seams this order touches):
  - Enemy(type, scene, homeRegionId, spawnX, spawnZ) (enemy.js ~:42);
    homeRegionId, cfg = CFG.enemy[type] via ai1For(enemy) (~:26-27).
  - Region-manager buildRegion spawns CONFIG rows (~:1784-1798):
    var bodyName = e.type === 'bandit' ? 'banditBody' : 'ghoulBody' - THIS
    TERNARY IS THE TYPE-TO-BODY MAP; generalize it (CONFIG.enemy[type]
    .body or a config map). eScale via groundHeight/groundMinY pin.
  - per-region persistence: dead stay dead via st.enemies[k] ('dead' ->
    hp 0, setFsm('dead'), deadFall 1) - pack machinery must be DERIVED
    state, not persisted, so a partial-kill + region-swap + return rebuilds
    pack state cleanly (derive pack membership from the alive/dead enemy
    list at build time).
  - anim: WH_CharacterAnim(meshRoot, getClips(bodyName),
    { variant: 'zombie'|'bandit' }) (~:95-99) - wolf clip-name family is
    DIFFERENT (WH_Wolf_*); anim.js VARIANTS (~:41-78) swap clip names per
    state with MODE_FALLBACK. Check anim.js's NAME mapping: enemy code
    seeks actions by state (walk/chase/attack/death); the CharacterAnim
    NAMES map owns the translation. EITHER add variant 'wolf' to
    VARIANTS mapping the 6 states to WH_Wolf_* names, OR name-normalize at
    getClips - PICK ONE, declare it, keep MODE_FALLBACK semantics.
  - CONFIG.enemy rows (bandit ~:1343, ghoul ~:1387): hpMax/moveSpeed/
    chaseSpeed/attackDamage/attackRange/attackCooldown/sightRadius/
    leashRadius/staggerTime/radius/aggroPingInterval/attackPhase{windup,
    active,recover,hitArcDeg,trackDegPerSec}/ai1{decisionSeconds,always
    KnowsRadius,strafeBandInner/Outer,strafeSpeedMult,strafeDirFlipSeconds,
    attackRadius,attackBias,guardChance,guardRespondRadius,guardSecondsMax,
    guardArcDeg,guardDamageMult}. Ghoul ai1 = { guardMode: 0 } (zombie
    law: every AI1 branch skips).
  - AI1 landed shapes (ai1For, decision loop, strafe band, guard posture) -
    wolves REUSE these exact shapes (doc 62 §5.1 hunt pattern).
  - drops: game.js stores a CONFIG.drops roll on the corpse (S4); enemies
    do not carry per-type drop tables yet - wolf drops = CONFIG.drops as-is
    this order (per-type drop tables are a later order if wanted).
  - damagePlayerFromEnemy -> player.resolveIncomingHit (game.js ~:1314);
    fromDir arc conventions live there - wolf lunges ride the same route.
  - enemy death: corpseFinalY seam (CC-C4 landed: corpses settle on
    terrain, enemy.js ~:160-170).
  - LIVE-ENEMY GROUND FEED (deferred from CC-C4, LANDS HERE): enemy.js
    ~:416/445/483 put LIVE enemies at y=0. Wolves must walk the hills:
    root.position.y = groundY(rid, x, z) each frame for home regions with
    terrain (WH_GROUND.has(homeRegionId)); A/B enemies stay exactly as
    today (0). ADDITIONALLY the idle-pose re-level line ~:483 re-levels to
    the bounding box - verify it does not double-apply with the body pin;
    if it does, feed it through the same ground term (guard per-region).
    KEEP the change minimal: a per-enemy helper in region-manager passed
    down, or a WH_GROUND read inside enemy.js guarded by homeRegionId -
    pick the seam that touches least.
- TERRAIN GEOMETRY (CC-C4/C4b landed): C walkable ground has hills
  (wh-ground.js B-TRI), cliffs ring at r~240 beyond the mountain foot, 4
  road notches + south valley. Wolf packs patrol INSIDE the playable disc
  (their loops must respect the radial clamp; clampEnemyToHomeSide already
  generalizes per-conn + home disc center CC-C2/C4).
- DANGERS TO A/B (acceptance): A/B enemies spawn/aggro/leash byte-identical;
  the type-to-body map change must not break bandit/ghoul (verify both
  still spawn with their existing clips); anim.js variant changes must not
  touch the bandit/zombie/caster variants.

## 1. THE ORDER (Nicko's binding design from doc 62 §5.1 + this session)

- WOLF TYPE (CONFIG.enemy.wolf row; all PROPOSED, Nicko tunes):
  hpMax 38, moveSpeed 4.6, chaseSpeed 7.5 (fastest enemy; wolves are
  pursuit predators), attackDamage 9, attackRange 2.1, attackCooldown 1.2,
  sightRadius 15, leashRadius 40, staggerTime 0.25 (light), radius 0.6,
  aggroPingInterval 0.2, attackPhase { windup 0.35, active 0.10, recover
  0.45, hitArcDeg 45, trackDegPerSec 220 }, ai1 { decisionSeconds 0.35,
  alwaysKnowsRadius 4.0, strafeBandInner 2.6, strafeBandOuter 6.0,
  strafeSpeedMult 0.8, strafeDirFlipSeconds 1.4, attackRadius 2.1,
  attackBias 0.7, guardChance 0.2, guardRespondRadius 5.0, guardSecondsMax
  0.8, guardArcDeg 45, guardDamageMult 0.5 }.
  Wolf attack = the Attack1 lunge-bite clip (0.7s): map attackPhase onto it
  (windup = rear shift, strike = the snap).
- PACK SYSTEM (js/enemy-pack.js NEW, or enemy.js additions if containment
  favors it - pick one, declare):
  - PACK definition: CONFIG.enemy.wolfPacks = [ per-region pack rows:
    { regionId: 'forest_of_the_old_king', waypoints: [[x,z],...], members:
    4, spawnSpread: 6 } ] - 3 PACKS placed per doc 62's L7/L8/L9 lanes
    (north woods, east woods, west woods; pick waypoint loops that cross
    the roads deliberately - R-62.7 road geometry; A5 checks it).
  - CLOSED-LOOP PATROL: each member walks the waypoint loop (WH_Wolf_Walk
    while on patrol; WH_Wolf_Run only while chasing); member offsets phase
    along the loop so the pack spreads; loops use the landed walk-block
    movement (not teleport).
  - PACK COHESION: centroid = mean of ALIVE members' positions; any member
    beyond leashFromCentroid (PROPOSED 26m) abandons its current goal and
    regroups toward the centroid (Run) until within regroupRadius
    (PROPOSED 12m). Nobody aggroes while > X from the pack (solo-pull
    refusal, doc 62: "nobody solo-pulls").
  - PACK AGGRO (BINDING): when one member enters combat (aggro event), ALL
    alive members within packAggroSpread (PROPOSED 40m) enter combat on
    the same target. The pack FSM carries: patrol / regroup / hunt. When
    combat ends (player dead/leashed/left), members return to the loop and
    resume patrol phases.
  - NIGHT BOLDNESS: sightRadius *= nightBoldnessMult (PROPOSED 1.5) while
    game.dayNight reads phase night ('night'); dawn/dusk/day = 1.0. Uses
    the landed clock predicate ONLY (no new state).
  - RELAY LUNGE: at most membersInFlight (PROPOSED 2) wolves in their
    attack windup simultaneously; the rest orbit in the strafe band until
    a slot frees (this is the doc 62 "one commits, others circle").
- WOLF BODY WIRING:
  - assets.js: MANIFEST.wolfBody + CHARACTERS.wolfBody = 6.
  - region-manager.js: generalize the body-name ternary to a CONFIG map
    (enemyBodyByType or per-enemy-row body field), wolf -> wolfBody.
  - enemy.js/anim.js: wolf variant (WH_Wolf_* name family) with MODE_
    FALLBACK; the six states map: idle->Idle, walk/patrol->Walk,
    chase->Run, attack->Attack1, hit->Hit, death->Death.
  - Ground feed: live enemies on terrain (Section 0).
- SPAWNS: 3 packs x 4 wolves = 12 wolf rows (CONFIG enemy rows carry
  packId; region C enemies array; enemies array rows gain packId +
  optional waypointPhase). Wolf rows are REGION-C-ONLY. A/B arrays
  byte-identical.
- NOT TOUCH: magic/classes lane (S1-S6), dagger lane, player.js combat,
  camp/daynight/save, A/B enemy rows (byte-identical), doc 62/63 numbers.

## 2. SCOPE CONTRACT

TOUCH: prototype/js/CONFIG.js, prototype/js/enemy.js, prototype/js/
region-manager.js, prototype/js/game.js (aggro plumbing + spawn map
generalization ONLY), prototype/js/anim.js (wolf variant), prototype/js/
assets.js (manifest + CHARACTERS ONLY), prototype/builds/v8-playable.html.
NOT TOUCH (read-only): player.js, camp.js, daynight.js, save.js, spells.js,
inventory.js, leveling.js, index.html, style.css, docs/* (except none),
io/* (except none), art-direction/* (NONE - the rig is done), tools/*.
CRG IMPACT (baked per law, run 2026-10-08 @ 06918bc): impact --files
enemy.js CONFIG.js region-manager.js game.js anim.js --depth 2 --max-results
10 -> 183 nodes directly changed, 0 nodes impacted within 2 hops,
0 additional files affected.

## 3. ACCEPTANCE CRITERIA (Nicko playtests; A1-A7)

- A1 PACKS PATROL: three wolf packs patrol their loops in C (4 wolves
  each, spread out, walking); loops cross the King's Roads; nobody clips
  hills (they walk ON terrain), nobody climbs cliffs.
- A2 COHESION: aggroing a straggler refuses the pull until packmates are
  near; the pack moves as a group; stragglers left behind regroup.
- A3 PACK-PULLS-PACK: hitting one wolf brings the whole pack (within the
  spread) onto you; relay lunges - they don't all pile in at once, some
  circle while others bite.
- A4 NIGHT: at night they find you from farther away (boldness multiplier);
  at day they patrol calmer.
- A5 THE MODEL: wolves render as YOUR rigged wolf (grey, textured, correct
  ground seating on slopes); Walk on patrol, Run when chasing, lunge bite
  in combat, hit-stagger reacts, death drops it prone and the corpse
  persists; corpse loot rolls the standard table.
- A6 A/B UNMOVED: bandits and ghouls behave EXACTLY as before (spawn,
  clips, AI1, drops); the C door gate, mountains, roads, magic/classes,
  daggers all untouched.
- A7 SAVE/LOAD: kill 2 of 4 wolves, save at camp, load - the 2 stay dead,
  the pack regroups around survivors and resumes the loop.

## 4. PROCESS LAW (standing, unchanged)

- Bundle rebuild (python3 tools/build_v8.py) BEFORE each commit, bundle in
  the same commit; push origin feat/world-visuals after every commit;
  commit identity CaptainPickard. NO harness, NO headless browser, NO game
  run - syntax checks (node --check via
  /usr/local/lib/python3.12/site-packages/playwright/driver/node) on
  edited JS only; IO flips 8793 host-side after gate review (NOT the
  builder). Write to Nicko in English.

## 5. REPORT (final message)

Files changed, syntax results, bundle bytes, commit SHAs + push
confirmations, the A1-A7 self-audit table (one line each, with numbers
where possible: pack spread math, nightBoldness assertion, relay slot
max), and any deviations with measured justification.