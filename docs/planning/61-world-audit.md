# Witch Hunter: World, Ground, Light-Box and Asset Audit (static, report only)

## Headline findings

*Tags: **[INF-H/M/L]** marks an inference with high, medium or low confidence. **[BENCH]** marks general souls-like practice, which has no repo evidence. Every other claim cites `file:line`. Light values are computed in r185 physical units (diffuse = albedo/π × irradiance), with sRGB-decoded hex colours and Rec.709 luminance.*

1. **Every prop renders about half underground.**
   - The loader grounds each template by writing `root.position.y = -minY` (`assets.js:110-120`).
   - `region-manager.js:327` then overwrites it with `obj.position.set(p.x, 0, p.z)`, and `:329` scales around the sunk pivot.
   - Meshy meshes are centred on their bounding box (`SPIKE-LOG.md:234-235`, `assets.js:104-106`). So each prop loses about half its height below y=0: tree root flares, the gate and archway openings, and the statue base are all buried.
   - The code path is certain **[INF-H]**. The ~50% figure depends on each GLB being bbox-centred **[INF-M-H]**.
   - No test would catch this. The only grounding probe checks the player alone, and only one side of the tolerance (`tests/wh_v3_anim_probes.py:192-203`).
2. **The ground renders black.**
   - `region-manager.js:288-290` sets `color: 0x3d3a2c` **and** a `map` whose base is the same colour, so the material multiplies them.
   - Linear albedo drops to ≈0.2% in region A and ≈0.03% in region B (`0x232620`). After exposure 1.6 and the ACES toe, the near ground outputs under 1/255 **[INF-H, computed]**.
   - The whole procedural canvas (moss, puddles, blotches, `:165-239`) is invisible.
   - Its Nearest-without-mipmaps filtering (`:246-248`) is the same salt-and-pepper defect already fixed in the viewer (`SPIKE-LOG.md:78-83`). It will show up as soon as the ground is lit.
3. **The lights form a flat, shadowless daytime rig.**
   - AmbientLight 4.0 plus HemisphereLight 1.5 against one warm-white directional light at 59° elevation (`CONFIG.js:15-24`, `game.js:54-64`).
   - The key sits behind the camera on the main northward path, so it front-lights everything the camera sees.
   - Computed lit-to-shadow ratio on vertical surfaces: **1.43:1 in region A, 1.23:1 in region B**, i.e. 0.3-0.5 stop **[INF-H]**.
   - `ambientLightLevel` only scales the key (`game.js:427-429`). Region B, meant to be darker, just gets flatter.
   - There are no point lights, and the two lantern posts are unlit (`CONFIG.js:64-65`). The slice spec requires "one diegetic key (lantern) + moon fill + fog density 0.018" (`31-vertical-slice-scope.md:35-36`).
4. **Only half the retro look is implemented.**
   - Missing: internal-resolution render, point-sampled upscale, dither, grain and rim light (`game.js:34-36`). All are required by `29-art-style-bake-off-spike.md:73-75,107-111` and `31:143-148`.
   - The result is sharp, aliased HD silhouettes over chunky 256/512 px Nearest texels, i.e. mixed-resolution pixels.
   - It also costs 4-10× the fragment work of the 540-720p target.
   - The arsenal viewer already does this correctly (`arsenal-viewer.template.html:169-180`).
5. **Characters use the wrong asset variant and hold most of the texture memory.**
   - `assets.js:44-46` loads raw `races_regen/*.glb` bodies (2048 px atlases, linear filtering). The stated reason is that "no pixelated variants exist" (`assets.js:6-7`, `prototype/README.md:67-69`).
   - That premise is out of date: the v3 pipeline produced `races/<name>-pixelated.glb` with the same 28-32k-tri mesh, a 512 px 5-bit texture and normals (`regen_pipeline_v3.py:13-15`, `SPIKE-LOG.md:318-328`).
   - The three loaded bodies take an estimated ≈67 MB of the ≈85 MB texture total **[INF-M]**.
6. **Nothing in the world guides the player.**
   - The chokepoint is an invisible 8-unit gap in an invisible plane. `markerScale` and `wallHeight` are declared but never read (`CONFIG.js:186,192`).
   - The neighbouring region stays hidden until you cross (`region-manager.js:358,390-391`). The only cue is DOM text (`index.html:21`, `game.js:392-395`).
   - The default spawn camera (`camYaw = π`, `player.js:92`) faces south, away from every prop, toward the ground-disc edge 45 units away. The code comment claiming it faces −z is wrong.
   - The only object at the gate is region A's ghoul. Its spawn point (2, −30) is on the wrong side of its own boundary, so it walks in place against the clamp forever (`CONFIG.js:53`, `region-manager.js:116-133`, `enemy.js:191-196`) **[INF-H]**.
7. **The world is a flat disc with no collision and open edges.**
   - There is no prop collision, terrain, gravity or radial clamp. `gravityY`, `xMin` and `xMax` are never read, and the only clamp is the boundary plane (`region-manager.js:99-113`).
   - The player walks through trees and can walk off the radius-90 disc.
   - The camera has no ground collision. At max zoom and min pitch it ends up at y ≈ 2.6 + 14·sin(−15°) ≈ **−1.0**, i.e. underground (`player.js:873-880`, `CONFIG.js:236-237`).
8. **Set dressing uses up the triangle budget.**
   - Biome props are ~30k tris each (`59-biome-object-library.md:122-130`).
   - Region B totals about **1.45M tris, 72% of the slice's 2M budget** (`31:150`), before any ground cover, decor, VFX or extra enemies.
   - A tree stump costs 15× a 2k-tri kit prop. There is no LOD and no instancing.
   - Draw calls (~53 in A, ~69 in B) are not the constraint.
9. **Crossing a region boundary causes a GPU spike.**
   - `disposeRegion` disposes geometry, materials and textures that are shared with the template cache and with the other region (`region-manager.js:365-384`). `clone(true)` shares them (`three.classic.js:23422-23423`).
   - Pre-warm only builds a hidden scene graph, and hidden objects are never uploaded (`three.classic.js:77841`).
   - So the reveal frame re-uploads or first-uploads tens of MB. The hitch certainly exists **[INF-H]**; its size is unmeasured.
10. **The assets we already own are what the world is missing.**
    - 113 of 139 GLBs are never loaded.
    - The crypt kit (chandelier, pillars, steps, sarcophagus, skulls) plus the candelabra and 8 unused church-kit pieces are exactly the landmark, light-pool and height-variation pieces the regions lack.
    - Four Darkwood reference images (roots, moss drapes, brambles, puddles) are made and waiting on Meshy credits (`59:133-147`).
    - No rest or camp space exists where the locked decor item family could be shown (`sui/move/wh-items/sources/items.move:52`, `11-warp-camp.md:117-121`).

**Scope:** static read of:
- **Docs:** 02, 03 and 27, plus 11, 24, 28, 29, 31, 58, 59 and 60 for rulings and budgets.
- **Prototype:** `prototype/{index.html, style.css, server.py}` and all 9 files in `prototype/js/`.
- **Art pipeline:** in `art-direction/3d/`: the manifest, `meshy_driver.py`, `queue.json`, the retexture/pixelate/regen/normals scripts and the arsenal viewer template; plus `art-direction/3d-spike/SPIKE-LOG.md`.
- **GLBs:** file names only under `art-direction/3d/assets/**`; no binary contents read.
- **Engine:** vendored r185 source, only where engine behaviour decides a claim.

