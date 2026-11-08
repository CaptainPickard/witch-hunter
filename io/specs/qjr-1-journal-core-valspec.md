# QJR-1 Journal Core Validation Spec (v1, Testerbot-owned; written BEFORE the Devbot build)

Round: qjr-1 (journal CORE: entries model, unlock edge, save roundtrip, HUD
button + panel skeleton/list). Worktree /tmp/wh-worldfeat @ feat/world-visuals,
HEAD recorded at dispatch (V-0). Spec: io/specs/qjr-1-journal-core-spec.md;
this file binds S-7 A1-A10. Test style: node one-shots ONLY (fake-DOM recorder
harness, see Harness law). NO harness runs, NO headless-browser smoke tests, NO
browser automation (no-harness-playtest-gate standing order). NO git writes
(NO-GIT law): validate the tree as found; IO commits after the verdict.
Read-only git (rev-parse/status/diff/log) allowed, REQUIRED for census groups.
NO serving checks: the post-verdict flip / served-URL verification is IO's
step, never Testerbot's.

## File law for the round

TOUCHED (may differ from V-0 baselines only after landing):
  prototype/js/CONFIG.js (new CONFIG.journal top-level block ONLY — S-1)
  prototype/js/game.js (FIVE added '// QJR-1'-tagged lines, nothing else — S-3)
  prototype/index.html (exactly ONE new script tag — S-4)
  prototype/style.css (append-ONE-section at EOF only — S-5)
  prototype/js/journal.js (NEW file, whole module — S-2)
  prototype/builds/v8-playable.html (rebuilt artifact, tools/build_v8.py)
ZERO-TOUCH (sha256 UNCHANGED through the whole validation):
  prototype/js/npc.js, wareffort.js, save.js, camp.js, chest.js, cooking.js,
  touch-controls.js, player.js, region-defs.js (all under prototype/js/)
Any ZERO-TOUCH sha change at ANY point = immediate FAIL (no grace, no
re-derivation license). Journal is read-only over the quest machinery:
journal.js may read WH_NPC.questState() but never writes quest state.

## Pre-checks (sha the files BEFORE reading any landed code)

V-0. Record sha256 FIRST of: CONFIG.js, game.js, index.html, style.css, npc.js,
     wareffort.js, save.js (all prototype/js-or-root paths under /tmp/
     wh-worldfeat), + prototype/builds/v8-playable.html (pre-build sha AND
     byte size) + the byte size of style.css (V-1d append-only check needs it)
     + `git -C /tmp/wh-worldfeat rev-parse HEAD`. Also write the validator-
     authored one-shot /tmp/qjr1_pre_config.js output to
     /tmp/qjr1_pre_config_keys.json: CONFIG top-level keys, warEffort.ladder
     keys+values, regionC.quest keys, inventoryUI keys. After validation re-run
     ALL (V-11); the report carries the pre/post sha table. IO-logged
     pre-dispatch baselines (must MATCH before Devbot lands):
     HEAD   dd93ad8ec7dc75dfba91b90d64759d1b7f0037ea
     CONFIG.js     92cf9c5586ea11d96f4cb4d583fd171b1d02a63ecf5d98ef5272ebb83e734f3e
     game.js       afe066a1697bf15d563914a15b9bccd1bfe300901d8f75a0f54e7131ffe733fd
     index.html    9fbae01d1583cd98bc9fb7ac08ea7deedb73623ba1af67afbd54b00d088b230b
     style.css     1bdc088ddde9090e1d94cf0341aad00f63fe97de7bbc9da7b4e22ee9c1802e0b
     npc.js        cf9137db41d76d8cc80fa37460a6b23d7beb84315850477f7b56862ac8ca3f31
     wareffort.js  ad4b7f05520c8e567bde287b30dd7afb5d9679a8310f4bdd222cb4742c67b1b4
     save.js       823fad17167c3bff2a5663bd3ba510867cdeb2bfe3a0682352492f1609574e11
     A mismatch before Devbot lands = the tree changed under dispatch; STOP and
     re-derive before designing checks.
V-0b. Pre-sha the remaining six zero-touch files (camp/chest/cooking/
     touch-controls/player/region-defs — no IO baseline; this recording IS the
     baseline). HEAD must equal the V-0 sha at every verdict moment (V-11
     re-proves at the end).

## Landing gate (poll discipline)

