# HP1 - ENEMY HEALTH BARS (change order)

- date: 2026-10-07 | order: HP1 | branch: feat/world-visuals | baseline: f6a05bc
- builder: Claude Code print mode, model opus, --max-turns 80,
  --permission-mode acceptEdits, allowedTools Read/Write/Edit/Bash
- worktree: /tmp/wh-worldfeat | serving: 8793 atomic flip + webui /playtest-feat/
- laws: NO harness / headless browser of any kind. Nicko's playtest is the
  ONLY acceptance test. One order at a time. Syntax checks on edited JS only.

## STATE (verified census 2026-10-07)

- Baseline ADOPTED: f6a05bc "feat(ck1): campkit wiring" (worktree == origin,
  host fetch exit 0, rev-parse verifies). History: AI1 landed 6aaf339 (S1
  lock-on awareness + strafe band + decision loop) and e325005 (S2 guard
  posture + 0.5x front-arc mitigation). CK1 campkit wiring landed f6a05bc.
- No other session in flight (no claude processes; stale scratch/campkit_*.py
  untracked = CK1 residue, leave alone). Worktree clean, no conflict markers.
- Serving verified: 8793 -> releases/f6a05bc (relative), host curl 200 on
  prototype/builds/v8-playable.html, md5 9f77b0ce.
- Enemy truth: this.hp set to cfg.hpMax at spawn (enemy.js:47), decremented in
  takeDamage (enemy.js:628, hp<=0 -> fsm 'dead' at :645). Enemies NEVER heal
  and dead enemies stay in game.enemies (corpse persists for loot; region
  rebuild restores corpses via deadFall>=1, enemy.js:151-172). Bandit+ghoul
  share the Enemy class -> one bar implementation covers both.
- HUD truth: setupHud game.js:196 (game.hud registry, DOM created/looked up
  there); per-frame HUD update loop exists (updateHud game.js:751). Lock-on
  projection pattern: updateReticle game.js:993-1008 (v.project(camera),
  screen px via (v.x*0.5+0.5)*innerWidth / (-v.y*0.5+0.5)*innerHeight,
  v.z>1||v.z<-1 -> hide). current lock target = game.player.lockTarget.
