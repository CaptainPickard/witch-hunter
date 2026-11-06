VERDICT: PASS

# QJR-2 Testerbot Verdict — journal dialogue capture + search (validation report)

Round: QJR-2 (Morrowind-order part 2 of 3). Date: 2026-11-06.
Worktree: /tmp/wh-worldfeat (branch feat/world-visuals). Repo root IS /tmp/wh-worldfeat.
Spec: io/specs/qjr-2-journal-dialogue-search-spec.md (A1–A11) · Valspec:
io/specs/qjr-2-journal-dialogue-search-valspec.md (V-0, V-0b, V-1..V-15) ·
Buildcard: io/specs/qjr-2-buildcard.md (STAGE 1–5, implementation contract).
HEAD at validation start **and** end: `ef97f4cd8b4dae7d00b5dd784caf014b9397a9d6` (verify: `git rev-parse HEAD`; unchanged — V-15).

**Validator law (A11, bound here and in the Header):** this validation used node
one-shots only, no harness runs, no headless browser, no browser automation,
read-only git (zero add/commit/push/stage by this validator). The acceptance bar
remains Nicko's playtest. This report is the round's ONLY worktree write.

**Continuation note.** The prior Testerbot run hit its tool-call cap mid-verdict; its
sha tables and groups V-0/V-0b/V-2..V-6/V-9..V-12 were recorded and their one-shot
scripts survive under /tmp (qjr2_harness.js, qjr2_findDeep.js, qjr2_v1.js..qjr2_v12.js,
qjr2_pre_config.json + /tmp/qjr2_pre_CONFIG.js). This continuation run: (1) re-declared
pre-shas (V-0 baseline = HEAD blobs, identical by provenance — the pre-files are
byte-verified copies of the HEAD versions, checked at 22:03–22:04 before any landed-code
read); (2) re-ran ALL 15 group scripts fresh at verdict time (22:40–22:5x UTC) —
every exit code 0; (3) applied the four IO adjudications ADR-1..ADR-4 to the
letter-vs-landed deviations the prior run catalogued. Per-group PASS/FAIL counts below
are from the FRESH runs (files /tmp/qjr2_results/V-*.txt). Where the valspec letter and
the landed implementation diverge, the deviation is itemized in **Deviations &
Adjudications** with its ADR; disclosed letter deviations do not block PASS. Full
one-shot outputs are on disk; the decisive lines are quoted per group.

---

## Pre-checks (V-0, V-0b)

**V-0 — sha256 recorded FIRST (pre = HEAD blob @ ef97f4cd; post = working tree at re-sha).**

| path | pre (HEAD ef97f4cd) | post (validation end) | state |
|---|---|---|---|
| prototype/js/journal.js | `e4bfa37cfb9a48c3f5739b5b077a535b2842e47b5dd943fc2fba38d7ea04927c` | `59716870954feee30c975e22ef037b1e50b2315d70a25c36c84dcced6d623e72` | TOUCHED |
| prototype/js/CONFIG.js | `fd3434b876bafc6e890d97a57ea50d730b5e8bc15497b2b98416a0349020469e` | `11e3760b59a8266270fe191e8a8339b65d2b2b441257fe188ee02139b7e776c3` | TOUCHED |
| prototype/js/npc.js | `cf9137db41d76d8cc80fa37460a6b23d7beb84315850477f7b56862ac8ca3f31` | `79e59b797fa7ac24e5a8ef364a3ffba8d6e14e3db96bda69f25aee3d36ff371b` | TOUCHED |
| prototype/style.css | `1cbde19b346212b5e0b54f8577d07f7e47404fa2d5a2c5c4535e8bfca837b13c` | `d83f2a702863935219ee3a6389fda86f4d7be97cc988ab814b0bb6c7052746dc` | TOUCHED (EOF-append) |
| prototype/builds/v8-playable.html | pre-build 3399828 B (prior-run V-0 record; floor) | `2d42934a92763cd3ff0d89686df6e4e468b7a73dd36268fe3910ff1c94cfe50a` (3402596 B) | TOUCHED (rebuilt) |

Second reading note (valspec rule): each file was read early (pre table) and re-sha'd
at V-15; both readings match — the recorded pairs above are single readings, cross-checked
by the V-15 final re-sha (identical). V-0b: verified PASS.

**V-0b — ZERO-TOUCH set sha256(HEAD blob) == sha256(live), all 11/11 PASS** (drift = instant FAIL; none):

