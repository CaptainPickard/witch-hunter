# CK1 - CAMPKIT WIRING (change order, 2026-10-07)

Status: BRIEF - DO NOT START until Nicko's explicit go.

## 1. LOCKED RULINGS (Nicko clarify Q1-Q4, 2026-10-07 - binding)

Q1: the DEPLOYED kit adopts kit fire pit + kit bedroll; pegs ride along as a
    decorative module; the kit TENT is NOT adopted this round.
Q2: the deployed kit's tent stays whTent (Nicko's Meshy tent, scale 2.2,
    door orientation as tuned 10-06). Untouched.
Q3: the deployed kit's fire = kit stone-ring firepit (replaces the m15
    banditCampfire LOOK). Cook station, fuel rules, light socket unchanged.
Q4: the bandit world camp (darkwood_edge tutorial site) KEEPS the bandit
    look (m15 iron tripod + m16 bandit bedroll + whTent tent). Zero change.
Identity law: the kit is the PLAYER camp's look; bandit props stay bandit.

## 2. STATE BLOCK (verified 2026-10-07)

- Worktree /tmp/wh-worldfeat, branch feat/world-visuals, HEAD e325005 (AI1
  landed: 6aaf339 S1 + e325005 S2, origin verified host-side, 8793 flipped
  to e325005, served md5 4d16d40e, HTTP 200). Worktree clean apart from
  untracked scratch/ files (campkit_id.py, campkit_sheet.py, io_icons512/ -
  LEAVE ALONE).
- Kit assets COMMITTED UNWIRED: art-direction/3d/assets/camp/wh-campkit.glb
  + wh-campkit-pixelated.glb (2b31576 assets + 90ef135 QA docs). QA stills
  scratch/campkitqa/ (qa sheet + 3-angle proofs + underside.json + qa.json).
- Kit structure (parsed from the GLB JSON chunk 10-07): 4 root nodes at
  identity transforms, meshes ['tent','bedroll','firepit','pegs'], baked as
  ONE composed site. Per-node bounds (pixelated, meters, kit-local):
    tent     min [-1.85,0.00,-1.34]  max [1.63,1.56,1.34]
    bedroll  min [ 0.11,0.02,-1.14]  max [0.68,0.34,1.15]  center ~(+0.40, 0, +0.005)
    firepit  min [ 0.63,0.02,-0.51]  max [1.63,0.27,0.41]  center ~(+1.13, 0, -0.05)
    pegs     min [-1.74,0.02,-1.15]  max [1.60,0.29,1.15]
  30,000 tris (tent 27008 / bedroll 1782 / firepit 985 / pegs 225). 512px
  5-bit atlas, amber 0.115% area - 95.9% on firepit, 0 on bedroll/pegs.
- Current live wiring: CONFIG.camp.assets (CONFIG.js ~1473-1479):
    fire:    { glb: 'banditCampfire', scale: 1.0 }
    bedroll: { glb: 'banditBedroll', scale: 1.0 }
    tent:    { glb: 'whTent', scale: 2.2 }
  CONFIG.camp.modules (~1486-1491): fire [0,0] hook cook + cookFire station
  startLit true; bedroll [3.0,1.0] rotY PI/2 hook sleep; tent [0,3.6] rotY 0
  hook sleep menuAnchor true. worldCamps: banditCamp tent-only module +
  respawn/face rows (5.0,-54.6 / 6.0,-55.7 / 2.5,-52). deploy: maxSites 1,
  maxReachM 9, startAheadM 4, pathBand 2.5, ghost rows.
- camp.js (612 lines, window.WH_CAMP): makePiece(key, ghostMat) at ~line 65
  reads K.assets[key], uses window.WH_ASSETS.instance(A.glb), sets scale,
  swaps materials when ghost. buildSiteGroup adds one obj per module row at
  [offset[0], 0, -offset[1]] + rotY. moduleWorld / siteYaw frame law: group
  yaw = atan2(f.x, f.z); local (right, 0, -back).
