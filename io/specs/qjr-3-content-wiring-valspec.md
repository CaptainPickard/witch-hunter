# QJR-3 Journal Content Wiring Validation Spec (v2, Testerbot-owned; authored 2026-11-06 and AMENDED same-day — see the amendment note)

Round: qjr-3 (journal content wiring: war-board clerk + camp folk + one
findDaughter-anchor line; 3 new topics in CONFIG, 2 append sites in wareffort.js,
1 in camp.js). Worktree /tmp/wh-worldfeat @ feat/world-visuals, HEAD recorded at
dispatch (V-0). Spec: io/specs/qjr-3-content-wiring-spec.md; this file binds its
A1-A12.
AMENDMENT 2026-11-06 (Testerbot, second authoring dispatch): the Devbot QJR-3
build landed while this valspec was the only file in flight — the landed diff
is pinned in 'Landed-state pin' below; G1, G8, G9 and V-11 are marked AMENDED
accordingly. The landed code was audited seam-for-seam against A1-A12 and
matches; G2-G7 and G10 stand as written. Format + harness law continue io/specs/qjr-2-journal-dialogue-search-valspec.md
and the STAGE 6 fake game/window stub pattern of io/specs/qjr-1-buildcard.md.
Test style: node one-shots ONLY (fake-DOM recorder harness, see Harness law).
NO harness runs, NO headless-browser smoke tests, NO browser automation, NO npm.
NO git writes (NO-GIT law): read-only git (rev-parse/status/diff/numstat) allowed
and REQUIRED for the V-1 census. build_v8.py runs are allowed (V-9). NO serving
checks: build+flip+served-bytes verification is IO's step, never Testerbot's.

## File law for the round

TOUCHED — `git -C /tmp/wh-worldfeat status --porcelain` at verdict time must show
EXACTLY these paths and NOTHING else (V-1), and `git diff --numstat HEAD` must
show 0 deletions on every one (A8 zero-touch law, V-1):
  prototype/js/CONFIG.js    (mod: journal.topics gains requisition, firstFill,
                             campRest; ONE `// QJR-3` tag allowed on the topics
                             comment; NOTHING else in CONFIG moves)
  prototype/js/wareffort.js (mod: 1 module-local `var JT` line + 2 append sites;
                             NOTHING else moves)
  prototype/js/camp.js      (mod: 1 module-local `var CJ` line + 1 append site;
                             NOTHING else moves)
  prototype/builds/v8-playable.html (rebuilt artifact, tools/build_v8.py)
ZERO-TOUCH (sha256 UNCHANGED through the whole validation):
  prototype/js/journal.js, npc.js, save.js, game.js, player.js, chest.js,
  cooking.js, inventory.js, touch-controls.js, region-defs.js,
  prototype/index.html, prototype/style.css.
Any ZERO-TOUCH sha change at ANY point = immediate FAIL (no grace). Journal stays
read-only over quest machinery; no CSS, no DOM, no THREE/scene work (A12, V-10).

## Pre-checks

