# CC-WB2 Validation Spec (v2, Testerbot-owned; written BEFORE the Devbot build)

Round: cc-wb2 (doc 42 Part 2 ladder on the CC-WB1 board). Worktree
/tmp/wh-worldfeat @ feat/world-visuals, HEAD recorded at dispatch (V-0). Spec:
io/specs/cc-wb2-ladder-spec.md. Devbot brief: io/specs/cc-wb2-devbot-brief.md.
Test style: node one-shots ONLY (THREE shim + fake game/inventory harness,
/tmp/wb1_smoke.js precedent). NO harness runs, NO headless browser smoke
tests, NO browser automation of any kind (no-harness-playtest-gate standing
order). NO git writes (NO-GIT law): validate the working tree as found; IO
commits after the verdict. Read-only git (rev-parse/status/diff/log) is
allowed and REQUIRED for the census groups.

## Pre-checks (sha the files BEFORE reading them)

V-0. Record sha256 FIRST of all four law files: prototype/js/CONFIG.js,
     prototype/js/wareffort.js, prototype/js/game.js, prototype/index.html,
     + prototype/builds/v8-playable.html (pre-build) and
     `git -C /tmp/wh-worldfeat rev-parse HEAD`. After validation re-run all
     and diff: you must know you validated what Devbot actually wrote, not a
     later/earlier state. The report carries the pre/post sha table.
     IO-logged pre-dispatch baselines (must MATCH before Devbot lands):
     game.js afe066a1697bf15d563914a15b9bccd1bfe300901d8f75a0f54e7131ffe733fd,
     CONFIG.js 9da84bd62ff3460a1e388cd57538b2dddbe8ab5ef7d45b26d53ad17d4020b9b2,
     wareffort.js 6f5d03af6e11266741b7cd2b69926765e5e08f66ee6a17038ea023ef1e12da99,
     index.html 9fbae01d1583cd98bc9fb7ac08ea7deedb73623ba1af67afbd54b00d088b230b.
     A mismatch before Devbot lands = the tree changed under dispatch; STOP
     and re-derive before designing checks.
V-0b. Preflight: `game.js` + `prototype/index.html` must exist and sha
     UNCHANGED through validation (S-6.7 zero-touch law) — re-check at both
     ends. HEAD sha must be UNCHANGED from the V-0 recording whenever the
     verdict runs (V-10 re-proves at the end).

## Landing gate (poll discipline)

Devbot lands CONFIG.js + wareffort.js edits + a rebuilt build artifact.
Poll with `sha256sum` until BOTH hold, or poll >= 15 minutes before any FAIL
conclusion: (i) CONFIG.js or wareffort.js pre-sha CHANGED (the ladder is
landing), (ii) built html contains the 'CC-WB2' marker. A landing detected
mid-poll re-pins V-0's post-baselines; re-check game.js/index.html shas are
still at the V-0 values before treating the tree as validatable.

## V-groups (each a numbered node check; bind spec S-6)

V-1 CONFIG census (S-6.1) — exact assertions:
  - V-1a: CONFIG.warEffort.ladder exists with EXACTLY the 7 keys basePay,
    overBonusStepPct, overBonusCapPct, repeatQuotaGrowthPct,
    repeatQuotaCapMult, repeatBasePayStepPct, overDoneText (Object.keys set
    equality on the ladder object).
  - V-1b: ladder values EXACT per S-1: basePay === 0.5, overBonusStepPct ===
    10, overBonusCapPct === 100, repeatQuotaGrowthPct === 50,
    repeatQuotaCapMult === 3, repeatBasePayStepPct === 15, overDoneText ===
    'Requisition filled. The quartermaster pays a bonus for the extra iron.'
    (6 numerics typeof 'number', overDoneText typeof 'string').
  - V-1c: boardSeat + requisition + items.warOrder byte-identical to the
    pre-build WB1 block (sha/JSON identity vs the V-0 snapshot).
  - V-1d: `git --no-pager diff --stat` (and `git diff --` hunk scan) shows
    ONLY prototype/js/CONFIG.js + prototype/js/wareffort.js (+ the built
    artifact); game.js / index.html appear in NO hunk.
  - V-1e: CONFIG.js parses clean: `node -e "require(prototype/js/CONFIG.js)"`.

