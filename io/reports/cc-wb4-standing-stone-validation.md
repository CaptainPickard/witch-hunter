VERDICT: PASS

CC-WB4 Standing Stone — independent re-validation (Testerbot round 2).
Re-executed every gate V0..V13 per io/specs/cc-wb4-standing-stone-valspec.md.
Worktree /tmp/wh-worldfeat, branch feat/world-visuals, HEAD f98b83c032466837d6e17997ace6f2b7556e16ef
(UNCHANGED start-to-finish). Node one-shots only; NO git writes; NO harness
browser; NO npm; NO network. Harness mirrors the WB2 valspec shape (v4rows.js
battery): real CONFIG.js+wareffort.js loaded fresh per boot, fake inventory/
game, WH_AFF stub with deed LOG-ONLY (score pinned per row), WH_JOURNAL stub.

GATE VERDICTS (14 gates: 14 PASS / 0 FAIL)

V0 PASS — sha-law. Recorded FIRST (before reading any landed code).
  Dispatch pins (required): game.js, index.html, style.css matched EXACTLY at
  first read. git rev-parse HEAD == f98b83c032466837d6e17997ace6f2b7556e16ef.
  V0 pre/post sha256 table (identical pre vs post; no drift):
    prototype/js/CONFIG.js  abd9808f1ad1d5bc84d394edb359788a9b42112e04cf028bcae24456252de062
    prototype/js/wareffort.js e15b3ae9557bc44af2e6417e24b7b93064928fdb49dd18004ffc42428489fcd7
    prototype/js/game.js    226bb7d5bbed70edf980aa4b8ffbcd141355c878eb419ce3fe47d9cf9b1f03ec  (pin match)
    prototype/index.html    ea80cb3d4aace34f55d4bdf221e2b50beae1174e189356919c4f55178e316ed7  (pin match)
    prototype/style.css     2eb19186c0f4310938d73ac30fffc34b9dd53248eea66582e114b6101f764bda  (pin match)
    prototype/builds/v8-playable.html e2b4c8939ae8298e100e9c2a73c1a8c482e569a31796538be0a479691ac558cf

V1 PASS — diff law. git status/diff: EXACTLY prototype/js/CONFIG.js
  (+25/-0), prototype/js/wareffort.js (+145/-11) + the V12 artifact
  prototype/builds/v8-playable.html (+171/-12). game.js/index.html/style.css
  byte-identical (pins above; hunk scan zero hits).

V2 PASS — CONFIG census. repeatStanding === 25 (number); stone keys EXACTLY
  {thresholdRepeats,quotaCapMult,payPct,offerText,doneText,crossingToast},
  values 3 / 4 / 130 (numbers) with all THREE strings byte-EXACT
  (grep -F count 1 each over the landed file). journal.topics.warEffortStone
  key set {id,title,source,body} exact, id 'war-effort-stone', title
  'The requisition stone', source 'The quartermaster', body
  'Three hauls to the war board and the hold raised its requisition stone.
  The quartermaster counts larger contracts on it now - the front grows, and
  the hold grows with it.' (landed single-quote style, values exact;
  grep -F: 'id...stone' =1, title =1, source =1 [word matches 4 across
  topics], body =1). Topics APPEND-ONLY: old topics 8 -> new 9, added
  [warEffortStone] ONLY. boardSeat/requisition/ladder/rotYFacesRoadNorth/
  lsKey all JSON-identical to the pre-build snapshot (JSON.stringify deep
  equal). weExtraKeys vs old = [repeatStanding, stone] only.

