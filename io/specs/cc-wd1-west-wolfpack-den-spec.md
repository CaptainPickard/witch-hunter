# CC-WD1 SPEC — West Wolfpack Den Site (doc 41 Family 1, first den body)

Round: CC-WD1 · 2026-11-06 · Author: IO (gate step 1)

## AMENDMENT A-1 (IO, 2026-11-06, pre-build): site moved off the slope

Pre-build WH_GROUND seat probe (scratch/cc-wd1/seat_probe.js, CORE analytic
heightA) showed every (-255,-410)-area row on 48-59 deg slope, |y| up to 27.7
(the SW rim mountain foot). Site rescinded; new verified site: hollow center
(-194, -451) - y 1.7, center slope 2.5 deg, patch relief 0.4 m over 5 m,
31.3 m from every west spawn row + waypoint (min wolf row 19.4 m inside the
12 m build disc = the pack dens can be SEATED as spec'd), nearest prop
(witchwoodTree -178.2,-424.2) 31.1 m, nearest fire 65.8 m, westRoad edge
77.0 m, C-center 211.8 m <= 262 m cap. Margins re-derived:
- G-2 recomputed 38.0 -> 25.0 m (the 38 figure was old-site-derived; the den
  SHOULD sit near its pack's loop; 25 m keeps the patrol path off the hollow;
  nearest row/waypoint pair after layout = 25.96 m).
- G-6 engine-aligned: nodes >= 4.0 m tree-class / >= 3.0 m other props
  (CONFIG.gather.placement treePropM/propM), mutual >= 6.0 m (C band).
- Row count: section 3.1 lists 3+3+3+2 = 11 prop rows (2 skullPile + 1
  buriedCoffin = 3 larder rows), not 8 - header typo, the list is law.
- Final IO layout (authored + clearance-verified; Testerbot re-derives):
  deadTree (-190,-446) (-197,-445) (-201,-445);
  mossBoulder (-199,-455) (-196,-458) (-201,-451);
  skullPile (-189,-454) (-187,-452); buriedCoffin (-186,-456);
  rubblePile (-189,-449) (-186,-446);
  bonePile nodes (-192.5,-461) (-184,-450) (-204,-453.5) (-198.5,-441)
  (node set constraint-solved for mutual >= 6 / props >= 3-4 / center <= 12;
  clearance.py CLEARED 12/12 margins + seat probe ALL 15 rows <= 8.6 deg,
  |y| <= 2.0).
Art anchor (viewed + absorbed this wake): concept-05-night-ambush.png —
moonlit path, dual light (cold moon rim + warm lantern), muddy track
flanked by low stone walls, dead vegetation, two hulking white-eyed
wolves mid-leap. PALETTE LAW for the den: indigo/charcoal base, NO new
warm accents (the lantern amber belongs to the traveling player, not the
den); den dressing = bone/bare-earth neutrals only. The accent stays
where the anchor puts it: on the hunter.

## 1. Source of truth

- docs/planning/41-wilderness-encounters.md — Family 1 Dens and Lairs:
  "Structure: an entrance (cave mouth, hollow, thicket), a den body, a
  brood (the pack), and the LARDER (cached kills, bones, sometimes a
  past victim's gear: the den's loot identity is what the beast ate)."
- docs/planning/34 bestiary grammar: beasts = no block/parry (wolf rows
  carry zero new combat fields; CC-C5 pack behavior untouched).
- CC-C5 pack law (CONFIG.wolfPacks): members/waypointPhase rows derive
  patrol slots; packs keyed by id+regionId. This round adds NO pack, NO
  wolf row, NO behavior change — the L8 'west' pack keeps its exact
  loop. The den site is WHERE the brood lives, not a mechanical change.

## 2. Site placement (pre-verified this wake against all C objects)

Den hollow center: **(-255, -410)**, region C (Forest of the Old King,
center (0,-366), playable r 278.5 → site r 258.8 ✅ inside, SW quadrant
"rim mountain foot" per CC-C15's relocation note).

Cleared distances (verified by script this wake):
- west pack loop waypoints: min 38.0 m (-224,-388); all >= 38 m
- all 4 C fires: min 161.3 m
- all roads incl. westNotch bed: min 44.0 m
- nearest existing prop: 65.8 m (wolf spawn row)
- nearest enemy row: the wolf spawn rows above (65.8 m)

## 3. The build (CONFIG rows ONLY + one gather.js line)

### 3.1 CONFIG.regionC.props additions (8 rows; all PROPOSED, Nicko tunes)

Den body at the hollow — assets from the verified MANIFEST only
(assets.js lines 1-130; every key below exists):
- Thicket mouth (doc 41: "cave mouth, hollow, thicket"): 3 deadTree in
  a broken arc facing NE (toward the pack loop), radii -0.5 m..+1.5 m
  from center, scales 1.4-1.9, rotY facing inward.
- Hollow rim: 3 mossBoulder (SW arc, scales 1.3-2.0).
- The LARDER: 2 skullPile + 1 buriedCoffin (past victim's gear), NE of
  center, 4-7 m from the hollow middle, rotYs varied.
- Scatter floor identity: 2 rubblePile (chewed earth), SE flank.

Row law (copy CC-C17 shape): every row { asset, x, z, rotY, scale }.
y is NEVER set: region-manager whGroundFeed() seats C props on terrain
(footY) automatically — confirmed this wake.

### 3.2 CONFIG.regionC.nodes additions (first C gather nodes; 4 rows)

- 3x { type: 'bonePile', ... } near the larder cluster (6-10 m site
  radius), 1x { type: 'bonePile' } at the thicket mouth approach.
- All 4 >= 5 m from every new prop (gather.placement.propM) and from
  each other >= 6 m (C band spacing law).
- bonePile nodeType EXISTS (CONFIG.gather.nodeTypes: boneShard x2,
  respawnSec 150) — no new type, no new item, no new recipe.

### 3.3 gather.js terrain seat (THE one non-CONFIG line; <20-line law)

gather.js NodeManager.makeNode hard-codes holder.position.set(x, 0, z)
and the respawn path sets mesh.position.set(pick.x, 0, pick.z). In a
heightfield region these float/bury. Add a WH_GROUND seat:

  holder.position.set(x, window.WH_GROUND && window.WH_GROUND.has(regionId) ?
    window.WH_GROUND.heightAt(regionId, x, z) : 0, z);

same treatment for the respawn line (mesh.position.set). TWO lines
total, no logic changes, marker bob untouched. This is a disclosed
tiny-fix inline under PRIMARY law 4 (<20 lines, no logic), landed by IO
with the CONFIG rows, and Testerbot validates the WHOLE diff anyway.

### 3.4 NO-GO list (explicit non-goals this round)

- No new wolfRows, no packs change, no L8 waypoint edits.
- No new enemy types, no combat fields, no loot rolls.
- No roads, no scatterOverrides, no terrain edits.
- No game.js / enemy.js / region-manager.js / region-defs.js touches.
- No new assets, no manifest edits, no texture work.
- No doc 41 status change (stays PROPOSED); doc untouched.

## 4. Acceptance criteria (Testerbot verbatim anchors)

A-1 Build: `python3 tools/build_v8.py` in the worktree exits 0.
A-2 Bundle markers: `grep -c west_hollow_den prototype/builds/v8-playable.html`
    >= 6; ledger of distinct contributors >= 4 (props block banner,
    nodes block banner, one prop row comment, one node row comment).
    Marker string `west_hollow_den` appears in: the props-section banner
    comment (1), the nodes-section banner comment (1), and >= 2 row
    comments distributed across prop and node rows (>= 4 total
    contributors). Baseline count today = 0 (verified).
A-3 CONFIG diff purity: `git diff prototype/js/CONFIG.js` shows ONLY
    additions inside the regionC props[] and nodes[] arrays (+ the
    west_hollow_den banner comments). Zero deletions outside the two
    insertion hunks; zero '-' lines except headers.
A-4 gather.js diff: exactly 2 changed lines (the two seat lines), no
    other hunks; `node --check prototype/js/gather.js` exits 0.
A-5 Syntax: node --check on CONFIG.js, gather.js, game.js exits 0.
A-6 Geometry proof: Testerbot re-runs a distance script (scratch/cc-wd1/
    clearance.py, new file, Devbot writes it on scratch/cc-ec1/ shape)
    proving rows 1-8.2 below. Script exits 0; every margin printed.
A-7 Node legality: every new node row's type exists in
    CONFIG.gather.nodeTypes; every new prop row's asset key exists in
    the MANIFEST (grep assets.js). Zero unknown keys.
A-8 Save safety: no new region, no region-defs change → save.js
    untouched; `git diff prototype/js/save.js` empty.
A-9 Baseline invariants: `grep -c "'west'" prototype/js/CONFIG.js`
    unchanged from baseline (1 pack row); wolfPacks block byte-identical
    (`git diff` shows no hunk touching wolfPacks); L8 waypoints exact.

## 5. Geometry margins (Testerbot checks in scratch/cc-wd1/clearance.py)

G-1 Every new prop row >= 5.0 m from every wolf spawn row in regionC
    (28 rows) — the pack never spawns inside the den mouth.
G-2 Every new prop row >= 38.0 m from every west-pack waypoint (the
    patrol loop never clips the hollow).
G-3 Every new prop row >= 20.0 m from every fire in regionC.
G-4 Every new prop row >= 30.0 m from every road segment (C roads +
    notch beds; segment distance, not point).
G-5 Prop-to-prop: new rows >= 3.0 m from ALL pre-existing C props, and
    >= 2.5 m from each other (they form a cluster, not a pile).
G-6 Node rows: >= 5.0 m from all props (new + old), >= 6.0 m from each
    other (C band spacing), inside the site (<= 12 m from hollow center).
G-7 Site radius: every new row <= 262 m from C center (playable
    278.5 - margin 16.5).
G-8 Seat law: script prints WH_GROUND.heightAt('forest_of_the_old_king',
    x, z) per row (requires: scratch/cc-wd1 seat stub that loads
    CONFIG + wh-ground CORE THREE-free, scratch/cc-c5/cc-c8 pattern);
    |y| <= 26 m (the heightfield hMax ceiling) and slope over 1 m
    <= 31 deg (C4b cliff-guard convention) for every row.

## 6. Devbot deliverables

- scratch/cc-wd1/clearance.py (new, runnable, prints G-1..G-8).
- The CONFIG.js edits (3.1, 3.2) + the banner comments carrying the
  west_hollow_den marker string.
- The gather.js 2-line seat (3.3), reported in the build note.
- io/reports/cc-wd1-build-note.md with: exact diff stat pastes, the
  bundle marker ledger, clearance output, and any numbered ED-n
  deviations (CC-EC1 form).
- NO git commands (NO-GIT clause). NO harness runs. NO headless browser
  smoke tests. node --check + grep + python clearance only.

## 7. IO close-out law (post-verdict)

Testerbot PASS → IO commits (identity CaptainPickard
<pickard.nicko@gmail.com>) + pushes feat/world-visuals via the HTTPS
credential route; build verified; release flip; served-bytes check;
journal + GOALS tick. Testerbot FAIL → ED loop or IO inline-landing
per the 2-death law, disclosed in the round note.
