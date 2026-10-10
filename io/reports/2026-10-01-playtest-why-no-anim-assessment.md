# Assessment: "none of the new animations or combat changes have taken effect"

Date: 2026-10-01. Author: IO. Assessment-only (no code, per Nicko).

## TL;DR

The work IS in the dev branch and IS live on the workspace — I verified from
real runs: dev @ dc697ce pushed, all served JS byte-identical to the tree,
the AnimationMixer advancing frames in a real browser, walk/attack clips
playing, 26/26 assets loading. What Nicko is hitting is a presentation-layer
break on the public playtest surface, not missing code. There are two
independent causes, and one of them is invisible from my headless probes.

## What actually ships today (verified, not assumed)

| Surface | State |
|---|---|
| dev branch | dc697ce (whanim2 runtime) — pushed, verified via ls-remote |
| Server-side JS | /playtest/js/*.js byte-identical to tree (7/7 shas match) |
| RAIL BUTTON route freshness | CONFIRMED FRESH 2026-10-01: all 12 core assets (10 JS + style.css + rigged GLB) byte-identical dev == served via authenticated 8787 context; fresh-tab AND same-tab-revisit probes both get WH_CharacterAnim + anim instance (no-store headers working) |
| Rigged GLBs | Serve 200 on /playtest/ and /witchhunter/ (4.4MB human) |
| Animations in a FRESH browser | walk clip advances (t 0.00->0.45), attack seek works, mixer live |
| Single-file build | prototype/builds/v7-playable.html is STALE: pre-whanim2 content (0 CharacterAnim, old non-rigged bodies, bodyBob still present) |

## Root cause 1 (proven): enforced CSP kills every texture on the WebUI route

The WebUI playtest route (8787:/playtest/) serves the page + scripts with an
enforced Content-Security-Policy (api/helpers.py CSP template). The new
whanim1/whanim2 pipeline re-exports character GLBs with EMBEDDED textures
(images stored inside the GLB, no external URIs — verified in all rigged
GLBs). THREE.GLTFLoader decodes embedded images through blob: URLs with
fetched blobs -> the enforced CSP has img-src data: blob: but NO blob: in
connect-src, so the FETCH of the blob is refused:

- 208 "Connecting to 'blob:...' violates CSP" / "Fetch API cannot load blob:"
  console errors on /playtest/ (8787)
- Same page, same files, no CSP (8793 control): texture loads clean,
  mapImgW=2048, 0 blob errors.
- Player renders as a BLANK WHITE mannequin on 8787; textured dark cloak +
  silver sword on the control.
- In-page probe under the enforced CSP: TextureLoader(data:) = OK,
  TextureLoader(blob:) = BLOCKED. That is the exact break line.

Old Meshy bodies were also embedded-texture, but the v5-era loader ran on the
8792 no-CSP proxy, so nobody noticed. whanim2 moved characters onto the
WebUI-served route visibly.

Consequence: on 8787, characters/props render untextured (mannequins).
Animations DO still play on 8787 in fresh browsers — but a white mannequin
snapping between skeleton poses can easily read as "no animation", especially
since the OLD body-bob/walk-bounce presentations are retired (A11) and sword
poses changed.

## Root cause 2 (probable, unprovable from here): Nicko's browser state

My fresh-context headless runs on 8787 show anim.clip advancing. So if the
code were the only factor, Nicko would see white-but-ANIMATING characters.
"NONE of the new animations took effect" points at a second layer: a stale
tab or browser cache pinning old JS (/playtest/ assets carry no-store from
the file handler, but the HTML shell can persist via the app service worker
if it was registered, or plain browser back-forward cache on a long-lived
tab). The classic signature: everything in a fresh/incognito window works,
his pinned tab doesn't. Cannot verify from the server side — he needs to
hard-refresh / new tab at minimum.

## Also contributing (minor)

- The Playtest rail button (window.location.href='/playtest') is cache-prone
  exactly like the graph.html precedent (pitfall 67: same symptom class,
  fixed there by hard-refresh).
- README still advertises 8792/witchhunter + Tailscale as THE public route;
  the tailscale serve is not running in this box's namespace right now, so
  if Nicko has the public URL bookmarked, that route may be dead entirely
  (worth confirming which URL he actually opens).

## Addendum 2026-10-01 (post-Nicko-feedback): signature discrimination

Nicko reports: "same animations as before, grey blocks, no attack swing
moveset, no skeleton, no Blender anim-run assets, sword backwards (hilt
hits the enemy)."

Findings from live probes at the same hour (all on the REAL current code):

1. The sword-backwards defect is REAL and reproduced on the live dev tree:
   the strike-frame probe shows the weapon mesh's +Y (tip axis after the
   PI Z-rotation in Player.setWeapon) pointing AWAY from the facing
   direction through most of the swing window (tipDotFacing negative in
   5 of 6 samples), only crossing positive briefly mid-swing. The
   setWeapon comment claims "tip leads -Z at strike" but the measured
   geometry disagrees — either the hand-track orientation assumption is
   wrong for this clip or the PI rotation sign is backwards. GAME DEFECT,
   not presentation.
2. The swing moveset DOES exist and plays on the current tree: free-run
   probe of a real click-attack samples R_UpperArm traveling ~232 deg
   across windup->strike (real skeletal articulation); enemy windup shows
   a monotonic raise-back telegraph (w 0.87->0.68 across 0.55s).
   The clip data itself carries per-bone channels for all 20 bones.
3. "Grey blocks" matches the CSP texture kill proven for the 8787 route:
   skinned mesh loads (1 skinned + 1 rigid child, 0 stand-ins, mixer live,
   6 clips bound) but EVERY texture blob fetch is refused (208 errors),
   so characters render white/grey while still animating. On the clean
   origin the same character is textured. A rigid grey mannequin that
   only slides + bobs is EXACTLY what 8787 shows for the FIRST frames
   before/around clip transitions at 4-11 fps... BUT the arm-travel
   probe above ALSO holds on 8787 (same quaternion trajectory), so the
   skeletal motion reaches 8787 too.
4. Therefore Nicko's "same animations as before / no skeleton" reading is
   dominated by two things: (a) all texture/material detail stripped on
   his route (white mannequin = 'grey blocks'), (b) the sword-backwards
   defect destroying the swing's readability (hilt-first arc reads as
   'no moveset'), and (c) plausibly stale-tab JS on top. The structural
   difference (skinned meshes, sockets, clips) is present in his build;
   the PRESENTATION of it is broken in two compounding ways.

Fix plan ranking updated: B1 = sword orientation (game defect, blocking),
B2 = data: texture intake (CSP-immune), B3 = rail-button cache-buster +
fresh-tab confirmation, A optional (blob: in connect-src) as
defense-in-depth. No code written per assessment-only instruction.

### Option A — Fix the WebUI playtest route's CSP (recommended first)
Widen the enforced CSP template in api/helpers.py: add `blob:` to
connect-src (or route texture blobs through a same-origin texture endpoint,
which is the belt-and-braces version). Both are 1-3 line changes in ONE file
(api/helpers.py template `{connect_src}` interpolation or the img pipeline).
Then: container restart (backend python change) + Nicko hard-refresh.
- Pros: fixes the real defect class at the chokepoint for EVERY future
  embedded-GLB asset; keeps the live-serve convenience; small blast radius.
- Cons: touches the WebUI security template -> needs care + a Testerbot
  check that the CSP stays tight elsewhere (report-only mode exists).
- Effort: S (hours incl. validation). Gate: IO spec -> Devbot -> Testerbot.

### Option B — data:-URI texture rewrite in the whanim pipeline
GLTFLoader accepts an on-demand transform; simplest robust variant: in
prototype/js/assets.js, install a loader hook that rewrites embedded
image blobs to data: URIs before the internal TextureLoader runs
(TextureLoader(data:) already PROVEN to pass the current CSP).
- Pros: fixes textures on ANY origin (8787, 8793, file://, future embeds)
  without touching WebUI security headers; game-repo-only change.
- Cons: one-time in-memory rewrite cost (10 GLBs, trivial); slightly hacky
  if done naively (must intercept at the GLTFLoader parse level, not
  post-hoc material surgery).
- Effort: M (a focused Devbot round + Testerbot A/B on both origins).
- This also permanently de-couples the game from WebUI CSP policy churn.

### Option C — Rebuild + rewire the single-file build (parallel track)
prototype/builds/v7-playable.html is stale (pre-anim2). Rebuild it with
tools/build_v7.py --embed-anim and make it the playtest target (button ->
builds/v7-playable.html). Fully inlined blob: textures STILL hit the same
CSP on 8787, so Option C alone does NOT fix 8787; but served from the
8792-style origin (or as a data:-inlined build), it's CSP-immune.
- Pros: one-click artifact, closest to "release build" thinking.
- Cons: extra build step to keep fresh every round (already bitten once
  today: build drifted from sources mid-session).
- Verdict: do NOT make this the primary playtest path; keep as artifact.

### Option D — Do nothing code-wise; change the access path
Point the Playtest button at the clean-origin server (8792-style, e.g.
a WebUI-proxied /witchhunter/ route that strips CSP, or keep the existing
8792 origin and publish it via the ssh-tunnel/Tailscale route in README).
- Pros: zero game-code risk, zero security-template churn; immediate.
- Cons: leaves textures broken on the main /playtest/ route for anyone who
  lands there; origin split stays confusing (8787 white, 8792 fine).

## Recommended plan (for Nicko's call)

1. Nicko first: hard-refresh or open /playtest in a new/incognito tab and
   confirm whether he sees white mannequins ANIMATING (expected with fresh
   cache) vs literally nothing moving (old-JS cache layer).
2. Implement Option B (game-side data: texture intake) — root-cause fix for
   the class, no security-surface changes, gate via Devbot->Testerbot with
   the A/B probe as the acceptance bar (mapImgW>0 on 8787, 0 blob errors).
3. Optionally follow with A (blob: in connect-src) as defense-in-depth for
   any future fetch()-based asset path, validated against the CSP template
   tests.
4. Rebuild v7-playable.html (Option C hygiene) so the artifact matches dev.
5. Update README playtest routes + report at the end.

No code has been written; dev branch untouched by this assessment.