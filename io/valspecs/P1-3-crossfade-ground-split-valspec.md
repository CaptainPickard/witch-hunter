# P1-3 REMAINDER — Validation Spec (fog crossfade + half-disc ground split)
Testerbot valspec for /tmp/wh-worldfeat/io/specs/P1-3-crossfade-ground-split-spec.md.
Worktree /tmp/wh-worldfeat, branch feat/world-visuals. Runner: node CLI only; NO browser,
NO HTML page open. Target files:
- /tmp/wh-worldfeat/prototype/js/game.js (applyCross ~1004, applyRegionLighting ~1374,
  cemeteryFogTick ~1395, applyDayNight ~1627, tick ~3160-3276)
- /tmp/wh-worldfeat/prototype/js/region-manager.js (whVisualGroundRadius ~305, buildRegion
  ~1841, ground disc ~1862-1876, tickTransition ~2110, cross handler ~2128-2146)
- /tmp/wh-worldfeat/prototype/js/CONFIG.js (world ~130, regionA 169, regionB 381,
  boundary 2809, preWarm ~2893, CFG.phases night fog rows 4633+)
Line refs = current HEAD; match by unique grep string when lines drift.

## AMBIGUITY RESOLUTIONS (read first; checks are written against these)
A1 boundary sign + orientation: the spec asserts "CFG.boundary.z = 25 (home A
   z<25, home B z>25)" and "A-half = { x^2+z^2 <= R_vis^2, z <= 25 }". The code
   disagrees: CONFIG.js:2811 sets boundary.z = -25, regionA spawn z=74.0
   (CONFIG.js:172, A home side z >= -25) and regionB spawn z=-45 (CONFIG.js:384,
   B side z <= -25). The valspec follows the CODE (A-half = z >= CFG.boundary.z,
   B-half = z <= CFG.boundary.z) and every plane literal in tests is derived
   from CFG.boundary.z at runtime, never the hard-coded 25; A's half is the one
   containing A's spawn z=74 (this flip mirrors the spec's, so a -z-oriented
   implementation ALSO passes if it internally flips the sign of the plane it
   reads). Flag the discrepancy in the verdict either way.
A2 marker string: spec says "agreed on dispatch" but does not fix it. Marker
   agreed = the literal string `WH_P1_3_REGIONFADE_V1`. It must appear inline in
   /tmp/wh-worldfeat/builds/v8-playable.html and come from game.js.
A3 "budget: single null check": validated structurally (inactive path = one
   guard + return; no allocations/lerps before the guard), not by timing.

## AC1 — Pure-logic checks (node; three.js NOT loaded — re-implement math)
T1 smoothstep curve: `node -e "var ss=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};var bad=0;for(var i=0;i<2001;i++){var x=i/2000,w=ss(x);if(w<0||w>1)bad=1;if(i>0&&w<ss((i-1)/2000)-1e-12)bad=1;if(x===0&&Math.abs(w)>1e-12)bad=1;if(x===1&&Math.abs(w-1)>1e-12)bad=1}process.exit(bad?1:0)" && echo T1-PASS`
T2 lerp endpoints: fade end must equal the toId night fog row + fill target.
   Expected rows (CFG.phases.night.fog, CONFIG.js:4634-4639):
   hold_outskirts { color 0x9aa0a3, density 0.012 } (regionA fogColor/fogDensity 178-179);
   darkwood_edge  { color 0x6f7477, density 0.024 } (regionB 386-387).
   Fill targets (hemiBaseIntensity 0.55, CONFIG.js:30) * ambientLightLevel *
   regionBFillMult 1.15 (CONFIG.js:38) * hemiFillMult: A (level 1.0, line 197)
   = 0.55; B (level 0.55) = 0.55*0.55*1.15 = 0.347875.
   `node -e "var lerp=(a,b,w)=>a+(b-a)*w;var e=1e-9;function ck(n,a,b){if(Math.abs(a-b)>e){console.log('FAIL '+n,a,b);process.exit(1)}}ck('w0fog',lerp(3.3,0.012,0),3.3);ck('w1fogA',lerp(3.3,0.012,1),0.012);ck('w1fogB',lerp(3.3,0.024,1),0.024);ck('fillA',0.55*1.0*1.0,0.55);ck('fillB',0.55*0.55*1.15,0.347875);console.log('T2-PASS')"`
