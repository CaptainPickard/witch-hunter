# QJR-4 Bestiary Journal — Testerbot Validation Report

- Round: QJR-4 · Worktree: /tmp/wh-worldfeat · Branch: feat/world-visuals (code judged UNCOMMITTED in the working tree; HEAD = e1d66d6)
- Validator: independent Testerbot gate (re-ran all probes itself; Devbot summary not trusted).
- Date: 2026-11-07 · Method: static QA + node -e / vm.runInThisContext VM probes only. NO-GIT (no add/commit/push), no harness, no headless browser.
- Build artifact: prototype/builds/v8-playable.html — sha256 `3fd0c5c3c583e89884f9f261735bcc9752ef74c8b48a43b2c7c5a3b8858b2279`; title stamp `build 11-07 19:09Z e1d66d6`; grep WH_BESTIARY in build = 20.

## P-0 Pre-flight census — PASS

```
M prototype/builds/v8-playable.html      M prototype/js/CONFIG.js
M prototype/index.html                   M prototype/js/enemy.js
M prototype/js/game.js                   M prototype/js/journal.js
M prototype/style.css
?? io/reports/qjr4_a9_probe.py  ?? io/reports/qjr4_config_verify.py
?? io/reports/qjr4_devbot_probe.py  ?? io/specs/qjr-4-bestiary-buildsummary.md
?? prototype/js/bestiary.js
```
- Every M file is on the valspec allowlist; `?? prototype/js/bestiary.js` is the new module; `?? io/specs/qjr-4-bestiary-buildsummary.md` is the permitted Devbot report lane. `?? io/reports/*.py` ×3 are Devbot probe leftovers — flagged (see Deviations D-4); they are report-lane files, not code.
- Stat: CONFIG.js +54, enemy.js +6/-0, game.js +9/-0, journal.js +133/-16(+117 net by insertion), index.html +2/-0, style.css +50/-0, build +537/-0. Zero deletions in style.css; enemy.js strictly additive.

## Verdict matrix (VERDICT: PASS — 13/13 V + C-1/C-2, zero blocking findings)

