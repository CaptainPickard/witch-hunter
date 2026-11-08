# SPEC — CC-EC1: Coven Acolyte (doc 34 enemy caster + magicDefense hook activation)

Round: CC-EC1, 2026-11-06. Owner: IO (gatekeeper). Branch: feat/world-visuals,
worktree /tmp/wh-worldfeat. Build tool: tools/build_v8.py (newest). Build + commit
BEFORE any playable claim. Children NEVER push (NO-GIT clause). No harness runs,
no headless browser smoke tests — Nicko's playtest is the acceptance bar.

## Concept-art anchor (art law)

- Anchor pieces: art-direction/concepts/char-09-coven-wizard.png (+web twin) and
  char-02-thrall.png. Palette law for ALL new visuals: charcoal/deep-teal robes,
  desaturated earths, ONE accent per frame = cyan magic glow (#4fd8c8 family);
  hostile heraldry reads crimson but NO red on the acolyte frame (the accent is
  the staff orb). Oversized hood, gnarled staff, skull-trinket clutter tell
  "enemy caster" before any spell.
- Magic language: spell light must read cyan (0x4fd8c8 family) — NOT the player
  firebolt orange. Wispy emission, not solid bolts.

## Scope

ONE new enemy type + its one spell + the magicDefense choke activation. This is
a presentation-complete slice of doc 34 (section 5 analog), NOT the full doc-34
perception/taunt/pack rewrite (that is parked as a separate order; AI1 machinery
stays).

### 1. CONFIG (prototype/js/CONFIG.js)

1.1 `CONFIG.enemy.coven` row (append AFTER wolf, sibling of bandit/ghoul/wolf):
    - hpMax: 60, moveSpeed: 3.4, chaseSpeed: 4.6 (slower than bandit 5.0),
      attackDamage: 0 (melee disabled in v1), attackRange: 0, attackCooldown: 0,
      sightRadius: 20, leashRadius: 40, staggerTime: 0.45, radius: 0.7,
      aggroPingInterval: 0.2.
    - attackPhase: windup: 0.55, active: 0.12, recover: 0.85, hitArcDeg: 50,
      trackDegPerSec: 180 (cadence numbers ride a real clock; melee harm is
      0 so active-window harm comes only from the spell tick in 2.2).
    - bodyByType += coven: 'covenBody'; animVariantByType += coven: 'bandit'
      (bandit variant over the chosen rig's universal 6-clip set; anim.js
      universal-name fallback covers the miss — expect ~5 benign anim warns
      per coven body, death name IS universal WH_Death).
    - [Testerbot census correction C2 BINDING: body/PNG rows live in
      assets.js, NOT CONFIG.assets — MANIFEST (assets.js ~:16-165) gets
      covenBody; BODY_PNG (assets.js ~:181-185) is the png map.]
    - MANIFEST += covenBody:
      'art-direction/3d/assets/races_regen/rigged/human-female-caster.rigged.glb'
      IF that file exists, ELSE
      'art-direction/3d/assets/races_regen/rigged/elf-dawn-refuser-male.rigged.glb'
      (verified: human-female-caster does NOT exist on disk => use the elf
      fallback; test -f before finalizing; report which was used).
    - BODY_PNG row for covenBody:
      ONLY IF a suitable existing png can be reused (census
      art-direction/3d/assets for an existing pixelated png of the chosen body;
      else omit the pngs row, body renders raw — record the deviation).
    - [Testerbot census correction C5 BINDING: CHARACTERS (assets.js ~:229)
      += covenBody: 6 — REQUIRED. Without it assets.js skips clip capture
      (:714 gate) and instances share a skeleton (:814 cloneTemplate). The
      elf glb carries exactly 6 universal clips.]
    - CONFIG.enemyWeapon stays untouched (no melee weapon for coven).
    - NEW `CONFIG.enemySpell.covenBolt` (sibling of spell.firebolt; NOT inside
      spell.* — keep the player spell registry untouched):
      kind: 'projectile', focusCost 0, damage: 14, speed: 16, hitRadius: 0.8,
      maxRange: 22, castWindup: 0.55 (== attackPhase.windup; the spawn instant
      = the attackPhase 'active' entry), castCooldown: 2.6, schoolColor:
      0x4fd8c8, name: 'Coven Bolt', glyph 'CB', light { color 0x4fd8c8,
      intensity: 6.0, distance: 9, decay: 2, flickerPct: 8 },
      projectileLight { color 0x4fd8c8, intensity: 2.0, distance: 6, decay: 2,
      flickerPct: 10 }.
    - CONFIG.leveling.xpSources += kill_coven: 30 (hp 60 x ~0.5 law).

1.2 `CONFIG.regionC.enemies` — APPEND-ONLY (row-index persistence law:
     enemy save state keys by row number; NEVER reorder/insert between existing
     rows): 2 coven rows appended at the very END of the array:
    `{ type:'coven', x:-118.4, z:-238.2 }` and `{ type:'coven', x:-99.2,
    z:-249.1 }` — SW moor area near the regionC center (0,0 is C center; these
    sit between the SW camps and the den mouth area, away from camps/pack
    loops/den door line; devbot must verify >25m from every camp prop row, wolf
    pack loop waypoint, and the den door interactAt (-163.4,-202.6); adjust
    coords slightly if a clearance check fails, keep >25m from all).

### 2. Enemy class machinery (prototype/js/enemy.js)

- bodyByType/animVariantByType consumers: via WH_Enemy.bodyNameFor and
  cfgFor — confirm zero new code needed there (existing generalized maps).
- NEW spell-casting branch in Enemy.prototype.update, gated
  `if (this.type === 'coven' && ...)`:
  - FSM stays idle/aggro/chase/attack/stagger/dead; 'attack' = the cast cycle.
  - Cast cadence: while in FSM 'attack' (aggro'd, player alive, within castRange
    22m — reuse enemySpell.maxRange as castRange): start a cast clock
    cast clock castT 0→attackPhase.windup (0.55s) with a cyan glow on the staff
    hand growing with castT (emissive pulse, presentation only), then at windup
    expiry spawn the bolt: `window.WH_SPELLS.spawnEnemyBolt(game.scene,
    'covenBolt', {x,y,z}, dirX, dirZ)` (NOT WH_SPELLS.spawn — that reads
    CONFIG.spell and returns null for 'covenBolt') from an origin 1.2m up at
    the enemy pos + 0.3 toward
    the player; direction = normalized (playerPos - enemyPos) at spawn instant
    (snap-shot, no tracking). After spawn, recover = attackPhase.recover
    (0.85s), then re-enter 'attack' hold (re-cast cadence = windup+recover =
    1.4s base, gated by CONFIG.enemySpell.covenBolt.castCooldown 2.6s between
    bolt spawns). If the player leaves castRange during windup, cancel the cast
    clock (glow decays, cycle restarts on re-entry, no bolt).
  - Movement: NO chase-to-melee. In 'attack' hold: keep distance — if dist < 8m
    back away at moveSpeed x 0.6; if dist > 16m approach at chaseSpeed x 0.5;
    8-16m = drift 0. Face the player continuously (existing yaw behavior).
  - Aggro path: existing sense machinery (sight+dark-sense) → 'aggro' → 'chase'
    approach until within castRange, then the coven branch takes hold.
  - Coven NEVER enterStagger? NO — coven stagger like bandits (staggerTime 0.45);
    a stagger CANCELS an in-flight cast clock (no bolt fires mid-stagger).
  - On death: existing kill path (setFsm dead + onKilled → 'kill_coven' XP via
    the existing 'kill_' + type concat — no new code; verify kill_coven award
    works through the existing path with the CONFIG row).
- Melee harm: NONE (attackDamage 0). The attack-phase 'active' window calls
  canDamagePlayer(attackDamage=0) harmlessly (existing code path with 0) — OR
  skip the melee active-window call for coven via the same `type === 'coven'`
  gate; devbot's choice, must be documented in the build note.

### 3. magicDefense choke (player.js resolveIncomingHit — AMENDED: no player.js edit)

- AMENDMENT (binding, supersedes the two bullets below it): resolveIncomingHit
  is NOT modified at all. magicDefense is applied at the bolt-hit call site in
  game.js only, per the NORMATIVE block below. The two bullets below are
  historical drafts kept for gate traceability — build per the NORMATIVE block
  ONLY.
- [HISTORICAL DRAFT] Insert BEFORE parry/block arc math a spell-classification
  branch: attacker has attacker.isSpell = true → reduced = damage *
  max(0, 1 - WH_LEVEL.magicDefense()); if reduced <= 0 return false; else fall
  through with damage = reduced. [NO LONGER THE PLAN]
- The coven bolt's damage on player-hit routes as a SPELL HIT. [HISTORICAL
  DRAFT — superseded by the NORMATIVE block below; kept for traceability]
