# ROUND J2 CONTRACT (FIX 2): CLOSE the open trunk bottoms (IO -> Claude Code)

SHORT RUN. No Meshy. No harness/game loops. Commit early, both branches.
Round J's diagnosis was right (open-bottomed root arches) but its sink-only
fix leaves sky VISIBLE under the trunk arch in the after-b proof still
(vision-verified by IO). Close the geometry instead.

## THE FIX (per variant a/b/c, on the CURRENT pixelated GLBs)

Blender, per variant, deterministic:
1. Backup current GLB to /tmp/roundJ2-backup/ first.
2. Import wh-reachtree-<v>-pixelated.glb.
3. The trunk underside hole: find the trunk's root-arch boundary loop (the
   open edge ring near the bottom of the trunk between root flares) and FILL
   IT: create a "root pad" - a flat cap slightly CONCAVE (dome pressed down
   0.06 GLB units at the center) so from any side view NO sky shows under
   the trunk, and from top-down it's hidden inside the root flare volume.
   Implementation hint (bmesh): collect boundary edges of the largest
   connected component within the bottom 30% (z < p30), find the loop
   enclosing the trunk center axis, bridge/fill with a disk; apply a small
   downward bulge on the disk's interior verts (proportional to distance
   from the loop edge). If the boundary loop is fragmented, snap the 0.15m
   far fragments FIRST (reuse the Round I4 snap rule so the loop closes) and
   note any piece counts.
   DO NOT delete visible root flare mass.
4. Reweld (position weld + UV-seam copies + smooth normals + zero-normal
   repair): reuse scratch/weld_uv_roundI2b.py / I2d / I2e pipeline steps as
   needed (read their headers, they are proven; they operate on the current
   GLB in place with correct GLB chunk types - b'JSON' not b'UTF8').
   Ensure NORMAL attribute present + unit (they verify + repair).
5. OVERWRITE art-direction/3d/assets/biome_library/wh-reachtree-<v>-
   pixelated.glb (same names; .glb mid + raw stay untouched).
6. Verify each: trimesh load OK; underside ray test
   (scratch/roundJ_underside.py): median ground gap <= 0.02 GLB units and
   footprint >0.15m-up <= 3%; ortho renders front/side + a low base-persp
   each into scratch/roundJ2-proof/<v>-*.png; vision-check: sky must NOT
   show under the trunk from ANY of the 3 persp angles (0/120/240).
7. Keep CONFIG.assets.groundSink values from Round J (they still help sink
   the pad into the soil).

## ALSO (small, same run)

- dev oak float: dev's CONFIG has livingOak rows with y: 1.57/1.63 lifting
  oaks off the ground (feat fixed this in 44580ce). PORT the relevant part
  of 44580ce to dev (only the CONFIG row y-value corrections for the oak
  rows; do NOT port unrelated changes). Report the rows you fixed.

## Commits (CaptainPickard <pickard.nicko@gmail.com>, both branches, same
messages):
- fix(assets): close reach-tree trunk undersides (Round J2)
- fix(world): dev oak ground rows from 44580ce (Round J2, dev only)
- build: v7 bundle (worktree only)
Also commit scratch/roundJ2-proof/ + io/roundJ-provenance.md J2 addendum +
any new script. No push. Do not touch other files; no main; no
light/player/enemy/moveset/region-defs; never read/commit
scratch/.mixamo-credentials.txt or .mixamo-storage.json.

## Report (<= 50 lines)

Per-variant pad stats (boundary loop verts, cap faces, concave depth),
underside ray results before/after (+footprint %), verification table,
proof stills list, dev oak rows fixed, commits table, watch items.