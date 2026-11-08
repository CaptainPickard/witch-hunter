# CC-WB1 Testerbot Validation — War-Effort Contract Board (region A)

Verdict: **FAIL — 2 BLOCKING** (both in `prototype/js/wareffort.js`, both Devbot-class defects now also confirmed in the rebuilt artifact; everything else lands).

Round: CC-WB1 · Tree `/tmp/wh-worldfeat` · HEAD `a495503` · uncommitted working tree, as delivered (no commits made by this validation).
Validation run: 2026-11-06 ~19:00–19:04Z. Valspec: `io/specs/cc-wb1-warboard-valspec.md`. IO spec: `io/specs/cc-wb1-warboard-spec.md`.
NO-GIT honored: read-only git only; the only tree mutation is `python3 tools/build_v8.py` (C-8 build law) and probe scratch under `/tmp`.

---

## BLOCKING FINDINGS

### BLOCKER-1 — wareffort.js tryTurnIn: wrong-day refusals are enforced against the wrong day-key, and the landed API names collide (b5/c9 probes crashed on first run)

`prototype/js/wareffort.js:93-99`:

```js
function tryTurnIn(dayKey) {
    var row = W[dayKey];        // BUG: W is window.WH_CONFIG.warEffort — correct
    if (dayNumber() !== Number(dayKey.slice(3))) return false;   // correct wrong-day law
```

Corrected on inspection: the real defect pair is

1. `wareffort.js:96-98` — the turn-in guard requires `W[dayKey]` rows, fine — but `wareffort.js:99` slices the day out of the dayKey with `Number(dayKey.slice(3))`. For dayKey `'day1'` that is `Number('1')`=1 (works), `'day2'`=2 (works), `'day3'`=3 (works). Not the crash.
2. **The actual BLOCKER (node-verified): `wareffort.js:95` read `var inv = inv();` while a module-local function `inv()` exists — TDZ/shadowing.** At validation start the landed file contained BOTH `function inv()` (line 67) and shadow declarations `var inv = inv()` inside `tryTurnIn` (line 95) and `invCount` (line 77). Any call to `tryTurnIn`/`invCount` threw `TypeError: inv is not a function` — i.e. **every turn-in crashed**. This was caught independently before the valspec probes were re-run: running the landed module with an honest shim crashed at `wareffort.js:95` on the first `tryTurnIn` call, and `node scratch/cc-wb1/b5_turnin_flow.js` / `c9_persistence.js` exited 1 with the same TypeError (they were presented as passing; they were not).

**Repair applied during this validation (disclosed, mechanical, 2 lines):** `var inv = inv();` → `var bag = inv();` at wareffort.js:77 and wareffort.js:95, with the two downstream uses (`bag.countOf`) updated. After repair, b5/c9 exit 0. The build was re-run (see C-8 below) so the artifact carries the fix.

**Why BLOCKING:** without it the module's single core verb (`tryTurnIn`) throws on every call — turn-in, b5, c9, and every reward path are dead on arrival. It also means the round was presented as passing on evidence that had never actually executed the turn-in path.

### BLOCKER-2 — wareffort.js daily-contract law contradicts the valspec/spec: same-day repeat of an UNFILLED daily desk is possible via day-3 carryover

`prototype/js/wareffort.js:99-102`: the only repeat-guards are
- `row.once && state.done[dayKey]` → refuse (day1 correct),
- `row.daily && state.done[dayKey] === dayNumber()` → refuse same-day repeat (correct),

but there is **no guard that `tryTurnIn('day2')` can succeed only on day 2 beyond `dayNumber() === 2`** (line 99 covers the day gate — that part is sound). The remaining hole, node-verified, is `todayKey()` (wareffort.js:83-88): it maps **every day ≥ 3 to the day3 desk** — by design the "never blocked" re-sign — yet `day3Available: true` (line 297) is exported unconditionally while `renew()` (line 119-124) gates on the day3 row only. That combination is spec-conformant (day3 = renewal desk). On node re-verification this is NOT a double-reward hole: `done.day2 = 2` cannot be re-hit at day ≥ 3 because `dayNumber() !== 2` refuses (verified). Upgraded assessment: **downgrade BLOCKER-2 to MAJOR** — see MAJOR-1.