V3 PASS — ledger law (case-insensitive zero hits for pact/creditor/
  undersovran/debt). Scopes: FULL wareffort.js = 0/0/0/0; CONFIG warEffort
  block = 0/0/0/0; warEffortStone topic = 0/0/0/0; built artifact CC-WB4
  scopes (warEffort block, stone topic, embedded wareffort.js region
  CC-WB2-anchor..boardPos) = 0/0/0/0. All four new strings byte-present in
  CONFIG.js AND the built html, individually ledger-clean. Full-text scan of
  the built artifact returns 43/2/0/1 — adjudicated: byte-IDENTICAL
  pre-build (git show f98b83c artifact = 43/2/0/1); every hit is pre-existing
  prior-round text (inlined three.js bundle substrings 'compaction',
  '.clipaction', 'shieldimpact'; QJR-4 bestiary comments 'no creditor, no
  signatory, no terms'), NOT CC-WB4 text.

V4 PASS — pinned rows a..q EXACT (v4rows.js, one battery, valspec text
  binding; coins = countOf('stolenCoin') delta, haul never quota-truncated):
  a r0 press score0 -> 1 warOrder, active true, postedDay 1, toast
    ===RQ.offerText, requisition topic appended. PASS
  b r1 press score24 -> waiting toast EXACT, 0 warOrder, active false,
    postedDay null, requisition topic NOT appended. PASS
  c r1 press score25 -> paper, RQ.offerText, prompt
    'E - War Board (0/9 iron ore)'. PASS
  d r1 ore9 score60 -> +5 exactly, haul removed, firstFill appended. PASS
  e r2 ore14 -> +9. PASS
  f fill at r2 14 ore -> stone-topic count 1, stoneSeen true, toast pair
    [crossingToast, ST.doneText] in order, coins 9 (pay 91000 pre-rise r2
    law), NEXT award r3 toasts ST.offerText, exactly ONE warEffortFill deed
    (no crossing deed). PASS
  g restore {P5 r3 flag} 3 ore -> prompt 'E - War Board (3/20 iron ore)'. PASS
  h r3 ore20 -> +19, ST.doneText. PASS
  i r3 ore22 -> +21, overDoneText (over>=1 wins). PASS
  j r4 3 ore -> 'E - War Board (3/24 iron ore)'. PASS
  k r4 ore24 -> +25, ST.doneText. PASS
  l r5 3 ore -> 'E - War Board (3/24 iron ore)' SAME string as j (cap peg). PASS
  m r4 ore26 -> +27. PASS
  n fill 20 at r3 flag-true -> count stays 0 (NO append), stoneSeen stays
    true, toast ST.doneText, coins 19, second triggering resolve appends
    nothing. PASS
  o restore WB2 4-key r5 (no flag) -> topic appended once, stoneSeen true,
    crossingToast EXACT, dressing rebuilt (3 children), prompt
    'E - War Board (0/24 iron ore)', deed log EMPTY (crossing pays NO
    standing). PASS
  p restore WB1 3-key -> capture EXACTLY
    {active:false,postedDay:2,resolvedDay:2,repeatIndex:0,stoneSeen:false},
    NO topic, NO toast. PASS
  q fresh r0 flag false, 3 fills at d+1/d+2/d+3 (6/9/14 ore) -> topic counts
    after each resolve [0,0,1] — crossing fires EXACTLY on the third
    resolve, crossingToast EXACT there, stoneSeen true. PASS

V5 PASS — award/done text law at the stone tier. r3 idle press (score 60)
  toasts ST.offerText EXACTLY; r3 quota-exact fill toasts ST.doneText
  (post-resolve tier); r3 over-band (22 ore, V4i) keeps landed overDoneText;
  journal appends UNCHANGED (r3 award STILL appends 'war-effort-requisition',
  every fill STILL appends 'war-effort-first-fill'); idle prompt UNCHANGED
  'E - War Board (Take a requisition)'.

V6 PASS — gate is re-post-only. Turn-in branch fires with score 1 at r1
  (9 ore -> fill succeeds, +5). r0 press at score 0 AND at score 24 both
  award (gate never binds r0; 25 is NOT the r0 law — RS gates r>=1 only).
  Blocked press leaves postedDay null and the press is consumed (return
  true, waiting toast, NO paper, NO day). Same-day re-press at score 60
  awards: postedDay set by the re-press on the SAME day (block consumed no
  day). Rows d/e at score 60 pass; r2 turn-in at score 1 pays WB2-exact +9 —
  the gate never touches turn-in (S-6.3 shape). Prior-child V6 adjudication
  (deleg_d84da3a4 pinned trace: blocked press -> postedDay null +
  resolvedDay null) CONFIRMED consistent with the valspec wording; isolated
  one-shot re-evidenced fresh here (V4b + V6 above) — PASS.

V7 PASS — once-law across paths. f/n/o/q each as its own fresh one-shot:
  f=1, n=0, o=1, q=1; within each path a second triggering resolve/restore
  appends NOTHING more (f second resolve count stays 1; o second restore of
  the captured flag payload stays 1; q 4th resolve stays 1). Row o's WB2
  payload carries no flag -> the restore law re-arms and the crossing
  legitimately fires once per profile (valspec rationale adopted). Deed log:
  exactly one 'warEffortFill' per fill (4 fills = 4 deeds in the q-loop
  extension), NEVER any crossing deed.

V8 PASS — restore law. restore({}) AND restore({stoneSeen:'x'}) = no-op
  (state unchanged, fresh r0 defaults); restore({active:true,postedDay:1,
  resolvedDay:1,stoneSeen:'x'}) = recognized keys admitted + stoneSeen false
  (wrong-typed flag beside recognized keys does NOT poison the load);
  MEANINGFUL flag: restore r5 flag-true = NO topic, NO toast (flag
  silences); rollNewDay after crossing: post-crossing payload
  {resolvedDay:5} at day 6 -> the press first ROLLS (active/postedDay/
  resolvedDay reset) then CONTINUES into the idle branch — one-press
  re-post at score 60 with repeatIndex 5 + stoneSeen true SURVIVING
  (landed interact/press flow; corroborated live by V4q), plus the
  same-day-spent press consumed with postedDay still 5. capture() key set
  EXACTLY {active,postedDay,resolvedDay,repeatIndex,stoneSeen}; fresh r0
  after restore({}) = all-default + stoneSeen false.

V9 PASS — public surface. Object.keys(WH_WarEffort) EXACTLY
  {init,tryOpen,interactPrompt,capture,restore,boardPos} (6 keys, sorted
  boardPos,capture,init,interactPrompt,restore,tryOpen), every value
  typeof 'function', no extra/missing key vs landed WB1/WB2 shape.
  CONFIG parses clean via global.window=global require one-shot (module top
  throws nothing, NO THREE required — loaded without any THREE shim).

V10 PASS — headless (window.THREE undefined). init(g) does NOT build:
  scene.add called 0 times (no cc-wb1 board, no cc-wb2 tally, no cc-wb4
  stone anywhere in the scene). capture() returns the 5-key payload.
  restore at repeatIndex 5 (flagless) does NOT throw, leaves sane values
  (repeatIndex 5 held, active true), sets stoneSeen true (state law, visuals
  only skipped), appends the stone topic once (journal is not a visual),
  fires the crossing toast via the inventoryUI stub (toast() is not
  THREE-gated; landed law).

V11 PASS — dressing census (retained-construction-args shim). Group
  'cc-wb4-stone-dressing' EXISTS at r0 with 0 children, created INSIDE the
  EXISTING 'cc-wb1-war-effort-board' root (NOT a sibling; board root count
  exactly 1), built AFTER the cc-wb2-repeat-tally group in buildBody order,
  BEFORE any headless guard decision. At r=3 (restore): EXACTLY 3 children —
  plinth BoxGeometry(0.7,0.5,0.45) pos (-0.55,0.25,-0.35) color 0x8a8577
  roughness 1.0 (NEW stone-gray material, not board oak/parch); pole
  BoxGeometry(0.04,0.8,0.04) pos (-0.8,2.6,0.1) oak 0x4a3a2a; pennant
  PlaneGeometry(0.4,0.28) pos (-0.58,2.78,0.1) parch 0xd2b48c DoubleSide.
  Pole/pennant SHARE the board's own oak/parch material OBJECTS (identity
  compare true), NO red, NO second emissive; tri budget 12+12+2 = 26 <= 120.
  Fill r2->r3 leaves 3 children IMMEDIATELY (call-site proof). Double
  restore = clear-then-fill, still exactly 3 (no duplication).