T3 half-chord: `node -e "var R=90,p=25,xc=Math.sqrt(R*R-p*p);console.log(xc.toFixed(2));if(Math.abs(xc-86.46)>0.02)process.exit(1);if(xc.toFixed(0)!=='86')process.exit(1);console.log('T3-PASS')"`
   Runner must ALSO re-run with plane/groundRadius taken from the files:
   `node -e "var fs=require('fs'),t=fs.readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js','utf8');var R=+t.match(/groundRadius:\s*(\d+)[^\n]*playable disc/)[1];var p=+t.match(/boundary:\s*{\s*z:\s*(-?\d+)/)[1];var xc=Math.sqrt(R*R-p*p);console.log(R,p,xc.toFixed(2));if(Math.abs(xc-86.46)>0.02)process.exit(1);console.log('T3b-PASS')"`
T4 shape-winding spot test (half-disc covers the home half, chord at the plane).
   Reconstruct the constructor's numbers: rotX(-PI/2) maps geometry +y to world
   z = -y. Plane is taken from the code per A1 (may be negative); A's home half
   is the half containing A's spawn z (CONFIG.js:172 -> z=74, so A-half here is
   z >= 0 when |plane| = 25). Sample the derived arc and require every sampled
   point ON or INSIDE the circle; then assert pure half-plane membership on the
   A side (A-half = { x^2+z^2 <= R^2, z >= |plane| side } per A1):
   `node -e "var R=90,p=25,xc=Math.sqrt(R*R-p*p);var a0=Math.asin(p/R),a1=Math.PI/2+(Math.PI/2-a0);var hits=0,tot=100;for(var i=0;i<tot;i++){var a=a0+(a1-a0)*i/tot;var x=R*Math.cos(a),y=R*Math.sin(a),z=-y;if(Math.abs(z)>=p&&x*x+y*y<=R*R+1e-6)hits++}console.log('arc pts on-or-inside:',hits+'/'+tot);if(hits!==tot)process.exit(1);var inA=(x,z)=>x*x+z*z<=R*R&&z>=0;var ok=inA(0,30)&&inA(xc,25)&&inA(30,80)&&inA(60,20)&&!inA(0,-90)&&!inA(45,-10);console.log('A-home membership:',ok?'PASS':'FAIL');if(!ok)process.exit(1);console.log('T4-PASS')"`
   (T4's arc sweep samples angles asin(p/R)..(PI/2+(PI/2-asin(p/R))) through the
   rotX(-PI/2) mapping and only accepts points on |z| >= p that stay inside the
   circle — the chord half must NOT include the far side. The membership tail
   spot-checks the A home half { x^2+z^2<=R^2, z>=0 } (+z side per A1, spawn
   z=74 lives here) against A-family anchors and rejects the far half. If the
   implementation derives negative-side angles, flip the z sign — membership
   must hold for the side applyCross actually crosses into and the chord must
   still sit at CFG.boundary.z.)
T5 fog rows = CONFIG verbatim (night): grep the night block
   `grep -n "hold_outskirts: { color: 0x9aa0a3, density: 0.012" /tmp/wh-worldfeat/prototype/js/CONFIG.js`
   and `grep -n "darkwood_edge: { color: 0x6f7477, density: 0.024" /tmp/wh-worldfeat/prototype/js/CONFIG.js`
   — exactly one hit each, inside CFG.phases.night.
T6 fade duration flows only from CONFIG: `grep -n "sceneFade" /tmp/wh-worldfeat/prototype/js/CONFIG.js /tmp/wh-worldfeat/prototype/js/game.js`
   → CONFIG defines a CFG.sceneFade block with durationSec: 1.5 near preWarm
   (CONFIG.js ~2893); game.js reads CFG.sceneFade.durationSec, no other 1.5
   literal for fade timing (`grep -n "1\\.5" /tmp/wh-worldfeat/prototype/js/game.js | grep -iv "den\\|fadeout"`
   must show no new crossfade timing literal).

