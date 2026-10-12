// Witch Hunter prototype v2 - asset manifest + GLB loading.
// D1 fix: manifest paths are RELATIVE (no leading slash) and are resolved
// against document.baseURI at load time via new URL(...).href, so the game
// works identically served at / and under any proxy prefix such as
// /witchhunter/ (tailnet path). Do not hardcode proxy prefixes here.
// Prefer -pixelated variants for props; rigged characters keep their raw mesh
// and swap in a pre-baked pixelated atlas PNG at postload (R4, kill switch
// CONFIG.assets.pixelatedBodies).

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;

  // ---- Manifest: logical name -> relative path (NO leading slash) -----------
  var MANIFEST = {
    // graveyard props (pixelated variants preferred)
    gravestoneObelisk: 'art-direction/3d/assets/graveyard/gravestone-obelisk-pixelated.glb',
    stoneCrossTilted: 'art-direction/3d/assets/graveyard/stone-cross-tilted-pixelated.glb',
    graveMound: 'art-direction/3d/assets/graveyard/grave-mound-pixelated.glb',
    buriedCoffin: 'art-direction/3d/assets/graveyard/buried-coffin-pixelated.glb',

    // biome library (darkwood dressing pass, all pixelated)
    cemeteryGate: 'art-direction/3d/assets/biome_library/m1-pixelated.glb',
    picketFence: 'art-direction/3d/assets/biome_library/m2-pixelated.glb',
    mourningStatue: 'art-direction/3d/assets/biome_library/m3-pixelated.glb',
    yewTree: 'art-direction/3d/assets/biome_library/m5-pixelated.glb',
    livingOak: 'art-direction/3d/assets/biome_library/m16-living-oak-pixelated.glb',
    witchwoodTree: 'art-direction/3d/assets/biome_library/m17-witchwood-pixelated.glb',
    youngAsh: 'art-direction/3d/assets/biome_library/m19-birch-pixelated.glb',
    // m18-dead-tree lives in biome_library (Astrabot 10-03)
    deadTree: 'art-direction/3d/assets/biome_library/m18-dead-tree-pixelated.glb',
    // Round E vegetation scatter (scratch/tree_meshy.py, io/roundE-veg-provenance.md):
    // extra trees are props; bushes + grass render instanced (region-manager)
    youngBirch: 'art-direction/3d/assets/biome_library/wh-tree-birch-young-pixelated.glb',
    youngDeadTree: 'art-direction/3d/assets/biome_library/wh-tree-dead-young-pixelated.glb',
    bushA: 'art-direction/3d/assets/biome_library/wh-bush-a-pixelated.glb',
    bushB: 'art-direction/3d/assets/biome_library/wh-bush-b-pixelated.glb',
    grassTuft: 'art-direction/3d/assets/biome_library/wh-grass-tuft-pixelated.glb',
    // Round G tree-ring bush (io/roundG-provenance.md): Nicko's Meshy snare
    // bush, decimated to 3000 tris; raw had no texture, so Round H vertex-paints
    // it (COLOR_0 two-tone: dark canes, ash-rose roses; scratch/snare_color_roundG.py)
    whBushSnare: 'art-direction/3d/assets/biome_library/wh-bush-snare-pixelated.glb',
    // Round H free-ground bush (io/roundH-provenance.md): Meshy bramble, decimated
    // to 2500 tris with per-face UV transfer, texture posterized 512 NEAREST
    // (scratch/decimate_roundH.py + scratch/bramble_bake_roundH.py)
    bramble: 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb',
    // Round I gothic reach-trees (io/roundI-provenance.md): 3 Meshy variants, twig tips
    // reattached + decimated to 3500 tris, texture posterized 512 NEAREST
    // (scratch/decimate_roundI.py --snap + scratch/reachtree_bake_roundI.py)
    reachTreeA: 'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb',
    reachTreeB: 'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb',
    reachTreeC: 'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb',
    // Round F boundary wall + gate (io/roundF-wall-provenance.md): wall
    // segments render instanced (region-manager buildWorld). b3Gate is the
    // b3-gate GLB with its near-closed door leaves cut out
    // (scratch/gate_open_cut.py); the lantern carries an amber emissive map.
    whWallA: 'art-direction/3d/assets/biome_library/wh-wall-vinestone-a-pixelated.glb',
    whWallB: 'art-direction/3d/assets/biome_library/wh-wall-vinestone-b-pixelated.glb',
    whLanternHang: 'art-direction/3d/assets/biome_library/wh-lantern-hang-pixelated.glb',
    b3Gate: 'art-direction/3d/assets/biome_library/b3-gate-open-pixelated.glb',
    fallenLog: 'art-direction/3d/assets/biome_library/m7-pixelated.glb',
    treeStump: 'art-direction/3d/assets/biome_library/m8-pixelated.glb',
    mossBoulder: 'art-direction/3d/assets/biome_library/m9-pixelated.glb',
    // CC-C7 nest props: the EXISTING biome-library bone/rib pile (B6 batch,
    // on disk since the biome pass; 10,889 tris) - first manifest row.
    b6Bones: 'art-direction/3d/assets/biome_library/b6-bones-pixelated.glb',
    // R2: darkwood light-socket props (doc 61 batches B2/B3)
    banditCampfire: 'art-direction/3d/assets/biome_library/m15-bandit-campfire-pixelated.glb',
    lanternWaymarker: 'art-direction/3d/assets/biome_library/b3-waymarker-pixelated.glb',
    // C3 camps (js/camp.js): the bandit camp's world bedroll + the kit's
    // placeholder bedroll (CONFIG.camp.assets)
    banditBedroll: 'art-direction/3d/assets/biome_library/m16-bandit-bedroll-pixelated.glb',
    // C3.1c (Nicko 10-06): HIS Meshy tent (share C78d78, task 01a1130b) -
    // dreary medieval 1-person canvas, door +Z, bed roll modeled inside.
    // 1584k tris raw -> 30k decimated, per-face UV medoid, 512+5bit.
    // (scratch/tent_bake_c31c.py + tent_rebake_nodefault.py)
    whTent: 'art-direction/3d/assets/camp/wh-tent-pixelated.glb',
    // CK1 (Nicko 10-07): the player camp kit - ONE composed site, 4 root nodes
    // (tent / bedroll / firepit / pegs); camp.js makePiece extracts per node.
    whCampkit: 'art-direction/3d/assets/camp/wh-campkit-pixelated.glb',

    // church-kit props + trees
    // Round K (io/roundK-provenance.md): Meshy lantern-post-v2, one welded piece, decimated
    // 2500 + posterize512 (scratch/lanternpost_bake_roundK.py). Rollback = restore the line below.
    // lanternPost: 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb',
    // Round L (io/roundL-provenance.md): Meshy lantern-post-v3, arm-hook design (cage hangs
    // off-axis from the arm's hook), one welded piece, 2500 + posterize512
    // (scratch/lanternpost_bake_roundL.py). v2 retired to the comment below (rollback).
    // lanternPost: 'art-direction/3d/assets/church-kit/lantern-post-v2-pixelated.glb',
    lanternPost: 'art-direction/3d/assets/church-kit/lantern-post-v3-pixelated.glb',
    rubblePile: 'art-direction/3d/assets/church-kit/rubble-pile-pixelated.glb',
    churchArchway: 'art-direction/3d/assets/church-kit/church-archway-pixelated.glb',
    churchCornerButtress: 'art-direction/3d/assets/church-kit/church-corner-buttress-pixelated.glb',
    churchPewBroken: 'art-direction/3d/assets/church-kit/church-pew-broken-pixelated.glb',
    ironFenceSection: 'art-direction/3d/assets/church-kit/iron-fence-section-pixelated.glb',
    ironFenceCorner: 'art-direction/3d/assets/church-kit/iron-fence-corner-pixelated.glb',

    // characters (whanim1 rigged exports; props below stay rigid)
    // 10-04: rigged copy + WH_SlashR2L/WH_SlashL2R/WH_Thrust chain clips
    // (scratch/blender_chain_clips.py). Rollback: human-hunter-male.rigged.glb
    // Order D: + WH_ShieldRaise/WH_ShieldImpact/WH_ParrySwipe/
    // WH_GuardBreakStagger (scratch/blender_shield_clips.py, appended by
    // scratch/glb_append_clips.py - the 9 earlier clips are byte-identical).
    // 10-05 Round C: combat-chain.glb + 12 Mixamo WH_Sword*/WH_Shield* clips
    // (scratch/mixamo_player.json; chain clips byte-identical). Rollback:
    // human-hunter-male.combat-chain.glb
    playerBody: 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb',
    // DAG (2026-10-09) CLIP SOURCE ONLY (never instanced): a rigged.glb copy
    // + WH_DagSlashR2L / WH_DagSlashL2R / WH_DagSlashR2Lb (Phase A2,
    // scratch/blender_dagger_clips.py; same 22 nodes / 20 joints). player.js
    // setBody merges its WH_Dag* clips into the playerBody CharacterAnim, so
    // combat-sword.glb stays byte-identical. A failed load = no dagger clips
    // (dagger moves fall back to the shared 'attack' clip like handAxe).
    playerDagClips: 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-dagger.glb',
    banditBody: 'art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb',
    // 10-05: rigged copy + 7 Mixamo WH_*_Zombie clips (13 total).
    // Rollback: undead-ghoul-male.rigged.glb
    ghoulBody: 'art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.mixamo.glb',
    // CC-C5 (2026-10-11): the rigged wolf (21 joints, 6 WH_Wolf_* clips; the
    // 512px 5-bit atlas is embedded - mesh/skin/clips byte-identical to
    // wolf.rigged.glb, so no BODY_PNG row). Region C packs only.
    wolfBody: 'art-direction/3d/assets/races_regen/rigged/wolf.rigged.pixelated.glb',
    // CC-C7 (2026-10-12): the Rot Mother boss (17,573 tris) + her rot spawn
    // (2,094 tris), the SHIPPED 512px 5-bit pixelated bakes (raw-texture
    // twins rotmother.glb / rotspawn.glb are NOT for the game). UNRIGGED: no
    // CHARACTERS row (0 clips) - anim.js RIGID_CLIPS placeholders play.
    rotmotherBody: 'art-direction/3d/assets/races/rotmother-pixelated.glb',
    rotspawnBody: 'art-direction/3d/assets/races/rotspawn-pixelated.glb',

    // weapons (pixelated)
    longsword: 'art-direction/3d/assets/weapons/longsword-pixelated.glb',
    handAxe: 'art-direction/3d/assets/weapons/hand-axe-pixelated.glb',
    // DAG (2026-10-09) curved Meshy dagger (scratch/dagger_bake.py; NORMAL baked in)
    dagger: 'art-direction/3d/assets/weapons/dagger-curved-pixelated.glb',
    // 10-04 left-hand shield (no NORMAL attribute: prepTemplate rebuilds it)
    roundShield: 'art-direction/3d/assets/weapons/round-shield-pixelated.glb',
    // 10-05 hand torch (scratch/torch_bake.py; NORMAL baked in)
    torch: 'art-direction/3d/assets/weapons/torch-pixelated.glb'
  };

  // R4: rigged body -> offline-baked atlas (512 NEAREST + 5-bit posterize).
  var BODY_PNG = {
    playerBody: 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.pixelated.png',
    banditBody: 'art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.pixelated.png',
    ghoulBody: 'art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.rigged.pixelated.png'
  };

  // Resolve a manifest-relative path against the document base URL, falling
  // back to the parent directory when the page lives in a subdirectory
  // (e.g. builds/v2-playable.html must resolve art-direction/... at the
  // repo root, not at builds/art-direction/...).
  // Page at http://host/          -> http://host/art-direction/...
  // Page at http://host/witchhunter/ -> http://host/witchhunter/art-direction/...
  // Page at http://host/builds/x.html -> http://host/art-direction/...
  function resolveUrl(relPath) {
    try {
      var base = document.baseURI;
      var pageDir = base.slice(0, base.lastIndexOf('/') + 1);
      if (/\/builds\//.test(pageDir)) {
        pageDir = pageDir.replace(/\/builds\/$/, '/');
      }
      return new URL(relPath, pageDir).href;
    } catch (e) {
      // Extremely defensive: strip leading slash and fall back.
      return relPath.replace(/^\//, '');
    }
  }

  // Final resolved URL per logical name (populated at load time).
  var RESOLVED = {};
  Object.keys(MANIFEST).forEach(function (name) {
    RESOLVED[name] = resolveUrl(MANIFEST[name]);
  });

  // ---- Loading ---------------------------------------------------------------

  var cache = {};      // logical name -> ground-aligned THREE.Group template
  var clips = {};      // logical character name -> shared AnimationClip objects
  // value = expected clip count (load sanity check). Order B: playerBody's
  // combat-chain.glb legitimately holds 9 (6 whanim1 + WH_SlashR2L /
  // WH_SlashL2R / WH_Thrust) - the old flat "6" warned on every boot.
  // Order D: 13 = those 9 + the 4 shield/block clips.
  // Round C: 25 = those 13 + 12 Mixamo sword/shield clips (combat-sword.glb).
  // Round D: 28 = 13 + 12 + 3 Mixamo WH_SS_* chain attacks (the old "27"
  // here was off by one - the GLB census is 28).
  // MAGANIM Phase A: 42 = 28 + 14 WH_Mag_* (Lite Magic Pack, 5477e98).
  // DAG: playerDagClips 9 = 6 whanim1 + 3 WH_Dag* (clip source only).
  // CC-C5: wolfBody 6 = WH_Wolf_Idle/Walk/Run/Attack1/Hit/Death.
  var CHARACTERS = { playerBody: 43, banditBody: 6, ghoulBody: 6, playerDagClips: 9, wolfBody: 6 };
  var failed = {};     // logical name -> true (stand-in substituted)
  var loadedCount = 0;
  var GROUND_META = {}; // holder uuid -> measured height, width, raw groundMinY

  // 2026-10-03 grey-stand-in resilience (Astrabot, brief: io/missions/
  // 2026-10-03-astrabot-greybox-brief.md): a one-off multi-MB asset fetch
  // stall/timeout or parse error used to swap the procedural stand-in in
  // permanently on the FIRST load error (no retry, quiet warn), killing the
  // model AND its animation clips in one go. Now: ALL assets retry
  // (CONFIG.assets.bodyRetryCount, default 2) with backoff; if retries
  // exhaust, the stand-in stays but a loud one-line banner names the asset
  // and the cause (network vs parse vs timeout), stamped into the HUD.
  var BODY_RETRY_COUNT =
    (CFG.assets && typeof CFG.assets.bodyRetryCount === 'number') ?
      CFG.assets.bodyRetryCount : 2;
  var BODY_RETRY_DELAY_MS =
    (CFG.assets && typeof CFG.assets.bodyRetryDelayMs === 'number') ?
      CFG.assets.bodyRetryDelayMs : 750;
  var bootFailures = [];   // failed boot-critical assets (the loud red line)
  var lateFailures = [];   // failed deferred assets (dim line under it)

  // 2026-10-11 asset pipeline (io/missions/2026-10-11-asset-pipeline.md):
  // ~90 MB / 50 parallel fetches on a ~1 MB/s phone pipe under a flat 20 s
  // abort timed every multi-MB GLB out. Now: CONFIG.assets.bootCritical
  // loads first through a small pool (criticalPoolSize), the boot barrier
  // opens on those alone, the rest stream after (streamPoolSize) and
  // late-swap any stand-in instance handed out meanwhile. Each attempt's
  // timeout scales with the asset size and a timed-out fetch is ABORTED
  // (a zombie download would keep eating the pipe while its retry runs).
  var AC = CFG.assets || {};
  function cfgNum(key, dflt) { return typeof AC[key] === 'number' ? AC[key] : dflt; }
  var BYTES_PER_MB = 1e6;
  var TIMEOUT_PER_MB = cfgNum('assetTimeoutMsPerMb', 6000);
  var TIMEOUT_MIN_MS = cfgNum('assetTimeoutMinMs', 20000);
  var TIMEOUT_MAX_MS = cfgNum('assetTimeoutMaxMs', 120000);
  var CRITICAL_POOL = Math.max(1, cfgNum('criticalPoolSize', 4));
  var STREAM_POOL = Math.max(1, cfgNum('streamPoolSize', 6));
  var STALL_LINE_MS = cfgNum('stallLineAfterMs', 8000);

  // clamp(perMb x sizeMB, min, max); size unknown (0) = the min.
  function timeoutForBytes(bytes) {
    var ms = TIMEOUT_PER_MB * (bytes > 0 ? bytes : 0) / BYTES_PER_MB;
    return Math.round(Math.min(TIMEOUT_MAX_MS, Math.max(TIMEOUT_MIN_MS, ms)));
  }
  function mbText(bytes) { return (bytes / BYTES_PER_MB).toFixed(1); }

  // Boot-critical names in CONFIG order (unknown names dropped loudly);
  // DEFERRED = every other manifest name in manifest order.
  var IS_CRITICAL = {};
  var CRITICAL = (AC.bootCritical || []).filter(function (name) {
    if (!MANIFEST[name]) {
      console.warn('[WH assets] bootCritical names no manifest asset: ' + name);
      return false;
    }
    if (IS_CRITICAL[name]) return false;
    IS_CRITICAL[name] = true;
    return true;
  });
  var DEFERRED = Object.keys(MANIFEST).filter(function (name) { return !IS_CRITICAL[name]; });

  var status = {};         // name -> 'queued' | 'loading' | 'loaded' | 'failed'
  var knownBytes = {};     // name -> size learned from Content-Length (retries inherit)
  var active = {};         // name -> { loaded, total, start } of the attempt in flight
  var firstStart = {};     // name -> first attempt start (the stall line's clock)
  var pendingHolders = {}; // name -> stand-in holders handed out before it settled
  var bootDone = false;

  // 2026-10-03 loading screen (Nicko change order): REAL per-asset progress.
  // game.js registers a callback; 2026-10-11 it receives bootState() (the
  // boot-critical settled/total + received bytes + the slowest stalled
  // asset) on every critical settle, on byte progress (throttled) and on a
  // 1 s heartbeat until the boot barrier opens.
  var bootProgressCb = null;
  var lastProgressEmit = 0;
  function setBootProgressCb(fn) { bootProgressCb = fn; }
  function bootState() {
    var st = { done: 0, total: CRITICAL.length, loadedBytes: 0, knownBytes: 0, stall: null };
    var t = Date.now();
    CRITICAL.forEach(function (name) {
      var s = status[name], a = active[name];
      if (s === 'loaded' || s === 'failed') st.done++;
      if (a) {
        st.loadedBytes += a.loaded;
        st.knownBytes += a.total;
        var elapsed = t - firstStart[name];
        if (elapsed >= STALL_LINE_MS && (!st.stall || elapsed > st.stall.elapsedMs)) {
          st.stall = { name: name, loaded: a.loaded, total: a.total, elapsedMs: elapsed };
        }
      } else if (s === 'loaded') {
        st.loadedBytes += knownBytes[name] || 0;
        st.knownBytes += knownBytes[name] || 0;
      }
    });
    return st;
  }
  function bootProgressTick(force) {
    if (!bootProgressCb || bootDone) return;
    var t = Date.now();
    if (!force && t - lastProgressEmit < 250) return;
    lastProgressEmit = t;
    bootProgressCb(bootState());
  }
  function bootHeartbeat() {
    if (bootDone) return;
    bootProgressTick(true);
    setTimeout(bootHeartbeat, 1000);
  }

  function classifyError(err) {
    var msg = (err && (err.message || err.statusText)) || String(err || 'unknown');
    var reason;
    if (/abort|timed?\s*out/i.test(msg)) reason = 'timeout/abort';
    else if (/fetch|network|status\s*\d+/i.test(msg)) reason = 'network';
    else if (/parse|json|binary|magic|unsupported|header|version/i.test(msg)) reason = 'parse';
    else reason = 'load';
    return { reason: reason, msg: msg };
  }

  // HUD stamp: persistent one-liner in #wh-hud naming each stand-in asset +
  // cause, visible for the whole session regardless of the load-note lifecycle.
  // 2026-10-11: the loud line lists FAILED boot-critical assets only; failed
  // deferred (streamed) assets sit on a small dim line below it.
  function flushAssetFailureNote() {
    if (!bootFailures.length && !lateFailures.length) return;
    var parent = document.getElementById('wh-hud');
    if (!parent) return;
    var el = document.getElementById('wh-asset-fail-note');
    if (!el) {
      el = document.createElement('div');
      el.id = 'wh-asset-fail-note';
      el.style.cssText = 'position:absolute;top:128px;left:8px;font-size:12px;' +
        'color:#ff9d9d;z-index:40;letter-spacing:0.5px;text-transform:none;';
      parent.appendChild(el);
    }
    el.textContent = bootFailures.length ? 'Asset stand-in: ' + bootFailures.join(', ') : '';
    if (!lateFailures.length) return;
    var late = document.getElementById('wh-asset-fail-late');
    if (!late) {
      late = document.createElement('div');
      late.id = 'wh-asset-fail-late';
      late.style.cssText = 'font-size:10px;color:#a88;opacity:0.7;margin-top:2px;';
      el.appendChild(late);
    }
    late.textContent = 'streamed stand-in: ' + lateFailures.join(', ');
  }

  function makeStandIn(name) {
    // Procedural box/cone stand-in per spec hard constraint 5. Logged.
    console.warn('[WH assets] substitution: procedural stand-in for ' + name);
    failed[name] = true;
    return buildStandIn(name);
  }

  // The stand-in geometry alone: makeStandIn (final, marks failed) and the
  // placeholder instance() hands out while an asset is still in flight.
  function buildStandIn(name) {
    var group = new THREE.Group();
    var mat = new THREE.MeshStandardMaterial({
      color: CFG.assets.standInColor,
      roughness: 0.9,
      metalness: 0.0,
      side: THREE.DoubleSide
    });
    var mesh = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.8, 0.6), mat);
    mesh.name = 'standin-' + name;
    group.add(mesh);
    return groundAlign(group);
  }

  // Measure at identity before placement transforms. The inner correction
  // scales with the holder, unlike an offset baked on the template root.
  function groundAlign(root) {
    var box = new THREE.Box3().setFromObject(root);
    var valid = isFinite(box.min.y) && isFinite(box.max.y);
    var minY = valid ? box.min.y : 0;
    var holder = new THREE.Group();
    holder.add(root);
    root.position.y -= minY;
    holder.updateMatrixWorld(true);
    GROUND_META[holder.uuid] = {
      height: valid ? box.max.y - box.min.y : 1.8,
      width: valid ? box.max.x - box.min.x : 0,
      groundMinY: minY
    };
    return holder;
  }

  // Round J: per-asset extra sink below the groundAlign floor, gated by
  // name via CONFIG.assets.groundSink (GLB units, so it scales with the
  // holder). GROUND_META keeps the measured bounds; the sink is recorded.
  function applyGroundSink(name, root) {
    var sinks = CFG.assets && CFG.assets.groundSink;
    var sink = sinks && sinks[name];
    if (!(sink > 0)) return;
    var holder = root.parent;
    root.position.y -= sink;
    holder.updateMatrixWorld(true);
    GROUND_META[holder.uuid].groundSink = sink;
  }

  // 2026-10-03 measured weapon sizing (Nicko: "comically large"): divide the
  // CONFIG.assets.weaponTargetHeight goal by the MEASURED GROUND_META height
  // of the loaded GLB. Uniform axes mean height IS the blade/pommel length.
  // Kill switch: weaponScaleEnabled false (or no CONFIG table / no meta)
  // returns 1 so legacy hardcoded scaling applies untouched.
  function weaponScale(name) {
    var AC = CFG.assets;
    if (!AC || AC.weaponScaleEnabled === false) return 1;
    if (!AC.weaponTargetHeight || AC.weaponTargetHeight[name] === undefined) return 1;
    var tmpl = cache[name];
    var meta = tmpl && GROUND_META[tmpl.uuid];
    if (!meta || !(meta.height > 0)) return 1;
    return AC.weaponTargetHeight[name] / meta.height;
  }

  function prepTemplate(group, isPixelated) {
    // Render settings per validated Witch Hunter 3D setup:
    // DoubleSide for safety (R3), NearestFilter on pixelated textures (R2).
    group.traverse(function (obj) {
      if (!obj.isMesh) return;
      // 10-04: GLBs exported without NORMAL (round shield, some legacy
      // props) light as black under lit materials; rebuild before use.
      if (obj.geometry && obj.geometry.attributes &&
          obj.geometry.attributes.position && !obj.geometry.attributes.normal) {
        obj.geometry.computeVertexNormals();
      }
      if (obj.isSkinnedMesh) obj.frustumCulled = false;
      obj.castShadow = false;
      obj.receiveShadow = false;
      var mats = Array.isArray(obj.material) ? obj.material : [obj.material];
      mats.forEach(function (m) {
        if (!m) return;
        m.side = THREE.DoubleSide;
        if (m.map) {
          m.map.magFilter = isPixelated ? THREE.NearestFilter : m.map.magFilter;
          m.map.minFilter = isPixelated ? THREE.LinearMipmapLinearFilter : m.map.minFilter;
          m.map.generateMipmaps = true;
          m.map.needsUpdate = true;
        }
        if (m.isMeshStandardMaterial) {
          m.metalness = Math.min(m.metalness, 0.25);  // tame Meshy metalness (POC)
          m.roughness = Math.max(m.roughness, 0.6);
        }
      });
    });
    return group;
  }

  // R4 postload swap: replace the body's atlas map with its pixelated PNG
  // (the template map is shared by every clone). TextureLoader defaults are
  // wrong for glTF UVs (flipY true, no colour space), so set state explicitly.
  // Kill switch off, no PNG entry, or a PNG load error keeps the original.
  function swapBodyMap(name, root, done) {
    var rel = CFG.assets.pixelatedBodies && BODY_PNG[name];
    if (!rel) { done(); return; }
    new THREE.TextureLoader().load(resolveUrl(rel), function (tex) {
      root.traverse(function (obj) {
        if (!obj.isMesh) return;
        var mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        mats.forEach(function (m) {
          if (!m || !m.map || m.map === tex) return;
          var old = m.map;
          tex.flipY = false;
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.wrapS = old.wrapS;
          tex.wrapT = old.wrapT;
          tex.magFilter = THREE.NearestFilter;
          tex.minFilter = THREE.LinearMipmapLinearFilter;
          tex.generateMipmaps = true;
          tex.needsUpdate = true;
          m.map = tex;
          m.needsUpdate = true;
          old.dispose();
        });
      });
      done();
    }, undefined, function (err) {
      console.warn('[WH assets] pixelated atlas failed for ' + name + ', keeping original: ' + err);
      done();
    });
  }

  // CSP-safe embedded-texture intake (whanim3, 8f777bb): the manager
  // modifier is synchronous; populate it before the parser starts resolving
  // texture URLs. GLB image bufferViews are converted only once.
  var embeddedDataUris = new Map();
  var imageUrls = [];

  function registerEmbeddedImagePlugin(loader, mgr) {
    // CSP forbids even an attempted fetch(blob:) on enforced origins. Read
    // the RESPONSE POLICY, not the route name, before choosing the path.
    if (!registerEmbeddedImagePlugin.blobPolicy) {
      registerEmbeddedImagePlugin.blobPolicy =
        fetch(document.baseURI, { credentials: 'same-origin' })
          .then(function (response) {
            // 2026-10-11: only the headers matter - drop the page body (the
            // inlined build is MBs that would share the boot pipe)
            if (response.body && response.body.cancel) response.body.cancel().catch(function () {});
            var csp = response.headers.get('content-security-policy');
            if (!csp) return true;
            var match = csp.match(/(?:^|;)\s*connect-src\s+([^;]+)/i);
            return !match || /(?:^|\s)blob:(?:\s|$)/i.test(match[1]);
          }).catch(function (err) {
            console.warn('[WH assets] cannot inspect CSP; using FileReader for embedded images:', err);
            return false;
          });
    }
    function asDataUri(blob) {
      return new Promise(function (accept, reject) {
        var reader = new FileReader();
        reader.onload = function () { accept(reader.result); };
        reader.onerror = function () { reject(reader.error || new Error('image FileReader failed')); };
        reader.readAsDataURL(blob);
      });
    }
    function releaseAll() {
      imageUrls.forEach(function (u) {
        URL.revokeObjectURL(u);
        embeddedDataUris.delete(u);
      });
      imageUrls.length = 0;
    }
    mgr.setURLModifier(function (resourceUrl) {
      return resourceUrl.indexOf('blob:') === 0 && embeddedDataUris.has(resourceUrl) ?
        embeddedDataUris.get(resourceUrl) : resourceUrl;
    });
    loader.register(function (parser) {
      return {
        name: 'WH_embedded_image_data',
        beforeRoot: function () {
          var sources = parser.json.images || [];
          return registerEmbeddedImagePlugin.blobPolicy.then(function (canFetchBlob) {
            // ImageBitmapLoader decodes via fetch(data:), also forbidden by
            // connect-src on CSP origins. ImageLoader uses img-src instead.
            if (!canFetchBlob) parser.textureLoader = new THREE.TextureLoader(mgr);
            return Promise.all(sources.map(function (source) {
              if (source.bufferView === undefined || !/^image\//.test(source.mimeType || '')) {
                return Promise.resolve();
              }
              return parser.getDependency('bufferView', source.bufferView).then(function (bytes) {
                var blob = new Blob([bytes], { type: source.mimeType });
                var imageUrl = URL.createObjectURL(blob);
                imageUrls.push(imageUrl);
                var conversion = canFetchBlob ?
                  fetch(imageUrl).then(function (response) {
                    if (!response.ok) throw new Error('image fetch status ' + response.status);
                    return response.blob();
                  }).then(asDataUri).catch(function () { return asDataUri(blob); }) :
                  asDataUri(blob);
                return conversion.then(function (dataUri) {
                  embeddedDataUris.set(imageUrl, dataUri);
                  source.uri = imageUrl;
                  delete source.bufferView;
                });
              });
            }));
          }).catch(function (err) {
            releaseAll();
            throw err;
          });
        },
        afterRoot: function () { releaseAll(); }
      };
    });
  }

  // Stream the GLB bytes through fetch so the loader sees Content-Length +
  // per-chunk progress and can ABORT on timeout (GLTFLoader.load keeps its
  // FileLoader private). onBytes(received, contentLength or 0).
  function fetchBytes(url, ctrl, onBytes) {
    return fetch(url, { credentials: 'same-origin', signal: ctrl ? ctrl.signal : undefined })
      .then(function (res) {
        if (!res.ok) throw new Error('fetch status ' + res.status + ' ' + (res.statusText || ''));
        var len = parseInt(res.headers.get('Content-Length') || '', 10) || 0;
        onBytes(0, len);
        if (!res.body || !res.body.getReader) {
          return res.arrayBuffer().then(function (buf) {
            onBytes(buf.byteLength, len);
            return buf;
          });
        }
        var reader = res.body.getReader(), chunks = [], got = 0;
        function pump() {
          return reader.read().then(function (r) {
            if (r.done) {
              var out = new Uint8Array(got), off = 0;
              chunks.forEach(function (c) { out.set(c, off); off += c.byteLength; });
              return out.buffer;
            }
            chunks.push(r.value);
            got += r.value.byteLength;
            onBytes(got, len);
            return pump();
          });
        }
        return pump();
      });
  }

  // One load attempt, racing the per-attempt timeout. Resolves {ok:true,gltf}
  // or {ok:false,info:{reason,msg}}; never rejects. 2026-10-11: the deadline
  // (from attempt start) = timeoutForBytes(size): the size inherited from an
  // earlier attempt, else Content-Length once headers land, else the bytes
  // received so far - re-armed as the size becomes known. Covers fetch +
  // parse like the old flat timeout; on expiry the fetch is aborted.
  function loadAttempt(name, url) {
    return new Promise(function (resolve) {
      var settled = false, timer = null, limit = 0;
      var start = Date.now();
      var ctrl = typeof AbortController === 'function' ? new AbortController() : null;
      var job = active[name] = { loaded: 0, total: knownBytes[name] || 0, start: start };
      if (firstStart[name] === undefined) firstStart[name] = start;
      function finish(v) {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        if (active[name] === job) delete active[name];
        resolve(v);
      }
      function arm() {
        var ms = timeoutForBytes(Math.max(knownBytes[name] || 0, job.loaded));
        if (ms === limit) return;
        limit = ms;
        clearTimeout(timer);
        timer = setTimeout(function () {
          if (settled) return;
          if (ctrl) ctrl.abort();
          finish({ ok: false, info: { reason: 'timeout/abort',
            msg: 'no complete response within ' + limit + 'ms (' + mbText(job.loaded) +
              ' of ' + (job.total ? mbText(job.total) : '?') + ' MB)' } });
        }, Math.max(0, start + ms - Date.now()));
      }
      arm();
      fetchBytes(url, ctrl, function (loaded, total) {
        if (settled) return;
        job.loaded = loaded;
        if (total > 0) {
          job.total = total;
          knownBytes[name] = total;
        }
        arm();
        if (IS_CRITICAL[name]) bootProgressTick(false);
      }).then(function (buf) {
        if (settled) return;
        if (!knownBytes[name]) knownBytes[name] = buf.byteLength;
        var mgr = new THREE.LoadingManager();
        var loader = new window.WHGLTFLoader(mgr);
        registerEmbeddedImagePlugin(loader, mgr);
        loader.parse(buf, url.slice(0, url.lastIndexOf('/') + 1), function (gltf) {
          finish({ ok: true, gltf: gltf });
        }, function (err) {
          finish({ ok: false, info: classifyError(err) });
        });
      }, function (err) {
        finish({ ok: false, info: classifyError(err) });
      });
    });
  }

  function loadOne(name, url, isPixelated) {
    // Bounded retry applies to ALL assets (2026-10-03 change order, Nicko:
    // oak+witchwood stand-ins from a one-off tunnel stall): the multi-MB
    // fetches (rigged bodies, big biome trees) are the most exposed. Parse
    // failures do NOT retry (a corrupt file stays corrupt) - only network
    // and timeout/abort classes do. Stand-in fallback always remains.
    var maxAttempts = 1 + BODY_RETRY_COUNT;
    status[name] = 'loading';
    function attempt(n) {
      return loadAttempt(name, url).then(function (v) {
        if (v.ok) return v;
        var retryable = v.info.reason !== 'parse';
        if (retryable && n + 1 < maxAttempts) {
          var delay = BODY_RETRY_DELAY_MS * (n + 1);   // linear backoff
          console.warn('[WH assets] retry ' + (n + 1) + '/' + BODY_RETRY_COUNT +
            ' for ' + name + ' (' + v.info.reason + ') in ' + delay + 'ms');
          return new Promise(function (r) { setTimeout(r, delay); })
            .then(function () { return attempt(n + 1); });
        }
        return v;
      });
    }
    var settled = attempt(0).then(function (v) {
      if (v.ok) {
        var root = v.gltf.scene;
        if (CHARACTERS[name]) {
          clips[name] = v.gltf.animations || [];
          if (clips[name].length !== CHARACTERS[name]) {
            console.warn('[WH assets] expected ' + CHARACTERS[name] + ' clips for ' +
              name + ', got ' + clips[name].length);
          }
        }
        prepTemplate(root, isPixelated);
        cache[name] = groundAlign(root);
        applyGroundSink(name, root);
        return new Promise(function (resolve) {
          swapBodyMap(name, root, function () {
            loadedCount++;
            status[name] = 'loaded';
            lateSwap(name);
            resolve(cache[name]);
          });
        });
      }
      var info = v.info;
      // LOUD end-of-retries banner: names the asset and WHY (network vs parse
      // vs timeout), styled so it cannot scroll past unnoticed.
      console.error('%c[WH ASSETS] STAND-IN: ' + name + ' failed to load (' +
        info.reason + ') after ' + maxAttempts + ' attempt(s). URL: ' + url +
        ' CAUSE: ' + info.msg + ' - model + animations dead for this session.',
        'background:#4d0000;color:#ffdddd;padding:2px 6px;font-weight:bold');
      cache[name] = makeStandIn(name);
      status[name] = 'failed';
      delete pendingHolders[name];   // the handed-out stand-ins simply stay
      (IS_CRITICAL[name] ? bootFailures : lateFailures)
        .push(name + ' (' + info.reason + ' - ' + info.msg + ')');
      flushAssetFailureNote();
      return cache[name];
    });
    // 2026-10-03 loading screen: tick exactly once per asset, after it
    // settles as loaded OR stand-in (swapBodyMap atlas wait included).
    return settled.then(function (res) {
      if (IS_CRITICAL[name]) bootProgressTick(true);
      return res;
    });
  }

  function loadByName(name) {
    var url = RESOLVED[name];
    return loadOne(name, url, url.indexOf('-pixelated') !== -1);
  }

  // At most `size` loads in flight, started in list order; resolves once
  // every name settled (loadOne never rejects).
  function runPool(names, size, run) {
    return new Promise(function (resolve) {
      var next = 0, inFlight = 0, done = 0;
      if (!names.length) { resolve(); return; }
      function pump() {
        while (inFlight < size && next < names.length) {
          inFlight++;
          run(names[next++]).then(function () {
            inFlight--;
            done++;
            if (done === names.length) resolve();
            else pump();
          });
        }
      }
      pump();
    });
  }

  // 2026-10-11 two-phase preload. Resolves (the BOOT BARRIER) once every
  // bootCritical asset settled; failures become stand-ins, never block boot.
  // The deferred names then stream through the larger pool - whenAllSettled()
  // resolves when they are in too.
  var bootPromise = null, allPromise = null;
  function preloadAll() {
    if (bootPromise) return bootPromise;
    Object.keys(MANIFEST).forEach(function (name) { status[name] = 'queued'; });
    bootHeartbeat();
    bootPromise = runPool(CRITICAL, CRITICAL_POOL, loadByName).then(function () {
      bootDone = true;
      console.log('[WH assets] boot barrier: ' + CRITICAL.length + ' critical assets settled (' +
        bootFailures.length + ' stand-ins); streaming ' + DEFERRED.length + ' more');
      return cache;
    });
    allPromise = bootPromise.then(function () {
      return runPool(DEFERRED, STREAM_POOL, loadByName);
    }).then(function () {
      console.log('[WH assets] loaded ' + loadedCount + ' assets, ' +
        Object.keys(failed).length + ' stand-ins');
      return cache;
    });
    return bootPromise;
  }

  function whenAllSettled() {
    preloadAll();
    return allPromise;
  }

  // Rigged characters need independently rebound bones; props remain rigid.
  function cloneTemplate(name, tmpl) {
    if (CHARACTERS[name] && clips[name] && clips[name].length) {
      return window.WHSkeletonUtils.clone(tmpl);
    }
    return tmpl.clone(true);
  }

  // 2026-10-11: an asset still in flight hands out a placeholder stand-in
  // (NOT marked failed); lateSwap puts the real mesh into that same holder
  // when the asset lands, so the caller's placement transform stays. A
  // late-swapped rigged body gets the mesh, not the clips (the boot bodies
  // are all bootCritical, so no live caller hits that).
  function instance(name) {
    var tmpl = cache[name];
    if (!tmpl) {
      if (status[name] === 'queued' || status[name] === 'loading') {
        var holder = buildStandIn(name);
        (pendingHolders[name] = pendingHolders[name] || []).push(holder);
        return holder;
      }
      return makeStandIn(name);
    }
    return cloneTemplate(name, tmpl);
  }

  function lateSwap(name) {
    var list = pendingHolders[name];
    if (!list) return;
    delete pendingHolders[name];
    list.forEach(function (holder) {
      var old = holder.children[0];
      holder.remove(old);
      old.traverse(function (o) {
        if (!o.isMesh) return;
        o.geometry.dispose();
        o.material.dispose();
      });
      holder.add(cloneTemplate(name, cache[name]).children[0]);
      holder.updateMatrixWorld(true);
    });
    console.log('[WH assets] late swap: ' + name + ' replaced ' + list.length + ' stand-in(s)');
  }

  window.WH_ASSETS = {
    MANIFEST: MANIFEST,
    RESOLVED: RESOLVED,
    resolveUrl: resolveUrl,
    setBootProgressCb: setBootProgressCb,
    preloadAll: preloadAll,
    whenAllSettled: whenAllSettled,
    CRITICAL: CRITICAL,
    DEFERRED: DEFERRED,
    bootState: bootState,
    timeoutForBytes: timeoutForBytes,
    instance: instance,
    getClips: function (name) { return clips[name] || []; },
    getTemplate: function (name) { return cache[name] || null; },
    groundHeight: function (name) {
      var tmpl = cache[name];
      if (!tmpl) return 1.8;
      var meta = GROUND_META[tmpl.uuid];
      return meta ? meta.height : 1.8;
    },
    groundMinY: function (name) {
      var tmpl = cache[name];
      var meta = tmpl && GROUND_META[tmpl.uuid];
      return meta ? meta.groundMinY : 0;
    },
    getMeta: function (name) {
      var tmpl = cache[name];
      var meta = tmpl && GROUND_META[tmpl.uuid];
      return meta ? { height: meta.height, width: meta.width,
                      groundMinY: meta.groundMinY } : null;
    },
    weaponScale: weaponScale,
    isLoaded: function (name) { return !!cache[name]; },
    isFailed: function (name) { return !!failed[name]; },
    isPending: function (name) { return status[name] === 'queued' || status[name] === 'loading'; },
    loadedCount: function () { return loadedCount; }
  };
})();