- Bolt player-hit route (NORMATIVE, single source of truth):
  - WHO applies MD: the CALL SITE (game.js) applies magicDefense exactly once:
    reduced = round(dmg * (1 - WH_LEVEL.magicDefense())) then
    damagePlayerFromEnemy(reduced, {isSpell: true, pos: {x,y,z of the bolt at
    hit}}). resolveIncomingHit is NOT modified for MD (no double mitigation).
  - Why parry is naturally safe: the parry branch in resolveIncomingHit
    requires attacker.enterStagger to exist — a bare {isSpell,pos} attacker has
    none, so a bolt is never parry-staggered. Do NOT add fields that would open
    that branch.
  - What still applies to a bolt hit unchanged: roll i-frames (early exit),
    shield block (chip on the already-reduced amount; guard break math normal),
    dagger guard past window = full reduced damage via step 4.
  - One hit per bolt: spent/hitFlash pattern exactly like Firebolt's (0.15s).
- Bolt vs player collision circle (Testerbot census correction C1 BINDING):
  CONFIG.player.radius ALREADY EXISTS = 0.7 (CONFIG.js ~:1569, consumed by
  enemy melee reach game.js/enemy.js and prop push-out). Do NOT add or change
  it. Circle test = hitRadius 0.8 + 0.7 = 1.5 m using the LIVE
  window.WH_CONFIG.player.radius value (never hardcoded).

