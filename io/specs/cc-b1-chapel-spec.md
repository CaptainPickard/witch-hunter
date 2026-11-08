# CC-B1 · Ruined Chapel Landmark, Region B (doc 61 P1-2) — io/spec — WAKE 34

## Mission

Assemble a **ruined chapel** in region B (`darkwood_edge`, CONFIG.js `regionB`)
at the forest centre from on-disk church-kit GLBs, lit by the candelabra —
doc 61 P1-2's physical-landmark bullet. This is the region's first TRUE
landmark (today's tallest objects are trees) and its amber-pool anchor.

Config-only round: no game.js / region-manager.js / engine changes. Everything
lands as CONFIG.js rows + assets.js manifest rows + one `lightSockets` entry,
all flowing through existing machinery (prop rows, `computeFireSockets`,
`lightSockets`, `noCollide`, `scatter.keepOut`).

## Art law (standing order 2026-11-06)

Anchors used this round (viewed by IO in framing pass):
- concept-01-darkwood.png — cool monochrome (indigo/charcoal/mist-grey), ONE
  amber accent (lantern flame), moonlit gothic ruin silhouette as canon.
- scene-01-bard-skeleton.png — ossuary nave read: pointed arches, moonbeam
  through broken vault, candle pools, "celebration of decay" mood.

Translation: the chapel is COOL; its one warmth is the candelabra pool at the
altar. Single-accent rule: region B's warm family = banditCampfire +
lanternWaymarker + new candelabra socket (all three live in the ruin cluster,
≤ 25 m apart — one family per H1 AMENDMENT B grammar).

## Environment (fixed paths)

- Worktree: /tmp/wh-worldfeat, branch feat/world-visuals, current HEAD c78e4e7.
- Repo files touched: prototype/js/CONFIG.js, prototype/js/assets.js ONLY.
- Build: `cd /tmp/wh-worldfeat && python3 tools/build_v8.py` (newest build tool;
  deterministic stamp law — title carries HEAD sha). Verify the stamp changed.
- NO-GIT: Devbot/Testerbot children NEVER commit or push. IO is sole gatekeeper.
- No harness runs, no headless browser smoke tests, no automated playability
  validation. Nicko's playtest is the acceptance bar. Offline probes (node, no
  three) are allowed — that is code QA.

## The kit (55 files, git-tracked, art-direction/3d/assets/church-kit/)

Unused pieces this round consumes: church-wall-window, church-window-frame,
church-roof-beam, church-altar, church-pulpit, church-pew (intact),
candelabra — all have `-pixelated.glb` variants on disk.
Already-wired pieces (DO NOT add manifest rows for these): churchArchway,
churchCornerButtress, churchPewBroken, rubblePile, ironFenceSection,
ironFenceCorner, lanternPost, deadTree.

## Seat (data-driven; PROPOSED, Nicko tunes)

Region B already prototypes the ruin cluster at (8..16, -41..-63): the
churchArchway row (x 8, z -58, rotY 0.9, scale 2.2), churchCornerButtress
(x -14, z -62, rotY 0.3, scale 2.0), churchPewBroken (x 16, z -52, rotY -0.7,
scale 1.8), cemetery gates/gravestones, banditCampfire (2.5, -52),
lanternWaymarker (-6.5, -47). The chapel ASSEMBLES AROUND THESE ROWS without
moving them (their x/z are locked; rotY may be re-seated only with an inline
comment saying so).

Proposed nave (compass: −z = NORTH toward the C door, +x = east): long axis
WEST-EAST, centre ≈ (0, −58), footprint ≈ x −16..17, z −66..−50. The player
enters B from the south gate and C's door waits north — the ruin stands
BROADSIDE to that walk, its lit altar visible down the 33 m east-west axis
(the concept-01 read: walking toward a lit ruin).
- WEST face (x ≈ −17.5): 3× churchWallWindow in a line along z at z −63.5 /
  −57.5 / −51.5, rotY ≈ π/2-ish so the plane faces EAST into the nave
  (scale 2.2 ⇒ 2.87 m run each — measured width 1.30 m; pieces stand ~2.0 m
  tall at 2.2), gaps ≈ 3.1 m between them (ruined sections, walk-through).
  The EXISTING churchCornerButtress (−14, −62) LOCKED reads as the north-west
  angle fragment; ONE new churchCornerButtress row mirrors it on the
  south-west angle (PROPOSED ≈ (−13.5, −54.5), rotY mirrored).
- NORTH face (z ≈ −66): 2× churchWallWindow (rotY ≈ π, planes facing SOUTH
  into the nave), seats ≈ (−3.5, −66) and (3.5, −66), 1 gap walk-through.
