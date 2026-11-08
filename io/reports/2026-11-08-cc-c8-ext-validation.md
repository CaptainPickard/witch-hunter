# CC-C8-EXT Validation — Underworld Constants

Date: 2026-11-08
Validator: Testerbot (independent of Devbot)
Worktree: /tmp/wh-worldfeat @ HEAD 23c3b56
Valspec: io/valspecs/cc-c8-ext-underworld-constants-valspec.md (A1–A8 applied in order)
Spec: io/specs/cc-c8-ext-underworld-constants-spec.md

Amendment rulings in effect:
- A1: V3 expected values = spec's Affected Configuration table only (ladder + fog color/density).
- A2: V3 checks `fog.color === region.fogColor`, `fog.density === region.fogDensity` (no cem* — CONFIG.js has none).
- A3: The four V10 anchors exist verbatim at HEAD; if found, use them as code evidence.
- A4: V8 is met by `lightIntensity === 0` in the area constant row.
- A5: V6 is source order only: rot_den first, remaining five in E/F/I/J/K/L spec order.
- A6: V13 non-scope = game.js/lighting.js/underground.js. lighting.js and underground.js DO NOT EXIST at HEAD — treated as out-of-scope, not a FAIL; daynight.js byte-count is compared to the pre snapshot (21098).
- A7: V12 note may live anywhere within ±10 lines of prior lines 43-44.
- A8: Pre-change evidence already captured at /tmp/wh_c8ext_pre/ (HEAD 23c3b56 pre-build).

Spec–valspec contradiction found and ruled: V13's verbatim command references `prototype/js/lighting.js` and `prototype/js/underground.js`, which do not exist at HEAD (A6 says "game.js/lighting.js/underground.js" — but only game.js and daynight.js exist). The diff-based portion of V13 (`git diff --stat HEAD -- …`) also fails for the same reason. Recorded as a spec/valspec contradiction; applied A6's ruling — non-scope files that exist get a git-diff check; non-existent files are treated as out-of-scope, not a FAIL. See NOTES.

---

## V1 — Scope

```
$ git diff --name-only HEAD | sort
docs/planning/64-region-registry.md
prototype/js/CONFIG.js
```
PASS

## V2 — Key set

```
$ node -e "...Object.keys(CFG.dayNight.constantPhases).sort()..."
["armory_deep","rot_den","the_remains","tithe_vaults","veil_crypt","veil_galleries","veil_spire_approach"]
```
PASS — exactly the 7 required keys, sorted.

## V3 — Skeleton + ladder + fog mirrors regionDefs

```
$ node -e "<full skeleton/ladder/fog comparator>"
PASS
```
PASS — all six rows carry: night skeleton (hemiFillMult 1, lightColor 0xa8bce6, lightIntensity 0, azimuthDeg 0, elevationDeg 30, discColor 0xdfe7f2, discGlowColor 0xa8bce6); ladder values (hemiSkyColor/hemiGroundColor/zenithColor/horizonBand/horizonGlow/stars/discOpacity/exposureMult) per the A1/A2-corrected table; fog single-keyed by area id; fog.color === region.fogColor and fog.density === region.fogDensity vs CONFIG[regionE/F/I/J/K/L].

## V4 — rot_den identical

```
$ node -e "<JSON.stringify(post) === JSON.stringify(pre)>"
PASS
```
PASS

## V5 — phases.night identical

```
$ node -e "<JSON pre vs JSON post>"
PASS
```
PASS

## V6 — Source order (A5)

```
$ awk '/^  constantPhases: \{/{f=1} f{print} f && /^  \},/{exit}' prototype/js/CONFIG.js \
  | grep -E "^    (rot_den|veil_crypt|veil_galleries|armory_deep|veil_spire_approach|tithe_vaults|the_remains):"
    rot_den: {
    veil_crypt: {
    veil_galleries: {
    armory_deep: {
    veil_spire_approach: {
    tithe_vaults: {
    the_remains: {
```
PASS — rot_den first; remaining five in E/F/I/J/K/L spec table order.

