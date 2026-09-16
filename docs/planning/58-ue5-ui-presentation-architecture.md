# 58 - UE5.8 UI/HUD & Presentation Architecture Spec

Drafted 2026-09-16, UE5.8 UI and presentation architecture spec (doc 31 engine plan governs). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions, not edits.

Scope: the UI/HUD & PRESENTATION module only. UMG HUD minimum, the sprite/billboard stack, layered equipment presentation, the pixel register material + post-process chain, and the GLB import pipeline wiring. This doc authors engine structure, not look-and-feel invention: doc 24's art bible (LOCKED 2026-09-12) and doc 29's bake-off results govern the look; doc 53 owns core structure; doc 54 owns combat internals; doc 30 owns the remote operating manual. No gameplay content. GAS stays deferred (doc 31); nothing here adopts it.

Inherited conventions (doc 53, not re-decided): WH/FWH/EWH naming prefixes; /Game/WH/ folder law; UWHDataRegistry is the only DataTable reader; tick groups per doc 53 section 2.4; PROPOSED on every invented number or name in this doc.

## 1. UMG HUD MINIMUM

Doc 31 IN list: "the HUD minimum (health, stamina, poise, boss bar, target reticle)". Slice 1 builds exactly that set plus the two locked doc 35 presentation rulings that are HUD-structural. Nothing more.

### 1.1 Widget class map

All Widget Blueprints under /Game/WH/UI/ (doc 31 folder plan; doc 53 naming: `WBP_WH` + name). Base user widget C++ classes in Source/WHGame/UI/ where logic is code, not layout (PROPOSED split, standard UMG shape).

| Widget | Class (PROPOSED) | /Game/WH/ path | Binds to | Cites |
|---|---|---|---|---|
| WBP_WH_HUD | UWHHUDWidget (root container) | /Game/WH/UI/WBP_WH_HUD | composition root only | doc 31 UI folder |
| WBP_WH_Health | UWHHealthWidget | /Game/WH/UI/WBP_WH_Health | player health attr (doc 33 formulas) | doc 31 IN list |
| WBP_WH_Stamina | UWHStaminaWidget | /Game/WH/UI/WBP_WH_Stamina | stamina pool (doc 33) | doc 31 IN list |
| WBP_WH_Poise | UWHPoiseWidget | /Game/WH/UI/WBP_WH_Poise | poise meter (doc 33) | doc 31 IN list |
| WBP_WH_BossBar | UWHBossBarWidget | /Game/WH/UI/WBP_WH_BossBar | boss encounter state hook (UP-5) | doc 31 IN list |
| WBP_WH_Reticle | UWHReticleWidget | /Game/WH/UI/WBP_WH_Reticle | lock-on/aim state (doc 32) | doc 31 IN list |
| WBP_WH_DamageNumbers | UWHDamageNumbersWidget | /Game/WH/UI/WBP_WH_DamageNumbers | damage pipeline events (doc 54) | doc 35 G11 ruling 2 (LOCKED) |
| WBP_WH_Focus | UWHFocusWidget | /Game/WH/UI/WBP_WH_Focus | Focus attr (reserved hook) | doc 35 G11 ruling 3 (LOCKED) |

Slice 1 ships the first six; WBP_WH_Focus is a structural reservation only (doc 35: hidden for non-casters, renders when Focus first becomes relevant; magic is OUT of slice 1, doc 31). No widget outside this table enters slice 1.

### 1.2 Data-binding contract (interface level)

Binding is PULL in tick group 5 (doc 53 section 2.4: PostUpdateWork is the save/UI read slot; "HUD pull (doc 58)" is named there). Structure (PROPOSED):

- One C++ interface `IWHHUDDataSource` (PROPOSED) implemented by AWHPlayerCharacter (health/stamina/poise reads, doc 33 stat formulas) and by the boss-bar provider. The HUD root holds a TScriptInterface to the source; no widget reaches into UWHCombatComponent internals (doc 54 owns those; this doc owns only the read surface).
- Event pushes are edge-only: combat entry/exit, boss encounter start/end, damage-number events cross as delegates declared on the interface (PROPOSED signatures: `OnDamageNumberRequested(FWHDamageNumberEvent)`, `OnBossEncounterActive(bool)`). Payloads carry display-ready ids and numbers already derived by doc 54's pipeline; the HUD performs no combat math (doc 54 section 3 owns calculators).
- FWHOnAxisChanged (doc 53 delegate, "HUD + AI consumers") remains the faction-axis read path; the slice HUD does not render axis meters (OUT, doc 31).
- No presentation beat writes ledger cells. The HUD is read-only over the subsystems (doc 53 section 2.2); nothing in this module writes save state.

