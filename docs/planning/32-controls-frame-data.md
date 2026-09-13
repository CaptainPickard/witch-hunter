# 32 - Controls, Camera, Player Animation Set, Combat Frame Data

Status: PROPOSED (Astrabot hard-numbers pass, 2026-09-13). Roll band
values in section 4.2 LOCKED by Nicko, 2026-09-13 (docs 33/34 version).
Remaining numbers PROPOSED.

Extends 28-controls-camera-gdd.md (three camera registers, lock-on rate
cap, logical facing rule, 16-view ruling) and closes
30-prototype-gap-analysis.md G3 (input binding), G4 (camera completion),
G5 (player body/animation set), G10 (combat frame data). Verb grammar
source: 04-combat-system.md. Drink grammar source: 10-cooking-meals-drinks.md
via 00-README-index.md decision 63 (no estus flask). Traversal numbers
honor 03-world-design.md scale locks. Every number is PROPOSED except
the roll band values in section 4.2 (locked by Nicko, 2026-09-13);
frame data is at 60 fps, one frame = 0.02 s (16.67 ms). Shared scales: health
300-1500, stamina 80-160, damage 1-999 per hit, armor flat reduction
plus percentage cap, stats 1-99, tiers T1-T5, grades C/B/A/S.

## 1. Input Binding (G3)

Conventions: TAP = press/release under 0.30 s (18 f); HOLD = 0.30 s or
longer. Modifier keys are hold-to-shift. Rebinding is free-form in the
options menu; these are defaults.

### Keyboard + Mouse

| Action | Default binding |
|---|---|
| Move | WASD |
| Light attack | LMB |
| Heavy attack | RMB tap |
| Charged heavy (Judgment Cut class) | RMB hold 0.60 s (36 f) |
| Block (hold) / Parry (tap) | Shift |
| Dodge roll | Space |
| Sprint (hold, stamina drain) | Shift while moving + no block |
| Interact / loot | E |
| Lock-on toggle / soft-switch | MMB tap / MMB flick or Q |
| Aim mode (dual-mode, stationary reticle) | Alt hold or C |
| Use health potion (drink) | R |
| Spell/technique wheel | 1-5 direct slots, Tab opens wheel |
| Crouch (hold) | Ctrl |
| Inventory | I |
| Character/menu | K |
| Camera recenter (non lock-on) | MMB double-tap |

Keyboard dual-mode aiming per 04-combat-system.md: standing or crouched
plus Alt-hold = reticle; moving without Alt = lock-on fire.

### Gamepad (XInput/Xbox layout)

| Action | Default binding |
|---|---|
| Move | Left stick |
| Camera | Right stick |
| Light attack | X / Square |
| Heavy attack | Y / Triangle |
| Charged heavy | Y hold 0.60 s |
| Block (hold) / Parry (tap) | LB / L1 |
| Off-hand block/bash | RB / R1 |
| Dodge roll | B / Circle |
| Sprint (hold) | L3 or LB while moving |
| Interact / loot | A / Cross |
| Lock-on toggle / soft-switch | R3 click / flick RS |
| Aim mode | LT / L2 |
| Use health potion | D-pad Up |
| Spell/technique wheel | D-pad Down, slots D-pad L/R |
| Crouch | D-pad Right |
| Inventory | Menu/Options |
| Character/menu | View/Share |

Both schemes: hold D-pad Up opens potion belt selection instead of
instant drink when more than one potion type is carried.

## 2. Camera Completion (G4)

Extends 28-controls-camera-gdd.md. Registers EXPLORATION/COMBAT/AIM are
inherited unchanged; numbers below fill that doc's open items.

- SENSITIVITY DEFAULTS: free camera yaw 2.5 deg per 1 mm mouse at 800
  dpi equivalent, 45 deg/s per full stick deflection ramping to 120
  deg/s over 0.50 s (30 f). Lock-on reduces both by 40 percent. Slider
  range 25-200 percent of default.
- LOCK-ON RATE CAP (inherited rule, now numeric): camera angular
  velocity during lock-on capped at 180 deg/s; view reselection hides
  inside hit-stop, per 28-controls-camera-gdd.md.