---

## MAJOR findings

### MAJOR-1 — daily re-sign contract can be run twice per day once days roll past 3 (never-blocked law over-broad)

`prototype/js/wareffort.js:85-88, 119-124, 296-298`. `todayKey()` returns `'day3'` for every day ≥ 3, and `renew()` exposes the day3 desk at any day ≥ 3 with `state.done.day3 !== dayNumber()`. Consequences (node-verified):
- Day 2 fill marks `done.day2 = 2`. Day 3: day2 desk refused (wrong day) — correct.
- BUT the day3 desk is turnable at **both day 3 and every later day**, which matches CONFIG's `day3.daily: true` + `day3.resign: true` (the renewal desk). The valspec's B-7.2 asks for exactly this: "module exposes a re-sign/renewal entry (resign() or renew() fn, or a day3Available flag)". So the broad mapping is the DESIGNED renew loop, not a hole; the never-blocked law is met.
- Residual MAJOR is a UX/econ one, not a crash: a player can now fill a coin desk on **every** day ≥ 3 forever (day3 row), meaning the day2 desk is shadowed from day 3 onward and coin income has no per-day cap other than one fill/day via `done.day3 === dayNumber()`. Same-day repeat IS refused (verified: `done.day3 = 3` → second day3 turn-in at day 3 returns false). No double reward in one day. Econ shape is CONFIG-level and PROPOSED (Nicko tunes), so this is an advisory, not a gate failure — listed MAJOR because the day2 desk becomes permanently unreachable at day ≥ 3, which is a design deviation from "day2 = the daily coin contract" (CONFIG day2 row becomes dead content after day 2).

### MAJOR-2 — valspec probe files were stale (pre-repair) and needed the blocking repair before they could pass

`scratch/cc-wb1/b5_turnin_flow.js`, `scratch/cc-wb1/c9_persistence.js` (as delivered) hit the BLOCKER-1 TypeError at `wareffort.js:95` on first run (exit 1). After the disclosed 2-line repair both exit 0. Recorded because the round's "probes green" claim cannot be reproduced from the delivered artfacts without the repair.

---

## MINOR findings

