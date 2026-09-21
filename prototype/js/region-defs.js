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
      props: cfgRegion.props
    };
  }

  var regions = {};
  regions[CFG.regionA.id] = makeRegion(CFG.regionA, 1);
  regions[CFG.regionB.id] = makeRegion(CFG.regionB, -1);

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
    }
  ];

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

  // Neighbor id for a region (v1: single neighbor per region).
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
    neighborOf: neighborOf
  };
})();