## AC2 — Code-walk invariants (grep/awk on game.js / region-manager.js)
T7 applyCross gate path: within applyCross (game.js ~1004) the pre-existing
   applyRegionLighting(tr.newActiveId) at line 1014 is REPLACED for gate
   crosses by the fade start. Check:
   `awk 'NR>=1004 && NR<=1022' /tmp/wh-worldfeat/prototype/js/game.js`
   and assert (a) a snapshot of live state — scene.fog.color / scene.fog.density /
   hemiLight.intensity — is taken BEFORE any overwrite, (b) the instant
   applyRegionLighting call is now conditional on NOT being a fade/gate cross,
   (c) a den-door guard exists: when tr.conn.door exists (game.js 3162-3166
   shows the conn.door shape) NO fade starts.
   Grep-able assertions (each must hit inside game.js):
   `grep -n "regionFade" /tmp/wh-worldfeat/prototype/js/game.js | head`
   expects: null init, snapshot capture in applyCross, regionFadeTick def,
   call site ~3273, pendingDispose + completion dispose.
   `grep -n "regionFade = null" /tmp/wh-worldfeat/prototype/js/game.js` (module init)
   `grep -n "fogColor.*clone\|scene.fog.color.clone" /tmp/wh-worldfeat/prototype/js/game.js`
   `grep -n "fogDensity" /tmp/wh-worldfeat/prototype/js/game.js | grep regionFade`
   `grep -n "hemiLight.intensity" /tmp/wh-worldfeat/prototype/js/game.js` — the
   snapshot line must appear at/above the fade-start lines in applyCross.
T8 tick order EXACTLY applyDayNight -> regionFadeTick -> cemeteryFogTick in the
   frame body (game.js ~3272-3274):
   `awk 'NR>=3268 && NR<=3276' /tmp/wh-worldfeat/prototype/js/game.js` (line
   numbers drift if lines were added above; if the call site is not in this
   window, locate it: `grep -n "cemeteryFogTick();" /tmp/wh-worldfeat/prototype/js/game.js`
   and inspect the 6 lines above — the ONLY lines allowed between
   applyDayNight() and cemeteryFogTick() are the regionFadeTick(dt) call and
   its comment).
   `grep -n "regionFadeTick(" /tmp/wh-worldfeat/prototype/js/game.js`
   expect definition + exactly ONE call site, between the applyDayNight() line
   and the cemeteryFogTick() line. Any other position = FAIL.
T9 dispose-only-at-completion: in region-manager.js tickTransition cross
   handler (~2128-2146) disposeRegion(oldId) is GONE (deferred to game.js):
   `awk 'NR>=2127 && NR<=2150' /tmp/wh-worldfeat/prototype/js/region-manager.js`
   — the 'cross' branch must reveal groups[newId].visible = true, keep the old
   group visible (no oldId dispose, no disposeHiddenExcept(null) there).
   In game.js the dispose lives in regionFadeTick completion:
   `grep -n "disposeRegion(pendingDispose\|disposeRegion(regionFade.pendingDispose" /tmp/wh-worldfeat/prototype/js/game.js`
   must find exactly one call inside regionFadeTick's t>=dur branch, plus the
   matching `disposeHiddenExcept(null)` on the same branch (hygiene parity with
   the old cross handler). No disposeRegion call added in applyCross itself.
T10 forceCross/switchTo/switchRegion untouched (spec design 3):
   `awk 'NR>=1019 && NR<=1030' /tmp/wh-worldfeat/prototype/js/game.js`
   switchRegion must still call applyRegionLighting(regionId) + setSkyArea
   directly (no fade) — this is the switchTo / respawn instant-swap path.
   `grep -n "forceCross" /tmp/wh-worldfeat/prototype/js/game.js /tmp/wh-worldfeat/prototype/js/region-manager.js`
   — forceCross body (region-manager.js ~2136-2148) unchanged: it must NOT
   reference regionFade at all.
   `grep -n "regionFade" /tmp/wh-worldfeat/prototype/js/region-manager.js`
   must return NOTHING (fade state lives in game.js only).
T11 C-region path untouched: buildRegion ground branch
   `awk 'NR>=1859 && NR<=1880' /tmp/wh-worldfeat/prototype/js/region-manager.js`
   — region.center (C) keeps full CircleGeometry + offset; the half-disc
   Shape/absarc construction appears ONLY in the no-center (A/B) branch.
   `grep -n "absarc\|THREE.Shape\|ShapeGeometry" /tmp/wh-worldfeat/prototype/js/region-manager.js`
   — all hits confined to the no-center ground build block (~1862).
T12 half-plane orientation: the chord geometry must use CFG.boundary.z directly
   (A1: -25). `grep -n "boundary.z" /tmp/wh-worldfeat/prototype/js/region-manager.js | head`
   — the new ground build must reference CFG.boundary.z (not a hardcoded
   25/-25). The rotX(-PI/2) mapping comment (world z = -geometry y) must be
   present or the angle derivation visibly consistent with it.

