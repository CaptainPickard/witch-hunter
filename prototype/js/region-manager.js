// Witch Hunter prototype v1 - THE CORE SYSTEM: instance-region lifecycle.
// Single active region, pre-warm + hysteresis, per-region state persistence,
// boundary blocked except the chokepoint. Transition logic helpers are
// THREE-free so the validation harness can exercise them with mocks.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var DEFS = window.WH_REGION_DEFS;

  // ---- THREE-free transition core (RegionManagerLogic) -----------------------
  // Pure state machine over ids/numbers. No THREE, no document. The live
  // RegionManager delegates to this so behavior is testable DOM-free.

  function RegionManagerLogic(initialRegionId) {
    this.activeId = initialRegionId;
    this.prewarmedId = null;
    this.buildCounts = {};            // regionId -> times built
    this.buildCounts[initialRegionId] = 1;
    this.regionStates = {};           // regionId -> { enemies: {idx: 'dead'|...} }
    this.boundary = CFG.boundary;
    this.chokepoint = CFG.chokepoint;
    this.preWarmDistance = CFG.preWarm.distance;
    this.hysteresisDistance = CFG.preWarm.hysteresis;
  }

  RegionManagerLogic.prototype.activeRegionIds = function () {
    return [this.activeId];
  };

  RegionManagerLogic.prototype.stateFor = function (regionId) {
    if (!this.regionStates[regionId]) {
      this.regionStates[regionId] = { enemies: {}, crossed: 0 };
    }
    return this.regionStates[regionId];
  };

  // Returns null, 'prewarm' (neighbor built hidden), 'dispose' (pre-warm
  // thrown away), or 'cross' (region swap; newActiveId set).
  RegionManagerLogic.prototype.tickTransition = function (x, z) {
    var result = { action: null, newActiveId: null, mappedPos: null };
    var conn = DEFS.connectionBetween(this.activeId, DEFS.neighborOf(this.activeId));
    if (!conn) return result;

    var dist = DEFS.distanceToBoundary(conn, z);
    var neighborId = DEFS.neighborOf(this.activeId);
    var insideChoke = DEFS.insideChokepoint(conn, x);

    // crossing: player crossed the plane inside the chokepoint corridor.
    // Direction-agnostic: fires when the player's plane side differs from the
    // ACTIVE region's home side (walking into the neighbor's half), so both
    // A->B and B->A crossings trigger. (The old code compared against the
    // fixed conn.fromSide, which made B->A returns impossible.)
    var sideNow = DEFS.sideOfPlane(conn, z);
    var activeSide = DEFS.regions[this.activeId].side;
    if (insideChoke && sideNow !== activeSide) {
      // map position across, preserving approach direction: place the player
      // just past the plane ON THE NEIGHBOR'S HOME SIDE (not merely the
      // opposite of their current side, which can re-trigger a cross back).
      var mapped = DEFS.mapPositionAcross(conn, x, z, 2,
        DEFS.regions[neighborId].side);
      result.action = 'cross';
      result.newActiveId = neighborId;
      result.mappedPos = mapped;
      this.stateFor(this.activeId).crossed++;
      this.stateFor(neighborId).crossed++;
      this.activeId = neighborId;
      this.prewarmedId = null;         // consumed by the swap
      this.buildCounts[neighborId] = (this.buildCounts[neighborId] || 0) + 1;
      return result;
    }

    // pre-warm: close to boundary, approach direction faces the neighbor
    if (dist <= this.preWarmDistance && this.prewarmedId !== neighborId) {
      this.prewarmedId = neighborId;
      this.buildCounts[neighborId] = (this.buildCounts[neighborId] || 0) + 1;
      result.action = 'prewarm';
      return result;
    }

    // hysteresis: player turned back beyond pre-warm band -> dispose pre-warm
    if (this.prewarmedId !== null &&
        dist > this.preWarmDistance + this.hysteresisDistance) {
      this.prewarmedId = null;
      result.action = 'dispose';
      return result;
    }

    return result;
  };

  // Boundary clamp for the player: blocked everywhere except inside the
  // chokepoint interval. Returns true if the position was clamped.
  // Clamp by the ACTIVE region's home side (logic.activeId), not by the
  // position's current side: a player who walks past the plane outside the
  // corridor is trespassing on the neighbor's side and must be pushed back
  // into their own region, regardless of which side they are now on.
  RegionManagerLogic.prototype.clampPlayerPlane = function (pos) {
    var conn = DEFS.connections[0];
    if (!conn) return false;
    var insideChoke = DEFS.insideChokepoint(conn, pos.x);
    if (insideChoke) return false;     // free passage in the corridor
    var homeSide = DEFS.regions[this.activeId].side;   // +1 for A, -1 for B
    if (homeSide === 1) {
      // A side: keep z >= planeCoord (+ small epsilon)
      if (pos.z < conn.planeCoord) { pos.z = conn.planeCoord; return true; }
    } else {
      // B side: keep z <= planeCoord
      if (pos.z > conn.planeCoord) { pos.z = conn.planeCoord; return true; }
    }
    return false;
  };

  // Enemies never cross: hold at the boundary on the home-region side.
  RegionManagerLogic.prototype.clampEnemyToHomeSide = function (enemy, boundary) {
    var conn = DEFS.connections[0];
    if (!conn) return false;
    var margin = CFG.enemy.holdAtBoundaryMargin;
    var isHomeA = enemy.homeRegionId === CFG.regionA.id;
    var clamped = false;
    if (isHomeA) {
      // A enemies stay on +z side; also block them sliding along x outside
      // the chokepoint into B, and hold them back by the margin even in the
      // corridor (enemies never cross, spec D2).
      var limit = conn.planeCoord + margin;
      if (enemy.pos.z < limit) { enemy.pos.z = limit; clamped = true; }
    } else {
      var limitB = conn.planeCoord - margin;
      if (enemy.pos.z > limitB) { enemy.pos.z = limitB; clamped = true; }
    }
    // R5 P0-5 (C11): enemies share the player's rim; the home-side hold line
    // stays authoritative when the radial pull would cross it.
    if (whClampRadial(enemy.pos, whPlayRadius(), isHomeA ? 1 : -1,
        conn.planeCoord + (isHomeA ? margin : -margin))) clamped = true;
    return clamped;
  };

  // ---- R5 P0-5: world bounds + prop colliders (no THREE import) -------------

  // Playable disc radius: player and enemies are held inside it.
  function whPlayRadius() {
    return CFG.world.groundRadius - CFG.world.playerMargin;
  }

  // Visual ground radius per region. FogExp2 is 95% opaque at
  // d95 = sqrt(-ln(1 - fogOpaqueFrac)) / density; the disc reaches
  // visualGroundFogMult * d95 past the playable rim so its edge is never seen.
  function whVisualGroundRadius(regionId) {
    var W = CFG.world;
    var d95 = Math.sqrt(-Math.log(1 - W.fogOpaqueFrac)) /
      DEFS.regions[regionId].fogDensity;
    return Math.max(W.groundRadius, whPlayRadius() + W.visualGroundFogMult * d95);
  }

  // Radial rim clamp that respects a home-side plane limit (limitZ null = no
  // limit). Pulling toward the origin moves z toward 0, which can re-cross
  // the plane on B's side: then slide along the plane line onto the rim.
  function whClampRadial(pos, r, side, limitZ) {
    var d = Math.sqrt(pos.x * pos.x + pos.z * pos.z);
    if (!(d > r)) return false;        // inside (NaN is left to the callers)
    var k = r / d;
    pos.x *= k;
    pos.z *= k;
    if (limitZ !== null && (side === 1 ? pos.z < limitZ : pos.z > limitZ)) {
      pos.z = limitZ;
      pos.x = (pos.x < 0 ? -1 : 1) * Math.sqrt(Math.max(0, r * r - limitZ * limitZ));
    }
    return true;
  }

  // Does a prop circle meet the gate corridor rectangle (chokepoint x-span,
  // boundary.z +- colliderCorridorHalfDepth)? Such props never collide.
  function whMeetsCorridor(x, z, r) {
    var hw = CFG.chokepoint.width / 2;
    var hd = CFG.world.colliderCorridorHalfDepth;
    var nx = Math.max(CFG.chokepoint.centerX - hw, Math.min(CFG.chokepoint.centerX + hw, x));
    var nz = Math.max(CFG.boundary.z - hd, Math.min(CFG.boundary.z + hd, z));
    var dx = x - nx, dz = z - nz;
    return dx * dx + dz * dz <= r * r;
  }

  // Collider table for one region from CONFIG props + asset footprints.
  // C14 (IO ruling, R5): vegetation-class (trunk-dominant) props get TRUNK
  // colliders — radius = footprint/2 * TRUNK_RATIO — canopy leaves must be
  // brushable; trunk-is-the-body props (posts/stones/boulders/fences) keep
  // the full footprint. Devbot-classified list: TRUNK_ASSETS.
  var TRUNK_RATIO = 0.25;
  var TRUNK_ASSETS = { livingOak: 1, witchwoodTree: 1, birchTree: 1,
    deadTree: 1, deadTree2: 1, ancientOak: 1, hangingTree: 1,
    twistedSapling: 1, thornbush: 1, bramble: 1, largeFern: 1, deadShrub: 1,
    mossyStump: 1, hollowStump: 1 };
  function colliderRadius(name, width, scale) {
    var r = width * scale / 2;
    if (TRUNK_ASSETS[name] || /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name)) {
      return r * TRUNK_RATIO;
    }
    return r;
  }

  function whPropColliders(regionId, meta) {
    var props = DEFS.regions[regionId].cfg.props;
    var out = { circles: [], exempt: [], complete: true };
    for (var i = 0; i < props.length; i++) {
      var p = props[i];
      var m = meta(p.asset);
      if (!m) out.complete = false;
      var row = { index: i, name: p.asset, x: p.x, z: p.z,
                  r: m ? colliderRadius(p.asset, m.width, p.scale) : 0 };
      if (whMeetsCorridor(p.x, p.z, row.r)) out.exempt.push(row);
      else if (row.r > 0) out.circles.push(row);
    }
    return out;
  }

  RegionManagerLogic.prototype.playRadius = whPlayRadius;
  RegionManagerLogic.prototype.visualGroundRadius = whVisualGroundRadius;

  // Full player clamp = boundary plane + radial rim in ONE call (game.js
  // clampPlayerToBounds returns early on true, so the rim must not depend on
  // the plane clamp not firing). Returns true if either clamp fired.
  RegionManagerLogic.prototype.clampPlayer = function (pos) {
    var plane = this.clampPlayerPlane(pos);
    var conn = DEFS.connections[0];
    var limitZ = (conn && !DEFS.insideChokepoint(conn, pos.x)) ? conn.planeCoord : null;
    var rim = whClampRadial(pos, whPlayRadius(), DEFS.regions[this.activeId].side, limitZ);
    return plane || rim;
  };

  // Circle push-out against static colliders [{x, z, r}]: afterwards
  // |pos - c| >= c.r + radius for each circle visited; a dead-centre hit
  // pushes along +x (no NaN).
  RegionManagerLogic.prototype.pushOutCircles = function (pos, radius, circles) {
    var hit = false;
    for (var i = 0; i < circles.length; i++) {
      var c = circles[i];
      var dx = pos.x - c.x, dz = pos.z - c.z;
      var min = c.r + radius;
      var d2 = dx * dx + dz * dz;
      if (!(d2 < min * min)) continue;
      var d = Math.sqrt(d2);
      if (d < 1e-6) { dx = 1; dz = 0; d = 1; }
      pos.x = c.x + dx / d * min;
      pos.z = c.z + dz / d * min;
      hit = true;
    }
    return hit;
  };

  // ---- Procedural pixel-art ground texture (darkwood palette) ----------------
  // Boot-time cost only: one 256x256 canvas per region, cached on the canvas
  // element (region dispose throws away the CanvasTexture wrapper, the canvas
  // itself is reused on rebuild). No per-frame work.

  var GROUND_CANVAS_CACHE = {};

  function whRng(seed) {
    // mulberry32: small deterministic PRNG so each region's texture is stable.
    return function () {
      seed |= 0;
      seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function whHexToRgb(hex) {
    return [(hex >> 16) & 255, (hex >> 8) & 255, hex & 255];
  }

  function whCss(rgb, jitter, rand) {
    var j = Math.round(jitter * (rand() * 2 - 1));
    var r = Math.max(0, Math.min(255, rgb[0] + j));
    var g = Math.max(0, Math.min(255, rgb[1] + j));
    var b = Math.max(0, Math.min(255, rgb[2] + j));
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  function buildGroundCanvas(regionId) {
    if (GROUND_CANVAS_CACHE[regionId]) return GROUND_CANVAS_CACHE[regionId];
    var gtc = CFG.world.groundTexture ||
      { size: 256, repeat: 12, blotchCount: 140, mossDensity: 0.06, puddleDensity: 0.03 };
    var size = gtc.size;
    var canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    var ctx = canvas.getContext('2d');

    // Darkwood canon palette. Dominant tone per region (A olive, B charcoal);
    // the other region's tone is the secondary for tonal cross-blend.
    var isA = regionId === CFG.regionA.id;
    var dominant = whHexToRgb(isA ? CFG.world.groundColorA : CFG.world.groundColorB);
    var secondary = whHexToRgb(isA ? CFG.world.groundColorB : CFG.world.groundColorA);
    var umber = whHexToRgb(0x4a3f2a);
    var moss = whHexToRgb(0x56583a);
    var puddle = whHexToRgb(0x15171a);
    var rand = whRng(isA ? 1013904223 : 2040042217);

    // Base: dominant tone.
    ctx.fillStyle = whCss(dominant, 0, rand);
    ctx.fillRect(0, 0, size, size);

    // Noise blotch clusters: secondary mud and burnt umber blobs in pixel-art
    // sized cells (1 to 2 px) so NearestFilter keeps hard edges.
    var blotchCount = gtc.blotchCount;
    for (var i = 0; i < blotchCount; i++) {
      var cx = Math.floor(rand() * size);
      var cy = Math.floor(rand() * size);
      var cells = 4 + Math.floor(rand() * 12);
      var tone = rand() < 0.6 ? secondary : umber;
      var jitter = 6 + rand() * 10;
      for (var c = 0; c < cells; c++) {
        var px = (cx + Math.floor(rand() * 7) - 3 + size) % size;
        var py = (cy + Math.floor(rand() * 7) - 3 + size) % size;
        var w = rand() < 0.5 ? 1 : 2;
        ctx.fillStyle = whCss(tone, jitter, rand);
        ctx.fillRect(px, py, w, w);
      }
    }

    // Fine grain: scattered single pixels of both tones so no area reads as
    // one flat color.
    var grainCount = Math.floor(size * size * 0.10);
    for (var g = 0; g < grainCount; g++) {
      ctx.fillStyle = whCss(rand() < 0.5 ? dominant : secondary, 14, rand);
      ctx.fillRect(Math.floor(rand() * size), Math.floor(rand() * size), 1, 1);
    }

    // Moss accents: pale sickly yellow-green specks, low density.
    var mossCount = Math.floor(size * size * gtc.mossDensity);
    for (var m = 0; m < mossCount; m++) {
      var mw = rand() < 0.3 ? 2 : 1;
      ctx.fillStyle = whCss(moss, 10, rand);
      ctx.fillRect(Math.floor(rand() * size), Math.floor(rand() * size), mw, mw);
    }

    // Wet puddle specks: near-black, slightly clustered.
    var puddleCount = Math.floor(size * size * gtc.puddleDensity);
    for (var p = 0; p < puddleCount; p++) {
      var sx = Math.floor(rand() * size);
      var sy = Math.floor(rand() * size);
      var specks = 1 + Math.floor(rand() * 3);
      for (var s = 0; s < specks; s++) {
        var px2 = (sx + Math.floor(rand() * 4) - 2 + size) % size;
        var py2 = (sy + Math.floor(rand() * 4) - 2 + size) % size;
        ctx.fillStyle = whCss(puddle, 4, rand);
        ctx.fillRect(px2, py2, 1, 1);
      }
    }

    GROUND_CANVAS_CACHE[regionId] = canvas;
    return canvas;
  }

  function makeGroundTexture(regionId) {
    var gtc = CFG.world.groundTexture || { repeat: 12 };
    var tex = new THREE.CanvasTexture(buildGroundCanvas(regionId));
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestMipmapLinearFilter;
    tex.generateMipmaps = true;
    var caps = window.WH_GAME && window.WH_GAME.renderer &&
      window.WH_GAME.renderer.capabilities;
    tex.anisotropy = Math.min(4, caps ? caps.getMaxAnisotropy() : 4);
    tex.colorSpace = THREE.SRGBColorSpace;
    // R5: repeat scales with the visual disc so texel density stays repeat/90
    var rep = gtc.repeat * whVisualGroundRadius(regionId) / CFG.world.groundRadius;
    tex.repeat.set(rep, rep);
    return tex;
  }

  // ---- Live region manager (THREE scene wiring) ------------------------------

  function RegionManager(scene, enemyStateRestoreCb) {
    this.logic = new RegionManagerLogic(CFG.regionA.id);
    this.scene = scene;
    this.groups = {};                 // regionId -> THREE.Group (visible or pre-warm)
    this.enemies = {};                // regionId -> [WH_Enemy]
    this.restoreEnemyState = enemyStateRestoreCb || function () {};
    this.buildCounter = 0;            // mock-observable build counter
  }

  RegionManager.prototype.activeRegionIds = function () {
    return this.logic.activeRegionIds();
  };

  RegionManager.prototype.clampEnemyToHomeSide = function (enemy, boundary) {
    return this.logic.clampEnemyToHomeSide(enemy, boundary);
  };

  // R5 P0-5: collider table per region (cached once every footprint is known).
  RegionManager.prototype.propColliders = function (regionId) {
    this.colliders = this.colliders || {};
    if (this.colliders[regionId]) return this.colliders[regionId];
    var table = whPropColliders(regionId, function (name) {
      return window.WH_ASSETS.getMeta(name);
    });
    if (table.complete) this.colliders[regionId] = table;
    return table;
  };

  // R5 P0-5: push a circle (player) out of the ACTIVE region's prop colliders.
  // The first call (boot frame 1) also writes the spawn validator report.
  RegionManager.prototype.pushOutOfProps = function (pos, radius) {
    if (!this.spawnReport) this.spawnReport = this.validateSpawns();
    return this.logic.pushOutCircles(pos, radius,
      this.propColliders(this.logic.activeId).circles);
  };

  // R5 P0-5 spawn validator over BOTH regions straight from CONFIG: (i) home
  // side (props past the plane, enemies past the hold line), (ii) inside the
  // playable radius, (iii) region spawn outside every collider. Logs one
  // console line; never throws.
  RegionManager.prototype.validateSpawns = function () {
    var report = { props: 0, enemies: 0, violations: [], exempt: [] };
    try {
      var self = this;
      var rPlay = whPlayRadius();
      var plane = CFG.boundary.z;
      var hold = CFG.enemy.holdAtBoundaryMargin;
      [CFG.regionA.id, CFG.regionB.id].forEach(function (rid) {
        var reg = DEFS.regions[rid];
        var isA = reg.side === 1;
        var bad = function (kind, index, name, x, z, why) {
          report.violations.push({ kind: kind, region: rid, index: index,
            name: name, x: x, z: z, why: why });
        };
        reg.cfg.props.forEach(function (p, i) {
          report.props++;
          if (isA ? !(p.z > plane) : !(p.z < plane)) bad('prop', i, p.asset, p.x, p.z, 'side');
          if (Math.sqrt(p.x * p.x + p.z * p.z) > rPlay) bad('prop', i, p.asset, p.x, p.z, 'radius');
        });
        reg.cfg.enemies.forEach(function (e, i) {
          report.enemies++;
          if (isA ? !(e.z >= plane + hold) : !(e.z <= plane - hold)) bad('enemy', i, e.type, e.x, e.z, 'side');
          if (Math.sqrt(e.x * e.x + e.z * e.z) > rPlay) bad('enemy', i, e.type, e.x, e.z, 'radius');
        });
        var table = self.propColliders(rid);
        table.exempt.forEach(function (c) {
          report.exempt.push({ kind: 'collider-corridor', region: rid, index: c.index,
            name: c.name, x: c.x, z: c.z, r: c.r });
        });
        table.circles.forEach(function (c) {
          var dx = reg.spawn.x - c.x, dz = reg.spawn.z - c.z;
          var d = Math.sqrt(dx * dx + dz * dz);
          if (d < c.r + CFG.player.radius) {
            bad('spawn', c.index, c.name, reg.spawn.x, reg.spawn.z,
              'spawn inside collider r=' + c.r.toFixed(3) + ' d=' + d.toFixed(3));
          }
        });
      });
    } catch (err) {
      report.error = String(err);
    }
    console.log('[WH spawn-validator] props=' + report.props + ' enemies=' +
      report.enemies + ' violations=' + report.violations.length + ' exempt=' +
      report.exempt.length + (report.error ? ' error=' + report.error : '') +
      ' ' + JSON.stringify(report.violations));
    return report;
  };

  // Build a region group from CONFIG data (props + ground + enemies). Pre-warm
  // builds set visible=false.
  RegionManager.prototype.buildRegion = function (regionId, hidden) {
    if (this.groups[regionId]) {
      // already built (pre-warm): just reveal or keep hidden
      if (!hidden) this.groups[regionId].visible = true;
      return this.groups[regionId];
    }
    var region = DEFS.regions[regionId];
    var group = new THREE.Group();
    group.name = 'region-' + regionId;
    this.buildCounter++;

    // ground disc: procedural pixel-art canvas texture (boot-time, cached),
    // region-biased blotch mix (A olive-dominant, B charcoal-dominant)
    var groundMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      map: makeGroundTexture(regionId),
      roughness: 1.0, metalness: 0.0, side: THREE.DoubleSide
    });
    var ground = new THREE.Mesh(
      new THREE.CircleGeometry(whVisualGroundRadius(regionId), 48),
      groundMat
    );
    ground.rotation.x = -Math.PI / 2;
    ground.name = 'ground';
    group.add(ground);

    // Cheap mist layer (CONFIG.mistPlane): one large flat semi-transparent
    // plane at low height. Visual only, no collider. Region-gated by id.
    var mistCfg = CFG.mistPlane;
    if (mistCfg && mistCfg.enabled && regionId === mistCfg.regionId) {
      var mistMat = new THREE.MeshBasicMaterial({
        color: mistCfg.colorHex,
        transparent: true,
        opacity: mistCfg.opacityX100 / 100,
        side: THREE.DoubleSide,
        depthWrite: false
      });
      var mist = new THREE.Mesh(
        new THREE.PlaneGeometry(whVisualGroundRadius(regionId) * 2,
          whVisualGroundRadius(regionId) * 2),
        mistMat
      );
      mist.rotation.x = -Math.PI / 2;
      mist.position.y = mistCfg.y;
      mist.name = 'mist-plane';
      group.add(mist);
    }

    // props from manifest
    var regionCfg = region.cfg;
    for (var i = 0; i < regionCfg.props.length; i++) {
      var p = regionCfg.props[i];
      var obj = window.WH_ASSETS.instance(p.asset);
      obj.position.set(p.x, p.y || 0, p.z);
      obj.rotation.y = p.rotY;
      obj.scale.setScalar(p.scale);
      group.add(obj);
    }

    // enemies (fresh instances; dead state restored below)
    this.enemies[regionId] = [];
    for (var j = 0; j < regionCfg.enemies.length; j++) {
      var e = regionCfg.enemies[j];
      var enemy = new window.WH_Enemy(e.type, this.scene, regionId, e.x, e.z);
      var bodyName = e.type === 'bandit' ? 'banditBody' : 'ghoulBody';
      var eBody = window.WH_ASSETS.instance(bodyName);
      var eScale = CFG.world.characterHeight /
        (window.WH_ASSETS.groundHeight(bodyName) || CFG.world.characterHeight);
      eBody.scale.setScalar(eScale);
      eBody.position.y = -(window.WH_ASSETS.groundMinY(bodyName) * eScale);
      // Enemy bob writes the holder position; keep the lift on one level.
      eBody.children[0].position.y += window.WH_ASSETS.groundMinY(bodyName);
      enemy.setBody(eBody);
      this.enemies[regionId].push(enemy);
      group.add(enemy.root);
    }

    // per-region persistence: dead stay dead
    var st = this.logic.stateFor(regionId);
    for (var k = 0; k < this.enemies[regionId].length; k++) {
      if (st.enemies[k] === 'dead') {
        this.enemies[regionId][k].hp = 0;
        this.enemies[regionId][k].setFsm('dead');
        this.enemies[regionId][k].deadFall = 1;
      }
    }

    group.visible = !hidden;
    this.scene.add(group);
    this.groups[regionId] = group;
    return group;
  };

  // Unload + dispose a region's scene contents.
  RegionManager.prototype.disposeRegion = function (regionId) {
    var group = this.groups[regionId];
    if (!group) return;
    this.scene.remove(group);
    group.traverse(function (obj) {
      if (obj.isMesh) {
        if (obj.geometry) obj.geometry.dispose();
        var mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        mats.forEach(function (m) {
          if (!m) return;
          if (m.map) m.map.dispose();
          if (m.roughnessMap) m.roughnessMap.dispose();
          if (m.normalMap) m.normalMap.dispose();
          m.dispose();
        });
      }
    });
    delete this.groups[regionId];
    delete this.enemies[regionId];
  };

  // Main per-frame entry. Applies transition logic to live scene. Returns the
  // transition result for the caller (HUD updates etc).
  RegionManager.prototype.tickTransition = function (x, z) {
    var result = this.logic.tickTransition(x, z);
    if (result.action === 'prewarm') {
      this.buildRegion(result.newActiveId || this.logic.prewarmedId, true);
    } else if (result.action === 'dispose') {
      var pid = this.logic.prewarmedId;
      // logic already cleared prewarmedId; find what it was via groups
      var neighbor = DEFS.neighborOf(this.logic.activeId);
      if (neighbor && this.groups[neighbor] && !this.groups[neighbor].visible) {
        this.disposeRegion(neighbor);
      }
    } else if (result.action === 'cross') {
      var oldId = DEFS.neighborOf(result.newActiveId);
      // reveal the pre-warmed neighbor (instant swap: already built)
      var newGroup = this.groups[result.newActiveId];
      if (newGroup) {
        newGroup.visible = true;
      } else {
        this.buildRegion(result.newActiveId, false);
      }
      // unload old region
      if (this.groups[oldId]) this.disposeRegion(oldId);
      this.enemies[result.newActiveId] = this.enemies[result.newActiveId] || [];
    }
    return result;
  };

  RegionManager.prototype.updateEnemies = function (dt, playerPos, playerAlive, canDamagePlayer, activeId) {
    var list = this.enemies[activeId] || [];
    var boundary = { z: CFG.boundary.z };
    var self = this;
    for (var i = 0; i < list.length; i++) {
      var e = list[i];
      e.update(dt, playerPos, playerAlive, canDamagePlayer, boundary, this);
    }
    // circle push-out among enemies + player
    var circles = [{ pos: playerPos, radius: CFG.player.radius }];
    for (var j = 0; j < list.length; j++) {
      if (list[j].fsm !== 'dead') circles.push({ pos: list[j].pos, radius: list[j].cfg.radius });
    }
    for (var k = 0; k < list.length; k++) {
      if (list[k].fsm === 'dead') continue;
      var others = circles.slice();
      others.splice(k + 1, 1);
      list[k].separateFrom(others, CFG.enemy.separationPush, dt);
    }
    // record dead state for persistence
    var st = this.logic.stateFor(activeId);
    for (var m = 0; m < list.length; m++) {
      if (list[m].fsm === 'dead') st.enemies[m] = 'dead';
    }
  };

  RegionManager.prototype.getEnemies = function (activeId) {
    return this.enemies[activeId] || [];
  };

  // Debug summary for window.WH_DEBUG.
  RegionManager.prototype.debugSummary = function () {
    var self = this;
    var states = {};
    Object.keys(this.logic.regionStates).forEach(function (rid) {
      var dead = 0, total = 0;
      var list = self.enemies[rid] || [];
      total = Math.max(list.length, Object.keys(self.logic.regionStates[rid].enemies).length);
      list.forEach(function (e) { if (e.fsm === 'dead') dead++; });
      Object.keys(self.logic.regionStates[rid].enemies).forEach(function (k) {
        if (self.logic.regionStates[rid].enemies[k] === 'dead') dead = Math.max(dead, Number(k) + 1 > dead ? dead + 1 : dead);
      });
      states[rid] = { deadEnemies: dead, knownEnemies: total, crossed: self.logic.regionStates[rid].crossed };
    });
    return states;
  };

  window.WH_RegionManager = RegionManager;
  window.WH_RegionManagerLogic = RegionManagerLogic;
})();