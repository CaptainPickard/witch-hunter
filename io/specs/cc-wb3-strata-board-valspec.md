# CC-WB3 Validation Spec (Testerbot; written BEFORE the Devbot build)

Round: cc-wb3 strata requisition board, Lord's Hold (region G). IO spec:
`io/specs/cc-wb3-strata-board-spec.md` (this file validates its Acceptance
criteria A1..A10 only — the spec is the truth source; nothing here re-writes it).
Worktree /tmp/wh-worldfeat @ feat/world-visuals, HEAD at valspec pin:
`cf9d61eb3d09a17824799d513b5436ffc3d2b2db`.

**STANDING ORDER (binding):** playability itself is NICKO's bar. There is no
simulator, no harness run, no headless browser smoke, no browser automation of
any kind. The verdict child validates CODE ONLY via node one-shots + static
source checks. Nothing in this file, nor in any PASS it produces, is a playability
claim.

**NO-GIT law:** never commit/push/stage/clone/config; read-only git
(rev-parse/status/diff) is required for the diff probe. Probe scripts live at
`/tmp/ccwb3/` (OUTSIDE the worktree); the ONLY worktree write is the verdict
report. NO-GIT also means: validate the working tree as found; IO commits.

**Smoke precedent:** the node one-shot pattern is the /tmp/wb1_smoke2.js law
(stub window/document, real CONFIG, fake game). The surviving concrete
reference implementation: `scratch/cc-wb2/wb2_harness.js` — reuse its shape.
Pre-check V-0 (sha256 of CONFIG.js, game.js, index.html, wareffort.js, the
built html + `git rev-parse HEAD`, recorded FIRST, re-run at verdict close)
carries over from io/specs/cc-wb2-ladder-valspec.md V-0 verbatim.

Pinned anchors (re-grepped 2026-11-07, HEAD cf9d61eb):
- `regionG: {` CONFIG.js:1687; `id: 'lords_hold'` :1688; props array :1735-1868.
- `window.WH_CONFIG.warEffort = {` CONFIG.js:4416 (strataEffort inserts adjacent).
- `affinity.deeds` block: CONFIG.js:4881 (warEffortFill: 10).
- wareffort.js = 277 lines, export `window.WH_WarEffort` — DO NOT TOUCH.

---

## HARNESS CONTRACT (all module probes; /tmp/wb1_smoke2.js pattern)

One shared `harness.js` at /tmp/ccwb3/ loaded by every module one-shot. The
builder's module `js/strataeffort.js` (export `window.WH_StrataEffort`) MUST
run against EXACTLY this fake surface and nothing more:

1. `global.window = global; global.document = { createElement: fn }` stub —
   wareffort.js's `el()` helper calls document.createElement; strataeffort.js
   may reuse it, so the stub must exist headless.
2. Real CONFIG: `require('/tmp/wh-worldfeat/prototype/js/CONFIG.js')` →
   `window.WH_CONFIG`. Module reads `CFG.strataEffort` ONLY (no warEffort
   reads, no ladder reads).
3. Fake inventory object with EXACTLY the WB1 smoke shape: `slots` array
   (cap 60/stack), `addItem(id,count) -> added`, `removeItem(id,count) ->
   removed`, `countOf(id) -> n`. The module calls `game.inventory` first,
   `window.WH_INVENTORY` fallback (WB1 `inv()` grammar); NO slot poking, NO
   facade bypass. rot-silk / rot-gland / strataOrder / stolenCoin are plain
   string ids at runtime.
4. Fake journal: `window.WH_JOURNAL = { append: fn(id, title, body, day, source) }`
   with appends captured; module must guard `if (JT && window.WH_JOURNAL)` and
   append the `strata` topic id on award AND on fill.
5. Fake AFF: `window.WH_AFF = { deed: fn(id, times) }` (deed ids captured),
   called via `if (window.WH_AFF) window.WH_AFF.deed('strataFill')` on fill.
6. Fake game: `dayNight = { day: <int> }` (dayNumber() reads only); region
   gate via `regionManager.logic.activeId = 'lords_hold'` (near() must keep
   the WB1 `if (game.regionManager)` guard); `player = { state:'alive',
   inputSuspended:false, pos:{x:6.0, z:-782.0} }`; `inventoryUI.toast(t)`
   captured into an array; `scene` = FakeScene (add captured) or explicitly
   `null`.
7. HEADLESS-SAFE LAW: `init(g)` with `game.scene === null` must not throw and
   must skip visuals (buildBody only when `game.scene && window.THREE`). The
   harness verifies both the skip and the no-throw.
8. THREE shim (when scene provided): Group/Mesh/BoxGeometry/PlaneGeometry/
   MeshStandardMaterial/DoubleSide with retained constructor args for the
   material census (scratch/cc-wb2/wb2_harness.js shape).
