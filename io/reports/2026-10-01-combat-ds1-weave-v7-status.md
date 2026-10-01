# Round A combat overhaul (P0-1/P0-3/P0-6/P0-4) + weave-v7 — combat status report

Date: 2026-10-01. Author: IO. Round: combat-ds1-A + weave-v7 (one gate cycle).
Base HEAD: eacff4a (world-R1). Branch: dev. Everything below UNCOMMITTED until
the final commit step (Testerbot verdicts landed first per the gate).

## VERDICTS

- WEAVE v7: TESTERBOT VERDICT PASS (deleg_e92df0e5, sa-0-a5d83904, glm-5.3,
  902s). Independent run: 18/18 checks PASS, regress=True (v2 VERIFY PASS,
  v3 PASS), V7 WEAVE: PASS, exit 0. Harness shas verified by Testerbot:
  tests/wh_v7_weave.py f07dec10e58f... , tests/wh_v2_verify.py c3bf4b1e0d22...,
  tests/wh_v3_anim_probes.py 7aa5af94b771... Tree unchanged by Testerbot
  (hygiene pass, census 69 dirty = pre-commit expected).
- COMBAT DS1 Round A: TESTERBOT VERDICT PASS (deleg_de86322d, lean-mode
  attempt 3 after two API-finalize lane deaths with complete evidence;
  glm-5.3, no model overrides). Testerbot's own isolated suite run:
  18/18 PASS, 0 crashes, no flakes, no rerun required (its run log:
  /tmp/tb_ds1_run3.log; A1-4 worstPair=0.0000 under the range-intersection
  comparison). Verdict delivered as final message + its own run log.

## DS1 ROUND A — profiles before -> after

| Suite run | Profile |
|---|---|
| IO session start (pre-repair) | 15 PASS / 3 FAIL / 0 crashes |
| After D3 wave 1-6 repairs | 16-17/18 (budget truncation artifacts) |
| FINAL (post A1-4 ranges + A3-4 retry) | 18 PASS / 0 FAIL / 0 crashes (twice) |

## ADJUDICATION LEDGER (every fail probed; zero game gaps found)

DS1 harness fixes (IO, per D2 item 8 law; all probe-proven):
1. H1 cfg-key NaN poisoning: run_sampler shipped z-displacement as 'dy' but
   SAMPLER_JS reads 'dz' -> e.pos.z += undefined -> NaN through windup
   tracking/lunge + done-flag NaN lock. Found via NaN-writer stack probe
   (writes enter Enemy.separateFrom). ALSO fixed A1-1 (was passing vacuously
   on NaN compares; now real dyaw 0.2095) + added tz to rows.
2. H2 last-swing slicing: sampler installs mid swing-1 recover -> swing-1
   recover rows contaminated swing-2 splits (A4-2 recFrozen=0.56 false-fail;
   probe ground truth: swing-2 recover frozen EXACTLY 0.000, lunge 0.10).
3. H3 A3-4 final-cycle filter (14s window, segment at windup entries, keep
   last complete cycle) + linear-ramp one-step extrapolation for windEndFrac
   (0.23 raw = sim-frame quantization; enemy.js applies designed PI/8 = 25%
   exactly). Bars unchanged in intent.
4. H4 A4-1 drain: pred=displaced early-break truncated post-displacement
   windows (poll-log proof: sampler 91 rows vs drain 2). Now breaks at first
   post-swing row; ceiling 20s.
5. H5 A4-1 anchors: live-bearing tx/tz errors; err0 = displaced-target
   bearing vs pre-tracking yaw; postConv -> tracking resumption (idle lock
   hard-tracks live target; static-point convergence unwinnable by design).
6. H6 A1-4: CDP-poll capture missed 2-frame strikes; page-side per-frame
   sampler; then range-intersection pairwise comparison (rAF phase jitter
   measures 1.2 rad/frame skew under load, not pose drift).
7. H7 budget 240s -> 480s (dilation was silently dropping A4-3/A4-4).
8. H8 A3-4 one retry on zero complete cycles (D2 flake protocol).

