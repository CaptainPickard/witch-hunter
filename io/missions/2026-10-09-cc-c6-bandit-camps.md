# CC-C6 · Bandit Camps of the Old King — Alpha / Bravo / Charlie (doc 62 §5.3)

Change-order brief, written 2026-10-09 by IO from docs/planning/62 §5.3
(camp law: campkit props, USABLE cook fires, AI1 guards, loot at camp,
NO containers), docs/planning/63 CC-C6, and the landed cooking/camp
machinery.

## 0. STATE (verified 2026-10-09 @ f8c07e7; re-verify anchors - they drift)

- TIP: f8c07e7 (wolf packs landed). Clean tree, origin equal.
- CAMP LOCATIONS (doc 62 landmark table, lines 121-123):
  - L4 Bandit camp Alpha (-60, +180): 2-3 bandits, firepit, bandit props.
  - L5 Bandit camp Bravo (+95, +130): 3-4 bandits, firepit, bandit props.
  - L6 Bandit camp Charlie (-140, -140): 4 bandits (deepest, best loot
    tier). NOTE: best loot tier today = MORE BONUS ROLLS on corpses (the
    drop system has no tier table; per-type drop tables are a future order
    if wanted - keep the loot implementation honest: Charlie guards just
    drop the same table; do NOT fake a tier, mark in the report).
- COOK STATION MACHINERY (cooking.js): station registry rows
  { id, kind: 'cookFire', regionId, asset, x, z, startLit } loaded from
  CONFIG.cookING.stations (~:2248, banditFire in B is the pattern);
  Cooking.addStation (~:191) takes runtime rows too - C3 camp cook modules
  register through the same API. Prompt/refuel/recipe text all live under
  CONFIG.cooking.text; deadwood fuel refuel loop exists.
- CAMP PROPS: banditCampfire (m15 kit firepit GLB + light socket def
  CONFIG ~:101), banditBedroll, whCampkit nodes (player kit). Bandit camps
  use BANDIT props (m15 fire / m16 bedroll), NOT the player kit - doc 62:
  "reusing bandit props + campkit firepit/bedroll/pegs (CK1 pattern: player
  camp kit vs bandit props already both exist)".
- BANDIT AI: CONFIG.enemy.bandit (full AI1 row at ~:1343-1382) - guards
  spawn as ordinary bandit rows with ai1 on (guardMode nonzero default
  per the landed AI1 posture e325005/6aaf339).
- C TERRAIN (CC-C4): camps sit on the heightfield; every prop seats via
  footY; camp placement props must NOT fight the roads (CFG.roads /
  GEO.road clearance) or the rim cliffs (r<240 walkable); the camp-edge
  fix (CC-C3 camp.js region-aware) means PLAYER camps can deploy near
  these camps - keep-out for camp placement comes from the camp.prop
  clearance (bandit props are CONFIG props, camp.js prop-clearance kicks
  in automatically).
- WOLF PACKS (CC-C5): wolves patrol loops crossing roads; pack camps sit
  INSIDE two of the loops' vicinity by design (ambush geography, Nicko's
  hill-blind-spot instinct) - verify no wolf loop waypoint passes THROUGH
  a camp clearing (loops_probe.js exists at scratch/cc-c5/).
- LIGHT: banditCampfire light socket def exists (CONFIG ~:101, heightFrac
  0.55, intensity 3.2); startLit fires glow + are cookable.

## 1. THE ORDER (doc 62 §5.3 binding)

