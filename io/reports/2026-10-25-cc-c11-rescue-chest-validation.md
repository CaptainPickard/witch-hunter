# CC-C11 · Rescue + Reward validation report — Testerbot gate step 4

Base `512d82f` (`feat/world-visuals`, `/tmp/wh-worldfeat`). Builder output uncommitted in tree. Static gate only; no harness/browser/server per no_harness law. Nicko playtest still required.

## PRES re-verification

| Check | Result |
|---|---|
| `git diff --stat 512d82f` = `{CONFIG.js +16/0, assets.js +4/0, npc.js +80/0, game.js 33/1, index.html +1/0, builds/v8-playable.html rebuild +318/-1}` | PASS |
| New untracked `prototype/js/chest.js` | PASS |
| New untracked `scratch/cc-c11/*` (8 files) + `io/reports/2026-10-25-cc-c11-rescue-chest.md` | PASS |
| Protected files byte-identical: save.js, camp.js, enemy.js, player.js, cooking.js, region-defs.js, style.css, touch-controls.js | PASS |
| game.js single removed line = the C10 interact-chain line only | PASS |
| No `git add`, `git commit`, or any git mutation | PASS |
| `git diff --check` clean | PASS |

## Per-AC validation

| AC | Focus | Evidence | Verdict |
|----|-------|----------|---------|
| **A1** | Quest completion chain keeps C10 3-line intro and state machine; `questState()` returns original string; only two assignments (`lineIdx===2` → active; return talk → complete); daughter body exists in D while active&&!rescued, appears beside farmer in C while rescued. | `grep questState()` in game.js:2627,2639 — original string getter still called. `sed -n 165p` in npc.js: `lineIdx === 2 && quest === Q.states[0] → quest = 'active'`. `sed -n 207p` in npc.js: `quest = 'complete'; lineIdx = -2` on return talk. `updateDaughter()` in npc.js: `inDen = quest==='active' && !rescued && rid===CFG.regionD.id`; `atHome = rescued && rid===CFG.regionC.id`. | **PASS** |
| **A2** | Exactly one sarcophagus row in `regionD.props` with den-inside/ lair-outside clearance, no wall/y key. | `grep stoneSarcophagus` in CONFIG.js: exactly 1 row `{ asset: 'stoneSarcophagus', x: -201, z: -185, rotY: 0.4, scale: 1.2 }`, no `wall:` or `y:` key. Independent derivation: `dCenter = 15.8114 ≤ 32.5` PASS, `dLair = 18.6011 ≥ 12.5` PASS, nearest non-sarcophagus prop `whWallB` at `28.0893 ≥ 1.0` PASS. | **PASS** |
| **A3** | Chest exists at the player-deployed camp site, positioned by camp pegs offset, only while quest complete and not ghost. | `probe_chest` STATIC PASS: 24 slots (6×4), only deployed sites via `camps()`, per-frame position from pegs; example pegs (12,17.4) → chest (14.2,15.6), offset `[2.2,1.8]`, `interactM 2.5`, `campRadius 2.5`. `window.WH_Chest` exports = `init, update, interactPrompt, tryOpen, capture, restore` (exact match to B13). | **PASS** |
| **A4** | Return talk after rescued marks quest complete; completion line shown (not C10 repeat). | `sed -n 207p` in npc.js: `if (quest === 'active' && rescued) { quest = 'complete'; lineIdx = -2; } else if (quest === 'complete') lineIdx = -3;`. `showLine()` maps `lineIdx === -3 → D.lineComplete`. `updateQuestLine()` in game.js: `detail.state === 'complete' → CFG.regionC.quest.hudComplete`. | **PASS** |
| **A5** | Save block additive: `questState.findDaughter = {state,rescued}` + `chest=[24 slots]`; old missing chest block no-op; legacy quest string restore. | `probe_save` STATIC PASS. `grep` in game.js: `data.questState.findDaughter = window.WH_NPC.questStateDetail()` (2629), `data.chest = window.WH_Chest.capture()` (2630), `stored` variants (2641-2642), `window.WH_Chest.restore(data.chest)` (2651). `capture()` in chest.js returns `Array(24)` of `null\|{id,count}`; `restore()` no-ops on `undefined`. | **PASS** |
| **A6** | `python3 tools/build_v8.py` rebuilds clean; bundle picks up the new module + assets. | `prototype/builds/v8-playable.html` = 3304619 bytes (rebuilt). Marker counts: `WH_Chest=9`, `stoneSarcophagus=5`, `dwarfFemaleBody=3`. Builder self-report claimed `WH_Chest=16`, `dwarfFemaleBody=4` — self-report counts are wrong, but the A6 bar is presence + rebuild, both satisfied. | **PASS** |
| **A7** | Ledger PASS unchanged — C11 adds no regionA/C dressing/loot/farm rows. | `python3 scratch/cc-c10/ledger3.py /tmp/wh-worldfeat` stdout byte-equal to `scratch/cc-c11/ledger3.txt` (548 bytes). `cmp` = BYTE-EQUAL. `git diff --quiet 512d82f -- scratch/cc-c10/ledger3.py` = OK. | **PASS** |
| **PRES** | Non-goal files unchanged; no dead code, no commented-out block, no TODO added, no unrelated reformat. | See PRES table above. | **PASS** |

## Deviation adjudication

**Deviation 1 — Wall-ring clearance note:** The pre-existing regionD wall ring centroid `(-155.6,-211.4)` is ~43.7m from the den center `(-186,-180)`. The sarcophagus is placed by den-local coordinates `(-15,-5)`, not by ring-relative offsets. The B5 binding bars are met: `dCenter ≤ 32.5` (15.81), `dLair ≥ 12.5` (18.60), `dWalkway ≥ 2.0` (18.60), `dProp ≥ 1.0` wall (28.09). No protected wall/dressing row was moved. **ACCEPTED** — this is a pre-existing geometry fact that was already present in C10; the builder correctly used the binding den-center/lair coordinates. Nicko should verify visual route in playtest.

**Deviation 2 — Chest text under `CONFIG.camp.chest` instead of `CONFIG.npc.chest`:** B6 explicitly accepts "any of these" CONFIG keys for the rescue toast. The live config has no top-level `CONFIG.npc`; the camp chest block is a new sanctioned addition per B13 (first chest implementation). The rescue toast is CONFIG-driven via `quest.rescuedToast` and goes through `game.inventoryUI.toast`. No dead top-level NPC config was introduced. **ACCEPTED** — the placement is the only live location and matches the B6 spirit exactly.

## Verdict

All 8 ACs (A1-A7 + PRES) pass. Zero blockers. Two builder deviations adjudicated and accepted.

C11 VALIDATION PASS ac-passed 8/8 blocking 0
