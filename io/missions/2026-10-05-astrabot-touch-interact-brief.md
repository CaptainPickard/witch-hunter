# ASTRABOT MISSION BRIEF - Order S3b: touch INTERACT button (world-interact = pickup/gather, future chests/doors)
2026-10-05, from IO. Nicko's order (10-05, phone playtest):
- "im testing on my phone so I cant press E, I need a virtual button to 'interact'
  with the world. Pick up can bind to this. We will use this to access chests
  (Nicko: 'checked' = chests), doors etc in the future."

You are Astrabot, Claude Code print-mode agent, worktree /tmp/wh-worldfeat
(branch feat/world-visuals). Laws as always. Commit + push once. This is a
SMALL order.

## CHANGES
1. CONFIG.touch.buttons gains interact: { x, y, label } - place it adjacent to
   the right-hand cluster (attack/block/dodge at x 0.55-0.90), suggest
   { x: 0.72, y: 0.52 } or wherever it does not overlap sprint/attack on a
   phone; label 'USE' (or icon-style text - match existing button labels).
2. touch-controls.js: wire btnPress('interact') -> the SAME dispatch the E key
   runs: pickup first (game world items), then gather (nodes). The E key path
   in game.js is tryPickup() then tryGather() - route the button through one
   shared function (add window.WH_GAME_INTERACT() or a game-interior hook,
   same pattern as handButton) so keyboard, touch, and FUTURE interactables
   (chests, doors) all call one entry point.
3. Button visibility: always visible on touch like the others (no proximity
   hiding yet - prompt UX exists separately). Press feedback = same style as
   other buttons.
4. No gameplay logic changes - pickup/gather rules are untouched. The button
   IS the E key on phone.

## AC (Nicko, phone)
| AC | Test |
|---|---|
| I1 | USE button visible in the right cluster, no overlap with attack/block/dodge sprint |
| I2 | Press near an item box: picks up (same as E) |
| I3 | Press near a ready node: gathers (same as E) |
| I4 | Press with nothing in range: nothing happens (no error) |
| I5 | E on desktop still works identically (shared path, no double-fire) |

Report: appended INTERACT BUTTON section to scratch/
astrabot_stage2_drops_gather_report.md (committed). Final chat: commit sha +
placement + what to playtest.