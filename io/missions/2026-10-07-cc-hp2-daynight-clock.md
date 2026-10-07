# HP2 - DAY/NIGHT CLOCK (post-first-sleep only) (change order)

- date: 2026-10-07 | order: HP2 | branch: feat/world-visuals | baseline: HP1
  landed commit (see STATE) on top of f6a05bc
- builder: Claude Code print mode, model opus, --max-turns 80,
  --permission-mode acceptEdits, allowedTools Read/Write/Edit/Bash
- worktree: /tmp /tmp/wh-worldfeat | serving: 8793 atomic flip + webui
  /playtest-feat/
- laws: NO harness / headless browser of any kind. Nicko's playtest is the
  only acceptance test. One order at a time. Syntax checks on edited JS only.

## STATE (verified census 2026-10-07 @ f6a05bc)

- f6a05bc "feat(ck1): campkit wiring" pushed; 8793 flipped; curl 200 md5
  9f77b0ce. AI1 S1 6aaf339 + S2 e325005 landed before it. HP1 (enemy health
  bars) lands BEFORE this order starts (one order at a time); baseline for
  this brief is HP1's landing commit on f6a05bc - re-run the census command
  block below before dispatch.
- DayNight mechanics live: js/daynight.js WH_DAYNIGHT. this.dormant = true at
  construction (:126, day 0 tutorial night, frozen). beginCycle() :152-157 -
  dormant -> dawn day 1 (ONLY js/camp.js calls it: the FIRST Save-and-Heal).
  nextDawn() :165 - free-running -> next day's dawn WAKE-SNAP (clock = blend
  window held at dawn). Save restore (save.js:143-150): day from save, phase
  not startPhase or day > 0 => dormant false - so CONTINUE of any day>=1 save
  boots the clock visible, CONTINUE of a day-0 dormant save hides it.
  Dormant tick return :184-185. Phase bounds CONFIG.js:1580 bounds
  {dawn:0, day:0.05, dusk:0.5, night:0.55}, blendSec :1582 90s slow
  transitions, blendFrac LEGACY :1581 - do not use.
- dayNight reads: day (int >= 0), dormant (bool), timeOfDay (0..1 across the
  FULL cycle), phase ('dawn'|'day'|'dusk'|'night'). NO heal/hp coupling, NO
  new timers needed. game.js owns the instance (game.dayNight), camp.js owns
  the menu (Save / Save-and-Heal / LOAD).
- HUD truth: index.html #wh-hud contains wh-bars (left), wh-fps, tuner,
  region name, reticle, mouse chip, death overlay, boot note. game.js huds at
  :196-206. updateHud :751.
- Bundle: python3 tools/build_v8.py from repo root.

## CODE-REVIEW-GRAPH IMPACT (baked 2026-10-07, alias wh-worldfeat @ f6a05bc)

impact --files prototype/js/daynight.js prototype/js/camp.js prototype/js/save.js
prototype/js/game.js prototype/js/CONFIG.js prototype/style.css
prototype/index.html --repo /tmp/wh-worldfeat:
- 137 nodes directly changed
- 0 nodes impacted within 2 hops
- 0 additional files affected
HUD-isolated. Only visual reads of DayNight; no cycle logic changes.

## LOCKED RULINGS (clarify 2026-10-07, Nicko answered)

1. GATED POST-FIRST-SLEEP: clock exists only when the day clock is running.
   Hidden while dormant (day 0 tutorial night). Appears from the first
   Save-and-Heal wake onward. CONTINUE loads of any day>=1 save show it.
   Predicate: exactly (!dn.dormant) - no new save fields, no new timers.
2. TOP = WAKE: the needle at TOP (12:00) reads the wake moment. Both
   beginCycle() and nextDawn() land the needle at top (beginCycle -> dawn,
   nextDawn -> held dawn wake-snap). The dial maps timeOfDay 0..1 clockwise
   from top: t=0 top (wake/dawn start), t=0.05 dusk-line... (dawn 0-0.05,
   day 0.05-0.5, dusk 0.5-0.55, night 0.55-1.0). The cycle reads as one
   revolution per 100-minute in-game day; the needle position IS the answer
   to "how much day/night remains": in the day segment the needle sweeps the
   right half top->down (day remaining = arc behind it), in the night
   segment it sweeps the left half (night remaining).
   Geometry law: needle angle = timeOfDay * 2PI, measured clockwise from
   12 o'clock.
   NOTE (IO): beginCycle lands at t=0 (needle top, start of day segment).
   nextDawn wake-snap holds dawn (t=0) - needle top. Same visual: top = wake.
3. FACE: CIRCULAR DIAL (Nicko picked over the horizontal bar). Right half =
   day (warm amber-tinted segment), left half = night (dark blue-grey
   segment). One rotating needle. NO numbers anywhere.
4. SEGMENT TINTS: muted darkwood-register chrome; may subtly nod to the
   CONFIG dayNight phase row colors (dawn/day/dusk/night rows at
   CONFIG.js:1559+, e.g. day zenith 0x56606e, night zenith 0x070a18,
   dawn horizonGlow 0xa8948a, dusk horizonGlow 0x9c8478); the needle is the
   single accent (warm amber, e.g. from the day disc family 0xf0e6cc).
   Pure DOM/CSS - border-radius:50% circle + conic-gradient halves (or two
   half-disc pseudo-elements). NO new PNG assets, no textures, no canvas.
