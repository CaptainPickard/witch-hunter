# Astrabot Mission Brief - grey stand-in box on playtest (2026-10-03)

Nicko order: diagnose + fix. NO automated harness runs - his playtest is the
acceptance bar. One change order at a time; commit to feat/world-visuals IN
THE WORKTREE at /tmp/wh-worldfeat. Do NOT touch /workspace/witch-hunter (dev
checkout) or any other branch. No new design docs; edit this file with your
findings section only.

## Symptom
Nicko plays via the WebUI side-menu Playtest button (route /playtest-feat/ on
the 8787 webui, permissive-CSP) and/or direct http://localhost:8793/ through
the Tailscale tunnel. Reported: player character renders as a GREY BOX, the
character model and its animations are gone. World visuals (night lighting,
pixelation, trees etc.) otherwise fine.

## Ground truth established by IO (do not re-derive)
- Grey box = procedural stand-in: prototype/js/assets.js makeStandIn(),
  BoxGeometry(0.6,1.8,0.6), fires only when a GLB fails load/parse; logged as
  "[WH assets] substitution: procedural stand-in for <name>".
- Animations come from the same rigged GLB (races_regen/rigged/*.rigged.glb),
  so one failed body load kills model + anims together. Player = playerBody.
- All 3 rigged GLBs + pixelated PNGs ARE present in the worktree (player 4.4MB).
- Server-side probes ALL CLEAN with playwright (host venv /root/whpw-venv):
  - 8793 direct: 28 assets loaded, 0 stand-ins, no console errors.
  - 8793 + IO permissive CSP replayed: same clean result.
  - 8787 /playtest-feat/ with real password login: same clean result; only
    REPORT-ONLY blob: connect-src CSP logs (no img violations).
- Vendor gltf-loader.classic.js is byte-identical between dev and feat.
- assets.js DIFFERS from dev (feat predates whanim3 CSP-immune URL-modifier
  intake; dev commit 8f777bb fixed a blob:-texture/CSP failure whose symptom
  was WHITE bodies, not grey stand-ins - different failure class, but the
  texture-intake area of assets.js is the suspect neighborhood).
- Stale servers exist host-side (pid 1434371 on 8793 serving a BROKEN host
  /tmp/wh-worldfeat with 74 files deleted incl. pixelated PNGs; pid 2590278
  on 8791 serving dev). Nicko's browser could have hit any of these via
  tunnel. IO will kill them separately; treat THIS brief's probes as canonical.

## IO's working hypotheses (ranked)
1. CLIENT-side, transient: 8-10MB multi-MB GLB fetch over the tunnel timed out
   or got corrupted once; loader has NO retry and swaps stand-in permanently.
   Nicko's browser may have stale cached JS referencing old asset layout.
2. CSP interplay: enforced CSP on some surface Nicko hit (old /playtest/
   route, or cached login page) blocked blob:/data: intake -> body parse fail.
   whanim3 fixed this on dev by converting blob:->data: on fetch failure;
   feat tree lacks that fix.
3. Race/parse order in feat assets.js postload pixelated-atlas swap
   (CONFIG.assets.pixelatedBodies kill switch) corrupting materials on some
   timing -> but that would not remove the MODEL, so stand-in theory fits
   better. Verify anyway.

## Your task
A) Root-cause: from the evidence above, identify the most probable concrete
   cause of a one-off client-side stand-in substitution, and make the loader
   resilient so it CANNOT recur silently:
   - add bounded retry (e.g. 2 retries with backoff) for character body GLB
     fetch/parse failures before falling back to stand-in;
   - stand-in fallback stays (never block the game), but it must now log a
     loud one-line console banner identifying WHICH asset failed and WHY
     (network vs parse), and stamp it into the HUD boot line if HUD exists;
   - if diagnosis shows the whanim3-style data:-URI fallback is needed in the
     feat tree's loader, port it (loader is vendor/classic, keep changes
     minimal and consistent with dev's implementation 8f777bb - read it with
     git show 8f777bb -- prototype/vendor/gltf-loader.classic.js).
B) Fix must be confined to prototype/js/assets.js (+ vendor loader only if
   A-diagnosis demands), CONFIG knob if needed.
C) Commit to feat/world-visuals in /tmp/wh-worldfeat. Message format:
   "fix: playtest stand-in resilience - <one line> (Astrabot, brief: <this
   file path>)". NO harness runs. NO pushes (IO pushes).
D) Append a "## Astrabot findings" section to this file with: confirmed cause,
   what changed (files/lines), what to look for when Nicko plays (one line).

## Guardrails
- Do not run servers; two may already be up (8793/8791) - do not kill or
  start any.
- Do not modify CONFIG defaults except adding a retry knob if needed
  (CONFIG.assets.bodyRetryCount or similar, default on).
- Do not touch dev branch, /workspace/witch-hunter working tree, io/specs,
  docs/planning. One commit + one brief edit. Report back through IO.