| V | Verdict | One-line evidence |
|---|---------|-------------------|
| V-1 | PASS | VM probe: born=false after init()+update() alone; born flips true only via appendSight (wolf) / appendKill (ghoul); bestiary.js:190-193 init holds game ref only; no other born setter (grep: lines 76, 99, 185 only) |
| V-2 | PASS | enemy.js:518 & :522 guarded `window.WH_BESTIARY.appendSight(this)` immediately after setFsm('aggro')/('chase') inside the canPull transition block; enemy.js diff = +6/-0 exactly those two lines + kill hand-off + 2-line comment; grep appendSight count = 2; probe: same ref 3× → witnessed=['wolf'] no dup; 2nd instance → still ['wolf'] (per-TYPE); days {wolf:3} once; unknown types ignored |
| V-3 | PASS | Kill hook enemy.js:978 sits in takeDamage's hp≤0 branch directly AFTER `if (Enemy.onKilled) Enemy.onKilled(this);` (:976); one site only (grep count 1); probe: appendKill({type:'not-a-type'}) → silent, born stays false PRE-flip (V-3's core edge) |
| V-4 | PASS | Liar-protect bypass verified: lair wither path enemy.js:1314-1322 (dieOnMasterDeath: hp=0 + setFsm('dead'), never takeDamage); restored-corpse path enemy.js:1281-1285 + region-manager.js:1932-1939 (restoreLairs: hp=0 + setFsm('dead'), never takeDamage); takeDamage's `if (this.fsm === 'dead') return false;` (:957) doubly denies both |
| V-5 | PASS | bestiary.js:100-107 cadence: `n===1` → first-kill string; `n % every === 0` (every = CFG killToastEvery, default 5 guard :101) → kill 2-4 silent by pure math; VM probe cadence run: kills 1-5 → toasts = [first-kill ghoul], then [.. + slain x5] — exactly 2, no duplicate |
| V-6 | PASS | game.js:2692 data.bestiary capture / :2713 stored.bestiary explicit write / :2731 restore(data && data.bestiary) — all three adjacent to corresponding journal lines; probe: restore(undefined)=fresh empty; malformed rows dropped; journal restore path :2729 receives data.journal independently |
| V-7 | PASS | VM probe (vm.runInThisContext): unknown → no throw + born false; bandit kill1 → born true, kills 1; kill2, kill3 → tally 2,3 + no second toast; restore wolf {3, day 9} → 3; restore {wolf:-2} → 0, born false, no toast; restore(null) → empty, born false; +7 extra malformed shapes all exact |
| V-8 | PASS | journal.js:213-228 two-tab build (tabJournal/tabBestiary from CONFIG), pointerdown+preventDefault+stopPropagation+tabIndex -1 (:226-260); shared query filter feeds both pages (:303 search input → renderCurrentPage; bestiary.js renderPage hay = title+page+sigil :241); nomatch line each page (:89 journal, :257 bestiary); Esc handler :339 + death closePanel :203 unchanged; `.journal-panel` width untouched (style.css:1601) |
| V-9 | PASS | style.css diff EOF +50/-0 (zero deletions, no gradient/glow declarations; the sole "gradient" match is the comment "no gradients"); all 11 hex tokens pre-exist in HEAD grep counts: 4a4034=10, 6a6350=12, 14110e=14, 3d382e=8, d8d2c0=16, 2a231b=10, 5a5344=13, b7ac8f=1, c9a94a=6, b0472f=1, 7a7160=2; parchment tokens #e3dcc4 ×8 / #d3c8a8 ×2 pre-exist; one accent class per row sigil only (rowFor :209) |
| V-10 | PASS | bestiary.js player-facing literals: 15 quoted strings — 'use strict', 1 CSS class join (bestiary-row-locked), 4 class names (bestiary-footer / journal-nomatch / bestiary-row / bestiary-row-page), ' - ' & 1 space joins → ALL CSS/structural, all referenced at .bestiary-* definitions in the appends style.css; zero content literals (titles/pages/sigils/toasts all via CFG = CONFIG.journal.bestiary); CONFIG.journal.text byte-identical (CONFIG.js diff = exactly +54 bestiary-block lines between :4899 and :4954) |
| V-11 | PASS | node --check on 8 files OK (bestiary, journal, enemy, game, CONFIG, save, region-manager, touch-controls); diffs match: enemy.js +6/-0 (2 sight :518/:522, kill :978, 3-line comment :1749-1751); game.js +9/-0 (5 hooks :2646/:2692/:2713/:2731/:3272 + 3 comments); CONFIG.js +54 EOF-pure (byte-identical :1-4899) with 10 entry keys each title+sigil+page+accent; index.html:72-74 one new src + 1 comment line; QJR-1/2/3 behaviors intact (quest unlock edge, append dedupe, QJR-2 tc focus, search guard in box) |
| V-12 | PASS | Rebuild self-run: exit 0, byte-identical (3fd0c5c3…2279 both sides pre/post rebuild) — clean, artifact fresh; grep WH_BESTIARY ≥1 = 20; stamp `build 11-07 19:09Z e1d66d6` = deterministic HEAD-commit-time + short sha (tools/build_v8.py:32-46); the `19:09:31+00:00` git log shows exactly the HEAD commit time |
| V-13 | PASS | All probes self-run from /tmp/wh-worldfeat via node -e / vm.runInThisContext (no harness, no headless browser); each V-id echo PASS in this report; report-first (this file written before delegation result & chat summary; chat summary kept <60 lines) |

## Content review (Ledger law)

