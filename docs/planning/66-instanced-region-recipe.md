# 66 - Instanced-Region Recipe (the cookie-cutter for pocket regions)

Status: RECIPE, 2026-11-06 (IO autopilot wake 15, tree tip 2d072ba). Companion
to doc 64 (region registry + slots H1-H6, the claim ledger), doc 47 (altar
delves GDD), docs 62/63 (region C). Source of truth for every landed value
cited here: CONFIG.js @ 2d072ba (3936 lines), region-defs.js,
region-manager.js, wh-ground.js, save.js, daynight.js.

Purpose (Nicko directive 2026-11-06, "instanced areas are a FIRST-CLASS lane"):
distill the two landed chains (CC-AD1 veil_crypt, CC-AD2 veil_galleries) plus
the D-den machinery into ONE template. After this doc, every new instanced area
is SPEC-FROM-TEMPLATE: IO fills the blanks, Testerbot pins sha windows by
content anchor, Devbot lands it, the probe re-runs the constants, IO commits,
doc 64 flips the slot row. No new machinery needs inventing — zero deviations
were found during the doc 64 census, and this recipe generalizes cleanly to
slots H1-H6.

## 0. When to use this recipe

- A new OWN-DISC pocket/interior/hold reached by a DOOR
  (interact-hook + walk-back plane): use this recipe. Covers pockets D/E/F
  today and every doc 64 hold slot (H1-H6).
- A NEW shared-boundary walk-across region (A/B plane style): NOT this
  recipe — plane-0 machinery is a one-off (A/B on shared disc, chokepoint
  row). Do not generalize it; the pocket door grammar is the lane.
- NOT for scatter sites on C (Redseam mine, bandit camps): those are
  dressing + enemy rows, no region row, no door.

## 1. The five artifacts every instance round carries (in order)

1. ART ANCHOR — law 1: view + name the concept piece(s) before any code.
   Pick from art-direction/concepts/ (36-piece set) or a committed new piece
   (generation BLOCKED as of 11-06; anchors from the existing set). Doc 64
   pre-maps each slot: H1/H2 = concept-06-siege-council, H3 = concept-08-
   veil-spire, H4/H5 = need a piece before build. The spec carries an
   "Art anchor" section with palette law (one accent per frame, no new
   accent colors anywhere else).
2. IO SPEC — section 2-8 of this recipe filled in for the claim (io/specs/
   cc-<round>-<name>-spec.md). Every tunable marked PROPOSED (Nicko tunes).
3. VALSPEC — Testerbot writes BEFORE Devbot starts (gate order). Pin file
   sha windows BY CONTENT ANCHOR, not line numbers (V-6 lesson: line pins
   drift). Baseline the valspec with the UI-class + key-guard law where
   relevant (QJR-3 lesson: pre-empt letter-vs-landed disputes).
4. PROBE SUITE — Devbot lands geometry + save checks:
   - scratch/cc-<round>/solve_geometry.py: CONFIG-ROW-PARSED (parse the
     region's live rows from CONFIG.js / region-defs.js — no hard-coded
     spec constants for the new rows), then assert EVERY clearance law of
     sec 6 below. Pattern exists: scratch/cc-ad1/solve_geometry.py,
     scratch/cc-ad2/solve_geometry.py (85 checks, ALL CONSTRAINTS: PASS).
   - scratch/cc-<round>/save_roundtrip.js: THREE-free node eval of
     CONFIG.js -> region-defs.js -> save.js with the stubbed game surface
     (pattern: scratch/cc-ad1/save_roundtrip.js). Asserts capture
     (regionId rides through), restore (region gate + teleport), negative
     control (unknown id falls back to activeId).
5. BUILD NOTE + REGISTRY FLIP — scratch/cc-<round>/build-note.md (files
   touched, deviations + adjudication, probe output digest, build sha) and
   the doc 64 slot-row move RESERVED -> LIVE in the SAME commit as the
   CONFIG change (slot law). GOALS.md tick + change log the same wake.

## 2. SPEC sec 2 — the CONFIG region row (shape on the nearest sibling)