V-0. Record sha256 FIRST of CONFIG.js, wareffort.js, camp.js + the six named
     ZERO-TOUCH files, prototype/index.html, prototype/style.css, and
     prototype/builds/v8-playable.html (pre-build sha + byte size) +
     `git -C /tmp/wh-worldfeat rev-parse HEAD`. After validation re-run ALL (V-11
     re-prove); the report carries the pre/post sha table. No IO baselines exist
     for this round — this recording IS the baseline. AMENDED (build landed
     early): for the builds artifact the recorded sha + size ARE the
     landed-build baseline observed at audit time (v8-playable.html
     544397fceebb961711a79c946a537c36f9c4b014eac16f78a6079f96673bcea7,
     3402596 bytes — re-derive, don't trust this line). HEAD must equal the
     V-0 sha at every verdict moment only for the git-committed tree (HEAD
     itself stays e694562 while the QJR-3 edits live uncommitted); a drift
     in the TOUCHED files' UNCOMMITTED state during validation = the tree
     changed under dispatch — STOP and re-derive before designing checks.

## Landed-state pin (Testerbot amendment, 2026-11-06 ~23:04Z — binds G1/G8/G9/V-11)

The Devbot QJR-3 build landed WHILE this valspec was the only file in flight
(parallel dispatch). No QJR-3 verdict exists yet, so nothing is invalidated —
but the 'written BEFORE the build' framing is void and G9's fresh-bake
sequence is re-based on the landed artifact. This valspec remains the
validation authority; groups G2-G7 and G10 stand as written; G1, G8, G9 and
V-11 are AMENDED. Landed state, read at HEAD e694562 + uncommitted edits:

- git diff --numstat: prototype/js/CONFIG.js +20/-0; wareffort.js +3/-0;
  camp.js +2/-0; builds/v8-playable.html +26/-1 (its ONLY deletion is the
  <title> stamp swap — see G8).
- Exact seams ALREADY IN PLACE (all verify-greps re-anchor on markers):
  CONFIG.js: 3764 journal opens; 3779 'topics: {'; 3780 the ONE '// QJR-3'
  comment; 3781 requisition; 3787 firstFill; 3793 campRest; 3799 rescue;
  3805 complete; topics block closes at 3813. QJR-1 keys shifted +18 lines
  (rescue id now 3801, complete id 3807).
  wareffort.js: 10 'var JT = CFG.journal && CFG.journal.topics;  // QJR-3'
  (between CFG at 9 and W at 11); 191 the award append — after the 185
  satchel-full early-return and after 186-189 active/postedDay/awardQuota/
  offer-toast; 218 the fill append — after 213 resolve() and 216
  setPapersVisible(false), before 219 the over-band/exact toast ternary
  (ONE shared site; the over-band path cannot double-write).
  camp.js: 22 'var CJ = CFG.journal && CFG.journal.topics;  // QJR-3'; 327
  the append — first statement after the 322-325 dusk/night gate + return,
  before 328 (var self, ms) / 333 (resting = true) / 334-338 (prepareWake,
  fade, wake-state profile write). Refused rests return at 325 and never
  reach 327.
- Markers in the built artifact as of this audit: 'war-effort-requisition'
  appears exactly once and 'camp-first-rest' exactly once.
- The line numbers above are check-time CITATIONS only: the verifier
  re-derives each with grep -n '<marker>' prototype/js/<file> and treats a
  +/-3-line drift as PASS — the content match is the assertion, the number
  is the citation. Probes derive runtime values from CONFIG, never from this
  pin (SEAT from CFG.warEffort.boardSeat; quota via quotaQ(); camp strings
  from CFG.camp).

## Harness law (shared by all node one-shots)

- Runner: `node /tmp/qjr3_<name>.js` one-shots authored by the validator fresh
  at validation time under /tmp/ (scratch — NEVER inside the worktree or
  prototype/). Each loads real modules in order: CONFIG.js, journal.js,
  wareffort.js, camp.js — via `vm.runInThisContext` (or fs+eval with a stub
  `window`), ES5 IIFEs so a plain stub environment suffices. NO npm, NO jsdom.
- Fake game stub (STAGE 6 pattern): `window.WH_CONFIG` real; `document` stub with
  createElement/addEventListener recorders that swallow DOM work (camp.js and
  journal.js init paths must not run their real buildMenu/panel builds — the
  tests drive Camp.prototype methods and WH_JOURNAL.append directly, NOT init()).
- Inventory stub: recorder object with addItem(id, n) (returns what fit; 0 when
  flagged full), countOf(id), removeItem(id, n). Installed on
  `game.inventory` AND `window.WH_INVENTORY`.
- Journal recorder: when a test wants to spy WITHOUT the real journal, install a
  stub `window.WH_JOURNAL` whose append(id, title, body, day, source) records the
  call with the journal module's current game.dayNight.day supplied by the test.
  When a test wants real dedupe/roundtrip, load the real journal.js with a game
  stub whose dayNight.day is settable (fake clock).
- Day clock: `game.dayNight.day = N` set explicitly per scenario; camp instance
  needs `this.dayNight` pointing at the same fake clock ({ dormant:false,
  phase:'dusk'|'night'|'day', day:N, nextDawn(), beginCycle() recorders,
  prepareWake() recorder }).
- Camp driver: `new window.WH_CAMP.Camp(fakeDeps)` needs menuCamp set (a fake
  camp object with respawn:{x,z}), resting=false, menuEl/fadeEl/classList stubs,
  toast recorder, writeProfile forced true, rest() spied (real Camp.prototype.rest
  may run against the fake deps — assert its recorders fire but its payload shape
  is what matters in V-7). setTimeout replaced by a synchronous executor so the
  saveAndHeal chain completes inside one script run.
- WH_WarEffort driver: real module; `init(game)` runs; THREE left undefined so
  buildBody() is skipped (headless-safe per spec); setPapersVisible/rebuildTallyPins
  are internal no-ops without THREE. `game.regionManager` omitted; player pos set
  to the board SEAT so near() passes (SEAT from CFG.warEffort.boardSeat, else the
  fallback {x:5.9,z:-15.5}).
- Expected PASS/FAIL rule is per-check below: PASS = the recorded/asserted fact
  holds; FAIL = any violation recorded, and ONE failed check fails its whole V-x
  group (but the run continues to collect the remaining evidence).

## Check groups (map to spec acceptance criteria)

G1 — V-2 Topics shape (node one-shot /tmp/qjr3_topics.js + grep)
  Check: load CONFIG.js; assert WH_CONFIG.journal.topics gains EXACTLY 3 keys
  (requisition, firstFill, campRest) on top of existing rescue+complete; assert
  every id/title/source/body string against A1 verbatim, modulo JS escaping and
  the hyphen-vs-em-dash spelling shown ('war-effort-requisition',
 'Requisition papers', 'The quartermaster' exactly (both requisition+firstFill
 sources = 'The quartermaster'), campRest source =
  'Camp folk', id 'camp-first-rest', title 'Taken in at the camp'; body strings
  byte-compare against the normative A1 lines including the possessives
  "garrison's" and "Old King's Barrow"). AMENDED (Testerbot audit): the
  byte-compare source is the normative A1 block in the IO spec, NOT this
  round's Context prose — the campRest body does NOT contain 'Old King's
  Barrow, west past the dead trees' (that phrasing exists only in the QJR-1
  seedBody, CONFIG.js:3772); the landed campRest string '...the barrow west
  of the dead trees, the Old King's Barrow, where the mist keeps its own
  accounts...' matches A1 exactly and PASSES). Assert no id collision with
  'rescue-findDaughter' / 'quest-findDaughter-complete'.
  PASS rule: exact topic objects per A1 + zero collisions.
  FAIL rule: any missing/extra key, any string differing beyond escaping, any id
  reusing an existing id.
  Grep corroboration: `grep -n "war-effort-requisition\|war-effort-first-fill\|camp-first-rest" prototype/js/CONFIG.js` shows 3 hits inside the topics block only.