### 1.3 Input-context-driven visibility (doc 32 contexts)

Contexts: `Exploration`, `Combat`, `Delve` (EWHInputContext, doc 53 section 3.2; doc 32 names the play surfaces, Delve enters via doc 47). Visibility rules (PROPOSED wiring of locked sources):

- WBP_WH_HUD root: active in all three contexts (meters are always-on, doc 31 IN list).
- WBP_WH_Reticle: rendered on aim-mode entry (dual-mode stationary reticle, Alt hold or C, doc 32 binding table) and on lock-on (fade-in 0.15 s / 9 f, doc 32 section on reticle). Hidden in plain Exploration with neither active.
- WBP_WH_BossBar: active only while a boss encounter is flagged live; the flag source is the doc 56 encounter wiring via the interface delegate (UP-5). It never renders from a hardcoded level check.
- WBP_WH_DamageNumbers: context-independent; gating is by damage direction (doc 35 G11: ON for player hits, OFF for incoming), not by context.
- Context transitions arrive as edge events from AWHPlayerController's context stack (doc 53 section 3.2); the HUD subscribes and toggles visibility actors, it never polls input state.

### 1.4 HUD-minimum acceptance hooks (doc 31 acceptance test)

The doc 31 acceptance gate (5 external viewers, 60 fps, night conditions; verb-type read within 250 ms; die-twice-to-boss without instruction; "weighty" unprompted) puts these obligations on the HUD:

- The HUD must not occlude the target silhouette band at the doc 28 COMBAT register (player reads 15-25 percent frame height, doc 29/28); meters anchor to screen edges, PROPOSED safe-zone margins reserved as tunable constants, not art.
- The reticle must resolve the locked target within the 250 ms read window's latency budget: reticle visuals are bound to the same lock-on frame index the doc 53 bridge stamps (section 3.3 there), so no extra smoothing pass delays it (PROPOSED; verified by T58-02/T58-07).
- Death/respawn and potion-drink flows (doc 31 IN list) surface only through existing widget state; no new HUD beats are invented for them.
- Boss bar presence is required for the optional boss remix path (doc 31 IN list); its cut at the M4 checkpoint must degrade to "widget absent", not "widget erroring" (test T58-01 covers both stances).

## 2. SPRITE/BILLBOARD STACK

Carrier ruling first (it reorders the source docs): doc 29 RESOLVED 2026-09-13 (Nicko) - the game is a TRUE 3D world; low-poly pixelated 3D meshes are the character/prop carrier; docs 25/26/27 production specs are demoted to REFERENCE (kept for palette law, QA methodology, lessons). Doc 27's layered paper-doll system itself remains LOCKED as the equipment presentation MODEL (D1/D2/D3 approved, and its build-order step 5 already names the UE5 shape). This section authors the UE structure that carries that model on the 3D carrier, and states where billboards still exist.

### 2.1 Layered paper-doll as UE slot components

Doc 27's runtime model (a stack of layers at one anchor, equip = swap what a slot reads) maps to UE as (PROPOSED structure, doc 27 semantics):

- One AWHCharacterPresentationActor (PROPOSED class, /WH/Characters/ shared) owning the layer stack: a base skeletal mesh component (the body) plus one child USkeletalMeshComponent (or UStaticMeshComponent for rigid pieces) per EQUIPMENT SLOT.
- Layer classes carried verbatim from doc 27's amendment (LOCKED 2026-09-13):
  - CANON LAYERS (always on, part of the body look, never toggleable): linen base, leg harness, faulds, gorget. In UE these are body sub-meshes, not slot components; race-card bodies ship in neutral under-layers (doc 27 D2, R1).
  - EQUIPMENT SLOTS (swappable at runtime): cloak/back, gloves, chest, helm/head, weapon, plus FX overlay reserved. These are the fashion-expression surface (doc 27 section 2 layer list).
