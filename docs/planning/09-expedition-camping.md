# 09 - Expedition and Camping (Partial Survival)

Proposed 2026-09-11 by Nicko. This doc captures the expedition-preparation
loop: partial survival mechanics layered on top of the tavern save system.

## Design Intent
Make expeditions into the far wilderness a self-contained preparation loop.
Towns/taverns are the hub; the road and the deep dark are the expedition.
Camping is the field answer to healing and rest - the bridge between "you are
safe in town" and "you are deep in blighted territory with no tavern for a
day's travel."

## The Two-Tier Rest System
1. TOWN (tavern): full service. Restores everything, cures all ailments,
   sets your respawn point (rent a room), restocks supplies, buys/sells,
   crafting stations, faction contacts. This is where expeditions are
   planned and launched.
2. CAMP (wilderness): partial service. Laying out a bedroll or tent and
   camping for the night restores health and stamina over time and cures
   short-term ailments (fatigue, mild cold, small debuffs). It does NOT
   replace the tavern: it does not set your respawn point (or only under
   specific conditions, see Open Questions), it heals slower, and it has
   costs and risks the tavern does not.

## Why This Loop Works
- The weight-based inventory becomes a real expedition constraint: every
  bedroll, tent, torch bundle, and ration competes with loot for carry
  weight. Going deep means deciding what you can afford to bring back.
- Preparation becomes gameplay: buying supplies, choosing gear, reading the
  map for defensible camp sites, and timing departures (leave at dawn, not
  at dusk).
- The fixed-difficulty world gets a pressure valve without softening: instead
  of scaling enemies down, the game lets you PREPARE harder to reach harder
  places.
- Night becomes meaningful: camping is when the world's night dangers (see
  03-world day/night question) finally have teeth.

## Camping Mechanics (first pass)
- Camp kit tiers: Bedroll (light, fast, minimal healing), Tent (medium,
  full night rest), Expedition Kit (heavy, full rest + ailment cure + buff).
- Camp requires: a defensible or hidden site (terrain matters), flint/firewood
  for a campfire (fire = healing speed and cooking), food (accelerates
  recovery, grants morning buffs).
- Campfire cooking: raw ingredients become simple meals; better ingredients =
  better morning buffs. Feeds the alchemy/cooking skill space (see Open
  Questions).
- Site selection: camping near ruins/roads is faster but riskier; deep woods
  is safer from patrols but closer to beast territory. A light risk-reward
  read of the terrain.
- Night events: campsites can attract wandering threats (wolves, bandits,
  worse). The camp encounter is the game saying "you chose to sleep HERE."
- Weather interacts: rain kills fires and slows recovery; cold biomes demand
  the tent tier minimum. (Weather doc lives in 03-world.)

## Save and Respawn Interaction (proposed)
- Camping SAVES the game (autosave on completing camp) but does NOT move your
  respawn point. Death still sends you to the last tavern where you rented a
  room. This keeps taverns as the anchor while removing the "lost two hours
  of progress to a single mistake" feel-bad.
- Alternative (harsher, more Daggerfall): camping heals but does not save;
  saving is tavern-only. Harsher but purer.

## Loop Summary
Plan at the tavern -> buy/carry supplies -> travel at fixed danger -> camp to
sustain the push -> fight deeper -> carry loot back (or stash it) -> return
to town to sell, craft, save, and plan a bigger expedition.

## Open Questions
1. Does camping save the game, or is saving tavern-only? RESOLVED
   2026-09-11: camps save, taverns remain respawn points; unlocked warp
   camps become the default forward respawn (taverns still usable).
2. Can camping ever set a respawn point? RESOLVED 2026-09-11: the unlocked
   warp camp becomes the forward respawn (default), taverns still usable.
3. How deep do survival needs go? RESOLVED 2026-09-11: food is buff-only,
   never required; certain camp gear IS required to camp. See
   10-cooking-meals-drinks for the food buff system.
4. Camping inside dungeons? RESOLVED 2026-09-11: OVERWORLD ONLY.
5. Does cooking become its own small skill line? RESOLVED 2026-09-11: YES,
   Cooking is its own skill line. See 10-cooking-meals-drinks.
6. Camp gear durability: RESOLVED 2026-09-11: gear can be destroyed in
   night ambushes (the tent you sleep in is safe).
7. Time cost: RESOLVED 2026-09-11: night skips ONLY on interacting with
   the bedroll/bed to sleep; the player can stay up cooking/interacting
   freely - sleeping is the day-restart mechanism (mornings = consume
   the day's meal/drink).