### 3.1 Item stat hook (no new items)

No new item carries stats.magicDefense today (the equipped-hands items sum via
equippedItems() = hands only). Census: if no item carries stats.magicDefense,
the hook is LIVE but inert until an item grants it (expected: 0 always in v1).
This is the intended v1 activation: the choke is in the wall waiting for gear.
This round does NOT add magicDefense items (separate round if wanted).

### 3.2 spells.js bolt class + spawn helper

- New class `WH_CovenBolt` lives in spells.js (registry home of projectile
  classes). Registry gets a second spawn helper:
  `WH_SPELLS.spawnEnemyBolt(scene, 'covenBolt', origin, dirX, dirZ)` reading
  CONFIG.enemySpell['covenBolt'] (return null for unknown id).
- Visual: ONE emissive-style MeshBasicMaterial sphere, radius 0.22, color =
  enemySpell.schoolColor (0x4fd8c8). NO pooled dynamic light in v1 — census how
  firebolt gets its in-flight light (CONFIG.playerLight.projectilePoolSize
  pool); if that pool is player-firebolt-specific, skip it for the coven bolt
  and RECORD the deviation (accepted by IO: simpler, keeps the light pool
  untouched).

### 3.3 Update loop insertion

game.js update loop: after the firebolts update loop, add the enemy-bolt update
loop (same keep-alive filter pattern as firebolts enemy hit → keep.push).

## 4. Not in scope (record, don't build)

- Doc-34 perception/taunt/pack rewrite, roll/block AI on coven (AI1 stays for
  bandit/wolf/ghoul shapes), coven camps/encounter tables, magicDefense ITEMS,
  Rot-Mother work, magicDefense vs AI1 bandit guard (guardDamageMult applies
  to melee+firebolt ONLY, coven bolts are NOT AI1 guard-relevant — the coven
  has no ai1 block), any doc-34 open items (rout tables).

## 5. Acceptance criteria (Testerbot validates these)