Write the spec line "shape the row EXACTLY on CONFIG.<sibling>'s key set" +
the new values. Key set law (D/E/F shape; copy sibling key set verbatim,
change values only):

- id: one-word place names for pockets (D/E/F pattern: rot_den, veil_crypt,
  veil_galleries); hold_ prefix for surface holds, fort_ for fortified
  sites (naming rule doc 64). name: display string.
- center: { x, z } — geometry law: disc centers chain OUTWARD from the
  parent region along a -z or +z line (x preserved, z stepped), because the
  engine door math is Z-HARD-CODED (axis field is decorative: probe finding
  in AD2 sec 5; region-manager tickTransition/insideDoorWindow/
  holdAtLockedDoor read planeCoord as z only). Axis-x planes DO NOT EXIST
  as machinery today; do not spec one without a first-principles round.
- groundRadius: pocket interiors 20-34 (D 34, E 20, F 26); surface holds
  generous per Nicko (H1 wants r 120-160, doc 64). groundY: 0 flat disc —
  "flat disc (C hidden while <id> active: no z-fight)" is the one-active
  law. Heightfield pockets possible but NOT machined today (C is the only
  fbm region; wh-ground heightAt special-cases it) — a heightfield pocket
  would be its own round.
- groundColor/groundColor2: anchor palette. groundSeed: FRESH every round
  (floor pattern must differ from every sibling — E 1662061329 family vs D
  1662061218 vs C; do not reuse a landed seed).
- scatter: false for hand-authored pockets (excludes the round from the
  Round E scatter via CONFIG.scatter gate — whScatterPlan checks
  cfg.scatter === false). True only if the disc wants scatter dressing.
- spawn: inside the disc, behind the mouth plane, far edge convention
  (E spawn 10 m deep of the disc's far end; landing row = spawn row).
- gravityY: -22 every landed row (do not change).
- fogColor/fogDensity/ambientLightLevel: the darkness ladder. Law:
  fogDensity = sqrt(-ln 0.05) / d95_target. Landed: D 0.12 (d95 14.4 m),
  E 0.13 (12.75), F 0.145 (12.0). Each stratum one step darker via
  ambientLightLevel (D 0.06, E 0.07, F 0.055) + density bump. Pick the
  sibling and step by the anchor's mood.
- door: the full grammar (sec 4 law below), with:
  - planeZ = the mouth's outer face z (disc-local -radius-ish, matches the
    ring's gap lane);
  - doorX + doorHalfWidth sized to the ring gap's walkable lane (the gap
    lane must CLEAR the door window: landing crosses fully — D mouth
    4.6 m gap, halfWidth 3.0; F gap lane |x|<=2.2, halfWidth 2.4 window);
  - suspendDepthM 0, wallGapPadM 0, interactM 3.5 (landed family);
  - interactAt = the OTHER side's hook (parent-side position, PROBE it
    clear of parent dressing: >= 4.0 m from every parent collider);
  - land: BOTH directions, x NOT preserved across chains — land rows place
    the player inside the destination's play radius, on the destination's
    home side of the plane, >= 8 m inside the ring, faceX/faceZ = the
    landing view target;
  - fadeIn 0.3 / fadeOut 0.5 / exitFadeOut 0.8 (den family),
    text.prompt 'E - <verb> <place>'.
- enemies: count 0-2 for pockets (E 2 coven, F 2 ghoul wardens), clearance
  per sec 6. New enemy types are their own round (excluded surface).
- props: ring wall first (whWallA/B chord-circle, sec 3 law), then identity
  prop (ONE), then dressing. All assets from the EXISTING manifest list
  (whWallA/whWallB/stoneSarcophagus/stoneSteps/skullPile/graveMound/
  blightcap/mossBoulder/rubblePile + the rest of the manifest — never
  invent asset keys).
- lairs/rotLair: boss rows only when the round IS a lair (D pattern,
  homeRegionId + instance-after-enemy-rows note).

## 3. SPEC sec 3 — the parent-region edit (the aperture) + ring law