No files were modified.

---

## 1. Current-state inventory

### 1a. World layout

| Element | As implemented | Evidence |
|---|---|---|
| Region model | Two regions; only one is active and visible at a time. A "Hold Outskirts" is z > −25; B "Darkwood Edge" is z < −25 | `CONFIG.js:42-44,103-105,182-183`; `region-defs.js:17-34` |
| Region footprint | Each region is its own flat ground disc, radius 90, both centred on the same origin. Only the home half of each disc is gameplay; the other half is empty floor | `CONFIG.js:27`; `region-manager.js:293-299` |
| Boundary | Invisible plane at z=−25. Outside the corridor the player is clamped to the home side. Enemies stop 1.5 units short, even inside the corridor | `region-manager.js:99-133`; `CONFIG.js:355` |
| Chokepoint | One invisible corridor, x∈[−4,4]. Crossing moves the player 2 units past the plane and keeps x | `CONFIG.js:189-193`; `region-defs.js:39-49,65-68,80-87`; `region-manager.js:57-72` |
| Chokepoint dressing | None. The only cue is DOM text, shown within 30 units of the plane and \|x\|<16 | `CONFIG.js:186,192` (never read); `index.html:21`; `game.js:392-395` |
| World edge | None. `xMin`/`xMax` are never read and there is no radial clamp | `CONFIG.js:184-185`; `region-manager.js:99-113` |
| Streaming | Neighbour is built hidden when the player is ≤30 units from the plane and disposed beyond 50. Crossing reveals it and disposes the old region in the same tick | `CONFIG.js:195-198`; `region-manager.js:74-91,388-413` |
| Spawn and respawn | A at (0,45), B at (0,−45); spawn camera yaw π (faces +z/south). Death respawns at a bare coordinate with no rest point | `CONFIG.js:45,106`; `player.js:92`; `game.js:289-295` |
| Enemy placement | 3 per region, literal x/z. A: bandits (−6,−8) and (10,−14), ghoul **(2,−30)**, which is outside A. B: ghouls (−8,−38) and (9,−50), bandit (0,−60) | `CONFIG.js:50-54,111-115` |
| Prop placement | Hand-typed literal tables `{asset,x,z,rotY,scale}`: A has 44, B has 60. y is forced to 0. `scale` multiplies the native Meshy size (~2 units on the largest axis). Data lives in CONFIG but nothing is procedural: no scatter rules, exclusion zones or per-asset metadata | `CONFIG.js:55-100,116-177`; `region-manager.js:322-331` |
| Prop extents | A: x −27.8…29.4, z −19.9…31.1; the nearest prop is 14 units north of spawn. B: x −37.4…36.4, z −35.6…−79.9 | `CONFIG.js:56-99,117-176` |
| Content | A: a graveyard cluster with fence runs (e.g. `CONFIG.js:71-73`). B: 33 trees, a 4-piece ruin (archway, buttress, pew, rubble at `:150-153`), two cemetery gates standing mid-forest (`:169-170`) | same |
| Collision | Props have none. Player and enemies only push each other apart as circles. Firebolts hit enemies only. Enemy sight is radius only, with no line of sight | `region-manager.js:423-433`; `spells.js:60-75`; `enemy.js:152-160` |
| Vertical footing | All actors at constant y=0. `gravityY` and `velY` are never used | `CONFIG.js:46,107`; `player.js:41,926`; `game.js:459,638,693` |
| Persistence | Dead enemies stay dead, per region, per session | `region-manager.js:348-356,434-438` |

### 1b. Ground surface

| Aspect | As implemented | Evidence |
|---|---|---|
| Mesh | `CircleGeometry(90, 48)`: a 48-triangle flat fan at y=0 | `region-manager.js:293-297` |
| Material | MeshStandardMaterial with **color = groundColorA/B *and* map = canvas texture**, roughness 1, metalness 0, DoubleSide | `region-manager.js:288-292`; `CONFIG.js:28-29` |
| Texture source | Procedural 256² canvas per region (seeded mulberry32): base tone, 140 blotch clusters, 10% grain, 6% moss, 3% puddle specks | `region-manager.js:142-239`; `CONFIG.js:30-36` |
| UV and tiling | Planar UVs across the 180-unit diameter, repeated 12× → one tile per 15 units, ~17 texels per unit, 144 copies of one tile | `region-manager.js:241-252` |
| Filtering | Nearest for both magnification and minification, no mipmaps, sRGB | `region-manager.js:246-249` |
| Effective albedo | A: 0.047 (colour) × 0.047 (texel) ≈ **0.0022** linear. B: ≈ **0.0003**. Renders at under 1/255 near the player before fog **[INF-H]** | computed |
| Collision / footing | Nothing samples the ground; y=0 matches the flat mesh by construction. Walking off the mesh is possible | 1a |
| Mist layer (B only) | 180×180 PlaneGeometry at y=1.5, MeshBasicMaterial 0xc5c9cc, opacity 0.14, DoubleSide, no depth write, no collider | `region-manager.js:303-320`; `CONFIG.js:202-208` |

### 1c. Light box

| Element | Value | Evidence |
|---|---|---|
| AmbientLight | 0x8a8fa8 @ **4.0**. Never scaled by region | `CONFIG.js:17-18`; `game.js:56` |
| HemisphereLight | Sky 0x6b7fa8 / ground 0x3a3a44 @ 1.5 | `CONFIG.js:21-23`; `game.js:58` |
| DirectionalLight (key) | 0xfff2dd @ 1.2 × `ambientLightLevel` (A 1.0, B 0.55). Position (30,60,20) aimed at origin: 59° elevation, on the +x/+z side, i.e. behind the camera on the northward path. No shadow | `game.js:60-63,427-429`; `CONFIG.js:19-20,49,110` |
| Point / spot lights | **None** | no PointLight or SpotLight in `prototype/js` |
| Emissive | Spell-glow sphere (MeshBasic 0xff7722, r 0.12); firebolt sphere (r 0.18). The sword's "armed" emissive pulse is dead code: `p.sword` is a Group with no `.material` | `game.js:150-154,202-223,628-632`; `spells.js:33-38` |
| Shadows | Shadow map off; every mesh has castShadow and receiveShadow false. CONFIG notes SwiftShader | `CONFIG.js:12`; `game.js:43`; `assets.js:127-128` |
| Fog | FogExp2. A: 0x9aa0a3 @ 0.012; B: 0x6f7477 @ 0.024. Switches instantly on crossing. `fogNearFactor`/`fogFarFactor` never read | `game.js:50,422-430,690-697`; `CONFIG.js:37-38,47-48,108-109` |
| Fog distances (50% / 90% / 99%) | A: 69 / 126 / 179 units. B: 35 / 63 / 89 units | computed: d = √(−ln(1−f))/ρ |
| Background / sky | Flat colour equal to the fog colour. No sky mesh, moon, stars or skyline | `game.js:49,424` |
| Tone mapping | ACESFilmic, exposure 1.6, sRGB output. Fog is mixed *after* tone mapping, in output colour space, so fog and background show their exact hex | `game.js:38-42`; `three.classic.js:75006,37702-37711` |
| Renderer / camera | Antialias off; device pixel ratio min(DPR, 2); full window size. FOV 60, near 0.1, far 500. Orbit distance 7 (3-14), pitch −15°…65°, height 2.6 | `game.js:34-36,571-572`; `CONFIG.js:234-239` |
| Pixelation / post | **No post-processing and no render target.** The pixel look is texture-only: baked 256 or 512 px 5-bit textures, Nearest magnification on URLs containing `-pixelated`, and the Nearest ground canvas. Bodies keep linear-filtered 2048 px textures | `assets.js:133-137,181`; `region-manager.js:246-247` |

