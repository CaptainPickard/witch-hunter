# CC-WB4 — Standing Gate + Requisition Stone (doc 42 Part 2 standing layer on the WB1 board)

Spec author: IO (Autopilot wake 48, 2026-11-09). Repo worktree: /tmp/wh-worldfeat,
branch feat/world-visuals (HEAD f98b83c at spec time). Build: python3 tools/build_v8.py
(repo root). No harness runs, no headless browser smoke tests — node one-shots
only; Nicko's playtest is the acceptance bar.

## Scope

Lands doc 42 Part 2's standing layer on the landed CC-WB2 board machinery
(js/wareffort.js @ f98b83c):

1. STANDING GATE ON REPEATS: the board re-posts a contract only while the
   hunter's standing (CC-AF1 axis, WH_AFF.score()) meets the repeat bar
   (CONFIG PROPOSED 25). The FIRST contract of a ladder (repeatIndex 0) needs
   no standing — the entry ask stays open to everyone (doc 42: never a T5 ask
   of a T2 hold). Below bar at idle press = press consumed, waiting toast, no
   paper awarded. Standing recovers the way it always does (rescue +25,
   kill_coven +8, kills, strataFill +10) — no deadlock, the axis stays the
   single source.
2. REQUISITION STONE TIER-UP (doc 42 Part 2 standing effects): three RESOLVED
   contracts (repeatIndex >= 3) raise the hold's requisition stone — the board
   gains its stone-below banner dressing AND posts bigger contracts for every
   repeat after the raise: quota cap 18 -> 24 (stone capMult 4 on the base 6)
   and base pay x1.3 (payPct 130, exact floor). The quota ladder keeps its own
   1.5-growth, so the raise is monotone (r3 -> 20, r4+ pegged 24), never a
   drop. One-time journal line (whence: the quartermaster) + crossing toast.
3. PAYLOAD: capture()/restore() gain ONE key `stoneSeen` (bool). Full additive
   law in S-4.

The one-contract-per-day cadence, rollNewDay, haul grammar, proximity gate,
prompt chain and the game.js save-wrap call sites are LANDED machinery —
this round touches ZERO lines in game.js and index.html. style.css untouched.

Ledger note: garrison/quartermaster texture only (doc 42 texture; doc 44's
creditor-face law does not bind board text). No line names the creditor, the
pact, or its terms.

## Art anchor (law 1)

This wake's vision-QA pass: day-06-council.png (white banners with the golden
sunburst over a war table in ruined stone — earned rank reads as banner +
stone, daylight formal gravity) + char-03-bannerman-good.png (the great
cream/gold stag banner raised over the hold at night — recognition heraldry)
+ concept-06-siege-council.png (bureaucratic weight, warm amber vs cold blue).
Palette law: the board keeps WB1 parchment/oak + the ONE amber lantern accent
(unchanged); the NEW dressing adds STONE GRAY 0x8a8577 (the existing neutral
palette token from CONFIG.affinity.text.barNeutral) for the plinth, and the
pennant REUSES the board's parchment material (the sunburst anchor reads as a
plain parchment pane, no second emissive, NO red — red stays the pact/danger
law).

## S-1. CONFIG.js — CONFIG.warEffort additions (inside the warEffort block)

    repeatStanding: 25,        // CC-WB4: repeats beyond the first need this standing to re-post (PROPOSED, Nicko tunes)
    stone: {                   // CC-WB4: doc 42 Part 2 three-resolve requisition stone (all PROPOSED, Nicko tunes)
      thresholdRepeats: 3,     // lifetime resolutions that raise the stone
      quotaCapMult: 4,         // stone cap = 4x base = 24 ore (pre-stone cap = ladder.repeatQuotaCapMult = 3 -> 18)
      payPct: 130,             // stone base pay multiplier, x1.3, exact milli-unit floor
      offerText: 'The requisition stone stands at the board. The hold wants more iron for the front.',
      doneText: "The stone accepts the haul. The quartermaster pays by the stone's word.",
      crossingToast: 'The hold raises the requisition stone.'
    }

New journal topic appended to CONFIG.journal.topics (requisition voice, APPEND
ONLY, single-line strings, ledger-safe):

    warEffortStone: {
      id: 'war-effort-stone',
      title: 'The requisition stone',
      source: 'The quartermaster',
      body: 'Three hauls to the war board and the hold raised its requisition stone. The quartermaster counts larger contracts on it now - the front grows, and the hold grows with it.'
    }

Existing warEffort keys (boardSeat, rotYFacesRoadNorth, requisition, ladder)
stay byte-identical.

## S-2. js/wareffort.js — law additions (additive; WB2 economics unchanged at r<3)

Config reads at module top: `var ST = W.stone || null;` and
`var RS = (typeof W.repeatStanding === 'number') ? W.repeatStanding : null;`
(null = the feature is OFF and the landed WB2 behavior holds verbatim — the
CONFIG.js shipped in this round always carries both, this is the older-profile
safety law).

