// whanim2: presentation-only animation; the combat FSM owns every timing edge.
(function () {
  'use strict';

  var CFG = window.WH_CONFIG.animRt;
  var NAMES = {
    idle: 'WH_Idle', walk: 'WH_Walk', run: 'WH_Run',
    attack: 'WH_Attack1', hit: 'WH_Hit', death: 'WH_Death'
  };
  // 10-04 chain clips: CONFIG move id -> per-move player clip. Bodies without
  // the clip (enemies, handAxe moves, older GLBs) use the shared 'attack'.
  // Round D: Mixamo sword-pack attacks baked into combat-sword.glb; thrust
  // slot plays an overhead chop (pack has no stab). A missing WH_SS_* clip
  // falls back to the authored 10-04 clip (MOVE_FALLBACK_NAMES). Rollback:
  // revert MOVE_NAMES values to MOVE_FALLBACK_NAMES (+ CONFIG move timings).
  var MOVE_NAMES = {
    slashR2L: 'WH_SS_SlashR2L',
    slashL2R: 'WH_SS_SlashL2R',
    thrust: 'WH_SS_Overhead'
  };
  var MOVE_FALLBACK_NAMES = {
    slashR2L: 'WH_SlashR2L', slashL2R: 'WH_SlashL2R', thrust: 'WH_Thrust'
  };
  // 10-05 per-body clip-name variants (options.variant). A slot whose override
  // clip is absent from the loaded GLB falls back to the NAMES default, so a
  // GLB regen can never strand a state. moves replaces MOVE_NAMES wholesale.
  // zombie: Mixamo ghoul set; death stays canonical (WH_Death_Zombie ends
  // standing and reads wounded, not dead).
  // bandit: Mixamo axe set on the cape-fixed orc; death canonical, no moves.
  // sword: player Mixamo sword-and-shield locomotion (combat-sword.glb);
  // attack/hit/death canonical, moves IS MOVE_NAMES (same object: identity
  // checks elsewhere treat it as the default chain-move player body).
  var VARIANTS = {
    zombie: {
      names: {
        idle: 'WH_Idle_Zombie', walk: 'WH_Walk_Zombie', run: 'WH_Run_Zombie',
        attack: 'WH_Attack_Zombie', hit: 'WH_Hit_Zombie', death: 'WH_Death'
      },
      moves: {}
    },
    bandit: {
      names: {
        idle: 'WH_Idle_Melee', walk: 'WH_Walk_Melee', run: 'WH_Run_Melee',
        attack: 'WH_Attack_High', hit: 'WH_Hit_Large_L', death: 'WH_Death'
      },
      moves: {}
    },
    sword: {
      names: {
        idle: 'WH_SwordIdle', walk: 'WH_SwordWalk', run: 'WH_SwordRun',
        attack: 'WH_Attack1', hit: 'WH_Hit', death: 'WH_Death'
      },
      moves: MOVE_NAMES
    }
  };

  function CharacterAnim(body, clips, options) {
    var variant = options && options.variant ? VARIANTS[options.variant] : null;
    if (options && options.variant && !variant) {
      console.warn('[WH anim] unknown variant ' + options.variant);
    }
    this.body = body;
    this.clips = clips;
    this.names = {};
    this.moveNames = variant ? variant.moves : MOVE_NAMES;
    this.mixer = new THREE.AnimationMixer(body);
    this.actions = {};
    this.clip = null;
    this.locomotion = 'idle';
    this.hitActive = false;
    this.dead = false;
    this.attackPhase = null;
    this.attackSerial = 0;
    var self = this;
    Object.keys(NAMES).forEach(function (state) {
      var name = variant && variant.names[state] || NAMES[state];
      var clip = THREE.AnimationClip.findByName(clips, name);
      if (!clip && name !== NAMES[state]) {
        console.warn('[WH anim] missing ' + name + ', falling back to ' + NAMES[state]);
        name = NAMES[state];
        clip = THREE.AnimationClip.findByName(clips, name);
      }
      if (!clip) {
        console.warn('[WH anim] missing ' + name);
        return;
      }
      self.names[state] = name;
      var action = self.mixer.clipAction(clip);
      if (state === 'hit' || state === 'attack' || state === 'death') {
        action.setLoop(THREE.LoopOnce, 1);
        action.clampWhenFinished = true;
      }
      self.actions[state] = action;
    });
    Object.keys(this.moveNames).forEach(function (move) {
      var clip = THREE.AnimationClip.findByName(clips, self.moveNames[move]);
      if (!clip && MOVE_FALLBACK_NAMES[move]) {
        clip = THREE.AnimationClip.findByName(clips, MOVE_FALLBACK_NAMES[move]);
        if (clip) {
          console.warn('[WH anim] move ' + move + ' missing ' + self.moveNames[move] +
            ', falling back');
        }
      }
      if (!clip) return;
      var action = self.mixer.clipAction(clip);
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true;
      self.actions[move] = action;
    });
    this.mixer.addEventListener('finished', function (event) {
      if (event.action === self.actions.hit && !self.dead) {
        self.hitActive = false;
        self.transition(self.locomotion, CFG.oneShotFadeSeconds);
      }
    });
    this.transition('idle', 0);
  }

  CharacterAnim.prototype.transition = function (state, seconds, restart) {
    if (!this.actions[state] || this.dead && state !== 'death') return;
    if (this.clip === state && !restart) return;
    var prev = this.actions[this.clip];
    var next = this.actions[state];
    // Interrupting a fade must not leave an older third action contributing
    // pose/weight when the next transition begins.
    var actions = this.actions;
    Object.keys(actions).forEach(function (key) {
      if (actions[key] !== prev && actions[key] !== next) actions[key].stop();
    });
    if (prev && prev !== next) prev.fadeOut(seconds);
    next.stopFading();
    next.reset();
    next.enabled = true;
    next.setEffectiveWeight(1);
    if (seconds) next.fadeIn(seconds);
    next.play();
    this.clip = state;
    // A superseded hit clip fades out disabled and never emits 'finished';
    // release the latch here or setLocomotion stays blocked indefinitely.
    if (state !== 'hit') this.hitActive = false;
  };

  CharacterAnim.prototype.setLocomotion = function (speed, running) {
    if (this.dead) return;
    var state = speed <= 0.01 ? 'idle' : (running ? 'run' : 'walk');
    this.locomotion = state;
    // syncPlayer/syncEnemy only call this after their FSM attack branch ends.
    // A finished attack action remains named 'attack'; transition out of it
    // rather than leaving all clip weights at zero during locomotion.
    if (!this.hitActive) this.transition(state, CFG.crossfadeSeconds);
    if (state === 'walk' || state === 'run') {
      var action = this.actions[state];
      if (action) {
        var cycleMeters = state === 'walk' ? CFG.walkMetersPerCycle : CFG.runMetersPerCycle;
        action.timeScale = speed * action.getClip().duration / cycleMeters;
      }
    }
  };

  CharacterAnim.prototype.hit = function () {
    if (this.dead || !this.actions.hit) return;
    this.hitActive = true;
    this.transition('hit', CFG.oneShotFadeSeconds, true);
  };

  CharacterAnim.prototype.death = function (alreadyDead) {
    if (this.dead || !this.actions.death) return;
    this.dead = true;
    this.hitActive = false;
    this.transition('death', alreadyDead ? 0 : CFG.oneShotFadeSeconds);
    if (alreadyDead) {
      this.actions.death.time = this.actions.death.getClip().duration;
      this.actions.death.paused = true;
    }
  };

  // 10-04: the player clip is phase-mapped like the enemy one - windup /
  // strike / recover each own a clip segment and play over the CONFIG move's
  // durations, so per-move timings (thrust vs slash) drive the clip.
  // moveId picks the per-move chain clip when the body has it.
  CharacterAnim.prototype.playerAttack = function (phase, phaseTime, durations, moveId) {
    var key = this.moveNames[moveId] && this.actions[moveId] ? moveId : 'attack';
    if (this.dead || !this.actions[key]) return;
    // Chained swings sharing a clip stay in it and re-seek (no self-crossfade);
    // a chain step onto another per-move clip crossfades like any one-shot.
    if (this.clip !== key) this.transition(key, CFG.oneShotFadeSeconds, true);
    this.attackPhase = phase;
    // Seeking to the FSM clock also handles chained/restarted attacks without
    // allowing mixer drift or a render hitch to move the damage window.
    this.seekAttack(phase === 'windup' ? 0 : phase === 'strike' ? 1 : 2,
      phaseTime, [durations.windup, durations.strike, durations.recover], key);
  };

  // Shared attack-clip seek: segment 0 windup [0, s), 1 strike/active
  // [s, 2s), 2 recover [2s, end) with s = attackClipStrikeFraction * length.
  // Per-move clips are authored on their CONFIG stage proportions, so their
  // segment edges are the move's own windup / windup+strike fractions.
  CharacterAnim.prototype.seekAttack = function (seg, phaseTime, durations, key) {
    var action = this.actions[key || 'attack'];
    var clip = action.getClip();
    var a, b;
    if (key && key !== 'attack') {
      var total = Math.max(1e-4, durations[0] + durations[1] + durations[2]);
      a = clip.duration * durations[0] / total;
      b = clip.duration * (durations[0] + durations[1]) / total;
    } else {
      a = clip.duration * CFG.attackClipStrikeFraction;
      b = a * 2;
    }
    var part = seg === 0 ? { start: 0, span: a } :
      seg === 1 ? { start: a, span: b - a } :
      { start: b, span: clip.duration - b };
    action.timeScale = part.span / Math.max(1e-4, durations[seg]);
    action.time = Math.min(clip.duration, part.start +
      Math.max(0, phaseTime) * action.timeScale);
  };

  CharacterAnim.prototype.enemyAttack = function (phase, phaseTime, durations) {
    if (this.dead || !this.actions.attack) return;
    if (phase === 'windup' && this.attackPhase !== 'windup') {
      this.transition('attack', CFG.oneShotFadeSeconds, true);
      this.attackSerial++;
    }
    this.attackPhase = phase;
    this.seekAttack(phase === 'windup' ? 0 : phase === 'active' ? 1 : 2,
      phaseTime, [durations.windup, durations.active, durations.recover]);
  };

  CharacterAnim.prototype.syncPlayer = function (player, dt) {
    if (player.state !== 'alive') {
      this.death();
    } else if (player.attacking) {
      var ph = player.getAttackPhase();
      this.playerAttack(ph.stage, ph.t, ph.durations, player.attackMoveId);
    } else {
      this.attackPhase = null;
      this.setLocomotion(player.animMoveSpeed || 0, !!player.sprinting || player.rolling);
    }
    this.update(dt);
  };

  CharacterAnim.prototype.syncEnemy = function (enemy, dt) {
    if (enemy.fsm === 'dead') {
      // deadFall 1 before any death clip ran = corpse restored by a region rebuild
      this.death(enemy.deadFall >= 1);
    } else if (enemy.fsm === 'attack') {
      this.enemyAttack(enemy.attackPhase, enemy.attackPhaseT, enemy.cfg.attackPhase);
    } else {
      this.attackPhase = null;
      this.setLocomotion(enemy.animMoveSpeed || 0,
        (enemy.animMoveSpeed || 0) > enemy.cfg.moveSpeed);
    }
    this.update(dt);
  };

  CharacterAnim.prototype.revive = function () {
    this.mixer.stopAllAction();
    this.dead = false;
    this.hitActive = false;
    this.attackPhase = null;
    this.clip = null;
    this.transition('idle', 0);
    this.mixer.update(0);
  };

  CharacterAnim.prototype.update = function (dt) {
    this.mixer.update(dt);
    if (this.dead && this.actions.death && this.actions.death.paused) {
      this.actions.death.time = this.actions.death.getClip().duration;
    }
  };

  CharacterAnim.prototype.getState = function () {
    var action = this.actions[this.clip];
    var time = action ? action.time : 0;
    var duration = action ? action.getClip().duration : 1;
    var weights = {};
    var self = this;
    Object.keys(this.names).forEach(function (state) {
      var act = self.actions[state];
      weights[self.names[state]] = act && (act.isRunning() ||
        (self.dead && state === 'death' && self.clip === 'death')) ?
        act.getEffectiveWeight() : 0;
    });
    Object.keys(this.moveNames).forEach(function (move) {
      var act = self.actions[move];
      if (act) weights[self.moveNames[move]] = act.isRunning() ? act.getEffectiveWeight() : 0;
    });
    return { clip: this.names[this.clip] || this.moveNames[this.clip] || null, time: time,
      phase: duration ? time / duration : 0, weights: weights,
      timeScale: action ? action.timeScale : 0,
      locomotion: this.names[this.locomotion], attackSerial: this.attackSerial };
  };

  CharacterAnim.VARIANTS = VARIANTS;
  window.WH_CharacterAnim = CharacterAnim;
})();
