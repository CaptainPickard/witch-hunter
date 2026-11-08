# ASTRABOT MISSION BRIEF - Torch GLB asset (small: one mesh, pipeline, manifest; NO game wiring)
2026-10-05, from IO. Nicko's order (10-05 stage-2 design round):
- Torch = gear item, EITHER hand, drives the existing item light stat
  (CONFIG.items[*].light, mechanism LIVE since the light order).
- Ship the mesh FIRST as its own mission; the gather/drop code order wires it later.

You are Astrabot, Claude Code print-mode agent, worktree /tmp/wh-worldfeat
(branch feat/world-visuals).

## 0. LAWS (hard)
- NO automated harness or headless-browser runs. Nicko's playtest + the ortho
  QA sheet are the gates for ASSETS (asset lane exception, same as the tree
  missions: ortho_preview.py sheet, Nicko eyeballs).
- Art law: pixelated pipeline (512px NEAREST + 5-bit posterize), raw mesh as-is
  (28-32k tris max), darkwood palette, ONE accent per frame (amber flame = the
  human fire accent; the ember head glows amber, everything else darkwood/iron).
- Every parameter from CONFIG or the build script; commits + pushes to
  feat/world-visuals per sub-block.

## 1. DELIVERABLE (one asset + plumbing)
1. MESH: torch GLB via the standard pipeline (Meshy draft -> pixelate pass ->
   mesh, same chain as m16/m17 missions). Hand-held scale: roughly 0.55-0.7
   units tall (compare: roundShield ext ~2.0 raw units with weaponScale ~measured;
   longsword 0.528 weaponScale - measure and set CONFIG weaponScale-style entry:
   CONFIG.assets.weaponScale.torch = <measured>).
   - Shape: darkwood shaft, iron wrap ring, ember/flame head (amber accent,
     slightly emissive-looking via texture even though the REAL light is the
     item light stat).
   - NO skeleton/rig needed - it mounts to a hand bone like the shield
     (attributes POSITION+TEXCOORD_0+NORMAL preferred so it lights properly;
     the shield shipped without NORMAL and assets.js rebuilds normals - match
     the shield's attribute set is fine).
2. MANIFEST: assets.js MANIFEST.torch = 'art-direction/3d/assets/weapons/
   torch-pixelated.glb' (weapons/ dir like round-shield).
3. CONFIG.items.torch: REAL item entry (kind 'torch', hands both,
   stackCap 1, glyph 'TR', category 'gear') + block: none + light:
   { color 0xffa040, intensity: matched to ~1.3x firebolt's feel (firebolt =
   intensity 10.0 distance 12; torch target: intensity 9-11, distance 14-16,
   decay 2, flickerPct 7) - final numbers in CONFIG with a comment that
   playtest tunes them }.
   - kind: ADD 'torch' to the hand kind vocabulary (caster/melee/shield stay;
     torch is NOT a caster - RMB with only a torch does nothing; torch +
     glove both equipped = both lights live, item stat on the torch hand).
4. QA sheet: scratch/torch-qa/ ortho sheet (ortho_preview.py pattern) - front/
   side/top, pixelation visible, palette check.
5. REPORT: scratch/astrabot_torch_asset_report.md - pipeline log, measured
   ext + chosen weaponScale, attribute set, manifest/CONFIG diffs, AC table.

## 2. EXPLICITLY NOT IN THIS MISSION
- No hand-mount wiring (the code order does setupHandMeshes-style mount +
  torchTargetHeight + per-hand light hookup).
- No drop/gather flow. No enemy drops.
- No CONFIG.gather at all.

## 3. AC (Nicko eyeballs the sheet + the file lands)
| AC | Test |
|---|---|
| T1 | Torch GLB exists at the manifest path, loads via the standard loader (a viewer script or the loader smoke path WITHOUT headless browser - static GLB parse in Python is fine) |
| T2 | Pixelation: 512 NEAREST + 5-bit posterize evident in the QA sheet |
| T3 | One accent: amber flame head, everything else darkwood/iron |
| T4 | Manifest + CONFIG.items.torch (with light stats) + weaponScale committed |
| T5 | 9 existing clips + all previous art untouched (no GLB others modified) |

Final chat message: commits with shas, measured scale numbers, AC table.