# TESTERBOT SPEC — Witch Hunter CC-C10: Farmer NPC + Dialog UI + Quest Seed (gate step 2)

Author: Testerbot gate step 2 (independent validator-author). Date: 2026-10-25.
Devbot spec of record: io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md (IO-authored, read-only;
mismatches with the live tree are amendment notes B1..Bn below, never patched in the brief by me).
Tree at authoring: e3444ec (feat/world-visuals, worktree /tmp/wh-worldfeat; `git log -1 --format=%h`
= e3444ec). `git diff --stat e3444ec -- prototype` = empty at authoring (clean code base). All CC-C10
diffs are measured against e3444ec. Pre-existing untracked: scratch/cc-c10/{testerbot-valspec-prompt.md,
valspec-run1.log} (IO dispatch files, not builder output), scratch/cc13b-*, scratch/extract_rows.cjs.
Process law: doc 62 §13 (one order, NO harness runs, syntax checks only, Nicko playtests);
doc 63 CC-C10 (placeholders first, Astrabot flagged not dispatched, questState additive save block).

## LIVE ANCHORS (line-verified by reading the files at e3444ec)
L1  prototype/index.html (71 lines): `<script src="js/camp.js">` :65, `<script src="js/save.js">` :66 ->
    npc.js insertion point = new line between :65 and :66 (the only sanctioned index.html hunk).
    `<div id="wh-gate-hint">Enter the Darkwood</div>` :27 inside #wh-hud (:12-41). game.js last :70.
L2  game.js setupHud :196-207; `gateHint: document.getElementById('wh-gate-hint')` :201;
    gatherPrompt (the interact prompt element) :202.
L3  game.js setGateHint(visible, text) :519-525 — owns #wh-gate-hint textContent per frame (A/B gate,
    B/C door hints). The quest line must NOT reuse this element (B5).
L4  game.js interact() :1859-1864; chain at :1862-1863 =
    [1 tryPickup, 2 lootCorpseNearest, 3 tryCookStation, 4 tryCampSleep, 5 tryDenDoor, 6 tryDoorway,
    7 tryNotch, 8 tryGather]. HOOK POINT = new term between index 7 (tryNotch) and 8 (tryGather)
    (B12). Guard :1860 (inputSuspended / not alive -> false) stays first.
L5  game.js tryDoorway :1938-1942, locked toast :1940 `CFG.regionC.door.text.locked` (B/C arch);
    lockedDoorNear :1934-1936. tryDenDoor :1876-1885 + denDoorNear :1872-1874 + startDenFade/
    denFadePeak/endDenFade/denFadeTick :1891-1929 (CFG.regionD.door, the SW den = quest target).
L6  game.js updateInteractPrompt :2158-2185 (mirrors interact()); branches: corpse :2165, cook
    :2167, camp :2169, den door :2171, locked door :2173, notch :2175-2176, gather else :2177-2180;
    element write :2182-2184. Talk-prompt branch point = after notchNear :2176, before the gather
    else :2177 (B4).
L7  E key -> interact(): keydown listener :1826-1831 (CFG.inventoryUI.pickupKey; camp placement
    first :1829). Touch USE: touch-controls.js :614-616 -> WH_DEBUG.interact (game.js :2345) -> the
    same interact() chain. No touch-controls.js edit is needed or allowed.
L8  game.js setupSaveHooks :2549-2597. CC-C7 lairs comment :2558-2562; base trio captured :2563-2564
    (`var baseCapture = S.capture, baseSave = S.save, baseRestore = S.restore;`); S.capture wrap
    :2565-2569 (`data.lairs = ...` :2567); S.save wrap :2570-2579 (stored re-write :2573-2576,
    `stored.lairs` :2575); S.restore wrap :2580-2583 (`restoreLairs(data.lairs)` :2581 then
    baseRestore :2582). quitPersist :2588-2593 calls WH_SAVE.save (= the wrapped save).
