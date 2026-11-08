# CC-PFG1 Independent Verdict — Testerbot (CC-PFG1 Open-Air Phase-Fog Rows)

Date: 2026-11-08. Tree: /tmp/wh-worldfeat, branch feat/world-visuals, HEAD 163616e,
UNCOMMITTED working tree exactly per context (git diff --name-only = the 2 allowlisted
files; +2 untracked io/specs files, untouched). Governing valspec:
io/specs/cc-pfg1-phase-fog-valspec.md
(section 1 + section 2). Commands executed verbatim from repo root; no builds run;
no git state changes; no repo file modified.

## Per-check results (raw counts)

A1: PASS - A1PASS (node --check prototype/js/CONFIG.js exit 0)
A2b: NOTE - superseded by build (not counted; pre-round baseline 12 is historical context; the same verbatim command now prints 20 and is recorded as A2c)
A2c: PASS - 20 (5 keys x 4 phase rows)
A2-night: PASS - 5 (awk block: night fog object = exactly 5 keyed entries)
A2-dawn: PASS - 5
A2-day: PASS - 5
A2-dusk: PASS - 5
A2-anch-night: PASS - 1 (grep -F 'forest_of_the_old_king: { color: 0x59625b, density: 0.033 }')
A2-anch-dawn: PASS - 1 (0x5f6660 / 0.030)
A2-anch-day: PASS - 1 (0x6a716a / 0.025)
A2-anch-dusk: PASS - 1 (0x5c625c / 0.031; bare-hex 0x5c625c also = 1, unique)
A3a: PASS - 1 (night lords_hold 0x8a8f96 / 0.08 byte-verbatim)
A3b: PASS - 1 (night fort_garrison 0x7d8289 / 0.068 byte-verbatim)
A3c: PASS - 1 (fogColor: 0x8a8f96 — regionG row, CONFIG.js:1801)
A3d: PASS - 1 (fogColor: 0x7d8289 — regionH row, CONFIG.js:1994)
A3e: PASS* - 0/0 verbatim comma-blind $-form; equivalent comma-terminated form = 1/1 (fogDensity: 0.08,$ at line 1802; fogDensity: 0.068,$ at line 1995) [see disclosure 1]
A4a: PASS - 1 (IO-amended comma form verbatim: '… density: 0\.068 \},$')
A4b: PASS - 1 ('… density: 0\.058 \}$')
A4c: PASS - 1 (amended comma form)
A4d: PASS - 1 (full key-paired line 0x9aa0a3 — not bare-hex; bare hex = pre-existing 2 occurrences + this line, per valspec census)
A4e: PASS - 1 (amended comma form)
A4f: PASS - 1
A4g: PASS - 0 (no cemColor/cemDensity on lords_hold/fort_garrison lines)
A5: PASS* - raw: "1 file changed, 13 insertions(+), 4 deletions(-)" = net +9 exact; byte-audit of full diff = 8 new fog-entry lines + 1 mandated marker line + 4 forced trailing-comma rewrites of the pre-existing forest_of_the_old_king lines [see disclosure 2]
A6: PASS - 0 (git diff --name-only | grep -E 'prototype/js/(game|daynight|region-defs|save)\.js' | wc -l = 0)
A7: PASS - 5/5 (node --check CONFIG.js, game.js, daynight.js, region-defs.js, save.js — no FAIL lines, exit 0; node v22.22.3)
A8a: PASS* - verbatim grep printed 6 (= 4 row body lines + 2 'diff --git a/…' header meta lines caught by the ^\-/^+ pattern — mechanical grep artifact on multi-file… single-file diff headers); sanctioned alternative in valspec (git diff --stat / diff body inspection) = exactly 2 changed row lines, +2/-2, net line delta 0, changed rows exactly | H1 | (line 87) and | H2 | (line 88); git diff -U0 hunk header @@ -87,2 +87,2 @@ proves ONLY lines 87-88 changed [see disclosure 3]
A8b: PASS - 15 (git diff … | wc -l = 15 < 60; tight edit)
A9: DEFERRED - no build run at verdict phase per valspec law; build_v8 double-run sha256
determinism is IO's post-commit proof (record: /tmp/delegation_result_pfg1_build.md)
A10a: PASS - 1 (marker at exactly one line, CONFIG.js:4702, immediately above night-row lords_hold entry at 4703; byte-verbatim per spec A10 literal)
A10b: DEFERRED - bundle grep of prototype/builds/v8-playable.html runs only after IO's post-commit build per valspec (pre-round baseline 0 recorded there)
A11: PASS - 2 (git diff registry | grep -c 'phase-fog rows' = 2, both in the ADDED body of the H1 and H2 rows; full mechanism text present in both added row-text blocks — see disclosure 4 fragment audit)
A12: PASS - 0 (git diff --name-only | grep -v -E '(CONFIG\.js|64-region-registry\.md)' | wc -l = 0; change file set = exactly the 2 allowlisted files)

