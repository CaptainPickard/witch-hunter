# C3 CHANGE ORDER - SLEEP / TENT MENU / CAMPSITE DEPLOY (stage 3 cooking arc, order 3)

Builder: Claude Code print-mode, model opus, allowedTools Read/Write/Edit/Bash.
Dispatched only by IO on Nicko's go. NO automated game runs of any kind (no
harness, no headless browser, no smoke pass - explicit addendum to every brief
per standing law). Validation = playwright driver node --check per edited JS
file ONLY (/usr/local/lib/python3.12/site-packages/playwright/driver/node).
Nicko's playtest is the only acceptance test. At dispatch IO injects the
code-review-graph blast radius of the touched files into this context (impact
command; if the tool is missing the dispatch stops until /app/venv is fixed).

## STATE (verified 2026-10-06 morning)
- feat/world-visuals worktree /tmp/wh-worldfeat clean at 0956c91 (HD sky
  re-emit + moon reposition, APPROVED). Pushed (ls-remote verified). Build:
  tools/build_v8.py -> prototype/builds/v8-playable.html.
- Serving surfaces verified: 8793 = release 0956c91 (md5 match), /playtest-feat/
  live-serves the worktree.
- C1 cooking landed (stations registry, BuffSet, cook panel, one-meal-a-day
  cap, kit toast + inert CAMP button). C2 day/night landed (dormant boot,
  beginCycle, dayCounter, per-area sky pools). C2b pano pools + HD re-emit
  landed. All APPROVED by Nicko playtest.
- CONFIG.camp DOES NOT EXIST yet. prototype/js/camp.js DOES NOT EXIST yet.
- The Astrabot camp-kit GLB (wh-campkit) is a SEPARATE asset lane
  (io/missions/2026-10-05-astrabot-campkit-brief.md, awaiting Nicko's
  dispatch word). C3 ships with placeholder stand-ins (below); swapping the
  real GLB is a one-line asset-path change afterward.

## DESIGN CANON (Nicko, locked in chat; do not re-derive or re-ask)
1. TUTORIAL LAW: the day/night cycle is NOT automatic. Game boots dormant-
   locked night; dayNight.beginCycle() fires ONLY on the player's FIRST
   sleep (Save and Heal at a camp). C3 DELETES the playtest hatch:
   CONFIG.dayNight.autoBeginSec + the bootT tick block in DayNight.tick
   (daynight.js lines with "!!! PLAYTEST-ONLY HATCH").
