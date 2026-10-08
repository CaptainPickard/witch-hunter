# CC-C4b · Rim Mountains — the Old King's Wall of Stone (R-62.8)

Change-order brief, written 2026-10-08 by IO from Nicko's ruling (R-62.8,
clarify recommendations accepted 2026-10-08: terrain cliffs via the
heightfield rim term + 3 road notches + skyline silhouette), R-62.7's
crossroads contract (the 3 branch roads point at notch mouths, marked in
CONFIG comments), and the CC-C1/C4 terrain program. Base f3ace65 (CC-C4a
flora+roads landed). Branch feat/world-visuals, worktree /tmp/wh-worldfeat.
ONE order at a time. Merge to dev/main = Nicko's call only. Always English.

## 0. WHY THIS ORDER

C's rim is an invisible plane + clamp. R-62.8: the region gets MOUNTAINS
— the boundary becomes geometry the player SEES and cannot climb (the
slope guard is the physics), with three notches where the King's Roads
visibly exit toward the future areas, softly blocked at the rim line
until those regions exist. This also completes doc 61's landscape-identity
gap: the mountain ring IS the region's skyline.

## 1. LOCKED RULINGS THIS ORDER RIDES (verbatim from the accepted clarify)

- Mountains = TERRAIN CLIFFS via a heightfield rim term (recommended and
  accepted: natural, no new engine tech; NOT boulder-wall props, NOT
  scree-only). 3 path notches carved N/E/W + silhouette.
- Road mouths: VISIBLE-BUT-GATED — the road continues through the notch
  into fog; a soft blocker (dormancy-toast style, reason-naming) holds the
  player at the rim line until the future regions land.
- One combined region-level look: mountains + notches + scree decoration.

## 2. VERIFIED STATE BLOCK (census @ f3ace65; RE-GREP anchors)

- wh-ground.js (274 lines): makeField(T, flats, rim) wh-ground.js:58 —
  the RIM HOOK EXISTS: rim = { from, to } currently fades height to 0
  radially (heightA :85-98, multiply by (1 - smoothstep(rim.from,
  rim.to, rr))). fieldFor maps T.pocket + T.stonePad to plane-local
  flats (:164-170), T.rim passed through. buildTerrain (S grid + vertex
  colors moss->stone by smoothstep(0.3, hMax*0.9, h) :124,
  MeshStandard flatShading) :108-135. gridTri B-TRI :140-153.
  CFG.regionC.terrain rows: CONFIG.js:552+ (seed 1337, S 140, hMax 5,
  pocket... stonePad..., cullDistanceM 170 etc).
- C roads (CC-C4a): CFG.roads rows — C spine glade->Stone ring +
  N/E/W branches; notch mouths MARKED in CONFIG comments: N (0,-596),
  E (240,-366), W (-240,-366) (C-local disc center (0,-366): NOTCH
  RADIALS: N bearing +z-ish along -z... precise: N mouth at z=-596 =
  230 NORTH of center; E mouth at x=240 = 240 east; W at x=-240).
  camp.js roadsFor keep-outs; whRoadsFor region-manager.js:1975.
