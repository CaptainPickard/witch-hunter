# CC-AD1 SPEC — Veil Spire Crypt Mini-Delve (doc 47 strata V1 + doc 62 shell law)

Round: CC-AD1 · 2026-11-06 · Author: IO (gate step 1)
Branch/worktree: feat/world-visuals @ /tmp/wh-worldfeat · Build tool: tools/build_v8.py
Art anchor (palette/mood law): **art-direction/concepts/concept-08-veil-spire.png**
(+ concepts-web/char-09-coven-wizard.png for the occupants' accents: charcoal/deep-teal
robes, ONE cyan cast-glow accent on coven bolts per CC-EC1; the crypt itself carries ONE
crimson ember accent per the spire's lava-fissure language. Everything else: basalt
charcoal, bruised-purple gloom, under-lit and atmospheric.)

## 1. What this round is

A single bounded interior pocket region — THE OLD THRONE'S CRYPT (doc 47, Veil strata
V1, PROPOSED layout reading): a hand-authored mini-delve reachable from the Forest of
the Old King via the north-rim notch, following the proven CC-C8 den pattern (regionD).
It gives the freshly-landed Coven Acolyte (CC-EC1, magicDefense hook LIVE) an interior
arena where its cast loop matters more than chase radius, and it seeds the altar-delve
direction with real code and a real place.

Doc anchors: docs/planning/47-altar-delves-gdd.md SECTION 2 strata V1 (crypt of the
old throne: dignified dead, undead elders among them, broken altar stones above);
docs/planning/62 region-shell law (own disc, own fog/fill/constantPhase, door window,
walkFrom semantics); CC-EC1 build note (coven behavior contract: keep-distance
override stays ON INSIDE the crypt).

PROPOSED, Nicko tunes: every coordinate, radius, light, and loot number is a tunable
seat, marked as such in comments.

## 2. New region: CONFIG.regionE (id `veil_crypt`)

Shape the row EXACTLY on CONFIG.regionD's (the den): same key set, new values. Append
it as a NEW sibling block after regionD (never touching any pre-existing row; all
additions only). Contents:

- id: 'veil_crypt'. name: "The Old Throne's Crypt".
- center: { x: 0, z: -596 } — the north notch's mouth coordinate (the notch blockers
  and keepOut rows already sit there); the crypt disc lands UNDER the forest floor,
  conceptually beneath the spire-base hill the notch cuts into.
