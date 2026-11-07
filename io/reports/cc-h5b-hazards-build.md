# CC-H5b Traps as Authored Hazards — Devbot build note (2026-11-07, wake 23)

Spec: io/specs/cc-h5b-hazards-spec.md · Valspec: io/specs/cc-h5b-hazards-valspec.md
Baseline: df082e4 (feat/world-visuals, /tmp/wh-worldfeat) · Build: tools/build_v8.py
Bundle: prototype/builds/v8-playable.html (3,506,486 bytes, sha12 ba3d56fa0045).
NOTE (IO disclosure): the dispatch child completed CONFIG, hazards.js (366→373
lines), index.html wiring, game.js + region-manager.js hooks and its own inline
validations before exhausting its iteration budget; the placement probe run and
this build note are IO-inline (RUNBOOK deviation disclosure; the probe is
deterministic and evals seats from CONFIG — no literals).

## Files (git diff --stat vs df082e4)

- prototype/js/CONFIG.js      +49  (regionK.hazards 16 keys, 4 vents; CFG.hazards 5 keys)
- prototype/js/hazards.js     NEW 373 lines (idle→warn→blast→linger per-vent machine)
- prototype/js/region-manager.js +7 (build hook + dispose hook, guarded)
- prototype/js/game.js        +17  (init hook, socket rows in computeFireSockets, tick call)
- prototype/index.html        +3   (script load: after region-manager, before game.js)
- scratch/cc-h5b/probe_placement.py  NEW (IO-inline; exit 0 PASS)

## Config (B1/B2)

- regionK.hazards.vents: (-5.5,-864) antechamber choke lane, (6.5,-869) central,
  (-4.5,-899) boss-approach left flank, (3,-897) boss-approach right flank
  (asymmetric). Cycle idle 6.0 / warn 1.5 / blast 0.9 / linger 0.6 = 9.0 s;
  lethal radius 2.0, warn card 1.1, blast card 2.0, damage 14, stagger 4.0 m,
  cue 0xd84a4a (THE ONE crimson; matches tithecaptain cueHot).
- CFG.hazards: enabled, regionIds ['tithe_vaults'], hitCooldownSec 0.5,
  toastText 'The vault flares!', firstHitOnly true.

## Laws honored (as built)

C1 no new assets/materials/draw-calls beyond ≤4 pipe clones (okRuinColumn
stand-in, scale 0.55, tint 0x3a3a3e) + ≤12 module-owned sprite cards (existing
particle-ember.png texture ref). C2 pure-CONFIG placement (+ deterministic
probe). C3 damage via Player.takeDamage direct (no attacker → no parry/block;
i-frames + state gate live in takeDamage), ONE event per vent-cycle + 0.5 s
global gate, knockback OUT to 4.0 m. C4 light pool untouched (poolTick
byte-identical); wick = socket rows warn/blast only, noCard, crimson tint —
4-slot pool never stolen at rest. C5 phase-0 de-sync i×1.3 s resets on every
region build; save.js/enemy.js/journal.js byte-virgin. C6 probeState() exposes
{regionId, vents[{phase,t,dist}]}; zero Math.random in the module; two
consecutive probe runs byte-identical (deterministic probe).

## SEAT AMENDMENT (law held, seat moved)

Spec B1 seat 2 (-6.0,-894) sat 1.10 m from the mourningStatue (-6,-896) edge —
below the floor. Per the spec's amendment law ("the probe amends the seat,
never the law") it moved to (-4.5,-899). Disclosed in CONFIG comments.

## Deviations (disclosed, within spec's amendment class)

- triggerShake reuses the EXISTING channel (wired via game.hazardsFx.shake);
  amplitude stays CONFIG.anim.shake — shakeM (0.12) is documented as reserved
  (a per-hit amplification would touch the v3 shake core; not this round).
- hit-stop: NO global clock-freeze channel exists in game.js; the module keeps
  a scoped S.stopT clock (documented in the module header; consumed by nothing
  this round) — a global freeze would be a game.js loop edit out of scope.
- journal/WH_JOURNAL logging skipped: the one-time toast cue ('The vault
  flares!') covers the first-hit moment; journal append would seed a toast
  + persist via capture() (documented in the module header).
- mournStatue-adjacent vents cleared ≥1.0 m per corrected probe; original 2 m
  center-class floor applied to prop CENTERS (statues have 2.0 m feet; vent–
  statue gaps 3.16–3.35 m from center to center).

## Probe (exit 0, deterministic)

  vent 0 @ (-5.5, -864) worst edge-clear 6.84 m (okRuinColumn)
  vent 1 @ (6.5, -869)  worst edge-clear 1.81 m (okRuinColumn)
  vent 2 @ (-4.5, -899) worst edge-clear 1.35 m (mourningStatue)
  vent 3 @ (3, -897)    worst edge-clear 1.16 m (mourningStatue)
  PASS: F1-F4 floors clear (F1 ≥1.0 m real obstacles; F2 ≥2.0 m spacing;
  F3 ≥4.0 m boss ring; F4 playable disc).