G2 — V-3 Award event (node one-shot /tmp/qjr3_award.js)
  Check: fresh module load; stub WH_JOURNAL recorder; scenario 1 idle board:
  tryOpen() with empty stub bag → addItem(RQ.itemId,1) returns 1 → assert
  recorder holds exactly ONE append whose id === JT.requisition.id
  ('war-effort-requisition'), title from CONFIG, source 'The quartermaster',
  day === undefined (A9: no day argument — assert append was called with day arg
  === undefined, i.e. the site passes `undefined` positionally).
  Scenario 2: bag flagged full (addItem returns 0) → tryOpen() → recorder EMPTY
  (satchel-full refusal fires nothing — A4 says NOT the refusal).
  Scenario 3: after scenario 1 success (board active), call tryOpen() again with
  oreCount 0 → recorder STILL exactly one entry (second take fires nothing).
  Scenario 4: fresh load, two consecutive idle awards in one day is impossible
  by design (active path taken); instead restore a foreign logic state is out of
  scope — skip.
  PASS rule: 1/0/0 appends across the three scenarios in order.
  FAIL rule: append fires on refusal; wrong id/source; a day argument passed.

G3 — V-4 Fill event (node one-shot /tmp/qjr3_fill.js)
  Check: scenario 1: seed a real award first (take), then set bag ore count
  exactly quotaQ(logic.repeatIndex) (read quotaQ and oreRequired live from
  CONFIG.warEffort.requisition — landed field CONFIG.js:3397 'oreRequired: 6'
  at repeatIndex 0; derive, never hardcode) → tryOpen() → recorder holds
  exactly ONE append id 'war-effort-first-fill' (shared site, not a second).
  Scenario 2 (over-band): fresh load, award, set ore ABOVE quota (quota+2) →
  tryOpen() → assert still exactly ONE 'war-effort-first-fill' entry, NOT two
  (the over-band toast path must share the single site — A5).
  Scenario 3: fresh load, award, ore BELOW quota → tryOpen() → zero appends.
  PASS rule: 1/1/0 appends, id always 'war-effort-first-fill'.
  FAIL rule: double append on over-band; append on the not-enough-ore refusal.

