# CC-AD2 SPEC — The Erased Galleries (doc 47 Veil strata V2, chained off veil_crypt)

Round: CC-AD2 · 2026-11-06 · Author: IO (gate step 1)
Branch/worktree: feat/world-visuals @ /tmp/wh-worldfeat · Build tool: tools/build_v8.py

Art anchor (art law): **art-direction/concepts/concept-08-veil-spire.png +
day-08-veil-spire.png** (the erased statue field — headless plinth figures on
heavy plinths, rotting red drape, blood-on-ash accent rule) and
**concept-05-night-ambush.png** (interior fog tiers). Interior frame
generation is BLOCKED this round (io image_gen provider openai-codex is dead:
expired 2026-07-17 ChatGPT-plan OAuth, no API key — open thread); this build
carries the 4 APPROVED anchors' language instead. Palette law for every new
row: obsidian/ash greys, bruised-purple shadow, ONE crimson accent =
blightcap caps. No new accent colors.

Doc anchors: docs/planning/47-altar-delves-gdd.md SECTION 2 strata V2 (THE
ERASED GALLERIES: "the debt's paperwork made stone", undead wardens of the
galleries, witch-fauna nesting in the erasures); docs/planning/19 erased
statue field (surface sibling); docs/planning/34 undead grammar (ghouls: no
dodge, no parry, relentless, zone denial); doc 62 region-shell law (own disc,
own fog/fill, door window, walkFrom semantics); CC-AD1 spec (the parent
round: crypt rows + conn shape).

PROPOSED, Nicko tunes: every coordinate, radius, light, and count is a tunable
seat, marked in comments.

## 1. What this round is

Two additions, one region chain:

A. **The west aisle (regionE edit, interior)** — the crypt gains its deeper
   sibling's entrance: ONE processional gap in its west ring wall (erase ONE
   existing whWall row, add ONE mourner pair AT the opening) + ONE new
   interact door hook (E-to-descend, same family as the landed crypt door).

