# ASTRABOT MISSION BRIEF - Left-hand shield equip + Radiance light spell
2026-10-04, from IO. Nicko's orders (10-04 playtest report + follow-ups):

1. "I want to be able to equip a shield when I press the '1' key, unequipping
   the fireball from the left hand. If I repress '1' it should reequip the
   fireball again."
2. "I want the left hand to have a shield as default when any of the 1-5
   options are unequipped."
3. "I want a spell on '2' that creates a light source that follows me around
   for 60 seconds. During this time I am free to equip other spells or shield.
   Once cast, the light does not go away when the spell is unequipped."
4. Answers from IO clarification round:
   - Pressing the currently-held spell's key AGAIN returns the left hand to
     the shield (stow-to-shield).
   - Switching between two spells (e.g. fireball held, press 2) switches
     DIRECTLY spell->spell, no shield flash in between.
   - Boot default left hand = FIREBALL (belt slot 1 selected + equipped).
     Shield therefore appears on the first stow press.
   - Recasting Radiance while a light is alive resets that light's timer to
     60s. Never stack multiple radiance lights.
   - Shield asset EXISTS - do not generate anything with Meshy:
     art-direction/3d/assets/weapons/round-shield-pixelated.glb
     (measured by IO: 2000 faces, ext 1.99 x 2.0 x 0.39 raw units,
     attributes POSITION+TEXCOORD_0 only, NO NORMAL).

You are Astrabot, running as a Claude Code print-mode agent in the
witch-hunter repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Report file, commits, and pushes as in previous missions.

## 1. Current mechanics (verified by IO this session - do not re-research)

Config surface (prototype/js/CONFIG.js):
- CONFIG.belt.slots = 5, regripSeconds = 0.3. Belt defaults set in
  player.js constructor: this.belt = ['firebolt', null, null, null, null],
  selectedBeltSlot = 0, boot selected spell = 'firebolt'.
- CONFIG.spell.firebolt = {focusCost 8, damage 12, speed 40, hitRadius 0.5,
  maxRange 30, castWindup 0.25, castCooldown 0.3, schoolColor 0xff7722}.
- CONFIG.loadout.toggleSeconds = 0.8 (Q toggle, flips activeLoadout 1<->2,
  offhand 'spell'/'shield' derived at player.js ~783-795. Leave Q AS-IS -
  the new '1'..5 path is a separate quick stow/equip switch that does NOT
  run the 0.8s toggle window and does NOT reset the chain or armed state).
- Blocking rules (v6): RMB-hold blocks ONLY while offhand === 'shield'
  (player.canCast returns false when offhand !== 'spell'; block path
  requires offhand === 'shield'). KEEP this split: RMB = cast when a spell
  is equipped, block when the shield is equipped. Spells never block.

Code surface:
- player.js: selectBeltSlot(i) (keys Digit1-5, ~411-425): sets
  selectedBeltSlot, regripTimer, fires onSpellSelected. getSelectedSpellId()
  returns belt[selectedBeltSlot]. offhand derive at ~794-796 from
  activeLoadout (the Q system). castWindup ticked by game.js ~1145-1156
  which calls WH_SPELLS.spawn(scene, spellId, origin{x,y,z}, dirX, dirZ).
- game.js: castWindup tick completes the cast -> WH_SPELLS.spawn(...)
  (spawn currently only knows Firebolt). offhand glow:
  game.spellGlow (left-hand emissive orb, visible when offhand==='spell,
  colored by CFG.spell[sid].schoolColor) - positioned at the mirrored idle
  pose (~408-419). Player lantern lives on yawFrame.
- spells.js: window.WH_SPELLS = { registry..., spawn(scene, spellId,
  origin, dirX, dirZ) -> Firebolt | null }; Firebolt class exists.
- assets.js: MANIFEST logical->path; prepTemplate(root, isPixelated)
  traverse-normalizes materials; swapBodyMap swaps the body atlas PNG;
  groundMeta/weaponScale measurement utils exist (longsword precedent:
  CONFIG.assets.weaponScale.longsword = 0.528 measured).
