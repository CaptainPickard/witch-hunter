# CC-AD2 IO round log (gatekeeper bookkeeping, 2026-11-06)

## Devbot handoff (gate step 3) — deviations adjudicated by IO BEFORE commit

Devbot landed the round but introduced seats that drifted the spec seat
coordinates beyond the IO spec's stated tolerance (numerics +-0.05):

1. SPEC mourner seats: mourningStatue (-15.5,-593) / rubblePile (-15.0,-599.5)
   LANDED: mourningStatue (-12.35,-589.15) / rubblePile (-14.25,-597.55)
   (drift 3.85 m / 1.95 m).
   ADJUDICATION: ACCEPTED. The spec's own seats VIOLATED the spec's own
   clearance laws against the LANDED crypt ring (ring-edge distance 2.2 m /
   2.6 m < 4.0 law) and the aperture lane (statue seat sat inside the
   aperture walkable lane). Devbot's seats are the compliant solution:
   ring 4.05 m (statue), 2.36 m lane minimum (>= 1.5), covens 6.41 m,
   probe ALL PASS 85/85. This is the working tolerance the spec itself set
   for iterate-until-PASS; the drift is the fix, not a violation. The probe
   comment block + build note carry the full chain.
2. Spec A-2 wording named coordinates that were unsittable as written;
   FUTURE spec law (self-note): pre-spec probe MUST seat every spec row
   against the LANDED parent ring before freezing coordinates (the AD2
   pre-spec probe seated only the E-hook, not the mourner pair).

Devbot additionally added ONE F-region rubblePile prop row ({-7,-641}) that
the spec's props list did not enumerate (spec listed 8 rows incl. the statue;
landed F props = 8 incl. statue + rubble flanker... spec's rubblePile listed
at (-7,-641); LANDED matches). Census: spec 8 = landed 8.

## Build + marker ledger (IO re-verified)

- tools/build_v8.py rerun by IO: exit 0, bundle 3,370,962 bytes.
- Rebuild identity: sha256 of landed bundle == rerun bundle
  (17200e06aa3fd612f6874dbf62223f161c92d2a9b05d5ff0d6078b4463dd3f50).
- Marker: grep -c veil_galleries build = 9 (>= 8).
- Stash note: one PRE-EXISTING stash@{0} dated to the 10-05 v7-era worktree
  (400 files, base e80b932). Untouched by this round; NOT a Devbot artifact.
- game.js diff: EMPTY (0 lines). Files touched: CONFIG.js (+124/-2),
  region-defs.js (+39/-0), bundle. node --check both js files: PASS.

## Gate status

- Step 1 (IO spec): DONE io/specs/cc-ad2-veil-galleries-spec.md
- Step 2 (Testerbot valspec): DONE io/specs/cc-ad2-veil-galleries-valspec.md
  (child-written; IO aligned its criterion-number matrix to the IO spec
  list; substance unchanged)
- Step 3 (Devbot build): DONE (this log = IO adjudication of its seats)
- Step 4 (Testerbot independent validate): NEXT (separate dispatch, after
  IO commits the round so the diff basis pins)
