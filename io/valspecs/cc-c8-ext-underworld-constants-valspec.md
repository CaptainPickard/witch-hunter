# VALIDATION SPEC — CC-C8-EXT Underworld Always-Dark Completion

**Round:** CC-C8-EXT (build not yet started)
**IO spec:** io/specs/cc-c8-ext-underworld-constants-spec.md (read IN FULL before running any check)
**Predecessor round:** CC-C8 (rot_den always-dark, the precedent this round clones x6)
**Worktree:** /tmp/wh-worldfeat (branch feat/world-visuals)
**Validator:** Testerbot child (independent of Devbot; no code edits, no git ops)
**Report convention:** io/reports/2026-11-08-cc-c8-ext-validation.md
**Anchor rule:** every check pins by content anchor (key name / id string / serialized value), NEVER by line number. V-6 lesson.

---

## Pre-Change Evidence (capture BEFORE any build lands)

Run from worktree root against pre-change HEAD. Save raw bytes for after-build diff. All output under `/tmp/wh_c8ext_pre/`.

```bash
mkdir -p /tmp/wh_c8ext_pre
cd /tmp/wh-worldfeat
git rev-parse --short HEAD > /tmp/wh_c8ext_pre/HEAD.sha
wc -c prototype/js/CONFIG.js prototype/js/daynight.js > /tmp/wh_c8ext_pre/filebytes.txt
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
var fs = require('fs');
fs.writeFileSync('/tmp/wh_c8ext_pre/constantPhases.json',
  JSON.stringify(CFG.dayNight.constantPhases, null, 2));
fs.writeFileSync('/tmp/wh_c8ext_pre/dayNight.phases.night.json',
  JSON.stringify(CFG.dayNight.phases.night, null, 2));
var wanted = { E:'veil_crypt', F:'veil_galleries', I:'armory_deep',
               J:'veil_spire_approach', K:'tithe_vaults',
               L:'the_remains', D:'rot_den' };
var out = {};
Object.keys(wanted).forEach(function (k) {
  var R = CFG['region'+k];
  out[wanted[k]] = { regionKey: 'region'+k, fogColor: R.fogColor,
    fogDensity: R.fogDensity, ambientLightLevel: R.ambientLightLevel };
});
fs.writeFileSync('/tmp/wh_c8ext_pre/regionFogRows.json',
  JSON.stringify(out, null, 2));
console.log('pre-change captured');
"
```

### Snapshot invariants (assert PRE-build; re-assert POST-build as regression gate)

- I-a `Object.keys(CFG.dayNight.constantPhases)` deep-equals `["rot_den"]` (one key, no more).
- I-b `CFG.dayNight.phases.night` JSON-serializes to a value set matching `dayNight.phases.night.json` byte-for-byte after a `JSON.parse` round-trip. Anchor: keys list must include `hemiSkyColor,hemiGroundColor,hemiFillMult,lightColor,lightIntensity,azimuthDeg,elevationDeg,exposureMult,fog,zenithColor,horizonBand,horizonGlow,stars,discColor,discGlowColor,discOpacity` (16 keys, in the order produced by the source file) and `fog` must have exactly `{hold_outskirts,darkwood_edge,forest_of_the_old_king}`.
- I-c `regionFogRows.json` content matches the table below. This is ALSO the post-build assertion source for V3 fog clones.

### Verified pre-change region fog rows (HEAD 23c3b56)

IO AUDIT AMENDMENT A1 (2026-11-08, pre-build): the first-draft table listed
armory_deep with lords_hold's fog values (0x8a8f96 / 0.08) — WRONG. The
captured regionFogRows.json is authoritative. Corrected table (hex shown as
captured decimal; 0x0a0810 = 657424, 0x090710 = 591632, 0x05070a = 329482):

| areaId                | regionKey | fogColor   | fogDensity | ambientLightLevel |
|-----------------------|-----------|------------|------------|-------------------|
| veil_crypt            | regionE   | 657424     | 0.13       | 0.07              |
| veil_galleries        | regionF   | 657424     | 0.145      | 0.055             |
| armory_deep           | regionI   | 657424     | 0.13       | 0.07              |
| veil_spire_approach   | regionJ   | 657424     | 0.15       | 0.05              |
| tithe_vaults          | regionK   | 657424     | 0.16       | 0.045             |
| the_remains           | regionL   | 591632     | 0.17       | 0.04              |
| rot_den (control)     | regionD   | 329482     | 0.12       | 0.06              |