- CAMP CONTENT (literal CONFIG rows - placement is config, never procedural):
  - Region C props rows gain the camp furniture (m15 firepit + m16 bedroll
    x2 + a few bandit-camp dressing props already in the manifest: rubble/
    log/stones if wanted - keep it MINIMAL and readable).
  - CONFIG.cooking.stations gains THREE rows: banditFireA (Alpha -60,+180),
    banditFireB (Bravo +95,+130), banditFireC (Charlie -140,-140) — kind
    cookFire, regionId forest_of_the_old_king, asset banditCampfire,
    startLit true, rotY to face the clearing (props seat at y=0 plane rows;
    y comes from the footY feed like other C props).
  - Region C enemies rows gain the guards: Alpha 3, Bravo 3, Charlie 4
    (bandit type, ordinary rows; they auto-get AI1). Guards placed in a
    guard spread around the fire (8-14m), NOT on top of props (the
    spawn-side prop clearance already nukes overlaps - follow the A/B
    bandit row conventions, enemy.z >= plane + hold checks apply per-side;
    region C rows obey the C-side checks region-manager validates).
  - CAMP IDENT: each camp reads as a camp (fire + bedrolls + a couple of
    dressing props scattered).
- USABLE FIRES (binding): a traveler can cook at ANY of the three fires -
  the cook-station surface is already region-generic via the registry row
  (regionId matches). Verify: E at an unlit/low fire offers refuel;
  lit fire offers Cook (graveSoup/fallback); recipes/buffs unchanged.
- LOOT: guards drop the CONFIG.drops table like every bandit (stolenCoin +
  bonus roll). NO containers, NO chests (CC-C12 quest reward owns chests).
- WOLF OVERLAP GUARD: confirm packs' loops do not cross camp clearings
  (run/derive from loops_probe); if one does, nudge the waypoint (declare
  the nudge in the report, do NOT silently edit loop geometry otherwise).

## 2. SCOPE CONTRACT

TOUCH: prototype/js/CONFIG.js (props + stations + enemy rows), prototype/
builds/v8-playable.html. OPTIONALLY prototype/js/enemy.js ONLY IF a guard
needs type-specific behavior (NOT expected). NOT TOUCH (read-only): cooking.js (registry already generic), camp.js, player.js, anim.js, assets.js,
game.js, index.html, style.css, docs/*, io/*, art-direction/*.
CRG IMPACT (baked, run 2026-10-09 @ f8c07e7): impact --files CONFIG.js
enemy.js game.js --depth 2 -> 129 nodes directly changed, 0 impacted
within 2 hops, 0 additional files. Expected ACTUAL touch: CONFIG.js + bundle
only (data-only order).

## 3. ACCEPTANCE CRITERIA (Nicko playtests; A1-A6)

- A1 THREE CAMPS: Alpha/Bravo/Charlie visible as camps (fire + bedrolls +
  dressing) on the terrain, props seated, near the doc 62 coordinates.
- A2 FIRES COOKABLE: E at a lit fire offers Cook; cooking there works
  (graveSoup/fallback flows exactly as at the B fire); refuel with
  deadwood works; fire dies and relights.
- A3 GUARDS: 3/3/4 bandits guard the camps with AI1 posture (strafe band,
  guard mitigation); engaging pulls the CAMP guards, not the wolf packs
  (unless a wolf loop genuinely crosses the clearing - declared).
- A4 LOOT: guard corpses roll the standard drop table; no chests anywhere.
- A5 WORLD COHERENCE: roads stay clear (no camp prop on a road band);
  player camp placement near a camp refuses via existing prop clearance;
  wolf packs still patrol.
- A6 A/B UNMOVED: B bandit fire (banditFire) behaves exactly as today;
  night cycle, door gate, magic/classes untouched.

## 4. PROCESS LAW (standing)

- Bundle rebuild before each commit, bundle in the commit; push after every
  commit; identity CaptainPickard; NO harness/headless/game runs (syntax
  checks only, node --check at playwright-driver). IO flips 8793 after gate
  review. English to Nicko.

## 5. REPORT

Files changed, syntax results, bundle bytes, commit SHAs + pushes,
A1-A6 self-audit (numbers: guard coordinates/distance to fire, road
clearances, wolf-loop overlap check verdict), deviations honestly flagged
(Charlie loot tier = honest same-table note).