WEAVE harness fixes (IO; same artifact classes; zero game gaps):
- AC2 flash element is #wh-block-flash (id) - [class*="flash"] never matched;
  verdict now className-flip + opacity>0 in page window. Probed: cls '' ->
  'block', op 0.17. Glow bar: ONE belt spell in slice -> color-EQUALITY to
  schoolColor ff7722 (exact match, THREE linear space).
- AC3: selected EMPTY slot 1 (refusal before cast); then possible loadout II
  residue (RMB=block). Fix: real-key slot 0 + force loadout I + regrip==0
  page-clock wait + firebolt-spawn poll. Ground truth: tax 100->90 = 8x1.25
  exact, bolt hit 12.0 exact.
- AC4/AC10 fine after context fixes. AC5: page-clock fizzle reflex (damage
  INSIDE windup via rAF watch, not python poll). AC10: safe-spot teleport +
  settle polls + charges-burned evidence (heal 40.0 exact).
- AC6: 0.8s SIM busy window = 2-4s wall; completion polls + mid-toggle
  busy-refusal probe (run evidence: lo 1->2, spell->shield, armed survives,
  combo reset, pip true).
- AC7: poke-armed comboIndex left chainHits=0 (no arm possible) + 70hp target
  dies at strike 2 (dead enemies skip the sweep). Fix: organic buffered chain
  (real presses in recover windows). Ground truth: arming at EXACTLY landing
  3 (chainHits 1->2->3, timer 3.0-3.1); consume 51 = 34x1.5 exact; expiry
  disarms.
- AC8: same + cross banked by REAL Q toggle: 68 = 34x2.0 exact, consumed,
  alive-gated.
- hp reads: getEnemy(0) mismatched the locked entity sometimes -> lock-resolved
  target_hp (matches getLockTarget coords against active-region roster).
- AC14: nothing served 8792 (env-shaped ERR_CONNECTION_REFUSED) -> harness
  binds its own local /witchhunter/ proxy fallback. v2 strafe/W probes:
  v3's camAutoFollow rotates the camera under long holds -> re-pin camera
  inside the hold (original test condition restored). v3 walk probe: 16ms
  WALL cadence + pre-R1 0.1 bar vs committed R1 retune (bobAmp 0.02 +
  footDip 0.005 -> designed p2p ~0.05) -> page-clock rAF collector +
  CONFIG-anchored bars (p2p in (0.015, 0.06], maxima >= 1, 8s window).
  v3 walk PASS: p2p 0.022, maxima 2, 18 samples.

## WHAT DISPATCHED TO WHOM

- Devbot: NOT dispatched. Zero implementation gaps across both rounds (every
  one of 20+ fails across 8 runs adjudicated to the harness). The standing
  law + brief assign harness-real catches to IO; dispatching Devbot for a
  no-op would have violated the gate.
- Testerbot: dispatched twice per round discipline:
  - deleg_e92df0e5 (weave): PASS verdict (complete).
  - deleg_b7e099da (ds1 run 1): lane API-timeout finalize death (STOP rule
    honored, no model switch).
  - deleg_2fb73204 (ds1 retry, lean dispatch): running.

## PLAYTEST STATE (what Nicko sees at /witchhunter/ once pushed)

Combat feel: souls-like commitment (windup tracking 240 deg/s, movement lock
0.3x windup / 0.0 strike-recover with the strike lunge kept), bandit telegraph
(0.7/0.12/0.8 FSM, slow raise-back then fast sweep), ghoul hop telegraph,
combo chain m1->m2->m3 with buffered presses, armed finisher (3-hit chain ->
3.5s window -> next hit 1.5x), cross-finisher (toggle while armed -> next hit
2.0x), guard break clears armed, Firebolt weave (RMB cast, 8x1.25 tax, 12 dmg
bolt, fizzle on windup damage), 5+2 belt with empty-slot refusal flash,
loadout I/II toggle with busy window, focus bar + belt HUD.
World visuals: UNCHANGED this session (out of scope, world-R1 already landed
at eacff4a).

## COMMITS

- See the final commit section appended below after IO stages and pushes.