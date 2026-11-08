# CC-C6B · Fire burn is region-scoped — fires only burn in the ACTIVE region

Micro-order brief, written 2026-10-11 by IO. Nicko go 2026-10-11 ("Fix fire
now"). One behavioral defect from CC-C6, one surgical fix.

## 0. STATE (verified 2026-10-11 @ 241718e)

- cooking.js Station.update (C.fire.burnTickSec cadence, ~:73-80) burns
  EVERY station in the registry every frame regardless of region. 4
  startLit fires x 240s fuel = all dead ~4 min after boot, while the
  player is nowhere near 3 of them (C fires are unreachable until the
  first Save-and-Heal clears the door gate).
- Cooking.prototype.update (cooking.js ~:483) iterates stations; it is
  called every frame from game.js ~:2846 with game.cooking owning
  this.dayNight and the region manager reachable via game (passed in
  opts? VERIFY at dispatch: cooking.js constructor opts — game.js ~:1784).
- Fires: banditFire (darkwood_edge), banditFireA/B/C
  (forest_of_the_old_king) + C3 player-deployed camp fires carry
  regionId of the deploying region (C3 camp sites record regionId).

## 1. THE FIX (Nicko's ruling 2026-10-11)

- A fire burns fuel ONLY while its region is the game's ACTIVE region:
  in Cooking.prototype.update, pass an active-region gate into
  Station.update (or check inside): if station.regionId !== activeRegionId,
  pause the passive burn (burnAcc frozen at 0; cooking channel logic
  UNTOUCHED — a cook can only be running in the active region anyway,
  since the panel opens by proximity in that region).
- Effects: B's fire keeps full behavior whenever B is active (including
  during a C visit it PAUSES - the fire waits for you; when you return to
  B it resumes burning from its paused fuel. This is the intended
  "the world waits at the fire" reading, not a new persistence system).
- NO save change: fuel is session-state as today.
- NOT in scope: per-fire tuning (startFuelSec stays 240), lighting
  visual states, camp.js, enemy/anything else.

## 2. SCOPE CONTRACT

TOUCH: prototype/js/cooking.js (the gate ONLY), prototype/js/game.js
(ONLY if the constructor needs the region-manager getter passed - prefer
zero game.js changes, the Cooking instance already receives opts from
game.js ~:1784; VERIFY what opts carry), prototype/builds/v8-playable.html.
NOT TOUCH: CONFIG.js, player.js, camp.js, daynight.js, save.js,
everything else.
CRG IMPACT (baked, run 2026-10-11 @ 241718e): cooking.js + game.js ->
125 nodes directly changed, 0 impacted within 2 hops, 0 additional files.
Expected actual: cooking.js (+game.js zero-line) + bundle.

## 3. ACCEPTANCE (Nicko playtests; A1-A4)

- A1: boot the game, idle anywhere for >4 min: B's bandit fire still lit
  WHILE IN B when you reach it (burning counts only B-active time).
- A2: cross into C; the C fires (startLit) are LIT on first arrival
  (they never burned while you weren't there).
- A3: cook + refuel flows at a C fire work exactly as before (channel,
  recipes, buffs, deadwood refuel); B's fire unchanged in behavior.
- A4: nothing else drifted (wolf packs, camps, classes, A/B).

## 4. PROCESS LAW (standing)

Bundle before each commit, same-commit bundle, push after, identity
CaptainPickard, no harness/headless/game runs (node --check only), IO
flips 8793 after gate review.

## 5. REPORT

Files changed, syntax results, bundle bytes, commit sha + push, A1-A4
self-audit (assert the gate logic line numbers + the paused-on-inactive
behavior), deviations.