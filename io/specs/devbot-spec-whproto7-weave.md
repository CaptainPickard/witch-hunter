# DEVBOT SPEC — Witch Hunter v7 "Weave Slice"
Repo: /workspace/witch-hunter, branch dev. Base commit: d06f659 (v6 block/parry).
Authority: docs/planning/04-combat-system.md "RULING PASS (combat-architecture
session, 2026-09-22)" parts A-D; doc 33 ruling pass; doc 17 cross-ref.
Read those first. This spec operationalizes them for the Three.js prototype.

## SCOPE
Implement the combat rhythm layer v1 in the existing vertical prototype:
armed finishers (chain-gated OFFENSIVE techniques), spell-in-hand battle-mage
weave, the 5+2 magic belt, and two loadouts. Slice limits: ONE spell
(Firebolt), ONE authored cross-finisher pair, loadout I = weapon+spell,
loadout II = weapon+shield. No art changes. No enemy AI changes.

## FILE PLAN
1. prototype/js/CONFIG.js — add tunables (logic files must read CONFIG, never
   literals):
   player: focusMax 100, focusRegenPerSec 8, focusRegenDelay 0.5,
           castFocusTaxMult 1.25
   spell: { firebolt: { focusCost 8, damage 12, speed 40, hitRadius 0.5,
           maxRange 30, castWindup 0.25, castCooldown 0.3,
           schoolColor 0xff7722 } }
   belt: { slots: 5, regripSeconds 0.3, consumableSlots: 2 }
   loadout: { toggleSeconds 0.8 }
   armed: { windowSeconds 3.5, damageMult 1.5, crossDamageMult 2.0 }
   consumable: { healthPotion: { heal 40, charges 3 } }
2. NEW prototype/js/spells.js — window.WH_SPELLS registry + Firebolt
   projectile class (pos, vel, update(dt) moves + range-lifetime, collision
   vs enemy circles calls enemy.takeDamage once then dies). IIFE style,
   window globals, no ES modules, no class syntax (match prototype).
   Script tag order: after assets.js, BEFORE player.js.
3. prototype/js/player.js:
   - focus pool + regen (regen delay after spend, mirrors stamina pattern)
   - offhand implement derived from active loadout: 'spell' | 'shield'
   - KeyQ toggleLoadout(): busy for loadout.toggleSeconds (cannot attack,
     cast, block, roll during toggle); resets combo chain
     (comboIndex=0, comboQueued=false, recoverFullyElapsed=false); KEEPS
     armedTimer running; if armedTimer>0 at toggle moment, sets crossArmed=true
   - RMB routing by implement: spell -> tryCast(); shield -> tryBlock()
     (v6 block path MUST be unchanged in loadout II)
   - tryCast(): refuse while rolling, attacking-strike (windup allowed),
     toggling, regripping, guardBroken, dead/dying, or focus < cost
     (HUD flash on refusal). Starts castWindup timer; on windup completion
     spawn Firebolt toward lock target (or facing), spend focus =
     focusCost * castFocusTaxMult (weapon in main hand = tax always in slice),
     start castCooldown.
   - FIZZLE: if player takes damage (hp loss) during castWindup, cancel cast,
     spend NO focus, HUD fizzle flash.
   - belt: Digit1..Digit5 selects slot (refuse empty slot w/ flash), swaps
     bound spell + glow color, starts regrip timer. Selection NEVER touches
     combo chain or armed state.
   - CASTING NEVER RESETS THE CHAIN: comboIndex/comboQueued unchanged by any
     cast action.
   - ARMED FINISHER: when comboIndex reaches moveset.comboChainCap (3) and
     that 3rd strike LANDS (consumeAttackSweep consumed), set
     armedTimer = armed.windowSeconds. Decays in update. tryAttack while
     armedTimer>0 consumes it: that attack's damage * armed.damageMult.
     GUARD BREAK clears armedTimer (stagger counterplay). Dying/dead clears.
   - CROSS-FINISHER: tryAttack while crossArmed consumes it:
     damage * armed.crossDamageMult, crossArmed=false. crossArmed clears if
     armedTimer expires or guard break.
   - consumables: KeyR = slot 1 health potion (heal 40, not above hpMax,
     refuse at full hp or 0 charges w/ flash); KeyT = slot 2 (empty, refuse).