- **C-1: PASS — the ten CONFIG.js page strings (:4933-4952) contain NO creditor identity, NO signatory name, NO pact terms.** All pact/tithe/Veil mentions are witnessed-fact only, with no terms or creditor named:
  - bandit: "takes it in tithes **I have seen collected** at crossroads" — witnessed fact; no creditor.
  - zealot: "**Whatever pact** it keeps, it keeps it out loud and alone" — explicitly refuses to know terms.
  - tithecaptain: "watched its carts take grain and iron… receipts no one can read. **I have never seen it pay.**" — observation only; zero terms.
  - lastchancel: "At its threshold **I have heard the tithes being counted.**" — witnessed; the hunter **has not yet stepped inside** (terms withheld).
  - coven: "the Veil storms I watched as a boy" — witnessed natural event.
  - zealot title "Veil-Touched" — state as seen from outside.
  - Also non-violating: no creditor or signatory name anywhere; no numerals (no amounts); no agreement language; no contract vocabulary beyond the four permitted witnessed-fact forms.
- **C-2: PASS — sigils: ten single glyphs (all ≤3 chars, no images), accents limited to amber/crimson/bone/ash.** Grep accents: bone×1(bandit), ash×2(ghoul, rotspawn), amber×1(wolf), crimson×6(coven, zealot, rotmother, scarreader, tithecaptain, lastchancel) — exactly ten, exactly the four permitted accent tokens; glyph audit (each 1 codepoint, no images): bandit '†', ghoul '☠', wolf '❂', coven '✶', zealot '☀', rotmother '✿', rotspawn '✿', scarreader '〰', tithecaptain '⚖', lastchancel '♆'. All are single-glyph, ≤3 chars, no images. (Devbot noted the rotmother/rotspawn shared '✿' as a deliberate visual-family pairing; the valspec's C-2 has no uniqueness bar, only the glyph-size/accent-color limits, so this is within spec.)

## Deviations (four Devbot items — adjudication)

1. **open/closeForTest/setOpen/renderPage extra API on bestiary module** — ACCEPTED, non-blocking. Bestiary.js:275-277: setOpen (one boolean swap, :198), closeForTest (wraps it), renderPage (journal.js:67-73 consumes exactly this shape). Zero behavior change (no born-flip, no toast, no DOM side effects beyond the page render journal already owns). These are the exact journal-owned DOM-contract hooks the build needs to keep journal.js owning the panel; they are additive and self-describing. Keep.
2. **Suppressed codex hint on journal page** — ACCEPTED, non-blocking. journal.js:318-321: a `bestiary-hint` div is appended ONLY when BC.text.hint is truthy, and CONFIG's journal.page text 'Escape to close' is byte-identical to HEAD; the codex block's cfg `.hint` is a separate, unused CONFIG key — no journal-page behavior change, byte-identical text contract preserved. This is a config-gated no-op on the journal page; harmless. Keep. (IO may drop the unused `hint` key in a later tune pass at its own discretion.)
3. **"killToastEvery first-kill ruling"** — Devbot ruled that kill #1 of a type uses the `killToastTitleUnseen` first-kill shape regardless of whether the type was previously sight-witnessed, and every >1 kill toasts only at n % killToastEvery === 0 (5, 10, 15...). Confirmed against bestiary.js:100-107 and CONFIG "toast on first kill + every 5th kill of a type" (:4909); VM cadence probe: kills 1..5 → exactly 2 toasts. ACCEPTED as spec-faithful. Keep.
4. **3 leftover Devbot probe scripts in io/reports/** — **FLAG FOR CLEANUP**, non-blocking but should not ride the commit. They were single-use Devbot validation leftovers, not deliverables, and would be dead weight in the build lane forever. Per the task contract, **IO should delete all three before commit** — this validator did not touch them (NO-GIT scope, plus my own probes were inline in chat). **Clean them.**

## Final verdict

**VERDICT: PASS**
- V-1..V-13 all PASS (13/13). C-1 PASS, C-2 PASS. Zero blocking findings; all four deviations adjudicated non-blocking.
- The build artifact is clean & reproducible (byte-identical rebuild, sha256 3fd0c5c3…2279, marker count 20, stamp `11-07 19:09Z e1d66d6` from the deterministic law).
- Pre-commit cleanup requested of IO: delete the three `io/reports/qjr4_*_probe.py` Devbot leftovers.
- NO-GIT honored; no harness, no headless browser, no playable claims.
