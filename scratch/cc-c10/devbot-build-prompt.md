You are Devbot, building change order CC-C10 (Farmer NPC + Dialog UI + Quest Seed)
in the Witch Hunter THREE.js prototype. Worktree: /tmp/wh-worldfeat, branch
feat/world-visuals, HEAD = e3444ec. You implement. You NEVER commit, push, or
run any git write command (status/log/diff/show only). NO browser, NO harness,
NO Playwright, NO server runs. Nicko's playtest is the acceptance of record.

READ FIRST (in order):
1. io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md     (the change order brief)
2. io/specs/testerbot-spec-wh-cc-c10-farmer.md            (validation spec — LIVE
   ANCHORS L1-L22 are your line-number map; PER-AC PROBE SPEC defines the bars;
   its AMENDMENT NOTES B1-B12 are sanctioned; your output must pass its probes)
3. skimming for pattern references: prototype/js/camp.js (tent menu DOM pattern),
   prototype/js/game.js (interact chain :1859-1864, updateInteractPrompt
   :2158-2185, setupSaveHooks :2549-2597, setupHud :196-207, loop tail :3060-3066)

IO RULINGS (binding, applied on top of the valspec):
- B3 = option (b): farmerBody = the RAW existing GLB
  'art-direction/3d/assets/races_regen/rigged/dwarf-male-smith.rigged.glb'.
  NO pixelated bake, NO new GLB files anywhere. Record the art-law waiver
  (placeholder-for-Astrabot) in your report.
- B2: direction copy is WEST (from the farmstead the den mouth is due west).
  HUD quest text: "Find the farmer's daughter - Old King's Barrow (W)"
  (ASCII hyphen, B11). Dialog line2 points westward.
- B1: the quest copy names the Region D den door "the Old King's Barrow"
  (lore naming, sanctioned); code-wise the target is CFG.regionD.door. Do NOT
  touch either door path or CONFIG door block (A6 byte-identity).
- B12: talk hook rank = between tryNotch and tryGather, prompt branch mirrored
  at the same rank in updateInteractPrompt.
- B9: prompt text = house style from CONFIG: "E - Talk" style is fine; put the
  string in CONFIG.regionC.npc, not game.js.
- B10: farmer stands in bind pose, accepted for this placeholder (RECORD in
  report). Stand-in box until lateSwap comes free via WH_ASSETS.instance.
- B6: farmer name comes from CONFIG ("Farmer Aldric"); a small DOM label in
  npc.js is accepted (form is RECORD, not gated).
- B5/B4/B7/B8 as written in the valspec: H1-H6 hunks only in game.js; dialog
  + quest-line DOM built in npc.js with inline styles + own el() copy; ledger
  via scratch/cc-c10/ledger3 copies; builds/v8-playable.html rebuilt.

BUILD ORDER (do these in sequence; verify each before moving on):
1. CONFIG.js: add regionC.npc block (asset 'farmerBody', x/z within 25 m of
   cottage (150.5,-256.7), rotY facing the yard/road, interactM 3, name
   'Farmer Aldric', dialog block with >= 4 strings: line1 greeting+daughter
   taken, line2 Old King's Barrow + WEST hint, line3 activation, repeat line
   "The barrow door, hunter. Bring her home.", plus Continue/Close button
   labels) and regionC.quest block { id 'findDaughter', states
   ['available','active','complete'] } after regionC.rotLair close, before
   regionC close. Tag every added hunk with a `// CC-C10` comment.
2. assets.js MANIFEST: add farmerBody key (raw dwarf GLB path) after
   rotspawnBody-ish area and okFarmBarn = 'art-direction/3d/assets/old_king/
   ok-farm-barn-pixelated.glb' after okRuinColumn. MANIFEST keys only.
3. NEW prototype/js/npc.js: window.WH_NPC = { init, update, talkPrompt,
   openDialog, closeDialog }. Farmer mesh cloned via WH_ASSETS.instance /
   SkeletonUtils clone, planted at WH_GROUND.footY/heightAt for regionC, only
   visible + interactable when regionManager.logic.activeId === regionC.id,
   culled by CFG.regionC.cullDistanceM or explicit npc cullM. Local el() copy
   (camp.js pattern). Dialog panel: root overlay appended to #wh-root with
   inline styles, classes inv-panel/inv-title/cook-btns/cook-btn; 3 lines
   advance on Continue; on line 3 set quest state 'active' EXACTLY once; Close
   closes; Esc closes; state-aware re-talk when already 'active' shows only
   the repeat line; NO 'complete' assignment anywhere. Open/close pairs
   player.setInputSuspended + game.inventoryUI.blocked (camp.js pattern); any
   open dialog forces the interact chain guard to refuse (E must not advance
   the chain while talking). Death/region change force-close. ZERO
   player-facing string literals in npc.js - all from CONFIG.