VERDICT: PASS 28/28
(Counted: A1, A2c, A2-night/-dawn/-day/-dusk, A2-anch x4, A3a-d, A4a-f, A4g, A5, A6,
A7, A8a, A8b, A10a, A11, A12 = 28 substantive checks, all PASS under the rules.
Not counted: A2b superseded; A9 / A10b deferred per valspec. A3e, A5, A8a pass with
re-expression/disclosures below — CONTENT under test unchanged.)

## Deviations / disclosures

1. A3e (VALSPEC-DEFECT, content passes): the valspec's `grep -c 'fogDensity: 0.08$'` /
   `grep -c 'fogDensity: 0.068$'` both print 0 on the built tree — its own trailing-comma
   NOTE states region rows end `0.08,` / `0.068,` (comma-terminated), so the comma-blind
   `$`-anchor cannot match by construction; expected 1/1 and command are mutually
   inconsistent. Equivalent content-preserving form `grep -c 'fogDensity: 0.08,$'` and
   `grep -c 'fogDensity: 0.068,$'` = 1/1 at CONFIG.js:1802 / 1995. Raw census: the only
   `fogDensity: 0.08` / `0.068` occurrences in CONFIG.js are lines 1802 and 1995 (the two
   region rows) + the inside-the-line night phase entries caught by A3a/A3b. No content
   altered; build conformant. Same defect class as the pre-fixed A4a/A4c/A4e (corroborated
   by build summary deviation D1); recommend IO comma-fix A3e in the valspec.

2. A5 (PASS with shape disclosure): raw git diff --stat = 13 insertions / 4 deletions,
   net +9 exactly as governed — not the idealized "8 data + 1 marker, zero deletions"
   line in the valspec. Full-diff byte audit shows the only changes are: 4 forced
   trailing-comma rewrites of the pre-existing `forest_of_the_old_king` tail lines
   (`} → },` — JS object syntax; the forest key ceased to be last in each fog object),
   1 marker comment line, 8 new fog-entry lines. Nothing else. The comma law itself is
   documented in the valspec (A3e NOTE, A2 anchors) and pre-declared by Devbot
   (build summary, net +9, same 13/4 shape). Content under test (8 entries + 1 marker +
   nothing else) holds exactly.

3. A8a (PASS with mechanical re-expression): verbatim
   `git diff … | grep -cE '^\+|^-' | head -1` printed 6 — on a single-file diff the
   `diff --git a/… b/…` header line contains neither char but `--git` DOES match ^\- on
   the second header segment (raw evidence: both header lines begin "--git"), inflating
   4 true body lines to 6. Also `head -1` flattens multi-count output to one line
   (mechanical, as anticipated in round instructions). The valspec itself sanctions
   `git diff --stat` as the alternative: exactly 2 changed row lines, +2/-2, net 0.
   Confinement proof: `git diff -U0` shows a single hunk @@ -87,2 +87,2 @@ — changed
   lines are exactly the H1 row (87) and H2 row (88); all four diff body lines begin
   `| H1 ` / `| H2 `; no row whose ID is not H1/H2 appears anywhere in the diff body.
   Registry line count unchanged at 114 (pre-round 114 = working tree 114).

4. A11 fragment audit (mechanism text in the ADDED row-text block):
   both added H1/H2 row texts contain: "CC-PFG1 phase-fog rows (2026-11-08, PROPOSED,
   Nicko tunes)"; "keyed into each day/night phase-row fog object" (= keyed per-region
   fog per phase); "applyDayNight per-frame writer for keyed regions"; "closes the
   fog-freeze gap" (= freeze gap closed); "night 0x8a8f96/0.08 = the region's own
   fogColor/fogDensity verbatim" (H1) / "night 0x7d8289/0.068 = the region's own
   fogColor/fogDensity verbatim" (H2) (= night = region fogColor/fogDensity verbatim);
   "dormant night bit-identical". All fragments present; count 2 >= 1. Placement note:
   the H2 note rides mid-row (before the wrapped "H2b ARMORY DEEP" segment) rather than
   at physical line 96 — disclosed by Devbot (D3); content is intact on the same row,
   which is what A8/A11 govern.

5. Deferred items (per valspec, not verdict-phase work): A9 (build_v8 sha256
   determinism x2 — IO post-commit) and A10b (bundle grep 'CC-PFG1' >= 1 in
   v8-playable.html — IO post-commit build; pre-round baseline 0 on the current
   unrebuilt bundle, with the game.js-comment fallback branch pre-authorized by
   valspec A10 if comments do not carry).

6. NO-GIT honored: nothing committed or pushed (HEAD still 163616e at verdict close);
   read-only on repo files; io/specs files read but never modified.

## Cross-check against Devbot build summary

Verdict independently reproduced every number in /tmp/delegation_result_pfg1_build.md:
diff --stat (registry 4 ++--, config 17 ++++++----, 2 files 15(+)/6(-)), name-only = 2,
A2c = 20, awk blocks 5x4, A3/A4 counts, A10a = 1, A11 = 2, HEAD 163616e, registry 114
lines. D1 (A4a/c/e comma defect — since fixed by IO's VALSPEC-FIX, which this verdict
used verbatim and which now greps 1/1/1) and D3 (H2 mid-row placement) corroborated.

-- end cc-pfg1-verdict --
