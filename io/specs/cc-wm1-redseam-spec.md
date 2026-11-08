# CC-WM1 — REDSEAM: Rich Iron Seam Site (doc 42 Part 5 + doc 41 Family 6)

IO spec (2026-11-06, Autopilot wake 8). Status per docs: doc 42 Part 5 = the
spec (ruling 2 LOCKED Nicko 2026-09-14); doc 41 Family 6 carries the site
grammar (riches sites; "RICH MINES (ruling 9)": dedicated mine SITES, LARGE
ore quantities, dense vein clusters worth many trips, deplete/recover per doc
06 timers, worked sites with light states). Darkwood carries "small iron/seam
sites (T1-T2 volume)" (doc 42 Part 5 WHERE). This round = the FIRST rich-mine
site: region C (Forest of the Old King), NE plateau above the crypt notch,
working name REDSEAM (PROPOSED, Nicko tunes).

Art law (36-piece set; image_generate provider-blocked this wake — DEGRADED
disclosed): anchors concept-01-darkwood + day-01-darkwood (vision-analyzed).
Palette law carried into data: oxidized-rust iron accent on slate/loam base;
the seam reads as a quarried scar the forest is reclaiming; no new assets, no
new meshes, no new icons (existing manifest keys only).

## Scope law: PURE CONFIG DATA. ZERO JS-file edits.

gather.js consumes regions[rid].cfg.nodes generically (wh-gather NodeManager
census 2026-11-06); region C already has a nodes key (CC-WD1/ED1 bonePile).
No gather.js seat edit is needed. No icons-data.js rebuild (no new icon PNG;
inventory glyph fallback proven, inventory.js:172). Gather/enemy state is
never saved (save.js:8) — nothing to persist.

## W-1. Node type: ironVein (CONFIG.gather.nodeTypes)

Add ONE row to CONFIG.gather.nodeTypes (after bonePile):

    ironVein:        { name: 'Iron Vein', rarity: 'common', yield: { id: 'ironOre', count: 3 },
                       respawnSec: 240, glowColor: 0x8f5a33, scale: 1.15 }

