# Astrabot Mission Brief - sword grip orientation (2026-10-03, round 2)

Nicko change order after playing ed9f0e7 (verbatim): "the sword is at the hand
point, but the hilt of the sword is still at the opposite end, it need to be
rotated 180 degrees it seems. Also, when being held the sword need to be
pointing forward, currently its pointing straight down, at the exact same
angle as the arm. When you grip a sword hilt the sword blade is pointing in
front of you."

Baseline: feat/world-visuals @ ed9f0e7 in worktree /tmp/wh-worldfeat. All
previous work confirmed working (models/anims, retry, loading screen, spawn
facing, weapon scale at the hand point). NO harness runs - his playtest is
the bar. esprima syntax checks only. ONE commit to feat/world-visuals IN THE
WORKTREE, then append "## Astrabot findings" and amend (message starts
"fix: sword grip"). NO pushes. No touching: /workspace/witch-hunter, servers,
io/specs, docs/planning, art GLB binaries.

## IO read of the situation (verify against code, then act)
- The mount at prototype/js/player.js setWeapon() (~128-155) is the dev
  whanim3 port: it computes a mount quaternion from the REST hand basis
  (hand.updateWorldMatrix at rest pose) mapping GLB blade axis (0,-1,0) to
  restTip.negate() + cant(0.12,0,0.12).
- Nicko's in-game result: blade points STRAIGHT DOWN parallel to the forearm,
  hilt at the wrong end. Two compounding suspects:
  (1) the dev whanim3 measurement was taken against DEV's animated attack1
      hand basis - but here it is applied at REST basis, so the baked
      orientation reads differently in feat (forked anim runtime differs);
  (2) tip negate logic may be fighting the actual rest bone axes of the feat
      re-rigged export.
- Do NOT hand-tune magic numbers and hope. Do this instead, in order:
  A) OFFLINE RIG MEASUREMENT: write a throwaway python script (scratch/, not
     committed) that parses the glTF JSON chunk of
     art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.glb
     (python struct/gzip - the JSON chunk is plain) and dumps the R_Hand bone
     node's rest T/R/S and its node hierarchy (which node is R_Forearm /
     R_UpperArm, their axes). Compute the hand's local coordinate basis.
     From THAT, derive which local axis is "grip forward" (blade should point
     along fingers-forward direction, NOT along the forearm Y).
  B) Implement the mount from measurement: blade (GLB -Y) mapped to the
     measured grip-forward axis (+ a small measured cant so the edge aligns
     properly), pommel below the fist. If the rig data shows the hand bone's
     rest basis in this export, use it directly - do not guess.
  C) Put the final orientation into CONFIG (e.g. CONFIG.assets.weaponMount =
     { axis: 'x'|'y'|'z', sign: 1|-1, cant: [0.12,0,0.12] }) so the next
     change order is a data edit, not a code dive. Default on, keep kill
     switch semantics consistent with weaponScaleEnabled.
  D) Apply the SAME mount to the bandit handAxe (enemy.js) - it shares the
     mount quaternion.
- Acceptance (Nicko plays): blade points forward on grip (in front of the
  player), hilt/pommel at the fist end (grip in hand), sword NOT parallel to
  the forearm, survives idle/walk/3-swing stages without re-entering the arm.

## Guardrails
- player.js setWeapon + CONFIG.js only (+ enemy.js axe mount). Leave scale
  logic from ed9f0e7 untouched.
- If measurement is ambiguous, pick the most defensible reading and state
  exactly what you assumed in findings so Nicko's next order targets it.
- Keep diff tight (~100 lines). Player copy law: never "free"; no agent names.