You are Devbot, building change order CC-C11 (Rescue + Reward: quest completion
chain + CAMP CHEST) in the Witch Hunter THREE.js prototype. Worktree
/tmp/wh-worldfeat, branch feat/world-visuals, HEAD = 512d82f. Do NOT commit or
push (IO owns the git gate).

SPECS OF RECORD (read all three in full before touching code):
1. io/missions/2026-10-25-cc-c11-rescue-chest.md (order brief; rulings
   R-C11.1..6 already applied - do not re-litigate).
2. io/specs/testerbot-spec-wh-cc-c11-rescue.md (validation spec - the
   authoritative anchor set with line numbers; amendments B1-B14 are
   SANCTIONED as written; follow its probe definitions exactly).
3. io/reports/2026-10-25-cc-c10-farmer.md (C10 build precedent: module
   patterns, save-wrap pattern, report + probe conventions to mirror).

BUILD REQUIREMENTS (summary; the valspec is authoritative on details):
- CONFIG.js: completion lines + rescued HUD text keys in regionC.quest;
  sarcophagus row in regionD (den-local, probe-clear d_lair >= 12.5m per
  B5, inside den disc r34, seeded, seed labeled); CONFIG.camp.chest block
  (offset beside pegs, interactM, capacity 24); chest text keys.
- assets.js: MANIFEST-ONLY additions: stoneSarcophagus (crypt
  stone-sarcophagus-pixelated.glb) + dwarfFemaleBody (races_regen
  dwarf-female.rigged.glb, RAW per R-C11.3/B10). Not bootCritical.
- NEW js/chest.js: window.WH_Chest = { init, update, interactPrompt,
  tryOpen, capture, restore }; procedural chest body; spawns only when
  quest 'complete', beside pegs of the deployed camp site (derive from
  WH_Camp.camps(), re-place-safe, camp.js UNTOUCHED); panel opens ONLY
  within CONFIG.camp.interactRadius; 24-slot 6x4 tent-menu style; own el()
  copy (B4); deposit/withdraw via WH_Inventory item model
  (addItem/removeItem); capture/restore = 24-slot array (B7).
- npc.js extension: rescue interaction (sarcophagus proximity in D while
  quest 'active': dialog line -> questState.rescued=true + toast); daughter
  placeholder (dwarf-female body) via state-driven visibility (B3): hidden
  until rescued; appears beside farmer at homestead after rescue; return
  talk while rescued -> state 'complete' + completion lines + completion
  HUD text (fixes the C10 repeat-line deviation, B11).
- game.js sanctioned hunks ONLY: interact chain gains tryRescue then
  tryChest between tryTalkNpc and tryGather (B12 binding order);
  updateInteractPrompt mirror branches; WH_Chest.init after WH_NPC.init;
  WH_Chest.update(dt) in loop tail after WH_NPC.update(dt); setupSaveHooks
  chest block capture/restore beside questState (schema stays v1, additive).
- index.html: ONE new script tag js/chest.js after npc.js (L1 order).
- Build: python3 tools/build_v8.py; node --check every touched js file;
  bundle rebuilt; grep the bundle for markers.
- Ledger: python3 scratch/cc-c10/ledger3.py re-run -> must be BYTE-EQUAL
  PASS at all 3 centres (B14; regionC untouched).
- Probes FIRST: run scratch/cc-c11/tb_den_geom.py for the sarcophagus
  site; probe before paste; seeds labeled; copy law.
- Probes into scratch/cc-c11/; report to io/reports/2026-10-25-cc-c11-rescue-chest.md
  (rows, coords, probe outputs, ledger lines, deviations list, build bytes).
- Deviations: any brief/valspec mismatch you hit = a numbered deviation
  note in the report, never a silent workaround.

HARD LAWS: No harness/browser/server. No git commands other than reading
(git status/diff/log). Write scope EXACTLY: CONFIG.js, assets.js, js/chest.js
(new), js/npc.js, game.js, index.html, scratch/cc-c11/*, io/reports/*.
NOT TOUCH: save.js, enemy.js, camp.js, player.js, cooking.js, style.css,
touches-controls.js, region-defs.js, A/B region rows, docs/, io/specs/,
io/missions/.

FINISH LINE (final message, exactly):
CC-C11 DONE rescue daughter chest ledger PASS build <bytes>

MANDATORY: when you finish, write your complete summary to
/tmp/delegation_result_c11_build.md including: what you changed (files +
hunks), commands run (with outputs), ledger lines, deviations list, and any
blockers. Your result will NOT be visible in the chat unless you write this
file.