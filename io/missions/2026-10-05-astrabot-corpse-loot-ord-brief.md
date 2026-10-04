# ASTRABOT MISSION BRIEF - Order S4: corpse loot container (unlooted corpse = gold glow + rising sparks; boxes RETIRED for enemy drops)
2026-10-05, from IO. Nicko's order (10-05 stage-2 playtest):
- "Instead of the corpses dropping actual boxes, can we not present an unlooted
  corpse with goldfish glow [gold-ish glow] and some spark like effects slowly
  rising from it. And when a corpse has been fully looted this effect goes away
  and there is no longer anything to open at the corpse? This seems much better."
- Ruling confirmed: enemy drops live ON THE CORPSE as a loot container. The
  boxes remain ONLY for player G-drops (dropped = an item lying on the ground;
  killed = loot the body).

You are Astrabot, Claude Code print-mode agent, worktree /tmp/wh-worldfeat
(branch feat/world-visuals). Laws as always (no harness/headless, CONFIG-driven,
commit+push per sub-block, report). Small-medium order.

## 1. DESIGN (binding)
1. Enemy death: the S1 drop ROLL is unchanged (guaranteed 1x stolenCoin +
   20% weighted bonus) but the result is STORED ON THE CORPSE as
   enemy.corpseLoot = [{id, count}, ...] instead of spawning WorldItems.
   No boxes from kills, ever.
2. UNLOOTED presentation while corpseLoot is non-empty:
   - A soft GOLD glow: additive billboard sprite behind/over the corpse,
     gold-amber (CONFIG color, gold = coin/human accent, 0xd8b2.. family),
     gentle pulse (CONFIG seconds), scale ~ the torso.
   - SPARKS: small unlit motes rising slowly from the body (random drift,
     fade out at top), recycled pool PER ACTIVE corpse, CONFIG count/rate/
     speed/size/color. Cheap: no lights, no materials allocation per frame.
   - NO PointLight on corpses (light budget stays: 4 pool + flame cards).
     The glow sprite must read at night on its own - additive blending.
3. LOOTING: the interact() chain gains a corpse step: tryPickup() ||
   lootCorpseNearest() || tryGather() (ground boxes first - your drops -
   then corpses, then nodes). lootCorpseNearest(x, z, radius): nearest unlooted
   corpse in radius; transfers ALL corpseLoot entries through
   inventory.addItem (stack-join rules); entries that do NOT fit stay in the
   corpse (partial loot: corpse stays glowing until empty); toast per transfer
   batch summary (e.g. 'Looted: Stolen Coin x1'); corpse becomes looted when
   its list empties: glow+sparks STOP (fade out ~0.5s) and the interact step
   skips it forever after.
4. Prompt: reuse the gather-prompt UI pattern - near an unlooted corpse show
   'USE - Loot' (touch/desktop same wording; E and USE both route the chain).
5. Corpse lifetime rule (playtest): when the corpse is removed (region
   rebuild/reset), unlooted loot goes WITH it (vanishes). A CONFIG comment
   marks where the real-game persistence story will attach later.

## 2. CURRENT MECHANICS (verified - do not re-research)
- enemy.js: death path settles corpse via corpseFinalY (~124-145); corpse
  persists as the enemy object's root in the region list.
- game.js: scheduleDrops is wired via window.WH_Enemy.onKilled (line ~952);
  currently spawns WorldItems after CONFIG.drops.spawnDelaySec. REPLACE this
  path with the corpse-loot storage; the S1 roll helper (CONFIG.drops weights)
  is reused as-is. interact() at ~965: tryPickup() || tryGather() (touch USE
  + E share it). Gather prompt element: wh-gather-prompt (~196) - reuse its
  pattern for the loot prompt (or generalize the element, your call, report).
- WorldItems/G-drop flow: UNTOUCHED (player drops stay boxes; pickup first
  in the interact chain).
- Light budget law sits in CONFIG.playerLight - do not exceed it.

## 3. CONFIG additions (CONFIG.corpseLoot)
{ glowColor, glowPulseSec, glowScale, sparks: { count, riseSpeed, drift,
  lifetimeSec, size, color }, lootRadius: 1.6, promptText: 'USE - Loot',
  fadeOutSec: 0.5 } - plus CONFIG.drops gets a comment: 'drops are stored on
  the corpse; boxes are player G-drops only'.

## 4. AC (Nicko playtests)
| AC | Test |
|---|---|
| C1 | Kill: NO boxes; the corpse glows gold with sparks rising, gently pulsing |
| C2 | USE/E near the corpse: 'Looted: Stolen Coin x1' (+bonus when rolled); glow+sparks fade, corpse is plain again |
| C3 | Inventory full: loot refuses (toast), corpse STILL glowing with remaining loot |
| C4 | Partial: full inventory takes what fits - loot again after freeing space takes the rest, then the effect ends |
| C5 | G-drop of any item still spawns/picks a box (your flow unchanged); pickup wins when both a box and a corpse are in reach |
| C6 | Node gathering unchanged (corpses win over nodes in the chain when both near) |
| C7 | No new PointLights in the scene (light budget identical); glow reads at night |
| C8 | No boot warnings; no latch/locomotion regressions (kill during walk resumes walking) |

## 5. Report
Append CORPSE LOOT section to scratch/astrabot_stage2_drops_gather_report.md
(committed). Final chat: commits with shas, AC table, knobs, undone items.