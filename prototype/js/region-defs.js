// Witch Hunter prototype v1 - region layout + boundary/transition data.
// Region geometry, enemy rosters and props are declared in CONFIG (see
// CONFIG.regionA / CONFIG.regionB). This file derives the runtime region
// records from CONFIG so every tunable stays CONFIG-driven, and exposes a
// THREE-free transition helper table for logic tests (see section 2 of the
// validation spec).

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;

  // ---- Derived region records ------------------------------------------------

  // Region A occupies z > boundary.z; region B occupies z < boundary.z.
  // sideOfBoundary: +1 for A, -1 for B. Used by clamping and position mapping.
  function makeRegion(cfgRegion, sideOfBoundary) {
    return {
      id: cfgRegion.id,
      name: cfgRegion.name,
      cfg: cfgRegion,
      side: sideOfBoundary,
      spawn: { x: cfgRegion.spawn.x, z: cfgRegion.spawn.z },
      fogColor: cfgRegion.fogColor,
      fogDensity: cfgRegion.fogDensity,
      ambientLightLevel: cfgRegion.ambientLightLevel,
      enemies: cfgRegion.enemies,
      props: cfgRegion.props,
      // CC-C2: a region with its own disc (regionC) carries center +
      // groundRadius; A/B leave them unset = the shared disc at the origin,
      // radius CFG.world.groundRadius (today's path)
      center: cfgRegion.center || null,
      groundRadius: cfgRegion.groundRadius || null
    };
  }

  var regions = {};
  regions[CFG.regionA.id] = makeRegion(CFG.regionA, 1);
  regions[CFG.regionB.id] = makeRegion(CFG.regionB, -1);
  // CC-C2: side is the plane-0 (A/B) convention only; C lies on the -z side
  // of it but is NOT a member of connections[0]. Door sides live
  // per-connection (conn.sides) - B is -1 on plane 0 and +1 on the B/C plane.
  regions[CFG.regionC.id] = makeRegion(CFG.regionC, -1);

  // Region adjacency: each region lists the regions reachable from it and the
  // single chokepoint crossing that connects them. Entrances/exits exist ONLY
  // on this path (spec D2); everywhere else the boundary is blocked.
  var connections = [
    {
      from: CFG.regionA.id,
      to: CFG.regionB.id,
      axis: 'z',                        // boundary plane normal axis
      planeCoord: CFG.boundary.z,       // boundary plane at z = planeCoord
      fromSide: 1,                      // A side is +z
      chokepointCenterX: CFG.chokepoint.centerX,
      chokepointHalfWidth: CFG.chokepoint.width / 2
    },
    // CC-C2: B/C DOOR on B's north edge. The plane z = planeCoord exists
    // only as a cross-line INSIDE the door window (no wall anywhere else);
    // sides are per-connection (B occupies z >= -86, C z <= -86). gatedTo:
    // crossings INTO this region obey the game.js gate predicate (tutorial
    // law: locked while the day/night clock is dormant).
    {
      from: CFG.regionB.id,
      to: CFG.regionC.id,
      axis: 'z',
      planeCoord: CFG.regionC.door.planeZ,
      sides: {},
      door: {
        doorX: CFG.regionC.door.doorX,
        doorHalfWidth: CFG.regionC.door.doorHalfWidth,
        suspendDepthM: CFG.regionC.door.suspendDepthM,
        wallGapPadM: CFG.regionC.door.wallGapPadM,
        arch: CFG.regionC.door.arch,
        gatedTo: CFG.regionC.id
      }
    }
  ];
  connections[1].sides[CFG.regionB.id] = 1;
  connections[1].sides[CFG.regionC.id] = -1;

  // ---- THREE-free transition helpers (used by region-manager and tests) ------

  // Returns the connection between two region ids, or null.
  function connectionBetween(fromId, toId) {
    for (var i = 0; i < connections.length; i++) {
      var c = connections[i];
      if ((c.from === fromId && c.to === toId) || (c.from === toId && c.to === fromId)) {
        return c;
      }
    }
    return null;
  }

  // Is (x, z) inside the passable chokepoint interval of this connection?
  function insideChokepoint(conn, x) {
    return x >= conn.chokepointCenterX - conn.chokepointHalfWidth &&
           x <= conn.chokepointCenterX + conn.chokepointHalfWidth;
  }

  // CC-C2: is x inside a door connection's window? (|x - doorX| <= half-width)
  function insideDoorWindow(conn, x) {
    return !!conn.door && Math.abs(x - conn.door.doorX) <= conn.door.doorHalfWidth;
  }

  // CC-C2 per-connection membership + sides. A connection without a sides
  // table (connections[0], A/B) reads the region's plane-0 side (today's
  // convention, unchanged).
  function isMember(conn, regionId) {
    return conn.from === regionId || conn.to === regionId;
  }

  function otherEnd(conn, regionId) {
    return conn.from === regionId ? conn.to : conn.from;
  }

  function sideIn(conn, regionId) {
    return conn.sides ? conn.sides[regionId] : regions[regionId].side;
  }

  // Every connection a region is a member of, in table order.
  function connectionsOf(regionId) {
    var out = [];
    for (var i = 0; i < connections.length; i++) {
      if (isMember(connections[i], regionId)) out.push(connections[i]);
    }
    return out;
  }

  // Which side of the boundary plane is z on, relative to the connection?
  // +1 means the from-region side, -1 means the to-region side.
  function sideOfPlane(conn, z) {
    return z > conn.planeCoord ? 1 : -1;
  }

  // Map a position across the boundary: x (tangent) preserved; z placed
  // targetSide-deep past the plane. targetSide = the side (in region-defs
  // convention: +1 A, -1 B) the player should LAND on, normally the
  // destination region's home side, so the crossing cannot re-trigger.
  function mapPositionAcross(conn, x, z, depth, targetSide) {
    var dist = Math.abs(z - conn.planeCoord);
    var side = targetSide !== undefined ? targetSide : -sideOfPlane(conn, z);
    return {
      x: x,                             // tangent preserved
      z: conn.planeCoord + side * Math.max(dist, depth)
    };
  }

  // Distance from a point to the boundary plane (absolute, along normal axis).
  function distanceToBoundary(conn, z) {
    return Math.abs(z - conn.planeCoord);
  }

  // Is the point on the from-region side of this connection?
  function isOnFromSide(conn, z) {
    return sideOfPlane(conn, z) === conn.fromSide;
  }

  // Neighbor id for a region (v1: first neighbor in table order; CC-C2 the
  // region manager walks connectionsOf instead).
  function neighborOf(regionId) {
    for (var i = 0; i < connections.length; i++) {
      if (connections[i].from === regionId) return connections[i].to;
      if (connections[i].to === regionId) return connections[i].from;
    }
    return null;
  }

  window.WH_REGION_DEFS = {
    regions: regions,
    connections: connections,
    connectionBetween: connectionBetween,
    insideChokepoint: insideChokepoint,
    sideOfPlane: sideOfPlane,
    mapPositionAcross: mapPositionAcross,
    distanceToBoundary: distanceToBoundary,
    isOnFromSide: isOnFromSide,
    neighborOf: neighborOf,
    insideDoorWindow: insideDoorWindow,
    isMember: isMember,
    otherEnd: otherEnd,
    sideIn: sideIn,
    connectionsOf: connectionsOf
  };
})();