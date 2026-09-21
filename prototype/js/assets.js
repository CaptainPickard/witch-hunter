// Witch Hunter prototype v2 - asset manifest + GLB loading.
// D1 fix: manifest paths are RELATIVE (no leading slash) and are resolved
// against document.baseURI at load time via new URL(...).href, so the game
// works identically served at / and under any proxy prefix such as
// /witchhunter/ (tailnet path). Do not hardcode proxy prefixes here.
// Prefer -pixelated variants for props; races_regen characters have no
// pixelated variants (D4b-3), raw mesh is accepted for characters.

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

    // church-kit props + trees
    lanternPost: 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb',
    deadTree: 'art-direction/3d/assets/church-kit/dead-tree-pixelated.glb',
    rubblePile: 'art-direction/3d/assets/church-kit/rubble-pile-pixelated.glb',
    churchArchway: 'art-direction/3d/assets/church-kit/church-archway-pixelated.glb',
    churchCornerButtress: 'art-direction/3d/assets/church-kit/church-corner-buttress-pixelated.glb',
    churchPewBroken: 'art-direction/3d/assets/church-kit/church-pew-broken-pixelated.glb',

    // characters (races_regen, raw meshes, no pixelated variants exist)
    playerBody: 'art-direction/3d/assets/races_regen/human-hunter-male.glb',
    banditBody: 'art-direction/3d/assets/races_regen/orc-male-warrior.glb',
    ghoulBody: 'art-direction/3d/assets/races_regen/undead-ghoul-male.glb',

    // weapons (pixelated)
    longsword: 'art-direction/3d/assets/weapons/longsword-pixelated.glb'
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

  var cache = {};      // logical name -> cloned THREE.Group template
  var failed = {};     // logical name -> true (stand-in substituted)
  var loadedCount = 0;
  var GROUND_META = {}; // template uuid -> {height, width} measured bbox

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
    return group;
  }

  // Ground-align a loaded GLB template. Meshy meshes ship with a CENTERED
  // pivot (bounds span y=-1..+1), so an instance placed at y=0 sinks half
  // its height into the ground. Measure the template's world bbox once and
  // shift the template's inner root so minY sits at y=0. Instances then
  // inherit the correction via clone(true). Store the measured height for
  // scale normalization by callers.
  function groundAlign(group) {
    var box = new THREE.Box3().setFromObject(group);
    if (!isFinite(box.min.y) || !isFinite(box.max.y)) return;
    var minY = box.min.y;
    group.position.y -= minY;          // shift so feet/minY = 0
    group.updateMatrixWorld(true);
    GROUND_META[group.uuid] = {
      height: box.max.y - box.min.y,
      width: box.max.x - box.min.x
    };
  }

  function prepTemplate(group, isPixelated) {
    // Render settings per validated Witch Hunter 3D setup:
    // DoubleSide for safety (R3), NearestFilter on pixelated textures (R2).
    group.traverse(function (obj) {
      if (!obj.isMesh) return;
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

  function loadOne(name, url, isPixelated) {
    return new Promise(function (resolve) {
      var loader = new window.WHGLTFLoader();
      var done = false;
      var timer = setTimeout(function () {
        if (!done) { done = true; resolve(makeStandIn(name)); }
      }, CFG.assets.timeoutMs);
      loader.load(url, function (gltf) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        var root = gltf.scene;
        prepTemplate(root, isPixelated);
        groundAlign(root);
        cache[name] = root;
        loadedCount++;
        resolve(root);
      }, undefined, function (err) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        console.warn('[WH assets] load failed for ' + name + ' at ' + url + ': ' + err);
        resolve(makeStandIn(name));
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

  // Instance a fresh copy from the cache (Scene.clone(true) clones meshes).
  function instance(name) {
    var tmpl = cache[name];
    if (!tmpl) return makeStandIn(name);
    return tmpl.clone(true);
  }

  window.WH_ASSETS = {
    MANIFEST: MANIFEST,
    RESOLVED: RESOLVED,
    resolveUrl: resolveUrl,
    preloadAll: preloadAll,
    instance: instance,
    groundHeight: function (name) {
      var tmpl = cache[name];
      if (!tmpl) return 1.8;
      var meta = GROUND_META[tmpl.uuid];
      return meta ? meta.height : 1.8;
    },
    isLoaded: function (name) { return !!cache[name]; },
    isFailed: function (name) { return !!failed[name]; },
    loadedCount: function () { return loadedCount; }
  };
})();