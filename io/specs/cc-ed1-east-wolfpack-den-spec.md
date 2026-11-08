# CC-ED1 SPEC — East Wolfpack Den Site (doc 41 Family 1, second den body)

Issued by IO, 2026-11-06, wake 5. Executes the GOALS.md lane "east-pack den
body (cheap symmetry on west_hollow_den machinery)". The build is a strict
sibling of CC-WD1: same gate shape, same row shape, same laws — a second den
on the east flank for the east pack ('east' id, L7 Wolf den East).

## 1. Source of truth

- doc 41 Family 1 (dens and lairs): entrance (cave mouth, hollow, thicket),
  den body, brood (the pack — already live as CONFIG.wolfPacks 'east'),
  LARDER (cached kills; "the den's loot identity is what the beast ate").
- Machinery: io/specs/cc-wd1-west-wolfpack-den-spec.md (landed fd286d5,
  Testerbot PASS 13/13). This round reuses its EXACT conventions: row shape,
  marker-banner comment shape, node-type reuse, clearance table, build flow.
- Art anchors (viewed this wake, vision law): concept-05-night-ambush +
  day-05-ambush. Palette law carries over from WD1: moonlit/earth-neutral
  base, den dressing = bone/bare-earth neutrals, NO new warm accents (the
  amber in both anchors belongs to the hunter's lantern, never the den).
- Art law (GOALS): pixelated everything, darkwood palette, one accent per
  frame. No new assets are added this round, so the law binds the dressing
  choice: existing manifest props only, neutral tones.

## 2. Site placement (PROVEN pre-spec this wake — no A-1 amendment needed)

WD1's lesson made law: probe before freeze. Evidence in scratch/cc-ed1/:
- site_scan.py — 380 coarse candidates from the full CONFIG census (east
  waypoints, all wolf rows, fires, roads, props), then a node one-shot
  terrain pass: best cluster at (210,-445), y=0.61, slope 4.1 deg.
- preseat_probe.js — the FINAL 15-row table below vs WH_GROUND: ALL 15 PASS
  (y range 0.05..1.42, slope1m 2.0..8.7 deg, all within |y|<=26 / <=31 deg).
- clearance_ed1.py — full G-1..G-7 table below: CLEARED with real margins
  (pre-landing run; post-landing re-run uses the same script, whose NEW_TAG
  line exclusion drops this round's own rows from the census — the WD1
  G-5a self-match fix is baked in).

Den site center (210,-445). The east pack loop's southern extremity is
(205,-398) — the den sits 47 m SOUTH of the loop's southern point (west den
sits ~31 m south of its loop's edge). Mouth faces the loop (north), rim
south: same orientation grammar as west_hollow_den. Deliberate asymmetry vs
a strict x-flip: rim boulders 2-3 sit at (208,-452)/(217,-445) (not the exact
flip (212,-452)/(217,-451)) and deadTree 3 at z=-440 — the site reads as a
second den, not a photocopy; seat+clearance proven at the FINAL coords.

## 3. The build (CONFIG rows ONLY — gather.js seat already landed in CC-WD1)

### 3.1 CONFIG.regionC.props additions (11 rows; all PROPOSED, Nicko tunes)

Insert after the last west_hollow_den prop row (currently the rubblePile at
(-186,-446)), inside regionC.props. Precede with the marker banner comment
(exact wording below, carries east_hollow_den + anchor citation):

    // east_hollow_den CC-ED1: the east pack's DEN SITE (doc 41 Family 1,
    // second den body; io/specs/cc-ed1-east-wolfpack-den-spec.md; art anchors
    // concept-05-night-ambush + day-05-ambush - moonlit hollow, indigo/charcoal
    // base, den dressing = bone/bare-earth neutrals, NO new warm accents).
    // Hollow center (210,-445), south of the east pack patrol loop (southern
    // extremity (205,-398), nearest prop row 41.77 m; site probe: y 0.05-1.42,
    // slope <= 8.7 deg over 1 m; clearance_ed1.py CLEARED G-1..G-7). Thicket
    // mouth arc (3 deadTree, N-facing) / hollow rim (3 mossBoulder, S arc) /
    // the LARDER (2 skullPile + buriedCoffin = a past victim's cache) /
    // chewed-earth rubble (2 rubblePile).

Rows (exact, no y key — region-manager whGroundFeed() seats C props):

    { asset: 'deadTree', x: 206, z: -440, rotY: 5.60, scale: 1.70 },   // east_hollow_den thicket mouth W
    { asset: 'deadTree', x: 213, z: -439, rotY: 5.90, scale: 1.90 },   // east_hollow_den thicket mouth mid (tallest, the mouth's gate)
    { asset: 'deadTree', x: 217, z: -440, rotY: 0.40, scale: 1.40 },   // east_hollow_den thicket mouth E
    { asset: 'mossBoulder', x: 215, z: -449, rotY: 0.80, scale: 1.80 },   // east_hollow_den rim S
    { asset: 'mossBoulder', x: 208, z: -452, rotY: 2.10, scale: 2.00 },   // east_hollow_den rim SW
    { asset: 'mossBoulder', x: 217, z: -445, rotY: 4.60, scale: 1.30 },   // east_hollow_den rim E
    { asset: 'skullPile', x: 205, z: -448, rotY: 0.30, scale: 1.20 },   // east_hollow_den larder pile 1
    { asset: 'skullPile', x: 203, z: -446, rotY: 2.80, scale: 1.00 },   // east_hollow_den larder pile 2
    { asset: 'buriedCoffin', x: 202, z: -450, rotY: 1.20, scale: 1.60 },   // east_hollow_den larder: the past victim's cache
    { asset: 'rubblePile', x: 205, z: -443, rotY: 5.10, scale: 1.10 },   // east_hollow_den chewed earth W
    { asset: 'rubblePile', x: 202, z: -440, rotY: 0.90, scale: 1.00 },   // east_hollow_den chewed earth NW

### 3.2 CONFIG.regionC.nodes additions (4 rows; second larder cache set)

Insert after the last west_hollow_den node row ((-198.5,-441)), inside
regionC.nodes. Precede with the marker banner comment (exact wording below):

    // east_hollow_den CC-ED1: the east den's LARDER cache nodes (doc 41
    // Family 1 loot-identity law; CONFIG.gather bonePile, boneShard x2 yield,
    // respawn 150 - SAME type, no new node type, no new item, no new recipe).
    // Node seats ride the CC-WD1 gather.js WH_GROUND terrain seat (already
    // landed; NO code changes this round).

Rows (exact):

    { type: 'bonePile', x: 208.5, z: -455 },   // east_hollow_den larder cache S (by the rim boulders)
    { type: 'bonePile', x: 199.5, z: -446 },   // east_hollow_den larder cache W (by the coffin)
    { type: 'bonePile', x: 220, z: -447.5 },   // east_hollow_den outer scatter E
    { type: 'bonePile', x: 214.5, z: -435 },   // east_hollow_den thicket mouth approach N

### 3.3 gather.js — NO changes

The CC-WD1 terrain seat lines are already in gather.js (landed fd286d5).
This round touches gather.js ZERO lines. V-3 this round = gather.js diff
EMPTY (git diff prototype/js/gather.js has zero hunks).

### 3.4 NO-GO list (explicit non-goals this round)

- No wolfPacks changes (east OR west rows, OR waypoints). Byte-purity law.
- No new enemy types, no combat fields, no loot rolls, no respawn edits.
- No roads, no scatterOverrides, no terrain edits, no region changes.
- No gather.js, game.js, enemy.js, region-manager.js, region-defs.js,
  save.js, assets.js touches. The ONLY file that changes is CONFIG.js.
- No doc 41 status change (stays PROPOSED); doc untouched.
- No new assets, no manifest edits, no texture work, no new node types.

## 4. Acceptance criteria (Testerbot verbatim anchors)

A-1 Build: `python3 tools/build_v8.py` in the worktree exits 0.
A-2 Bundle markers: `grep -c east_hollow_den prototype/builds/v8-playable.html`
    >= 6; ledger of distinct contributors >= 4 (props block banner, nodes
    block banner, one prop row comment, one node row comment). Baseline
    count today = 0 (verified pre-build).
A-3 CONFIG diff purity: `git diff prototype/js/CONFIG.js` shows ONLY
    additions inside the regionC props[] and nodes[] arrays (+ the two
    east_hollow_den banner comments). Zero deletions; both hunks sit
    immediately after the west_hollow_den rows (props: after the
    rubblePile (-186,-446) row; nodes: after the bonePile (-198.5,-441) row).
A-4 gather.js diff EMPTY (3.3).
A-5 Syntax: node --check on CONFIG.js + gather.js exits 0.
A-6 Geometry proof: Testerbot re-runs scratch/cc-ed1/clearance_ed1.py
    POST-LANDING (same file, NEW_TAG exclusion active) — exits 0, every
    margin printed and inside the section-5 limits.
A-7 Node legality: every new node row's type 'bonePile' exists in
    CONFIG.gather.nodeTypes; every new prop row's asset key exists in the
    MANIFEST (grep assets.js). Zero unknown keys.
A-8 Save safety: no new region, no region-defs change -> save.js untouched;
    `git diff prototype/js/save.js` empty.
A-9 Baseline invariants: wolfPacks block byte-identical (`git diff` shows
    NO hunk touching wolfPacks); east pack L7 waypoints exact
    ([[190,-318],[214,-322],[222,-340],[220,-372],[205,-398],[178,-388],
    [166,-360],[192,-334]]); `grep -c "id: 'east'" prototype/js/CONFIG.js`
    unchanged from baseline.

## 5. Geometry margins (Testerbot checks in scratch/cc-ed1/clearance_ed1.py)

Union law (WD1 A-1): the 15 new rows (11 props + 4 nodes) govern G-1..G-3;
G-4 stays prop-set only (matches the WD1 amendment wording we mirror).
G-1 Every new union row >= 5.0 m from every wolf spawn row (measured
    12.03 pre-landing).
G-2 Props >= 25.0 m from every east-waypoint (41.77).
G-2n Nodes >= 20.0 m from every east-waypoint (38.20).
G-3 Union >= 20.0 m from every fire (81.54).
G-4 Props >= 30.0 m from every road segment edge, segment distance minus
    halfWidth 2.2 (69.36).
G-5a Props >= 3.0 m from ALL pre-existing C props (176.17).
G-5b Props >= 4.0 m from all pre-existing tree-family props (41.23).
G-5c New props >= 2.5 m from each other (2.83 — the mirrored larder pair;
    west carries the identical 2.83 pair).
G-6a Nodes >= 4.0 m from all tree-family props old+new (4.27).
G-6b Nodes >= 3.0 m from all other props old+new (3.04).
G-6c Nodes >= 6.0 m from each other (12.73).
G-6d Nodes <= 12 m from center (10.97 max).
G-7 Union <= 262 m from C center (0,-366) (234.61 max).
G-8 Seat law (PROVEN PRE-SPEC, preseat_probe.js ALL-15): per row,
    |WH_GROUND.heightAt('forest_of_the_old_king',x,z)| <= 26 and slope over
    1 m <= 31 deg. Testerbot re-runs the probe against the landed rows
    (coords read from CONFIG, not the spec table).

## 6. Devbot deliverables

- The CONFIG.js edits (3.1, 3.2) exactly as written above (rows + banners).
- Re-run scratch/cc-ed1/preseat_probe.js and clearance_ed1.py post-landing;
  paste both outputs in the build note.
- io/reports/cc-ed1-build-note.md with: git diff --stat paste, the bundle
  marker ledger (grep -c + contributor list), clearance + probe outputs,
  node --check results, and any numbered ED-n deviations (CC-EC1 form).
- NO git commands (NO-GIT clause: no commit, no push, no branch). NO
  harness runs. NO headless browser smoke tests. node --check + grep +
  python clearance only.

## 7. IO close-out law (post-verdict)

Testerbot PASS -> IO commits (identity CaptainPickard
<pickard.nicko@gmail.com>) in /tmp/wh-worldfeat on feat/world-visuals,
builds v8, flips the release server to the new sha via
tools/wh_release_flip.py, verifies served bytes (200 + marker grep on
SERVED bytes), journals, ticks GOALS.md. Children NEVER push.
