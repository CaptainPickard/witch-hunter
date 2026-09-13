# 35 - Slice Systems (HUD/UI, Inventory, Save, Economy, Death Edges)

Status: PROPOSED (Astrabot hard-numbers pass, 2026-09-13). G11-G15
rulings LOCKED by Nicko, 2026-09-13 (see sections below; squire
per-level increment and G13/G14/G15 leftovers stay open). Remaining
tuning PROPOSED.

Closes gaps G11-G15 from 30-prototype-gap-analysis.md at slice-1 depth.
Every number is PROPOSED, not locked. Shared scales: health 300-1500,
stamina 80-160, damage 1-999 per hit, stats 1-99, tiers T1-T5, grades
C/B/A/S, currency integers. Docs 31-34 (slice scope, controls/frame
data, equipment/formulas, enemy AI/bestiary) are parallel, named only.

## G11. HUD AND UI SPECIFICATION

Inherited: 02-art-style.md locks "modern Souls-style, clean menus,
diegetic touches where cheap," the character menu carrying the moral
axis. 04-combat-system.md makes readability the fairness contract: the
HUD must read player state as well as enemy telegraphs.

### HUD layout (proposed)
- Top left, stacked: health, stamina, Focus bars. Focus bar hidden for
  non-casters, renders when Focus first becomes relevant (LOCKED by
  Nicko, 2026-09-13). Flat fill, one accent each, no gradients.
- Health: damage paints a pale "recent damage" tail decaying over 1.5
  seconds, then the fill recedes. Heals snap above 50 percent, animate
  below.
- Stamina (80-160 scale): flashes the danger accent below 25 percent. The
  stamina-breaked state (04) shatters the bar into three segments that
  rejoin as regen restores it. The ~1 second regen pause (04) dims the bar
  edge so players read the pause without a timer.
- Poise is NOT a bar on any HUD. Stagger animation is the read. Cheapest
  rule that still honors the fairness contract.
- Buff/debuff icons: max 5, under the bars, duration ring each. Doc 10
  meals, doc 09 buffs, doc 17 wards land here.
- Bottom right: 4 quick-use slots, cycling cursor, never a combat pause
  menu.
- Bottom center: interaction prompt, one verb plus one noun.