Devbot lands CONFIG.js + game.js + index.html + style.css edits + NEW
js/journal.js + a rebuilt artifact. Poll with `sha256sum` (>= 30 s interval)
until ALL of: (i) CONFIG.js, game.js, index.html, style.css pre-shas EACH
changed, (ii) prototype/js/journal.js EXISTS, (iii) `grep -c 'QJR-1'` on
prototype/builds/v8-playable.html >= 1, (iv) `git diff -U0 --
prototype/js/game.js | grep '^+' | grep -c 'QJR-1'` >= 5 (poll signal only;
the EXACT five-line census is V-1e). Poll cap: poll >= 15 minutes before ANY
"landing never happened" FAIL conclusion. A landing detected mid-poll re-pins
V-0's post-baselines; before treating the tree as validatable, re-check EVERY
zero-touch sha is still at its V-0 value (mid-landing drift = FAIL).

## V-groups (each a numbered node check; bind spec S-7 A1-A10)

V-1 File census (A1) — exact assertions:
  - V-1a: prototype/js/journal.js EXISTS and is NEW (untracked, or pure-
    addition with zero '-' diff lines); `node --check prototype/js/journal.js`
    exit 0; `grep -c THREE prototype/js/journal.js` === 0 (pure DOM, S-6 law).
  - V-1b: `git diff -U0 -- prototype/index.html`: EXACTLY ONE added line equal
    to `<script src="js/journal.js"></script>`, ZERO removed lines, the line
    directly above it is the wareffort.js script tag (manager tier, before
    save.js/touch-controls). No other tag/comment/attribute.
  - V-1c: CONFIG.js diff: ZERO removed lines; ALL added lines sit inside the
    new top-level `journal: {` block (a SIBLING of inventoryUI/camp, not
    nested); `node -e "require('/tmp/wh-worldfeat/prototype/js/CONFIG.js')"`
    exit 0; post top-level key set = pre-snapshot keys + EXACTLY {'journal'}.
  - V-1d: style.css append-only law: sha256 of the FIRST <V-0 style.css byte-
    size> bytes of the landed file === the V-0 style.css sha (pre content is a
    byte-prefix; zero edits/reorders above EOF).
  - V-1e: game.js diff is EXACTLY the five lines: `git diff -U0 --
    prototype/js/game.js` has ZERO removed lines and EXACTLY 5 added lines;
    after stripping any trailing comment each added line EQUALS a pinned code
    line, each exactly once:
      if (window.WH_JOURNAL) window.WH_JOURNAL.init(game);
      if (window.WH_JOURNAL) data.journal = window.WH_JOURNAL.capture();
      if (window.WH_JOURNAL) stored.journal = window.WH_JOURNAL.capture();
      if (window.WH_JOURNAL) window.WH_JOURNAL.restore(data && data.journal);
      if (window.WH_JOURNAL) window.WH_JOURNAL.update(dt);
    every added line carries '// QJR-1'; anchor adjacency via grep -B1 — (1)
    directly after the WH_AMBUSH init line, (2)/(3)/(4) directly after the
    warEffort capture / stored / restore lines, (4) BEFORE baseRestore, (5)
    directly after WH_NPC.update(dt).
  - V-1f: all NINE zero-touch shas re-read === V-0/V-0b values.

V-2 Unlock edge (A2) — /tmp/qjr1_v2.js, fresh harness: init(fakeGame) with
  WH_NPC.questState() === 'available', dayNight.day = 4: isBorn() === false;
  button node EXISTS (id 'wh-journal-btn') but hidden (style.display 'none');
  #wh-journal present, no 'open' class. Flip questState -> 'active'; update()
  EXACTLY once: isBorn() true; entries.length === 1; entries[0].id ===
  'quest-findDaughter'; entries[0].day === 4 (the fake day); entries[0]
  .title/body/source === CONFIG.journal.text.seedTitle/seedBody/seedSource;
  button visible (display no longer 'none'); isOpen() false (birth opens
  nothing); toasts array EMPTY (seed stays silent — the dialog panel is
  closing; QJR-2 revises entry toasts).

V-3 Edge single-fire (A3) — /tmp/qjr1_v3.js: fresh harness as V-2; fire the
  edge with one update, then update() x 50 MORE while questState stays
  'active': entries.length STILL EXACTLY 1; entries[0] same object identity
  (===, no re-seed); toasts still empty; isBorn() true throughout.