## V7 — daynight.js untouched

```
$ git diff HEAD -- prototype/js/daynight.js | wc -l
0
```
PASS

## V8 — Light intensity (A4)

```
$ node -e "<log lightIntensity for each of the six>"
veil_crypt lightIntensity= 0 OK
veil_galleries lightIntensity= 0 OK
armory_deep lightIntensity= 0 OK
veil_spire_approach lightIntensity= 0 OK
tithe_vaults lightIntensity= 0 OK
the_remains lightIntensity= 0 OK
```
PASS — `lightIntensity === 0` on every new row. Supporting trace (A4 chain): daynight.js:498–505 holds `copyRow(this.state, K)` every frame while in a constant area; game.js:1937–1985 `applyDayNight()` reads `dn.state` and writes `game.moonLight.intensity = S.lightIntensity` (line 1955) → 0.

## V9 — Fog key shape

```
$ node -e "<Object.keys(row.fog) for each of the six>"
veil_crypt ["veil_crypt"] OK
veil_galleries ["veil_galleries"] OK
armory_deep ["armory_deep"] OK
veil_spire_approach ["veil_spire_approach"] OK
tithe_vaults ["tithe_vaults"] OK
the_remains ["the_remains"] OK
```
PASS — each fog object has exactly one key equal to its area id.

## V10 — Code anchors (A3: anchors found at HEAD → used as code evidence)

```
$ grep -n "function constantRow" prototype/js/daynight.js
225:  function constantRow(areaId) {
$ grep -n "setSkyArea(tr.newActiveId)\|setSkyArea(regionId)" prototype/js/game.js
1122:    game.dayNight.setSkyArea(tr.newActiveId);   // C2b: area's sky variant (1s fade)
1133:    game.dayNight.setSkyArea(regionId);
$ grep -n "if (constantRow(areaId)) return;" prototype/js/daynight.js
391:    if (constantRow(areaId)) return;      // CC-C8: no pano in an always-dark area (tick hides them)
$ grep -n "copyRow(this.state, K);" prototype/js/daynight.js
500:      copyRow(this.state, K);
```
PASS — 4/4 anchors present verbatim. Dormant-order trace (supporting evidence): daynight.js:223–227 constantRow returns the row or null; daynight.js:495–505 DayNight.tick holds the constant look via copyRow on every frame in a constant area and sets constantHeld=true; daynight.js:444–453 SkyPool.tick's constant branch hides the pano A-layer, shows the dome and star/glow underlay; game.js:1122/1133 region-tracker feeds setSkyArea(tr.newActiveId)/setSkyArea(regionId) into the same code path.

## V11 — Wiring

```
--- (a) SkyPool tick constant branch ---
223:  // CC-C8 ALWAYS-DARK: the constant row of an area (CONFIG.dayNight.
224-  // constantPhases, rot_den) or null. No clock math anywhere on this path.
225:  function constantRow(areaId) {
226-    return D.constantPhases ? D.constantPhases[areaId] || null : null;
227-  }
...
391:    if (constantRow(areaId)) return;      // CC-C8: no pano in an always-dark area (tick hides them)
392-    this.retarget('time');
...
442:    // CC-C8 ALWAYS-DARK: the gradient underlay only (the constant row's
443:    // near-black dome + stars + dim disc); leaving re-targets via setArea
444:    if (constantRow(this.area)) {
445:      this.phase = dn.phase;
--- (b) region-tracker feed ---
1122:    game.dayNight.setSkyArea(tr.newActiveId);   // C2b: area's sky variant (1s fade)
1133:    game.dayNight.setSkyArea(regionId);
--- (c) fog write-back keys ---
1962:    var f = S.fog[rid];
57:    for (k in row.fog) {
```
PASS — all three anchors found.

## V12 — Registry note (A7: note found within the ±10-line window of prior lines 43-44)

