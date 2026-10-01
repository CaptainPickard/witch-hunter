# 59 - Biome Object Library

Status: PROPOSED (IO, 2026-09-21, pending Nicko lock).
Source rulings (Nicko, 2026-09-21): (1) Meshy is the generator for all 3D
objects in the Witch Hunter buildout. (2) Art passes are organized BY BIOME
TYPE: catalog the objects a biome should contain, generate the set, then
populate region instances from the library afterward. (3) First pass scope
locked: Hold Outskirts (graveyard) and Darkwood Edge (forest) only,
roughly 10-20 objects. (4) The first Meshy batch fires only after the
Three.js v1 prototype is playable and validated, so the library lands
against the proven region format.

## PART 1: Conventions

- Every object entry: working name, category, source (doc 03 category list
  or doc 41 encounter family), gameplay role in regions, status.
- HAVE = a validated GLB already exists under art-direction/3d/assets/
  (prefer pixelated variants). MISSING = no GLB; candidate for Meshy.
- Tri targets follow doc 29 carrier + the 46-asset run defaults (props
  2k-15k tris at Meshy, decimation per manifest discipline).
- Pipeline per asset is the validated one: image_generate concept ref
  (canon frame as reference image, one object, neutral pose, flat dark
  gray background) -> vision QA -> Meshy image-to-3d -> UV rebuild ->
  512px NEAREST + 5-bit posterize pixelation -> commit raw + pixelated.
- Credit rule from Nicko stands: hard cap 700 credits per session,
  one retry max per asset, skip and log on double failure.

## PART 2: Region A, Hold Outskirts (graveyard set)

Context: settlement-edge cemetery per doc 03 Settlements (semi-procedural
surface sites, revenant spawns, grave goods). Existing coverage is strong
on grave markers, weak on boundary and structure.

| # | Working name | Category | Source | Status |
|---|--------------|----------|--------|--------|
| A1 | Grave marker, obelisk | Grave goods | 03 Settlements | HAVE (graveyard/gravestone-obelisk) |
| A2 | Grave marker, tilted cross | Grave goods | 03 Settlements | HAVE (graveyard/stone-cross-tilted) |
| A3 | Grave mound | Grave goods | 03 Settlements | HAVE (graveyard/grave-mound) |
| A4 | Buried coffin | Grave goods | 03 Settlements | HAVE (graveyard/buried-coffin) |
| A5 | Wrought-iron fence section | Boundary | 03 Settlements | HAVE (church-kit/iron-fence-section) |
| A6 | Wrought-iron fence corner | Boundary | 03 Settlements | HAVE (church-kit/iron-fence-corner) |
| A7 | Lantern post | Lighting | 03 Settlements | HAVE (church-kit/lantern-post) |
| A8 | Dead tree | Flora | 03 Darkwood | HAVE (church-kit/dead-tree) |
| A9 | Cemetery gate | Boundary | 03 Settlements | MISSING (candidate M1) |
| A10 | Wooden picket fence section | Boundary | 03 Settlements | MISSING (candidate M2) |
| A11 | Mourning statue | Grave goods | 03 Settlements | MISSING (candidate M3) |
| A12 | Skull pile | Grave goods | doc 36 altar texture | HAVE (crypt/skull-pile) |
| A13 | Stone sarcophagus | Grave goods | crypt interiors | HAVE (crypt/stone-sarcophagus) |

Region A gaps: 3 objects (M1-M3). The region reads as a graveyard today,
but has no entrance or fence variety, so the chokepoint gate that the
region system needs as its boundary marker has no asset.

## PART 3: Region B, Darkwood Edge (forest set)

Context: doc 03 Darkwood, the signature biome (dense, fog-choked, covens,
bandits, beasts) plus the locked per-biome ingredient category list: herbs
as visible world objects (moonbell, grave-moss, hemlock, BLIGHTCAP
signature), reagent spawn sites (Frost/Ember Motes in glade clearings,
Grave Motes densest here), coven groves, bandit presence.