G4 — V-5 Camp rest (node one-shot /tmp/qjr3_camp.js)
  Check: scenario 1 (dusk): Camp instance, dayNight.phase='dusk', journal
  recorder stub → saveAndHeal() (synchronous setTimeout) → exactly ONE append,
  id 'camp-first-rest', source 'Camp folk', day arg undefined.
  Scenario 2 (daytime refusal): fresh instance, phase='day', dormant=false →
  saveAndHeal() → zero appends; assert the sleepGate toast still fired (behavior
  unchanged — V-10 side-proof).
  Scenario 3 (plain save): call Camp.prototype.save() with phase='dusk' → zero
  appends (respawn-only save must NOT capture).
  Scenario 4 (load): call Camp.prototype.load() against an existing profile →
  zero appends.
  PASS rule: 1/0/0/0 appends.
  FAIL rule: append on refused rest, plain save, or load; duplicate on dusk pass.

G5 — V-6 Absent-journal guards (node one-shot /tmp/qjr3_guards.js)
  Check: `delete window.WH_JOURNAL;` BEFORE loading wareffort.js and camp.js;
  rerun the award, fill (both refusal paths + success), and camp dusk/night/day
  scenarios. Every path must complete with NO throw — the whole-call guard
  `if (JT && window.WH_JOURNAL)` / `if (CJ && window.WH_JOURNAL)` makes append a
  no-op (A7).
  Grep corroboration: each append site line matches
  `grep -nE "if \((JT|CJ) && window\.WH_JOURNAL\)" prototype/js/{wareffort,camp}.js`
  and yields exactly 3 hits total (2 in wareffort, 1 in camp); no site guards
  inner fields individually (e.g. no `JT.requisition &&`).
  PASS rule: all scenarios exit 0 with zero appends attempted; grep shows the 3
  whole-call guards and only whole-call guards.
  FAIL rule: any throw, any partial-field guard, any missing site.

