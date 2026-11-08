# Rot Mother v2 + Rot Spawn — ASSET VERDICTS (2026-10-12, IO round v2)

## Route that won
IMAGE-TO-3D from a recolored, surgically-delta'd ref of the Nicko-approved a1
base (attempt-1-locked). Ref = scratch/rotmother-qa2/ref_v6_34.png.
1. Ref-craft (free): region-mask-verified Meshy surgery on a1.glb —
   delta 1 skull-grin chasm deleted+filled (19,030 faces) = closed sunken face;
   delta 2 all belly drips deleted+filled (6,541 faces) = one continuous gut;
   delta 3 legs/talons/hips thickened (feathered field, no slicing);
   head shrunk + forward tilt kept; crest/arms/claws/STAYs untouched.
   Recolor: swamp-green body / sickly pale gut island (depth-banded interior,
   no silhouette contact) / sparse upper moss / charcoal claws.
2. Meshy image-to-3d attempts (meshy-5, 15cr each):
   M1 remesh 15k = FAIL (9 comps, 1.086% detached — remesh shatter)
   M2 remesh 30k = FAIL (8 comps, 6.525% — worse at higher target)
   M3 no-remesh  = PASS (182,444 tris, 1 comp, 0.000% detached)
   S1 spawn 2k remesh = PASS gen (2,094 tris, 1 comp, 0.000%)
   (S1-dup accidental double-submit -15cr, operator error, no verdict impact)
## Intake bake
- rotmother: fs 60k (parity-clean) -> Blender quad decimate ratio 0.3 ->
  ~18k -> 25/50 contact-slit heal eps-weld 3mm -> 5mm -> stray fan-tri
  delete. Final 17,573 tris, 1 contact-island, 0 faces outside (0.000%).
  Parity: spans reldiff [0.0, 0.0, 0.0] (bbox identical).
- rotspawn: no decimation (2,094 <= 3k).
- v3-lineage export twins (raw-tex + 512px NEAREST 5-bit pixelated), normals
  injected; -20 header bug CHECK/FIX on every export (declared==actual);
  attribute gate POSITION/NORMAL/TEXCOORD_0 equal counts on all files;
  Blender import OK on all 6 outputs (2 raws + 4 bakes).
## Files
- art-direction/3d/assets/races_regen/rotmother.glb (7.70MB, 182,444 tris)
- art-direction/3d/assets/races_regen/rotspawn.glb (2.35MB, 2,094 tris)
- art-direction/3d/assets/races/rotmother.glb + -pixelated.glb
- art-direction/3d/assets/races/rotspawn.glb + -pixelated.glb
## Verdicts
- ROTMOTHER: PASS (identity = a1 silhouette + all three deltas + female gut
  cues; kill-checks clean; texture QA render final_rotmother_{front,34,side}.png)
- ROTSPAWN: PASS (form/eyes/mouth/palette clean; final_rotspawn_*.png)
## Watch-items
- Meshy remesh path shatters this creature at any target; the no-remesh route
  + local decimation is the working recipe (15cr/asset at 936cr balance).
- Texture-placement nit: pale patch extends toward groin/upper thigh
  (readable as underbelly marking; NOT cloth geometry — verified).
- Spawn anim: still unrigged/static (CC-C7 placeholder clip round).
## Status
ASSET LANE COMPLETE on both. Game wiring is CC-C7 behavior lane (separate
dispatch, next round), AFTER Nicko reviews the final renders.