B. **New region: CONFIG.regionF (id `veil_galleries`)** — THE ERASED
   GALLERIES: an own-disc flat pocket region chained off the crypt's west
   flank (axis-z planes only; engine plane math is z-hard-coded — probe
   finding, see sc 4). F is THE ERASED GALLERIES stratum: r 26 basalt
   pantheon-in-shadow, 2 ghouls (the galleries' undead wardens), erased-
   statue dressing, darker than the crypt by one step.

Gameplay law: F is reachable ONLY through the crypt (walk-back F->E by the
mouth plane; E->F by the E-hook). The 3-day dormant gate does NOT apply to
either door (the chain has no gatedTo rows).

## 2. New region: CONFIG.regionF (id `veil_galleries`)

Append AFTER the regionE block (never touching any pre-existing row;
all additions + one regionE row deletion, see §3). Shape the row EXACTLY on
CONFIG.regionE's key set, new values:

- id: 'veil_galleries'. name: "The Erased Galleries".
- center: { x: 0, z: -640 } — 44 m due west-ward of the crypt center along
  -z (the galleries sit under C's west rim band; the crypt's fiction keeps).
- groundRadius: 26 (crypt is 20; the galleries are one stratum wider — still
  a tight pocket).
- groundY: 0 (flat disc; C/E hidden while F active — one-active-region law).
- groundColor: 0x11131a (one step colder than the crypt's 0x121418),
  groundColor2: 0x16181f, groundSeed: 1662061329 (fresh — floor pattern must
  DIFFER from the crypt's; do not reuse 1662061219).
- scatter: false (hand rows only, same as crypt).
- spawn: { x: 0, z: -650 } (the landing row's galleries end, 10 m deep).
- gravityY: -22.
- fogColor: 0x0a0810 (same near-black purple family), fogDensity: 0.145
  (d95 ≈ 12.0 m; crypt 0.13), ambientLightLevel: 0.055 (crypt 0.07 — one
  step darker; "the galleries swallowed the light").
- door: shape EXACTLY on regionE.door:
  - planeZ: -640 (the galleries mouth plane, crypt-side z equivalent),
  - doorX: 0, doorHalfWidth: 2.2 (lane 4.4 m), suspendDepthM: 0,
    wallGapPadM: 0, interactM: 3.5,
  - interactAt: { x: -14.5, z: -596 } (E-side hook: the crypt's WEST aisle
    aperture — probe-verified clear of crypt dressing),
  - land: {
      veil_crypt:      { x: 0,   z: -604, faceX: 0, faceZ: -604 },
      veil_galleries:  { x: 0,   z: -650, faceX: 0, faceZ: -650 }
    } (into F = the landing row facing the galleries' far end; back into E =
    the crypt's landed spawn row),
  - fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8 (den family), text: { prompt:
    'E - Descend into the galleries' }.
- enemies: 2 ghoul rows, galleries-local computed to world:
  { type: 'ghoul', x: -6, z: -636 }, { type: 'ghoul', x: 6.5, z: -635.5 }
  (both >= 8.0 m from spawn, >= 12.5 m from each other, >= 4.45 m walk-clear
  of the ring — probe-verified numbers).
- props (append-only):
  - THE ERASED FIGURE (identity prop, ONE): mourningStatue at (7, -641),
    rotY 4.0, scale 1.0 — the headless plinth figure, "names once stood".
  - Erasure dressing: 2x skullPile at (-10, -630) and (-12, -645), 2x
    blightcap at (11, -632) and (10.5, -646) (the ONE crimson accent), 2x
    mossBoulder at (-9, -650) and (9, -650), 1x rubblePile at (-7, -641).
  - Ring wall: 8 whWallA/B rows on chord-circle r 22 around (0,-640),
    alternating asset per the crypt's A/B rhythm (A at odd indices, B at
    even), scale ≈ 7.35 (chord 16.84 m / segment), sy 11.69 A / 11.55 B,
    sz 2.40, y -0.2, wall: 7 — with segment angular positions from angle 0
    (east, x+) stepping (i + 0.5) · 45°, i = 0..7. Write the rows with the
    same per-row shape keys as regionE's whWall rows. THE GAP: segment 0
    (east, centered +x from center) is OMITTED — its slot at bearing 22.5°
    and 337.5° side-colliders must NOT be written; the gap lane is |x| <= 2.2
    at z = -640 (the mouth). Devbot probe MUST verify zero ring colliders in
    the gap window and full coverage on every other bearing (scratch/
    cc-ad2/solve_geometry.py re-run with F rows live).
  - Every prop >= 4.0 m from every ring collider (raw), >= 6.0 m from
    spawn, >= 5.0 m from both ghouls, >= 4.0 m from each other (PROBE).

## 3. regionE edit (the west aisle)

- DELETE exactly ONE row from CONFIG.regionE.props: the existing whWallB at
  (-8.3, -612.0) — the crypt ring's west-south arch piece — replaced by the
  mourner pair (below). Nothing else in regionE.props changes.
- APPEND to CONFIG.regionE.props (after the rubblePile row):
  - { asset: 'mourningStatue', x: -15.5, z: -593, rotY: 2.6, scale: 0.9 }
  - { asset: 'rubblePile',     x: -15.0, z: -599.5, rotY: 1.2, scale: 1.1 }
  (the kneeling pair flanking the west aperture).
- APPEND the west-aperture collider law: the deleted whWallB's slot is the
  aperture; probe verifies the aperture lane stays walkable (no ring
  collider within 1.5 m of the lane x in [-14.5+-1.5] at z in [-596+-1.5])
  while the rest of the crypt ring keeps every other collider.
- regionE.enemies, regionE.door, all other rows: UNCHANGED.

## 4. region-defs.js registration + door wiring

- regions[CFG.regionF.id] = makeRegion(CFG.regionF, -1); appended after the
  regionE registration line (one new line, nothing modified).
- New connection: connections.push a row shaped EXACTLY on the landed CC-AD1
  E-crypt row (region-defs connections[3]): from CFG.regionE.id, to
  CFG.regionF.id, axis 'z', planeCoord = CFG.regionF.door.planeZ, sides {},
  door { doorX, doorHalfWidth, suspendDepthM, wallGapPadM, arch: null,
  gatedTo: null, walkFrom: CFG.regionF.id, interact: { from:
  CFG.regionE.id, x: interactAt.x, z: interactAt.z, radius: interactM },
  land: CFG.regionF.door.land }; then
  connections[4].sides[CFG.regionE.id] = -1;
  connections[4].sides[CFG.regionF.id] = 1; (E occupies z > planeCoord side
  on this conn's sides table, F z <=). Sides table + sides assignment lines
  ONLY; no helper changes, no logic-file changes.
- D-symmetry law: F occupies z <= planeZ (like E on conn[3] with E-side -1
  / F-side +1 flipped for this chain: E is the FROM region).

## 5. game.js + region-defs helper census (NO changes this round)

Probe findings to record in the build note (NOT to change):
- region-manager tickTransition/insideDoorWindow/holdAtLockedDoor read
  planeCoord as Z only (axis field decorative). The E->F chain reuses the
  axis-z walk-back pattern; the west entrance is an interact hook (no plane
  in E), so no axis work exists.
- game.js prompt chain: the F door prompt rides conn.door.text.prompt
  (denDoorNear -> portalNear loop covers it free).
- CONFIG.scatter: regionF's scatter:false row excludes it from the Round E
  scatter (whScatterPlan cfg.scatter === false gate).
- RegionManager spawn validator (validateSpawnSides + report paths) runs per
  region; regionF's rows must satisfy it (props/enemies inside play radius,
  spawn clear of collider circles) — Devbot probe asserts this shape.

## 6. Build + bundle

- Build with tools/build_v8.py IN THE WORKTREE (build-tool drift law: v8 is
  current; do not invent v9). Build AFTER the CONFIG + defs edits and the
  probe PASS.
- Bundle marker: grep -c 'veil_galleries' prototype/builds/v8-playable.html
  must be >= 8 (the valspec sets the exact bar).
- NO-GIT: Devbot and Testerbot never push; IO commits+pushes after the gate.

## 7. Acceptance criteria (Testerbot validates against these)

A-1 CONFIG.regionF exists with the full key set shaped on regionE; groundSeed
    differs; all values match §2 (tolerances: exact for ids/keys; numerics
    within 0.05 of the spec numbers).
A-2 The ONE regionE.props whWallB row (-8.3, -612.0) is deleted; the mourner
    pair rows exist at (-15.5, -593) / (-15.0, -599.5); NO other regionE
    prop row moved or changed (diff must show 1 deletion, 2 additions).
A-3 region-defs: regionF registered (makeRegion, side -1); connections[4]
    exists with walkFrom = veil_galleries, interact.from = veil_crypt, the
    land rows of §2, sides E=-1 / F=+1.
A-4 game.js has NO unrelated diffs (expect 0 lines changed there; the
    prompt chain needs none).
A-5 scratch/cc-ad2/solve_geometry.py RE-RUN against the landed rows returns
    ALL CONSTRAINTS: PASS (Devbot updates the probe's F constants from the
    CONFIG rows — parsing them live like the AD1 probe does — and the
    E-side sections keep their landed-regionE numbers).
A-6 Build: python3 tools/build_v8.py exit 0; bundle marker 'veil_galleries'
    count >= 8; build reproducibility (rebuild = identical sha256, Testerbot
    law).
A-7 Spawn validator shape: regionF props/enemies inside play radius
    (r 26 - margin); spawn clear of all F collider circles AND of the mourner
    pair colliders in E; ghouls holdable (home-side margins respected by the
    engine's per-connection enemy clamp).
A-8 Chain walkback: land rows place the player inside the destination's
    play radius on the home side of each door (E land = crypt spawn row;
    F land = (0,-650) which is z < planeZ -640 - 2.4, i.e. on F's home
    side, and >= 8 m from the gap plane inside F's own ring radius).
A-9 No new enemy types, no new assets, no changes outside prototype/js/
    CONFIG.js, region-defs.js, the bundle, scratch/cc-ad2/. game.js diff
    must be EMPTY (A-4).

## 8. Excluded surfaces (do not touch)

- No lighting/constantPhase code (region rows only).
- No witch-fauna nesting encounters (V2's signature tier — later round).
- No doc 47 edits (layout stays PROPOSED in the GDD).
- No image generation (provider dead; open thread).
- No dev-branch merge, no main pushes (feat/world-visuals only; merge
  feat->dev ONLY on Nicko's explicit call).