A pocket door needs a gap in SOMETHING. Two landed patterns, pick by parent:

- RING GAP (D, F): the pocket's own ring wall carries the mouth gap. Chord-
  circle law: N segments on r_disc_ring around center, segment angular
  positions from bearing (i + 0.5) * (360/N) deg, OMIT the segment under
  the mouth; per-row shape { asset: 'whWallA'|'whWallB' (alternate), x/z
  computed, rotY bearing+PI, scale: chord_m / 16.84 (raw ext X 1.899 ->
  world span), sy: 11.69 A / 11.55 B, sz: 2.40, y: -0.2, wall: 7 }.
  Colliders: region-manager whPropColliders writes p.wall circles r
  CFG.boundaryWall.collider.r (0.45) every <= 2 m along the row's local X —
  the probe rebuilds these exactly (sec 6). Probe MUST verify: zero ring
  colliders inside the gap window, full coverage on every other bearing,
  every prop >= 4.0 m raw from every ring collider.
- PARENT APERTURE (E->F pattern): erase EXACTLY ONE existing wall row from
  the parent's props (spec the row verbatim), append replacements (the
  mourner-pair law: identity-shaped dressing flanking the aperture) + keep
  every other parent row untouched. Spec asserts "diff shows N deletions,
  M additions, nothing else moved". Probe asserts the aperture lane stays
  walkable (no ring collider within 1.5 m of the lane x-window +-1.5) while
  the rest of the parent ring keeps every other collider.

## 4. SPEC sec 4 — region-defs registration + door wiring (canonical block)

Two lines + one push + two sides lines, NOTHING else in region-defs.js:

1. regions[CFG.<key>.id] = makeRegion(CFG.<key>, -1); — appended after the
   newest region's registration. The -1 is the plane-0 convention only
   (pockets lie on no plane-0 side; C0-7 law notes it for every new region).
2. var <X>D = CFG.<key>.door;
   connections.push({
     from: CFG.<parent>.id, to: CFG.<key>.id,
     axis: 'z', planeCoord: <X>D.planeZ, sides: {},
     door: {
       doorX: <X>D.doorX, doorHalfWidth: <X>D.doorHalfWidth,
       suspendDepthM: <X>D.suspendDepthM, wallGapPadM: <X>D.wallGapPadM,
       arch: null, gatedTo: null,
       walkFrom: CFG.<key>.id,
       interact: { from: CFG.<parent>.id, x: <X>D.interactAt.x,
                   z: <X>D.interactAt.z, radius: <X>D.interactM },
       land: <X>D.land
     }
   });
   connections[<n>].sides[CFG.<parent>.id] = -1;
   connections[<n>].sides[CFG.<key>.id] = 1;

