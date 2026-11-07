# CC-H1 SPEC — Lord's Hold (doc 64 slot H1 claim; doc 66 recipe instance sec 2-8)

Round: CC-H1 · 2026-11-07 · Author: IO (gate step 1)
Branch/worktree: feat/world-visuals @ /tmp/wh-worldfeat · Build tool: tools/build_v8.py
(newest-tool law: re-check tools/ for build_vX newer than v8 at build time; if a newer
exists use it and say so in the build note)
Art anchor (palette/mood law): **art-direction/concepts/concept-06-siege-council.png**
(IO re-viewed 2026-11-07 wake 16: brazier warmth on cold-slate night, banners, war-table
hub, gothic arches, overwhelming scale — gold-on-obsidian). Palette anchors for this
round (analysis readings, translated into landed CONFIG hexes): stone 0x8a8f96-family
cold slate, void shadows, ONE warm accent = amber/gold. Everything else stays muted;
NO crimson in this region (crimson is the Veil stratum's accent per doc 47 V3).

## 1. What this round is

The FIRST surface hold hub — proof-of-generality of the doc 66 recipe: first big disc
(groundRadius 126 vs F's 26), first constantPhase-free daylight-capable pocket, first
zero-enemy region. Reached from the Forest of the Old King along the north road: an E
hook on C's north road landing band crosses C -> H1; H1's south curtain-wall gate is the
walk-back plane. This round is the SHELL + HUB only: keep courtyard, war-table hub,
brazier light sockets, banner rows, gate arch, save-hook spot. Garrison/armory layers
(H2) and any NPC/quest wiring are LATER rounds (kept bounded; doc 64's slot law).

Doc anchors: docs/planning/66-instanced-region-recipe.md secs 2-8 (the template + H1
claim sheet); docs/planning/64-region-registry.md H1 row (LIVE-on-award law: moves in
THIS round's commit); docs/planning/48-endgame-gdd.md (the hold as endgame base reading
only — no endgame content claim this round); CC-AD1/AD2 spec pair (the sibling shape).

PROPOSED, Nicko tunes: every coordinate, radius, light, and prop number is a seat.

## 2. New region: CONFIG.regionG (id `lords_hold`)

Shape the row EXACTLY on CONFIG.regionF's (the galleries): same key set, new values.
Append it as a NEW sibling block after regionF (never touching any pre-existing row;
all additions only). Exact contents:

- id: 'lords_hold'. name: "Lord's Hold".
- center: { x: 0, z: -822 } — the hold disc sits fully OUTSIDE C's world footprint
  (C's disc spans to z -646; the hold's south edge z -696 leaves a 50 m gap; H1 is a
  FLAT disc with NO terrain row, so its ground has zero world-coords overlap — the
  one-active-region law hides C while H1 is active). Seat probe: scratch/cc-h1/seat_scan.py.
  (AMENDMENT C, IO correction 2026-11-07: the claim sheet's "first pick south rim"
  phrasing in doc 66 sec 8 was internally inconsistent — the x 0 road chain runs
  NORTH to notch (0, -596), so the hold seats NORTH of C, fully outside C's
  z -646 edge, exactly as this section seats it. The claim sheet's "north road
  chain" text governs; registry row updated in the close-out commit.)
- groundRadius: 126 (the claim sheet's r 120-160, first pick 126; playRadius 124.5).
- groundY: 0 (flat disc; C hidden while H1 is active — no z-fight).
- groundColor: 0x2f3339 (cold stone slate), groundColor2: 0x26292e (shadow secondary),
  groundSeed: 1662061440 (FRESH — must differ from every landed 1662061xxx seed).
- scatter: false (hand rows only — the hold yard is deliberately open; scatter would
  seed trees into the courtyard).
- spawn: { x: 0, z: -711 } (just inside the south gate; a death without a camp lands
  inside the hold, 11 m past the walk-back plane).
- gravityY: -22 (every landed region's value).
- fogColor: 0x8a8f96 (cold slate-blue night haze), fogDensity: 0.08 (d95 ≈ 21.6 m —
  the generous footprint READS across the yard; NOT the subterranean ladder. PROPOSED).
- ambientLightLevel: 0.10 (the hold runs the shared day/night clock — NO constantPhase
  row; doc 66 sec 2: surface hold law. The night's look = the shared sky + this fill).
- door: shape EXACTLY on regionF.door's key set:
  - planeZ: -700 (the gate plane, 4 m inside the disc's south edge z -696 — walk-out
    law; the plane lives ONLY in the hold: walkFrom lords_hold).
  - doorX: 0, doorHalfWidth: 4.5 (the gate window — claim sheet's 4.0-5.0).
  - suspendDepthM: 0, wallGapPadM: 0, interactM: 3.5.
  - interactAt: { x: 5.0, z: -500 } (C side: ON the north road at its landing band,
    probe-cleared: every C prop row >= 6.0 m away, 96.1 m clear of the crypt's own
    C-side hook, 96.1 m clear of the notch mouth (exclusion 26), standable inside C's
    playable disc (rC 134.1) — see seat_scan.py checks 1-4).
  - land: {
      forest_of_the_old_king: { x: 5, z: -500, faceX: 5, faceZ: -488 },
      lords_hold: { x: 0, z: -711, faceX: 0, faceZ: -802 }
    } (x is NOT preserved per the D/E/F law: the landing INTO the hold is the spawn
    row; the landing back onto C faces up the road toward the hold gate).
  - fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8 (the landed door fades, every row).
  - text: { prompt: 'E - Enter Lord\'s Hold' }.
- enemies: [] (zero rows — a hub, not a hunt; the garrison lives in H2's round).
- props (append-only hold interior; every row >= 4.0 m raw of the ring colliders,
  >= 6.0 m from spawn, >= 4.0 m mutual — seat_scan.py verified the hub cluster at
  11.3 m mutual, gate-lane clear 3.91; Devbot re-probes with clearance.py):
  1. THE CURTAIN WALL: 89 whWallA/whWallB segments (chord 8.79 m at scale 4.63, wall
     12 colliders ~ every 2 m) on the landed cadence, the gap at the SOUTH face
     (segment whose angular CENTER bearing is 90 deg OMITTED — the walk-in window
     |x| <= 4.5 at z -700). Rows EXACTLY as scratch/cc-h1/seat_scan_output.txt prints
     them (x, z, rotY, scale 4.63, sy 11.69 A / 11.55 B, sz 2.40, y -0.2, wall 12) —
     A/B alternate by index parity.
  2. THE WAR-TABLE HUB (the hold's identity; probe: hub (0, -782) = 82 m up the lane
     from the gate): 1x stoneSteps scale 1.4 as the dais plinth at (0, -780) — the
     table's stand (no table-shaped asset in the manifest: the gap is RECORDED in the
     build note per doc 66 sec 8; the dais + banners carry the tableau v1).
  3. 4x banditCampfire braziers (lightSockets.b3Gate-family sockets: lightSockets
     banditCampfire row exists — heightFraction 0.55, intensity 3.2 = the amber accent)
     at the hub square (±5.66, -776.34) / (±5.66, -787.66) — 8 m from the hub, 11.3 m
     mutual. THE ONE WARM ACCENT (4 sockets, one amber family).
  4. Banner dressing on the gate approach: 6x okFenceStonewall scale 1.2 as low
     parapet walls flanking the lane (±6.5 / ±13.5 at z -702/-704/-706 alternating
     sides — clear of the 4.5 m window).
  5. Barracks corner: 3x whTent scale 1.0 at (38, -796), (44, -802), (32, -804)
     (>= 4 m mutual, >= 30 m off the lane).
  6. Chapel corner: 1x churchArchway scale 2.2 at (-40, -800) facing the yard
     (rotY PI) + 2x churchCornerButtress scale 2.0 flanking at (-49, -804),
     (-49, -796).
  7. Yard dressing: 4x mossBoulder scale 1.5-2.2 at (20, -830), (-22, -826), (52, -842),
     (-58, -838); 2x rubblePile scale 1.1 at (12, -724), (-16, -736); 1x lanternPost
     scale 2.535 at (2.5, -706) (the gate's light socket, inside the lane's outer edge
     x window? — NO: at x 2.5 the post is 2.5 m off centerline, inside the window's
     4.5 m: SET x 6.5 (probe re-checks) — the gate lane stays clear).
- nodes: [] (none this round).

  **AMENDMENT B (IO clarification, applies before the build):** warm socket
  count is FIVE, not four: the 4 braziers (banditCampfire, intensity 3.2 each)
  PLUS the gate lanternPost row 7 (lightSockets.lanternPost exists, intensity
  9.0). All five are the ONE amber/gold warm family — the art law is one warm
  FAMILY (no crimson, no second accent color), not one socket count. Testerbot
  asserts: zero non-warm-family light rows in regionG props + exactly one warm
  family across the 5 sockets.

## 3. region-defs.js registration + door wiring (canonical sec 4 block, verbatim keys)

- `regions[CFG.regionG.id] = makeRegion(CFG.regionG, -1);` appended after the regionF
  registration line (one new line, nothing modified).
- New connection (connections[5]): shaped EXACTLY on the CC-AD2 connections[4] row:

      var GD = CFG.regionG.door;
      connections.push({
        from: CFG.regionF.id,   // WRONG — SEE AMENDMENT A BELOW
        to: CFG.regionG.id,
        axis: 'z',
        planeCoord: GD.planeZ,
        sides: {},
        door: {
          doorX: GD.doorX,
          doorHalfWidth: GD.doorHalfWidth,
          suspendDepthM: GD.suspendDepthM,
          wallGapPadM: GD.wallGapPadM,
          arch: null,
          gatedTo: null,
          walkFrom: CFG.regionG.id,
          interact: { from: CFG.regionC.id, x: GD.interactAt.x, z: GD.interactAt.z, radius: GD.interactM },
          land: GD.land
        }
      });

  **AMENDMENT A (IO correction, applies before the build):** `from` = CFG.regionC.id,
  NOT regionF — H1 hangs off C's north road, NOT off the galleries chain. The
  canonical block is otherwise exact. The comment line on the connection row cites
  CC-H1 and the seat probe path.
- Sides table (D-symmetry, the E-conn shape): the hold occupies z <= planeZ (-822 <
  -700), C occupies z > planeZ. Therefore:

      connections[5].sides[CFG.regionC.id] = -1;
      connections[5].sides[CFG.regionG.id] = 1;

  (mirrors the landed conn[3] crypt shape exactly: C -1, new pocket +1.)
- NOTE the sides-flip nuance vs conn[4]: F/E flipped because F's CHAIN runs from E
  (E is the from); here C is the from AND sits at z > planeZ, so the row is IDENTICAL
  to conn[3] (C -1, pocket +1). The probe asserts both land rows on home sides:
  land.lords_hold z -711 <= planeZ -700 (home side), land.forest_of_the_old_king
  z -500 > -700 (home side). NO change to any existing connections row. No helper
  changes, no logic-file changes (game.js diff must be EMPTY — the prompt/prompt
  chain + forceCross + land-row machinery is conn-carried since CC-C8/AD1; the exit
  fade rides tr.conn.door.exitFadeOut landed in AD1).

## 4. Engine census (record-only findings; NO code changes — doc 66 sec 5 verbatim)

Re-verified this wake before writing the spec (grep + read, files not touched):
- region-manager: tickTransition walks connectionsOf(activeId).filter(planeIn) — C
  gains a SECOND connection automatically (its first); prewarm chooses the NEAREST
  plane so C's door band near the crypt hook stays crypt-only until the player walks
  the north band; per-region clamp: `reg.center` path clamps H1 to r 124.5 (radial,
  center-carried) with NO code change; one-active law hides C while H1 is active.
- wh-ground: `regionCfg` sweep = every CONFIG top-level row with id + terrain.enabled
  — H1 carries NO terrain row, so WH_GROUND.has('lords_hold') false; H1's props seat
  on groundY 0 (whGroundFeed returns 0); C is untouched.
- save.js validRegion: regions[lords_hold] exists after makeRegion — additive blocks
  round-trip with NO edit (V-probe proves it the AD1 way).
- daynight.js: no constantPhases lords_hold row — applyRegionLighting reads the
  region's fogColor/fogDensity/ambientLightLevel (0.10) directly; the shared clock's
  night rows own the sky. SkyPool.setArea('lords_hold') retargets the shared pool —
  the panos show (surface law; NO code path needed: constantRow(areaId) || null only
  branches when a row EXISTS).
- scatter gate: scatter:false excludes H1 from whScatterPlan (same as D/E/F).
- spawn validator: validateSpawns covers A/B only (the landed shape) — H1's checks
  ride the probe (informational census; the probe is the gate — the record-only law).
- game.js prompt chain + exit fade: conn-carried (denDoorNear -> portalNear; the
  land rows + exitFadeOut on the crossed conn) — ZERO game.js diff (A-4).

## 5. EXCLUDED surfaces (do not touch this round)

- daynight.js constantPhases (surface law: NO row), light.js, player.js, enemy.js.
- save.js, camp.js, chest.js, npc.js (no camp/NPC wiring this round; the hold's
  save hook is the FREE save ride: a camp build inside H1 waits for H2).
- No new assets, no new GLBs, no art generation this round (the manifest kit covers
  every row; a bespoke hold-kit GLB set is a LATER art round if Nicko wants it).
- No war-table interact, no quest hooks, no HUD copy (the yard is dressing v1).
- No harness runs, no headless browser smoke tests (Nicko's playtest is the bar).
- The region name string "Lord's Hold" carries an ESCAPED apostrophe in the JS string
  (name: "Lord's Hold" double-quoted exactly as landed rows do — verify the exact
  quoting parses; node --check is the proof).

## 6. Acceptance criteria (Testerbot validates against these; write the valspec
## from them BEFORE Devbot starts)

1. Build: `python3 tools/build_v8.py` exits 0 IN THE WORKTREE; produces
   prototype/builds/v8-playable.html with `grep -c lords_hold` >= 8 on the BUNDLE.
2. CONFIG additionality: `git diff` on CONFIG.js shows ONLY added lines (no row
   deleted or modified); regionG appended after regionF; regionG carries NO enemies
   rows and NO terrain row.
3. region-defs additionality: only the makeRegion line + connections[5] block + two
   sides lines added; connectionBetween('forest_of_the_old_king','lords_hold')
   resolves; sides table C -1 / lords_hold +1 (node logic test, THREE-free).
4. game.js diff EMPTY; no unrelated diffs anywhere else (A-4/A-9).
5. Geometry: scratch/cc-h1/clearance.py (Devbot writes it, shape on scratch/cc-ad2/
   solve_geometry.py) re-run against the LANDED rows parses them live: every wall
   row's collider ring closes EXCEPT the door window; 89 wall rows / 1068 colliders;
   spawn + both land rows inside r 126 of center (0,-822); hub cluster clearances
   per spec sec 2 margins; door-lane window empty of colliders; octant coverage
   outside the gap arc ALL CONSTRAINTS PASS.
6. Save safety: validRegion('lords_hold') true; a save captured with activeId
   lords_hold round-trips (node logic test with a stubbed profile, the AD1
   save_roundtrip.js pattern — THREE-free, no browser).
7. Serve + flip (IO post-gate): curl 200 on
   http://172.16.5.1:8793/current/prototype/builds/v8-playable.html; marker grep on
   SERVED bytes shows lords_hold count >= 8.
8. Doc 64 slot row: the H1 row moves from RESERVED to LIVE in THIS round's commit
   with the landed seat numbers (the registry diff is the phase ledger).
9. Deviations: any row that cannot clear, any missing manifest key, any behavior
   deviation gets a numbered ED-n entry (never silently).

## 7. Explicit gate law for the children

- Devbot/Testerbot: NO-GIT clause — never commit, never push, never amend. Code in
  the worktree + reports only; IO is the sole committer (identity CaptainPickard
  pickard.nicko@gmail.com — children never set it).
- No harness runs, no headless browser smoke tests. node --check, grep, python
  clearance scripts, logic-level node smoke tests: the toolbox.
- Children inherit the io profile; degraded-provider law: provider stall with work
  landed = report and stop; 2 deaths = IO lands inline with disclosure.
- Dispatch briefs ride as FILES (one -p arg reading the brief path; no heredocs with
  & inside the terminal call; delegate goal text carries no <placeholders> or
  {braces}).
- A 420 s tool timeout is NOT a child death: read the delegation manifest
  (/root/.hermes/profiles/io/cache/delegation/live/<id>/manifest.json status/completed)
  before re-dispatching; never overwrite a file a possibly-live child may own.
