# CC-LS2 — Loader Surface Integrity: resolveUrl collapses prototype/ page-dir (SPEC, frozen)

Status: FROZEN 2026-11-08 (IO, autopilot wake 38)
Author seat: Devbot. Validator seat: Testerbot (independent). Children NEVER push.

## Problem (root cause, verified by IO this wake)

`resolveUrl()` in `prototype/js/assets.js` (lines ~218-230) resolves manifest+sky
paths against `document.baseURI`, stripping only a trailing `/builds/`. On every
serving surface where the page lives under a `prototype/` URL directory, art
URLs resolve to `.../prototype/art-direction/...`. `prototype/art-direction`
does NOT exist in git (verified: `git ls-tree origin/feat/world-visuals
prototype/` has no art entry). Consequences per surface:

- 8793 atomic-release surface (`/current/prototype/builds/v8-playable.html`):
  every GLB 404s -> ALL props/characters/skies render as procedural stand-ins.
  (server.py's translate_path quirk masks the bug on quirk-served roots, which
  is why local boots look fine and why this regressed silently.)
- WebUI button bundle page (`/playtest-feat/prototype/builds/v8-playable.html`):
  same 404s -> same stand-ins.
- WebUI button main page (`/playtest-feat/`) and quirk-served roots: unaffected
  (pageDir already has no `prototype/` segment) — must stay unaffected.

## Required change (single seam)

In `prototype/js/assets.js`, inside `resolveUrl()`, immediately after the
existing `/builds/` strip, add the analogous strip of a trailing `prototype`
page-dir segment:

    pageDir = pageDir.replace(/\/prototype\/$/, '/');

Nothing else changes: manifest paths, `new URL` usage, daynight/ember loaders
(they all ride the same `WH_ASSETS.resolveUrl`), build tooling.

## Acceptance criteria (each independently verifiable)

A1. `prototype/js/assets.js` changed by exactly the one line above (+ comment).
    No other source file diff in the commit.
A2. Rebuild: `python3 tools/build_v8.py` run from repo root succeeds; the
    rebuilt `prototype/builds/v8-playable.html` contains the new line.
A3. Boot-check (playwright-core, headless, the RUNBOOK BOOT-CHECK LAW tool):
    against the REBUILT bundle served so `prototype/art-direction/...` URLs
    were previously 404 — verify console shows the boot barrier "51 critical
    assets settled (0 stand-ins)", "loaded N assets, 0 stand-ins", and 0
    pageerrors. Do this for BOTH surfaces:
      A3a. serve of the repo root (any static server) loading
           /prototype/builds/v8-playable.html
      A3b. the quirk-style serve unchanged sanity: loading
           /builds/v8-playable.html from a serve rooted at prototype/ still
           boots with 0 stand-ins (no regression on the old-masked path).
A4. Pre-fix reproduction evidence (MUST be captured BEFORE the fix lands, or
    from the pre-fix HEAD checkout): the same boot-check against UNFIXED
    sources shows GLB 404s / stand-in warnings, proving the test can fail.
A5. IO-only post-gate: commit fix (single commit, message names CC-LS2 +
    surfaces), rebuild, commit build, flip 8793 (wh_release_flip.py via dhost
    CLI), verify `curl` 200 AND 0-stand-ins boot on
    `http://172.16.5.1:8793/current/prototype/builds/v8-playable.html`, and
    verify a GLB URL (`/current/art-direction/3d/assets/weapons/
    dagger-curved-pixelated.glb`) and its `prototype/`-prefixed sibling both
    return 200. Children do NOT push or flip.

## Constraints

- Gate order stands: Testerbot valspec FIRST (before Devbot build), then build,
  then independent Testerbot verdict.
- No harness runs beyond the boot-check tool (RUNBOOK LAW: boot-check is
  allowed; no playtest simulation, no headless game-session smoke).
- One unit: no feature work rides this commit.