Semantic law (copy into every spec, it is the #1 confusion point):
- walkFrom = the plane crossing exists ONLY in the named region (walk-back;
  in the parent the line runs through live terrain: no crossing, no clamp,
  no prewarm, no scatter clear there). The parent side enters by the
  interact E-hook (region-manager forceCross) at interactAt.
- sides table = which side of the plane each region occupies (D-symmetry:
  the FROM-side region's sign is +1 when the pocket sits at z <= planeZ —
  the landed rows are D +1/C -1 (outward -z), E +1/C -1, F +1/E -1; a
  +z-side pocket flips). Probe asserts land rows sit on their region's
  home side of planeCoord.
- gatedTo: 'veil'-style law ONLY on the B/C door (the 3-day dormant clock);
  every pocket chain carries gatedTo: null.
- No helper changes, no logic-file changes (the helper API —
  connectionBetween/insideDoorWindow/isMember/otherEnd/sideIn/connectionsOf/
  planeIn/sideOfPlane/mapPositionAcross — covers everything; doc 64 sec 1).

## 5. SPEC sec 5 — engine census (record-only findings; NO code changes)

Every recipe round states these as findings to note, NOT surfaces to touch:

- region-manager: one-active + neighbor PREWARM (CFG.preWarm.distance/
  hysteresis); per-region build/dispose; clamps; per-connection enemy
  clamp. Pocket chains inherit all of it free — that is WHY the recipe
  has no code sec.
- wh-ground: A/B/D/E/F read FLAT groundY discs; C is the only heightfield.
- save.js: additive blocks carry regionId (player P, camp K.respawn,
  world) behind validRegion() guards — any new id round-trips with NO
  edit; the probe proves it.
- daynight.js: D.constantPhases[areaId] branch = the always-dark sky rows.
  Add constantPhases.<id> ONLY when the pocket must be always-dark (D has
  it: hemiFillMult 1, exposureMult 0.75, stars 0.15; E/F ran without one —
  region fog/ambient sufficed; doc 64 notes this).
- scatter gate: CONFIG.scatter rows with scatter:false are excluded.
- game.js prompt chain: the door prompt rides conn.door.text.prompt through
  denDoorNear -> portalNear — zero game.js diff is the standard, and the
  spec's A-item says "game.js diff must be EMPTY".
- Region-manager spawn validator shape: props/enemies inside play radius,
  spawn clear of collider circles — the probe asserts it (validator is
  informational; the probe is the gate).

If a round would need to touch ANY of these files beyond CONFIG.js +
region-defs.js (+ daynight.js for a constantPhase row), it is NOT a
recipe instance — it is a machinery round and needs its own spec section
for the code change.

## 6. Probe constants — the universal clearance numbers

Every solve_geometry.py asserts (tolerances +-0.05 unless stated):

- spawn + both land rows inside groundRadius of center (with margin).
- enemies >= 8.0 m from spawn/land; >= 12.5 m from each other (floor
  accepted 12.4, probe tolerance +-0.15); >= 4.45 m walk-clear of the ring.
- props >= 4.0 m raw from every ring collider; >= 6.0 m from spawn/land;
  >= 5.0 m from every enemy; >= 4.0 m from each other.
- Ring: zero colliders in the door window (|x - doorX| <= doorHalfWidth at
  z = planeZ); every other bearing octant covered.
- Aperture parent edits: erased row verbatim; lane walkable (1.5 m);
  replacement rows on the sec 6 margins vs the remaining ring.
- conn sanity: from/to/axis/planeCoord/walkFrom/interact/land/sides all
  parsed live; land rows on home sides.
- Collider math for the probe: p.wall circles r 0.45 along the row's local
  X; whWallA/whWallB raw ext X 1.899; asset widths from measured footprints
  (copy the footprint table from scratch/cc-ad1/solve_geometry.py).

## 7. Acceptance-criteria skeleton (A-1..A-9, from AD1/AD2, reusable)

- A-1 CONFIG.<key> exists, full key set shaped on the sibling, groundSeed
  fresh, all values match spec (exact ids/keys; numerics +-0.05).
- A-2 parent edit exactly as spec'd (verbatim deletion count + additions;
  nothing else moved).
- A-3 region-defs: registration + conn row + sides table correct.
- A-4 game.js diff EMPTY; no unrelated diffs anywhere else.
- A-5 solve_geometry.py RE-RUN against landed rows: ALL CONSTRAINTS: PASS.
- A-6 build: python3 tools/build_v8.py exit 0 (newest-tool law: use the
  NEWEST build_vX in tools/ at build time); bundle marker count of the new
  region id >= 8; build determinism (rebuild = identical sha256).
