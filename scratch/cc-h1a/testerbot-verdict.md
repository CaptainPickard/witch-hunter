# Round CC-H1a — Door-Plane & Sides Correction: verdict summary

Testerbot (independent): VERDICT PASS. All criteria A-1..A-7 PASS.
- Landed edits verified by grep: CONFIG.js planeZ -662 (no -640 remaining),
  conn[5] sides C=1/G=-1, conn[4] sides untouched (E=-1/F=+1).
- Scope verified: git diff --stat = 3 files (CONFIG.js, region-defs.js,
  prototype/builds/v8-playable.html) + untracked io/specs/, scratch/.
  game.js, region-manager.js, enemy.js, save.js, daynight.js byte-clean.
- Probes: scratch/cc-h1a/sides_law_probe.js ALL CONSTRAINTS: PASS;
  scratch/cc-h1a/testerbot_tickcheck.js ALL CONSTRAINTS: PASS.
- Build: python3 tools/build_v8.py twice, exit 0, sha256
  193c728fee46611cf99bc8b78c814306357225d9edcfa16555b298e058713e17
  identical across runs, bundle 3422926 bytes, marker veil_galleries = 9.
- Engine law derived independently (sideOfPlane/tickTransition/
  clampEnemyToHomeSide): all door conns satisfy sideIn == sideOfPlane
  interior at spawn + own land rows; F ghouls (-6,-636)/(6.5,-635.5)
  unaffected by the corrected hold line (lim -660.5).
Notes: none blocking.
