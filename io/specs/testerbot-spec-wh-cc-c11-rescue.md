# TESTERBOT SPEC — Witch Hunter CC-C11: Rescue + Reward (Quest Completion Chain + CAMP CHEST) (gate step 2)

Author: Testerbot gate step 2 (independent validator-author). Date: 2026-10-25.
Devbot spec of record: io/missions/2026-10-25-cc-c11-rescue-chest.md (IO-authored, read-only;
rulings R-C11.1..6 are settled; mismatches with the live tree are amendment notes B1..Bn below,
never patched in the brief by me).
Tree at authoring: **935db87** (feat/world-visuals, worktree /tmp/wh-worldfeat; `git log -1
--format=%h` = 935db87). `git diff --stat HEAD` = empty at authoring (clean code base;
`git status --short` shows only untracked scratch/cc-c11/, scratch/cc13b-*, scratch/
extract_rows.cjs — IO dispatch + helper files, not builder output). All CC-C11 diffs are
measured against 935db87.
Process law: doc 62 §13 (one order, NO harness runs, syntax checks only, Nicko playtests);
doc 63 CC-C11 (procedural placeholder chest, raw placeholder daughter GLB per R-C11.3,
questState/chest additive save blocks, camp.js + save.js UNTOUCHED).

## LIVE ANCHORS (line-verified by reading the files at 935db87)

L1  prototype/index.html (72 lines): script order
    `<script src="js/camp.js">` :65, `<script src="js/npc.js">` :66, `<script src="js/save.js">`
    :67, `<script src="js/touch-controls.js">` :68, `<script src="js/wolf-debug.js">` :70,
    `<script src="js/game.js">` :71. CC-C11 insertion point = new line between :66 (npc.js)
    and :67 (save.js), i.e. index.html gains exactly one tag `<script src="js/chest.js">`
    so that chest.js loads after npc.js (R-C11.6).

L2  CONFIG.js regionC.npc block :1167-1189; quest block :1190-1197
    (`regionC.quest = { id: 'findDaughter', states: ['available','active','complete'],
    hudText: '...' }` :1193-1196). regionC close `},` :1198. CC-C11 additions land inside
    regionC after the quest block (completion lines + rescued HUD text keys, R-C11.1/5).

L3  CONFIG.js regionD block :1211-1322. `id: 'rot_den'` :1212, `center: { x: -186, z: -180 }`
    :1214, `groundRadius: 34` :1215, `spawn: { x: -156, z: -190 }` :1221. `lairs: [
    { type: 'rotmother', x: -185.8, z: -180.2 } ]` :1259-1261. props rows :1269-1309
    (10 whWall ring rows :1271-1280 + 4 mossBoulder :1283-1286 + 4 stoneSteps :1288-1291
    + 2 skullPile :1292-1293 + 3 graveMound :1294-1296 + 6 blightcap :1297-1302 + the
    nest ring of 5 graveMound :1304-1308). `rotLair` dressing block :1315-1321.
    Sarcophagus row must land inside regionD.props AND inside the disc r 34 from
    (-186, -180) (probe B5 — see AMENDMENTS).

L4  CONFIG.enemy.rotmother block :1907-1936. `lair: { x: 0, y: 6, region: 'D', flag: 'C' }`
    :1912 (den-local (0,+6) → world (-186,-174)). `lairRadius: 14` :1924 (minion spawner
    active-radius; = rearm.radius :1915). `radius: 1.1` :1920 (body circle).
    `rearm: { days: 3, trigger: 'proximity', radius: 14 }` :1915. Probe-clear bar (B5)
    = keep the sarcophagus (a) outside lair body + dressing pool + spawn→lair walkway
    and (b) inside the den disc r 34 (L3).

L5  CONFIG.camp block :2846-2925. `interactRadius: 2.5` :2847. assets :2851-2862
    (`pegs: { glb: 'whCampkit', node: 'pegs', scale: 1.6 }` :2861). `modules` :2869-2876 —
    pegs module at :2875 `{ id: 'pegs', hook: 'none', asset: 'pegs', offset: [0, 3.6],
    rotY: 0 }` (rides the tent spot; inert hook 'none'). `deploy.maxSites: 1` :2892.
    text block :2904-2923. CC-C11 `CONFIG.camp.chest` sub-block lands here, after
    the deploy block, with offset, interactM, capacity 24, and stack rules inherited
    from CONFIG.inventory. camp.js stays UNTOUCHED (PRES law).

L6  camp.js (677 lines). Exports `window.WH_CAMP = { Camp }` :674. `this.sites = []` :163
    (deployed kits, session-only; saved via capture :662-671). `Camp.prototype.camps()`
    :214 = `this.worldCamps.concat(this.sites)`. `deploy` :502-, the `maxSites` roll at
    :503-:556, `this.sites.push(site)` :578, `packUp` splice :586. The tent-menu el()
    helper and panel classes are private to camp.js :23-28+; chest.js must define its
    own copy (B4 — same law as C10 npc.js). Camp site shape (from save.js :91-95):
    `{ id, regionId, x, z, f: {x,z} }`.