| # | Working name | Category | Source | Status |
|---|--------------|----------|--------|--------|
| B1 | Dead tree | Flora | 03 Darkwood | HAVE (church-kit/dead-tree) |
| B2 | Living darkwood tree, variant 1 (oak) | Flora | 03 Darkwood woods | MISSING (candidate M4) |
| B3 | Living darkwood tree, variant 2 (yew) | Flora | 03 Darkwood woods | MISSING (candidate M5) |
| B4 | Witchwood grove tree | Flora | 03 Darkwood WITCHWOOD signature | MISSING (candidate M6) |
| B5 | Fallen log | Flora | 03 Darkwood | MISSING (candidate M7) |
| B6 | Tree stump | Flora | 03 Darkwood | MISSING (candidate M8) |
| B7 | Moss boulder | Terrain | 03 Darkwood | MISSING (candidate M9) |
| B8 | Bramble thicket | Flora | 03 Darkwood | MISSING (candidate M10) |
| B9 | Moonbell herb pickup | Harvest | 03 Darkwood herbs | MISSING (candidate M11) |
| B10 | Grave-moss herb pickup | Harvest | 03 Darkwood herbs | MISSING (candidate M12) |
| B11 | Hemlock herb pickup | Harvest | 03 Darkwood herbs | MISSING (candidate M13) |
| B12 | Blightcap mushroom pickup | Harvest | 03 Darkwood BLIGHTCAP signature | MISSING (candidate M14) |
| B13 | Bandit campfire | Encounter prop | doc 41 Family 1 (dens/lairs) | MISSING (candidate M15) |
| B14 | Bandit bedroll | Encounter prop | doc 41 Family 1 | MISSING (candidate M16) |
| B15 | Coven grove marker / witch totem | Encounter prop | 03 Darkwood coven glades | MISSING (candidate M17) |
| B16 | Glade mote shrine | Reagent spawn | 03 Darkwood reagent spawns | MISSING (candidate M18) |

Region B gaps: 14 objects (M4-M18). The forest currently has exactly one
flora asset, so a forest region cannot read as a forest yet. Harvest
pickups make the doc 03 gather loop visible in the prototype.

## PART 4: Meshy run log (fill on generation, post-v1-validation)

Not started. Batch fires after v1 is playable and Testerbot-validated.
Planned batch 1: M1-M3 + M4-M9 (9 credits x 15 = 135 credits approx).
Planned batch 2: M10-M18. Each row to record: candidate, credits, Meshy
task id, vision-QA verdict, tri count, pixelated commit path.

## Open Questions

1. NICKO: candidate list above (M1-M18) is the working set; kill or add
   before batch 1 fires.
2. Should living-tree variants get 2-3 meshes each (same mesh re-tinted
   via palette variant per doc 27, or separate meshes)?
3. Do herb pickups need a shared base mesh scaled/recolored, or one mesh
   per herb (one mesh each assumed in the matrix)?
## SESSION RULINGS (2026-09-21, Nicko)

R1 CANDIDATE LIST: ALL of M1-M18 CONFIRMED for generation, across two
   batches (~270 credits total, within the 700/session cap across resets).
R2 LIVING TREES: 3 DISTINCT MESHES (M4 oak, M5 yew, M6 witchwood), one
   Meshy run each. Silhouette variety rules; no palette re-tint variants.
R3 HERBS: ONE MESH EACH (M11-M14), no shared base. Each herb reads as its
   own distinct plant per doc 03's distinct herb identities.

Open questions 2 and 3 RESOLVED by R2/R3. Open question 1 RESOLVED by R1.

## BATCH PLAN

Batch 1 (this session, budget-capped): M1-M9 (9 assets, ~135 credits).
Batch 2 (after next credit reset on the 13th): M10-M18 (9 assets).
Run log entries go in Part 4 as each batch lands.

## PART 4: Meshy run log

2026-09-21 (batch 1, landed commit 59b3b52):
| ID | Asset | Credits | Vision-QA | Tris | Path |
|----|-------|---------|-----------|------|------|
| M1 | Cemetery gate | 15 | PASS | ~30k | biome_library/m1-pixelated.glb |
| M2 | Picket fence | 15 | PASS | ~30k | biome_library/m2-pixelated.glb |
| M3 | Mourning statue | 15 | PASS | ~30k | biome_library/m3-pixelated.glb |
| M4 | Living oak | 15 | PASS | ~30k | biome_library/m4-pixelated.glb |
| M5 | Yew | 15 | PASS | ~30k | biome_library/m5-pixelated.glb |
| M6 | Witchwood | 15 | PASS | ~30k | biome_library/m6-pixelated.glb |
| M7 | Fallen log | 15 | PASS | ~30k | biome_library/m7-pixelated.glb |
| M8 | Tree stump | 15 | PASS | ~30k | biome_library/m8-pixelated.glb |
| M9 | Moss boulder | 15 | PASS | ~30k | biome_library/m9-pixelated.glb |
Total: 135 credits. All 9 SUCCEEDED first try, pixelation v3 pass applied.