4. prototype/js/enemy.js — NO changes (Firebolt damage via existing
   takeDamage; no stagger from spells in this slice).
5. HUD (game.js + index.html + style.css):
   - Focus bar (blue) above stamina bar, label "Focus", same bar style.
   - Bottom-center belt row: 5 spell slots (key number labels 1-5), divider,
     2 consumable slots (R/T labels), divider, 2 loadout pips I/II (active
     pip highlighted). Selected spell slot tinted schoolColor.
   - Offhand spell glow: small emissive sphere at the left-hand anchor,
     color = selected spell schoolColor; hidden when implement is shield.
   - Armed state: weapon mesh emissive pulse while armedTimer>0.
   - HUD flashes reuse the v6 flash element pattern (cast refusal, fizzle,
     potion refusal). Monospace dark theme consistent.
6. Debug hooks in game.js setupDebugHooks (required for headless tests):
   getFocus, setFocus(v), getBelt() -> array of 5 ids/null,
   selectBeltSlot(i), getActiveLoadout() -> 1|2, toggleLoadout(),
   getOffhand() -> 'spell'|'shield', getCastState() -> {windup, cooldown,
   regrip, toggling}, getArmedState() -> {timer, cross},
   getFirebolts() -> [{x,z,alive}], useConsumable(slot), getConsumables(),
   getCombo() -> {index, queued}.
7. Build: add spells.js to index.html; create builds/v7-playable.html by
   inlining style.css + vendor + js (same approach as v1/v2 builds).
   Page title: "Witch Hunter v7 — Weave Slice".
8. Tests: implement against tests/wh_v7_weave.py authored by Testerbot
   (validation spec). All existing tests/wh_v2_verify.py and
   tests/wh_v3_anim_probes.py must still PASS.

## CONSTRAINTS
- No node on VPS: validate via Playwright headless python harnesses in
  tests/ (existing pattern). prototype/server.py serves builds/.
- Keep prototype conventions: IIFE + window globals, CONFIG-driven numbers,
  transform-only procedural animation.
- Do not break v6 block/parry regression tests.
- Do not commit; leave working tree for IO.

## ACCEPTANCE CRITERIA (Testerbot verifies, IO confirms)
AC1  All new tunables live in CONFIG; zero magic numbers in logic files.
AC2  Digit1-5 selects belt slots; selecting an empty slot is refused with a
     HUD flash; selection changes offhand glow color.
AC3  Cast spends focus (cost x 1.25 tax); Firebolt projectile spawns, flies,
     hits an enemy, enemy hp drops by spell damage.
AC4  Casting mid-chain does not change comboIndex/comboQueued.
AC5  Player damage during castWindup fizzles the cast; no focus spent; no
     projectile.
AC6  Q toggle: busy window blocks attack/cast/block/roll; combo chain resets;
     armedTimer survives; active HUD pip switches.
AC7  Full 3-hit chain landing arms the finisher (timer starts); next attack
     consumes it at 1.5x; timer expiry alone disarms.
AC8  Toggle while armed then attacking = cross-finisher at 2.0x, consumed.
AC9  Guard break clears armedTimer and crossArmed.
AC10 R potion heals 40 without overheal; refuses at full hp or 0 charges.
AC11 Focus bar + belt row (5+2+2) render in HUD with correct labels.
AC12 All debug hooks in AC-list respond correctly.
AC13 builds/v7-playable.html loads headless, render healthy (no console
     errors), WH_DEBUG present.
AC14 tests/wh_v2_verify.py and tests/wh_v3_anim_probes.py still PASS.
## AMENDMENT D2-WEAVE (2026-09-30, IO — weave validation adjudication; this file)

Trigger: weave harness (rebuilt after corruption; shares the ds1 rebuild
lineage) landed 10/18 with 8 fails. IO adjudicated all 8 with direct page
probes per the standing law. ZERO implementation gaps found; Devbot is NOT
dispatched for this round. Every fail was a validation-environment defect
of the SAME classes D2 ruled for ds1 (wall-clock windows under SwiftShader
page-clock dilation, CDP-poll sample starvation, selector/fixture errors).

