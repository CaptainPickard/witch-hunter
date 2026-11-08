# Valspec — CC-PFG1 Open-Air Phase-Fog Rows (Testerbot, BEFORE Devbot)

Round: 2026-11-08 wake 43. Governs Devbot's build; is the basis of the later
independent verdict. Static proofs ONLY — no browser, no game run, no harness
(hard law: PRIMARY law 2 — Nicko's playtest is the acceptance bar; these are
code QA). Repo: /tmp/wh-worldfeat, branch feat/world-visuals. Commands are run
from repo root unless a `cd:` line says otherwise.

Authoritative source: io/specs/cc-pfg1-phase-fog-spec.md (change inventory,
byte-frozen night values, PROPOSED table, A1-A11).

## 0. Law

- Every check is: ID | target file | exact command | expected output | pass
  condition.
- All greps CASE-INSENSITIVE on hex bodies (`grep -i` / `-iE`): the spec's
  lowercase literals are canon, but a same-value different-case hex in
  CONFIG.js is treated as a pass on hex-value law, flagged in the verdict.
- `#` precedes every comment in commands: comments are shell-safe.
# Anchors verified pre-round (Testerbot, this phase): night fog block at
# CONFIG.js:4697-4702, dawn 4712-4717, day 4728-4733, dusk 4743-4748.
# regionG fogColor/fogDensity at 1801-1802; regionH at 1994-1995. Tree clean
# at 163616e.

## 1. Census / proof map: A1..A11 -> exact static checks

### A1 syntax sanity
A1 | prototype/js/CONFIG.js | `node --check prototype/js/CONFIG.js && echo A1PASS` | stdout ends `A1PASS`; exit 0 | no syntax break after data-only additions.

### A2 fog-key census: 5 keys x 4 phase rows = 20
The KEY NAME `forest_of_the_old_king` alone appears 4 times in CONFIG.js
(entry lines); `darkwood_edge` appears 9 lines (4 as `( key: { color:` +
other uses), so key NAMES alone do not enumerate rows. Enumerate rows with
the per-row forest hex VALUE ANCHOR, then count keys within each row block.

Pre-round baseline (must hold — re-check before Devbot runs):
A2b | prototype/js/CONFIG.js | `grep -cE '^ +(hold_outskirts|darkwood_edge|forest_of_the_old_king|lords_hold|fort_garrison): \{ color:' prototype/js/CONFIG.js` | `12` | 3 existing keys x 4 rows, pre-round.

Post-build census:
A2c | prototype/js/CONFIG.js | `grep -cE '^ +(hold_outskirts|darkwood_edge|forest_of_the_old_king|lords_hold|fort_garrison): \{ color:' prototype/js/CONFIG.js` | `20` | 5 keys x 4 phase rows; exactly +8 vs baseline 12.

Per-phase-row split (run all six, the row-attribution block):
A2d | prototype/js/CONFIG.js | `LC=$(grep -c '^ *night: {$' prototype/js/CONFIG.js); ...` | each exit 0 | see valspec expansion below for the exact one-shots.

