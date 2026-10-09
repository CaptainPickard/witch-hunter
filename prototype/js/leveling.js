// Witch Hunter prototype - leveling (L1, io/missions/2026-10-07-cc-l1-leveling.md).
// Layer 1 (doc 07): XP -> character level -> CONFIG.leveling.pointsPerLevel
// stat points per level -> the nine stats. Layer 2 (doc 18): three skill
// lines rank by use with per-rank primary passives (no tier-up menus).
// LEVEL DOES NOT SCALE POWER: nothing reads the level number except the
// point grant; the stats and ranks are the power. All numbers from
// CONFIG.leveling (PROPOSED, Nicko tunes). Level 1 with no points spent and
// rank 1 lines = every multiplier 1 / every bonus 0 (today's numbers).
// Pure state + math: no DOM, no player / enemy imports. game.js feeds the
// events in (kills, gathers, cooks, hits, blocks, casts) and reads the
// numbers out (applyBuffStats, crit, ward, speed, spell power, stack caps).
// Exposes window.WH_LEVEL:
//   awardXP(source, amount)   amount defaults to CONFIG.leveling.xpSources[source];
//                             returns the levels gained (chains past several)
//   discover(kind, id)        first-of-kind XP ('discover_' + kind), once per id
//   xpForNext(level)          XP from level to level + 1
//   statPoints(key) / statBonus(key) / statTotal(key) / focusBonus()
//   spend(key) / recoup(key) / canRecoup(key) / commit()   CHARACTER tab +/-
//   useSkill(line, kind)      rank XP per use (CONFIG skillLines perUse)
//   skillRank(line) / skillProgress(line) / skillPassive(line, effect) /
//   skillMult(line, effect)
//   capture() / restore(data) / reset()   C4 save block (save.js)
//   onLevelUp(level, pts) / onRankUp(line, rank) / onChange()  hooks (game.js)

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var L = CFG.leveling;

  function num(v, fallback) {
    return typeof v === 'number' && isFinite(v) ? v : fallback;
  }

  function freshState() {
    var alloc = {}, committed = {}, ranks = {};
    L.stats.forEach(function (k) { alloc[k] = 0; committed[k] = 0; });
    Object.keys(L.skillLines).forEach(function (id) { ranks[id] = { rank: 1, xp: 0 }; });
    return { xp: 0, level: 1, pendingPts: 0, alloc: alloc, committed: committed,
      ranks: ranks, discovered: {} };
  }

  var st = freshState();

  var M = {
    onLevelUp: null,
    onRankUp: null,
    onChange: null
  };

  function changed() {
    if (M.onChange) M.onChange();
  }

  // ---- Layer 1: XP + level --------------------------------------------------------

  // round(base * level ^ exp): 100 / 283 / 520 / 800 ... (CONFIG.leveling.xpCurve)
  M.xpForNext = function (level) {
    return Math.max(1, Math.round(L.xpCurve.base * Math.pow(Math.max(1, level), L.xpCurve.exp)));
  };

  M.awardXP = function (source, amount) {
    var n = typeof amount === 'number' ? amount : num(L.xpSources[source], 0);
    if (!(n > 0)) return 0;
    st.xp += n;
    var gained = 0;
    while (st.level < L.maxLevel && st.xp >= M.xpForNext(st.level)) {
      st.xp -= M.xpForNext(st.level);
      st.level++;
      st.pendingPts += L.pointsPerLevel;
      gained++;
      if (M.onLevelUp) M.onLevelUp(st.level, L.pointsPerLevel);
    }
    changed();
    return gained;
  };

  // First-of-kind discovery: one award per (kind, id) per character.
  M.discover = function (kind, id, silent) {
    var key = kind + ':' + id;
    if (st.discovered[key]) return false;
    st.discovered[key] = true;
    if (!silent) M.awardXP('discover_' + kind);
    return true;
  };

  M.isDiscovered = function (kind, id) {
    return !!st.discovered[kind + ':' + id];
  };

  M.level = function () { return st.level; };
  M.xp = function () { return st.xp; };
  M.pendingPts = function () { return st.pendingPts; };
  M.xpFrac = function () {
    return st.level >= L.maxLevel ? 1 : Math.min(1, st.xp / M.xpForNext(st.level));
  };

  // ---- the nine stats ---------------------------------------------------------------

  M.statPoints = function (key) { return st.alloc[key] || 0; };

  // points * perPoint, clamped to the curve cap (null = uncapped)
  M.statBonus = function (key) {
    var c = L.statCurves[key];
    if (!c) return 0;
    var v = M.statPoints(key) * c.perPoint;
    return c.cap != null ? Math.min(c.cap, v) : v;
  };

  // base (today's number) + bonus. Pools read CONFIG.player live; the
  // multipliers start at 1, the chances / reductions at 0.
  var STAT_BASE = {
    health: function () { return CFG.player.hpMax; },
    stamina: function () { return CFG.player.staminaMax; },
    focus: function () { return CFG.player.focusMax; },
    speed: function () { return 1; },
    precision: function () { return 0; },
    ward: function () { return 0; },
    wisdom: function () { return 1; },
    carry: function () { return 1; },
    luck: function () { return 0; }
  };

  M.statTotal = function (key) {
    return (STAT_BASE[key] ? STAT_BASE[key]() : 0) + M.statBonus(key);
  };

  // L1.1 (Nicko 10-07): Wisdom no longer adds focus (focus = Focus stat's
  // job; Wisdom bought magic damage + magic defense instead; R-64.1 10-09
  // swapped that defense half for magic regen). Kept for the C4 restore
  // path; returns just the Focus stat's share (0 extra).
  M.focusBonus = function () {
    return M.statBonus('focus');
  };

  // R-64.1 (Nicko 10-09): focus regen multiplier = 1 + magicRegenPerPoint
  // (0.05) * Wisdom points, uncapped. player.js regen = focusRegenPerSec *
  // this * other mults (blocking 0.5): 0 wis 2.0/s, 10 wis 3.0/s.
  M.magicRegenMult = function () {
    return 1 + M.statPoints('wisdom') * (L.statCurves.wisdom.magicRegenPerPoint || 0);
  };

  // L1.1 magic defense was Wisdom points * magicDefensePerPoint. R-64.3
  // (Nicko 10-09): rehomed to an ITEM stat (CONFIG.equip.itemStats) - the
  // equipped-gear total, item-stat totalizing mirrors statTotal semantics
  // (sum of every source, 0 when none). Empty gear / hand = 0. INERT v1:
  // the future enemy-caster damage branch reads this (not built; no enemy
  // casts spells). Reads the player via WH_GAME (no player import here).
  M.magicDefense = function () {
    var g = window.WH_GAME, p = g && g.player;
    if (!p || !p.equippedItems) return 0;
    return p.equippedItems().reduce(function (sum, item) {
      return sum + (item.stats && item.stats.magicDefense || 0);
    }, 0);
  };

  M.spend = function (key) {
    if (st.pendingPts <= 0 || !(key in st.alloc)) return false;
    st.alloc[key]++;
    st.pendingPts--;
    changed();
    return true;
  };

  // '-' only takes back points spent since the last commit (the CHARACTER
  // screen closing commits): no free respec of earlier choices.
  M.canRecoup = function (key) {
    return (st.alloc[key] || 0) > (st.committed[key] || 0);
  };

  M.recoup = function (key) {
    if (!M.canRecoup(key)) return false;
    st.alloc[key]--;
    st.pendingPts++;
    changed();
    return true;
  };

  M.commit = function () {
    L.stats.forEach(function (k) { st.committed[k] = st.alloc[k]; });
  };

  // ---- Layer 2: skill lines by use --------------------------------------------------

  // doc 18 shape: full speed to slowFrom, then 1 + (rank - slowFrom) / slowSpan
  M.rankXpForNext = function (rank) {
    var R = L.rankCurve;
    var slow = rank < R.slowFrom ? 1 : 1 + (rank - R.slowFrom) / R.slowSpan;
    return Math.max(1, Math.round(R.perRank * slow));
  };

  M.useSkill = function (line, kind) {
    var def = L.skillLines[line], r = st.ranks[line];
    if (!def || !r) return 0;
    var n = num(def.perUse[kind], 0);
    if (!(n > 0) || r.rank >= L.rankCurve.maxRank) return 0;
    r.xp += n;
    var gained = 0;
    while (r.rank < L.rankCurve.maxRank && r.xp >= M.rankXpForNext(r.rank)) {
      r.xp -= M.rankXpForNext(r.rank);
      r.rank++;
      gained++;
      if (M.onRankUp) M.onRankUp(line, r.rank);
    }
    if (r.rank >= L.rankCurve.maxRank) r.xp = 0;
    changed();
    return gained;
  };

  M.skillRank = function (line) {
    return st.ranks[line] ? st.ranks[line].rank : 1;
  };

  M.skillProgress = function (line) {
    var r = st.ranks[line];
    if (!r || r.rank >= L.rankCurve.maxRank) return 1;
    return Math.min(1, r.xp / M.rankXpForNext(r.rank));
  };

  // (rank - 1) * perRank clamped to +-max: signed (staminaCost -0.04 = 4% cheaper)
  M.skillPassive = function (line, effect) {
    var def = L.skillLines[line];
    var p = def && def.passives[effect];
    if (!p) return 0;
    var v = (M.skillRank(line) - 1) * p.perRank;
    return Math.max(-p.max, Math.min(p.max, v));
  };

  M.skillMult = function (line, effect) {
    return 1 + M.skillPassive(line, effect);
  };

  // CONFIG.leveling.spellLines: the line a spell trains (null = none)
  M.spellLine = function (spellId) {
    return (L.spellLines && L.spellLines[spellId]) || null;
  };

  // ---- C4 save block ----------------------------------------------------------------

  M.capture = function () {
    var ranks = {};
    Object.keys(st.ranks).forEach(function (id) {
      ranks[id] = { rank: st.ranks[id].rank, xp: st.ranks[id].xp };
    });
    var alloc = {};
    L.stats.forEach(function (k) { alloc[k] = st.alloc[k]; });
    return { xp: st.xp, level: st.level, pendingPts: st.pendingPts, alloc: alloc,
      ranks: ranks, discovered: Object.keys(st.discovered) };
  };

  // Load-safe: a missing block (pre-L1 save) or bad fields = fresh defaults.
  // Restored points count as committed (no recoup of loaded choices).
  M.restore = function (data) {
    st = freshState();
    var d = data && typeof data === 'object' ? data : null;
    if (d) {
      st.level = Math.max(1, Math.min(L.maxLevel, Math.floor(num(d.level, 1))));
      st.xp = Math.max(0, num(d.xp, 0));
      st.pendingPts = Math.max(0, Math.floor(num(d.pendingPts, 0)));
      var a = d.alloc || {};
      L.stats.forEach(function (k) {
        st.alloc[k] = Math.max(0, Math.floor(num(a[k], 0)));
        st.committed[k] = st.alloc[k];
      });
      var rk = d.ranks || {};
      Object.keys(st.ranks).forEach(function (id) {
        var r = rk[id];
        if (!r) return;
        st.ranks[id].rank = Math.max(1, Math.min(L.rankCurve.maxRank, Math.floor(num(r.rank, 1))));
        st.ranks[id].xp = Math.max(0, num(r.xp, 0));
      });
      if (Array.isArray(d.discovered)) {
        d.discovered.forEach(function (k) { if (typeof k === 'string') st.discovered[k] = true; });
      }
    }
    changed();
  };

  M.reset = function () { M.restore(null); };

  window.WH_LEVEL = M;
})();
