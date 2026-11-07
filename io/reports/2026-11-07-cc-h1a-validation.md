# CC-H1a — Door-Plane & Sides Correction: Independent Validation

**Round:** CC-H1a (P0 playability blocker fix: conn[4]/conn[5] one-way doors)
**Scope:** CONFIG.js + region-defs.js (3 data lines) + v8 rebuild
**Commits:** f9fb8f4 (fix + test artifacts + H1a spec/valspec) + 7805998 (build)
**Verdict: PASS — 0 blocking.** All acceptance criteria A-1..A-7 PASS.

## Provenance (disclosure)

The Testerbot child of the 04:02Z wake completed both probe suites and its
verdict, then died before filing the canonical report here (scratch/cc-h1a/
testerbot-verdict.md survives; delegation manifests 03:59-04:01Z corroborate
gate order: valspec -> tickcheck -> build note -> verdict). This wake's IO
re-verified every claim independently before adopting the verdict:

- Both probe suites re-run fresh by IO at 2026-11-07 04:35Z:
  scratch/cc-h1a/sides_law_probe.js -> ALL CONSTRAINTS: PASS
  scratch/cc-h1a/testerbot_tickcheck.js -> ALL CONSTRAINTS: PASS
- Landed values verified by grep at HEAD 7805998:
  CONFIG.js:1611 regionF.door.planeZ = -662 (south-rim grammar, 4 m inside
  the r26 south rim -666; no -640 remaining)
  region-defs.js:217-218 conn[5].sides C=+1 / G=-1 (interior law:
  sideIn == sideOfPlane at each region's interior points)
- conn[4] confirmed untouched-as-landed-noop-verified: E=-1 / F=+1 hold under
  the corrected plane -662 (F interior z -650 now reads -1 < -662? no: -650 >
  -662 -> +1 = sideIn(F) PASS; probe EDIT rows PASS).

## Acceptance criteria

- A-1 scope: git diff --stat d6665ec..f9fb8f4 = 9 files — CONFIG.js (1 line),
  region-defs.js (sides table + comment), v8 bundle, cc-h1a spec/valspec,
  4 scratch files. game.js / region-manager.js / enemy.js / save.js /
  daynight.js byte-clean. PASS
- A-2 no engine edits: PASS (game.js untouched)
- A-3 sides-law probe: ALL CONSTRAINTS: PASS (re-run fresh 04:35Z). PASS
- A-4 enemy roster purity: F's 2 ghoul rows unchanged (probe output verbatim:
  {"type":"ghoul","x":-6,"z":-636}, {"type":"ghoul","x":6.5,"z":-635.5}). PASS
- A-5 build: build_v8.py deterministic, exit 0; sha256
  d1f14e23d6795eb161e6206d1841c368f233765a2c2e9566a0ceee22e8357970;
  3,422,926 bytes; marker veil_galleries x9. PASS
- A-6 byte-identity at serve: worktree v8 == served v8
  (curl http://172.16.5.1:8793/current/prototype/builds/v8-playable.html,
  sha-identical to 18 digits both). PASS
- A-7 all door connections + walk-backs: first-tick no-cross at spawn + own
  land row for D/E/F/G; walk-back crosses to parent inside door window for
  D->forest, F->veil_crypt, G->forest (outcrop lane / south mouth lane /
  gate lane). PASS

## Serve state at adjudication

Release releases/7805998 live at /tmp/wh-playtest-share/current (auto-prune
clean, single release dir); title stamp "Witch Hunter v9 - EPR1 Combat (build
11-07 04:02Z f9fb8f4)"; 8793 return 200; concepts-web jpg 200.

## Engine law (amendment landed doc 66 sec 10)

sideOfPlane(conn, z) = z > planeCoord ? 1 : -1. For a -z-chained pocket the
pocket interior sits at z < planeCoord -> sideIn(pocket) = -1, sideIn(parent)
= +1. The door plane MUST sit on the pocket's parent-facing edge (4 m inside
the rim, D/E mouth grammar) — a mid-plane disc (F was -640 on disc
-666..-614) admits no valid sides sign. Every future instanced-region round
asserts sideIn(spawnRow) == sideIn(region) + edge-of-rim plane + first-tick
no-cross + walk-back probes (reuse scratch/cc-h1a/sides_law_probe.js).