- assets.js: MANIFEST map (~line 40-100) logical name -> relative path;
  window.WH_ASSETS.instance(name) clones the ground-aligned cached template
  (SkelethonUtils.clone at ~line 536). Fire light: computeFireSockets
  (game.js) reads camp module rows (cookFire / startLit) - follows the
  MODULE, not the asset, so the fire GLB swap keeps the night light.

## 3. crg IMPACT (run 2026-10-07, graph updated first)

code-review-graph impact --repo /tmp/wh-worldfeat --files
prototype/js/camp.js prototype/js/CONFIG.js prototype/js/assets.js:
30 nodes directly changed, 0 nodes impacted (within 2 hops), 0 additional
files affected. Known limitation #343: window-globals callsites unresolved
- the manual census in section 2 is authoritative.

## 4. SCOPE CONTRACT (files + exact anchors)

Touch ONLY: prototype/js/assets.js (one MANIFEST row),
prototype/js/camp.js (one branch in makePiece + optionally a hook guard),
prototype/js/CONFIG.js (assets rows fire/bedroll + one pegs module row),
prototype/builds/v8-playable.html (rebuild).

- assets.js: ADD exactly one row inside the MANIFEST map (near the whTent
  row, same comment style):
    whCampkit: 'art-direction/3d/assets/camp/wh-campkit-pixelated.glb',
  Rollback = delete the row.
- camp.js makePiece: new branch when A.node is set:
    var obj = window.WH_ASSETS.instance(A.glb);
    find the descendant whose name === A.node (traverse obj, exact match,
    pick the FIRST match; if missing -> console.warn + fall back to the
    un-kit placeholders so the game never breaks);
    wrap it in a THREE.Group; INSIDE the wrapper set the child's
    position to minus the piece's baked center
      (firepit: (-1.13, 0, 0.05); bedroll: (-0.40, 0, -0.005)),
    so the module row's offset/rotY own placement from zero. The wrapper is
    what scale/rotY/position apply to (rows below keep scale 1.0, so this
    is a no-op today - keep raw kit units in the counter-offset).
    Ghost path unchanged: the existing traverse-material swap reaches the
    wrapped child.
- CONFIG.camp.assets becomes:
    fire:    { glb: 'whCampkit', node: 'firepit', scale: 1.0 },
    bedroll: { glb: 'whCampkit', node: 'bedroll', scale: 1.0 },
    tent:    { glb: 'whTent', scale: 2.2 }        // UNCHANGED (Nicko Q2)
- CONFIG.camp.modules: ADD one decorative row AFTER the tent row:
    { id: 'pegs', hook: 'none', asset: 'pegs', offset: [0, 3.6], rotY: 0 }
  and an assets row for it (ONE mechanism - the assets row owns scale):
    pegs: { glb: 'whCampkit', node: 'pegs', scale: 1.6 }  // PROPOSED, Nicko
    tunes - pegs ring scale vs the whTent base footprint; rides the tent
    spot so the ring reads around the tent. If any camp.js
  code switches on hook values (nearestSleep skips hook !== 'sleep'; the
  fire-socket pass reads cookFire; the interact prompt reads cook/sleep),
  verify hook 'none' is inert end to end and add a tiny skip-guard ONLY if
  a switch would misbehave - no other camp.js logic edits.
- Clearances: deploy validation tests every module of the kit - pegs adds
  one test point near the tent spot (same clearance outcome). No
  CONFIG.gather / scatter changes.
- FORBIDDEN: touching player.js, game.js, enemy.js, save.js, cooking.js,
  leveling.js, region-manager.js, moveset.js, spells.js. Editing or
  deleting ANY existing MANIFEST row or CONFIG.camp row (tent/worldCamps/
  deploy rows are frozen). Renaming nodes. Re-baking GLBs. The kit TENT
  stays unwired (optional future swap lives as a rollback comment).

## 5. ACCEPTANCE CRITERIA

Static (builder self-check, report actual counts):
- AC-S1: MANIFEST has whCampkit -> camp/wh-campkit-pixelated.glb; no other
  row touched (git diff of assets.js = exactly the added line).