- Interior: churchPulpit ≈ (10.5, −62), scale 2.0 ⇒ 2.17 m wide (~4 m tall),
  rotY facing WEST toward the nave; ONE churchPew intact ≈ (5.5, −62), rotY
  ≈ π/2 (long axis runs north-south, seat faces EAST toward the altar), scale
  1.8 ⇒ 3.6 m long. The EXISTING churchPewBroken (16, −52) reads as the
  fallen east fragment; NO move. (One pew — the mid-nave bandit spawn
  (0,−60) plus the locked archway make a second pew fail clearance.)
- ALTAR END (east): churchAltar ≈ (14.5, −58), scale 2.2 ⇒ 4.4 m wide ×
  1.16 m tall, rotY so its face points WEST into the nave. Candelabra ON the
  altar: same x/z, y on the altar top (hosted stack — see R3), scale 0.45
  (measured dims 1.94 × 0.69 × 1.98 m at scale 1; at 0.45 it is 0.87 m wide,
  0.89 m tall — a table candelabrum; flame lands ≈ 1.9-2.0 m above ground
  via heightFraction 0.85).
- Gable fragment ABOVE the altar end: churchWindowFrame ≈ (14.5, −58) same
  x/z as the altar, rotY facing WEST, RAISED y ≈ 2.15 (a broken window in
  the collapsed gable above the altar, scene-01 moonbeam read), 
  `noCollide: true` (raised-row grammar). Floor-level gable seating was
  probed and REJECTED: collides with LOCKED pewBroken (16,−52) and the altar
  circle — disclose if a different seat is used.
- The EXISTING churchArchway (8, −58) LOCKED re-roles as a MID-NAV collapsed
  wall stub (it stands 6.5 m west of the altar, not in the gable) — the altar
  pool spills around it; no move, no rotY change.
- Roof: 2× churchRoofBeam ACROSS the nave (rotY ≈ ±π/2 so the measured
  1.975 m length runs along z; scale ≈ 7.2 ⇒ ~14.2 m span, seats z −65..−51),
  raised y ≈ 3.8..4.2, PROPOSED x ≈ −6 and −2 (the surviving west-half
  rafters), `noCollide: true` (the CC-C8 raised-row grammar). ONE fallen
  rafter as ground debris: scale 2.6, PROPOSED ≈ (−9, −55), tilted rotY,
  GROUND level (no y key) so it KEEPS its collider circle (r ≈ 2.57 m) —
  probe must clear it vs altar/pulpit/archway/rafter neighbours.
- Dressing: reuse rubblePile + mossBoulder rows already in the cluster; add
  ≤ 2 new rubblePile rows inside the nave (PROPOSED west half ≈ (−12, −60)),
  1 lanternPost v3 at the west face exterior (scale 2.535 to match region A's
  law) OPTIONAL — only if probe headroom allows; when in doubt, skip it.

## Machinery contracts (verified by IO census 2026-11-07)

- New assets need ONLY a manifest row in prototype/js/assets.js (pattern:
  `name: 'art-direction/3d/assets/church-kit/<file>-pixelated.glb',`). Measured
  width/height metadata, colliders (r = width × scale / 2 from
  region-manager.js colliderRadius), and ground seating ALL derive at load.
- Lights: one `lightSockets` entry keyed by the manifest key, e.g.
  `candelabra: { heightFraction: 0.55, intensity: 5.5, offset: [0, 0] }`
  (PROPOSED, Nicko tunes; lanternPost 9.0 / campfire 3.2 are the scale refs).
  The socket then flows free: game.js computeFireSockets reads CONFIG prop
  rows by asset key — no engine code.
- Colliders: every prop row (unless `noCollide`) contributes one circle
  (r = width × scale / 2; trees get trunk ratio — n/a here). Fat circles on
  wide wall pieces are EXPECTED for chunky ruin dressing; ruined gaps keep the
  nave walkable.
- `y` key: region B is flat (groundY 0). New rows omit `y` (seat at ground)
  EXCEPT roof beams (raised y) and any row the probe seats on evidence.

## Scatter keep-out (must land with the rows)

One keepOut ellipse appended to CONFIG.scatter.keepOut (line ~2558):
`{ regionId: 'darkwood_edge', x: 0, z: -58, rx: 21, rz: 12.5 }` (PROPOSED,
Nicko tunes; AMENDED wake 34: rx widened 17→21 so the x −17.5 west-wall rows
and the SW buttress (−13.5,−54.5) sit INSIDE the ellipse and keep Round-E
auto flora out of the whole ruin) so Round-E auto trees/bushes never spawn
inside the nave. Grass stays (unblocked by design — moss floor inside the
ruin reads canon).

## Acceptance criteria (Testerbot validates these independently)

