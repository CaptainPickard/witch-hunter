# CC-C10 · Farmer NPC + Dialog UI + Quest Seed (change order)

Doc 63 Phase 4, first order. Dependencies CC-C4/C5-C17 SATISFIED (heightfield,
y-feed, den/Barrow door, farm set-dressing all landed). Doc 62 §13 process law:
ONE order, one builder run, playtest-approved before CC-C11 opens.

## GOAL

Nicko walks to the farmstead at the east half of Region C (homestead cluster
(150.5,-256.7) from CC-C17), talks to a farmer NPC, learns the quest ("my
daughter was taken into the Old King's Barrow"), and the quest activates with
a HUD line tracking it. Farmstead becomes a destination, not scenery.

## CONTEXT (verified 2026-10-25, feat/world-visuals @ 58ea081, worktree
/tmp/wh-worldfeat; serving 8793/current = releases/58ea081)

- Farm set-dressing IN PLACE (CC-C17v2): cottage, well, 6 fence posts,
  2 stonewalls, gate, 2 corner-v2, lanternPost at the homestead site, regionC
  giant rows carry cullM:140. DO NOT move/re-place these rows.
- Farmhouse BARN is NOT yet placed: ok-farm-barn-pixelated.glb exists on disk
  (art-direction/3d/assets/old_king/), not in the manifest.
- Barrow door exists as the quest target (CC-C8): CFG.regionC.door with
  locked toast game.js:1940 pattern, door at the SW den corridor.
- Doc 63 CC-C10 asset ruling STANDS: placeholder farmer first, Astrabot
  farmer/daughter/farmhouse flagged, NO Astrabot dispatch without Nicko.

## PLACEHOLDER FARMER ASSET (decided, no clarify needed)

- Body = art-direction/3d/assets/races_regen/rigged/dwarf-male-smith.rigged.glb
  (rigged villager-class body already on disk). Add manifest key farmerBody.
- Pixelation: if the GLB already ships pixelated-textured, use as-is. If it
  ships raw-textured, bake the pixelated variant with tools pixelate pipeline
  (color pixelation only, 512px NEAREST + 5-bit posterize, geometry as-is —
  the v3 art law) into assets/races_regen/rigged/ and point farmerBody at it.
- NO animation wiring: static pose, root placed ON the heightfield via
  WH_GROUND.heightAt. Idle sway v1 = none (keep the order small).
- Name plate: small DOM label like the lanternWaymarker sign pattern, text
  "Farmer Aldric" (T table entry, CONFIG string, not hardcoded).

## THE WORK

1. js/npc.js — NEW FILE, minimal surface:
   - window.WH_NPC: init(game), update(dt), talkPrompt(near bool/text),
     openDialog(farmer), closeDialog().
   - Farmer world row lives in CONFIG.regionC.npc: { asset: farmerBody,
     x, z, rotY facing the yard/eastRoad, heightAt footY via wh-ground
     (same pattern as props), interactM ~3 }.
   - Registration: CONFIG first (data rows), npc.js added to index.html
     AFTER camp.js BEFORE save.js (DOM builder + per-frame update; needs
     THREE + el() pattern from camp.js; save.js wrap untouched this order).
2. Dialog panel — tent-menu style (camp.js:236 pattern, inv-panel +
   cook-btns classes, el() helper). Open via E / touch USE when within
   interactM (hook INTO the existing game.js:1859 interact() chain AFTER the
   lock-skip / door / notch / cook / sleep checks — order: farmer sits with
   interactStation, no conflicts expected; reason-naming prompt toast or
   world label when in range: "Talk (E)").
   Panel content v1: 3 dialog lines progressing on click / button
   ("Continue"): line1 greeting + daughter taken; line2 "the Old King's
   Barrow" + door direction hint (SW, past the oak sentinels); line3 ->
   quest activate + Close. Re-talk after activation shows short state-aware
   line ("The barrow door, hunter. Bring her home."). All strings in
   CONFIG.regionC.npc.dialog (T-table convention).
3. QUEST STATE — additive, lairs-block pattern (game.js:2559 CC-C7 wrap is
   the template):
   - CONFIG.regionC.quest = { id: 'findDaughter', states: ['available',
     'active', 'complete'] }.
   - game.js WH_SAVE wrap gains questState block: { findDaughter: state
     string } captured in S.capture + S.save next to lairs, restore() hands
     it back (schema v1: older profile = quest 'available').
   - Advance to 'active' on dialog line3; 'complete' is CC-C11's job (do
     NOT wire completion this order).
4. HUD quest line — single line under the existing gate-hint element
   (game.js:201 wh-gate-hint pattern): active quest text
   "Find the farmer's daughter — Old King's Barrow (SW)" shown ONLY when
   questState.findDaughter === 'active'. No new HUD framework.
5. Farmhouse barn (small, in-scope per CC-C10 'farmhouse placeholder kit'):
   add okFarmBarn manifest key + ONE regionC.props row at the homestead
   (rotY facing the road, probe >= 26m from other props per cluster rules,
   cullM:140 per ROW SHAPE LAW). Ledger: rerun scratch/cc-c17/ledger2.py,
   both centres must stay <= 1,980,000.
6. SAVE/LOAD: questState must survive save + restore + the C4 boot class
   restore path. Death does not reset quest state.
7. BUILD: python3 tools/build_v8.py; node --check on every edited js;
   grep markers; bundle rebuild; report file.

## HARD LAWS (doc 62 §13 + standing)

- No git operations. No harness. No browser/server. Probes before paste.
- Write scope: CONFIG.js + assets.js (MANIFEST keys only) + NEW js/npc.js +
  index.html (one script tag) + game.js (interact chain hook + save wrap +
  HUD line) + scratch/cc-c10/ + io/reports/. NOTHING ELSE.
- A/B region rows byte-identical. camp.js/daynight.js/player.js untouched.
- Copy law. Seeds labeled. Ledger PASS required (<= 1,980,000 both centres).
- Placeholder art only; Astrabot farmer/daughter/farmhouse flagged, not
  dispatched.

## ACCEPTANCE (Nicko playtest, no harness)

A1 Walk B->C, farmstead reachable at the heightfield (footY correct, no
   sinking, cull band correct at fog depth).
A2 Approach farmer: "Talk (E)" prompt appears; E / USE opens dialog.
A3 Dialog: 3 lines progress, quest activates on line3, panel closes.
A4 HUD line "Find the farmer's daughter — Old King's Barrow (SW)" shows
   while active.
A5 Save at camp, reload: quest still active, farmer still re-talkable with
   the short state-aware line.
A6 Barrow door NOT changed (locked toast still fires while dormant).
A7 fps holds at the homestead (ledger PASS, barn row culled past fog).

## FINISH LINE (final message, exactly)

CC-C10 DONE farmer <asset-key> quest <state-key> ledger PASS build <bytes>