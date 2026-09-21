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
