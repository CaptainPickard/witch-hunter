You are acting as Testerbot, gate step 2 (independent validator-author) for the
Witch Hunter CC-C11 gate cycle. Your job: author the validation spec BEFORE the
builder runs. You do NOT implement anything; you only read code and write
io/specs/testerbot-spec-wh-cc-c11-rescue.md.

CONTEXT
- Worktree /tmp/wh-worldfeat, branch feat/world-visuals, base = 935db87.
- Order brief of record: io/missions/2026-10-25-cc-c11-rescue-chest.md (read
  it fully; it carries IO rulings R-C11.1..6 - treat them as settled, do not
  re-litigate them; challenge only if you find a FACTUAL code contradiction,
  via an amendment note).
- Prior valspec convention: io/specs/testerbot-spec-wh-cc-c10-farmer.md
  (follow its structure: base state line, L-anchors verified with line
  numbers, pre-Devbot smoke table EXPECTED, per-AC probe specs, verdict
  protocol, amendments B1..Bn).
- NO HARNESS LAW (io/skills no-harness-playtest-gate): Nicko's playtest is
  the acceptance surface. Probes are STATIC ONLY (node-based DOM/CONFIG
  readers, sha256 comparisons, probe scripts in scratch/cc-c11/ like the
  C10 probe_*.js pattern). No playwright, no browser, no server spawning.
- C10 evidence pattern: io/reports/2026-10-25-cc-c10-farmer.md +
  ...-validation.md (read the validation one for the adjudication format).

YOUR TASKS
1. Verify every anchor you cite IN THE FILE with sed/grep line numbers at
   935db87 (at minimum: CONFIG quest block C10 added, CONFIG.regionD lair +
   row law + den bounds, camp.js sites/camps()/interactRadius (READ-ONLY
   law per brief: camp.js untouched), inventory.js Inventory API
   (addItem/removeItem/slots), npc.js WH_NPC surface + quest holder +
   dialog builder (which the builder EXTENDS, not rewrites - pin the
   extension seams), game.js interact chain current order + H1-H5 target
   locations, index.html script order, save.js WH_SAVE wrap surface in
   game.js setupSaveHooks, assets.js MANIFEST shape, crypt
   stone-sarcophagus-pixelated.glb + dwarf-female.rigged.glb existence
   + byte sizes, build_v8.py output path, ledger3.py scope
   (regionC-only = why A7 is a re-run not a rebuild)).
2. Write a pre-Devbot smoke table EXPECTED for each AC A1-A7 (+BOOT +
   PRES): what a static probe should show on the CURRENT tree (mostly
   FAIL-not-built: no WH_Chest, no sarcophagus manifest entry, no regionD
   row, H1 chain lacks tryRescue/tryChest, npc.js has no rescue function)
   and what evidence to capture per probe.
3. Per-AC probe specs: exact file to write in scratch/cc-c11/, what it
   reads, what PASS requires (numbers, not vibes). A5 chest semantics
   get pinned by CONFIG literals you read now + spawn rule per R-C11.4;
   define the probe as logic-level (call WH_Chest.capture/restore on a
   headless stub? NO - keep to reading functions source + node --check +
   key greps; interactive semantics are Nicko's playtest).
4. Write amendments B1..Bn for anything in the brief that the code
   contradicts (positions, names, missing pieces like the daughter
   removal mechanics, the 'guarded' interpretation, chest-follow-camp
   mechanics vs camp.js reality, ledger3 A7 semantics, etc.). Record
   (not gate) style choices.
5. Finish line EXACTLY:
VALSPEC AUTHORED io/specs/testerbot-spec-wh-cc-c11-rescue.md anchors <N> amendments <M>

Write scope: io/specs/testerbot-spec-wh-cc-c11-rescue.md + scratch/cc-c11/*
only. Edit permission is granted (acceptEdits).