Per-AC adjudication (probes 2026-09-30, live tree, worktree builds state):
1. AC2: (a) flash verdict read [class*="flash"] which can never match the
   id-based #wh-block-flash element; correct verdict = className gains a
   flash kind + computed opacity > 0 inside a page-clock window. Probed:
   empty-slot press fires cls '' -> 'block', op up to 0.17. (b) glow bar
   demanded a color CHANGE with ONE belt spell in the slice; spec intent
   (L48-50, L69) = glow color equals the selected spell's schoolColor.
   Probed: ff7722 exact (THREE linear working space; convert before
   comparing). Harness fixed accordingly (real-key presses, page-clock
   poll).
2. AC3: harness selected belt slot 1 = EMPTY -> refusal before cast; then
   ran the cast in loadout II after AC6 in some orders (RMB = block).
   Probed: full chain works (focus 100->90 = 8x1.25 tax exact, bolt
   spawns, locked bandit 70->58 = 12.0 exact). Fix: real-key slot 0
   select, force loadout I, wait regrip==0 page-clock, poll for live
   firebolt spawn instead of fixed 0.3s wall wait.
3. AC6: fixed wall waits read pre-completion state (0.8s SIM busy window
   = 2-4s wall under dilation). Probed: toggle completes cleanly (lo
   1->2, spell->shield, toggling flag witnessed true then false, armed
   survives, combo reset, pip switches). Fix: page-clock polls for
   completion + a mid-toggle busy-refusal probe.
4. AC7 arm: harness armed via comboIndex POKE (chainHits stays 0 -> no
   arm possible) and used a 70hp target that DIES at strike 2 (dead
   enemies skipped by the sweep loop; no landing can register). Probed:
   real buffered 3-chain arms at exactly landing 3 (chainHits 1->2->3,
   armedTimer 3.0).
5. AC7/AC8 ratios: reads used getLockTarget().hp with F-press bounce
   (turning lock OFF mid-suite; hp -> null => delta 0) and getEnemy(0)
   mismatching the locked entity. Probed with a lock-resolved enemy
   read: baseline 34, consume = 51 = 34 x 1.5 EXACT (armed consumed),
   cross = 68 = 34 x 2.0 EXACT (cross consumed). Harness fixed to
   resolve hp by matching getLockTarget() coords against the active
   region enemy list, real organic chains, page-clock waits.
6. AC5 fizzle: fixed 80ms wall wait landed outside the windup under
   dilation (or the RMB was refused while castCooldown ran from AC4:
   focus 90.0 evidence). Probed: fizzle contract works (damage inside
   windup => focus untouched, no bolt). Fix: poll canCast() first, poll
   windup > 0, damage inside the window.
7. AC10: ran wherever the previous AC left the player (melee range ->
   hp punctured during fixed waits -> full-refuse misread). Fix: safe
   teleport + lock break + page-clock polls; charges-burned added to the
   refusal verdict.
8. AC14: env-shaped (nothing serves 8792 on this box; ERR_CONNECTION_
   REFUSED). Fix: local ThreadingHTTPServer proxy on 8792 mapping
   /witchhunter/* to prototype/ (same 8791 semantics), spawned by the
   harness. v2 regression PASSes against it. v3's walk probe had the
   wall-cadence defect (60 x 16ms wall < one bob cycle under dilation);
   rewritten to a page-clock rAF collector (same bars).

Standing-law note: all of the above are validation-harness-real catches
fixed BY IO; implementation files remain untouched by this amendment.
Verdict-time harness-freeze shas must be taken AFTER these fixes.

## AMENDMENT A1 (2026-10-02, IO — cross-reference; full text in devbot-spec-combat-ds1.md)

Weave FILE PLAN §3's "recoverFullyElapsed=false" for toggleLoadout is
AMENDED by ruling A-1 (2026-10-02): the toggle now calls endCombo()
(recoverFullyElapsed=true, comboIndex=0, chainHits=0, comboQueued=false),
so an idle toggle starts the next chain at m1 and the 3-hit arming rule
holds across toggles. AC6 reads only {index, queued} — unaffected
(re-validated in the 2026-10-02 integrity-review ladder: weave 18/18).
