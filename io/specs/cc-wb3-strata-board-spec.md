# CC-WB3 — Strata Requisition Board (IO spec, 2026-11-11)

Delve-chain closes its loop: the strata boards that already buy iron (CC-WB1)
now also buy the delve harvest. ONE new singleton module; NO engine file may be
touched. All numbers PROPOSED, Nicko tunes.

## Seat + scene

- Region G (lords_hold), war-table hub. Board root: x 6.0, z -782.0, rotY 4.712.
  Faces west toward the gate lane; 5.67 m clear of both dais braziers, 6.3 m
  east of the stoneSteps dais, 40.4 m radial (rim 124.5), 78 m off both door
  planes (z -700 / -948). Verified vs CONFIG regionG props this wake.
- Board body = the CC-WB1 board grammar re-dressed per concept-06-siege-council:
  two oak posts + dark board face + 2 parchment sheets + iron bracket strip +
  THE ONE amber lantern (emissive 0xffb347, the only emissive; NO crimson).
  Name strings prefix cc-wb3-. No other scene object.

## CONFIG.js (one new block next to CONFIG.warEffort ~4410 area)

    strataEffort: {
      boardSeat: { regionId: 'lords_hold', x: 6.0, z: -782.0, rotY: 4.712 },
      itemId: 'strataOrder',
      mats: [
        { id: 'rot-silk',  quota: 4 },
        { id: 'rot-gland', quota: 2 }
      ],
      reward: { id: 'stolenCoin', count: 5 },
      title: 'Strata Requisition',
      offerText: 'The quartermaster wants rot-silk and rot-gland from the delve strata below.',
      doneText: 'Strata requisition filled. The quartermaster marks the board.'
    },

Also:
- CONFIG.items gains 'strataOrder' (mirror the warOrder row exactly; name
  'Strata Requisition', glyph 'SR', category quest-paper precedent).
- CONFIG.journal.topics gains ONE row `strata` (id/title/body ~ the WB1
  requisition+fill voice; one topic, appended on award AND on fill).

## Module: js/strataeffort.js (NEW; generalizes js/wareffort.js; do NOT edit wareffort.js)

- IIFE singleton `window.WH_StrataEffort` with the WB1 API surface exactly:
  init(g) / tryOpen() / interactPrompt() / capture() / restore(data) / boardPos().
- State: { postedDay: null, active: false, resolvedDay: null } (NO repeatIndex
  ladder this round — WB2 ladder stays WB1-only).
- near(): VERBATIM WB1 grammar — region-gate via game.regionManager.logic.activeId
  === boardSeat.regionId, radius 2.6, player alive + not inputSuspended.
- One-day contract law VERBATIM WB1: interaction-time rollNewDay() only; a
  resolved board re-arms at the next dawn; spentToday() returns the press
  consumed, board does nothing.
- Idle press: award 1 strataOrder (or 'Your satchel is full.'), set active +
  postedDay, toast offerText, journal append (topic `strata`).
- Active press: check EVERY mat at quota (have >= 4 rot-silk AND >= 2 rot-gland;
  shortfall toast 'Not enough rot-silk/rot-gland for the strata order. (s/g)',
  exact counts); remove EXACTLY quota of each (surplus stays in the bag — no
  haul law, no over-band this round); add reward.count stolenCoin; resolve;
  papers hidden; journal fill append; toast doneText.
- interactPrompt(): idle = 'E - Strata Board (Take a requisition)'; active =
  'E - Strata Board (needs 4 rot-silk + 2 rot-gland)' built from CONFIG counts;
  spent = 'The board is spent until dawn.'; not near = ''.
- capture(): { active, postedDay, resolvedDay } (3-key payload). restore():
  missing/foreign payload = no-op (fresh idle board); booleans/numbers clamped
  per WB1's V-5n shape; papers visibility reset on restore.
- Headless-safe: buildBody only when game.scene + window.THREE exist (node
  one-shots skip visuals).

## Wiring (js/game.js + index.html — ONLY these two files besides the above)

- index.html: <script src="js/strataeffort.js"> AFTER wareffort.js.
- game.js init tier (after WH_WarEffort.init): WH_StrataEffort init hook.
- game.js E chain: tryStrata() branch ADDED AFTER tryWareffort() (both boards
  12 m apart; region gate makes them mutually exclusive).
- game.js prompt chain: WH_StrataEffort.interactPrompt() branch after the
  WH_WarEffort branch (same shape).
- game.js save-wrap: data.strataEffort capture / explicit-storage write /
  restore hand-off, three lines mirroring the warEffort lines exactly.

## Economy + affinity

- CONFIG.affinity.deeds gains `strataFill` (same delta value as warEffortFill;
  module calls window.WH_AFF.deed('strataFill') on fill, WB1 verbatim shape).

## Deliberate scope cuts (record, do not build)

- No WB2 ladder/over-band math on this board (fixed CONFIG pay per fill).
- No new item art beyond the glyph rows; no icon PNG.
- No board variant on the delve side (collection stays the hand-haul).

## Acceptance criteria (Testerbot validates ALL; node one-shot law, NO browser)

A1  Node load smoke: CONFIG parses; strataEffort block present with exactly the
    9 keys above; items.strataOrder row present; journal topic strata present;
    affinity.deeds.strataFill present.
A2  Fake-game one-shot: idle press adds 1 strataOrder + sets active/postedDay;
    press with (4 silk + 2 gland) removes EXACTLY 4/2 (bag surplus 5 silk
    untouched), adds EXACTLY 5 stolenCoin, sets resolvedDay = posted day,
    active false, repeatIndex-free payload.
A3  Shortfall press (2 silk + 2 gland): nothing removed, nothing granted.
A4  spentToday after fill: further press consumed with no changes; fake day+1
    rollNewDay re-arms (active false => award path again).
A5  Prompt strings match the spec (idle/active/spent/'' far).
A6  Capture/restore roundtrip: capture 3 keys; restore foreign payload + missing
    payload = no-op; restore of a real payload restores state + paper visibility.
A7  Seat clearance probe: board root distance to every CONFIG regionG props row
    >= 4.0 m; radial <= 124.5; NOT inside the z -700 or -948 door window bands
    (|x| <= 4.5 / 4.0); board 5.67 m from both dais braziers.
A8  Diff law: git diff --stat vs HEAD shows ONLY CONFIG.js, index.html, js/game.js
    modified + js/strataeffort.js ADDED. Any engine file = FAIL.
A9  Art law: exactly one emissive material (0xffb347) in the module; no crimson,
    no red channel values; no second light.
A10 Build: python3 tools/build_v8.py runs clean in the worktree; marker CC-WB3
    present in prototype/builds/v8-playable.html.

## Build environment (for the builder)

- Worktree /tmp/wh-worldfeat, branch feat/world-visuals. NEVER push, NO git
  clone/push/remote. Commit is IO's job after validation.
- No harness runs, no headless browser smoke tests (node one-shot logic checks
  like /tmp/wb1_smoke2.js ARE the accepted smoke form).
- Config file: /tmp/wh-worldfeat/prototype/js/CONFIG.js (grep 'warEffort: {'
  ~line 4410 for the insert; regionG row at ~line 1688).
- Build: python3 tools/build_v8.py IN THE WORKTREE; verify marker
  grep -c 'CC-WB3' prototype/builds/v8-playable.html >= 3.
