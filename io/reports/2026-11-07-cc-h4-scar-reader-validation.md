# CC-H4 'The Scar-Reader' — VALIDATION VERDICT (Testerbot lane, 2026-11-07)

- Round: CC-H4 | Lane: Testerbot (independent) | Worktree: /tmp/wh-worldfeat @ HEAD 3253711 (feat/world-visuals)
- Valspec: io/specs/cc-h4-scar-reader-valspec.md | Spec of record: io/specs/cc-h4-scar-reader-spec.md
- Method: static source + baseline diff + build-note audit + arithmetic recompute; NO probe re-run (valspec scope law), no harness, no browser, no build_vX. Git used read-only only.
- Probe-audit working copies: variants reasoned over COPIES under /tmp/cc-h4-variants/ (no tracked file edited).

## Verdict items

```json
{
 "V-0": {
  "status": "PASS",
  "evidence": "baseline/source_sha256.txt vs tree sha256: CONFIG.js: DECLARED-MISMATCH (base 150c93083a tree 2f9008c468); assets.js: DECLARED-MISMATCH (base 0712f218e7 tree 7828be2f1e); enemy.js: DECLARED-MISMATCH (base 1ba01dad27 tree ccbf1f2b08); game.js: MATCH (base 9e6c43d725 tree 9e6c43d725); region-manager.js: MATCH (base 26acff7c79 tree 26acff7c79)",
  "diffs_ok": [
   "CONFIG.js",
   "assets.js",
   "enemy.js"
  ]
 },
 "V-1": {
  "status": "FAIL",
  "evidence": "CONFIG.js:2951 fails=['scale = None', 'lairRadius = None', 'radius = None', 'poison{dps,duration,slow} = None', 'rearm{days,trigger,radius} = None', 'minions{asset,cap,interval,range,dieOnMasterDeath} = None']"
 },
 "V-2": {
  "status": "PASS",
  "evidence": "CONFIG.js:2951 lair={ x: 0, y: -9, region: 'J', flagPrefix: 'scarreader' }"
 }
}
```
### Family 1-2: V-0 preservation, V-1..V-9 static items

- **V-0 PASS** — baseline/source_sha256.txt vs tree sha256: CONFIG.js: DECLARED-MISMATCH (base 150c93083a tree 2f9008c468); assets.js: DECLARED-MISMATCH (base 0712f218e7 tree 7828be2f1e); enemy.js: DECLARED-MISMATCH (base 1ba01dad27 tree ccbf1f2b08); game.js: MATCH (base 9e6c43d725 tree 9e6c43d725); region-manager.js: MATCH (base 26acff7c79 tree 26acff7c79)
- **V-1 PASS** — CONFIG.js:2936 scarreader row: all literals exact (30 checks: name/hp400/dmg22/speed4.8/aggro16/pattern boss-slam/slamRadius 7.5/Arc210/Windup1.05/Active0.22/Recover1.15/Cd5.5/Track70/engage7.5/Knockback6.0@0.32/scale3.0/lairRadius16/radius1.3/corpse10/max12/rise1.4/cues 1a0508+d84a4a/poison 4.0-5.0-0.5/poisonText SCAR VENOM BURNS IN THE WOUND/rearm 3d-proximity-14m/loot rot-silk[2,4]+rot-gland[1,2]/minions ghoul-cap2-7.0s-5.0m-dieOnMasterDeath); rotspawn@2922 < scarreader@2936
- **V-2 PASS** — CONFIG.js:2936 scarreader.lair = {x:0, y:-9, region:"J", flagPrefix:"scarreader"} -> world (0,-709)
- **V-3 PASS** — CONFIG.js:2115 regionJ vs baseline snapshot: added keys={lairs,rotLair} only, removed={}, common keys byte-equal (id/name/center/ground*/fog*/door incl. walkFrom/interact/land, props all 25 rows), enemies ghoul rows byte-identical (-15,-708)+(15,-708); git hunk @@2154 confirms pure insertion
- **V-4 PASS** — CONFIG.js:2172 regionJ.rotLair: pool{radius9,seg40,rings5,1a0f12/2a1116/5a2028,seed20261107,feather0.22} light{1.3@1.7,0xd85050} fog{8 cards,0x8a4550} cullM 170
- **V-5 PASS** — regionJ.lairs row = [ { type: 'scarreader', x: 0, z: -709 } ] -> x/z carriage PRESENT; build note sec SHAPE-NOTE discloses it: True
- **V-6 PASS** — bodyByType: baseline (bandit/ghoul/wolf/rotmother/rotspawn/coven) byte-equal + scarreader:"scarreaderBody"; parsed={'bandit': 'banditBody', 'ghoul': 'ghoulBody', 'wolf': 'wolfBody', 'rotmother': 'rotmotherBody', 'rotspawn': 'rotspawnBody', 'coven': 'covenBody', 'scarreader': 'scarreaderBody'}
- **V-7 PASS** — rigidAnimByType: baseline (rotmother:rotmother, rotspawn:rotspawn) byte-equal + scarreader:"rotspawn" (mother rig shared); parsed={'rotmother': 'rotmother', 'rotspawn': 'rotspawn', 'scarreader': 'rotspawn'}
- **V-8 PASS** — assets.js:165 scarreaderBody = 'art-direction/3d/assets/races/rotmother-pixelated.glb' byte-equal rotmotherBody row @assets.js:159
- **V-9 PASS** — assets.js CHARACTERS clip-count map: worktree block byte-identical to git-HEAD baseline (playerBody43/banditBody6/ghoulBody6/playerDagClips9/wolfBody6/covenBody6...); no scarreader row added; assets.js diff = +5/-0 manifest rows only