R1 LANE: every chapel piece's collider circle keeps ≥ 8 m edge distance from
the B/C door window segment (x −4..4 at z −86) and from the A/B chokepoint
corridor (x ±6 at z −25). No circle may cover any gather node within 3 m,
enemy spawn within 4 m, the banditCampfire within 2 m, lanternWaymarker
within 1.5 m.
R2 MUTUAL: every NEW piece ≥ 0.6 m edge-to-edge (colliders may not overlap)
against ground pieces, EXCEPT: (a) INTENTIONAL ruined gaps ≥ 2.5 m between
wall rows (probe marks them, walk-through law); (b) the candelabra-vs-altar
stack (candelabra sits ON the altar: same x/z, explicit y, R3 exemption);
(c) pieces explicitly declared in the spec as re-used/locked rows keep their
existing seats; (d) DEBRIS-AMONG-FURNITURE (scene-01 anchor: scattered
debris amid the congregational furniture): NEW pieces vs the LOCKED
treeStump rows at (13.4,−58.7) and (13.0,−55.5) may overlap circles — the
dead forest reclaims the ruin; gameplay circles resolve independently.
Existing dressing (mossBoulder 17.1,−52.8, fallenLog,
treeStump 13.4,−58.7 / 13.0,−55.5 near the nave east) resolves ≥ 0.8 m from
NEW pieces or the NEW row is re-seated (existing rows are locked), (d)
exemptions aside.
R3 Y / NO-COLLIDE LAW: noCollide appears ONLY on raised rows (the two roof
beams y 3.8..4.2 and the one gable window y ≈ 2.15). The candelabra row
carries explicit y (altar top) and NO noCollide — it is exempt from R2
ground-overlap ONLY against the altar (circle-vs-circle overlap with the
altar is REQUIRED evidence of the stack). Every other ground-level row (incl.
the fallen rafter) has no y key and no noCollide key. Raised rows' 2D circles
still obey R1 edge rules vs ground pieces outside the nave; inside the
footprint, raised circles must not cover the altar/pulpit centres within 1 m.
R4 LIGHT: exactly ONE new lightSockets key, keyed to the candelabra manifest
name, comment noting the warm-family grammar. No other lightSockets churn.
R5 MANIFEST: 7 new keys (churchWallWindow, churchWindowFrame, churchRoofBeam,
churchAltar, churchPulpit, churchPew, candelabra) with exact paths to
existing on-disk files; no keys renamed/removed; no other manifest churn.
R6 SCATTER: the keepOut row present, regionId darkwood_edge, ellipse covers
the nave footprint (probe: every wall/altar/pew row seat inside the ellipse).
R7 TRI LEDGER: offline probe (node, no three, GLB header/json parse or
trimesh) reports the SUM of face counts of every consumed GLB at scale 1;
landmark law target ≤ 30k (doc 61 sec tri budget: landmarks up to ~30k for
1-2 instances). Report the number; fail above 60k.
R8 JS SANITY: prototype/js CONFIG.js + assets.js parse (node --check is fine
for a bare function-body? If CONFIG.js references window at top level, parse-
only via `node --check` still passes — it validates syntax only). Build runs:
`python3 tools/build_v8.py` produces builds/v8-playable.html; title stamp
changes (deterministic-stamp law: stamp = HEAD author time + sha, so a NEW
COMMIT is required for a visible stamp change — Devbot does NOT commit (NO-GIT);
Testerbot verifies the build OUTPUT changed vs pre-round bytes and grep-checks
the new asset keys + keepOut row appear in the built HTML).
R9 No file outside prototype/js/CONFIG.js and prototype/js/assets.js is
touched. No engine-behaviour edits smuggled in.

## Deliverables (Devbot)

- Edits in /tmp/wh-worldfeat worktree on feat/world-visuals (UNCOMMITTED).
- Probe script scratch/cc-b1_probe.cjs (clone the cc13b_probe.cjs pattern:
  parse CONFIG regionB + scatter rows, nominal widths for new assets —
  WIDTH table extended; exit 1 if any rule fails; print a seat table).
- Report io/specs/cc-b1-chapel-buildsummary.md: what landed, probe output,
  build size, stamp, tri ledger, deviations (if any) disclosed.

## Deliverables (Testerbot)

- Validation spec: io/specs/cc-b1-chapel-valspec.md (BEFORE Devbot starts).
- Independent verdict: io/reports/cc-b1-chapel-verdict.md — PASS/FAIL per
  rule R1-R9 with evidence lines (probe output), final verdict line.

## Explicitly out of scope

Silhouette cards, sky dome, moon sprite (art-gated, blocked on the image
provider), any A-side gate/mausoleum, engine or lighting-pool changes,
enemy/combat tuning, doc edits outside io/.
