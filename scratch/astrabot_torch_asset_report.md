# Astrabot report: torch GLB asset (2026-10-05)

Brief: io/missions/2026-10-05-astrabot-torch-asset-brief.md. Branch feat/world-visuals.
Result: **the torch landed on the first mesh attempt.** The GLB, manifest entry, CONFIG item and target height are all committed.
Meshy spend: **18 credits** (1444 -> 1426). One reference image and one mesh, no retries.

| commit | content |
|---|---|
| eb42745 | the torch GLBs, the reference image, and the Meshy and bake scripts plus their log |
| 4cdaf60 | the QA sheet, the QA renderer, and the static GLB parse check |
| c317a13 | MANIFEST.torch, CONFIG.items.torch and weaponTargetHeight.torch |

## Pipeline log

1. **Reference image.** Made with `scratch/torch_meshy.py t2i` on nano-banana. Task 01a10511-0e01-7134-a744-b8029e5cd4b1, 3 credits.
   The prompt asked for an upright torch on pure white with a darkwood shaft, one iron band, a charred cloth wrap with amber embers in it,
   and a short solid amber flame cap ("opaque, stylized, chunky"). It asked for no smoke, sparks or wisps, which come back as
   fragment clouds (lesson from the tree run).
   I used the first image. Output: `scratch/torchgen/torch-ref.png`.
2. **Matte.** `scratch/ref_matte.py` removed the background and cropped to the subject.
   Output: `scratch/torchgen/torch-ref-matte.png`. The same image is copied to `weapons/torch-ref.png`, the exact image sent to Meshy.
3. **Mesh.** `torch_meshy.py i23d` with meshy-5, quad topology, target_polycount 15000.
   Task id is in `scratch/torch_meshy_log.jsonl`. Cost 15 credits.
   It came back as one geometry with 30325 tris and a 2048 texture. The tris are inside the 28-32k law, so the mesh was used as-is.
   - Gate (`scratch/tree_gate.py`, welded): 11 components, the largest holds 30259 faces (**99.8%**), 0 far shards.
   - XZ center is (-0.003, -0.001) and ymin is -0.951, so the mesh is centered like the trees.
4. **Bake.** `scratch/torch_bake.py` is tree_bake.py with weapons-dir naming. It reuses `biome_pixelate.posterize512` and `export` unchanged:
   the mesh is left as-is, the texture is cut to 512px NEAREST with a 5-bit posterize, and NORMAL is injected.
   It writes three files to `weapons/`:
   - `torch.glb` (byte copy of the Meshy original, 2.5 MB)
   - `torch-pixelated.glb` (1.2 MB)
   - `torch-ref.png`
   - The pixelated file is about 10 times the size of round-shield-pixelated because it has about 30k tris, compared with the old weapons' ~2k. That is the same weight class as the m16-m19 trees.
5. **QA sheet.** `scratch/torch_qa.py` renders `scratch/torch-qa/torch-qa-sheet.png` and writes `torch-qa.json`.
   - Views: orthographic front, side and top, plus a close-up of the head.
   - Accent map: amber faces are highlighted and everything else is grey.
   - The 512 atlas is shown with two NEAREST 48x48 zooms.
   - It uses the tree_ortho.py renderer: no decimation and a true side view. The tree report explains why ortho_preview.py itself shreds 30k-tri meshes.
     This sheet adds a real top view (camera +Y).
6. **Load check (T1).** `scratch/torch_glb_check.py` reads the file the way GLTFLoader does, statically in Python with no browser.
   It checks the container, the JSON and BIN chunks, that every accessor stays in bounds, that attribute counts match, and that the image decodes.

## Measured numbers

| | value |
|---|---|
| raw ext X / Y / Z | 0.3342 / **1.8988** / 0.3341 (pos min y -0.9513, max y 0.9475) |
| GROUND_META.height (what weaponScale() divides by) | 1.8988 |
| chosen target height | **0.62 m** (brief range 0.55-0.7) |
| resulting scale | 0.62 / 1.8988 = **0.3265** |
| tris / verts | 30325 / 22587 |
| attributes | **POSITION + NORMAL + TEXCOORD_0** (the preferred set; better than the shield, which has no NORMAL) |
| texture | 512x512 PNG, every channel a multiple of 8 (5-bit); R/G/B levels 32 / 29 / 20 |
| material | OPAQUE, doubleSided, no skin, 0 animations |
| amber accent | 7.9% of surface area. The lowest amber face is at 0.81 of the height, and 0.0% of amber area is below 0.70 of the height |
| non-accent mean RGB | 24 / 20 / 17 (darkwood). The iron band reads mid-grey |