## AC3 — Budget check (structural)
T13 inactive path: read regionFadeTick def; its FIRST statements must be the
   `if (!regionFade) return;` guard (or equivalent single check) — zero
   allocations, color copies, or math before it. When active: exactly one
   THREE.Color lerp (or copy+lerpColors), two scalar lerps (fog.density,
   hemiLight.intensity), t += dt, completion = clear + ONE disposeRegion +
   ONE disposeHiddenExcept. No per-frame `new` in the tick body:
   `awk '/function regionFadeTick/,/function [a-zA-Z]+Tick/{print NR":"$0}' /tmp/wh-worldfeat/prototype/js/game.js | grep -c "new THREE"` → expect 0
   (a cached THREE.Color scratch var at module scope is allowed; if used, it
   must be declared once outside the tick body — note in verdict).

## AC4 — No new globals
T14 module-state surface: the spec (§ design 2) names exactly ONE new state
   — `regionFade = null | { t, dur, fromSnapshot, toId }` (+ the optional
   `regionFade.pendingDispose` holder, § design 3) — as a closure `var` in
   game.js, NOT a window global. window.* count delta:
   `git -C /tmp/wh-worldfeat show HEAD:prototype/js/game.js | grep -c "window\.WH_"`
   vs `grep -c "window\.WH_" /tmp/wh-worldfeat/prototype/js/game.js`
   — pre-change both are 168; delta MUST be 0 (any new window.WH_* global
   violates "no new globals beyond the documented module state", AC4).
   Same counts for region-manager.js: 41 now, delta must be 0. New bare
   global vars at top-level of game.js:
   `git -C /tmp/wh-worldfeat diff HEAD -- prototype/js/game.js | grep "^+" | grep -v "regionFade\|fillTarget\|w = smoothstep\|t += dt"`
   — any +window.X or unexpected module-scope `var` in the diff is an extra
   global; only regionFade-related declarations are allowed.
T15 no harness, no browser artifacts: no new files outside
   prototype/js/{game,region-manager,CONFIG}.js + builds/v8-playable.html:
   `git -C /tmp/wh-worldfeat diff HEAD --stat` — diff touches only the three JS
   files (build output regenerable). No test harness files, no puppeteer deps
   (`grep -in "puppeteer\\|playwright" /tmp/wh-worldfeat/package.json` → no hits).

## AC5 — Build
T16 tools/build_v8.py exists (`test -f /tmp/wh-worldfeat/tools/build_v8.py`).
T17 run `python3 /tmp/wh-worldfeat/tools/build_v8.py` from /tmp/wh-worldfeat
   (cwd ROOT); expect `wrote .../builds/v8-playable.html ... bytes`.
T18 marker: `grep -c "WH_P1_3_REGIONFADE_V1" /tmp/wh-worldfeat/builds/v8-playable.html`
   >= 1 AND the marker string is present in game.js itself
   (`grep -n "WH_P1_3_REGIONFADE_V1" /tmp/wh-worldfeat/prototype/js/game.js`)
   so the built bundle inlines it (build_v8.py inlines <script src> bodies into
   the html — nothing external). Title stamp still present:
   `grep -c "Witch Hunter v9 - EPR1 Combat (build" /tmp/wh-worldfeat/builds/v8-playable.html` = 1.
T19 regression guards in the built html: half-disc construction inlined
   (`grep -c "absarc" /tmp/wh-worldfeat/builds/v8-playable.html` >= 1) and old
   invariants intact (`grep -c "disposeHiddenExcept" /tmp/wh-worldfeat/builds/v8-playable.html` >= 1).

## Verdict template (fill, paste into report)
```
VALSPEC P1-3 xfade/split — verdict: PASS|FAIL  date: <YYYY-MM-DD>
T1 [ ] T2 [ ] T3 [ ] T3b [ ] T4 [ ] T5 [ ] T6 [ ]   # AC1 pure-logic
T7 [ ] T8 [ ] T9 [ ] T10 [ ] T11 [ ] T12 [ ]        # AC2 code-walk
T13 [ ]                                              # AC3 budget
T14 [ ] T15 [ ]                                      # AC4 globals/hygiene
T16 [ ] T17 [ ] T18 [ ] T19 [ ]                      # AC5 build
Notes/ambiguity hits: A1 plane = <value from CFG.boundary.z> ; A2 marker seen in build: <y/n>
FAIL requires: which T-id, file:line evidence, and the minimal diff to fix.
```
A PASS requires EVERY T-id checked; any single FAIL = overall FAIL. AC verdict
mapping: AC1 <- T1-T6, AC2 <- T7-T12, AC3 <- T13, AC4 <- T14-T15, AC5 <- T16-T19.