9. Day rolls are INTERACTION-TIME only: the fake "day+1" is
   `game.dayNight.day = d+1` then the next tryOpen()/interactPrompt() call —
   no timers, no tick hooks anywhere in the module.
10. State reset per test: `delete require.cache[<module path>]` + re-require
    (IIFE closure freshness, wb2_harness.js `reloadModule()` shape).
11. Save-wrap is NOT exercised in the harness — capture()/restore(data) are
    probed directly against the fresh module.

## EVIDENCE TABLE (probe -> evidence -> PASS)

Every probe's stdout is pasted VERBATIM into the verdict report; raw output
kept at /tmp/ccwb3/out/aN.txt. Commands run from /tmp/wh-worldfeat.

| # | Probe (exact command) | Evidence file | PASS threshold |
|---|---|---|---|
| A1 | `node /tmp/ccwb3/a1_config.js` | a1 output in the report | CONFIG parses; `strataEffort` block present with top-level key-set {boardSeat, itemId, mats, reward, title, offerText, doneText} EXACTLY (see spec-note); boardSeat = {lords_hold, 6.0, -782.0, 4.712}; mats = exactly [rot-silk 4, rot-gland 2]; reward {stolenCoin, 5}; `items.strataOrder` mirrors the warOrder row (name 'Strata Requisition', glyph 'SR', category 'document'); `journal.topics.strata` one row (id/title/body strings); `affinity.deeds.strataFill` present. All lines PASS, exit 0 |
| A2 | `node /tmp/ccwb3/a2_flow.js` | a2 output | idle press: +1 strataOrder, active=true, postedDay=day, offerText toast, journal append; active press with 9 silk + 2 gland: removes EXACTLY 4/2 (silk surplus 5 untouched), +5 stolenCoin, resolvedDay === postedDay, active=false, papers hidden; `Object.keys(capture())` === {active,postedDay,resolvedDay} EXACTLY (3 keys, repeatIndex-free); doneText toast; journal fill append; deed('strataFill') |
| A3 | `node /tmp/ccwb3/a3_shortfall.js` | a3 output | press with 2 silk + 2 gland: NOTHING removed, NOTHING granted, state unchanged (active still true, no resolvedDay); toast equals 'Not enough rot-silk/rot-gland for the strata order. (2/2)' — the (s/g) slot carries the HAVE counts interpolated at press |
| A4 | `node /tmp/ccwb3/a4_spent.js` | a4 output | after fill: same-day press returns consumed, ZERO inventory/state changes; fake day+1 then press re-arms award path (active true, postedDay = new day); a second day+1 re-arms again after each fill |
| A5 | `node /tmp/ccwb3/a5_prompts.js` | a5 output | idle 'E - Strata Board (Take a requisition)'; active EXACTLY 'E - Strata Board (needs 4 rot-silk + 2 rot-gland)' built FROM CFG counts (probe recomputes the string from CONFIG, then also pins the literal); spent 'The board is spent until dawn.'; far = '' |
| A6 | `node /tmp/ccwb3/a6_persist.js` | a6 output | capture = 3 keys; restore with foreign payload (string/number/null/array) and missing key payload = no-op, no throw, fresh idle board; restore(real payload) restores state AND paper visibility (hidden when spent, visible otherwise), WB1 V-5n clamp shape (non-boolean/non-number = clamp/null) |
| A7 | `node /tmp/ccwb3/a7_seat.js` | a7 output | seat-probe contract below; all recompute lines within thresholds, exit 0 |
| A8 | diff probe below | diff --stat + status output | ONLY the allowed file set, zero byte-sacred rows |
| A9 | `node /tmp/ccwb3/a9_art.js` + `grep -c 'emissive' prototype/js/strataeffort.js` + `grep -icE 'crimson' prototype/js/strataeffort.js` | a9 output | material census from retained ctor args: EXACTLY one material with emissive, value 0xffb347; zero crimson hits; zero red-channel-only material colors; zero Light constructors (no second light); every scene node name prefixed 'cc-wb3-' |
| A10 | build probe below | build stdout + marker count | build exit 0 in-tree; marker rule holds |

## SEAT-PROBE CONTRACT (A7 — recompute, never hardcode)

`/tmp/ccwb3/a7_seat.js`: (1) regex-extract the `regionG` props array straight
from CONFIG.js (span `regionG: {` .. the next top-level `regionX: {`), parse
every `{ asset, x, z, ... }` row (~111 rows; NO hardcoded coordinates); (2)
read `CFG.strataEffort.boardSeat` as the seat under test (x 6.0, z -782.0);
(3) recompute and assert:
- min distance to EVERY props row >= 4.0 m;
- the dais brazier pair (asset 'banditCampfire' at x ~ +5.66, z -776.34 /
  -787.66) each 5.67 m, tol ±0.05; both rows found from the array, not baked in;
