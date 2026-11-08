# C4 CHANGE ORDER BRIEF - SAVE PROFILE (full-profile localStorage) + C4-ADJACENT

Order: Nicko 2026-10-06. "Proceed with C4, also switching spells via the
action bar when equipped with only an offhand magic glove does not work...
Lets make it so that switching spells in the action bar changes any
equipped magic glove active spell... we do need a way to have different
spells when dual wielding magic gloves... Dispatch astrabot as much as
possible for this work, and claude code." Rulings clarified by Nicko:
"Proceed with C4 adjacent" = IO recommendations adopted for Q1-Q5 +
cook-panel icons folded into this order; moon azimuth stays a watch item.

Builder: Claude Code CLI print-mode, model opus,
--allowedTools "Read,Write,Edit,Bash", --max-turns 60, worktree
/tmp/wh-worldfeat, branch feat/world-visuals.

PARALLEL LANE WARNING: an Astrabot child is landing campkit GLB commits in
this worktree at the same time (paths: art-direction/3d/assets/camp/**,
scratch/campkitgen/**, scratch/campkit_*.py, io/missions docs). It is
FORBIDDEN from prototype/** and MANIFEST.json. You own the code lane.
Before each commit: git fetch; if origin tip moved, rebase onto
origin/feat/world-visuals; never checkout-under-serve; verify your commit
pushes (or STOP and report if the remote won't take it).

## VERIFIED STATE (IO census 2026-10-06, worktree truth)
- Branch feat/world-visuals tip before this order: 746212c (docs c4/campkit
  addendum) on top of ca41543 (AB1.1 dual-glove fix) / 6caa01b / 5e3920f
  (AB1 bar) / 9d19bbd (icons) / 72a8e31 / 187e882 (AB1 briefs).
- AB1 LANDED AND NICKO PLAYTESTED GOOD (verdict 10-06: "everything else is
  great"). Bar = player-mappable 5 slots, icons via window.WH_ICONS
  (js/icons-data.js data URIs), picker = right-click/long-press,
  CONFIG.actionbar.lsKey 'wh-actionbar-v1' persists. AB1.1 fix (this
  session, 5ed4e76): selectActionSlot(player.js:792) spell branch - ONE
  caster hand: plain or Shift select retunes THAT hand; TWO caster hands:
  plain = main, Shift = off (Order C C5 preserved). DO NOT REGRESS THIS.
- Camp (js/camp.js WH_CAMP): sites session-only, site frame {regionId,x,z,
  face}, worldCamps boot-loaded from CONFIG.camp.worldCamps, respawn =
  {regionId,x,z,face,campId}, tent menu = buildMenu (camp.js:188) rows
  [[save],[saveHeal],[cancel]], TUTORIAL LAW: camp.js Save-and-Heal is the
  ONLY beginCycle() caller (first rest = day 1 dawn), later rests
  nextDawn(). dayNight (js/daynight.js): dormant bool, day int (0 = first
  night), clock (sec into cycle), phase; boot DORMANT.
- Player (js/player.js): hp/hpMax, stamina/staminaMax, focus/focusMax,
  hands {right,left} item ids or null, belt (defaultSpells array),
  bindings {main,off}, consumables [{id,charges},null], state.
  Boot equip: CONFIG.equip.defaultHands.
- Cooking (js/cooking.js): CONFIG.cooking.recipes rows carry .known flag
  (learned on first cook, cooking.js:463); cooking.kitAcquired gates camp
  deploy; inventory grid = CONFIG.inventory.slots (24), items in
  inventory.items stacks {id,count}.
- Boot overlay: index.html #wh-load-note (title/bar/sub), game.js boot at
  :1873+, respawnPlayer at game.js:856.
- Buffs: game.cooking.buffs list + CONFIG.cooking.buffs (graveSoup/blandMush
  rows, dayMeal slot, day clearing). Buffs are DERIVED from foods eaten +
  the dayMeal slot - persist the SOURCE (inventory/recipes/day), then
  applyBuffStats recomputes. Persist the dayMeal slot id + day only.

## NICKO RULINGS (locked)
1. COVERAGE = FULL PROFILE: hp/focus/stamina (+maxes), inventory grid
   stacks, equipped hands, belt + bindings (per-hand), action-bar map
   (CONFIG.actionbar.lsKey already persists), consumable charges, recipe
   .known flags, cooking.kitAcquired, deployed camp sites (frame + region),
   camp respawn point, clock (day + phase + timeOfDay), player position +
   yaw (respawn-adjacent: save stores where you stood at the camp), the
   dayMeal slot. Fresh world spawns (trees/gather nodes/enemies) stay fresh.
2. TRIGGERS: camp menu Save / Save-and-Heal only + a save on menu quit
   (tab close / beforeunload if trivial: same profile write). Death saves
   NOTHING (no death-delta this round - doc 35 death-delta is a later
   order). No timed autosave.
3. SHAPE: ONE rolling profile, key wh-save-v1 (CONFIG.save.lsKey), every
   save overwrites, JSON schema versioned v1. Load = last save wins; with
   no save, boot stays the current fresh-boot flow.
4. LOAD UI: camp menu gains a LOAD row (disabled/dim when no save exists),
   and boot Continue: when a save exists the boot overlay gains a CONTINUE
   button under the bar (starts with the saved state); fresh start remains
   the default flow when no save exists AND via a small NEW GAME row on the
   boot overlay only when a save exists.
5. RESET: no wipe surface this round. NO debug key, NO delete row.
6. C4-ADJACENT (in scope): cook panel ingredient rows (cooking.js render)
   show text glyph abbreviations - switch them to WH_ICONS icons (24px,
   same pattern as the AB1 belt). Cook-panel ICONS only - no cook logic.
7. MAGIC CANON UNTOUCHED (10-05 binding): spells = learned knowledge; no
   consumable spell charges; the belt is quick slots over learned spells.
   The AB1.1 dual-glove select semantics are LOCKED - persistence restores
   bindings.main/bindings.off as saved.
8. NO harness runs, NO chromium, NO headless browser, NO game runs of any
   kind. Syntax validation = playwright driver node --check per edited
   file (NODE=/usr/local/lib/python3.12/site-packages/playwright/driver/node).

## BLAST RADIUS (baked; tool /app/venv/bin/code-review-graph, repo
/tmp/wh-worldfeat graph 215 files/1782 nodes/23739 edges, 10-06)
impact --files prototype/js/CONFIG.js prototype/js/camp.js
prototype/js/game.js prototype/js/cooking.js prototype/js/player.js
prototype/style.css prototype/index.html --depth 3:
  112 nodes directly changed, 0 nodes impacted (within 3 hops),
  0 additional files affected.

## SCOPE (implementation contract)
- S1 SAVE MODULE: new prototype/js/save.js (IIFE, window.WH_SAVE), loaded
  in index.html AFTER camp.js and BEFORE touch-controls.js. API:
  capture(game) -> plain object; restore(game, data) -> void;
  save(game) -> write CONFIG.save.lsKey {v:1, ts, ...data};
  load(game) -> data|null; has() -> bool; wipe stays internal-only.
  All state reads/writes through existing managers (game.player,
  game.camp.sites/respawn, game.cooking/game.cooking.buffs dayMeal,
  game.regionManager, dayNight module instance game.dayNight if exposed,
  else via game). Version field guards future migrations.
- S2 CAPTURE/RESTORE CONTRACT (exact fields): player {hp, focus, stamina,
  pos [x,z], yaw, hands {right,left}, belt [5], bindings {main,off},
  actionMap (read CONFIG.actionbar.lsKey raw JSON and embed), consumables};
  inventory {items: [{id,count}...]}; cooking {recipes known ids[],
  kitAcquired, dayMeal {buffId?, savedDay}}; camp {sites: [{regionId,x,z,
  face:{x,z}}], respawn}; world {day, phase, timeOfDay}.
  On restore: write inventory first, then equipDefaultHands ONLY for
  missing hands (restore overwrites), re-apply hands via existing
  equipItem/applyHandVisuals paths (regrip reset), rebuild camp sites
  through the camp manager's own site builder (regionId + x/z re-instantia-
  tion path already exists for region rebuilds - reuse it, never hand-add
  scene groups), set dayNight state directly (dormant=false only if saved
  phase != startPhase; else stay dormant per TUTORIAL LAW), teleport
  player, clamp hp/focus/stamina to maxes, applyBuffStats().
- S3 CAMP MENU: camp.js buildMenu + text rows gain LOAD (K.text.load
  'LOAD'); disabled state when !WH_SAVE.has() (dim, click = refusal toast
  CONFIG.save.text.noSave toast 'No save yet'). Save rows call
  WH_SAVE.save(game) FIRST, then existing behavior (Save + Save-and-Heal
  both write the profile; Save-and-Heal continues through its rest flow).
  Toast on save: CONFIG.save.text.saved 'Saved.' (camp toast path).
- S4 BOOT CONTINUE: game.js boot: if WH_SAVE.has() the boot overlay shows
  CONTINUE + NEW GAME rows (CONFIG.save.text.continue/newGame). The boot
  overlay currently auto-dismisses on assets settled - gate that dismissal:
  wait for BOTH assets settled AND rows handled. CONTINUE = restore(); NEW
  GAME = fresh flow + WH_SAVE.save() stays untouched (profile REPLACED on
  the first camp save - do not wipe on new game). No profile data read
  during asset preload (restore happens after boot completes, scene ready).
- S5 QUIT PERSIST: window beforeunload/pagehide (guard once, tiny) writes
  the same capture() profile ONLY when a cycle has begun
  (dayNight day > 0 or sites exist) - never on a fresh untouched boot.
  Keep it best-effort & quiet (localStorage is sync; no retry UI).
- S6 COOK PANEL ICONS (adjacent): cooking.js ingredient rows + result rows
  render WH_ICONS icon at 24px before the label (same DOM pattern as the
  AB1 belt slots: background-image, image-rendering pixelated). Recipe
  rows keep names; glyph spans replaced. NO cook logic changes.
- S7 CONFIG: CONFIG.save = { lsKey: 'wh-save-v1', version: 1,
  schema note, text: {saved, noSave, continue, newGame} } near
  CONFIG.actionbar. NO other CONFIG edits.
- S8 BUNDLE: python3 tools/build_v8.py from worktree root; commit the build
  artifact separately (build commit last). Markers in the bundle must
  verify: WH_SAVE (>=3), wh-save-v1 (>=1), C4 (>=1), data:image/png (>=16).

## FILES
- prototype/js/save.js (NEW)
- prototype/js/CONFIG.js (S7 block only)
- prototype/js/camp.js (S3 menu rows)
- prototype/js/game.js (S4 boot rows, S5 quit hook, restore wiring)
- prototype/js/cooking.js (S6 icon rows)
- prototype/style.css (save rows + boot rows + cook icon sizing)
- prototype/index.html (save.js script tag only)
- prototype/builds/v8-playable.html (build commit)

## HARDCODED LAWS (repeat verbatim in the prompt)
- NEVER touch /workspace/witch-hunter checkout, dev, main, docs/, tools/,
  io/ (except reading briefs), scratch/ (EXCEPT scratch/campkitgen is
  astrabot's - do not touch any scratch/).
- NEVER read/commit scratch/.mixamo-credentials.txt or .mixamo-storage.json.
- NO harness/chromium/headless browser/game runs of ANY kind.
- Commit identity CaptainPickard <pickard.nicko@gmail.com> on every commit.
- Push origin feat/world-visuals after EVERY commit.
- Commit units: (1) save.js + CONFIG block, (2) camp menu + boot + quit +
  style, (3) cook icons, (4) build artifact. Rebase law for parallel
  astrabot commits (top of brief).

## ACCEPTANCE (Nicko playtest, A-numbers)
- A1: Camp menu shows SAVE / SAVE AND HEAL / LOAD / CANCEL. LOAD dimmed
  before any save. SAVE writes the profile (toast 'Saved.').
- A2: Save at camp, walk away, fight, take damage, spend focus, eat, learn
  a recipe, deploy a second camp, advance the clock. LOAD from the camp
  menu restores: hp/focus/stamina, inventory contents, equipped hands,
  bar map, recipe knowledge, both camp sites, clock state, position at
  the save camp.
- A3: Save-and-Heal flow UNCHANGED otherwise (fade, wake-snap dawn, heal,
  day roll) and now also writes the profile first.
- A4: Boot with a save: CONTINUE + NEW GAME rows; CONTINUE enters the
  saved state at the same camp/clock; NEW GAME fresh. Boot with no save:
  current flow, no rows (or rows absent).
- A5: Reload mid-cycle between camps via browser refresh: profile written
  at last save + quit-persist; you re-enter at last camp save, not where
  you stood (quit persist writes POSITION ONLY per S5 - accept exactly
  either: (a) at last save state, or (b) at quit-time position, whichever
  the builder ships cleanly; IO will confirm).
- A6: Death: respawn flow unchanged; death does NOT corrupt or advance the
  profile; LOAD after a death still returns to the last SAVE.
- A7: Dual-glove/dual-caster state survives save/load: bindings restore
  per hand (AB1.1 semantics intact - main/off select behavior identical
  before and after save-load).
- A8: Cook panel ingredient + result rows show pixel icons (24px), cook
  logic identical (cook a Grave Soup to prove both learned-row icon and
  result icon).
- A9: Old AB1 bar/picker/keyboard behaviors unchanged (A1-A9 of AB1 brief
  stay green; the bar map persists independently of wh-save-v1).
- A10: node --check clean on all edited files; bundle markers per S8.

## FINAL REPORT SHAPE (<= 50 lines, child's tail-visible stdout)
- Commits table: sha | what (one line each, including the build commit).
- Schema v1 field list actually serialized (one line per top key).
- Marker counts: WH_SAVE / wh-save-v1 / C4 / data:image/png in the bundle.
- WATCH ITEMS: anything you could not verify (Nicko playtests the rest).

## OPEN DESIGN QUESTIONS THE CHILD MUST IMPLEMENT AS SPECIFIED (not decide)
- Restore ordering edge cases (camp site re-add before teleport, dayMeal
  restore vs buffs recompute) - S2 wording wins.
- A5 quit-persist semantics ambiguity: ship the cleaner of the two
  behaviors and FLAG it in the report for IO to confirm with Nicko.