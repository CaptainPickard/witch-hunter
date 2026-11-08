# CC-LS2 — Loader Surface Integrity (resolveUrl prototype/ strip) — VALSPEC (Testerbot, autopilot wake 38)

- Parent spec: `io/specs/cc-ls2-loader-surface-spec.md`, FROZEN by IO 2026-11-08.
  - PREFLIGHT: sha256(io/specs/cc-ls2-loader-surface-spec.md) = `2836d48cae49f1370c700b217b797b91aa81fe006db89634e328fd53191705f5`. If this changes after valspec write, abort and re-read.
- Worktree /tmp/wh-worldfeat, branch feat/world-visuals, HEAD `b006d5687c6b8d82467bc815b2890e002db1c71` (b006d56). All line anchors below are measured at valspec write against b006d56; if lines drifted when you validate, re-locate the named anchors, never hard-require stale numbers.
- NO-GIT: no commit, no push, no stash-drop, no config change by Devbot or Testerbot. Read-only `git log/show/diff/status/rev-parse` allowed for both. Valspec write itself touched no tracked file (this file and evidence live untracked under io/specs/ + scratch/cc-ls2-val/).
- Gate order stands: this valspec → Devbot build → independent Testerbot verdict.
- Runlaw: boot-check tool ONLY (RUNBOOK BOOT-CHECK LAW: no playtest simulation, no harness game-session smoke, no per-frame runtime).

## PRE-FIX EVIDENCE (A4) — captured BEFORE this valspec's fix-dependents may be trusted

- Canonical: `/tmp/wh-worldfeat/io/specs/cc-ls2-prefix-evidence.txt`
- Raw console log: `/tmp/wh-worldfeat/scratch/cc-ls2-val/prefix-boot-1.log` (449 lines)
- Repro harness: `/tmp/wh_pwtest/cc_ls2_boot.js` (playwright-core 1.65.0, chrome-headless-shell-1243, `--no-sandbox`)
- Repro boot: UNFIXED `prototype/builds/v8-playable.html` (HEAD bundle at b006d56, built stamp `410cc81`), loaded from a PLAIN static serve of the repo root: `python3 -m http.server 8801 --bind 127.0.0.1` (cwd /tmp/wh-worldfeat) → `http://127.0.0.1:8801/prototype/builds/v8-playable.html`.
- Measured result (2026-11-08T01:22Z, HEAD b006d56, assets.js resolveUrl at lines 219-231 with NO prototype strip):
  - `boot barrier: 51 critical assets settled (51 stand-ins); streaming 29 more`
  - `loaded 0 assets, 80 stand-ins`
  - exactly 80 lines `[WH assets] substitution: procedural stand-in for <name>` (one per manifest entry), 0 assets loaded
  - 243 HTTP 4xx/failed responses; all misdirected fetches hit `/prototype/art-direction/...` (e.g. `404 http://127.0.0.1:8801/prototype/art-direction/3d/assets/weapons/dagger-curved-pixelated.glb`)
  - pageerrors = 0 (the bug is silent-fatal to art, not to JS)
- Quirk-mask control (same unfixed worktree): server.py serve on 8794/8802 returns `200` for `prototype/art-direction/...` (translate_path strips the leading `prototype/` segment) — which is why boots from the quirk serve look clean and the bug regressed silently. Plain-serve 404 on `prototype/art-direction/...` is the unmasked failure signature.

## SPEC DEFECTS CAUGHT (resolved HERE; spec file NOT edited)