1. STONE ECONOMICS (only active when ST && logic.repeatIndex >= ST.thresholdRepeats):
   - quotaQ(r): cap becomes ST.quotaCapMult * base instead of LAD.repeatQuotaCapMult * base —
     the growth formula, base and round() are UNTOUCHED. Ladder (base 6, growth 1.5,
     round-half-up): r0 6, r1 9, r2 14, r3 20, r4 30->24, r5+ 24. Pre-stone (cap 18):
     r0 6, r1 9, r2 14, r3 18, r4 18.
   - baseM4(r): pre-stone exactly the landed 5000 + 750*r; stone-active
     floor((5000 + 750*r) * ST.payPct / 100). Stone rows: baseM4(3) = 9425,
     baseM4(4) = 9425 + floor(750*130/100) = 9425 + 975 = 10400.
   - bonusM4/coinsFrom/payM4/ratePct unchanged (bonus from the stone base keeps
     the landed floor shape).
2. STANDING GATE (only active when RS !== null): at the tryOpen idle branch
   (logic.active === false), when logic.repeatIndex >= 1: score =
   window.WH_AFF && typeof window.WH_AFF.score === 'function' ?
   window.WH_AFF.score() : 0. If score < RS: toast
   'The quartermaster waits on your standing. Deeds will speak.' and return
   true (press consumed, NO paper, postedDay stays null, active stays false).
   The r0 idle branch is UNTOUCHED. The active branch (turn-in) is UNTOUCHED —
   the gate exists only to re-post.
3. STONE CROSSING (once per lifetime, persisted): resolve() keeps its
   single increment. In the fill path AFTER resolve(), and in restore(), run
   stoneCrossing(): when logic.repeatIndex >= ST.thresholdRepeats && !logic.stoneSeen
   (and ST !== null): set logic.stoneSeen = true, append the warEffortStone
   journal topic via the JT/row shape of the landed firstFill append, and toast
   ST.crossingToast. Order in the fill path: crossing runs BEFORE the over-band
   doneText toast (both lines print; crossing first).
4. STONE DRESSING (S-3 art law, zero new assets): buildBody creates an EMPTY
   group named 'cc-wb4-stone-dressing' inside the board root (the exact lane
   shape of the landed cc-wb2-repeat-tally group, created BEFORE the headless
   guard decision). rebuildStoneDressing() mirrors rebuildTallyPins(): clears
   the group; when logic.repeatIndex >= ST.thresholdRepeats (ST null or r below
   threshold = empty group, byte-silent) it adds three meshes:
   - plinth: BoxGeometry(0.7, 0.5, 0.45), StoneGray 0x8a8577 roughness 1.0,
     position (-0.55, 0.25, -0.35) board-local;
   - pole: BoxGeometry(0.04, 0.8, 0.04) OakMaterial (the landed oak material),
     position (-0.8, 2.6, 0.1) — rises from the left post cap (post top y 2.2);
   - pennant: PlaneGeometry(0.4, 0.28), the landed parch material (DoubleSide),
     position (-0.58, 2.78, 0.1).
   Called from buildBody (after rebuildTallyPins), from the fill path resolve
   block and from restore(). Headless one-shot safety: guard on the group +
   window.THREE, the exact shape of rebuildTallyPins.
5. OFFER/DONE TEXT: when ST && logic.repeatIndex >= ST.thresholdRepeats at award
   time, the award toast uses ST.offerText instead of RQ.offerText (the journal
   requisition topic append is UNCHANGED — QJR-3 rows stay for the base board);
   at fill time, the done toast uses ST.doneText when the stone is up and
   over-band uses the over-band law as landed (over >= 1 keeps the overDoneText
   preference: over-band text wins at any tier, as landed).

## S-3. js/wareffort.js — persistence (additive: one key)

capture(): the landed 4-key payload gains stoneSeen: logic.stoneSeen === true.
restore(): the landed foreign-payload gate extends with
`typeof data.stoneSeen !== 'boolean'` in the all-unknown rejection condition
(any one recognized key still admits). Restore law: stoneSeen = data.stoneSeen
=== true ONLY, then repeatIndex restore as landed, then stoneCrossing() (the
restore-time refire for WB2 saves already past r3 — appends the topic once,
sets the flag), then rebuildTallyPins() + rebuildStoneDressing() +
setPapersVisible(!spentToday()) in the landed order.

WB1 3-key (repeatIndex absent -> 0, stoneSeen absent -> false) and WB2 4-key
loads stay clean. stoneSeen can never regress (no reset path; rollNewDay law
untouched).

## S-4. Pinned behavior table (valspec MUST bind every row as node one-shots)