4. index.html: add exactly one line `<script src="js/npc.js"></script>` between
   camp.js and save.js.
5. game.js hunks ONLY H1-H6:
   H1 interact() chain (:1862-1863): insert tryTalkNpc() between tryNotch() and
      tryGather(); all 8 existing terms in original order; guard :1860
      untouched; tryTalkNpc returns false when WH_NPC absent/out of range/not
      in region C; define tryTalkNpc near the other try* fns.
   H2 updateInteractPrompt (:2158-2185): one new else-if branch after the
      notch branch, before the gather else; text from CONFIG.
   H3 WH_NPC.init(game) call after `game.camp = new WH_CAMP.Camp` (:2517).
   H4 WH_NPC.update(dt) in the loop tail (:3060-3065 group).
   H5 setupSaveHooks (:2563-2583 region): additive-only questState wrap - in
      S.capture add data.questState = { findDaughter: <holder state> } next to
      data.lairs; in S.save add stored.questState next to stored.lairs inside
      the same try; in S.restore hand data.questState back with schema-v1
      fallback (missing/non-object/bad state -> 'available'). Comment block
      names CC-C10 like the CC-C7 one. One source of truth (RECORD which:
      WH_NPC state or game.questState). save.js byte-identical.
   H6 HUD quest line: new element (id wh-quest-line) created in JS, appended
      to #wh-hud near the setupHud area, positioned under #wh-gate-hint with
      inline style; per-frame toggle strictly on findDaughter === 'active';
      text from CONFIG. setGateHint + #wh-gate-hint byte-identical.
6. Barn row: exactly ONE regionC.props row appended (asset 'okFarmBarn',
   cullM 140, rotY + scale present, `// CC-C10` tag), placed within 60 m of
   the cottage, >= 26 m from every other props row and every camp fire,
   >= 8 m from road centrelines; sit slope RECORD. Write a scratch/cc-c10/
   probe script (ledger2_probe.js pattern) proving the distances offline
   before pasting (probes before paste law).
7. Ledger: create scratch/cc-c10/ledger3.py + ledger3_probe.js (copies, do
   NOT edit scratch/cc-c17/): T gains okFarmBarn (max(29500, GLB header tris))
   and farmerBody counted via the argv[6] hook (GLB header tris). PASS = worst
   <= 1,980,000 at all THREE centres (0,-366) R170, (-175,-266) R170,
   (150.5,-256.7) R170; missing list empty; whole-disc R280 recorded.
8. node --check on npc.js CONFIG.js assets.js game.js and every scratch/cc-c10/
   *.js (node binary: find the playwright-bundled node if bare node is absent).
9. python3 tools/build_v8.py; grep WH_NPC + findDaughter in the bundle; RECORD
   bytes.
10. Report: io/reports/2026-10-25-cc-c10-farmer.md - asset key + path, quest
    key + holder choice, RULINGS applied (B3b/B2/B1/B12), ledger 3-centre
    numbers, barn probe distances, farmer texture note (raw, A-pose expected),
    bundle bytes, any deviations. END your run with the finish line, EXACTLY:
    CC-C10 DONE farmer farmerBody quest findDaughter ledger PASS build <bytes>

HARD LAWS (PRES is validated post-build; violations = BLOCK):
- Write scope EXACTLY: prototype/js/CONFIG.js, prototype/js/assets.js,
  prototype/js/npc.js (new), prototype/index.html, prototype/js/game.js,
  prototype/builds/v8-playable.html (build artifact), scratch/cc-c10/**,
  io/reports/2026-10-25-cc-c10-farmer.md. NOTHING ELSE - no camp.js,
  daynight.js, player.js, save.js, style.css, touch-controls.js,
  region-manager.js, region-defs.js, enemy.js, wh-ground.js, no
  art-direction/** files, no scratch/cc-c17/* edits, no tests/.
- No git write ops. No commits. HEAD must still be e3444ec when you finish.
- CONFIG.js/assets.js diffs = additions only, inside the sanctioned areas.
  regionA/regionB byte-identical; every pre-existing regionC row
  byte-identical.
- No browser/harness/Playwright. Offline node probes only.
- Placeholder art only: no Astrabot, no Meshy, no new GLB files.
- If a probe fails, fix and re-run before pasting. Copy law: new code follows
  the existing file's style exactly (var, IIFE, window globals).
MANDATORY: when you finish, also write your full summary (what changed, probe
outputs, deviations) to /tmp/delegation_result_ccc10_build.md.