**Derived from the rig [INF-H, computed]:**
- **Fill share of upward-facing irradiance:** 61% in A, 74% in B.
- **Lit-to-shadow ratio on vertical faces:** 1.43:1 in A, 1.23:1 in B. On upward faces: 1.65:1 in A, 1.36:1 in B.
- **Key placement:** on the main path (walking toward −z) the key light is behind the camera, so there is no silhouette rim.

### 1d. Asset families

**On disk: 139 GLBs covering 60 distinct asset names.** "46" is the 2026-09-13 production run: 46 assets, 92 files counting raw and pixelated (`asset-manifest.md:10-11`).

| Directory | GLBs | Assets | Documented in manifest? | Loaded by prototype |
|---|---|---|---|---|
| `armor/` | 16 | 8 | yes (`:24-31`) | 0 |
| `biome_library/` | 27 (raw/, raw copy, pixelated) | 9 | no; documented in `59:120-131` | 9 pixelated |
| `church-kit/` | 30 | 15 | yes (`:42-56`) | 8 (7 placed; `ironFenceCorner` loaded but never placed) |
| `crypt/` | 10 | 5 | no; documented in `SPIKE-LOG.md:333-351` | 0 |
| `graveyard/` | 8 | 4 | yes (`:57-60`) | 4 |
| `races/` | 20 | 10 | rows exist but are **out of date** (manifest says 15k tris; files are now v3 28-32k, `SPIKE-LOG.md:326-328`) | 0 |
| `races_regen/` | 10 | (same 10 names) | no; documented in `SPIKE-LOG.md:256-263` | 3 raw |
| `weapons/` | 18 | 9 | yes (`:15-23`) | 2 |

The manifest covers 92 files; 47 are covered only elsewhere. `art-direction/3d-spike/` also holds 6 legacy GLBs (gravedigger body, helmet, gravestone), none referenced by the prototype.

**Loaded asset families (26 GLBs, `assets.js:15-51`):**

| Family | Logical names → file | Tris each | Texture | Placed in A | Placed in B |
|---|---|---|---|---|---|
| Graveyard (46-run) | obelisk, cross, mound, coffin → `graveyard/*-pixelated.glb` | 2k (`manifest:57-60`) | 256 px, 48-colour, 5-bit (`retexture.py:13-30`) | 5/3/5/2 | 2/2/0/0 |
| Biome library (v3) | m1 gate, m2 picket fence, m3 statue, m4 oak, m5 yew, m6 witchwood, m7 log, m8 stump, m9 boulder | **~30k** (`59:122-130`) | 512 px, 5-bit (`biome_pixelate.py:19-28`) | 0/5/1/1/1/0/2/5/6 | 2/2/0/7/8/9/4/4/7 |
| Church-kit (46-run) | lantern post, dead tree, rubble, archway, buttress, broken pew, iron fence, iron corner | 2k (`manifest:43-56`) | 256 px | 2/4/0/0/0/0/2/0 | 0/9/1/1/1/1/0/0 |
| Characters (raw Meshy) | player = human-hunter-male, bandit = orc-male-warrior, ghoul = undead-ghoul-male | 28-32k (`SPIKE-LOG.md:261`) | 2048 px raw, linear filtering **[INF-H]** (`SPIKE-LOG.md:277-278`) | player + 2 bandits + 1 ghoul | player + 1 bandit + 2 ghouls |
| Weapons (46-run) | longsword, hand axe | 2k (`manifest:15,17`) | 256 px | sword + 2 axes | sword + 1 axe |

- **Procedural meshes:** ground disc (48 tris), mist plane (2), spell glow (~80), one ~80-tri firebolt sphere per cast (never disposed, `spells.js:79-85`), and grey stand-in boxes on load failure (`assets.js:87-102`).
- **Missing entirely:** particles, ground cover, sky.

**Scene budget (only the active region renders):**

| Region | Draw calls | Triangles **[INF-M]** | Props | Actors | Lights |
|---|---|---|---|---|---|
| A | ≈53 | ≈0.80M (21×30k + 23×2k + 4 bodies ×30k + 3 weapons ×2k) | 44 | 4 | 3 (no point lights) |
| B | ≈69 | ≈1.45M (43×30k + 17×2k + 4×30k + 2×2k) | 60 | 4 | 3 (no point lights) |

- **Draw-call assumption:** one mesh and one primitive per GLB **[INF-H]**; the pipelines export a single geometry (`biome_pixelate.py:95-103`).
- **Textures:** 26 base-colour textures plus 1-2 ground canvases, ≈85 MB including mipmaps **[INF-M]**. The 3 bodies at 2048² account for ≈67 MB, the 9 biome textures at 512² for ≈12.6 MB, and the 14 kit textures at 256² for ≈4.9 MB.
- **Download:** ≈25 MB, re-fetched on every page load because the server sends `Cache-Control: no-store` (`server.py:51-53`) **[INF-L]**. The bodies alone are 3.6-4.6 MB each (`SPIKE-LOG.md:261`).

---

## 2. Design gap analysis vs the souls-like benchmark

