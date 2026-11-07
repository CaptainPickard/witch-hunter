# DEVBOT BUILD BRIEF — CC-H1 Lord's Hold (gate step 3)

You are Devbot. You implement round CC-H1 (the first castle-ready hold site,
"LORD'S HOLD") from two governing files in the worktree /tmp/wh-worldfeat on
branch feat/world-visuals (HEAD e8dda52):

1. io/specs/cc-h1-lords-hold-spec.md  — the spec (WITH amendments A, B, C:
   A corrects the connection 'from' to CFG.regionC.id; B clarifies the warm
   socket count is FIVE rows of one amber family; C clarifies the north seat)
2. io/specs/cc-h1-lords-hold-valspec.md — the validation spec Testerbot wrote
   BEFORE this build (you must satisfy every blocking V-check it contains)

## Your deliverables (all under /tmp/wh-worldfeat, NO-GIT law)

1. prototype/js/CONFIG.js — append regionG (id lords_hold) after regionF,
   additions ONLY, every row exactly as the spec section 2 prints them
   (89 curtain-wall rows: take them VERBATIM from
   scratch/cc-h1/seat_scan_output.txt lines 29-117, A/B alternate by index
   parity as printed; the 90-degree segment is OMITTED = gate gap).
2. prototype/js/region-defs.js — one makeRegion registration line after the
   regionF line + the connections[5] block shaped on the landed connections[3]
   row (CC-AD1: from regionC, walkFrom regionG, interact from C at
   door.interactAt) + the two sides lines (C = -1, lords_hold = +1).
   NOTHING else in the file changes.
3. scratch/cc-h1/clearance.py — the geometry gate, modeled on
   scratch/cc-ad2/solve_geometry.py: parse the LANDED regionG rows live from
   CONFIG.js (regex, no hard-coding the numbers you just wrote), rebuild the
   wall-collider circles per whPropColliders (r 0.45, asset width 1.899 x
   scale, wall 12 along local X), and assert EVERY clearance law of the spec
   section 2 + valspec V-5 (89 rows / 1068 colliders; ring closed EXCEPT the
   door window |x| <= 4.5 at z -700; spawn + both land rows inside r 126 of
   center (0, -822); hub cluster mutual/raw margins; door-lane window empty;
   octant coverage outside the gap arc; wall rows byte-match the frozen ring).
   Print one line per check with ok/FAIL + margin. Exit 0 only if ALL pass.
4. scratch/cc-h1/save_roundtrip.js — the THREE-free save proof modeled on
   scratch/cc-ad1/save_roundtrip.js: config + region-defs + save.js stubbed,
   capture/restore with activeId lords_hold, validRegion('lords_hold') true,
   negative control with an unknown region id.
5. Run: python3 scratch/cc-h1/clearance.py (must exit 0, ALL PASS) and
   node scratch/cc-h1/save_roundtrip.js (must exit 0, all PASS) and
   node --check prototype/js/CONFIG.js + node --check
   prototype/js/region-defs.js (must pass — this also proves the Lord's Hold
   name string quotes).
6. Verify the diff discipline: git diff --stat must show ONLY CONFIG.js and
   region-defs.js changed in prototype/; git diff on each shows ONLY added
   lines (no row deleted or modified); game.js diff EMPTY.
7. Write your build note to scratch/cc-h1/build-note.md: what you built, the
   clearance.py + save_roundtrip.js outputs (paste the PASS tails), any
   deviation as numbered ED-1..N entries (EVERY deviation disclosed, none
   silent), and confirmation you ran NO git write commands.

## Hard laws (from PRIMARY.md + the spec section 7)

- NO-GIT: never commit, never add to the index, never push, never amend,
  never set git identity. IO is the sole committer.
- No harness runs, no headless browser smoke tests, no playtesting.
  node --check, grep, python scripts, logic-level node: that is your toolbox.
- Do not regenerate art, do not touch manifest GLBs, do not modify any other
  file (daynight.js, save.js, camp.js, chest.js, npc.js, light.js, player.js,
  enemy.js, game.js: all read-only for you).
- Build tool: do NOT run tools/build_vX.py — the committed build is IO's
  gatekeeper step; your round ends at source files + probes + notes.
- Provider stall with work landed = report and stop cleanly (do not block).
