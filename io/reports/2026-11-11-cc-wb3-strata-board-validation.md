# CC-WB3 STRATA BOARD — INDEPENDENT VALIDATION VERDICT (Testerbot, 2026-11-07)

2026-11-11-cc-wb3-strata-board-validation.md — verdict runs 2026-11-07
(worktree clock; the requested report filename date is the IO-scheduled
run label). Independent Testerbot validation of the Devbot CC-WB3 build.
NO playability claims anywhere in this report (Nicko's bar).

## V-0 pre/post integrity

| File | sha256 (head 16) | pre | post |
|---|---|---|---|
| prototype/js/CONFIG.js | 66ccce98a08f8b86… | ✓ | ✓ identical |
| prototype/js/game.js | 67ac04503eb19963… | ✓ | ✓ identical |
| prototype/index.html | f7406d260693435b… | ✓ | ✓ identical |
| prototype/js/wareffort.js | 55a4e0c6836c8f10… | ✓ | ✓ identical |
| prototype/builds/v8-playable.html | b35762316e029901… | ✓ | ✓ identical |
| prototype/js/strataeffort.js (new) | 55ab36de09bfce19… | — | untracked, unchanged |

HEAD pinned: cf9d61eb3d09a17824799d513b5436ffc3d2b2db, branch feat/world-visuals.
Pre shas recorded before the A10 build; post shas re-run at verdict close —
byte-identical across the whole set.

## Probes (all run by Testerbot, /tmp/ccwb3/, stdout archived /tmp/ccwb3/out/)

harness.js + a1_config.js a2_flow.js a3_shortfall.js a4_spent.js a5_prompts.js
a6_persist.js a7_seat.js a8_gitprobe.js a9_art.js a10_build.js spot_cde.js
a7b_wb1seat.js. Modeled on scratch/cc-wb2/wb2_harness.js contract (shape
re-use; no verdict reuse, no scratch/cc-wb3 reads). A7 clearances recomputed
from CONFIG.js regionG props (regex extraction of the regionG span, ~111 rows,
no hardcoded coordinates). A8 run per the valspec diff probe AFTER the A10
build. Spot-checks (a)-(e): a8_gitprobe.js (a) + a7b_wb1seat.js (b) +
spot_cde.js (c)(d)(e).

## Per-criterion verdict

| # | Probe | Verdict | Evidence line |
|---|---|---|---|
| A1 | a1_config.js | PASS | CONFIG parses; strataEffort key set EXACTLY 7 keys {boardSeat,itemId,mats,reward,title,offerText,doneText}; boardSeat {lords_hold,6.0,-782.0,rotY 4.712}; mats [rot-silk 4, rot-gland 2]; reward stolenCoin×5; items.strataOrder {name 'Strata Requisition', glyph 'SR', category 'document'} mirrors warOrder row shape; journal.topics.strata one row (id/title/body + source); affinity.deeds.strataFill present |
| A2 | a2_flow.js | PASS | idle press +1 strataOrder, active=true, postedDay=day, offerText toast, journal append, no deed; fill with 9 silk + 2 gland removes EXACTLY 4/2 (surplus 5 silk untouched), +5 stolenCoin, resolvedDay===postedDay, active=false, docs hidden; capture() keys EXACTLY {active,postedDay,resolvedDay} before and after; doneText toast; journal fill append; deed('strataFill') |
| A3 | a3_shortfall.js | PASS | 2 silk + 2 gland press: bag UNCHANGED (nothing removed/granted), state UNCHANGED (active, no resolvedDay), journal+deed untouched; toast exactly 'Not enough rot-silk/rot-gland for the strata order. (2/2)' — (s/g) slots carry HAVE counts interpolated at press |
| A4 | a4_spent.js | PASS | after fill day 20 (resolvedDay 20): press consumed (true) with ZERO inventory/state/toast/journal/deed changes; day 21 press re-arms (active=true, postedDay 21, resolvedDay null, offer toast) and re-fills; repeat re-arm verified one more day-cycle |
| A5 | a5_prompts.js | PASS | idle 'E - Strata Board (Take a requisition)'; active recomputed FROM CFG counts AND pinned 'E - Strata Board (needs 4 rot-silk + 2 rot-gland)'; spent 'The board is spent until dawn.'; far/other-region/dead/suspended/12 m/2.6 m-boundary '' per gate law; next-dawn prompt back to idle |
| A6 | a6_persist.js | PASS | capture 3 keys repeatIndex-free; restore(string/number/null/array/undefined/WB2-shape/empty-object) no-op, no throw; real payload restores state AND paper visibility (same-day spent → hidden; past-resolved on later day → visible); V-5n clamp shape per WB1 oracle (numerics kept verbatim, non-number → null, active === true coercion) |
| A7 | a7_seat.js | PASS | regionG span parsed 111 rows; min dist EVERY row ≥ 4.0 m; brazier pair (5.66,-776.34)/(5.66,-787.66) = 5.670 m (tol ±0.05); stoneSteps 6.32 m; radial 40.45 ≤ 124.5; door bands |x| 6.0 > 4.5/-plane 82.0 m and |x| 6.0 > 4.0/-plane 166.0 m; rotY 4.712 on the CONFIG row |
| A8 | a8_gitprobe.js | PASS | status --porcelain -- prototype = 4 M + 1 ?? EXACT set (v8-playable.html, index.html, CONFIG.js, game.js + strataeffort.js); diff --stat rows = exactly those 4; wareffort.js + chest/gather/inventory/daynight/camp/save/region-manager/affinity/journal diffs EMPTY; HEAD === pinned |
| A9 | a9_art.js | PASS | material census: EXACTLY ONE emissive material, 0xffb347, intensity 0.9 > 0; zero red-dominant (crimson) colors or hex literals (classifier r≥0x80, r>2g, r>2b — amber 0xffb347 exempt, no crimson comment is a law comment not a color); zero Light constructors; cc-wb3- names on ALL nodes; 2 posts + face + 2 parchment + iron strip + lantern present |
| A10 | a10_build.js | PASS | python3 tools/build_v8.py exit 0 in-tree (run twice; no stray files); grep -c 'CC-WB3' v8-playable.html = 18 ≥ 3; build embeds strataeffort.js source + strataEffort CONFIG block |
| OVERALL | — | PASS | A1..A10 ALL PASS |

## Spot-checks beyond the table

(a) wareffort.js diff vs git HEAD EMPTY ✓ (probe a8_gitprobe.js PASS).
(b) WB1 board seat spot-check (a7b_wb1seat.js): CONFIG.warEffort.boardSeat =
{ hold_outskirts, x 5.9, z -15.5, rotY 3.14 } UNTOUCHED and byte-identical vs
git HEAD (git diff --stat HEAD -- prototype/js/CONFIG.js shows no -/+ on the
block); WB1 block keys {lsKey, boardSeat, rotYFacesRoadNorth, requisition,
ladder} intact. ✓
(c) E-chain order (spot_cde.js): 'tryWareffort() || tryStrata() || tryGather()'
— tryStrata ADDED AFTER tryWareffort within one expression; game.js defines
tryStrata(); init hook AFTER WH_WarEffort.init; prompt branch AFTER the war
branch. ✓
(d) Save-wrap (spot_cde.js + git diff): warEffort lines intact (no removed
lines in the diff; capture/explicit-storage/restore lines present in current
game.js) + strataEffort lines added EXACTLY once each (capture /
explicit-write / restore hand-off, all 3). ✓
(e) Journal (spot_cde.js): journal topics table parses (CONFIG require()
clean); strata row object with id/title/body strings; exactly one strata key
in topics; module append routes the CONFIG strata topic id on award AND fill. ✓

## Deviations & probe-side corrections (numbered)

1. Probe-side (not a build defect): shortfall toast slot order. The spec's
   "(s/g)" reads as silk-slots/gland-slots; the build interpolates HAVE counts
   "(2/2)" — the valspec A3 row resolves the reading ('the (s/g) slot carries
   the HAVE counts interpolated at press'). PASS under the valspec law.
2. Probe-side (not a build defect): restore() V-5n clamp — my first probe
   expected a finite-int clamp on day values; cross-checking the WB1 oracle
   (wareffort.js restore()) showed WB1 keeps numeric days verbatim and clamps
   only repeatIndex (absent in WB3). Probe corrected to the WB1 shape; PASS.
3. Probe-side (not a build defect): my first A8 run ran `git status
   --porcelain` unscoped and flagged io/specs + scratch/cc-wb3 untracked
   files. The valspec diff probe is scoped `-- prototype`; untracked io/
   scratch/ spec/probe files are worktree-adjacent by design and OUTSIDE the
   A8 set. Re-run scoped: exact expected set. The verdict report file is
   left untracked (NO-GIT); no commit/push/stage/config performed anywhere.
4. Probe-side: first A9 crimson classifier (r > 1.4×) misclassified the
   pinned amber 0xffb347; tightened to genuine crimson family (r ≥ 0x80,
   r > 2g, r > 2b) — the build carries ZERO crimson colors; 0xffb347 is the
   sole emissive. The word 'crimson' appears only inside a negated law
   comment, not as a color value. PASS.
5. A10 build artifact: grep -c 'CC-WB3' = 18 line hits (≥ 3 law). No
   worktree file outside the A8 expected set was dirtied by the build.

## Blockers

None. BLOCKER-carrying like WB1: none found this round.

## OVERALL

    VERDICT: PASS
    A1  PASS — CONFIG parses; 7-key strataEffort block; strataOrder row; strata topic; strataFill deed (a1_config.js)
    A2  PASS — idle award + exact 4/2 removal + 5 coins + resolvedDay===postedDay + 3-key payload (a2_flow.js)
    A3  PASS — shortfall press: zero removal/grant, toast 'Not enough rot-silk/rot-gland for the strata order. (2/2)' (a3_shortfall.js)
    A4  PASS — spent press consumed no-ops; day+1 re-arms award path; repeat re-arm verified (a4_spent.js)
    A5  PASS — idle/active/spent prompts exact (active recomputed from CFG counts); far = '' (a5_prompts.js)
    A6  PASS — capture 3 keys; foreign/missing no-op; real payload restores state + paper visibility; V-5n WB1 shape (a6_persist.js)
    A7  PASS — 111 regionG rows ≥ 4.0 m; braziers 5.67 m; stoneSteps 6.32 m; radial 40.45; door bands clear at 82/166 m (a7_seat.js)
    A8  PASS — status/diff-stat = exactly 4 M + strataeffort.js ??; engine files byte-identical; wareffort.js diff EMPTY (a8_gitprobe.js)
    A9  PASS — ONE emissive 0xffb347; zero crimson family; zero Light ctors; cc-wb3-* names (a9_art.js)
    A10 PASS — build_v8.py exit 0; CC-WB3 markers 18 ≥ 3 (a10_build.js)
    OVERALL: PASS (A1..A10 ALL PASS; no waivers this round)
    CODE-ONLY NOTE: this verdict validates code; playability is Nicko's bar.