| Pillar | Benchmark [BENCH] | Witch Hunter today | Gap |
|---|---|---|---|
| Navigation readability | You see the destination before you can reach it (Firelink → Undead Burg; Stormveil and the Erdtree in ER). Chokepoints are physical and glow (fog gates). Rest points are light beacons (BB lamps, ER Sites of Grace) | Invisible plane and gap; neighbour hidden until crossed; DOM hint; spawn camera faces away from all content; a ghoul walking in place at the gate (Headline 6). Props have no collision, so nothing implies a path | **Critical** |
| Landmark / skyline | A global compass silhouette (Erdtree, Yharnam's cathedral, Lothric) plus a local landmark per area | None. The flat background is the fog colour; the tallest objects are trees; the 4-piece ruin is sunk ~50% and hidden among trees. Doc 03 already places a natural global landmark, the Veil Spire, north-centre (`03-world-design.md:261-264`), and the canon frames show it (concept-01 and the darkwood reference, both viewed) | **Critical** |
| Atmosphere (fog layers, light pools, darkness gradients, colour script) | Height fog plus distance fog plus shafts; warm pools against a cold key (BB); per-area grade; time-of-day (DS3/ER) | One FogExp2 layer, one mist plane with a hard seam, no light pools, darkness from albedo only (fill is 61-74%), neutral grey fogs, no accent colour, no clock (`03:711-714` requires 24:1) | **Critical** |
| Composition (framing, verticality, corridor → arena rhythm) | Compression opening onto a reveal; arches and cliffs as vignettes; stairs and heights | Open flat disc at y=0; no framing along the camera path; the stone-steps asset sits unused; the only corridor is invisible | **High** |
| Ambient storytelling | Props arranged as scenes: corpses at a last stand, barricades, lit windows | Some intent (fence runs, a graveyard cluster, a forest ruin), undermined by sinking and by gates to nowhere (`CONFIG.js:169-170`). No focal story props (gallows, abandoned campfire, hanged lantern) | **Medium** |
| Camp / rest identity space | Firelink, Hunter's Dream and Roundtable Hold: a fixed composition with its own light identity | Absent. Respawn is a bare coordinate (`game.js:289-295`), and region B's respawn is inside two ghouls' chase radius (10.3-10.6 units vs a 14.4 trigger; `CONFIG.js:106,112-113,341`). The camp look is fully specified (`24-art-bible.md:62-64,111-118`; three camp concepts) | **High** |
| Screenshot value (marketing for the economy) | Lone backlit figure, landmark on the horizon, one warm light | None of the approved frame's five ingredients (moon, landmark silhouette, one amber pool, backlit figure, wet ground) is present. The first frame shows the player's back facing the empty south edge. The HUD and FPS counter are always on (`index.html:19`) | **Critical for the economy direction** |

**Art-bible QA checklist (`24-art-bible.md:320-331`) applied to today's frame:**

| # | Check | Result |
|---|---|---|
| 1 | Negative space | Partial, by accident: black ground plus pale fog |
| 2 | Tiny figure | Camera sits in the combat framing band: 22% of frame height at distance 7 (`28:22-23`) |
| 3 | One accent | **Fail** |
| 4 | Dither / grain | **Fail** |
| 5 | Rim light + diegetic sources only | **Fail** |
| 6 | No photoreal / pastel | Pass |

---

## 3. Function and performance gap analysis

### 3.1 Budget

- **Draw calls:** ≈53/69 against a 1,500 limit. Not a constraint.
- **Triangles:** 0.80M/1.45M against 2M (`31:150`). Region B is already at 72% with no ground cover, no decor and 4 actors. 43 biome props at ~30k each are 89% of B.
- **Why tri counts are high:** the Meshy quad setting (`meshy_driver.py:30`) produces about 2× the target in triangles. A 15k target gave 28-32k tris (`SPIKE-LOG.md:258-262`); a 2k target gave 3.5-5k faces (`:338-339`) **[INF-H]**.
- **Texture memory:** ≈85 MB, 79% of it in three raw body atlases. P0-7 brings the total to ≈22 MB **[INF-M]**.
- **Load:** synchronous r185 bundle (~80k lines), then 26 GLBs fetched in parallel, all gated on `Promise.all` (`assets.js:177-188`). Then region A builds, the loading note hides (`game.js:641`), and the first frame pays every upload and shader compile.
  - Slow links hit the 20 s per-asset timeout and show grey boxes (`assets.js:152-154`, `CONFIG.js:436`).
  - The test harness already waits 12 s on the proxy origin (`wh_v3_anim_probes.py:211`).

### 3.2 Post, shadow and fog costs

- **Post:** none today. The dominant GPU cost is full-resolution fill at up to 2× DPR, using MeshStandardMaterial with 3 lights, DoubleSide on everything (`assets.js:132`), and B's translucent mist plane covering most of the lower frame.
- **Shadows:** zero today. A directional shadow map would add a depth pass over up to 1.45M tris.
- **Fog:** FogExp2 costs next to nothing. The mist plane costs overdraw.

### 3.3 Artifact risks

| Risk | Status | Evidence |
|---|---|---|
| Tiling repetition (144 copies of one 256² tile, 15-unit period) | Hidden now; appears after P0-2 | `region-manager.js:241-252` |
| Minification sparkle | Hidden now; appears after P0-2 | `:246-248`; `SPIKE-LOG.md:78-83` |
| Faceted (flat-shaded) kit props and weapons: 46-run GLBs likely lack NORMAL, so GLTFLoader turns on `flatShading` | Likely active **[INF-M]** | `add_normals.py:4-10,190-194`; `gltf-loader.classic.js:3549,3608` |
| Lighting creases along UV seams (normals computed without welding vertices) | Hidden until a strong key light **[INF-M]** | `biome_pixelate.py:59-61`; `regen_pipeline_v3.py:47-57` |
| Three texture styles in one frame (2048 linear / 512 5-bit / 256 48-colour) | Active | 1d |
| Mixed-resolution pixels (HD aliased edges over chunky texels) | Active | `game.js:34-36` |
| Mist-plane seam at y=1.5 on every trunk and actor; camera drops under it at pitch below ≈ −9° | Active | `region-manager.js:303-320`; `CONFIG.js:206,237` |
| Visible world edge (A's south rim is 45 units behind spawn at ~25% fog; east/west ~42% visible) | Active | `CONFIG.js:27,45,48` |
| Camera underground or inside trunks | Active | `player.js:873-880`; `CONFIG.js:236-237` |
| z-fighting | None today. The two coplanar discs overlap if both regions ever render (relevant to P1-3) | `region-manager.js:293-299,358` |
| Far plane vs fog | No conflict (far 500 units ≫ 179/89 fog-opaque). Geometry beyond the fog is still rasterized. Depth precision ≈0.006 units at 100 **[INF-H]** | `game.js:571-572` |
| Fog and light pop instantly on crossing | Active | `game.js:422-430,690-697` |
| Mutating a shared material tints every clone (affects telegraph flashes and palette variants) | Latent | `assets.js:191-195`; `three.classic.js:23422-23423` |

### 3.4 Ground and footing correctness

| Check | Result | Evidence |
|---|---|---|
| Footing height vs mesh | Consistent only because both are flat y=0; nothing samples the ground | 1a, 1b |
| Prop grounding | Sunk ~50% of height **[INF-M-H]** | Headline 1 |
| Character float at rest | The offset is not scaled: \|minY\|·(1−s) ≈ **0.1 units** for a 2.0-unit native mesh scaled to 1.8 **[INF-M]** | `assets.js:114`; `game.js:624-626`; `player.js:119`; `region-manager.js:340-342` |
| Walk bob | The body only ever rises (abs of sine): +0-0.13 walking, +0-0.195 sprinting. No contact shadow | `player.js:757-770`; `CONFIG.js:389-404` |
| Corpses | Rotate −90° around a mid-body pivot, then drop 0.3. Enemies lie ≈0.4-0.5 units in the air; the player's corpse ≈0.7 **[INF-M]** | `enemy.js:239-251`; `player.js:670-672` |
| Off-mesh, collision, camera | See Headline 7 | |
| Existing test | Player only, one-sided (`minY ≥ −0.05`), so a float passes | `wh_v3_anim_probes.py:192-203` |

### 3.5 Risks to 60 fps on mid-range hardware

| Risk | Class |
|---|---|
| Fill rate at 2× DPR (no low-res pass, DoubleSide, mist overdraw) | HIGH on integrated GPUs and HiDPI screens |
| Region B vertex load (~1.45M tris, frustum culling only) | MED on integrated GPUs; LOW on GTX-1660 class |
| Crossing spike (re-upload plus first upload, possible recompiles) | HIGH, single-frame |
| First-frame compile and upload spike | MED |
| Adding or removing point lights at runtime (the light count is baked into shaders, so every material recompiles) | MED |
| Shadow map covering the whole scene | HIGH |
| CPU (~70 objects, 6 actors) | LOW |
| Testerbot uses SwiftShader (software GL, `CONFIG.js:12` note), so its FPS numbers say nothing about GPU performance | Measurement risk |

---

## 4. Recommendations

**Ordering constraints:**
- P0-2 and P0-3 must land together; otherwise the ground stays black.
- P0-1 must land before any placement or density work.
- P0-4 must land before P1-9.
- P0-6 must land before adding more regions or assets.
- The P0 set (all S or S-M) fits in one implementation round.
- Nothing below requires rigging.

### P0: correctness and the highest mood per hour

**P0-1 · Ground-align props and characters correctly (S code + S data).**
- **Problem:** props sit ~50% underground; characters float about 0.1 units.
- **Evidence:** `assets.js:110-120,191-195`; `region-manager.js:327-329`; `player.js:119`; `enemy.js:51`; `SPIKE-LOG.md:234-236`, where the viewer already fixed it with `-box.min.y * s`.
- **Change:**
  1. *Props:* wrap each loaded scene in a holder Group, set `root.position.y = -minY` inside it, and cache the holder. Callers' `position.set` and `scale` then act on the holder, so the base stays at y=0 at any scale.
  2. *Characters:* keep the mid-body pivot, because roll, death and lean rotate around it. Store the offset already scaled: `body.position.y = -minY*s`, set before `setBody`. Expose `WH_ASSETS.groundMinY(name)`.
  3. Change CONFIG prop `scale` to a world height `h` in metres, with `s = h / nativeHeight`. Run a one-time migration that keeps today's visible heights (`h ≈ scale × nativeH/2`), then re-tune.
  4. Re-tune the corpse drop (`enemy.js:242,250`) to the body's half-depth.
  5. Leave weapons alone; the combat audit owns grip pivots (`60-combat-audit-dark-souls.md:141,175`).
- **Acceptance:** M-01 and M-02 are two-sided, with \|minY\| ≤ 0.02.
- **Pipeline fit:** code only.
- **Economy:** **yes.** Player-placed decor must sit on the ground; this is the foundation of camp placement.

**P0-2 · Fix the ground material (S).**
- **Evidence:** `region-manager.js:246-248,288-292`.
- **Change:**
  - Set `color: 0xffffff` and let the canvas carry the palette (or bake the regional tint into the canvas).
  - Set `minFilter: NearestMipmapLinearFilter` and `generateMipmaps: true`; keep Nearest magnification; anisotropy ≤ 4.
- **Acceptance:** M-09 and M-12.
- **Economy:** **yes.** The ground is the stage in every screenshot.

**P0-3 · Relight with a lantern and a moon (S).**
- **Evidence:** `CONFIG.js:15-24,49,110`; `game.js:54-64,427-429`; `31:35-36`; `24:34-40`.
- **Change:** see §5.3. Summary:
  - Cut the AmbientLight.
  - Make a low, cool HemisphereLight the only fill, and have `ambientLightLevel` scale that fill.
  - Turn the directional into a low, cool moon placed on the −z side so it backlights the main path.
  - Add a warm PointLight lantern parented to the player.
  - Switch tone mapping to Neutral or AgX (both in r185, `three.classic.js:482,492`) and re-set exposure.
- **Acceptance:** M-10 readability floor and M-21 look metrics.
- **Pipeline fit:** optionally render the unused `weapons/gravedigger-lantern-pixelated.glb` as the visible lantern.
- **Economy:** **yes.** The lighting family becomes visible and becomes the look of every screenshot.

**P0-4 · Render at an internal resolution with a point-sampled upscale (S).**
- **Evidence:** `game.js:34-36,750-755`; `style.css:18-22`; `31:143-145`; `29:73-75`; `arsenal-viewer.template.html:169-180`.
- **Change:**
  - Add `CONFIG.renderer.internalHeight` (540 or 720).
  - Call `setPixelRatio(1)` and `setSize(round(h·aspect), h, false)` on boot and on resize.
  - Add `image-rendering: pixelated` to `#wh-canvas`.
  - The DOM HUD is unaffected, and the reticle maths stays valid because it uses window pixels (`game.js:372-373`).
- **Acceptance:** M-08 shows a lower frame time.
- **Pipeline fit:** screen pixels now match the baked 256/512 px Nearest texels.
- **Economy:** **yes.** This defines the marketing look.

**P0-5 · Fix world bounds, the camera and spawns (S).**
- **Evidence:** `region-manager.js:99-133`; `CONFIG.js:27,53,184-186,236-237`; `player.js:92,873-880`; `enemy.js:191-196`.
- **Change:**
  - Radially clamp player and enemies to `groundRadius − margin`, a CONFIG value.
  - Extend the *visual* ground to at least 1.1× the region's fog-opaque distance (A ≈ 200, B ≈ 100), scaling the texture repeat to keep texel density.
  - Clamp the camera to ≥ 0.4 units above the ground, with a maximum distance that depends on pitch.
  - Move spawn yaw into CONFIG, pointed at the content (`camYaw = 0` for A).
  - Add a boot-time validator: every prop and enemy must be on its home side and inside the playable radius. Fix the A ghoul's spawn to z ≥ −23.5, or make it a deliberate gate guard.
- **Acceptance:** M-13, M-15, M-16.
- **Economy:** no.

**P0-6 · Fix resource lifetime on region swap and actually pre-warm the GPU (S-M).**
- **Evidence:** `region-manager.js:365-384,388-413`; `three.classic.js:23422-23423,77841`.
- **Change:**
  - Tag template geometry, materials and textures `userData.whShared` at load. `disposeRegion` disposes only per-region resources (ground, mist, canvas texture).
  - During pre-warm, call `renderer.compile(group, camera, scene)` (`three.classic.js:77388`) and `renderer.initTexture()` (`:79537`), spread over 2-3 frames.
- **Acceptance:** M-05 and M-06.
- **Economy:** no. It does enable more regions.

**P0-7 · Load the v3 pixelated bodies (S).**
- **Evidence:** `assets.js:6-7,44-46,181`; `regen_pipeline_v3.py:13-15,77-83`; `SPIKE-LOG.md:318-328`.
- **Change:**
  - Point the three MANIFEST entries at `races/<name>-pixelated.glb`.
  - Correct the stale comments in `assets.js` and the prototype README.
  - Record that this supersedes D4b-3.
- **Pipeline fit:** this is exactly the user-approved "pixelation of the colors on the skin" output.
- **Economy:** **yes.** The character is where weapon and armor families are displayed.

### P1: major quality

**P1-1 · Blob contact shadows for actors (S).**
- **Evidence:** `CONFIG.js:12`; `02-art-style.md:27-29,60-61`; `player.js:757-770`.
- **Change:** one shared CircleGeometry with a radial CanvasTexture and a MeshBasicMaterial (transparent, no depth write, polygonOffset), fixed at y=0.02 under each actor's x/z and not bobbed. It fades and shrinks as the root rises (hop, death).
- **Economy:** partial.

**P1-2 · Landmark and skyline system (M).**
- **Change:**
  - Sky dome: a BackSide sphere with a gradient ShaderMaterial (fog off, no depth write) whose horizon colour equals the fog colour.
  - Moon Sprite with an additive halo, aligned with the moon light.
  - 2-3 silhouette cards (alpha-tested) at 0.8-0.9× the fog-opaque distance. The Veil Spire goes north, left unlit in Darkwood so the single amber accent survives (`24:55`); a fir-line card beside it.
  - Physical landmarks: in **B**, assemble a ruined chapel at the forest centre from church-kit pieces already on disk (wall-window, buttress, roof beam, window frame, archway, altar, pulpit, pews), lit by the candelabra. In **A**, a lit gate or mausoleum at the chokepoint.
- **Economy:** **yes** (screenshot heroes).

**P1-3 · Make the chokepoint physical, show the neighbour, and crossfade the swap (M).**
- **Evidence:** `CONFIG.js:186,192`; `region-manager.js:293-299,358`; `game.js:422-430`.
- **Change:**
  - Place the m1 cemetery gate plus iron-fence runs along the plane as the visible wall, with 2 lit lantern posts.
  - Split the ground into half-planes or one shared ground, so the pre-warmed neighbour's props can render as fogged silhouettes (enemies hidden) without z-fighting.
  - Crossfade fog colour, fog density and light values over ~1.5 s.
- **Acceptance:** M-22.
- **Economy:** partial.

**P1-4 · Prop colliders, camera collision and occluder fade (M).**
- **Change:**
  - Per-asset collider metadata: a base circle from the bbox footprint, or "none" for moss and brambles.
  - Resolve it with the existing circle push-out code.
  - Raycast from the camera target to the camera against collider cylinders and pull the camera in.
  - Fade occluding trees with `material.alphaHash` (r185) on per-instance material clones.
- **Acceptance:** M-14.
- **Economy:** partial. Camp placement needs these footprints.

**P1-5 · Triangle budget: LOD plus submit-time targets (M).**
- **Evidence:** `59:122-130`; `31:150`; `SPIKE-LOG.md:329-331` (decimation parked "until a game-side LOD pass is needed"); `meshy_driver.py:28-35`; `three.classic.js:22093`.
- **Change:**
  - Add a `THREE.LOD` per biome asset: LOD0 is the raw mesh as-is out to ~20 units; LOD1 is ≈25% of the tris; LOD2 is ≈8% or an impostor card beyond ~60 units.
  - Produce LOD1 and LOD2 either (a) by re-submitting the same reference to Meshy at a lower `target_polycount` (15 credits each, no local geometry processing), or (b) by offline decimation of rigid props only. Option (b) needs a Nicko ruling under the v3 directive.
  - Submit new scatter assets with `topology: 'triangle'`, or with quad at half the desired triangle count.
- **Economy:** indirect yes (leaves room for decor density).

**P1-6 · Consistent shading and texture style across asset families (S).**
- **Evidence:** `add_normals.py:4-10,190-194`; `gltf-loader.classic.js:3549,3608`; `biome_pixelate.py:59-61`; `regen_pipeline_v3.py:47-57`.
- **Change:**
  - Run `add_normals.py`, which already welds at 1e-4, over the church-kit, graveyard, weapons and armor pixelated folders.
  - Switch the v3 and biome normal steps to the welded path.
  - Choose one texture style for kit props. The 46-run originals may be re-downloadable by task id through `meshy_driver.py dl` (`manifest:15-60`) **[INF-L]**.
- **Pipeline fit:** normal injection is explicitly kept (`SPIKE-LOG.md:322-323`).
- **Economy:** **yes** (weapon and armor families render consistently).

**P1-7 · Layered atmosphere (M).**
- **Change:**
  - Height fog through a global `ShaderChunk` fog replacement installed before the first compile, adding a world-Y falloff to the distance term.
  - Tint the fog toward the moon direction in the same chunk.
  - Replace the y=1.5 mist plane with 6-12 low, soft-alpha mist cards at varied heights.
  - Recede the fog while locked on (`24:362-363`).
- **Acceptance:** M-10 and M-17.
- **Economy:** **yes**.

**P1-8 · Light pools and emissive props (M).**
- **Evidence:** `CONFIG.js:64-65`; `arsenal-viewer.template.html:202,254,259,272,275`; `24:34-37` ("every light is a location").
- **Change:**
  - A fixed pool of **4 PointLights**, never added or removed, so the shader light count stays stable. Each frame, reassign them to the nearest light sockets (lantern posts, candelabra, chandelier, campfire, firebolt) and fade intensity on handoff.
  - Flame cards (MeshBasic, additive) and halo Sprites.
  - Small emissive glass meshes on the lantern posts.
- **Acceptance:** M-19.
- **Economy:** **yes, strongly.** Lighting is one of the eight decor categories (`11:117-121`).

**P1-9 · Post pass for the retro look: dither, grain, grade (M; needs P0-4).**
- **Change:**
  - Render into a WebGLRenderTarget at internal resolution (HalfFloat, Nearest).
  - One full-screen pass: tone map, sRGB, per-region lift/gamma/gain, 4×4 Bayer ordered dither, animated grain and vignette (`58:103` single-pass fusion).
  - With a render target bound, three.js does not tone-map (`three.classic.js:37702-37713`), so tone mapping must move into this pass.
- **Cost:** ≈0.3-1 ms at 1080p output **[INF-M]**, within the 2.5 ms budget (`31:148`).
- **Economy:** **yes**.

**P1-10 · Rest point as an identity space (M).**
- **Evidence:** `game.js:289-295`; `CONFIG.js:106,112-113,341`; `03:144-157`; `11:106-128`; `24:62-64,111-118`.
- **Change:**
  - At each spawn, build a lit rest site (campfire or tavern door) with a pinned light-pool slot, ember particles and existing props arranged around it. Respawn there.
  - Keep a safe radius ≥ 17.3 units (1.2× the ghoul chase trigger) by moving B's two ghouls.
  - This becomes the camp-decor showroom.
- **Economy:** **yes, strongly**.

**P1-11 · Ground detail and large-scale variation (M, after P0-2).**
- **Change:**
  - A low-frequency world-space macro texture to break the 15-unit repeat, or a per-tile hash rotation in `onBeforeCompile`.
  - A worn path strip from spawn to gate to landmark.
  - Low-roughness puddle decals that catch the lantern's specular, as in concept-01's wet ground.
  - Scatter from B6.
- **Acceptance:** M-11.
- **Economy:** partial.

**P1-12 · The "armed" emissive pulse is dead code (S; route to the weave owner).**
- **Evidence:** `game.js:202` checks `p.sword.material` on a Group (`assets.js:194`, `game.js:628-632`).
- **Change:** find the weapon's first mesh, clone its material once, drive its emissive, and test it on the mesh.
- **Economy:** yes (the same path will display weapon enchant and affix glows).

### P2: polish and future

- **P2-1 · Day/night colour script (M).** Keyframe every light, fog and grade uniform to the 24:1 clock (§5.4). Light counts stay constant, so there are no shader recompiles. Economy: yes (screenshot variety).
- **P2-2 · Character-only shadow map (M).** Actors cast, the ground receives; 1024² PCF; tight orthographic frustum following the player. An upgrade over P1-1. Economy: no.
- **P2-3 · Instancing (M).** `InstancedMesh`/`BatchedMesh` (`three.classic.js:24728,26142`) once any asset exceeds ~20 copies (scatter, fences). Needs per-instance colour for variants. Economy: yes (decor density).
- **P2-4 · Item light box (M).** A deterministic render stage based on the arsenal-viewer rig that produces Display images and turntables for the five WHItem families (`market.move:54-58`; `items.move:52`). Economy: **yes, strongly**.
- **P2-5 · Photo mode and hero cameras (S-M).** Hide the HUD and FPS counter, free camera, fixed hero framings per region. Economy: **yes**.
- **P2-6 · Ambient particles (S).** `THREE.Points` motes, embers, fireflies, leaves and ash with pixel sprites. Economy: yes.
- **P2-7 · Data-driven placement (M-L).** Per-region JSON plus per-asset metadata (native height, footprint, collider, light sockets, emissive mask, decor category, family id), a Poisson scatter tool with exclusion zones, and a viewer-based placement editor. Economy: **yes, strongly** (this becomes the camp placement system).
- **P2-8 · Hygiene (S).**
  - Share and dispose firebolt geometry and materials (`spells.js:33-38,79-85`).
  - Remove or wire up the dead CONFIG keys (`CONFIG.js:37-38,46,107,184-186,192`).
  - Drop the unused `ironFenceCorner` load.
  - Allow ETag caching of GLBs in dev.
  - Use FrontSide on closed props.
  - Update `asset-manifest.md` to cover all 139 files.
  - Economy: no.

---

## 5. Light-box deep dive

### 5.1 Current rig vs souls-like practice [BENCH]

| Layer | What souls-likes do | Witch Hunter now |
|---|---|---|
| Key | One sun or moon, with shadows, colour and angle authored per area; often backlights the route | High warm-white "sun" behind the camera, no shadows, the same in both regions |
| Fill | Low and tinted; darkness is allowed | Ambient + Hemisphere = 61-74% of irradiance |
| Light pools | Bonfires, lamps, torches and windows act as beacons and safe spaces | None |
| Emissive | Candles, embers, magic, windows | Two small unlit-material spheres; the armed pulse is dead |
| Fog | Height fog, distance fog, shafts, fog gates | One FogExp2 layer and one mist plane |
| Sky | Skybox, moon, silhouettes | Flat colour |
| Grade | Per-area LUT, vignette | ACES plus exposure only |
| Time | Time-of-day in parts of DS3 and ER; BB's global moon shift | Static |

### 5.2 three.js mechanisms and cost

Cost classes: **FREE** is CPU or uniforms only; **LOW** is under ~0.3 ms; **MED** is ~0.3-1.5 ms; **HIGH** scales with scene triangles or is over 1.5 ms. The millisecond figures are GTX-1660-class at 1080p **[INF-M]**.

| Mechanism | Class | Notes |
|---|---|---|
| AmbientLight to 0; HemisphereLight as the only fill | FREE | Fixes the "ambientLightLevel" semantics |
| DirectionalLight as a low, cool moon, placed to backlight the route | FREE | Gives rim light on the main path |
| Player lantern: `PointLight`, decay 2, distance cutoff | LOW | Adds one light to every lit fragment |
| Fixed 4-light PointLight pool with nearest-socket assignment | LOW→MED | Linear in light count; three.js has no light culling; a constant count avoids recompiles |
| Emissive meshes plus additive halo `Sprite`s | LOW | Transparent quads; no depth write |
| Tone mapping ACES → Neutral (7) or AgX (6) | FREE | Keeps dark albedo out of ACES's toe; less hue skew on the amber accent |
| Height fog and moon-tinted fog via `ShaderChunk.fog_*` override | LOW | Install before the first compile |
| Sky dome gradient, moon Sprite, silhouette cards | LOW | 1-4 draw calls |
| Mist cards (6-12) and light-shaft cards | LOW-MED | Overdraw; keep them thin and low |
| Blob shadows | LOW | polygonOffset, y=0.02 |
| Character-only shadow map | MED | Actors cast, ground receives |
| Fresnel rim on actors via `onBeforeCompile` | LOW | Matches the proposed stronger rim on hostiles (`24:360-361`) |
| Internal-resolution render (P0-4) | Saves cost | 4-16× fewer fragments |
| Post pass (render target + grade + Bayer + grain) | LOW-MED | Tone mapping moves into this pass |
| `scene.environment` from a tiny PMREM | MED | Optional; skip for the PSX look |
| Colour-script interpolation; fog keyed to lock-on | FREE | CPU only |

### 5.3 The single lighting change with the most mood per hour: the lantern-and-moon relight (P0-3)

It is one change with two halves that must ship together. A point light added on top of a 4.0 ambient does not read.

- **Fill:** remove the AmbientLight. The HemisphereLight becomes the only fill: indigo-slate sky (0x4a5a80 class), near-black ground (0x16181e class), and it is what `ambientLightLevel` scales.
- **Moon:** 0xa8bce6 class, 25-35° elevation, on the −z side.
- **Lantern:** `PointLight` 0xffb060 class at ≈6-8 cd, distance ≈12, decay 2, with ±5% flicker, attached to the player's left-hip anchor.
- **Tone mapping:** Neutral or AgX, with exposure re-set so the fog stays the brightest large area.
- **Targets (ratios, not absolutes; tune in play):**
  - Moon to fill on vertical faces: 3-5:1 (1.6-2.3 stops). Today it is 1.2-1.4:1.
  - Lantern pool: at least +1.5-2 stops over moonlight within 3 units, falling back to moon-only by ~6-10 units. With 7 cd, irradiance is ≈1.6 at 1.5 units and ≈0.14 at 5 units **[INF-M]**.
  - Gate the final numbers on the M-10 readability floor. The spike needed a brightened set to pass (`29:151-153`).
- **What it buys:** the concept-01 amber pool, the single-accent rule satisfied, a darkness gradient, and rim-lit silhouettes. It costs about a dozen CONFIG lines and ~15 lines in `game.js`.

### 5.4 Colour-script proposal (feeds P2-1)

Keyframes per region follow the 24:1 clock (`03:711-714`) and the "every place exists twice" day/night rule (`24:43-46,105-108`).

| Keyframe | Moon / sun | Fill | Fog | Lantern | Accent |
|---|---|---|---|---|---|
| Night (default master) | Cool, low, backlit | Indigo, low | A slate-ash, B denser slate | On | Amber |
| Veil-charged night (`03:87-100`) | Dimmer, bluer | Lower | +30% density, bluer | On | Amber |
| Dusk / dawn edge | Warm and low, turning cool | Mauve-slate | Warm band at the horizon | Fading | Amber |
| Day ("honest grey-gold") | Grey-gold, higher, hard | Neutral grey | Pale ash; today's A value `0x9aa0a3` belongs here | Off | None or ember |
| Blight "wrong day" | Burned disc | Ash-violet | Ash grey | — | Blood-red |

- Lighting stays world-true for every player's alignment (`02:51-54`).
- The "danger half" of the day is signalled through HUD or grade cues, not by different lights per player.

---

## 6. Asset generation plan

- **Baseline:** the prior run produced 46 assets in ~2.5 h for 690 credits (`SPIKE-LOG.md:43-46`). The tree now holds 60 assets in 139 files.
- **Proposed plan:** a second run of the same size: **46 Meshy assets, 690 credits**, split across credit windows with the 700-credit cap and one retry per asset (`59:25-26`).
- **Order:** ranked by how alive the world feels per credit. If marketing needs decor screenshots first, move B4 ahead of B2 (B4 needs P1-10's rest space before anyone can see it).

| Batch | Contents | Count | Credits | Impact | Economy |
|---|---|---|---|---|---|
| **B0 Wire up what we own** | Crypt: chandelier, pillar, steps, sarcophagus, skull pile. Church-kit: candelabra, wall-window, window frame, roof beam, altar, pulpit, pew, iron corner. Weapons: gravedigger lantern (the player lantern mesh), round shield, greatsword. Plus the `races/*-pixelated` bodies | 17 | 0 | HIGH: landmark ruin, light pools, steps for height | Lighting-decor proof; gear display |
| **B-tex (not Meshy)** | Image-gen particle sprites (ember, mote, firefly, leaf, fog puff, ash), 3-4 skyline silhouettes, ground decals (puddle, path, ash) | ~14 textures | 0 | HIGH | Screenshots |
| **B1 Darkwood canon** | M10 bramble, M19 moss drape, M20 mud puddle, M21 gnarled roots (references already on dev, `59:133-147`) | 4 | 60 | HIGH (the canon frame's roots, moss and wet ground) | — |
| **B6 Low-poly scatter kit** | Bone scatter, leaf litter, pebbles, headstone fragments, mushroom cluster, fern/bracken | 6 | 90 | HIGH per credit | — |
| **B3 Landmarks** | Ruined spire or tower (skyline hero), mausoleum gate (A chokepoint), gallows, standing stones, lantern waymarker shrine, tavern door or rest shelter | 6 | 90 | HIGH (navigation) | Screenshot heroes |
| **B2 Harvest and encounters** | M11-M14 herbs, M15 bandit campfire (light socket), M16 bedroll, M17 witch totem, M18 mote shrine (emissive); approved in `59:102-109` | 8 | 120 | MED-HIGH (makes the gather loop visible) | Crafting inputs |
| **B4 Camp decor v1** | 2 per decor category (`11:117-121`): lighting (teal glass lantern, hearth brazier), banners (pole standard, wall banner with blank field), trophies (boar skull, pelt rack), rugs (2), furniture (table and stool, strongbox), shrines (light, dark), defenses (spike line, palisade), structures (small tent, lean-to) | 16 | 240 | MED | **Core: decor family (4)** |
| **B5 Gear variants** | Cloak, gloves, hood, belt lantern, satchel, light shield, plus scripted palette variants (doc 27 R4) | 6 (+N palette) | 90 | MED | **Core: weapon/armor families (0/1)** |

**Pipeline rules for these batches:**
1. Reference image → vision QA → Meshy image-to-3D, unrigged → v3 colour pass (512 px Nearest + 5-bit) → **welded** normal injection → commit raw + pixelated (`59:21-24`).
2. Set the triangle budget at submit time, not by local decimation. Quad topology produces ≈2× the target in triangles (`SPIKE-LOG.md:258-262,338-339`). Targets: scatter 1-3k (triangle topology); props, decor and gear 3-5k; landmarks up to ~30k for 1-2 instances.
3. Every asset gets a metadata sidecar (P2-7): native height, footprint, collider, light socket, emissive mask, decor category, family id.
4. Variants need per-instance materials or a palette-index uniform, because clones share materials (`assets.js:194`).
5. Characters and camp NPCs stay rigid, with procedural idles only. Gear attaches rigidly at measured anchors, as the arsenal viewer does (`asset-manifest.md:70-72`; `29:145-150`).

---

## 7. Measurement plan (Testerbot Playwright)

**Harness rules:**
- Use real CDP input for movement and camera.
- Read state through `window.WH_GAME` (`game.js:28`) and `WH_DEBUG`.
- Setup-only hooks (`WH_DEBUG.measure.*`: spawn a prop, set the camera) are measurement-only, not acceptance tests. Add them to the dev spec.
- Items marked **GPU** need a hardware-GL runner; SwiftShader results there are non-representative.

| ID | Measures | Method | Pass bar / record |
|---|---|---|---|
| M-01 | Prop grounding | `Box3` of every prop in `getRegionManager().groups[id]` → minY and sink ratio | After P0-1: \|minY\| ≤ 0.02 for all props. Baseline now ≈0.5 sink ratio |
| M-02 | Actor grounding | Body minY at idle (two-sided); maximum over a 2 s sprint; during the ghoul hop | Idle \|minY\| ≤ 0.02; record the peaks |
| M-03 | Corpse contact | Kill enemies, wait for the settle | \|minY\| ≤ 0.05 |
| M-04 | Scene budget | `renderer.info.render.{calls,triangles}` at 6 poses, plus an 8-yaw sweep in the B forest | < 1,500 calls, < 2M tris (`31:150`) |
| M-05 | Leaks | `info.memory.{geometries,textures}` and `info.programs.length` at boot, after 5 round-trip crossings, after 50 casts | Growth ≤ +2 |
| M-06 | Crossing spike (**GPU** for the size) | rAF timestamps, 60 frames before and 120 after each organic crossing | 0 frames > 33 ms (`31:157`) |
| M-07 | Load timeline | PerformanceResourceTiming per GLB, `preloadAll` resolve, first 10 frames, stand-in count; run on both origins | Record; 0 stand-ins |
| M-08 | Frame budget (**GPU**) | 10 s fixed-camera captures at 540p, 720p, DPR 1 and DPR 2 | p99 ≤ 16.6 ms on GTX-1660 / Steam Deck (`31:143-145`) |
| M-09 | Ground visible | Screen luminance in a 3-10 unit ring around the feet | After P0-2: mean ≥ 20/255, std-dev ≥ 4. Baseline ≈0-2/255 |
| M-10 | Fog readability | Enemy at 5/10/15/20/30 units; render with and without it to build a mask; Weber contrast | Record the distance where contrast drops below 25% (`24:353-358`), for exploration and lock-on fog |
| M-11 | Tiling | Autocorrelation of the ground at the projected 15-unit period | Record; decides whether P1-11 is needed |
| M-12 | Minification shimmer | 30-frame slow pan; temporal std-dev on ground pixels beyond 40 units | Lower after the mipmap fix |
| M-13 | Camera bounds | Organic max zoom + min pitch | Camera y ≥ 0.3 (math predicts ≈ −1.0 today) |
| M-14 | Camera occlusion | Scripted walk through the B forest; raycast camera → player chest | < 5% of frames occluded after P1-4 |
| M-15 | World edge | Walk south from A spawn for 60 s; check spawn view for a luminance step at the disc rim | Position stays within the radius; no visible rim |
| M-16 | Spawn validity | Every enemy on its home side and idle-stationary within 2 s | A's ghoul fails today |
| M-17 | Mist seam | Row-gradient spike at the projected y=1.5 line on trunks | Present now; absent after P1-7 |
| M-18 | Prop density tuning (**GPU**) | K ∈ {0, 25, 50, 100, 200} clones of oak, boulder and stump | ms per prop and the density cap at 60 fps; repeat after LOD |
| M-19 | Light-pool stability | Move and toggle pool lights | `info.programs.length` unchanged |
| M-20 | Footing feel | Log body minY and blob-shadow presence over sprint, roll and attack chain | Record maximum hover; tune `CONFIG.js:389-404` |
| M-21 | Look and marketing QA | Hero poses (A establishing, gate reveal, B ruin, rest point) at 1080p | Negative space 60-80% (`24:322`); exactly 1 accent-colour cluster (`24:325`); vision QA against `24:320-331` |
| M-22 | Crossing continuity | Background pixel across 30 frames of a crossing | No step > 3% per frame after P1-3 |

---

**Totals: P0 7 · P1 12 · P2 8 (27 recommendations).**