CONFIG-key law (IO): armory_deep is regionI (NOT "G" — regionG is
lords_hold, open-air, OUT of scope). doc-slot letters in planning prose are
not CONFIG keys.

---

## V1 — File scope: only the two allowed files modified by this round

**Assert:** the round's diff touches exactly `prototype/js/CONFIG.js` and
`docs/planning/64-region-registry.md` (registry-maintenance law: the
constantPhases change and its doc-64 note amendment land together); nothing
else under `prototype/` or `docs/`; `io/` is exempt (gate docs).

**Run:**
```bash
cd /tmp/wh-worldfeat
git diff --name-only HEAD | sort
```

**Pass criterion:** output is exactly two lines, sorted:
`docs/planning/64-region-registry.md`
`prototype/js/CONFIG.js`
Any other path = FAIL. (IO Amendment A2: first draft demanded one file only,
which contradicted the IO spec V11 doc-amendment requirement.)

---

## V2 — constantPhases gains exactly six new keys

**Assert:** `CFG.dayNight.constantPhases` after the build has exactly 7 keys, and the new key set is exactly the six area ids in IO spec section 2.

**Run:**
```bash
cd /tmp/wh-worldfeat
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
var ks = Object.keys(CFG.dayNight.constantPhases).sort();
console.log(JSON.stringify(ks));
"
```

**Pass criterion:** printed array deep-equals
`["armory_deep","rot_den","the_remains","tithe_vaults","veil_crypt","veil_galleries","veil_spire_approach"]`
(sorted order). Seven entries, no extras, no missing.

---

## V3 — Each new constant row: rot_den light-kin skeleton + SPEC stratum ladder + region fog verbatim

**Assert:** for each of the six new constant rows:
- Shared skeleton EXACTLY equals rot_den's values (same fields, same rationale
  as first draft): `hemiFillMult` (=1.0, ambientLightLevel not applied twice),
  `lightColor` (0xa8bce6), `lightIntensity` (= 0), `azimuthDeg` (=0),
  `elevationDeg` (=30), `discColor` (=0xdfe7f2 = 14647282 decimal),
  `discGlowColor` (=0xa8bce6).