- stoneSteps (0.0, -780.0) 6.32 m, tol ±0.05 (spec pins 6.3);
- radial vs `regionG.center` <= 124.5 (recomputes to 40.45);
- outside BOTH door window bands, reading each door row straight from the
  regionG span (door 1: planeZ -700, doorHalfWidth 4.5; door 2: planeZ -948,
  doorHalfWidth 4.0): for each row the probe asserts BOTH |boardZ - planeZ| >
  0-band reach outside the gate lane AND NOT(|boardX| <= doorHalfWidth when
  near the plane); recomputed at the seat this is |x|=6.0 > 4.5, with
  z-distances 82 m / 166 m — values read, never hardcoded;
- boardSeat.rotY === 4.712 present on the CONFIG row.
The prop-parse count and every computed distance are printed as evidence lines.

## DIFF PROBE (A8 — exact invocation, run AFTER the A10 build)

    git -C /tmp/wh-worldfeat diff --stat HEAD -- prototype
    git -C /tmp/wh-worldfeat status --porcelain -- prototype

Expected set (nothing else, no engine file, no scratch file inside prototype/):
- modified: prototype/js/CONFIG.js, prototype/index.html, prototype/js/game.js,
  prototype/builds/v8-playable.html (rebuilt artifact, expected because A10
  ran first — the build artifact diff row is part of the set, never a FAIL);
- added / untracked: `?? prototype/js/strataeffort.js`.
Byte-sacred spot check (each prints EMPTY):

    git -C /tmp/wh-worldfeat diff --stat HEAD -- prototype/js/wareffort.js \
      prototype/js/chest.js prototype/js/gather.js prototype/js/inventory.js \
      prototype/js/daynight.js prototype/js/camp.js prototype/js/save.js \
      prototype/js/region-manager.js prototype/js/affinity.js prototype/js/journal.js

Wiring census (supports A8; report lines, not new criteria): index.html
`grep -n 'strataeffort.js' prototype/index.html` = 1 hit, AFTER the wareffort
tag (line 69 area); game.js greps `tryWareffort() || tryStrata`, the
`WH_StrataEffort.interactPrompt` prompt branch after the WH_WarEffort branch,
the `WH_StrataEffort.init` hook after WH_WarEffort.init, and the save-wrap
capture/restore hand-off mirroring the warEffort lines (2670/2687/2701 area)
= the expected wiring rows. Anything beyond adds = FAIL.

## BUILD PROBE (A10 — marker line-count rule)

    python3 tools/build_v8.py
    grep -c 'CC-WB3' prototype/builds/v8-playable.html

Build runs IN THE WORKTREE, exit 0, and the marker count rule is LINE count:
`grep -c 'CC-WB3'` >= 3 (the io spec's pinned law). The raw `grep -o … | wc -l`
figure is reported alongside for the byte census but the line count >= 3 is
the gate. The build must not dirty any file outside the A8 expected set.

## SPEC-NOTE (one imprecision, resolved here)

IO spec A1 says "exactly the 9 keys above"; the CONFIG block it quotes defines
SEVEN top-level keys (boardSeat, itemId, mats, reward, title, offerText,
doneText). The only census that reaches 9 is 7 block keys + items.strataOrder
+ journal.topics.strata — so A1 binds key-set equality on the 7-key block
verbatim from the spec's own CONFIG quote, plus the separately-asserted items
row and journal row (and deeds.strataFill on top). That covers both readings;
a probe demanding 9 keys INSIDE the block alone FAILS nothing here.

---

## VERDICT REPORT

`io/reports/<date-the-verdict-runs>-cc-wb3-validation.md`, worktree, FIRST
line the banner. Structure: banner; V-0 pre/post sha table; per-criterion
A1..A10 PASS/FAIL each with the verbatim evidence lines; any FAIL shows
observed vs expected. No partial PASS: any FAILing criterion = FAIL verdict.
Playability is NOT in scope: the report contains no playability, feel, or
simulator claims of any kind.

## VERDICT BLOCK (template — fill every row; overall derives mechanically)

    VERDICT: PASS | VERDICT: FAIL
    A1  <PASS/FAIL> — <one evidence line>
    A2  <PASS/FAIL> — <one evidence line>
    A3  <PASS/FAIL> — <one evidence line>
    A4  <PASS/FAIL> — <one evidence line>
    A5  <PASS/FAIL> — <one evidence line>
    A6  <PASS/FAIL> — <one evidence line>
    A7  <PASS/FAIL> — <one evidence line>
    A8  <PASS/FAIL> — <one evidence line>
    A9  <PASS/FAIL> — <one evidence line>
    A10 <PASS/FAIL> — <one evidence line>
    OVERALL: PASS iff A1..A10 ALL PASS; any FAIL row => OVERALL: FAIL
    (no waivers this round; BLOCKER-carrying like WB1)
    CODE-ONLY NOTE: this verdict validates code; playability is Nicko's bar.
