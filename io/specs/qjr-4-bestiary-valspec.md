# QJR-4 Bestiary Journal — Testerbot Validation Spec

Round: QJR-4. Repo worktree: /tmp/wh-worldfeat (branch feat/world-visuals).
IO spec: io/specs/qjr-4-bestiary-spec.md — YOU read it fully before writing
your probes; its sec 3 acceptance criteria A-1..A-12 are the gate. This
valspec defines HOW each acceptance criterion is proven statically. You
write this valspec BEFORE Devbot starts (gate law) and update nothing of
the IO spec.

## Role reminder

You are Testerbot: code QA (not playtest). No harness runs, no headless
browser smoke tests, no git (NO-GIT — never add/commit/push). Your probes
are STATIC analysis of the source tree: node --check, node -e VM loads,
grep/augmented AST reads over the js/config/style files. Where behavior is
dynamic (kill flows), verify the WIRING (calls, guards, site positions),
not live gameplay.

## Pre-flight census (must pass before any V- check)

P-0 `git -C /tmp/wh-worldfeat status --porcelain` — record the dirty set
   BEFORE judging deviations; Devbot may not touch files outside the
   allowlist (below). Any file change outside the allowlist = FAIL.
Allowlist (the ONLY files permissible to change):
  - prototype/js/bestiary.js (NEW)
  - prototype/js/journal.js (tab + DOM)
  - prototype/js/enemy.js (4 guarded one-line hand-offs + 1 comment)
  - prototype/js/game.js (init/update/capture/restore hook lines)
  - prototype/js/CONFIG.js (CONFIG.journal additions only)
  - prototype/index.html (one script tag)
  - prototype/style.css (EOF append: tab + codex rows + accent classes)
  - prototype/builds/v8-playable.html (build artifact)
  - io/specs/qjr-4-bestiary-buildsummary.md (new report)
  - io/reports/2026-11-07-qjr-4-bestiary-validation.md (your own report lane; Devbot may pre-create the stub)

## Validation matrix

V-1 A-1 (unlock): static — bestiary tab hidden until born:
    - journal.js: the tab row hides the BESTIARY tab while
      window.WH_BESTIARY.isBorn() is false (code read: guard present at
      tab render + at update() birth edge re-render).
    - bestiary.js: born flips true ONLY via appendKill/appendSight paths
      (no other setter). init() must NOT set born.
V-2 A-2 (first sight idempotence): static —
    - enemy.js: EXACTLY two guarded `appendSight` sites, both inside the
      idle/aggro canPull transition region of Enemy.prototype.update
      (near the existing `this.setFsm('aggro')` / `this.setFsm('chase')`
      lines ~517/520); each line guarded
      `if (window.WH_BESTIARY)`; no other enemy.js lines changed (diff
      vs HEAD must be those + the kill hand-off + the comment only).
    - bestiary.js: appendSight keeps a per-INSTANCE Set (enemy object
      ref), derives type via enemy.type, ignores unknown types, and
      collapses per-type (row set is typed; a second instance adds
      nothing). A witnessed type still records firstSeen day once.
V-3 A-3 (kill): static —
    - enemy.js: kill hook sits in takeDamage's hp<=0 acknowledgement
      branch, AFTER the `if (Enemy.onKilled) Enemy.onKilled(this);` line,
      guarded `if (window.WH_BESTIARY) window.WH_BESTIARY.appendKill(this);`
      — one site only (grep count 1).
    - bestiary.js appendKill: unknown type = silent return (before any
      born flip); kill of an unseen type sets witnessed AND kills=1 in
      one event (no double toast path).
V-4 A-4 (attribution): static — the wither path (lair withered=true) and
    the restore-from-save path (region-manager restoreLairs ->
    setFsm('dead') on cleared) both bypass takeDamage (proven by
    reading those call sites: they call setFsm directly, never
    takeDamage). Kill hook therefore never fires on them. Note in your
    report the exact line numbers of both bypass paths.
V-5 A-5 (cadence): static — bestiary.js implements: first kill of a type
    toasts; subsequent kills toast only when kills % killToastEvery === 0
    (killToastEvery from CONFIG, default 5). Kill 2..4 of a type must
    NOT toast (math check in the code path). Unseen-first-kill uses the
    killToastTitleUnseen/first-kill string.
V-6 A-6 (save): static —
    - game.js: three wiring sites present and guarded
      (`data.bestiary = window.WH_BESTIARY.capture();` capture,
      `stored.bestiary = ...` explicit write, `restore(data.bestiary)`),
      matching the journal pattern (QJR-1 law) at the matching locations
      (adjacent to the existing journal lines in all three).
    - bestiary.js capture/restore: restore drops malformed rows
      (negative kill counts, non-array witnessed, non-object block),
      missing block = fresh empty, journal block untouched (journal's
      restore still receives its own data.journal key).
    - old-save safe: restore(undefined) leaves journal behavior
      identical (no exceptions; isBorn=false).
