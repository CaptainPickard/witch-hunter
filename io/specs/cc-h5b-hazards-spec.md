# CC-H5b — Traps as Authored Hazards (Tithe Vaults flame vents)

Date: 2026-11-07. Lane: V4B (wake 23 pick). Parent: CC-H5 (landed df082e4).
Art anchor: art-direction/concepts/concept-08-veil-spire.png + camp-dark-affinity
— charcoal/slate stone, ONE crimson accent per frame, no warm torchlight.
Doc laws: 47-altar-delves-gdd.md STRATA V4 ("the vault's own traps as authored
hazards"); 04-combat-system.md telegraph contract (a mandatory telegraph frame
flashing the danger accent); doc 24 no-particle-realism law (diegetic light).

## A. Design intent

The Tithe Vaults (regionK, plane-0 underground disc r34) currently kill only
through mobs. Strata V4's theme is "the collection side of the machine": the
vault itself should be hostile, not just the things in it. Round adds ONE
authored hazard primitive — the flame vent — placed by hand as a puzzle:
telegraphed, readable, dodgeable, cheap to render, zero new assets, zero new
lights, zero new draw calls (every visual is an existing pool card or an
instanced clone).

## B. CONFIG additions (js/CONFIG.js)

### B1. CFG.regionK.hazards (new key on regionK; nothing else on regionK moves)

```
hazards: {
  vents: [
    { x: -5.5,  z: -864 },  // antechamber choke lane, left of the spawn walk-in
    { x:  6.5,  z: -869 },  // central floor, between antechamber and boss seat
    { x: -6.0,  z: -894 },  // boss-approach left flank
    { x:  3.0,  z: -897 }   // boss-approach right flank (asymmetric: harder read)
  ],
  // timing: idle -> warn -> blast; independent per vent
  idleSec: 6.0,      // dormant
  warnSec: 1.5,      // telegraph (crimson card grow + light wick)
  blastSec: 0.9,     // flame card at full + light at peak
  lingerSec: 0.6,    // cooldown fade (harmless, dim)
  radiusM: 2.0,      // LETHAL radius (damage seat), centered on the pipe
  warnRadiusM: 1.1,  // visual radius the crimson card reaches at warn end
  blastRadiusM: 2.0, // visual radius the ember card reaches at blast start
  heightM: 2.2,      // card float above ground (visual only)
  damage: 14,        // hp per blast tick, once per player per vent-cycle
  hitStop: 0.10,     // seconds of global hit-stop when the player is struck
  cueHex: 0xd84a4a,  // THE ONE crimson accent (matches tithecaptain cueHot)
  cardIdleHex: 0x8a2a20,   // idle ember dim red-brown (always visible vent eye)
  cardBlastHex: 0xff8a3c,  // blast flame core (still inside the crimson family)
  shakeM: 0.12,      // camera shake magnitude on a player hit
  staggerMeters: 4.0 // player knockback distance, away from the vent center
}
```

Placement law: every vent seat must satisfy, over regionK's FULL built set
(ring colliders, props, enemy rows, lair seat, rot lair row, both land rows,
spawn, boss seat):
- ring-edge clearance >= 1.0 m (nearest ring circle edge to vent center);
- nearest enemy spawn >= 5.0 m;
- nearest prop collider edge >= 2.0 m (no vent sits inside furniture);
- boss-seat keepout >= 6.0 m (AMEND-1 floor inherited);
- land K (0,-856) >= 4.0 m and spawn walk-in (0,-864) >= 2.5 m from every
  vent center (the walk-in lane may graze the EDGE of one warn card but
  never a lethal blast circle at rest distance);
- spawn-walk corridor (0,-856)->(0,-880) |x| <= 2.2: at rest, ZERO vents
  inside the corridor; during a cycle, a corridor-crossing vent may only be
  in warn at landing (blast window never starts inside the corridor).
- The four seats above are IO-authored as the DEFAULT layout and MUST be
  re-validated by the placement probe (C2) against the live tables. A probe
  failure amends the seat, never the law.

### B2. CFG.hazards (global primitive block, sibling of CFG.raid)

```
hazards: {
  enabled: true,
  regionIds: ['tithe_vaults'],   // gate: only these regions run vents
  hitCooldownSec: 0.5,           // per-player global re-hit gate (all vents)
  toastText: 'The vault flares!',  // one-time first-hit cue (inventoryUI toast)
  firstHitOnly: true
}
```