A1. CONFIG.coven row matches §1.1 numbers exactly (hp60/speed3.4/chase4.6/sight20
    /leash40/stagger0.45/radius0.7/attackDamage 0).
A2. bodyByType/body-png rows: the chosen coven body path EXISTS on disk
    (census before writing the row; report which file). pixelated PNG only if an
    existing suitable png was found+reused (else omission + deviation note).
A3. Append-only verified: `git diff` of regionC enemies shows ONLY additions at
    the array end (no reorder/insert/modify of existing rows).
A4. kill_coven 30 in xpSources; 'kill_' + type path awards it (code-read verify:
    no new award code needed).
A5. Coven branch: cast cadence, range keep-distance band 8-16m, cast cancel on
    player leaving 22m during windup, stagger cancels cast, NO melee harm
    (canDamagePlayer never called with coven melee), face player while holding.
A6. CovenBolt class in spells.js, spawned via WH_SPELLS.spawnEnemyBolt; cyan
    MeshBasicMaterial emissive-style sphere; maxRange 22 die, hit-then-flash
    (0.15s, firebolt-pattern), one sphere per bolt; speed 16, hitRadius 0.8.
A7. Bolt-vs-player: 2D circle test (0.8 + CONFIG.player.radius); on hit:
    reduced=round(dmg*(1-WH_LEVEL.magicDefense())) at call site ->
    damagePlayerFromEnemy(reduced, {isSpell:true,pos}); resolveIncomingHit path
    verified by code-read: parry cannot trigger (bare attacker, no
    enterStagger), shield block works (chip on reduced dmg), roll i-frames work
    (early exit), MD applied EXACTLY ONCE. Dead/alive player state respected.
    (No headless smoke — code-read + spec anchors only.)
A8. game.js: enemy-bolt update loop after firebolts; dead-player guard on the
    bolt's player-hit call (bolt dies on player hit; no repeat-hit during flash
    — spent/hitFlash pattern like firebolt's).
A9. Art law: coven visual = charcoal/teal + cyan accent ONLY (no red/orange
    accents on the acolyte or its bolt). Char-09 anchor named in the build
    note; palette line in CONFIG comment.
A10. Bundle includes coven + spell blocks; build_v8.py runs clean; build output
     marker verifiable in prototype/builds/v8-playable.html (grep coven -> hit).
 A10b. Devbot builds per RUNBOOK (worktree, tools/build_v8.py, marker grep) and
  commits in the worktree with the gate line in the message (spec ->
  valspec -> build -> validate -> commit; NO-GIT clause: children NEVER push).
A11. No regressions: firebolts, bandit/ghoul/wolf/rotmother/rotspawn untouched
     behavior (coven additions are additive; row-index law: regionC additions
     at END only).
A12. Region clearance: the 2 coven spawn rows sit >25m from every camp, wolf
     pack waypoint, and the den door interactAt; devbot verifies against the
     regionC rows (devbot computes distances and reports them in the build
     note).

## 6. Gate flow (binding)

1. IO wrote this spec (gate step 1).
2. Testerbot writes the validation spec BEFORE Devbot starts (gate step 2).
3. Devbot builds from spec + valspec (gate step 3), commits in the worktree
   (CaptainPickard identity), NO-GIT (never push).
4. Testerbot validates independently (gate step 4) → PASS/FAIL verdict.
5. IO commits+pushes (gatekeeper), builds (build_v8), flips release, journals.

## 7. Art-law comment block (CONFIG coven comment must carry)

// CC-EC1 coven acolyte (doc 34 caster slice; art anchor char-09-coven-wizard):
// palette charcoal/teal robes + ONE cyan accent (0x4fd8c8); no red.
// magicDefense choke activation: WH_LEVEL.magicDefense() applied ONCE at the
// bolt->player call site (player.js resolveIncomingHit handles the rest).

## 7.1 Devbot build note must report

- covenBody glb chosen (path) + pixelated png decision (found/reused or omit).
- regionC clearance distances for both rows (min distance to camps/loops/door).
- deviation list vs spec (any, each with reason). Zero deviations = state it.
