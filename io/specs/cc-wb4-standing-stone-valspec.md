# CC-WB4 Validation Spec (Testerbot-owned; written BEFORE the Devbot build)

Branch: feat/world-visuals. Worktree: /tmp/wh-worldfeat. HEAD locked at f98b83c
(V0 sha table). Spec: io/specs/cc-wb4-standing-stone-spec.md. Node one-shots
ONLY — no harness runs, no headless browser smokes (no-harness-playtest-gate
standing order). Read-only git allowed for the census groups (V0/V1). NO
commits/pushes/stages by the validator (IO owns git); the validator's ONLY
worktree write is the verdict file (V13).

## Census (pre-build binding)

V0. sha-law: record FIRST (before reading any new code) sha256 of
    prototype/js/CONFIG.js, prototype/js/wareffort.js, prototype/js/game.js,
    prototype/index.html, prototype/style.css, prototype/builds/v8-playable.html
    + `git rev-parse HEAD` == f98b83c032466837d6e17997ace6f2b7556e16ef. At
    dispatch (pre-build, recorded): game.js
    226bb7d5bbed70edf980aa4b8ffbcd141355c878eb419ce3fe47d9cf9b1f03ec,
    index.html ea80cb3d4aace34f55d4bdf221e2b50beae1174e189356919c4f55178e316ed7,
    style.css 2eb19186c0f4310938d73ac30fffc34b9dd53248eea66582e114b6101f764bda.
    Re-run all shas at the end and carry the pre/post table in the verdict; HEAD
    must be UNCHANGED whenever the verdict runs. A mismatch before the build
    lands = the tree changed under dispatch; STOP.

V1. git status/diff law: ONLY prototype/js/CONFIG.js + prototype/js/wareffort.js
    modified, PLUS prototype/builds/v8-playable.html from the V12 build step
    (source census before the build: exactly 2 modified; after the build: exactly
    those 2 + the artifact); game.js, index.html, style.css byte-identical to
    the V0 shas (git diff --stat + hunk scan; sha256sum per V0).

V2. CONFIG census: warEffort.repeatStanding === 25 (typeof 'number');
    warEffort.stone Object.keys set equality EXACTLY {thresholdRepeats,
    quotaCapMult, payPct, offerText, doneText, crossingToast} (6 keys, no more,
    no less) with thresholdRepeats === 3, quotaCapMult === 4, payPct === 130
    (typeof 'number') and the THREE strings byte-EXACT per spec S-1:
    offerText === 'The requisition stone stands at the board. The hold wants
    more iron for the front.'; doneText === "The stone accepts the haul. The
    quartermaster pays by the stone's word."; crossingToast === 'The hold
    raises the requisition stone.'. journal.topics.warEffortStone key set
    exactly {id, title, source, body} with id === 'war-effort-stone',
    title === 'The requisition stone', source === 'The quartermaster', body
    === 'Three hauls to the war board and the hold raised its requisition
    stone. The quartermaster counts larger contracts on it now - the front
    grows, and the hold grows with it.' (single-line strings; topics APPEND
    ONLY). boardSeat/requisition/ladder JSON-identity vs the V0 pre-sha
    snapshot (JSON.stringify deep-equal).

V3. Ledger law: grep case-INSENSITIVE over the FULL text of
    prototype/js/wareffort.js, the FULL warEffort block of CONFIG.js, the full
    warEffortStone journal topic, and the built html (V12 artifact), for
    'pact', 'creditor', 'Undersovran', 'debt' — ZERO hits in any of those
    scopes. The four new strings + the topic body checked individually too.

## Behavioral one-shots (node, fake game + inventory + WH_AFF/WH_JOURNAL stubs)

