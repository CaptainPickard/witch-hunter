# CC-ED1 Build Note — Devbot

- **Round:** CC-ED1 — east_hollow_den (east wolfpack den, doc 41 Family 1 second den body)
- **Builder:** Devbot (subagent) · **Date:** 2026-11-06
- **Worktree:** /tmp/wh-worldfeat · branch `feat/world-visuals`, HEAD `fd286d5` (pristine at start; git status clean, 0 pre-existing diff hunks)
- **Governed by:** io/specs/cc-ed1-east-wolfpack-den-spec.md (build law; verbatim rows §3.1/§3.2) + io/specs/cc-ed1-east-wolfpack-den-valspec.md (validation law V-0..V-12) — both read fully before touching anything
- **Round law honored:** CONFIG.js rows ONLY (props + nodes hunks); gather.js untouched (BASELINE, 0 diff hunks). No git add/commit/push/stash (NO-GIT); all changes left unstaged. No harness run, no headless browser. Delivered scratch scripts run AS-IS (sha256 pre-landing = post-run, see §8).

## 1. Landed rows (CONFIG.js)

### 1a. Props hunk — 11 rows + banner, after `west_hollow_den chewed earth E` (old line 1165), before the props `]` close (old 1166)

Banner (lines 1166–1175) carries the literal marker `east_hollow_den` and cites BOTH art anchors `concept-05-night-ambush` + `day-05-ambush`:

```
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
```

Rows (§3.1 verbatim; new CONFIG lines 1176–1186):

```
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
```

Key set on every row: `asset, x, z, rotY, scale` + row comment only — no `y:` on any new row (art law: no y: keys). Assets are manifest-existing (assets.js lines 21 buriedCoffin / 32 deadTree / 64 mossBoulder / 72 skullPile / 99 rubblePile); no new asset, no assets.js change.

### 1b. Nodes hunk — 4 bonePile rows + banner into the EXISTING regionC `nodes: [` array, after the last WD1 node row (old line 1175, thicket mouth approach NE), before its `]` close (old 1176)

Banner (lines 1197–1201) carries the literal marker `east_hollow_den` and cites both art anchors' round law (art covered by the props banner; anchor pair cited in §3/1a above):

```
      // east_hollow_den CC-ED1: the east den's LARDER cache nodes (doc 41
      // Family 1 loot-identity law; CONFIG.gather bonePile, boneShard x2 yield,
      // respawn 150 - SAME type, no new node type, no new item, no new recipe).
      // Node seats ride the CC-WD1 gather.js WH_GROUND terrain seat (already
      // landed; NO code changes this round).
```

Rows (§3.2 verbatim; new CONFIG lines 1202–1205):

```
      { type: 'bonePile', x: 208.5, z: -455 },   // east_hollow_den larder cache S (by the rim boulders)
      { type: 'bonePile', x: 199.5, z: -446 },   // east_hollow_den larder cache W (by the coffin)
      { type: 'bonePile', x: 220, z: -447.5 },   // east_hollow_den outer scatter E
      { type: 'bonePile', x: 214.5, z: -435 },   // east_hollow_den thicket mouth approach N
```

## 2. Diff stat (V-6)

```
 prototype/builds/v8-playable.html | 30 ++++++++++++++++++++++++++++++
 prototype/js/CONFIG.js            | 30 ++++++++++++++++++++++++++++++
 2 files changed, 60 insertions(+)
```