**Deviation (please read):** the brief says "CONFIG.assets.weaponScale.torch = <measured>". There is no such table.
`WH_ASSETS.weaponScale(name)` computes `CONFIG.assets.weaponTargetHeight[name] / measured GROUND_META height`.
So I set `weaponTargetHeight.torch: 0.62` and recorded the measured height and the resulting scale (0.3265) in the comment next to it.
This matches how longsword, handAxe and roundShield are set up. A separate weaponScale table would be dead config.

## Diffs (game side)

- `prototype/js/assets.js`: added `MANIFEST.torch = 'art-direction/3d/assets/weapons/torch-pixelated.glb'`.
  Side effect: the boot preload walks every MANIFEST key (assets.js:375), so the torch now loads at boot. That adds about 1.2 MB, about the same as one tree.
- `prototype/js/CONFIG.js`:
  - `items.torch` replaces the commented-out DORMANT example:
    `{ id: 'torch', name: 'Torch', glyph: 'TR', category: 'gear', stackCap: 1, kind: 'torch', hands: ['left', 'right'], equipHint: 'leftHand', light: { color: 0xffa040, intensity: 10.5, distance: 15, decay: 2, flickerPct: 7 } }`.
    It has no `block`. A comment says playtest tunes the light numbers.
  - The kind vocabulary comment now lists `'torch'`, with a note that it has no hand action.
  - `weaponTargetHeight.torch: 0.62`.
- **No `mesh` key on items.torch, on purpose.** `setupHandMeshes` instances every gear item that has a `mesh`.
  `applyHandVisuals` only mounts melee and shield items, so a torch mesh would be made visible but never parented to a hand.
  The code order adds `mesh: 'torch'` together with its mount.
- **kind 'torch' needs no code change today:**
  - `player.handAction` falls through to null, so a torch-only hand has an inert button and RMB does nothing.
  - `equipItem`'s no-mesh refusal only applies to melee and shield.
  - `light.js handLightDef` returns `item.light` before its caster check, so torch + glove gives two lights, with the torch's stat on the torch hand.
- The comment at inventory.js:12 still lists 3 kinds. I left it because it is outside this mission's scope.
- The item has no startingItems entry and no drop source, so nothing in play hands it out yet.

## AC

| AC | Result | Evidence |
|---|---|---|
| T1 GLB at the manifest path and loads | **PASS** | `torch_glb_check.py` on `weapons/torch-pixelated.glb` reports "T1 PASS: container + accessors + image parse clean" (static Python, no browser) |
| T2 pixelation evident | **PASS** | QA sheet atlas panel shows 5-bit=True on the 512x512 atlas, the two NEAREST zooms show hard texel steps, and the levels are 32 / 29 / 20 |
| T3 one accent | **PASS** (Nicko eyeballs) | Accent map: the amber is only the flame cap plus the ember specks in the wrap. It covers 7.9% of the area, the lowest amber face is at 0.81 of the height, and the shaft and band have none. The rest is darkwood 24 / 20 / 17 with a grey iron band |
| T4 manifest + item + scale committed | **PASS** | c317a13 |
| T5 nothing else touched | **PASS** | sha1 of all 234 pre-existing GLBs under art-direction/3d/assets is identical before and after; the only additions are torch.glb and torch-pixelated.glb. The player combat-chain GLB still has all 13 clips (the 9 originals + 4 shield clips) and races_regen has no diff |

## Notes for the code order

- **Grip:** the torch is symmetric about Y (XZ 0.334 square) with the butt at raw y -0.951.
  After groundAlign, the butt sits at holder y 0 and the flame at about 1.899 × 0.3265 = 0.62.
  The natural grip is the lower third of the shaft, about holder y 0.25-0.35 (unscaled about 0.5-0.65 above the butt).
  Measure it the way the longsword `gripHolderY` was measured.
- **Light anchor:** the light should sit at the flame cap (holder y ≈ 1.80-1.90 unscaled) rather than at the hand bone.
  Otherwise the hand will hide the light. That decision belongs to the code order.
- No in-engine check was run, per the NO HARNESS law. Nicko's playtest and this sheet are the acceptance gates.