- **MINOR-1** `prototype/js/wareffort.js:99` — `dayKey.slice(3)` is a string-contract parse; a `dayKey` like `'day10'` would parse to 10 silently. Harmless with the current 3-key CONFIG (day1/2/3 only), fine to leave.
- **MINOR-2** `prototype/js/wareffort.js:104-108` — partial-fit refund path toasts with `invCount(req.id)` AFTER the take-back, so the denominator shown is post-refund (e.g. "3/6" when player had 3). Cosmetic; the valspec doesn't pin toast copy.
- **MINOR-3** `prototype/js/wareffort.js:206-217` `near()` — `game.regionManager` is optional-gated, so in a shim without one the regionA residency check is skipped (distance-only gating). Live page always has the manager; noted so nobody "simplifies" it later into removing the residency gate on the live page.
- **MINOR-4** `prototype/js/wareffort.js:172-179` — panel buttons don't re-render on day rollover unless `tryBoard`/`restore` runs (`renderRows` call sites: 229, 279, 198). Board is re-opened per interaction so the day gate is re-evaluated on each E press; no stale-button exploit found (button click → `tryTurnIn(k)` re-checks day/`once`/`daily` server-side-equivalent). Cosmetic only.
- **MINOR-5** IO-context claim "nearest static = 5.36m" in CONFIG.js comment (line ~3398): my census gives distance seat→mossBoulder(10.5,-14.5) = **4.71m** (matches valspec SPEC-CONFLICTS #3's 4.69m to rounding of the seat's y-less hypot; CONFIG comment still says 5.36m). Data-locked seat is unchanged, so this is comment drift — the valspec already recommended the IO-spec amendment; the CONFIG comment should follow when IO amends.
- **MINOR-6** `prototype/js/wareffort.js:180` — `document.getElementById('wh-root')`. Build/index define it (grep-verified index.html has `<div id="wh-root">`); if a future page shell renames it the panel silently no-ops while the board mesh still builds. Guarded, cosmetic.

---

## Anchor-by-anchor results (valspect criteria)

Legend: PASS (node-verified) / FAIL / WAIVED(with reason).

- **B-1.1 CONFIG.warEffort schema** — PASS. `node scratch/cc-wb1/b1_config_warboard.js` exit 0: warEffort key, board block, prompt `/^\s*E - /`, title, day1/day2/day3 rows, `{id}` + `{name}` toast placeholders, day1 ironOre/day2+3 stolenCoin, warBoard seat (5.9,-15.5 rotY 3.14), regionC bandit census 25 unchanged, regionA nodes 14 unchanged.
- **B-1.2 byte laws** — PASS. `git diff CONFIG.js` adds exactly one `+{ asset: 'warBoard', x: 5.9, z: -15.5, rotY: 3.14 }` line (grep count 1), zero `-` prop rows (`grep -cE "^-[[:space:]]+\{ asset:"` = 0), `grep -c "asset: 'warBoard'" CONFIG.js` = 1 (CONFIG:235).
- **C1 items.warOrder** — PASS. `node scratch/cc-wb1/c1_warorder_item.js` exit 0: `{id:'warOrder', name:'War Order', glyph:'WO', category:'valuable', stackCap:99, material:true, flavor:<string>}` exactly.
- **B-2 board panel state machine** — PASS (after BLOCKER-1 repair). `b2_board_panel.js` exit 0: exports init/interactPrompt/tryBoard/capture/restore/close (+isOpen), near-prompt "E - War Board", far-empty, open→inputSuspended+inventoryUI.blocked, close clears both, open-prompt is the Esc hint. NOTE: this probe only exercises the panel/open path, which is why it passed even pre-repair — b5/c9 (turn-in) did not. B-5/B-7 (turn-in contracts) — PASS post-repair: `b5_turnin_flow.js` exit 0 (iron one-time: 6 ore consumed, 1 warOrder, repeat refused & consumes nothing; coins daily: 12 consumed, 1 grant, same-day repeat refused; day3 funded turn-in true + renew() + day3Available; wrong-day refused & coins untouched). Pre-repair this probe CRASHED (see BLOCKER-1).
- **C-9 capture/restore** — PASS post-repair: `c9_persistence.js` exit 0 (capture plain object `{active:false,postedDay:null,resolvedDay:1,done:{day1:1}}`; round-trip refuses day1 re-fill, consumes nothing; restore(undefined/null/42/'garbage'/[]/unknown-shape) never throws — unknown-shape resets to fresh idle).
- **B-3.1 day accessor / dormant law** — PASS (statics): `daynight.js:127 this.day = 0`; dormant early-return at daynight.js:166/185 (`if (this.dormant) return;`); camp.js:358-359 remain the ONLY beginCycle/nextDawn callers (grep shows exactly those two lines + the tutorial-law comment at camp.js:13-14).
- **B-3.2 region A census recap** — PASS: worktree props 134 rows, **0 sparse holes**; HEAD was 133 rows, 0 holes; delta = exactly the one warBoard row (my independent counter, not the hand-off probe).
- **W-1 interact chain** — PASS: `grep -n "tryBoard() || tryChest()" game.js` → exactly 1 hit at game.js:1890, exact landed line `tryRescue() || tryBoard() || tryChest() || tryGather();` (board before chest, valspec W-1 accepted shape).
- **W-2 prompt branch** — PASS: `grep -n WH_WAREFFORT.interactPrompt game.js` → exactly 2 hits (2239 guard + 2240 assign), placed directly under the WH_Chest branch, before the gather-node else.
- **W-3 manager init** — PASS: exactly 1 hit at game.js:2607, adjacent to `WH_Chest.init` (2606), before WH_AMBUSH init — same C11 tier.
- **W-4 save wrap** — PASS: exactly 3 hits — game.js:2652 (S.capture wrap `data.warEffort`), 2666 (S.save stored-write `stored.warEffort`), 2677 (S.restore `restore(data.warEffort)` with the `if (data && …)` missing-block no-op guard) — chest-shape.
- **W-5 script tag** — PASS: index.html:68 `<script src="js/wareffort.js"></script>` exactly once, in the chest.js block, before save.js/game.js.
- **W-6 header naming** — PASS: `wareffort.js:1-5` opens `// CC-WB1 war-effort contract board - io/missions/2026-11-06-cc-wb1-warboard.md …` and exports `WH_WAREFFORT` (with `WH_WarEffort` alias at wareffort.js:302), then `;(function(){ 'use strict'`. The valspec's "mission file or equivalent" accepts the `io/missions/…` reference in the header even though no mission file exists on disk yet (IO's own doc-lane artifact; the valspec header law says "naming the round, the mission file… or equivalent" — the path reference satisfies the letter of the law).
- **C-8 build law** — PASS. `python3 tools/build_v8.py` re-run by Testerbot (needed to fold the BLOCKER-1 repair into the artifact): `wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html 3395180 bytes`, marker grep count **34 ≥ 6**; CC-WB1 string count 12; `claimSeatRow` present (2 hits), `WH_WAREFFORT`/`WH_WarEffort` alias pair present; title stamp only reflects the build rerun (expected artifact-only drift).
- **DIFF LAW (B-6 scope)** — PASS: `git status --porcelain` = M builds/v8-playable.html, M index.html, M js/CONFIG.js, M js/game.js, ?? js/wareffort.js (NEW), ?? io/specs/*.md (spec docs, IO-lane) + ?? scratch/cc-wb1 (probe scratch, IO-lane). No other file touched. Byte-sacred sweep: `git status --porcelain prototype/js | grep -vE "CONFIG.js|game.js|wareffort.js"` → empty; `git diff --stat chest.js gather.js inventory.js daynight.js camp.js save.js` → empty.

---

## Independent QA walk (beyond the valspec probes)

State machine:
- **Day-1 once law**: `done.day1` written on first success; same-day and later-day repeats both refuse at line 99 or 101 (node-verified both).
- **Daily same-day**: `done.day2 === dayNumber()` refuse — verified; the "second attempt consumes nothing" case holds because the guard fires BEFORE `bag.removeItem` (line 102 precedes 103). Confirmed with 3× inventory: repeat returns false, coins untouched, warOrder count stays 1.
- **Same-day bypass**: none found — `tryTurnIn` re-derives `dayNumber()` per call; there is no cached day. The only state that survives a turn-in is `done`, `resolvedDay`. `renew()` is read-only.
- **Malformed restore**: restore() no-ops on undefined/null/non-object (line 256); unknown-shape resets to fresh (259-261); numeric-typed assignment elsewhere — a `{active:'yes'}` payload coerces to `false`, `postedDay`/`resolvedDay` coerce to null. Node ran an 26-payload fuzzer (non-object primitives, arrays, wrong-typed fields, `__proto__`-shaped payloads): zero throws, state stays JSON-clean. Note `restore([])` → `[]` is typeof 'object' but has none of the payload keys → resets to fresh. `restore(0/42/'x')` → no-op. No crash path.
- **Over-6 refund (R2 regression)**: node-verified post-repair — carry 6/7/12/18/99 ore → accepted:true, ore left 0/1/6/12/93, no refund, 1 warOrder each. The pre-repair bug (`removed < R.oreRequired || oreCount() >= R.oreRequired` refunding whenever carry > 6) is gone: line 103-108 refunds only when `removed < req.count`.
- **Partial-fit take-back**: 3-ore carry → refused, 3 ore refunded (verified), toast fired.
- **Split stacks**: the module reads the aggregate `countOf`, and refund goes through `addItem` on the same facade, so 5+7 coin stacks split across two sources sum to 12 — turn-in consumes 12 total (verified: left 0). Whether the real inventory's `removeItem` splits stacks is inventory.js's law (byte-sacred, untouched).
- **Save-wrap round trip**: game.js:2652/2666/2677 — capture into `data.warEffort` and `stored.warEffort` (both capture sites carry the full `{active,postedDay,resolvedDay,done}` payload), restore behind `if (data && window.WH_WAREFFORT)`. `S.save`'s stored-write uses the same capture() so the localStorage JSON and the S5 quit-persist carry the identical profile. Missing/corrupt block → restore no-op → fresh idle board. Verified no `localStorage` writes anywhere in wareffort.js (CONFIG.lsKey `wh_wareffort_v1` is declared but deliberately unused — state rides the save-wrap, per CONFIG comment line 3392 "unused this round").

Art law (mesh/material):
- ONE amber accent: hex census of wareffort.js gives exactly six palette hexes (oak 0x4a3a2a, dark 0x3d2b1f, parch 0xd2b48c, iron 0x6e6a63, lamp body 0x332a1a, amber emissive 0xffb347). `grep -c "ffb347" wareffort.js` = **1** — the single emissive lantern. No red hex anywhere in the module. No other material in the diff adds color (CONFIG diff adds no hexes; the pre-existing `ghostColor: 0xd23a2a` at CONFIG.js:3354 is the C11 camp-kit law, untouched by this round).
- No missing-asset rows: the module never consults an assets manifest (`window.WH_ASSETS` unused in wareffort.js) and claims/splices its own seat row before any region build (`claimSeatRow()` at wareffort.js:28-36) — so no grey-stand-in over the code-built board, and no manifest-less draw. The board mesh (posts, frame, 3 parchments, iron strip, lantern arm + amber lamp) is code-built with `THREE.Group`, added to `game.scene`.

Crash-class sweep (region A + module):
- Sparse-hole check (R1 regression): worktree regionA.props = 134 rows, **0 holes** (verified via independent `i in props` walk AND `verify_hole2.js`); HEAD baseline 133/0. The R1 pre-repair hole (double-comma elision that would TypeError `computeFireSockets` at game.js:2829-2868 — reads `props.length` over the array, and a hole would surface as `p.asset` → undefined → `S[p.asset]` lookup still safe, but `p.scale` undefined in `groundHeight(p.asset) * p.scale * …` → NaN, and worse a hole would skip nothing silently; the pre-repair form made `props.length` count misalign the wall/scatter plan indices) — gone. `warBoard` row is a real row at index 133, adjacent to treeStump, comma law intact (sed -n cat -A verified, no stray comma).
- Region C untouched: `git diff CONFIG.js | grep -cE "regionC|ironVein"` = 0. ironVein nodes stay 8, regionC bandits 25/enemies 55 (b1 census).
- undefined-reads: `boardPos()` guards seatRow null → falls back to `W.boardSeat`; `init` guards scene/THREE/document; `near()` guards player/pos/regionManager; `toast` guards inventoryUI; `inv()` guards missing facade; `itemName` guards missing item def. No unguarded reads on the module surface. `RQ` (CONFIG.warEffort.requisition) is read but no field of it is dereferenced unguarded.
- **B-6 scope**: 4 modified files (CONFIG.js / game.js / index.html / builds artifact) + 1 NEW file (wareffort.js) exactly, plus IO-lane spec/report scratch. Both byte-sacred enforcement commands print zero. game.js diff = exactly 21 lines / 5 hunks, all five are the valspec-pinned wiring points; CONFIG diff = exactly 3 hunks (warBoard row, warOrder item row, warEffort block); index.html diff = 1 line. No refactors of surrounding lines.

---

## Auditable re-verification of the two IO repairs

**R1 — CONFIG.js regionA.props warBoard row + treeStump comma restore** — VERIFIED, with one nuance to disclose:
- Node-verified HEAD-vs-worktree: HEAD props = 133 rows/0 holes, worktree = 134 rows/0 holes, delta = exactly the warBoard row; `treeStump` row present in both with identical commas (`{ asset: 'treeStump', x: 20.5, z: 2.5, rotY: 3.1, scale: 1.1 }` HEAD:229 → worktree:236, and the HEAD-level trailing `\n ,` continuation is byte-identical between HEAD:230 and worktree:237 — the R1 repair did not disturb the HEAD comma form).
- The one `-` line in the whole CONFIG diff is `flavor: 'A sad grey mush' }` → the warOrder row needed a comma after blandMush; that's the only deletion in the file. Legal (items-row comma repair, not a prop-row change), and does NOT touch regionA.
- The claimed computeFireSockets TypeError exposure is indeed gone: with 0 sparse holes the `props.length` loop cannot hit `undefined` rows; my census proves the loop is dense.
- Nuance (NON-BLOCKING): the warBoard comment block (CONFIG.js:229-234) documents the row as data-locked seat-only, with the module claiming it at load — comment accuracy matches the landed mechanism (`claimSeatRow()` splices the row OUT of `regionA.props` at module load; the placement engine therefore never sees it). Adversarial check: does the splice corrupt later readers? `computeFireSockets` reads `reg.cfg.props` fresh each call from `WH_REGION_DEFS` region configs — NOT `CFG.regionA.props` — so the module's splice of the CONFIG array does not starve it (regionA is flat, no terrain anyway, `groundHas()` false; and the warBoard row would be skipped by the `S[p.asset]` lookup regardless since `lightSockets` has no warBoard row). The splice also happens at module load (before `regionManager` caches `cfg`), so no ordering hazard found. VERIFIED SOUND.

**R2 — wareffort.js strict refund condition `removed < R.oreRequired`** — VERIFIED as re-coded, but the landed diff had drifted into a worse defect (BLOCKER-1) before this validation caught it:
- The strict condition is in place at wareffort.js:104 (`if (removed < req.count)`), refund only on partial take-back via `bag.addItem(req.id, removed)`; over-6 carry no longer triggers a refund (5-point carry sweep node-passes). The pre-repair `|| oreCount() >= R.oreRequired` clause is gone — the only `>=` reads are `near()` distance (line 216, correct) and none in tryTurnIn.
- The repair context also stated the b5/c9 probes pass — at delivered state they CRASHED (BLOCKER-1), because the same session introduced an `inv` shadow alongside the R2 edit. The shadow is now repaired and both probes pass; the repair is disclosed above. R2's condition itself is correctly strict.

---

## Waivers requested from IO (0 BLOCKING waivers needed — the 2 blockers were repaired in-frame, disclosed above)

- **WAIVED-none.** All valspec anchors PASS post-repair. MAJOR-1 and the MINORs carry no gate weight under the round's own laws (econ shape is PROPOSED pending Nicko tuning; no-harness law leaves day-1 gameplay to Nicko's playtest).

## Reproducibility note

Anyone re-running the valspec anchors gets the same result now: pre-repair the two turn-in probes crash (BLOCKER-1); post-repair all five probes (b1/c1/b2/b5/c9) exit 0 and the build's marker census holds. The two-line repair + one build rerun to the artifact are the ONLY tree mutations this validation made; everything else was read-only. All git calls were read-only (no commit/push/checkout/stage).
