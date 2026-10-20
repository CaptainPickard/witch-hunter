# CC-C9 · Starting bandit campfire cooks again (tutorial cooking anchor)

## 1. RULING (Nicko, 2026-10-20)
"the latest build starting bandit campfire no longer allows the player to cook
at it, and this is the one campfire that should allow that so that the player
can learn cooking and obtain the camping mechanic."

CC-C6C's night-only re-kind (io/missions/2026-10-11-cc-c6c-bandit-fires-night.md)
was over-applied to the Region B STARTING fire. The C3 world-camp ruling
(CONFIG.camp worldCamps comment, 2026-10-06) already pinned this camp: the tent
sleeps, and "The bandit fire itself stays the CONFIG.cooking station". The
starting fire is the tutorial's DESIGNATED cooking station - it must teach
cooking and arm the first-recipe -> CAMP kit moment. Not an atmospheric bandit
fire.

## 2. CHANGE
CONFIG.js cooking.stations:
- banditFire (darkwood_edge, x 2.5 z -52): kind 'campfire' -> 'cookFire'.
- banditFireA / B / C (region C): STAY 'campfire' night-only - C6C holds for them.
- Comment updates: record this ruling on the row and in the kinds block.

## 3. WHAT THIS RESTORES (all existing code paths, zero new mechanics)
- Prompt 'E - Cook'; 3s cook channel (stand still); Grave Soup learn;
  blandMush fallback on wrong trios; deadwood refuel (promptBurnt / promptLow);
  240s start fuel + passive burn with CC-C6B region-pause. All C1/C2/C4
  cookFire behavior, identical to pre-C6C.
- isLit flips from night-clock back to fuel-driven (fuel > 0 || cooking): the
  fire can burn out and be re-fed with deadwood, same as the player kit fire,
  same as before C6C. startLit still seeds 240 on fresh sessions.

## 4. SCOPE CONTRACT
TOUCH: prototype/js/CONFIG.js ONLY (one row's kind + comments).
NO TOUCH: cooking.js (kind gate stays; A/B/C unchanged), camp.js, save.js
(no station kind/fuel persisted - old saves revive banditFire as cookFire on
load, the correct target behavior), enemy.js, assets.js, index.html, tools/.
BUILD: python3 tools/build_v8.py IN THE WORKTREE; node --check CONFIG.js;
grep-verify the bundle carries the change.

## 5. VALIDATION (Nicko playtest - no harness, his playtest is the bar)
At the tutorial fire (pre-first-rest, clock dormant):
1. Prompt reads 'E - Cook' (not 'E - Warm your hands').
2. Three ingredients -> 3s channel -> Grave Soup toast + recipe learned ->
   CAMP button appears (the camping mechanic moment).
3. Deadwood on a burnt/low fire refuels ('The fire takes.').
4. Region C fires STILL show 'E - Warm your hands' + the stranger toast
   (C6C preserved there).

## 6. WATCH-ITEMS
- 240s fuel can burn out mid-tutorial if the player idles; the
  promptLow/promptBurnt -> deadwood path is the recovery (pre-C6C norm). If
  Nicko wants a never-dies tutorial fire, that is NEW tuning, not this order.
- banditFireA/B/C socket lights stay night-clock driven (unchanged C6C path).
- Supersedes the C6C watch-item "tutorial fire going dark pre-rest" for THIS
  fire only: it is lit again on fresh sessions (fuel-driven).