# CC-H5b VALSPEC — Traps as Authored Hazards (Testerbot lane)

- Spec of record: `io/specs/cc-h5b-hazards-spec.md` (binding). Baseline: HEAD `df082e4` on `feat/world-visuals` (worktree `/tmp/wh-worldfeat`). Prototype paths under `prototype/` (CONFIG/region-defs live at `prototype/js/`).
- Check mapping: **V-1..V-10 ↔ spec section F items 1..10, one-to-one**. Probe AUDIT (PA-1/PA-2) rides V-7. Static lane: NO harness, NO headless browser, NO git mutations (status/log/diff permitted). Report-first: verdict to `io/reports/cc-h5b-hazards-validation.md` before the summary.

## BV-0 PRE-STATE (record raw before any build lands)

- `git -C /tmp/wh-worldfeat rev-parse HEAD` → `df082e432584988c9c8646607a896b0bd659cf28` (short `df082e4`); all `git diff/show` commands below use `df082e4`.
- `git -C /tmp/wh-worldfeat status --porcelain` at spec time = ONLY `?? io/specs/cc-h5b-hazards-spec.md`. Post-build ADDITIONS expected: `prototype/js/CONFIG.js`, `prototype/js/game.js`, `prototype/js/region-manager.js` (0–6 lines, may be absent), `prototype/js/hazards.js`, `prototype/index.html`, `prototype/builds/v8-playable.html`, `scratch/cc-h5b/*`, `io/reports/*`, `io/specs/cc-h5b-hazards-valspec.md`. ANY other dirty path ⇒ report + do not touch (blocking).
- Pre-build floors (recorded at df082e4): `grep -c hazard prototype/js/CONFIG.js` = **0**; `grep -rc WH_HAZARDS prototype/js/ | grep -v ':0'` = empty; `test ! -e prototype/js/hazards.js` passes; `ls scratch/cc-h5b/` absent. These flip non-zero only when Devbot's build lands.
- No separate baseline copy: every byte-compare extracts HEAD text via `git show df082e4:<path>`.

## V-1 CONFIG PARSE + HAZARD BLOCKS (F1)

Run from worktree root:
```
node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var C=window.WH_CONFIG,K=C.regionK,H=K.hazards,G=C.hazards;console.log(JSON.stringify({ventN:H.vents.length,vents:H.vents,hk:Object.keys(H),gk:Object.keys(G),rk:Object.keys(K)}))"
```
Key-set diff vs HEAD (only `hazards` may appear):
```
git show df082e4:prototype/js/CONFIG.js > /tmp/cc-h5b-config-head.js
node -e "global.window={};eval(require('fs').readFileSync('/tmp/cc-h5b-config-head.js','utf8'));console.log(Object.keys(window.WH_CONFIG.regionK).sort().join(','))" | tee /tmp/cc-h5b-rk-head.txt
node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));console.log(Object.keys(window.WH_CONFIG.regionK).sort().join(','))" | tee /tmp/cc-h5b-rk-new.txt
diff /tmp/cc-h5b-rk-head.txt /tmp/cc-h5b-rk-new.txt
```
Assert: vents length **4** with seats deep-equaling B1's table {x:-5.5,z:-864},{x:6.5,z:-869},{x:-6.0,z:-894},{x:3.0,z:-897}; `hk` = exactly {vents,idleSec,warnSec,blastSec,lingerSec,radiusM,warnRadiusM,blastRadiusM,heightM,damage,hitStop,cueHex,cardIdleHex,cardBlastHex,shakeM,staggerMeters} (16 keys, values per B1: cueHex 0xd84a4a, damage 14, hitStop 0.10, staggerMeters 4.0); `gk` = exactly {enabled,regionIds,hitCooldownSec,toastText,firstHitOnly} (5); `rk` diff shows ONLY the added key `hazards`. **FAIL ⇒ BLOCKING.**

## V-2 LOAD ORDER (F2)

`node --check prototype/js/hazards.js prototype/js/CONFIG.js` (each exits 0), then:
`grep -n "region-manager.js\|hazards.js\|ambush.js\|game.js" prototype/index.html`
Assert exactly ONE `hazards.js` line, whose line number sits strictly between the `region-manager.js` line (was 65 at df082e4) and the `game.js` line (was 77); the ambush.js line stays between them too (hazards may sit before or after ambush.js inside the band — ambush-relative order is NOT gated). **FAIL ⇒ BLOCKING.**

## V-3 BUILD HOOK + DISPOSE/TEXTURE LAW (F3)

