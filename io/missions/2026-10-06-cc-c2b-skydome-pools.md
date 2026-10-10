# C2b CHANGE ORDER - PAINTED SKY POOLS + PER-AREA DAILY ROTATION (stage 3 arc)

Builder: Claude Code print-mode, model opus, allowedTools Read/Write/Edit/Bash.
Dispatched by IO on Nicko's go. NO automated game runs of any kind (no
harness, no headless browser, no chromium smoke): validation = playwright
driver node --check per edited JS (node lives at
/usr/local/lib/python3.12/site-packages/playwright/driver/node). Nicko's
playtest IS the acceptance gate.

Hard laws: work ONLY in /tmp/wh-worldfeat (feat/world-visuals). First
command: cd /tmp/wh-worldfeat && git fetch
https://github.com/CaptainPickard/witch-hunter.git feat/world-visuals &&
git rev-parse HEAD FETCH_HEAD - if they differ on prototype/ or tools/
content, STOP and report. Identity CaptainPickard <pickard.nicko@gmail.com>.
Commit in units + push after EVERY commit. Never touch branches dev/main,
/workspace/witch-hunter, CONFIG.mouse, docs/. Never read/commit
scratch/.mixamo-credentials.txt or .mixamo-storage.json. Build =
python3 tools/build_v8.py + marker greps. Player copy never says "free".

## WHAT THIS ORDER DOES
The dome's procedural gradient sky is REPLACED by painted panorama textures
(one per phase from POOLS), cross-faded by the existing C2 day/night clock,
with a per-AREA daily rotation so each day and each area reads a different
sky over time (Nicko 10-06 ruling). C2's approved LIGHTING (directional
color/intensity, hemi mults, fog values, exposure, cemetery ramp) is
UNTOUCHED - only the dome's visuals change.

## THE POOLS (all committed at art-direction/textures/)
- day:   [ sky2/sky2-day.jpg   (approved A), sky3/sky3-dayB.jpg, sky3/sky3-dayC.jpg, sky3/sky3-dayD.jpg ]
- dawn:  [ sky2/sky2-dawn.jpg  (approved A), sky3/sky3-dawnB.jpg, sky3/sky3-dawnC.jpg, sky3/sky3-dawnD.jpg ]
- dusk:  [ sky2/sky2-dusk.jpg  (approved A), sky3/sky3-duskB.jpg, sky3/sky3-duskC.jpg, sky3/sky3-duskD.jpg ]
- night: [ sky2/sky2-nightA.jpg, sky2/sky2-nightB.jpg, sky2/sky2-nightC.jpg ]
All 2048x512 JPEGs, seam-fixed, 5-bit posterized + NEAREST baked in. The HD
masters live in scratch/sky-masters* - never commit them again (already in).

## ROTATION LAW (Nicko 10-06: "each new day cycle feels unique over time and
in each area of the game")
variantIndex = (dayCounter + AREA_POOL_OFFSET[areaId]) % pool.length.
- dayCounter = full clock wraps since beginCycle (0 on the dormant night).
- AREA_POOL_OFFSET: hold_outskirts 0, darkwood_edge 2 (per-area difference;
  more areas = one new offset each).
- Recompute only on phase ENTER and on region cross (region cross does a fast
  1.0s cross-fade to the area's variant for the CURRENT phase, hidden behind
  fog anyway).
- Dormant night (before first sleep): night pool [(0 + offset) % 3].

## WIRING CONTRACT
1. CONFIG.dayNight.pools = the 4 lists above (full URLs) + areaPoolOffset.
2. DOME PANO LAYERS in daynight.js (module owns them; game.js only calls
   applyDayNight as today):
   - Two inside-out spheres (MeshBasicMaterial, side BackSide, depthWrite
     false, fog false, radius just under the current dome) render the panos.
     Layer A (current) opacity 1; on phase enter, layer B gets the NEW
     phase's texture and fades in over that phase's blendFrac window, then
     A:=B and B idles. map.colorSpace = SRGBColorSpace; anisotropy 1;
     minFilter LinearMipmapLinearFilter (pixelation is baked in the
     textures).
   - The OLD procedural gradient dome + horizon glow stay as UNDERLAY while
     any pano is still loading (fallback = today's approved gradient, never
     a black sky). Once the current phase's pano is live, the gradient dome
     fades out (not disposed - it is the fallback forever).
   - RETIRED whenever panos are active: the moon/sun DISC sprite and the
     painted stars of the gradient dome. The live STAR TWINKLE Points layer
     STAYS compositing over the night pano (Nicko hybrid ruling), its
     opacity following the night phase's stars value, fading out by day.
3. PRELOAD: during each phase's first 20%, lazily TextureLoader-load the
   NEXT phase's variant for the current area; cache by URL in a map (max 6
   textures alive). On a load error (timeout/abort): retry ONCE, then keep
   the previous pano + gradient underlay (log to console, never black).
4. game.js: only the pano-layer init hook + region cross call. NO touches:
   light pool, fog machinery, cemeteryFog, exposure mults, HUD, cooking,
   moveset.
5. Texture URLs ride the existing asset path system (art-direction/... is
   served by /playtest-feat/ and 8793 /prototype/-relative as today).
6. index.html script order + build_v8.py: no new files unless a small
   skydome.js module is cleaner than growing daynight.js (builder's call;
   if added, declare in BOTH lists).

## PHASE-CHAIN REQUIREMENT (the four pools chain smoothly)
Dawn pano ends rose-lavender -> day starts grey; day ends grey -> dusk slate
+ amber; dusk ends near-night with stars -> night deep navy. The C2 blend
window (blendFrac) carries each fade; NO new timing knobs unless a fade
reads broken (then ONE CONFIG key, flagged in the report).

## ACCEPTANCE (Nicko playtest)
A1. Four distinct painted phase looks chain smoothly; no black/white pop.
A2. Same day, different area = different sky; crossing regions swaps variant
    (1s fade, behind fog).
A3. Day counter advances the variant next day (day B shows on day 2 in
    hold_outskirts if A played day 1).
A4. Night shows the big painted moon with cloud wisps; live twinkle stars
    still read over it; NO double moon (disc sprite retired during pano).
A5. Lighting/fog/cemetery/exposure identical to approved C2 at every phase
    (zero drift; only the dome imagery changed).
A6. No 20s asset-timeout crashes of the sky: preload + retry + fallback law.
A7. Dormant night shows a painted night pano immediately at boot.
A8. node --check passes all edited files; build marker greps non-zero
    (WH_DAYNIGHT present, WH_SKYPOOL marker added).

## COMMITS (units)
1. feat(sky): dome pano layers + CONFIG pools/offsets (WH_SKYPOOL marker)
2. feat(sky): per-area daily rotation + cross-fade + preload/fallback law
3. build: v8 bundle
(Textures are ALREADY committed by IO at art-direction/textures/sky* -
do NOT recommit them.)

## FINAL REPORT (<= 50 lines)
Files + knobs (CONFIG keys with values), pool URL table as shipped, texture
cache strategy, marker counts (WH_SKYPOOL, WH_DAYNIGHT), watch items for
Nicko's playtest (fade feel, moon size in-engine, twinkle-over-paint leg).