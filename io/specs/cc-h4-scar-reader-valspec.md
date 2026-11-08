# CC-H4 'The Scar-Reader' — Validation Spec (Testerbot lane)

- Round: CC-H4
- Lane: Testerbot (validation authoring + run gate)
- Spec of record: `io/specs/cc-h4-scar-reader-spec.md` (binding; this valspec validates it item by item)
- Baseline: frozen `scratch/cc-h4/baseline/` — HEAD `3253711` (HEAD.txt), pristine tree per `git_status_pristine.txt`, `source_sha256.txt` is the preservation floor for prototype/js/{CONFIG.js,enemy.js,assets.js,game.js,region-manager.js}
- Scope: static authoring only — no git mutations (status/log/diff permitted), no browser, no harness, no build_vX, no THREE runtime probe execution by THIS lane. The Devbot probe (family F items) is audited from its saved output; Testerbot never executes it.

## Validation items

Each cites the AC family letters (A–G) of `cc-h4-scar-reader-spec.md`. Run against the live tree AFTER Devbot's build; baseline references = `scratch/cc-h4/baseline/`.

- **V-0 Preservation floor** (all): re-hash prototype/js/{CONFIG.js,enemy.js,assets.js,region-manager.js,game.js} against `baseline/source_sha256.txt`; only files the build note declares changed may MISMATCH; any silent change ⇒ round FAIL. [gate]
- **V-1 CONFIG scarreader row** (A): grep CONFIG.js row `scarreader:` — name 'The Scar-Reader', hp 400, dmg 22, speed 4.8, aggro 16, `pattern: 'boss-slam'`, slamRadius 7.5, slamArcDeg 210, slamWindup 1.05, slamActive 0.22, slamRecover 1.15, slamCooldown 5.5, slamTrackDegPerSec 70, engageRange 7.5, poison {dps 4.0, duration 5.0, slow 0.5}, poisonText present (non-empty; AMB-7), slamKnockbackM 6.0, slamKnockbackSec 0.32, cueDark 0x1a0508, cueHot 0xd84a4a, scale 3.0, lairRadius 16, rearm {days 3, trigger 'proximity', radius 14}, loot rot-silk [2,4] + rot-gland [1,2], minions {asset 'ghoul', cap 2, interval 7.0, range 5.0, dieOnMasterDeath true}, radius 1.3, corpseLingerSec 10, maxCorpses 12, riseSec 1.4; row placed AFTER `rotspawn:`. [A]
- **V-2 row lair key** (A): scarreader.lair = {x 0, y -9, region 'J', flagPrefix 'scarreader'} — exact keys, none missing, none extra. [A]
- **V-3 regionJ.lairs + regionJ isolation** (B): regionJ block (CONFIG.js:2115, id 'veil_spire_approach') gains lairs row = `[{ type: 'scarreader' }]` per family B, x/z carriage only per V-5/AMB-2; every OTHER regionJ key byte-compared vs baseline `config_snapshot.json` regionJ object —ghouls {x:-15,z:-708}/{x:15,z:-708} (CONFIG.js:2154-2155), spire-root okRuinColumn triad (0,-700)/(-8,-696)/(8,-696) (CONFIG.js:2166-2168) unchanged; only `lairs` (+`rotLair` per B) may differ. [B]
- **V-4 regionJ.rotLair** (B): pool radius 9, segments 40, rings 5, color 0x1a0f12, color2 0x2a1116, speck 0x5a2028, textureSeed 20261107, edgeFeather 0.22; light {height 1.3, intensity 1.7, color 0xd85050}; fog 8 cards color 0x8a4550 (remainder per AMB-4); cullM 170. [B]
- **V-5 x/z disclosure gate** (B): lairs row carrying x:0,z:-709 (regionD legacy shape, CONFIG.js:1381-1383) is a DEVIATION — PASS only if build note discloses it; present AND undisclosed ⇒ FAIL. [B]
- **V-6 bodyByType** (C): bodyByType (CONFIG.js:2919) gained `scarreader: 'scarreaderBody'`; existing {bandit,ghoul,wolf,rotmother,rotspawn} entries byte-unchanged vs baseline. [C]
- **V-7 rigidAnimByType** (C): rigidAnimByType (CONFIG.js:2922) gained `scarreader: 'rotspawn'`; rotmother/rotspawn entries byte-unchanged. [C]
- **V-8 asset manifest** (C): assets.js manifest gains scarreaderBody = `'art-direction/3d/assets/races/rotmother-pixelated.glb'`, byte-identical to rotmotherBody (assets.js:159). [C]
- **V-9 CHARACTERS unchanged** (C): assets.js CHARACTERS map (~assets.js:243) has NO scarreaderBody key — byte-diff vs baseline shows the map untouched. [C]
- **V-10 deeds** (C): CONFIG deeds gained `kill_scarreader: 8`; kill_rotmother: 4 (CONFIG.js:4375), kill_rotspawn: 2 (CONFIG.js:4376) byte-unchanged. [C]
- **V-11 xpSources** (C): leveling xpSources gained `kill_scarreader: 200`; kill_rotmother: 240, kill_rotspawn: 14 (CONFIG.js:4413-4414) byte-unchanged. [C]
- **V-12 types list** (C): window.WH_ENEMY_TYPES (enemy.js:1735) appends 'scarreader' — array = ['bandit','ghoul','wolf','rotmother','rotspawn','scarreader'], order otherwise intact. [C]
- **V-13 lairOnDeath prefix** (D): enemy.js lairOnDeath (~enemy.js:1301) writes LAIR_STATE under prefix from cfg.lair.flagPrefix — `LAIR_STATE[L.nest.letter] = {cleared,day}` shape preserved, prefix generalized. [D]
- **V-14 captureLairs prefix** (D): captureLairs (~enemy.js:1678) flag = `(st.prefix || 'rotmother') + '_cleared_' + letter` — capture with no prefix still emits literal `rotmother_cleared_*`. [D]
- **V-15 rotmother byte-equality** (D): old keys round-trip the NEW code paths statically — every baseline save key `rotmother_cleared_[A-Z]` matches the new restore regex, and a capture with no prefix emits `rotmother_cleared_*`; restore semantics identical to baseline code. [D]
- **V-16 restoreLairs regex** (D): restoreLairs regex (~enemy.js:1686) = `/^(prefix)_cleared_([A-Z])$/` accepting any lowercase prefix; old `rotmother_cleared_X` matches first (back-compat order or alternation). [D]
- **V-17 cue override** (E): slamCueShow (~enemy.js:1605) reads this.cfg.cueDark/cueHot falling back per AMB-3 to shared CUE_DARK/CUE_HOT; rotmother (no cue keys) still gets shared colors — no undefined lerp. [E]
- **V-18 CUE init survival** (E): buildSlamCue shared CUE_DARK/CUE_HOT init (~enemy.js:1601) byte-unchanged vs baseline. [E]
- **V-19 probe contract** (F): `scratch/cc-h3/scc_lair_probe.py` (new path per AMB-8) present at the cited path, run by Devbot clean, exit 0, prints (a)–(f). Expected printed values: (a) nest world = (0,-709); (b) clear circle centered AT nest radius >= 6.0 m; (c) J props vs slam reach r 7.5 listed as REPORTED violators (report ≠ failure); (d) both ghouls >= 8.0 m from nest; (e) census exactly one `rotLair@` scarreader socket regionJ + exactly one rotmother socket regionD, zero duplicate socket ids; (f) 20261107 unique in CONFIG.js. [F]
- **V-20 build note** (G): `io/reports/2026-11-07-cc-h4-scar-reader-build.md` exists with: tint decision (scarreader per-row red cueDark 0x1a0508 / cueHot 0xd84a4a vs shared green CUE init), lairs-row shape consumed (bare {type} vs x/z carriage, which shape won), and every numeric deviation from A–G. Missing note ⇒ G FAIL; note silent on a deviation ⇒ the owning family FAILs. [G]

