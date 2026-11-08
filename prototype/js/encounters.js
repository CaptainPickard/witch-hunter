// Witch Hunter prototype - wilderness encounter tables (CC-EN1, io/specs/cc-en1-spec.md).
// A NIGHT DIRECTOR over Darkwood Edge (regionB): at clock phase 'night'
// (clock FREE-RUNNING only - the dormant boot look is night too), away from the
// bandit campfire, a party drawn from the authored doc-51 Section 2 night table
// (CONFIG.encounters.biomes.darkwood_edge) spawns 14 m+ from the player after a
// 2.0 s amber HUD cue. Parties are TRANSIENT: raiders carry e.raidMember = true
// (region-manager.js never records their corpses into regionStates), carry NO
// packId and NO CONFIG roster row - CC-C5 pack machinery untouched, save.js
// untouched, enemy.js untouched. RegionC keeps CC-AE1 as its night director;
// its table rows in CONFIG.encounters.biomes.forest_of_the_old_king are the
// DATA RECORD of what AE1 already rolls (EN1-4: no second director).
// State machine: 'idle' -> (gates g1..g7 + checkSec cadence + roll) ->
// 'lock' (seat found, reserved) -> 'warn' (CUE) -> 'live' -> (wipe / all idle /
// member gone) -> 'idle' + cooldown. Dawn cancels a pending warn (refund, no
// spawn, NO cooldown - AE1 law); a live raid finishes naturally (dawn does NOT
// interrupt it); nightParties resets when the phase leaves 'night'.
// Art law: no new materials, no new meshes, no new lights - spawn bodies come
// from WH_Enemy.makeBody (read-only reuse); the amber warn toast (inventoryUI
// toast, works screen-closed) is the round's ONE accent (EN1-2), same as AE1.
// RNG law (EN1-3): random draws exist ONLY inside pickSeat (angle),
// spawnParty (spacing bearing), and tick's roll branch. Seat predicates p1..p9
// are DETERMINISTIC in (x, z) - seat rejection never depends on RNG.
// Exposes window.WH_ENCOUNTERS:
//   init(game)   store the game ref (game.js owns the wiring, once)
//   tick(dt)     the state machine, one frame
//   state()      read-only snapshot { mode, party, nightParties, cooldownT }
//   pickSeat()   PURE seat picker: reads game/CONFIG/WH_GROUND only; its
//                random draws happen ONLY inside its own body

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var E = null;                    // CFG.encounters (bound in init; load-time safe)
  var D = null;                    // E.director shorthand
  var S = {
    game: null,
    mode: 'idle',
    checkT: 0,                     // check-cadence accumulator
    warnT: 0,                      // warn-cue countdown
    party: [],                     // the live party's members
    nightParties: 0,               // parties reserved this running night
    cooldownT: 0,                  // seconds left on the between-parties cooldown
    seat: null,                    // the seat locked at reserve time
    row: null                      // the comp plan locked at reserve time
  };

  function dist2(ax, az, bx, bz) {
    var dx = ax - bx, dz = az - bz;
    return Math.sqrt(dx * dx + dz * dz);
  }

  function deg2rad(d) { return d * Math.PI / 180; }

  // regionB's fire rows (predicate p3): the banditCampfire props of
  // darkwood_edge. CFG-wide sweep like AE1's fireRows so a future second fire
  // row inside regionB is picked up without touching this file.
  function fireRows() {
    var out = [];
    var props = CFG.regionB && CFG.regionB.props;
    if (!props) return out;
    for (var i = 0; i < props.length; i++) {
      if (props[i].asset === 'banditCampfire') out.push(props[i]);
    }
    return out;
  }

  // The biome table the roll reads (director.nightTable key). null when absent.
  function nightTable() {
    if (!E || !E.biomes) return null;
    return E.biomes[D.nightTable] || null;
  }

  // ---- seat picker (PURE; every random draw is INSIDE this body) --------
  function pickSeat() {
    if (!S.game || !S.game.player) return { ok: false, why: 'no-player' };
    var P = S.game.player;
    var world = CFG.world || {};
    var playableR = (world.groundRadius || 90) - (world.playerMargin || 1.5);
    var props = (CFG.regionB && CFG.regionB.props) || [];
    var nodes = (CFG.regionB && CFG.regionB.nodes) || [];
    var roster = (CFG.regionB && CFG.regionB.enemies) || [];
    var fires = fireRows();
    var ko = null;                 // p1: the darkwood_edge keepOut ellipse row
    var keepOut = (CFG.scatter && CFG.scatter.keepOut) || [];
    for (var k = 0; k < keepOut.length; k++) {
      if (keepOut[k].regionId === 'darkwood_edge') ko = keepOut[k];
    }

    for (var attempt = 0; attempt < 24; attempt++) {
      // 1. polar candidate inside the playable disc, radial band spawnBandR
      var angle = Math.random() * Math.PI * 2;
      var band = D.spawnBandR;
      var r = playableR * (band[0] + Math.random() * (band[1] - band[0]));
      var x = Math.cos(angle) * r;
      var z = Math.sin(angle) * r;

      // p1 keepOut: outside the chapel ellipse + margin (>= 1.15 normalized)
      if (ko) {
        var ex = (x - ko.x) / ko.rx, ez = (z - ko.z) / ko.rz;
        if (ex * ex + ez * ez < 1.15) continue;
      }
      // p2 props: clearance to every prop row that carries .x
      var propBad = false;
      for (var i = 0; i < props.length; i++) {
        if (props[i].x === undefined) continue;
        if (dist2(x, z, props[i].x, props[i].z) < D.seatMinPropM) { propBad = true; break; }
      }
      if (propBad) continue;
      // p3 fires: no seat near a campfire (safety-law spawns)
      var fireBad = false;
      for (var f = 0; f < fires.length; f++) {
        if (dist2(x, z, fires[f].x, fires[f].z) <= D.nearFireExclusionM) { fireBad = true; break; }
      }
      if (fireBad) continue;
      // p4 player: straight-line pop-in guard
      if (P.pos && dist2(x, z, P.pos.x, P.pos.z) < D.seatMinPlayerDistM) continue;
      // p5 slope: heightfield check when the region has one (regionB in the
      // runtime does NOT: WG.has('darkwood_edge') is false - else-pass branch)
      if (window.WH_GROUND && window.WH_GROUND.has(D.regionId)) {
        if (window.WH_GROUND.slopeTan(D.regionId, x, z) > D.seatMaxSlopeTan) continue;
      }
      // p6 boundary band (EN1-6 FINAL FORM): B-side AND >= band off the plane
      if (!(z <= CFG.boundary.z - D.boundaryBandM)) continue;
      // p7 nodes: gather-node clearance
      var nodeBad = false;
      for (var n = 0; n < nodes.length; n++) {
        if (nodes[n].x === undefined) continue;
        if (dist2(x, z, nodes[n].x, nodes[n].z) < D.nodeM) { nodeBad = true; break; }
      }
      if (nodeBad) continue;
      // p8 roster: static-enemy spawn clearance
      var rowBad = false;
      for (var e8 = 0; e8 < roster.length; e8++) {
        if (roster[e8].x === undefined) continue;
        if (dist2(x, z, roster[e8].x, roster[e8].z) < D.enemyRowM) { rowBad = true; break; }
      }
      if (rowBad) continue;
      // p9 ground: visual only - store the heightAt read, never clamp
      var y = window.WH_GROUND && window.WH_GROUND.has(D.regionId) ?
        window.WH_GROUND.heightAt(D.regionId, x, z) : 0;
      return { ok: true, x: x, z: z, y: y, attempts: attempt + 1 };
    }
    return { ok: false, why: 'seat-fail' };
  }

  // ---- gates (ALL must hold to reserve from 'idle') ---------------------------
  function gates() {
    var dn = S.game.dayNight;
    if (dn.dormant !== false) return false;                       // g1 dormant boot
    if (dn.phase !== 'night') return false;                       // g2 clock phase
    if (S.game.player.state !== 'alive') return false;            // g3 player alive
    var rm = S.game.regionManager;
    if (!rm || !rm.logic || rm.logic.activeId !== D.regionId) return false; // g4 region
    var fires = fireRows();
    for (var i = 0; i < fires.length; i++) {                      // g5 fires
      if (dist2(S.game.player.pos.x, S.game.player.pos.z,
        fires[i].x, fires[i].z) <= D.nearFireExclusionM) return false;
    }
    if (S.cooldownT !== 0) return false;                          // g6 cooldown
    if (S.nightParties >= D.partiesPerNightMax) return false;     // g7 per-night cap
    return true;                                                  // g8 = pickSeat
  }

  // Recheck the movable members against the same authored rows as pickSeat.
  // The locked seat remains the safe fallback when a spacing offset is blocked.
  function memberClear(x, z) {
    var props = (CFG.regionB && CFG.regionB.props) || [];
    var fires = fireRows();
    var nodes = (CFG.regionB && CFG.regionB.nodes) || [];
    var roster = (CFG.regionB && CFG.regionB.enemies) || [];
    for (var i = 0; i < props.length; i++) {
      if (props[i].x !== undefined &&
          dist2(x, z, props[i].x, props[i].z) < D.seatMinPropM) return false;
    }
    for (var f = 0; f < fires.length; f++) {
      if (dist2(x, z, fires[f].x, fires[f].z) <= D.nearFireExclusionM) return false;
    }
    var P = S.game.player;
    if (P.pos && dist2(x, z, P.pos.x, P.pos.z) < D.seatMinPlayerDistM) return false;
    if (!(z <= CFG.boundary.z - D.boundaryBandM)) return false;
    for (var n = 0; n < nodes.length; n++) {
      if (nodes[n].x !== undefined &&
          dist2(x, z, nodes[n].x, nodes[n].z) < D.nodeM) return false;
    }
    for (var e8 = 0; e8 < roster.length; e8++) {
      if (roster[e8].x !== undefined &&
          dist2(x, z, roster[e8].x, roster[e8].z) < D.enemyRowM) return false;
    }
    return true;
  }

  // ---- spawn (the proven AE1 grammar; raiders are TRANSIENT) -------------------
  function spawnParty(seat, row) {
    var rm = S.game.regionManager;
    var P = S.game.player;
    var list = rm && rm.enemies ? rm.enemies[D.regionId] : null;
    if (!list) return 0;           // defensive: region rebuilt under us
    var listKey = rm.logic ? rm.logic.activeId : D.regionId;
    var home = rm.enemies[listKey] || list;   // spawn into the ACTIVE region list
    // EN1-5 spacing: ONE random bearing for the whole party (RNG site #3 of 4);
    // member m (0-based): m 0 at the seat, later members alternate sides along
    // the bearing at Math.ceil(m/2) * D.spawnSpacingM. Per-member predicate
    // re-check p2/p3/p4/p6/p7/p8; a member failing any falls back to the seat.
    var bearing = Math.random() * Math.PI * 2;    // spacing bearing (RNG site)
    var bx = Math.cos(bearing), bz = Math.sin(bearing);
    var slots = [];
    for (var c = 0; c < row.comp.length; c++) {
      for (var m = 0; m < row.comp[c].n; m++) slots.push(row.comp[c].type);
    }
    var n = 0;
    for (var i = 0; i < slots.length; i++) {
      var type = slots[i];
      var sx = seat.x, sz = seat.z;
      var off = Math.ceil(i / 2) * D.spawnSpacingM;
      var side = (i % 2 === 1) ? 1 : -1;
      var mx = (i === 0) ? seat.x : seat.x + bx * off * side;
      var mz = (i === 0) ? seat.z : seat.z + bz * off * side;
      if (i > 0 && !memberClear(mx, mz)) { mx = seat.x; mz = seat.z; }
      var e = new window.WH_Enemy(type, rm.scene, D.regionId, mx, mz);
      e.raidMember = true;         // TRANSIENT law: the dead-state guard reads it
      e.setFsm('chase');           // pre-aggro: doc 34 "detection pre-set"
      e.yaw = Math.atan2(P.pos.x - mx, P.pos.z - mz);   // face the player
      e.setBody(window.WH_Enemy.makeBody(type));
      if (e.terrainHome) e.pos.y = e.groundY();
      e.root.position.copy(e.pos);
      e.yawFrame.rotation.y = e.yaw;
      home.push(e);                // rm.enemies keyed by active regionId
      if (rm.scene && rm.scene.add) rm.scene.add(e.root);       // parent = scene
      S.party.push(e);
      n++;
    }
    return n;
  }

  function partyOver() {
    S.mode = 'idle';
    S.party = [];
    S.cooldownT = D.cooldownSec;
  }

  function toast(text, seconds) {
    if (D.debugMute) return;       // debugMute suppresses ALL encounter toasts
    if (S.game && S.game.inventoryUI && S.game.inventoryUI.toast) {
      S.game.inventoryUI.toast(text, seconds);
    }
  }

  function tick(dt) {
    if (!E || !S.game || !D) return;
    var dn = S.game.dayNight;

    if (S.mode === 'idle') {
      if (S.cooldownT > 0) S.cooldownT = Math.max(0, S.cooldownT - dt);
      if (dn.phase !== 'night') { S.nightParties = 0; return; }
      if (!gates()) { S.checkT = 0; return; }
      S.checkT += dt;
      if (S.checkT < D.checkSec) return;
      S.checkT = 0;
      // g8: the seat must exist BEFORE anything is reserved (AE1 reserve law)
      var seat = pickSeat();
      if (!seat.ok) return;        // g8 refused: stays idle, nothing reserved
      // roll: weighted walk; debugForce bypasses ONLY the roll
      var t = nightTable();
      var row = null;
      if (D.debugForce) {
        row = t.night[t.night.length - 1];               // deterministic pick
      } else {
        var roll = Math.random();                        // RNG site (tick roll)
        var acc = 0;
        for (var i = 0; i < t.night.length; i++) {
          acc += t.weights[i + 1];
          if (roll < acc) { row = t.night[i]; break; }
        }
        if (!row) row = t.night[t.night.length - 1];     // float tail safety
      }
      S.nightParties++;
      S.mode = 'warn';
      S.warnT = D.warnSec;
      S.seat = seat;
      S.row = row;
      // the warn cue: amber accent on the HUD layer (works screen-closed),
      // fired BEFORE any spawn (AE1 warn-order law)
      toast(D.warnLine, D.warnSec + 0.6);
      return;
    }

    if (S.mode === 'warn') {
      // Dawn during warn: cancel - no spawn, refund the counter, NO cooldown.
      if (dn.phase !== 'night') {
        S.mode = 'idle';
        S.nightParties = 0;
        S.seat = null;
        S.row = null;
        return;
      }
      S.warnT -= dt;
      if (S.warnT > 0) return;
      var n = spawnParty(S.seat, S.row);   // spawn at the LOCKED warn-time seat
      if (n === 0) {               // region list vanished - refund, stay idle
        S.mode = 'idle';
        S.nightParties--;
        S.seat = null;
        S.row = null;
        return;
      }
      S.mode = 'live';
      S.seat = null;
      S.row = null;
      return;
    }

    if (S.mode === 'live') {
      // End when every member is dead (wipe), every member leashed home
      // (fsm 'idle'), or any member left the region list (rebuild / boundary
      // crossing -> end silently). Dawn does NOT interrupt a live party.
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
      if (allDead || allIdle || gone) partyOver();
      return;
    }
  }

  // ---- public surface ----------------------------------------------------------
  window.WH_ENCOUNTERS = {
    init: function (game) {
      // re-bind CONFIG at init: Nicko's retunes land this way too (only
      // WH_CONFIG.encounters fields change; nothing else is read at load)
      CFG = window.WH_CONFIG;
      E = CFG.encounters || null;   // absent block = dormant module, no throw
      D = E ? E.director : null;
      S.game = game;
      S.mode = 'idle';
      S.checkT = 0;
      S.warnT = 0;
      S.party = [];
      S.nightParties = 0;
      S.cooldownT = 0;
      S.seat = null;
      S.row = null;
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
    pickSeat: pickSeat
  };
})();
