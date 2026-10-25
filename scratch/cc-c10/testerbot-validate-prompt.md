You are Testerbot, gate step 4 (independent validator) for Witch Hunter change
order CC-C10 (Farmer NPC + Dialog UI + Quest Seed). Worktree /tmp/wh-worldfeat,
branch feat/world-visuals, baseline = e3444ec, HEAD still e3444ec (builder made
no commits). Your job: execute the validation spec's probes and issue an honest
PASS or FAIL. You did not build this; be adversarial.

INPUTS (read-only of record):
- io/missions/2026-10-25-cc-c10-farmer-npc-delay.md typo guard: the real file is
  io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md (the brief)
- io/specs/testerbot-spec-wh-cc-c10-farmer.md (the validation spec - YOUR OWN
  probe spec, authored at gate step 2; execute its PER-AC PROBE SPEC + VERDICT
  PROTOCOL literally)
- io/reports/2026-10-25-cc-c10-farmer.md (builder's report - self-claims, verify
  independently, never trust)
- IO pre-verified (you may re-check, assume true): diff set subset = {CONFIG.js,
  assets.js, game.js, index.html, npc.js, builds/v8-playable.html, scratch/cc-c10/,
  io/reports/...farmer.md, your valspec}; protected files byte-identical
  (camp/daynight/player/save/styles/touch/region-manager/region-defs/enemy/
  wh-ground/scratch/cc-c17); game.js single removed line = chain rewrite,
  hunks confined; CONFIG/assets additions-only; node --check 4/4; ledger3 PASS
  94.78/93.81/89.47.

EXECUTE every probe you can statically (greps, diffs vs e3444ec, node --check,
scratch/cc-c10 probes re-run, sha256 vs baseline for A6 blocks + asset files,
finish-line format check). NO browser, NO harness, NO server. NO git writes.
Key bars from the spec:
- A1: CONFIG regionC.npc keys (asset/x/z/rotY/interactM 2.5-4/name/dialog, farmer
  within 25 m of cottage, >= 1.5 m from every props row), footY/heightAt used
  (no literal y), regionC gating + cull in npc.js.
- A2: exactly one new term tryTalkNpc between tryNotch and tryGather; prompt
  else-if branch at the same rank; text from CONFIG; input-suspend pair on
  open/close; touch path untouched.
- A3: dialog DOM via el() copy + inv-panel/inv-title/cook-btns/cook-btn classes,
  inline overlay styles; >= 4 dialog strings in CONFIG; 'active' set exactly
  once; NO 'complete' assignment in npc.js/game.js; state-aware re-talk;
  Esc/death/region-change close; WH_NPC exposes init/update/talkPrompt/
  openDialog/closeDialog.
- A4: wh-quest-line element created in JS, appended to #wh-hud, gated strictly
  on active, text from CONFIG; setGateHint byte-identical.
- A5: S.capture gains data.questState next to data.lairs; S.save gains
  stored.questState in the same try; S.restore hands it back with schema-v1
  fallback to 'available'; CC-C10 comment block; save.js byte-identical; one
  source of truth (questState() reader exists - verify capture/HUD/restore all
  read the same holder).
- A6: sha256 of the door function bodies + CONFIG door blocks == e3444ec
  content (byte-compare the blocks; line shifts allowed, content not).
- A7: exactly one okFarmBarn row, cullM 140, CC-C10 tag; re-run the barn
  distance probe (>= 26 m props/fires, >= 8 m roads, within 60 m cottage);
  re-run scratch/cc-c10/ledger3.py (3 centres PASS, missing empty).
- PRES: untracked set subset (extra scratch files probe_dialog.js + 
  glb_header.py are builder-declared - rule them in or out against the spec's
  measurement-only law and note it); no new GLB files; no tests/; no harness;
  no Astrabot/Meshy artifacts; finish line format exact.
- Known builder deviations to adjudicate (brief/valspec against builder report):
  repeat line also shows when 'complete' (CC-C11 inherits); no collider; extra
  CONFIG keys (footR/bodyHeight/cullM/labelLiftM/labelM/dialog.hint/quest.hudText);
  dialog keys line1/line2/line3. Rule each BLOCKING or NONBLOCKING with reason.

OUTPUT: write io/reports/2026-10-25-cc-c10-farmer-validation.md containing:
per-AC table (PASS/FAIL + evidence lines), deviations adjudication, and the
verdict. Then stdout EXACTLY the finish line:
C10 VALIDATION <PASS|FAIL> ac-passed <n>/7 blocking <count>
List any blocking findings in the report with file:line evidence.