### Boss bar
Bottom center on lock-on with a named boss. Health fill plus a thin poise
bar beneath (poise shown only for boss-scale bodies; their staggers are
the encounter's rhythm). No phase pips; phases read via behavior per 04.

### Damage numbers policy
LOCKED by Nicko, 2026-09-13: OFF for hits on the player, ON by default
for player hits,
integers 1-999, small hits stacking into one rolling number. Numbers on
incoming hits push players to watch bars instead of telegraphs, breaking
the 04 contract. Crits get larger size and the danger accent, no color
change. Options toggle (30 G33).

### Menus (slice-1 set)
- INVENTORY: list view (G12), weight-descending sort, context menu (use,
  equip, drop, compare).
- CHARACTER: nine stats (1-99, 07), the single visible moral axis
  (11-warp-camp.md), titles with retention rules (07).
- FOLLOWER: 23-expedition-followers.md's menu, camp/tavern only at
  slice 1 (LOCKED by Nicko, 2026-09-13).
- MAP: abstract parchment; 13-territory-conquest.md's weather-map defers
  past slice 1.
- Spell/technique selection: attunement in menus; in-combat use goes via
  the quick-slot cycle. No radial menu in slice 1.
- Pause menu allowed (single-player), stops simulation.
- Diegetic ruling per 02's "where cheap": camp UI (09) and tavern save are
  diegetic, the rest abstract. One diegetic touch per screen.

Open questions (owner: Nicko): all three answered, LOCKED by Nicko,
2026-09-13 (damage numbers ON player hits / OFF incoming; Focus bar
hidden for non-casters; follower menu camp/tavern only). No open items
remain in G11.

## G12. INVENTORY MECHANICS

Inherited: 06-loot-and-resources.md locks Daggerfall-style weight-based
inventory, Carry Weight one of the nine stats (07), NOT slot Tetris.
11-warp-camp.md locks the valet as instant access to all camp chests;
23-expedition-followers.md gives the squire an overflow pool.

### Model (proposed)
- One pool, weight-ruled, with list filters (Gear, Consumables, Materials,
  Quest). Equipped gear is excluded from carried weight; it adds to EQUIP
  LOAD instead (04's separate combat-side weight), so the two weights never
  double-count.
- Capacity in weight units LOCKED by Nicko, 2026-09-13: 100 + Carry
  Weight x 2.5 (stat spans 1-99): 125 at base, ~350 at max.
- Quest items sit in a zero-weight quest pocket (LOCKED by Nicko,
  2026-09-13).
- Slot counts: 8 weapons max carried (2 in hands), 10 armor pieces worn
  per doc 27's visual layers, 4 quick-use slots, 3 attunement slots in
  slice 1.
- Stack rules: reagents/materials 99; arrows and bolts 50 per payload
  type (30 G29 wires the quiver later); food and drinks 10; potions 20;
  gear never stacks (rarity, tier, grade make each piece unique, 06).
- Overflow at zero headroom: pickup refused with a weight readout, never
  a forced drop. Squire overflow scales with squire level: base +150
  units at level 1 (23), plus a per-level increment PROPOSED at +15 per
  squire level (PROPOSED tuning, locked by Nicko 2026-09-13 as
  level-scaling with the increment number still to tune); squire items
  are lost only if the squire dies (G15). The valet (11) is the only
  instant-transfer surface, camp-only.
- Ground loot: all props render as sprites (06 locked), so drops spawn a
  small glow sprite plus a name label on aim, no physics. Despawn: 30
  in-game minutes in the field, forever in dungeons (03 persistence) and
  warp camp chests.
- Comparison UI: two-column delta on hover (weight, damage or armor, tier
  gate). Grade letters C/B/A/S as suffix; doc 33 defines grade math.

Open questions (owner: Nicko): all answered, LOCKED by Nicko,
2026-09-13 (capacity = 100 + Carry Weight x 2.5; quest items in a
zero-weight quest pocket; squire overflow scales with squire level,
base +150 at level 1, per-level increment PROPOSED at +15, tuning
open). No open items remain in G12.

## G13. SAVE AND PERSISTENCE

Inherited: 04-combat-system.md locks tavern-based save/respawn and camp
saves. 09-expedition-camping.md RESOLVED: camps save on completion,
taverns stay respawn points, unlocked warp camps become the default
forward respawn, camping is overworld only. 03-world-design.md locks
persistent procedural dungeons.

### Save triggers (complete for slice 1; ruling 8 below locked by
### Nicko, 2026-09-13)
1. Tavern room rental (save plus respawn point, 04).
2. Camp completion, morning of the camp (09).
3. Warp camp summon (11, Tier 1 saves the game).
4. Dungeon exit transition (dungeon cleared state writes on leaving).
5. Menu quit (full save, respawn point unchanged).
6. DEATH IS NOT A SAVE EVENT. Death writes the corpse position and drop
   as a delta to the existing save, nothing else. Reloading after death
   puts you at the last save with the corpse still in the world, which is
   what makes the run-back matter.
- No timed autosave and no region-transition autosave in slice 1.
- The dungeon-clear delta is written ONLY at the dungeon EXIT trigger
  (trigger 4), never at camp saves (LOCKED by Nicko, 2026-09-13).

### Save data model (proposed)
Single world blob for static state (dungeon seeds, 03) plus per-system
deltas: inventory, ledger fields (20), node respawn timers (06's 2-3 day
rule), vendor stock, camp build state, follower rosters, quest flags.
Vendor stock and NPC positions persist across save/load; restock runs on
the 2-3 day node clock. On death, the currency drop and corpse marker
persist through reload. Enemies killed after the last save are restored
alive on reload, bosses included, standard souls behavior.

### Checkpoint grammar consistent with doc 09
Tavern = full anchor: save, respawn point, full service. Warp camp =
forward anchor: save, default respawn, partial service. Wilderness camp =
save only, respawn point unchanged. Slice 1 has no warp camp yet, so the
grammar is tavern-anchor plus save-only camps. Resting at any anchor
respawns regular world enemies; dungeon layouts persist (03) but
inhabitants respawn on rest, except dungeon bosses.

Open questions (owner: Nicko): 1 answered, LOCKED by Nicko,
2026-09-13: the dungeon-clear delta writes only at the dungeon EXIT
trigger, never at camp saves. Remaining open:
2. Does the squire overflow pool save with party state or player inventory?
3. NG+ world reset (07, 12) needs a preserve-list; proposed: warp camp,
   follower rosters, ledger deed log. Confirm.

## G14. CURRENCY AND ECONOMY

Inherited: 00-README-index.md decision 4 locks a souls currency drop on
death. 06-loot-and-resources.md locks three vendor families (light, dark,
neutral brokers) and requisition contracts paying standing plus coin.
04-combat-system.md locks NO ITEM REPAIR, so no repair sink.

### Currency (LOCKED by Nicko, 2026-09-13)
SILVER MARKS, one integer pool, no subdivisions. Single neutral
currency, no faction-flavored variants. Docs 31-34 should use "marks"
in tables.

### Drop rates (proposed, layered on 06's four-layer tables)
Layers 1-2 (parts, materials) carry no currency value; monster-part-first
means parts feed crafting, not the purse. Currency comes from humanoid
kills, chests, and sales only. Humanoid kill bands per region tier: T1
2-8 marks, T2 5-15, T3 12-40, T4 30-90, T5 60-200. Beasts and undead
drop parts plus 0-3 marks. Boss bounties, flat: 150 / 400 / 1000 /
2500 / 6000 marks at T1-T5. Chests: 20-60 marks at T1-2, x3 per tier
above.

### Vendor baseline prices (proposed)
- Tavern room rental (the save/respawn cost, 04): 25 marks.
- Tavern meal (10's WELL-FED convenience tier): 8 marks.
- Rumor/intel: 50 base, 200 for den-key tier (05's "expensive" hook; 10's
  ledger-page meal grants one free).
- Follower hire, one-time (11's no-upkeep rule): 500 marks T1 quality,
  1500 T2, 5000 T3. Follower gear is the real sink (23).
- Potions: 15 minor, 40 standard, 120 greater.
- Gear: T1 weapon 100-200, T2 400-800, T3 1500-3000, T4 6000-12000, T5
  relics quest-only, never sold (06).
- Repair costs: NONE (04 locked). Late money buys T4/T5 gear, follower
  gear and hires, camp structures and defenses (11), intel, consumables,
  requisition standing. Thin at endgame; see open question 2.

Open questions (owner: Nicko): 1 and 2 answered, LOCKED by Nicko,
2026-09-13: the currency is Silver Marks, single neutral (no faction
scrip), and camp construction is the primary late-game money sink, no
new sink doc. Remaining open:
3. Do dark vendors refuse light-tainted currency, or is one currency
   universal (proposal: universal)?

## G15. DEATH AND RESPAWN EDGE RULES

Inherited: 04-combat-system.md locks death dropping XP/currency
recoverable at the corpse, tavern respawn. 09-expedition-camping.md and
11-warp-camp.md make the unlocked warp camp the default forward respawn.
10-cooking-meals-drinks.md locks corpse-recovery insurance redirecting the
NEXT death's drop to the tavern. 22-quests-factions-gdd-part3.md locks
that strain death rites do not change the penalty; undead players still
drop and recover at the corpse. 23-expedition-followers.md locks
permanent follower death, camp mourning and blame.

### Core run-back rule (death penalty LOCKED by Nicko, 2026-09-13)
- Death drops unspent currency and 25 percent of current-level XP
  progress
  at the corpse. Health, stamina, inventory, gear, follower roster: all
  untouched. The whole penalty; no durability (04), no stat damage, no
  item loss.
- Corpse marker: a pale light sprite at the drop point, visible through
  fog at 40 meters, no map icon in slice 1 (finding it is the game).
- Corpse despawn (LOCKED by Nicko, 2026-09-13): ONE corpse on the
  field; the NEWEST drop replaces the older corpse permanently, its
  drop LOST. Dying again dissolves
  the previous corpse, its drop LOST permanently. One corpse on the field
  at a time, harsher than two-corpse variants, which is what gives 10's
  insurance meal its value as the mercy valve.
- The insurance meal (10) redirects the drop to the last tavern counter
  instead of a corpse; a redirect death still dissolves any older corpse.
- Recovering the drop restores currency and the XP fraction. Resting at
  an anchor does not remove the corpse (no free soft reset).

### Edge cases (proposed rulings)
- Dying inside a camp raid: the drop lands at the camp center; the camp
  stays summoned (11) and the run-back is into your own defense, whose
  enemies a live raid has already respawned.
- Dying with the squire holding overflow: squire items are not dropped and
  not lost on player death. They are lost only if the SQUIRE dies, per
  23's permadeath. Keeps the squire strictly safer than the player,
  matching 23's behavior intent.
- Player corpse loot is separate from NPC corpse loot (06's grave goods)
  and carries no light-court reputation cost.
- Dying during a spine/transformation stage: death restarts the current
  STAGE, never the chain (22 locks the penalty shape; stages are the
  checkpoint grain).
- Repeated-death softlock: none needed mechanically (the drop persists
  until a newer death), but a 3-death streak with no recovery flags a
  hint line at the tavern. Pure readability aid, no cost.

Open questions (owner: Nicko): 1 and 2 answered, LOCKED by Nicko,
2026-09-13: one corpse on the field (newest drop replaces the older
permanently) and the death penalty is currency plus 25 percent of
current-level XP. Remaining open:
3. Does a camp-raid death also dissolve a corpse outside the camp, or
   does camp-center drop replace it?

## Verification hooks
Slice-1 acceptance: HUD reads bars, buffs, quick slots, one prompt line;
inventory survives overflow, stacking, and squire cases; save triggers 1-6
replay a camp plus tavern loop; a T1-T2 loop closes (earn 200 marks, buy
room, meal, potion, hire); death, run-back, corpse dissolve, and insurance
redirect all demonstrable in-engine.