Harness shape: mirror io/specs/cc-wb2-ladder-valspec.md. ONE node one-shot per
gate where practical. Load the REAL post-build CONFIG.js via
`global.window = global; require('<worktree>/prototype/js/CONFIG.js')` (no
THREE needed at module top) so the harness reads the real ST/RS/JT rows; then
load the REAL post-build prototype/js/wareffort.js. fake game:
inventory {addItem, removeItem, countOf} (cap 60/stack; coins stolenCoin, ore
ironOre, paper warOrder), dayNight.day a settable integer, regionManager.logic.
activeId = 'hold_outskirts', player {state:'alive', inputSuspended:false,
pos:{x:5.9, z:-15.5}}, inventoryUI.toast captured into an ordered array,
scene.add captured. WH_AFF stub: { score: () => <configurable>, deed: (id) =>
{ deeds.push(id); } } — deed is REQUIRED (the landed fill path calls
WH_AFF.deed('warEffortFill') on every fill; a score-only stub throws on the
first turn-in) and its log is asserted: exactly one 'warEffortFill' deed per
fill, NO extra deed at the stone crossing (S-5: the stone does not pay
standing). WH_JOURNAL stub: { appends: [], append: (id, title, body, a, src)
=> { appends.push({id, title, body, src}); } } — the 5-arg landed shape; the
once-law counters read appends filtered by id === 'war-effort-stone' ONLY
(every fill also appends the landed requisition/firstFill topics — those are
not counted).

V4. Pinned rows a..q of spec S-4 — every row exact. THE TABLE IS THE TRUTH:
    the tester re-derives NOTHING (node truth, recomputed at spec-writing:
    quotaQ prestone 6,9,14,18,18 / stone 6,9,14,20,24 — capMin laws; stone
    baseM4 floor(7250*1.3)=9425, floor(8000*1.3)=10400; d 51750 m4 -> 5;
    e 91000 -> 9; h 9425*20=188500 -> 19; i 188500+floor(9425*1.1)=10367
    +floor(9425*1.2)=11310 = 210177 -> 21; k 10400*24=249600 -> 25;
    m 249600+floor(10400*1.1)=11440+floor(10400*1.2)=12480=273520 -> 27;
    coinsFrom floor((pay+5000)/10000)); a value mismatch = the BUILD is
    wrong, never the table. Per-row WH_AFF score: score 60 (gate
    non-binding) in every economic row (d..m, o..q), and the gate rows
    pinned at a/c 0/25, b 24, V6 1. Rows d..m: fresh board state at the
    pinned repeatIndex, exactly `ore` carried, one tryOpen; assert coin
    delta = countOf('stolenCoin') delta EXACTLY and the FULL carried haul
    removed (countOf ironOre 0 after — removal is never quota-truncated,
    landed law), plus toast per V5's choice law.
    a  r0 idle press score 0      -> 1 warOrder added, active true, postedDay =
                                     day, toast === RQ.offerText exactly, requisition
                                     journal topic appended (landed law)
    b  r1 idle press score 24     -> toast === 'The quartermaster waits on your
                                     standing. Deeds will speak.' exactly, 0
                                     warOrder, active false, postedDay still null,
                                     requisition topic NOT appended
    c  r1 idle press score 25     -> paper awarded, toast === RQ.offerText,
                                     prompt === 'E - War Board (0/9 iron ore)'
    d  r1 turn-in ore 9           -> 5 coins (WB2 regression)
    e  r2 turn-in ore 14          -> 9 coins (WB2 regression)
    f  fill at r2 (14 ore, score 60) -> on THAT resolve: topic 'war-effort-stone'
                                     appended once, stoneSeen true, toast[0] ===
                                     ST.crossingToast exactly AND toast[1] ===
                                     ST.doneText (crossing BEFORE the done toast,
                                     both print), coins 9 (r2-law pay 91000 — the
                                     pay used pre-rise repeatIndex), the NEXT award
                                     (r3, score 60) toasts ST.offerText
    g  r3 quota read              -> restore {active:true, postedDay:5,
                                     resolvedDay:null, repeatIndex:3, stoneSeen:true}
                                     (5-key, flag set — no crossing), feed 3 ore,
                                     prompt === 'E - War Board (3/20 iron ore)'
    h  r3 turn-in ore 20          -> 19 coins
    i  r3 turn-in ore 22          -> 21 coins
    j  r4 quota read              -> as row g with repeatIndex:4, feed 3 ore,
                                     prompt === 'E - War Board (3/24 iron ore)'
    k  r4 turn-in ore 24          -> 25 coins
    l  r5 quota read              -> as row g with repeatIndex:5, prompt ===
                                     'E - War Board (3/24 iron ore)' — SAME string
                                     as row j (the cap peg; raw growth 46)
    m  r4 turn-in ore 26          -> 27 coins
    n  fill 20 at r3 (own one-shot: restore {active:true, postedDay:5,
       resolvedDay:null, repeatIndex:3, stoneSeen:true}, score 60)
                                     -> resolve r3->r4: stone-topic count stays at
                                     its row-start count (NO append), stoneSeen
                                     stays true, toast === ST.doneText (exact fill
                                     at the stone tier; over-band over>=1 keeps
                                     overDoneText per V5), coins 19
    o  restore WB2 4-key {active:true, postedDay:5, resolvedDay:null,
       repeatIndex:5} (NO stoneSeen key, score 60)
                                     -> topic 'war-effort-stone' appended once,
                                     stoneSeen true, toast === ST.crossingToast,
                                     dressing rebuilt (V11 census, 3 children),
                                     prompt === 'E - War Board (0/24 iron ore)'
    p  restore WB1 3-key {active:false, postedDay:2, resolvedDay:2} (no
       repeatIndex, no stoneSeen)
                                     -> repeatIndex 0, stoneSeen false, NO topic,
                                     NO toast, capture() = {active:false,
                                     postedDay:2, resolvedDay:2, repeatIndex:0,
                                     stoneSeen:false} exactly (5-key)
    q  fresh r0: restore {active:false, postedDay:null, resolvedDay:null,
       repeatIndex:0, stoneSeen:false}, fake day d, score 60. Fill days
       d+1 (6 ore, resolve 1), d+2 (9 ore, resolve 2), d+3 (14 ore,
       resolve 3) — each day increment (day += 1) precedes press(award)+fill;
       crossing fires EXACTLY on the third resolve: topic appended once,
       toast === ST.crossingToast exactly there, NO topic after resolves 1-2