Static audit:
```
grep -n "wh-hazards" prototype/js/region-manager.js prototype/js/hazards.js prototype/js/game.js
grep -c "new THREE.PointLight\|scene.add(" prototype/js/hazards.js
grep -c "particle-ember" prototype/js/hazards.js
```
Assert (a) `wh-hazards` group name present and built as a region-group child via the `CFG.hazards.regionIds` gate (contains `tithe_vaults` — read from the V-1 object, not a literal); (b) ZERO `new THREE.PointLight` and ZERO `scene.add(` in hazards.js (region-group child law; a region-manager guarded call of max +6 lines is C/E-permitted, counted via V-9's diff, disclosed); (c) `particle-ember` appears exactly ONCE (one shared texture load; sprites clone/reuse it — sprite cards ride game.flameCards' existing texture at game.js:176-191, so 0 is also PASS, disclosed); (d) disposeRegion path untouched in region-manager beyond the guarded hook (V-9 diff gates it) and no second texture/asset load in hazards.js (grep `png|glb` non-ember ⇒ FAIL). Runtime group inspection is out of lane (no browser); the child-of-region-group law is the static guarantee. **(a),(b),(d) MISSING ⇒ BLOCKING; (c) off-by-one ⇒ disclosed.**

## V-4 TICK PHASE MACHINE + DE-SYNC (F4)

Parse + on-paper math (no randomness; run from worktree root):
```
node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var H=window.WH_CONFIG.regionK.hazards;var c=H.idleSec+H.warnSec+H.blastSec+H.lingerSec;console.log(JSON.stringify({cycle:c,seq:['idle','warn','blast','linger'],off:[0,1.3,2.6,3.9]}))"
grep -n "idle\|warn\|blast\|linger" prototype/js/hazards.js | head -40
grep -c "Math.random" prototype/js/hazards.js
```
Assert: cycle = 6.0+1.5+0.9+0.6 = **9.0 s**; hazards.js implements idle→warn→blast→linger→idle with per-vent independent timers (each phase name present with CFG-key reads `idleSec/warnSec/blastSec/lingerSec`); de-sync = phase-0 offset `i * 1.3` (any equivalent arithmetic expression PASSes; absent ⇒ disclosed); `Math.random` count **0** in hazards.js (probeState must be pure; any nonzero ⇒ disclosed + re-audit whether it touches phase/damage — touching ⇒ BLOCKING). Phase-order wrong or timers not read from CFG ⇒ **BLOCKING**.

## V-5 DAMAGE LAW (F5)