- AC-S2: makePiece node branch present; all other camp.js functions
  byte-untouched (diff hunks limited to makePiece + optional hook guard).
- AC-S3: bundle rebuilt (python3 tools/build_v8.py from repo root; if
  python3 is not on PATH use /usr/local/bin/python3). Greps on the BUNDLE:
  'whCampkit' >= 3, 'node: ' + 'firepit' present, 'guardArcDeg' still 2
  (AI1 marker survives), 'WH_LEVEL' still 53 lines, 'Dexterity' still 1.
- AC-S4: git diff e325005..HEAD shows ONLY assets.js, camp.js, CONFIG.js,
  bundle (game.js / save.js / cooking.js / leveling.js / enemy.js empty).
- AC-S5: no new files. PROPOSED comments on every new tunable number.

Playtest (Nicko's verdict is the gate):
- AC-P1: deployed kit reads as the player's camp: amber-glow stone-ring
  firepit (not the bandit iron tripod) + kit bedroll; tent unchanged.
- AC-P2: cook at the fire, sleep at bedroll/tent, tent menu Save /
  Save-and-Heal / LOAD all work exactly as before.
- AC-P3: placement ghost still validates (red/green), pegs cause no
  placement refusals; the kit still packs/redeploys (maxSites 1 swap).
- AC-P4: at a distance the site reads composed - pegs ring around the tent
  instead of three scattered props.
- AC-P5: at night the fire light still pools at the firepit.
- AC-P6: the bandit tutorial camp is byte-identical to today (m15 + m16 +
  whTent, rotY -0.77, respawn/face rows unchanged).

## 6. COMMIT UNITS + PUSH LAW

- ONE unit: S1 = everything above (assets.js + camp.js + CONFIG.js) +
  bundle + commit 'feat(ck1): campkit wiring - player camp adopts kit
  firepit/bedroll/pegs (whTent tent unchanged, bandit camp bandit props)'
  + push origin feat/world-visuals. Identity stays CaptainPickard
  pickard.nicko@gmail.com.
- If max-turns bites, land the tree + bundle FIRST (commit counts), the
  push second; IO completes whatever remains.

## 7. HARD LAWS (verbatim repeats)

- NO automated harness or headless browser runs of any kind. Syntax checks
  on edited JS only (node is available via the playwright driver).
- One change order at a time. This brief is the whole order.
- Commit each unit to feat/world-visuals and push immediately.
- Never checkout-under-serve; worktree stays feat/world-visuals.
- Do not touch /workspace/witch-hunter main checkout.
- Leave untracked scratch/ files alone.
- No python3 on builder PATH - use /usr/local/bin/python3.

## 8. POST-LAND VERIFICATION (IO runs after the unit lands)

1. git -C /tmp/wh-worldfeat status (clean), log shows the S1 sha above
   e325005.
2. Host-side fetch + rev-parse origin/feat/world-visuals == HEAD
   (dhost host_exec, file-then-cat pattern, generous timeout).
3. Bundle marker greps per AC-S3 on the worktree bundle.
4. Flip 8793: tools/wh_release_flip.py <sha> via dhost host_exec with a
   timeout >= 800s (60s default silently kills flips mid-release-build,
   leaving an empty husk that 404s). If releases/<sha> lacks
   prototype/builds/, delete the husk and re-run.
5. Host curl 200 on /current/prototype/builds/v8-playable.html + marker
   greps on the served bytes; /playtest-feat/ serves the worktree live.
6. Hand Nicko both URLs + the AC-P1..P6 playtest flow.

## 9. OUT OF SCOPE THIS ROUND

Kit tent swap (rollback-comment option only), campkit MANIFEST in the
worldCamps rows, campkit in banditCamp, new fire VFX/flame sprite on the
pit, campkit pixel-icon for the cook panel, sleep-on-bedroll vs tent
distinction, any camp UI changes, anything in section 4 FORBIDDEN list.