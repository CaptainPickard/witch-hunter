# 65 - Caster Body Variant + Magic Cast Anims (Lite Magic Pack)

Order: Nicko 2026-10-10 (pack delivered via WebUI: Lite Magic Pack, 14 clip
FBXs + X Bot, staged at /workspace/witch-hunter/scratch/mixamo-fbx/magic-pack/).
Clarify ANSWERS (binding): FULL caster-body variant (not cast-only); 2H area
cast wired for the dual-glove kit; caster idle swap included. Canon: doc 15
(magic = wisdom stat lines), doc 18 (ranks by use), mixamo-anim-import skill
(retarget pipeline of record), EPR1 input grammar untouched.

## RULINGS

R-65.1 CLIP NAMING: all pack clips retarget to WH_Mag_* on the WH rig
(20-bone house shape, 60 channels, dense keys):
  Cast1H, Cast2H, Idle, Idle02, WalkF, WalkB, RunF, RunB,
  TurnL, TurnR, Jump, ReactSmall, ReactLarge, DeathBack.
Source mapping (staged FBX -> clip): Standing 1H Magic Attack 01 -> Cast1H;
Standing 2H Magic Area Attack 02 -> Cast2H; standing idle -> Idle; standing
idle 02 -> Idle02; Walk Forward/Back -> WalkF/WalkB; Run Forward/Back ->
RunF/RunB; Turn Left/Right 90 -> TurnL/TurnR; Standing Jump -> Jump;
React Small/Large From Front -> ReactSmall/ReactLarge; React Death Backward
-> DeathBack. X Bot.fbx = source skin, UNUSED by the retarget (motion only).

R-65.2 INPUT LAW (Round D, binding): retarget input = the CURRENT
combat-sword.glb (feat/world-visuals, 27 clips), snapshotted outside git
pre-bake; post-bake verify = ALL 27 prior clips byte-identical + binary-prefix
hash equality + 14 new clips 60ch/dense -> 41 total. CHARACTERS sanity
assets.js playerBody 27 -> 41 (Phase B).

R-65.3 VARIANT RULE: the player CharacterAnim gains variant 'caster'.
FULL CASTER MODE = BOTH hands hold caster implements (CONFIG.assets.caster
.items, v1 = ['magicGlove']), evaluated on hand-equip changes (setBody /
equipItem hook, no per-frame cost). Caster mode swaps: idle -> Idle02,
locomotion -> WalkF/RunF (+ backward split WalkB/RunB), reactions ->
ReactSmall/ReactLarge, death -> DeathBack. NOT swapped: the attack chain
(melee stays melee), the roll (procedural, unchanged), turns (no turn
infrastructure v1 - TurnL/TurnR/Jump/Idle(01) ride in the GLB unwired).

R-65.4 PARTIAL CASTER: exactly ONE caster implement equipped (e.g. the
no-class fallback kit's left glove) = body stays warrior (sword idle/walk/
run; the fallback warrior holds a glove forever - full-caster mode requires
both hands, else the fallback kit would live in a wizard body it never
chose). Cast one-shots (R-65.5) still play from ANY caster hand.

R-65.5 CAST ANIMS (presentation-only one-shots): on cast start, anim plays
Cast1H (single caster hand) or Cast2H (both-hands dual cast) via transition();
mechanics authoritative (tickCasts clocks, focus, tax, regen all untouched);
the one-shot plays over/under the cast flow, completion returns to
locomotion/state anims. Cast interrupted (hit fizzle / hand change / death):
the cast-start hook's lifecycle owner cancels the one-shot (same
lifecycle discipline as syncBlock's branchless frames - no latched flags).

R-65.6 SAVE: no new block (anim variant is derived from equipped hands;
inventory save already covers it).

R-65.7 SCOPE CONTRACT: TOUCH = player.js (cast hook + equip-change variant
evaluation), anim.js (variant system + locomotion/reaction/death branches +
backward split), CONFIG.js (assets.caster block + CHARACTERS sanity count),
assets.js (comment + count), bundle. NOT TOUCH = dodge path (inputDirWorld),
movement speeds, cast MECHANICS (tickCasts/focus/tax), moveset tables,
enemy.js, region files, save.js schema.