- CONFIG truth: window.WH_CONFIG in js/CONFIG.js; hud section :892; enemy
  section :829 (bandit/ghoul rows, ai1 sub-rows with "// PROPOSED, Nicko
  tunes" comment convention). Bundle: python3 tools/build_v8.py from repo root
  (inlines style.css + js/index.html -> prototype/builds/v8-playable.html).

## CODE-REVIEW-GRAPH IMPACT (baked 2026-10-07, alias wh-worldfeat @ f6a05bc)

impact --files prototype/js/enemy.js prototype/js/game.js prototype/js/CONFIG.js
prototype/style.css prototype/index.html --repo /tmp/wh-worldfeat:
- 107 nodes directly changed
- 0 nodes impacted within 2 hops
- 0 additional files affected
HUD-isolated. No cross-file blast. Proceed as scoped.

## LOCKED RULINGS (clarify 2026-10-07, Nicko answered)

1. VISIBILITY: a bar APPEARS when the enemy has taken damage at least once in
   its current life OR is the player's current lock-on target. It HIDES again
   only per ruling 2/3. Souls-style restraint - screen stays clean.
2. LOCKED AT FULL HP: while the enemy is the lock-on target and has NEVER
   been damaged, the bar STAYS VISIBLE at full fill (locked-target
   indicator) until the enemy dies or lock breaks.
3. FULL-HEALTH HIDE: when not locked and at full health, bar hides.
   Implementation note (IO ruling, verified in code): enemies never heal in
   this build, so (enemy.hp < enemy.hpMax) IS the "damaged this life"
   predicate - no new per-enemy state, no takeDamage hook. Read-only.
4. RENDER: bars are HUD DOM elements projected from the enemy world position
   every frame, reusing the updateReticle v.project(camera) pattern
   (game.js:993-1008). DOM is inherently face-on. Scale/dim mildly with
   distance per CONFIG rows. Hide when behind camera (v.z out of [-1,1]).
5. STYLE: pixel register + darkwood. Dark frame + fill in the player HP bar
   family (style.css:66-68 gradient #8f2f2a -> #5e1d19; frame like
   .bar-outer #5a5344). NO spell accent colors, NO blue/purple fill, NO
   pact-red - the fill is the same muted blood-iron family as the player HP
   bar, just smaller.
6. DEATH FADE (IO ruling from the code): corpses PERSIST for looting in this
   build, so a literal corpse-lifetime bar would linger forever. The bar
   fades OUT once fsms to 'dead' (deathFadeSec, PROPOSED 1.2s, covers the
   death fall visually), then is gone. Never rides the corpse, never lingers.
7. SPECIES: bandit and ghoul both get bars (same Enemy class - automatic).
8. ALL GEOMETRY IN CONFIG: new hud.hpbars section, every row commented
   "// PROPOSED, Nicko tunes". No magic numbers in game.js for look values.
9. ZERO INTERFERENCE: lock-on reticle, corpse gold glow (loot marker), XP pip
   and bar flow untouched. Bars are display-only - they read hp and
   lockTarget, they do not hook damage, XP, or AI.

## SCOPE CONTRACT

TOUCH (exactly these):
- prototype/js/CONFIG.js - append hud.hpbars section (see PROPOSED rows).
- prototype/js/game.js - in setupHud (~:196): create the bar-pool container
  div (single parent #wh-enemy-bars inside #wh-hud, pointer-events none;
  do NOT edit index.html - match the blockFlash/guardBreakText pattern at
  game.js:222-240 which creates DOM in setupHud). New per-frame updater
  called from the existing HUD/frame loop where updateHud runs: for each
  live enemy maintain one bar element (Map keyed by enemy object; sweep
  releases bars for enemies no longer in game.enemies). Per enemy per frame:
  project (enemy.pos.y + hpbars.heightAboveHeadM) via v.project(camera);
  set left/top px, width scale by distance, opacity by distance + death
  fade; display none when hidden (full hp + not locked) or behind camera.
  Visibility predicate exactly: (enemy.hp < enemy.hpMax) ||
  (game.player.lockTarget === enemy) - with death: on fsm 'dead' start fade,
  then release element. Do not modify lock-on logic, damage, or AI paths.
- prototype/style.css - .wh-ehb classes: outer (dark frame, border #5a5344
  family, bg rgba(0,0,0,0.55)), fill (HP family gradient #8f2f2a->#5e1d19),
  pixel register (no antialias blur, hard 1px edges, border-radius 0-2px).
NOT TOUCH:
- prototype/js/enemy.js (read-only: hp at :47, takeDamage :628, fsm 'dead'
  transitions - nothing added)
- prototype/index.html, js/daynight.js, js/camp.js, js/save.js, js/leveling.js
- C2/C3.1 look values, sky pools, camp menu, XP flow, AI1 behavior.

PROPOSED CONFIG rows (append under hud: ~CONFIG.js:892, exact names):
  hpbars: {
    widthPx: 46,               // PROPOSED, Nicko tunes
    heightPx: 6,               // PROPOSED, Nicko tunes
    heightAboveHeadM: 2.3,     // PROPOSED, Nicko tunes - world Y offset above enemy pos
    fadeStartM: 16,            // PROPOSED, Nicko tunes - distance where dimming begins
    fadeEndM: 32,              // PROPOSED, Nicko tunes - distance of minimum opacity
    minOpacity: 0.45,          // PROPOSED, Nicko tunes - alpha at fadeEndM+
    hideBeyondM: 40,           // PROPOSED, Nicko tunes - no bars past this
    scaleNearM: 6,             // PROPOSED, Nicko tunes - full width at/below this
    scaleFarM: 30,             // PROPOSED, Nicko tunes - width shrinks toward scaleFar, floor 0.8
    deathFadeSec: 1.2          // PROPOSED, Nicko tunes - fade-out once fsm 'dead'
  },

## ACCEPTANCE CRITERIA (Nicko playtests)

- A1: Boot NEW GAME to the day-0 tutorial night: NO bars anywhere.
- A2: Land one hit on a bandit: its bar appears instantly, fill matches the
  damage (about-full after one hit), stays visible afterward.
- A3: Back off until the bandit leashes/disengages: bar remains (it was
  damaged), nothing else on screen - restraint honored.
- A4: Lock a FRESH undamaged bandit: bar appears at full fill; break lock:
  bar hides (full hp + not locked). Repeat on a ghoul.
- A5: Ghoul bars behave identically to bandit bars (damage appears, lock
  shows, hide rules same).
- A6: Kill an enemy: bar fades during the death fall (~1s) and is GONE while
  the corpse lies lootable; no bar ever shows over a corpse.
- A7: Lock-on reticle, corpse gold loot glow, XP pip and HP bars all render
  unchanged; no overlap collision with the reticle position on a locked
  enemy (bar sits above the head, reticle centers on the body).
- A8: Walk away from a damaged enemy: bar shrinks and dims smoothly; past
  hideBeyondM it disappears; approach again and it returns.
- A9: Save-and-Heal at camp, then CONTINUE-load the save: bar flow unchanged
  by the load (world state only; bars re-derive per frame).

## VALIDATION LAW (no-harness gate)

- node --check on every edited JS (playwright driver node; NO game run, NO
  headless browser, NO harness).
- Greps post-build in the CURRENT bundle for markers: 'wh-enemy-bars',
  'hpbars', 'PROPOSED, Nicko tunes'.
- Evidence for done = Nicko's playtest verdict. Nothing else.

## COMMIT + SERVING

- ONE commit: feat(hp1): enemy health bars - HUD DOM projected bars above
  enemies (souls damage-taken/lock-target visibility, distance dim/scale,
  death fade, CONFIG hud.hpbars PROPOSED rows)
  Identity: CaptainPickard <pickard.nicko@gmail.com>. Push to
  origin/feat/world-visuals immediately after commit.
- Rebuild bundle (python3 tools/build_v8.py) BEFORE the commit so the
  bundle ships in the same commit (standing pattern).
- After push: 8793 flip tools/wh_release_flip.py <sha> with a RELATIVE
  releases/<sha> target, run host-side via /tmp/dhost.py host_exec with
  timeout >= 800s (60s default silently kills flips mid-build). If
  releases/<sha> lacks prototype/builds/, delete the husk and re-run.
  Verify: host curl 200 on prototype/builds/v8-playable.html + marker greps
  in the served bundle. webui /playtest-feat/ serves the worktree live.