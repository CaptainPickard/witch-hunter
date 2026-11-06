# CC-WB2 — War-Effort Reward Ladder (doc 42 Part 2 bands on the CC-WB1 board)

Spec author: IO (Autopilot wake 10, 2026-11-06). Repo worktree: /tmp/wh-worldfeat,
branch feat/world-visuals. Build: python3 tools/build_v8.py (repo root).
No harness runs, no headless browser smoke tests — node one-shots only; Nicko's
playtest is the acceptance bar.

## Scope

Add doc 42 Part 2's THREE-BAND REWARD LADDER to the landed CC-WB1 board
(js/wareffort.js @ a4d3736): QUOTA (base pay, unchanged WB1 economics),
OVER-DELIVERY (escalating per-item bonus on ore carried beyond quota, +10%/item,
per-item bonus rate capped at +100%), LADDER REPEAT (each resolution re-posts
the next day's contract at +50% quota, cap 3x base = 18 ore, and raises base
pay +15% per repeat). Turn-in hands over the WHOLE carried iron load
(hold-scale haul grammar) once the carrier reaches quota; below quota stays an
insufficient toast, nothing removed. The board mesh gains a REPEAT TALLY: one
oxidized-iron pin per completed repeat (render cap 8), echoing the doc 42
council-map planning surface.

The one-contract-per-day cadence, the new-day reset, the proximity gate, the
prompt chain, the save-wrap wiring (game.js capture/save/restore calling
WH_WarEffort.capture()/restore()) are all LANDED WB1 machinery — this round
touches ZERO lines in game.js and index.html. Additive capture payload keys
flow through the landed wrap untouched.

Ledger note: this is the war-effort/economy lane; doc 44's creditor-face law
does not bind board text (doc 42 texture: garrison/quartermaster flavor only).
No line names the creditor or the pact's terms.

## Art anchor (law 1)

concept-06-siege-council.png (viewed this wake): grim-dark council over a war
map; warm torch-amber vs cold moon-blue; bureaucratic weight. Palette law:
board stays WB1 parchment/oak + THE single amber lantern accent (unchanged);
tally pins = desaturated oxidized iron 0x6e6a63 (same iron as the bracket
strip), NO red (red = pact/danger law), no second emissive.

## S-1. CONFIG.js — CONFIG.warEffort.ladder (new key inside the warEffort block)

    ladder: {                            // CC-WB2 (doc 42 Part 2; all PROPOSED, Nicko tunes)
      basePay: 0.5,                      // coins per quota ore (WB1: 6 ore = 3 coins exactly)
      overBonusStepPct: 10,              // +10% per item over quota
      overBonusCapPct: 100,              // per-item bonus rate cap (+100%)
      repeatQuotaGrowthPct: 50,          // re-post growth per resolution
      repeatQuotaCapMult: 3,             // quota cap = 3x base (18 ore at base 6)
      repeatBasePayStepPct: 15,          // +15% base pay per repeat
      overDoneText: 'Requisition filled. The quartermaster pays a bonus for the extra iron.'
    }

Existing warEffort key boardSeat / requisition stay byte-identical.

## S-2. js/wareffort.js — payout law (EXACT integer arithmetic; no float drift)

Units law: all money math in integer MILLI-CENTS (1/10000 coin, name m4).
Per-item base rate at repeat index r (r = lifetime resolutions):

    baseM4(r) = 5000 + 750 * r                          // 0.5 coin +15%/repeat, exact ints
    quotaQ(r) = Math.min(Math.round(6 * Math.pow(1.5, r)), 18)   // r0 6, r1 9, r2 14, r>=3 18
    ratePct(k) = Math.min(100 + 10*k, 200)              // +10%/item over quota, +100% cap
    bonusM4(k, r) = baseM4(r) * ratePct(k) / 100        // exact int (bases are multiples of 250)

Payout once the turn-in reaches quota (ore = the WHOLE carried load, which the
board removes; x = ore - quotaQ(r)):

    payM4 = baseM4(r) * quotaQ(r) + SUM(bonusM4(k, r), k = 1..x)
    coins = Math.floor((payM4 + 5000) / 10000)          // round-half-up to whole coins