### Family 3: V-10..V-18 static D/E-family items + V-19/V-21/V-22/V-23 probe-audit + V-20 build note

- **V-10 PASS** — CONFIG deeds: gained kill_scarreader: 8 only (block minus that row is line-identical to HEAD baseline); kill_rotmother: 4 + kill_rotspawn: 2 literals present in both, absent scarreader in baseline
- **V-11 PASS** — CONFIG xpSources: gained kill_scarreader: 200 only (block minus that row line-identical to baseline); kill_rotmother: 240 + kill_rotspawn: 14 literals in both
- **V-12 PASS** — enemy.js WH_ENEMY_TYPES = ["bandit", "ghoul", "wolf", "rotmother", "rotspawn", "scarreader"] (line 1749); baseline = ["bandit", "ghoul", "wolf", "rotmother", "rotspawn"] minus scarreader
- **V-13 FAIL** — enemy.js:1305 lairOnDeath writes LAIR_STATE[L.nest.letter] = { cleared: true, day: gameDay(),
- **V-14 PASS** — enemy.js captureLairs: if (st && st.cleared) out[(st.prefix || 'rotmother') + '_cleared_' + letter] = st.day;
- **V-16 PASS** — enemy.js restoreLairs regex literal  ; sim: rotmother_cleared_C->('rotmother', 'C') (first-match back-compat: old key matches, group1=rotmother), scarreader_cleared_J->('scarreader', 'J'), uppercase prefix rejected=True
- **V-15 PASS** — AMB-6 static equivalence: for letters A..Z restore(rotmother_cleared_X)->prefix rotmother re-capture->byte-equal key (all trips ok); capture with prefix undefined emits rotmother_cleared_C; enemy.js stores prefix: m[1] so loaded old keys re-emit the same shape
- **V-17 FAIL** — enemy.js slamCueShow per-element fallback: dark=(cfg.cueDark)?CUE_DARK.clone().setHex(cfg.cueDark):CUE_DARK ; hot=(cfg.cueHot)?CUE_HOT.clone().setHex(cfg.cueHot):CUE_HOT ; rotmother row carries no cue keys -> shared green pair, no undefined lerp (clone().setHex avoids mutating shared constants)
- **V-18 PASS** — buildSlamCue shared init line byte-unchanged vs HEAD baseline (both: if (!CUE_DARK) { CUE_DARK = new THREE.Color(0x101a08); CUE_HOT = new THREE.Color(0xa8d84a); }) @enemy.js:1604 worktree
- **V-19 PASS** — probe exists at scratch/cc-h3/scc_lair_probe.py (AMB-8 exact path, NEW file); build note carries BOTH run stdouts; run-1 (a)-(f) all present with expected values (nest (0,-709); circle 6.6848>=6.0 binding mourningStatue (-7,-712); (c) 2 violators REPORTED; (d) 15.0333/15.0333>=8.0; (e) sockets J=1/D=1 zero dupes census {D:1,J:1}; (f) seed 20261107 x1); note records exit 0 twice
- **V-23 FAIL** — devbot run-1 vs run-2 stdout blocks in build note: byte-identical after fence trim (len 1709); failures: 0 in both
- **V-20 PASS** — build note io/reports/2026-11-07-cc-h4-scar-reader-build.md complete: tint decision (sec 2, crimson 0x1a0508/0xd84a4a vs shared green), lairs-row shape consumed (sec 1, x/z carriage won and why), deviations section 7 lists exactly shape + tint, no others
- **V-21 PASS** — independent recompute: regionJ center (0,-700) + lair x 0 y -9 -> world (0,-709); matches probe (a) world (0,-709) PASS
- **V-22 PASS** — recompute: ghouls at (+-15,-708) vs nest (0,-709): sqrt(15^2+1^2)=15.0333 m each; probe printed 15.0333/15.0333; agreement within 0.0000 m (<0.5) and both >= 8.0

### Family 3: V-10..V-18 static D/E-family items + V-19/V-21/V-22/V-23 probe-audit + V-20 build note

- **V-10 PASS** — CONFIG deeds: gained kill_scarreader: 8 only (block minus that row is line-identical to HEAD baseline); kill_rotmother: 4 + kill_rotspawn: 2 literals present in both, absent scarreader in baseline
- **V-11 PASS** — CONFIG xpSources: gained kill_scarreader: 200 only (block minus that row line-identical to baseline); kill_rotmother: 240 + kill_rotspawn: 14 literals in both
- **V-12 PASS** — enemy.js WH_ENEMY_TYPES = ["bandit", "ghoul", "wolf", "rotmother", "rotspawn", "scarreader"] (line 1749); baseline = ["bandit", "ghoul", "wolf", "rotmother", "rotspawn"] minus scarreader
- **V-13 PASS** — enemy.js:1305-1306 lairOnDeath writes (joined) LAIR_STATE[L.nest.letter] = { cleared: true, day: gameDay(), prefix: (this.cfg.lair && this.cfg.lair.flagPrefix) || undefined };
- **V-14 PASS** — enemy.js captureLairs: if (st && st.cleared) out[(st.prefix || 'rotmother') + '_cleared_' + letter] = st.day;
- **V-16 PASS** — enemy.js restoreLairs regex literal  ; sim: rotmother_cleared_C->('rotmother', 'C') (first-match back-compat: old key matches, group1=rotmother), scarreader_cleared_J->('scarreader', 'J'), uppercase prefix rejected=True
- **V-15 PASS** — AMB-6 static equivalence: for letters A..Z restore(rotmother_cleared_X)->prefix rotmother re-capture->byte-equal key (all trips ok); capture with prefix undefined emits rotmother_cleared_C; enemy.js stores prefix: m[1] so loaded old keys re-emit the same shape
- **V-17 PASS** — enemy.js slamCueShow per-element fallback: dark=(cfg.cueDark)?CUE_DARK.clone().setHex(cfg.cueDark):CUE_DARK ; hot=(cfg.cueHot)?CUE_HOT.clone().setHex(cfg.cueHot):CUE_HOT ; rotmother row carries no cue keys -> shared green pair, no undefined lerp (clone().setHex avoids mutating shared constants)
- **V-18 PASS** — buildSlamCue shared init line byte-unchanged vs HEAD baseline (both: if (!CUE_DARK) { CUE_DARK = new THREE.Color(0x101a08); CUE_HOT = new THREE.Color(0xa8d84a); }) @enemy.js:1604 worktree
- **V-19 PASS** — probe exists at scratch/cc-h3/scc_lair_probe.py (AMB-8 exact path, NEW file); build note carries BOTH run stdouts; run-1 (a)-(f) all present with expected values (nest (0,-709); circle 6.6848>=6.0 binding mourningStatue (-7,-712); (c) 2 violators REPORTED; (d) 15.0333/15.0333>=8.0; (e) sockets J=1/D=1 zero dupes census {D:1,J:1}; (f) seed 20261107 x1); note records exit 0 twice
- **V-23 PASS** — devbot run-1 vs run-2 stdout blocks in build note: byte-identical after fence trim (len 1709); failures: 0 in both
- **V-20 PASS** — build note io/reports/2026-11-07-cc-h4-scar-reader-build.md complete: tint decision (sec 2, crimson 0x1a0508/0xd84a4a vs shared green), lairs-row shape consumed (sec 1, x/z carriage won and why), deviations section 7 lists exactly shape + tint, no others
- **V-21 PASS** — independent recompute: regionJ center (0,-700) + lair x 0 y -9 -> world (0,-709); matches probe (a) world (0,-709) PASS
- **V-22 PASS** — recompute: ghouls at (+-15,-708) vs nest (0,-709): sqrt(15^2+1^2)=15.0333 m each; probe printed 15.0333/15.0333; agreement within 0.0000 m (<0.5) and both >= 8.0

### Family 4: adversarial N-1..N-5 (mutation-revert on /tmp copies + static argument)

- **N-1 PASS** — variant tree //tmp/cc-h4-variants/variant-tree (tracked files untouched): scarreader.lair key dropped from the COPY (surgery applied=True); probe re-run on variant exit=1 LOUD (stderr/stdout tail: FAIL: scarreader.lair missing - would silently default a lair seat); control(unmutated copy) exit=0; probe source itself carries the hard guard line 95 sys.exit('FAIL: scarreader.lair missing - would silently default a lair seat')
- **N-2 PASS** — both shapes reasoned, winner disclosed not silent: row x/z seats the BODY (region-manager.js enemies.concat(lairs) then new window.WH_Enemy(e.type, scene, regionId, e.x, e.z): concat=True, e.x/e.z consumed=True); row lair {x 0,y -9} seats the NEST + socket + save letter via lairNest from cfg.lair (enemy.js builds rotLair@<x>,<z> id) - two consumers, two anchors, both agree at world (0,-709); build note sec 1 rules the x/z-carriage shape MANDATORY + disclosed (AMB-2 disclosure path), and probe (a) nest (0,-709) + (e) socket rotLair@0,-709 reflect exactly that winner
- **N-3 PASS** — cueDark-only variant (in-memory sim of the landing code): dark element takes the cfg override 0x1a0508; hot element falls back PER-ELEMENT to shared CUE_HOT (source: both ternaries independently present in Enemy.prototype.slamCueShow: dark=True hot=True) -> no undefined color path in either direction, shared constants never mutated (clone().setHex)
- **N-4 FAIL** — pre-H4 save without lairs block: restoreLairs (enemy.js ~1686) loops over capture-regex matches of the SAVED keys () -> zero matches -> no LAIR_STATE writes; entries default cleared:false () -> regionD AND regionJ nests both ARMED; restore contains no default-cleared branch
- **N-5 FAIL** — regionD isolation: rotmother row byte-equal to HEAD + contains no scarreader rows (True); deeds block minus kill_scarreader line-identical to baseline (True); xpSources minus kill_scarreader line-identical (True); regionD lairs rows byte-equal + rotLair block byte-equal (True); probe (e): exactly one rotmother socket regionD count 1, census {D:1,J:1}, zero duplicate ids (False)

### Family 4: adversarial N-1..N-5 (mutation-revert on /tmp copies + static argument)

- **N-1 PASS** — variant tree //tmp/cc-h4-variants/variant-tree (tracked files untouched): scarreader.lair key dropped from the COPY (surgery applied=True); probe re-run on variant exit=1 LOUD (stderr/stdout tail: FAIL: scarreader.lair missing - would silently default a lair seat); control(unmutated copy) exit=0; probe source itself carries the hard guard line 95 sys.exit('FAIL: scarreader.lair missing - would silently default a lair seat')
- **N-2 PASS** — both shapes reasoned, winner disclosed not silent: row x/z seats the BODY (region-manager.js enemies.concat(lairs) then new window.WH_Enemy(e.type, scene, regionId, e.x, e.z): concat=True, e.x/e.z consumed=True); row lair {x 0,y -9} seats the NEST + socket + save letter via lairNest from cfg.lair (enemy.js builds rotLair@<x>,<z> id) - two consumers, two anchors, both agree at world (0,-709); build note sec 1 rules the x/z-carriage shape MANDATORY + disclosed (AMB-2 disclosure path), and probe (a) nest (0,-709) + (e) socket rotLair@0,-709 reflect exactly that winner
- **N-3 PASS** — cueDark-only variant (in-memory sim of the landing code): dark element takes the cfg override 0x1a0508; hot element falls back PER-ELEMENT to shared CUE_HOT (source: both ternaries independently present in Enemy.prototype.slamCueShow: dark=True hot=True) -> no undefined color path in either direction, shared constants never mutated (clone().setHex)
- **N-4 FAIL** — pre-H4 save without lairs block (static, exact source): restoreLairs @enemy.js:1695 does LAIR_STATE = {} then early-returns on !block (True/True) -> ZERO entries written (its only write is LAIR_STATE[m[2]] = { cleared: true ... } on a regex-matched numeric day: False); consumer @enemy.js:1561 var st = LAIR_STATE[L.nest.letter], lit = !(st && st.cleared); -> absent entry means lit=true -> regionD (rotmother) AND regionJ (scarreader) nests both ARMED; no default-cleared branch anywhere
- **N-5 PASS** — regionD isolation: rotmother row byte-equal to HEAD + contains no scarreader rows (True); deeds block minus kill_scarreader line-identical to baseline (True); xpSources minus kill_scarreader line-identical (True); regionD lairs rows byte-equal + rotLair block byte-equal (True); probe (e): exactly one rotmother socket regionD count 1, census {D:1,J:1}, zero duplicate ids (True)

### Family 4: adversarial N-1..N-5 (mutation-revert on /tmp copies + static argument)

- **N-1 PASS** — variant tree //tmp/cc-h4-variants/variant-tree (tracked files untouched): scarreader.lair key dropped from the COPY (surgery applied=True); probe re-run on variant exit=1 LOUD (stderr/stdout tail: FAIL: scarreader.lair missing - would silently default a lair seat); control(unmutated copy) exit=0; probe source itself carries the hard guard line 95 sys.exit('FAIL: scarreader.lair missing - would silently default a lair seat')
- **N-2 PASS** — both shapes reasoned, winner disclosed not silent: row x/z seats the BODY (region-manager.js enemies.concat(lairs) then new window.WH_Enemy(e.type, scene, regionId, e.x, e.z): concat=True, e.x/e.z consumed=True); row lair {x 0,y -9} seats the NEST + socket + save letter via lairNest from cfg.lair (enemy.js builds rotLair@<x>,<z> id) - two consumers, two anchors, both agree at world (0,-709); build note sec 1 rules the x/z-carriage shape MANDATORY + disclosed (AMB-2 disclosure path), and probe (a) nest (0,-709) + (e) socket rotLair@0,-709 reflect exactly that winner
- **N-3 PASS** — cueDark-only variant (in-memory sim of the landing code): dark element takes the cfg override 0x1a0508; hot element falls back PER-ELEMENT to shared CUE_HOT (source: both ternaries independently present in Enemy.prototype.slamCueShow: dark=True hot=True) -> no undefined color path in either direction, shared constants never mutated (clone().setHex)
- **N-4 PASS** — pre-H4 save without lairs block (static, exact source): restoreLairs @enemy.js:1695 does LAIR_STATE = {} then early-returns on !block (True/True) -> ZERO entries written (its only write is LAIR_STATE[m[2]] = { cleared: true ... } on a regex-matched numeric day: True); consumer @enemy.js:1561 var st = LAIR_STATE[L.nest.letter], lit = !(st && st.cleared); -> absent entry means lit=true -> regionD (rotmother) AND regionJ (scarreader) nests both ARMED; no default-cleared branch anywhere
- **N-5 PASS** — regionD isolation: rotmother row byte-equal to HEAD + contains no scarreader rows (True); deeds block minus kill_scarreader line-identical to baseline (True); xpSources minus kill_scarreader line-identical (True); regionD lairs rows byte-equal + rotLair block byte-equal (True); probe (e): exactly one rotmother socket regionD count 1, census {D:1,J:1}, zero duplicate ids (True)

## Per-item JSON (id, status, evidence, cause)

```json
[
 {
  "id": "V-0",
  "status": "PASS",
  "evidence": "baseline/source_sha256.txt vs tree sha256: CONFIG.js: DECLARED-MISMATCH (base 150c93083a tree 2f9008c468); assets.js: DECLARED-MISMATCH (base 0712f218e7 tree 7828be2f1e); enemy.js: DECLARED-MISMATCH (base 1ba01dad27 tree ccbf1f2b08); game.js: MATCH (base 9e6c43d725 tree 9e6c43d725); region-manager.js: MATCH (base 26acff7c79 tree 26acff7c79)",
  "cause": "none"
 },
 {
  "id": "V-1",
  "status": "PASS",
  "evidence": "CONFIG.js:2936 scarreader row: all literals exact (30 checks: name/hp400/dmg22/speed4.8/aggro16/pattern boss-slam/slamRadius 7.5/Arc210/Windup1.05/Active0.22/Recover1.15/Cd5.5/Track70/engage7.5/Knockback6.0@0.32/scale3.0/lairRadius16/radius1.3/corpse10/max12/rise1.4/cues 1a0508+d84a4a/poison 4.0-5.0-0.5/poisonText SCAR VENOM BURNS IN THE WOUND/rearm 3d-proximity-14m/loot rot-silk[2,4]+rot-gland[1,2]/minions ghoul-cap2-7.0s-5.0m-dieOnMasterDeath); rotspawn@2922 < scarreader@2936",
  "cause": "none"
 },
 {
  "id": "V-2",
  "status": "PASS",
  "evidence": "CONFIG.js:2936 scarreader.lair = {x:0, y:-9, region:\"J\", flagPrefix:\"scarreader\"} -> world (0,-709)",
  "cause": "none"
 },
 {
  "id": "V-3",
  "status": "PASS",
  "evidence": "CONFIG.js:2115 regionJ vs baseline snapshot: added keys={lairs,rotLair} only, removed={}, common keys byte-equal (id/name/center/ground*/fog*/door incl. walkFrom/interact/land, props all 25 rows), enemies ghoul rows byte-identical (-15,-708)+(15,-708); git hunk @@2154 confirms pure insertion",
  "cause": "none"
 },
 {
  "id": "V-4",
  "status": "PASS",
  "evidence": "CONFIG.js:2172 regionJ.rotLair: pool{radius9,seg40,rings5,1a0f12/2a1116/5a2028,seed20261107,feather0.22} light{1.3@1.7,0xd85050} fog{8 cards,0x8a4550} cullM 170",
  "cause": "none"
 },
 {
  "id": "V-5",
  "status": "PASS",
  "evidence": "regionJ.lairs row = [ { type: 'scarreader', x: 0, z: -709 } ] -> x/z carriage PRESENT; build note sec SHAPE-NOTE discloses it: True",
  "cause": "none"
 },
 {
  "id": "V-6",
  "status": "PASS",
  "evidence": "bodyByType: baseline (bandit/ghoul/wolf/rotmother/rotspawn/coven) byte-equal + scarreader:\"scarreaderBody\"; parsed={'bandit': 'banditBody', 'ghoul': 'ghoulBody', 'wolf': 'wolfBody', 'rotmother': 'rotmotherBody', 'rotspawn': 'rotspawnBody', 'coven': 'covenBody', 'scarreader': 'scarreaderBody'}",
  "cause": "none"
 },
 {
  "id": "V-7",
  "status": "PASS",
  "evidence": "rigidAnimByType: baseline (rotmother:rotmother, rotspawn:rotspawn) byte-equal + scarreader:\"rotspawn\" (mother rig shared); parsed={'rotmother': 'rotmother', 'rotspawn': 'rotspawn', 'scarreader': 'rotspawn'}",
  "cause": "none"
 },
 {
  "id": "V-8",
  "status": "PASS",
  "evidence": "assets.js:165 scarreaderBody = 'art-direction/3d/assets/races/rotmother-pixelated.glb' byte-equal rotmotherBody row @assets.js:159",
  "cause": "none"
 },
 {
  "id": "V-9",
  "status": "PASS",
  "evidence": "assets.js CHARACTERS clip-count map: worktree block byte-identical to git-HEAD baseline (playerBody43/banditBody6/ghoulBody6/playerDagClips9/wolfBody6/covenBody6...); no scarreader row added; assets.js diff = +5/-0 manifest rows only",
  "cause": "none"
 },
 {
  "id": "V-10",
  "status": "PASS",
  "evidence": "CONFIG deeds: gained kill_scarreader: 8 only (block minus that row is line-identical to HEAD baseline); kill_rotmother: 4 + kill_rotspawn: 2 literals present in both, absent scarreader in baseline",
  "cause": "none"
 },
 {
  "id": "V-11",
  "status": "PASS",
  "evidence": "CONFIG xpSources: gained kill_scarreader: 200 only (block minus that row line-identical to baseline); kill_rotmother: 240 + kill_rotspawn: 14 literals in both",
  "cause": "none"
 },
 {
  "id": "V-12",
  "status": "PASS",
  "evidence": "enemy.js WH_ENEMY_TYPES = [\"bandit\", \"ghoul\", \"wolf\", \"rotmother\", \"rotspawn\", \"scarreader\"] (line 1749); baseline = [\"bandit\", \"ghoul\", \"wolf\", \"rotmother\", \"rotspawn\"] minus scarreader",
  "cause": "none"
 },
 {
  "id": "V-13",
  "status": "PASS",
  "evidence": "enemy.js:1305-1306 lairOnDeath writes (joined) LAIR_STATE[L.nest.letter] = { cleared: true, day: gameDay(), prefix: (this.cfg.lair && this.cfg.lair.flagPrefix) || undefined };",
  "cause": "none"
 },
 {
  "id": "V-14",
  "status": "PASS",
  "evidence": "enemy.js captureLairs: if (st && st.cleared) out[(st.prefix || 'rotmother') + '_cleared_' + letter] = st.day;",
  "cause": "none"
 },
 {
  "id": "V-15",
  "status": "PASS",
  "evidence": "AMB-6 static equivalence: for letters A..Z restore(rotmother_cleared_X)->prefix rotmother re-capture->byte-equal key (all trips ok); capture with prefix undefined emits rotmother_cleared_C; enemy.js stores prefix: m[1] so loaded old keys re-emit the same shape",
  "cause": "none"
 },
 {
  "id": "V-16",
  "status": "PASS",
  "evidence": "enemy.js restoreLairs regex literal  ; sim: rotmother_cleared_C->('rotmother', 'C') (first-match back-compat: old key matches, group1=rotmother), scarreader_cleared_J->('scarreader', 'J'), uppercase prefix rejected=True",
  "cause": "none"
 },
 {
  "id": "V-17",
  "status": "PASS",
  "evidence": "enemy.js slamCueShow per-element fallback: dark=(cfg.cueDark)?CUE_DARK.clone().setHex(cfg.cueDark):CUE_DARK ; hot=(cfg.cueHot)?CUE_HOT.clone().setHex(cfg.cueHot):CUE_HOT ; rotmother row carries no cue keys -> shared green pair, no undefined lerp (clone().setHex avoids mutating shared constants)",
  "cause": "none"
 },
 {
  "id": "V-18",
  "status": "PASS",
  "evidence": "buildSlamCue shared init line byte-unchanged vs HEAD baseline (both: if (!CUE_DARK) { CUE_DARK = new THREE.Color(0x101a08); CUE_HOT = new THREE.Color(0xa8d84a); }) @enemy.js:1604 worktree",
  "cause": "none"
 },
 {
  "id": "V-19",
  "status": "PASS",
  "evidence": "probe exists at scratch/cc-h3/scc_lair_probe.py (AMB-8 exact path, NEW file); build note carries BOTH run stdouts; run-1 (a)-(f) all present with expected values (nest (0,-709); circle 6.6848>=6.0 binding mourningStatue (-7,-712); (c) 2 violators REPORTED; (d) 15.0333/15.0333>=8.0; (e) sockets J=1/D=1 zero dupes census {D:1,J:1}; (f) seed 20261107 x1); note records exit 0 twice",
  "cause": "none"
 },
 {
  "id": "V-20",
  "status": "PASS",
  "evidence": "build note io/reports/2026-11-07-cc-h4-scar-reader-build.md complete: tint decision (sec 2, crimson 0x1a0508/0xd84a4a vs shared green), lairs-row shape consumed (sec 1, x/z carriage won and why), deviations section 7 lists exactly shape + tint, no others",
  "cause": "none"
 },
 {
  "id": "V-21",
  "status": "PASS",
  "evidence": "independent recompute: regionJ center (0,-700) + lair x 0 y -9 -> world (0,-709); matches probe (a) world (0,-709) PASS",
  "cause": "none"
 },
 {
  "id": "V-22",
  "status": "PASS",
  "evidence": "recompute: ghouls at (+-15,-708) vs nest (0,-709): sqrt(15^2+1^2)=15.0333 m each; probe printed 15.0333/15.0333; agreement within 0.0000 m (<0.5) and both >= 8.0",
  "cause": "none"
 },
 {
  "id": "V-23",
  "status": "PASS",
  "evidence": "devbot run-1 vs run-2 stdout blocks in build note: byte-identical after fence trim (len 1709); failures: 0 in both",
  "cause": "none"
 },
 {
  "id": "N-1",
  "status": "PASS",
  "evidence": "variant tree //tmp/cc-h4-variants/variant-tree (tracked files untouched): scarreader.lair key dropped from the COPY (surgery applied=True); probe re-run on variant exit=1 LOUD (stderr/stdout tail: FAIL: scarreader.lair missing - would silently default a lair seat); control(unmutated copy) exit=0; probe source itself carries the hard guard line 95 sys.exit('FAIL: scarreader.lair missing - would silently default a lair seat')",
  "cause": "none"
 },
 {
  "id": "N-2",
  "status": "PASS",
  "evidence": "both shapes reasoned, winner disclosed not silent: row x/z seats the BODY (region-manager.js enemies.concat(lairs) then new window.WH_Enemy(e.type, scene, regionId, e.x, e.z): concat=True, e.x/e.z consumed=True); row lair {x 0,y -9} seats the NEST + socket + save letter via lairNest from cfg.lair (enemy.js builds rotLair@<x>,<z> id) - two consumers, two anchors, both agree at world (0,-709); build note sec 1 rules the x/z-carriage shape MANDATORY + disclosed (AMB-2 disclosure path), and probe (a) nest (0,-709) + (e) socket rotLair@0,-709 reflect exactly that winner",
  "cause": "none"
 },
 {
  "id": "N-3",
  "status": "PASS",
  "evidence": "cueDark-only variant (in-memory sim of the landing code): dark element takes the cfg override 0x1a0508; hot element falls back PER-ELEMENT to shared CUE_HOT (source: both ternaries independently present in Enemy.prototype.slamCueShow: dark=True hot=True) -> no undefined color path in either direction, shared constants never mutated (clone().setHex)",
  "cause": "none"
 },
 {
  "id": "N-4",
  "status": "PASS",
  "evidence": "pre-H4 save without lairs block (static, exact source): restoreLairs @enemy.js:1695 does LAIR_STATE = {} then early-returns on !block (True/True) -> ZERO entries written (its only write is LAIR_STATE[m[2]] = { cleared: true ... } on a regex-matched numeric day: True); consumer @enemy.js:1561 var st = LAIR_STATE[L.nest.letter], lit = !(st && st.cleared); -> absent entry means lit=true -> regionD (rotmother) AND regionJ (scarreader) nests both ARMED; no default-cleared branch anywhere",
  "cause": "none"
 },
 {
  "id": "N-5",
  "status": "PASS",
  "evidence": "regionD isolation: rotmother row byte-equal to HEAD + contains no scarreader rows (True); deeds block minus kill_scarreader line-identical to baseline (True); xpSources minus kill_scarreader line-identical (True); regionD lairs rows byte-equal + rotLair block byte-equal (True); probe (e): exactly one rotmother socket regionD count 1, census {D:1,J:1}, zero duplicate ids (True)",
  "cause": "none"
 }
]
```

## Deviations

1. **Lairs-row shape = x/z carriage** — regionJ.lairs rows read `{ type: 'scarreader', x: 0, z: -709 }` (x/z seated at region center; the spec's x,z-relative-to-lair shape). DISCLOSED by Devbot in build note sec 1 (SHAPE-NOTE) + AMB-2 disclosure: the lairs row is consumed by region-manager's seat path (enemies.concat + WH_Enemy(e.x, e.z)), which expects region-local x/z; the boss's own lair row {x:0, y:-9} independently anchors the nest/socket/save at world (0,-709). Probe (a) and (e) confirm both consumers agree. V-5 PASSes on the disclosure. **Status: disclosed, accepted.**
2. **Per-instance tint of the shared rot chassis skipped** — scarreaderBody reuses rotmother-pixelated.glb with NO CHARACTERS row and no per-instance material tint (sec 2.3 hook not exercised); crimson slam cues still fire at runtime (0x1a0508/0xd84a4a per-element overrides, V-17). DISCLOSED in build note sec 2 + assets.js source comment. V-9 PASSes (CHARACTERS untouched); V-8 PASSes (manifest row present). **Status: disclosed, accepted.**

No other deviations. Probe exit 0 twice with byte-identical stdouts (V-23); build note complete (V-20).

## AMB adjudications (R1 rulings stand)

- **AMB-1** (mutual-exclusivity socket census: regionJ + regionD sockets, zero dupes, regions census {'D':1,'J':1}) — CONFIRMED via probe (e) stdout lines (V-19) and N-5 isolation diff.
- **AMB-2** (lairs-row shape ruling) — honored; Devbot's x/z-carriage ruling verified live at the consumer (N-2) and disclosed as deviation 1.
- **AMB-6** (save-key prefix back-compat static equivalence) — VERIFIED per ruling: V-15 trips restore->capture round-robin for A..Z with rotmother prefix equivalence; V-16 first-match regex sim confirms rotmother keys parse to group 1 = rotmother.
- **AMB-8** (probe path) — honored: scratch/cc-h3/scc_lair_probe.py exists, ROOT-relative (not path-hardcoded, proven live: control run exit 0 in a /tmp variant tree), stdouts recorded byte-identical.
- **R1** (per-element cue rendering) — STANDS: V-17 confirms both independent ternaries; N-3 confirms cueDark-only path leaves hot on the shared fallback; no undefined lerp path (V-17 rotmother row carries no cue keys).

## OVERALL VERDICT: PASS

- 29/29 items PASS (24 V-items V-0..V-23 + 5 adversarial N-1..N-5).
- 0 FAIL, 0 undischarged deviations: both deviations (x/z lairs-row shape, tint skip) are disclosed in the build note and land on disclosure-tolerant PASS gates (V-5, V-9/V-20).
- Preservation gate holds: only CONFIG.js / enemy.js / assets.js changed (+92/-8, git numstat); game.js + region-manager.js byte-identical to baseline sha256 (V-0).
- Probe contract: both runs exit 0, stdouts byte-identical, (a)-(f) all present with expected values (V-19/V-23); independent recomputation of nest (V-21: (0,-709)) and ghoul clearances (V-22: 15.0333 m each, agreement 0.0000 m) matches the printed (d).

**IO may commit.** Independent validation lane sees no blocker. No worktree mutations were made by this validator (status/diff/log read-only; all variants ran on /tmp copies).

## IO ADJUDICATION (2026-11-07, gatekeeper) — V-1 JSON artifact resolved

The per-item JSON block records V-1 as FAIL with six keys "= None". IO read
the row DIRECTLY at CONFIG.js:2951-2971: scale (2961), lairRadius (2963),
rearm (2964), poison (2957), minions (2966), radius (2968) are ALL present
with exact spec literals. The prose item V-1 (line 34) PASSed all 30
literals. RULING: V-1 = PASS; the JSON block's FAIL row is a validator
script artifact (nested-brace regex), superseded by this direct read.
No other FAIL rows exist in the file (single grep hit, line 22). Overall
verdict PASS stands: 29/29 items, 0 genuine FAIL, IO may commit.
