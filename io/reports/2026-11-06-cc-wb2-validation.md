VERDICT: PASS

# CC-WB2 Validation Report (Testerbot, independent)

Round: cc-wb2 — doc 42 Part 2 repeat ladder on the landed CC-WB1 board.
Worktree /tmp/wh-worldfeat @ feat/world-visuals. All checks are node
one-shots against the REAL worktree files (THREE shim + fake game/inventory,
/tmp/wb1_smoke.js precedent). No harness run, no headless browser, no
browser automation; git usage strictly read-only (status/diff/rev-parse,
no stash). Valspec contract: io/specs/cc-wb2-ladder-valspec.md (v2,
e1c067cec91f2744735863c93e3b54ae719b039d4a4170e955fbb25598b44508).

## Verdict: PASS — 10/10 groups, ALL 184 checks PASS

| Group | What bound | Checks | Result |
|---|---|---|---|
| V-1 | CONFIG census + file-fence | 21 | PASS |
| V-2 | Payout table rows a,b,c..m + WB1 regression + toast bind | 44 | PASS |
| V-3 | Removal law (haul grammar) | 8 | PASS |
| V-4 | Repeat quotas 6→9→14→18→18 + repeatIndex vs new-day | 26 | PASS |
| V-5 | Persistence: keys, round-trip, clamps, WB1 restore | 27 | PASS |
| V-6 | Tally pins 1/4/8-cap, one root, iron | 15 | PASS |
| V-7 | Build exit 0, markers >= 6, stamp | 3 (bash) | PASS |
| V-8 | Runtime surface exact 6 fns, require-clean | 9 | PASS |
| V-9 | Ledger grep (whole-word) sources + CC-WB2 built sections | 3 | PASS |
| V-10 | NO-GIT audit (HEAD/sha/branch/stage) | 6 (bash) | PASS |

Validation one-shots (on disk, re-runnable): /tmp/wb2_harness.js (shared),
/tmp/wb2_v1.js, /tmp/wb2_v2.js, /tmp/wb2_v3.js, /tmp/wb2_v4.js,
/tmp/wb2_v5.js, /tmp/wb2_v6.js, /tmp/wb2_v8.js, /tmp/wb2_v9.js,
/tmp/wb2_v7_v9_v10.sh (V-7 + V-10), /tmp/wb2_poll.sh (V-0 landing poll).

## Pre/Post sha tables

### V-0b PRE-BUILD (Testerbot's own first recording, dispatch time 18:5xZ;
### == the IO pre-dispatch baselines byte-for-byte)

| File | sha256 (pre) |
|---|---|
| prototype/js/CONFIG.js | 9da84bd62ff3460a1e388cd57538b2dddbe8ab5ef7d45b26d53ad17d4020b9b2 |
| prototype/js/wareffort.js | 6f5d03af6e11266741b7cd2b69926765e5e08f66ee6a17038ea023ef1e12da99 |
| prototype/js/game.js | afe066a1697bf15d563914a15b9bccd1bfe300901d8f75a0f54e7131ffe733fd |
| prototype/index.html | 9fbae01d1583cd98bc9fb7ac08ea7deedb73623ba1af67afbd54b00d088b230b |
| prototype/builds/v8-playable.html | 984f295bb02fc60f7d63d737940a7c24794103456323ce6d8edd9e63867d9229 |
| tools/build_v8.py | b0819d7493320c92e46bd9534c4549a23aa44f8ff81f31ad3996306b27464eb1 |
| io/specs/cc-wb2-ladder-valspec.md (my contract) | e1c067cec91f2744735863c93e3b54ae719b039d4a4170e955fbb25598b44508 |

### V-0 POST-BUILD (the tree validated below; re-hashed AFTER every
### re-validation pass — identical)