Pre-stone rows = WB2 byte-regression (must hold with CONFIG present):

  a. r0 idle press with score 0  -> paper awarded (1 warOrder), quota 6
  b. r1 idle press, score 24     -> waiting toast, NO paper, active stays false
  c. r1 idle press, score 25     -> paper awarded, quota 9 (base quotaQ(1))
  d. r1 turn-in ore 9            -> 5 coins (WB2 row i, byte-regression)
  e. r2 turn-in ore 14           -> 9 coins (WB2 row k, byte-regression)
  f. r2->r3 resolve (ore 20 at r2? NO — r2 quota is 14; resolve r2->r3 via a
     fill of ore 14 at r2)      -> stoneCrossing fires THAT resolve
  g. r3 quota read               -> 20 (stone cap active)
  h. r3 turn-in ore 20           -> baseM4(3)=9425, pay 188500 m4 -> 19 coins
  i. r3 turn-in ore 22           -> pay 188500 + 10367 + 11310 = 210177 -> 21 coins
  j. r4 quota read               -> 24 (cap)
  k. r4 turn-in ore 24           -> baseM4(4)=10400, pay 249600 -> 25 coins
  l. r5 quota read               -> 24 (pegged)
  m. r4 turn-in ore 26           -> x=2 over-band ON TOP of the stone table:
     pay = 10400*24 + floor(10400*110/100)=11440 + floor(10400*120/100)=12480
     = 249600 + 11440 + 12480 = 273520 -> 27 coins
  n. crossing once-law: resolve r3->r4 (fill at r3) -> second journal topic NOT
     appended (stoneSeen held), toast is the normal over/done path
  o. restore: WB2 4-key profile {repeatIndex 5} -> stoneCrossing refires (topic
     appended, stoneSeen true), dressing built, quota 24
  p. restore: WB1 3-key profile  -> repeatIndex 0, stoneSeen false, no topic
  q. stoneSeen=false restore at r0, then THREE fills spanning days
     (d+1, d+2, d+3) -> crossing fires exactly on the third resolve

Row g..m use ST.payPct 130, ST.quotaCapMult 4 with the CONFIG block of S-1.
The node harness mirrors the landed fake-game + inventory shape from the WB2
valspec (io/specs/cc-wb2-ladder-valspec.md) — same instrument, grown.

## S-5. Out of scope (explicit)

No game.js/index.html/style.css edits (census-enforced). No WB1 board mesh or
seat changes; no WB2 ladder math change at r<3; no strataeffort.js change; no
smelting, no rich-mine tier 2, no vendor, no war-state/siege multiplier (doc 13
not built), no second board, no contract variety, no paper consumption change,
no icon PNGs, no region props/enemies/nodes changes anywhere, no new scene
roots beyond the three meshes inside the EXISTING board root, no new journal
UI, no standing UI change (the CHARACTER column already reads the axis), no
deed map change (warEffortFill/strataFill stay +10; the stone does not pay
standing — doc 42's standing-per-contract line is already covered by the
landed fill deed).

## S-6. Acceptance criteria (bind into valspec)

  1. node census: CONFIG.warEffort carries repeatStanding + stone exactly per
     S-1; boardSeat/requisition/ladder byte-identical to landed WB2;
     CONFIG.journal.topics.warEffortStone present; git diff shows ONLY the
     warEffort block + topics append + wareffort.js changes.
  2. Pinned table S-4 rows a..q ALL exact via node one-shot (fake game +
     inventory + WH_AFF stub harness).
  3. WB2 turn-in regression: rows d, e match the landed WB2 pinned values at a
     pre-stone standing of 60 (gate non-binding at those rows) AND at standing
     24 the r1 award blocks (row b) without changing any turn-in row.
  4. Once-law: crossing appends exactly once across resolve-path AND
     restore-refire paths (rows f, n, o, q).
  5. Dressing: with three.js absent (headless), buildBody skips
     cc-wb4-stone-dressing children; with a THREE stub, r3 rebuild = 3 children
     with the exact S-2 geometry/material/position laws; pre-stone rebuild = 0
     children.
  6. Census of files: ONLY prototype/js/CONFIG.js + prototype/js/wareffort.js
     modified (git status law); game.js + index.html + style.css byte-untouched
     (sha-preflight in valspec).
  7. Build: python3 tools/build_v8.py exit 0; CC-WB4 marker count in built html
     >= 6 (grep -o 'CC-WB4' | wc -l); artifact committed with the round.
  8. Runtime smoke: CONFIG loads clean; WH_WarEffort public surface unchanged
     (init/tryOpen/interactPrompt/capture/restore/boardPos); capture() at r0
     = landed WB2 keys + stoneSeen:false.
  9. Tri budget: the dressing adds <= 120 triangles (4 boxes + 2 planes
     headroom) — probe asserts 0 (headless) with the stub asserting 3 mesh
     children max at the threshold.
 10. Ledger: no board/journal string names the creditor, the pact, or its
     terms.
 11. NO harness runs, NO headless browser smokes (node one-shots only).