5. NEEDLE: a single line/marker pivoting at dial center, length < radius,
   transform: rotate(deg) with transform-origin at pivot; CSS transition or
   per-frame set - per-frame set from dn.timeOfDay in the existing HUD
   update path (updateHud game.js:751 family) with the dormant check.
6. PLACEMENT: top-center of the HUD (Nicko picked). Absolutely positioned,
   stays clear of: wh-bars (top-left), touch toggle (right), belt row
   (bottom).
7. MUST NOT BREAK: day/night visuals (NO look-value edits anywhere - the
   phases rows, C2/C3.1 values untouched), wake-snap, sky pools, camp menu,
   death overlay, boot overlay, save schema (NO new save fields), DayNight
   tick math, C4 save restore.

## SCOPE CONTRACT

TOUCH (exactly these):
- prototype/js/CONFIG.js - append hud.dayClock section (see PROPOSED rows).
- prototype/js/game.js - in setupHud: create the clock DOM (dial + needle)
  inside #wh-hud (do NOT edit index.html - match blockFlash/guardBreakText
  setup pattern game.js:222-240); store refs game.hud.dayClock,
  game.hud.dayClockNeedle. In the per-frame HUD update path: when dn.dormant
  -> display none; else display block and set needle rotation from
  dn.timeOfDay (angle = timeOfDay * 360 deg clockwise from top). If hp1
  landed, its per-frame bar updater exists in the same loop - ADD the clock
  update, do not restructure the loop. Day int display: NONE (ruling 3,
  "no numbers anywhere").
- prototype/style.css - #wh-day-clock: circle ~64px, conic-gradient right
  half warm amber-tinted (day), left half dark blue-grey (night), thin
  frame, pixel register (hard edges, no blur or glow), subtle inner shadow
  to sit in darkwood chrome; .wh-dc-needle: 2px warm-amber line, pivot
  center, transform rotate.
NOT TOUCH:
- prototype/js/daynight.js (read-only: dormant beginCycle nextDawn timeOfDay)
- prototype/js/camp.js, js/save.js (read-only: Save-and-Heal flow, restore)
- prototype/index.html, js/enemy.js, js/leveling.js
- CONFIG dayNight phases rows, lighting, sky pools, any look values.

PROPOSED CONFIG rows (append under hud: ~CONFIG.js:892, exact names):
  dayClock: {
    sizePx: 64,                // PROPOSED, Nicko tunes
    topPx: 14,                 // PROPOSED, Nicko tunes - #wh-hud top offset
    frameColor: '#5a5344',     // PROPOSED, Nicko tunes - same family as .bar-outer
    daySeg: '#8a6b3a',         // PROPOSED, Nicko tunes - right half tint (day, amber-muted)
    nightSeg: '#23283a',       // PROPOSED, Nicko tunes - left half tint (night, blue-grey)
    needleColor: '#d8c9a0',    // PROPOSED, Nicko tunes - single accent
    needleLenFrac: 0.42        // PROPOSED, Nicko tunes - needle length x radius
  },

## ACCEPTANCE CRITERIA (Nicko playtests)

- A1: Boot NEW GAME: no clock anywhere during the day-0 tutorial night.
- A2: First Save-and-Heal at a camp: on wake the clock APPEARS with the
  needle at TOP (wake/dawn held).
- A3: Watch it through morning->midday: the needle sweeps DOWN the RIGHT
  (amber) half clockwise; visually "day remaining" reads off the dial.
- A4: Dusk->night: needle crosses the BOTTOM and sweeps UP the LEFT (dark)
  half; night reads the same way.
- A5: Survive to the next dawn: needle is back at TOP; the day the dial
  reads stays continuous.
- A6: CONTINUE a day>=1 save: clock appears immediately at the saved
  timeOfDay position. CONTINUE a dormant day-0 save: no clock.
- A7: Day/night visuals untouched: sky, fog, light look exactly as approved
  (C2/C3.1/C2b values); wake-snap still snaps; sky pools unchanged.
- A8: Camp menu Save / Save-and-Heal / LOAD all behave as before; death
  overlay and boot overlay unaffected; no DOM in index.html.
- A9: No numbers anywhere on the clock; dial is pure CSS (no PNG, no
  textures, no canvas).

## VALIDATION LAW (no-harness gate)

- node --check on every edited JS (playwright driver node; NO game run, NO
  headless browser, NO harness).
- Greps post-build in the CURRENT bundle: 'wh-day-clock', 'dayClock',
  'PROPOSED, Nicko tunes'.
- Evidence = Nicko's playtest verdict. Nothing else.

## COMMIT + SERVING

- ONE commit: feat(hp2): day/night clock - dormant-gated circular dial with
  wake-top needle (no numbers, pure CSS, reads WH_DAYNIGHT state only,
  CONFIG hud.dayClock PROPOSED rows)
- Identity CaptainPickard <pickard.nicko@gmail.com>; push to
  origin/feat/world-visuals right after commit. Rebuild bundle BEFORE
  committing (bundle ships in the same commit).
- Flip 8793: tools/wh_release_flip.py <sha> via dhost host_exec, timeout
  >= 800s, RELATIVE releases/<sha> target; if releases/<sha> lacks
  prototype/builds/, delete husk and re-run. Verify host curl 200 + marker
  greps in the served bundle. webui /playtest-feat/ stays the live worktree.