## C. js/hazards.js (new module, ~200-260 lines)

Load order: AFTER js/region-manager.js, BEFORE js/game.js (index.html; same
band as ambush.js with the same comment style). Exposes window.WH_HAZARDS:
init(game), tick(dt), state(), probeState() (pure readout for probes:
per-vent phase + time-in-phase + distance to player, no Math.random use).

### C1. Build (drains, no new materials)

Region-group child, added in region-manager buildRegion ONLY for regions in
CFG.hazards.regionIds (the module registers a build hook; no region-manager
branch needed if the hook pattern exists — else add ONE guarded call, max
+6 lines, disclosed):
- ONE THREE.Group 'wh-hazards' per region build (dispose-safe: it is a
  region-group child; disposeRegion already frees it).
- Per vent: ONE cone/pipe mesh, CLONED from an existing vent-ish prop's
  mesh template (okRuinColumn small-scale tinted charcoal is the approved
  stand-in: scale 0.55, y -0.1, tint 0x3a3a3e — reads as a floor stub) PLUS
  TWO sprites from the EXISTING game.flameCards ember texture
  (particle-ember.png): an idle eye card (warning always visible) and a
  warn/blast card pool drawn from game.lightPool's SPARE card slots only if
  free — else a per-vent OWN sprite (max 4 vents -> max 4 sprites; the
  ember texture is shared, material per vent, AdditiveBlending,
  depthWrite false, same grammar as the pool cards).
- Cards start invisible; idle card visible at opacity 0.35 idle-wick scale
  0.28 — ALWAYS visible (the authored-readable law: you can see the danger
  before it fires).

### C2. Placement probe (scratch/cc-h5b/probe_placement.py)

Python probe (node evals, same solve_geometry.py lineage as CC-H5):
- eval CONFIG.js + region-defs.js, walk regionK FULL set, verify EVERY
  B-section clearance for every vent seat; print a per-vent PASS table +
  a corridor-cycle analysis (worst-case vent at max walk speed crossing the
  corridor during a full idle->warn->blast cycle);
- verify: no new lights (probe greps the diff for addLight/createPointLight
  outside the declared sprite/light-pool reuse), no new assets in the
  manifest (grep assets.js diff), no new draw calls beyond <= 8 sprites +
  <= 4 pipe clones (count from the built group),
- exit 0 = all clear, list every FAIL with its binding seat.

### C3. Tick (state machine, per vent, regionK-active only)

- Phase machine: idle -> warn -> blast -> linger -> idle. Phase timers
  independent per vent; vents DE-SYNC by construction (phase 0 start offsets
  staggered: vent i starts at phase 'idle' with offset i * 1.3 s).
- idle: eyes wick (idle card opacity 0.30-0.42 sine, period 2.2 s).
- warn: warn card grows scale 0.28 -> 1.1 (ease-out), opacity ramp
  0.35 -> 0.85, wick light slot (see C4) intensity 0 -> ~2.2, cue color
  0xd84a4a. NO damage in warn.
- blast: blast card scale 1.1 -> blastRadiusM (ease-out per 0.1 s), opacity
  0.95 -> 0.55 over blastSec, light 2.2 -> 3.2 then decay to 0.6 in
  linger, damage ONCE: any player inside radiusM at ANY tick of blast
  takes damage/hit-stop/shake/knockback (below), then vents set
  vent.hitDone = true for the cycle.
- linger: cards fade to 0, light decays to 0; harmless.
- Damage law: the hit uses Player.takeDamage DIRECTLY (a vent is not an
  attacker: no parry/block path — resolveIncomingHit is for enemy attacks
  only; disclosed deviation from the enemy path, justified by doc 47:
  the vault is the hazard, not an opponent). i-frames still gate (player
  roll wins, takeDamage already checks iframes). One hit per vent-cycle
  (hitDone) + CFG.hazards.hitCooldownSec global gate.
- Knockback: push player OUT along the vent->player delta to
  staggerMeters from the vent center (clamp to region rim afterwards via
  the standard clamp); hit-stop: game.hitStopT += hitStop (reuses the
  existing global hit-stop channel; verify the channel name at build — if
  the channel differs, use whatever game.js exposes for enemy-hit hit-stop
  and disclose); shake: reuse the enemy-hit camera shake channel if
  exposed, else set the game.shake amplitude directly (disclose).
- Toast: first player hit ever (session) -> CFG.hazards.toastText via
  inventoryUI.toast, once (firstHitOnly flag in module state).