```
$ sed -n 38,50p docs/planning/64-region-registry.md
  den/outcrop digging at the D/E mouths). Rim fade 240..280->skirt + rim
  mountain ridge term on C.
- save.js: additive per-message save blocks carry regionId (player
  P.regionId, camp K.respawn.regionId, message-scoped world region) with
  validRegion() guards — the pattern any new instance's save roundtrip uses.
- daynight.js: constantPhases.<regionId> = an always-dark sky row (rot_den
  today; E/F ran WITHOUT one so far — region fog/ambient only). CC-C8-EXT
  (2026-11-08) landed six constant rows: veil_crypt, veil_galleries,
  armory_deep, veil_spire_approach, tithe_vaults, the_remains; the E/F gap
  above is historical, and these underworld interiors now hold one look.
- Scatter (CONFIG.scatter): A/B/C only; D/E/F scatter:false (hand rows only).

## 2. LIVE region table (values from CONFIG.js @ d5da65a)
```
PASS — the note sits at lines 43-47 (inside the ±10-line window), names all six ids, mentions CC-C8-EXT, and carries a bracketed date.

## V13 — Scope guard (A6 ruling applied)

```
$ wc -c prototype/js/CONFIG.js prototype/js/daynight.js
364238 prototype/js/CONFIG.js
 21098 prototype/js/daynight.js
385336 total

$ diff <(pre-snapshot) <(current)
   (pre filebytes.txt was:)
   360381 prototype/js/CONFIG.js
    21098 prototype/js/daynight.js
   381479 total

$ node --check prototype/js/CONFIG.js && echo CONFIG-syntax-ok
CONFIG-syntax-ok

$ git diff --stat HEAD -- prototype/js/game.js prototype/js/lighting.js prototype/js/underground.js
   (no output)
```
PASS — daynight.js byte-identical to the pre snapshot (21098); CONFIG.js grew by exactly 3857 bytes (364238 − 360381); CONFIG.js parses; game.js has no diff; lighting.js and underground.js do not exist at HEAD and per A6 are out-of-scope, not a FAIL. See NOTES.

---

## VERDICT: PASS 13/13

## FAILED CHECKS

None.

## NOTES

1. **Spec–valspec contradiction (V13)**: the valspec's verbatim command lists `prototype/js/lighting.js` and `prototype/js/underground.js`, but neither file exists at HEAD (only `prototype/js/light.js` exists among similar names). Both `wc -c` and `git diff --stat HEAD -- …` exit non-zero on a missing path. Ruling applied per A6: "non-scope" means files that exist in the tree get a diff check; files that do not exist are out-of-scope, not a FAIL. The byte-compare and syntax-check portions of V13 still ran cleanly on the files that do exist (CONFIG.js, daynight.js). If future rounds want lighting/underground coverage, the valspec text needs to be amended to name real files (e.g. `prototype/js/light.js`).

2. **A3 in effect**: all four V10 anchors were found verbatim at HEAD, so the code evidence they provide was used directly (constantRow at daynight.js:225, setSkyArea feed at game.js:1122/1133, the pano early-return at daynight.js:391, copyRow(this.state, K) at daynight.js:500). No simulation was needed for V10.

3. **A4 in effect**: V8 was judged on `lightIntensity === 0` alone; no harness boot was run. The supporting source chain (copyRow writes state.lightIntensity every frame in a constant area, applyDayNight assigns it to game.moonLight.intensity at game.js:1955) is documented above.

4. **A6 in effect**: pre-change evidence dir /tmp/wh_c8ext_pre/ existed at HEAD 23c3b56 with all four files; the constantPhases.json held only the rot_den row, dayNight.phases.night.json held the pre-build night row — both used verbatim for V4 and V5.

5. **A7 in effect**: the registry note was found at lines 43-47, inside the ±10-line window around the prior lines 43-44; it names all six areas, mentions CC-C8-EXT, and carries the bracketed date 2026-11-08.

6. **Read-only validation**: zero changes made under prototype/js/ or docs/. The only file written by this round is this report.

Sign-off: Testerbot — 2026-11-08 — independent validation of CC-C8-EXT verdict: PASS 13/13.