2. TENT MENU (locked): interacting with the camp's tent OR bedroll opens a
   menu with EXACTLY TWO options:
   - "Save" = set respawn point here. Does NOT rest, does NOT heal, does
     NOT clear buffs, does NOT clear the day's meal slot, does NOT advance
     or begin the day/night cycle (player keeps exploring the tutorial
     night if he saves during it).
   - "Save and Heal" = the full rest life cycle: fully heal, CLEAR ALL
     buffs (graveSoup + blandMush + any future buff), CLEAR the day's meal
     slot (room for new morning buffs), set respawn point, advance the
     clock to MORNING (day restart: dormant -> beginCycle = day 1 dawn;
     already free-running -> day++ and clock 0 = dawn). Campfire fuel
     state untouched (the kit's fire AND world fires keep their fuel).
3. CAMPSITE DEPLOY (locked): the CAMP button becomes real. Deploys the kit
   (fire + bedroll + tent) on open ground only. Red ghost preview follows
   the ground; placement is REFUSED near trees/props/world
   objects/gather nodes/enemies - REUSE the gather-node clearance rules
   (CONFIG.gather clearances + CONFIG.scatter.clear + keepOut zones + dirt
   path band + gate corridor; trees 4m, other props 3m, enemy spawns 5m,
   spawn 6m, nodes per-region spacing radii). Refusal = toast + ghost
   stays (reposition or cancel). Deployed campsite lives on a SEPARATE
   manager (NOT region content) so region rebuilds never eat it. The camp
   system stays MODULAR (data-driven camp modules {id, prop, interact
   hook, CONFIG row}) - the roadmap adds quest-gated STORAGE CHEST and
   CRAFT BENCH and eventually the warp camp (docs 09/11/50: cook's tent,
   retinue, prestige). NO special-casing the bandit fire.
4. TUTORIAL ARC ORDER: cooking tutorial happens FIRST at the Region B
   bandit campfire (C1, already live). Kit reveal (first recipe learned,
   C1) becomes the deploy trigger. Sleep = day restart = the
   one-meal-per-day slot clears. First sleep EVER = beginCycle; afterwards
   every Save and Heal rolls the day over.

## DELIVERABLES

### D1 - Sleep owns the cycle trigger (delete the hatch)
- CONFIG.js: delete dayNight.autoBeginSec (and its comment block); keep
  startPhase: 'night', dormant boot, beginCycle() API exactly as is.
- daynight.js: delete bootT + the autoBeginSec block inside tick()'s
  dormant branch; dormant stays frozen forever until beginCycle() is
  called by the camp module.
- No other file may call beginCycle.

### D2 - Camp manager (new file prototype/js/camp.js, window.WH_CAMP)
- CONFIG.camp: { interactRadius: 2.5 (same feel as cooking), deploy: {
  clearances mirroring the gather-node rules - read the SAME CONFIG rows
  (gather + scatter.clear + keepOut), do not copy magic numbers into a new
  table; pathBand: 2.5 }, modules: [] } - modules are DATA rows so future
  camp modules (chest, bench, warp) slot in: one deployed campsite
  registers its module hooks from one row each. Keep the initial module
  set exactly: fire (cook: registers a cooking station row via
  WH_COOKING.addStation - CAMP GROWTH LAW row shape, nothing special-cased
  vs the bandit fire; fuel = CONFIG.cooking.fire rules), bedroll (sleep
  hook), tent (sleep hook + the menu anchor).
- Manager owns: deployable state (kit acquired = cooking.kitAcquired as
  the only gate), placement mode, the deployed sites list (session-
  persist only; C4 rides after), scene group per site, re-add on region
  rebuild (sites store regionId + x/z; the manager re-instantiates when
  that region is built/active - region dispose/rebuild must never delete
  a site).
- WORLD CAMPS: a camp module row may ALSO bind to a pre-placed world prop
  (no deploy, no kit). Tutorial anchor (canon: the Region B cooking
  tutorial is where the first rest happens): camp.js renders the
  m16-bandit-bedroll prop at a CONFIG.camp.worldCamps row next to the
  bandit campfire (darkwood_edge, coords beside x 2.5 z -52, ~3m off so
  both interact radius and the fire ring stay clean), sleep hook = the
  SAME tent menu. The bandit fire's C1 cook behavior is untouched (the
  bedroll module is sleep-only). The player's FIRST sleep can therefore
  happen at the world bedroll OR at a deployed kit - whichever comes
  first in play. World camp visuals here are NOT the placeholder kit
  dress-up below; the bedroll is a real shipped asset.
- PLACEHOLDER VISUALS (pending the Astrabot wh-campkit GLB): stand the
  site out of existing biome_library meshes - m15-bandit-campfire for the
  fire and m16-bandit-bedroll for the bedroll, plus a simple dark canvas
  A-frame built procedurally (few boxes) for the tent. Single
  CONFIG.camp.assets row per piece so swapping in the real GLBs later is
  a one-line edit per piece. Placeholder look is FINE for this order's
  playtest; do not spend time dressing it.
- Deploy UX: CAMP button (already on HUD, inert) -> placement mode: red
  ghost follows the ground under the crosshair/cursor (raycast to y=0,
  clamp to the active region's playable bounds), CAMP button or Escape
  cancels, click/E confirms. Confirm runs the clearance check (D2 module
  + gather rules): pass = place, refuse = toast (new CONFIG.camp.text
  row) + ghost stays. While in placement mode movement and combat inputs
  are suspended (inventory-panel pattern); a death or region cross while
  placing cancels placement silently.
- WH_DEBUG hooks consistent with the existing debug surface (placement
  state, site list) so Nicko can be talked through diagnostics if needed.

### D3 - Tent/bedroll interaction + menu (DOM modal, inv-panel pattern)
- game.js interact() chain: after cooking stations, before gather,
  nearest camp sleep module within CONFIG.camp.interactRadius of the
  player opens the TENT MENU (one world-interact priority slot; prompt
  text "E - Camp" via CONFIG.camp.text). The kit's FIRE keeps the C1
  cook prompt/panel (nearestCookStation unchanged - camp station rides
  the same registry).
- Menu: EXACT option strings "Save" and "Save and Heal" (+ a Cancel row /
  Escape closes). Same DOM modal pattern as the cook panel (input
  suspended while open, world keeps running). Touch path button rows like
  the inventory/cook screens (touch-controls pattern).

### D4 - Rest semantics (the life cycle)
- Save: set camp.respawn = { regionId, x, z } (the site's tent-facing
  offset ~1.5m so the player never respawns inside the fire ring). Toast:
  "Respawn point set". NOTHING else changes: no heal, no buff clear, no
  meal-slot clear, no clock change (dormant stays dormant).
- Save and Heal: (order matters) 1) clear ALL buffs (BuffSet clear-all;
  hpMax recompute so a graveSoup +20 drop clamps current hp), 2) full
  heal hp = recomputed hpMax, stamina full, 3) clear the day's meal slot
  (cooking mealDay -> invalid so the new day's first dayMeal applies),
  4) set respawn point, 5) day restart: dormant -> dayNight.beginCycle()
  (day 0 -> 1, dawn); free-running -> day++ with clock = 0 (dawn,
  consistent with dayCounterOf/sky rotation law). Campfire fuel untouched
  everywhere (kit fire and world fires keep burning per their fuel).
