# ASTRABOT ORDER B BRIEF - WITCH HUNTER CAMP KIT GLB (stage 3 arc, rides C2/C3)

Asset lane: Astrabot (meshy gen + blender bake). Brief committed to
io/missions/ per standing law. NO dispatch until Nicko says so.

## Goal
One new GLB: the WITCH HUNTER CAMP KIT - a small deployable campsite the
player sets from the CAMP button (C3). Not a loose pair of props: a composed
site, readable at DS-bonfire distance.

## Composition (one GLB, origin at ground center, Y-up, meters)
- RIDGE TENT: A-frame canvas, worn and weather-stained; ~2.2m long, 1.4m
  wide, 1.1m tall. Slightly askew (hand-pitched, not factory).
- BEDROLL: rolled blanket + strap, lying at the tent mouth, offset so the
  interact point faces outward.
- FIRE PIT: ring of 5-7 fire-blackened stones with charred stubs inside and
  a soot decal feel at center - deliberately modest, NOT the bandit
  campfire's iron tripod look (this is the PLAYER's camp).
- Staked corners: 4-6 small pegs + taut line hints on the tent.

## Canon laws (binding, from the art bible)
- Pixelated everything: 512px NEAREST + 5-bit posterize, raw mesh as-is
  (28-32k tris target, hard ceiling ~35k), no geometry post-processing.
- PALETTE: darkwood - desaturated canvas (warm grey-green), aged leather
  straps, charcoal stones. ONE ACCENT per frame: the amber fire-glow tint on
  the pit stones' inner faces ONLY (human fire = amber, no cyan, no red).
- Tone: gothic, moonlit-world, lived-in melancholy. Nothing cheery.
- Deliver BOTH: raw .glb + -pixelated.glb (the pipeline pair, same as other
  families). Name: wh-campkit (+ wh-campkit-pixelated).
- Path: art-direction/3d/assets/camp/ (new family).

## Tech requirements
- ONE mesh per element (tent, bedroll, pit, pegs) so C-day can toggle/hide
  pieces; node names: tent, bedroll, firepit, pegs.
- Ground-contact base: no undersides visible from any of 0/120/240 persp
  angles (the Round J lesson); flat shading OK, weld rims.
- Origin centered between tent and pit; scale 1:1 to meters (props scale in
  engine: CONFIG row will place at scale 1.0).
- No rig, no animation, no embedded textures beyond the atlas.

## Verification (cheap, allowed by the no-harness law)
- Headless Blender: byte invariants + node names present + tri count report.
- Static geometry probes + 3-angle ortho renders for the underside check.
- NO game run, NO chromium, NO harness.

## Land
- Commits on feat/world-visuals: assets commit + docs proof stills; build
  commit only if CONFIG wiring is in scope for this order (it is NOT -
  C3 wires placement; stop at the asset commits).
- Report: tri counts per node, palette check, proof-still list, commit shas.

## DISPATCH ADDENDUM (IO, 2026-10-06 evening - reads BEFORE starting)

- DISPATCHED 10-06 by Nicko's order ("dispatch astrabot as much as
  possible"), parallel to the C4 save-order builder.
- LANE ISOLATION (hard law, two builders in one worktree): touch ONLY
  - art-direction/3d/assets/camp/**        (new family, your outputs)
  - scratch/campkitgen/**                  (your working dir: refs, mats, bakes, logs)
  - scratch/campkit_*.py                   (clones of the tree/torch pipeline helpers)
  - scratch/MANIFEST.torch-style entries   NONE - MANIFEST.json is CODE LANE: DO NOT EDIT
  Absolutely NO other paths. If you believe a MANIFEST/CONFIG edit is
  required, STOP and report instead - IO wires the manifest row.
- MESHY_KEY: provided in your shell environment at dispatch (env-only).
  Never echo it, never write the key value to any file, never commit it.
  Balance was 1107 at dispatch; FLOOR = 1087 (cap 20 credits this mission:
  ~3cr ref + 15cr mesh + headroom for ONE re-roll). SERIAL ONLY: one
  submit, confirm task id, let it return, then the next. The floor check
  in your cloned helper points at START_BALANCE=1107.
- Pipeline (torch precedent, clone per-mission): scratch/torch_meshy.py
  (t2i + i23d, serial, nano-banana ref), scratch/ref_matte.py,
  scratch/torch_bake.py -> campkit_bake.py (posterize512 + export,
  NORMAL injection, camp/ naming), scratch/tree_gate.py for component
  sanity, torch_qa/qa_sheet pattern for the proof stills. meshy-5,
  quad topology, target_polycount 15000-22000 (28-32k tri law gives
  headroom; hard ceiling 35k).
- NO harness runs, NO chromium, NO headless browser of ANY kind; no game
  runs of any kind. Verification = byte invariants, node-name probe,
  tri counts, 3-angle ortho/proof RENDER stills only (Nicko playtests).
- Commit identity CaptainPickard <pickard.nicko@gmail.com>. Commit unit:
  assets+scripts in one commit, QA stills in the next. Push
  origin feat/world-visuals after EACH commit. Before each commit:
  git fetch + confirm origin tip == your local tip (another builder is
  landing commits in parallel; if it moved, rebase your work: fetch +
  rebase onto origin/feat/world-visuals, re-verify, then continue).
- Commit ONLY your lane paths above; never stage anything else.
  FINAL REPORT: <= 30 lines: commits table (sha | content), tri counts
  per node, palette check sentence, proof-still list, watch items.