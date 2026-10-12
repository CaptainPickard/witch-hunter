// whanim2: presentation-only animation; the combat FSM owns every timing edge.
(function () {
  'use strict';

  var CFG = window.WH_CONFIG.animRt;
  function BLK_ANIM() { return window.WH_CONFIG.block.blockAnim; }
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
  // DAG (2026-10-09): the dagger chain's clips (combat-dagger.glb, merged
  // into the player clip list by player.setBody). Only the dagger moveset
  // emits these move ids, so they play iff the dagger is the wielded weapon;
  // bodies without the clips create no action (no fallback, unchanged).
  var MOVE_NAMES = {
    slashR2L: 'WH_SS_SlashR2L',
    slashL2R: 'WH_SS_SlashL2R',
    thrust: 'WH_SS_Overhead',
    dagSlashR2L: 'WH_DagSlashR2L',
    dagSlashL2R: 'WH_DagSlashL2R',
    dagSlashR2Lb: 'WH_DagSlashR2Lb'
  };
  var MOVE_FALLBACK_NAMES = {
    slashR2L: 'WH_SlashR2L', slashL2R: 'WH_SlashL2R', thrust: 'WH_Thrust'
  };
  // Order D shield/block clips (player body only; NOT sword moves). All are
  // LoopOnce + clamp: raise/impact/swipe all END on the same guard frame, so
  // whichever one ran last, clamped, IS the block hold pose. The stagger ends
  // in a crouch the guard-break stun sits in.
  var CLIP_NAMES = {
    shieldRaise: 'WH_ShieldRaise', shieldImpact: 'WH_ShieldImpact',
    parrySwipe: 'WH_ParrySwipe', guardBreak: 'WH_GuardBreakStagger'
  };
  var SHIELD_HOLD = { shieldRaise: true, shieldImpact: true, parrySwipe: true };
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
    },
    // CC-C5: the rigged wolf (wolf.rigged.pixelated.glb, WH_Wolf_* family).
    // Patrol walks, chase / regroup runs, the lunge bite is the attack clip.
    // attackSegs = the bite's own segment edges (clip fractions, measured
    // from the GLB keys): rear shift (jaw opens, spine back) 0..0.24 s, the
    // snap (jaw shut, neck forward) 0.24..0.39 s, recover to 0.70 s.
    wolf: {
      names: {
        idle: 'WH_Wolf_Idle', walk: 'WH_Wolf_Walk', run: 'WH_Wolf_Run',
        attack: 'WH_Wolf_Attack1', hit: 'WH_Wolf_Hit', death: 'WH_Wolf_Death'
      },
      moves: {},
      attackSegs: [0.24 / 0.7, 0.39 / 0.7]
    }
  };
  // MAGANIM (doc 65 R-65.3..R-65.5): player body MODE (setVariant), apart
  // from the per-body variant above. 'warrior' = no swaps. 'caster' swaps
  // idle / locomotion (+ backward split) / reactions / death to the WH_Mag_*
  // set; attack chain, roll, turns, Jump, Idle01 are never swapped. A mode
  // key whose clip is missing resolves through MODE_FALLBACK down to the
  // universal state, so a variant clip failure never bricks presentation.
  var MODE_NAMES = {
    magIdle: 'WH_Mag_Idle02', magWalk: 'WH_Mag_WalkF', magWalkBack: 'WH_Mag_WalkB',
    magRun: 'WH_Mag_RunF', magRunBack: 'WH_Mag_RunB', magHitSmall: 'WH_Mag_ReactSmall',
    magHitLarge: 'WH_Mag_ReactLarge', magDeath: 'WH_Mag_DeathBack',
    Cast1H: 'WH_Mag_Cast1H', Cast2H: 'WH_Mag_Cast2H',
    Cast1H_L: 'WH_Mag_Cast1H_L'       // MAGICLASS: mirrored Cast1H, off (left) hand casts
  };
  var MODES = {
    warrior: {},
    caster: {
      idle: 'magIdle', walk: 'magWalk', walkBack: 'magWalkBack', run: 'magRun',
      runBack: 'magRunBack', hitSmall: 'magHitSmall', hitLarge: 'magHitLarge',
      death: 'magDeath'
    }
  };
  var MODE_FALLBACK = { walkBack: 'walk', runBack: 'run', hitSmall: 'hit', hitLarge: 'hit' };
  var LOOPED = { magIdle: true, magWalk: true, magWalkBack: true, magRun: true, magRunBack: true };
  var HIT_KEYS = { hit: true, magHitSmall: true, magHitLarge: true };
  var DEATH_KEYS = { death: true, magDeath: true };
  var CAST_SHOTS = { Cast1H: true, Cast2H: true, Cast1H_L: true };
  var CAST_1H = { Cast1H: true, Cast1H_L: true };   // MAGICLASS: the 1H shots (either hand)
  function CASTER() { return window.WH_CONFIG.assets.caster; }
  // CAST1H2: a clip's tracks whose node (track name up to the first '.') is in
  // `nodes` - GLTFLoader track names are '<NodeName>.<property>', node names
  // unique, so this splits a dense bake exactly at the waist.
  function nodeTracks(clip, nodes) {
    return clip.tracks.filter(function (track) {
      return nodes.indexOf(track.name.split('.')[0]) !== -1;
    });
  }
  // CAST1H2: the legs' cycle rate under the upper-body shot - the same law
  // setLocomotion applies to the full walk / run action (idle stays 1).
  function legScale(action, speed, running) {
    if (speed <= 0.01) return 1;
    return speed * action.getClip().duration /
      (running ? CFG.runMetersPerCycle : CFG.walkMetersPerCycle);
  }

  function CharacterAnim(body, clips, options) {
    var variant = options && options.variant ? VARIANTS[options.variant] : null;
    if (options && options.variant && !variant) {
      console.warn('[WH anim] unknown variant ' + options.variant);
    }
    this.body = body;
    this.clips = clips;
    this.names = {};
    this.moveNames = variant ? variant.moves : MOVE_NAMES;
    this.attackSegs = variant && variant.attackSegs || null;   // CC-C5 (wolf only)
    this.mixer = new THREE.AnimationMixer(body);
    this.actions = {};
    this.clip = null;
    this.locomotion = 'idle';
    this.hitActive = false;
    this.dead = false;
    this.attackPhase = null;
    this.attackSerial = 0;
    this.mode = 'warrior';
    this.modeNames = {};
    // CAST1H2 (R10/R11): Cast1H plays torso-only over lower-body variants of
    // the locomotion (lazy, keyed by '<clip>__lower'); lowerActive = the one
    // carrying the legs under the running shot, null otherwise.
    this.castUpper = false;
    this.lowerActions = {};
    this.lowerActive = null;
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
    Object.keys(CLIP_NAMES).forEach(function (key) {
      var clip = THREE.AnimationClip.findByName(clips, CLIP_NAMES[key]);
      if (!clip) return;
      var action = self.mixer.clipAction(clip);
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true;
      self.actions[key] = action;
    });
    // MAGANIM: mode + cast-shot clips (bodies without them build nothing)
    Object.keys(MODE_NAMES).forEach(function (key) {
      var clip = THREE.AnimationClip.findByName(clips, MODE_NAMES[key]);
      if (!clip) return;
      // CAST1H2 (R10): the 1H shot's action runs the upper-node tracks only
      // (same duration); this.clips keeps the full clip untouched.
      if (CAST_1H[key] && CASTER().castUpperBody) {
        clip = new THREE.AnimationClip(clip.name + '__upper', clip.duration,
          nodeTracks(clip, CASTER().castUpperNodes));
        self.castUpper = true;
      }
      var action = self.mixer.clipAction(clip);
      if (!LOOPED[key]) {
        action.setLoop(THREE.LoopOnce, 1);
        action.clampWhenFinished = true;
      }
      self.actions[key] = action;
      self.modeNames[key] = MODE_NAMES[key];
    });
    this.mixer.addEventListener('finished', function (event) {
      if ((event.action === self.actions.hit || event.action === self.actions.magHitSmall ||
           event.action === self.actions.magHitLarge) && !self.dead) {
        self.hitActive = false;
        self.transition(self.locomotion, CFG.oneShotFadeSeconds);
      }
    });
    this.transition('idle', 0);
  }

  CharacterAnim.prototype.transition = function (state, seconds, restart) {
    if (!this.actions[state] || this.dead && !DEATH_KEYS[state]) return;
    if (this.clip === state && !restart) return;
    // Leaving 'hit' for any other clip ends the hit reaction. An interrupted
    // (faded / stopped) hit action never fires the mixer 'finished' event, so
    // hitActive would latch and setLocomotion would never transition again.
    if (!HIT_KEYS[state]) this.hitActive = false;
    var prev = this.actions[this.clip];
    var next = this.actions[state];
    // Interrupting a fade must not leave an older third action contributing
    // pose/weight when the next transition begins.
    var actions = this.actions;
    Object.keys(actions).forEach(function (key) {
      if (actions[key] !== prev && actions[key] !== next) actions[key].stop();
    });
    // CAST1H2 (R14): any state change ends the upper-body shot's legs. The
    // lower variants live outside this.actions, so the loop above never sees
    // them: stale ones stop, the live one fades out with prev (a hard stop
    // would drop the legs toward the bind pose under the fade-in).
    var lowers = this.lowerActions;
    var legs = this.lowerActive ? lowers[this.lowerActive] : null;
    Object.keys(lowers).forEach(function (name) {
      if (lowers[name] !== legs) lowers[name].stop();
    });
    if (prev && prev !== next) prev.fadeOut(seconds);
    next.stopFading();
    next.reset();
    next.enabled = true;
    next.setEffectiveWeight(1);
    if (seconds) next.fadeIn(seconds);
    next.play();
    if (legs) {
      // back to the locomotion the legs were running: keep their phase
      if (legs.getClip().name === next.getClip().name + '__lower') next.time = legs.time;
      if (seconds) legs.fadeOut(seconds); else legs.stop();
      this.lowerActive = null;
    }
    this.clip = state;
    // A superseded hit clip fades out disabled and never emits 'finished';
    // release the latch here or setLocomotion stays blocked indefinitely.
    if (!HIT_KEYS[state]) this.hitActive = false;
  };

  // MAGANIM: 'warrior' | 'caster' (player.js evaluates it on hand changes).
  // Only stores the mode: the next sync frame resolves every clip through it
  // and crossfades via transition(), so nothing is latched here.
  CharacterAnim.prototype.setVariant = function (mode) {
    this.mode = MODES[mode] ? mode : 'warrior';
  };

  // Universal state ('idle', 'walkBack', 'hitLarge', 'death', ...) -> the
  // action key this mode plays. Missing variant clip -> MODE_FALLBACK chain
  // -> the universal state (warrior: walkBack -> walk, hitSmall -> hit).
  CharacterAnim.prototype.resolve = function (state) {
    var key = MODES[this.mode][state];
    if (key && this.actions[key]) return key;
    return MODE_FALLBACK[state] ? this.resolve(MODE_FALLBACK[state]) : state;
  };

  CharacterAnim.prototype.locomotionKey = function (speed, running, backward) {
    var base = speed <= 0.01 ? 'idle' : (running ? 'run' : 'walk');
    return this.resolve(backward && base !== 'idle' ? base + 'Back' : base);
  };

  CharacterAnim.prototype.setLocomotion = function (speed, running, backward) {
    if (this.dead) return;
    var state = this.locomotionKey(speed, running, backward);
    var base = speed <= 0.01 ? 'idle' : (running ? 'run' : 'walk');
    this.locomotion = state;
    // syncPlayer/syncEnemy only call this after their FSM attack branch ends.
    // A finished attack action remains named 'attack'; transition out of it
    // rather than leaving all clip weights at zero during locomotion.
    if (!this.hitActive) this.transition(state, CFG.crossfadeSeconds);
    if (base === 'walk' || base === 'run') {
      var action = this.actions[state];
      if (action) {
        var cycleMeters = base === 'walk' ? CFG.walkMetersPerCycle : CFG.runMetersPerCycle;
        action.timeScale = speed * action.getClip().duration / cycleMeters;
      }
    }
  };

  // MAGANIM: large = the player's big-hit cut (caster ReactLarge); warrior
  // and enemies resolve both sizes to 'hit'.
  CharacterAnim.prototype.hit = function (large) {
    var key = this.resolve(large ? 'hitLarge' : 'hitSmall');
    if (this.dead || !this.actions[key]) return;
    this.hitActive = true;
    this.transition(key, CFG.oneShotFadeSeconds, true);
  };

  CharacterAnim.prototype.death = function (alreadyDead) {
    var key = this.resolve('death');
    if (this.dead || !this.actions[key]) return;
    this.dead = true;
    this.hitActive = false;
    this.transition(key, alreadyDead ? 0 : CFG.oneShotFadeSeconds);
    if (alreadyDead) {
      this.actions[key].time = this.actions[key].getClip().duration;
      this.actions[key].paused = true;
    }
  };

  // MAGANIM (R-65.5): presentation-only cast one-shot ('Cast1H' | 'Cast1H_L' | 'Cast2H')
  // from player.tryCast. Repeat guard: the same shot still running is not
  // re-triggered. The attack chain owns the body while a swing runs (a
  // windup weave cast shows no shot). Completion clamps; the next sync frame
  // crossfades back to locomotion.
  // CAST1H: castShotKey = the shot this call actually started (or that is
  // still running), null when none plays - player.tryCast gates the 1H
  // fire-at-peak windup on it. Cast1H plays at castShotSpeed, set once per
  // start and never reset (transition() stops it on the next state change);
  // Cast2H keeps timeScale 1.
  // CAST1H2: with castUpperBody the Cast1H shot is torso-only (castOverlay);
  // the refusal paths above stay round 1 and never touch the locomotion.
  CharacterAnim.prototype.castShot = function (shot) {
    var action = CAST_SHOTS[shot] ? this.actions[shot] : null;
    if (this.dead || this.attackPhase || !action) { this.castShotKey = null; return; }
    if (this.clip === shot && action.isRunning()) { this.castShotKey = shot; return; }
    if (CAST_1H[shot] && this.castUpper) { this.castOverlay(action, shot); return; }
    this.transition(shot, CFG.oneShotFadeSeconds, true);
    if (this.clip !== shot) { this.castShotKey = null; return; }
    if (CAST_1H[shot]) action.timeScale = CASTER().castShotSpeed;
    this.castShotKey = shot;
  };

  // MAGANIM: the cast's lifecycle owner (fizzle / hand change) ends a running
  // shot back to the state anim. No-op when no shot is on.
  CharacterAnim.prototype.endCastShot = function () {
    this.castShotKey = null;
    if (CAST_SHOTS[this.clip]) this.transition(this.locomotion, CFG.crossfadeSeconds);
  };

  CharacterAnim.prototype.castShotRunning = function () {
    return !!(CAST_SHOTS[this.clip] && this.actions[this.clip].isRunning());
  };

  // CAST1H2 (R11): locomotion action key -> its lower-body variant (tracks of
  // castLowerNodes only, loops like the full clip), built on first use.
  CharacterAnim.prototype.lowerAction = function (key) {
    var full = this.actions[key];
    if (!full) return null;
    var clip = full.getClip();
    var name = clip.name + '__lower';
    if (!this.lowerActions[name]) {
      this.lowerActions[name] = this.mixer.clipAction(new THREE.AnimationClip(name,
        clip.duration, nodeTracks(clip, CASTER().castLowerNodes)));
    }
    return this.lowerActions[name];
  };

  // CAST1H2: start `legs` phase-continuous with `src` (the full locomotion or
  // the lower variant it takes over from); fade 0 = instant full weight.
  function startLegs(legs, src, fade) {
    legs.stopFading();
    legs.reset();
    legs.enabled = true;
    legs.setEffectiveWeight(1);
    if (src) legs.time = src.time % legs.getClip().duration;
    if (fade) legs.fadeIn(fade);
    legs.play();
  }

  // CAST1H2 (R12): the Cast1H shot as an upper-body overlay, without
  // transition(): the legs keep the current locomotion on its lower variant
  // while the torso-only shot fades in. Same lifecycle as round 1 (clip =
  // 'Cast1H', castShotKey, clamp hold, exit through transition()).
  // MAGICLASS: shot = 'Cast1H' | 'Cast1H_L' (the mirrored off-hand shot).
  CharacterAnim.prototype.castOverlay = function (action, shot) {
    shot = shot || 'Cast1H';
    var fade = CFG.oneShotFadeSeconds;
    var key = this.resolve(this.locomotion);
    var full = this.actions[key];
    var legs = this.lowerAction(key);
    if (!legs) { this.castShotKey = null; return; }
    var prev = this.actions[this.clip];
    var held = this.lowerActive ? this.lowerActions[this.lowerActive] : null;
    // every other action stops (hit / shield singles, stale lower variants);
    // the pose being left fades out under the shot like a transition() prev
    var actions = this.actions;
    var lowers = this.lowerActions;
    Object.keys(actions).forEach(function (k) {
      if (actions[k] !== prev && actions[k] !== action) actions[k].stop();
    });
    Object.keys(lowers).forEach(function (n) {
      if (lowers[n] !== held) lowers[n].stop();
    });
    if (prev && prev !== action) prev.fadeOut(fade);
    if (legs !== held) {
      // off the full locomotion: identical leg tracks at the same phase, so
      // the lower variant takes the legs at full weight (no pop) while the
      // full action's arms fade out under the shot's
      var src = held || (prev === full ? full : null);
      startLegs(legs, src, src === full ? 0 : fade);
      if (held) held.fadeOut(fade);
    }
    legs.timeScale = full.timeScale;
    action.stopFading();
    action.reset();
    action.enabled = true;
    action.setEffectiveWeight(1);
    action.fadeIn(fade);
    action.play();
    action.timeScale = CASTER().castShotSpeed;
    this.hitActive = false;
    this.clip = shot;
    this.castShotKey = shot;
    this.lowerActive = legs.getClip().name;
  };

  // CAST1H2 (R13): under the overlay shot the legs follow the movement - a
  // start / stop / direction change crossfades onto that locomotion's lower
  // variant; the cycle rate tracks the speed like setLocomotion's.
  CharacterAnim.prototype.syncCastLegs = function (player) {
    var legs = this.lowerAction(this.resolve(this.locomotion));
    var held = this.lowerActions[this.lowerActive];
    if (!legs) return;
    if (legs !== held) {
      startLegs(legs, held, CFG.crossfadeSeconds);
      held.fadeOut(CFG.crossfadeSeconds);
      this.lowerActive = legs.getClip().name;
    }
    legs.timeScale = legScale(legs, player.animMoveSpeed || 0, !!player.sprinting);
  };

  // MAGANIM backward split: the existing roll-basis signal (player.moveDirWorld,
  // written by the walk block) against the body facing (player.yaw). Only a
  // lock-on holds the facing off the move dir; unlocked, the body turns into
  // the move dir (720 deg/s), so a reversal would only flash the Back clip.
  function movingBackward(player) {
    var d = player.moveDirWorld;
    return !!(d && player.lockTarget && !player.rolling &&
      d.x * Math.sin(player.yaw) + d.z * Math.cos(player.yaw) < CASTER().backwardDot);
  }

  // Order D: blocked hit / landed parry one-shots. Each call is one NEW
  // resolved enemy hit, so it restarts the clip (from guard back to guard).
  CharacterAnim.prototype.shieldImpact = function () {
    if (this.dead || !this.actions.shieldImpact) return;
    this.transition('shieldImpact', BLK_ANIM().impactCrossfadeSec, true);
  };

  CharacterAnim.prototype.shieldParry = function () {
    if (this.dead || !this.actions.parrySwipe) return;
    this.transition('parrySwipe', BLK_ANIM().parryCrossfadeSec, true);
  };

  // Order D state-driven block presentation (called from syncPlayer only when
  // the player is alive and not attacking). Returns true when it owns the
  // pose this frame; false hands over to setLocomotion. No latched flags:
  // every decision reads player state + this.clip each frame, and leaving
  // goes through transition() like any other clip change.
  CharacterAnim.prototype.syncBlock = function (player) {
    var cfg = BLK_ANIM();
    if (player.guardBroken && this.actions.guardBreak) {
      // stagger plays once and clamps on its crouch for the rest of the stun
      this.transition('guardBreak', cfg.guardBreakCrossfadeSec);
      return true;
    }
    if (player.rolling) return false;          // roll wins (it also ends the block)
    if (player.blocking && this.actions.shieldRaise) {
      // a real (unblocked, e.g. from behind) hit reaction finishes first
      if (this.hitActive) return true;
      if (!SHIELD_HOLD[this.clip]) this.transition('shieldRaise', cfg.raiseCrossfadeSec);
      return true;
    }
    // the parry branch ends the block (mechanics); the swipe still finishes
    if (this.clip === 'parrySwipe' && this.actions.parrySwipe.isRunning()) return true;
    return false;
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
    } else if (this.attackSegs) {
      a = clip.duration * this.attackSegs[0];
      b = clip.duration * this.attackSegs[1];
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
      // MAGANIM: a running cast shot holds the pose like the parry swipe
      if (this.syncBlock(player) || this.castShotRunning()) {
        // keep the locomotion state current so the exit crossfade targets it
        this.locomotion = this.locomotionKey(player.animMoveSpeed || 0,
          !!player.sprinting, movingBackward(player));
        // CAST1H2: an overlay shot's legs keep walking (no state re-transition)
        if (this.lowerActive) this.syncCastLegs(player);
      } else {
        this.setLocomotion(player.animMoveSpeed || 0, !!player.sprinting || player.rolling,
          movingBackward(player));
      }
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
    this.transition(this.resolve('idle'), 0);
    this.mixer.update(0);
  };

  CharacterAnim.prototype.update = function (dt) {
    this.mixer.update(dt);
    // dead = the clip is the death key death() played (transition refuses
    // every other clip once dead)
    var death = this.dead && DEATH_KEYS[this.clip] ? this.actions[this.clip] : null;
    if (death && death.paused) {
      death.time = death.getClip().duration;
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
    Object.keys(CLIP_NAMES).forEach(function (key) {
      var act = self.actions[key];
      // a clamped (finished) shield clip still holds the pose at full weight
      if (act) weights[CLIP_NAMES[key]] = act.enabled && self.clip === key ?
        act.getEffectiveWeight() : (act.isRunning() ? act.getEffectiveWeight() : 0);
    });
    // MAGANIM: mode / cast-shot weights in caster mode, or while one is the clip
    Object.keys(this.modeNames).forEach(function (key) {
      if (self.mode !== 'caster' && self.clip !== key) return;
      var act = self.actions[key];
      // a clamped death / cast shot still holds the pose while it is the clip
      weights[self.modeNames[key]] = act.isRunning() ||
        self.clip === key && (self.dead || CAST_SHOTS[key]) ? act.getEffectiveWeight() : 0;
    });
    return { clip: this.names[this.clip] || this.moveNames[this.clip] ||
      (this.moveNames === MOVE_NAMES ? CLIP_NAMES[this.clip] : null) ||
      this.modeNames[this.clip] || null,
      time: time,
      phase: duration ? time / duration : 0, weights: weights,
      timeScale: action ? action.timeScale : 0,
      locomotion: this.names[this.locomotion] || this.modeNames[this.locomotion],
      mode: this.mode, attackSerial: this.attackSerial };
  };

  CharacterAnim.VARIANTS = VARIANTS;
  window.WH_CharacterAnim = CharacterAnim;

  // ---- CC-C7 RIGID_CLIPS: placeholder clip set for UNRIGGED bodies -----------
  // The rot mother / rot spawn GLBs ship without a skeleton, so no
  // AnimationClip can drive them. V1 placeholder = the bandit 6-clip pattern
  // (idle / walk / attack / hit / death + 1 spare) authored as procedural
  // rigid poses on the body holder; a real rig round replaces this table.
  // Presentation-only like CharacterAnim: the enemy FSM owns every timing
  // edge (attack = the windup / active / recover phase fractions). clipScale
  // = playback rate of the free-running clips (idle / walk / spare); 'death'
  // is the existing rigid fall in enemy.js updateDeathVisual (pose() null).
  // A null name = the body has no such clip (rot spawn: no hit flinch).
  // Pose: rotX (+ = pitch forward, facing +Z), rotZ roll, rotY yaw wobble,
  // swayX lateral shift, lift root y (m), grow holder scale factor (spare).
  var RIGID_CLIPS = {
    rotmother: {
      clipScale: 1.0,                 // brief sec 6: the slow feel comes from pattern timing
      names: { idle: 'RM_Idle', walk: 'RM_Lumber', attack: 'RM_Slam', hit: 'RM_Hit',
               death: 'RM_Death', spare: 'RM_Rise' },
      idle: { period: 2.6, bob: 0.05, pitch: 0.03 },
      walk: { radPerM: 2.2, bob: 0.08, roll: 0.08, lean: 0.14, yawOsc: 0.05 },
      // windup rears back + rises (the body-lean telegraph), the active
      // window slams forward past upright, recover eases back to stand
      attack: { rear: -0.32, slam: 0.5, lift: 0.18, tremble: 0.012 },
      hit: { flinch: -0.1 },
      spare: { from: 0.15 }           // re-arm: grows from 15% out of the nest
    },
    rotspawn: {
      clipScale: 1.3,                 // brief sec 6
      names: { idle: 'RS_Idle', walk: 'RS_Crawl', attack: 'RS_Lunge', hit: null,
               death: 'RS_Death', spare: 'RS_Emerge' },
      idle: { period: 1.4, bob: 0.02, pitch: 0.05 },
      walk: { radPerM: 4.5, bob: 0.03, roll: 0.05, lean: 0.0, yawOsc: 0.16 },
      attack: { rear: -0.22, slam: 0.3, lift: 0.04, tremble: 0.02 },
      hit: null,
      spare: { from: 0.2 }            // spawn: wriggles up out of the rot ground
    }
  };

  function easeInOut(p) { return p * p * (3 - 2 * p); }

  function RigidAnim(variantKey) {
    this.key = variantKey;
    this.v = RIGID_CLIPS[variantKey];
    this.clipScale = this.v.clipScale;
    this.t = 0;                       // free-running clock (x clipScale)
    this.walkPhase = 0;
    this.clip = 'idle';
    this.clipT = 0;                   // seconds in the current clip (x clipScale)
    this.riseT = -1;                  // spare clip clock (-1 = off)
    this.riseSec = 1;
  }

  // Spare clip: the body grows up out of the ground over seconds (/ clipScale).
  RigidAnim.prototype.rise = function (seconds) {
    this.riseT = 0;
    this.riseSec = Math.max(0.05, seconds || 1);
  };

  RigidAnim.prototype.setClip = function (c) {
    if (this.clip === c) return;
    this.clip = c;
    this.clipT = 0;
  };

  // One sample per frame from the enemy's live FSM. Returns null for death
  // (the rigid fall owns the corpse) - else the pose enemy.js applies.
  RigidAnim.prototype.pose = function (enemy, dt, moveSpeed) {
    var v = this.v, s = this.clipScale;
    this.t += dt * s;
    this.clipT += dt * s;
    if (enemy.fsm === 'dead') { this.setClip('death'); return null; }
    var out = { rotX: 0, rotZ: 0, rotY: 0, swayX: 0, lift: 0, grow: 1 };
    if (this.riseT >= 0) {
      this.riseT += dt * s;
      var rp = Math.min(1, this.riseT / this.riseSec);
      out.grow = v.spare.from + (1 - v.spare.from) * easeInOut(rp);
      out.rotZ = Math.sin(this.riseT * 9) * 0.06 * (1 - rp);
      if (rp >= 1) this.riseT = -1;
      this.setClip('spare');
      return out;
    }
    if (enemy.fsm === 'attack' && enemy.attackPhase !== 'idle') {
      // FSM-timed: phase fraction of the CONFIG phase edges (no clock drift)
      var P = enemy.cfg.attackPhase, A = v.attack;
      var f = Math.min(1, enemy.attackPhaseT / Math.max(1e-4, P[enemy.attackPhase] || 1));
      if (enemy.attackPhase === 'windup') {
        var w = easeInOut(f);
        out.rotX = A.rear * w;
        out.lift = A.lift * w;
        out.rotZ = Math.sin(this.t * 40) * A.tremble * w;   // the strain shudder
      } else if (enemy.attackPhase === 'active') {
        out.rotX = A.rear + (A.slam - A.rear) * f;
        out.lift = A.lift * (1 - f);
      } else {
        out.rotX = A.slam * (1 - easeInOut(f));
      }
      this.setClip('attack');
      return out;
    }
    var moving = moveSpeed > 0;
    if (moving) {
      var W = v.walk;
      this.walkPhase += dt * s * moveSpeed * W.radPerM;
      var ph = this.walkPhase;
      out.lift = Math.abs(Math.sin(ph)) * W.bob;
      out.rotZ = Math.sin(ph * 0.5) * W.roll;
      out.rotY = Math.sin(ph) * W.yawOsc;
      out.rotX = W.lean;
      out.swayX = Math.sin(ph * 0.5) * W.roll * 0.5;
      this.setClip('walk');
    } else {
      var I = v.idle;
      var b = Math.sin(this.t * Math.PI * 2 / I.period);
      out.lift = (b * 0.5 + 0.5) * I.bob;
      out.rotX = b * I.pitch;
      this.setClip('idle');
    }
    // hit flinch rides over idle / walk while the stagger visual runs
    if (v.hit && enemy.staggerTimer > 0) {
      var k = enemy.staggerTimer / window.WH_CONFIG.anim.stagger.visualDuration;
      out.rotX += v.hit.flinch * k;
      if (this.clip !== 'walk') this.setClip('hit');
    }
    return out;
  };

  // Debug / validation read-out (same keys CharacterAnim.getState leads with).
  RigidAnim.prototype.getState = function () {
    return { clip: this.v.names[this.clip] || null, state: this.clip,
      time: this.clipT, clipScale: this.clipScale, rigid: true };
  };

  RigidAnim.CLIPS = RIGID_CLIPS;
  window.WH_RigidAnim = RigidAnim;
})();
