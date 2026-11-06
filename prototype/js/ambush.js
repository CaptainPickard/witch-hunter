// Witch Hunter prototype - night raids (CC-AE1, io/specs/cc-ae1-night-raids-spec.md).
// A raid director over the Old King's Roads of region C: at clock phase
// 'night' (clock FREE-RUNNING only - the dormant boot look is night too, so
// the wake gate reads dayNight.dormant === false), away from bandit fires,
// a party of stock enemies (2 bandit + 1 wolf, doc 34 §6 night road row)
// spawns 14-17.5 m off a road centerline BEHIND the player, pre-aggroed,
// after a 2.0 s warning HUD cue. Parties are TRANSIENT: raiders carry
// e.raidMember = true (region-manager.js never records their corpses into
// regionStates), carry NO packId and NO CONFIG roster row - CC-C5 pack
// machinery untouched, save.js untouched, enemy.js untouched.
// State machine: 'idle' -> (gates + checkSec roll) -> 'warn' (CUE) -> 'live'
// -> (wipe / leash home / silent region-rebuild end) -> 'idle' + cooldown.
// Dawn cancels a pending warn (refund, no spawn); a live raid finishes
// naturally (the stock leash does the work); nightParties resets at dawn.
// Art law: no new materials, no new meshes, no new lights - the amber warn
// toast (inventoryUI toast, works screen-closed) is the round's ONE accent.
// Spawn grammar mirrors the landed recipe (Enemy.prototype.spawnMinion,
// js/enemy.js, used read-only): new WH_Enemy(type, scene, regionId, x, z) +
// setBody(WH_Enemy.makeBody(type)) + list.push into rm.enemies[regionId] +
// rm.scene.add(e.root).
// Exposes window.WH_AMBUSH:
//   init(game)     store the game ref (game.js owns the wiring, once)
//   tick(dt)       the state machine, one frame
//   state()        read-only snapshot { mode, party, nightParties, cooldownT }
//   pickRaidSeat() PURE seat picker: reads game/CONFIG/WH_GROUND only; its
//                  Math.random calls happen ONLY inside its own body
// Seat law (A-1 lock law, scratch/cc-ae1/ probe v3): rear anchor = player
// pos + (sin, cos) of (P.yaw + PI + jitter(rearSpreadDeg)) at 12 m -> nearest
// sample point on a seat road row (.points rows of raid.regionId; stone ring
// + notch beds EXCLUDED) within roadSeekRadiusM -> perpendicular offset in
// spawnBandM (random side, uniform) -> validate: branch-road notch-mouth arc
// (terminal point, kingsRoad exempt), WH_GROUND.slopeTan, CONFIG.regionC.props
// clearance, stone-ring radius around (0, -366), fires >= nearFireExclusionM
// (UNIFIED with the player gate) -> else slide along the road polyline toward
// the rear anchor's road-projection, seatSlideM per retry, seatRetries max.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var R = null;                    // CFG.raid (bound in init; load-time safe)

  var SEAT_ROADS = ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'];
  var BRANCH_TERMINALS = {         // notch-mouth exclusion arcs (terminal pt)
    northRoad: { x: 0, z: -596 },
    eastRoad: { x: 240, z: -366 },
    westRoad: { x: -240, z: -366 }
  };

  // ---- session state (rebuilt by init; NOTHING persists or saves) -----------
  var S = {
    game: null,
    mode: 'idle',                  // idle | warn | live
    checkT: 0,                     // trigger-check cadence accumulator
    warnT: 0,                      // warn-cue countdown
    party: [],                     // the live raid's members
    nightParties: 0,               // parties reserved this running night
    cooldownT: 0,                  // seconds left on the between-raids cooldown
    seat: null,                    // the seat locked at warn time
    prevPhase: null                // phase seen on the previous tick (new-night edge)
  };

  // per-road polyline precompute (CONFIG.roads rows are static; the memo
  // caches geometry only - it never writes into CONFIG)
  var roadCache = new Map();

  function dist2(ax, az, bx, bz) {
    var dx = ax - bx, dz = az - bz;
    return Math.sqrt(dx * dx + dz * dz);
  }

  function deg2rad(d) { return d * Math.PI / 180; }

  function wrapAngle(a) {         // shortest angular difference form (-PI..PI]
    while (a > Math.PI) a -= Math.PI * 2;
    while (a < -Math.PI) a += Math.PI * 2;
    return a;
  }

  // Cumulative arc-length geometry for one road row: sample every 1 m so
  // pointAt(s) and perpAt(s) are exact, plus the segment index per sample.
  function roadGeom(row) {
    var g = roadCache.get(row);
    if (g) return g;
    var pts = row.points;
    var samples = [];              // { x, z, arc } every ~1 m along the polyline
    var segs = [];                 // { ax, az, dx, dz, len, arc0 }
    var arc = 0;
    for (var i = 0; i + 1 < pts.length; i++) {
      var ax = pts[i][0], az = pts[i][1];
      var bx = pts[i + 1][0], bz = pts[i + 1][1];
      var len = dist2(ax, az, bx, bz);
      var dx = 0, dz = 0;
      if (len > 1e-9) { dx = (bx - ax) / len; dz = (bz - az) / len; }
      segs.push({ ax: ax, az: az, dx: dx, dz: dz, len: len, arc0: arc });
      if (i === 0) samples.push({ x: ax, z: az, arc: 0 });
      var n = Math.max(1, Math.ceil(len / 1));
      for (var j = 1; j <= n; j++) {
        var t = Math.min(1, j / n);
        samples.push({ x: ax + (bx - ax) * t, z: az + (bz - az) * t,
          arc: arc + len * t });
      }
      arc += len;
    }
    g = { samples: samples, segs: segs, total: arc };
    roadCache.set(row, g);
    return g;
  }

  // Position + unit perpendicular on a road polyline at arc length s.
  function pointAt(g, s) {
    if (s <= 0) s = 0;
    if (s > g.total) s = g.total;
    for (var i = 0; i < g.segs.length; i++) {
      var seg = g.segs[i];
      if (s <= seg.arc0 + seg.len || i === g.segs.length - 1) {
        var t = s - seg.arc0;
        if (t < 0) t = 0;
        if (t > seg.len) t = seg.len;
        return { x: seg.ax + seg.dx * t, z: seg.az + seg.dz * t,
          px: -seg.dz, pz: seg.dx };
      }
    }
    return null;
  }

  // Arc length of the closest point of the polyline to (x, z) (the projection).
  function projectArc(g, x, z) {
    var bestArc = 0, bestD = Infinity;
    for (var i = 0; i < g.segs.length; i++) {
      var seg = g.segs[i];
      var t = ((x - seg.ax) * seg.dx + (z - seg.az) * seg.dz) / (seg.len || 1);
      if (t < 0) t = 0;
      if (t > seg.len) t = seg.len;
      var px = seg.ax + seg.dx * t, pz = seg.az + seg.dz * t;
      var d = dist2(px, pz, x, z);
      if (d < bestD) { bestD = d; bestArc = seg.arc0 + t; }
    }
    return bestArc;
  }

  // fire rows for the SEAT validation: the A-1 probe law's set - the 7
  // banditCampfire rows of regionC.props (valspec §1 pins exactly these for
  // the seat predicates; probe v1/v3 evidence is regionC-scoped)
  function seatFireRows() {
    var out = [];
    var props = CFG.regionC && CFG.regionC.props;
    if (!props) return out;
    for (var i = 0; i < props.length; i++) {
      if (props[i].asset === 'banditCampfire') out.push(props[i]);
    }
    return out;
  }

  // fire rows for the PLAYER gate g5: the spec reads CONFIG-wide ("nearest
  // CONFIG banditCampfire row distance (player) > nearFireExclusionM") - every
  // region's props rows
  function fireRows() {
    var out = [];
    var regions = ['regionA', 'regionB', 'regionC', 'regionD', 'regionE'];
    for (var r = 0; r < regions.length; r++) {
      var props = CFG[regions[r]] && CFG[regions[r]].props;
      if (!props) continue;
      for (var i = 0; i < props.length; i++) {
        if (props[i].asset === 'banditCampfire') out.push(props[i]);
      }
    }
    return out;
  }

  // null when the seat passes EVERY lock-law predicate, else the 'why' string.
  // P = the player pose (AE1-A player floor); pos { x, z } read live.
  function seatWhy(x, z, seatArc, g, row, P) {
    // a. notch-mouth exclusion: the seat's road point within the branch
    //    road's terminal arc (probe mouthEnd = last notchMouthExclusionM of
    //    the road); kingsRoad exempt (spec: branch terminals only)
    if (BRANCH_TERMINALS[row.id] && g.total - seatArc < R.notchMouthExclusionM) {
      return 'notch-mouth';
    }
    // a2. AE1-A rendered-road floor: distance to the road the player SEES -
    //     the SWAYED render geometry via the engine's own pure helper
    //     (window.WH_RegionGeom.distToRoad walks whRoadLine: Catmull-Rom +
    //     sideways sway, exactly what the renderer draws). Polyline fallback
    //     (the old law) only when region-manager.js is absent (harness/node).
    var RG = window.WH_RegionGeom;
    var roadD;
    if (RG && typeof RG.distToRoad === 'function') {
      roadD = RG.distToRoad(row, x, z);
    } else {
      var pp = pointAt(g, projectArc(g, x, z));
      roadD = dist2(pp.x, pp.z, x, z);
    }
    if (roadD < R.seatMinRoadRenderedM) return 'road-rendered';
    // a3. AE1-A player floor: straight-line seat-to-player distance
    //     (pop-in guard; geometry-independent)
    if (P && P.pos && dist2(x, z, P.pos.x, P.pos.z) < R.minPlayerDistM) {
      return 'player-dist';
    }
    // b. ground slope (WH_GROUND heightfield; region has a heightfield)
    if (window.WH_GROUND && window.WH_GROUND.has(R.regionId)) {
      if (window.WH_GROUND.slopeTan(R.regionId, x, z) > R.seatMaxSlopeTan) {
        return 'slope';
      }
    }
    // c. CONFIG prop rows clearance (rows with .x)
    var props = CFG.regionC && CFG.regionC.props;
    if (props) {
      for (var i = 0; i < props.length; i++) {
        var p = props[i];
        if (p.x === undefined) continue;
        if (dist2(x, z, p.x, p.z) < R.seatMinPropM) return 'prop';
      }
    }
    // d. the Stone (0, -366) ring radius
    if (dist2(x, z, 0, -366) < R.stoneRingExclusionR) return 'stone';
    // e. fires >= nearFireExclusionM (one unified number; the SEAT gate uses
    // the probe's law set - the 7 regionC fire rows the valspec pins)
    var fires = seatFireRows();
    for (var f = 0; f < fires.length; f++) {
      if (dist2(x, z, fires[f].x, fires[f].z) < R.nearFireExclusionM) {
        return 'fire';
      }
    }
    return null;
  }

  // ---- seat picker (PURE; every Math.random call is INSIDE this body) -------
  function pickRaidSeat() {
    if (!R || !S.game || !S.game.player) return { ok: false, why: 'no-state' };
    var P = S.game.player;
    var yaw = P.yaw + Math.PI +                    // rear arc, then jitter +-rearSpreadDeg
      (Math.random() * 2 - 1) * deg2rad(R.rearSpreadDeg);

    // 1. rear anchor, 12 m out along the (jittered) rear-arc bearing
    var ax = P.pos.x + Math.sin(yaw) * 12;
    var az = P.pos.z + Math.cos(yaw) * 12;

    // 2. the seat-eligible road rows of the raid region (.points rows ONLY;
    //    stoneRing has .ring; stoneApproach + notch beds are excluded by id)
    var rows = [];
    for (var i = 0; i < CFG.roads.length; i++) {
      var rd = CFG.roads[i];
      if (rd.regionId !== R.regionId) continue;
      if (!rd.points) continue;
      if (SEAT_ROADS.indexOf(rd.id) === -1) continue;
      rows.push(rd);
    }

    // 3. seek: nearest sample point on any seat road within roadSeekRadiusM
    var best = null, bestGeom = null, bestRow = null, bestD = Infinity;
    for (var r = 0; r < rows.length; r++) {
      var g = roadGeom(rows[r]);
      for (var s = 0; s < g.samples.length; s++) {
        var sm = g.samples[s];
        var d = dist2(sm.x, sm.z, ax, az);
        if (d < bestD) { bestD = d; best = sm; bestGeom = g; bestRow = rows[r]; }
      }
    }
    if (!best || bestD > R.roadSeekRadiusM) return { ok: false, why: 'no-road' };

    // 4. seat candidate = road point + perpendicular offset (random side,
    //    uniform in spawnBandM), slid along the road toward the rear anchor's
    //    road-projection on later attempts
    var side = Math.random() < 0.5 ? 1 : -1;
    var mag = R.spawnBandM[0] + Math.random() * (R.spawnBandM[1] - R.spawnBandM[0]);
    var slideDir = projectArc(bestGeom, ax, az) >= best.arc ? 1 : -1;

    var slide = 0, why = null;
    var arc = best.arc;
    for (var attempt = 0; attempt <= R.seatRetries; attempt++) {
      var pt = pointAt(bestGeom, arc);           // ALWAYS on the polyline
      var x = pt.x + pt.px * mag * side;
      var z = pt.z + pt.pz * mag * side;
      why = seatWhy(x, z, arc, bestGeom, bestRow, P);
      if (why === null) {
        // diagnostics: the seat's bearing from the player vs the rear-arc
        // bearing (P.yaw + PI) - the rear-arc measure (rearSpreadDeg window)
        var delta = wrapAngle(Math.atan2(x - P.pos.x, z - P.pos.z) -
          (P.yaw + Math.PI));
        return { ok: true, x: x, z: z, roadId: bestRow.id, slide: slide,
          bearingDeg: delta * 180 / Math.PI };
      }
      if (attempt === R.seatRetries) break;
      slide++;
      arc += R.seatSlideM * slideDir;            // march toward the projection
    }
    return { ok: false, why: why || 'seat-fail', roadId: bestRow.id, slide: slide };
  }

  // ---- gates (ALL must hold to enter 'warn' from 'idle') ---------------------
  function gates() {
    var dn = S.game.dayNight;
    if (dn.dormant !== false) return false;                       // g1 dormant boot
    if (dn.phase !== 'night') return false;                       // g2 clock phase
    if (S.game.player.state !== 'alive') return false;            // g3 player alive
    var rm = S.game.regionManager;
    if (!rm || !rm.logic || rm.logic.activeId !== R.regionId) return false; // g4 region
    var fires = fireRows();
    for (var i = 0; i < fires.length; i++) {                      // g5 fires (unified 50)
      if (dist2(S.game.player.pos.x, S.game.player.pos.z,
        fires[i].x, fires[i].z) <= R.nearFireExclusionM) return false;
    }
    if (S.cooldownT !== 0) return false;                          // g6 cooldown
    if (S.nightParties >= R.partiesPerNightMax) return false;     // g7 per-night cap
    return true;                                                  // g8 = pickRaidSeat
  }

  // ---- spawn (the proven runtime grammar; raiders are TRANSIENT) -------------
  function spawnParty(seat) {
    var rm = S.game.regionManager;
    var P = S.game.player;
    var list = rm.enemies[R.regionId];
    if (!list) return 0;           // defensive: region rebuilt under us
    var plan = [];
    var b;
    for (b = 0; b < R.party.banditCount; b++) plan.push('bandit');
    for (b = 0; b < R.party.wolfCount; b++) plan.push('wolf');
    var n = 0;
    for (var i = 0; i < plan.length; i++) {
      var type = plan[i];
      var e = new window.WH_Enemy(type, rm.scene, R.regionId, seat.x, seat.z);
      e.raidMember = true;         // TRANSIENT law: the dead-state guard reads it
      e.setFsm('chase');           // pre-aggro: doc 34 "detection pre-set"
      e.yaw = Math.atan2(P.pos.x - seat.x, P.pos.z - seat.z);   // face the player
      e.setBody(window.WH_Enemy.makeBody(type));
      if (e.terrainHome) e.pos.y = e.groundY();
      e.root.position.copy(e.pos);
      e.yawFrame.rotation.y = e.yaw;
      list.push(e);                // rm.enemies keyed by regionId
      if (rm.scene && rm.scene.add) rm.scene.add(e.root);       // parent = scene
      S.party.push(e);
      n++;
    }
    return n;
  }

  function raidOver() {
    S.mode = 'idle';
    S.party = [];
    S.cooldownT = R.cooldownSec;
  }

  function toast(text, seconds) {
    if (R.debugMute) return;       // debugMute suppresses ALL ambush toasts
    if (S.game && S.game.inventoryUI && S.game.inventoryUI.toast) {
      S.game.inventoryUI.toast(text, seconds);
    }
  }

  // ---- frame tick -------------------------------------------------------------
  function tick(dt) {
    if (!R || !S.game) return;
    var dn = S.game.dayNight;

    if (S.mode === 'idle') {
      if (S.cooldownT > 0) S.cooldownT = Math.max(0, S.cooldownT - dt);
      // Dawn (the phase leaves 'night'): the per-night counter resets and the
      // director sleeps until night returns. The reset also re-arms the moment
      // night BEGINS again (phase 'day' -> 'night'), however the day passage
      // was ticked (or not ticked at all).
      if (dn.phase !== 'night') { S.nightParties = 0; return; }
      if (S.prevPhase !== null && S.prevPhase !== 'night') S.nightParties = 0;
      if (!gates()) { S.checkT = 0; return; }
      S.checkT += dt;
      if (S.checkT < R.checkSec) return;
      S.checkT = 0;
      // per-check roll; debugForce bypasses ONLY this roll (seats still must
      // pass) - Math.random is tick's ONLY call site, confining RNG law
      if (!R.debugForce && Math.random() >= R.triggerChance) return;

      // reserve + pick the seat ONCE (locked through the raid)
      var seat = pickRaidSeat();
      if (!seat.ok) return;        // g8 refused: stays idle, nothing reserved
      S.nightParties++;
      S.mode = 'warn';
      S.warnT = R.warnSec;
      S.seat = seat;
      // the warn cue: amber accent on the HUD layer (works screen-closed)
      toast(R.warnLine, R.warnSec + 0.6);
      return;
    }

    if (S.mode === 'warn') {
      // Dawn during warn: cancel - no spawn, refund the counter, NO cooldown.
      if (dn.phase !== 'night') {
        S.mode = 'idle';
        S.nightParties = 0;
        S.seat = null;
        return;
      }
      S.warnT -= dt;
      if (S.warnT > 0) return;
      var n = spawnParty(S.seat);  // spawn at the LOCKED warn-time seat
      if (n === 0) {               // region list vanished - refund, stay idle
        S.mode = 'idle';
        S.nightParties--;
        S.seat = null;
        return;
      }
      S.mode = 'live';
      S.seat = null;
      return;
    }

    if (S.mode === 'live') {
      // End when every member is dead (wipe), every member leashed home
      // (fsm 'idle'), or any member left the region list (rebuild / boundary
      // crossing -> end silently). Dawn does NOT interrupt a live raid.
      var allDead = S.party.length > 0;
      var allIdle = S.party.length > 0;
      var gone = false;
      var rm = S.game.regionManager;
      var list = rm && rm.enemies && rm.logic ? rm.enemies[rm.logic.activeId] : null;
      for (var i = 0; i < S.party.length; i++) {
        var e = S.party[i];
        if (e.fsm !== 'dead') allDead = false;
        if (e.fsm !== 'idle') allIdle = false;
        if (!list || list.indexOf(e) < 0) gone = true;
      }
      if (allDead || allIdle || gone) raidOver();
      return;
    }
    S.prevPhase = dn.phase;        // remember for the new-night edge reset
  }

  // ---- public surface ----------------------------------------------------------
  window.WH_AMBUSH = {
    init: function (game) {
      // re-bind CONFIG at init: the validator harness swaps window.WH_CONFIG
      // for a frozen debugMute clone per case, and Nicko's retunes land this
      // way too (only WH_CONFIG.raid fields change; geometry is untouched)
      CFG = window.WH_CONFIG;
      R = CFG.raid;                // CFG.raid exists at load time (spec §0)
      S.game = game;
      S.mode = 'idle';
      S.checkT = 0;
      S.warnT = 0;
      S.party = [];
      S.nightParties = 0;
      S.cooldownT = 0;
      S.seat = null;
      S.prevPhase = null;
    },
    tick: tick,
    state: function () {
      return {
        mode: S.mode,
        party: S.party.length,
        nightParties: S.nightParties,
        cooldownT: S.cooldownT
      };
    },
    pickRaidSeat: pickRaidSeat
  };
})();