## Probe-audit items (Testerbot independently derives; not Devbot's own run)

- **V-21 Nest parse recompute** (F-a): from CONFIG text alone — regionJ center (0,-700) + lairs-row x + lair y -9 — Testerbot recomputes world nest = (0,-709) and asserts the probe's (a) matches. [F-a]
- **V-22 ghoul distance recompute** (F-d): by arithmetic on CONFIG.js:2154-2155 — sqrt(15^2 + 1^2) ≈ 15.033 m from nest (0,-709) for each ghoul; probe's printed (d) distances must agree within 0.5 m and both >= 8.0. [F-d]
- **V-23 probe determinism** (F): Testerbot inspects Devbot's two consecutive probe runs (or requests the re-run): both exit 0, (a)–(f) stdout blocks byte-identical. [F]

## Adversarial block (Testerbot negative probes — static/mutation-revert)

- **N-1 lair key dropped** (A/F): working-copy variant of the scarreader row MISSING lair ⇒ must fail loudly (probe aborts / socket missing flagged), never silently default a region letter or socket. Revert.
- **N-2 lairs-row x/z vs spec shape** (B/F): working-copy lairs row `[{ type:'scarreader', x:0, z:-709 }]` alongside row lair {x 0,y -9} — which shape wins per AMB-2 (x/y lair key governs socket position; legacy x/z carriage is display/compat only unless build note rules otherwise); probe (a)/(e) must reflect the winner, not silently pick one.
- **N-3 cueDark without cueHot** (E): row carrying only cueDark ⇒ slamCueShow falls back per-element (shared hot, row dark); no undefined color path. [E]
- **N-4 old save without lairs block** (D): restore a profile whose data lacks `lairs` entirely ⇒ restoreLairs no-ops, regionD AND regionJ nests both ARMED, no default-cleared state.
- **N-5 regionD isolation** (B/F): full diff gate — rotmother row (CONFIG.js:2866-2896), regionD lairs (CONFIG.js:1381-1383) and rotLair (CONFIG.js:1254-1265), deeds/xp rotmother-rotspawn literals byte-unchanged vs baseline; probe (e) still yields exactly one rotmother socket in regionD.

