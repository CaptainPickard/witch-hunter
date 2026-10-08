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
  // CC-C2: walks EVERY connection of the active region (B has two: the A/B
  // chokepoint plane and the B/C door). A region with one connection (A,
  // C) runs exactly the single-connection logic of before.
  RegionManagerLogic.prototype.tickTransition = function (x, z) {
    var result = { action: null, newActiveId: null, mappedPos: null };
    var conns = DEFS.connectionsOf(this.activeId);
    if (!conns.length) return result;

    // crossing: player crossed the plane inside the chokepoint corridor (or
    // a door's window; a locked door never crosses - game.js gate predicate).
    // Direction-agnostic: fires when the player's plane side differs from the
    // ACTIVE region's home side (walking into the neighbor's half), so both
    // A->B and B->A crossings trigger. (The old code compared against the
    // fixed conn.fromSide, which made B->A returns impossible.)
    for (var i = 0; i < conns.length; i++) {
      var conn = conns[i];
      var neighborId = DEFS.otherEnd(conn, this.activeId);
      var open = conn.door ?
        DEFS.insideDoorWindow(conn, x) && !this.doorLocked(conn, neighborId) :
        DEFS.insideChokepoint(conn, x);
      var sideNow = DEFS.sideOfPlane(conn, z);
      var activeSide = DEFS.sideIn(conn, this.activeId);
      if (open && sideNow !== activeSide) {
        // map position across, preserving approach direction: place the player
        // just past the plane ON THE NEIGHBOR'S HOME SIDE (not merely the
        // opposite of their current side, which can re-trigger a cross back).
        var mapped = DEFS.mapPositionAcross(conn, x, z, 2,
          DEFS.sideIn(conn, neighborId));
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
    }

    // pre-warm: close to the NEAREST connection's plane, approach direction
    // faces that neighbor. One pre-warm slot: a held pre-warm is only
    // replaced after the hysteresis below disposes it (no rebuild thrash
    // between B's two planes; with one connection this is the old
    // prewarmedId !== neighborId test).
    var near = conns[0];
    for (var j = 1; j < conns.length; j++) {
      if (DEFS.distanceToBoundary(conns[j], z) < DEFS.distanceToBoundary(near, z)) near = conns[j];
    }
    var dist = DEFS.distanceToBoundary(near, z);
    var nearId = DEFS.otherEnd(near, this.activeId);
    if (dist <= this.preWarmDistance && this.prewarmedId === null) {
      this.prewarmedId = nearId;
      this.buildCounts[nearId] = (this.buildCounts[nearId] || 0) + 1;
      result.action = 'prewarm';
      return result;
    }

    // hysteresis: player turned back beyond pre-warm band of the pre-warmed
    // neighbor's own plane -> dispose pre-warm
    if (this.prewarmedId !== null) {
      var pc = DEFS.connectionBetween(this.activeId, this.prewarmedId);
      if (!pc || DEFS.distanceToBoundary(pc, z) > this.preWarmDistance + this.hysteresisDistance) {
        this.prewarmedId = null;
        result.action = 'dispose';
        return result;
      }
    }

    return result;
  };

  // CC-C2 tutorial-law gate: crossings INTO conn.door.gatedTo are locked
  // while the predicate game.js installs (doorGate = !dayNight.dormant
  // inverted: true = locked) says so. No predicate = open.
  RegionManagerLogic.prototype.doorGate = null;
  RegionManagerLogic.prototype.doorLocked = function (conn, toId) {
    return !!(conn.door && conn.door.gatedTo === toId && this.doorGate && this.doorGate(conn));
  };

  // CC-C2 radial suspension: inside an OPEN door window within suspendDepthM
  // of the plane the active region's rim clamp does not apply, so a player
  // whose disc ends short of the line (C: rim z = -87.5, line -86) can reach
  // and cross it. The far half of the band only while the door is open
  // (that frame crosses); a locked door keeps the rim on the far half, so
  // a player in B's north strip never gains ground past B's rim.
  RegionManagerLogic.prototype.inOpenDoorBand = function (pos) {
    var conns = DEFS.connectionsOf(this.activeId);
    for (var i = 0; i < conns.length; i++) {
      var conn = conns[i];
      if (!conn.door || !DEFS.insideDoorWindow(conn, pos.x)) continue;
      var d = DEFS.sideIn(conn, this.activeId) * (pos.z - conn.planeCoord);
      if (d > conn.door.suspendDepthM || -d > conn.door.suspendDepthM) continue;
      if (d >= 0 || !this.doorLocked(conn, DEFS.otherEnd(conn, this.activeId))) return true;
    }
    return false;
  };

  // CC-C2 gate AT the line: on the frame the player would cross a LOCKED
  // door plane out of the active region's home half inside the window, z
  // is held at the line (crossing-frame hold, not a positional yank).
  // prevZ = this frame's pre-move z (game.js). A player already past the
  // line (stepped sideways into the window from B's north strip) is never
  // held; moving back toward home is always free.
  RegionManagerLogic.prototype.holdAtLockedDoor = function (prevZ, pos) {
    var conns = DEFS.connectionsOf(this.activeId);
    var held = false;
    for (var i = 0; i < conns.length; i++) {
      var conn = conns[i];
      if (!conn.door || !DEFS.insideDoorWindow(conn, pos.x)) continue;
      if (!this.doorLocked(conn, DEFS.otherEnd(conn, this.activeId))) continue;
      var s = DEFS.sideIn(conn, this.activeId);
      if (s * (prevZ - conn.planeCoord) >= 0 && s * (pos.z - conn.planeCoord) < 0) {
        pos.z = conn.planeCoord;
        held = true;
      }
    }
    return held;
  };

  // CC-C2: is the player near a door's arch while it is locked toward the
  // other side? (game.js reason toast + interact prompt)
  RegionManagerLogic.prototype.lockedDoorNear = function (pos, radius) {
    var conns = DEFS.connectionsOf(this.activeId);
    for (var i = 0; i < conns.length; i++) {
      var conn = conns[i];
      if (!conn.door || !this.doorLocked(conn, DEFS.otherEnd(conn, this.activeId))) continue;
      var dx = pos.x - conn.door.doorX, dz = pos.z - conn.planeCoord;
      if (dx * dx + dz * dz <= radius * radius) return conn;
    }
    return null;
  };

  // Boundary clamp for the player: blocked everywhere except inside the
  // chokepoint interval. Returns true if the position was clamped.
  // Clamp by the ACTIVE region's home side (logic.activeId), not by the
  // position's current side: a player who walks past the plane outside the
  // corridor is trespassing on the neighbor's side and must be pushed back
  // into their own region, regardless of which side they are now on.
  // CC-C2: plane 0 applies to its members only (C is not on it); door
  // connections have NO plane clamp (the plane is a cross-line in the
  // window, see holdAtLockedDoor).
  RegionManagerLogic.prototype.clampPlayerPlane = function (pos) {
    var conn = DEFS.connections[0];
    if (!conn) return false;
    if (!DEFS.isMember(conn, this.activeId)) return false;
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
  // CC-C2: per-connection. A/B homes run today's plane-0 rules unchanged;
  // a home off plane 0 (C) holds margin-deep on its side of EVERY
  // connection it is a member of, then inside its own disc. (C spawns no
  // enemies in CC-C2: the rows exist for the next order.)
  RegionManagerLogic.prototype.clampEnemyToHomeSide = function (enemy, boundary) {
    var conn = DEFS.connections[0];
    if (!conn) return false;
    var margin = CFG.enemy.holdAtBoundaryMargin;
    if (!DEFS.isMember(conn, enemy.homeRegionId)) {
      var held = false;
      var homeConns = DEFS.connectionsOf(enemy.homeRegionId);
      for (var c = 0; c < homeConns.length; c++) {
        var hs = DEFS.sideIn(homeConns[c], enemy.homeRegionId);
        var lim = homeConns[c].planeCoord + hs * margin;
        if (hs * (enemy.pos.z - lim) < 0) { enemy.pos.z = lim; held = true; }
      }
      var home = DEFS.regions[enemy.homeRegionId];
      if (home && home.center &&
          whClampRadialAt(enemy.pos, whPlayRadius(enemy.homeRegionId), home.center)) held = true;
      return held;
    }
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
  // CC-C2: per region (regionId optional): a region's own groundRadius
  // (C = 280) else the global CFG.world.groundRadius (A/B, and every
  // no-argument caller: today's value). playerMargin stays global.
  function whGroundRadius(regionId) {
    var reg = regionId ? DEFS.regions[regionId] : null;
    return (reg && reg.groundRadius) || CFG.world.groundRadius;
  }

  function whPlayRadius(regionId) {
    return whGroundRadius(regionId) - CFG.world.playerMargin;
  }

  // Visual ground radius per region. FogExp2 is 95% opaque at
  // d95 = sqrt(-ln(1 - fogOpaqueFrac)) / density; the disc reaches
  // visualGroundFogMult * d95 past the playable rim so its edge is never seen.
  function whVisualGroundRadius(regionId) {
    var W = CFG.world;
    var d95 = Math.sqrt(-Math.log(1 - W.fogOpaqueFrac)) /
      DEFS.regions[regionId].fogDensity;
    var r = Math.max(whGroundRadius(regionId),
      whPlayRadius(regionId) + W.visualGroundFogMult * d95);
    // CC-C3: a region may floor it (C: the edge past the 1/255 fog depth of
    // its thinnest phase fog from any reachable camera); A/B leave the row
    // unset = the formula alone
    var floor = DEFS.regions[regionId].cfg.visualGroundMinRadius;
    return floor ? Math.max(r, floor) : r;
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

  // CC-C2: rim clamp for a region with its own disc center (no plane limit:
  // C's sides are door cross-lines, not walls).
  function whClampRadialAt(pos, r, center) {
    pos.x -= center.x;
    pos.z -= center.z;
    var hit = whClampRadial(pos, r, 1, null);
    pos.x += center.x;
    pos.z += center.z;
    return hit;
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

  // Round E: plan (optional) = whScatterPlan output; its extra trees join the
  // table as ordinary trunk colliders (index 'scatter<i>').
  // Round F: wall (optional) = whWallPlan output; its circles on this
  // region's side of the plane (within WALL_SIDE_PAD_M; chord + arch always)
  // join the table. Never corridor-exempt: arch legs/plugs bound the doorway.
  var WALL_SIDE_PAD_M = 3;
  function whPropColliders(regionId, meta, plan, wall) {
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
    if (plan) {
      if (!plan.complete) out.complete = false;
      for (var j = 0; j < plan.trees.length; j++) {
        var t = plan.trees[j];
        if (t.r > 0) out.circles.push({ index: 'scatter' + j, name: t.asset,
          x: t.x, z: t.z, r: t.r });
      }
    }
    // CC-C2: the world wall bounds the shared A/B disc only (plane-0
    // members); C's own disc never takes its circles
    if (wall && DEFS.isMember(DEFS.connections[0], regionId)) {
      if (!wall.complete) out.complete = false;
      var side = DEFS.regions[regionId].side;
      for (var k = 0; k < wall.colliders.length; k++) {
        var w = wall.colliders[k];
        if (side * (w.z - CFG.boundary.z) > -WALL_SIDE_PAD_M) out.circles.push(w);
      }
    }
    return out;
  }

  RegionManagerLogic.prototype.playRadius = whPlayRadius;
  RegionManagerLogic.prototype.visualGroundRadius = whVisualGroundRadius;

  // Full player clamp = boundary plane + radial rim in ONE call (game.js
  // clampPlayerToBounds returns early on true, so the rim must not depend on
  // the plane clamp not firing). Returns true if either clamp fired.
  // CC-C2: inside an open door band the rim is suspended (inOpenDoorBand);
  // a region with its own disc (C) clamps to that disc; A/B unchanged.
  RegionManagerLogic.prototype.clampPlayer = function (pos) {
    var plane = this.clampPlayerPlane(pos);
    if (this.inOpenDoorBand(pos)) return plane;
    var reg = DEFS.regions[this.activeId];
    if (reg.center) {
      var rimC = whClampRadialAt(pos, whPlayRadius(this.activeId), reg.center);
      return plane || rimC;
    }
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
    // CC-C2: a region with its own ground palette (C deep forest) paints
    // the same recipe from its CONFIG tones + seed
    var rc = DEFS.regions[regionId].cfg;
    if (rc.groundColor !== undefined) {
      dominant = whHexToRgb(rc.groundColor);
      secondary = whHexToRgb(rc.groundColor2);
      rand = whRng(rc.groundSeed);
    }

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
    // (CC-C2: per-region visual radius, global 90 reference: C's r ~336
    // disc gets ~45 repeats = the same ~15 m per tile as A/B)
    var rep = gtc.repeat * whVisualGroundRadius(regionId) / CFG.world.groundRadius;
    tex.repeat.set(rep, rep);
    return tex;
  }

  // ---- 10-03 change order 2: dirt path ribbon (Nicko: clearing walk to the
  // cemetery). Visual-only decal strip through region A's south clearing;
  // trees/lanterns are placed by CONFIG generation relative to the same sway
  // centerline x = swayAmp*sin(2pi(z-zFrom)/swayPeriod). No collider.
  // CC-C4a: seed (optional) = a CFG.roads row's textureSeed; A's ribbon
  // calls with none = today's canvas.
  function buildDirtPathCanvas(seed) {
    var size = 128;
    var canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    var ctx = canvas.getContext('2d');
    var rand = whRng(seed || 78002024);
    var dirt = whHexToRgb(0x5a4a33);      // packed-dirt umber (darkwood canon)
    var dirtDark = whHexToRgb(0x463a27);  // wet-mud tone
    var pebble = whHexToRgb(0x6e5f45);
    ctx.fillStyle = whCss(dirt, 0, rand);
    ctx.fillRect(0, 0, size, size);
    // mud blotch clusters, pixel-art cells (same recipe as the ground canvas)
    for (var i = 0; i < 60; i++) {
      var cx = Math.floor(rand() * size);
      var cy = Math.floor(rand() * size);
      var cells = 4 + Math.floor(rand() * 10);
      var tone = rand() < 0.55 ? dirtDark : dirt;
      var jitter = 6 + rand() * 8;
      for (var c = 0; c < cells; c++) {
        var px = (cx + Math.floor(rand() * 7) - 3 + size) % size;
        var py = (cy + Math.floor(rand() * 7) - 3 + size) % size;
        var w = rand() < 0.5 ? 1 : 2;
        ctx.fillStyle = whCss(tone, jitter, rand);
        ctx.fillRect(px, py, w, w);
      }
    }
    // scattered pebbles + dark grain
    for (var g = 0; g < 260; g++) {
      ctx.fillStyle = whCss(rand() < 0.35 ? pebble : dirtDark, 8, rand);
      var gw = rand() < 0.85 ? 1 : 2;
      ctx.fillRect(Math.floor(rand() * size), Math.floor(rand() * size), gw, gw);
    }
    // soft darker edges (u extremes) so the strip blends into the mud ground
    var edgeW = 9;
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = whCss(dirtDark, 0, rand);
    ctx.fillRect(0, 0, edgeW, size);
    ctx.fillRect(size - edgeW, 0, edgeW, size);
    ctx.globalAlpha = 1;
    return canvas;
  }

  // Path centerline x at z (shared by the ribbon and the Round E scatter).
  function whPathCenterX(DP, z) {
    return DP.swayAmp * Math.sin(2 * Math.PI * (z - DP.zFrom) / DP.swayPeriod);
  }

  // Horizontal distance from (x, z) to the centerline polyline (1 m steps).
  function whDistToPath(DP, x, z) {
    var span = DP.zFrom - DP.zTo;
    var n = Math.ceil(span);
    var best = Infinity;
    var ax = whPathCenterX(DP, DP.zFrom), az = DP.zFrom;
    for (var i = 1; i <= n; i++) {
      var bz = DP.zFrom - Math.min(span, i);
      var bx = whPathCenterX(DP, bz);
      var ex = bx - ax, ez = bz - az;
      var len2 = ex * ex + ez * ez;
      var t = len2 > 0 ? ((x - ax) * ex + (z - az) * ez) / len2 : 0;
      t = Math.max(0, Math.min(1, t));
      var dx = x - (ax + ex * t), dz = z - (az + ez * t);
      var d = Math.sqrt(dx * dx + dz * dz);
      if (d < best) best = d;
      ax = bx; az = bz;
    }
    return best;
  }

  function buildDirtPath(regionId) {
    var DP = CFG.world.dirtPath;
    if (!DP || DP.regionId !== regionId) return null;
    // strip geometry in world space: per-segment quads along the sway curve,
    // v UV accumulates by arc length so the texture flows along the path.
    var segLen = 6;
    var zFrom = DP.zFrom, zTo = DP.zTo, hw = DP.halfWidth;
    var span = zFrom - zTo;
    var segCount = Math.ceil(span / segLen);
    var positions = [];
    var uvs = [];
    var indices = [];
    var arc = 0;
    var pxPrev = null, pzPrev = null;
    for (var s = 0; s <= segCount; s++) {
      var zz = zFrom - Math.min(span, s * segLen);
      var cx = whPathCenterX(DP, zz);
      var nx = 0, nz = 1;
      if (pxPrev !== null) {
        var dx = cx - pxPrev, dz = zz - pzPrev;
        var len = Math.sqrt(dx * dx + dz * dz) || 1;
        nx = dz / len; nz = -dx / len;    // left normal in XZ
        arc += len;
      }
      pxPrev = cx; pzPrev = zz;
      // v0 = c - n*hw, v1 = c + n*hw; uv u spans repeatAcrossWidth tiles
      positions.push(cx - nx * hw, DP.y, zz - nz * hw,
                     cx + nx * hw, DP.y, zz + nz * hw);
      uvs.push(0, arc / DP.tileLengthMeters,
               DP.repeatAcrossWidth, arc / DP.tileLengthMeters);
      if (s > 0) {
        var b = s * 2;
        // winding: CCW seen from +y so face normals point UP
        indices.push(b - 2, b, b - 1,  b - 1, b, b + 1);
      }
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position',
      new THREE.BufferAttribute(new Float32Array(positions), 3));
    geo.setAttribute('uv',
      new THREE.BufferAttribute(new Float32Array(uvs), 2));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    var tex = new THREE.CanvasTexture(buildDirtPathCanvas());
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestMipmapLinearFilter;
    tex.generateMipmaps = true;
    tex.colorSpace = THREE.SRGBColorSpace;
    var caps = window.WH_GAME && window.WH_GAME.renderer &&
      window.WH_GAME.renderer.capabilities;
    tex.anisotropy = Math.min(4, caps ? caps.getMaxAnisotropy() : 4);
    var mat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      map: tex,
      roughness: 1.0, metalness: 0.0, side: THREE.DoubleSide,
      // decal recipe: same y as the ground would z-fight; offset + 0.02 lift
      polygonOffset: true,
      polygonOffsetFactor: -1,
      polygonOffsetUnits: -1
    });
    var mesh = new THREE.Mesh(geo, mat);
    mesh.name = 'dirt-path';
    return mesh;
  }

  // ---- CC-C4a: the King's Roads (CONFIG.roads polyline rows) ----------------
  // A road row is A's dirtPath recipe (halfWidth, tileLengthMeters,
  // repeatAcrossWidth, the dirt canvas) on a WAYPOINT centerline instead of
  // the z-swayed line: points = [[x, z], ...] through a Catmull-Rom curve
  // (or ring = {x, z, r}: a closed circle), resampled every ROAD_STEP_M of
  // arc, then pushed sideways by swayAmp * sin(2pi s / swayPeriod), ramped
  // to 0 over swayRampM at both ends so junctions + notch mouths stay put.
  // A's CFG.world.dirtPath row is NOT migrated: whRoadsFor lists it first
  // for its region and every caller reads it through whDistToPath exactly as
  // before (A byte-identical); rows here carry points/ring and take the
  // polyline path. Lines are pure (no THREE), cached per row id.
  var ROAD_STEP_M = 2;
  var ROAD_LINES = {};
  function whRoadLine(R) {
    if (ROAD_LINES[R.id]) return ROAD_LINES[R.id];
    var raw = [], i, k;
    if (R.ring) {
      var nr = Math.ceil(2 * Math.PI * R.ring.r / ROAD_STEP_M);
      for (i = 0; i <= nr; i++) {
        var th = 2 * Math.PI * i / nr;
        raw.push(R.ring.x + R.ring.r * Math.cos(th), R.ring.z + R.ring.r * Math.sin(th));
      }
    } else {
      var P = R.points;
      for (i = 0; i < P.length - 1; i++) {
        var p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
        var segN = Math.max(1, Math.ceil(Math.sqrt((p2[0] - p1[0]) * (p2[0] - p1[0]) +
          (p2[1] - p1[1]) * (p2[1] - p1[1])) / ROAD_STEP_M));
        for (k = 0; k < segN; k++) {
          var t = k / segN, t2 = t * t, t3 = t2 * t;
          raw.push(
            0.5 * (2 * p1[0] + (p2[0] - p0[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
              (3 * p1[0] - p0[0] - 3 * p2[0] + p3[0]) * t3),
            0.5 * (2 * p1[1] + (p2[1] - p0[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
              (3 * p1[1] - p0[1] - 3 * p2[1] + p3[1]) * t3));
        }
      }
      raw.push(P[P.length - 1][0], P[P.length - 1][1]);
    }
    var n = raw.length / 2, s = [0];
    for (i = 1; i < n; i++) {
      var ex = raw[2 * i] - raw[2 * i - 2], ez = raw[2 * i + 1] - raw[2 * i - 1];
      s.push(s[i - 1] + Math.sqrt(ex * ex + ez * ez));
    }
    var L = s[n - 1], amp = R.swayAmp || 0, ramp = R.swayRampM || 1;
    var pts = [], minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (i = 0; i < n; i++) {
      var a = Math.max(0, i - 1), b = Math.min(n - 1, i + 1);
      var tx = raw[2 * b] - raw[2 * a], tz = raw[2 * b + 1] - raw[2 * a + 1];
      var tl = Math.sqrt(tx * tx + tz * tz) || 1;
      var w = Math.min(1, s[i] / ramp, (L - s[i]) / ramp);
      w = w * w * (3 - 2 * w);
      var off = amp ? amp * w * Math.sin(2 * Math.PI * s[i] / R.swayPeriod) : 0;
      var x = raw[2 * i] + tz / tl * off, z = raw[2 * i + 1] - tx / tl * off;
      pts.push(x, z);
      minX = Math.min(minX, x); maxX = Math.max(maxX, x);
      minZ = Math.min(minZ, z); maxZ = Math.max(maxZ, z);
    }
    return (ROAD_LINES[R.id] = { pts: pts, n: n,
      minX: minX, maxX: maxX, minZ: minZ, maxZ: maxZ });
  }

  // Every road of a region: A's dirtPath row (if its region) + CFG.roads rows.
  function whRoadsFor(regionId) {
    var out = [], DP = CFG.world.dirtPath;
    if (DP && DP.regionId === regionId) out.push(DP);
    (CFG.roads || []).forEach(function (R) { if (R.regionId === regionId) out.push(R); });
    return out;
  }

  // Horizontal distance from (x, z) to a road's centerline. A's dirtPath row:
  // whDistToPath (unchanged). Polyline rows: exact within ROAD_FAR_M of the
  // line's bounding box, else the box distance (a lower bound - every caller
  // only asks "closer than a band <= ROAD_FAR_M?").
  var ROAD_FAR_M = 30;
  function whDistToRoad(R, x, z) {
    if (!R.points && !R.ring) return whDistToPath(R, x, z);
    var Ln = whRoadLine(R);
    var bx = Math.max(Ln.minX - x, 0, x - Ln.maxX), bz = Math.max(Ln.minZ - z, 0, z - Ln.maxZ);
    var bd = Math.sqrt(bx * bx + bz * bz);
    if (bd > ROAD_FAR_M) return bd;
    var p = Ln.pts, best = Infinity;
    for (var i = 0; i < Ln.n - 1; i++) {
      var ax = p[2 * i], az = p[2 * i + 1];
      var ex = p[2 * i + 2] - ax, ez = p[2 * i + 3] - az;
      var len2 = ex * ex + ez * ez;
      var t = len2 > 0 ? ((x - ax) * ex + (z - az) * ez) / len2 : 0;
      t = Math.max(0, Math.min(1, t));
      var dx = x - (ax + ex * t), dz = z - (az + ez * t);
      var d = dx * dx + dz * dz;
      if (d < best) best = d;
    }
    return Math.sqrt(best);
  }

  // Ribbon for one CFG.roads row: 3 vertices across (edge, center, edge) so a
  // cross-slope crease of the heightfield cannot swallow the middle; every
  // vertex seats on WH_GROUND.heightAt + R.lift in a heightfield region
  // (else R.lift over y 0). Same decal material recipe as A's ribbon.
  var ROAD_CANVAS = {};
  function buildRoad(regionId, R) {
    var Ln = whRoadLine(R), p = Ln.pts, hw = R.halfWidth;
    var G = window.WH_GROUND, terr = G && G.has(regionId);
    var positions = [], uvs = [], indices = [], arc = 0;
    for (var i = 0; i < Ln.n; i++) {
      var a = Math.max(0, i - 1), b = Math.min(Ln.n - 1, i + 1);
      var tx = p[2 * b] - p[2 * a], tz = p[2 * b + 1] - p[2 * a + 1];
      var tl = Math.sqrt(tx * tx + tz * tz) || 1;
      var nx = tz / tl, nz = -tx / tl;    // left normal in XZ (A's convention)
      if (i > 0) {
        var dx = p[2 * i] - p[2 * i - 2], dz = p[2 * i + 1] - p[2 * i - 1];
        arc += Math.sqrt(dx * dx + dz * dz);
      }
      for (var c = -1; c <= 1; c++) {
        var vx = p[2 * i] + nx * hw * c, vz = p[2 * i + 1] + nz * hw * c;
        positions.push(vx, (terr ? G.heightAt(regionId, vx, vz) : 0) + R.lift, vz);
        uvs.push((c + 1) / 2 * R.repeatAcrossWidth, arc / R.tileLengthMeters);
      }
      if (i > 0) {
        var q = i * 3;
        indices.push(q - 3, q, q - 2,  q - 2, q, q + 1,
                     q - 2, q + 1, q - 1,  q - 1, q + 1, q + 2);
      }
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(uvs), 2));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    var cv = ROAD_CANVAS[R.textureSeed] = ROAD_CANVAS[R.textureSeed] ||
      buildDirtPathCanvas(R.textureSeed);
    var tex = new THREE.CanvasTexture(cv);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestMipmapLinearFilter;
    tex.generateMipmaps = true;
    tex.colorSpace = THREE.SRGBColorSpace;
    var caps = window.WH_GAME && window.WH_GAME.renderer &&
      window.WH_GAME.renderer.capabilities;
    tex.anisotropy = Math.min(4, caps ? caps.getMaxAnisotropy() : 4);
    var mat = new THREE.MeshStandardMaterial({
      color: 0xffffff, map: tex,
      roughness: 1.0, metalness: 0.0, side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1
    });
    var mesh = new THREE.Mesh(geo, mat);
    mesh.name = 'road-' + R.id;
    return mesh;
  }

  // ---- Round E: seeded vegetation scatter (THREE-free, pure) -----------------
  // whScatterPlan(regionId, meta) is a pure function of CONFIG (scatter block,
  // region props/spawn/enemies/nodes, dirt path, boundary/chokepoint) and the
  // measured footprints meta(name) -> {width, height}. Each layer draws from
  // its own mulberry32 stream seeded by scatter.seed ^ hash(regionId:layer)
  // and consumes a FIXED number of draws per item, so the same inputs give
  // the same plan on every build and tuning one layer never moves another.

  function whHashStr(s) {
    var h = 2166136261;                // FNV-1a 32-bit
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function whPickWeighted(rand, rows) {
    var total = 0, i;
    for (i = 0; i < rows.length; i++) total += rows[i][1];
    var u = rand() * total;
    for (i = 0; i < rows.length; i++) {
      u -= rows[i][1];
      if (u < 0) return rows[i];
    }
    return rows[rows.length - 1];
  }

  // CC-C4a: a region's scatter params = CFG.scatter with the region's
  // cfg.scatterOverrides laid over it (one level deep: an object key merges
  // key-by-key, anything else - arrays, numbers - replaces). No override
  // row (A/B) = CFG.scatter itself, the very same object.
  function whScatterCfg(cfg) {
    var SC = CFG.scatter, O = cfg.scatterOverrides;
    if (!O) return SC;
    var out = {};
    Object.keys(SC).forEach(function (k) { out[k] = SC[k]; });
    Object.keys(O).forEach(function (k) {
      var base = SC[k], ov = O[k];
      if (base && ov && typeof base === 'object' && typeof ov === 'object' &&
          !Array.isArray(base) && !Array.isArray(ov)) {
        var m = {};
        Object.keys(base).forEach(function (j) { m[j] = base[j]; });
        Object.keys(ov).forEach(function (j) { m[j] = ov[j]; });
        out[k] = m;
      } else {
        out[k] = ov;
      }
    });
    return out;
  }

  // meta(name) -> {width, height}; CC-C4a: meta.heightAt(x, z) (optional) =
  // the terrain seat, carried on every instance as y (the plan stays pure:
  // the caller hands the height function in; none = no y, A/B as before).
  function whScatterPlan(regionId, meta) {
    var plan = { trees: [], instances: {}, complete: true,
      stats: { trees: 0, treeMisses: 0, ringBushes: 0, ringSkipped: 0,
               freeBushes: 0, grass: 0 } };
    if (!CFG.scatter || !CFG.scatter.enabled) return plan;
    var reg = DEFS.regions[regionId];
    var cfg = reg.cfg;
    if (cfg.scatter === false) return plan;   // CC-C2 gate (a region may still opt out)
    var SC = whScatterCfg(cfg);
    var C = SC.clear;
    var side = reg.side;
    var plane = CFG.boundary.z;
    // CC-C4a: an own-disc region (C) samples + bounds on its disc; A/B: the
    // shared disc at the origin with the plane side test (unchanged calls)
    var ctr = reg.center;
    var rPlay = ctr ? whPlayRadius(regionId) : whPlayRadius();
    var roads = whRoadsFor(regionId);
    var gx = CFG.chokepoint.centerX;
    var TWO_PI = Math.PI * 2;
    var heightAt = meta.heightAt || null;

    function m(name) {
      var v = meta(name);
      if (!v) plan.complete = false;
      return v;
    }
    function lerp(range, u) { return range[0] + (range[1] - range[0]) * u; }
    function stream(layer) { return whRng((SC.seed ^ whHashStr(regionId + ':' + layer)) | 0); }

    // CONFIG props as circles: r = gameplay collider radius, trunk = trunk
    // radius (width*scale/2*TRUNK_RATIO) for ring hosts, else 0.
    var hosts = {};
    SC.bushes.ringHosts.forEach(function (n) { hosts[n] = 1; });
    var circles = [];
    var trees = [];
    cfg.props.forEach(function (p) {
      var pm = m(p.asset);
      var c = { x: p.x, z: p.z,
        r: pm ? colliderRadius(p.asset, pm.width, p.scale) : 0,
        trunk: (pm && hosts[p.asset]) ? pm.width * p.scale / 2 * TRUNK_RATIO : 0 };
      circles.push(c);
      if (c.trunk > 0) trees.push(c);
    });
    var points = (cfg.enemies || []).concat(cfg.nodes || []);
    var enemyCount = (cfg.enemies || []).length;

    function inRegion(x, z, pad) {
      if (ctr) {
        var cx = x - ctr.x, cz = z - ctr.z;
        return Math.sqrt(cx * cx + cz * cz) <= rPlay - pad;
      }
      if (Math.sqrt(x * x + z * z) > rPlay - pad) return false;
      return side === 1 ? z > plane + pad : z < plane - pad;
    }
    // road bands: pathM = a fixed band from every centerline (trees, free
    // bushes); null = each road's own ribbon half-width + grass.pathPadM
    // (grass, rings, colonies). A: its one dirtPath row, the same tests.
    function nearRoad(x, z, pathM) {
      for (var r = 0; r < roads.length; r++) {
        var lim = pathM === null ? roads[r].halfWidth + SC.grass.pathPadM : pathM;
        if (whDistToRoad(roads[r], x, z) < lim) return true;
      }
      return false;
    }
    // CC-C2: door mouths of this region's door connections stay clear like
    // the A/B gate point (gateM); A has none
    var doors = DEFS.connectionsOf(regionId).filter(function (c) { return !!c.door; });
    // spawn + gate (point and collider corridor) + door mouths + path band
    function clearOfWorld(x, z, pathM) {
      var dx = x - reg.spawn.x, dz = z - reg.spawn.z;
      if (dx * dx + dz * dz < C.spawnM * C.spawnM) return false;
      dx = x - gx; dz = z - plane;
      if (dx * dx + dz * dz < C.gateM * C.gateM) return false;
      for (var d = 0; d < doors.length; d++) {
        dx = x - doors[d].door.doorX; dz = z - doors[d].planeCoord;
        if (dx * dx + dz * dz < C.gateM * C.gateM) return false;
      }
      if (whMeetsCorridor(x, z, 0)) return false;
      if (nearRoad(x, z, pathM)) return false;
      return true;
    }
    var keepOut = (SC.keepOut || []).filter(function (k) { return k.regionId === regionId; });
    // enemy spawns, gather nodes and keep-out ellipses (trees + free bushes)
    function clearOfPoints(x, z) {
      for (var e = 0; e < keepOut.length; e++) {
        var kx = (x - keepOut[e].x) / keepOut[e].rx, kz = (z - keepOut[e].z) / keepOut[e].rz;
        if (kx * kx + kz * kz < 1) return false;
      }
      for (var i = 0; i < points.length; i++) {
        var lim = i < enemyCount ? C.enemyM : C.nodeM;
        var dx = x - points[i].x, dz = z - points[i].z;
        if (dx * dx + dz * dz < lim * lim) return false;
      }
      return true;
    }
    // inside any circle's r + pad (skip = the ring's own host)
    function hitsCircles(x, z, pad, skip) {
      for (var i = 0; i < circles.length; i++) {
        var c = circles[i];
        if (c === skip) continue;
        var lim = c.r + pad;
        var dx = x - c.x, dz = z - c.z;
        if (dx * dx + dz * dz < lim * lim) return true;
      }
      return false;
    }
    function sampleDisc(rand) {
      var rr = rPlay * Math.sqrt(rand());
      var th = TWO_PI * rand();
      if (ctr) return { x: ctr.x + rr * Math.cos(th), z: ctr.z + rr * Math.sin(th) };
      return { x: rr * Math.cos(th), z: rr * Math.sin(th) };
    }
    function addInstance(name, x, z, rotY, scale) {
      var it = { x: x, z: z, rotY: rotY, scale: scale };
      if (heightAt) it.y = heightAt(x, z);   // CC-C4a: exact terrain seat (C)
      (plan.instances[name] = plan.instances[name] || []).push(it);
    }

    // 1. extra trees: best-candidate - of N valid samples keep the one
    // farthest from every tree, the rim and the boundary plane.
    var T = SC.treesExtra;
    var rt = stream('trees');
    var target = T.targetCount[regionId] || 0;
    for (var t = 0; t < target; t++) {
      var best = null, bestGap = -1;
      for (var k = 0; k < T.candidates; k++) {
        var s = sampleDisc(rt);
        if (!inRegion(s.x, s.z, C.edgeM) || !clearOfWorld(s.x, s.z, C.pathM) ||
            !clearOfPoints(s.x, s.z) || hitsCircles(s.x, s.z, T.propClearM, null)) continue;
        var treeGap = Infinity;
        for (var q = 0; q < trees.length; q++) {
          var tdx = s.x - trees[q].x, tdz = s.z - trees[q].z;
          treeGap = Math.min(treeGap, Math.sqrt(tdx * tdx + tdz * tdz));
        }
        if (treeGap < T.minSpacingM) continue;
        // score counts the rim + plane as neighbours so the interior gaps win
        var gap = Math.min(treeGap, rPlay - Math.sqrt(s.x * s.x + s.z * s.z),
          Math.abs(s.z - plane));
        if (gap > bestGap) { best = s; bestGap = gap; }
      }
      var pick = whPickWeighted(rt, T.assets);
      var rotY = rt() * TWO_PI;
      var height = lerp([pick[2], pick[3]], rt());
      if (!best) { plan.stats.treeMisses++; continue; }
      var tm = m(pick[0]);
      var scale = tm && tm.height > 0 ? height / tm.height : 1;
      var row = { asset: pick[0], x: best.x, z: best.z, rotY: rotY, scale: scale,
        r: tm ? colliderRadius(pick[0], tm.width, scale) : 0 };
      plan.trees.push(row);
      var tc = { x: row.x, z: row.z, r: row.r,
        trunk: tm ? tm.width * scale / 2 * TRUNK_RATIO : 0 };
      circles.push(tc);
      trees.push(tc);
    }
    plan.stats.trees = plan.trees.length;

    var B = SC.bushes;
    var grassPathM = null;               // per-road ribbon band (nearRoad)
    function bushPick(rand, rows) {
      var bp = whPickWeighted(rand, rows);
      var h = lerp([bp[2], bp[3]], rand());
      var bm = m(bp[0]);
      var sc = bm && bm.height > 0 ? h / bm.height : 1;
      return { name: bp[0], scale: sc, own: bm ? bm.width * sc / 2 * B.selfRadiusFrac : 0,
               rotY: rand() * TWO_PI };
    }

    // 2. bush rings around EVERY tree (CONFIG ring hosts, then scatter trees)
    var R = B.atTreeRing;
    // CC-C4a: R.pathM (optional, C) = rings keep the trees' centerline band;
    // unset (A/B) = the ribbon band, as before
    var ringPathM = R.pathM !== undefined ? R.pathM : grassPathM;
    var rr2 = stream('rings');
    for (var h = 0; h < trees.length; h++) {
      var host = trees[h];
      var n = R.count[0] + Math.floor(rr2() * (R.count[1] - R.count[0] + 1));
      var a0 = rr2() * TWO_PI;
      for (var slot = 0; slot < n; slot++) {
        var ang = a0 + slot * TWO_PI / n + (rr2() - 0.5) * (TWO_PI / n) * 0.5;
        var rad = host.trunk * lerp(R.radiusFrac, rr2());
        var bp2 = bushPick(rr2, R.assets || B.assets);
        var bx = host.x + Math.cos(ang) * rad, bz = host.z + Math.sin(ang) * rad;
        if (!inRegion(bx, bz, 0) || !clearOfWorld(bx, bz, ringPathM) ||
            hitsCircles(bx, bz, bp2.own, host)) { plan.stats.ringSkipped++; continue; }
        addInstance(bp2.name, bx, bz, bp2.rotY, bp2.scale);
        plan.stats.ringBushes++;
      }
    }

    // 3. free bushes: uniform over the region, tree rejection rules
    var rf = stream('freeBushes');
    for (var fa = 0; fa < B.freeBushes * 30 && plan.stats.freeBushes < B.freeBushes; fa++) {
      var fs = sampleDisc(rf);
      var fp = bushPick(rf, B.assets);
      if (!inRegion(fs.x, fs.z, C.edgeM) || !clearOfWorld(fs.x, fs.z, C.pathM) ||
          !clearOfPoints(fs.x, fs.z) || hitsCircles(fs.x, fs.z, T.propClearM, null)) continue;
      addInstance(fp.name, fs.x, fs.z, fp.rotY, fp.scale);
      plan.stats.freeBushes++;
    }

    // 4. grass: uniform; skips only path, spawn, gate and collider circles
    var G = SC.grass;
    var gm = m(G.asset);
    var rg = stream('grass');
    for (var ga = 0; ga < G.count * 10 && plan.stats.grass < G.count; ga++) {
      var gs = sampleDisc(rg);
      var gh = lerp(G.height, rg());
      var grot = rg() * TWO_PI;
      var gsc = gm && gm.height > 0 ? gh / gm.height : 1;
      var gown = gm ? gm.width * gsc / 2 : 0;
      if (!inRegion(gs.x, gs.z, 0) || !clearOfWorld(gs.x, gs.z, grassPathM) ||
          hitsCircles(gs.x, gs.z, gown, null)) continue;
      addInstance(G.asset, gs.x, gs.z, grot, gsc);
      plan.stats.grass++;
    }

    // 5. CC-C4a ground colonies (SC.groundLayers, absent for A/B): per layer
    // `clusters` colonies of [min,max] items within spreadM of a seed point;
    // seeds obey the tree/free-bush rules (+ nearTreeFrac of them start at a
    // ring host's trunk band), items the grass rules. Fixed draws per item.
    (SC.groundLayers || []).forEach(function (L) {
      var lm = m(L.asset);
      var rl = stream('layer:' + L.id);
      var made = 0, items = 0;
      for (var la = 0; la < L.clusters * 30 && made < L.clusters; la++) {
        var ls = sampleDisc(rl);
        var nu = rl(), npick = rl(), nang = rl() * TWO_PI, nrad = rl();
        if (trees.length && nu < L.nearTreeFrac) {
          var th2 = trees[Math.floor(npick * trees.length)];
          var rad2 = th2.trunk * lerp(L.treeBandFrac, nrad);
          ls = { x: th2.x + Math.cos(nang) * rad2, z: th2.z + Math.sin(nang) * rad2 };
        }
        if (!inRegion(ls.x, ls.z, C.edgeM) || !clearOfWorld(ls.x, ls.z, C.pathM) ||
            !clearOfPoints(ls.x, ls.z)) continue;
        made++;
        var nItems = L.perCluster[0] + Math.floor(rl() * (L.perCluster[1] - L.perCluster[0] + 1));
        for (var li = 0; li < nItems; li++) {
          var lr = L.spreadM * Math.sqrt(rl()), lth = rl() * TWO_PI;
          var lh = lerp(L.height, rl());
          var lrot = rl() * TWO_PI;
          var lsc = lm && lm.height > 0 ? lh / lm.height : 1;
          var lx = ls.x + lr * Math.cos(lth), lz = ls.z + lr * Math.sin(lth);
          if (!inRegion(lx, lz, 0) || !clearOfWorld(lx, lz, grassPathM) ||
              hitsCircles(lx, lz, lm ? lm.width * lsc / 2 : 0, null)) continue;
          addInstance(L.asset, lx, lz, lrot, lsc);
          items++;
        }
      }
      plan.stats['layer:' + L.id] = made + '/' + items;
    });
    return plan;
  }

  // ---- Round F: boundary wall ring + gate arch (THREE-free, pure) -----------
  // whWallPlan(meta) is a pure function of CONFIG (boundaryWall, lightSockets,
  // both regions' props) and measured footprints. WORLD-level: one plan for
  // the shared disc, not per region. Streams: seed ^ hash('wall:ring'|
  // 'wall:chord'); fixed draws per segment (ring: jitter, rotJitter; chord:
  // facing, rotJitter) drawn BEFORE the exclusion test, so a nudge or drop
  // never shifts later segments.
  function whWallPlan(meta) {
    var W = CFG.boundaryWall;
    var plan = { segments: [], colliders: [], arch: null, lantern: null, sockets: [],
      doorArches: [],
      complete: true,
      stats: { ring: 0, chordE: 0, chordW: 0, nudged: 0, drops: 0, dropReasons: [],
               overDropLimit: false, colliders: 0, doorGap: 0 } };
    if (!W || !W.enabled) return plan;
    var TWO_PI = Math.PI * 2;
    var DEG = Math.PI / 180;
    function m(name) {
      var v = meta(name);
      if (!v) plan.complete = false;
      return v;
    }
    function stream(layer) { return whRng((W.seed ^ whHashStr('wall:' + layer)) | 0); }

    // exclusion targets: every CONFIG prop collider of BOTH regions
    var props = [];
    [CFG.regionA.id, CFG.regionB.id].forEach(function (rid) {
      DEFS.regions[rid].cfg.props.forEach(function (p, i) {
        var pm = m(p.asset);
        var r = pm ? colliderRadius(p.asset, pm.width, p.scale) : 0;
        if (r > 0) props.push({ id: rid + '#' + i + ':' + p.asset, x: p.x, z: p.z, r: r });
      });
    });
    var L = W.segmentLengthUnits;
    var CR = W.collider.r, CN = W.collider.perSegment;
    var EX = W.exclusion;
    // collider circle centers along a segment (axis = local X after rotY)
    function segCircles(x, z, rotY) {
      var ax = Math.cos(rotY), az = -Math.sin(rotY);
      var out = [];
      for (var k = 0; k < CN; k++) {
        var t = (k + 0.5) / CN - 0.5;          // -1/3, 0, +1/3 for CN = 3
        out.push({ x: x + ax * t * L, z: z + az * t * L });
      }
      return out;
    }
    function clash(cs) {
      for (var i = 0; i < cs.length; i++) {
        for (var j = 0; j < props.length; j++) {
          var p = props[j], lim = p.r + EX.clearM + CR;
          var dx = cs[i].x - p.x, dz = cs[i].z - p.z;
          if (dx * dx + dz * dz < lim * lim) return p.id;
        }
      }
      return null;
    }
    function scaleFor(asset) {
      var am = m(asset);
      var sx = am && am.width > 0 ? L / am.width : 1;
      return { sx: sx, sy: am && am.height > 0 ? W.heightM / am.height : sx,
               sz: sx * W.depthScale };
    }
    var scales = {};
    W.assets.forEach(function (a) { scales[a] = scaleFor(a); });
    function addSegment(kind, i, asset, x, z, rotY, cs) {
      var s = scales[asset];
      plan.segments.push({ kind: kind, i: i, asset: asset, x: x, z: z, rotY: rotY,
        sx: s.sx, sy: s.sy, sz: s.sz });
      for (var k = 0; k < cs.length; k++) {
        plan.colliders.push({ index: 'wall-' + kind + i + '.' + k, name: asset,
          x: cs[k].x, z: cs[k].z, r: CR });
      }
    }
    function drop(kind, i, why) {
      plan.stats.drops++;
      plan.stats.dropReasons.push(kind + i + ' vs ' + why);
      if (plan.stats.drops > EX.maxDrops) plan.stats.overDropLimit = true;
    }

    // 1. ring: N segments around the full circle, chord <= length - overlap
    // so neighbours butt; asset alternates; radial jitter is a circular
    // 1-2-1 smoothing of per-segment uniform draws (no hard steps).
    // CC-C2: door connections cut the ring - a segment whose x-extent meets
    // the door window (+ wallGapPadM) near the door plane is not built (no
    // mesh, no colliders); draws are taken first, so no other segment moves
    var doorConns = DEFS.connections.filter(function (c) { return !!c.door; });
    function inDoorGap(x, z) {
      for (var d = 0; d < doorConns.length; d++) {
        var dr = doorConns[d].door;
        if (Math.abs(x - dr.doorX) < dr.doorHalfWidth + dr.wallGapPadM + L / 2 &&
            Math.abs(z - doorConns[d].planeCoord) < L) return true;
      }
      return false;
    }
    var R = W.radius;
    var N = Math.ceil(TWO_PI * R / (L - W.overlapM));
    var rr = stream('ring');
    var raw = [], rotJ = [];
    for (var i = 0; i < N; i++) {
      raw.push(rr() * 2 - 1);
      rotJ.push((rr() * 2 - 1) * W.jitter.rotJitterDeg * DEG);
    }
    for (i = 0; i < N; i++) {
      var sm = (raw[(i + N - 1) % N] + 2 * raw[i] + raw[(i + 1) % N]) / 4;
      var r0 = Math.max(W.minRadius, R + W.jitter.radial * sm);
      var th = i * TWO_PI / N;
      // local X along the tangent (-sin th, cos th); local +Z (the GLB's
      // front face) then points at the disc center
      var rot = -th - Math.PI / 2 + rotJ[i];
      var asset = W.assets[i % W.assets.length];
      if (inDoorGap(r0 * Math.cos(th), r0 * Math.sin(th))) { plan.stats.doorGap++; continue; }
      var placed = false, why = null;
      for (var nd = 0; nd <= EX.nudgeMaxM + 1e-9; nd += EX.nudgeStepM) {
        var rx = (r0 - nd) * Math.cos(th), rz = (r0 - nd) * Math.sin(th);
        var cs = segCircles(rx, rz, rot);
        var hit = clash(cs);
        if (!hit) {
          addSegment('ring', i, asset, rx, rz, rot, cs);
          if (nd > 0) plan.stats.nudged++;
          placed = true;
          break;
        }
        if (why === null) why = hit;
      }
      if (placed) plan.stats.ring++;
      else drop('ring', i, why);
    }

    // 2. chord along the boundary plane, both sides of the corridor, from
    // chordFromX to the ring intercept; same alternation, random facing
    // (the ivy front shows to region A or B), no radial jitter (on-plane).
    var zc = W.chordZ;
    var xEnd = W.chordToRim ? Math.sqrt(Math.max(0, R * R - zc * zc)) : W.chordFromX + L;
    var span = xEnd - W.chordFromX;
    var nc = Math.max(1, Math.ceil(span / (L - W.overlapM)));
    var step = span / nc;
    var rc = stream('chord');
    [1, -1].forEach(function (sd) {
      for (var c = 0; c < nc; c++) {
        var face = rc() < 0.5 ? 0 : Math.PI;
        var rj = (rc() * 2 - 1) * W.jitter.rotJitterDeg * DEG;
        var cx = sd * (W.chordFromX + (c + 0.5) * step);
        var crot = face + rj;
        var ccs = segCircles(cx, zc, crot);
        var chit = clash(ccs);
        var kind = sd === 1 ? 'chordE' : 'chordW';
        if (chit) { drop(kind, c, chit); continue; }
        addSegment(kind, c, W.assets[c % W.assets.length], cx, zc, crot, ccs);
        plan.stats[kind]++;
      }
    });

    // 3. gate arch over the chokepoint: scale so the measured clear opening
    // is >= fitOpening. Pillar blocks (opening edge .. outer half-width,
    // full depth) are ringed by leg circles inset by legs.r, plus corner
    // plugs at the four doorway-mouth corners, just OUTSIDE the opening.
    // NOT whMeetsCorridor-exempt: they are the doorway.
    var A = W.arch;
    var gm = m(A.asset);
    if (gm && gm.width > 0) {
      var s = A.fitOpening / (A.openingFrac * gm.width);
      var sz = s * A.depthScale;
      var ca = Math.cos(A.rotY), sa = Math.sin(A.rotY);
      // arch-local (x, z) -> world, like obj.rotation.y
      var toWorld = function (lx, lz) {
        return { x: A.x + lx * ca + lz * sa, z: A.z - lx * sa + lz * ca };
      };
      var opening = A.openingFrac * gm.width * s;
      var xi = opening / 2;                       // pillar inner face
      var xo = gm.width * s / 2;                  // pillar outer face
      var hd = A.depthFrac * gm.width * sz / 2;   // half depth
      var apexY = A.apexFrac * gm.height * s;
      plan.arch = { asset: A.asset, x: A.x, z: A.z, rotY: A.rotY,
        offsetX: -A.openingCenterFrac * gm.width * s,   // centers the opening on (x, z)
        scale: s, scaleZ: sz, opening: opening, halfWidth: xo, halfDepth: hd,
        apexY: apexY, height: gm.height * s };
      var LG = A.legs;
      var legCount = 0, plugCount = 0;
      [1, -1].forEach(function (sd) {
        // perimeter of the inset rectangle [xi + r, xo - r] x [-hd + r, hd - r]
        var x0 = xi + LG.r, x1 = xo - LG.r, z0 = -hd + LG.r, z1 = hd - LG.r;
        var nx = Math.max(1, Math.ceil((x1 - x0) / LG.spacingM));
        var nz = Math.max(1, Math.ceil((z1 - z0) / LG.spacingM));
        var pts = [];
        for (var a = 0; a < nx; a++) pts.push([x0 + (x1 - x0) * a / nx, z1]);   // front face
        for (a = 0; a < nz; a++) pts.push([x1, z1 - (z1 - z0) * a / nz]);       // outer face
        for (a = 0; a < nx; a++) pts.push([x1 - (x1 - x0) * a / nx, z0]);       // back face
        for (a = 0; a < nz; a++) pts.push([x0, z0 + (z1 - z0) * a / nz]);       // inner face
        pts.forEach(function (pt) {
          var w = toWorld(sd * pt[0], pt[1]);
          plan.colliders.push({ index: 'arch-leg' + (sd === 1 ? 'E' : 'W') + legCount++,
            name: A.asset, x: w.x, z: w.z, r: LG.r });
        });
        if (A.plugCorners) {
          [hd, -hd].forEach(function (pz) {
            var w = toWorld(sd * (xi + A.plugR), pz);
            plan.colliders.push({ index: 'arch-plug' + plugCount++, name: A.asset,
              x: w.x, z: w.z, r: A.plugR });
          });
        }
      });
      plan.stats.archLegs = legCount;
      plan.stats.archPlugs = plugCount;

      // 4. lantern hung under the opening apex (arch child) + its socket
      var LT = W.lantern;
      var lm = m(LT.asset);
      if (lm && lm.height > 0) {
        var lh = LT.heightM * LT.scale;
        var ly = apexY - LT.topBelowApexM - lh;   // base y; hook top = apex - topBelowApexM
        plan.lantern = { asset: LT.asset, localY: ly, scale: lh / lm.height, height: lh };
        var SK = CFG.lightSockets[A.asset];
        if (SK) {
          var so = toWorld(SK.offset[0], SK.offset[1]);
          plan.sockets.push({ id: A.asset + '@lantern', x: so.x, y: ly + lh * SK.heightFraction,
            z: so.z, intensity: SK.intensity, weight: 1 });
        }
      }
    }
    // 5. CC-C2 door arches (region-defs conn.door.arch): the gate-arch fit
    // math on the door's own row; VISUAL ONLY (no leg colliders - the
    // door's gate logic is the door; region-manager holdAtLockedDoor)
    doorConns.forEach(function (c) {
      var DA = c.door.arch;
      var dm = DA ? m(DA.asset) : null;
      if (!dm || !(dm.width > 0)) return;
      var ds = DA.fitOpening / (DA.openingFrac * dm.width);
      plan.doorArches.push({ asset: DA.asset, x: DA.x, z: DA.z, rotY: DA.rotY,
        offsetX: -DA.openingCenterFrac * dm.width * ds,
        scale: ds, scaleZ: ds * DA.depthScale });
    });
    plan.stats.colliders = plan.colliders.length;
    return plan;
  }

  // One InstancedMesh per template mesh (the Round E GLBs are single-mesh:
  // one per asset per region). Shares the pixelated template's geometry and
  // material; matrices are written ONCE here, never per frame. Whole-mesh
  // frustum culling over the instance bounding sphere. Round F: items may
  // carry per-axis sx/sy/sz (+ y) instead of a uniform scale.
  function whBuildInstanced(name, list) {
    var tmpl = window.WH_ASSETS.getTemplate(name);
    var out = [];
    if (!tmpl || !list || !list.length) return out;
    tmpl.updateMatrixWorld(true);
    var inv = new THREE.Matrix4().copy(tmpl.matrixWorld).invert();
    var local = new THREE.Matrix4();
    var mat = new THREE.Matrix4();
    var pos = new THREE.Vector3();
    var quat = new THREE.Quaternion();
    var scl = new THREE.Vector3();
    var up = new THREE.Vector3(0, 1, 0);
    tmpl.traverse(function (o) {
      if (!o.isMesh) return;
      local.multiplyMatrices(inv, o.matrixWorld);
      var im = new THREE.InstancedMesh(o.geometry, o.material, list.length);
      for (var i = 0; i < list.length; i++) {
        var it = list[i];
        pos.set(it.x, it.y || 0, it.z);
        quat.setFromAxisAngle(up, it.rotY);
        if (it.sx !== undefined) scl.set(it.sx, it.sy, it.sz);
        else scl.setScalar(it.scale);
        mat.compose(pos, quat, scl).multiply(local);
        im.setMatrixAt(i, mat);
      }
      im.instanceMatrix.needsUpdate = true;
      im.computeBoundingSphere();
      im.frustumCulled = true;
      im.castShadow = false;
      im.receiveShadow = false;
      im.name = 'scatter-' + name;
      out.push(im);
    });
    return out;
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
    }, this.scatterPlan(regionId), this.wallPlan());
    if (table.complete) this.colliders[regionId] = table;
    return table;
  };

  // Round F: the world wall plan (one for the shared disc; cached once every
  // footprint is known, like the scatter plan; logs its counts once).
  RegionManager.prototype.wallPlan = function () {
    if (this.wallPlanCache) return this.wallPlanCache;
    var plan = whWallPlan(function (name) {
      return window.WH_ASSETS.getMeta(name);
    });
    if (plan.complete) {
      this.wallPlanCache = plan;
      console.log('[WH wall] ' + JSON.stringify(plan.stats));
      if (plan.stats.overDropLimit) {
        console.warn('[WH wall] drops ' + plan.stats.drops + ' > maxDrops ' +
          CFG.boundaryWall.exclusion.maxDrops + ': ' + plan.stats.dropReasons.join('; '));
      }
    }
    return plan;
  };

  // Round F: world-level light sockets (gate-arch lantern), live in BOTH
  // regions; fresh objects per call (game.js computeSockets writes .d).
  RegionManager.prototype.worldSockets = function () {
    var s = this.wallPlan().sockets;
    var out = [];
    for (var i = 0; i < s.length; i++) {
      out.push({ id: s[i].id, x: s[i].x, y: s[i].y, z: s[i].z,
                 intensity: s[i].intensity, weight: s[i].weight });
    }
    return out;
  };

  // Round F: build the wall ring + chord (one InstancedMesh per wall asset =
  // 2 draw calls) and the gate arch + hung lantern ONCE into a world group
  // added straight to the scene. Region groups are disposed on swaps; this
  // group is not a region group, so disposeRegion never touches it and a
  // rebuild can never double-add it (guarded by this.worldGroup).
  RegionManager.prototype.buildWorld = function () {
    if (this.worldGroup) return this.worldGroup;
    var plan = this.wallPlan();
    if (!plan.complete) return null;  // footprints not known yet: next buildRegion retries
    var group = new THREE.Group();
    group.name = 'world-boundary-wall';
    var W = CFG.boundaryWall;
    var byAsset = {};
    plan.segments.forEach(function (sg) {
      (byAsset[sg.asset] = byAsset[sg.asset] || []).push({ x: sg.x, y: -W.sinkM, z: sg.z,
        rotY: sg.rotY, sx: sg.sx, sy: sg.sy, sz: sg.sz });
    });
    Object.keys(byAsset).forEach(function (name) {
      whBuildInstanced(name, byAsset[name]).forEach(function (im) {
        im.name = 'wall-' + name;
        group.add(im);
      });
    });
    if (plan.arch) {
      var A = plan.arch;
      var arch = new THREE.Group();          // unscaled: origin = opening center
      arch.name = 'gate-arch';
      arch.position.set(A.x, 0, A.z);
      arch.rotation.y = A.rotY;
      var gate = window.WH_ASSETS.instance(A.asset);
      gate.position.x = A.offsetX;
      gate.scale.set(A.scale, A.scale, A.scaleZ);
      arch.add(gate);
      if (plan.lantern) {
        var lan = window.WH_ASSETS.instance(plan.lantern.asset);
        lan.position.set(0, plan.lantern.localY, 0);
        lan.scale.setScalar(plan.lantern.scale);
        lan.traverse(function (o) {
          // pixel-art glass: the emissive map gets the same nearest filter
          // prepTemplate gives the base map (shared template material)
          if (o.isMesh && o.material && o.material.emissiveMap) {
            o.material.emissiveMap.magFilter = THREE.NearestFilter;
            o.material.emissiveMap.needsUpdate = true;
          }
        });
        arch.add(lan);
      }
      group.add(arch);
    }
    // CC-C2: door arches (world group: seen from both sides of the door)
    plan.doorArches.forEach(function (D) {
      var da = new THREE.Group();          // unscaled: origin = opening center
      da.name = 'door-arch';
      da.position.set(D.x, 0, D.z);
      da.rotation.y = D.rotY;
      var dg = window.WH_ASSETS.instance(D.asset);
      dg.position.x = D.offsetX;
      dg.scale.set(D.scale, D.scale, D.scaleZ);
      da.add(dg);
      group.add(da);
    });
    this.scene.add(group);
    this.worldGroup = group;
    return group;
  };

  // Round E: scatter plan per region (cached once every footprint is known,
  // like the collider table; logs its counts once).
  RegionManager.prototype.scatterPlan = function (regionId) {
    this.scatterPlans = this.scatterPlans || {};
    if (this.scatterPlans[regionId]) return this.scatterPlans[regionId];
    var meta = function (name) {
      return window.WH_ASSETS.getMeta(name);
    };
    // CC-C4a: a heightfield region seats every instance on the exact B-TRI
    // ground (tiny ground cover: the exact seat, not footY); A/B: none
    var G = window.WH_GROUND;
    if (G && G.has(regionId)) {
      meta.heightAt = function (x, z) { return G.heightAt(regionId, x, z); };
    }
    var plan = whScatterPlan(regionId, meta);
    if (plan.complete) {
      this.scatterPlans[regionId] = plan;
      console.log('[WH scatter] ' + regionId + ' ' + JSON.stringify(plan.stats));
    }
    return plan;
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

  // CC-C4 prop y-feed: the terrain seat under a prop's footprint (min ground
  // at its center + 4 points at terrain.propFootR) in a heightfield region;
  // 0 everywhere else (A/B: today's y).
  function whGroundFeed(regionId, x, z) {
    var G = window.WH_GROUND;
    if (!G || !G.has(regionId)) return 0;
    return G.footY(regionId, x, z, DEFS.regions[regionId].cfg.terrain.propFootR);
  }

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
    this.buildWorld();                // Round F: world wall, once (no-op after)

    // ground disc: procedural pixel-art canvas texture (boot-time, cached),
    // region-biased blotch mix (A olive-dominant, B charcoal-dominant)
    // CC-C4: a heightfield region (WH_GROUND.has: C only) walks on the
    // seeded terrain mesh; its flat disc stays only as the SKIRT under and
    // outside the 560 m mesh square, plain-colored at the mesh's rim color
    // (the rim fades to h 0, so mesh edge and skirt meet flush). A/B: the
    // textured flat disc exactly as before.
    var hasTerrain = window.WH_GROUND && window.WH_GROUND.has(regionId);
    var groundMat = hasTerrain ? new THREE.MeshStandardMaterial({
      color: region.cfg.terrain.meshColorMoss,
      roughness: 0.95, metalness: 0.0, side: THREE.DoubleSide
    }) : new THREE.MeshStandardMaterial({
      color: 0xffffff,
      map: makeGroundTexture(regionId),
      roughness: 1.0, metalness: 0.0, side: THREE.DoubleSide
    });
    var ground = new THREE.Mesh(
      new THREE.CircleGeometry(whVisualGroundRadius(regionId), 48),
      groundMat
    );
    ground.rotation.x = -Math.PI / 2;
    // CC-C2: own-disc region (C): centered on its disc, sunk to groundY
    // (B's disc is y = 0) so the two never z-fight
    if (region.center) {
      ground.position.set(region.center.x, region.cfg.groundY || 0, region.center.z);
    }
    ground.name = 'ground';
    group.add(ground);
    // CC-C4: the terrain mesh (built once, ~27 ms, cached by WH_GROUND; a
    // region dispose frees its GPU buffers, three re-uploads on re-entry)
    if (hasTerrain) group.add(window.WH_GROUND.mesh(regionId));

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

    // 10-03 change order 2: dirt path ribbon (visual only, region-gated by
    // CFG.world.dirtPath.regionId; no collider, polygon-offset decal).
    var dirtPath = buildDirtPath(regionId);
    if (dirtPath) group.add(dirtPath);
    // CC-C4a: the region's CFG.roads ribbons (C: the King's Roads; unlit -
    // no light rows exist for roads; one mesh per road = 5 draw calls in C)
    (CFG.roads || []).forEach(function (R) {
      if (R.regionId === regionId) group.add(buildRoad(regionId, R));
    });

    // props from manifest
    var regionCfg = region.cfg;
    // CC-C3: a region whose CONFIG sets cullDistanceM (C only) records every
    // prop for the per-frame visibility cull (cullProps); A/B: no list
    var cullList = regionCfg.cullDistanceM ? [] : null;
    for (var i = 0; i < regionCfg.props.length; i++) {
      var p = regionCfg.props[i];
      var obj = window.WH_ASSETS.instance(p.asset);
      obj.position.set(p.x, whGroundFeed(regionId, p.x, p.z) + (p.y || 0), p.z);
      obj.rotation.y = p.rotY;
      obj.scale.setScalar(p.scale);
      group.add(obj);
      if (cullList) cullList.push({ obj: obj, x: p.x, z: p.z });
    }

    // Round E scatter: extra trees as normal props (colliders via
    // propColliders), bushes + grass as one InstancedMesh per asset.
    var plan = this.scatterPlan(regionId);
    for (var si = 0; si < plan.trees.length; si++) {
      var sTree = plan.trees[si];
      var tObj = window.WH_ASSETS.instance(sTree.asset);
      tObj.position.set(sTree.x, whGroundFeed(regionId, sTree.x, sTree.z), sTree.z);
      tObj.rotation.y = sTree.rotY;
      tObj.scale.setScalar(sTree.scale);
      group.add(tObj);
      if (cullList) cullList.push({ obj: tObj, x: sTree.x, z: sTree.z });
    }
    this.cullLists = this.cullLists || {};
    if (cullList) this.cullLists[regionId] = cullList;
    // CC-C4a: a region with scatterCellM (C) buckets each asset's instances
    // into scatterCellM grid cells: one InstancedMesh per (asset, cell) that
    // joins the cull list as ONE object at its centroid, hidden whole when the
    // player is past scatterCullM + the cell's radius (no per-instance
    // culling). A/B: one InstancedMesh per asset, frustum culling only.
    var cellM = regionCfg.scatterCellM;
    Object.keys(plan.instances).forEach(function (name) {
      var all = plan.instances[name];
      if (!cellM || !cullList) {
        whBuildInstanced(name, all).forEach(function (im) { group.add(im); });
        return;
      }
      var cells = {};
      all.forEach(function (it) {
        var key = Math.floor(it.x / cellM) + ':' + Math.floor(it.z / cellM);
        (cells[key] = cells[key] || []).push(it);
      });
      Object.keys(cells).forEach(function (key) {
        var list = cells[key], cx = 0, cz = 0, r = 0, q;
        for (q = 0; q < list.length; q++) { cx += list[q].x; cz += list[q].z; }
        cx /= list.length; cz /= list.length;
        for (q = 0; q < list.length; q++) {
          r = Math.max(r, Math.sqrt((list[q].x - cx) * (list[q].x - cx) +
            (list[q].z - cz) * (list[q].z - cz)));
        }
        var hide = regionCfg.scatterCullM + r;
        var show = regionCfg.scatterCullM * regionCfg.cullShowFrac + r;
        whBuildInstanced(name, list).forEach(function (im) {
          group.add(im);
          cullList.push({ obj: im, x: cx, z: cz, hide2: hide * hide, show2: show * show });
        });
      });
    });

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
        if (obj.isInstancedMesh) obj.dispose();   // Round E: instance buffer
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
    if (this.cullLists) delete this.cullLists[regionId];   // CC-C3
  };

  // CC-C3 per-frame visibility cull (C only: regions without a cull list,
  // A/B, return at once). Distance from the PLAYER (x, z) to each recorded
  // prop: visible props hide past cullDistanceM, hidden props re-show inside
  // cullDistanceM * cullShowFrac (hysteresis, no flicker at the band). Both
  // bands sit past C's fog-invisible depth (CONFIG.regionC ledger), so the
  // toggle is never seen. No allocation; no geometry rebuild.
  RegionManager.prototype.cullProps = function (regionId, x, z) {
    var list = this.cullLists && this.cullLists[regionId];
    if (!list) return;
    var cfg = DEFS.regions[regionId].cfg;
    var hide2 = cfg.cullDistanceM * cfg.cullDistanceM;
    var show = cfg.cullDistanceM * cfg.cullShowFrac, show2 = show * show;
    for (var i = 0; i < list.length; i++) {
      var c = list[i], dx = c.x - x, dz = c.z - z, d2 = dx * dx + dz * dz;
      // CC-C4a: a scatter cell carries its own bands (scatterCullM + radius)
      if (c.obj.visible) {
        if (d2 > (c.hide2 || hide2)) c.obj.visible = false;
      } else if (d2 < (c.show2 || show2)) {
        c.obj.visible = true;
      }
    }
  };

  // Main per-frame entry. Applies transition logic to live scene. Returns the
  // transition result for the caller (HUD updates etc).
  // CC-C2: with more than one neighbor the hidden (pre-warm) group and the
  // region left behind are tracked by id, not by neighborOf (single
  // neighbor: the same groups as before).
  RegionManager.prototype.disposeHiddenExcept = function (keepId) {
    var self = this;
    Object.keys(this.groups).forEach(function (rid) {
      if (rid !== keepId && rid !== self.logic.activeId && !self.groups[rid].visible) {
        self.disposeRegion(rid);
      }
    });
  };

  RegionManager.prototype.tickTransition = function (x, z) {
    var prevActiveId = this.logic.activeId;
    var result = this.logic.tickTransition(x, z);
    if (result.action === 'prewarm') {
      this.buildRegion(result.newActiveId || this.logic.prewarmedId, true);
    } else if (result.action === 'dispose') {
      // logic already cleared prewarmedId: every hidden group goes
      this.disposeHiddenExcept(null);
    } else if (result.action === 'cross') {
      var oldId = prevActiveId;
      // reveal the pre-warmed neighbor (instant swap: already built)
      var newGroup = this.groups[result.newActiveId];
      if (newGroup) {
        newGroup.visible = true;
      } else {
        this.buildRegion(result.newActiveId, false);
      }
      // unload old region
      if (this.groups[oldId]) this.disposeRegion(oldId);
      this.disposeHiddenExcept(null);   // CC-C2: no stale pre-warm of a third region
      this.enemies[result.newActiveId] = this.enemies[result.newActiveId] || [];
    }
    // CC-C3: the active region's prop cull (on a cross: at the mapped spot)
    this.cullProps(this.logic.activeId,
      result.mappedPos ? result.mappedPos.x : x,
      result.mappedPos ? result.mappedPos.z : z);
    return result;
  };

  // C3 death respawn at a camp in the OTHER region: the 'cross' swap of
  // tickTransition without walking the gate (target built or revealed, old
  // region disposed, logic re-pointed). game.js applies lighting / sky /
  // banner like a cross. Returns false when already active.
  RegionManager.prototype.switchTo = function (regionId) {
    var oldId = this.logic.activeId;
    if (regionId === oldId) return false;
    this.logic.activeId = regionId;
    this.logic.prewarmedId = null;
    this.logic.buildCounts[regionId] = (this.logic.buildCounts[regionId] || 0) + 1;
    if (this.groups[regionId]) this.groups[regionId].visible = true;
    else this.buildRegion(regionId, false);
    if (this.groups[oldId]) this.disposeRegion(oldId);
    this.disposeHiddenExcept(null);     // CC-C2: no stale pre-warm of a third region
    this.enemies[regionId] = this.enemies[regionId] || [];
    return true;
  };

  RegionManager.prototype.updateEnemies =function (dt, playerPos, playerAlive, canDamagePlayer, activeId) {
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
  window.WH_ScatterPlan = whScatterPlan;   // Round E: pure, for debug/tests
  window.WH_WallPlan = whWallPlan;         // Round F: pure, for debug/tests
  // C3 camp deploy clearances (js/camp.js): the same pure helpers the
  // scatter uses for the dirt path band, the gate corridor and the rim
  window.WH_RegionGeom = {
    distToPath: whDistToPath,
    roadsFor: whRoadsFor,             // CC-C4a: A's dirtPath + CFG.roads rows
    distToRoad: whDistToRoad,
    meetsCorridor: whMeetsCorridor,
    playRadius: whPlayRadius
  };
})();