- groundRadius: 20 (den is 34; the crypt is a tighter pocket — claustrophobic per the
  art anchor's "digestive system" guidance. PROPOSED, Nicko tunes).
- groundY: 0 (flat disc; C is hidden while E is active — same law as the den).
- groundColor: 0x121418 (basalt charcoal), groundColor2: 0x171a20 (slate-purple
  shadow secondary), groundSeed: 1662061219.
- scatter: false (hand rows only, like the den).
- spawn: the landing row's crypt end (see §3).
- gravityY: -22 (den's value).
- fogColor: 0x0a0810 (bruised near-black purple), fogDensity: 0.13 (d95 ≈ 13.3 m —
  the far wall is a black thought; PROPOSED, Nicko tunes).
- ambientLightLevel: 0.07.
- door: shape EXACTLY on regionD.door: planeZ at the crypt side of the notch
  (crypt-local z -16 = world z -612 — PROPOSED), doorX 0, doorHalfWidth 2.4 (narrower
  than the den's 3.0 — the tomb mouth), suspendDepthM 0, wallGapPadM 0, interactM 3.5.
  interactAt: { x: 0, z: -596 } (C-side: the notch mouth itself — E there enters the
  crypt). land: {
    forest_of_the_old_king: { x: 0, z: -596, faceX: 0, faceZ: -366 },
    veil_crypt: { x: 0, z: -604, faceX: 0, faceZ: -604 }
  } — landing INTO the crypt puts the player at crypt-local (0, -8) facing the
  altar-side; walking to the mouth plane crosses back out. fadeIn 0.3, fadeOut 0.5,
  exitFadeOut 0.8, text: { prompt: 'E - Descend into the crypt' }.
- enemies: 2 coven rows (type 'coven'), placed clear of the spawn and the altar,
  crypt-local: (5, 4) and (-6, 6) (world (5, -592) / (-6, -594) — world x here equals
  crypt-local x since center.x = 0; crypt-local z = world z + 596). Compute and keep
  >= 8.0 m from spawn and door windows (the coven keep-distance override needs room;
  the crypt is r 20, so there is room).
- props: append-only crypt interior:
  - The ALBETAR — altar-side feature (the crypt's identity + crimson accent, one
    prop only): 1x stoneSarcophagus + 2x stoneSteps stacked as an altar plinth at
    crypt-local (0, 6) (world z -590), rotY facing the door; the ONE crimson accent
    is a single small firebolt-shaped ember light... NO — keep it asset-only v1: the
    accent is the blightcap pair's faint red caps + the altar stones (no new light
    code this round; light code is §5's excluded surface).
  - Ring wall: 8 whWallA/whWallB segments (crypt r ~17-18 chord ring, sy ~9, sz
    2.4, wall: 8 colliders " every 2 m — the crypt is CLOSED except the door gap at
    crypt-local z -16, open-arch pattern like the den's mouth gap). Scale rows from
    the den's (r 24, 10 segments) down to r 18 / 8 segments; write the ring with
    the SAME per-row shape as regionD's whWall rows (asset, x, z, rotY, scale, sy,
    sz, y: -0.2, wall: 8).
  - Dignified dead dressing: 2x skullPile, 4x blightcap, 2x mossBoulder spread clear
    of the door lane and the ring (min 4 m from every wall row, min 6 m from spawn,
    min 5 m from each coven start — so nobody spawns inside a collider or in a
    caster's face).
  - Optional 1x rubblePile near the door gap flank (tomb-collapse language).

## 3. region-defs.js registration + door wiring

- region-defs: `regions[CFG.regionE.id] = makeRegion(CFG.regionE, -1);` appended
  after the regionD registration line (one new line, nothing modified).
- New connection: connections[3] = { from: CFG.regionC.id, to: CFG.regionE.id }
  shaped EXACTLY on the CC-C8 connection row (region-defs connections[2] in source):
  axis 'z', planeCoord = CFG.regionE.door.planeZ, sides {}, door { doorX,
  doorHalfWidth, suspendDepthM, wallGapPadM, arch: null, gatedTo: null, walkFrom:
  CFG.regionE.id, interact: { from: regionC, x: interactAt.x, z: interactAt.z,
  radius: interactM }, land: CFG.regionE.door.land }; then
  `connections[3].sides[CFG.regionC.id] = -1; connections[3].sides[CFG.regionE.id] = 1;`
- D-symmetry law: regionE occupies z <= planeZ (like D: z >= planeZ is the region
  side). Verify the sideOfBoundary arithmetic in the door-plane logic tests holds
  for both sides (the plane only exists walkFrom the crypt for the walk-back).

## 4. game.js generic-ization (the only logic change beyond CONFIG/defs wiring)

Three regionD-keyed reads become per-region (mechanical, addition-shaped):

1. tryDenDoor (game.js ~1907): `var D = CFG.regionD.door;` becomes
   `var R = window.WH_REGION_DEFS.regions[game.regionManager.logic.activeId === CFG.regionD.id ? CFG.regionD.id : CFG.regionE.id]` — NO, simpler and byte-law-compliant:
   read the conn from denDoorNear() itself: `var conn = denDoorNear(); var D = conn
   && conn.door;` and use D.* throughout that block (conn is already the portalNear
   result; its .door carries every setting; door.text stays per-region via
   conn.door.text — note: CONFIG region rows each carry their own `text` under
   door, so no table change is needed).
2. The E-prompt chain (game.js ~2219): `text = CFG.regionD.door.text.prompt;` becomes
   prompt-from-conn: capture conn = denDoorNear() first, then `text = conn.door.text.prompt;`.
3. The walk-back exitFadeOut (game.js ~3071): `startDenFade(0, CFG.regionD.door.exitFadeOut, null)` becomes
   `startDenFade(0, tr.conn.door.exitFadeOut, null)` (tr.conn is checked non-null on
   the line above — reuse it).

Byte law: no deletion-driven rewrites; each change is a small local substitution the
diff shows. If any of the three reads a CONFIG row that does NOT carry the needed key,
fail the build and report — never silently default.

## 5. EXCLUDED surfaces (do not touch this round)

- light.js, daynight.js constantPhases (the crypt runs on its region fog/fill row
  v1 — a bespoke constantPhase row `veil_crypt` MAY be appended IF trivial; flag it
  in the build note; do not modify the existing rot_den row), sky pools, weather.
- player.js, save.js, camp.js, chest.js, npc.js (save machinery is generic via
  region-defs.validRegion — no edit needed; camp is not built in the crypt).
- The altar is dressing-only v1: no interact, no loot, no quest hook (the delve's
  final act and reward are a LATER round; keep this round bounded).
- No new assets, no new GLBs, no art generation (all dressing assets exist in the
  manifest already — list in the build note which keys were used).
- No harness runs, no headless browser smoke tests (Nicko's playtest is the bar).

## 6. Acceptance criteria (Testerbot validates against these; write the valspec from
them BEFORE Devbot starts)

1. Build: `python3 tools/build_v8.py` exits 0 IN THE WORKTREE; produces
   prototype/builds/v8-playable.html with `grep -c veil_crypt` >= 8 (new marker).
2. CONFIG additionality: `git diff` on CONFIG.js shows ONLY added lines (no row
   deleted or modified anywhere in the file); regionE block appended after regionD;
   enemy rows for regionE carry type 'coven'.
3. region-defs additionality: only the makeRegion line + connections[3] block +
   two sides lines added; connectionBetween('forest_of_the_old_king','veil_crypt')
   resolves (node smoke: node -e test on logic helpers THREE-free).
4. game.js: the three generic-izations compile (node --check all 5 touched files)
   and the E-prompt/exitFade paths read per-conn values, not CFG.regionD.
5. Geometry: every regionE prop/enemy row passes a clearance check (new
   scratch/cc-ad1/clearance.py, shape on scratch/cc-ec1/clearance.py): every wall
   row's wall-collider ring closes EXCEPT the door gap; spawn/land rows inside r 20;
   covens >= 8.0 m from spawn, >= 8.0 m from each other (two independent casters,
   no stacking), >= 4.0 m from every wall collider; props >= 4.0 m from walls,
   >= 6.0 m from spawn, >= 5.0 m from covens.
6. Save safety: validRegion('veil_crypt') true via region-defs; a save taken
   INSIDE the crypt (regionId veil_crypt) round-trips (the save.js machinery is
   generic — validate via node --check + logic test with a stubbed profile, no
   browser).
7. Serve + flip: release flip lands (IO post-gate step), curl 200 on
   http://172.16.5.1:8793/current/prototype/builds/v8-playable.html, marker grep on
   SERVED bytes shows veil_crypt count >= 8.
8. Deviations: any row that cannot clear (geometry), any missing manifest key, or
   any behavior deviation gets a numbered ED-n entry in the build note the way
   CC-EC1 did — never silently.

## 7. Explicit gate law for the children

- Devbot/Testerbot: NO-GIT clause — never commit, never push. Produce code in the
  worktree + reports; IO is the sole committer.
- No harness runs, no headless browser smoke tests. node --check, grep, python
  clearance scripts, and logic-level node smoke tests are the toolbox.
- Children inherit io profile; degraded-provider law: if a child transport dies
  with work landed, report and stop; 2 deaths = IO lands inline with disclosure
  (CC-EC1 precedent).