## Verdict shape

- One JSON verdict per V-id + N-id: `{"id":"V-n","status":"PASS|FAIL","evidence":"<CONFIG.js:NNN or probe-line reference>","cause":"<required when FAIL>"}`.
- Deviations list: every disclosed divergence from AC families A–G (source, spec line, build-note disclosure line). An undisclosed deviation forces its family's items FAIL.
- AMB adjudication requests list AMB-1..n separately — never folded into PASS/FAIL.
- Round verdict = PASS only if ALL items PASS, all deviations disclosed, all AMBs adjudicated or explicitly waived by IO; verdict written to `io/reports/2026-11-07-cc-h4-scar-reader-validation.md` in JSON form, with the (a)–(f) probe outputs attached.

## AMB list

- **AMB-1**: B specifies regionJ `lairs` while D-generalized restoreLairs/lairSockets (~enemy.js:1700) reads ALL region rows' lairs — any other region later adopting `lairs` gets a socket automatically; accept as intended, fail-closed: v1 gate flags only regionJ+regionD.
- **AMB-2**: family B leaves the lairs-row shape open (bare `[{type:'scarreader'}]` vs regionD legacy `{type,x,z}` with disclosure) — socket position ownership (row lair x/y vs row x/z) is undefined; fail-closed: bare shape is the compliance default (V-3), N-2 must state which shape won rather than choosing silently, build note discloses any x/z carriage.
- **AMB-3**: E says per-instance cueDark/cueHot colors with fallback to shared, but does not state per-element or all-or-nothing fallback when only one cue key is present; fail-closed: per-element fallback (N-3), unless the spec of record states otherwise.
- **AMB-4**: family B fog "8 cards" is a count only — card asset/size/position fields unspecified; fail-closed: presence of 8 card rows + color checked, field-level details left to Devbot and listed in the build note.
- **AMB-5**: C's assets.js change is described as "manifest" while CONFIG-side registrations (V-6/V-7) ride bodyByType/rigidAnimByType — exact registry object names in assets.js (CHARACTERS stays untouched per C) are inferred, not quoted; fail-closed: validator greps for `scarreaderBody` in assets.js outside CHARACTERS, not for a specific object name.
- **AMB-6**: D asks "old keys round-trip new regex + capture with no prefix emits rotmother_cleared_*" as a STATIC item, but round-trip is runtime behavior; fail-closed: static equivalence proof only (regex text + emit expression read), no runtime execution in this lane.
- **AMB-7**: A requires poisonText but no exact wording; fail-closed: presence/non-empty only.
- **AMB-8**: F cites `scratch/cc-h3/scc_lair_probe.py` (an H3-path name for an H4 round); path does not exist in scratch today — treated as the required NEW path (Devbot creates it); fail-closed: item fails if probe lands at any other path without a build-note note.

## AMENDMENT R1 (2026-11-07, IO) — rulings on AMB-1..8; all ACCEPTED as fail-closed

- AMB-1 ACCEPTED: the probe additionally lists every region's lairSockets
  count; the gate asserts NO socket count changed in any region other than
  +1 in regionJ (scarreader) — regionD stays exactly 1.
- AMB-2 ACCEPTED: bare { type: 'scarreader' } is the compliance default;
  x/z carriage allowed only with build-note disclosure (spec sec 3b note).
- AMB-3 ACCEPTED: cue fallback is PER-ELEMENT — a row carrying only cueDark
  falls back to the shared CUE_HOT for the hot color, and vice versa.
- AMB-4 ACCEPTED: fog gates = cards count 8 + the exact literal keys listed
  in spec sec 3c; unnamed remainder is builder's choice within the rotLair
  fog schema.
- AMB-5 ACCEPTED: 'assets manifest' = the registry object that defines
  rotmotherBody (assets.js ~line 159); check = grep scarreaderBody present
  there, absent from the CHARACTERS clip-count map.
- AMB-6 ACCEPTED: lane D stays static-equivalence (regex accepts both key
  shapes; emission writes the prefix form). True runtime round-trip is
  Nicko-playtest territory; the probe may simulate capture->restore with a
  plain string map if cheap, optional not gating.
- AMB-7 ACCEPTED: poisonText gate = present + non-empty string.
- AMB-8 ACCEPTED: probe is CREATED by Devbot at scratch/cc-h3/
  scc_lair_probe.py exactly (cc-h3's footprint table sits in that dir).