- RIM + clamp current: whClampRadial at whPlayRadius(regionId) = 280 -
  1.5 = 278.5 (per-region CC-C2/C4); the rim FADE row
  CFG.regionC.terrain.rim (if set — check; C4 shipped visualGroundMinRadius
  400 CONFIG.js:543 instead; the mesh spans z -646..-86/x -280..280 and
  fades at its square's edge — CHECK the actual C rim row values).
- Door/toast machinery: CFG.regionC.door.text (:538) rows + the
  interact chain tryDoorway + setGateHint + holdAtLockedDoor
  (region-manager.js:155 family, game.js:1201-1205 area). Region
  banner showRegionName.
- ROAD heights: CC-C4a nudged road waypoints to gentle terrain (heightAt
  tables in its builder log); notch-approach road ends sit at the rim
  (road rows END at the rim line today — nothing beyond).

## 3. IMPLEMENTATION CONTRACT

3.1 THE MOUNTAIN RING (wh-ground.js + CONFIG.js):
- NEW rim-shape capability in makeField: today rim = a fade-to-0;
  CC-C4b adds rimMOUNTAINS (a new optional terrain row read per region,
  default absent = today's behavior; A/B have no terrain at all, C
  switches profile): CONFIG.regionC.terrain.rim = { from: 240, blend:
  30, peakH: 34, cliffSlopeDeg: 38 PROPOSED }:
  - height(x,z) for r (disc-local radius) > rim.from: the fBm height
    rises along a smoothstep band from+blend -> the ridgeline: ridgeH
    = peakH * (0.75 + 0.45 * noiseLump(x,z)) where the LUMP seed derives
    from the T.seed salt stream (deterministic; the ridge is NOT a
    perfect ring: elevation + noise, so peaks/valleys read; the notch
    terms of 3.2 subtract from it).
  - The rise SLOPE from rim.from to the ridge foot must exceed the
    climb cap everywhere outside the notches (cliffSlopeDeg 38 > cap 31
    sprint) — the slope GUARD then blocks climbing NATURALLY: assert in
    the builder report (max slope sampled along the rim band vs 31/45).
  - VERTEX COLORS: heights > stone-threshold take colHigh (stone) —
    raise the threshold so the mountain ring reads STONE on upper
    slopes, moss foothills below (existing moss->stone lerp; retune
    threshold rows PROPOSED).
- THE SEAM: beyond the 560 plane the SKIRT stays (CC-C4's flat skirt at
  rim color); the mountain ring INSIDE the plane edge means the plane
  boundary sits ON the ridge (r 278.5 >= plane half 280 - 1.5): the mesh
  edge and skirt must meet at the ridge base (fade the ridge back down
  in the last ~15m to the plane edge: rim.to vs plane edge — builder
  arithmetic, documented; SKIRT color = stone).
- CAMERA: the ring rises ~34m at the rim: verify the far-plane (camera
  far 500) + fog still compose; the ring top must be VISIBLE from the
  region interior through fog (fog density 0.033 at 120m+... the ring
  from the Stone (r 0) is 2240+ away? NO: ring radius ~240-278 from
  center; from the Stone the E/W ring distance ~240m — check visibility
  vs the fog wall (may read as silhouette only = FINE, that IS the
  skyline); the builder prints the fog-transmittance estimate at 240m
  and the visible-from-glade distance (110m from (0,-96) to the N rim).
- B-TRI EXACTNESS: the grid + sampler regenerate with the new heightA —
  the C4a roads re-nudge against the NEW heights (see 3.2); determinism
  hash changes (document the new grid hash pair).

3.2 THE THREE NOTCHES (wh-ground.js + CONFIG.js + roads):
- For EACH notch i (N, E, W at the marked mouths): a CANE-CARVED CORNER
  — the ridge height subtracts a notch window (smoothstep on the road's
  approach direction within notchHalfWidth ~10m PROPOSED): inside the
  window the ridge does not rise; the ground continues along the road
  bed (the road's heightAt values) until the rim line (playable edge).
  The road rows extend ~30m INTO the notch (a visible descending road
  bed toward fog; beyond the playable rim the slope guard + rim clamp
  hold — the road visually exits, the player cannot follow beyond the
  rim line).
- SOFT BLOCKER (game.js interact + CONFIG text): at each notch mouth,
  an interact zone (the road end, radius ~5m): E shows toast —
  'The road beyond is lost. For now.' PROPOSED text (reason-naming
  convention). Reuse the doorway prompt surface pattern (CC-C2's
  tryDoorway family, cfg text rows). NO new hint element: the existing
  prompt/toast surfaces suffice.
- ROAD RETUNE: the 3 branch road end segments re-nudge to the notch bed
  heights (the ridge changed the terrain around the mouths); the
  SPINE + ring are away from the rim — verify unchanged (heightAt
  table diff: same at r < 200).
- NOTCH + SCATTER: trees/props keep out of the notch mouths (the
  C4a keep-outs + notchHalfWidth); boulders MAY line the notch (scree
  at the mountain foot — a few PROPOSED rows).

3.3 SKYLINE + LIGHTING (CONFIG.js rows PROPOSED):
- The ring as the region silhouette: the fog tuning so the ridge reads
  through haze (fog row tweak PROPOSED if needed — the builder computes
  transmittance at 110/240m for the new ridge heights; if opaque, LOWER
  the fog density a touch (0.033 -> ~0.026-0.028 PROPOSED) so the ring
  silhouettes WITHOUT revealing the world edge (the skirt/ring now
  provides the edge cover — the fog's world-edge job is delegated to
  the mountains; verify by geometry: from the playable rim, the sight
  line to the world edge beyond the plane... the mountains now BLOCK
  the line of sight: document the geometry argument).
- SCREE DECORATION: PROPOSED ~12 scattered stonefrag/boulder rows at
  the ring's foot (r 220-240), natural rockfall look.
- C4a's moss slab fork marker: unchanged.

3.4 CAMP + MIST INTERPLAY (camp.js if needed, region-manager.js):
- Camp edge check: unchanged (the rim clamp still governs; the notch
  approach may allow a camp deeper toward the mouth — fine).
- Mist plane: rides its CONFIG height (C anchor unchanged — the mist
  lies in the forest bowl, not on the slopes).

3.5 BUNDLE + SERVING (standing law):
- node --check every edited JS; python3 tools/build_v8.py; bundle in
  the SAME commit.
- Commit (author CaptainPickard <pickard.nicko@gmail.com>):
  'feat(cc-c4b): rim mountains - heightfield cliff ring (deterministic
  ridge + noise lumps, slope-guard-blocked, stone vertex band), three
  road notches N/E/W (visible road beds exiting into fog, soft-blocker
  toasts at the mouths), scree foot decoration, fog/silhouette retune,
  roads re-nudged, A/B byte-identical'
  + push origin feat/world-visuals immediately.
- Do NOT flip 8793 (IO-side). Report FLIP-HOST-SIDE-PENDING + sha.
- NO harness, NO headless browser, NO game run: syntax checks only.

## 4. SELF-CHECKS THE BUILDER RUNS (report contents)

1. node --check every edited JS.
2. Determinism: two C grid builds hash-equal (new hash pair printed).
3. Cliff slope audit: sampled max slope along the rim band (r 240-278,
   64 samples) outside notches vs the climb caps (31/45) — the guard
   binds everywhere except the notches; print binding fraction.
4. Notch bed audit: heightAt along each notch's road bed (the road
   stays walkable: max grade through the window; the blocker radius
   zone flat enough to stand).
5. Fog/silhouette numbers: transmittance at 110m (N rim from glade),
   240m (E/W rims from the Stone), ring visibility verdict + any fog
   row change applied.
6. Seam audit: mesh edge vs skirt at the ridge base (no crack, no
   z-fight; skirt color = stone).
7. Road diff table: spine/ring heights unchanged (r < 200); branch end
   segments re-nudged (delta list).
8. A/B invariance argument + bundle size.

## 5. ACCEPTANCE CRITERIA (Nicko playtests; A1-A6)

- A1 THE RING: walking anywhere in C, mountains rise around the region —
  stone-topped, moss-foothilled, silhouetting through fog from the
  Stone and the glade; the world edge is GONE (the ring replaces it).
- A2 CLIMBING FAILS NATURALLY: attempting to walk up the rim ring at
  any non-notch point stalls on the slope (the guard, not a wall); no
  wall-y feel, no invisible plane hit inside the ring.
- A3 THE NOTCHES: the three roads run INTO their notch mouths; each road
  bed visibly descends toward fog; E near a road end gives the reason
  toast; you cannot cross the rim line.
- A4 THE ROADS STILL WORK: the glade->Stone spine + ring road + fork
  unchanged by the rim work (same walk as C4a).
- A5 SCREE + FLORA: the mountain foot has rock debris; trees/bushes
  don't grow on the cliff band.
- A6 A/B UNCHANGED + SAVE/LOAD: A/B identical; a C save/load on a
  mountainside still seats y correctly (the sampler's new grid).

## 6. SCOPE CONTRACT

TOUCH: prototype/js/wh-ground.js (rim + notch terms), CONFIG.js,
region-manager.js (skirt/scree/skirt-color + any rim-feed reuse),
game.js (notch blocker interact + toast hookup), prototype/builds/
v8-playable.html (rebundle).
NOT TOUCH: js/region-defs.js (no conn changes; the notch blocker is an
interact zone, NOT a connection), js/camp.js (unless the edge check
needs a notch-aware line — expected none), js/daynight.js, js/save.js,
js/player.js, js/enemy.js, js/corpse-loot.js, js/assets.js (mountains
are procedural), index.html, style.css, tools/*, docs/*, io/*,
scratch/*, art-direction/*.
CRG IMPACT (baked per law, run 2026-10-08 @ f3ace65): impact --files
wh-ground.js CONFIG.js region-manager.js game.js --depth 2 --max-results
12 → **139 nodes directly changed, 0 nodes impacted within 2 hops, 0
additional files**.

## 7. IF THE SPEC MEETS REALITY AND DISAGREES

Obey the code's actual shape, land the INTENT, log deviations. Violations
to avoid: no region-defs/connection changes (the notch blocker is
interact-zone machinery), no camp.js rewrite, no per-frame cost beyond
the existing feeds (the ridge is baked into the grid at build — zero
per-frame new work), no A/B path edits. The terrain stays deterministic
and B-TRI exact.