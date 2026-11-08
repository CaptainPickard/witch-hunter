# Rot Mother — Meshy text-to-3d QA verdict (Astrabot, 2026-10-11)

**OUTCOME: STOP. All 3 attempts failed QA. Budget exhausted per brief (max 3 gens).
No intake bake, no races/ or races_regen/ files written, nothing wired into the game.
IO/Nicko decide: accept a defective candidate, change the design, or switch path.**

Renders: `attempts/aN_{front,34,side}.png` (768 px, Blender 4.5.4 Workbench, grey clay,
ortho) + `aN_strip.png` (the 3 angles side by side) + `aN_thumb.png` (Meshy thumbnail).
Request records (prompt, params, task id, credits): `attempts.json`.
Kill-check numbers come from `scratch/rotmother_cc.py` (trimesh, vertices merged, face-adjacency components).

All three are `text-to-3d-preview` = GEOMETRY ONLY (no UVs, no texture; a1 had
POSITION+NORMAL only). That is the grey-clay tell. Any pass would still have needed the
Round G flat-colour fallback or a paid refine pass (see the watch-items).

| # | task id | credits | tris | components / detached faces | verdict |
|---|---------|---------|------|-----------------------------|---------|
| 1 | 01a1299d-a8f5-7589-a60b-b927df81053f | 20 | 1,260,752 | 1 / 0 (0.00%) | FAIL: identity |
| 2 | 01a129a0-6f23-77e3-9b7b-6d13c9144340 | 20 | 3,064 | 42 / 67 (2.19%) | FAIL: menace + cloth + fragments |
| 3 | 01a129a1-8365-724b-939d-f7689bf35d5e | 20 | 2,817 | 199 / 491 (17.43%) | FAIL: fragments + cloth + no belly |

## Attempt 1 (seed 71101, no remesh)
- Form: hunched, gaunt long arms, distended belly, very long spindly clawed fingers, forward
  neck in side view. The menace is strong and it is the best creature read of the three.
- Kill-checks: floating fragments NONE (1 component). Melted blobs none. Holes none visible.
  No base plane.
- **Wrong identity:** it does not read as female. It reads as a sexless or male alien ghoul.
  The head is a large bulbous alien skull, not a small sunken one. The "moss" came out as
  bony coral spikes on the head and forearms.
- Polycount: target_polycount was ignored without should_remesh. The mesh is 1.26 M tris
  (30.3 MB), which cannot ship as-is.

## Attempt 2 (seed 71102, should_remesh + triangle, 3000)
- Delta vs 1: explicit woman/crone markers (wide hips, hair in thick fused clumps), "tiny
  shrunken head", softer moss mounds, should_remesh on.
- Form: clearly female, with a huge swollen belly. But it reads as a plain pregnant woman in
  a ragged skirt. No hunch, a normal-size head, zero menace. **Wrong identity (tone).**
- Kill-checks: a ragged cloth skirt, which the brief bans. 41 small detached bits (67 faces)
  at the shoulder/hair knot and the skirt hem.

## Attempt 3 (seed 71103, should_remesh + triangle, 3000)
- Delta vs 2: dropped "pregnant", added "monstrous... inhuman, no clothing / no cloth",
  "deeply hunched, head thrust forward below the shoulders", "grossly bloated corpse belly",
  big smooth moss lumps.
- Form: female, hunched, gaunt arms, clawed hands. The head is forward in the side view and
  it is creepier than 2.
- **Fails:** the signature bloated belly is GONE (the torso is slim). A shredded skirt
  appeared anyway despite "no clothing / no cloth". There is a **shard explosion**: 198
  detached pieces (491 faces, 17.4%) in the skirt strips and the hair. Hard kill.

## Evidence-bank read
- The brief's prompt is self-contradicting for text-to-3d. "Bloated belly" pulls the model
  toward a pregnant-woman template (a2), and Meshy's preview model then adds clothing.
  "Monstrous creature" pulls toward a sexless ghoul (a1). Every attempt held only 2 of the
  3 must-haves (female, bloated, menacing).
- Remesh at 3000 tris turns thin hair and cloth into detached shards (a2 2.2%, a3 17.4%).
  The un-remeshed a1 was perfectly connected.

## Watch-items / options for IO + Nicko
1. **Accept a1 with defects.** Connected, menacing, and the belly is there, but no female
   read. Needs (a) a declared, QA'd decimation to game budget (Blender decimate or a Meshy
   remesh task) and (b) colour: the Round G flat rot-green fallback, or a Meshy refine
   texture pass (a paid task on the preview id). Raw GLB kept locally, not committed (30 MB):
   `scratch/rotmother-qa/dl/a1.glb`.
2. **Switch to image-to-3d.** Draw or generate a concept ref that pins all three traits
   (female crone + bloated + hunched, no cloth). The ref-craft path controls identity far
   better than text. About 20 credits per attempt.
3. **Design change.** Drop the female read (a1 as "the Rot Mother" by name and lore only)
   or drop the belly (a3's silhouette, but it would need a no-remesh regen to kill the shards).
