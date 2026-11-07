# CC-H1a — Door-Plane & Sides Correction (IO valspec, FINAL v2)

Author: IO (CaptainPickard). Date: 2026-11-07.
Status: SUPERSEDED-DRAFT replaced by this final version — the first draft
analyzed the F plane sitting at its disc center and proposed enemy seat
relocations; the final design (below) moves F's plane to its south-rim
mouth instead, which fixes the bug with ZERO gameplay-content changes
(enemy roster, props, rings, spawn/land rows all byte-unchanged).

Validation criteria (what Testerbot checks):

V-1 CONFIG.js regionF.door.planeZ == -662 (was -640). No other CONFIG.js
    change; `planeZ: -640` absent repo-wide.
V-2 region-defs.js conn[4] sides UNTOUCHED (E -1 / F +1) — with the
    corrected south-rim plane, sideIn(F) = +1 == sideOfPlane(land -650 vs
    -662) and sideIn(E) = -1 == sideOfPlane(F spawn -650 on the E side...
    parent reading) — the landed signs become CORRECT with no edit.
V-3 region-defs.js conn[5] sides: C 1 / G -1 (law: sideIn(R) ==
    sideOfPlane at R's interior; G interior -711 sits z < -700 => -1,
    C stands z > -700 => +1). Interior law comment replaces the old
    D-symmetry comment.
V-4 Engine-tick evidence: real RegionManagerLogic first-tick at each door
    region's spawn + own land row == NO cross (prewarm/null). Walk-back
    lanes cross to the parent: D outcrop -> forest, F south mouth ->
    veil_crypt, G gate -> forest. Probes:
    scratch/cc-h1a/sides_law_probe.js, scratch/cc-h1a/testerbot_tickcheck.js
    (Testerbot's independent probe) — both ALL CONSTRAINTS: PASS.
V-5 Enemy clamp safety with the corrected tables: F's two ghouls
    (-6,-636) / (6.5,-635.5) vs hold line lim = plane -662 + sideIn(F)
    (+1) x margin 1.5 = -660.5: both seats south of it (z -636 > -660.5),
    inside F's disc, no clamp. G has no enemies (hub).
V-6 Scope: git diff --stat shows EXACTLY prototype/js/CONFIG.js (1 line),
    prototype/js/region-defs.js (2 sides lines + comment),
    prototype/builds/v8-playable.html. game.js / region-manager.js /
    enemy.js / save.js / daynight.js byte-identical to HEAD.
V-7 Build: tools/build_v8.py exit 0; deterministic (two identical
    sha256); marker veil_galleries >= 8 in the bundle.
V-8 Playability remains Nicko's bar: no harness, no headless browser —
    the tick-level evidence above is code QA, not playtest.

Verdict artifacts: scratch/cc-h1a/testerbot-verdict.md (Testerbot PASS,
7/7 criteria), scratch/cc-h1a/build-note.md (Devbot).