- STRATUM LADDER (IO spec sec 2 creative rows — these are NOT rot_den clones;
  they step down with depth; the checker below asserts the spec's HEX LITERALS
  directly as JS hex — no decimal conversion anywhere, IO Amendment A4 after
  a hand-conversion error was caught in audit: hex is the only authority):
  - veil_crypt:        hemiSkyColor 0x171c2a, hemiGroundColor 0x07080a, zenithColor 0x02030a, horizonBand 0x080612, horizonGlow 0x0e0a16, stars 0.15, discOpacity 0.2, exposureMult 0.75
  - veil_galleries:    hemiSkyColor 0x151a26, hemiGroundColor 0x06070a, zenithColor 0x020307, horizonBand 0x070510, horizonGlow 0x0d0914, stars 0.12, discOpacity 0.15, exposureMult 0.75
  - armory_deep:       same values as veil_crypt exactly (built as E's family per AD1)
  - veil_spire_approach: hemiSkyColor 0x141823, hemiGroundColor 0x050609, zenithColor 0x010305, horizonBand 0x06040d, horizonGlow 0x0b0812, stars 0.10, discOpacity 0.12, exposureMult 0.72
  - tithe_vaults:      hemiSkyColor 0x12161f, hemiGroundColor 0x040507, zenithColor 0x010204, horizonBand 0x050309, horizonGlow 0x090610, stars 0.08, discOpacity 0.10, exposureMult 0.72
  - the_remains:       hemiSkyColor 0x101419, hemiGroundColor 0x030406, zenithColor 0x010203, horizonBand 0x040307, horizonGlow 0x080510, stars 0.06, discOpacity 0.08, exposureMult 0.70
- `fog` is a single-key object, key = the area id, value = `{color: <region fogColor>, density: <region fogDensity>}` from the matching `regionX` row (table in pre-change evidence).

**Run:**
```bash
cd /tmp/wh-worldfeat
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
var cp = CFG.dayNight.constantPhases;
var rot = cp.rot_den;
var SKELETON = { hemiFillMult: 1, lightColor: 0xa8bce6, lightIntensity: 0,
  azimuthDeg: 0, elevationDeg: 30, discColor: 0xdfe7f2, discGlowColor: 0xa8bce6 };
var LADDER = {
  veil_crypt:          { hemiSkyColor: 0x171c2a, hemiGroundColor: 0x07080a, zenithColor: 0x02030a, horizonBand: 0x080612, horizonGlow: 0x0e0a16, stars: 0.15, discOpacity: 0.2,  exposureMult: 0.75 },
  veil_galleries:      { hemiSkyColor: 0x151a26, hemiGroundColor: 0x06070a, zenithColor: 0x020307, horizonBand: 0x070510, horizonGlow: 0x0d0914, stars: 0.12, discOpacity: 0.15, exposureMult: 0.75 },
  armory_deep:         { hemiSkyColor: 0x171c2a, hemiGroundColor: 0x07080a, zenithColor: 0x02030a, horizonBand: 0x080612, horizonGlow: 0x0e0a16, stars: 0.15, discOpacity: 0.2,  exposureMult: 0.75 },
  veil_spire_approach: { hemiSkyColor: 0x141823, hemiGroundColor: 0x050609, zenithColor: 0x010305, horizonBand: 0x06040d, horizonGlow: 0x0b0812, stars: 0.10, discOpacity: 0.12, exposureMult: 0.72 },
  tithe_vaults:        { hemiSkyColor: 0x12161f, hemiGroundColor: 0x040507, zenithColor: 0x010204, horizonBand: 0x050309, horizonGlow: 0x090610, stars: 0.08, discOpacity: 0.10, exposureMult: 0.72 },
  the_remains:         { hemiSkyColor: 0x101419, hemiGroundColor: 0x030406, zenithColor: 0x010203, horizonBand: 0x040307, horizonGlow: 0x080510, stars: 0.06, discOpacity: 0.08, exposureMult: 0.70 }
};
var map = { veil_crypt:'regionE', veil_galleries:'regionF',
            armory_deep:'regionI', veil_spire_approach:'regionJ',
            tithe_vaults:'regionK', the_remains:'regionL' };
var fails = [];
Object.keys(map).forEach(function (area) {
  var row = cp[area];
  if (!row) { fails.push(area+': missing'); return; }
  Object.keys(SKELETON).forEach(function (k) {
    if (row[k] !== SKELETON[k]) fails.push(area+'.'+k+' skeleton mismatch: '+row[k]+' want '+SKELETON[k]);
  });
  var L = LADDER[area];
  Object.keys(L).forEach(function (k) {
    if (row[k] !== L[k]) fails.push(area+'.'+k+' ladder mismatch: '+row[k]+' want '+L[k]);
  });
  if (!row.fog) { fails.push(area+'.fog missing'); return; }
  var fk = Object.keys(row.fog);
  if (fk.length !== 1 || fk[0] !== area) { fails.push(area+'.fog keys wrong: '+JSON.stringify(fk)); return; }
  var want = CFG[map[area]];
  var got = row.fog[area];
  if (got.color !== want.fogColor)    fails.push(area+'.fog.color mismatch');
  if (got.density !== want.fogDensity) fails.push(area+'.fog.density mismatch');
});
if (fails.length) { console.log('FAIL'); fails.forEach(f => console.log(' - '+f)); process.exit(1); }
console.log('PASS');
"
```

**Pass criterion:** prints `PASS`, exits 0. Any printed FAIL line = check fails; paste full output into the report.
(IO Amendment A3: first draft asserted every scalar clones rot_den, which
contradicted the IO spec's stratum ladder creative rows. The ladder is the
spec; rot_den donates only the light-kin skeleton. Decimal values in the
ladder are the spec's hex literals; Devbot may write hex, the validator
compares numerically.)

---

## V4 — rot_den constant row NOT touched

**Assert:** the existing `constantPhases.rot_den` block is unchanged after the build.

**Run:**
```bash
cd /tmp/wh-worldfeat
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
var fs = require('fs');
var pre = JSON.parse(fs.readFileSync('/tmp/wh_c8ext_pre/constantPhases.json','utf8')).rot_den;
var post = CFG.dayNight.constantPhases.rot_den;
console.log(JSON.stringify(post) === JSON.stringify(pre) ? 'PASS' : 'FAIL');
"
```

**Pass criterion:** prints `PASS`. If FAIL, the round mutated the rot_den control row — REJECT and report.

---

## V5 — dayNight.phases.night NOT touched

**Assert:** `CFG.dayNight.phases.night` is byte-identical (after JSON round-trip) to the pre-change snapshot.

**Run:**
```bash
cd /tmp/wh-worldfeat
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
var fs = require('fs');
var pre = JSON.parse(fs.readFileSync('/tmp/wh_c8ext_pre/dayNight.phases.night.json','utf8'));
var post = JSON.parse(JSON.stringify(CFG.dayNight.phases.night));
var a = JSON.stringify(pre), b = JSON.stringify(post);
if (a === b) { console.log('PASS'); }
else { console.log('FAIL'); console.log('pre : '+a); console.log('post: '+b); process.exit(1); }
"
```

**Pass criterion:** prints `PASS`. If FAIL paste both lines into the report.

---

## V6 — Textual anchor: seven constantPhases area keys present in CONFIG.js source

**Assert (source-text level, defense against VM-load lies):** the literal substrings appear inside the `constantPhases: { … }` block. Content-anchor: block starts at the line containing `constantPhases: {` and ends at the next top-level `  },` after it.

**Run:**
```bash
cd /tmp/wh-worldfeat
awk '/^  constantPhases: \{/{f=1} f{print} f && /^  \},/{exit}' prototype/js/CONFIG.js \
  | grep -E "^    (rot_den|veil_crypt|veil_galleries|armory_deep|veil_spire_approach|tithe_vaults|the_remains):"
```

**Pass criterion:** exactly seven lines of output, one per area id, in any order. Six or fewer, or any extraneous indent level (`^    ` = 4 spaces, one level deeper than `constantPhases: {` itself) = FAIL.

---

## V7 — daynight.js unchanged

**Assert:** the round does not modify `prototype/js/daynight.js`. The constant-override wrapper at the `// CC-C8 ALWAYS-DARK:` branch and the `if (constantRow(areaId)) return;` guard in `SkyPool.prototype.setArea` are the existing mechanics this round's new rows just feed; they must not move.

**Run:**
```bash
cd /tmp/wh-worldfeat
git diff HEAD -- prototype/js/daynight.js | wc -l
```

**Pass criterion:** prints `0`. Any non-zero diff = FAIL (defense against Devbot trying to "fix" the tick or guard logic in this round).

---

## V8 — Light intensity is 0 for every new constant row (always-dark law)

**Assert:** every one of the six new rows has `lightIntensity: 0`. (Moon pinned to zero is the always-dark contract — see IO spec sec 2 note.)

**Run:**
```bash
cd /tmp/wh-worldfeat
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
['veil_crypt','veil_galleries','armory_deep','veil_spire_approach','tithe_vaults','the_remains'].forEach(a => {
  var v = CFG.dayNight.constantPhases[a] && CFG.dayNight.constantPhases[a].lightIntensity;
  console.log(a, 'lightIntensity=', v, v === 0 ? 'OK' : 'FAIL');
});
"
```

**Pass criterion:** every printed line ends with ` lightIntensity= 0 OK`. Any `FAIL` suffix on any line = check fails.

---

## V9 — Fog key inside each new constant row equals the area id

**Assert:** the nested `fog` map on each new constant row has exactly one key, and that key is the area id itself (this is what daynight.js's fog-picker keys on).

**Run:**
```bash
cd /tmp/wh-worldfeat
node -e "
global.window = {};
require('./prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
['veil_crypt','veil_galleries','armory_deep','veil_spire_approach','tithe_vaults','the_remains'].forEach(a => {
  var keys = Object.keys((CFG.dayNight.constantPhases[a]||{}).fog || {});
  console.log(a, JSON.stringify(keys), keys.length === 1 && keys[0] === a ? 'OK' : 'FAIL');
});
"
```

**Pass criterion:** every line shows a one-element array containing the area id itself and ends `OK`.

---

## V10 — Static wiring proof: constantRow lookup keys match setSkyArea feed (NO browser)

**IO Amendment A5 (2026-11-08): the first draft demanded browser/DevTools
smoke (walk into veil_crypt, read `constantHeld`). PRIMARY law 2 forbids
harness/browser validation — Nicko's playtest is the acceptance bar; V2/V3
prove the rows and the mechanism is rot_den-proven in production. Replaced
with a static wiring proof:**

**Assert:** (a) `constantRow(areaId)` in daynight.js indexes
`D.constantPhases` by the SAME id shape setSkyArea is fed (game.js region
transitions pass `tr.newActiveId` / `regionId` = region ids like
'veil_crypt'); (b) the tick override copies `state` from the constant row;
(c) SkyPool.setArea's constantRow guard retires panos. Quote the three code
sites by content anchor.

**Run:**
```bash
cd /tmp/wh-worldfeat
grep -n "function constantRow" prototype/js/daynight.js
grep -n "setSkyArea(tr.newActiveId)\|setSkyArea(regionId)" prototype/js/game.js
grep -n "if (constantRow(areaId)) return;" prototype/js/daynight.js
grep -n "copyRow(this.state, K);" prototype/js/daynight.js
node -e "
global.window = {};
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;
var ids = ['veil_crypt','veil_galleries','armory_deep','veil_spire_approach','tithe_vaults','the_remains'];
var miss = ids.filter(id => !CFG.dayNight.constantPhases[id] || !CFG.dayNight.constantPhases[id].fog[id]);
console.log(miss.length === 0 ? 'PASS key-shape: constantPhases[fog] keyed by region id' : 'FAIL ' + JSON.stringify(miss));
console.log('region ids in CONFIG match lookup keys:', ids.every(id => !!window.__probe), '');
"
```

**Pass criterion:** all four greps return hits (quotes pasted into the report)
AND node prints the PASS key-shape line. The wiring is the same code path
rot_den exercises every frame — no runtime probe needed.

**V10b — Dormant-order trace (IO spec sec 6 V9 duty, corrected by IO
2026-11-08):** quote `prototype/js/daynight.js` around the
`// CC-C8 ALWAYS-DARK:` comment (the DayNight.prototype.tick wrapper).
CONFIRMED ORDER (matches IO spec sec 4): coreTick runs FIRST; the constant
override is DORMANT-INDEPENDENT (`if (K) copyRow(this.state, K)` fires even
while dormant — correct: the den reachable pre-camp renders its constant look);
the `constantHeld` restore branch copies `D.phases[D.startPhase]` when leaving
to an area WITHOUT a constant row while the clock is frozen. Validator asserts
the quoted code shows exactly this order and adds one sentence: why the six
new rows change nothing while dormant (answer: the veil chain door is locked
while dormant, so no dormant player ever stands in E/F/I(armory)/J/K/L, and
A/B/C/lords_hold/fort_garrison have no constant rows so the override is null
there either way).

---

## V11 — Static proof: SkyPool constant branch + region-tracker id feed (NO browser)

**IO Amendment A5 (2026-11-08, same law as V10): first draft demanded
DevTools probes of live Three.js objects. Replaced with static quotes:**

**Assert:** (a) SkyPool.tick's constant branch exists and hides pano layers
in constant areas; (b) the region-transition call chain feeds setSkyArea
region ids from the same tracker that drives applyDayNight's `rid` (so
constantPhases keys resolve); (c) fog write-back: applyDayNight reads
`S.fog[rid]` — for a constant area, state.fog now carries the area's own key
(copyRow of the constant row), so fog resolves.

**Run:**
```bash
cd /tmp/wh-worldfeat
# (a) SkyPool tick constant branch
grep -n -A6 "CC-C8" prototype/js/daynight.js | sed -n 1,20p
# (b) region-tracker feed
grep -n "setSkyArea" prototype/js/game.js
# (c) fog write-back keys
grep -n "var f = S.fog\[rid\];" prototype/js/game.js
grep -n "for (k in row.fog)" prototype/js/daynight.js
```

**Pass criterion:** each grep returns the expected site (paste quotes); the
validator explains in one sentence why a constant-area state.fog carries the
area's own id key after the copyRow override (answer: copyRow iterates
`row.fog` keys, and each new row's fog is keyed by its area id — proven by
V3/V9).

