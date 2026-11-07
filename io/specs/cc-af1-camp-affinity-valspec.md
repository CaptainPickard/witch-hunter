# CC-AF1 VALIDATION SPEC (Testerbot) — written BEFORE Devbot starts

Target: /tmp/wh-worldfeat worktree (feat/world-visuals), source round per
io/specs/cc-af1-camp-affinity-spec.md. Testerbot validates CODE ONLY (probes,
static checks, run-in-node or jsdom where feasible — NO headless browser smoke
tests, no harness). Verdict = PASS/FAIL with evidence lines; write the report to
io/reports/2026-11-07-cc-af1-camp-affinity-validation.md and DO NOT message Nicko.

## V-0 preflight (sha coherence)
- git -C /tmp/wh-worldfeat status --porcelain shows only expected round files;
  record HEAD sha before Devbot's work starts (expected = 3498ede on
  feat/world-visuals + this valspec file).

## V-1 static census
- js/affinity.js exists; IIFE; exposes window.WH_AFF with the exact API names:
  score, tier, tierFire, deed, crossed, capture, restore, onChange.
- CONFIG.affinity ladder ids EXACT: sworn-dark, feared, neutral, honored,
  sworn-light; deeds keys EXACT: rescue_findDaughter(25), warEffortFill(10),
  kill_ghoul(4), kill_rotmother(4), kill_rotspawn(2), kill_wolf(0),
  kill_bandit(-4), kill_coven(8); clamp 100.
- journal topics ids 'camp-affinity-good' / 'camp-affinity-dark' present with
  camp-folk source rows.

## V-2 behavior probes (mock WH_JOURNAL as an append-collector; fresh state per case)
- P1 deed math: rescue +25; three fills +30 each side; kill_ghoul loop to clamp;
  kill_bandit loop to -100; assert every intermediate; unknown deed id returns
  false and changes nothing; deed('kill_wolf', 5) changes nothing (delta 0).
- P2 tier table EXACT per spec A3 (49/50/80/-49/-50/-80/0 probe rows; fire hexes:
  honored 0xffdf8a, sworn-light 0xfff2c8, feared 0xff5a3c, sworn-dark 0xff2a2a,
  neutral fire null).
- P3 restore semantics: restore(undefined) -> score 0 crossed {}; restore(garbage)
  does not throw; restore({score:'x', crossed:7}) -> safe fresh (numbers coerced
  or rejected cleanly, module must not be left in an inconsistent tier).
- P4 crossing fires exactly once: honored up -> good topic collected once; drop
  back under 50 and cross again in the SAME session -> no second append; same
  for feared/dark; then restore({score:0, crossed:{}}) -> crossing can refire
  (a restored fresh map is the only refire path — the save's map governs).
- P5 onChange fires exactly once per deed() call that changes the score, zero on
  no-ops.

## V-3 integration guards
- G1: game.js storeCorpseLoot carries the guarded WH_AFF deed line AFTER the
  awardXP/discover pair.
- G2: wareffort.js fill site carries it after the JT.firstFill append site.
- G3: npc.js tryRescue carries it after the JT.rescue append.
- G4: game.js computeFireSockets forwards p.color into the socket when present
  (and nothing else changed in that function).
- G5: camp.js fireProps rows get color ONLY when WH_AFF live and tierFire() != null;
  static check: the banditCampfire CONFIG rows (21 in region props; census via
  grep "asset: 'banditCampfire'") are UNCHANGED in count.
- G6: setupSaveHooks: capture aff block + restore guarded call.
- G7: inventory.js: STANDING section guarded on WH_AFF; bar class switches with
  tier; onChange wired in game.js guarded.
- G8: index.html: exactly one added script line, position after leveling.js; no
  other index.html change.

## V-4 build + diff law
- Devbot has ALREADY run python3 tools/build_v8.py from the worktree root (exit 0).
- Testerbot re-runs it: exit 0 again and the file is byte-stable (deterministic
  stamp law — sha256 equal across the two runs).
- Marker greps on prototype/builds/v8-playable.html: WH_CONFIG.affinity, WH_AFF,
  'camp-affinity-good', 'Sworn of the Dawn' all present.
- git diff HEAD --stat: expected files ONLY (CONFIG.js, affinity.js, index.html,
  game.js, wareffort.js, npc.js, camp.js, inventory.js, style.css, spec/valspec/
  reports, this round's journal-side files are NOT in the worktree diff).
- ZERO deletions: git diff HEAD -U0 | grep -c '^-' minus header lines == 0
  (verify programmatically and PRINT THE COUNT).

## V-5 NO-GIT clause
- Children made no commit and no push: git log -1 stays at the pre-round sha for
  the child work; the ONLY commit (if IO already landed by validation time) must
  carry the CaptainPickard identity — check `git log -1 --format='%an %ae'`.

Report: header (sha, branch), per-V results with PASS/FAIL lines, deviations
found (each with severity + whether spec-deviation or bug), final verdict line:
"VERDICT: PASS" or "VERDICT: FAIL (reason(s))". Keep the report under ~150 lines.