G6 — V-7 Roundtrip + schema (node one-shot /tmp/qjr3_roundtrip.js)
  Check: driver script that (a) awards (take), (b) fills, (c) rests (dusk) —
  with the REAL journal.js loaded and a settable day clock — then calls
  WH_JOURNAL.capture(); serializes; starts a FRESH module load (new vm context
  or process) restoring into a pristine journal: restore(block) → assert the
  entries array holds each of the three new ids EXACTLY once (no phantom dupes)
  alongside however many seed rows apply; then re-award + re-fill + re-rest on
  the fresh journal with the fake clock advanced → assert zero NEW entries
  (dedupe by id, A10). Assert warEffort capture() keys are the FOUR-key payload
  {active, postedDay, resolvedDay, repeatIndex} (schema unchanged — spec OUT:
  save schema untouched; landed code wareffort.js:240-243) and camp profile
  schema unchanged. AMENDED (Testerbot audit): do NOT compare against a
  "pre-round fresh-load capture of the ZERO-TOUCH camp.js" — camp.js is a
  TOUCHED file this round and no pre-round runtime baseline exists. The
  schema authority is the UNTOUCHED save.js (zero-touch sha table): the
  profile's camp block is built only there — save.js:92-97
  `camp: { sites: [{id, regionId, x, z, face:{x,z}}], respawn: copyRespawn(...) }`
  — and camp.js feeds it only via `respawnCamp.respawn` (save.js:73) whose
  shape is set by Camp.prototype.setRespawn (camp.js:305-308: regionId/x/z/
  face/campId). Assert: (a) save.js diff empty (zero-touch), (b) the camp.js
  diff contains ONLY the CJ var line + the one guarded append (G8), (c) at
  runtime the G4 dusk driver's writeProfile spy receives a camp object whose
  .respawn has exactly the keys {regionId, x, z, face, campId} and the save
  payload recorded by a WH_SAVE.save spy (window.WH_SAVE stubbed) carries
  camp.sites/respawn shapes identical to save.js's literals — i.e. no new
  keys injected into camp's own profile anywhere.
  PASS rule: entries survive exactly once; repeat events mint nothing;
  warEffort capture keys are exactly the 4-key set; camp schema proven via the
  save.js authority (diff empty + respawn key-shape assertion above).
  FAIL rule: dupes after restore; extra payload keys; missing entries.
  (Note: journal block persistence itself is pre-QJR-2 behavior under test here
  only to prove the new ids ride it.)

G7 — V-8 Day/source stamps (node one-shot /tmp/qjr3_days.js)
  Check: with the real journal and clock set to day N, fire all three events
  (take, fill, dusk rest); WH_JOURNAL.capture() → each entry `day === N`
  (normalizes via journal defaults — A9), sources: requisition + firstFill =
  'The quartermaster', campRest = 'Camp folk' — exactly per A1.
  Then advance clock to N+1 and repeat both board events (day rolled:
  resolvedDay < new day so rollNewDay re-arms) → requisition and firstFill ids
  STILL appear once each (the new-day re-award must not mint a dupe either —
  A10 across days).
  PASS rule: day stamps === event-time day; source strings exact; no dupes
  across the day roll.
  FAIL rule: day stamped by the call site (any non-undefined day argument),
  wrong source strings, a second entry after the day rolled.

G8 — V-1 Census + A8 tag (read-only git + grep) — AMENDED (Testerbot audit
  of the landed build):
  Check: `git -C /tmp/wh-worldfeat status --porcelain` lists EXACTLY
  prototype/js/CONFIG.js, prototype/js/wareffort.js, prototype/js/camp.js,
  prototype/builds/v8-playable.html and nothing else; `git diff --numstat`
  shows 0 deletions on CONFIG.js, wareffort.js and camp.js, and on
  builds/v8-playable.html EXACTLY ONE deleted line — the <title> build-stamp
  swap (the landed tree shows
  `-<title>Witch Hunter v9 - EPR1 Combat (build 11-06 22:16Z 4e723af)</title>`
  replaced by the QJR-3-stamped title; this is the deterministic stamp law
  from the QJR-1/QJR-2 verdicts, NOT an A8 source deletion — any OTHER
  deleted line in the artifact or in any source = FAIL on A8);
  `grep -rn "QJR-3" prototype/js/{CONFIG,wareffort,camp}.js` (AMENDED
  anchors; no line numbers asserted): CONFIG exactly ONE tag (the topics
  comment — landed at CONFIG.js:3780), wareffort exactly THREE (JT
  var + 2 sites — landed at 10/191/218), camp exactly TWO (CJ var + 1 site
  — landed at 22/327); `git diff -- prototype/style.css prototype/index.html
  prototype/js/journal.js prototype/js/npc.js` is empty; all V-0 ZERO-TOUCH
  shas re-derived and equal (game.js/save.js/player.js/chest.js/cooking.js/
  inventory.js/touch-controls.js/region-defs.js/journal.js/npc.js/index.html/
  style.css per the File-law list).
  PASS rule: exact path set, 0 source deletions + the single title-stamp
  deletion in the artifact, tag counts EXACT as listed, zero-touch shas
  unchanged.
  FAIL rule: any extra touched path, any deleted source line, any deleted
  artifact line other than the title stamp, tag-count drift, any ZERO-TOUCH
  sha drift.