V-2 Payout table (S-6.2) — EXACT via module public surface
  (set day via fakeGame.dayNight.day, award paper via tryOpen, add ore via
  bag.addItem('ironOre', n), tryOpen() to turn in; assert coin delta =
  bag.countOf('stolenCoin') and ore removal = bag.countOf OreItemId):
  - V-2f rows pinned EXACTLY (no re-derivation — this table is the truth;
    quota-band rows a,b are also the WB1 regression bind S-6.3):
      a. ore 6,  r0 -> +3 coins, 0 ore left, 0 coins before
      b. ore 5,  r0 -> insufficient toast, NOTHING removed, coin delta 0
      c. ore 7,  r0 -> +4
      d. ore 8,  r0 -> +4
      e. ore 10, r0 -> +6
      f. ore 16, r0 -> +11
      g. ore 17, r0 -> +12
      h. ore 26, r0 -> +21
      i. ore 9,  r1 -> +5
      j. ore 10, r1 -> +6
      k. ore 14, r2 -> +9
      l. ore 18, r3 -> +13
      m. ore 18, r4 -> +14   (quota pegged at cap 18; base pay still grows)
    each row: fresh board state at the pinned repeatIndex, exactly `ore`
    carried, one tryOpen; assert the coin delta EXACTLY equals the pinned
    value and (rows c..m, i..m over-band rows) the carried ore countOf is 0
    after turn-in; the toast text for x>=1 rows is ladder.overDoneText (V-2g)
    and for row b the landed requisition-doneText-family insufficiency
    message (row b = WB1 byte-behavior: same landed '(n/6)' toast grammar).
  - V-2g: x >= 1 turns use ladder.overDoneText toast text EXACTLY (the S-1
    string, verbatim); x === 0 turn-ins use the landed requisition.doneText
    verbatim ('Requisition filled. The quartermaster marks the board.').

V-3 Removal law (S-6.4): r0 turn-in carrying EXACTLY 16 ore removes ALL 16
  (countOf before === countOf after + 16; NOT quota-truncated at 6/10),
  pays +11 coins (row f). Extra case: carrying 26 at r0 removes 26, +21
  (row h) — removal is never quota-clamped.

V-4 Ladder repeat (S-6.5) — exact assertions:
  - V-4h quota sequence at award/turn-in time by repeatIndex:
    r0->6, r1->9 (round(6*1.5^1)), r2->14 (round(13.5)=14 per
    round-half-up law — NOT 13), r3->18 (Math.round(20.25)=20 capped by
    repeatQuotaCapMult*base 18), r4->18 (pegged). Assert via
    interactPrompt's '(n/q)' quota slot while active at each r, and via the
    turn-in accept threshold (ore = q-1 insufficient, ore = q accepted).
  - V-4i prompt template byte-kept: while active
    'E - War Board (' + oreCount + '/' + quota + ' iron ore)' with the
    landed WB1 prompt shape, only the number now ladder-derived.
  - V-4j repeatIndex increments EXACTLY once per resolve, never at award,
    never at new-day; resolve at r -> day rollover -> interactPrompt()
    -> repeatIndex still r (rollNewDay law: S-4 pinned); the next day's
    award then shows the SAME r-quota (not r+1).
  - V-4k row m bind: at r4 with ore 18 (>= quota 18, x=0) the payout is
    14 coins pinned (row m of the table); the r4 base-rate 1.5^4
    growth carries it (baseM4(4) = 8000), NO re-derivation license.

V-5 Persistence (S-6.6) — exact assertions:
  - V-5l capture() payload after a real resolve has EXACTLY the 4 keys
    {active, postedDay, resolvedDay, repeatIndex} (Object.keys set equality,
    no 5th key, none missing) — additive B-5 (no lsKey, no schema bump).
  - V-5m round-trip: restore({active:true, postedDay:N, resolvedDay:null,
    repeatIndex:R}) then capture() deep-equals the payload EXACTLY for
    R = 0, 1, 7, 18.
  - V-5n clamp law: restore with repeatIndex -3 / '7' (string number) /
    2.5 / Infinity / 'x' (junk string) / true / absent key all produce
    capture().repeatIndex === 0 exactly (non-negative int; missing/foreign
    = 0; no throw).
  - V-5o WB1 3-key restore: restore({active, postedDay, resolvedDay})
    exactly (no repeatIndex key) loads with capture() =
    {active, postedDay, resolvedDay KEPT, repeatIndex: 0} — backward
    compatible; spent/papers visibility restored per landed law.
  - V-5p restore(null) / restore(undefined) / restore('garbage') /
    restore([]) / restore(42): no throw, state unchanged-and-clean per the
    landed WB1 restore law.