- COLLISION: spring-arm with 0.30 m probe radius, pull-in over 0.10 s
  (6 f), push-out over 0.25 s (15 f). Indoors, camera auto-blends to
  2.2 m distance with +0.4 m shoulder offset; blockable by a per-room
  flag for tight corridors.
- REGISTER TRANSITION RATES: exploration (8 m) to combat (5 m) zoom
  blends over 0.50 s (30 f); combat to aim (1.8 m over-shoulder) over
  0.35 s (21 f). Blends are time-based, not distance-based.
- AIM REGISTER: adds one zoom step to 55 deg FOV (from combat's 65),
  reticle fade-in 0.15 s (9 f). No second zoom step; charged spells do
  not zoom further.
- RECENTER: no auto-recenter outside lock-on; stick-flick recenter
  snaps yaw to movement direction over 0.40 s (24 f).
- BOSS-SCALE CAMERA (G30 first pass): targets above 3 m height add a
  dolly-out multiplier, camera distance = 5 m + 0.6 m per target meter
  up to 11 m; lock-on pivot targets the torso, not the head.
- SHAKE: hit feedback shake per 04-combat-system.md bake-in, 0.25 m
  amplitude, 0.30 s decay, capped 2 simultaneous sources.

## 3. Player Body and Slice-1 Animation Set (G5)

One human body (03-world-design.md human lock), one hero-tier rig with
region sub-meshes per 29-art-style-bake-off-spike.md KNOWN ISSUES 1,
16-direction rendering per 28-controls-camera-gdd.md LOCKED ruling
(logical facing drives logic, render snaps views). 26 clips:

| # | Clip | Frames @60fps | Seconds | Notes |
|---|---|---|---|---|
| 1 | Idle combat | 4 loop | 0.07 | 8-view ambient rule, doc 28 |
| 2 | Idle relaxed | 4 loop | 0.07 | non-combat |
| 3 | Walk fwd | 8 loop | 0.13 | 4-frame rule from doc 04 bake-in |
| 4 | Walk back | 8 loop | 0.13 | |
| 5 | Sprint | 8 loop | 0.13 | |
| 6 | Light attack 1 (slash R) | 22 | 0.37 | 6/4/12 startup/active/recovery |
| 7 | Light attack 2 (slash L) | 22 | 0.37 | chain from LA1 cancel window |
| 8 | Heavy attack | 40 | 0.67 | 14/6/20 |
| 9 | Charged heavy release | 48 | 0.80 | 20/8/20 |
| 10 | Block raise (to hold) | 8 | 0.13 | |
| 11 | Block idle (hold loop) | 4 | 0.07 | |
| 12 | Block hit react | 10 | 0.17 | |
| 13 | Parry swipe | 18 | 0.30 | active window inside |
| 14 | Riposte (parry punish) | 45 | 0.75 | |
| 15 | Backstab opener | 40 | 0.67 | |
| 16 | Roll fwd | 30/37/48 by band | 0.50/0.62/0.80 | band-dependent, section 4.2: fast/standard/slow |
| 17 | Roll back | 30/37/48 by band | 0.50/0.62/0.80 | same clip re-timed per band |
| 18 | Roll L / R (mirrored 1x) | 30/37/48 by band | 0.50/0.62/0.80 | one authoring clip per band, mirror |
| 19 | Hit react light | 12 | 0.20 | |
| 20 | Hit react heavy | 16 | 0.27 | |
| 21 | Stagger (poise break) | 50 | 0.83 | committed punish window |
| 22 | Stamina-break kneel | 36 | 0.60 | |
| 23 | Potion drink | 40 | 0.67 | interruptible at f30 |
| 24 | Death | 30 | 0.50 | then ground pose |
| 25 | Interact / loot pickup | 20 | 0.33 | |
| 26 | Tavern-respawn stand | 18 | 0.30 | |

Authoring time per 31-vertical-slice-scope.md: this set is 35-45 h on
the first rig. Per-pose frame budgets for enemies (8 wind-up/stagger,
4 idle/walk) are inherited from 04-combat-system.md bake-in.

## 4. Combat Frame Data (G10)

Structure locked in 04-combat-system.md; all numbers PROPOSED first
pass. f = frames at 60 fps; s = seconds.

### 4.1 Attacks (Long Blade, slice-1 reference weapon)

| Verb | Startup | Active | Recovery | Total |
|---|---|---|---|---|
| Light attack 1 | 6 f / 0.10 s | 4 f / 0.07 s | 12 f / 0.20 s | 22 f / 0.37 s |
| Light attack 2 (chain) | 5 f / 0.08 s | 4 f / 0.07 s | 13 f / 0.22 s | 22 f / 0.37 s |
| Light attack 3 (chain end) | 6 f / 0.10 s | 5 f / 0.08 s | 19 f / 0.32 s | 30 f / 0.50 s |
| Heavy attack | 14 f / 0.23 s | 6 f / 0.10 s | 20 f / 0.33 s | 40 f / 0.67 s |
| Charged heavy | 20 f / 0.33 s | 8 f / 0.13 s | 20 f / 0.33 s | 48 f / 0.80 s |
| Chain cancel window | LA1 f14-20 (0.23-0.33 s) into LA2 | | | |

Stamina costs (stamina scale 80-160): light 12, heavy 25, charged
heavy 40, block-hit absorb 10 per absorbed swing (chip poise transfers
per 04-combat-system.md), parry attempt 8.

### 4.2 Roll, i-frames, stamina break

Roll frame data is band-dependent. Equip-load bands LOCKED by Nicko,
2026-09-13 (docs 33/34 version wins): fast roll, light band (0-10.0
load), 30 f total, 11 i-frames, 22 stamina; standard roll, medium band
(10.1-20.0), 37 f total, 6 i-frames, 26 stamina; slow roll, heavy band
(20.1-30.0), 48 f total, 3 i-frames, 32 stamina. Roll disabled above
30.0 load. One authoring clip per band, re-timed.

| Entry | Number |
|---|---|
| Roll total | 0.50-0.80 s by band: fast 30 f / 0.50 s, standard 37 f / 0.62 s, slow 48 f / 0.80 s |
| Roll i-frame window | late window starting 0.20 s in (f12) every band: fast f12-f23 (11 f / 0.18 s), standard f12-f18 (6 f / 0.10 s), slow f12-f15 (3 f / 0.05 s) |
| Roll recovery (action-lock) | after the i-frame window to roll end: fast f24-f30, standard f19-f37, slow f16-f48 |
| Roll stamina cost | 22-32 by band: fast 22, standard 26, slow 32 |
| Roll distance | 2.2 m light band, 1.8 m medium, 1.4 m heavy |
| Roll speed bands (equip load) | light 4.0 m/s, medium 3.4 m/s, heavy 2.7 m/s |
| Stamina-break trigger | 0 stamina from any action |
| Stamina-break duration | 36 f / 0.60 s, no actions |
| Stamina regen pause | 1.00 s after any stamina action (doc 04) |
| Regen rate, idle/walk | 25 stamina/s |
| Regen rate, blocking | 12.5 stamina/s (50 percent cut, doc 04) |
| Regen rate, attacking/charging | 2 stamina/s |

### 4.3 Parry windows by source (order per doc 04, widest to narrowest)

| Source | Window | Punish reward |
|---|---|---|
| Shield parry | 10 f / 0.17 s | normal riposte (18 f / 0.30 s punish window) |
| Riposte Master (Shield/Defense Adept) | 14 f / 0.23 s | poise-breaking riposte |
| Twin-Parry (Dual Wielding) | 12 f / 0.20 s | normal riposte, wider window |
| Lever Guard (Polearms shaft) | 8 f / 0.13 s | heavy counter (30 f / 0.50 s window) |
| Bare blade parry | 6 f / 0.10 s | heavy counter |
| Enemy (faction soldiers only) | 5 f / 0.08 s, telegraphed stance | n/a |
| Parry active frames within swipe | window opens at f4 after input | |
| Riposte (successful punish) | 45 f / 0.75 s total, active f10-f24 | |

### 4.4 Block, backstab, stagger/poise

| Entry | Number |
|---|---|
| Block raise time | 8 f / 0.13 s to full arc |
| Block arc (base) | 120 deg vs logical facing |
| Block arc (Firm Stance) | 160 deg (04-combat-system.md) |
| Block hit react | 10 f / 0.17 s |
| Backstab window (stealth opener) | 40 f / 0.67 s animation, active f8-f20, x2.5 damage vs unaware humanoid (doc 15 Stealth grammar) |
| Riposte (from parry) x2.0 damage | 45 f / 0.75 s |
| Poise pool, player (reference) | light armor 60, medium 90, heavy 130 |
| Poise pool, enemies | bandit 50, wolf 80, boss remix 220 |
| Poise damage | light 10, heavy 30, charged 45, Blunt-class +50 percent |
| Poise regen delay | 2.5 s without a poise hit |
| Stagger (poise break) | 50 f / 0.83 s committed, extended +15 f by Concussive Force class effects |
| Chip poise through block | 30 percent of listed poise damage |

### 4.5 Drink, movement, gait

| Entry | Number |
|---|---|
| Potion drink (health) | 40 f / 0.67 s; effect applies at f30, cancel-locked f1-f29, walk-cancel after |
| Potion effect | +25 percent max health, min 60, instant (doc 10 drinks never heal, potions are the health channel) |
| Belt selection hold | +12 f / 0.20 s before drink starts |
| Walk speed | 2.4 m/s |
| Jog (default move) | 4.2 m/s |
| Sprint (stamina 8/s) | 6.0 m/s |
| Sprint-to-stamina ratio check | 80 stamina = 10 s sprint, honors 03-world-design.md ~15-min walk gap at jog |
| Mounted reference (OUT of slice) | 11 m/s to honor doc 03 mounted math |
| Crouch move | 1.6 m/s |
| Jump | 0.5 s air time, no i-frames, costs 5 stamina (doc 03 traversal verbs; jump is a gap verb, not a dodge) |

### 4.6 Lock-on and soft-target (G3/G4 bridge)

| Entry | Number |
|---|---|
| Lock-on acquire radius | 18 m |
| Soft-switch (flick) | retargets nearest-in-arc 90 deg, 0.15 s (9 f) blend |
| Lock-on break | target dies or exits 24 m |
| Facing snap on lock | 0.20 s (12 f) yaw blend |

## 5. Consistency Checks

- Startup + active + recovery sums match the clip list in section 3
  for every attack (LA1 6+4+12=22 f, heavy 14+6+20=40 f, charged
  20+8+20=48 f).
- Roll i-frame windows (fast 11 f, standard 6 f, slow 3 f, each a late
  window starting 0.20 s in at f12) sit inside the doc 04 contract that
  Slip the Blade's 2 s reward keys off (04-combat-system.md EXPERT
  menu). Roll totals 0.50-0.80 s and costs 22-32 stamina by equip-load
  band (docs 33/34 version, locked by Nicko, 2026-09-13).
- Parry window ordering matches 04-combat-system.md exactly: shield >
  Riposte Master > Twin-Parry > Lever Guard > bare blade. Note: doc 04
  orders Riposte Master second, wider than Twin-Parry; table follows.
- No estus flask (00-README-index.md decision 63): the drink is a
  crafted-potion channel with carry-weight economy, drink time 0.67 s
  sits between Souls estus (~0.7 s) and a hard interruption window.
- 16-view rule (28-controls-camera-gdd.md LOCKED) applies to every
  directional clip in section 3 except idle/walk (4-frame 8-view
  ambient budget per doc 04 bake-in).

## 6. Open Items

- All values await playtest revision at 31-vertical-slice-scope.md M3.
- Enemy frame data mirrors the player table at listed stat blocks; a
  separate enemy table is G9 territory (bestiary pass).
- Shield-bash and off-hand timings are techniques, not slice-1 verbs;
  deferred to the techniques pass.
- Charged-heavy hold threshold 0.60 s needs controller trigger-curve
  validation in M2.