G9 — V-9 Build + marker — AMENDED (the build already landed; verdict-time
  discipline replaces the fresh-bake sequence):
  Check (the artifact is ALREADY built — landed with +26/-1 in the diff, its
  only deletion the <title> stamp swap): FIRST assert the artifact is
  current: `git diff --stat HEAD -- prototype/builds/v8-playable.html` shows
  it modified (it carries the landed QJR-3 bump; if a future state makes
  sources newer than the artifact, RE-BAKE with `python3 tools/build_v8.py`
  from the worktree root and assert exit 0 — the bake is allowed by law and
  is IO's flip step that Testerbot never performs). Then
  `grep -c "war-effort-requisition" prototype/builds/v8-playable.html` >= 1
  AND `grep -c "camp-first-rest" prototype/builds/v8-playable.html` >= 1
  (audit-time count: exactly 1 each). The verifier records the artifact's
  sha + byte size (V-0 baseline: 3402596 bytes) into the report.
  Post-check re-grep of the SOURCES (G1/G5/G8 hits still there — nothing
  mutates sources at any point of validation).
  PASS rule: markers greppable in the built artifact AND artifact mtime
  >= every touched source's mtime (or a re-bake was performed cleanly);
  sources untouched.
  FAIL rule: either marker missing, artifact stale vs sources without a
  clean re-bake, or sources mutated.

G10 — V-10 No CSS/DOM/scene/interact drift
  Check: sha(style.css), sha(index.html), sha(game.js) unchanged (V-0 table);
  `git diff prototype/js/wareffort.js prototype/js/camp.js` contains NO line
  touching THREE (`new THREE.`), `document.createElement`, `addEventListener`,
  `.style.`, classList manipulation, or interactPrompt()/toast() copy strings —
  the ONLY allowed diff hunks are (a) the module-local var line, (b) the three
  guarded append lines. npc.js diff empty (rescue/complete untouched). Also
  assert via G2/G4 recorders that interact chain behavior is unchanged: the
  satchel-full/not-enough-ore/sleepGate toasts still fire and tryOpen still
  returns its usual booleans, and journal entry COUNT is the only new side
  effect on the success paths.
  PASS rule: diff hunks limited to the append plumbing; zero-touch shas hold;
  toast/return-value behavior identical on refusal paths.
  FAIL rule: any DOM/THREE/CSS line in the diff, any copy change, any new
  behavior on refusal paths.

V-11. Re-prove census AFTER everything — AMENDED (landed-build reality): rerun
      the V-0 shas + HEAD (must equal V-0), rerun `git status --porcelain`
      (same four-path set), rerun the amended G1-G10 verdicts so all evidence
      is post-final-state. Report carries pre/post sha table + a verdict line
      per V-1..V-10. AMENDED G8 expectations (title-stamp deletion;
      marker-anchored tag counts) apply. If the worktree drifted while
      validating (any source sha change or a new touched path): STOP, mark
      the affected groups INVALIDATED in the report, and re-derive from the
      new landed state before re-running those groups.

## Deliverables

- Testerbot verdict: io/reports/2026-11-06-qjr-3-content-wiring-validation.md
  (verdict per V-1..V-10, sha pre/post table, one-shot script list + outputs).
- Code verdict authority: this file. Children NEVER push — NO-GIT.
