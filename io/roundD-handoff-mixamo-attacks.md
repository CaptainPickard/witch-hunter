# ROUND D HANDOFF: Mixamo attack clips for the longsword chain combo
Written by IO 2026-10-05 for a fresh session. Read this + load the two skills
listed below before acting.

## Skills to load first (they encode the standing laws)
1. skill_view(name='witch-hunter-playtest-serving') - repo/serve topology,
   serve law, playtest-era laws, CSP gotcha.
2. skill_view(name='no-harness-playtest-gate') - automated harness runs BANNED;
   Nicko playtests; syntax checks + still renders only.

## Verified repo state (2026-10-05 end of Round C)
- Repo /workspace/witch-hunter (host sees /root/projects/witch-hunter, same
  bind, ONE .git). Branches:
  - dev @ a402374 (main checkout) - Mixamo rounds A/B/C + plan doc landed.
  - feat/world-visuals @ 81803f7 (git worktree at /tmp/wh-worldfeat) - same
    rounds + Order D shield clips; served build @ 81803f7.
- Served surface: HOST container wh-playtest-8793 (python:3-alpine, --network
  host, binds HOST /tmp/wh-worldfeat-clean:/srv RO) serves
  /prototype/builds/v7-playable.html. Refresh law: git -C /tmp/wh-worldfeat-clean
  reset --hard <feat-sha> (HOST-side; host /tmp != container /tmp).
  Host-verify via python3 /tmp/dhost.py "<host cmd>".
- Player build state on feat: playerBody = human-hunter-male.combat-sword.glb
  (25 clips: 13 Order-D chain/shield clips + 12 Round-C Mixamo clips: WH_SwordIdle,
  WH_SwordWalk, WH_SwordRun, WH_SwordWalkBack, WH_SwordIdleAlt, WH_ShieldBlockIdle,
  WH_ShieldCrouchIdle, WH_SwordStrafeL/R, WH_SwordTurnL/R, WH_SwordCrouchIdle).
  assets.js feat clip-count check = 25. dev has 21-clip variant (9 chain + 12).
- Ghouls = zombie variant, bandits = bandit variant (both passing, TESTERBOT
  PASS 10-05). Do not touch ghoul/bandit paths in Round D.

## What Round D is (Nicko order 2026-10-05)
Replace the SELF-AUTHORED Blender chain-combo attack clips with Mixamo sword
pack attack animations:
- Chain slots today (anim.js MOVE_NAMES): slashR2L -> 'WH_SlashR2L',
  slashL2R -> 'WH_SlashL2R', thrust -> 'WH_Thrust'. These were authored in
  headless Blender (commits 1632097..a890f41) and are synced to the combat FSM
  via playerAttack(stage=windup/active/recover, t, durations) -> seekAttack
  which seeks stage time offsets [durations.windup, active, recover].
- ADJUDICATE FIRST (blocking): where do phase durations come from for
  getAttackPhase (player.js)? If clip-duration-derived, Mixamo replacement
  timing works automatically. If CONFIG-fixed, update CONFIG.attackPhase
  durations to match the chosen Mixamo clips' natural strike timing
  (windup = moment before impact frame, active = strike follow-through,
  recover = rest). Testerbot must audit this mapping explicitly.
- Candidate attack clips in scratch/mixamo-fbx/swordpack/ (51 files, GENERIC
  names like "idle (2)" / "turn"): identify by name+motion with
  scratch/swordpack_probe.py (exists, measures travel/turn/hips motion).
  Strong candidates: sword and shield slash (power/downward/cross/combo),
  stable sword outward slash, stable sword inward slash, one hand sword combo,
  two hand sword combo, sword and shield attack high/low. PICK EXACTLY 3 for
  the combo (right-to-left slash, left-to-right slash, thrust-equivalent or
  a stab/overhead; keep the game's R2L -> L2R -> thrust RHYTHM - if the pack
  has no true thrust, an overhead/downward slash may sub in IF it reads as a
  third distinct move; document the substitution for Nicko).
- New WH names (no collisions): WH_SS_SlashR2L, WH_SS_SlashL2R, WH_SS_Overhead
  ( naming YOURS; must stay in WH_ namespace and not collide with any existing
  player clip name).
- KEEP the authored WH_SlashR2L/WH_SlashL2R/WH_Thrust CLIPS in the GLB (never
  delete). Rollback = flip MOVE_NAMES back (one-line revert).