Run these four value-anchored pairs (each first line proves WHICH row the
forest hex sits in; second line counts the row's 5 entries):

  # night row (forest anchor 0x59625b)
  grep -cF 'forest_of_the_old_king: { color: 0x59625b, density: 0.033 }' js/CONFIG.js   # expect 1
  grep -cE '^ +(hold_outskirts|darkwood_edge|forest_of_the_old_king|lords_hold|fort_garrison): \{ color:' js/CONFIG.js | head -0   # not this way — use the block method below

The block method (the real check) — put the four literals in a loop:
A2-night | prototype/js/CONFIG.js | `awk '/^ +night: \{$/{inr=1;next}/^ +\}/{inr=0}inr&&/^ +(hold_outskirts|darkwood_edge|forest_of_the_old_king|lords_hold|fort_garrison): \{ color:/{c++}END{print c+0}' prototype/js/CONFIG.js` | `5` | night fog block contains exactly 5 keyed entries (forest_of_the_old_king anchor line `forest_of_the_old_king: { color: 0x59625b, density: 0.033` MUST also grep 1 inside this block; verify: `sed -n '4697,4702p' prototype/js/CONFIG.js` shows the 4 keys + the 5th = the new lords_hold/fort_garrison pair).
A2-dawn | prototype/js/CONFIG.js | same awk with `/^ +dawn: \{$/` opener | `5` | dawn row: 5 keys. forest anchor inside dawn block: `forest_of_the_old_king: { color: 0x5f6660, density: 0.030`.
A2-day | prototype/js/CONFIG.js | same awk with `/^ +day: \{$/` opener | `5` | day row: 5 keys. forest anchor: `forest_of_the_old_king: { color: 0x6a716a, density: 0.025`.
A2-dusk | prototype/js/CONFIG.js | same awk with `/^ +dusk: \{$/` opener | `5` | dusk row: 5 keys. forest anchor: `forest_of_the_old_king: { color: 0x5c625c, density: 0.031` (NOTE: 0x5c625c is UNIQUE in CONFIG.js — grep -c 0x5c625c = 1 — this hex alone pins the dusk row; the other three forest hexes are each 1-of-1 within phase rows: 0x59625b also appears at CONFIG.js:634 as regionC's fogColor, so the phase-row attribution MUST use the full key line, not the bare hex).

Byte-anchor double-check per row (each must print exactly 1):
A2-anch | prototype/js/CONFIG.js | `grep -cF 'forest_of_the_old_king: { color: 0x59625b, density: 0.033 }' prototype/js/CONFIG.js` | `1` | night-phase row enumerated (repeat with 0x5f6660/0.030 → dawn, 0x6a716a/0.025 → day, 0x5c625c/0.031 → dusk; each also =1).

### A3 night byte-verbatim (frozen)
A3a | prototype/js/CONFIG.js | `grep -cF 'lords_hold: { color: 0x8a8f96, density: 0.08 }' prototype/js/CONFIG.js` | exactly `1` | byte-verbatim night lords_hold entry.
A3b | prototype/js/CONFIG.js | `grep -cF 'fort_garrison: { color: 0x7d8289, density: 0.068 }' prototype/js/CONFIG.js` | exactly `1` | byte-verbatim night fort_garrison entry.
A3c | prototype/js/CONFIG.js | `grep -c 'fogColor: 0x8a8f96' prototype/js/CONFIG.js` | `1` | regionG fogColor row untouched.
A3d | prototype/js/CONFIG.js | `grep -c 'fogColor: 0x7d8289' prototype/js/CONFIG.js` | `1` | regionH fogColor row untouched.
A3e | prototype/js/CONFIG.js | `grep -c 'fogDensity: 0.08$' prototype/js/CONFIG.js; grep -c 'fogDensity: 0.068$' prototype/js/CONFIG.js` | `1` and `1` | region-row densities (with trailing comma) intact; NOTE trailing-comma law: region rows end `0.08,` and `0.068,`; phase entries end `}` no comma.

### A4 PROPOSED value check (dawn / day / dusk)
All six greps exact-literal, same-line, case-insensitive, each = 1. Pre-round
baseline for ALL SIX currently prints 0 (Testerbot verified) — so each is a
pure addition proof.

  # dawn
A4a | prototype/js/CONFIG.js | `grep -ciE '^ +lords_hold: \{ color: 0x9c9184, density: 0\.068 \},$' prototype/js/CONFIG.js` | `1` | dawn lords_hold.
A4b | prototype/js/CONFIG.js | `grep -ciE '^ +fort_garrison: \{ color: 0x8b827a, density: 0\.058 \}$' prototype/js/CONFIG.js` | `1` | dawn fort_garrison.
  # day
A4c | prototype/js/CONFIG.js | `grep -ciE '^ +lords_hold: \{ color: 0xa2a8ab, density: 0\.045 \},$' prototype/js/CONFIG.js` | `1` | day lords_hold.
A4d | prototype/js/CONFIG.js | `grep -ciE '^ +fort_garrison: \{ color: 0x9aa0a3, density: 0\.038 \}$' prototype/js/CONFIG.js` | `1` | day fort_garrison.
  # dusk
A4e | prototype/js/CONFIG.js | `grep -ciE '^ +lords_hold: \{ color: 0x84807a, density: 0\.088 \},$' prototype/js/CONFIG.js` | `1` | dusk lords_hold.
A4f | prototype/js/CONFIG.js | `grep -ciE '^ +fort_garrison: \{ color: 0x78736c, density: 0\.076 \}$' prototype/js/CONFIG.js` | `1` | dusk fort_garrison.

A4g | prototype/js/CONFIG.js | `grep -ciE 'lords_hold.*cemColor|cemColor.*lords_hold|fort_garrison.*cemColor|cemColor.*fort_garrison' prototype/js/CONFIG.js` | `0` | G/H entries carry NO cemColor/cemDensity (copyRow gates hasCem on cemColor presence, daynight.js:58-60 — a stray cem key would make hasCem flip).

### A5 diff shape (config)
A5 | prototype/js/CONFIG.js | `git diff --stat prototype/js/CONFIG.js` | `8 insertions` data + `1 insertion` marker comment; net `+9` lines | exactly 8 new fog-entry lines + the 1 mandated CC-PFG1 comment line, nothing else.

### A6 no engine diff
A6 | game.js, daynight.js, region-defs.js, save.js | `git diff --name-only | grep -E 'prototype/js/(game|daynight|region-defs|save)\.js' | wc -l` | `0` | none of the four engine files diff (applyDayNight already reads any fog key — game.js:1962-1966; copyRow/lerpRow iterate row.fog — daynight.js:57-60, 78-84).

### A7 all-loadable sanity
A7 | all four engine files | `for f in prototype/js/CONFIG.js prototype/js/game.js prototype/js/daynight.js prototype/js/region-defs.js prototype/js/save.js; do node --check $f || echo FAIL $f; done` | no FAIL lines; exit 0 | all five parse; A1 not a one-off.

### A8 registry edit confined to G/H rows
A8a | docs/planning/64-region-registry.md | `git diff docs/planning/64-region-registry.md | grep -cE '^\+|^-' | head -1` (or git diff --stat) | exactly 2 changed row lines (the H1 live table row at line 87 — the G/Lord's Hold row — and the H2 fort_garrison row at line 88); net line-count delta 0; NO other table row (any line whose row ID is NOT H1 or H2) appears in the diff body.
A8b | docs/planning/64-region-registry.md | `git diff docs/planning/64-region-registry.md | wc -l` | < 60 total diff lines | tight edit.

### A9 determinism: BUILD IS IO-OWNED post-commit; verdict runs NO builds
A9 | (none — verdict-time note) | NO build command runs at verdict phase | build_v8 double-run sha256-identical is IO's post-commit proof, disclosed in the IO build summary | verdict phase records `VALSPEC-A9: build proof deferred to IO post-commit`; Testerbot NEVER runs build_v8 itself.

### A10 marker
A10a | prototype/js/CONFIG.js (verdict phase) | `grep -n 'CC-PFG1 phase-fog rows' prototype/js/CONFIG.js` | `>= 1` hit at exactly ONE line, immediately above the night row's lords_hold entry | marker comment byte-law.
A10b | prototype/builds/v8-playable.html (verdict phase) | `grep -c 'CC-PFG1' prototype/builds/v8-playable.html` | `>= 1` | NOTE: runs at verdict phase only, AFTER IO's post-commit build; pre-round baseline grep of the CURRENT v8-playable.html = 0 (Testerbot verified). A10's bundle branch (comments do carry: the C2 comment rows already ride into the bundle, 4 hits of `Region C deep-forest fog (night = CONFIG.regionC verbatim)` in v8 today) — so the bundle check should pass; if it fails, fall back to the game.js comment branch per IO spec A10 and disclose in the verdict.

### A11 registry note text
A11 | docs/planning/64-region-registry.md | `git diff docs/planning/64-region-registry.md | grep -c 'phase-fog rows'` | `>= 1` line in the diff ADDED body, AND the full mechanism note per spec A11 rides the same added row-text block: keyed per-region fog per phase, applyDayNight per-frame writer for keyed regions, freeze gap closed, night = region fogColor/fogDensity verbatim, dormant night bit-identical.

### Change-file allowlist
A12 | whole repo | `git diff --name-only | grep -v -E '(prototype/js/CONFIG\.js|docs/planning/64-region-registry\.md)' | wc -l` | `0` ONLY if the diff is empty besides those two; with A10b's game.js fallback fired, expect `game.js` here and RE-CLASSIFY as A10-disclosed, not a violation. Baseline `git diff --name-only | wc -l` pre-round = 0 (clean tree, verified).

## 2. Pre-round census table (all Testerbot-verified at 163616e)

| anchor | value | count today | means |
|---|---|---|---|
| `forest_of_the_old_king: { color: 0x59625b, density: 0.033 }` (F) | exact line | 1 | night phase fog entry exists now |
| `forest_of_the_old_king: { color: 0x5f6660, density: 0.030 }` (F) | exact line | 1 | dawn phase fog entry exists now |
| `forest_of_the_old_king: { color: 0x6a716a, density: 0.025 }` (F) | exact line | 1 | day phase fog entry exists now |
| `forest_of_the_old_king: { color: 0x5c625c, density: 0.031 }` (F) | exact line | 1 | dusk phase fog entry exists now |
| `lords_hold: { color: 0x8a8f96, density: 0.08 }` | 0 matches | — | A3 target absent pre-round |
| `fort_garrison: { color: 0x7d8289, density: 0.068 }` | 0 matches | — | A3 target absent pre-round |
| PROPOSED hexes 0x9c9184/0x8b827a/0xa2a8ab/0x84807a/0x78736c | 0 matches each | — | all six A4 greps start clean |
| `0x9aa0a3` | 2 matches | 187 (regionF fogColor) + 4698 (night hold_outskirts) | A4d's new fort_garrison 0x9aa0a3 must NOT collide — anchor grep is KEY+VALUE line not bare hex |
| `0x84807a` | 0 | — | A4e dusk lords_hold pure-new |
| `0x78736c` | 0 | — | A4f dusk fort_garrison pure-new |
| `fogColor: 0x8a8f96` | 1 | — | regionG row |
| `fogColor: 0x7d8289` | 1 | — | regionH row |
| `CC-PFG1` in CONFIG.js | 0 | — | A10a is a pure addition |
| `phase-fog rows` in registry doc | 0 | — | A11 is a pure addition |
| `CC-PFG1` in v8-playable.html | 0 today (pre-commit, unrebuilt) | — | A10b runs only post-commit |

VALSPEC-FIX (IO, post-build, Devbot deviation 1 adopted): A4a/A4c/A4e line-anchor now ends "\},$" — the lords_hold entries carry the mandated trailing comma (first of each pair); the original "\}$" form was comma-blind and printed 0 on the built tree. Confirmed by IO diff inspection.

## 3. Ambiguities found + resolutions baked in

1. The IO spec's census wording ("each of the four phase rows' fog object
   contains EXACTLY the 5 keys") is ambiguous about HOW to attribute an entry
   line to its parent row (grep -c on a key name counts ALL rows at once).
   RESOLUTION: use the four forest_of_the_old_king VALUE ANCHORS to pin rows
   (each pins its phase row 1:1 via the byte-exact `key+hex+density` line);
   the awk block-counter in A2-night/-dawn/-day/-dusk is the enforcement
   check; a bare-key-name grep is rejected as census evidence.

2. Row-attribution caveat: 0x59625b appears TWICE in CONFIG.js (once at
   line 634 as regionC's own fogColor, once at 4701 in the night phase row).
   Bare-hex greps would over-match; the full key-line form
   `forest_of_the_old_king: { color: 0x59625b, density: 0.033 }` is the
   unique attribution (grep -F = exactly 1). RESOLUTION baked into A2-anch.

3. `0x9a` collision: 0x9aa0a3 appears twice today (regionF fogColor at 187;
   night hold_outskirts at 4698). Bare-hex grep for the day fort_garrison
   value would read 2 today and 3 after. RESOLUTION: A4d greps the FULL
   key-paired line, never the bare hex. Same defense for A4e's 0x84807a and
   A4f's 0x78736c (currently 0-of-1 but enforced line-form anyway for
   symmetry).

4. Densities 0.08 / 0.068 in the NIGHT phase entry vs the REGION rows: both
   carry these numbers, so bare-density greps over-match. RESOLUTION:
   A3e uses `$`-anchored line form (region rows end `0.08,` with comma;
   phase entries end `0.08 }` brace-terminated) — the exact-line form is
   what the spec intends.

5. A2's census count: 20 = 5 keys x 4 rows. But hold_outskirts/darkwood_edge
   appear 9 lines (4 = the phase-row entries; 1 = save.js/region-defs.js
   other uses), so key-name-only grep would read 9. RESOLUTION: A2's
   post-build census = 20 via the FULL entry-line grep (enforced as
   `^ +KEY: { color:` — which counts ONLY fog-entry lines), with the
   per-row awk block counter A2-night/-dawn/-day/-dusk as the primary proof.

6. A10's bundle branch is UNRESOLVED pre-commit (build hasn't run). Today's
   bundle already carries C2/C8 comment strings (4 + 51 hits), so the
   expected-post-commit outcome is >= 1 hit. RESOLUTION baked in: A10b is
   marked verdict-phase-only; the fallback branch (game.js comment) is
   A12's re-classified exception and NOT a spec violation.

## 4. Verdict-time runbook (Devbot build done; no code edits by Testerbot)
1. Run every check in section 1 in order (A1, A2b/A2c, A2-night/-dawn/-day/-
   dusk, A2-anch x4, A3a-e, A4a-g, A5, A6, A7, A8a-b, A10a-b, A11, A12).
2. A9's line: no builds; note the sha256 determinism claim must come from
   IO's post-commit build summary.
3. Collate into io/reports/cc-pfg1 verdict file: one line per check ID -
   PASS/FAIL, plus any A10/A12-disclosed deviations.

-- end valspec cc-pfg1 --