V5. Award/done text law at the stone tier (S-2.5): r3 idle press (score 60)
    toasts ST.offerText EXACTLY; r3 quota-exact fill toasts ST.doneText (and
    the crossing fill of row f does the same — the toast reads the POST-resolve
    tier); over-band fill (r3, 22 ore) keeps the landed overDoneText preference
    (over >= 1 wins at ANY tier, as landed); the journal appends are UNCHANGED —
    the r3 award STILL appends the requisition topic 'war-effort-requisition'
    and every fill STILL appends 'war-effort-first-fill' (QJR-3 rows stay for
    the base board; assert both in the WH_JOURNAL stub). Idle prompt at the
    stone tier is UNCHANGED: 'E - War Board (Take a requisition)'.

V6. Gate is re-post-only (S-2.2): turn-in branch fires with score 1 at r1
    (feed 9 ore with score 1 -> fill succeeds, coins 5). No paper at score 24 =
    only the idle branch. r0 press at score 0 AND r0 press at score 24 both
    award (gate never binds r0). Blocked press (row b) leaves postedDay null:
    same-day re-press at score 60 awards (the block consumed no day). Rows
    d/e at score 60 prove the gate never touches turn-in; S-6.3 shape.

V7. Once-law across paths: V4 f/n/o/q each run as its own fresh one-shot (own
    module state, own journal stub); the 'war-effort-stone' append count per
    path is f=1, n=0, o=1, q=1, and WITHIN each path a second triggering
    resolve/restore appends nothing more (stoneSeen guards each profile).
    Rationale: row o's WB2-payload restore carries NO stoneSeen key, so the
    restore law (stoneSeen = data.stoneSeen === true ONLY) re-arms the flag and
    the crossing legitimately fires once per profile — "count === 1 at the end
    of one continuous profile" is unreachable across o+q at once; the IO
    spec's once-law is PER PROFILE, not per installation. Deed log check: no
    'warEffortFill' is ever appended by the crossing path (S-5).