```
grep -n "takeDamage\|resolveIncomingHit\|parry\|block\|hitDone\|hitCooldownSec" prototype/js/hazards.js
```
Assert: player-hurt call is `player.takeDamage(<damage>)` DIRECT (no attacker argument passed, so game.js:1363's `resolveIncomingHit(amount, attacker)` path is unreachable — resolveIncomingHit must NOT appear in hazards.js); `hitDone` present (one hit per vent-cycle); `hitCooldownSec` read from `CFG.hazards` (GLOBAL gate across vents, not per-vent state); i-frame gate is inherited — quote player.js:1812-1813 (`takeDamage` returns early on `this.iframes > 0` or non-alive state) in the report; knockback+hitStop+shake+toast wired (grep `staggerMeters|shake|toast` all non-zero, toast gated by firstHitOnly). Channel-name deviations for hit-stop/shake are C3-declared (use whatever game.js exposes, disclose) ⇒ **disclosed only**; resolveIncomingHit present or a second damage event per cycle ⇒ **BLOCKING**.

## V-6 LIGHT + POOL DISCIPLINE (F6)

PoolTick body byte-identity (span by content anchor, closing first `  }` at 2-space indent after `function poolTick(dt) {`):
```
awk '/function poolTick\(dt\)/,/^  \}/' prototype/js/game.js > /tmp/cc-h5b-pooltick-new.txt
git show df082e4:prototype/js/game.js | awk '/function poolTick\(dt\)/,/^  \}/' > /tmp/cc-h5b-pooltick-head.txt
cmp /tmp/cc-h5b-pooltick-head.txt /tmp/cc-h5b-pooltick-new.txt && echo POOLTICK-VIRGIN
```
computeSockets growth cap (C4: max +5 lines):
```
awk '/function computeSockets\(\)/,/^  \}/' prototype/js/game.js > /tmp/cc-h5b-sock-new.txt
git show df082e4:prototype/js/game.js | awk '/function computeSockets\(\)/,/^  \}/' > /tmp/cc-h5b-sock-head.txt
diff /tmp/cc-h5b-sock-head.txt /tmp/cc-h5b-sock-new.txt | grep -c "^[<>]"
```
Assert: POOLTICK-VIRGIN (0-line body diff); socket rows for vents only during warn/blast and carry `noCard:true` + color from `cueHex` (grep `noCard|cueHex` in hazards.js/socket-push span); pooled slots never held at rest — row emission is conditional on phase (source check: `grep -n "warn\|blast" prototype/js/hazards.js` shows the socket condition). PoolTick span ≠ HEAD ⇒ **BLOCKING (spec F6 verbatim)**; computeSockets growth > 5 lines ⇒ disclosed; missing noCard/cueHex row keys ⇒ **BLOCKING** (lastSockets consumers law, C4).

## V-7 PLACEMENT PROBE RUN + PROBE AUDIT (F7 + PA)

Run twice from worktree root (determinism):
```
python3 scratch/cc-h5b/probe_placement.py; python3 scratch/cc-h5b/probe_placement.py
```
Assert: exit **0** on both; stdout prints a **per-vent PASS table (4 rows, every seat)** + corridor-cycle analysis + the C2 audit lines (no-new-lights grep, no-new-assets manifest grep, draw-call/sprite count ≤8 sprites + ≤4 pipe clones); two runs' clearing lines byte-identical (timestamps aside — probeState is pure). **PROBE AUDIT — PA-1 anti-hardcode scan (blocking):**
```
grep -nE "(-5[.]5)|(6[.]5)|(-6[.]0)|(^|[^0-9.])3[.]0($|[^0-9.])" scratch/cc-h5b/probe_placement.py
```
MUST print nothing: the probe carries NO vent coordinate literals in its source — every seat is read from the eval'd `WH_CONFIG.regionK.hazards.vents` table (the CONFIG table itself is the only place the coordinates exist); any hit ⇒ probe is hardcoding, V-7 FAIL (a probe failure amends the seat, never the law — and a hardcoded probe cannot be trusted to amend). Advisory (report-only): grep −864/−869/−894/−897 the same way. **PA-2 seat-source proof (blocking):** `grep -n "readFileSync\|WH_CONFIG\|hazards.vents" scratch/cc-h5b/probe_placement.py` shows (1) eval of `prototype/js/CONFIG.js` + `prototype/js/region-defs.js` and (2) seat iteration from the parsed hazards table, not a copied list. Exit ≠ 0, missing table, PA-1 hit, or PA-2 absence ⇒ **BLOCKING**.

## V-8 SYNTAX + REBUILD + MARKER (F8)

```
for f in js/CONFIG.js js/hazards.js js/game.js js/region-manager.js; do node --check prototype/$f || echo BAD $f; done
python3 tools/build_v8.py
grep -c "CC-H5b" prototype/builds/v8-playable.html
```
Assert: no BAD; build_v8.py exits 0 and its last line reports `wrote .../builds/v8-playable.html <bytes>` (regenerated, NOT hand-edited — V-9's index/diff law plus the write timestamp confirm); bundle grep ≥ 1 — the bundle grep on the build_v8 output is the SERVED-bytes stand-in under the no-headless law (no browser run is performed or needed). **Any BAD, build exit ≠ 0, or marker 0 ⇒ BLOCKING.**

## V-9 FILE DIFF GATES (F9)

```
for f in save enemy light inventory region-defs; do printf "%s " $f; git diff df082e4 -- prototype/js/$f.js | wc -l; done
git diff --stat df082e4 -- prototype/js/CONFIG.js prototype/js/game.js prototype/js/region-manager.js prototype/index.html
git diff df082e4 -- prototype/index.html
```
Assert (line counts): `save 0`, `enemy 0`, `light 0` — **NONZERO ⇒ BLOCKING, no disclosure escape** (spec F9 hard zeros). `inventory:` expected 0; NONZERO only with a build-note disclosure that the toast path read the EXISTING toast (`inventoryUI.toast`, no new toast channel) ⇒ **disclosed**, else FAIL. `region-defs:` expected 0 (no registration this round; nonzero ⇒ disclosed, scrutinize against V-1's key-set gate). index.html diff = exactly ONE `+` line (the script tag) ⇒ else BLOCKING. CONFIG.js ≈ +45 and game.js +2..8 (wiring) + region-manager 0..6 recorded; exceeding these envelopes without a build-note note ⇒ disclosed-deviation FAIL per the adjudication rules below.

## V-10 PLAYABILITY DEFERRAL (F10)

Process law, evidence by absence: NO harness/headless/browser smoke may have run for this round.
```
grep -rln "puppeteer\|playwright\|headless" scratch/cc-h5b/ io/reports/*cc-h5b* 2>/dev/null
```
Assert only spec/valspec-own text matches (or nothing). Playability verdict is Nicko's acceptance bar (PRIMARY law 2) — record DEFERRED, never run. A found browser-run artifact ⇒ **BLOCKING** (lane violation, not a code defect).

## ADJUDICATION RULES (shared)

- Every V-Item gets one verdict + evidence line (`CONFIG.js:NNN` / probe line / diff line). Cause REQUIRED on FAIL.
- BLOCKING = the item's named hard asserts above; a blocking FAIL fails the round until amended (probe failure amends the seat, never the law).
- Disclosed-class escapes: region-manager hook lines ≤6, computeSockets ≤+5, game.js wiring, hit-stop/shake channel names, inventory.js toast touch, journal flavor append (C5), hazards.js size 200-260, index.html comment style, probe formatting. Each requires an explicit build-note disclosure in `io/reports/cc-h5b-hazards-build.md`; present-and-undisclosed ⇒ owning V-item FAIL (H4 precedent V-5 rule).
- Where spec B-section prose and section F disagree, F's floor governs; record both numbers.
- Round verdict PASS iff V-1..V-10 all PASS (incl. PA-1/PA-2 riding V-7), all disclosures present, written report-first to `io/reports/cc-h5b-hazards-validation.md`.