L9  Restore callers: setupSaveHooks() invoked at :2481 (before both callers); camp LOAD
    profile.restore :2534 `window.WH_SAVE.restore(game, window.WH_SAVE.load(game))`; boot CONTINUE
    (C4 boot restore path) :2696 same call. Both resolve WH_SAVE.restore at call time -> wrapped.
L10 save.js: load() :121-125 returns the parsed object iff `data.v === S.version` (extra keys like
    lairs / questState pass through untouched); restore(game, data) :163ff; capture :58; save :107.
    CONFIG.save :1636, version: 1 :1638. Death path: respawnPlayer does not call restore/load
    (grep of its body: no restore/load/quest) -> quest state survives death if held in memory.
L11 game.js loop :2892-3066; tail: cooking.update :3060, camp.update :3061, updateHud :3063,
    updateInteractPrompt :3065, render :3066. WH_NPC.update(dt) call site = in this tail (B4).
L12 game.js game.camp = new WH_CAMP.Camp :2517; panel input-suspend pattern onOpenChange
    :2526-2529 (`game.inventoryUI.blocked = open; game.player.setInputSuspended(open);`), same as
    cooking :1813-1816. WH_NPC.init(game) call site = after :2517 (camp built, region manager live).
L13 camp.js el(tag, cls, text) :23-28 (IIFE-private, NOT exported); tent menu section header :236,
    buildMenu :238-262 (root id wh-camp-menu, `inv-panel camp-menu-panel` :242, `inv-title` :244,
    `cook-btns camp-menu-btns` :245, `cook-btn camp-menu-btn` buttons :251, `inv-hint` :259,
    appended to #wh-root :260); setMenu :265-273; Esc handler :647.
L14 style.css: #wh-gate-hint :150-165 (bottom 18%, centered, opacity toggled by .visible);
    .inv-panel :583; #wh-gather-prompt :1065/.visible :1081; .cook-btns :1153; #wh-camp-menu
    :1334-1350 (ID-scoped overlay: display none -> flex on .open, z-index 20). style.css is OUT of
    write scope (B5).
L15 CONFIG.js: regionA :156-366, regionB :368-468 (A/B byte-identity range); regionC :470-1150
    (door :540-562 with text :556-561; notchText :564-568; enemies :575-634; terrain :719; props
    :798-1126, last row :1125, `],` :1126; rotLair :1138-1149; regionC close `},` :1150);
    regionD :1163, regionD.door :1189. CC-C17 FARM HOMESTEAD rows :1061-1086 (cottage :1073 at
    (150.5,-256.7) rotY 3.15; well :1074; gate :1075; posts/corners/stonewalls :1076-1085;
    lanternPost :1086), all cullM 120. INSERTION AREA: regionC.npc + regionC.quest = new keys after
    rotLair's close :1149 and before regionC's close :1150; barn row = appended inside props before
    :1126 (or directly after the farm block :1086).
L16 assets.js MANIFEST :16-159; CC-C17 old_king block comment :103-106 + keys :107-116 (okFarmBarn
    insertion = after okRuinColumn :116); character bodies :118-150 (farmerBody insertion area,
    e.g. after rotspawnBody :150); BODY_PNG :162-166 (out of scope: MANIFEST keys only);
    CHARACTERS :209 (no farmerBody row expected); clone via WHSkeletonUtils.clone :795;
    instance(name) :805-820 (stand-in + lateSwap :822-833 while in flight); WH_ASSETS :836.
L17 wh-ground.js heightAt(regionId, x, z) :294, footY(regionId, x, z, r) :305, exported :373.
L18 scratch/cc-c17/ledger2.py (40 lines): c17 slice = every regionC row after the last
    banditCampfire (:20); tally `T[a]` :22-23 (KeyError on any asset absent from T); CAP 1,980,000
    :14; centres (0,-366) and (-175,-266) R 170 :28; whole-disc R 280 info :34.
    ledger2_probe.js: T table :20-28 (NO okFarmBarn, NO farmerBody), extra-rows hook argv[6] :32,
    `missing` :33 (non-empty -> FAIL), per-prop cull `p.cullM || CULL` :54. Last recorded:
    94.78% / 93.81% (58ea081 commit msg).
L19 Assets on disk: art-direction/3d/assets/races_regen/rigged/dwarf-male-smith.rigged.glb
    4,275,044 B, NO pixelated twin in that dir (rigged dir has only the 3 R4 PNGs + wolf .pixelated);
    art-direction/3d/assets/old_king/ok-farm-barn-pixelated.glb 1,000,080 B (committed 58ea081, no
    manifest row; IO tri table 29.5k: io/missions/2026-10-20-cc-c17b-integration-v2.md:20).
L20 tools/: NO GLB pixelate pipeline (only io_icon_pixelize.py); precedent = scratch/cc-c17/
    intake_pixelate.py (old_king-specific, 512 NEAREST + 5-bit, outputs to old_king/).
L21 tools/build_v8.py OUT = prototype/builds/v8-playable.html (:8, write :33); that file is TRACKED
    and rebuilt by every prior order (58ea081 stat).
L22 "Barrow": grep -i barrow over CONFIG.js / region-defs.js / game.js = 0 hits. The quest target
    door in code is CFG.regionD.door (Rot Mother's den, CC-C8), mouth pool (-167.8,-199.6) :1141.

## PRE-DEVBOT SMOKE — EXPECTED (tree = e3444ec; the captured run is authoritative)
| Check | Expected pre-Devbot | Evidence to capture |
|----|----|----|
| F1 npc.js | ABSENT: `test -f prototype/js/npc.js` false | ls output |
| F2 manifest farmerBody | ABSENT: `grep -c farmerBody prototype/js/assets.js` = 0 | count |
| F3 manifest okFarmBarn | ABSENT: `grep -c okFarmBarn prototype/js/assets.js` = 0 | count |
| F4 CONFIG regionC.npc / quest | ABSENT: grep `npc: {` / `quest: {` / `findDaughter` / `Farmer Aldric` in CONFIG.js = 0 each | counts |
| F5 save wrap questState | ABSENT: `grep -c questState prototype/js/game.js` = 0 (lairs trio present :2565-2583) | count + sed of :2563-2583 |
| F6 index.html npc tag | ABSENT; camp.js :65 immediately followed by save.js :66 | grep -n |
| F7 HUD quest line | ABSENT: no quest-line element/ id in game.js or index.html | grep |
| F8 ledger | PASS via ledger2.py (no barn row): 94.78% / 93.81% (reproduce; record exact) | stdout (node path, see Probe notes) |
| A1 | PARTIAL: farmstead rows present :1061-1086 (PASS/unchanged); farmer ABSENT -> FAIL | row count 14 farm rows |
| A2 | FAIL: no talk branch in interact() :1862-1863 nor updateInteractPrompt | chain line text |
| A3 | FAIL: no dialog panel / dialog strings | grep |
| A4 | FAIL: no quest HUD line | grep |
| A5 | FAIL: no questState in capture/save/restore | F5 |
| A6 | PASS (baseline): tryDoorway :1938-1942 + tryDenDoor :1876-1885 + CFG.regionC.door :540-562 + CFG.regionD.door :1189ff | sha256 of those line ranges (baseline for post-build compare) |
| A7 | PASS (baseline ledger F8); no barn row | F8 numbers |
| PRES | PASS: `git diff --stat e3444ec -- prototype io/specs io/reports` empty except this valspec | stat |

## PER-AC PROBE SPEC (post-build; static + node only — NO Playwright, NO tests/ files, NO browser,
## NO server; acceptance of record = Nicko playtest. Every probe = file inspection or offline node.)

Probe notes: node may not be on PATH in this container — resolve the playwright-bundled node binary
and use it for `node --check` and the ledger (offline scripts only, no browser). All greps run
against the worktree; "diff" = `git diff e3444ec -- <path>` (read-only).

### A1 — Farmstead reachable, farmer footY correct, cull band correct
- CONFIG: regionC.npc block exists inside regionC (after :1149, before regionC close) with keys
  asset === 'farmerBody', numeric x, z, rotY, interactM (2.5 <= interactM <= 4; brief "~3"), name
  string 'Farmer Aldric', dialog sub-block (A3). Farmer (x,z) within 25 m of the cottage
  (150.5,-256.7) and >= 1.5 m from every regionC.props row (no clipping into fence/well; RECORD min).
- Footing: npc.js places the root via WH_GROUND.heightAt or footY(regionC.id, x, z[, r]) (grep in
  npc.js), not a literal y. Offline node probe (builder writes scratch/cc-c10/probe_npc.js on the
  ledger2_probe window-stub pattern; validator re-runs): prints heightAt at the farmer x,z, slope
  over a 1 m ring (RECORD; <= 20 deg expected), nearest-prop distance, distance to C centre (<= 270).
- Region gating: npc.js only shows / interacts while regionManager.logic.activeId === regionC.id
  (grep); farmer mesh hidden or disposed outside C. Farmer cull: visible only within
  CFG.regionC.cullDistanceM or an explicit npc cullM (RECORD which; must not be infinite).
- Asset: MANIFEST farmerBody points at an existing file (`test -f`); per B3, either the sanctioned
  `dwarf-male-smith.rigged.pixelated.glb` (texture <= 512, NEAREST; builder report records dims +
  sha256 of the raw source unchanged) OR the raw rigged.glb with the art-law flag in the report.
  Raw source GLB sha256 unchanged vs e3444ec blob in all cases.

### A2 — "Talk (E)" prompt + E / USE opens the dialog
- interact() chain: diff of :1862-1863 = exactly one new term inserted between tryNotch() and
  tryGather() (e.g. `tryTalkNpc()`), all 8 existing terms present in the original order; guard
  :1860 unchanged. The new try* function returns false when WH_NPC absent / out of range / not in C.
- updateInteractPrompt: one new `else if` branch after notchNear (:2175-2176) and before the gather
  else, text from CONFIG (regionC.npc.dialog / text), no literal string in game.js. Bar: CONFIG prompt
  string contains "Talk" and "E" (B9: "Talk (E)" literal or house "E - Talk ..."; RECORD).
- Range: talk test uses interactM from CONFIG (grep `interactM` in npc.js); squared or hypot
  distance on x/z.
- Touch: no touch-controls.js diff; USE reaches the hook via WH_DEBUG.interact (L7).
- Input: dialog open calls player.setInputSuspended(true) + inventoryUI.blocked = true; close
  reverses both (grep in npc.js, L12 pattern). While a dialog is open, interact() returns false
  (guard :1860) so E cannot re-open/advance through the chain — advancing is the panel's button
  (or an npc.js key listener scoped to the open panel; RECORD).

### A3 — 3 lines progress, quest activates on line 3, panel closes
- CONFIG.regionC.npc.dialog holds >= 4 strings: line1 (greeting + daughter taken), line2 (Barrow +
  direction hint), line3 (activation), repeat line (exact brief text "The barrow door, hunter.
  Bring her home." or IO-tuned), plus button labels Continue / Close. npc.js contains zero
  player-facing string literals (grep for quoted words in textContent assignments = CONFIG refs only).
- npc.js dialog: DOM built with a local el() (camp.js :23-28 copy) using classes inv-panel,
  inv-title, cook-btns, cook-btn (L13); root appended to #wh-root; root overlay styled inline
  (B5; no style.css diff). Line index advances on Continue; on the line-3 step the quest state is
  set 'active' exactly once (grep: single assignment site of 'active'); Close -> closeDialog().
- State-aware re-talk: when findDaughter === 'active', openDialog shows the repeat line (+ Close),
  never re-runs lines 1-3 (code-path inspection).
- Completion NOT wired: no assignment of 'complete' anywhere in npc.js / game.js (grep
  `'complete'` = only CONFIG.regionC.quest.states).
- Esc closes the dialog (RECORD; camp.js :647 pattern) and death/region change force-closes it
  (input never left suspended: grep that update() closes on player.state !== 'alive').
- WH_NPC surface: window.WH_NPC exposes init, update, talkPrompt, openDialog, closeDialog (grep
  each name as a property of the exported object).

### A4 — HUD quest line while active
- A new element (id e.g. wh-quest-line) created in JS (setupHud area :196-207 or npc.js), appended
  to #wh-hud, positioned just under #wh-gate-hint (inline style; RECORD bottom %). #wh-gate-hint
  and setGateHint :519-525 byte-identical.
- Visibility toggled per frame strictly on `findDaughter === 'active'` (single predicate site);
  text from CONFIG (brief literal "Find the farmer's daughter — Old King's Barrow (SW)", em dash or
  ASCII ' - ' accepted, B11). Hidden in 'available' and 'complete'.

### A5 — Save at camp, reload: quest still active, re-talk shows the short line
- game.js save wrap (:2563-2583 region), additive only (no '-' lines in that region):
  (a) S.capture wrap adds `data.questState = { findDaughter: <state> }` next to data.lairs;
  (b) S.save wrap adds `stored.questState = ...` next to stored.lairs inside the same try;
  (c) S.restore wrap hands data.questState to the quest holder BEFORE or AFTER baseRestore (RECORD)
      with schema-v1 fallback: missing / non-object / state not in CONFIG.regionC.quest.states ->
      'available'. The comment block names CC-C10 like the CC-C7 one.
- One source of truth: capture, HUD and restore all read/write the same holder (WH_NPC state or
  game.questState; RECORD which). NEW GAME (no restore) starts 'available' (in-memory default).
- Paths covered by construction (static): camp LOAD :2534, boot CONTINUE :2696 (C4 boot restore
  path), quitPersist :2592 — all go through the wrapped trio (L9). save.js byte-identical.
- Death: no quest reset in respawnPlayer or the death flow (grep questState/findDaughter outside
  the sanctioned sites = 0).
- Live A5 = Nicko playtest (save at camp -> reload -> CONTINUE -> HUD line + repeat line).

### A6 — Barrow door NOT changed
- sha256 of game.js line blocks tryDoorway/lockedDoorNear and tryDenDoor/denDoorNear/fade helpers,
  and of CONFIG regionC.door :540-562 + regionD.door block, == the pre-Devbot smoke baseline
  (content-hash of the function bodies, line numbers may shift). `CFG.regionC.door.text.locked`
  still the :1940 toast. region-manager.js / region-defs.js byte-identical.

### A7 — fps holds at the homestead (ledger PASS, barn culled past fog)
- Barn row: exactly ONE new `asset: 'okFarmBarn'` row in regionC.props, cullM: 140, rotY present,
  scale present, comment tag `// CC-C10`. Probe (scratch/cc-c10/, builder-written, validator re-run):
  barn >= 26 m from every other regionC.props row and every banditCampfire/camp fire, >= 8 m from
  road centrelines, seat slope RECORD; within 60 m of the cottage (homestead cluster).
- MANIFEST okFarmBarn === 'art-direction/3d/assets/old_king/ok-farm-barn-pixelated.glb' (file
  exists, sha256 == 58ea081 blob).
- Ledger (B7): run scratch/cc-c10/ledger3.py (copy of ledger2 + probe with T.okFarmBarn = max(29500,
  GLB header) and farmerBody pseudo-row via the argv[6] hook, T.farmerBody = GLB header tris). Bars:
  `missing` empty; worst <= 1,980,000 at (0,-366) R170 AND (-175,-266) R170 AND homestead
  (150.5,-256.7) R170; whole-disc R280 RECORD. The original ledger2.py is NOT edited
  (scratch/cc-c17 byte-identical). Report the 3 worst numbers + % of 2M.

### FILE-LEVEL / BUILD / PRESERVATION (PRES)
- `node --check` exit 0 on: prototype/js/npc.js, CONFIG.js, assets.js, game.js (and any scratch/
  cc-c10/*.js).
- index.html diff = exactly +1 line `<script src="js/npc.js"></script>` between camp.js and
  save.js, 0 removed lines.
- CONFIG.js diff = additions only (`grep -c '^-[^-]'` = 0); all added lines inside regionC (between
  :470 and the regionC close). regionA :156-366 / regionB :368-468 and every pre-existing regionC
  row byte-identical. assets.js diff = additions only, inside MANIFEST (2 keys + comments).
- game.js diff confined to hunks H1-H6 (B4): H1 interact chain line + new try* fn; H2 prompt
  branch; H3 WH_NPC.init call; H4 WH_NPC.update call; H5 save wrap questState; H6 HUD line
  element + toggle. Removed lines only at the chain line :1862-1863. Any other hunk = scope FAIL.
- Byte-identical vs e3444ec: camp.js, daynight.js, player.js, save.js, style.css,
  touch-controls.js, region-manager.js, region-defs.js, enemy.js, wh-ground.js, scratch/cc-c17/*.
- `git diff --stat e3444ec` + porcelain (untracked) set must be a subset of: prototype/js/{CONFIG,
  assets,game,npc}.js, prototype/index.html, prototype/builds/v8-playable.html (B8),
  scratch/cc-c10/**, io/reports/*cc-c10*, io/specs/testerbot-spec-wh-cc-c10-farmer.md, and (only
  if IO rules B3(a)) art-direction/3d/assets/races_regen/rigged/dwarf-male-smith.rigged.pixelated.glb.
  Anything else = BLOCK. Builder made no commits: `git log -1 --format=%h` still e3444ec.
- Bundle: python3 tools/build_v8.py ran; prototype/builds/v8-playable.html mtime newer than the js
  edits and contains `WH_NPC` and `findDaughter`; byte size RECORD (finish-line <bytes>).
- Report: io/reports/2026-10-25-cc-c10-*.md exists, states asset key, quest key, ledger numbers
  (3 centres), barn probe distances, farmer texture dims, bundle bytes, finish line.
- Grep markers: `CC-C10` comment tag on every new CONFIG/assets/game.js hunk.
- Placeholder law: no Astrabot/Meshy calls (no new scratch/treegen or meshy logs); no new GLB
  besides the B3(a) file.
- Finish line format: `CC-C10 DONE farmer farmerBody quest findDaughter ledger PASS build <bytes>`.

## VERDICT PROTOCOL
PASS iff F-pins flipped (npc.js, farmerBody, okFarmBarn, regionC.npc/quest, questState, script tag
present), A1-A7 static bars PASS, node --check all green, ledger 3-centre PASS, PRES PASS.
BLOCK: scope violation, any git mutation by the builder, A/B row drift, save.js/camp.js/daynight.js/
player.js drift, ledger FAIL or crash, harness/browser artifacts (tests/ files, playwright runs).
Static PASS = "ready for Nicko playtest", never "accepted"; A1-A7 acceptance of record = playtest.

## AMENDMENT NOTES (brief vs live tree e3444ec; I own the bars, IO owns rulings)
B1. Barrow identity / A6: no "Barrow" exists in code (L22). CFG.regionC.door (+ locked toast :1940)
    is the B/C ARCH at z -86, not a SW barrow door; the SW den (CC-C8) is CFG.regionD.door with NO
    lock (E enters, tryDenDoor :1876). The brief conflates the two. A6 bar = BOTH door paths + both
    CONFIG door blocks byte-identical. Naming the Rot Mother den "the Old King's Barrow" in dialog
    is a lore/copy call for IO/Nicko (CC-C11 inherits it).
B2. Direction copy: homestead (150.5,-256.7) -> den mouth (-167.8,-199.6) is dx -318, dz +57 = due
    WEST (slightly toward B), not SW; "SW" holds only from the map centre. CONFIG copy, Nicko tunes;
    RECORD, not gated.
B3. Farmer pixel bake is outside write scope: the brief's "assets/races_regen/rigged/" is really
    art-direction/3d/assets/races_regen/rigged/ (not in scope), and there is no tools/ pixelate
    pipeline (L20). The source is a raw rigged GLB (L19). IO ruling needed: (a) allow exactly ONE
    new file dwarf-male-smith.rigged.pixelated.glb (scratch/cc-c10 copy of intake_pixelate logic,
    geometry/skin/clips preserved, wolf.rigged.pixelated precedent), or (b) ship the raw GLB as a
    placeholder with an art-law waiver. BODY_PNG (:162) is out of scope (MANIFEST keys only).
    Without a ruling I validate whichever path the builder took and flag it.
B4. game.js scope is incomplete: npc.js cannot run without WH_NPC.init(game) (after :2517) and
    WH_NPC.update(dt) (loop tail :3060-3065), and "Talk (E)" belongs in updateInteractPrompt :2158
    (otherwise the per-frame gather prompt contradicts it). Sanctioned hunk set H1-H6 (PRES).
B5. DOM without index.html/style.css: the HUD quest line must be created in JS with inline style
    (index.html = one script tag only) and must not reuse #wh-gate-hint (setGateHint owns it).
    #wh-camp-menu overlay CSS is ID-scoped (style.css :1334-1350), so the dialog root needs inline
    overlay style; class reuse (.inv-panel/.cook-btns/.cook-btn) is fine. camp.js el() is private
    (:23), so npc.js defines its own copy.
B6. Name-plate precedent missing: lanternWaymarker is a GLB + lightSockets row (assets.js :75,
    CONFIG :109), with no DOM label. A projected DOM label in npc.js with its text from CONFIG
    ("Farmer Aldric") is accepted; its form is RECORD, not an A-gate.
B7. Ledger: ledger2.py as-is CRASHES on an appended barn row (T[a] KeyError :22-23) and its probe
    would list okFarmBarn as missing -> FAIL; scratch/cc-c17 is out of scope, and neither script
    counts the NPC (not in props). Sanctioned: scratch/cc-c10/ledger3 copies (T += okFarmBarn,
    farmerBody via the argv[6] hook). The homestead sits at r 186 from (0,-366), outside both brief
    R170 discs, so A7 adds a third gated centre at (150.5,-256.7).
B8. tools/build_v8.py writes the tracked prototype/builds/v8-playable.html (L21), which is not in
    the brief's write scope; it is sanctioned as the build artifact.
B9. Prompt style: house prompts read 'E - Examine the arch' (CONFIG :558/:567); the brief says
    "Talk (E)". Either is accepted from CONFIG; literal RECORD. Touch USE already routes through
    WH_DEBUG.interact (L7), so no touch-controls.js edit.
B10. "Static pose" = bind pose: the dwarf GLB is rigged with clips (whanim1 pass), has no CHARACTERS
    row (:209), and is cloned via SkeletonUtils with no mixer, so it will likely stand in A/T-pose.
    It is not bootCritical, so expect a stand-in box until lateSwap. RECORD for Nicko, not a
    builder fault.
B11. The HUD string's em dash vs the ASCII ' - ' house style: either accepted; RECORD.
B12. Hook position: "farmer sits with interactStation" is ambiguous. I pinned it to between tryNotch
    and tryGather (L4), which is consistent with "AFTER lock-skip/door/notch/cook/sleep"; the prompt
    branch is mirrored at the same rank (L6).
