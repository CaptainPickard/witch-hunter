# 13 - Territory Conquest Meta (The Moving Map)

Proposed 2026-09-11 by Nicko. The dynamic system behind the Two Thrones main
struggle: how the continent's political boundaries actually move during a
playthrough.

## Core Principle (locked with Nicko)
Territory change is TRIGGER-DRIVEN and EMERGENT, not scripted-linear:
- Each hold/territory has VULNERABILITY TRIGGERS - world-state conditions
  that, when met, cause the OPPOSING faction to invade and conquer it.
- Triggers fire whether the player KNOWS about them or not: completing the
  opposing faction's required quest flips the territory, but so does
  ACCIDENTALLY killing the king or the main noble of a hold. The world does
  not care whether you meant it.
- "You either complete the required quest from the opposing faction or
  complete the objective regardless without knowing it" - both roads lead
  to conquest. Deliberate strategy and emergent accident produce the same
  world movement, which makes the world feel alive and consequential.
- The player should DISCOVER that this system exists through play
  (exploration-based): rumors, refugees, map changes, patrol shifts. The
  conquest rules are discoverable knowledge, not a UI tutorial.

## Trigger Anatomy (first pass)
Every hold has a stability model with discoverable vulnerability conditions:
1. SUCCESSION CRISIS: the hold's ruler (king, lord, matriarch) dies. The
   opposing faction claims the vacuum -> invasion window opens. Killing the
   main noble of a hold is the canonical accidental trigger.
2. DECIMATION: the hold's garrison/military strength falls below a threshold
   (player destroys patrols, clears forts, drains resources via quests
   completed for the other side).
3. LEGITIMACY LOSS: the hold's populace/factions turn (player completes
   quests that undermine the ruling family - smear, famine relief diverted,
   heir scandal).
4. SIEGE EVENT: the opposing faction masses forces (visible: war camps on
   roads, war councils in taverns, refugee flows). The player can join the
   siege on either side.
- A triggered hold enters INVASION WINDOW state for some days: the opposing
  faction's armies mobilize; the player can defend (side with the current
  ruler) or enable (side with the invaders) or ignore (the map moves
  without them).

## What Changes When a Hold Flips
- Political boundary on the map moves; the hold's banner changes.
- Occupying garrisons/patrols change; enemy types in the wilds shift.
- Prices, taxes, safe roads, tavern rumors change.
- Minor noble families of the losing side flee, die, or bend the knee
  (retinue/quest hooks).
- Player's faction standing with both courts shifts; the moral axis may
  drift from the act itself (massacre = evil deed regardless of which side
  benefited).
- QUEST AVAILABILITY reshuffles: the new ruler's questline replaces the old.

## Reconquest and the Living Nobility (locked with Nicko, 2026-09-11)
- YES, HOLD FLIP BACK: reconquest is real. There is a genuine, ongoing
  power struggle - no conquest is permanent. A flipped hold can be taken
  back by its original court (or by anyone), and taken again. The map is
  contested ground for the whole playthrough.
- CONQUEST REWARDS - LAND GRANTS: flipped holds can be GIVEN to the leaders
  of the victorious conquest. This makes the nobility layer of the game
  PROCEDURALLY GENERATED: different Sirs, names, and clans rise and fall as
  they gain power with their political faction, win, and lose.
- A LIVING, BREATHING WORLD that can be lived in: noble houses have
  lifecycles (rise with victory, fall with defeat), so the political cast
  is never static. New minor families appear as fortunes shift; defeated
  clans fade, flee, or rebuild elsewhere.
- Design intent: the player can be part of this cycle - a successful player
  leader can rise from nobody to hold-holder to clan-founder; a player who
  backs the losing side can watch their patron's house collapse.

## IO Proposals (ideas from IO - unconfirmed, for review)
A. THE MAP READS LIKE WEATHER: a war-torn hold shows smoke columns, refugee
   columns on roads, war-camp sprites, burned farmsteads; a conquered hold
   under new rule flies the new banner and has new patrols. Exploration is
   how you READ the strategic map without a politics UI.
