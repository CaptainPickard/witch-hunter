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
    fallenLog: 'art-direction/3d/assets/biome_library/m7-pixelated.glb',
    treeStump: 'art-direction/3d/assets/biome_library/m8-pixelated.glb',
    mossBoulder: 'art-direction/3d/assets/biome_library/m9-pixelated.glb',
    // R2: darkwood light-socket props (doc 61 batches B2/B3)
    banditCampfire: 'art-direction/3d/assets/biome_library/m15-bandit-campfire-pixelated.glb',
    lanternWaymarker: 'art-direction/3d/assets/biome_library/b3-waymarker-pixelated.glb',

    // church-kit props + trees
    lanternPost: 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb',
    rubblePile: 'art-direction/3d/assets/church-kit/rubble-pile-pixelated.glb',
    churchArchway: 'art-direction/3d/assets/church-kit/church-archway-pixelated.glb',
    churchCornerButtress: 'art-direction/3d/assets/church-kit/church-corner-buttress-pixelated.glb',
    churchPewBroken: 'art-direction/3d/assets/church-kit/church-pew-broken-pixelated.glb',
    ironFenceSection: 'art-direction/3d/assets/church-kit/iron-fence-section-pixelated.glb',
    ironFenceCorner: 'art-direction/3d/assets/church-kit/iron-fence-corner-pixelated.glb',

    // characters (whanim1 rigged exports; props below stay rigid)
    // 10-04: rigged copy + WH_SlashR2L/WH_SlashL2R/WH_Thrust chain clips
    // (scratch/blender_chain_clips.py). Rollback: human-hunter-male.rigged.glb
    // 10-05 Round C: combat-chain.glb + 12 Mixamo WH_Sword*/WH_Shield* clips
    // (scratch/mixamo_player.json; chain clips byte-identical). Rollback:
    // human-hunter-male.combat-chain.glb
    // Round D: + 3 Mixamo WH_SS_* chain attacks (24 total).
    playerBody: 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb',
    banditBody: 'art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb',
    // 10-05: rigged copy + 7 Mixamo WH_*_Zombie clips (13 total).
    // Rollback: undead-ghoul-male.rigged.glb
    ghoulBody: 'art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.mixamo.glb',

    // weapons (pixelated)
    longsword: 'art-direction/3d/assets/weapons/longsword-pixelated.glb',
    handAxe: 'art-direction/3d/assets/weapons/hand-axe-pixelated.glb'
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
  var CHARACTERS = { playerBody: true, banditBody: true, ghoulBody: true };
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
  var bootFailures = [];

  // 2026-10-03 loading screen (Nicko change order): REAL per-asset progress.
  // game.js registers a callback fired on each manifest asset settling
  // (loaded OR stand-in), so the bar fraction is settled/total; retry
  // backoff just delays that asset's tick.
  var bootProgressCb = null;
  function setBootProgressCb(fn) { bootProgressCb = fn; }
  function bootProgressTick() {
    if (bootProgressCb) bootProgressCb();
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
  function flushAssetFailureNote() {
    if (!bootFailures.length) return;
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
    el.textContent = 'Asset stand-in: ' + bootFailures.join(', ');
  }

  function makeStandIn(name) {
    // Procedural box/cone stand-in per spec hard constraint 5. Logged.
    console.warn('[WH assets] substitution: procedural stand-in for ' + name);
    failed[name] = true;
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

  // One load attempt, racing the per-attempt timeout. Resolves {ok:true,gltf}
  // or {ok:false,info:{reason,msg}}; never rejects.
  function loadAttempt(name, url) {
    return new Promise(function (resolve) {
      var settled = false;
      var mgr = new THREE.LoadingManager();
      var loader = new window.WHGLTFLoader(mgr);
      registerEmbeddedImagePlugin(loader, mgr);
      var timer = setTimeout(function () {
        if (settled) return;
        settled = true;
        resolve({ ok: false, info: { reason: 'timeout/abort',
          msg: 'no response within ' + CFG.assets.timeoutMs + 'ms' } });
      }, CFG.assets.timeoutMs);
      loader.load(url, function (gltf) {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolve({ ok: true, gltf: gltf });
      }, undefined, function (err) {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolve({ ok: false, info: classifyError(err) });
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
          // playerBody combat-sword.glb: 9 chain + 12 Sword (Round C) + 3 SS (Round D).
          var expected = name === 'playerBody' ? 24 : 6;
          if (clips[name].length !== expected) {
            console.warn('[WH assets] expected ' + expected + ' clips for ' + name +
              ', got ' + clips[name].length);
          }
        }
        prepTemplate(root, isPixelated);
        cache[name] = groundAlign(root);
        return new Promise(function (resolve) {
          swapBodyMap(name, root, function () {
            loadedCount++;
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
      bootFailures.push(name + ' (' + info.reason + ' - ' + info.msg + ')');
      flushAssetFailureNote();
      return cache[name];
    });
    // 2026-10-03 loading screen: tick exactly once per asset, after it
    // settles as loaded OR stand-in (swapBodyMap atlas wait included).
    return settled.then(function (res) {
      bootProgressTick();
      return res;
    });
  }

  // Preload every manifest entry. Resolves when all settle (failures become
  // stand-ins, never block boot).
  function preloadAll() {
    var jobs = [];
    Object.keys(MANIFEST).forEach(function (name) {
      var url = RESOLVED[name];
      jobs.push(loadOne(name, url, url.indexOf('-pixelated') !== -1));
    });
    return Promise.all(jobs).then(function () {
      console.log('[WH assets] loaded ' + loadedCount + ' assets, ' +
        Object.keys(failed).length + ' stand-ins');
      return cache;
    });
  }

  // Rigged characters need independently rebound bones; props remain rigid.
  function instance(name) {
    var tmpl = cache[name];
    if (!tmpl) return makeStandIn(name);
    if (CHARACTERS[name] && clips[name] && clips[name].length) {
      return window.WHSkeletonUtils.clone(tmpl);
    }
    return tmpl.clone(true);
  }

  window.WH_ASSETS = {
    MANIFEST: MANIFEST,
    RESOLVED: RESOLVED,
    resolveUrl: resolveUrl,
    setBootProgressCb: setBootProgressCb,
    preloadAll: preloadAll,
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
    loadedCount: function () { return loadedCount; }
  };
})();