- The 60s playtest cycle stays the CONFIG default - rest timing must read
  correctly at 60s AND at the real-game 600s scale.

### D5 - Death respawn honors the camp
- respawnPlayer(): if a camp respawn point is set, respawn there (same
  region today's respawnAt path; OTHER region = force the region switch
  reusing the tickTransition 'cross' steps - buildRegion if needed,
  mappedPos/set pos, applyRegionLighting, dayNight.setSkyArea, region
  name banner - as one small helper so death-in-A respawning at a
  camp-in-B never walks the transition). No camp respawn set = today's
  behavior exactly.
- Death clears nothing else; buffs/meals/fire state persist through death
  as today.

### D6 - Build + land + verify serving
- Rebuild tools/build_v8.py -> prototype/builds/v8-playable.html; commit
  code order (feat/c3-sleep-tent-camp: CONFIG + camp.js + game.js +
  cooking.js hooks + style.css if needed) and build commit to
  feat/world-visuals; PUSH (HTTPS credential-store route; the deploy key
  is read-only).
- Syntax: node --check via the playwright driver on every edited JS file.
- Serving verification (both surfaces): host curl 8793
  /current/prototype/builds/v8-playable.html = 200 + new marker grep
  non-zero; /playtest-feat/ route serves the worktree (spot-check marker
  via the webui container route). NO harness, NO chromium pass.
- Report: files touched, markers to grep, commit shas, serving proof.

## ACCEPTANCE CRITERIA (Nicko's playtest script - all at 60s cycle)
1. Boot -> region A graveyard path at night, sky NEVER moves by waiting
   (hatch deleted; dormant holds indefinitely - watch past the old 15s
   mark).
2. Walk region B, cook at the bandit fire, learn Grave Soup -> kit toast
   -> CAMP button appears (C1 behavior unchanged by C3).
3. CAMP button press: ghost preview appears, follows the ground, red
   preview; walking near the bandit camp props/trees shows refusal toast
   on confirm; open ground confirms placement; Escape/CAMP cancels
   cleanly.
4. Deployed kit: fire interacts as a cook station (E opens the C1 cook
   panel, ADD WOOD works), tent/bedroll E opens the TENT MENU.
5. Tent menu "Save": toast "Respawn point set", NO heal, NO buff/meal
   change, NO clock change (if done during the dormant night the night
   stays; save mid-day keeps the clock position).
6. Tent menu "Save and Heal" while dormant: buffs clear, hp full, morning
   dawn + day 1 begins (first free-running cycle; sky rotates from now on).
   Soup eaten after rest is applied fresh (meal slot cleared).
7. Free-running at dusk: "Save and Heal" again -> morning, day counter
   +1, buffs cleared, meal slot empty, kit fire fuel unchanged, bandit
   fire fuel unchanged.
8. Set a camp in region B, walk back to region A, die on purpose ->
   respawn at the camp in region B (correct region look, sky area,
   banner), not the region A spawn.
9. Cross A<->B twice with a camp deployed: the site stays exactly where
   placed, fire fuel state preserved through the transitions.
10. Bland Mush / Grave Soup behaviors otherwise unchanged (no regressions
    in the cook panel, cap toast, buff chips).
11. World bedroll: at the region B bandit fire the placed bedroll opens
    the SAME tent menu via E BEFORE any cooking (first sleep possible
    pre-kit); the bandit fire still cooks/feeds normally (sleep-only
    module never hijacks the fire's interact).

## OUT OF SCOPE (do not touch)
- The Astrabot wh-campkit GLB (separate lane; placeholder visuals this
  order).
- C4 save profile (localStorage) - Save/Save-and-Heal stay session-only.
- Moonlight azimuth vs painted moon (open watch item, Nicko's call).
- HP bar 120% width watch item, CAMP button/touch overlap watch item,
  flames-in-burnt-mesh watch item (open watch items, not C3).
- Camp growth roadmap (storage chest, craft bench, warp camp) - only the
  modular module-row shape now, zero implementations ahead of the roadmap.
- Merge to dev/main (Nicko's explicit call only, as always).