## ACCEPTANCE (Nicko playtests)
- M1 Magician NEW GAME: magic idle at rest; magic walk/run while moving.
- M2 firebolt (main-hand glove) = 1H cast anim on cast.
- M3 dual-cast kit cast = the 2H area-cast anim.
- M4 fallback kit (sword + single glove): warrior body everywhere; its glove
  casts still show the 1H cast anim.
- M5 in caster mode: small hit = ReactSmall feel, big hit = ReactLarge, death
  = backward death. Sword mode reactions unchanged.
- M6 nothing else moved: DODGE (re-probe mandatory), attacks, wisdom regen,
  classes, saves, Region C.

## CAST1H FIX (2026-10-10, io/missions/2026-10-10-cast1h-fix.md)
Nicko 10-10: the 1H glove cast plays >= 1.5x faster and the firebolt leaves
the hand at the extension peak (it fired at castWindup 0.25 s, ~11% into
the 2.3 s clip). Measured (scratch/mag_cast_peak.json, FK on the GLB):
WH_Mag_Cast1H R_Hand peak f32/70 = 0.4638 (Cast2H 0.6808, not tuned).
- C1 anim.castShot: Cast1H action timeScale = assets.caster.castShotSpeed
  1.5, set once per start, never reset; Cast2H stays 1. castShotKey = the
  shot actually started (null when none; endCastShot clears it).
- C2 player.tryCast: single-glove (not casterMode) main-hand projectile cast
  with castShotKey 'Cast1H' stretches the SAME windup clock to
  max(castWindup, fire1HFraction 0.46 * cast1HClipSeconds 2.3 / 1.5) =
  0.71 s. No new scheduler; fizzle / hand change / belt rebind / respawn
  clear it as before. Origin = castOrigin's live hand-glow sample (no change).
- C3 castProgress clamped to [0, 1] (glow pulse) under the longer windup.

## CAST1H ROUND 2 - UPPER-BODY OVERLAY (2026-10-10, io/missions/2026-10-10-cast1h2-overlay.md)
Nicko 10-10: the 1H cast another +50% faster, and only the torso casts - the
legs keep walking / running / idling under it (before: legs froze in the cast
stance while the player slid).
- R8 assets.caster.castShotSpeed 1.5 -> 2.25. The round-1 tryCast windup
  reads the live row: fire = 0.46 * 2.3 / 2.25 = 0.47 s after accept (still
  the hand peak). No player.js / game.js change.
- R9 castUpperBody (kill switch) + castUpperNodes (12: Spine..R_Hand) +
  castLowerNodes (8: Hips, Root, legs). Census: every one of the 42 player
  clips is a dense bake of all 20 nodes, 12 upper + 8 lower, no overlap, no
  orphan (scratch/glb_bone_census2.py -> scratch/mag_cast_track_partition.json).
- R10 actions.Cast1H = 'WH_Mag_Cast1H__upper' (upper-node tracks, same
  duration); this.clips keeps the full clip; Cast2H stays full-body.
- R11 anim.lowerAction(key): lazy '<clip>__lower' loop of the resolved
  locomotion clip (caster Mag_* or warrior Sword* sets), lower tracks only.
- R12 anim.castOverlay (castShot's Cast1H path, no transition()): other
  actions stop, the pose being left fades out under the shot, the legs move
  to the locomotion's lower variant at the same phase and full weight
  (identical leg tracks -> no pop), the torso shot fades in at 2.25x.
  clip / castShotKey / clamp hold / refusals exactly as round 1.
- R13 anim.syncCastLegs (syncPlayer hold branch): movement changes mid-cast
  crossfade the legs to the new lower variant; leg rate follows the speed
  with setLocomotion's law.
- R14 exit: transition() frees the legs - stale lower variants stop, the live
  one fades out with prev and hands its phase to the locomotion it returns
  to. Every cancel site (fizzle, hand change, hit, death, respawn, attack,
  block) already ends through transition(), so none changed.
- castUpperBody false = round-1 behavior (full Cast1H clip, transition path).