---

## V12 — No stray edits: daynight.js untouched; docs/ limited to registry file

**Assert:** `prototype/js/daynight.js` byte count equals the pre-change
captured value; the ONLY doc file changed is
`docs/planning/64-region-registry.md` (the registry-maintenance amendment
V1 allows; nothing else under docs/).

**Run:**
```bash
cd /tmp/wh-worldfeat
diff <(wc -c prototype/js/daynight.js) <(grep daynight.js /tmp/wh_c8ext_pre/filebytes.txt)
git diff --name-only HEAD -- docs/
```

**Pass criterion:** `diff` prints nothing (byte count identical) AND the
second command prints exactly one line:
`docs/planning/64-region-registry.md`
(IO Amendment A6: first draft asserted docs/ count = 0, contradicting the
spec's V11 doc-amendment requirement; corrected to the one-file allowlist.)

---

## V13 — node --check + amendment-log closeout

**IO Amendment A7 (2026-11-08): first draft had no syntax gate. Added:**

**Run:**
```bash
cd /tmp/wh-worldfeat
node --check prototype/js/CONFIG.js && echo SYNTAX-OK
```

**Pass criterion:** prints `SYNTAX-OK`, exit 0.

---

## Amendment Log

(IO rulings issued mid-round are recorded here with date + IO sign-off.
Validator applies amendments in order; all amendments below were issued
PRE-build during IO's valspec audit.)

| date | ruling | IO sign-off |
|------|--------|-------------|
| 2026-11-08 | A1: pre-change armory_deep row corrected to captured values (657424 / 0.13) — first draft carried lords_hold values | IO |
| 2026-11-08 | A2: V1 allows docs/planning/64-region-registry.md (registry-maintenance law) | IO |
| 2026-11-08 | A3: V3 skeleton = rot_den light-kin fields only; creative fields assert the SPEC stratum ladder | IO |
| 2026-11-08 | A4: V3 ladder compares JS hex literals; no decimal conversions (hand-conversion error caught) | IO |
| 2026-11-08 | A5: V10/V11 browser smoke replaced with static wiring proofs (PRIMARY law 2) | IO |
| 2026-11-08 | A6: V12 docs diff allowlist = registry file only | IO |
| 2026-11-08 | A7: V13 node --check added | IO |
| 2026-11-08 | A8: V10b dormant-order trace added (IO spec sec 6 V9 duty; first draft's dormant claim was inverted, IO corrected via live code trace) | IO |

---

## Verdict Format

Final report (io/reports/2026-11-08-cc-c8-ext-validation.md) MUST end with this exact block:

```
VERDICT: PASS <x>/13
FAILED CHECKS: [none | V<n>, V<n>, ...]
NOTES:
- <free-form, one bullet per material observation>
- <evidence paths, console transcripts pasted as fenced blocks>
- <any deviations from spec that were waived by amendment>
```

- `x` = number of checks that passed out of 13.
- List every failed check by id (V1..V13). Use the exact id format.
- For any FAIL, paste the failing command's full stdout + stderr into the report body.
- Pre-change evidence (all files in `/tmp/wh_c8ext_pre/`) must be referenced from the report appendix.
- Validator signs off at the bottom: `Validated by: Testerbot (cc-c8-ext) — <ISO-8601 timestamp>`.

---

**End of valspec.** Devbot does not read this file. Builder and validator are independent. IO routes the report.
