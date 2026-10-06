# C2 CHANGE ORDER - DAY/NIGHT CYCLE (stage 3 cooking arc, order 2)

Builder: Claude Code print-mode, model opus, allowedTools Read/Write/Edit/Bash.
Dispatched only by IO on Nicko's go. NO automated game runs of any kind (no
harness, no headless browser, no smoke pass). Validation = playwright driver
node --check per edited JS file ONLY (/usr/local/lib/python3.12/site-packages/
playwright/driver/node). Nicko's playtest is the only acceptance test.

## STATE (verified 2026-10-05)
- feat/world-visuals worktree /tmp/wh-worldfeat clean at 6657c22 (C1 cooking
  APPROVED by Nicko playtest + ADD WOOD amendment). Build: tools/build_v8.py ->
  prototype/builds/v8-playable.html.
- C1 landed: CONFIG.cooking (interactRadius, channelSeconds 3, interruptKeys,
  buffDurationFallbackSec 480, fire{startFuelSec 240, burnPerCookSec 10,
  burnTickSec 1, refuelCooks 4, fuelItem deadwood}, stations[], recipes[],
  fallbackResult, buffs{}, hint{}, text{} incl addWoodBtn, toastChainSec,
  kitButton), prototype/js/cooking.js (Station burn + cook panel + BuffSet),
  game.js hooks, inventory.js food-use, style.css.
- CONFIG.lighting: hemi fill (hemiBaseIntensity * region ambientLightLevel),
  moon directional 0xa8bce6 @ 0.9 (azimuth 0, elevation 30), tonemap/exposure
  from R2. game.js: skyTick() (dome/moon camera-anchored, star twinkle),
  cemeteryFogTick() (region A fog ramp), update() calls both.
- NO day clock anywhere. Region fog: regionA cemeteryFog, regionB fogColor
  0x6f7477 fogDensity 0.024 (darkwood canon).

## DESIGN CANON (Nicko, locked in chat 10-05)
1. Full sky cycle THIS ORDER: dawn > day > dusk > night. The CURRENT night rig
   (moon look, exact current intensities/fog) IS the night phase - at night
   the build must look IDENTICAL to today (zero drift of the approved look).
2. Day length CONFIG-tunable, default 600 real seconds per in-game day
   (supersedes buffDurationFallbackSec; keep the key as fallback rename
   buffDurationDaySec or similar, C1 comment updated).
3. Rest = morning rides C3 (bedroll/tent). C2 ships the clock + cycle only.
4. ONE-MEAL-PER-DAY cap plugs in THIS order (doc 10 canon): the first BUFFED
   meal eaten in a day applies its buff and fills the day's meal slot; any
   further buffed meal that day is eaten but grants no buff ("You have
   already eaten today" toast; CONFIG text). Non-buffed food (Bland Mush) is
   never capped. New day (clock wrap or, after C3, rest) clears the slot.
5. Grave Soup buff duration: 1 in-game day = CONFIG day length (600s), no
   longer the 480 fallback. Refresh-on-reeat still refreshes duration (and
   still consumes the meal + respects the cap: refresh counts as the day's
   meal if no meal eaten yet today).
6. Cooking stays possible any time (morning-ritual gating is C3+ via rest).

## SCOPE (implementation contract)
1. CONFIG.dayNight: { dayLengthSec: 600, startPhase: 'night', phases: {...} }.
   Phase table drives: hemi fill mult, moon/directional intensity, fog color
   + density per region (darkwood night = TODAY's exact values; day = pale
   daylight per art tone: gothic but readable, keep palette darkwood not
   cheerful), tone exposure mult, star visibility, moon/sun dome position.
   Sun: reuse the moon directional as sun by day (warm-day tint acceptable
   via phase tint, NO new light objects; light pool untouched).
2. js/daynight.js (NEW module, same patterns as cooking.js registration):
   phase state machine over dayLengthSec, phase boundaries dawn/day/dusk/
   night (CONFIG fractions of the cycle), per-frame lerp of tint/intensity/
   fog between phases (smooth transitions, no pops), exposes current phase +
   day count + time-of-day fraction; game.js update() calls its tick and
   night phase reuses TODAY'S exact lighting values (verified constant match).
3. BuffSet consumes daynight: buff durations are measured in DAYS (1 day),
   countdown by clock; eating logic implements the meal cap (4); HUD buff
   chip label unchanged, duration readout may show day-fraction.
4. CSS: nothing beyond existing patterns if possible.
5. index.html + tools/build_v8.py: add js/daynight.js to concat order
   (before game.js, after cooking.js).
6. CONFIG.cooking edits: meal-cap text keys, buff duration now day-based
   (keep buffDurationFallbackSec only as a fallback if daynight missing).

## HARD LAWS
- Work ONLY in /tmp/wh-worldfeat on feat/world-visuals. First command: cd
  /tmp/wh-worldfeat && git fetch https://github.com/CaptainPickard/witch-hunter.git
  feat/world-visuals && git rev-parse HEAD FETCH_HEAD - if they differ with
  prototype/ or tools/ changes on FETCH_HEAD, STOP and report to IO.
- Never touch dev/main, /workspace/witch-hunter, CONFIG.mouse, docs/.
- Night phase must byte-match today's lighting values for hemi/moon/fog keys
  (copy them, do not approximate). The approved night look may not drift.
- Do not weaken cooking/interact logic from C1. Player copy never says "free".
- Commit identity CaptainPickard <pickard.nicko@gmail.com>. Commit units:
  (1) CONFIG dayNight + phase tables, (2) js/daynight.js + hooks, (3)
  meal cap + buff duration conversion, (4) build: v8 bundle + grep marker
  (WH_DAYNIGHT appears in the bundle). Push after EVERY commit.
- NO new deps; vanilla JS + THREE only, same bundle pattern.

## ACCEPTANCE (Nicko playtest list)
A1. Boot = night look identical to the approved build (he verifies visually).
A2. Waiting through dawn: world brightens smoothly; day is pale daylight,
    darkwood palette preserved.
A3. Dusk -> night returns exactly to today's look. Full cycle = 600s.
A4. Eating Grave Soup at night: buff lasts THROUGH dawn/day/dusk into the
    next night (1 in-game day), chip shows it; re-eat before expiry only
    refreshes.
A5. One meal per day: second buffed meal same day = "already eaten" toast,
    no second buff; Bland Mush still edible freely.
A6. Clock wrap clears the meal slot; next buffed meal applies again.
A7. Cooking anytime still works exactly like C1 (panel, fuel, channel).
A8. Cemetery fog ramp + star twinkle unchanged; no light-pool regressions.

## FINAL REPORT (<= 50 lines)
Files + CONFIG knobs (phase table values with the night = today's values
proof), phase math summary, commits table with shas + push confirmations,
marker counts, watch items.