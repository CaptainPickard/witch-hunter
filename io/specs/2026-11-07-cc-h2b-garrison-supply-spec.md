# CC-H2b — Garrison Supply Node Layer (regionH content wiring V1)

Round: CC-H2b, 2026-11-07. Author: IO (spec + acceptance). Gate: Testerbot
valspec -> Devbot build -> Testerbot verdict -> IO commit+push+flip.
Worktree: /tmp/wh-worldfeat, branch feat/world-visuals. Build: tools/build_v8.py.
Children NEVER push (NO-GIT). No harness runs, no headless browser smoke tests.
Art anchors (viewed this wake): concept-06-siege-council + char-04-bannerman-dark
(war-table/stone interior, slate + ember, crimson banned in H2 dressing);
garrison supply identity follows doc 41's loot-identity law (bones = what the
garrison ate) and doc 42 (iron feeds the war-effort loop).

## Scope

CONFIG.js regionH block ONLY (lines ~1880-2016): add a `nodes:` array after the
`props:` array closes, plus 4 appended dressing rows inside `props`. Zero engine
edits, zero new node types, zero new items, zero save-format changes, zero art
files, zero doc changes. Everything is data the landed engines already read:
gather.js NodeManager reads Every region's cfg.nodes generically
(game.js:1831-1833 -> WH_REGION_DEFS.regions; fort_garrison registers at
region-defs.js:190).

## Frozen seats (BY DATA - do not move; source = scratch/cc-h2b/seat-scan.py
PASS 15/15 committed alongside)

nodes (EXACT rows, 11 total):
  { type: 'bonePile', x: -56, z: -1032 },   // ossuary corner W heap
  { type: 'bonePile', x: -63, z: -1044 },   // ossuary corner SW heap
  { type: 'bonePile', x: -50, z: -1044 },   // ossuary corner S heap
  { type: 'ironVein', x: 66,  z: -1042 },   // armory ore store E
  { type: 'ironVein', x: 58,  z: -1050 },   // armory ore store W
  { type: 'bonePile', x: 22,  z: -1046 },   // armory-yard wreckage heap
  { type: 'bonePile', x: -20, z: -992 },    // yard wreck heap W
  { type: 'bonePile', x: -13, z: -986 },    // breach approach flank (W of lane)
  { type: 'bonePile', x: 13,  z: -986 },    // breach approach flank (E of lane)
  { type: 'bonePile', x: 44,  z: -996 },    // yard-edge ossuary tail
  { type: 'ironVein', x: 44,  z: -1022 }    // yard-edge ore cache

props (EXACT rows, 4 total, appended after the LAST existing whWallA row, before
the array's closing):
  { asset: 'b6Bones', x: 46, z: -1076, rotY: 2.4, scale: 1 },       // armory-corner dead-arms clutter
  { asset: 'rubblePile', x: 36, z: -1042, rotY: 0, scale: 1 },      // rubble between kits and boulder
  { asset: 'okFenceStonewall', x: -66, z: -1024, rotY: 1.57, scale: 1 },  // west ossuary partition
  { asset: 'graveMound', x: -58, z: -1008, rotY: 0, scale: 1 }      // ossuary mound

## Laws the build must honor

L-1 NodeTypes purity: only 'bonePile' (boneShard x2, respawn 150) and
    'ironVein' (ironOre x3, respawn 240). No CONFIG.gather.nodeTypes edits.
L-2 Light law: no lightSockets-bearing asset in new rows (banned this round:
    whTent, whCampkit, banditCampfire, lanternPost, torch). The amber family
    stays FOUR sockets exactly as landed in CC-H2. Crimson banned (art law).
L-3 Colliders: b6Bones/rubblePile/graveMound/okFenceStonewall are all
    point-collider assets. BANNED: any whWallA/whWallB row without a wall: key
    (it takes ONE trunk collider -> ghost ends; wall-key rows are out of scope).
L-4 Byte isolation: the only config bytes changed are inside the regionH block
    (nodes array + 4 appended props rows). Every other region, nodeTypes,
    economy, campaign block byte-identical. game.js/index.html/other js
    untouched.
L-5 gameplay placement law (already satisfied by the frozen seats): every node
    >= 4.0 m from props/walls, >= 5.0 m from sentries (-10,-975)/(11,-976),
    >= 6.0 m from spawn (0,-955) and door-land rows, >= 3.0 m from light
    sockets, 6.0 m node-to-node, outside the breach lane |x|<=4, rho <= 78.5.
L-6 No new comments beyond seat-id lines; keep the existing CC-H2 comment laws.

## Acceptance criteria (Testerbot validates ALL)

A-1 regionH.nodes exists with EXACTLY the 11 rows above (type/x/z float-equal
    to the scan output; no extras).
A-2 props ends with EXACTLY the 4 rows above, appended in order, nothing else
    added; all 4 assets exist in assets.js manifest names.
A-3 CONFIG.js diff vs HEAD shows insertions ONLY in the regionH block (the
    nodes array + 4 prop rows). Byte-diff proof: nodeTypes/gather/economy/
    regionA-G blocks + game.js + index.html + all other js unchanged.
A-4 scratch/cc-h2b/seat-scan.py committed + reruns to 15/15 PASS on the landed
    config rows (the script's frozen seats == landed seats).
A-5 NodeManager purity: no js file outside CONFIG.js differs from HEAD (git
    status clean except CONFIG.js + the new scratch dir).
A-6 Marker proof after build_v8: served-side v8 contains the new node count
    strings (grep proof: regionH-block node rows present; WH_AFF/CC-AF2/H2
    prior markers unchanged).
A-7 Save purity: gather nodes are stateless runtime objects (no save.js edits;
    profile format untouched - A-1..A-5 subsume).
A-8 Verdict file: io/reports/2026-11-07-cc-h2b-validation.md PASS/FAIL with
    per-criterion results.

## Non-goals (recorded for future rounds)

World-chest storage machinery (camp chest only today; chest.js is CC-C11
camp-bound) = separate round. H2b interior rooms, H5 War Camp, deeper delve
strata V3 = separate rounds (blocked on new concept art this wake: art provider
Codex 400 persists, retry owed recorded).
