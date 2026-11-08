# CC-WB1 Testerbot Validation Spec — War-Effort Contract Board (region A)

Round: CC-WB1 (doc 42 Part 8 'The War Ledger', world-feature round, IO spec
`io/specs/cc-wb1-warboard-spec.md`). This is the independent validation
contract. Devbot builds; Testerbot executes the anchors below verbatim and
reports PASS/FAIL per anchor. No anchor may be weakened or skipped without
IO sign-off.

Branch: `feat/world-visuals` (worktree root `/tmp/wh-worldfeat`).
All commands assume `cd /tmp/wh-worldfeat` first.

**PLAYTEST LAW (binding):** no harness runs, no headless browser smoke, no
playwright, no browser automation of any kind. Validation = node one-shot
probes (THREE shim pattern) + static source checks only. Nicko playtests;
Testerbot validates in the sandbox.

---

## INDEPENDENT CENSUS (Testerbot-verified, HEAD 3bc82fc, 2026-11-06)

Re-grepped from source this session — not copied from the IO spec.

### Spec-assumption verdicts (the five spec-pinned assumptions, each with file:line evidence)

| # | Spec assumption | Verdict | Evidence |
|---|---|---|---|
| (a) | Inventory public accessor used at runtime | **PINNED as `window.WH_INVENTORY.{addItem,removeItem,countOf}`** | `prototype/js/inventory.js:763-765` (`addItem/removeItem/countOf` delegate to `M.active`); `game.js:1786-1787` (`game.inventory = new INV.Inventory(); INV.active = game.inventory`) so the static module facade routes to the live instance. Gather pickup path consumes this same surface via `inventory.addItem` at `prototype/js/gather.js:117`-`122` (whole-yield fit, take-back on partial). Spec's wording "bag reads through game.inventory" describes the same object — the facade and `game.inventory` are the same live `Inventory`. **Devbot MUST call `window.WH_INVENTORY.addItem/removeItem/countOf`** (the facade), the module-owned pattern chest.js uses (chest.js reads `game.inventory.slots` directly but for deposit/withdraw calls `G.inventory.addItem/removeItem`). For pure count checks `window.WH_INVENTORY.countOf(id)` is the shortest correct form. |
| (b) | `game.dayNight.day` accessor | **VERIFIED VALID** | `prototype/js/daynight.js:127` (`this.day = 0; // 0 = the tutorial's first night; +1 per new day`), incremented at daynight.js:156 (beginCycle), 168 (nextDawn), 190 (tick wrap). Instantiated `game.dayNight = new window.WH_DAYNIGHT.DayNight()` at `game.js:2483`. Begin-cycle/next-dawn callers are ONLY `js/camp.js`: camp.js:358-359 (`if (dn.dormant) dn.beginCycle(); else dn.nextDawn();`). **Dormancy caveat (pin for B-3):** `DayNight.prototype.tick` returns early while dormant (daynight.js:184 `if (this.dormant) return;`), so `game.dayNight.day` stays **0** until the first camp Save and Heal. Deploying a camp does NOT advance the day. |
| (c) | Four wiring line numbers in HEAD game.js | **VERIFIED, one correction** | Interact chain E key: `game.js:1890` (`tryRescue() || tryChest() || tryGather();` — line 1888 is `function interact() {`, the chain tail is line 1890; spec's "line 1888-1889" is off by 1-2 lines). Prompt block: `game.js:2229-2230` (`window.WH_Chest && window.WH_Chest.interactPrompt()` — spec pins 2229, exact). Manager init: `game.js:2594` (`if (window.WH_Chest) window.WH_Chest.init(game);` — exact). Save nest: `game.js:2637` (capture), `game.js:2649` (save), `game.js:2658` (restore) — spec's "2637-2648" understates the range; restore sits at **2658**. Use these: **1890 / 2229-2230 / 2594 / 2637+2649+2658**. |
| (d) | Toast path used by modules | **VERIFIED** | `game.js:1838` `toast: function (text) { game.inventoryUI.toast(text); }` (the C1 cooking wiring injects this into modules). Toast signature: `InventoryUI.prototype.toast = function (text, seconds)` at `prototype/js/inventory.js:677-685` (seconds optional, default `CFG.inventoryUI.toastSeconds`). Modules may also toast directly via `game.inventoryUI.toast(...)` (game.js:1817, 1967, 2189). Either is acceptable; the injected-callback pattern matches the module convention. |
| (e) | chest.js clone template | **VERIFIED** | `prototype/js/chest.js` = IIFE writing `window.WH_Chest` with `{ init, interactPrompt, tryChest, close, capture, restore, render }` (chest.js:29, 39, 64, 92, 262-285, 312). Game-coupling list matches spec exactly: `game.scene`, `game.player`, `game.inventoryUI.toast`, `game.inventory`, `game.camp`, `game.warEffort` is NEW (no existing warEffort key). Script tag pattern: `prototype/index.html:67` (`<script src="js/chest.js"></script>`), adjacent gather.js:56, ambush.js:73. Board script tag must sit in the same block. |

### Other census facts pinned by this valspec

- `CONFIG.items` (opens `window.WH_CONFIG.items = {` at CONFIG.js:3085): **no `warOrder` row**
  (probe `c1_warorder_item.js` => `warOrder row: undefined`). `stolenCoin` at
  3130 (category valuable, stackCap 999), `ironOre` at 3153 (category
  ingredient, default stackCap).
- `regionA` (`hold_outskirts`, opens CONFIG.js:156) `props` holds **no
  `warBoard` row** (probe `b1_config_warboard.js` pre-build FAIL as designed).
  Nearest static `mossBoulder` seats from prop census: (17.2,-9), (-24.4,23),
  (5.5,8.5), (-2.5,-6.5), **(10.5,-14.5)**, (-20.5,-12.5) — nearest to board
  (5.9,-15.5) is (10.5,-14.5) at **4.69m** (spec's 5.36m figure does not
  reproduce from census data; corrected, non-blocking — seat is still the
  spec's data-locked (5.9,-15.5)).
- `regionA.nodes` = **14 rows** (herbBundle x6, deadwoodPile x4,
  mushroomCluster x4). This round adds **zero** regionA nodes (board is a
  prop, not a node).
- `regionC` (`forest_of_the_old_king`, opens CONFIG.js:470) `enemies` block
  opens 575: **55 rows total, 25 bandit** (22 pre-WM1 + 3 CC-WM1 squatters).
  WB1 adds zero enemies.
- `regionC.nodes` = **8 ironVein** (CC-WM1 seats: 53,-577 / 55.5,-573.5 /
  61,-572 / 64,-575.5 / 63.5,-582 / 57,-584 / 51.5,-581.5 / 50,-574). All in
  the Redseam pocket. WB1 consumes 1 per day-1 contract run; unchanged by
  this round except as runtime harvest targets.
- `WH_GROUND.has('hold_outskirts') = false` — region A is FLAT by design;
  `game.ground.heightAt` is NOT to be consulted for region A seats (board y=0,
  prop convention).
- `CONFIG.camp` key exists at CONFIG.js:3287 (`window.WH_CONFIG.camp = {`);
  nested `chest` block at 3345-3346. **NO `CONFIG.warEffort` key exists.**
- `CONFIG.gather.interactRadius` = 1.6 (node E range).
- Save wiring: `save.js` capture at save.js:58; game.js wraps at 2632-2661;
  quit-persist day>0||sites>0 gate at 2667-2668.
- `prototype/builds/v8-playable.html` + `tools/build_v8.py` exist.
- `prototype/vendor/three.classic.js` exists (shim path).

## SEVERITY LEGEND

- **BLOCKER** — build is rejected, Devbot must fix and re-stage.
- **MAJOR** — build is rejected unless IO grants a written waiver.
- **MINOR** — reported in the validation report; does not block commit.

Every anchor below is BLOCKER unless stated otherwise.

---

## SECTION B — CONFIG + module content (spec B-1, B-3 content, C1)

### B-1.1 — CONFIG.warEffort key exists, mandated schema

Command:

    node scratch/cc-wb1/b1_config_warboard.js

Expected: every line `PASS`, final exit 0. The probe asserts:

- `window.WH_CONFIG.warEffort` exists with a `board` block, a
  `prompt` string (`E - ...`), a `title` string, day rows `day1`, `day2`,
  `day3`, a turned-in toast containing `{id}`, an expiry toast containing
  `{name}`.
- Day rows embed names: day1 => `ironOre`, day2/day3 => `stolenCoin`
  (iron once, coins daily).
- `regionA.props` gains a `warBoard` row with EXACT `{ x: 5.9, z: -15.5,
  rotY: 3.14 }` (data-locked seat; ground-truthed — do not move).
- regionC bandit count = 25 unchanged, regionA node count = 14 unchanged.

This probe FAILS on HEAD today (pre-build) by design; PASS defines done.

### B-1.2 — byte-diff law: regionA.props gains exactly one row

Command:

    git diff prototype/js/CONFIG.js | grep -cE "^-[[:space:]]+\{ asset:"
    # Expected: 0 (no prop retyped or deleted)
    git diff prototype/js/CONFIG.js | grep -cE "^\+[[:space:]]+\{ asset: 'warBoard', x: 5\.9, z: -15\.5, rotY: 3\.14"
    # Expected: 1 (exactly the one board row, exact seat wording)

Enforces the region A byte law: hold_outskirts region rows stay
**byte-sacred** — this feature adds **one row and nothing else** to regionA.

### C1 — CONFIG.items.warOrder row

Command:

    node scratch/cc-wb1/c1_warorder_item.js

Expected:

    warOrder row: {"id":"warOrder","name":"War Order","glyph":"WO","category":"valuable","stackCap":99,"material":true,"flavor":"..."}
    C1 PASS

exit 0. Fields: `{ id:'warOrder', name:'War Order', glyph:'WO',
category:'valuable', stackCap:99, material:true, flavor:'<string>' }` —
mirrors the rot-silk/rot-gland valuables row-law at CONFIG.js:3136-3145.

---

## SECTION CORE — js/wareffort.js module behavior (spec B-2, B-4, B-5, B-7)

All module probes use the THREE shim pattern (established house pattern,
same as scratch/cc-wb1/dump.js + seat_probe_v2.js).

### B-2 — board panel state machine + prompts

Command:

    node scratch/cc-wb1/b2_board_panel.js

Expected: all `PASS`, final line
`B-2 PASS — board panel state machine + prompts behave`, exit 0.

Asserts (module surface mandated by this valspec — Devbot builds to this):

- `window.WH_WAREFFORT` exposes **exactly these public functions**:
  `init(game)`, `interactPrompt()`, `tryBoard()`, `close()`, `capture()`,
  `restore(data)`. (Clone law from chest.js; `render` may be optional for
  the board but the six above are required.) An `isOpen()` getter is
  expected for the probe (add it; one line).
- `interactPrompt()` returns the CONFIG prompt string near the board seat
  (5.9,-15.5), null/empty at 100m+ distance, and (when open) the close-hint
  prompt.
- `tryBoard()` near the board returns true, opens the panel, sets
  `player.inputSuspended = true`, sets `inventoryUI.blocked = true`.
- `close()` clears the open flag and unsuspends input.

### B-5 / B-7 — turn-in contracts (iron once, coins daily, day-3 re-sign)

Command:

    node scratch/cc-wb1/b5_turnin_flow.js

Expected: all `PASS`, final line
`B-5 PASS — iron one-time, coins daily, day-3 re-sign path present,
wrong-day refused`, exit 0.

Asserts:

- Module exposes `tryTurnIn(dayKey)`: consumes the day row's turn-in against
  `window.WH_INVENTORY` accessors, grants 1 `warOrder`, fires the turned-in
  toast, returns true on a live contract.
- **B-7.1 day-1 one-time:** day1 at day=1 with 6 ironOre => consumed (countOf
  ironOre === 0), granted exactly 1 warOrder; a SECOND day1 turn-in attempt
  returns false and consumes nothing.
- **B-7.2 coins daily:** day2 at day=2 with 12 stolenCoin => consumed,
  granted 1 warOrder; a same-day second attempt returns false (daily).
- **B-7.2 day-3 re-sign:** day3 at day=3 with 12 stolenCoin => same
  consumption/grant; module exposes a re-sign/renewal entry
  (`resign()` or `renew()` fn, or a `day3Available` flag) so the
  never-blocked law is provable statically.
- **Wrong-day refuse:** calling `tryTurnIn('day2')` at day=1 returns false
  and leaves coin count untouched.

### C-9 — capture/restore persistence

Command:

    node scratch/cc-wb1/c9_persistence.js

Expected: all `PASS`, final line
`C-9 PASS — capture/restore round-trips contract state`, exit 0.

Asserts: `capture()` returns a plain object; `restore(snapshot)` after a
fresh reset reproduces the done-state (post-restore day1 turn-in refused,
inventory untouched); `restore(undefined)` / `restore(null)` do not throw
(chest.js C-9 law mirrored: a missing block = no-op fresh model).

---

## SECTION W — game.js wiring (spec B-3, B-6, law A)

### W-1 — interact chain E key (game.js:1890 row)

Command:

    grep -n "tryBoard() || tryChest()" prototype/js/game.js

Expected: exactly **1** hit, at the interact chain (currently line 1890),
showing `tryBoard` placed **right before `tryChest`** (board wins over the
camp chest in the chain order). Equivalent acceptable: `... tryRescue() ||
tryBoard() || tryChest() || tryGather();`.

### W-2 — prompt block (game.js:2229-2230 row)

Command:

    grep -n "WH_WAREFFORT.interactPrompt" prototype/js/game.js

Expected: exactly **2** hits in the prompt block — one guard
(`window.WH_WAREFFORT && window.WH_WAREFFORT.interactPrompt()`) and one
assignment. Placement right before the WH_Chest branch (line 2229 region).

### W-3 — manager init (game.js:2594 row)

Command:

    grep -n "WH_WAREFFORT.init" prototype/js/game.js

Expected: exactly **1** hit, in the section init block adjacent to the
`window.WH_Chest.init(game)` line (2594 region).

### W-4 — save nest (game.js 2637/2649/2658 rows)

Command:

    grep -n "WH_WAREFFORT.capture\|WH_WAREFFORT.restore" prototype/js/game.js

Expected: exactly **3** hits — capture inside the `S.capture` wrap (2637
region), capture inside the `S.save` wrap's stored-write (2649 region),
restore inside `S.restore` (2658 region). Follow the WH_Chest capture/restore
pattern exactly (guard `if (window.WH_WAREFFORT)`).

### W-5 — script tag in index.html

Command:

    grep -n "wareffort.js" prototype/index.html

Expected: exactly **1** hit, `<script src="js/wareffort.js"></script>`,
in the same script block as chest.js (index.html:67 area) — before game.js.

### W-6 — js/wareffort.js header naming

Command:

    head -5 prototype/js/wareffort.js

Expected: a header comment naming the round (`CC-WB1`), the mission file
(`io/missions/2026-11-06-cc-wb1-warboard.md` or equivalent), and the
window export `WH_WAREFFORT`; IIFE `'use strict'` body (chest.js pattern).

---

## SECTION B-3 — gameplay order static checks

B-3 is a PLAYTEST item (Nicko) — this round's no-harness law means
Testerbot does NOT execute the day-1 live loop. Static stand-ins:

### B-3.1 — day-counter accessor + dormant-law probe (static)

Command:

    grep -n "this.day = 0\|if (this.dormant) return" prototype/js/daynight.js && grep -n "beginCycle\|nextDawn" prototype/js/camp.js

Expected: `this.day = 0` at daynight.js:127; the dormant early-return at
daynight.js:184; camp.js:358-359 remain the ONLY beginCycle/nextDawn
callers. **Confirms the day counter the rows depend on advances ONLY
through the camp rest path** — so the B-3 "day counter reads 1 at deploy"
reading is a Nicko playtest judgment, not a node-probe gate.

### B-3.2 — region A byte-sacred census (recap, enforced by B-1.2)

Only the one warBoard row is added. No regionA nodes/enemies changes.
`grep -c "asset: 'warBoard'" prototype/js/CONFIG.js` = **1**.

---

## SECTION C-8 — build law

Command:

    python3 tools/build_v8.py && grep -c "wareffort\|WH_WAREFFORT\|CC-WB1\|warOrder\|warEffort" prototype/builds/v8-playable.html

Expected: build prints `wrote ... v8-playable.html <N> bytes` with N > the
pre-round size; marker count **>= 6** (new module file inline + CONFIG row
comments + wiring comments; **MINOR floor note**: exact placement not
mandated, but a count < 6 means the round's markers did not land at all).

---

## DIFF LAW (whole-file, binding)

Allowed-touched files this round, and only these:

| File | Allowed change |
|---|---|
| `prototype/js/CONFIG.js` | Add `CONFIG.warEffort` key (new block); add one `warBoard` row to `regionA.props`; add `warOrder` row to `items`. Nothing else. |
| `prototype/js/game.js` | Add tryBoard link at the interact chain; add WH_WAREFFORT prompt branch; add WH_WAREFFORT init; add WH_WAREFFORT capture (x2) + restore lines; comment tags. Nothing else. No refactors of surrounding lines. |
| `prototype/index.html` | Add one `<script src="js/wareffort.js"></script>` tag. Nothing else. |
| `prototype/js/wareffort.js` | **NEW FILE** — the whole module. |
| `prototype/builds/v8-playable.html` | Rebuilt artifact output of tools/build_v8.py only. |

**Everything else byte-sacred**: chest.js, gather.js, inventory.js,
daynight.js, camp.js, save.js, region-defs.js, wh-ground.js, all other
sources — **zero** diff lines allowed.

Enforcement (both must print zero):

    git status --porcelain prototype/js | grep -vE "CONFIG.js|game.js|index.html|wareffort.js"
    # Expected: (empty)
    git diff --stat prototype/js/chest.js prototype/js/gather.js prototype/js/inventory.js prototype/js/daynight.js prototype/js/camp.js prototype/js/save.js
    # Expected: (empty output / all-zero)

## NO-GIT clause

Testerbot never runs git mutations; Devbot never commits/stages — IO is the
sole git gatekeeper. The byte-diff law reads `git diff` (unstaged) directly —
no `git add` anywhere.

---

## SPEC-CONFLICTS (imprecisions found while census-verifying the IO spec)

1. **Spec's interact-chain line number (line 1888-1889) is off by 1-2 lines.**
   The real E-chain tail sits at **game.js:1890** (`tryRescue() || tryChest()
   || tryGather();`). `function interact() {` opens at 1888. The valspec
   pins W-1 to the exact string and accepts the line number wherever it
   lands post-edit. *Recommended IO-spec text amendment: "line 1890" instead
   of "lines 1888-1889".* No runtime impact.

2. **Spec's save-nest range "2637-2648" understates the restore site.** The
   WH_Chest restore line is at **2658** (`if (data && window.WH_Chest)
   window.WH_Chest.restore(data.chest);`). The warp spans 2637 (capture) /
   2649 (stored-write capture) / **2658** (restore). WB1 must add all three.
   Baked into W-4.

3. **Spec's "nearest static mossBoulder (10.5,-14.5) at 5.36m" does not
   reproduce from census.** Independent census gives (10.5,-14.5) ->
   (5.9,-15.5) distance = **4.69m** (hypot(5.9-10.5, -15.5+14.5)).
   Non-blocking: the spec's seat (5.9,-15.5) rotY 3.14 is data-locked and
   unchanged; only the clearance claim is mismeasured. B-1.1 still passes
   either way. *Recommended IO-spec amendment: 4.69m.*

4. **B-3 "at camp deploy the day counter now reads 1" is not node-checkable
   and technically imprecise.** `game.dayNight.day` reads **0** at camp
   deploy (deploy doesn't advance the clock; the day counter first becomes
   1 on the first Save and Heal — camp.js:358 beginCycle). The intended
   claim is "the day-1 contract row becomes readable once the day's dawn
   has begun." The valspec corrects this: B-3 is asserted statically via
   B-3.1 (dormancy law pinned, day accessor valid), with the live day-1
   loop left to Nicko's playtest law. *Recommended IO-spec amendment:
   reword to "after the first Save and Heal, the day counter reads 1".*

5. **Spec B-7 wording "bag reads through game.inventory" — pinned to the
   WH_INVENTORY facade.** Both are the same live object at runtime
   (game.js:1786-1787 makes `game.inventory === WH_INVENTORY.active`), but
   the module-law clone from chest.js + the gather pickup path standardize
   on the static facade accessors. Valspec pins
   `window.WH_INVENTORY.addItem/removeItem/countOf` so future refactors of
   `game.inventory` can't silently break the module.

---

## HOW TO RUN

1. `cd /tmp/wh-worldfeat`. NO-GIT clause holds.
2. Diff-law census (git status + byte-sacred diff --stat) — abort if any
   byte-sacred file dirty.
3. **B-1.1, B-1.2, C1** — CONFIG content anchors.
4. **B-2, B-5, C-9** — module behavior probes (node one-shots).
5. **W-1 … W-6** — game.js + index.html wiring statics.
6. **B-3.1, B-3.2** — day-accessor statics + region A census recap.
7. **C-8** — build law.
8. Report result per anchor as PASS / FAIL / WAIVED with one line of
   evidence each. Block commit until every BLOCKER passes and IO has signed
   off any MAJOR waivers.

Probe scripts (all under `scratch/cc-wb1/`, run from repo root):

| Script | Anchor |
|---|---|
| `scratch/cc-wb1/b1_config_warboard.js` | B-1.1 |
| `scratch/cc-wb1/c1_warorder_item.js` | C1 |
| `scratch/cc-wb1/b2_board_panel.js` | B-2 |
| `scratch/cc-wb1/b5_turnin_flow.js` | B-5 / B-7 |
| `scratch/cc-wb1/c9_persistence.js` | C-9 |

(Pre-build, every probe FAILs by design — PASS defines the Devbot done state.)
