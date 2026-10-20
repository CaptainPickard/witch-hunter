# CC-C11 · Sleep gate: sleep/heal only at dusk or night (save stays free)

## 1. RULING (Nicko, 2026-10-20)
"if the player tries to sleep and heal again anytime before dusk/night, the
player is barred with a message, 'cannot sleep, it is not yet Dusk/Night'.
The player can save all they want, but not sleep and heal, they must wait to
dusk/night before resetting to a new day." Context report: a kit camp in the
Old King's Forest + sleep = "it just goes black" (a daytime sleep attempt -
now refused before any fade, so the confusing black roll cannot trigger).

## 2. BEHAVIOR
- TENT MENU unchanged: Save / Load always available at any phase.
- SAVE AND HEAL = sleep: allowed ONLY while dn.dormant (frozen tutorial
  night - the FIRST rest must still start the cycle: beginCycle is called
  ONLY from rest(), C3 tutorial law) OR dn.phase is 'dusk' / 'night'.
- Refused otherwise: toast 'Cannot sleep, it is not yet Dusk/Night.'
  (CONFIG.camp.text.sleepGate; Nicko's exact message), menu STAYS OPEN,
  NOTHING else runs (no fade, no prepareWake, no resting latch).
- Sleeping at dusk/night: existing path (nextDawn -> new day, wake at dawn,
  C4.1 wake-state checkpoint). Sleep during the 45-min day window must wait.

## 3. CHANGE
- CONFIG.js camp.text += sleepGate row.
- camp.js saveAndHeal(): phase gate at the top (dormant || dusk || night).
- No other files. Bundle rebuild.

## 4. ACCEPTANCE
- A1: sleep attempt in dawn/day -> toast, no fade, menu stays, clock unchanged.
- A2: dormant first rest still begins the cycle (tutorial law intact).
- A3: save / load rows work at any phase (untouched paths).
- A4: node --check clean; bundle rebuilt + served 8787 / 8793.
- A5: NO harness, NO headless smoke runs - Nicko's playtests are the test.

## 5. SCOPE CONTRACT
TOUCH: prototype/js/CONFIG.js (one text row), prototype/js/camp.js (the
gate), prototype/builds/v8-playable.html (rebuild), this brief. Nothing else.