V-4 Dedupe + append/toast (A4) — /tmp/qjr1_v4.js: fresh harness, edge fired:
  - append('quest-findDaughter', 'dupTitle', 'dupBody') again: entries.length
    still EXACTLY 1; live entries deep-equal the pre-call state; ZERO toasts
    (dedupe no-op: no toast, no write, no order change).
  - append('topic-wolf', 'Wolves trail the cart road', 'wolf body'): length
    EXACTLY 2, newest-FIRST (entries[0].id 'topic-wolf', entries[1].id
    'quest-findDaughter'); entries[0].day === current dayNight.day (the
    default); toast fired EXACTLY ONCE with text ===
    CONFIG.journal.text.toastNew + 'Wolves trail the cart road'.

V-5 Roundtrip + no-aliasing (A5) — /tmp/qjr1_v5.js, fresh harness, edge + one
  appended entry (2 entries):
  - capture() returns EXACTLY the keys {born, entries} (set equality); every
    row EXACTLY {id,title,body,day,source} (set equality per row); order
    newest-first preserved; born === true.
  - restore(capturedBlock) -> isBorn() true; entries deep-equal the captured
    rows (JSON equality, ORDER INCLUDED), button visible; capture() after
    restore identical to the input block.
  - NO ALIASING: mutate the captured payload hard (payload.entries.push({});
    payload.entries[0].title = 'MUTATED'; per-row field writes) -> live
    entries unchanged (clone5 independence, S-2 law).

V-6 Old-save + clamp (A6) — /tmp/qjr1_v6.js; EVERY sub-case crash-free (no
  throw, one-shot asserts each):
  - restore(undefined), questState 'active': born true, entries [], button
    visible; a following update() keeps entries [] (old-save journal starts
    empty; QJR-3 backfills).
  - restore(undefined), questState 'available': born false, entries [], button
    hidden; fake openKey press does NOT open the panel (isOpen() stays false —
    the !born early return, S-2 key-handler law).
  - restore({born:true, entries:[{id:1,title:'t',body:'b',source:'s',day:-5},
    null, 'garbage', {id:'ok',title:'T',body:'B',source:'S',day:2.7}]}):
    EXACTLY 1 valid row — id 'ok', day === 3 (2.7 rounds-to-integer law),
    title/body/source preserved; the {id:1, day:-5} row, null, and 'garbage'
    each DROPPED (negative day / malformed rows dropped, never crashed).
    Non-finite bind: a row with day NaN and one with day Infinity each DROPPED
    (finite-day rows only). born true -> button shown after the restore.

V-7 Panel input law (A7) — /tmp/qjr1_v7.js: fresh harness, edge fired, player
  alive, inventoryUI.blocked false:
  - OPEN via button pointer: dispatch the registered pointerdown handler with
    a spy event — preventDefault AND stopPropagation both called;
    inventoryUI.blocked === true; player.setInputSuspended spy history ===
    [true]; #wh-journal HAS the 'open' class; isOpen() true.
  - openKey toggle: dispatch keydown CONFIG.journal.openKey while closed ->
    opens with the SAME pair (blocked true, spy [true]).
  - Esc: dispatch Escape while open -> blocked === false; spy history ===
    [true, false] (BOTH reversed, npc.js:178-179 law); 'open' class gone;
    isOpen() false. CLASS-ONLY law: the recorder shows NO write to rootEl
    style.display at any point; panel state toggles exclusively via the
    .open class on #wh-journal.
  - DEATH: reopen (spy history [true,false,true]), set player.dead = true,
    update() -> panel closed, blocked === false, spy history ===
    [true,false,true,false] (suspension released, npc.js:252 law).