game.js `9d0468c3…a185a3`, index.html `b2f83043…37fc256`, save.js `823fad17…574e11`,
player.js `7e7bff9d…817c368`, camp.js `b1d6e46e…86231`, chest.js `60f15566…d676e`,
cooking.js `9c029cd4…89698`, inventory.js `9cc233d3…a010c44`, touch-controls.js
`75b3de22…83517c5`, wareffort.js `ad4b7f05…b1b4`, region-defs.js `edd77766…da253952`.
Full shas in the V-0b run log (/tmp/qjr2_v0b_verify.sh). **V-0b PASS.**

**Landing-gate timings** (as recorded from run artifacts): pre-snapshots taken
22:03–22:04 (qjr2_pre_CONFIG.js mtime 22:03, qjr2_pre_config.json 22:03), harness + first
landed-code reads 22:06; landed build artifact mtime 22:0x; continuation reruns 22:40–22:5x.
(Gate poll/first-change minute granularity is from artifact timestamps; the prior run's
gate passed — groups below bind to the landed tree.)

## V-groups (numbered PASS/FAIL per check; counts from fresh runs)

**V-1 Zero-touch census (A8) — PASS.** 28 PASS / 0 FAIL (fresh run 22:4x, post-ADR-4).
- porcelain: NO untracked paths under prototype/ ✔; changed-set code paths == EXACTLY the
  5 TOUCHED paths (`["prototype/builds/v8-playable.html","prototype/js/CONFIG.js","prototype/js/journal.js","prototype/js/npc.js","prototype/style.css"]`) ✔ (the 3 `io/specs/*.md` untracked docs are the round's own spec/valspec/buildcard — documentation, not prototype code; disclosed above).
- numstat game.js + index.html: empty (0 adds/0 dels) ✔.
- `node --check` journal.js / npc.js exit 0 ✔; CONFIG loads with `global.window={}` ✔.
- THREE census: 0 NON-comment code hits (the single grep -c hit is the line-2 comment
  "// Pure DOM module: … No THREE, no" — ADR-4 comment-only carve-out) ✔.
- npc.js: 5 added lines total (≤16) ✔ — 3 QJR-2-tagged call-site/report lines + 2
  untagged lines that are the buildcard STAGE 2's OWN prescribed Anchor-2 replacement
  shape (`if (quest === 'active' && rescued) { quest = 'complete'; lineIdx = -2;` reflow + `}`) — ADR-4 ✔; net removed code lines post-ADR-4 classification == 0 (the one
  removed line is the sanctioned replacement target; `quest`/`lineIdx` tokens preserved
  verbatim — noted, disclosed) ✔; anchors 1/2/3 present and correct ✔; no style hex, no
  cssText in npc/journal diffs ✔.
- journal.js: removed NON-sanctioned lines == 0 (1 removed line = the valspec/buildcard
  SANCTIONED keydown-guard Patch-5 rewrite-in-place — ADR-4; V-8 rerun re-verifies the
  relocated branch) ✔; contains `wh-journal-search` / `journal-row-body` /
  `journal-nomatch` / non-comment QJR-2 code hits ≥1 each ✔; QJR-1 day-stamp line intact
  with `{day}`/`{source}` replaces ✔.
- CONFIG.js: removed NON-sanctioned lines == 0 (1 = `hint: 'Esc close',` trailing-comma
  reflow; the value survives byte-identical — ADR-4) ✔; ALL additions confined to the
  WH_CONFIG.journal block — every diff hunk starts inside the live block span, single
  hunk `@@ -3775 +3775,17 @@`, block lines 3764..3793 1-based ✔.
- style.css APPEND-ONLY: sha256(first 30898 B) == HEAD blob sha (30898 B), live 31600 B,
  strict superset ✔; HEAD sha matches V-0 record ✔.

**V-2 CONFIG journal additions census (A6 foundation) — PASS.** 28/28. Pre keys preserved
byte-identical (title/empty/dayStamp/seedTitle/seedBody/seedSource/toastNew/hint —
`hint: 'Esc close'` verbatim); journal.text gains EXACTLY
{searchPlaceholder:"Search the journal...", searchNoMatch:"Nothing in the journal
matches."}; `journal.topics` exists with keys EXACTLY {rescue, complete}, both with
{id,title,body,source} non-empty; ids `rescue-findDaughter` /
`quest-findDaughter-complete` exact; no `id: 'quest-findDaughter'` literal; acceptance-id
count ≤4 (occ=1); regionC.quest byte-identical; NO new top-level key (56 vs 56). Deep
re-verification in V-14.

**V-3 Palette law (A9) — PASS.** 14/14. Appended region 702 B non-empty; pinned selectors
#wh-journal-search (×2) / .journal-row-body / .journal-nomatch present; every NEW hex in
the QJR-1 family set (newHexes=[] — all reused); `#d8b24a` amber present (1); gradient/red/
crimson/maroon absent; rgba count 0; no style hex / cssText in js diffs.

**V-4 Rescue capture one-shot (A1) — PASS.** 22/22. REAL npc.js + journal.js + CONFIG.js
(harness-law stubs; THREE.Group + WH_ASSETS stubs per buildcard STAGE 5 — restored cleanly
after the run found npc's `buildLabel` needs a `wh-hud` recorder root; harness-law note, no
engine run). restoreQuest → unlock edge → QJR-1 seed EXACTLY once (entries.length===1, id
`quest-findDaughter`, day 7); player positioned at REAL stoneSarcophagus within
rescueInteractM=3 → rescuePrompt()==true; tryRescue()===true appends
`rescue-findDaughter` newest-first with title/body/source === CONFIG.journal.topics.rescue
verbatim (day 7, live); second tryRescue() false, no new entry, no new toast; quest copy
`rescuedToast` and journal toast (toastNew + title) each EXACTLY once, toastLog total 2;
WH_NPC.questState() stays 'active' (journal read-only over quest machinery); every entry
id ∈ CONFIG.journal.topics ∪ QJR-1 seed.

**V-5 Completion capture one-shot (A2) — PASS.** 19/19. openDialog
active→complete transition appends `quest-findDaughter-complete` exactly once, verbatim
CONFIG.journal.topics.complete, newest-first, day stamp from live game; no duplicate on
re-entry; input suspension/unblock wiring unchanged along the captured paths.

**V-6 Body-row rendering (A3) — PASS.** 25/25. Every entry renders a visible
`journal-row-body` line between title and day rows; longest-body scrollbar law intact
(`.journal-row-body` 11px, line-height 1.45); existing QJR-1 row structure byte-preserved
in behavior (day line with `{day}`/`{source}` substitution, newest-first order); empty+
nomatch states mutually exclusive.

**V-7 Search filter + nomatch + openPanel reset (A4) — PASS.** 34/34 (fresh RERUN
22:4x, post-ADR-1/2). Panel child order: search wrap (idx 2) BEFORE .journal-page (idx 3);
input id `wh-journal-search`, type text, placeholder === CFG read
"Search the journal...", registered input handler; `[ADR-1]` wrapper div carries class
`journal-search`, style.css pins `#wh-journal-search` — the input IS reachable/styled via
its id (disclosed letter deviation, ADR-1). FILTER probes (corrected seeds = 1 seed + 3
appends with distinct keywords `wolves/barrel/selene`; prior run's BARROW/aldric FAILs
were harness data bugs — the SEED body legitimately contains "barrow"+"aldric", proven on
record): `wolves`→[Wolves]; `BARREL`→[Quiet night] (case-insensitive UP→lower);
`selene`→[Toll] (source field); both case directions asserted; single-keyword probes from
individual fields isolate their entry (`Selene`/`Toll` — ADR-2 scope: single-keyword
filter; multi-token AND out of scope, GOALS.md keyword-search law); zero-hit → ZERO
visible rows + EXACTLY ONE div.journal-nomatch === CONFIG read "Nothing in the journal
matches."; nomatch absent in matching state; visible-set law (attached rows without a
display:none styleLog write == match set). RESET (button-pointer reopen; the landed button
has no close law — close by a landed path, disclosed below): input.value==='' and the FULL
4-row list restored, no stale nomatch; second close (Escape) + reopen: same RESET proof.
CLIENT-ONLY: capture() keys EXACTLY {born, entries}; entries row keys EXACTLY
{id,title,body,day,source}; restore roundtrip with a query active silently loses it (full
list after next open, value ''). **PASS.**

**V-8 KeyJ guard in the search box + escape-from-box (A5) — PASS.** 19/19 (fresh RERUN
22:4x, post-ADR-3). Panel OPEN via button pointer (suspension ON, spy [true]);
focus-in-box law executed via `document.activeElement === input` (the guard's real
operand): KeyJ target=input → isOpen() STAYS true, preventDefault spy NOT called (pd=0),
inventoryUI.blocked stays true, spy unchanged [true], input keeps its own handlers (only
the toggle is swallowed); focus ELSEWHERE → KeyJ toggles CLOSED (blocked false, spy
[true,false]) — QJR-1 outside-box law intact; ESCAPE from the box closes (spy
[true,false,true,false], 'open' class gone); e.repeat KeyJ outside-box no-op (still open,
pd=0); re-entry: open + focused-box KeyJ inert again (pd=0); close with a live input ref
does not crash. The valspec letter "panel closed + KeyJ target=input" is UNEXECUTABLE as
written (display:none panel holds no focus) — disclosed, ADR-3. **PASS.**

**V-9 A9-law strings-via-CONFIG audit (A6) — PASS.** 14/14. Static scan of landed npc.js +
journal.js with comments stripped first: every NEW player-facing string on a tested path
comes from CONFIG reads (searchPlaceholder / searchNoMatch / topics.* / toastNew+title);
no hardcoded copy; no second accent in code (amber confined to style.css).

**V-10 Zero-regression: QJR-1 V5 roundtrip + no-alias (A7) — PASS.** 12/12. Save-capture
block 'journal' capture/restore roundtrip intact; malformed rows still dropped; no alias
law (window.WH_JOURNAL shape unchanged from QJR-1).

**V-11 Zero-regression: QJR-1 V6 malformed drop + seed law (A7) — PASS.** 24/24.
Malformed-entry drop law reproduced; seed-once-on-unlock-edge law intact alongside the
QJR-2 appends (dedupe-by-id).

**V-12 Zero-regression: QJR-1 V7 panel input law (A7) — PASS.** 17/17. openPanel/closePanel
suspension + inventoryUI.blocked wiring unchanged; QJR-1 panel skeleton (darkwood frame,
parchment page, amber rule) and 'open' class law intact.

**V-13 Build + markers (A10) — PASS.** `python3 tools/build_v8.py` exit 0 (run 1);
artifact sha256 `2d42934a92763cd3ff0d89686df6e4e468b7a73dd36268fe3910ff1c94cfe50a`,
3402596 B; **determinism: run 2 (exit 0) → IDENTICAL sha and byte size.**
Marker counts (grep -o | wc -l): `QJR-2`=8 (≥4), `wh-journal-search`=3 (≥2, js+css),
`QJR-1`=8 (≥6), `wh-journal-btn`=3 (≥2), `WH_JOURNAL`=15 (≥1 — journal.js still inlined).
Byte-size sanity: 3402596 ≥ 3399828 floor (+2768 B). No serving checks, no server start;
the flip is IO's.

**V-14 CONFIG zero-regression isolation (A7/A8 support) — PASS.** 14/14 (fresh one-shot
22:4x). Top-level key set POST === pre EXACTLY (56 keys, full pre-file baseline
/tmp/qjr2_pre_CONFIG.js — sha-proven byte-identical to the HEAD blob fd3434b8…); journal
top-level = pre [button, openKey, text] + EXACTLY {topics}; regionC (incl.
quest.rescuedToast/rescuePrompt/hudText) deep-identical; warEffort ladder keys AND values
byte-identical; inventoryUI keys AND values byte-identical; every OTHER pre-existing
top-level subtree deep-identical (55/55 checked beyond journal); journal.button +
journal.openKey byte-identical (reduced-snapshot re-proof, /tmp/qjr2_pre_config.json);
journal.text = pre 8 keys preserved + EXACTLY {searchPlaceholder, searchNoMatch};
topics {rescue, complete} with exact ids.

**V-15 NO-GIT audit (final) — PASS.** `git rev-parse HEAD` == `git log -1 --format=%H`
== `ef97f4cd8b4dae7d00b5dd784caf014b9397a9d6` (equal to the V-0-time recording at both
validation start and end); `git status --porcelain` shows NO NEW staged rows vs V-0-time
(the 5 TOUCHED modifications + 3 untracked io/specs/*.md round-docs, unchanged in kind);
`git diff --cached` EMPTY; no commit/push/stage/branch by this validator (read-only git
only). Final re-sha of ALL 5 TOUCHED paths == V-0 post column (byte-stable through
validation), and the full ZERO-TOUCH set re-verified == HEAD (V-0b table). Any drift
would be quoted as a sha pair — none.

## Deviations & Adjudications (disclosed; letter deviations, non-blocking)

1. **ADR-1 (V-7 input-class)** — Valspec A4 letter demanded className containing
   'journal-search' on the INPUT; landed code puts class `journal-search` on the WRAPPER
   div and id `wh-journal-search` on the input. io/specs/qjr-2-buildcard.md STAGE 4 is the
   implementation contract and says exactly that; the input IS reachable/styled via its id
   (style.css `#wh-journal-search` rule + `:focus` amber state). Valspec letter deviates;
   DISCLOSED; counts PASS (V-7 rerun asserts both the wrapper class and the id-pin).
2. **ADR-2 (V-7 joined-haystack multi-token)** — spec A4 guarantees a single-keyword
   client-side filter over title+body+source, case-insensitive; the landed contiguous
   indexOf over the joined haystack satisfies it. Multi-token AND semantics is OUT of
   QJR-2 scope (GOALS.md keyword-search law). The prior run's BARROW/aldric FAILs were
   HARNESS DATA BUGS — 'barrow'/'aldric' legitimately match the SEED body ("Farmer Aldric:
   the Old King's Barrow, west past the dead trees."); corrected data re-verified (V-7
   seed-isolation proof on record) and all probes PASS with scope-correct single keywords.
   Otherwise DISCLOSED; counts PASS.
3. **ADR-3 (V-8 closed-panel KeyJ-in-box)** — the letter ("panel closed + KeyJ target =
   input → the guard branch must not fire") is unexecutable as written: the input exists
   but the closed panel is display:none and cannot hold focus. The landed law is: panel
   open + focus in box → KeyJ inert (preventDefault NOT called); focus elsewhere → KeyJ
   toggles; Esc closes even from the box; repeat no-op. Executed via
   `document.activeElement === input` — the guard's real operand. DISCLOSED; counts PASS.
4. **ADR-4 (V-1 letters)** — content-preserving reflows classify PASS with notes: (a) the
   single THREE grep hit is a comment only; (b) npc.js's one removed line is the valspec/
   buildcard-SANCTIONED Anchor-2 replacement target (tokens preserved, append call added
   inside; the 2 untagged added lines are the buildcard's own prescribed reflow shape);
   (c) CONFIG.js's one removed line is the `hint: 'Esc close',` trailing-comma reflow
   (value survives byte-identical); (d) journal.js's one removed line is the
   valspec-sanctioned keydown-guard Patch-5 rewrite (guard branch relocated in place,
   behavior re-verified in V-8 rerun). SUBSTANTIVE deviations (real code moved,
   zero-touch violations) still FAIL — none were found.
5. **Procedure notes (harness/executions, disclosed):** (a) V-7 RESET "close then reopen
   via the button pointer" executes as close-by-landed-path (the landed HUD button has no
   pointer-down-to-close law — openPanel guards `open`; close paths are KeyJ-outside-box /
   Escape / closeForTest) then reopen-via-button-pointer; openPanel-reset law itself fully
   proven, both close routes (button-assisted and Escape). (b) V-4/V-5 one-shots needed
   the `wh-root`/`wh-hud` recorder roots registered (npc buildLabel reads #wh-hud at init)
   — harness-law stub, no engine behavior mocked. (c) V-14 used the full pre-file
   /tmp/qjr2_pre_CONFIG.js (sha-proven == HEAD blob) as the 56-key baseline and the
   reduced /tmp/qjr2_pre_config.json for its recorded journal/quest probe rows.
   (d) V-1 counts the round's own io/specs/*.md untracked docs as documentation, not
   code-census violations (prototype/ untracked = 0 still holds).

## Verdict rationale

All 15 groups PASS on fresh runs at verdict time: V-0 (sha recording), V-0b (11/11
zero-touch), V-1 (28), V-2 (28), V-3 (14), V-4 (22), V-5 (19), V-6 (25), V-7 (34), V-8
(19), V-9 (14), V-10 (12), V-11 (24), V-12 (17), V-13 (deterministic ×2 + all marker
floors), V-14 (14), V-15 (audit + stable re-sha). Zero substantive FAILs. The four
letter-vs-landed deviations are disclosed and adjudicated non-blocking per ADR-1..ADR-4.
NO-GIT held: working tree carries the 5 TOUCHED paths + round docs; HEAD unchanged.

VERDICT: PASS
