# World R4 — Pixelated character bodies: Devbot implementation report (DRAFT)

Date: 2026-10-02. Branch: feat/world-visuals (worktree /tmp/wh-worldfeat).
Gate step 3 (Devbot). Tree at dispatch: 902a3e2. Code base: cce06eb (R3 marker).
Specs of record: io/specs/devbot-spec-wh-world-r4.md (MECHANISM RULING :32-45,
OFFLINE BAKE) + io/specs/testerbot-spec-wh-world-r4.md (amendments B1-B9 binding).
carrier-req: Testerbot revalidates harness on lane recovery.

## STATUS: implementation + harness written; SMOKE NOT CAPTURED
Python execution was gated by the session's permission layer: every
`python3 <script>` call (build.py, the harness) needed approval, and this
non-interactive session couldn't grant it. Shell writes were gated too.
**No harness run happened. /tmp/whr4_smoke_devbot.log does not exist.** The
pre-Devbot expectations table has NOT been checked against a run. Treat every
bar below as unverified until the commands in "Runner steps" are run.

## Per-file changes
### prototype/js/CONFIG.js (1 hunk, pure insertion inside assets {} :478-481)
- Inserted after `timeoutMs` (old line 479): a 2-line kill-switch comment +
  `pixelatedBodies: true,`. `timeoutMs` and `standInColor` lines are
  byte-unchanged. I put the key before `standInColor` so I didn't have to add
  a comma to that line (no line is removed).

### prototype/js/assets.js
- Header comment :6-7 now describes the R4 atlas swap (3 lines replace 2).
- `BODY_PNG` table placed right after MANIFEST: playerBody/banditBody/
  ghoulBody -> `races_regen/rigged/<stem>.rigged.pixelated.png`.
- ONE helper `swapBodyMap(name, root, done)` placed between prepTemplate and
  loadOne. Kill switch off or no table entry -> `done()` runs synchronously,
  so the original path is unchanged (same ordering). Kill switch on ->
  `THREE.TextureLoader` loads the PNG, then for each mesh map it sets
  explicitly (B4): `flipY=false`, `colorSpace=THREE.SRGBColorSpace`,
  `wrapS/wrapT` copied from the original map, `magFilter=Nearest`,
  `minFilter=LinearMipmapLinear`, `generateMipmaps=true`, `needsUpdate`;
  then `m.map = tex`, `m.needsUpdate`, and `old.dispose()` (it is never
  uploaded, so this is a swap, not an add). If the PNG fails to load, a
  warning is logged and the original atlas stays.
- loadOne success path: `loadedCount++; resolve(...)` now runs inside the
  swap callback, so preloadAll resolves only after the swap. Clones share
  the template material, so live instances share the PNG map.
- Byte-identical: groundAlign, prepTemplate, instance, makeStandIn,
  resolveUrl, preloadAll, CHARACTERS, the WH_ASSETS API (PRES checks this
  by extracting each function).

### Harness: tests/r4parts/part01..08.py + build.py -> tests/wh_world_r4_validation.py
- I assembled the artifact by hand with the Write tool, then confirmed it
  with `cat tests/r4parts/part0[1-8].py | cmp - tests/wh_world_r4_validation.py`
  (IDENTICAL), and grep found no duplicate `def`. It has NOT been
  py_compiled; build.py does that.
- part01 plumbing (identity = lightPool + ambientIntensity 0 + internalResDiv
  + pixelatedBodies + CONFIG byte equality; self-spawn on an ephemeral port;
  never 8791; full request log feeding the 8791 BLOCK). part02 JS probes +
  the B2 route rewrite (exactly-once count). part03 screen metrics, in-harness
  A2 probe, per-context collection (ON and OFF are separate contexts; flake
  retry max 2). part04 pre-Devbot baseline + R4-1/R4-2/R4-3. part05 PNG proof +
  R4-4. part06 R4-5. part07 PRES. part08 verdict/main.

## How each AC is implemented (valspec mapping)
- R4-1: one TEX_JS evaluate per context. ON bars (1)-(7) plus live-instance
  map uuid == template uuid. OFF bars: rewrite count == 1, 2048 dims, no
  'pixelated' in src, mag/min/flipY/colorSpace equal the pre capture exactly,
  0 PNG requests.
- R4-2: initTexture on all 3 template maps, then a forced render, then
  `info.memory`. Bars: texture and geometry counts equal ON vs OFF, and the
  per-body ratio === 16.0 from dims (bytes = w*h*4*4/3, recorded).
- R4-3: (a) draw to a 512 canvas -> <= 32 levels per channel (mod-8 and
  top-8 recorded; OFF recorded as a discrimination check). (b) one evaluate:
  shown -> body hidden -> restored; mask > 8; >= 400 px or settle-retry;
  bars D_on <= 0.60*D_off and E_on - E_off >= 0.10. If (a) passes and (b)
  misses -> FAIL-RETUNE-PENDING. Artifacts: tests/artifacts/r4-screen-*.png.