## Pipeline rules (proven, reuse - do not reinvent)
- Bake: scratch/mixamo_retarget.py (constraint+bake route; per-clip RT_ NLA
  tracks; action_slot assignment needed or the 4.5 exporter throws with
  target_id_type None; bone_heuristic='BLENDER'; exporter flags in
  scratch/mixamo-retarget-report.md). Output per branch:
  human-hunter-male.combat-sword.glb built FROM THAT BRANCH's combat-chain.glb
  (dev 9-base -> 24 clips expected; feat 13-base -> 28 expected). Update the
  assets.js clip-count checks accordingly.
- Verify: scratch/verify_retarget.py (BIN-chunk prefix byte-identical +
  append-only JSON invariant for ALL originals; new clips 60ch/20node/30fps;
  quat norms 1.0; --held-pose exists for genuinely static clips - the three
  attack clips are NOT held poses, keep the frozen-threshold check active for
  them). Regression: scratch/test_mixamo_retarget.py (11/11 - add a round D
  pair test cheaply if supported).
- Wire: extend anim.js VARIANTS.sword? NO - the sword variant exists and its
  moves is the SHARED MOVE_NAMES object BY IDENTITY (feat's Order D code checks
  anim.js:340 identity). SAFEST ROUTE: rewire MOVE_NAMES itself to the new
  clip names (slashR2L -> 'WH_SS_SlashR2L', etc.) with a per-slot fallback to
  the authored names if a Mixamo clip is missing (same pattern as names
  fallback; console.warn on fallback). This keeps the identity check intact
  and the change minimal. player.js needs NO change.
- Serve: commits on BOTH branches (same messages), build_v7.py IN
  /tmp/wh-worldfeat, build commit, push dev:dev +
  feat/world-visuals:feat/world-visuals, HOST refresh reset --hard, host curl
  verify (200 + grep -c WH_SS_SlashR2L >= 1) before telling Nicko to play.

## Hard laws ( violations = blocked rounds)
- ZERO Mixamo-site work (account is bot-gated; all assets on disk already).
- NO automated game/harness/browser-loop runs (Nicko is the tester; 10-04 law).
- Canonical .rigged.glb bytes never change. Authored chain clips never deleted.
- Still renders for Nicko: max 3 stills (rest, slashR2L mid-strike, thrust/
  overhead mid-strike), full size, into scratch/roundD-proof/. Vision-analyze
  each once. No contact sheets, no QA mills.
- Dispatch Claude Code for ALL token-heavy work (Nicko 10-05 routing).
- If a step fails twice on real errors: mark FAILED with exact error, continue
  the rest, never fabricate.

## Claude Code dispatch command (verbatim template)
cd /workspace/witch-hunter && export PATH=$HOME/.local/bin:$PATH && \
claude -p "$(cat <contract-file>)" --model opus \
--allowedTools "Read,Write,Edit,Bash,Glob,Grep" --max-turns 80 \
--output-format json > /tmp/cc_roundD.json 2>/tmp/cc_roundD.err;
echo "EXIT=$?" >> /tmp/cc_roundD.err
(run backgrounded; IO reads /tmp/cc_roundD.json when EXIT lands)

## Testerbot audit (after Claude Code lands, BEFORE Nicko playtest)
Write a valspec (pattern: io/testerbot-valspec-bc.md) and dispatch:
claude -p "$(cat <valspec>)" --model opus --allowedTools "Read,Bash"
--disallowedTools "Edit,Write,NotebookEdit" --max-turns 60 --output-format json
MUST cover: commit scope audit (git show --stat every SHA), phase-durations
adjudication review, invariant re-run (both branches), identity check intact,
serving verification (8793 200 + marker), disclosed watch-items documented.

## Close-out checklist
[ ] 3 Mixamo attack clips baked + invariants green (both branches)
[ ] MOVE_NAMES rewired with fallbacks; identity check intact
[ ] Phase durations adjudicated + documented (clip-derived or CONFIG-updated)
[ ] Testerbot opus audit = PASS
[ ] Both branches committed + pushed; build committed; HOST refreshed; curl verified
[ ] plan doc Round D section committed (dev)
[ ] Rollback documented (MOVE_NAMES one-line revert)
[ ] Nicko playtest verdict posted in chat = the real acceptance bar
[ ] Parked items stay parked: 9 unhooked baked clips, bandit cape panel, ~55deg
    idle stance, kick/cast/draw/sheath hooks - note them in the plan doc, do not
    do them unbidden.