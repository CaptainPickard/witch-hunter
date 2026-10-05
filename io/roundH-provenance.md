# Round H provenance: south spawn, cemetery fog, snare recolor, bramble

Two Claude Code runs on 2026-10-05. Brief: io/missions/2026-10-05-cc-roundH-tone.md.
The first run died mid-way with its work uncommitted. The continuation run
(io/missions/2026-10-05-cc-roundH-continuation.md) harvested that work as-is and finished the rest.

## Meshy credit ledger

| run | step | credits | balance |
|---|---|---|---|
| dead run | measured start (the brief said 1255) | | 1285 |
| dead run | t2i bramble ref (task 01a10961-f7aa-71b5-91aa-6816dad1ced1) | -3 | 1282 |
| dead run | i23d bramble, target 2000 tris (task 01a10963-2ac6-7165-93f5-45abfd962999) | -15 | 1267 |
| continuation | no Meshy calls | 0 | 1267 |

Total spent: 18 of the 30-credit cap. Log: scratch/tree_meshy_log.jsonl (START_BALANCE 1285, CAP 30).

## Dead run (harvested as-is, not redone)

- **South spawn**: CONFIG regionA.spawn = (2.5, 74.0). This is the midpoint between the south
  wall point on the path (0, 86) and the first lantern (5.04, 62). Checked by
  scratch/roundH_spawn_probe.py, output in scratch/roundH-proof/spawn_probe.json:
  - prop edge gap 4.88 m;
  - outside the keepOut (normalized distance 1.941);
  - nearest enemy 25.75 m (ghoul), 0 nudges;
  - 3.78 m off the path centerline (halfWidth 2.7), so it is off the ribbon. Nicko's
    midpoint order stands.
- **Cemetery fog ramp**: CONFIG regionA.cemeteryFog = keepOut zone hold_outskirts, density
  0.030, color 0x7f8ea6, rampStart 1.35, rampEnd 0.55. game.js cemeteryFogTick() is an O(1)
  smoothstep lerp between the region base and these targets, called from the frame loop.
- **Snare recolor**: scratch/snare_color_roundG.py writes two-tone COLOR_0 into
  biome_library/wh-bush-snare-pixelated.glb. The signed landing record is the last row of
  scratch/treeqa/roundH/snare_color.jsonl: canes sRGB [40,40,32], roses [136,104,104],
  rose_pct 45.9.
- **Bramble raw**: Meshy t2i ref, matted with ref_matte.py --dark, then i23d to
  scratch/treegen/roundH/wh-bramble-meshy.glb. The run asked for 2000 tris and got
  28355 tris with a 2048 texture. QA gate_a FAIL (6050 UV islands), see
  scratch/treeqa/roundH/gate.jsonl.
- Still 01-spawn-view.png.

## Continuation run (0 Meshy credits)

- **Decimate**: scratch/decimate_roundH.py takes the raw mesh from 28355 to 2499 tris
  (welded 15060 verts, then 1578 welded / 7497 unshared). It uses the same weld +
  fast_simplification as Round G. The texture is kept through a per-face UV transfer: each
  face takes the medoid texel of 4 closest-point probes on the raw mesh. Two runs give
  byte-identical output. Signed rows are in scratch/treeqa/roundH/decimate.jsonl.
- **Bake: texture path** (the raw has a baseColor texture). scratch/bramble_bake_roundH.py
  applies biome_pixelate.posterize512 (512 NEAREST + 5-bit) and export. It lands:
  - biome_library/wh-bramble-pixelated.glb
  - wh-bramble.glb (decimated mesh + raw texture)
  - raw/wh-bramble.glb (Meshy byte copy)
  - refs/wh-bramble-ref.png

  The bake is deterministic (byte-identical across two runs). The Meshy texture is
  greyscale because the t2i ref was grey, so the bramble reads as grey/brown canes with no
  rose colour.
- **Wire**: assets.js MANIFEST.bramble. CONFIG.scatter.bushes.assets is now
  [['bramble', 1, 1.4, 2.0]], with the rollback rows kept in a comment. atTreeRing stays
  whBushSnare. The wh-bush-a/b GLBs stay in the repo.
- **Mirrors** (scratch/roundH-proof/):
  - wall_mirror.json is byte-identical to Round G.
  - scatter counts are identical to Round G in both regions:
    - hold_outskirts: trees 14, rings 305, free 20, grass 220
    - darkwood_edge: trees 10, rings 130, free 20, grass 220
  - Both mirrors are deterministic across two runs.
- **Stills**:
  - 02-cemetery-fog-approach (fence mouth, w 0.942, density 0.029).
  - 03-bramble-snare-closeup: youngDeadTree (-76.3, 16.8), ring 4, nearest bramble 7.6 m;
    the camera is on the map-centre side and the player lantern sits between the camera
    and the pair.
  - 01 was kept from the dead run.
