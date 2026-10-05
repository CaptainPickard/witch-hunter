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