- R4-4: v3 runs through `python3 -c`: rewrite the ORIGINS line in memory
  (regex count must == 1) and exec it, so the file is untouched. ds1 runs
  with WH_BASE_ROOT. v2 runs with the proxy set to 127.0.0.1:9. 8791 URLs
  in subprocess output feed the BLOCK. In-harness: 6 clips, bones ON==OFF,
  GLB sha == cce06eb blobs. wh_v7_weave is SKIP-NOTED.
- R4-5: R1 subprocess with WH_R1_PORT + WH_R2_FLOOR=0. Inherited waiver
  classes A2/A3/A4/A6/A7/A8 are re-verified in-run. A1 must PASS without a
  waiver. A2 non-worsening bars (+0.005) apply per actor + walk.
- PRES: allowed set exactly; hunk windows; forbidden files = BLOCK; GLBs
  unchanged; PNG blobs == 8bd137a; index sha pin; v7 rebuild on a temp copy;
  secrets + "free" scans.
- PNG: HTTP 200, image/png, 512x512, served == worktree == 8bd137a blob.
- Verdict: PASS only if every gating AC passes (R4-5 may be WAIVED). Any
  SKIP-NOTED AC makes the verdict FAIL and is listed in `skip_noted`. BLOCK
  on any BLOCK, BOOT/NET failure, or >= 3 flakes. Exit 0 always.

## Deviations (flagged for Testerbot revalidation)
1. A2 pre/post numbers come from an in-harness probe. The probe reads R1's
   own `JS_PLAYER_BODY_MINY` / `ENEMY_MINY_JS` verbatim and replicates the R1
   sprint protocol (13 x 160 ms). I did this because R1's evidence string
   only lists actors above 0.02, and the valspec's smoke uses
   WH_W4_FLOOR=0, which would never capture R1 numbers. R1's own A2
   evidence is still recorded (`r1_a2_evidence`).
2. Pre-Devbot baseline source, in priority order: (i) this run, when the
   tree has no `pixelatedBodies` key; it writes tests/artifacts/
   r4-pre-off.json + r4-pre-a2.json. (ii) WH_W4_PRE_A2 or those files.
   (iii) a git-archive copy of 8bd137a measured live. Because my pre-Devbot
   smoke never ran, the first post-Devbot run will use (iii).
3. A4-nightrig re-verification: R4 runs no R2 subprocess, so the R2 L4/L10
   chain isn't available. The waiver now requires game.js, region-manager.js,
   player.js, style.css and index.html to be unchanged since cce06eb, plus
   the CONFIG hunks to be assets-only (rig byte-identical to the validated R3
   marker).
4. Self-spawn readiness uses CONFIG byte equality only, so the pre-Devbot
   tree can boot. BOOT records whether full R4-signature identity holds.
   Reuse still needs the full identity.
5. assets.js insert windows allow ±1 line, because git's diff can slide a
   blank or brace line by one when an insertion sits next to an identical
   line.
6. ds1 still spawns prototype/server.py on its own default port 8791 (that
   file is unchanged, as the valspec requires). If the landed server holds
   8791, that spawn just fails to bind. If 8791 is free, ds1 would bind it
   briefly and terminate it on exit. None of our page requests go there.
   ds1 loads builds/v7-playable.html, a tracked build with inlined JS, so it
   does not exercise the new assets.js. Recorded, not changed.

## Amendments not satisfied
- Not run, therefore nothing below is proven: the pre-Devbot table check, the
  smoke log, all bars. Every amendment B1-B9 is implemented in code. B8:
  this round did no re-bake. The PNGs are untouched and the harness proves
  their bytes against 8bd137a.

## Runner steps (IO / Testerbot)
    cd /tmp/wh-worldfeat
    python3 tests/r4parts/build.py
    WH_SMOKE=1 WH_W4_FLOOR=0 python3 tests/wh_world_r4_validation.py \
      > /tmp/whr4_smoke_devbot.log 2>&1      # ~10-15 min SwiftShader
    python3 tests/wh_world_r4_validation.py > /tmp/whr4_full.log 2>&1
Expected smoke on the post-Devbot tree: BOOT PASS; R4-1/2/3, PNG, PRES give
their real verdicts; R4-4/R4-5 SKIP-NOTED, so the verdict is FAIL with
skip_noted [R4-4, R4-5]. Optional pre-Devbot capture: stash only
assets.js + CONFIG.js with a WIP commit or tagged stash, run the smoke to
write tests/artifacts/r4-pre-*.json, then restore.

## Not touched
index.html, player.js, game.js, enemy.js, anim.js, region-manager.js,
style.css, rigged GLBs, PNG bytes. No commits, no pushes, no servers started.