V-6 Pins (S-6.8) — exact assertions:
  - V-6q tally sub-group inside the EXISTING board root: after 1 resolve ->
    1 pin child; 4 resolves -> 4; restore({repeatIndex:10, active:false,
    postedDay:1, resolvedDay:1}) -> 8 (render cap); restore repeatIndex 3 ->
    3. Pins = iron 0x6e6a63 material; NO red (the three-shim census reads
    material.color identity, not pixel color).
  - V-6r one board root EXACTLY: game.scene's added root list contains
    EXACTLY one object named 'cc-wb1-war-effort-board' (S-5: no new roots,
    no rename); tally is a SUB-group of that root, not a sibling.

V-7 Build + markers (S-6.9) — exact: `python3 tools/build_v8.py` runs from
  the repo root with exit code 0; 'CC-WB2' marker count in
  prototype/builds/v8-playable.html via `grep -o 'CC-WB2' | wc -l` >= 6;
  the report logs the byte size of the built artifact and its title stamp;
  build writes nothing outside the census of V-1d.

V-8 Runtime surface (S-6.10) — exact: node one-shot loads real CONFIG.js
  + real wareffort.js with the THREE shim; WH_WarEffort exposes exactly the
  6 public functions {init, tryOpen, interactPrompt, capture, restore,
  boardPos} — Object.keys(WH_WarEffort) length EXACTLY 6, every key typeof
  'function', no extra/missing key, no changed signature vs WB1.

V-9 Ledger (S-6.11) — exact: grep case-INSENSITIVE over the FULL text of
  prototype/js/wareffort.js and the FULL warEffort block of CONFIG.js (plus
  the built html) for 'pact', 'creditor', 'Undersovran', 'debt' —
  ZERO hits anywhere in those scopes (the round board lane speaks
  garrison/quartermaster flavor only; the doc-44 creditor face never leaks).

V-10 NO-GIT audit (final): `git -C /tmp/wh-worldfeat rev-parse HEAD` equals
  the V-0 sha; `git status --porcelain` has no NEW staged rows; `git diff
  --cached` EMPTY; `git log -1 --format=%H` equals the V-0 sha. No
  commit/push/stage/branch by this validator (read-only git only).

## Harness law (all V-groups)

- ONE node one-shot per group where practical (bash-chained node -e blocks
  acceptable for the greps/sha lines).
- Fake inventory = /tmp/wb1_smoke.js shape (slots, cap 60/stack, addItem /
  removeItem / countOf); coins = stolenCoin; ore = ironOre; paper = warOrder.
- fakeGame = dayNight.day settable integer; regionManager.logic.activeId =
  'hold_outskirts' (boardSeat region); player alive, unsuspended, pos at the
  boardSeat (5.9, -15.5); inventoryUI.toast captured in an array; scene.add
  captured; THREE shim sufficient for boardBody + tally pins (mesh / group /
  material shims with the actual construction args retained for census).
- No new file writes inside the worktree from the validator (report and
  scratch scripts live at /tmp; the ONLY worktree write is the verdict
  report io/reports/2026-11-06-cc-wb2-validation.md).

## Verdict file

Write io/reports/2026-11-06-cc-wb2-validation.md (worktree): FIRST line is
the one-line `VERDICT: PASS` or `VERDICT: FAIL` banner, then per-group
PASS/FAIL with the actual node one-shot output lines, the two sha tables
(pre/post per V-0), and — on any FAIL — every failed check with observed
vs expected value. No partial PASS: any FAILing group = FAIL verdict.
Cross-bind: V-0 sha recording is mandatory FIRST (before reading any new
code); if the two V-2 runs read different shas (V-2a/V-2b at different
times), both readings go in the report and the SECOND is the validated one,
explicitly labeled.