- D1 (A3 token "loaded N assets"): measured at valspec write — MANIFEST = 80 entries, CONFIG `bootCritical` = 51 (CONFIG.js:3766-3778), DEFERRED = 29, and the settled-stream line at b006d56 on a healthy boot reads exactly `loaded 80 assets, 0 stand-ins` (per 410cc81 commit message census). V-3 hard-requires N=80.
- D2 (A5 "prototype/-prefixed sibling returns 200"): as of valspec write, `http://172.16.5.1:8793/current/prototype/art-direction/3d/assets/weapons/dagger-curved-pixelated.glb` returns 404 on the CURRENT release (no `prototype/art-direction` in git; the 8793 server is a plain http.server, no quirk). A5 is IO-only; IO owns making that curl pass (however IO's flip lands it) — Devbot and this valspec's V-1..V-4 are NOT blocked by it.
- None of D1-D2 blocks the build.

## V-1 (spec A1) — exactly-one-line diff scope in prototype/js/assets.js

PASS requires all of:

1. `git -C /tmp/wh-worldfeat diff HEAD -- prototype/js/assets.js` present; the added code lines (non-comment) are EXACTLY ONE, and it matches byte-for-byte the frozen seam line:
   `        pageDir = pageDir.replace(/\/prototype\/$/, '/');`
   (8-space indent: inside resolveUrl's `if (/\/builds\//.test(pageDir)) { ... }` block at today's lines 223-225; allow a comment line `+`-adjacent per A1 "(+ comment)".)
2. `git -C /tmp/wh-worldfeat status --short` shows NO other tracked source file modified except `prototype/js/assets.js` and `prototype/builds/v8-playable.html`. Untracked `io/specs/*` and `scratch/*` are permitted (valspec/evidence).
3. No pre-existing line deleted or modified: `git diff -U0 HEAD -- prototype/js/assets.js | grep -E '^-[^-]'` yields only comment/whitespace lines, if any.
4. `node --check /tmp/wh-worldfeat/prototype/js/assets.js` exits 0.
5. The line sits inside `function resolveUrl(relPath)` (locate by grep, not line number) and AFTER the existing `/builds/` strip.

FAIL if: any second behavior line changed, any file under prototype/js/ other than assets.js differs, or a manifest path was touched.

## V-2 (spec A2) — rebuild via tools/build_v8.py; rebuilt bundle contains the new resolver line

PASS requires all of:

1. `cd /tmp/wh-worldfeat && python3 tools/build_v8.py` exits 0 and prints `wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html <bytes> bytes`. (The build tool is the build's tool — running it is not a git op; deterministic-law stamp keeps same-HEAD rebuilds byte-identical in the unchanged regions.)
2. The rebuilt `prototype/builds/v8-playable.html` contains the new resolver line EXACTLY once: `grep -c 'pageDir\.replace(/\\/prototype\/\$\/, '"'"'\/'"'"')' prototype/builds/v8-playable.html` = 1.
3. The line is adjacent to the pre-existing strip in the inlined copy: `grep -n -A1 'pageDir = pageDir.replace(/\\/builds\\/' prototype/builds/v8-playable.html` shows the prototype strip as the next non-blank code line.
4. HEAD bundle sha256 (no-fix reference) = `856d42f4bb00621877bf797f20f9dc1cc1a08edf2da2453843098e4cf8a3c471`; after the fix + rebuild the bundle sha changes (record new sha). A rebuild that does NOT change the bundle means assets.js wasn't saved before building — FAIL.

FAIL if: build errors, bundle unchanged, line count ≠ 1, or line appears outside the inlined assets.js block.

## V-3 (spec A3) — boot-checks: 0 pageerrors, barrier settled, 0 stand-ins on BOTH surfaces

Harness (exists, edit-free for reuse): `cd /tmp/wh_pwtest && node cc_ls2_boot.js <URL> > <log> 2>&1`. It prints one `CONSOLE:` line per interesting message, `NET:` lines for HTTP >= 400 / failures, then `FINAL pageerrors=N` and `BADCOUNT=N`, and waits 55s so deferred streaming completes. Serves (ports are free 88xx band; 8791/8793/8794 and capture-serves 8801/8802 are taken):

- **A3a serve (unmasked, bug-exercising):** `cd /tmp/wh-worldfeat && python3 -m http.server 8810 --bind 127.0.0.1` (plain static, repo root). PRE-BOOT SANITY (must hold, else the serve is wrong): `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8810/prototype/art-direction/3d/assets/weapons/dagger-curved-pixelated.glb` = **404**, and the unprefixed sibling `http://127.0.0.1:8810/art-direction/3d/assets/weapons/dagger-curved-pixelated.glb` = **200**. Boot `http://127.0.0.1:8810/prototype/builds/v8-playable.html` (page URL literally contains `/prototype/`).
- **A3b serve (quirk-style, unchanged-path sanity):** `cd /tmp/wh-worldfeat/prototype && python3 server.py 8811` (same shape as the standing 8794 repro server). Boot `http://127.0.0.1:8811/builds/v8-playable.html` — pageDir has NO `prototype/` segment; this is the old-masked path that must not regress.

PASS requires ALL of the following for EACH of the two boots (logs → `scratch/cc-ls2-val/val-boot-a.log` and `val-boot-b.log`):

1. `FINAL pageerrors=0` in the log.
2. Barrier line present and clean: `grep -E '^CONSOLE: \[WH assets\] boot barrier: 51 critical assets settled \(0 stand-ins\)' <log>` = exactly 1 line.
3. Final stream line clean: `grep -E '^CONSOLE: \[WH assets\] loaded 80 assets, 0 stand-ins' <log>` = exactly 1 line (D1: N=80 fixed by census).
4. Zero stand-in machinery: `grep -c '\[WH ASSETS\] STAND-IN:'` = 0 AND `grep -c 'substitution: procedural stand-in'` = 0.
5. `BADCOUNT=0` — zero responses with status 400-599 or failed requests across the whole boot (this is what fails pre-fix: BADCOUNT=243).
6. At least one GLB fetch visibly hits the correct base: log contains NET-free evidence via barrier lines only (BADCOUNT=0 implies fetches went to `/art-direction/...` and got 200; A3a's URL set differs from pre-fix's `/prototype/art-direction/...` — spot-check by adding `page.on('response')` output only if you need the positive list).

FAIL if any boot misses a line, shows stand-ins, pageerrors, or BADCOUNT > 0 on either surface. A3a failure with A3b pass means the prototype/ strip is wrong; A3b failure means the fix overmatched a pageDir that never carried `prototype/`.

## V-4 (spec A4) — pre-fix failing evidence exists (captured BEFORE the fix)

PASS requires all of (read-only; no re-boot of unfixed sources — the worktree must carry the fix when you validate):

1. `/tmp/wh-worldfeat/io/specs/cc-ls2-prefix-evidence.txt` exists and contains: the barrier line with `(51 stand-ins)`, the stream line `loaded 0 assets, 80 stand-ins`, at least 80 stand-in substitution lines, at least one `NET: 404 .../prototype/art-direction/...` line, and the capture header naming HEAD b006d56 and the plain repo-root serve on 8801.
2. Raw log `scratch/cc-ls2-val/prefix-boot-1.log` exists and reproduces the same greps (it is the primary capture; the evidence .txt is its curated view).
3. The harness `/tmp/wh_pwtest/cc_ls2_boot.js` exists and matches the boot used in V-3 (same tool, same settle behavior) — proving the passing/failing line is the FIX, not a harness change.
4. Evidence proves the V-3 test CAN fail: the failure signature (`51 stand-ins` / `BADCOUNT>0` / stand-in substitution spam) is exactly what V-3 forbids.

## V-5 (spec A5) — IO-ONLY, post-gate. Marked: IO executes this; Devbot must not; Testerbot does NOT validate-execute

Restatement of frozen A5 for the record (single commit naming CC-LS2 + surfaces → rebuild → commit build → `wh_release_flip.py <sha>` via dhost CLI on 8793 → `curl 200` + 0-stand-ins boot on `http://172.16.5.1:8793/current/prototype/builds/v8-playable.html` → GLB URL `http://172.16.5.1:8793/current/art-direction/3d/assets/weapons/dagger-curved-pixelated.glb` and its `prototype/`-prefixed sibling both 200). See SPEC DEFECT D2 for today's observed sibling 404 — resolution is IO's. Children NEVER push or flip. If a Testerbot verdict is requested while any V-1..V-4 item is unpassable, FAIL the verdict and name the failing item(s) — do not wait on V-5.

## Verdict sheet (fill in the independent Testerbot run)

- [ ] V-1 one-line diff scope: PASS/FAIL (diff stat + the matched line quoted)
- [ ] V-2 rebuild + bundle line: PASS/FAIL (build output + grep count + old/new sha256)
- [ ] V-3a boot unmasked serve: PASS/FAIL (pageerrors / barrier / stream / BADCOUNT)
- [ ] V-3b boot quirk serve: PASS/FAIL (same four numbers)
- [ ] V-4 pre-fix evidence: PASS/FAIL (greps against io/specs/cc-ls2-prefix-evidence.txt)
- [ ] V-5: N/A-Testerbot (IO post-gate)
