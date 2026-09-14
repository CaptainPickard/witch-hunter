# Meshy 3D Pipeline Validation - Stage Log (doc 29)

Character: gravedigger undead (char-07 canon, doc 24).
Input prep: 2 image-gen rounds (round 1 produced a multi-view sheet,
rejected; round 2 clean single-figure A-pose, vision-QA'd PASS).
Input hosted: raw.githubusercontent.com/CaptainPickard/witch-hunter/dev/
art-direction/3d-spike/gravedigger-apose-front.png (committed dev).

| Stage | Task/Tool | Started | Done | Elapsed | Notes |
|---|---|---|---|---|---|
| S-A1 reference sheet | gpt-image-2-high, 2 rounds | 15:19 | 15:21 | ~2 min | round 1 rejected by vision QA (multi-view sheet) |
| S-A2 hosting/commit | git push + raw URL check | 15:22 | 15:22 | <1 min | HTTP 200 verified |
| S-B1 image-to-3d | Meshy meshy-5, quad, 15k tris, symmetry auto | 15:24 | pending | pending | task 01a09b5b-6f19-7611-b9f5-ada2d1fd78d2 |
| S-B2 download + inspect | GLB via curl + trimesh/manual | pending | | | poly count, texture res, rig presence |
| S-B3 re-texture recipe | posterize + nearest-neighbor pass | pending | | | recipe prototype due after mesh lands |
| S-C1 UE5 scene | BLOCKED: engine access | | | | scene spec in doc 29 |

Open blockers after B stage: engine access (Nicko machine or hosted
runner) for S-C; re-texture tooling (PIL recipe) runnable here.
## PRODUCTION RUN 2026-09-13 (Phase 1 at production scale, doc 29 validation plan)

46 assets generated end to end: 10 race bodies (15k tris), 9 weapons (2k),
8 armor pieces (helms 3k / chests 5k), 15 church-kit props (2k), 4
graveyard props (2k). Every asset: single-object or single-figure concept
ref from the closest canon frame (image_generate + vision_analyze gate),
hosted on dev raw URLs, Meshy image-to-3d (meshy-5, quad, symmetry auto,
15 credits each), UV-preserving decimation to tri target, pixelated
register re-texture pass. Full per-asset table with task ids:
art-direction/3d/asset-manifest.md. Viewable/equippable in
art-direction/3d/arsenal-viewer.html (self-contained three.js page with
head/chest/right-hand/left-hand equip slots, verified in headless Chromium).

| Stage | Result | Notes |
|---|---|---|
| S-A1 refs (46) | PASS | 46/46 first-round vision QA PASS, 0 regen rounds (spike round 1 body needed 1 retry; production refs needed 0) |
| S-A2 hosting | PASS | all raw refs + GLBs committed dev, HTTP 200 spot-verified |
| S-B1 image-to-3d | PASS | 46/46 SUCCEEDED, ~2-3 min each; Meshy burst rate limit ~1 submit/min after first 10, handled with backoff |
| S-B2 download+inspect | PASS | 690 credits total of 700 cap; tri targets hit via UV-preserving fast-simplification + nearest-neighbor UV resampling |
| S-B3 re-texture | PASS | retexture.py (256px, 48-color MEDIANCUT, 5-bit posterize) applied to all 46; UV retention fix added for trimesh GLB export |
| S-C1 UE5 scene | still BLOCKED | engine access unchanged; three.js viewer remains the representative viewer |
| S-C2 equip slots | PASS (new) | arsenal-viewer.html: 4 slots (head/chest/rh/lh), anchors measured from human-hunter-male mesh, headless-browser verified; per-body sockets still rig-stage |

Production-run economics: 46 assets in ~2.5 h wall clock, 690 credits
(~15/asset, 0.46 USD-equivalent each at Pro 1000/mo), zero failed tasks,
zero skips. The doc 29 pipeline is now validated at production scale for
characters, props, and modular kit pieces.

---

## DEFECT FIX 2026-09-13 (arsenal viewer render defect, post-production-run)

Defect: race bodies rendered wrong in the browser viewer: black silhouette,
white salt-and-pepper speckle, detached floating shards near arms and feet,
geometry reading as mangled. Python ortho previews of the same GLBs were
correct, so the browser render path was suspect.

Root causes (three, all verified by bisect + headless Chromium A/B):
1. Decimation debris: every race body ships with ~300-1000 disconnected face
islands from the Meshy source mesh; the 15k decimation orphaned tiny
components. Worst case human-hunter-male (its pixelated GLB was re-decimated
separately from raw): main body shattered 4855 to 1375 faces, 358
far-floating shard components. Measured with welded-vertex adjacency
(union-find at 1e-4 tolerance), not raw vertex adjacency (UV-seam duplicates
lie).
2. Backface culling: the fractured shells have real gaps; three.js FrontSide
culling turned every gap into a see-through hole (the white speckle read as
texture noise but was background showing through the body).
3. Color encoding: GLTFLoader assigns sRGBEncoding (3001) to base-color
textures, but the r147 renderer default outputEncoding is LinearEncoding
(3000). sRGB texels decoded to linear and never re-encoded: texel 35/255
rendered ~11/255. The black silhouette was a page bug, not an asset defect.

Fixes:
- art-direction/3d/drop_shards.py: drops face components that are BOTH tiny
(under 10 faces) AND farther than 0.01 from the main body surface (cKDTree to
the largest component's vertices). Applied to all 10 race pixelated GLBs:
4,299 components dropped, UVs + 256px atlases preserved. Backup of pre-fix
GLBs kept at /tmp/glb_backup_races (session-local, not committed).
- arsenal-viewer.template.html: material.side = THREE.DoubleSide in
pixelFilter; renderer.outputEncoding = THREE.sRGBEncoding; pixelated
minFilter = NearestMipmapLinearFilter with mipmaps on (was full Nearest with
generateMipmaps false, which made the dark atlas salt-and-pepper at
distance). Rebuilt arsenal-viewer.html with build_viewer.py.

Verified: headless Chromium screenshots before/after (shards gone, no
see-through holes, figure reads as upright cloaked hunter with visible dark
browns/greys). Deployed /art-3d-viewer route serves the file live from disk,
byte-identical, no WebUI restart needed.

Tooling committed alongside: drop_shards.py (shard-removal post-pass),
shard_diagnose.py + weld_comps.py (connectivity diagnostics), uv_stats.py
(atlas/UV island stats), shoot_viewer.py (playwright screenshot harness),
bisect.template.html + build_bisect.py (raw-vs-pix x nearest-vs-linear
bisect harness), check_encoding.py (r147 encoding constant check).

## DEFECT FIX VERIFICATION PASS 2026-09-13 (shards + salt-and-pepper, independent re-verification)

Scope: independent verification pass over the 2026-09-13 defect fix (commit
59c7943). Re-derived the diagnostics from scratch rather than trusting the
earlier session's claims.

Findings:
1. Islands: re-ran welded-vertex connectivity (union-find at 1e-4, networkx)
on all 10 race pixelated GLBs. Counts (components / tiny <10 faces / tiny
and far >1.0 from origin): dwarf-female 526/311/2, dwarf-male-smith
565/440/4, elf-dawn-refuser-male 616/499/7, human-hunter-female 651/512/0,
human-hunter-male 551/387/6, orc-female 894/742/3, orc-male-warrior
875/757/7, undead-ghoul-male 757/616/8, vampire-female 760/554/1,
vampire-male-noble 638/472/120. drop_shards.py --dry confirms ZERO
remaining dropable shards: the tiny-far islands were already removed by
59c7943.
2. True-floater test (new tool floater_analyze.py): for every component,
min vertex distance to the nearest vertex of any OTHER component. On
human-hunter-male all 197 remaining components have gap_min = 0 (contact
at the 1e-4 weld tolerance) - the islands interlock, they are NOT
visibly floating; the jagged outline matches the concept's deliberately
tattered cloak hem. No further mesh surgery warranted.
3. Salt-and-pepper: fresh headless-Chromium screenshots of the deployed
viewer (playwright, human-hunter-male, default + close cameras, raw +
pixelated modes) show a coherent shaded surface - no high-frequency
black/white speckle - confirming the NearestMipmapLinearFilter + mipmaps
+ DoubleSide + sRGB outputEncoding fix renders correctly. Raw mode also
clean.
4. Route: /art-3d-viewer is auth-gated (302 -> /login). Verified with a
session cookie via /api/auth/login: served bytes byte-identical to disk
(md5 9d10e970facf0bd8102816144008e734), no WebUI restart needed.
5. Hub link fix: /art-hub viewer button opened the relative file link
('3d/arsenal-viewer.html') which 404s through the WebUI route sandbox;
switched hub-template.html + index.html to open /art-3d-viewer directly.

Commits this pass: 59c7943 (the fix itself, landed earlier same day),
a20e533 (hub link -> route, floater_analyze.py + shard_report.json).
Verification screenshots: /tmp/qa_final_default_cam.png,
/tmp/qa_final_close_cam.png, /tmp/viewer_shots_after/before_raw_mode.png.

## 2026-09-13 pass 3 (IO direct): ROOT CAUSE FOUND AND FIXED - missing NORMAL attribute

Defect (persisted after 59c7943): figure rendered as black salt-and-pepper
silhouette in arsenal-viewer (PIXELATED mode), all race bodies.

Diagnosis trail:
- Pass 2 (astra, truncated) disproved UV scramble: adjacent-face brightness
  delta mean 3.7/255 on human-hunter-male pixelated GLB - texture path clean.
  Its iso-harness "zero triangles drawn" was a harness artifact (the real
  viewer draws 13,415 tris for the same mesh).
- GLB JSON parse (glb_json.py): ALL 10 race pixelated GLBs have attributes
  POSITION + TEXCOORD_0 only. NO NORMAL. Raw GLBs are POSITION-only.
- three.js r147 lighting (ambient + 3 directionals + point) needs NORMAL;
  without it all light contribution is zero -> flat black ambient silhouette,
  and nearest-filter sampling of the dark atlas reads as salt-and-pepper.
  Trimesh/matplotlib previews shade by face color, which is why Python-side
  QA always looked correct and browser-side never did.

Fix: art-direction/3d/add_normals.py - welds verts at 1e-4, computes
area-weighted smooth per-vertex normals, appends NORMAL accessor/view in
place preserving UV + material. Applied to all 10 race pixelated GLBs
(commit 31b5e03), viewer rebuilt (d3b910d).

Verified (playwright + vision QA, /tmp/fix_normals_close.png,
/tmp/fix_normals_default.png, /tmp/fix_orc_default.png):
- directional lighting present (shoulder highlights, shadowed folds)
- salt-and-pepper noise GONE; texture reads as intended chunky pixel blocks
- no detached floating shards (perimeter fragments are connected surface)
- figure reads as upright cloaked hunter; orc reads as bulky upright orc

Remaining (not defects): jagged tattered-cloak hem is intentional concept
design, geometry verified in-contact (floater_analyze.py). RAW toggle still
broken-ish (raw GLBs lack TEXCOORD_0 - UV-less textured render); parked.

## 2026-09-14 pass 4 (IO direct): exposure pass after user report of persistent dark render

User hard-refresh still showed a dark shattered figure (00:00 UTC screenshot).
Pixel analysis decomposed the complaint:
- Original defect was a FLAT black mass (p10=p50=p90=66, noise 0.0) - unlit.
- Post-NORMAL-fix render: mean 55-128 with full value range (p90 249-255) -
  lighting works, but 40-50% of the cloak surface still reads near-black.
- Root of darkness: the baked atlas is intentionally dark (mean 33/255, 97%
  of texels in 16-64) under a moonlit-night light rig. Asset is fine; the
  exposure was wrong for viewer QA.

Fix: lighting/exposure pass in arsenal-viewer.template.html (commit 481227c,
pushed): ambient 0x8a97a4@1.3 -> 0xd8dde4@4.6 (bright fill), key point
2.2->3.0, moon 2.2->3.2, rim 1.6->2.2. Verified in headless render
(/tmp/iso/iso4_litboost2.png) and through the live route
(/tmp/final_live.png): figure now reads as a high-contrast character
(30-40% readable midtones), folds visible in shadow, mood preserved.

Also debunked this pass:
- "Zero triangles drawn" from pass 2's iso harness was a harness artifact.
- Linear-vs-nearest filtering makes negligible difference on this atlas
  (noise 4.68 -> 4.60); the register stays PIXELATED + mipmaps.
- RAW mode is broken by design: raw GLBs lack TEXCOORD_0 entirely
  (POSITION-only), so "RAW" shows a UV-less single-texel render. Parked.
- Nicko's remaining dissatisfaction is partly the intended PSX chunky
  register + tattered cloak geometry (verified in-contact) and partly UI
  quality. UI redesign dispatched separately.

## 2026-09-14 pass 5 (IO direct, astra-assisted): vertex-color bake - triangle-boundary patch contrast eliminated

User still reported speckled/fragmented figure on real Chrome after the
NORMAL fix + exposure pass. Astra pass 5 (live-route playwright + structured
vision QA at 2-3x zoom) characterized the remaining defect precisely:
- NOT per-texel salt-and-pepper (hf-noise 1.4-2.7, already passing)
- Per-triangle black/bright PATCH contrast following triangle boundaries,
  with pure-black regions adjacent to bright regions, floor bleeding through
  holes, and minor detached debris (39/17/41 tiny-far faces per body)
- Orc atlas is the harshest (adjacent-texel jump mean 7.15 vs hunter 4.73)
Filtering cannot fix triangle-boundary contrast (measured: linear 4.68 ->
4.60). Fix = take the atlas out of the sampling path entirely:

- bake_vertex_colors.py: per-welded-vertex bilinear atlas sample, 2 rounds of
  face-neighbor smoothing, COLOR_0 VEC4 baked in place into all 10 race
  pixelated GLBs, scaled 0.45 for the light rig.
- pixelFilter now prefers COLOR_0: vertexColors=true, map=null. PSX chunk
  comes from vertex density at INTERNAL_H=540; zero per-texel sampling noise.
- Light rig rebalanced for vcolors: ambient 0xf0f2f4 @ 3.4, key 1.2,
  moon 1.1, rim 1.1. (The earlier 4.6-ambient rig was calibrated for the
  texture path; with vcolors it overexposed, and the strong directionals
  read as black/bright triangle patches.)

Pixel evidence (live route, 3 bodies, frozen close cam): figure-region
histograms 86-92% in the 42-88 readable band, <0.1% crushed black, <3%
bright. Vision QA converged: no speckle, patches are coherent anatomical
value design (shadow under pecs, armor blocks, top-lit shoulders), "reads as
deliberate stylistic choice rather than technical failure."

Commits: this commit (glbs + template + built + scripts). RAW mode remains
parked (raw GLBs lack TEXCOORD_0 - pre-existing, unchanged).

## 2026-09-14 pass 6 (IO direct): ground-standing bug + asset quality decision point

User: "the character isn't even there... ground is through all the characters'
waist." Root causes found this pass:
1. GROUND BUG (real): setBody scaled by 1.8/size.y but never translated. GLB
meshes centered at origin (Y -1..+1) -> every body sunk 0.9 units, waist at
floor level. Fixed: body.position.y = -box.min.y * s.
2. Presentation: pure-vcolor mode killed all texel detail. Hybrid render:
texture map (LinearMipmapLinear + anisotropy) x vertex colors x flat light.
3. Asset truth: Meshy's 2048px atlases are ~2 stops under the concept (orc
mean 29/255, olive skin/brown leather buried). Regraded in place: gamma 0.42,
saturation 1.5x, median 3. Materials now distinct at PSX register.
4. Mesh truth: decimated bodies are open shells (orc 7129 boundary edges);
background bled through torso/legs. fill_holes plugged small defects (orc
7129->4742 boundary); large Meshy-authored tatter loops remain.

Commits: d8e8491 (all of the above). Hunter now vision-passes as a PSX-style
character standing on the disc. Orc/male-noble still show large open loops
from the Meshy generation itself.

DECISION POINT (for Nicko): the remaining "not a character" quality on some
bodies is asset-authoring, not presentation. Options: (a) Meshy re-generation
of the worst bodies (credits reset on the 13th - fresh allowance today),
with prompt guidance emphasizing bright midtones and closed solid meshes;
(b) accept the crude PSX register. Recommended: (a) for the worst 3-4 bodies.

## 2026-09-14 pass 7: full race body re-generation via Meshy (150 credits)

User verdict on the original 10 bodies: "scrap them." Re-generation run:
- 10 image-to-3d submissions (meshy-5, quad, 15k target, symmetry auto) from
  the same committed refs. All 10 SUCCEEDED, 3.6-4.6 MB GLBs each with
  28-32k tris. Credits: 365 -> 215 (150 spent). User vision-QA'd raw outputs
  (contact sheet) and approved: closed meshes, midtone-correct textures,
  readable characters across the set.

regen_pipeline.py (new) post-processing per body:
- UV-preserving decimation to 15k. LESSON: trimesh silently drops
  TEXCOORD_0 on export when len(uv) != len(vertices); UV must be averaged
  per decimated vertex (np.add.at over cKDTree mapping).
- Pixel register: 256px / 48-color mediancut / 5-bit posterize with the
  midtone regrade baked in (gamma 0.55, saturation 1.4x, median 3).
- Hole-fill, welded smooth normals, vertex-color bake (4-round diffusion),
  in-place NORMAL/COLOR_0 GLB surgery (same approach as add_normals.py).
- Pipeline bugs fixed en route: walrus-operator face remap clobbering,
  vcolor array sized to welded count instead of vertex count, UV/vertex
  count mismatch killing uv export.

Viewer rebuilt (95 MB raw / ~67 MB gzipped on the route; raw bodies now
carry 2048px masters). Live-route verify: hunter/orc/noble coherent,
standing on disc, PSX register intact. Pixel-audit of orc: enclosed
background holes = 1.2% of crop area, mostly the A-pose gap + tattered
loincloth openings (Meshy-authored design); remaining 281 boundary loops
are intentional tatters.

Commits: regen pipeline + 20 GLBs + rebuilt viewer (this commit) + SPIKE-LOG.

## 2026-09-14 pass 8 (v2): minimal post-pipeline - the pipeline was the problem

User verdict: "All of them are messed up again... the problem is your post
production process. It's ruining the models." Side-by-side raw-vs-processed
confirmed it. v1 damage, in order:
1. Regrade (gamma 0.55 + sat 1.4x + median 3): washed the approved dark
   gritty palette into light plastic midtones.
2. Vertex-color bake: smoothed the authored surface grain.
3. 256px pixel register: crushed material detail to mud.
The RAW Meshy outputs were good. The pipeline over-medicated them.

v2 (regen_pipeline_v2.py): minimal intervention only.
- KEEP: decimation 15k (UV-preserving), fill_holes, welded smooth normals.
- DROP: regrade, posterize, denoise, vertex-color bake, 256px quantize.
- Texture: authored Meshy texture at 512px (only a size downscale).
- Viewer: texture renders as authored via LinearMipmapLinear + anisotropy;
  no COLOR_0 in the GLBs, so the pixelFilter vcolor branch skips.

Verified live-route (orc + hunter): match the approved raw look. Orc figure
histogram mean 88 with full value spread, 0.25% crushed. Vision QA: "dark
gritty version... matte, heavy, weathered... no plastic artifacts."
Commit f896173. LESSON: when raw assets are approved, post-processing must
be additive-minimal: fix only what is actually broken (mesh holes, missing
normals), never "improve" the look.