V12 PASS — deterministic rebuild. python3 tools/build_v8.py exit 0;
  'CC-WB4' marker count in prototype/builds/v8-playable.html = 21 >= 6
  (three consecutive greps: 21, 21). TWO consecutive builds byte-identical
  (sha e2b4c893...ac558cf both runs). The LANDED artifact was ALREADY
  byte-identical to the deterministic rebuild (pre==A1, cmp SAME), so the
  dirty artifact = the deterministic built state. Title stamp carries HEAD's
  pinned commit date + short sha: 'build 11-08 12:10Z f98b83c'
  (DETERMINISTIC-BUILD law holds: stamp from the pinned HEAD).

V13 PASS — this verdict file at io/reports/cc-wb4-standing-stone-validation.md,
  first line VERDICT: PASS, per-gate PASS with actual one-shot output lines
  (representative) + the V0 pre/post sha table. NO partial PASS: every gate
  green. NO repo commits/stages/pushes by the tester (git writes 0; the ONLY
  repo write is this file, per the valspec V13 law).

AMENDMENT LOG
  AMEND-1 (V3, built-artifact scope): the FULL-TEXT grep of the built html
  carries the whole prior-round bundle, whose inlined three.js r185 code and
  QJR-4 bestiary comments contain pre-existing 'pact'/'creditor' substring
  hits (43/2 pre == 43/2 post, byte-identical). Adjudicated per V3's own
  scope list: the ROUND-Touched scopes (full wareffort.js text, warEffort
  CONFIG block, stone topic, built CC-WB4 scopes) are ALL zero-hit — PASS.
  The full-file residual is documented, not suppressed.

EVIDENCE FILES (outside the repo)
  /tmp/wb4v2_out/v4rows.js     — V4 rows a..q + V5 + V6 + V7 + V8 + V9
                                 battery: SUMMARY 90/90 failures=0 (exit 0)
  /tmp/wb4v2_out/v3v10v11.js   — V3 ledger + V10 headless + V11 dressing:
                                 SUMMARY 60/60 failures=0 (exit 0)
  /tmp/wb4v2_out/v4_pins.js    — independent V4 pin census (min(r,8)):
                                 rootCount 1, tally-sub-of-root, iron
                                 0x6e6a63 shared, no red — all PASS
  /tmp/wb4v2_out/art_pre.html  — artifact snapshot byte-compared around the
                                 double rebuild (cmp SAME)
  Prior /tmp/wb4v_out logs cross-checked: v6_core/v7v8 legacy-profile greens
  corroborate; v8.log's 3 stale-fails (score-only stub without WH_AFF.deed
  + legacy coin-seed drift) are re-evidenced PASS on fresh runs here.
  WB2 byte-regression rows d/e/f also cross-read vs cc-wb2-ladder-valspec.md
  pin shape — consistent.

RESULT: 14 gates, 14 PASS, 0 FAIL, 0 BLOCKERS. CC-WB4 standing-stone round
is VALIDATED at HEAD f98b83c (uncommitted CC-WB4 tree = the round under
test; artifact = deterministic rebuild, byte-stable).
