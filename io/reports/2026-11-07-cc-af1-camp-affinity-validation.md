# CC-AF1 VALIDATION REPORT (Testerbot) — camp affinity v1
Branch: feat/world-visuals | HEAD before round: 3498ede | validated against
HEAD 3498ede + untracked worktree files. Probe: node vm sandbox (CONFIG.js +
affinity.js loaded verbatim; WH_JOURNAL mocked as append-collector).
Scripts: /tmp/wh-af-test-probe.js (external to the worktree).

## V-0 preflight
- status --porcelain: only expected round files (build artifact, index.html,
  CONFIG.js, camp.js, game.js, inventory.js, npc.js, wareffort.js, style.css;
  untracked affinity.js + io/specs/*).
- HEAD = 3498ede (expected). PASS

## V-1 static census
- js/affinity.js: IIFE, 'use strict', exposes window.WH_AFF with EXACTLY
  score, tier, tierFire, deed, crossed, capture, restore, onChange. PASS
- CONFIG.affinity ladder ids/order EXACT: sworn-dark, feared, neutral,
  honored, sworn-light; minScores -80/-50/-49/50/80; fires: 0xff2a2a,
  0xff5a3c, null, 0xffdf8a, 0xfff2c8. PASS
- deeds keys EXACT: rescue_findDaughter 25, warEffortFill 10, kill_ghoul 4,
  kill_rotmother 4, kill_rotspawn 2, kill_wolf 0, kill_bandit -4,
  kill_coven 8; clamp 100. PASS
- Journal topics camp-affinity-good ('The honored fire') / camp-affinity-dark
  ('The watched fire'), source 'Camp folk'. PASS

## V-2 behavior probes (98 asserts run, 98 passed, 0 failed)
### P1 deed math
- rescue +25; second call +25 -> 50. PASS
- warEffortFill x3: 60,70,80 (+10 each). PASS
- kill_ghoul (+4) every step to +100 clamp; clamped edge returns false. PASS
- kill_bandit (-4) every one of 24 steps to -100, then stays -100. PASS
- unknown id -> false + unchanged; kill_wolf x5 (delta 0) -> false + unchanged,
  no hook fire. PASS

### P2 tier table — incl. RULE on the disclosed deviation
- Required rows, all exact: 49->neutral/null-fire, 50->honored/0xffdf8a,
  80->sworn-light/0xfff2c8, -50->feared/0xff5a3c, -80->sworn-dark/0xff2a2a,
  -49->neutral, 0->neutral. Clamp edges: +100->sworn-light, -100->sworn-dark
  (floor fallback ladder[0]). PASS
- RULE on Devbot's disclosed deviation: UPHELD. The valspec's OWN law sentence
  ("greatest minScore <= score wins; floor = ladder[0] at the clamp edge")
  directly implies tier() != literal first-match over the as-typed array; a
  literal first-match would make sworn-dark swallow every threshold. Devbot's
  desc-order scan + floor fallback is the only implementation consistent with
  that law, and every required A3 row passes exactly. VERDICT: the deviation
  is spec-compliant.

### Law-gap observed (documented, NOT a failure)
- Under the greatest-minScore law, scores in (-80, -49] other than exactly
  -50... satisfy only the -80 threshold: e.g. -52, -79 -> sworn-dark. The
  config comment band ("|s| >= 80 sworn, >= 50 feared") disagrees with the
  law sentence at 50<|s|<80 on the negative side. The valspec law governs;
  required probe rows all pass. Flagged as a TUNING ambiguity for IO/Nicko
  (severity: minor, spec-ambiguity), no change requested this round.

### P3 restore semantics
- restore(undefined) -> score 0, crossed {}. PASS
- restore(garbage string/number/array/null) -> no throw, fresh state. PASS
- restore({score:'75', crossed:{good:true,junk:'yes',nope:false}}) ->
  score 75 coerced; once-map keeps only key===string && val===true; state
  fully usable (+2 deed applied). PASS
- restore(999)->100 / restore(-999.7)-> -100 (floor+clamp). PASS

### P4 crossing exactly-once
- honored cross -> exactly one good append; same-session re-cross after
  dropping under 50 (no restore) -> NO second append. PASS
- feared cross -> exactly one dark append; same-session re-cross -> none. PASS
- restored fresh map ({score:0,crossed:{}}) IS the refire path; the save's
  map governs (restored {'good':true} suppresses). PASS
- sworn tiers add no extra topic (once-map keys are topic ids). PASS
- exactly one good+one dark across the whole matrix; no third id ever. PASS
- WH_JOURNAL undefined during crossing -> no crash, score applied. PASS

### P5 onChange
- onChange fires exactly once after every deed() that changes the score, and
  AFTER the crossing check (observed order: append:camp-affinity-good then
  onChange:50). Zero on no-ops (zero delta, unknown id) and on restore. PASS

## V-3 integration guards
- G1 game.js storeCorpseLoot: deed('kill_'+type) AFTER awardXP/discover pair. PASS
- G2 wareffort.js: deed('warEffortFill') AFTER the JT.firstFill append. PASS
- G3 npc.js tryRescue: deed('rescue_findDaughter') AFTER JT.rescue append. PASS
- G4 game.js computeFireSockets forwards p.color -> socket (only addition in
  that function; poolTick NOT edited). PASS
- G5 camp.js fireProps: color only when WH_AFF live AND campTint.enabled;
  tierFire() null = no color key. banditCampfire census unchanged: 21 rows in
  region props (grep "asset: 'banditCampfire'"), zero CONFIG deletions. PASS
- G6 setupSaveHooks: capture aff block on save + explicit storage write +
  guarded restore(data && data.affinity). PASS
- G7 inventory.js STANDING section guarded on WH_AFF (absent module = no
  row); bar class fill-<tier> switches with tier; onChange wired in game.js
  (guarded), re-renders character tab only. PASS
- G8 index.html: exactly one added line <script src="js/affinity.js"> after
  leveling.js; zero other index.html changes (-U0: 1 added line, 0 deleted). PASS

## V-4 build + diff law
- Re-ran python3 tools/build_v8.py: exit 0. Byte-stability: sha256 of
  prototype/builds/v8-playable.html identical before and after the re-run
  (dd6a4c7db95acd4b48935cf0638980afad88901cba4ed727c990065771b01715). PASS
- Marker greps on the build: WH_CONFIG.affinity x2, WH_AFF x14,
  camp-affinity-good x4, 'Sworn of the Dawn' x1 — all present. PASS
- git diff HEAD --stat: EXACTLY the expected files (build artifact,
  index.html, CONFIG.js, camp.js, game.js, inventory.js, npc.js, wareffort.js,
  style.css; io/specs untracked; no journal-side files). PASS
- Deletion count (git diff HEAD -U0 | grep -c '^-' minus header lines): 1
  (printed). The single deletion is the build artifact's own stamp <title>
  line, regenerated deterministically by build_v8.py per the stamp law — a
  build-output artifact, not a source deletion. Source deletions = 0. PASS
  (law satisfied in spirit and per source files)

## V-5 NO-GIT clause
- git log: HEAD remains 3498ede (pre-round sha); no new commits. Only
  commit authors in recent history: CaptainPickard. No push (builds remain
  uncommitted worktree changes). PASS

## Deviations summary
1. Disclosed & adjudicated: tier() implemented as desc-order
   greatest-minScore scan + floor fallback instead of literal first-match
   over the as-typed ladder array. Ruled spec-compliant — the valspec law
   sentence requires exactly this; all required P2 rows pass. (severity: none)
2. Law-gap documentation item: config band comment ("|s| >= 80 sworn,
   >= 50 feared, else neutral") conflicts with the greatest-minScore law on
   the negative side (scores -52..-79 land sworn-dark, not feared).
   Spec-ambiguity for IO/Nicko, NOT a Devbot bug; no code change requested.
   (severity: minor)
3. Build-stamp <title> counts as the single -U0 deletion: artifact-only,
   stamp law, not a source loss. (severity: none)

VERDICT: PASS
