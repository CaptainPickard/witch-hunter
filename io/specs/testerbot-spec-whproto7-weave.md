# TESTERBOT SPEC — Witch Hunter v7 "Weave Slice" validation
Repo: /workspace/witch-hunter, branch dev. Harness: tests/wh_v7_weave.py
(authored by this spec). Target build: builds/v7-playable.html served by
prototype/server.py (WH_BASE_ROOT / WH_BASE_PROXY env overrides, v2 pattern).
Playwright sync API, headless chromium (--enable-unsafe-swiftshader).

## METHOD
- Load the v7 build once; assert clean load first (AC13) before any combat
  probing. Zero console errors / pageerrors is itself an assertion.
- Drive input through real input paths where the input path is the criterion
  (page.keyboard for Digit1-5 / Q / R / T, page.mouse right-click for cast,
  left-click for attack). Use WH_DEBUG hooks (page.evaluate) for state
  setup/reads: setFocus/getFocus, getBelt/selectBeltSlot, getActiveLoadout/
  toggleLoadout, getOffhand, getCastState, getArmedState, getFirebolts,
  getCombo, getConsumables, useConsumable, plus v2 hooks (teleportPlayer,
  setCameraYaw, getLockTarget, getPlayer).
- Every check prints "AC<n> <name>: ... => PASS/FAIL"; exit code 0 only if
  all pass. AC14 runs tests/wh_v2_verify.py and tests/wh_v3_anim_probes.py
  as subprocesses and requires both exit 0.
- Numeric tolerances are generous (rAF throttling): damage ratios 1.5x within
  [1.3,1.7], 2.0x within [1.6,2.4], focus tax = cost*1.25 exact value read
  from CONFIG at runtime.
- If a required hook/input probe is missing, the test FAILS with a message
  naming the missing hook — do not silently skip.

## CHECKLIST (maps 1:1 to IO spec AC1-AC14)
- AC1  CONFIG tunables present (focus pool, spell.firebolt, belt, loadout,
       armed, consumable) with spec values; read via window CONFIG object.
- AC2  Digit1-5 selects belt slots (getBelt reflects selection side effects:
       offhand glow color/tint changes; selecting an empty slot is refused
       with a HUD flash).
- AC3  Cast spends focus = focusCost*castFocusTaxMult; Firebolt spawns
       (getFirebolts alive), flies, hits locked enemy, enemy hp -spell damage.
- AC4  Cast mid-chain leaves getCombo() {index,queued} unchanged.
- AC5  Damage to player during castWindup fizzles: no focus spent, no
       projectile spawned.
- AC6  Q toggle: busy window (getCastState().toggling) blocks attack+cast;
       combo chain resets to {0,false}; armedTimer survives toggle; HUD
       active loadout pip switches I<->II; getOffhand flips spell/shield.
- AC7  3 landed strikes arm finisher (getArmedState().timer>0); next attack
       consumes it (timer back to 0) at ~1.5x damage vs measured baseline hit.
- AC8  Toggle while armed sets cross=true; next attack consumes it at ~2.0x
       damage and clears cross.
- AC9  Guard break clears armedTimer and crossArmed (trigger via player guard
       break path; if no callable trigger exists, FAIL naming the gap).
- AC10 KeyR heals 40 capped at hpMax; refused at full hp or 0 charges with
       flash; getConsumables reflects charge decrement; KeyT slot empty refuses.
- AC11 HUD: focus bar + "Focus" label, belt row 5 spell slots (labels 1-5),
       divider, 2 consumable slots (R/T), 2 loadout pips I/II with active
       highlight.
- AC12 All debug hooks respond: presence + one live round-trip each
       (setFocus->getFocus, selectBeltSlot->getBelt, toggleLoadout->
       getActiveLoadout, etc.).
- AC13 builds/v7-playable.html loads headless, title "Witch Hunter v7 —
       Weave Slice", WH_DEBUG object present, zero console errors.
- AC14 wh_v2_verify.py and wh_v3_anim_probes.py still exit 0.

## REPORT
Harness prints per-check lines and a final "V7 WEAVE: PASS|FAIL" plus counts.