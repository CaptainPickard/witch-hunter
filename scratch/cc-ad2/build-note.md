# CC-AD2 build note (Devbot for IO, 2026-11-06)

Round: The Erased Galleries (doc 47 Veil strata V2), chained off veil_crypt.

## Files touched

- prototype/js/CONFIG.js — regionE edits (A-2): erased whWallB (-8.3,-612.0);
  appended mourner pair (2 rows) at the props tail. New regionF block
  appended after regionE (A-1): id veil_galleries, full key set per spec
  section 2.
- prototype/js/region-defs.js — regions[veil_galleries] registration
  (makeRegion, side -1) + connections[4] shaped exactly on conn[3]:
  from E, to F, axis z, planeCoord F.door.planeZ (-640), walkFrom F,
  interact.from E at (-14.5,-596) r 3.5, sides E -1 / F +1, land rows per
  spec. No helpers touched.
- prototype/builds/v8-playable.html — rebuild via tools/build_v8.py.
- game.js: ZERO lines (A-4). No other files.

## Seat deviations (disclosed, adjudicated in scratch/cc-ad2/io-adjudication.md)

Mourner pair spec seats sat ON the landed crypt ring edge (2.2/2.6 m < 4.0)
and inside the aperture lane. Landed seats are the compliant scan:
mourningStatue (-12.35,-589.15) ring 4.05 m, rubblePile (-14.25,-597.55).
All other rows match spec numerics exactly (probe tolerance +-0.05).

## Probe (CONFIG-row-parsed)

scratch/cc-ad2/solve_geometry.py: ALL CONSTRAINTS: PASS (85 checks) —
F shell, ring gap window (0 colliders in |x|<=2.2 @ z -640, full octant
coverage elsewhere), ghouls (>= 8 from spawn, 12.51 mutual >= 12.4 floor,
>= 14.9 m ring walk-clear), props (all margins), E west aisle (aperture
lane 2.36 min, whWallB absence, remaining ring 7 rows), conn[4] sides + land
rows on home sides.

## Build (IO re-run verified)

- python3 tools/build_v8.py -> exit 0, 3,370,962 bytes.
- sha256 rebuild identity: 17200e06...3dd3f50 (landed == rerun).
- grep -c veil_galleries build = 9 (>= 8).
- node --check CONFIG.js + region-defs.js: PASS.

## Art law

No new accent colors. ONE crimson accent = blightcap caps (2 in F). Anchors:
concept-08-veil-spire + day-08-veil-spire (erased statue field) +
concept-05-night-ambush (fog tiers). Existing manifest assets only.