- File set changed = exactly `{prototype/js/CONFIG.js, prototype/builds/v8-playable.html}` (git status --short: `M` on both only + the delivered io/specs/* and scratch/cc-ed1/* untracked). save.js diff = 0 lines. gather.js diff = 0 hunks. assets.js diff = empty.
- CONFIG.js diff = 2 hunks, pure-add: 30 insertions, 0 deletions (`grep -c "^-[^-]"` = 0).
- Diff-grep `wolfPacks|waypoint|packId`: no matches. wolfPacks block sha256 unchanged pre/post: `2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd`.
- CONFIG.js sha256: baseline `5b064ce4b5f9cf1c6d6e2cadfa26a3ae48eb7413a955dcfe0060bac9ce6431e6` (== V-0 pinned `5b064ce4…`) → post-edit `e493a04ed8b2ebea1058490844b996aa4e993bd57ff8a4c84394ced646b69706`.

## 3. Marker ledger (V-12)

`grep -c east_hollow_den`:
- prototype/js/CONFIG.js: **17** (baseline 0) — 15 row comments + 2 banner comments
- prototype/builds/v8-playable.html: **17** (baseline 0) — 1:1 landed; requirement >= 6 MET

Distinct contributors in the bundle ledger: **6 kinds of comment-carrying contributors** (props banner; thicket mouth rows; rim rows; larder rows {2 skullPile + buriedCoffin}; chewed-earth rows; nodes banner+node rows) — >= 4 MET. No row carries more than 3 hits; banners each carry exactly 1 hit.

CONFIG.js per-hit (`grep -n east_hollow_den prototype/js/CONFIG.js`):

```
1166:      // east_hollow_den CC-ED1: the east pack's DEN SITE (doc 41 Family 1,      <- banner 1
1176:      { asset: 'deadTree', x: 206, z: -440, ...  // east_hollow_den thicket mouth W
1177:      { asset: 'deadTree', x: 213, z: -439, ...  // east_hollow_den thicket mouth mid ...
1178:      { asset: 'deadTree', x: 217, z: -440, ...  // east_hollow_den thicket mouth E
1179:      { asset: 'mossBoulder', x: 215, z: -449, ...  // east_hollow_den rim S
1180:      { asset: 'mossBoulder', x: 208, z: -452, ...  // east_hollow_den rim SW
1181:      { asset: 'mossBoulder', x: 217, z: -445, ...  // east_hollow_den rim E
1182:      { asset: 'skullPile', x: 205, z: -448, ...  // east_hollow_den larder pile 1
1183:      { asset: 'skullPile', x: 203, z: -446, ...  // east_hollow_den larder pile 2
1184:      { asset: 'buriedCoffin', x: 202, z: -450, ...  // east_hollow_den larder: the past victim's cache
1185:      { asset: 'rubblePile', x: 205, z: -443, ...  // east_hollow_den chewed earth W
1186:      { asset: 'rubblePile', x: 202, z: -440, ...  // east_hollow_den chewed earth NW
1197:      // east_hollow_den CC-ED1: the east den's LARDER cache nodes (doc 41       <- banner 2
1202:      { type: 'bonePile', x: 208.5, z: -455 },  // east_hollow_den larder cache S ...
1203:      { type: 'bonePile', x: 199.5, z: -446 },  // east_hollow_den larder cache W ...
1204:      { type: 'bonePile', x: 220, z: -447.5 },  // east_hollow_den outer scatter E
1205:      { type: 'bonePile', x: 214.5, z: -435 },  // east_hollow_den thicket mouth approach N
```

Bundle per-hit (`grep -n east_hollow_den prototype/builds/v8-playable.html`):

```
88337:      // east_hollow_den CC-ED1: the east pack's DEN SITE (doc 41 Family 1,      <- banner 1
88347:      { asset: 'deadTree', x: 206, z: -440, ...  // east_hollow_den thicket mouth W
88348:      { asset: 'deadTree', x: 213, z: -439, ...  // east_hollow_den thicket mouth mid ...
88349:      { asset: 'deadTree', x: 217, z: -440, ...  // east_hollow_den thicket mouth E
88350:      { asset: 'mossBoulder', x: 215, z: -449, ...  // east_hollow_den rim S
88351:      { asset: 'mossBoulder', x: 208, z: -452, ...  // east_hollow_den rim SW
88352:      { asset: 'mossBoulder', x: 217, z: -445, ...  // east_hollow_den rim E
88353:      { asset: 'skullPile', x: 205, z: -448, ...  // east_hollow_den larder pile 1
88354:      { asset: 'skullPile', x: 203, z: -446, ...  // east_hollow_den larder pile 2
88355:      { asset: 'buriedCoffin', x: 202, z: -450, ...  // east_hollow_den larder: the past victim's cache
88356:      { asset: 'rubblePile', x: 205, z: -443, ...  // east_hollow_den chewed earth W
88357:      { asset: 'rubblePile', x: 202, z: -440, ...  // east_hollow_den chewed earth NW
88368:      // east_hollow_den CC-ED1: the east den's LARDER cache nodes (doc 41       <- banner 2
88373:      { type: 'bonePile', x: 208.5, z: -455 },  // east_hollow_den larder cache S ...
88374:      { type: 'bonePile', x: 199.5, z: -446 },  // east_hollow_den larder cache W ...
88375:      { type: 'bonePile', x: 220, z: -447.5 },  // east_hollow_den outer scatter E
88376:      { type: 'bonePile', x: 214.5, z: -435 },  // east_hollow_den thicket mouth approach N
```

Row-comment parity CONFIG↔bundle: 17/17.

## 4. Clearances — V-3 delivered script (run AS-IS, `python3 scratch/cc-ed1/clearance_ed1.py`)

Pre-landing (pristine CONFIG, reference table from IO/Testerbot spec §9) vs post-landing (this build) — exact reproduction:

```
                  pre-landing (IO/Testerbot)      post-landing (Devbot)
G-1  >= 5         12.03                           12.03
G-2  >= 25        41.77                           41.77
G-2n >= 20        38.20                           38.20
G-3  >= 20        81.54                           81.54
G-4  >= 30        69.36                           69.36
G-5a >= 3         176.17                          176.17
G-5b >= 4         41.23                           41.23
G-5c >= 2.5       2.83                            2.83
G-6a >= 4         4.27                            4.27
G-6b >= 3         3.04                            3.04
G-6c >= 6         12.73                           12.73
G-6d <= 12        10.97                           10.97
G-7  <= 262       234.61                          234.61
```

Verbatim post-landing output:

```
PASS G-1 union-vs-wolfspawn >= 5: 12.03
PASS G-2 props-vs-eastwp >= 25: 41.77
PASS G-2n nodes-vs-eastwp >= 20: 38.20
PASS G-3 union-vs-fires >= 20: 81.54
PASS G-4 props-vs-roadsedge >= 30: 69.36
PASS G-5a props-vs-preother >= 3: 176.17
PASS G-5b props-vs-pretree >= 4: 41.23
PASS G-5c newprops-mutual >= 2.5: 2.83
PASS G-6a nodes-vs-tree >= 4: 4.27
PASS G-6b nodes-vs-other >= 3: 3.04
PASS G-6c nodes-mutual >= 6: 12.73
PASS G-6d nodes-from-center <= 12: 10.97
PASS G-7 union-from-Ccenter <= 262: 234.61
INFO G-8-seen-by-preseat_probe (sep script)
RESULT: CLEARED
```

exit code 0 · **RESULT: CLEARED post-landing** ✅ (required literal `RESULT: CLEARED` present)

## 5. Probe — V-8 delivered script (run AS-IS, `node scratch/cc-ed1/preseat_probe.js`)

Verbatim output:

```
WH_GROUND.has(forest_of_the_old_king) = true
PASS deadTree      (206,-440) y=1.12 slope1m=6.1deg
PASS deadTree      (213,-439) y=0.91 slope1m=6.9deg
PASS deadTree      (217,-440) y=0.56 slope1m=8.8deg
PASS mossBoulder   (215,-449) y=0.31 slope1m=2.5deg
PASS mossBoulder   (208,-452) y=0.69 slope1m=5.9deg
PASS mossBoulder   (217,-445) y=0.20 slope1m=4.0deg
PASS skullPile     (205,-448) y=0.80 slope1m=6.0deg
PASS skullPile     (203,-446) y=0.93 slope1m=5.7deg
PASS buriedCoffin  (202,-450) y=1.13 slope1m=5.4deg
PASS rubblePile    (205,-443) y=0.90 slope1m=4.2deg
PASS rubblePile    (202,-440) y=1.15 slope1m=3.2deg
PASS bonePile      (208.5,-455) y=0.81 slope1m=5.1deg
PASS bonePile      (199.5,-446) y=1.26 slope1m=3.7deg
PASS bonePile      (220,-447.5) y=0.05 slope1m=2.0deg
PASS bonePile      (214.5,-435) y=1.42 slope1m=8.7deg
ED1 PRE-SPEC SEAT: ALL 15 PASS
```

exit code 0 · **ED1 PRE-SPEC SEAT: ALL 15 PASS** ✅ · y-range 0.05..1.42, slope-range 2.0..8.8 deg (deadTree W 8.8 = probe's own float print; valspec ED-9 adjudicated — no deviation).

**V-9.3 cross-check (performed, per "must be performed" law):** landed CONFIG rows parsed back vs the probe's hardcoded table — 11 prop rows + 4 node rows = 15 total; `ALL 15 MATCH (asset,x,z exact)`.

## 6. node --check — V-4 (7 files)

```
CONFIG.js OK
gather.js OK
game.js OK
save.js OK
region-manager.js OK
region-defs.js OK
assets.js OK
```

**7/7 OK.**

## 7. Build — V-5 / V-9 / V-10

- `python3 tools/build_v8.py` → `wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html 3339134 bytes`, exit code **0** ✅
- Bundle marker count via grep -c: **17** (>= 6 MET).

**V-10 art-law grep** on all `+` lines of the CONFIG diff (`grep -inE "lantern|campfire|startLit|light:|color|0xff|0xf[0-9a-f][0-9a-f]|ember|torch|glowColor"`): 0 matches — no warm accents, no y: keys, bone/bare-earth dressing only. (Known benign near-grep explained by the valspec: `rotY 4.60` for `-4.60`; no warm-color tokens on any row.)

## 8. Baseline + integrity pins (V-0 / V-11)

- HEAD: `fd286d5ffa184abe67b9c562c3ddbad12334dbd7`
- CONFIG.js baseline sha256 `5b064ce4b5f9cf1c6d6e2cadfa26a3ae48eb7413a955dcfe0060bac9ce6431e6` = V-0 pin
- gather.js sha256 `492d6337061244362be39809d1f71dc5a5cb306a6a32e5394c6e9a766fbbf6ea` = V-0 pin; 0 diff hunks post-build
- scratch shas — pre == post, never edited: site_scan.py `5491151606a414ea6ee61daa18a77aaf018a9764b2d42d9a4cca2a8424d7d5c1`, preseat_probe.js `c73fdd357a0621f7c6cbc3980217e84b3a25f65b2696e3e6f87f1b044ba23da6`, clearance_ed1.py `68acab5b4f6454fc70d1d6453375e7e7ac0c7462c87b0961db077bceef2f2c11`
- Censuses stable pre/post: `'east'` 6, `id: 'east'` 2, `type: 'wolf'` 28, bonePile 8→12, `west_hollow_den` 17 (unchanged)
- Smart-quote byte check (U+201C/D/2018/9) on CONFIG.js: 0/0/0/0 — ASCII-only quotes preserved
- wolfPacks block sha256 pre == post (above) — pack rows byte-identical
- save.js diff 0 lines; assets.js diff empty

## 9. ED-n deviations

**None encountered.** Full list from valspec review:

- **ED-1** (no "pre" anchor drift): G-5 margins reproduced exactly; C has no pre-existing props.
- **ED-2** (WD1 census intact): 17 WD1 markers unchanged; WD1 rows byte-identical; this round appended AFTER them per the required position.
- **ED-5** (props close / nodes open): landed at the required positions; both anchors unique; no fuzzy-match nesting (patch diffs above show both hunks at the correct sites, 0 deletions).
- **ED-6** (no pack-code edit): wolfPacks byte-identical; censuses stable; this round = pure rows/comments.
- **ED-7** (clearance must re-clear): 13 margins reproduced exactly; RESULT: CLEARED post-landing.
- **ED-8** (manifest reuse): all 5 asset keys resolve to existing assets.js manifest lines (§1a); no new assets; assets.js diff empty.
- **ED-9** (slope float print): probe prints slope1m=8.8deg for deadTree (217,-440) vs spec banner 8.7 — adjudicated by the valspec as the probe's ceiling-of-degree print on the 2 m span; ALL PASS regardless; no action.
- **ED-10** (banner-only law): both ED1 banner comments carry `east_hollow_den` and the props banner cites both `concept-05-night-ambush` + `day-05-ambush`; row comments each carry `east_hollow_den` exactly once.

## 10. Verdict

All gates green: node --check 7/7 OK · clearance RESULT: CLEARED post-landing (13/13 margins) · probe ALL 15 PASS · build exit 0 · bundle markers 17 (>= 6) with 6 distinct comment-contributor kinds (>= 4) · CONFIG↔bundle parity 17/17 · gather.js/save.js/assets.js/wolfPacks untouched · NO-GIT honored (0 commits, changes unstaged). Ready for Testerbot CC-ED1 validation per spec §10 (they run the same two AS-IS scripts + their own harness checks).
