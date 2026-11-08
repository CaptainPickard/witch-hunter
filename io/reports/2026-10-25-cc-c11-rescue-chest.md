# CC-C11 · Rescue + Reward build report

Base `512d82f` (`feat/world-visuals`, `/tmp/wh-worldfeat`). No commit/push, browser/server/harness or protected-file edit. Static gate only; Nicko playtest is still required.

## Delivered

- `prototype/js/CONFIG.js`: new rescue/completion dialog and HUD copy; `regionD.props` adds exactly one `stoneSarcophagus` row; `camp.chest` is 24 slots (6×4), offset `[2.2,1.8]` from the pegs in the site frame, `interactM:2.5`; camp interaction radius remains `2.5`. Prompts: `E - Search the sarcophagus`, `E - Open the chest`.
- `prototype/js/assets.js`: manifest-only `stoneSarcophagus` pixelated crypt GLB and RAW `dwarfFemaleBody` rigged GLB; no bootCritical entry. Original GLB hashes match the HEAD blobs: `5f179e7d948dc41a2c11d784258c9d3c475397d872de1916b3fba7b90ded13c2` and `802d803270485ef5c419c830736bb91bd4fa5a560372d651dffd677c59833fd5`.
- `prototype/js/chest.js` (new): exports `init, update, interactPrompt, tryOpen, capture, restore`. Procedural lid/body. `game.camp.camps()` is read per frame, world camps excluded; first deployed site's pegs anchor the chest, and replacement/region changes rederive its position. Tent-menu-style overlay `#wh-chest-menu` with 24 chest cells and bag cells, click-to-deposit/withdraw using Inventory's `addItem/removeFromSlot`. The chest's site-frame offset relative to the kit center is `[2.2,5.4]` (pegs `[0,3.6]` + chest delta `[2.2,1.8]`). Range uses `min(chest.interactM, camp.interactRadius)` from the chest anchor; the open panel closes on distance/region/death/quest lock. Save block is a clone of the 24 slot rows; undefined older block is a no-op.
- `prototype/js/npc.js`: one skeleton-safe daughter body (RAW bind pose) exists in D at the sarcophagus while active/not rescued; rescue hides it in the same interaction and subsequent frames place that one body beside farmer in C. `questStateDetail()` returns `{state,rescued}`; original string `questState()` and seven C10 exports remain. Intro `quest='active'` assignment remains the only site (line 165); return talk after rescue sets `quest='complete'` (line 207); complete re-talk shows `lineComplete`, not C10 repeat. Rescue opens `lineRescue` dialog and CONFIG-driven toast. Legacy string quest saves still restore.
- `prototype/js/game.js`: H1 interact chain talk→rescue→chest→gather (line 1885); H2 prompt branches in the same order (line 2223); H3 chest init after NPC (line 2589); H4 chest update after NPC (line 3133); H5 additive capture/save/restore lines in the existing save wrap (lines 2628–2651), with `questState.findDaughter={state,rescued}` and `chest=[24 slots]`. Quest HUD now shows rescued and complete copy. `prototype/index.html` has exactly one new tag directly after `npc.js`.
- `prototype/builds/v8-playable.html` rebuilt (sanctioned tracked artifact); probe outputs and scripts live under `scratch/cc-c11/`.

## Geometry and probes

`CC-C11-20261025-01` sarcophagus row: world `(-201,-185)`, den-local `(-15,-5)`, `rotY 0.4`, `scale 1.2`, no `wall:` or sink `y:`. `tb_den_geom.py` baseline: 34 existing props, ring centroid `(-155.6,-211.4)`; boss lair `(-186,-174)`; den center `(-186,-180)`. `probe_sarc.js` was run **before** pasting the row, then after pasting: `dCenter=15.8114 ≤32.5`, `dLair=18.6011 ≥12.5` (GLB raw width 2, scaled collider radius 1.2), `dWalkway=18.6011 ≥2`, nearest row `whWallB` 28.0893m (`≥1.0`), one sarcophagus row. Probe seed is labeled in the row and script. Manifest file 406160 bytes; dwarf placeholder 5105468 bytes. The regular prop footprint collider is used (no `wall:` integer).

`node --check` exit 0 on all five touched JS files and all four `probe_*.js` scripts plus `probe_sarc.js`; `probe_rescue`, `probe_dialog2`, `probe_chest`, `probe_save` each printed `STATIC PASS`. `git diff --check` clean. `python3 tools/build_v8.py` wrote **3304619 bytes**; rebuilt bundle marker counts: `WH_Chest=16`, `stoneSarcophagus=5`, `dwarfFemaleBody=4`.

`python3 scratch/cc-c10/ledger3.py /tmp/wh-worldfeat` was run twice, then re-run after the final bundle; last stdout byte-equal to archived `scratch/cc-c11/ledger3.txt` (548 bytes):

```text
CC-C10 rows: 2  (farmerBody x1, okFarmBarn x1; farmer via the argv[6] hook at (146.5,-264.5) cullM 120)
CC-C10 added tris (sum, before cull): 57524
LEDGER centre (0,-366) R 170: worst 1895571 = 94.78% of 2M at (-102,-282)  missing none  -> PASS
LEDGER centre (-175,-266) R 170: worst 1876200 = 93.81% of 2M at (-103,-278)  missing none  -> PASS
LEDGER centre (150.5,-256.7) R 170: worst 1789446 = 89.47% of 2M at (82.5,-342.7)  missing none  -> PASS
whole disc (0,-366) R 280 (info): worst 1895571 = 94.78% at (-102,-282)
LEDGER PASS (cap 1980000)
```

## Numbered deviations / risks

1. The **pre-existing** regionD wall ring center `(-155.6,-211.4)` is about 43.7m from the den center/lair region at `(-186,-180)`; several unchanged dressing rows also fall outside the den disc. The chosen sarcophagus follows the binding B5 boss-lair / den-disc clearance coordinates rather than the displaced wall-ring center. No protected wall/dressing row was moved. Nicko should check the rescue route visually in playtest; static clearance cannot prove traversability or visual guard placement.
2. The brief calls for `CONFIG.npc.chest` text keys, but the live config has no top-level `CONFIG.npc`; the sanctioned camp block is `CONFIG.camp.chest`, and the validation amendment B6 explicitly accepts a CONFIG quest text key for rescue toast. Chest text is therefore under `CONFIG.camp.chest`, rescue copy under `CONFIG.regionC.quest` / `regionC.npc.dialog`. No dead top-level NPC config was introduced.

**Blockers:** none for the static/build gate. Runtime/browser acceptance deliberately not run per hard law. No files staged: task's `No git commands other than reading` overrides Devbot's usual stage step. Other pre-existing untracked `scratch/cc13b-*` / `scratch/extract_rows.cjs` files were not touched.

CC-C11 DONE rescue daughter chest ledger PASS build 3304619
