# Astrabot report - BUGHUNT: player walk animation stuck

2026-10-05, brief: io/missions/2026-10-05-astrabot-walkanim-bugfix-brief.md.
Static reading only (no harness / headless runs, per LAW 0).

## Symptom
The player moves (position updates) but the walk/run clip never plays. The
body holds a pose (the last attack clip clamped at its end, or idle).

## Root cause (latch in anim.js, not new Order C code)
`CharacterAnim.hitActive` is a latch:
- set in `hit()` (anim.js:98, `player.takeDamage` -> `anim.hit()`, player.js:1184)
- cleared ONLY by the mixer `'finished'` event of the hit action (anim.js:51),
  plus `death()` / `revive()`.
- `setLocomotion` refuses to transition while it is set (anim.js:86 before,
  now :90): `if (!this.hitActive) this.transition(state, ...)`.

`playerAttack` (anim.js:122 before) does `if (this.clip !== key)
this.transition(key, ..., true)`. If the player is hit mid-swing (or swings
during the hit flinch), the very next `syncPlayer` crossfades away from 'hit':
the hit action is `fadeOut`-ed and three.js `_updateWeight`
(vendor/three.classic.js:54314-54321) sets `enabled = false` when the fade
ends. A later transition `stop()`s it outright. Either way the action never
reaches its end, so **`'finished'` is never dispatched and `hitActive` stays
true for good**. From then on every `setLocomotion` call only sets
`timeScale` on a walk action that isn't playing. The body stays frozen on the
clamped attack clip while the FSM keeps moving the player. Only death and
respawn (`revive()`) clear it.

Chain: take damage while attacking (common in real combat) -> hit clip
interrupted by attack clip -> no 'finished' -> hitActive latched ->
locomotion transitions blocked -> walk never plays.

### Regression window note
The mechanism predates Order C: `hitActive` and the per-move
`clip !== key` transition both exist at a890f41 (10-03), an ancestor of
a8b1a0d. I read all of the Order C player.js / game.js / touch-controls diffs.
None of it touches `attacking`, `animMoveSpeed`, `syncPlayer` reachability or
any `anim.*` call. Most likely Order C's two-button combat only made the
trigger (hit while swinging) more frequent in Nicko's play. The Order B
playtest just never hit it. Enemies share the same code (enemy.js:429 +
`enemyAttack`), so they could latch the same way, and the fix covers them too.

## IO's suspects
1. **Branch starvation / attacking stuck**: NO. `attackTimer -= dt` runs
   unguarded (player.js ~1310), and `attacking` clears at `attackTimer <= 0`.
   Starvation does happen, but one level lower: `setLocomotion` IS reached,
   and its inner transition is the one blocked, by `hitActive`.
2. **Per-hand cast windup never resolving**: NO. `tickCasts` zeroes
   `c.windup` before `completeCast` on every path. `dropPendingCast` /
   `cancelCastFizzle` zero both fields. Cast state also never feeds
   `attacking` or the anim at all.
3. **attackMoveId / weaponId drift**: NO. `weaponId` is untouched by Order
   C. `startAttack` / `getChainCap` / `getAttackPhase` are unchanged in the diff.
4. **transition() restart storm**: NO. No new caller of `anim.transition`
   in Order C or the light order. The glow orbs / hand lights parented to
   `L_Hand` / `R_Hand` are unnamed children and cannot rebind tracks. The
   related failure was a *missing* transition (the latch), not too many.
5. **Order C game.js gating of syncPlayer**: NO. `syncPlayer` is still called
   unconditionally each frame (game.js:1396). The cast tick moved into
   `tickCasts` with no early return in the loop.

## Fix
`anim.js` `transition()`: `if (state !== 'hit') this.hitActive = false;`.
Any transition to another clip (attack override, locomotion, death) ends the
hit reaction, so an interrupted hit can no longer latch. No new tunables. A
hit that plays to its end behaves exactly as before ('finished' -> back to
locomotion).

## Regressions re-verified by reading
- **Attack chain**: `playerAttack` still transitions on clip change and
  re-seeks. Hit-during-attack still lets the attack override the flinch next
  frame (unchanged), and now also releases the latch. Back to walk at chain
  end via `setLocomotion`.
- **Roll cancel**: roll drives `animMoveSpeed = rollSpeed`, `running = true`
  -> 'run'. Unaffected. A roll during an uninterrupted hit still waits for the
  hit to finish (unchanged).
- **Cast windup both hands**: no anim involvement. `tickCasts` /
  `cancelCastFizzle` untouched.
- **Q swap**: `toggleLoadout` / `equipItem` don't touch the anim.
- **Radiance / hand lights**: light.js only parents lights / orbs to hand
  bones. Untouched.
- **Death / revive**: `death()` transitions to 'death' (clears hitActive, as
  it already did). `revive()` unchanged.

## Playtest (Nicko)
W1-W6 per the brief. Specifically repro the trigger: let an enemy hit you
**while you swing**, then walk away. Walk should play (before the fix it
froze for the rest of the life).