V-8 Build + markers (A8; A10 title-stamp clause): `cd /tmp/wh-worldfeat &&
  python3 tools/build_v8.py` exit 0 from the repo root; on
  prototype/builds/v8-playable.html: `grep -o 'QJR-1' | wc -l` >= 6;
  `grep -o 'wh-journal-btn' | wc -l` >= 2; the built html inlines journal.js —
  'js/journal.js' OR a known journal.js sentinel ('WH_JOURNAL') present >= 1.
  Byte-size sanity: log the built size; must be >= the V-0 pre-build byte
  size. Determinism: run the build a SECOND time (exit 0); artifact sha after
  run 2 IDENTICAL to run 1 (title-stamp deterministic). NO serving checks, no
  server start, no URL fetch (the flip is IO's).

V-9 CONFIG isolation (A9) — /tmp/qjr1_v9.js: read journal.js, strip ALL //
  line comments and /* */ blocks FIRST (comments exempt), then extract every
  single-/double-quoted string literal. A literal is ALLOWED only if:
    (a) a CONFIG path/key member used for reads (e.g. 'journal');
    (b) an id/class string from the spec: wh-journal-btn, wh-journal,
        journal-panel, journal-rule, journal-page, journal-row,
        journal-row-title, journal-row-day, journal-empty, inv-panel,
        inv-title, inv-hint, wh-root;
    (c) structural/boilerplate: 'use strict'; instantiated DOM tag names;
        event names (keydown, Escape, pointerdown, mousedown, click,
        contextmenu); attribute/property strings (id, class, style, display);
        the spec-pinned tooltip 'Journal (J)'.
  The one-shot FAILS on any literal outside these classes. HARD second bar:
  NO string literal may EQUAL any CONFIG.journal.text VALUE (glyph, 'JOURNAL',
  the empty line, seedTitle, seedBody, seedSource, 'Journal: ', 'Esc close')
  or the openKey value ('KeyJ') — every journal string lives in
  CONFIG.journal.text; the module reads only CFG.journal.*.

V-10 Zero-regression (A10): JSON.stringify comparison vs the V-0 pre-snapshot
  — warEffort.ladder keys AND values byte-identical; regionC.quest keys
  byte-identical; inventoryUI keys AND values (openButton included)
  byte-identical; CONFIG top-level post key set = pre + {'journal'} only.
  All NINE zero-touch shas re-read a SECOND time === V-0/V-0b values. Note the
  builds/ title-stamp result from V-8's two-run determinism.

V-11 NO-GIT audit (final) — `git -C /tmp/wh-worldfeat rev-parse HEAD` equals
  the V-0 sha; `git log -1 --format=%H` equals it; `git status --porcelain`
  shows NO NEW staged rows vs the V-0-time recording; `git diff --cached`
  EMPTY; no commit/push/stage/branch by this validator (read-only git only).
  THEN re-sha ALL V-0 files + the whole zero-touch set; the report carries the
  pre/post sha table; any unexpected drift = FAIL with the sha pair quoted.

## Harness law (all V-groups; journal.js is pure DOM)

- NO THREE shim: the harness is a fake-document recorder set, minimal for a
  DOM-only journal. document.createElement returns recorder nodes: id,
  className, classList (add/remove/contains journaled), style object (display
  readable/writable, every write journaled), child arrays,
  appendChild/prepend/removeChild recorders, an addEventListener REGISTRY (the
  test dispatches stored fns with spy events carrying preventDefault /
  stopPropagation spies), key/which fields; document.body and the #wh-root
  lookup are recorder roots. If journal.js touches THREE, the absent global
  FAILS visibility — do NOT add a THREE shim. fake game: player {dead:false,
  setInputSuspended spy}, inventoryUI {blocked flag, toast(app) -> toasts
  array}, dayNight {day: 4, settable integer}; NO scene needed.
- window.WH_NPC = { questState: () => stateVar }, settable, installed BEFORE
  journal.js loads (restore's old-save law depends on restore ORDER — journal
  after WH_NPC.restoreQuest — so the one-shot sets WH_NPC state pre-restore).
  window.CONFIG loaded REAL from prototype/js/CONFIG.js; journal.js loaded
  REAL (require) after the shims; window.WH_JOURNAL captured; init(fakeGame)
  per one-shot.
- One-shot files authored FRESH by the validator at validation time as
  /tmp/qjr1_<group>.js, run via `node /tmp/qjr1_<group>.js` with cwd =
  /tmp/wh-worldfeat; each prints PASS/FAIL per assertion, exits non-zero on
  any FAIL. This valspec prescribes the ASSERTIONS; the validator authors the
  code fresh. NOTHING is written inside the worktree except the verdict
  report; scratch scripts and the pre-snapshot live in /tmp.

## Verdict file

Write io/reports/2026-11-06-qjr-1-journal-core-validation.md (worktree; the
ONLY worktree write): FIRST line is the one-line `VERDICT: PASS` or
`VERDICT: FAIL` banner, then per-group PASS/FAIL (V-0, V-0b, V-1..V-11) with
the actual node one-shot output lines, the pre/post sha tables (V-0 + V-0b),
the landing-gate timings (poll start, first-change minute), and — on any FAIL
— every failed check with observed vs expected. No partial PASS: any FAILing
group = FAIL verdict. Cross-bind: V-0 sha recording is mandatory FIRST (before
reading any landed code); if two readings of the same file happen at different
times, both go in the report and the SECOND is the validated one, explicitly
labeled. A1-A10 bind map: A1=V-1, A2=V-2, A3=V-3, A4=V-4, A5=V-5, A6=V-6,
A7=V-7, A8=V-8, A9=V-9, A10=V-10; the landing gate feeds every group; V-11
closes the round.
