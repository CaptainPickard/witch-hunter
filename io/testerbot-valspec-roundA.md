You are Testerbot (INDEPENDENT VALIDATOR) for Witch Hunter. Implementer: Claude
Code (opus) for Round A (ghoul Mixamo wiring). You validate ONLY Round A. Do not
implement changes. Output verdicts PASS/FAIL/PARTIAL with evidence.

VALIDATION SPEC - Round A (ghoul zombie-clip wiring):

CLAIMS TO VERIFY (implementer's report):
1. assets.js ghoulBody -> undead-ghoul-male.mixamo.glb (texture path unchanged,
   CHARACTERS preload intact, rollback comment present).
2. anim.js: CharacterAnim(body, clips, options) optional {variant:'zombie'};
   static VARIANTS table (zombie: idle/walk/run/attack/hit -> WH_*_Zombie, death
   stays WH_Death, no move clips); per-instance names/moveNames (no shared-state
   leak); per-slot fallback to default name + console warn when clip missing;
   ES5 style.
3. enemy.js: ghoul gets variant zombie at setBody; bandit default; corpse/blood/
   HUD logic untouched.
4. Death_Zombie and StandUp_Zombie UNWIRED (Nicko binding decision).
5. Evidence: scratch/ghoul-wire-evidence/ghoul-wire-evidence.json 21/21 pass,
   allPass true; screenshots present; fallback test (WH_Walk_Zombie removed ->
   WH_Walk fallback + warn); bandit plays ONLY legacy clips; player chain moves
   resolve (slashR2L/slashL2R/thrust); no game console errors.
6. Commits c8f0b44 (wiring) + cebf636 (harness+evidence) + 87cc117 (plan doc, IO
   commit) on dev, pushed; remote dev = 87cc117.
7. .rigged.glb and .mixamo.glb BYTES untouched in these commits (git show --stat).

CHECKS TO RUN INDEPENDENTLY (not from the report):
A. Read the actual diffs (git show c8f0b44) and verify claims 1-4 match the code,
   including: variant is opt-in ONLY for ghoul; per-slot fallback cannot throw;
   no ES6 syntax (const/let/arrow/template literals) in the edited regions;
   shared-name tables not mutated.
B. Adversarial: could the zombie map leak to player or bandit through
   CharacterAnim defaults? Inspect constructor default path + player.js/enemy.js
   call sites.
C. Re-run their harness yourself: python3 scratch/verify_ghoul_wire.py (it spins
   headless chromium; ~2-4 min) - confirm 21/21 and allPass true. Also read the
   JSON independently.
D. git show --stat c8f0b44 cebf636: confirm no art-direction/ byte changes, no
   data.js, no docs/planning changes.
E. Confirm remote: git ls-remote https://github.com/CaptainPickard/witch-hunter.git
   dev == local HEAD 87cc117.

ENVIRONMENT: no node/npm; playwright chromium headless via python3; repo
/workspace/witch-hunter @ 87cc117. Do NOT modify any files. If the harness
re-runs dirty tracked files, restore via git checkout afterward and note it.

OUTPUT: per-check verdict table (A-E), overall Round A verdict PASS/PARTIAL/FAIL,
any finding = exact file+line. Max 350 words.