- A-7 spawn validator shape (inside radius, collider-clear spawn).
- A-8 chain walkback: land rows inside play radius on home sides.
- A-9 surface discipline: no new enemy types, no new assets, no changes
  outside prototype/js/CONFIG.js, region-defs.js, (daynight.js ONLY if a
  constantPhase row is spec'd), the bundle, and scratch/cc-<round>/.
- NO-GIT clause in every dispatch: children never push; IO commits +
  pushes (identity CaptainPickard <pickard.nicko@gmail.com>), builds in
  the worktree, flips, verifies served bytes (sha + marker), moves the
  doc 64 slot row, ticks GOALS, journals.

Gate process lessons baked in (do not relearn):
- Dispatch context rides IN the brief file (one -p arg; no heredocs with
  & inside the terminal call — write a script file instead).
- delegate_task goal text must not contain <placeholders> or {braces}.
- A 420s TOOL timeout is not a child death: check the delegation manifest
  (/root/.hermes/profiles/io/cache/delegation/live/<id>/manifest.json,
  status/completed) before re-dispatching; NEVER overwrite a file a
  possibly-live child may own (wake-13 lesson). Children stay read-only in
  production writes (reports/probes only); IO reaps orphans post-timeout.
- Valspec pins sha windows by content anchor, not line number (V-6).
- Testerbot validates INDEPENDENTLY (fresh probe run, its own greps) and
  issues PASS/FAIL; IO re-verifies claims by grep/build before commit.

## 8. Worked example — H1 Lord's Hold (the claim sheet for the next round)

Slot H1 (doc 64): surface hold hub, generous footprint, anchor
concept-06-siege-council (viewed 11-06 wake 15: gold-on-obsidian war-hall,
brazier warmth on cold blue night, banners, war-table hub, arches +
buttresses, ONE accent = torch amber/gold; palette anchors: void 0x0A0E14,
midnight 0x1B2631, slate 0x2C3E50, stone 0x4A4A4A, accent amber 0xFFB347 /
gold 0xD4AF37 — hexes are the analysis reading, not landed CONFIG values;
the spec picks actual hexes from the anchor).

Template fill for H1 (starting points, all PROPOSED):

- id 'lords_hold' (hold_ prefix law). center: outward from C's south rim
  (the hold is the doc 48 endgame base; C center (0,-366), keep x 0 chain
  and step z; EXACT seat = probe-verified clear of C dressing on the
  chosen approach). groundRadius 140 (range 120-160).
- groundY 0 flat disc (hold layer 1); courtyard pockets later rounds
  (chained stratum = H2 garrison/armory off H1, E/F pattern).
- fog near-surface: surface night mood, NOT the subterranean ladder —
  fogDensity ~0.08 (d95 ~22 m, generous footprint reads), ambient 0.10.
  constantPhase row: NO (surface hold runs the day/night clock).
- door: the plane = an outer-wall gate gap on the -z face... geometry: H1's
  ring is a large curtain wall; spec N segments + gate gap with the sec 3
  ring law; interactAt on C-side at the approach road mouth; walkFrom
  lords_hold; halfWidth sized to a gate (4.0-5.0 window).
- dressing: war-table hub (stoneTable identity — if the manifest lacks a
  table-shaped asset, use the closest landed kit and note the gap in the
  build note; DO NOT invent asset keys), brazier-light accents via landed
  lair-style light grammar only if the round specs it, banners as
  graveMound/blightcap-free plain dressing (keep ONE accent: amber light).
- enemies: 0 (a hub, not a hunt) — garrison rows are H2's round.
- save: rides free (sec 5). doc 64: slot H1 row moves LIVE same commit
  with the landed seat numbers.
- Build order for the round: spec from this recipe (fill sec 2-6) ->
  Testerbot valspec -> Devbot build + probes -> verdict -> IO commit 1
  (code + doc 64 row + spec/valspec/verdict artifacts) -> build_v8 ->
  commit 2 (stamp) -> flip -> serve verify -> journal.

H1 is DELIBERATELY the proof-of-generality: first surface hold, first big
disc (r 140 vs F's 26), first non-dark constantPhase-free pocket, first
no-enemy region. If H1 lands through the recipe unchanged, H2-H6 are
stamp-ins; if it needs machinery, the deviation becomes the recipe's next
amendment BEFORE H2.

## 9. Recipe maintenance

- Any machinery discovered during a claim that the template lacks gets
  amended HERE first (version bump + what changed), then the claim runs.
- The probe constants (sec 6) are the tuned defaults; a slot MAY tighten
  (smaller margins), never loosen without a disclosed adjudication note.
- doc 64 stays the slot ledger; dev merge of feat/world-visuals ONLY on
  Nicko's explicit call (unchanged law; playtest debt currently 10+ rounds).