### C4. Light discipline

- ZERO new PointLights. The wick light is the EXISTING lightPool: hazards
  pushes ONE socket { id: 'hazardVent#i', intensity: ..., color: cueHex,
  noCard: true, weight: 1.0 } into computeSockets() via a WH_GAME-provided
  hook — if no hook exists, add ONE function computeSockets entry pushing
  WH_HAZARDS.socketsFor(rm.logic.activeId) rows (max +5 lines, disclosed).
  Only when a vent is IN warn/blast (not idle/linger) does its socket row
  appear, so the pool's 4 slots are never stolen at rest.
- game.lastSockets consumers unaffected (socket rows carry the same keys).

### C5. Save/persistence law

- NO save state: vents reset to phase-0 idle offsets on every region build
  and on save load. save.js untouched. Journal (js/journal.js) may log the
  first vent hit 'the vault flared' as flavor ONLY IF journal.js already
  has a zero-cost append path (else skip; disclose the choice).

### C6. Debug hooks

- WH_HAZARDS.probeState() returns { vents: [{ phase, t, dist }], regionId }.
- ?whdbg=1 unchanged; wolf-debug.js untouched.

## D. Enemy/hazard interplay (must NOT change)

- Enemies ignore vents (no steering change; enemy.js untouched).
- updateEnemies call site in game.js gains no hazard coupling — WH_HAZARDS
  ticks from its own call right after WH_AMBUSH.tick(dt) (game.js +2 lines
  max for the tick + init wiring, same pattern as ambush wiring).
- Vents never target or aggro; they are fixed-point authored hazards.

## E. Files touched (expected)

- js/CONFIG.js (+~45 lines: regionK.hazards + CFG.hazards)
- js/region-manager.js (0-6 lines: the guarded build hook, if needed)
- js/game.js (+2-8 lines: init + tick wiring + socket rows)
- js/hazards.js (new)
- index.html (+1 script line)
- prototype/builds/v8-playable.html (REGENERATED by tools/build_v8.py; do
  NOT hand-edit)
- scratch/cc-h5b/probe_placement.py (probe)
- io/reports/cc-h5b-hazards-build.md, io/reports/cc-h5b-hazards-validation.md

## F. Acceptance criteria (Testerbot gate order)

1. CONFIG parse: regionK.hazards.vents EXACTLY 4 seats; CFG.hazards keys
   exactly the 5 B2 keys; no other regionK key moved/renamed (key-set diff
   vs df082e4 = ONLY the hazards addition).
2. index.html: hazards.js loads AFTER region-manager.js, BEFORE game.js.
3. Build hook: region-group 'wh-hazards' exists iff the build entered a
   regionIds-gated region; disposeRegion leaves no stale sprite materials
   (traverse count: group's sprites all share ONE texture ref
   particle-ember.png; no second texture load).
4. Tick law: phase machine transitions idle->warn->blast->linger->idle with
   the CFG timings (probe math on paper, no randomness); de-sync offsets
   present (vent0 vs vent1 phase start differs by exactly 1.3 s modulo the
   cycle).
5. Damage law: exactly ONE damage event per vent-cycle; i-frame wins
   verified by reading takeDamage's check; no parry/block path possible
   (no attacker object passed); hitCooldownSec honored across vents.
6. Light law: computeSockets emits ZERO rows at rest for hazards; exactly
   <= 4 rows during warn/blast; every row carries noCard true + color
   cueHex; pool Tick path unedited (poolTick body diff = 0 lines).
7. Placement probe (C2) exit 0 with the FULL clearance table printed.
8. node --check on every touched js file; build_v8.py regenerates the
   bundle; the marker grep on SERVED bytes (post-flip) shows CC-H5b.
9. save.js diff = 0; enemy.js diff = 0; light.js diff = 0; inventory.js
   (toast path reads existing toast ONLY) diff should be 0.
10. Playability belongs to Nicko (acceptance bar, per PRIMARY law 2): no
    harness, no headless browser run. Testerbot validates CODE + PROBE
    only.

## G. Out of scope this round

- Spike traps / pendulum blades / arrow walls (future V4C lanes).
- Blight-weather underground variant (doc 03 PROPOSED) — separate round.
- The Remains (V5) chamber, Scar-Reader (V3) strata, new strata J/K art
  (blocked on the image provider fix, tracked in the wake-23 journal).
- Enemy LOS ignoring hazards (already the case; no change needed).
