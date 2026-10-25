# CC-C11 · Rescue + Reward: Quest Completion Chain + CAMP CHEST (change order)

Doc 63 Phase 4, second order. Dependencies SATISFIED: CC-C10 78d8640 (quest
findDaughter active + dialog UI + questState save block + WH_NPC surface),
CC-C8 (den interior scene-swap + Rot Mother lair), CK1 (campkit pegs).
Design authority: doc 62 s7 (quest chain) + s8 (CAMP CHEST R-62.5) + s13
law (ONE order at a time). Worktree /tmp/wh-worldfeat, branch
feat/world-visuals; base = 78d8640 (CC-C10 tip; serving = this build).

## RULINGS (IO, recorded - no clarify round needed)
- R-C11.1 RESCUE FEEL: doc 62 s7 already adjudicates OQ-62.4: instant
  'rescued' state, NO escort mechanic; walk-out together is visual polish
  only. v1 read: on rescue the daughter placeholder REMOVES from the
  chamber and appears standing beside the farmer at the homestead (she is
  safe at home when you return). No follower AI, no walk-out pathing.
- R-C11.2 SARCOPHAGUS: the crypt kit asset stone-sarcophagus-pixelated.glb
  EXISTS on disk (art-direction/3d/assets/crypt/, already pixelated per
  the art law). Manifest it + place ONE row in regionD near the Rot Mother
  lair. Guarded = the lair enemies ARE the guard by C8 design; no new AI.
- R-C11.3 DAUGHTER PLACEHOLDER: dwarf-female.rigged.glb
  (races_regen/rigged, same dwarf family as the C10 dwarf-smith farmer
  placeholder). RAW (art-law waiver mirror of B3b: placeholder family),
  Astrabot-replaced later. Static, no collider, no clips required (mixer
  optional = bind pose is fine for v1, consistent with the farmer).
- R-C11.4 CAMP CHEST: procedural placeholder box (Astrabot chest GLB stays
  flagged). Spawns ONLY when quest findDaughter is 'complete', beside the
  campkit pegs OF ANY DEPLOYED campkit site (WH_Camp.camps() sites; if no
  site is deployed, it waits and spawns with the first deploy).
  Derive the chest position from the camp site each frame (rides the site
  list automatically: re-placed camps carry the chest; camp.js stays
  UNTOUCHED). Panel opens ONLY within camp interactRadius of a deployed
  site. 24 slots 6x4, tent-menu DOM styling, deposit/withdraw using the
  existing Inventory item model (addItem/removeItem, {id,count} slots).
- R-C11.5 QUEST STATE: states stay available -> active -> complete
  (3-state machine, doc 62). rescue interaction requires 'active' and sets
  an addititve rescued:true sub-field inside the findDaughter state object
  (do NOT add a 4th top-level state). Return talk while rescued:true moves
  to 'complete'. Completion = dialog copy change + HUD line change; this
  ALSO fixes the C10 deviation (the repeat line currently shows on
  'complete').
- R-C11.6 MODULES: new js/chest.js (window.WH_Chest: init, update,
  interactPrompt, tryOpen, capture, restore; owns chest panel + save
  block). npc.js owns rescue + daughter + completion lines. game.js owns
  chain hooks + save hooks + init/update calls. save.js UNTOUCHED (chest
  block rides the WH_SAVE wrap surface next to lairs/questState).

## THE WORK
1. CONFIG: regionC.quest gains completion lines + rescued HUD text keys;
   regionD gains the sarcophagus row (probe-clear: outside the Rot Mother
   lair body radius + lair dressing pool + the spawn->lair walkway, inside
   the den disc r34, den-local coords, seeds labeled); CONFIG.camp.chest
   block (offset beside pegs [~2.2, ~1.8] PROPOSED, interactM, capacity 24,
   stack rules inherit CONFIG.inventory); CONFIG.npc.chest text keys.
2. assets.js manifest: stoneSarcophagus (crypt path) + dwarfFemaleBody
   (races_regen path). NOT bootCritical (stand-in box law applies).
3. js/chest.js: procedural box body + lid, sit beside the pegs of the
   nearest deployed camp site (derive from WH_Camp.camps(); re-place-safe),
   visible only on 'complete'; E opens the 24-slot panel (tent-menu style,
   camp-gated); deposit/withdraw via Inventory calls; capture()/restore()
   = slots arrays only (never shipped item lists).
4. npc.js: rescue interaction (near sarcophagus in D while quest active:
  'rescue' dialog line + daughter swap + questState.rescued=true + toast);
   return talk while rescued:true -> 'complete' + completion lines + HUD;
   daughter placeholder at the homestead beside the farmer (post-rescue
   only, persists via questState.rescued).
5. game.js (sanctioned hunks only): H1 interact chain gains tryRescue()
   and tryChest() branches (order: ... tryNotch || tryTalkNpc || tryRescue
   || tryChest || tryGather); H2 updateInteractPrompt mirror branches;
   H3 init: WH_Chest.init(g) after WH_NPC.init; H4 update loop tail:
   WH_Chest.update(dt) after WH_NPC.update(dt); H5 setupSaveHooks: chest
   block capture/restore alongside questState (schema stays v1, additive).
6. index.html: ONE new script tag js/chest.js after npc.js.
7. BUILD: python3 tools/build_v8.py; node --check every touched js; bundle
   rebuilt; grep markers.
8. REPORT: io/reports/2026-10-25-cc-c11-rescue-chest.md (rows, coords,
   probe outputs, deviations, build bytes). Probes into scratch/cc-c11/.

## HARD LAWS (unchanged)
No harness/browser/server. No git commits. Probes before paste. Seeds
labeled. Copy law. node --check each edit.
Write scope: CONFIG.js + assets.js (MANIFEST only) + js/chest.js (new) +
js/npc.js + game.js (H1-H5 only) + index.html (+1 tag) + scratch/ +
io/reports/. NOT TOUCH: save.js, enemy.js, camp.js, style.css, player.js,
cooking.js, A/B/C region gameplay rows beyond the sarcophagus row.

## ACCEPTANCE (Nicko playtests; static-probe verifiable)
- A1 chain start talk still works (C10 behavior byte-preserved): active
  quest HUD line; sarcophagus E does NOTHING while quest not active.
- A2 sarcophagus in the den near the lair, probe-clear (lair body +
  dressing + walkway), manifest loads (200, stand-in OK), collider solid.
- A3 rescue: E at the sarcophagus while active -> dialog + rescued:true +
  toast; daughter placeholder REMOVED from chamber, appears beside farmer
  (persists via questState).
- A4 completion: return talk -> 'complete' + completion copy + HUD
  completion line; repeat-line-on-complete GONE (C10 deviation fixed).
- A5 chest: spawns beside pegs on the FIRST deployed camp after complete;
  follows camp re-placement; 24-slot panel opens ONLY within camp
  interactRadius; deposit/withdraw works both ways (Inventory model).
- A6 save/load: questState (complete + rescued) + chest slots + daughter
  visual all persist; older profile without the chest block loads clean.
- A7 ledger3 re-run PASS unchanged (regionC disc untouched; sarcophagus
  is regionD, chest is dynamic, daughter is npc-side).
- PRES: protected files byte-identical (save.js, enemy.js, camp.js,
  player.js, cooking.js, style.css, A/B gameplay rows); diff set == write
  scope; HEAD untouched (no builder commits).

FINISH LINE (final message, exactly):
CC-C11 DONE rescue daughter chest ledger PASS build <bytes>