L7  inventory.js (770 lines). `window.WH_Inv` (per file header :9-11: "Inventory
    constructor (one per player; game.js owns the instance); addItem / removeItem /
    countOf / slotAt / forEachSlot -> delegate to active"). Inventory(slotCount) :54-59;
    `slots[i] = null | { id, count }` :52. `addItem(id, count)` :63;
    `removeItem(id, count)` :88-:99; `removeFromSlot(i, count)` :104; `hasRoomFor(id)`
    :115. CC-C11 chest capture()/restore() operates on a bare array-of-slots
    (R-C11.4: `[{id,count} | null] × 24`) and never ships item lists.

L8  npc.js (232 lines). Exports `window.WH_NPC = { init, update, talkPrompt, openDialog,
    closeDialog, questState, restoreQuest }` :223-231. Dialog showLine() :118-124
    (`if (lineIdx === 2 && quest === Q.states[0]) quest = 'active';` :123 = the ONE
    assignment site of 'active'). questState() :201-204; restoreQuest(block) :206-210.
    CC-C11 must EXTEND, not rewrite: keep the exported names above, ADD rescue + daughter
    + completion-line support. Extension seams: additional functions on WH_NPC
    (e.g. `rescuePrompt()`, `tryRescue()`, `tryComplete()` / completion state machine), and
    a completion path replacing the no-'complete' state at :162 (grep confirms zero
    'complete' literals outside CONFIG.quest.states at base).

L9  game.js interact chain. `function interact()` :1876-1881. Guard :1877
    (`inputSuspended || state !== 'alive'`). Chain line :1880: `tryPickup() ||
    lootCorpseNearest(...) || tryCookStation() || tryCampSleep() || tryDenDoor() ||
    tryDoorway() || tryNotch() || tryTalkNpc() || tryGather();` — terms indexed
    `[1 tryPickup, 2 loot, 3 cook, 4 camp, 5 denDoor, 6 doorway, 7 notch, 8 talkNpc,
    9 gather]`. CC-C11 hook H1 = insert `tryRescue()` and `tryChest()` between
    tryTalkNpc (idx 8) and tryGather (idx 9); net chain becomes 11 terms.

L10 game.js npcNear/tryTalkNpc seam. `npcNear()` :1978-1980; `tryTalkNpc()`
    :1982-1985. tryNotch :1969-1976. tryGather :2165-. CC-C11 hooks (H1) install
    `rescueNear()`+`tryRescue()` and `chestNear()`+`tryChest()` next to these,
    inside the same comment fence (CC-C10 :1975 marker).

L11 game.js updateInteractPrompt :2187-2213. Branch ladder: corpse :2193-:2195, cook
    :2196-:2197, camp sleep :2198-:2199, den door :2200-:2201, locked door :2202-:2203,
    notch :2204-:2205, npc :2206-:2207 (`CFG.regionC.npc.dialog.prompt`), gather else
    :2208-:2210. CC-C11 hook H2 = two `else if` branches between the npc branch and the
    gather else — order: rescue first, chest second (mirror of H1).

L12 game.js setupHud :203-225 + questLine. `updateQuestLine()` :197-201 toggles
    `#wh-quest-line` opacity on `WH_NPC.questState() === 'active'` (:198). questLine
    element created :217-:224 with text `CFG.regionC.quest.hudText` :219, inline style
    :220-222, appended to `#wh-hud` :223. CC-C11 replaces the single predicate with
    a 2-state switch (rescued HUD text while 'active'+rescued:true; completion line at
    'complete', R-C11.5 / A4); text keys from CONFIG.regionC.quest (B2).

L13 game.js setupSaveHooks :2582-2638. CC-C7/CC-C10 wrap comment block :2591-2600.
    base trio captured :2602 (`var baseCapture = S.capture, baseSave = S.save,
    baseRestore = S.restore;`). S.capture wrap :2603-2608 (`data.lairs` :2605,
    `data.questState` :2606). S.save wrap :2609-2619 (`stored.lairs` :2614,
    `stored.questState` :2615). S.restore wrap :2620-2624 (`restoreLairs` :2621,
    `restoreQuest` :2622, `baseRestore` :2623). quitPersist :2629-2637. CC-C11 hook
    H5 = add chest capture/restore additive lines INSIDE the same wrapped trio; no
    edits to save.js (PRES).

L14 game.js WH_NPC.init / loop tail. `if (window.WH_NPC) window.WH_NPC.init(game);` :2569.
    Loop tail :3095-3110: `cooking.update` :3101, `camp.update` :3102, `WH_NPC.update(dt)`
    :3103, `updateQuestLine()` :3104, `applyBuffStats` :3105, `updateHud` :3106,
    `updateEnemyBars` :3107, `updateDayClock` :3108, `updateInteractPrompt` :3109,
    `render()` :3110. CC-C11 hook H3 = `if (window.WH_Chest) window.WH_Chest.init(game);`
    immediately after :2569 (next line). H4 = `if (window.WH_Chest)
    window.WH_Chest.update(dt);` immediately after :3103 (before updateQuestLine, so the
    chest's camp-site-derive happens before the quest line reads rescued state).

L15 save.js (301 lines, UNTOUCHED). `capture(game, opts)` :58-103 returns the profile
    object (additive-extra-keys pass through the localStorage JSON; version check at
    load() :121-125 keys on `data.v === S.version` only). `save(game, opts)` :107-.
    `restore(game, data)` :163-. The chest block must ride game.js's wrapped trio
    (`stored.chest = window.WH_Chest.capture()` / `window.WH_Chest.restore(data.chest)`);
    schema stays `v: 1` (R-C11.5 additive).

L16 assets.js MANIFEST :16-159. crypt-kit rows :71-:72 (`stoneSteps`, `skullPile`).
    Character bodies :118-150 (… `rotspawnBody` :150, `farmerBody` :156 — see L17).
    `clone via WHSkeletonUtils.clone` :795; `instance(name)` :805-820; stand-in +
    lateSwap :822-833. CC-C11 inserts exactly TWO keys: `stoneSarcophagus:
    'art-direction/3d/assets/crypt/stone-sarcophagus-pixelated.glb'` (after skullPile
    :72) and `dwarfFemaleBody: 'art-direction/3d/assets/races_regen/rigged/
    dwarf-female.rigged.glb'` (after farmerBody :156). NOT bootCritical (R-C11.2/3).

L17 On-disk GLB (read with `ls -la` at 935db87, both files exist):
    `art-direction/3d/assets/crypt/stone-sarcophagus-pixelated.glb` = 406,160 B
    (paired raw stone-sarcophagus.glb 5,712,432 B — pixelated twin already shipped).
    `art-direction/3d/assets/races_regen/rigged/dwarf-female.rigged.glb` = 5,105,468 B
    (NO pixelated twin in that dir for the dwarf family — R-C11.3 is the art-law
    waiver mirror of the C10 farmer ruling B3b: ship the raw rigged GLB as the
    placeholder, Astrabot replaces later).

L18 tools/build_v8.py: `OUT = P / 'builds' / 'v8-playable.html'` :8 (`P` = repo /
    prototype :6-7); write :33; "wrote" line :34. Tracked file
    `prototype/builds/v8-playable.html` is rebuilt by every order (C10 B8 law = the
    bundle artifact is sanctioned).

L19 scratch/cc-c10/ledger3.py re-run semantics (CC-C11 A7 = "PASS unchanged"):
    ledger3 is regionC-scoped only (props = `cfg['props']` from dump_cfg.js of
    regionC rows + barn + farmer pseudo-row), centres :28 = (0,-366),(-175,-266),
    (150.5,-256.7) at R 170, whole-disc info at R 280. CC-C11 adds ZERO regionC rows
    (sarcophagus is regionD; chest is dynamic camp-side; daughter is npc-side via
    WH_NPC not a props row). So A7 is a re-run of the C10 ledger3.py byte-identical,
    NOT a rebuild — same probe, same T table, same PASS bars.

L20 scratch/cc-c11/tb_den_geom.py (pre-existing helper, IO-dispatched): runs against
    CONFIG.js and prints every regionD.props row with distances from region disc
    centre and ring centroid. Baseline (at 935db87): region disc centre (-186,-180) r 34,
    ring centroid (-155.6, -211.4) r ~23-25, lair row (-185.8,-180.2) dCenter 0.3,
    spawn (-156,-190) dCenter 31.6. CC-C11 probes may reuse / extend it (recommended:
    add a probe-clear sweep in scratch/cc-c11/probe_sarc.js per A2 spec below).

## PRE-DEVBOT SMOKE — EXPECTED (tree = 935db87; static greps at authoring, all MUST show
## the "not built" or "unchanged baseline" pattern; evidence = grep/sed outputs below)

| Check | Expected pre-Devbot | Evidence to capture |
|----|----|----|
| F1 chest.js | ABSENT: `test -f prototype/js/chest.js` false | ls output |
| F2 WH_Chest | ABSENT: `grep -c "WH_Chest" prototype/js/*.js` = 0 everywhere (no hits in any game file) | counts |
| F3 manifest stoneSarcophagus / dwarfFemaleBody | ABSENT: `grep -c stoneSarcophagus prototype/js/assets.js` = 0; `grep -c dwarfFemaleBody prototype/js/assets.js` = 0 | counts |
| F4 CONFIG camp.chest / regionD sarcophagus row / regionC.quest rescue | ABSENT: grep `chest:` / `sarcophagus` / `rescued` / `hudComplete` / `hudRescued` in CONFIG.js = 0 each (regionD.props has no sarcophagus row; regionC.quest has only states+hudText :1193-1196) | counts + sed of :1193-:1197 |
| F5 tryRescue / tryChest in interact() chain | ABSENT: chain line :1880 is exactly `[1 tryPickup, 2 loot, 3 cook, 4 camp, 5 denDoor, 6 doorway, 7 notch, 8 talkNpc, 9 gather]` (9 terms, original order). `grep -cE "tryRescue|tryChest" prototype/js/game.js` = 0 | chain line text + count |
| F6 index.html chest script tag | ABSENT; npc.js :66 immediately followed by save.js :67 (no :66.5 tag) | grep -n |
| F7 rescue / completion in npc.js | ABSENT: `grep -c rescue prototype/js/npc.js` = 0; `grep -c "'complete'" prototype/js/npc.js` = 0 (only `Q.states = ['available','active','complete']` literal in npc.js source); `grep -c daughter prototype/js/npc.js` = 0 | counts |
| F8 chest save-block wrap | ABSENT: `grep -c "WH_Chest" prototype/js/game.js` = 0; `grep -c "stored.chest\|data.chest" prototype/js/game.js` = 0; lairs + questState trio wraps present :2603-2624 baseline | sed of :2602-2624 + count |
| F9 ledger3 re-run baseline | PASS via `python3 scratch/cc-c10/ledger3.py` at 935db87 = C10 last-recorded values (94.78% / 93.81% at the C10 centres); this is the A7 baseline | stdout numbers |
| BOOT | PASS (current): script order L1, `node --check` clean on all existing js, bundle exists | grep L1 + ls of builds/ |
| A1 | FAIL: no sarcophagus / rescue / chest; only tryTalkNpc on the chain; sarcophagus E does nothing because no sarcophagus row exists and no tryRescue seam exists | F3 + F5 |
| A2 | FAIL: no sarcophagus row in regionD.props, no stoneSarcophagus manifest key | F3 |
| A3 | FAIL: no rescue function in npc.js, no rescue dialogue, no rescued state | F7 |
| A4 | FAIL: no completion lines, no hudComplete key, `updateQuestLine` gated on `'active'` only (no rescued / complete branch) | F4 + L12 |
| A5 | FAIL: no WH_Chest, no chest module, no chest save block, no camp.chest | F1 + F2 + F4 + F8 |
| A6 | FAIL: no chest block in save wrap; no rescue in quest restore | F8 |
| A7 | PASS (baseline ledger F9, no regionC rows added) | F9 numbers |
| PRES | PASS: `git diff --stat 935db87 -- prototype io/specs io/reports io/missions` empty except this valspec | stat |

## PER-AC PROBE SPEC (post-build; static + node only — NO Playwright, NO browser, NO
## server, NO harness runs; acceptance of record = Nicko playtest. Every probe = file
## inspection or offline node reader. Probe files live in scratch/cc-c11/.)

Probe notes: the C10 pattern is re-used — node may not be on PATH in this container; the
playwright-bundled node binary is the executor (offline scripts only, no browser).
Validator re-runs every probe the builder cites. Greps/diffs against the worktree; "diff
lines" are `git diff 935db87 -- <path>` (read-only).

### A1 — chain start talk still works (C10 behaviour byte-preserved); sarcophagus E does
### nothing while quest not active

- interact() chain after H1: exactly two new terms (`tryRescue()`, `tryChest()`)
  inserted between tryTalkNpc and tryGather; original 9 terms present in original
  order; guard :1877 unchanged. The CC-C10 line :1880 is the ONLY removed `-` line
  in the game.js diff for that hunk.
- tryTalkNpc / npcNear behaviour unchanged: `git diff 935db87 -- prototype/js/game.js`
  for the function bodies of `npcNear()` and `tryTalkNpc()` = empty (any edit there
  = BLOCK unless it's a comment-only line, recorded).
- updateQuestLine at :197-:201 (C10 baseline): the `'active'`-only predicate is the
  pre-C11 state; post-C11 it MAY grow a second comparison (rescued:true → hudRescued
  key) — RECORD the new predicate body.
- Sarcophagus-no-quest bar (static): grep `tryRescue` body — it MUST return false
  when `WH_NPC.questState() !== 'active'` OR `WH_NPC.questStateDetail().rescued`
  is truthy (any rescued sub-field read pattern is fine; RECORD the exact source).
  Code-path: while quest is 'available' there is no path into the rescue branch.
- Nicko playtest gate: fresh boot → talk to farmer → rescue not yet possible because
  quest is not active until line 3.

### A2 — sarcophagus in the den near the lair, probe-clear, manifest loads, collider solid

- CONFIG: regionD.props gains exactly ONE row with `asset: 'stoneSarcophagus'` (literal
  manifest key from L16). Comment tag `// CC-C11` present. Numeric x, z; rotY, scale
  present. Optional sink `y:` allowed but RECORD.
- Probe-clear (probe file scratch/cc-c11/probe_sarc.js — builder writes, validator
  re-runs; offline require of CONFIG.js + the C10 ledger2_probe stub pattern):
  prints
  (a) sarc x,z, dCenter (must be ≤ 34 − row-clear-pad; RECORD),
  (b) distance to boss lair body = dist((x,z), (-186, -174)); bar: ≥ lair body
  radius (radius 1.1 :1920, body circle) + sarc body radius (computed from manifest
  GLB scale × footprint; RECORD) + a 2.0 m dressing-pool pad → **d_lair ≥ ~3.1 m
  RECORD, recommended ≥ 6 m for the spawn→lair walkway** (see B5),
  (c) distance to the spawn→lair walkway segment from (-156,-190) → (-186,-174);
  bar ≥ 2.0 m (RECORD exact),
  (d) distance to every existing regionD.props row (34 rows, per L3 + L20
  tb_den_geom.py); bar ≥ 1.5 m from every non-whWall row, ≥ 1.0 m + row-clear-pad
  from every whWall row (RECORD min).
- Manifest: MANIFEST stoneSarcophagus path resolves to an existing file
  (`test -f`), byte size = 406,160 B (per L17); sha256 unchanged vs the 935db87
  blob (post-build: `git ls-files --error-unmatch art-direction/3d/assets/crypt/
  stone-sarcophagus-pixelated.glb` + sha256sum read-only diff against the index).
  No new GLB written for the sarcophagus (R-C11.2 pixelated law already satisfied
  on disk).
- Collider: not bootCritical → stand-in box law applies (B10 mirror); the runtime
  prop collider pattern reads from the manifest's per-asset footprint (grep assets.js
  collider path and the existing stoneSteps / skullPile precedent). No whWall-style
  `wall:` integer expected on the sarcophagus row (RECORD whether present).

### A3 — rescue: E at the sarcophagus while active → dialog + rescued:true + toast;
### daughter swap; persists via questState

- npc.js EXTENDED, not rewritten (law R-C11.6): all 7 C10 exports still present
  (`init, update, talkPrompt, openDialog, closeDialog, questState, restoreQuest`).
  Records grep for `window.WH_NPC` :223-:231 baseline → post-build grep diff
  must show ADDED exports only (e.g. `rescuePrompt`, `tryRescue`,
  `questStateDetail` — RECORD actual names).
- 'active' assignment site: still exactly ONE literal `quest = 'active'`
  (was :123 in L8). RECORD its new line number.
- 'complete' assignment: exactly ONE literal `quest = 'complete'` (grep
  `'complete'` in npc.js; the only other hits allowed are in CONFIG-derived state
  array references and comparisons). RECORD its line.
- rescued sub-field: any of (a) `WH_NPC.questStateDetail() ===
  { state, rescued }`, (b) a separate `WH_NPC.rescued()` getter, (c) fields on a
  `questState` object — RECORD which; the persistent shape written to
  `data.questState` in game.js must carry the rescued bit (R-C11.5: additive
  sub-field, NOT a 4th top-level state).
- Daughter swap: grep npc.js for the daughter placeholder pattern (e.g.
  `dwarfFemaleBody`, `daughterRoot`, `shown = here && dist <= cullM` style): there
  must be (a) a chamber-located daughter body visible while quest is active AND
  rescued is false, (b) a farm/homestead-located daughter body visible while
  rescued is true (post-rescue OR post-'complete'), (c) ONE owner — the chamber
  body is REMOVED when rescued flips true (RECORD the code path doing the removal:
  scene.remove, dispose, or visible toggle).
- Toast on rescue: grep npc.js / game.js for a `game.inventoryUI.toast(...)` call
  inside the rescue path, with text from a CONFIG key (RECORD; B6 house style).
- Probe (scratch/cc-c11/probe_rescue.js — offline require pattern): re-reads
  npc.js source and CONFIG.js, prints the rescued state machine transitions and
  the four body-visibility predicates; PASS bars = the predicates above all hold.

### A4 — completion: return talk → 'complete' + completion copy + HUD completion line;
### repeat-line-on-complete GONE (C10 deviation fixed)

- CONFIG.regionC.quest gains (after L2 block:1193-:1196): `hudComplete` (the
  completion HUD text key) + rescued HUD text key (e.g. `hudRescued`); RECORD
  exact key names. regionC.npc.dialog gains `lineComplete` / `lineRescued` (or
  equivalent, RECORD). String literals are CONFIG-only; zero player-facing strings
  in npc.js / game.js (grep for `"..."` textContent assignments = 0 outside
  existing C10 baseline).
- updateQuestLine: predicate switched from `'active'`-only to a state machine
  — 'active' → hudText; 'active' + rescued:true → hudRescued; 'complete' →
  hudComplete. RECORD the new function body (line range) and the predicate.
- repeat-line deviation fix: pre-C11 openDialog at :163 in npc.js sets
  `lineIdx = -1 unless quest is available`, which means repeat currently shows on
  'complete' too (C10 B-note: this WAS the recorded deviation). Post-C11: the
  openDialog path when `quest === 'complete'` MUST show the completion line
  (lineComplete / lineRescued), not the C10 repeat ("The barrow door, hunter.
  Bring her home."). RECORD the new `showLine` case ladder.
- Probe (scratch/cc-c11/probe_dialog2.js — offline): enumerates the dialog
  state machine: available→line1/2/3, active→repeat, active+rescued→completion,
  complete→completion. PASS bar = the C10 'active'-only predicate has been
  replaced AND the complete-state shows the completion line, not the repeat.

### A5 — chest: spawns beside pegs on the FIRST deployed camp after complete; follows
### camp re-placement; 24-slot panel camp-gated; deposit/withdraw both ways

- CONFIG.camp.chest block exists (after L5 :2902 deploy block) with: `offset`
  [right, back] m in the site frame (PROPOSED [2.2, 1.8] per brief R-C11.4; RECORD
  actual), `interactM` (m), `capacity: 24` (R-C11.4), `slotsX: 6, slotsY: 4` RECORD,
  stack rules inherit CONFIG.inventory (no override literal). Comment tag `// CC-C11`.
- chest.js exists, exports `window.WH_Chest = { init, update, interactPrompt,
  tryOpen, capture, restore }` (R-C11.6; RECORD actual export list; minimum = those
  six names as properties). `node --check` on chest.js = 0.
- Spawn rule: chest body is built/revealed ONLY when `WH_NPC.questState() ===
  'complete'` AND `WH_Camp.camps()` (L6 :214) returns at least one deployed site;
  chest position derives from the deployed-site record's pegs module spot (the
  CONFIG.camp.modules entry pegs offset [0, 3.6] :2875) translated by the new
  CONFIG.camp.chest.offset. Probe (scratch/cc-c11/probe_chest.js, offline): reads
  chest.js source + CONFIG, prints the derive function body. PASS bar = grep finds
  `camps()` (or `sites` iteration with the worldCamps concat) AND the pegs offset
  [0, 3.6] AND the chest offset — no hardcoded world x,z for the chest anchor.
- Re-place-safe: chest.js reads `camps()` per frame inside `update(dt)` (grep for
  the call site) — NOT a one-time anchor on init (law R-C11.4).
- Camp-gated interact: `tryOpen` / `interactPrompt` returns false when the player
  is > CONFIG.camp.interactRadius (L5 :2847) from ANY deployed camp site (RECORD
  which radius the chest actually uses: its own `chest.interactM` or camp
  `interactRadius`; the brief says "within camp interactRadius of a deployed site"
  → bar = a `camps()` distance check exists, radius key from CONFIG).
- 24-slot panel: 6×4 DOM grid, tent-menu styling pattern (the camp.js :236-259
  classes — `inv-panel`, `inv-title`, `cook-btns`, `cook-btn`, `inv-hint` — are
  reused via chest.js's own `el()` copy; camp.js is OUT of write scope). Grep for
  the slot grid construction; PASS bar = 24 slot cells, classes above.
- Deposit/withdraw: grep chest.js for calls into WH_Inv (L7): `addItem`,
  `removeItem` (or `removeFromSlot`). Chest slots are a local array of 24
  `{id, count} | null` rows (RECORD container shape). Bidirectional = grep shows
  BOTH directions: deposit path (player → chest via `Inventory.removeFromSlot` +
  chest slot push) and withdraw path (chest → player via chest slot clear +
  `Inventory.addItem`). Interactive semantics = Nicko playtest.
- Persistence: chest capture returns an array of 24 slot rows (no item-list
  shipping, R-C11.4); restore hands it back. Grep `capture()` and `restore()`
  bodies. Schema additive (L13).

### A6 — save/load: questState (complete + rescued) + chest slots + daughter visual
### all persist; older profile without the chest block loads clean

- setupSaveHooks (L13 :2602-2624): additive edits only. PASS bars (diff against
  935db87 shows zero `-` lines inside the wrapped-trio region):
  (a) S.capture wrap gains `if (window.WH_Chest) data.chest =
      window.WH_Chest.capture();` next to the questState line.
  (b) S.save wrap gains `if (window.WH_Chest) stored.chest =
      window.WH_Chest.capture();` inside the same try.
  (c) S.restore wrap gains `if (data && window.WH_Chest)
      window.WH_Chest.restore(data.chest);` before or after `restoreQuest`
      (RECORD order).
  (d) questState block now carries the rescued sub-field (per A3): grep
      `data.questState = { findDaughter: ... }` shows the new shape; RECORD.
- Older-profile-clean bar: restore body tolerates `data.chest === undefined`
  (grep for the guard); `WH_NPC.restoreQuest(undefined)` still falls back to
  'available' (was L8 baseline; RECORD it still does). No save.js diff.
- Daughter visual persistence: daughter body visibility (per A3 probe) is a
  pure function of `WH_NPC` rescued state, so restore of the rescued bit restores
  the visual (RECORD the code path that ties visibility to rescued on restore).
- Probe (scratch/cc-c11/probe_save.js — offline): reads game.js wrapped trio +
  save.js, prints the new wrap lines and the guard pattern; PASS bars above.

### A7 — ledger3 re-run PASS unchanged (regionC disc untouched)

- Run `python3 scratch/cc-c10/ledger3.py /tmp/wh-worldfeat` (per L19 — the
  builder does NOT write a new ledger for C11). Expected = the C10 last-recorded
  numbers, byte-equal stdout (94.78% / 93.81% / homestead %) and `LEDGER PASS`.
- PASS bar: zero new regionC rows (sarcophagus is regionD; chest is dynamic;
  daughter is npc-side via WH_NPC, not a props row). Static: `git diff 935db87 --
  prototype/js/CONFIG.js` shows zero edits inside the `regionC.props` block
  (lines :798-:1126 baseline) AND zero edits to `regionC.enemies`, `regionC.nodes`,
  `regionC.spawn`.
- RECORD the full stdout on the post-build re-run (any change in the three centre
  numbers or the whole-disc info line = BLOCK).

### FILE-LEVEL / BUILD / PRESERVATION (PRES)

- `node --check` exit 0 on every touched js: prototype/js/{chest.js (new), npc.js,
  CONFIG.js, assets.js, game.js} plus every scratch/cc-c11/probe_*.js.
- index.html diff = exactly +1 line `<script src="js/chest.js"></script>` between
  `js/npc.js` :66 and `js/save.js` :67 (post-build: npc.js :66, chest.js :67,
  save.js :68); zero removed lines.
- CONFIG.js diff = additions only (`grep -c '^-[^-]'` = 0 on the diff), inside:
  (a) regionC.npc.dialog sub-block + regionC.quest block (rescued/completion
  keys), (b) regionD.props (the ONE sarcophagus row), (c) CONFIG.camp (the new
  `chest` sub-block). regionA, regionB, every pre-existing regionC row, regionD
  rows other than the one new sarcophagus, and CONFIG.camp's other keys
  byte-identical.
- assets.js diff = additions only inside MANIFEST: exactly 2 new keys
  (`stoneSarcophagus`, `dwarfFemaleBody`) + their comment lines. No BODY_PNG edit.
  No CHARACTERS edit. `bootCritical` list untouched.
- game.js diff confined to hunks H1-H5: H1 interact chain line + new `tryRescue` /
  `tryChest` functions (next to the C10 tryTalkNpc fence :1975); H2
  updateInteractPrompt branches; H3 `WH_Chest.init` call after :2569; H4
  `WH_Chest.update` call after :3103; H5 save-wrap additive lines. Removed `-`
  lines allowed ONLY at the chain line :1880 and at the `updateQuestLine`
  predicate :198 (which is extended for rescued/complete). Any other removed line
  = scope FAIL.
- npc.js diff = additions only (extension seams only, R-C11.6); the original 7
  exports stay; zero `-` lines except comment-only edits (RECORD each).
- Byte-identical vs 935db87: prototype/js/{save.js, camp.js, enemy.js, player.js,
  cooking.js, daynight.js, wh-ground.js, region-manager.js, region-defs.js,
  anim.js, corpse-loot.js, gather.js, icons-data.js, leveling.js, light.js,
  moveset.js, spells.js, touch-controls.js, wolf-debug.js, inventory.js},
  prototype/style.css, prototype/vendor/**, scratch/cc-c17/**, scratch/cc-c10/**,
  art-direction/** (the two GLBs already on disk; no new GLB files).
- `git diff --stat 935db87` + porcelain = subset of: prototype/js/{chest.js
  (new file), CONFIG.js, assets.js, npc.js, game.js}, prototype/index.html,
  prototype/builds/v8-playable.html (B8 mirror — build artifact, tracked),
  scratch/cc-c11/**, io/reports/2026-10-25-cc-c11-*.md, io/specs/
  testerbot-spec-wh-cc-c11-rescue.md. Anything else = BLOCK. Builder made no
  commits: `git log -1 --format=%h` still 935db87.
- Bundle: `python3 tools/build_v8.py` ran; `prototype/builds/v8-playable.html`
  mtime newer than the js edits; `grep -c "WH_Chest\|stoneSarcophagus\|
  dwarfFemaleBody" prototype/builds/v8-playable.html` ≥ 3; byte size RECORD
  (finish-line <bytes>).
- Report: io/reports/2026-10-25-cc-c11-rescue-chest.md exists, states the
  sarcophagus row x/z/rotY/scale + probe-clear distances (to lair body, to
  walkway, to nearest regionD row), the chest offset + interactM + capacity
  literals actually used, the rescued + complete state-machine diff, ledger3
  stdout, bundle bytes, finish line.
- Grep markers: `// CC-C11` comment tag on every new CONFIG / assets / game.js /
  npc.js / chest.js hunk.
- Placeholder law: no Astrabot / Meshy calls (no new treegen or meshy logs in
  scratch/); no NEW GLB written (the two GLBs on disk at L17 suffice per
  R-C11.2/3).
- Finish-line format (builder's final message):
  `CC-C11 DONE rescue daughter chest ledger PASS build <bytes>`.

## VERDICT PROTOCOL

**PASS** iff every F-pin flips (chest.js exists, WH_Chest + tryRescue + tryChest
present, stoneSarcophagus + dwarfFemaleBody manifest keys, the sarcophagus
regionD row, the camp.chest sub-block, the rescued/complete CONFIG keys, the
index.html script tag, the additive save-wrap lines for both questState-detail
and chest), every A1-A7 static bar holds, `node --check` all green, ledger3
re-run PASS byte-equal, PRES PASS.

**BLOCK**: any scope violation; any git mutation by the builder (any commit, any
push, any unstash); any removed line in the wrapped-trio save-wrap region other
than the chain line + updateQuestLine predicate; any edit to save.js / camp.js /
enemy.js / player.js / cooking.js / style.css / touch-controls.js /
region-manager.js / region-defs.js / wh-ground.js / assets.js outside MANIFEST /
prototype/vendor/ / scratch/cc-c10/ / scratch/cc-c17/; any harness/browser/
playwright artifacts (tests/ files, .playwright/, server logs); any new GLB
written outside the two files at L17 (which themselves must be byte-stable).

Static PASS = "ready for Nicko's playtest", never "accepted"; A1-A7 acceptance
of record = Nicko playtest.

## AMENDMENT NOTES (brief vs live tree 935db87; I own the bars, IO owns rulings)

B1. **Walkway anchor ambiguity — spawn→lair line segment.** The brief says
    "outside the spawn→lair walkway." At 935db87: spawn = regionD.spawn
    (-156, -190) :1221; lair body centre = world (-186, -174) per L4
    (-186+lair.x 0, -180+lair.y 6). The walkway segment is the straight line
    between those two points. A2's probe-clear bar (c) uses that line segment,
    2.0 m minimum perpendicular distance. RECORD the actual computed distance;
    if the chosen row is ever pulled < 2.0 m to the line, that is a probe-clear
    FAIL, not an amendment.

B2. **HUD text keys: names are PROPOSED, content Nicko-tunes.** The brief says
    "regionC.quest gains completion lines + rescued HUD text keys" without
    fixing names. L2 lists the existing `hudText` only. A4 records the actual
    key names (`hudRescued` / `hudComplete` / `hudRescuedText` — any of these
    or house style accepted) and the actual string literals; both come from
    CONFIG. The C10-predicate `questLine.textContent = CFG.regionC.quest.hudText`
    :219 will need to become state-aware; the element and its style stay
    byte-identical except the textContent binding. Copy = Nicko tunes; not a
    gate.

B3. **Daughter removal mechanics ambiguity.** R-C11.1 says "the daughter
    placeholder REMOVES from the chamber and appears standing beside the farmer
    at the homestead (she is safe at home when you return). No follower AI, no
    walk-out pathing." Static interpretation I validate (not an IO re-litigation,
    just a binding reading): (a) ONE daughter body owner (WH_NPC), (b) visible
    while `quest === 'active' AND rescued === false` AT the den (chamber), (c)
    visible while `rescued === true` (any quest state) AT the homestead beside
    farmer (CONFIG.regionC.npc x,z :1169), (d) removal = visible:false or
    scene.remove on rescue, not a tween / pathing. A3's probe bars are written
    against this reading. If the builder instead spawns TWO bodies and toggles,
    that is accepted too — RECORD.

B4. **chest.js cannot share camp.js's private helpers.** camp.js :23-:28 `el()`
    is IIFE-private (not exported); the same is true of the camp panel builders.
    Per C10 law (B5 mirror), chest.js must define its own `el()` copy and its
    own inline-style overlay root; reusing only the camp.js class names
    (`inv-panel`, `cook-btns`, `cook-btn`, `inv-title`, `inv-hint`) which are
    styled in style.css (OUT of write scope, so the inline-overlay rule still
    holds for the chest root). RECORD the chest root id and inline style.

B5. **Disc-edge clamp + probe-clear radii are derivations, not brief literals.**
    CONFIG.regionD.groundRadius = 34 :1215. The worldMargin / playerMargin law
    (world.js :120-:121) reads ~1.5 m. So the sarcophagus row must satisfy
    dCenter ≤ 32.5 (RECORD actual). The lair body + dressing pool + walkway
    radii I use are: body radius = CONFIG.enemy.rotmother.radius :1920 (1.1 m),
    the nest dressing pool radius = CONFIG.regionD.rotLair.pool.radius :1316
    (10 m) — the sarcophagus distance from (-186,-174) must be ≥ pool radius +
    sarc body radius + 1 m pad → **d_lair ≥ 12.5 m is the binding bar** (I
    record the brief's "outside the lair dressing pool" as binding; RECORD
    actual distance). Walkway = 2.0 m perpendicular-distance minimum. If the
    builder's row is probe-clear on dCenter ≤ 32.5 AND d_lair ≥ 12.5 AND
    d_walkway ≥ 2.0 AND d_prop ≥ 1.5 (non-wall) / ≥ 1.0 (whWall), that is A2
    PASS.

B6. **Toast surface: game.inventoryUI.toast is the house pattern.** game.js
    :1811, :1856, :1860, :1957, :1971 use `game.inventoryUI.toast(text)` (or
    the CFG-driven variants). No chest-specific toast helper exists. The rescue
    toast comes from a CONFIG key (e.g. CONFIG.regionC.quest.rescuedToast or
    CONFIG.npc.chest.text — any of these, RECORD) and goes through
    `game.inventoryUI.toast`. Static bar: grep finds the toast call inside the
    rescue path with a CONFIG ref, not a literal.

B7. **chest capture/restore shape.** R-C11.4: "capture()/restore() = slots
    arrays only (never shipped item lists)." I validate: capture() returns an
    Array(24) of `null | { id, count }` rows (matching Inventory slot shape,
    L7); restore(slots) writes that array into the chest model and is a no-op
    on `undefined` (L13 law). No calls into WH_Inv.addItem / removeItem during
    capture or restore (those are runtime operations, not save-load
    operations); if any are present, RECORD and reason.

B8. **tools/build_v8.py writes a tracked file (prototype/builds/
    v8-playable.html).** C10 B8 law (sanctioned build artifact) applies
    verbatim. The bundle is rebuilt and the new byte size appears in the
    finish line.

B9. **Prompt style: "E - Open the chest" / "E - Chest" / house either accepted.**
    The C10 B9 house style is `'<Key> - <Verb>'` with the key literal ("E - Talk
    to Farmer Aldric" :1187). Any of "E - Chest", "E - Open the chest",
    "E - Search the sarcophagus" (rescue prompt) accepted; RECORD the CONFIG
    literals used.

B10. **Bind-pose daughter is fine for v1.** R-C11.3 waives the pixel bake and
    the mixer (the dwarf rigged GLB ships stand-in-box + lateSwap; bind pose
    is the C10 farmer B10 equivalent). The daughter body will likely stand in
    A/T pose with no clips running — RECORD for Nicko, not a builder fault.

B11. **`'complete'` repeat-line deviation = the C10 leftover.** The C10
    validation (io/reports/2026-10-25-cc-c10-farmer-validation.md:73)
    documents openDialog's repeat-line showing on 'complete' as a known
    short-fall (repeat is the "else" branch). R-C11.5's "this ALSO fixes the
    C10 deviation" is therefore binding on CC-C11 — the A4 bar (complete-state
    shows completion line, not repeat) is the recorded fix. The completion
    line is shown instead of the repeat exactly when `quest === 'complete'`.

B12. **Hook position H1 between tryTalkNpc and tryGather, binding.** The brief
    at line 67 says "tryNotch || tryTalkNpc || tryRescue || tryChest ||
    tryGather" — I record that as the binding chain order (talk → rescue →
    chest → gather). The chest follows the rescue so a single E tap near both
    a completing-farmer and a chest cannot open the chest before the talk
    completes; the order also keeps gather last. updateInteractPrompt (H2)
    mirrors: npc branch :2206 : then rescue : then chest : then gather else.
    RECORD the line numbers on the post-build diff.

B13. **chest.js is the FIRST chest implementation in the codebase.** There is
    no prior chest module (grep `WH_Chest` and `tryChest` = 0 at F1/F2/F5). The
    brief's R-C11.6 list of exports (`init, update, interactPrompt, tryOpen,
    capture, restore`) is binding; the names and the arity are what I grep for.
    RECORD actual export list on the post-build diff.

B14. **A7 "PASS unchanged" = ledger3 re-run, not a rebuild.** L19 + L20. The
    brief's A7 wording is binding: no ledger3.py edit, no ledger3_probe.js
    edit, no new T rows (sarcophagus is regionD which is outside the ledger's
    regionC scope; chest is dynamic; daughter is npc-side). The stdout numbers
    must be byte-equal to the C10 last-recorded values at the three centres.