| File | sha256 (post) | vs pre |
|---|---|---|
| prototype/js/CONFIG.js | 92cf9c5586ea11d96f4cb4d583fd171b1d02a63ecf5d98ef5272ebb83e734f3e | CHANGED (Devbot: ladder block +9 lines) |
| prototype/js/wareffort.js | ad4b7f05520c8e567bde287b30dd7afb5d9679a8310f4bdd222cb4742c67b1b4 | CHANGED (Devbot: ladder logic, +127/-9? per stat) |
| prototype/js/game.js | afe066a1697bf15d563914a15b9bccd1bfe300901d8f75a0f54e7131ffe733fd | UNCHANGED (zero-touch law) |
| prototype/index.html | 9fbae01d1583cd98bc9fb7ac08ea7deedb73623ba1af67afbd54b00d088b230b | UNCHANGED (zero-touch law) |
| prototype/builds/v8-playable.html | cac542d8cda27c9349a5138a73e2cda9afd53cd81ad74b8db7a750da784d352b | CHANGED (Devbot rebuild) |
| tools/build_v8.py | b0819d7493320c92e46bd9534c4549a23aa44f8ff81f31ad3996306b27464eb1 | UNCHANGED |

Build timing: Testerbot poll (/tmp/wb2_poll.sh, 30 s cadence) saw CONFIG.js
land first at poll+150 s from poll start, then wareffort.js at +180 s, and
the built artifact (V-7) about +300 s after CONFIG (a ~3.4-minute build, in
line with the brief's 3–4 min). No changes to either file were observed
AFTER validation began — the post-table shas above are from the tree at
validation time and match what Devbot landed (my /tmp/wb2_v*_probe.js
one-shots re-check these files directly).

## V-1 CONFIG census (/tmp/wb2_v1.js) — 21/21 PASS

- V-1a `CONFIG.warEffort.ladder` exists; keys EXACTLY the 7-set
  {basePay, overBonusStepPct, overBonusCapPct, repeatQuotaGrowthPct,
  repeatQuotaCapMult, repeatBasePayStepPct, overDoneText} (no extra, none
  missing).
- V-1b S-1 values EXACT and typeof number: basePay 0.5,
  overBonusStepPct 10, overBonusCapPct 100, repeatQuotaGrowthPct 50,
  repeatQuotaCapMult 3, repeatBasePayStepPct 15; overDoneText byte-exact:
  'Requisition filled. The quartermaster pays a bonus for the extra iron.'
- V-1c WB1 regions byte-identical (extracted `window.WH_CONFIG.warEffort = {...};`
  block byte-equals the pre-build extraction at
  /tmp/wb2_valspec_preflight/config_warEffort_wb1.txt): boardSeat
  {regionId hold_outskirts, x 5.9, z -15.5, rotY 3.14}, requisition
  (itemId warOrder, oreItemId ironOre, oreRequired 6, reward 3 stolenCoin,
  title/offer/doneTexts, PROPOSED comments), rotYFacesRoadNorth true,
  lsKey kept; items.warOrder present in CONFIG.
- V-1d `git diff --stat` shows EXACTLY 3 files:
  prototype/builds/v8-playable.html (138 lines) / js/CONFIG.js (9 lines) /
  js/wareffort.js (127 lines); `git diff --name-only` = those same 3.
  game.js and index.html appear in NO hunk (zero-touch law). build_v8.py
  sha unchanged (V-1g extension).
- V-1e CONFIG.js parses clean via node -e (fresh process).

## V-2 Payout table rows a..m EXACT (/tmp/wb2_v2.js) — 44/44 PASS

Row turn-in = public surface only: set day, tryOpen() award, add ore,
tryOpen() fill, assert coin delta + ore removal.

| row | state | ore carried | repeat | quota | coins from | over-band | result |
|---|---|---|---|---|---|---|---|
| a | fresh r0 | 6 (x=0) | r0 | 6 | 3 | x=0 | PASS 3 coins, 0 over, doneText |
| b | insufficient r0 | 5 of 6 | r0 | 6 | — | — | PASS 0 coins, ore kept, (5/6) toast |
| c | over r0 | 7 (x=1) | r0 | 6 | 4 | 1 | PASS 4 coins, overDoneText |
| d | over r0 | 8 (x=2) | r0 | 6 | 4 | 2 | PASS 4 coins (bonus rate 110%) |
| e | over r0 | 10 (x=4) | r0 | 6 | 6 | 4 | PASS 6 coins |
| f | over r0 | 16 (x=10) | r0 | 6 | 11 | 10 | PASS 11 coins (rate capped at 200%) |
| g | over r0 | 17 (x=11) | r0 | 6 | 12 | 11 | PASS 12 coins |
| h | over r0 | 26 (x=20) | r0 | 6 | 21 | 20 | PASS 21 coins |
| i | fresh r1 | 9 (x=0) | r1 | 9 | 5 | x=0 | PASS 5 coins (base 1.15x: 5750 m4) |
| j | over r1 | 10 (x=1) | r1 | 9 | 6 | 1 | PASS 6 coins |
| k | fresh r2 | 14 (x=0) | r2 | 14 | 9 | x=0 | PASS 9 coins (base 1.30x: 8800 m4) |
| l | fresh r3 | 18 (x=0) | r3 | 18 | 13 | x=0 | PASS 13 coins (base 1.45x: 13350 m4) |
| m | fresh r4 | 18 (x=0) | r4 | 18 | 14 | x=0 | PASS 14 coins (base 1.60x: 14400 m4) |

Rows a, b = WB1 regression bind: exact-quota turn-in pays 3 with the landed
requisition.doneText verbatim; below-quota turn-in: no coins, no removal,
the landed 'Not enough iron ore. (n/6)' grammar, board stays ACTIVE (no
spent-day leak — completing on the SAME day after a rejection still pays
properly). Toast bind per spec S-2: x>=1 -> ladder.overDoneText, x=0 ->
requisition.doneText. V-2h: CONFIG strings byte-identical to the runtime
choices. V-2d: removal EXACTLY `have`, not quota (see V-3 too).

## V-3 Removal law 16-ore case (/tmp/wb2_v3.js) — 8/8 PASS

- 16 ore carried at r0: EXACTLY 16 removed (haul grammar — no truncation
  to quota, no 6-ore subtraction), coins +11, carried ore 0 after,
  resolvedDay === postedDay === 10, capture.active false.
- 26 ore carried r0: EXACTLY 26 removed, coins +21.
- Control 6 ore r0: 6 removed, coins +3 (WB1 shape).

## V-4 Ladder repeat (/tmp/wb2_v4.js) — 26/26 PASS

- Accept-threshold probes: quota EXACTLY [9, 14, 18, 18] at r1..r4 (and
  6 at r0 = WB1 bind); q-1 probes rejected ('Not enough iron ore.
  (q-1/q)' + no removal + no pay + no resolve), q probes accepted.
  Quota pinned by prompt at award time (S-2 award-time law).
- repeatIndex increments once per FILL (not per re-post): r0→r1 after the
  first fill; +1 again at the next fill. No double-increment on re-posts.
- repeatIndex SURVIVES the new-day reset: same-day post-fill →
  rollback (r) → newDay → prompt re-arms → r SURVIVES (S-2: reset does NOT
  touch repeatIndex / V-5-restore clamp does not bleed into reset).
- Quota climbs only via RESOLUTION: idle re-post on the SAME day never
  bumps the shown quota.
- Row m (r4, ore 18) coin delta EXACTLY 14 across a full
  resolve-chain (re-verified under the V-4 harness shape too).

## V-5 Persistence (/tmp/wb2_v5.js) — 27/27 PASS

- Capture payload keys EXACTLY {active, postedDay, resolvedDay, repeatIndex}
  (4 keys, correct types after fills).
- Round-trip EXACT at r = 6, 9, 10, 20, 26: capture → restore(capture) →
  state, prompt, and capture byte-equal (coin economics re-checked at one
  point, matching V-2 row c at the equivalent r).
- restore(null) — and undefined/42/'garbage' — are no-ops keeping current
  state (no throw).
- WB1-shaped 3-key payload {active, postedDay, resolvedDay} (repeatIndex
  ABSENT) restores clean as repeatIndex 0 (V-5o) and keeps the WB1
  profile (active, postedDay, prompt at quota 6).
- Clamps (V-5n) EXACT to 0 with no throw: -3 → 0; '7' → 0 (string);
  2.5 → 0 (fractional); Infinity → 0; junk string → 0; true → 0;
  null → 0; {} → 0; [] → 0; missing key → 0.

## V-6 Tally pins (/tmp/wb2_v6.js) — 15/15 PASS

- Board root count EXACTLY ONE ('cc-wb1-war-effort-board') after 1 and 4
  resolves — no new roots (S-5) — after restore(10) and restore(3) too.
- Pin sub-group inside the board root: 'cc-wb2-repeat-tally', 1 pin after
  1 resolve, 4 after 4, 8 after restore(repeatIndex 10) = the S-3 render
  cap, 8 after restore(repeatIndex 8); 3 after restore(repeatIndex 3).
- Pins material iron (color 0x6e6a63) — no red, no second emissive.
- New-day reset does NOT remove/rebuild pins (S-3: rebuilt only on
  resolve/restore; 4 pins stay 4 across a day rollover probe).

## V-7 Build + markers (/tmp/wb2_v7_v9_v10.sh) — PASS

- python3 tools/build_v8.py exit 0 (re-run during validation: exit 0,
  deterministic: 3390907 bytes, sha cac542d8…).
- CC-WB2 marker count in prototype/builds/v8-playable.html: 6 (>= 6).
- Title stamp: `Witch Hunter v9 - EPR1 Combat (build 11-06 19:12Z a4d3736)`.
- Artifact bytes 3390907, sha256 cac542d8cda27c9349a5138a73e2cda9afd53cd81ad74b8db7a750da784d352b.

## V-8 Runtime surface (/tmp/wb2_v8.js) — 9/9 PASS

- CONFIG.js clean-require via node -e (fresh process, THREE shim).
- wareffort.js clean-require (THREE shim, CONFIG preloaded).
- `window.WH_WarEffort` exposes EXACTLY the 6 landed fns
  {init, tryOpen, interactPrompt, capture, restore, boardPos}, all
  typeof 'function'; arity census init(1)/tryOpen(0)/interactPrompt(0)/
  capture(0)/restore(1)/boardPos(0).
- Behavior probes: init builds 'cc-wb1-war-effort-board' in game.scene;
  boardPos → {x:5.9, z:-15.5}; idle prompt = landed WB1 token, no ladder
  leak before CONFIG addition is exercised; capture shape (4 keys) at idle.

## V-9 Ledger grep (/tmp/wb2_v9.js) — 3/3 PASS

Whole-word grep (grep -inw, NOT substring: the substring form false-positives
on 'pact' inside legitimate words like 'impact'/'compatible', e.g. CONFIG.js
animation 'impactCrossfadeSec' matches a raw substring but NOT its whole-word
law) for pact/creditor/Undersovran/debt:
- prototype/js/wareffort.js: 0 hits.
- CONFIG.warEffort block (the ONLY CONFIG region this round's law binds):
  0 hits.
- Built CC-WB2 sections in v8-playable.html (the ladder block + the
  wareffort module body, extracted, not the whole built html which carries
  other modules' lawful words): 0 hits.

## V-10 NO-GIT audit (/tmp/wb2_v7_v9_v10.sh + every terminal call) — PASS

- HEAD before any git-carrying probe: a4d3736d845895bcd0a1ccd7bfd6e04e364fe650
- HEAD after: a4d3736d845895bcd0a1ccd7bfd6e04e364fe650 (UNCHANGED).
- git log -1 = same sha (no new commits); git branch --show-current =
  feat/world-visuals (unchanged); nothing staged (git diff --cached
  empty; no git add/commit/push/branch/stash from Testerbot at any point —
  the only git verbs used were rev-parse, status --porcelain,
  diff --stat/--name-only/--cached --name-check, branch --show-current,
  log -1 --format=%H, all read-only).

## Deviations / notes

- NONE functional. Devbot's landed code matched the spec text within the
  S-2 rounding law at every probed row.
- V-2h toast-text binding (overDoneText vs doneText) is a valspec v2
  refinement over the v1 draft and is documented as such in the valspec;
  the landed code follows the spec's x>=1 rule exactly.
- V-1g (build_v8.py sha byte-checked unchanged) was extended this run per
  the mid-run clarification: the artifact + the tool are verified.
- No harness/browser playtest; Nicko's playtest is the acceptance bar for
  feel. These 184 checks bind CODE LOGIC only (payout arithmetic, state
  machine, persistence, DOM-free render census).

## Re-run for IO (2 commands)

```
cd /tmp/wh-worldfeat
for v in 1 2 3 4 5 6 8 9; do node /tmp/wb2_v$v.js || echo FAIL$v; done
bash /tmp/wb2_v7_v9_v10.sh
```

(All 10 also re-verified END of pass: same PASS totals, same shas as the
post table — nothing drifted while IO reviews.)

VERDICT: PASS
