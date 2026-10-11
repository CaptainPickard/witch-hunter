# CC-C6C · Bandit fires burn only at night; never cookable - camp fires own cooking

Micro-order brief, written 2026-10-11 by IO. Nicko ruling 2026-10-11
(session, verbatim intent): "all bandit fires are lit at night, and out
during the day. No fuel needed, but you can't cook on them. You can only
cook with your own camp fire, or other designated cooking station in the
world." Supersedes the CC-C6 read of "usable cook stations" for BANDIT
camp fires (doc 62 §5.3 amended by this ruling - note it in the next doc
revision or the order report).

## 0. STATE (verified 2026-10-11 @ 81781f7)

- cooking.js Station: { id, kind ('cookFire' today for ALL rows), regionId,
  asset, x, z, fuel, burnAcc, cooking }. isLit() = fuel > 0 || cooking.
  canCook() = fuel >= C.channelSeconds. update(dt, activeRegionId) burns
  only in the active region (CC-C6B, :77 gate). refuel() adds deadwood
  fuel. promptFor: burnt -> promptBurnt, else canCook -> promptCook else
  promptLow (cooking.js ~:243-244). interactStation: canCook -> panel
  open, else refuel (~:250). socketIntensity: isLit -> base, else
  burntLightIntensity (~:228-239). nearestStation filters by regionId.
- Station rows TODAY: CONFIG.cooking.stations (~:2290+): banditFire
  (darkwood_edge, startLit true) + CC-C6's banditFireA/B/C
  (forest_of_the_old_king, startLit true). C3 player camp fires register
  at DEPLOY time via camp.js:558 addStation({ id: site.id+':'+row.id,
  kind: st.kind ('cookFire' from CONFIG.camp.modules.fire ~:2388),
  regionId: rid, asset: K.assets[row.asset].glb, x, z, startLit }).
- Clock predicate precedent: enemy.js ~:45 isNight(dn) = !!dn && dn.phase
  === 'night' (CC-C5 night boldness). The Cooking instance receives
  opts.dayNight (game.js ~:1784) + opts.activeRegionId getter (CC-C6B
  game.js ~:1795). No further game.js access needed.
- Fuel economy: C.fire.startFuelSec 240, burnPerCookSec, refuelCooks,
  fuelItem deadwood; refuel + cook-channel deduction both live in
  cooking.js. CC-C6B made bandit fires' fuel effectively player-arrival
  gated; THIS order removes fuel meaning from bandit fires entirely.

## 1. THE RULING (binding)

- BANDIT FIRES (the 4 CONFIG stations: banditFire, banditFireA/B/C) are
  ATMOSPHERIC fire pits:
  - LIT exactly while the local clock reads phase 'night'; OUT during
    dawn/day/dusk (dusk boundary = the flip happens when the phase STRING
    changes - the same predicate convention as CC-C5's night boldness, no
    blend-window subtlety v1).
  - NOT COOKABLE at any time: no cook channel through them (E opens NO
    cook panel), NO deadwood refuel (E near a bandit fire does NOTHING or
    a flavor toast - pick: a single flavor toast "The bandits' fire - it
    offers nothing to a stranger." NEW text row, prompt path only).
  - NO FUEL mechanics: never burn, never refuel; isLit is a pure function
    of the clock (keep the fuel fields inert for simplicity - do NOT
    delete them; the kind gate keeps this honest without restructuring).
- COOKABLE STATIONS: only (a) the player's own deployed camp fire (the C3
  kit module) - unchanged, full cook/refuel mechanics; (b) FUTURE
  designated stations ride a NEW kind. Introduce kind 'campfire' (or
  'hearth') for NON-cookable atmospheric fires NOW: the 4 bandit rows
  re-kind to 'campfire'; the registry/prompt/interact/socket paths key on
  kind:
  - canCook(): kind !== 'cookFire' -> false (hard).
  - refuel(): kind !== 'cookFire' -> flavor toast, no fuel item spent.
  - promptFor(): kind !== 'cookFire' -> the flavor prompt ("E - Warm your
    hands" flavor read + the toast on E; NO cook panel path).
  - socketIntensity(): isLit() still drives light: for 'campfire' kind,
    isLit = the night clock (not fuel).
  - interact flow: kind 'campfire' -> the toast; NO panel, NO refuel.
- PLAYER CAMP FIRE (the kit): stays kind 'cookFire', startLit semantics,
  fuel/refuel/deadwood everything unchanged. Its light also stays
  fuel-driven (a player fire dies without fuel - unchanged).
- NIGHT FUNCTION: cooking.js gains the same isNight(dn) helper shape
  (enemy.js ~:45); 'campfire' isLit = isNight(this.dayNight). Dormant
  clock (pre-first-rest) = never night = bandit fires OUT (consistent
  with the tutorial's frozen day - fine, B's tutorial fire going dark is
  actually a nice pre-camp signal; declare it in watch-items).

## 2. SCOPE CONTRACT

TOUCH: prototype/js/cooking.js (kind gate + isNight + isLit branch +
prompt/interact/socket/refuel branches), prototype/js/CONFIG.js (4 station
rows kind 'campfire' + CONFIG.cooking.text flavor rows + a banditFireKind
comment block), prototype/builds/v8-playable.html.
NOT TOUCH: camp.js (kind 'cookFire' rides from CONFIG.camp.modules as
today), player.js, daynight.js, save.js, game.js (the CC-C6B getter
already carries what the update loop needs; night reads via the HELD
dayNight instance), index.html, style.css, docs/*, io/*, art-direction/*.
CRG IMPACT (baked, run 2026-10-11 @ 81781f7): cooking.js + CONFIG.js ->
10 nodes directly changed, 0 impacted within 2 hops, 0 additional files
(smallest blast radius of the C lane - the gate concentrates in cooking.js
branch lines).

## 3. ACCEPTANCE (Nicko playtests; A1-A6)

- A1 NIGHT LIGHT: at night, bandit fires (B's tutorial fire + Alpha/Bravo/
  Charlie) are LIT (light sockets glow); at dawn they go out (prompt
  flips, socket intensity = burnt).
- A2 NO COOK: E at a bandit fire at ANY hour: the flavor toast only, NO
  cook panel ever.
- A3 CAMP FIRE COOKS: the player's deployed camp fire still opens the
  cook panel, burns fuel, refuels with deadwood; all recipes/buffs as
  before.
- A4 DORMANT-START: fresh profile (clock dormant) - bandit fires read OUT
  (frozen day), no cook anywhere but a player fire.
- A5 NIGHT WOLVES/DOOR/REGRESSION FREE: wolves still bold at night,
  door still gates, mountains/roads/camps furniture untouched.
- A6 B FIRE VISUAL: light pool ties to night (the burntLightIntensity row
  path drives it - verify via socketIntensity branch).

## 4. PROCESS LAW (standing)

Bundle before each commit, same-commit bundle, push after every commit,
identity CaptainPickard, NO harness/headless/game runs (node --check
only), IO flips 8793 after gate review. English to Nicko.

## 5. REPORT

Files changed, syntax results, bundle bytes, commit + push, A1-A6
self-audit (assert the kind-gate lines + the isNight predicate), the
doc-62 §5.3 amendment note (for the docs to carry next session),
deviations.