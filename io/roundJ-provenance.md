# Round J provenance: reach-trees floating above the ground

## Mechanism

The Meshy reach-tree meshes (a/b/c) have open bottoms: the trunk is a shell
with no floor, and its root-flare tips hang lower than the trunk underside.
`assets.js` groundAlign puts the LOWEST vertex at y=0 (Box3.setFromObject,
correct and identical to the accessor bounds). So each tree stands on its
root tips with sky showing under the trunk. Raycasting straight up through
the trunk footprint gives a median gap of 0.27 / 0.80 / 0.39 m at scale 10
(a / b / c), with 100% of the footprint more than 0.15 m off the ground. The
raw Meshy GLBs (scratch/treegen/roundI/*-meshy.glb) show the same gaps
(0.25 / 0.81 / 0.41 m), so the bake, snap and weld passes did not cause it.
The loader, instance() and `p.y || 0` are all correct. B (worst, ~0.8 m, on
visible stilts) and C are the trees that read as floating; A is milder.

## Fix (engine-side, name-gated)

`CONFIG.assets.groundSink = { reachTreeA: 0.0312, reachTreeB: 0.0878,
reachTreeC: 0.0500 }` in GLB units, and `assets.js applyGroundSink(name,
root)` runs right after groundAlign in loadOne. It lowers the inner root by
the sink inside the holder, so the sink scales with both the CONFIG prop
scale and the height-driven scatter scale, and InstancedMesh template
matrices pick it up. Each value is the p75 of the trunk-underside height
(scratch/roundJ_underside.py). Other assets are untouched, and GROUND_META
keeps the measured bounds (`groundSink` is recorded on it). Rollback:
`groundSink: {}`. GLBs are unchanged. A GLB-side fix would have meant
clipping the roots, because groundAlign re-grounds on the lowest vertex
however the mesh is translated.

## Evidence

- scratch/roundJ_box3.py: loader Box3 min y -0.8592 / -0.6586 / -0.9430, no
  node transforms (matches the vertex min).
- scratch/roundJ_underside.py: gap at sink 0 vs the chosen sink, p50:
  a 0.27 -> -0.05 m, b 0.80 -> -0.08 m, c 0.39 -> -0.11 m.
- scratch/roundJ-proof/: before/after-<v>-persp.png (eye 0.5 m, 2 m beyond
  the root flare), after-<v>-persp-az120/240.png, before/after-<v>-ortho.png.

## Round J2 addendum: closing the trunk undersides (GLB-side)

Round J's sink still left sky visible through the base in its own proof
stills (after-a/b az120/az240). The "open bottom" turned out to be a misnomer:
the welded meshes have **0 boundary edges in the bottom 30%**, so no loop was
there to fill. The sky came from (1) the raised root arch under the trunk
(0.03-0.09 GLB units) and (2) see-through slits where flares pull away from
the trunk 1.3-1.8 m up and 2.3-2.9 m out (traced with Blender ray casts).

`scratch/roundJ2_rootpad.py` (+ `roundJ2_webs.py`) appends two kinds of
geometry to the single primitive and never moves existing vertices:
- **Root pad**: a closed plug under the arch. Its footprint R(theta) walks out
  from the trunk axis while the mesh overhangs (underside < 0.20) and stops
  where a flare meets the ground. The top follows the underside + 0.004
  (inside the shell), and the walls drop to ymin + 0.003. The concave bottom
  disk is only 0.0025 deep, not 0.06: a deeper dome would undercut the root
  tips, then groundAlign would re-ground on the pad and lift the whole tree.
- **Webs**: voxelise the base (8 cm, vertical parity), apply a 3D closing
  (r = 6 vox), and keep only the new voxels that lie on a see-through line of
  sight (rotated-volume test, 36 azimuths x 4 elevations). Those are meshed
  as closed volumes (surface nets + Taubin 120 + fast_simplification 0.9).
UVs come from the nearest bark vertex. NORMAL is written explicitly, unit
length with no NaNs. The JSON/BIN chunk types are correct, and accessor
min/max are rewritten. ymin is unchanged, so CONFIG.assets.groundSink
still applies.

| v | pad V/F | web vox / F | V before->after | F before->after |
|---|---|---|---|---|
| a | 338/480 | 11716 / 3256 | 10271->12259 | 3499->7235 |
| b | 338/480 | 950 / 462 | 1879->2462 | 3472->4414 |
| c | 338/480 | 827 / 428 | 1934->2508 | 3418->4326 |

Underside rays (roundJ_underside.py, scale 10, sink 0): median gap a 0.27 ->
0.02 m, b 0.80 -> 0.02 m, c 0.39 -> 0.01 m. Footprint >0.15 m: 100% -> 0%
for all three. With the Round J sink, the pre-J2 footprint was 5/4/15% and is
now 0/0/0%.
Sky-hole pixels (scratch/roundJ2_skyholes.py: sky components not connected
to the open sky, lower frame): 0/120/240 = 0 on all 9 stills (before: a
0/168/341, b 0/130/33, c 0). Extra 9-azimuth sweep: a 1877 -> 0, b 1007 ->
49 (tiny slits at az150/180/300/330), c 0 -> 0.
Proof: scratch/roundJ2-proof/<v>-persp-az{0,120,240}.png and
<v>-ortho-{front,side}.png. scratch/roundJ2_base_render.py is
roundJ_base_render.py with ortho honouring the azimuth.
Backups of the pre-J2 GLBs are in /tmp/roundJ2-backup/ (not committed).
