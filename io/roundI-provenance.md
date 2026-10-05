# Round I provenance: gothic reach-trees replace half the witchwoods

One Claude Code run on 2026-10-05. Brief: io/missions/2026-10-05-cc-roundI-reacht.md (3 variants,
on Nicko's mid-dispatch order). IO's reference render is scratch/treegen/roundI/reach-tree-ref.png.
Per the brief, it was not re-analyzed; the t2i prompts are the brief's distilled text.

## Meshy credit ledger (scratch/tree_meshy.py guard: START_BALANCE 1267, CAP 60, floor 1207)

| step | task | credits | balance |
|---|---|---|---|
| measured start (= brief) | | | 1267 |
| t2i refA (reference match) | 01a10998-84e7-7323-bd47-32ce80ea65c5 | -3 | 1264 |
| t2i refB (broad claw-spread) | 01a1099a-a7c1-75b2-97d9-9c3818884d14 | -3 | 1261 |
| t2i refC (tall, lean, sparse) | 01a1099c-654e-7154-aa62-bc9b3e647269 | -3 | 1258 |
| i23d A, meshy-5, target 2000 | 01a1099d-bfaf-76d7-b37a-cced3245e80e | -15 | 1243 |
| i23d B, meshy-5, target 2000 | 01a1099f-065b-7012-bd62-98e499fa0cd5 | -15 | 1228 |
| i23d C, meshy-5, target 2000 | 01a109a0-75eb-7446-b002-fa98eb05e854 | -15 | 1213 |

Total spent: 54 of 60. No re-rolls: one i23d re-roll costs 15, and only 6 credits were left under
the cap, so the guard would refuse it.

## Refs

- The prompts are the brief's base text; B and C add their modifiers before the style tail. The
  three refs come back clearly distinct: A is the reference match, B is broader than tall with a
  sideways claw spread, and C is taller with a lean and a sparser crown.
- Matte: ref_matte.py at tol 60 (Round H's --dark default) ate the dark bark (the bg is pure
  0-3 black), so it was rerun at `12 --dark --pocket=12`. --pocket is new and backward compatible:
  sky pockets between twigs larger than N px go transparent, which stops the fine canopy reading
  as solid black mass.

## Raw QA (scratch/treeqa/roundI/gate.jsonl, *-raw-front/side.png)

| variant | faces | welded largest | tinyFar | ext X/Y/Z | gate(a) |
|---|---|---|---|---|---|
| A | 12577 | 56.2% | 1 | 1.626 / 1.570 / 1.488 | FAIL |
| B | 14675 | 54.0% | 1 | 1.554 / 1.156 / 1.577 | FAIL |
| C | 12579 | 38.5% | 1 | 1.573 / 1.777 / 1.550 | FAIL |

The failure is not a shard storm (tinyFar 1 each). Meshy-5 returned the tertiary twig tips as
separate face-dense shells, parked a 0.06-0.23 gap (median ~0.08) off the limb ends. Vision QA:
none of them reads as a blob or lollipop. Each has a buttress-root trunk that grounds and limbs
reaching out on both front and side axes, and each matches its ref's silhouette character.

## Decimate + bake

- scratch/decimate_roundI.py is decimate_roundH.py (weld, then fast_simplification, then per-face
  medoid UV transfer) at a 3500-tri budget, plus `--snap`. Snap translates each detached twig-tip
  piece rigidly so it touches the nearest attached geometry. It is greedy, nearest first, capped at
  0.25 units, and uses no RNG. All pieces reattached (A 59, B 85, C 96; max move 0.17 / 0.23 / 0.21).
  Signed rows are in scratch/treeqa/roundI/decimate.jsonl (two runs).
- scratch/reachtree_bake_roundI.py is bramble_bake_roundH.py looped over a/b/c: texture path,
  posterize512 (512 NEAREST + 5-bit). The bake is byte-identical across two runs, and the raw/
  copies are byte copies of the Meshy output. The texture is monochrome grey (mean chroma 1.4-1.9
  of 255), so no tint was added.

| variant | raw tris | decimated tris | gate(a) after snap+decimate | in-game ext W x H (units) |
|---|---|---|---|---|
| A | 12577 | 3499 | PASS (70.7%) | 1.558 x 1.567 |
| B | 14675 | 3499 | FAIL (58.8%, tinyFar 0) | 1.447 x 1.084 |
| C | 12579 | 3500 | FAIL (56.7%, tinyFar 1) | 1.423 x 1.729 |

## Wire (CONFIG + assets.js, both branches, identical edits)

- MANIFEST adds reachTreeA/B/C pointing at biome_library/wh-reachtree-<a|b|c>-pixelated.glb.
- CONFIG props: of the 17 witchwoodTree rows in file order, the odd-indexed rows are now
  A,B,C,A,B,C,A,B. Only the asset id changed; x/z/rotY/scale are untouched.
- scatter treesExtra adds ['reachTreeA'|'reachTreeB'|'reachTreeC', 1, 15.5, 18.5] next to witchwood.
- bushes.ringHosts adds the three ids. CONFIG props ring only if their asset is listed there;
  scatter trees always ring. Ring asset stays whBushSnare.
- Collider: the region-manager colliderRadius regex /tree|.../i matches reachTree*, so trunk-like
  r*0.25 applies (verified in scatter_mirror.collider_radius too).

## Mirrors (scratch/roundI-proof/)

- wall_mirror.json: deterministic across two runs, byte-identical to Round H.
- scatter_mirror.json: deterministic across two runs. Counts are unchanged from Round H:
  - hold_outskirts: trees 14, rings 305, free 20, grass 220
  - darkwood_edge: trees 10, rings 130, free 20, grass 220

  The tree mix shifted. Scatter reach trees: hold_outskirts A x2, B x1; darkwood_edge A x2, B x1.
  No scatter witchwood or C landed this seed.

## Run-end note (IO)

The run was cut by the Claude Code session limit at ~34 min ("You've hit
your session limit - resets 2:30am UTC"), AFTER all generation, QA, wiring
and 2 of 3 stills. IO finished the remainder inline as gatekeeper: ferried
the render r3b 03-world-mix.png into scratch/roundI-proof/, committed the
CONFIG/assets wiring + script edits + still, and wrote this note. Still
03's vision read: the mix is visually DISTINCT (horizontal jagged reach vs
vertical smooth witchwood) with a scale watch item (reach-tree reads
heavier - watch in playtest).

## I6 addendum: why the first mix read as nothing

Nicko's playtest: "still the same old ones". The Round I swaps and scatter landed
8 CONFIG reach trees plus 2-3 scatter ones per region. Every one of them stood 41-88 m
from the new spawn (2.5, 74), and none stood within 12 m of the walked dirt path
(centerline x(z) = 1.6 sin(2pi(z-86)/34), z 32..86). About 59 region-A yews wall the
path view on both sides, 7-11 m off the centerline. So every cone silhouette the player
saw was a yew. The mix was correct but out of sight.

Fix (CONFIG regionA props only, dev + feat/world-visuals): 6 rows placed by IO in even
z-steps on alternating sides, 8-11 m off the centerline:
A (7.16, 38.0), B (-12.57, 42.5), C (7.29, 49.5), A (-6.82, 56.5), B (8.44, 67.5),
C (-7.29, 66.5). Re-checked against all 133 region-A props: nearest neighbours are
3.33 / 3.54 / 5.64 / 3.63 / 3.48 / 4.61 m (all >= 3.0, so no nudge).

- wall_mirror: byte-identical to HEAD (ring 145, colliders 603), deterministic.
- scatter_mirror: deterministic. hold_outskirts rings 305 -> 319 (+14),
  ringSkipped 3 -> 10. darkwood_edge unchanged (130).
- scratch/roundI6-proof/04-path-corridor.png: spawn chase rig, 60 deg vFOV, looking
  down the path. 4 of the 6 new trees read as jagged horizontal-spread silhouettes
  against the yew cones.
