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
    livingOak: 'art-direction/3d/assets/biome_library/m4-pixelated.glb',
    yewTree: 'art-direction/3d/assets/biome_library/m5-pixelated.glb',
    witchwoodTree: 'art-direction/3d/assets/biome_library/m6-pixelated.glb',
    fallenLog: 'art-direction/3d/assets/biome_library/m7-pixelated.glb',
    treeStump: 'art-direction/3d/assets/biome_library/m8-pixelated.glb',
    mossBoulder: 'art-direction/3d/assets/biome_library/m9-pixelated.glb',
    // R2: darkwood light-socket props (doc 61 batches B2/B3)
    banditCampfire: 'art-direction/3d/assets/biome_library/m15-bandit-campfire-pixelated.glb',
    lanternWaymarker: 'art-direction/3d/assets/biome_library/b3-waymarker-pixelated.glb',

    // church-kit props + trees
    lanternPost: 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb',
    deadTree: 'art-direction/3d/assets/church-kit/dead-tree-pixelated.glb',
    rubblePile: 'art-direction/3d/assets/church-kit/rubble-pile-pixelated.glb',
    churchArchway: 'art-direction/3d/assets/church-kit/church-archway-pixelated.glb',
    churchCornerButtress: 'art-direction/3d/assets/church-kit/church-corner-buttress-pixelated.glb',
    churchPewBroken: 'art-direction/3d/assets/church-kit/church-pew-broken-pixelated.glb',
    ironFenceSection: 'art-direction/3d/assets/church-kit/iron-fence-section-pixelated.glb',
    ironFenceCorner: 'art-direction/3d/assets/church-kit/iron-fence-corner-pixelated.glb',

    // characters (whanim1 rigged exports; props below stay rigid)
    playerBody: 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.glb',
    banditBody: 'art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.glb',
    ghoulBody: 'art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.rigged.glb',

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

  function loadOne(name, url, isPixelated) {
    return new Promise(function (resolve) {
      var loader = new window.WHGLTFLoader();
      var done = false;
      var timer = setTimeout(function () {
        if (!done) {
          done = true;
          cache[name] = makeStandIn(name);
          resolve(cache[name]);
        }
      }, CFG.assets.timeoutMs);
      loader.load(url, function (gltf) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        var root = gltf.scene;
        if (CHARACTERS[name]) {
          clips[name] = gltf.animations || [];
          if (clips[name].length !== 6) {
            console.warn('[WH assets] expected 6 clips for ' + name + ', got ' + clips[name].length);
          }
        }
        prepTemplate(root, isPixelated);
        cache[name] = groundAlign(root);
        swapBodyMap(name, root, function () {
          loadedCount++;
          resolve(cache[name]);
        });
      }, undefined, function (err) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        console.warn('[WH assets] load failed for ' + name + ' at ' + url + ': ' + err);
        cache[name] = makeStandIn(name);
        resolve(cache[name]);
      });
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
    isLoaded: function (name) { return !!cache[name]; },
    isFailed: function (name) { return !!failed[name]; },
    loadedCount: function () { return loadedCount; }
  };
})();