- anim.js: MOVE_NAMES maps longsword chain moves to per-move clips
  (combat-chain.glb, 9 clips). Enemies use WH_Attack1.

## 2. WORK ORDER A - left-hand implement system (shield default)

State machine replaces the offhand derive line while KEEPING the Q system:
- New player fields: leftHand = { mode: 'spell', spellId: 'firebolt' }
  (boot default per Nicko's answer). mode 'spell' | 'shield'.
- offhand property stays the single source other code reads
  (game.js checks p.offhand === 'spell'): offhand = leftHand.mode.
- Key handling (Digit1-5, replace selectBeltSlot wiring ONLY - keep the
  function, add the equip toggle on top):
  * slot k has no spell -> refusal flash (existing empty-slot path).
  * leftHand is 'spell' && leftHand.spellId === belt[k-1] -> STOW:
    leftHand = { mode: 'shield' }; regrip window 0.3s (belt.regripSeconds);
    NO chain reset, NO armed reset, NO attack interruption (it is a quick
    stow; if attacking mid-swing let the swing finish attacking state).
  * else -> EQUIP belt[k-1]: leftHand = { mode:'spell', spellId:BELT },
    regripTimer, onSpellSelected(spellId) (glow re-colors). If currently
    BLOCKING while stowing (shield->spell transition), endBlock() first
    (block only exists on shield hand). Spell->spell direct switch = same
    equip path, no intermediate shield.
- Boot: constructor sets leftHand = { mode: 'spell', spellId: 'firebolt' }
  and selectedBeltSlot = 0 (fireball out at spawn).
- Q toggle (loadout swap) now just sets leftHand = shield-mode when it
  lands on loadout 2, spell-mode (belt[selectedBeltSlot]) when loadout 1 -
  preserving every existing Q-side effect (toggle window, chain reset).
  Keep Q fully functional for both modes.
- Shield VISUAL: 
  * manifest: roundShield: 'art-direction/3d/assets/weapons/round-shield-pixelated.glb'
  * engine safety (protects this + all legacy props): in prepTemplate's
    traverse (assets.js), if obj.isMesh && !obj.geometry.attributes.normal
    -> obj.geometry.computeVertexNormals() BEFORE material normalize.
  * attach the roundShield instance to the L_Hand bone of the player body
    (player.js after body create: find bone via body.getObjectByName
    ('L_Hand', true) on the cloned body; fallback = yawFrame anchor when
    the fallback stand-in body mounts). Mirror the WEAPON mount pattern:
    measure raw GLB bounds in assets (GROUNDMETA path exists), scale =
    CONFIG.assets.weaponScale.roundShield (MEASURE so hand-held diameter
    is ~1.0-1.1m - compute from the 1.99 raw, expected ~0.5, but MEASURE,
    do not trust this number), face orientation knob
    CONFIG.assets.shieldMount = { rollDeg: N, offset: [x,y,z] } with
    defaults you measure (shield face should read forward/edge-on slightly
    outside the left hip - use the same getWeaponDef pattern style as
    bladeAxisY/rollDeg, measured, not guessed).
    IMPORTANT: the equipped shield may be a NON-animated child added at
    equip (visible toggle on stow/remove). Keep the mesh creation ONE
    equip path callable for both spell equip and stow.
- HUD: the belt row must reflect leftHand: the slot matching the equipped
  spell gets the active tint; when mode==='shield', show a small 'S'
  glyph badge on the divider or dim ALL spell slots except selected
  (implementation freedom, keep it subtle, no layout changes).

## 3. WORK ORDER B - Radiance (KEY 2, slot 2 = 'radiance')

- CONFIG.spell.radiance = {
    focusCost: 10, castWindup: 0.3, castCooldown: 0.3,
    durationSeconds: 60, lightColor: 0xffb36b, lightIntensity: 2.2,
    lightDistance: 14, glowColor: 0xffd9a0, orbRadius: 0.14,
    bobAmp: 0.06, fadeOutSeconds: 1.0
  } (all tunable; you may finalize better defaults, KEEP KEYS + NAMES).
- belt default becomes ['firebolt', 'radiance', null, null, null]
  (slot 2 filled so key '2' works immediately).
- spells.js: RadianceEffect class (orb mesh = emissive sphere school color
  + THREE.PointLight DEDICATED light added to the scene - NOT the fixed
  prop light pool: the pool is nearest-socket semantics for lantern posts,
  radiance must not steal it). Parent the effect to the player yawFrame
  with measured offset (upper-left, ~[ -0.45, 1.9, 0.1 ] + bob on y), so
  it follows movement without per-frame world math; re-parent through
  effect.attatch(player) in game.js (pattern = attachPlayerLantern).
- spawn() dispatch: spawn(scene, 'radiance', ...) returns the effect
  handle; game.js keeps game.radiances = [effect] (MAX 1: recast resets
  the SAME effect's timer to 60s and re-fades in - never a second light).
- LIFETIME LAW (the core of Nicko's request): once spawned, the light is
  INDEPENDENT of leftHand/offhand entirely. Switching to shield, another
  spell, toggling loadout, rolling, dying (light persists through
  death+respawn and keeps following), NEVER removes it early. The ONLY
  end conditions: timer expiry (fade over fadeOutSeconds then dispose
  orb+light) or recast-refresh (timer reset to 60).
- Casting restrictions are the EXISTING canCast() rules (focus, windup,
  cooldown, alive). Radiance is cast from the spell hand like firebolt;
  after completion the implement stays 'radiance' until the player stows.
- WH_DEBUG: expose getRadianceState() -> { active, remainingSeconds,
  lightIntensity } (pattern of getCastState/getArmedState).

## 4. ACs (self-verified, listed in your report)

- AC1 boot = fireball equipped; pressing 1 stows to shield; pressing 1
  again re-equips fireball. (state traces in report)
- AC2 pressing 2 while fireball held switches directly to radiance
  (no shield intermediate).
- AC3 with shield equipped: RMB blocks (existing blocking path), no cast.
  With any spell: RMB casts, no block.
- AC4 Radiance cast spawns orb+light that follows the player; stowing the
  spell to shield does NOT remove the light; timer expiry removes it with
  fade; recast resets timer to 60; never stacks.
- AC5 light persists through death/respawn and keeps following.
- AC6 chain/armed state untouched by any 1-5 press (verify code path).
- AC7 all numbers in CONFIG; engine code has no magic numbers.
- AC8 all prototype JS parses (esprima) + no dangling refs to removed keys.
- AC9 prepTemplate normal-fallback present (shields/legacy props safe).
- AC10 shield measured scale recorded in report + CONFIG.

## 5. Hard laws (unchanged)

- NO automated harness or headless browser runs of ANY kind. Static checks
  (esprima/grep) only. Nicko's playtest is the only acceptance test.
- One change order arc: A then B, in that order, separate commits
  (feat commit + feat commit), push after each. Never commit to dev/main.
- Never touch: CONFIG.renderer, the merged dev/main branches,
  scratch/blender_chain_clips.py output GLBs, region placements,
  CONFIG.world.dirtPath, the moveset weapon chain CONFIG (except nothing
  here requires touching it).
- All engine numbers from CONFIG keys. No hardcoded agent names anywhere.
  Player copy never uses the word " free ".
- If a mechanism is IMPOSSIBLE as specified, stop that sub-order, write
  findings to scratch/report notes, continue the other, and list it.

## 6. Report

scratch/astrabot-equip-radiance-report.md - AC evidence, measured shield
scale, the offsets you chose, anything left undone + why. Final chat
message: short summary (commits, AC table, tuning knobs, watch items).