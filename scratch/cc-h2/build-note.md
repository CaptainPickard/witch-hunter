# CC-H2 Devbot build note — garrison-courtyard round (IO spec cc-h2-garrison-spec.md)

Worktree /tmp/wh-worldfeat, branch feat/world-visuals, HEAD 24a6e95 at START and
UNCHANGED at finish (verified git log --oneline -1 after all edits; NO-GIT clause
honored: zero commits/pushes/checkouts/branches/worktrees written; every git op
ran was READ-ONLY — diff/log/status/numstat/show). Build tool:
python3 tools/build_v8.py (newest-tool law). NO harness runs, NO headless
browser runs — validation is python probes + static census only.

## 1. What changed (files + line counts; git diff -U0 24a6e95 --numstat)

- prototype/js/CONFIG.js  (+152 / -3)
  a. regionG aperture (spec sec 1): deleted EXACTLY the two landed south-pole
     flank curtain rows, byte-identical:
       { asset: 'whWallA', x: 4.4, z: -947.92, rotY: 6.25, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
       { asset: 'whWallB', x: -4.4, z: -947.92, rotY: 0.03, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
     and inserted the ONE 3-line `//` comment block (BV-002: "one comment block"
     = the 3 printed lines as a unit) directly above the next surviving row,
     verbatim per spec sec 1:
       // CC-H2 (doc 64 slot H2): the two south-pole flank rows ERASED 2026-11-07
       // — the garrison breach; the plane rides z -948 (regionH door row), the
       // aperture lane stays |x| <= 4 (probe: scratch/cc-h2/seat_scan.py).
     NOTHING else in regionG moved: the remaining 87 curtain rows + all 24
     dressing rows + door/spawn/land are byte-identical (clearance.py census +
     the -U0 hunk shows exactly the 2 deletions and the 3 comment lines).
  b. regionH block (spec secs 2 + 3): appended after regionG's closing `},`
     (one blank line separator), 148 lines total = 11-line comment header
     (byte-exact incl. the ============================== banner) + every key
     byte-exact: id 'fort_garrison', name 'Garrison Keep', center {0,-1024},
     groundRadius 80 (playRadius 78.5), groundY 0, groundColor 0x33363c,
     groundColor2 0x2a2d33, groundSeed 1662061651 (grep -c in CONFIG.js = 1,
     the regionH row only; fresher than every landed seed
     1217/1218/1219/1329/1440), scatter false, spawn {0,-955}, gravityY -22,
     fogColor 0x7d8289, fogDensity 0.068, ambientLightLevel 0.09, door
     {planeZ -948, doorX 0, doorHalfWidth 4.0, suspendDepthM 4, wallGapPadM 0,
     land.fort_garrison {0,-955,face 0,-1100}, land.lords_hold
     {0,-941,face 0,-822}, fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8}. The spec
     sec 2 `# props` pseudo-line is spec notation only — the real file carries
     the sec 3 props block with `//` comments (BV-002-style reading honored).
     Absences asserted by clearance.py: NO walkFrom, NO interactAt/interactM,
     NO arch row, NO gatedTo, NO text row, NO constantPhase, NO terrain row
     (seat_scan's PROPOSED hook (0,-934)/m 3.5 intentionally NOT landed,
     BV-003). enemies: exactly 2 bandit rows (-10,-975) / (11,-976).
     props: 66 rows = 16 sec 3 manifest rows byte-exact from
     props_scan_output.txt (asset/x/z/rotY/scale identical; the probe prints
     floats, the file prints ints — value-exact per valspec V-3.2 spelling
     law) + the 2 okFenceStonewall flankers (10,-968)/(-10,-968) + the
     48-seat H2 curtain ring pasted verbatim from seat_scan_output.txt
     RING ROWS (printed asset column = ground truth: first row whWallB
     14.99,-945.42 rotY 3.33, strict BA alternation in ring order).
     Light law (BV-001 resolved IO option b, recorded in the landed comments):
     regionH socket-carrying rows = banditCampfire (0,-990) + lanternPost
     (6.5,-954) + the 2 whCampkit rows = ONE warm amber family, FOUR sockets;
     'torch' has NO lightSockets row (pure dressing); crimson zero
     (no blightcap or any crimson-family asset in the 18 dressing rows).
- prototype/js/region-defs.js  (+37 / -0)
  a. Registration: the 2-line C0-7 law comment + `regions[CFG.regionH.id] =
     makeRegion(CFG.regionH, -1);` appended directly after the regionG
     registration line, before any other line moves (side -1 = the plane-0
     convention only; H sits on no plane-0 side). Spec sec 4(a) requires the
     C0-7 law note "in the adjoining comment", so the note rides immediately
     above the registration line (the landed CC-H1 registration carries its
     own 4-line C0-7 note the same way). Nothing else modified.
  b. connections[6] block + sides table inserted after the conn[5] sides pair
     and BEFORE the 'THREE-free transition helpers' comment (the insert
     ceiling), EXACTLY per spec sec 4: the 10-line sec 10 comment banner, then
     `var HD = CFG.regionH.door;` + connections.push({ from: CFG.regionG.id,
     to: CFG.regionH.id, axis: 'z', planeCoord: HD.planeZ, sides: {}, door:
     { doorX: HD.doorX, doorHalfWidth: HD.doorHalfWidth,
     suspendDepthM: HD.suspendDepthM, wallGapPadM: HD.wallGapPadM,
     arch: null, gatedTo: null, land: HD.land } }) — NO walkFrom row, NO
     interact row (two-sided B/C grammar). Then the SIDES TABLE banner and the
     two adjacent literal rows: connections[6].sides[CFG.regionG.id] = 1;
     connections[6].sides[CFG.regionH.id] = -1. No existing connection or
     helper touched; node --check passes.
- prototype/builds/v8-playable.html  (+190 / -4) — regenerated by
  python3 tools/build_v8.py from source AFTER the final region-defs edit
  (3,436,213 bytes); bundle census confirms the landed aperture comment, the
  regionH block, conn[6], sides rows and groundSeed 1662061651; the two
  deleted byte rows appear NOWHERE.
- scratch/cc-h2/clearance.py (NEW), scratch/cc-h2/build-note.md (this file),
  scratch/cc-h2/append_regionH.py (the paste-verbatim helper used for the
  regionH append; disclosed in sec 5 ED-1 below).
- game.js and EVERY other JS file: diff EMPTY (`git diff -U0 24a6e95 --
  prototype/js/game.js` = 0 lines; numstat shows only the three declared
  files; daynight.js untouched — no constantPhase row spec'd).

## 2. Clearance probe (scratch/cc-h2/clearance.py)

Live-parses prototype/js/CONFIG.js + prototype/js/region-defs.js (loader shape
on scratch/cc-h1/clearance.py; NO hard-coded spec constants feed the new-row
assertions — ring geometry, props, door keys, conn keys, sides signs all read
from the landed text; only the physics constants ride the landed law: AW
1.899, wall collider r 0.45, sideOfPlane definition replicated from the
region-defs helper `z > planeCoord ? 1 : -1`). 146 checks covering every
valspec V-5/V-6/V-7 constraint:

- V-6 A (H2 ring): 48 ring rows; 384 colliders (wall 8 x 1.899 x scale 5.29);
  strict A/B alternation; every row |hypot(x, z+1024) - 80| <= 0.6 (max dev
  0.0052); window strip |x| <= 4 /\ |z + 948| <= 3 EMPTY; lane samples (x
  -4..4 step 0.5 on the plane) nearest collider 7.4905 >= 1.0; mouth bearing
  arc [82.8, 97.2] (seat-scan convention atan2(z-cz, x-cx) % 360) holds 0
  colliders; every octant >= 8 (min octant 34).
- V-6 C (props): all 18 landed dressing rows (16 manifest + 2 flankers) rho
  <= 78.5; >= 4.0 m raw of BOTH rings (G post-erase 1044-collider set + H2
  384; min G-ring 4.29 at the lanternPost); >= 6.0 from spawn + both land
  rows (min 6.5765); >= 4.0 mutual across all 18 (min 5.6569); >= 5.0 from
  both sentries (min 7.0); flankers >= 16.0 off the H2 ring (23.1151 /
  23.1171) and >= 4.0 off the G post-erase ring (20.29 / 20.31).
- V-6 D (enemies): exactly 2 bandit rows; mutual 21.0238 >= 12.5; each
  >= 8.0 from spawn and both land rows (22.3607 / 23.7065); inside play
  radius (50.01 / 49.24); >= 4.45 walk-clear of the H2 ring (29.9891 /
  30.7862) AND of the G post-erase ring (27.30 / 28.33) — neither sentry sits
  anywhere near the window lane.
- V-5 (sides law, doc 66 sec 10, BOTH directions):
  sideOfPlane(conn6, -822) == 1 == sideIn(conn6, 'lords_hold') AND
  sideOfPlane(conn6, -1024) == -1 == sideIn(conn6, 'fort_garrison');
  land rows home-side: land.fort_garrison z -955 <= planeZ -948;
  land.lords_hold z -941 > -948; spawn depth past the plane 7.0 >=
  suspendDepthM 4.
- V-7 (G aperture post-erase): 87 curtain rows live (89 landed minus the
  erased pair); 1044 colliders (87 x wall 12); lane domain x -4..4 with z
  -951..-945 (0.25 m grid, 825 samples) has 0 colliders within 1.5 m of any
  sample (nearest 5.1604); both deleted byte strings absent from CONFIG.js
  (full string + row-body prefix search both clean); no surviving G wall row
  at (±4.4, -947.92); G dressing row count unchanged (24).
- conn[6] shape: from/to/axis/planeCoord/sides{} + door{doorX, doorHalfWidth,
  suspendDepthM, wallGapPadM, arch: null, gatedTo: null, land: HD.land}; NO
  walkFrom, NO interact anywhere in the block; both sides-table rows present
  with the sec 10 banner; makeRegion(CFG.regionH, -1) registration present.

FINAL LINE (exit 0): ALL CONSTRAINTS: PASS (146 checks)
Cross-run of the IO pre-spec probe against the LANDED rows:
python3 scratch/cc-h2/props_scan.py (live tree) -> MANIFEST CHECKS: PASS.

## 3. Build (A-10 / V-8)

- python3 tools/build_v8.py IN THE WORKTREE -> rewrote
  prototype/builds/v8-playable.html (3,436,213 bytes).
- Title stamp: NEW (date-time changed vs the pre-build bundle). The stamp
  derives DETERMINISTICALLY from the HEAD commit (build-tool law, tool lines
  39-46): OLD 'Witch Hunter v9 - EPR1 Combat (build 11-07 04:02Z f9fb8f4)'
  -> NEW 'Witch Hunter v9 - EPR1 Combat (build 11-07 04:35Z 24a6e95)'.
  Changed title text on an unchanged HEAD is exactly the intended effect (the
  tool stamps the HEAD the tree edits ride).
- Bundle greps: 'fort_garrison' count = 5 on the LANDED bundle (lines):
  CONFIG regionH id row + land key + def registration comment + conn comment +
  conn to row. Valspec V-8's floor `grep -c fort_garrison >= 8` DOES NOT
  HOLD at that count — recorded as a spec-vs-bundle variances for Testerbot /
  IO adjudication (see sec 5 ED-2): the landed traceability basis is 7
  `CC-H2` comment tags across CONFIG.js + region-defs.js (7 in the bundle)
  and clearance.py's 146 live re-parsed assertions over every landed row,
  identical to the CC-H1 adjudication precedent (BV-001/0b-2: marker counts
  are traceability proxies, the clearance re-parse is the hard gate). The
  landed sibling region markers in this bundle: veil_galleries 9
  (5 comment tags vs H2's 7), lords_hold 6 — the round's marker counts ride
  per-region comment density and comment law, not a per-region constant.
  IO's rebuild is the marker-floor completion gate exactly as in H1.
- node --check CONFIG.js region-defs.js: OK post-edit (both parse clean).

## 4. Spec sec 5 engine census (record-only; NO code changes)

- tickTransition: fort_garrison walks ONE connection (conn[6], planeIn true
  both — no walkFrom). lords_hold walks TWO (conn[5] walkFrom lords_hold +
  conn[6] planeIn-both). connectionsOf('fort_garrison') == [conn[6]];
  connectionBetween(lords_hold, fort_garrison) == conn[6].
- inOpenDoorBand / holdAtLockedDoor: gatedTo null on conn[6] ->
  doorLocked always false -> no hold path on conn[6]. Band edge |z -
  planeZ| <= suspendDepthM = 4 (region-manager line 169, edge-inclusive):
  crossing x 0 at z -948 ± 4 lifts BOTH disc clamps (G playable south rim
  -946.5 sits inside the band; H2 usable north rim -945.5 likewise).
- clampEnemyToHomeSide: the sentries' home side on conn[6] = sideIn(conn6,
  'fort_garrison') = -1; hold line = planeCoord + (-1) * 1.5 = -949.5;
  sentries at z -975/-976 <= -949.5 -> NEVER clamped (seats sit 25+ m past
  the hold line toward the H2 interior).
- The fade read: game.js ~line 3097 rides tr.conn.door.exitFadeOut = 0.8 on
  the walk-cross landing (AD1 law); fadeIn 0.3 / fadeOut 0.5 are landed in
  the door row but consumed by the interact path only (unused under B/C
  grammar; kept per the landed field set).
- Prewarm: G-side players near the south curtain prewarm fort_garrison
  (conn[6] nearest plane); fort_garrison players prewarm lords_hold
  everywhere in the north band of the yard (conn[6], both sides planeIn-true).

## 5. Deviations ledger

- ED-1 (self, process): the append_regionH.py paste helper's first write
  doubled the 12-row non-ring manifest run. Caught immediately by the
  landed-vs-spec byte-diff check, removed in one targeted delete; the final
  landed sequence is single and clearance.py's exact 18-row dressing census
  re-affirms 146/146 PASS. Disclosed for the record; no residual drift.
- ED-2 (self, recorded for Testerbot/IO adjudication): the landed bundle
  carries fort_garrison x 5 vs valspec V-8's declared >= 8 marker floor.
  Cause: the spec's landed shape yields only 3 literal id rows in source
  (CONFIG id + land key; region-defs conn to) — sibling counts ride per-region
  comment density (veil_galleries 9 / lords_hold 6 in the same bundle).
  Adjudication route (H1 precedent BV-001 0b-2): marker greps are
  traceability proxies; the hard gate is clearance.py's 146 live re-parsed
  assertions + 7 CC-H2 tags in the bundle. IO's rebuild completes the
  V-1/V-8 marker question exactly as in the CC-H1 round. The registration
  line now also rides the required C0-7 law note (spec sec 4(a)); no other
  spec deviation exists.
- BV-001 resolved: IO option b already adjudicated into spec sec 3 wording
  (FOUR-socket amber family); the lightSockets table untouched; observed
  socket-carrying rows = 4 (banditCampfire + lanternPost + 2 whCampkit), all
  one warm family; torch explicitly socket-free; crimson zero.
- BV-002 honored: the aperture insertion is ONE 3-line comment block.
- BV-003 honored: interactAt/interactM/text landed NOWHERE (absence asserted
  by clearance.py).

## 6. Diff stat (git -C /tmp/wh-worldfeat diff --stat; READ-ONLY)

 prototype/js/CONFIG.js      | 152 ++++++++++++++++++++++++++++++++++++++++++++++-
 prototype/js/region-defs.js |  37 ++++++++++++++++++
 (git diff -U0 24a6e95 --numstat adds: prototype/builds/v8-playable.html
 +190/-4 — the rebuilt bundle. Untracked additions: io/specs/cc-h2-*.md inputs
 + scratch/cc-h2/* — no other tracked file moved; git status porcelain shows
 only the three declared modified files + those untracked paths.)

## 7. IO close-out (2026-11-07, post-verdict)

- Testerbot verdict: PASS 8/8 (io/reports/2026-11-07-cc-h2-validation.md),
  2 variances, both resolved by IO before commit:
  - VAR-1 resolved: the survivor row x -13.17 re-letter-flipped by the paste
    helper (whWallB+sy 11.69 vs landed whWallA) — restored byte-identical to
    24a6e95 (inline <20-line no-logic fix, IO-disclosed); probes re-run ALL
    PASS post-fix (clearance 146, verdict_clearance 132, verdict_sides 53).
  - VAR-2/ED-2 (stale stamp): resolves at the IO rebuild — commit 1 lands
    source at HEAD, build_v8 stamps from the new HEAD's author time.
- Landing law applied (doc 66 sec 8 build order): IO commit 1 (CONFIG.js +
  region-defs.js + docs 64/66 + spec/valspec/verdict/probes) -> build_v8 ->
  IO commit 2 (stamped bundle) -> flip -> serve verify.
- Devbot's pre-commit bundle was built from source HEAD 24a6e95 (stamp
  11-07 04:35Z 24a6e95): source-correct, stamp-stale by the deterministic
  law; not a code defect.