V-7 A-7 (unknown/malformed): code-path proof in a node VM: load
    CONFIG.js + bestiary.js (with a stubbed window/document), call
    appendKill({type:'not-a-type'}) -> no throw, born stays false;
    appendKill({type:'bandit'}) -> born true, kills.bandit===1;
    appendKill({type:'bandit'}) again -> 2 and NO toast; restore({born:true,
    witnessed:['wolf'], kills:{wolf:3}, days:{wolf:9}}) then killsOf
    ===3; restore({kills:{wolf:-2}}) -> dropped; restore(null) -> empty.
    (Stub document.createElement etc. as no-op returning fake nodes.)
V-8 A-8 (UI): static —
    - journal.js: tab row grammar = two labels from CONFIG
      (tabJournal/tabBestiary), pointerdown activation with
      preventDefault+stopPropagation, tabIndex -1; search filters BOTH
      tabs (query state shared; bestiary page rebuild filtered on
      title+page+sigil text as spec'd: title+page at minimum);
      nomatch line on each page; Esc + death close unchanged; panel
      width unchanged (320px CSS untouched for .journal-panel).
    - style.css: EOF APPEND ONLY (diff check: no deletion/modification
      of existing lines — git diff must show only '+' lines in
      style.css); classes .bestiary-* and .codex-accent-* defined using
      ONLY existing palette hex tokens (grep each hex in your report and
      verify each appears already in the pre-change style.css — provide
      the token→pre-existing-line proof).
    - locked rows: undiscovered entries render as sigil-only locked rows
      + footer count line ('{n} beasts remain undescribed.') from CFG.
V-9 A-9 (art law): style.css new lines audited hex-by-hex: every hex
    token in the diff is a pre-existing token; per-row ONE accent
    (sigil class only; row text stays ink tokens); page background =
    parchment (#e3dcc4/#d3c8a8 tokens) unchanged; no gradients/glow
    (grep your diff for 'gradient' and 'box-shadow.*glow' — none).
V-10 A-10 (A9 law): grep bestiary.js for player-facing string literals —
    any quoted string NOT present in CONFIG.journal.bestiary (or a
    non-string like CSS class join) = FAIL. CONFIG.journal.text
    (journal's own block) byte-identical to pre-change CONFIG.js (git
    diff on CONFIG.js touches ONLY the bestiary additions inside
    CONFIG.journal; nothing else in CONFIG.js changes).
V-11 A-11 (regression): git diff vs HEAD audit:
    - enemy.js diff = exactly the four guarded lines + comment (verify
      no logic lines moved).
    - journal.js diff = tab row + tab render/rebuild + shared search
      only; the QJR-1/2/3 behaviors (unlock edge, append dedupe, search
      guard in box, tc focus) must survive (code read each).
    - game.js diff = hook lines + capture/restore only; index.html
      diff = one script tag.
    - node --check PASSES on bestiary.js, journal.js, enemy.js, game.js,
      CONFIG.js, save.js, region-manager.js, touch-controls.js.
    - CONFIG.js loads in a node VM (window stub) with zero errors and
      CONFIG.journal.bestiary.entries has ALL TEN keys
      (bandit,ghoul,wolf,coven,zealot,rotmother,rotspawn,scarreader,
      tithecaptain,lastchancel), each with title+sigil+page+accent.
V-12 A-12 (build): python3 tools/build_v8.py runs clean (exit 0); output
    v8-playable.html contains `<script>`-inlined bestiary source (grep
    'WH_BESTIARY' in the build: >= 1 match) + tab stamp
    '(...build MM-DD HH:MMZ <sha>)'. Report sha256 of the built file.
    Build BEFORE claims; no playable claims.
V-13 (probe discipline): probes run from /tmp/wh-worldfeat; results
    PRINTED, each V-id echoed PASS/FAIL. Report-first: write your
    verdict file FIRST (io/reports/2026-11-07-qjr-4-bestiary-validation.md),
    then keep your FINAL CHAT SUMMARY under 60 lines (child-death-by-
    census law).

## Content review (ledger law, doc 51 + 44)

C-1 The 10 page strings + titles: terse hunter field-note voice; NO
    creditor identity, no signatory name, no pact TERMS; 'pact'/'tithe'
   /'Veil' allowed as witnessed facts only. Flag any violation as a
    blocking verdict.
C-2 Sigils: single glyph or ≤3 chars, no images; accents limited to
    amber/crimson/bone/ash.

## Verdict rules

- Each V-n = PASS/FAIL with one-line evidence (file:line or probe
  output). FAIL on any V-1..V-12 = gate FAIL. C- violations = blocking.
- Disclosed minor deviations (e.g., an extra guard line) are allowed but
  must be listed as DEVIATIONS with adjudication (non-blocking with IO
  acceptance).
- Your report file path (valspec copy lives at
  io/reports/2026-11-07-qjr-4-bestiary-validation.md). PASS with 0
  blocking = green light for IO commit.