- Identical anchor contract (doc 27 R2): every piece is rigged to the SAME skeleton, attached at the SAME sockets (doc 29 KNOWN ISSUES 3: "sockets defined once per rigged skeleton, not per piece"). Socket names are section 4.3's contract.
- Equip swap = attach/detach + material swap at the slot component, no regeneration, no pipeline run (doc 27 section 2; doc 29 S-C0 PASS proved exactly this shape: separate helmet mesh attached to/detached from a head anchor at runtime).
- Occlusion rule (doc 29 KNOWN ISSUES 1, confirmed in-engine): bodies ship as REGION SUB-MESHES (skull/hood, torso-soft, torso-armored, limbs, robe-skirt); a slot piece that covers a region hides the soft sub-mesh under it. The slot table maps piece type to hidden regions (PROPOSED DataTable DT_WHEquipmentVisuals, columns: PieceId, SlotClass, HiddenRegions, ZOrder; authored per doc 27's z-order table need, no gameplay stats in it).

### 2.2 Material stack and palette variants

- One pixel register material function (MF_WHPixelRegister, section 3.2) is the base of every piece's material stack (doc 31 /WH/Art/Materials folder purpose).
- Each equipped piece gets a Material Instance Constant of the layer material; palette variants (doc 27 R4: fashion tiers via palette swaps, NOT new art; steel/iron/blacksteel/cold iron for armors, cloth dyes per biome signature) are MIC parameter-block overrides on that function (PROPOSED parameter layout; doc 29 confirms "variant palettes are near-free on shared geometry").
- Quality bar carried (doc 27 R5): pieces match the approved register; QA is the doc 29 re-texture vision QA, not a new bar. This doc invents no palettes; variant colors come from doc 24's palette law only.

### 2.3 Billboard vs mesh stance per asset class

| Asset class | Carrier | Stance | Cites |
|---|---|---|---|
| Characters (player, bandit, wolf, boss) | low-poly 3D skeletal mesh, pixelated textures | mesh, never billboard | doc 29 RESOLVED |
| Props/kit (graveyard, church, crypt) | GLB static meshes | mesh | doc 29, doc 30 Phase 2-3 |
| Equipment pieces (helm, shield, weapons) | GLB meshes at sockets | mesh slot pieces | doc 29 S-C0, doc 27 step 5 |
| HUD sprite consumers (icons, reticle art) | Paper2D sprites in UMG | sprite, HUD-only | doc 53 module table: "Paper2D - HUD sprite consumers, doc 58 - stock" |
| Sprite atlases (8-direction turnarounds, race-card bodies) | reference material only | NOT imported for slice 1 runtime | doc 29 demotion clause |

Billboard-vs-mesh is therefore not a per-asset open choice: the doc 29 ruling fixed it by class. The billboard material path from doc 25 S7 stays a REFERENCE recipe; no runtime billboard components enter /Game/WH/ for slice 1 (UP-4 records the retirement scope). Should a future ruling re-introduce billboards (e.g. doc 08's carried "boss/colossal sprite treatment" and "runtime perf budget for hundreds of billboard sprites" opens), this section's slot-component anchor contract is the point they plug in; nothing here pre-builds them.

### 2.4 Slice-1 equipment presentation scope

Doc 31 OUT: "equipment mechanics beyond one sword + one shield visual". Slice 1 builds: the body (human hunter, doc 26 human-lock via doc 31), one Long Blade piece, one shield piece, at hand sockets (doc 54 weapon class slice: LongBlade built fully, doc 54 section 4). The slot-component structure is built NOW so later pieces are data, not code (doc 27 build order step 5). No armor-tier content (doc 40) enters slice 1; its presentation arrives through the same slot table.

## 3. PIXEL REGISTER POST-CHAIN

Doc 29's register stack, as UE post-process. Folder: /WH/Art/PostProcess (doc 31); materials in /WH/Art/Materials (doc 31). Scene placement and per-level lighting live in /WH/World (doc 31); this doc owns the material/post stack structure only.

### 3.1 Render target chain

- RENDER TARGET: scene renders at 720p internal, upscaled point-sampled to 1080p output (doc 31 G23 locked target: "60 fps locked at 1080p output, 720p internal point-sampled upscale"; doc 02 scaling law via doc 29). UE shape (PROPOSED): a post-process material sampling a downsampled scene texture with nearest-neighbor filtering (t.2darray/T2DPoint-compatible sampler state, PERCENTAGE sampling OFF), driven from a scene-capture-free path: r.ScreenPercentage set to 66.7 (720/1080) plus a nearest-neighbor upscale post material, PROPOSED as the cheapest engine-native route, validated at M1 (doc 31 milestone M1 "register in-engine").
- DITHER: ordered dithering as a post-process material stage (doc 29 scene spec; doc 24 mood register: "checkerboard dithering in gradients"). PROPOSED: 4x4 Bayer matrix in MF_WHPixelRegister's post variant, applied in the same pass as the upscale to avoid a second full-screen pass (PROPOSED single-pass fusion; budget per 3.4).
- GRAIN: film grain over everything (doc 24 mood register LOCKED line; doc 29 scene spec). PROPOSED: animated grain texture in the same post material, one asset.
- POST VOLUME: one post-process volume per level owns the chain; the shared settings live in a PostProcessData asset under /WH/Art/PostProcess/MMP_WHRegister (PROPOSED asset name), instanced by WH_Arena_Darkwood (doc 31 world folder). No per-actor post overrides in slice 1.

### 3.2 Pixel register material function (mesh side)

The re-texture recipe proven in doc 29 (S-B3 PASS, "scripted PIL pass... zero per-body manual work") splits build-time vs runtime:

- BUILD TIME (offline, on the VPS, doc 30 loop): 256px downsample, 48-color MEDIANCUT quantize, 5-bit posterize (doc 29 S-B3 exact recipe; scripts in art-direction/3d-spike/scripts). Output: palette-locked PNG per material zone.
- RUNTIME (in-engine, MF_WHPixelRegister, PROPOSED node inventory): nearest-neighbor sampling (mipmaps OFF, doc 29 re-texture stage), rim-light fresnel term (doc 29 material/lighting stage: "rim-light via fresnel term, register-legal, diegetic keyed to lantern/moon"), light-tint material behavior (doc 02 tech pillar 3 via doc 25 S7). The function is palette-law-agnostic: the palette arrives as a per-asset palette texture generated at build time from doc 24's per-character/biome law (PROPOSED mechanism; the law itself is doc 24 section 3, not re-stated here).
- MIPMAPS OFF on character/prop albedos (doc 29 re-texture stage). PROPOSED engine setting: LODInfo mipmap bias 0 with noMipmaps on the small texture set; texture groups set in DefaultDeviceProfiles (PROPOSED profile name WH_PixelRegister).

### 3.3 Fog and night lighting law hookup

- FOG DENSITY 0.018: the doc 29 scene-readability PASS number, carried into doc 31's arena law ("fog density 0.018, 29 scene-readability PASS"). It is EXPLORATION-state fog (PROPOSED mapping): doc 29 keys fog to two states, EXPLORATION (thick) and LOCKED-ON COMBAT (receded, doc 24 bake-in proposal). UE shape: exponential height fog on a single fog component; density is a scalar driven by the lock-on state (doc 32 lock-on section) through the post/chase camera (PROPOSED driver: AWHPlayerController reads lock-on state changes and interpolates density; interpolation time PROPOSED 0.5 s, tunable).
- NIGHT LAW: single diegetic key (lantern at player) + moon fill + rim via fresnel (doc 24 mood register LOCKED: "small diegetic sources only"; doc 29 scene spec lighting row). The mood-lighting blueprint is doc 30 Phase 2's deliverable ("lock the mood-lighting blueprint"); this doc wires it as: one keyed light rig per lighting state (night masters, day pairs per doc 24's 24:1 day/night law), parameterized by doc 24's per-biome accent table (doc 24 section 3). Exactly ONE accent per frame/state (doc 24 palette law); accent ownership rule (cyan=magic, amber=human fire, red=pact/danger, teal=neutral court) is doc 24's open ruling, cited not re-decided.
- READABILITY FLOOR: dark characters need a brightened set (slate background, doubled moon/rim/ambient, fog 0.018) to read at the doc 28 combat register (doc 29 VALIDATION MEMO, scene readability PASS after key-light raise). The lighting rig bakes that brightened set as its baseline (PROPOSED: the night-master key values from the spike scene carry into the arena's lighting blueprint).
- Budget hooks for this section: the full post chain (low-res + dither + grain + fog) is one line-item in doc 31 G23: under 2.5 ms GPU for the whole chain, total GPU under 14 ms (doc 31 G23 PROPOSED cells). No new numbers are invented here; counters in section 5.

## 4. GLB IMPORT PIPELINE (doc 30 as engine-side prerequisites)

Doc 30's remote manual is the operating envelope; this section authors the engine-side prerequisites and settings the import loop must serve. Repo ruling already locked: separate witch-hunter-ue repo, LFS for binaries (doc 31; doc 53 section 1.1 resolved doc 30's open item).

### 4.1 Control/data planes (carried, doc 30)

- DATA PLANE: GitHub, GLBs + textures + manifests commit to the repo on dev; the PC pulls (doc 30 plane 1). LFS tracks *.glb and the palette textures.
- CONTROL PLANE: Tailscale + UE Remote Control API on :30010; IO drives run_python_file through the MCP server (doc 30 recommended configuration; UE 5.8 first-party MCP audited before adoption per doc 31).
- VERIFICATION PLANE: HighResShot renders to Saved/Renders/, pushed to the renders/ branch or scp-pulled (doc 30 plane 3). Vision QA against concept frames, same loop as the 2D pipeline (doc 30 loop step 4).
- Import script: ue/import_asset.py (doc 30 names it): pulls latest, runs an AssetImportTask for new GLBs, applies the pixel material function, reports asset paths back (doc 30 loop step 2). This doc authors what that script must configure (4.2-4.4); the script itself is implementation, authored at M0/M1 (doc 31 milestones).

### 4.2 Import settings per asset class

| Asset class | Import shape | Settings (PROPOSED unless cited) | Cites |
|---|---|---|---|
| Static prop GLB (church-kit, graveyard, crypt, rubble) | StaticMesh | build as-is, no Nanite (pixel register + nearest sampling makes LOD chains counterproductive), simple collision per kit piece, lightmap UVs skipped | doc 29 v3 raw-mesh approach |
| Skeletal body GLB (races, spike bodies) | SkeletalMesh + PhysicsAsset stub | preserve region sub-mesh split (KNOWN ISSUES 1), sockets defined once per skeleton (4.3), root at ground line (normalized 1.8 figure, head anchor y=1.63 per doc 29 KNOWN ISSUES 3) | doc 29 |
| Equipment GLB (helmets, weapons, shields, armor) | StaticMesh (rigid) or SkeletalMesh (cloth-backed, PROPOSED by piece type) | attach-at-socket pivot convention: origin at the anchor socket, not mesh center (doc 27 R2 anchor contract carried to 3D) | doc 29 S-C0 |
| Weapon GLB (weapons/) | StaticMesh | socket-pivot origin, one material slot per palette zone (doc 27 R4 variant mechanics) | doc 54 weapon classes |

- Raw mesh as-is: import applies NO mesh cleanup beyond import defaults; color pixelation is the only visual treatment (doc 29: "raw mesh as-is per the v3 locked approach, color pixelation only"; re-texture pass owns the look, 3.2).
- Mesh budget per asset: 28-32k tris (spec-brief figure, PROPOSED; doc 31's scene-level budget is under 2 M triangles and under 20 skinned meshes, which the worst-case 8-body slice scene fits with headroom, doc 31 G23). Measured anchors: spike body 15k tris, helmet 3k tris (doc 29 S-B1). Per-class bands are UP-3.

### 4.3 Socket contract (doc 54 weapon classes)

- Sockets are defined ONCE per rigged skeleton (doc 29 KNOWN ISSUES 3) and named (PROPOSED, mapping doc 27's R2 anchor pixels to 3D): WH_Socket_Head, WH_Socket_HandR, WH_Socket_HandL, WH_Socket_Back. Doc 27's anchor contract (same ground line, same shoulder/hip/wrist anchors per direction) is the 2D ancestor; the 3D contract is the socket list plus per-socket transform constants authored in the rig stage (doc 31 auto-rig stage owns socket QC: "socket check against 29's anchor rule").
- Consumer: doc 54's weapon classes (DT_WeaponClass 9 rows: ShortBlade, LongBlade, Blunt, Axes, Polearms, Archery, DualWield, Shield, Unarmed; slice 1 builds LongBlade fully, doc 54 section 4). Hand anchoring: LongBlade -> WH_Socket_HandR; shield -> WH_Socket_HandL (PROPOSED mapping; doc 27's weapon layer already declares right/left hand anchors). Doc 54 owns combat semantics of the classes; this doc owns only the attachment points.
- Equipment slot components (section 2.1) attach at the same sockets; one contract serves weapons, armor pieces, and future FX layers.

### 4.4 LFS/git data-plane wiring

- witch-hunter-ue repo: Config/DefaultRemoteControl.ini committed per doc 30's setup checklist (web server autostart :30010, bEnableRemotePythonExecution=True, function-call gates ON, console gate OFF, Tailscale-bound); /WH/Art assets and GLB sources under LFS (patterns: *.glb, *.png under Art/, PROPOSED).
- Source-of-truth split: raw GLB + palette PNGs live in THIS repo under art-direction/3d/ (current layout, verified below); the witch-hunter-ue repo carries imported uassets + the import scripts + manifests. Planning docs never enter the UE repo (doc 53 section 1.1).
- Verified inventory (this session, `git ls-files`): 108 tracked GLBs under art-direction/: 3d-spike 6 (gravedigger body, helmet, gravestone + pixelated variants), 3d/assets: armor 16, church-kit 30, crypt 10, graveyard 8, races 20, races_regen 10, weapons 18; 54 are *-pixelated.glb variants, 54 are base meshes (44 unique names after the races/races_regen dedup pair). The spec brief's "46 committed GLBs" does not match the tracked count; recorded as UP-2 rather than silently adopted.
- Import manifest: art-direction/3d/manifest.json per kit (PROPOSED schema: source glb path, target /Game/WH path, material-function assignment, socket map, budget row). The import script consumes it; Testerbot diffs it against the tracked GLB tree (T58-04).

## 5. TEST PLAN (Testerbot)

Grep-able and structural checks against the witch-hunter-ue repo and this doc, named exactly:

| Check | Validates | Method |
|---|---|---|
| T58-01 | Widget class map presence | /Game/WH/UI/ contains exactly WBP_WH_HUD, WBP_WH_Health, WBP_WH_Stamina, WBP_WH_Poise, WBP_WH_BossBar, WBP_WH_Reticle (+ WBP_WH_DamageNumbers); missing/extra = fail (section 1.1 table) |
| T58-02 | Binding contract: HUD is read-only over the interface | no UI class includes WHCombatComponent.h or touches combat component members directly; interface delegates are the only push path (grep Source/WHGame/UI for direct member access) |
| T58-03 | Register stack shader nodes | MF_WHPixelRegister contains: nearest-neighbor sampler, 5-bit posterize/48-color palette input, ordered-dither node, grain node; MMP_WHRegister drives 720p-internal point-sampled upscale (material node inventory via import-script report) |
| T58-04 | GLB import list completeness | manifest rows diffed against `git ls-files 'art-direction/**/*.glb'` (108 tracked, 54 base); every base mesh appears in the manifest or carries an explicit slice-1 exclusion note |
| T58-05 | Mesh budget per asset | import report tri-counts within the 28-32k PROPOSED band (or the UP-3-resolved bands); over-budget assets fail the import report |
| T58-06 | Perf budget hooks | scripted stat capture (stat RHI/stat unit via Remote Control Python) at the doc 31 scripted 8-enemy orbit fight, night fog: under 1,500 draw calls, under 2M triangles, post chain under 2.5 ms, 60 fps with 0 hitches above 33 ms over 5 min (doc 31 G23 test row) |
| T58-07 | Readability QA bar | doc 29 criteria 1 as the gate: 5-viewer panel, enemy verb type identified within 250 ms at the doc 28 COMBAT register under night + fog 0.018; plus the qa_gate.py silhouette-contrast metric adapted for meshes (doc 29 criterion 1) |
| T58-08 | Ledger compliance | grep of UI text tables + widget defaults for doc 44 Part 2 forbidden facts returns zero matches (section 6) |

## 6. Constraints compliance

- NO new art direction: every look-governing number here is carried (fog 0.018, 720p/1080p, one-accent law, dither/grain) with citations; invented UE-structural names and tunables carry PROPOSED. Conflicts became UP items, not edits.
- GAS deferred: no GAS types, components, or tags appear in any structure above.
- Ledger compliance (spec constraint 4): no HUD or presentation beat encodes a doc 44 Part 2 forbidden grant. The HUD carries no text or state naming creditor identity, the witch's masks, or the debt's authorship; boss-bar labels are encounter-table rows (doc 56 ownership), damage numbers are numeric only (doc 35 G11), and no presentation surface reads ledger reveal-gate cells beyond the doc 53 interface (T58-08 enforces).

## Open questions (doc 08 format)

- UP-1: Import target root: doc 30's loop step 2 names /Game/Assets/<kit>; doc 31's locked folder law puts all gameplay assets under /Game/WH/. This doc authors /Game/WH/ paths and flags the doc 30 line as stale. Assignment: Nicko one-line ruling confirming /Game/WH/ governs; doc 30 annotation to follow.
- UP-2: GLB import inventory: the brief says "46 committed GLBs"; the tracked tree holds 108 GLBs (54 base + 54 pixelated variants; 44 unique base names after races/races_regen dedup). Which set is the slice-1 import list (spike 6 + which asset kits)? Assignment: Nicko + IO inventory pass before M1.
- UP-3: Per-asset mesh budget band 28-32k tris is brief-invented; measured spike meshes are 15k (body) and 3k (prop). Confirm the band or adopt measured per-class bands (body / prop / equipment). Assignment: Nicko at the first import batch (M0/M1 timing per doc 31).
- UP-4: Billboard retirement scope: doc 29 demoted sprite production to reference; this doc builds no runtime billboards for slice 1 and keeps Paper2D HUD-only. Confirm billboards stay retired until a ruling revives them (doc 08 carries the boss-sprite and billboard-perf opens). Assignment: Nicko.
- UP-5: Boss-bar runtime source: liveness flags serialize in FWHSaveWorldFlags (doc 53 section 4.1) but the bar needs a doc 56 encounter-table activation hook; the interface delegate shape here is PROPOSED. Assignment: doc 56 author (contract owner) with Nicko confirming the activation event.
- UP-6: Reticle presentation (size, shape, fade curve): doc 32 rules behavior (fade-in 0.15 s, dual-mode stationary reticle) but no visual ruling exists; the UI/UX art direction doc is an open doc 08 item. Assignment: UI/UX art direction session (doc 08 "UI/UX art direction doc").
- UP-7: Poise presentation: doc 31's IN list includes poise but no doc rules bar-vs-icon; PROPOSED a thin bar mirroring stamina's. Assignment: Nicko (one-line, same pass as UP-6).

## Completion report

- Sections delivered: 1 (UMG HUD minimum: widget map, binding contract, context visibility, acceptance hooks), 2 (sprite/billboard stack: paper-doll slot components, material/palette stack, billboard-vs-mesh table, slice-1 scope), 3 (pixel register post-chain: 720p point-sample upscale, dither, grain, material function, fog 0.018 + night law hookup, budget hooks), 4 (GLB import pipeline: planes, per-class import settings, socket contract, LFS/git wiring, manifest), 5 (test plan T58-01..08), plus constraints compliance and this report.
- Counts: 8 widget classes declared (6 slice-1 + 2 doc 35 structural: DamageNumbers, Focus); 1 shared material function + 1 post-process material + per-piece MIC palette instances; 4 sockets; 1 slot DataTable (DT_WHEquipmentVisuals); import pipeline covering the verified 108-GLB tracked corpus (54 base meshes); 8 test checks.
- Open questions: UP-1..7 above, each with an assignment; all invented numbers/names carry PROPOSED.
- Spec conflicts: doc 30's /Game/Assets path vs doc 31's /Game/WH/ law (UP-1); the brief's "46 committed GLBs" vs the tracked 108 (UP-2); the 28-32k tri band vs measured 15k/3k anchors (UP-3). No locked ruling was edited; conflicts are recorded, not resolved here.
- File left untracked in the planning repo; no commits, no other files touched.