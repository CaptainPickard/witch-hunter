# CC-C13a · Astrabot asset-bake verdict sheet (Old King's Forest dressing set)

Batch: 16/16 Meshy bakes landed (batch resume by IO after the child's 30-min
session wall; 48 credits spent, 615 remain). Tri census + 3-angle QA renders
+ 4x4 review montage. IO vision-QA verdicts below. NOTHING WIRED INTO THE
GAME YET - per law, assets ship after Nicko reviews the renders.

## VERDICT TABLE (IO vision-QA on the review sheet + per-asset passes)

| Asset | Tris | Cap | Silhouette QA | IO verdict |
|---|---|---|---|---|
| ok-farm-cottage | 28,632 | 30,000 | roof/base proportions skewed, frayed edges | REVIEW - Nicko's eye (roof big; pixelate may save it) |
| ok-farm-barn | 35,112 | 30,000 | coherent long shed | TRI-DECIMATE (17% over) |
| ok-farm-haybale | 4,204 | 4,000 | mound OK | TRI-DECIMATE (5% over) |
| ok-farm-silo | 14,455 | 15,000 | peaked tower OK | PASS |
| ok-farm-well | 11,481 | 12,000 | kiosk-like well OK | PASS |
| ok-ruin-wall-straight | 8,367 | 8,000 | pedestal-like, fuzzy | PIXELATE + REVIEW |
| ok-ruin-wall-corner | 9,285 | 8,000 | coherent | TRI-DECIMATE (16% over) |
| ok-ruin-arch | 10,131 | 8,000 | ruined tower read OK | TRI-DECIMATE (27% over) |
| ok-ruin-column | 4,140 | 5,000 | (render bug; mesh fine) | PASS (re-render pending) |
| ok-ruin-rubble | 11,097 | 6,000 | coherent pile | TRI-DECIMATE (85% over) |
| ok-tree-oak | 28,721 | 30,000 | gnarled ancient oak PASS | PASS |
| ok-tree-pine | 26,714 | 25,000 | tall pine PASS | TRI-DECIMATE (7% over) |
| ok-fence-post | 2,866 | 3,000 | thin post PASS | PASS |
| ok-fence-corner | 55,738 | 2,000 | WRONG OBJECT (bolt/bracket, 27x over) | REJECT - regenerate |
| ok-fence-gate | 2,588 | 3,000 | PASS | PASS |
| ok-fence-stonewall | 2,487 | 3,000 | PASS | PASS |
(Empty tiles in the montage = the 3 column views lost to a TextureVisuals
bug + haybale views ordered after it; per-file renders all exist except column.)

## IO RECOMMENDATION (awaiting Nicko)
1. ACCEPT the 9 PASS / decimate-then-accept rows (decimation = the repo's
   proven mesh QA pipeline, scratch/cc-c8 decimate_m9.py pattern).
2. REGENERATE ok-fence-corner once (prompt: 90-degree timber fence corner,
   two rail sockets, 3 planks; image-to-3d from ok-fence-corner-ref.png).
3. PIXELATE everything (512 NEAREST + 5-bit posterize, art law) BEFORE the
   second look - the gray fuzz in these QA renders is the raw render
   helper, not the mesh.
4. THEN wire: farm site (quest giver), ruin clusters replace the C13b
   church-kit stand-ins, tree variants join the scatter, fence kit replaces
   the C13b-normalized picket/iron rows.

## FILES
Raws: scratch/treegen/old_king/raw/*.glb (16). Concept refs:
art-direction/concepts/old_king/*-ref.png (16). QA views (33):
art-direction/concepts/old_king/bake-qa/. Montage: review-sheet.png.
Log: scratch/treegen/old_king/old_king_meshy_log.jsonl.