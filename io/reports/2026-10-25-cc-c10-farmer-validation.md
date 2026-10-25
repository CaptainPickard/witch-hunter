# CC-C10 validation: Farmer NPC, Dialog UI, Quest Seed (Testerbot gate step 4)

Validator: Testerbot, independent of the builder. Date: 2026-10-25.
Tree: /tmp/wh-worldfeat, feat/world-visuals. `git log -1 --format=%h` = **e3444ec**, so the builder made no commits.
Spec executed: io/specs/testerbot-spec-wh-cc-c10-farmer.md (PER-AC PROBE SPEC + VERDICT PROTOCOL).
Brief: io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md. Builder report: io/reports/2026-10-25-cc-c10-farmer.md. The builder's claims were re-checked, not trusted.
Method: static only. I used greps, `git diff e3444ec`, sha256 of baseline blobs against the worktree, and a re-run of ledger3.py. I ran no browser, no harness, no server and no git writes.

**Static PASS means the build is ready for Nicko's playtest. It does not mean accepted.** The acceptance of record for A1-A7 is the playtest.

## Probe limits (honest record)
The sandbox denied direct calls to the playwright-bundled node binary. A python `-c` or an out-of-tree script that would spawn it was also denied. As a result:
- **`node --check`**: I could not re-run it myself. I rely on IO's pre-verification (4/4 on npc/CONFIG/assets/game), which the order says to assume true.
- **probe_npc.js, probe_barn.js, probe_dialog.js**: I could not re-run these. Instead:
  - I read their committed outputs (scratch/cc-c10/*.txt).
  - I audited their source: each is an offline `require` of the prototype files, with no browser, network or file writes.
  - I recomputed the distances that matter by hand from the CONFIG rows (below).
- **ledger3.py**: re-run directly with `python3 scratch/cc-c10/ledger3.py`. It spawns node internally, and that was allowed. The output is reproduced below.

## Per-AC table

| AC | Result | Evidence |
|---|---|---|
| **A1** farmer seat / gating / cull | **PASS** | See A1 detail below. |
| **A2** talk prompt + E / USE | **PASS** | See A2 detail below. |
| **A3** dialog lines, activation, close | **PASS** | See A3 detail below. |
| **A4** HUD quest line | **PASS** | See A4 detail below. |
| **A5** save / restore questState | **PASS** | See A5 detail below. |
| **A6** door untouched | **PASS** | See A6 detail below. |
| **A7** barn + ledger | **PASS** | See A7 detail below. |

### A1: farmer seat, gating, cull (PASS)
- **CONFIG**: `regionC.npc` at CONFIG.js:1167ff sits inside regionC, after rotLair's close and before the regionC close. regionD starts at :1211.
  - asset 'farmerBody', x 146.5, z -264.5 (:1169), rotY 3.15, interactM 3 (inside the 2.5-4 bar), name 'Farmer Aldric', dialog sub-block.
- **Distance to cottage** (150.5,-256.7): 8.77 m (bar ≤ 25).
- **Nearest prop row**, recomputed by hand from the CONFIG rows:
  - okFenceStonewall (141.7,-266.5) at 5.20 m
  - okFencePost (141.8,-262.2) at 5.23 m
  - okFencePost (147.4,-269.7) at 5.28 m
  - well at 8.4 m
  - Minimum **5.20 m** (bar ≥ 1.5).
- **Footing**: npc.js:71 calls `WH_GROUND.footY(CFG.regionC.id, N.x, N.z, N.footR)`, with no literal y.
  - footY exists at wh-ground.js:305 and is exported at :373.
  - probe_npc.txt: heightAt 3.51, slope 3.77° (bar ≤ 20), C centre 178.2 m (bar ≤ 270).
- **Gating**: `inC()` at npc.js:141-144 tests `regionManager.logic.activeId === CFG.regionC.id`. `shown = here && dist <= N.cullM` sets `root.visible` (:182-183).
- **Cull**: explicit npc `cullM: 120`, which is finite.
- **Asset**:
  - MANIFEST farmerBody (assets.js:156) points at the raw rigged GLB, which exists (4,275,044 B).
  - Its index blob equals e3444ec:…dwarf-male-smith.rigged.glb (486a9dca…), and `git status` is clean there.
  - Path B3(b) was taken. The art-law flag is recorded in the builder report and in assets.js:152-155.

### A2: talk prompt and E / USE (PASS)
- **Chain** (game.js:1880): `… tryDoorway() || tryNotch() || tryTalkNpc() || tryGather();`.
  - Exactly one new term, inserted between tryNotch and tryGather. All 8 original terms keep their order.
  - The guard at :1877 is unchanged. This is the only removed `-` line in the game.js diff.
- **tryTalkNpc / npcNear** (game.js:1978-1985, defined right after tryNotch): they return false if WH_NPC is absent or `talkPrompt()` is false. talkPrompt is false outside C, when not shown, when not alive, when input is suspended, when the dialog is open, or when out of range (npc.js:152-157).
- **Prompt branch**: `else if (npcNear())` at game.js:2206-2207 sits after the notch branch and before the gather else.
  - Its text is `CFG.regionC.npc.dialog.prompt` = 'E - Talk to Farmer Aldric', which contains "Talk" and "E" (B9 house style).
- **Range**: `Math.hypot` on x/z against `N.interactM` (npc.js:148, :156).
- **Touch**: no touch-controls.js diff. USE reaches the same chain through WH_DEBUG.interact.
- **Input suspend pair**: `setOpen()` (npc.js:132-138) sets `inventoryUI.blocked = open` and calls `player.setInputSuspended(open)`, symmetric on open and close.
  - Verified the target APIs: player.js:561 (it also unbinds and rebinds the mouse, so the buttons are clickable) and inventory.js:356 (blocked).
- **Advancing**: the Continue button only. There is no E-advance, and the guard refuses E while the dialog is open (RECORD).

### A3: dialog lines, quest activation, close (PASS)
- **DOM**: built with the local `el()` copy (npc.js:32-37). It uses the classes `inv-panel`, `inv-title`, `cook-btns`, `cook-btn` and `inv-hint`.
  - The root `#wh-npc-dialog` has an inline overlay style (z-index 20) and is appended to #wh-root (npc.js:91-116). There is no style.css diff.
- **Strings**: 8 in CONFIG: line1, line2, line3, repeat (exactly the brief text), cont, close, hint, prompt.
  - Every textContent in npc.js comes from N or D.
- **'active'**: there is a single assignment, at npc.js:123 (`quest = 'active'`, only on line 3 and only while available).
  - The only other 'active' literal is the read-only comparison in game.js:198.
- **'complete'**: no hits in npc.js or game.js. It appears only in CONFIG `quest.states`.
- **Re-talk**: `openDialog` (npc.js:163) sets lineIdx = -1 unless the quest is available. The repeat line shows and Continue is hidden (:119-121), so lines 1-3 never re-run.
- **Close paths**:
  - Esc: npc.js:216-220, scoped to `dialogOpen`. There is no conflict: camp.js:647 acts only when placing or when its menu is open, and inventory.js:321 ignores Esc while closed.
  - Death and region change: npc.js:185.
  - Restore: npc.js:209.
- **Exports**: `window.WH_NPC = { init, update, talkPrompt, openDialog, closeDialog, questState, restoreQuest }` (npc.js:223-231).
- **WH_ASSETS calls**: everything npc.js uses exists in the export (assets.js:855-877): instance, getTemplate, groundHeight, isLoaded, isFailed. WHSkeletonUtils.clone exists (vendor/skeleton-utils.classic.js:496).

### A4: HUD quest line (PASS)
- **Element**: `#wh-quest-line` is created in setupHud (game.js:215-224) and appended to #wh-hud.
  - Its inline style is `bottom: calc(18% - 28px)`, just under the gate hint's 18% (RECORD).
  - Its text is `CFG.regionC.quest.hudText`.
- **Visibility**: there is a single predicate site, game.js:198 (`WH_NPC.questState() === 'active'`), called every frame at :3104. It is hidden in 'available' and 'complete'.
- **setGateHint**: byte-identical (sha256 81e506d9… for both baseline :519-525 and worktree :536-542).

### A5: save and restore questState (PASS)
- **Capture**: `data.questState = { findDaughter: WH_NPC.questState() }` at game.js:2606, next to data.lairs.
- **Save**: `stored.questState` at :2615, inside the same try, next to stored.lairs.
- **Restore**: `WH_NPC.restoreQuest(data.questState)` at :2622 runs **before** baseRestore (RECORD).
- **Schema-v1 fallback**: npc.js:206-209 maps a missing block, a non-object or a state not in Q.states to `Q.states[0]` ('available').
- **Comment block**: the CC-C10 block at :2596-2600 sits next to CC-C7's.
- **Diff shape**: the save-wrap diff has 0 `-` lines.
- **Holder**: a single module variable `quest` (npc.js:48). Capture, save, HUD and restore all go through `questState()` and `restoreQuest()`. A NEW GAME starts at 'available'.
- **save.js**: byte-identical. The paths below all go through the wrapped trio:
  - camp LOAD
  - boot CONTINUE
  - quitPersist (WH_SAVE.save)
- **Death**: no questState or findDaughter hits outside the sanctioned sites.

### A6: door untouched (PASS)
Every block below has the same sha256 in the e3444ec blob and the worktree.

| Block | Baseline lines | Worktree lines | sha256 |
|---|---|---|---|
| game.js den door + fade helpers + lockedDoorNear + tryDoorway | :1866-1945 | :1883-1962 (+17 shift) | eadc8f73… |
| CONFIG regionC.door | :540-562 | :540-562 | 0d2838c9… |
| CONFIG regionD to end of file (includes regionD.door :1189 → :1237) | :1163-EOF | :1211-EOF | 494be0e9… |
| CONFIG :1-1083 (regionA, regionB and regionC through the farm rows) | :1-1083 | :1-1083 | dc4c1ea9… |

- The locked toast `CFG.regionC.door.text.locked` is still in place (game.js:1957).
- region-manager.js and region-defs.js are byte-identical.

### A7: barn and ledger (PASS)
- **Barn row**: exactly **1** `asset: 'okFarmBarn'` row (CONFIG.js:1093): x 136.5, z -234.7, rotY 3.15, scale 5.50, cullM 140, `// CC-C10` tag.
- **Distances**, recomputed by hand from the CONFIG rows:
  - cottage 26.08 m (bar ≥ 26 and within 60 of the cottage)
  - treeStump (162.8,-232.1) 26.4 m
  - yew (172.1,-242.9) 36.5 m
- **Fires and roads** are from probe_barn.txt, not re-run by me: fires 41.5 m, roads 133.7 m (eastRoad), seat slope 5.2° (RECORD).
- **MANIFEST okFarmBarn**: `art-direction/3d/assets/old_king/ok-farm-barn-pixelated.glb`, 1,000,080 B. Its index blob 9082026c… equals the e3444ec blob, and it is unchanged.
- **ledger3.py re-run (validator)**:
  ```
  CC-C10 rows: 2  (farmerBody x1, okFarmBarn x1; farmer via the argv[6] hook at (146.5,-264.5) cullM 120)
  LEDGER centre (0,-366) R 170: worst 1895571 = 94.78% of 2M  missing none  -> PASS
  LEDGER centre (-175,-266) R 170: worst 1876200 = 93.81% of 2M  missing none  -> PASS
  LEDGER centre (150.5,-256.7) R 170: worst 1789446 = 89.47% of 2M  missing none  -> PASS
  whole disc (0,-366) R 280 (info): worst 1895571 = 94.78%
  LEDGER PASS (cap 1980000)
  ```
- scratch/cc-c17 is byte-identical (`git diff --stat` is empty), so ledger2.py was not edited.

## PRES (file level / build / preservation): PASS
- **Changed set**: 5 tracked files are modified: CONFIG, assets, game, index.html and builds/v8-playable.html.
  - The untracked files are npc.js, scratch/cc-c10/**, io/reports/…farmer.md, the valspec, and the pre-existing scratch/cc13b-* and extract_rows.cjs.
  - This is a subset of the sanctioned set. There are no new GLB or GLTF files, no `tests/`, and no harness or playwright artifacts.
  - No Meshy or Astrabot artifacts or logs: none of the untracked files matches.
- **Protected files**: `git diff --stat e3444ec` is empty for camp, daynight, player, save, touch-controls, region-manager, region-defs, enemy, wh-ground, style.css, scratch/cc-c17 and art-direction.
- **index.html**: +1/-0. `<script src="js/npc.js"></script>` sits between camp.js and save.js.
- **CONFIG.js**: +48/-0, in 2 hunks, both inside regionC. **assets.js**: +8/-0, MANIFEST only.
- **game.js**: +44/-1. The 8 diff hunks map to H1-H6 (HUD fn and setupHud = H6; chain + tryTalkNpc = H1; prompt = H2; init = H3; save wrap = H5; loop tail = H4).
  - The only removed line is the chain line, and every hunk carries a `CC-C10` tag.
- **Bundle**: prototype/builds/v8-playable.html is **3,289,591 B** and its mtime (06:11:48) is newer than every edited source.
  - It contains WH_NPC 21 times (14 lines; the builder's "x14" is a `grep -c` line count) and findDaughter 11 times.
- **Builder finish line**: `CC-C10 DONE farmer farmerBody quest findDaughter ledger PASS build 3289591` matches the format exactly, and the byte count equals the bundle size.
- **Extra scratch files**: both are **ruled IN**. They fall under scratch/cc-c10/** and are measurement only.
  - `probe_dialog.js` is an offline node DOM-stub logic probe. It only `require`s prototype files, writes no files, uses no browser, playwright or network, and is not under tests/. The valspec allows "offline node" probes.
  - `glb_header.py` reads the GLB with `open(f,'rb')` only, and writes nothing.
- **IO dispatch files** (devbot-build-prompt.md, *-run*.log, testerbot-*-prompt.md) are IO's, not the builder's, and fall under scratch/cc-c10/**.

## Deviations adjudication
| # | Deviation | Ruling | Reason |
|---|---|---|---|
| D1 | The repeat line also shows when the quest is 'complete'. | **NONBLOCKING** | Nothing assigns 'complete' in this order (grep 0), so the branch can only be reached through a hand-edited save. Completion copy belongs to CC-C11 and is inherited there. |
| D2 | The farmer has no collider, so the player walks through him. | **NONBLOCKING** | No brief step or A-gate asks for collision. He is a static placeholder. Record it for Nicko's playtest. |
| D3 | Extra CONFIG keys: footR, bodyHeight, cullM, labelLiftM, labelM, dialog.hint, quest.hudText. | **NONBLOCKING** | They are additions only, inside regionC.npc and regionC.quest. They keep tunables and strings out of code, as the copy law and A3 require. The valspec asks for an explicit npc cullM (A1), and A4 requires the HUD text to come from CONFIG (hudText). |
| D4 | The dialog keys are named line1, line2 and line3. | **NONBLOCKING** | The valspec A3 names exactly these keys. |
| D5 | HUD text reads '(W)' with an ASCII ' - ', and the prompt reads 'E - Talk to Farmer Aldric'. | **NONBLOCKING** | These are IO rulings B2, B11 and B9 (devbot-build-prompt.md:21, :29). Both forms are accepted by the valspec. |
| D6 | The farmer is the raw 2048 JPEG GLB, LINEAR-filtered and not pixelated, standing in bind pose. | **NONBLOCKING** | IO ruled B3 = (b) and B10 accepted (devbot-build-prompt.md:17, :31). The art-law flag is recorded in the report and in assets.js:152-155. Astrabot stays flagged, not dispatched. |

## Non-gating observations (for the playtest)
- **O1**: The farmer and the cottage are 8.77 m apart, centre to centre. The cottage footprint at scale 3.68 is not measured statically, so eyeball any clipping.
- **O2**: The stand-in to GLB swap leaves the WH_ASSETS pending holder detached. It still gets lateSwapped into an orphan, which is a one-time small leak and is harmless.
- **O3**: The quest activates as soon as line 3 is *shown*, before Close. This matches the brief ("line3 -> quest activate + Close").
- **O4**: Seating relies on the groundAlign holder offset (assets.js:389-403), which survives `WHSkeletonUtils.clone`. Confirm in the playtest that the feet do not sink or float.

## Blocking findings
None.

## Verdict
**PASS: 7/7 ACs, 0 blocking.** The build is ready for Nicko's playtest. This is not acceptance.

C10 VALIDATION PASS ac-passed 7/7 blocking 0