2026-09-22 (darkwood dressing session, IO):
- Canon biome reference saved: refs/darkwood-concept.jpeg (commit 43cb90b).
- Concept refs generated + vision-QAed + pushed (same commit):
  M10-bramble-thicket-ref.png (PASS),
  M19-hanging-moss-drape-ref.png (PASS; drape includes its host branch
  by design - the branch IS the mount point),
  M20-mud-puddle-ref.png (PASS),
  M21-gnarled-root-cluster-ref.png (PASS).
- MESHY 402 BLOCKED: credit probe submit of M10 returned HTTP 402
  Payment Required. Credits exhausted. ZERO new meshes generated this
  session. Retry M10/M19/M20/M21 (4 x 15 = 60 credits) at the next
  credit window; refs are on dev and verified 200 on raw.githubusercontent.
- Scene dressing proceeded with EXISTING inventory: M4-M9 are on disk
  and unused by the prototype; region re-skin used m1-m9 + graveyard +
  church-kit props only (see spec specs/astrabot-spec-darkwood-dressing.md).

2026-10-01 (batch retry — doc 59 ordered batch, landed commit 71dae10
on feat/world-visuals):
| ID | Asset | Credits | Vision-QA | Tris | Path |
|----|-------|---------|-----------|------|------|
| M10 | Bramble thicket | 15 | PASS | 46.7k | biome_library/m10-pixelated.glb |
| M19 | Hanging moss drape | 15 | PASS | 15.2k | biome_library/m19-pixelated.glb |
| M20 | Mud puddle decal | 15 | PASS | 2.5k | biome_library/m20-pixelated.glb |
| M21 | Gnarled root cluster | 15 | PASS | 5.2k | biome_library/m21-pixelated.glb |
Total: 60 credits. All 4 SUCCEEDED first try, pixelation v3 pass applied
(512px NEAREST + 5-bit posterize verified byte-level, normals injected).
Notes:
- 402 unblocked: Nicko rotated the Meshy key (now env/file-only, old
  exposed key superseded) and topped the account to 3000 credits.
- Submit targets (doc 61 s6 rule 2): 2000 tris M10/M19/M21, 1200 M20;
  meshy-5 quad topology returns raw counts above (soft target).
- Atlas-level numeric scan: 0 cyan/magenta strays, 0 white holes across
  all four atlases; thumbnail QA 4/4 PASS (grimdark coherence check).
- Task IDs: M10 01a0f5c2-72f5-7074-81e1-8bdb271e607e, M19 01a0f5c3-7708-
  7416-aa6f-751c4a9632a9, M20 01a0f5c4-7974-7149-8666-e8ee889a7ca7,
  M21 01a0f5c5-7c8b-77ae-ab84-bd094919fac6.
- Branch note: assets committed to feat/world-visuals (worktree; dev
  checkout owned by the blender-anim session). Runtime dressing with
  these assets rides the world code rounds (R2 onward).

2026-10-01 (B6 scatter kit, PARTIAL 5/6, commit 72752ef
on feat/world-visuals):
| ID | Asset | Credits | Vision-QA | Tris | Path |
|----|-------|---------|-----------|------|------|
| B6-bones | Bone scatter | 15 | PASS | 10.9k | biome_library/b6-bones-pixelated.glb |
| B6-leaves | Leaf litter mat | 15 | PASS | 5.3k | biome_library/b6-leaves-pixelated.glb |
| B6-pebbles | Pebble scatter | 15 | PASS | 3.7k | biome_library/b6-pebbles-pixelated.glb |
| B6-stonefrags | Headstone fragments | 15 | PASS | 3.0k | biome_library/b6-stonefrags-pixelated.glb |
| B6-mushrooms | Mushroom cluster | 15 | PASS | 3.2k | biome_library/b6-mushrooms-pixelated.glb |
| B6-bracken | Withered bracken | 15 | FAIL-retry | (r2 in flight) | — |
Total: 75 spent (bracken credits consumed on failed mesh; retry ref
B6-bracken-ref-r2.png vision-QA PASS, resubmit follow-up). Retry rule:
one retry max per doc 59 conventions.
Refs note: B6 + B2 + B3 reference art generated this session
(parented on darkwood-concept.jpeg), QA PASS 100%.