V8. Restore law: foreign payload no-op — restore({}) AND
    restore({stoneSeen:'x'}) (the NEW gate shape: typeof stoneSeen !==
    'boolean' in the all-unknown rejection — S-3) both leave state unchanged;
    one recognized key still admits: restore({active:true, postedDay:1,
    resolvedDay:1, stoneSeen:'x'}) loads with stoneSeen false (a wrong-typed
    stoneSeen beside recognized keys does NOT poison the load). The MEANINGFUL
    flag case: restore({active:true, postedDay:1, resolvedDay:1,
    repeatIndex:5, stoneSeen:true}) restores with NO topic and NO toast (the
    flag silences it, at r5, past threshold). rollNewDay law untouched (S-3):
    after any crossing, day += 1 then tryOpen rolls the new day (active false,
    postedDay null, resolvedDay null) while repeatIndex and stoneSeen survive
    — capture() still carries stoneSeen true. capture() key set EXACTLY
    {active, postedDay, resolvedDay, repeatIndex, stoneSeen} (Object.keys
    equality; the landed 4 keys + stoneSeen only); capture() at fresh r0
    after restore({}) = all-default + stoneSeen false.

V9. Public surface: Object.keys(WH_WarEffort) set equality EXACTLY
    {init, tryOpen, interactPrompt, capture, restore, boardPos} — 6 keys, every
    value typeof 'function', no extra/missing key, no changed signature vs
    landed WB1 (WB2 V-8 shape). CONFIG parses clean via the one-shot
    `global.window = global; require('<worktree>/prototype/js/CONFIG.js')`
    — module top throws nothing, no THREE required.

## Dressing (code-level, stubbed THREE or headless law check)

V10. Headless (window.THREE undefined): init(g) does NOT build (scene.add
     called 0 times — no 'cc-wb1-war-effort-board', no 'cc-wb2-repeat-tally', no
     'cc-wb4-stone-dressing' anywhere); capture() returns the 5-key default
     payload; restore at repeatIndex 5 (active:true, postedDay:1, resolvedDay:1)
     does NOT throw (the rebuild guards on window.THREE, landed
     rebuildTallyPins shape) and leaves sane values (no topic, no toast — headless
     crossing still sets stoneSeen true: state law, visuals only skipped).

V11. THREE stub present (construction args retained in the shim for census,
     WB2 harness law): the group 'cc-wb4-stone-dressing' is created in
     buildBody as a SUB-group inside the EXISTING 'cc-wb1-war-effort-board'
     root (NOT a sibling), created BEFORE the headless guard decision; one
     board root only. rebuildStoneDressing mirrors landed rebuildTallyPins
     (clear-then-fill, guard on the group + window.THREE) and is called from
     buildBody AFTER rebuildTallyPins, from the fill path resolve block and
     from restore(). At r<3 (and ST null): 0 children — group exists, EMPTY.
     At r>=3: exactly 3 children — box plinth (0.7,0.5,0.45) pos
     (-0.55,0.25,-0.35) color 0x8a8577 roughness 1.0; box pole (0.04,0.8,0.04)
     pos (-0.8,2.6,0.1) oak color 0x4a3a2a; plane pennant (0.4,0.28) pos
     (-0.58,2.78,0.1) parch color 0xd2b48c, side DoubleSide (the landed parch
     material — NO second emissive, NO red: material census by color identity,
     not pixels). Fill at r2->r3 with the stub leaves 3 children immediately
     (call-site proof). Tri budget <= 120 (actual math: 12+12+2 = 26; spec
     S-6.9 headroom).

## Build (post-verdict gate steps; Testerbot runs the deterministic rebuild)

V12. `python3 tools/build_v8.py` from the repo root, exit 0; 'CC-WB4' marker
     count in prototype/builds/v8-playable.html via `grep -o 'CC-WB4' | wc -l`
     >= 6; re-run -> byte-identical artifact (two consecutive runs — the
     DETERMINISTIC-BUILD law derives the title stamp from HEAD's commit date
     + HEAD sha, both pinned during this round, so determinism holds). The
     built artifact is then the ONE extra modification V1 admits.

V13. Verdict file at io/reports/cc-wb4-standing-stone-validation.md: FIRST line
     the one-line `VERDICT: PASS` or `VERDICT: FAIL` banner, then per-gate
     PASS/FAIL with the actual node one-shot output lines and the V0 pre/post
     sha table; on any FAIL, observed vs expected per failed check; NO partial
     PASS (any FAILing gate = FAIL verdict). NO repo commits/stages/pushes by
     the tester.

## Amendments (Testerbot may amend this spec pre-build: record each as AMEND-n
with the reason in the verdict file; substantive spec changes go back to IO).