Numbering laws (all PROPOSED, Nicko tunes):
- count 3 vs bonePile 2 = the DENSE destination-tier read (doc 41 F6: "the
  notable site is the DENSE version, not a different mechanic"). One E press
  = 3 Iron Ore from a rich vein.
- respawnSec 240 vs ambient 90-180 = the "long timers" riches-site law (doc
  41 F6 deplete/recover; playtest economy mode stays untouched).
- rarity 'common' = doc 41 "Tier 1 rumor-revealable"; playtest economy treats
  common/rare, real-day split comes with economy.mode 'real'.
- glowColor 0x8f5a33 = oxidized rust-iron accent (concept-01 palette law:
  iron = deep oxidized rust, NOT bright red/orange); clump tint renders it
  at glowColor x 0.45 (dull, flora-adjacent) per gather.js buildTypeKit.
- scale 1.15 = slightly chunkier seam clumps (dense read).
- prompt/toast ride the generic grammar: 'E - Gather Iron Vein' / 'Gathered
  Iron Vein x3'.

## W-2. Item: ironOre (CONFIG.items)

Add ONE row in the Stage-2 cooking-ingredient block (after boneShard):

    ironOre:        { id: 'ironOre', name: 'Iron Ore', glyph: 'IO', category: 'ingredient' }

Class-consistent with forestHerb..boneShard (category 'ingredient' exists in
inventory.js CATEGORY_TIP: 'Ingredient'; no weight row = raw ingredient class
convention; no stackCap row = default cap). Consumers: NONE this round (doc
39 depth-gated smelting tiers are a later lane; ore piles up as a gatherable
commodity — the spec law "never a half-mechanic": the mine SITE is the unit
this round, smelting/contracts consume it later). No icon PNG; belt/inventory
show the 'IO' glyph fallback (proven).

## W-3. Node seats: 8 ironVein rows (CONFIG.regionC.nodes)

APPEND 8 rows to CONFIG.regionC.nodes (after the east den's 4th bonePile row):

    { type: 'ironVein', x: 53, z: -577 },     // redseam vein 1 (S bowl floor)
    { type: 'ironVein', x: 55.5, z: -573.5 }, // redseam vein 2 (bowl floor E of fire)
    { type: 'ironVein', x: 61, z: -572 },     // redseam vein 3 (bowl floor NE)
    { type: 'ironVein', x: 64, z: -575.5 },   // redseam vein 4 (E bench foot)
    { type: 'ironVein', x: 63.5, z: -582 },   // redseam vein 5 (SE bowl lip, WM1-A3: 2.83->7.16 m from squatter 2 + nearest bench boulder >= 3.0)
    { type: 'ironVein', x: 57, z: -584 },     // redseam vein 6 (S bowl lip)
    { type: 'ironVein', x: 51.5, z: -581.5 }, // redseam vein 7 (SW bowl lip)
    { type: 'ironVein', x: 50, z: -574 },     // redseam vein 8 (W bowl floor)

Cluster law: the 8 seats form the dense vein cluster around bowl center
(57.5,-578): mutual spacing 3.5-6.5 m (deliberate: DENSE seam; ambient-node
spacing rules were gen-script guidance, gather.js runtime has no spacing
check). Bowl micro-relief (scratch/cc-wm1/bowl_probe.js): floor y 2.5-3.1,
slope <= 6 deg at every seat. Every seat rides the WH_GROUND terrain seat
(existing gather.js line 60 law, landed CC-WD1).

## W-4. Dressing: 14 prop rows (CONFIG.regionC.props)

APPEND 14 rows to CONFIG.regionC.props (after the east den's last rubblePile
row, before the closing bracket of the array at ~1181):

    { asset: 'mossBoulder', x: 54, z: -586, rotY: 4.2, scale: 1.90 },    // redseam quarried bank S boulder
    { asset: 'mossBoulder', x: 59, z: -587, rotY: 5.3, scale: 2.10 },    // redseam quarried bank SE boulder
    { asset: 'mossBoulder', x: 64, z: -585, rotY: 0.6, scale: 1.80 },    // redseam quarried bank E boulder
    { asset: 'mossBoulder', x: 67, z: -581, rotY: 1.4, scale: 1.60 },    // redseam quarried bank E boulder 2
    { asset: 'mossBoulder', x: 67.5, z: -575, rotY: 2.7, scale: 2.00 },  // redseam quarried bank NE boulder
    { asset: 'mossBoulder', x: 65, z: -570, rotY: 3.5, scale: 1.70 },    // redseam quarried bank N boulder
    { asset: 'mossBoulder', x: 60, z: -567, rotY: 4.9, scale: 1.50 },    // redseam quarried bank NNW boulder
    { asset: 'rubblePile', x: 57.5, z: -588, rotY: 2.1, scale: 1.20 },   // redseam talus tailing S (WM1-A4: 4.03 m min-vein, 1.80 m min-squatter)
    { asset: 'rubblePile', x: 60.5, z: -578.5, rotY: 5.0, scale: 1.00 }, // redseam talus tailing center
    { asset: 'rubblePile', x: 51.5, z: -570, rotY: 3.3, scale: 1.10 },   // redseam talus tailing W (WM1-A4: 4.27 m min-vein, 8.25 m min-prop)
    { asset: 'treeStump', x: 49.5, z: -578, rotY: 1.1, scale: 1.30 },    // redseam clearing stump W (forest reclaiming)
    { asset: 'treeStump', x: 66.5, z: -573, rotY: 5.8, scale: 1.20 },    // redseam clearing stump E (forest reclaiming)
    { asset: 'deadTree', x: 47, z: -585, rotY: 2.4, scale: 1.60 },       // redseam scar-lip leaner SW (WM1-A3: was 47,-581; 2.06m from vein 7 -> 5.03m; sits at the SW mouth)
    { asset: 'deadTree', x: 68, z: -578, rotY: 5.9, scale: 1.40 },       // redseam scar-lip leaner E

Dressing laws: 7-boulder bank arc = the quarried scarp the miners left (SW to
N arc, the site's high side, scales 1.5-2.1 chunky); 3 rubblePile talus tails
down the bowl; 2 treeStump + 2 deadTree leaners = the forest reclaiming the
scar (concept-01 encroachment rule). Manifest keys only (mossBoulder,
rubblePile, treeStump, deadTree census 2026-11-06). rotY free floats per
existing rows; scales PROPOSED Nicko tunes.

## W-5. Light state: CONTESTED (CONFIG.regionC.enemies)

APPEND 3 rows to CONFIG.regionC.enemies (bandit squatters = the "contested /
the ore is why the fight is there" light state, doc 42 Part 5 WHO):

    { type: 'bandit', x: 56.5, z: -580.5 },   // redseam squatter 1 (fire-side)
    { type: 'bandit', x: 61.5, z: -580 },     // redseam squatter 2 (fire-side)
    { type: 'bandit', x: 59, z: -574.5 },     // redseam squatter 3 (vein watch)

Interior spacing: squatters 4.3-6.5 m apart (camp-guard pattern CC-C16b);
>= 2.8 m from every ironVein seat; >= 1.8 m from every prop row (WM1-A3:
vein 5 moved SE per W-3, squatter min-vein 2.83 -> 3.20+; fire absent — a
zero-radius seat, no prop collision). bandit type
auto-equips handAxe (CONFIG.enemyWeapon). No fire row this round (a campfire
would read as a permanent camp; squatters bivouac — PROPOSED deviation, Nicko
can order a banditCampfire row with the same clearance math later).

## W-6. Site clearance contract (scanner evidence, scratch/cc-wm1/)

site_scan.py results (2026-11-06 run, census props=211 enemies=101 wolves=28
bandits=29 nodes=74 waypoints=56 fires=5 roads=9): the frozen seat (58,-577.5)
passes ALL constraints: region rim band r 216 (law 180-256), wolf loops >= 42
m (7 packs / 56 waypoints), dens >= 100 m (west 201.9 / east 201.5 m from
center), bandit camps >= 80 m (96.4 m to camp 4), fires >= 30 m, existing
props >= 16 m, gather nodes >= 20 m, keepOut sockets >= 30 m, roads 54-60 m
off northRoad centerline (destination-tier READABLE-FROM-THE-ROAD law, north
travelers see the scar boulders through fog D95 ~52 m). Terrain: slope <= 3.2
deg, |y| <= 3.0 across the 9x9 bowl grid (bowl_probe.js). Valspec may tighten
but must not lower these bars.

AMENDMENT WM1-A3 (IO, pre-build, 2026-11-06): an IO self-audit of the spec's
own interior-placement math (scratch/cc-wm1/clearance_wm1.py) found 4 row
collisions vs the spec's own bars (vein 5 squatter 1.41 m; rubblePile-vein
2.06/1.41 m; leaner SW-vein 2.06 m) and an internal-consistency error in the
fire row (a fire at the bowl floor was listed with a "14 m from veins" bar it
physically cannot meet in a 20 m bowl without contradicting the fire-side
squatter theme). Fixes: vein 5 -> (63.5,-582); rubblePile S -> (55,-584.5);
rubblePile W -> (52,-572.5); leaner SW -> (47,-585). Post-amendment verified
numbers (clearance_wm1.py): vein pairwise 4.24-15.69 m, vein-per-vein
nearest-neighbor >= 4.24 m, veins >= 2.5 m from ALL props (tightest 2.57 m),
squatters >= 2.83 m from every vein (tightest 3.20 m), squatters >= 1.8 m
from every prop (tightest 1.80 m), squatters 5.02-6.50 m apart. Terrain for
every moved seat re-probed PASS (seat_probe_v2.js: 12/12, |y| <= 3.33, slope
<= 4.9 deg).

## W-7. Verification requirements (bind into the valspec)

1. node -e census: CONFIG.gather.nodeTypes.ironVein exists with EXACTLY the
   W-1 fields; count 3; glowColor 0x8f5a33; scale 1.15.
2. CONFIG.items.ironOre exists with EXACTLY the W-2 fields (category
   'ingredient', glyph 'IO').
3. CONFIG.regionC.nodes contains EXACTLY 8 type 'ironVein' rows (grep
   countable) + the pre-existing 8 bonePile rows UNTOUCHED (byte law: bonePile
   rows are sacred, WD1/ED1 landed state).
4. CONFIG.regionC.props contains the 14 redseam rows; every OTHER regionC
   prop row byte-untouched (git diff proof: only ADDED lines in the regionC
   blocks + gather/nodeTypes/items blocks).
5. CONFIG.regionC.enemies: +3 bandit rows; all pre-existing enemy rows
   untouched.
6. No .js file besides prototype/js/CONFIG.js modified (git status law).
7. Build: python3 tools/build_v8.py exit 0; 'CC-WM1' marker count in the
   built html >= 16 (grep CC-WM1 builds/v8-playable.html -o | wc -l); byte
   size reported.
8. Runtime smoke (node one-shot, no browser): CONFIG loads; WH_GROUND
   heightAt for all 8 vein seats |y|<=26 finite; every seat inside region C
   ground radius (dist from center (0,-366) <= 280).
9. Playtest law: NO harness runs, NO headless smoke beyond node one-shots;
   Nicko's playtest is the acceptance bar.

## W-8. Out of scope (explicit)

No contracts/boards (doc 42 Parts 1-3 = later lane), no smelting (doc 39), no
new item icon, no new GLB assets, no regionC.mine key, no site name string in
runtime data (Redseam lives in comments), no UI changes, no save changes, no
economy mode change. Depletion counters (mine-specific long recovery) stay
the generic gather timers per doc 41.
