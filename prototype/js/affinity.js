// CC-AF1 camp affinity (Nicko MorROWIND order 2026-11-07, io/specs/
// cc-af1-camp-affinity-spec.md) - doc 12's single good<->evil axis on the
// prototype: a DEED-DRIVEN standing score (PROPOSED, Nicko tunes), a
// CHARACTER-tab STANDING readout, the kit camp fire tinting by tier and
// journal lines from the camp folk on tier crossing (QJR-3 topic pattern).
// Pure state + math like leveling.js: no DOM beyond the guarded WH_JOURNAL
// appends. Exposes window.WH_AFF:
//   score()     current integer standing [-100, +100] (0 fresh)
//   tier()      ladder row: first row (desc order) with minScore <= score
//   tierFire()  tier fire hex or null (null = the pool keeps its own colour)
//   deed(id, times)  add CONFIG.affinity.deeds[id] * (times || 1), clamped;
//               unknown id or 0 delta = no-op (false), else true
//   crossed(id) once-map read - a tier crossing never refires in a session
//   capture()/restore(data)  C4 save block (game.js); a missing or garbage
//               block restores fresh: score 0, crossed {}
//   onChange    one call after every deed() that changes the score, fired
//               AFTER the crossing check

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.affinity;
  var CAMP_GOOD = window.WH_CONFIG.journal.topics.campAffinityGood;
  var CAMP_DARK = window.WH_CONFIG.journal.topics.campAffinityDark;

  function freshState() {
    return { score: 0, crossed: {} };
  }

  var st = freshState();

  var M = {
    onChange: null
  };

  function changed() {
    if (M.onChange) M.onChange();
  }

  // append(id, title, body, undefined, source) - the QJR-3 call shape
  // (js/camp.js / js/npc.js pattern): the journal core stays optional.
  function appendTopic(t) {
    var J = window.WH_JOURNAL;
    if (J && window.WH_JOURNAL.append) {
      window.WH_JOURNAL.append(t.id, t.title, t.body, undefined, t.source);
    }
  }

  // Once per tier per lifetime of the save: entering honored the FIRST time
  // appends 'camp-affinity-good', entering feared the FIRST time appends
  // 'camp-affinity-dark'. Sworn tiers add NO topic in v1; the once-map keys
  // are the topic ids, so a later sworn crossing does not refire them and the
  // crossing map records nothing extra. The map NEVER resets on its own -
  // the courts remember. restore() with its fresh map is the only refire path.
  function crossCheck() {
    var s = st.score;
    if (s >= 50 && !st.crossed['camp-affinity-good']) {
      st.crossed['camp-affinity-good'] = true;
      appendTopic(CAMP_GOOD);
    }
    if (s <= -50 && !st.crossed['camp-affinity-dark']) {
      st.crossed['camp-affinity-dark'] = true;
      appendTopic(CAMP_DARK);
    }
  }

  M.score = function () { return st.score; };

  // tier() = first row (desc) with minScore <= s (spec A): the ladder array is
  // typed worst->best for reading, so "first (desc)" = the row with the
  // GREATEST minScore <= s (a first-match over a desc-sorted scan); that is
  // also the exact A3/probe table (49 neutral, 50 honored, 80 sworn-light,
  // -50 feared, -80 sworn-dark). Rows never overlap.
  M.tier = function () {
    var s = st.score, best = null;
    for (var i = 0; i < CFG.ladder.length; i++) {
      var r = CFG.ladder[i];
      if (s >= r.minScore && (!best || r.minScore > best.minScore)) best = r;
    }
    // below the floor (s < -80 can't happen through deed(); restore clamps
    // to +-CFG.clamp = the sworn-dark edge) the bottom band applies
    return best || CFG.ladder[0];
  };

  M.tierFire = function () {
    var t = M.tier();
    return t && t.fire != null ? t.fire : null;
  };

  // deeds[id] * (times || 1), clamped to +-CONFIG.affinity.clamp. Unknown id
  // or delta 0 = a no-op (false, no hook fire). |s| >= 80 is sworn.
  M.deed = function (id, times) {
    var def = CFG.deeds[id];
    if (def === undefined) return false;
    var n = typeof times === 'number' && isFinite(times) ? Math.floor(times) : 1;
    var d = def * n;
    if (d === 0) return false;
    var clamped = Math.max(-CFG.clamp, Math.min(CFG.clamp, st.score + d));
    if (clamped === st.score) return false;
    st.score = clamped;
    crossCheck();
    changed();
    return true;
  };

  M.crossed = function (tierId) {
    return !!st.crossed[tierId];
  };

  M.capture = function () {
    var crossed = {};
    var k;
    for (k in st.crossed) {
      if (Object.prototype.hasOwnProperty.call(st.crossed, k)) crossed[k] = true;
    }
    return { score: st.score, crossed: crossed };
  };

  // Load-safe (leveling.js restore pattern): a missing / malformed block is a
  // fresh 0 / {} - numbers are coerced and the once-map keeps only plain keys
  // mapping to true. Never throws on garbage rows.
  M.restore = function (data) {
    st = freshState();
    var d = (data && typeof data === 'object' && !(data instanceof Array))
      ? data : null;
    if (d) {
      var s = Number(d.score);
      if (isFinite(s)) st.score = Math.max(-CFG.clamp, Math.min(CFG.clamp, Math.floor(s)));
      if (d.crossed && typeof d.crossed === 'object' && !(d.crossed instanceof Array)) {
        Object.keys(d.crossed).forEach(function (k) {
          if (typeof k === 'string' && d.crossed[k] === true) st.crossed[k] = true;
        });
      }
    }
    // no changed(): a restore is not a deed - the readouts render on their own
    // schedule (CONTINUE path rebuilds the column once the panel opens)
  };

  window.WH_AFF = M;
})();