Pinned smoke table (valspec MUST bind every row; quota-band row b is the WB1
byte-regression):

  a. (ore 6,  r0) -> 3 coins      b. (ore <6, r0) -> insufficient, nothing removed
  c. (ore 7,  r0) -> 4  d. (ore 8, r0) -> 4  e. (ore 10, r0) -> 6
  f. (ore 16, r0) -> 11  g. (ore 17, r0) -> 12  h. (ore 26, r0) -> 21
  i. (ore 9,  r1) -> 5  j. (ore 10, r1) -> 6  k. (ore 14, r2) -> 9
  l. (ore 18, r3) -> 13  m. (ore 18, r4) -> 14 (quota pegged at cap, pay still grows)

State model: WB1's { postedDay, active, resolvedDay } gains ONE key
`repeatIndex` (int, lifetime resolutions). resolve increments it; the new-day
reset (rollNewDay) does NOT touch it; restore() of a WB1 3-key profile =
repeatIndex 0 (backward compatible). Award-time quota = quotaQ(repeatIndex).
Prompt while active: 'E - War Board (n/' + quotaQ(repeatIndex) + ' iron ore)'.
Turn-in toast: over-band uses CFG.warEffort.ladder.overDoneText when x >= 1,
else the existing requisition.doneText.

## S-3. js/wareffort.js — repeat tally pins (mesh law)

Tally = sub-group inside the EXISTING board root (the round still adds exactly
one scene root). Pins: iron 0x6e6a63 boxes 0.05 x 0.05 x 0.12 laid along the
lower frame front lip (y ~1.02, spacing 0.12, first pin x -0.42, board-local).
Render min(repeatIndex, 8). Rebuilt on resolve (+1 pin) and on restore
(tally mirrors restored repeatIndex); new-day reset leaves pins.

## S-4. Persistence (additive)

capture() payload { active, postedDay, resolvedDay, repeatIndex }. restore()
validates shape as landed (known-key subset) and clamps repeatIndex to a
non-negative integer (missing/foreign = 0). WB1 profiles (3 keys) load clean.
No lsKey, no schema bump — same save-ride as WB1.

## S-5. Out of scope (explicit)

No game.js/index.html edits (census-enforced). No standing/reputation economy
(doc 05 gates repeat tiers — standing not built; unbounded repeats this round,
PROPOSED). No war-state/siege multiplier (doc 13 not built). No second board,
no contract variety, no paper consumption change (papers remain receipts),
no vendor, no smelting, no Redseam/gather changes, no icon PNGs, no region
props/enemies/nodes changes anywhere, no new scene roots.

## S-6. Acceptance criteria (bind into valspec)

  1. node census: CONFIG.warEffort.ladder exists with the exact S-1 fields;
     boardSeat + requisition byte-identical to landed WB1; items.warOrder
     untouched; regionA/B/C/D/E/F rows untouched (git diff shows ONLY the
     warEffort block + wareffort.js changes).
  2. Payout table S-2 rows a..m ALL exact via node one-shot (fake game +
     inventory harness; set day, feed ore, call the public surface; assert
     coin deltas + inventory deltas).
  3. WB1 regression: row a (6 ore -> 3 coins) + row b (insufficient toast,
     no removal) byte-behavior identical to landed WB1.
  4. Over-delivery removal law: turn-in at ore 16 removes ALL 16 ore
     (haul grammar), +11 coins.
  5. Ladder repeat: resolve at r0 -> new-day award shows prompt quota 9;
     resolve again -> quota 14; resolve -> quota 18 (cap); resolve again ->
     quota still 18 and pay row m holds. repeatIndex increments per resolve
     and survives the new-day reset.
  6. Save round-trip: capture() -> restore() exact incl. repeatIndex;
     restore(null) fresh idle; WB1 3-key restore = repeatIndex 0.
  7. Census of files: ONLY prototype/js/CONFIG.js + prototype/js/wareffort.js
     modified (git status law); game.js + index.html byte-untouched
     (sha-preflight in valspec).
  8. Pins: after 1 resolve = 1 pin mesh child; after 4 = 4; after 10 = 8
     (render cap).
  9. Build: python3 tools/build_v8.py exit 0; CC-WB2 marker count in built
     html >= 6 (grep -o 'CC-WB2' | wc -l); artifact committed with the round.
 10. Runtime smoke: CONFIG loads clean; WH_WarEffort public surface unchanged
     (init/tryOpen/interactPrompt/capture/restore/boardPos).
 11. Ledger: no board string names the creditor, the pact, or its terms.
 12. NO harness runs, NO headless browser smokes (node one-shots only).
