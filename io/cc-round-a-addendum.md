ROLE ADDENDUM (read AFTER io/astrabot-brief-ghoul-wire.md):
You are the IMPLEMENTER for this brief (Devbot lane). The brief file is your
complete contract: read it FIRST, follow it exactly, ask nothing.
- Implement the ghoul wiring per its task list. ES5 style only (var/prototype,
  window globals) - match surrounding code.
- Run the validation steps it specifies and save the evidence it names
  (scratch/ghoul-wire-evidence/ JSON + screenshots).
- Commit EARLY and OFTEN with feat: messages (git identity already configured).
- PUSH to origin dev ONLY after syntax checks green + behavioral evidence
  recorded. Verify push with git rev-list origin/dev..dev --count === 0.
- Do NOT touch: bandit wiring, player wiring beyond the smoke test, data.js,
  docs/planning, canonical .rigged.glb bytes, .mixamo.glb bytes.
- NO Mixamo site work. NO Blender work in this round.
- Report back as your FINAL message: changed files + per-file summary, evidence
  JSON path, screenshot paths, assertion results (13 clips / zombie transitions /
  bandit legacy / player chain / console errors), commit SHAs, push confirmation,
  any deviations + why. If a step is impossible in this environment, stop that
  step, mark FAILED with the exact error, and continue the rest - do not
  fabricate results.
Environment facts: no node/npm on this box; JS checks via python3 + playwright
(python -m playwright or the scratch/ driver patterns; chromium binary under
$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome with --no-sandbox;
use headless=new). Blender NOT needed this round.