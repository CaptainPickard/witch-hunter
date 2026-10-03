# Astrabot Mission Brief - loading screen with progress bar (2026-10-03)

Nicko change order (verbatim intent): "get a loading bar that progresses when
the game starts up so im not looking at 'Loading Assets...' text. Have it say
Witch Hunter then the loading bar beneath that."

Confirmed working baseline: feat/world-visuals @ 7c9b5f6 (character models +
anims back, all-asset retry live, spawn facing center). Build on exactly this
head. NO harness runs - his playtest is the acceptance bar. Syntax-check edited
JS with esprima only. Commit to feat/world-visuals IN THE WORKTREE
/tmp/wh-worldfeat, single commit, then append "## Astrabot findings" to this
file and amend (message unchanged, starts "feat:"). NO pushes (IO pushes).
Do not touch /workspace/witch-hunter, other branches, servers (8793 host
container + webui route are IO-managed), io/specs, docs/planning.

## Acceptance criteria (playtest bar)
1. During boot: full-screen dark overlay showing the title "Witch Hunter" with
   a horizontal progress bar beneath it. No plain "Loading assets..." text as
   the primary element (it may live as a small sub-caption or be replaced).
2. The bar reflects REAL progress: fraction of manifest assets settled
   (loaded OR stand-in) over total - the loader already counts these. No fake
   timed animation.
3. On completion the overlay fades out smoothly and never blocks input;
   game boots exactly as today (region A, spawn facing center).
4. If any asset ends as a stand-in, the existing pink HUD failure note
   (flushAssetFailureNote / #wh-asset-fail-note) must still be visible AFTER
   the overlay is gone - do not remove or re-parent it in a way that breaks it.
5. Styling matches the existing HUD/design language: darkwood palette, the
   pixel/pixelated aesthetic, restrained; amber is the fire/human accent -
   acceptable for the bar fill; no other accent colors. Player copy law:
   never the word "free"; no hardcoded agent names.
6. Works identically on both serving surfaces (/ 8793 and /playtest-feat/
   8787) - i.e. plain relative paths, no server-side changes needed; do not
   modify server.py or the webui.

## Where to look (IO pre-read, save yourself the walk)
- prototype/index.html line 24: <div id="wh-load-note">Loading assets...</div>
  (styled #wh-load-note in style.css ~169-183 incl. .hidden).
- prototype/js/game.js ~753: game.hud.loadNote.classList.add('hidden') at boot
  complete; setupHud() ~150 grabs it. WH_ASSETS.preloadAll() ~727.
- prototype/js/assets.js: preloadAll() ~319-330 (loadedCount, failed map,
  Promise.all over loadOne jobs). loadOne resolves per asset - the natural
  per-asset progress hook point (retry delays just delay that asset's tick).
- CONFIG.js has no loading-screen knobs today; add one only if genuinely
  needed (fade ms), default on.

## Guardrails
- Keep the diff tight; vanilla JS ES5-consistent with the tree; no frameworks.
- Do not alter loader retry semantics or stand-in behavior (just hook progress).
- Do not remove #wh-load-note uses elsewhere without checking references.
- Report back through IO; do not start/stop servers; no pushes.
## Astrabot findings
Implemented on feat/world-visuals, single commit amended with these findings
(baseline 36e1f97). Commit hash changes on amend; final hash reported to IO.

- Files: prototype/index.html (+7), prototype/style.css (+42/-4 net),
  prototype/js/assets.js (+20), prototype/js/game.js (+22), prototype/js/CONFIG.js
  (+2). ~90 lines, vanilla ES5, three esprima parse checks pass.
- The overlay IS the existing #wh-load-note, restructured in index.html into
  #wh-boot-title ("Witch Hunter", uppercased darkwood ivory), #wh-boot-bar with
  #wh-boot-bar-fill, and a demoted sub-caption #wh-boot-sub (old "Loading
  assets..." text lives here, now with a live "n / 28" count). No "Loading
  assets..." as primary element anymore.
- Real progress source: in loadOne (js/assets.js) the settle chain was captured
  as `settled`; a final `.then` fires bootProgressTick() exactly once per asset
  AFTER it settles loaded-or-stand-in (swapBodyMap atlas wait included, so the
  tick order matches actual completion). setupHud() registers the callback via
  new WH_ASSETS.setBootProgressCb and counts ticks over
  Object.keys(WH_ASSETS.MANIFEST).length = 28, setting the fill width to
  round(100*done/total)%. No timed/fake animation. Retry semantics untouched:
  backoff only delays that asset's tick. Promise.all / preloadAll contract
  unchanged (both then-chains pass values through).
- Fade-out: at boot complete game.js sets transition from
  CONFIG.hud.bootOverlayFadeMs (new knob, 900ms default; CSS fallback 0.9s)
  then adds .hidden (opacity 0 + pointer-events:none), so the overlay never
  blocks input during or after the fade; the node stays in the DOM like before.
- Failure note: #wh-asset-fail-note creation/append in assets.js untouched,
  still z-index 40 in #wh-hud while the overlay sits at z-index 30, so a
  stand-in note remains visible after the overlay fades. flushAssetFailureNote
  firing mid-load is fine - it simply sits under the overlay until boot done.
- Palette: title #d8d2c0 (HUD ivory), bar frame #4a4034, bar well #14110e,
  sub-caption #8a7f70; single accent is the amber fill #d8b24a (same value as
  the existing reticle/soul fill). No new accent colors, no "free", no agent
  names. Relative paths only; nothing server-side touched.
- Not executed in a browser per hard law (no harness runs); Nicko's reload is
  the acceptance bar. If he wants a different fade length, it is one CONFIG
  number: hud.bootOverlayFadeMs.