B. RUMOR ECONOMY: taverns are the intel hub (ties into 03-world taverns).
   Rumors reveal trigger states ("the old lord's health fails," "the
   garrison is half its strength," "the vampire court sends envoys to
   Duke X"). Buying rumors = planning conquest; selling intel = neutral
   court gameplay.
C. ESCALATION LADDER per hold: rumors -> patrols thin -> border skirmishes
   -> siege -> conquest. The player can intervene at any rung. Early-rung
   interventions are cheap (deliver supplies, warn the lord); late-rung
   interventions are dramatic (assassinate the invader's general, break a
   siege).
D. PLAYER-HELD HOLDS: if the player aids a conquest decisively (kills the
   lord personally, leads the siege), the grateful throne may GRANT the
   player a hold - tying the conquest meta to the warp camp system (a
   conquered hold could become the ultimate warp-camp site, or the player
   becomes its minor nobility).
E. DOMINO RULE: adjacent holds with low stability can cascade (a fallen
   hold destabilizes its neighbors). Creates natural campaign arcs without
   scripting.
F. TOTAL DOMINATION ENDGAME: if one throne conquers ALL holds, the world
   enters a NEW STATE (not a credits roll): a fully dark world (vampiric
   sun, undead patrols, inverted economy) or a fully light world (the
   blighted zones cleansed, new cities founded). The game continues in the
   winner's world; the endgame is a changed world, not a credits roll.
G. COUNTERWEIGHT: the loser's court gets desperation mechanics (dark
   rituals, conscription, last-stand buffs) so comebacks are possible and
   late-game stays tense.
H. RETINUE AS ARMY: late-game conquest actions could use the retinue
   (guards, orc mercenaries) as the player's own war party - the retinue
   collection loop pays off in the conquest meta.

## RULING PASS (open-questions sweep, 2026-09-14, Nicko)
HOLD DEFENSE: EVENT-BASED DEFENSE. The player cannot garrison a hold
personally; defense plays as triggered events when doc 13's war
engine targets a hold the player is allied with. Warning window
(Veil-Tide forecasting, tavern rumors) then choose: defend (a timed
battle event with the retinue) or skip (the hold may fall, map reads
it). No stationed-garrison mechanic; retinue deployment stays doc
23's expedition layer.
## Open Questions (status as of the 2026-09-11 second sweep)
1. Hold count: RESOLVED (20-30 holds, each a real place: noble family,
   tavern, dungeon cluster).
2. Reconquest: RESOLVED (YES - map is contested ground; procedural
   nobility rises and falls with conquest; land grants to victors).
3. Off-screen resolution: RESOLVED (triggers resolve off-screen;
   consequences witnessed on arrival).
4. DEFENSE of holds the player cares about: STILL OPEN (defend quests,
   hired garrisons, retinue deployment) - quests GDD item.
5. Pace: RESOLVED (background slow-burn war, stalemate by default,
   accelerated/tipped by player).
6. Regicide: RESOLVED (cascade only with no suitable heirs; alternate
   routes: defense destabilization, famine/economic warfare).
7. Neutral-court war profiteering: STILL OPEN (lean: yes - mercenaries
   and smugglers sell to both sides; gives neutral players a wartime arc)
   - quests GDD item.
8. Procedural nobility generation rules: PARTIALLY RESOLVED via doc 14
   (race-flavored naming, marriage race-shift, player founds with own
   name); remaining: name pool depth, heraldry generation, clan lifecycle
   depth - world GDD item.
9. Comeback events: RESOLVED (mass demon summon / divine intervention).
   OWNERSHIP ADDENDUM 2026-09-14 (Nicko, doc 44 Part 5B): both
   comeback events are THE WITCH'S MACHINE. The demon summon (dark
   bankruptcy) is her creditor enforcement; the Blessed Host (light
   divine intervention) is HER SURGE, called through a Church her
   compelled queen rules: salvation in effect, harvest in purpose.
   Three comebacks (Last Dance / demon invasion / Blessed Host), one
   farmer (doc 44).