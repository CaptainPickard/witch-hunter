# World R1 implementation report (reconstructed by IO from verified evidence)

Status: Devbot (gpt-6-sol/openai-codex lane) implemented the round but hit the
30-minute delegation wall at 92 API calls AFTER code was complete, BEFORE
writing this report. IO reconstructed it from the live diff + measured runs;
every claim below is tool-verified.

## What was implemented (spec: io/specs/devbot-spec-wh-world-r1.md)

### D1 P0-1 ground-align (holder structure) — assets.js
- groundAlign(root) now WRAPS the template in a holder Group; inner root
  gets position.y -= minY (measured at identity); holder is the cached
  template (assets.js:106-121). Scale-invariant by construction.
- GROUND_META keyed by holder uuid: {height, width, groundMinY} (:85,:117).
- makeStandIn results go through groundAlign too; cache/resolve paths all
  store the holder (assets.js:101, :155, :165, :174).
- New accessors: groundMinY(name) (:213-217), getMeta(name) (:218-223).
- groundHeight semantics unchanged (height consumed by game.js:625-626 +
  region-manager.js:341-342 for normalization).

### D1 P0-1 prop placement — region-manager.js
- Prop loop: obj.position.set(p.x, p.y || 0, p.z) (:330) — no y overwrite,
  optional lift support added per spec 1.2. scale.setScalar unchanged.

### D1 P0-1 player/enemy bodies
- game.js:628-630: pBody.position.y = -(groundMinY * pScale) BEFORE
  setBody; children[0].position.y += groundMinY (equivalent two-line lift;
  harness-verified). bodyBaseY picks up the scaled offset; player.js
  untouched (READ-ONLY honored).
- region-manager.js:346-348: eBody lift + holder-level compensation
  before enemy.setBody. enemy.js bodyBaseY semantics unchanged.
- NOTE: enemy.js additionally contains R1's measured corpse final-Y
  (corpseFinalY, updateDeathVisual at :75-100): computed ONCE at death
  start from Box3 of root (axe included), root.position.y interpolated
  to corpseFinalY + settle bounce; ANIM keys untouched.

### D2 P0-2 ground material — region-manager.js
- Ground material color 0xffffff for both regions (canvas carries the
  region-biased palette) (:293).
- makeGroundTexture: minFilter NearestMipmapLinearFilter,
  generateMipmaps true, anisotropy = min(4, caps.getMaxAnisotropy())
  (:246-253). magFilter Nearest unchanged; repeat=12 unchanged; canvas
  resolution unchanged; mist plane untouched.

### D3 debug hook
- game.js:458 getAssetMeta -> WH_ASSETS.getMeta (single addition).

### CONFIG.js
- Zero new keys (per spec 1.7 preference).
- TWO R1-tagged value changes: walk.bobAmp 0.09->0.02, walk.footDipAmp
  0.04->0.005 (documented deviation: A2 idle/sprint tolerance requires
  feet contact; amplitude-only, no timing keys touched). Verified R1-only.

## Measured results (IO runs of tests/wh_world_r1_validation.py)

Pre-fix smoke (Testerbot, 17:41): A1 104/104 props sunk (worst yewTree
-9.88), A2 idle floats 0.083-0.140, A3 corpse 0.082, A4 ground mean 9.24
sd 1.57. Verdict FAIL as expected pre-fix.

Post-fix (IO full run): 8 PASS / 0 FAIL / 1 RECORD, 0 flakes.
- A1: props=104 missJoin=0 minYViol=0 heightViol=0
- A2: idleBad=[] sprintMaxDev=0.033
- A3: corpse minY=0.009 (organic kill, clicks=20)
- A4: groundBand mean=56.37 sd=16.83 (need >20 / >4)
- A5: RECORD meanTempStddev=0.000 (non-blocking watch item)
- A6: floors intact (weave d2893c23... 10/8; ds1 9093216d...)
- A7: rebuild clean, consoleErr=0 pageErr=0, idx/css freeze-ok,
  buildHash f1a358c6ed55, rebuildRc=0 byte-identical
- A8: scope clean, secrets clean

Independent validation (Testerbot, 18:39): verdict PASS. Independent
full-suite re-run matches (its /tmp/testerbot_r1_fullsuites.log: same 8/1
profile, A3 minY=0.010, A4 mean=56.64/sd=16.88). Byte-identical rebuild
f1a358c6ed55 before=after. ds1 suite crash-run (18/18 NameError on the
other workstream's mid-rebuild harness) proven TREE-STATE-INVARIANT via
static analysis (fresh() undefined at 18 call sites) — not R1-caused,
owned by the combat-ds1 round.

## Deviations from spec (both documented, both verified)
1. Player/enemy body lift implemented as position.y + children[0]
   compensation pair instead of spec 1.3's single-line form (equivalent
   math; harness-verified through A2 both idle and sprint).
2. CONFIG walk.amp values changed (spec 1.7 said prefer zero keys; this
   is a value tune of EXISTING keys, not new keys — A2 feet-contact
   tolerance). Tagged R1 in comments.

## Committal boundary (gate ruling, recorded)
- assets.js, region-manager.js, game.js, CONFIG.js: R1 hunks are cleanly
  separable; committed as reconstructed R1-only versions (built from
  HEAD + verified R1 hunks; weave/ds1 hunks remain uncommitted).
- enemy.js: R1's corpse fix lives inside the SAME regions as the
  combat-ds1 round's yawFrame restructure and phase FSM (updateDeathVisual
  reads this.yawFrame added by combat-ds1). NOT separable without
  shipping unvalidated combat code. RULING: enemy.js stays uncommitted;
  its corpse fix ships with the combat-ds1 commit. Consequence: the
  committed A3 behavior is verified in the dirty tree, and the CORPSE
  part of that behavior is conditional on enemy.js landing in the
  combat round; A1/A2/A4 are fully committed-code-verifiable.
- index.html / style.css / player.js / spells.js / tests/wh_v7_weave.py /
  tests/wh_combat_ds1_validation.py / tools/build_v7.py: not R1, left as-is.
- prototype/builds/v7-playable.html committed ONLY as the R1-verified
  build (it embeds the dirty tree's weave code; the committed tree's own
  build equivalent is derivable via tools/build_v7.py). Flagged in commit
  message.

## Precision-map final line numbers (this round's sites)
- assets.js: holder wrap :106-121; accessors :213-223; loader caches
  :155,:165,:174.
- region-manager.js: texture :246-253; material :293; prop loop :330;
  enemy body :346-348.
- game.js: WH_DEBUG hook :458; player body :628-630.
- CONFIG.js: walk.bobAmp :387; walk.footDipAmp :396 (R1-tagged).
- enemy.js (uncommitted, ships with combat round): corpseFinalY :38;
  updateDeathVisual :75-100.

## Amendment requests: none open.
## Out-of-surface edits: none (verified by A8 set-difference at verdict time).