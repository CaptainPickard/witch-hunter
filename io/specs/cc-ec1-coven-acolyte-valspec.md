# VALSPEC — CC-EC1 Coven Acolyte (Testerbot, gate step 2)

Validates: `/tmp/wh-worldfeat/io/specs/cc-ec1-coven-acolyte-spec.md` (232 lines, read in full).
Worktree: `/tmp/wh-worldfeat` (branch `feat/world-visuals`). Repo root `/root/projects/witch-hunter`.
Written 2026-11-06. All anchors below re-verified TODAY by Testerbot; line numbers ARE CURRENT
but re-check on arrival at gate step 4 (drift = re-census, not fail).

Laws (bind Testerbot AND Devbot): NO push by children (NO-GIT). NO harness runs, NO headless
browser smoke tests — static checks + build only; Nicko's playtest is the only playtest bar.
Devbot does not modify code outside the file set in §R1.

---

## 0. Census corrections vs the IO spec (Testerbot-verified 2026-11-06 — Devbot builds to THESE)

| # | Spec says | Actually (verified) | Required build behavior |
|---|-----------|---------------------|------------------------|
| C1 | §3 CONFIG.player.radius is NOT defined; ADD radius: 0.8 as new key | `CONFIG.player.radius` EXISTS = **0.7** at CONFIG.js:1569 and is live-consumed: game.js:1305 + game.js:2056 (`pushOutOfProps(..., CFG.player.radius)`), enemy.js:411 (`attackRange + player.radius` melee reach) | **Do NOT add/change the key.** Reuse 0.7. Bolt circle test = 0.8 + 0.7 = **1.5 m** (see §NE-3). Setting 0.7→0.8 or duplicating the key = BLOCKING (D1) — it widens every enemy's melee reach and prop push-out (A11 regression). Record deviation. |
| C2 | §1.1 `CONFIG.assets.bodies` / `CONFIG.assets.pngs` tables | Do not exist. Body table = **MANIFEST in assets.js:16** (banditBody:146, ghoulBody:150, wolfBody:155, farmerBody:165); pixelated map = **BODY_PNG in assets.js:181-185**. CONFIG.assets:2130 holds pipeline settings only (`pixelatedBodies: true` at 2224) | covenBody row goes in assets.js MANIFEST; pngs decision = assets.js BODY_PNG. Naming-only correction; record deviation. |
| C3 | §1.1 pngs fallback path `races_regen/rspec/coven-acolyte.pixelated.png` | **No rspec/ dir exists**; pixelated pngs live only in `races_regen/rigged/` and only for human-hunter-male / orc-male-warrior / undead-ghoul-male. No elf png. | pngs row OMITTED (spec §1.1 sanctions). Any pngs row pointing at a nonexistent file = BLOCKING (D2). |
| C4 | (context census) regionC.enemies "ends with CC-C16b camp-guard rows" | Array spans CONFIG.js **575–634** (50 rows today); CC-C16b guards sit at **588–599** (4 camps × 3, mid-array); the array ends with the **CC-C6 Charlie row `{type:'bandit',x:-138.1,z:-516.8}` at line 631** (close bracket 634) | Coven rows append AFTER line 631, landing at row indices **50 and 51**. Appendix check in §V3 asserts 50 pre-existing rows unchanged. |
| C5 | (context census) animVariantByType coven→'bandit' "so CHARACTERS needs NO new row" | **FALSE and unsafe.** assets.js:714 captures clips ONLY `if (CHARACTERS[name])`; assets.js:814 `cloneTemplate` uses WHSkeletonUtils.clone ONLY when `CHARACTERS[name] && clips[name]`. No CHARACTERS row ⇒ zero clips captured (no anims at all) + `tmpl.clone(true)` shared skeleton across the two coven instances (both deform from one skeleton). Elf GLB parsed today: exactly 6 universal clips `[WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run, WH_Walk]` | **ADD `covenBody: 6` to CHARACTERS (assets.js:229).** REQUIRED for runtime correctness. Also note enemy.js:178 defaults any rowless type to variant 'bandit' anyway; with the elf body the 'bandit' variant names (WH_*_Melee/Attack_High/Hit_Large_L) miss and anim.js:141-152 falls back to the universal names — expect exactly 5 benign `[WH anim] missing ... falling back` warns per coven body instance (death name IS universal WH_Death). This is EXPECTED, not a bug. |
| C6 | §1.2 covenBody = human-female-caster.rigged.glb IF it exists | `human-female-caster.rigged.glb` DOES NOT EXIST (dir census today). `elf-dawn-refuser-male.rigged.glb` exists with 6 clips | Use the sanctioned fallback: elf-dawn-refuser-male.rigged.glb. Devbot must `test -f` before finalizing and report the choice. |

---

## 1. Verified anchors (gate-step-4 quick table)

- CONFIG.js: player.radius 1569 (=0.7) · spell.firebolt 1606-1624 (dmg12 speed40 hitRadius0.5 maxRange30 windup0.25 cd0.3) · projectilePoolSize note 49 · regionA.enemies 176 · regionB.enemies 376 · regionC.enemies 575-634 · CC-C16b guard rows 588-599 · CC-C6 rows 615-631 · banditCampfire props 1057-1060 · den door `interactAt {x:-163.4,z:-202.6}` 1254 · enemy.bandit 1784 (ai1 1803-1818) · ghoul 1820 · wolf 1846 · bodyByType 1968 · animVariantByType 1970 · wolfPacks 1980-2000 (8 packs × 8 waypoints = 64) · CONFIG.assets 2130 · itemStats.magicDefense registry 3219-3221 (INERT v1 — no item carries stats.magicDefense anywhere in CONFIG) · xpSources kills 3305-3309
- assets.js: MANIFEST 16 · banditBody 146 · ghoulBody 150 · wolfBody 155 · BODY_PNG 181-185 · CHARACTERS 229 · clip-capture gate 714-719 · cloneTemplate 813-818 · instance 825
- enemy.js: bodyNameFor 82 · FSM init 93 · setBody 153-155 · variant pick 178 → `|| 'bandit'` · update 304 · stagger exit 384 · attack phase 385-433 · melee-reach uses player.radius 411 · `canDamagePlayer(this.cfg.attackDamage, this)` 416
- player.js: resolveIncomingHit 1599 (alive exit 1600, i-frame exit 1601, parry branch 1618-1623 — **requires `attacker.enterStagger`** to exist, 1619) · equippedItems 1015
- game.js: firebolts state 32 · damagePlayerFromEnemy 1361-1363 · awardXP `'kill_' + enemy.type` 2111 · player cast site 2981-3000 (WH_SPELLS.spawn 2990; wisdom mult 2996-2998) · firebolt update loop 3014-3021 · computeSockets 2789-2795 (firebolts only)
- spells.js: Firebolt ctor 18 · update 43 · spent/hitFlash 0.15 46-50 · `e.takeDamage(...); this.spent = true` 68-70 · die ~84 · `spawn:` 168-171 (unknown id → null) · getSpellConfig 173
- leveling.js: awardXP 62-64 (defaults to xpSources[source]) · magicDefense 149-154 (equippedItems().reduce over item.stats.magicDefense)
- anim.js: VARIANTS 50 (bandit names 59-64) · per-state miss → universal-name fallback with warn 141-152
- Disk (verified today): NO human-female-caster.rigged.glb; NO rspec/; elf-dawn-refuser-male.rigged.glb = 6 clips; concepts anchor `art-direction/concepts/char-09-coven-wizard.png` EXISTS.
- Baseline: `grep -rn "coven\\|Coven" prototype/js/` = ZERO hits today (clean slate).

## 2. Base commit rule

At gate step 4, find Devbot's commit: `git -C /tmp/wh-worldfeat log --oneline -5`. All diff checks
run against its parent (`<BASE>` = the sha before Devbot's commit). If Devbot made >1 commit,
diff `<first-parent-of-first-devbot-commit>..HEAD` as one unit.

---

## 3. Per-criterion checks (A1 → A12)

### V1 — A1: CONFIG.enemy.coven row numbers (grep-assert exact equality)
Command: `grep -n -A22 "coven: {" prototype/js/CONFIG.js` (must start right after the wolf row, ~line 1846+).
Assert EXACT (numeric equality table §NE-1): hpMax 60 · moveSpeed 3.4 · chaseSpeed 4.6 ·
attackDamage 0 · attackRange 0 · attackCooldown 0 · sightRadius 20 · leashRadius 40 ·
staggerTime 0.45 · radius 0.7 · aggroPingInterval 0.2 · attackPhase {windup 0.55, active 0.12,
recover 0.85, hitArcDeg 50, trackDegPerSec 180}. Row is a SIBLING of bandit/ghoul/wolf (same
CONFIG.enemy object), NOT inside wolf. `grep -n "enemyWeapon" prototype/js/CONFIG.js` diff-unchanged
(covered by §R1 too). PASS iff every number matches §NE-1 and placement is sibling-after-wolf.

### V2 — A2: body/png rows (corrected home = assets.js, per C2/C3/C6)
1. `grep -n "covenBody" prototype/js/assets.js` → MANIFEST row (≥1 hit) with EXACTLY the fallback path
   `art-direction/3d/assets/races_regen/rigged/elf-dawn-refuser-male.rigged.glb` (unless Devbot proves a
   better existing rigged humanoid exists — then Testerbot re-censuses the file on disk).
2. `test -f art-direction/3d/assets/races_regen/rigged/elf-dawn-refuser-male.rigged.glb` → exists.
3. `sed -n '181,190p' prototype/js/assets.js` → BODY_PNG has **NO covenBody row** (omission = expected
   deviation ED-2). Any covenBody pngs row = check the path on disk; nonexistent = BLOCKING (D2).
4. `grep -n "covenBody: 6" prototype/js/assets.js` → CHARACTERS row present (C5, REQUIRED).

### V3 — A3 + A11 row-law: append-only regionC diff (RUNNABLE)
1. `git -C /tmp/wh-worldfeat show <BASE>..HEAD -- prototype/js/CONFIG.js | grep -c "^-.*type:"` → the
   CONFIG.js diff must show **zero deleted/modified `{type:` rows anywhere** (A/B/C arrays all intact).
2. Strong-form: extract the regionC enemies array from both revisions and assert prefix property —
   `git show <BASE>:prototype/js/CONFIG.js` vs `git show HEAD:prototype/js/CONFIG.js`, slice lines
   575-634 (re-locate by `enemies: [` after the CC-C5 wolf-pack comment), row-parse both, assert:
   old 50 rows are rows 0-49 of new array byte-for-byte (x, z, type, packId, waypointPhase all equal),
   new array length 52, rows 50-51 are the two coven rows at the END (`{type:'coven',x:-118.4,z:-238.2}`
   then `{type:'coven',x:-99.2,z:-249.1}` — spec coords; §V10 governs adjusted coords).
3. `git diff <BASE>..HEAD -- prototype/js/CONFIG.js | grep "^[+-]"` visually swept: no reorder/insert
   between existing rows, no index shifts, no other enemy-row edits.
PASS iff all three.

### V4 — A4: kill_coven XP through the existing path
1. `grep -n "kill_coven" prototype/js/CONFIG.js` → exactly one hit in xpSources: `kill_coven: 30`.
2. Code-read: NO new award code. game.js:2111 `window.WH_LEVEL.awardXP('kill_' + enemy.type)` + coven.onKilled
   = the existing setFsm-dead/onKilled path; leveling.js awardXP defaults to `xpSources[source]`.
   `git diff <BASE>..HEAD -- prototype/js/leveling.js` → EMPTY. `git diff <BASE>..HEAD -- prototype/js/game.js`
   must show NO edit at the :2111 line.
PASS iff xpSources row present AND no new award machinery AND leveling.js untouched.

### V5 — A5: coven cast branch (code-read walkthrough with expected branch behavior)
Locate: `grep -n "coven" prototype/js/enemy.js` → a `type === 'coven'` gate inside Enemy.prototype.update
(update starts :304). Read the branch; must show ALL of:
1. **Cadence**: FSM 'attack' = cast cycle; cast clock `castT` runs 0→enemySpell.castWindup (0.55);
   cyan glow on staff hand scales with castT (emissive presentation only); at windup expiry:
   `window.WH_SPELLS.spawnEnemyBolt(...)` (NOT `WH_SPELLS.spawn`, NOT CONFIG.spell — spawn() would
   return null for 'covenBolt', see spells.js:168-171) with origin = enemy pos + 0.3 toward player,
   y +1.2; dir = normalized (playerPos − enemyPos) computed at the spawn INSTANT (snap-shot, no tracking);
   then recover = attackPhase.recover (0.85); re-enter attack hold; re-cast gated by
   CONFIG.enemySpell.covenBolt.castCooldown 2.6 (> windup+recover 1.4 ✓). Base cycle 1.4s, effective ≥2.6s.
2. **Range keep-distance**: dist<8 → back away at moveSpeed×0.6 (=2.04u/s); dist>16 → approach at
   chaseSpeed×0.5 (=2.3u/s); 8-16 → drift 0. Face the player continuously (existing yaw).
3. **Cancel**: player leaves castRange 22 (= enemySpell.maxRange) during windup → cast clock cancels,
   glow decays, NO bolt, cycle restarts on re-entry.
4. **Stagger cancels cast**: coven staggers like bandits (staggerTime 0.45 via existing takeDamage/
   enterStagger machinery); on stagger entry the in-flight castT resets and no bolt can fire mid-stagger.
5. **No melee harm**: either (a) the shared attack-phase active-entry call fires
   `canDamagePlayer(this.cfg.attackDamage /* =0 */, this)` harmlessly, or (b) the coven gate skips it —
   EITHER is acceptable per spec §2, but the choice MUST be stated in the build note; in both cases
   no code path can apply nonzero coven melee damage.
6. **Aggro path unchanged**: existing sense → aggro → chase; coven branch takes hold only within castRange.
PASS iff all 6 behaviors are present in the branch read + build-note statement for (5).

### V6 — A6: WH_CovenBolt class (spells.js)
1. `grep -n "WH_CovenBolt\\|spawnEnemyBolt" prototype/js/spells.js` → class + registry helper present;
   `spawnEnemyBolt(scene, spellId, origin, dirX, dirZ)` reads `CONFIG.enemySpell[spellId]` (NULL for
   unknown id — mirror the spells.js:169 pattern) and returns null when kind ≠ 'projectile'-family or unknown.
2. Visual: ONE MeshBasicMaterial sphere (emissive-style), radius **0.22**, color = S.schoolColor
   (0x4fd8c8). NO PointLight constructed/consumed by the class (expected deviation ED-3: the
   CONFIG.enemySpell.covenBolt.projectileLight numbers may exist in CONFIG but must remain inert —
   grep Devbot's class for `PointLight` → zero; and `git diff <BASE>..HEAD -- prototype/js/light.js` → EMPTY).
3. Mechanics mirror Firebolt's: advance speed 16; lifetime = maxRange/speed = **1.375s** die past 22m;
   per-bolt mesh (no shared instances); hit-then-flash: on player hit → spent=true + hitFlash 0.15 →
   die when flash expires (copy the spells.js:46-50 shape); no movement/collision during flash.
4. Circle test = vs PLAYER positions: radius composition hitRadius 0.8 + `window.WH_CONFIG.player.radius`
   (= 0.7 per C1, total 1.5m). Uses the LIVE CONFIG value, never a hardcoded 0.8+0.8.
PASS iff 1-4 all hold; BLOCKING (D3/D4) if covenBolt routes through WH_SPELLS.spawn / CONFIG.spell, or a
pooled light is borrowed from the player firebolt pool.

### V7 — A7: MD choke at call site ONLY (the binding amendment)
1. `git diff <BASE>..HEAD -- prototype/js/player.js` → **EMPTY** (resolveIncomingHit :1599 untouched —
   no spell-classification branch, no MD math, no edits at the parry branch :1618-1623).
2. game.js bolt-player call site code-read: `reduced = Math.round(dmg * (1 - window.WH_LEVEL.magicDefense()))`
   applied EXACTLY ONCE, then `damagePlayerFromEnemy(reduced, { isSpell: true, pos: {x,y,z of bolt} })`.
   dmg source = CONFIG.enemySpell.covenBolt.damage (14) read as-is — NO wisdom/skill multiplier
   (`grep` Devbot's enemy-bolt block for `skillMult` → zero; the mult at :2996-2998 is player-cast only).
3. Parry-safety proof (code-read): the attacker object is a bare `{isSpell, pos}` literal;
   resolveIncomingHit parry branch requires `attacker.enterStagger` (player.js:1619) — absent ⇒ parry
   can NEVER stagger a bolt; Devbot added NO methods to the attacker (grep the call-site object literal
   for `enterStagger` → zero). Adding fields that open the branch = BLOCKING (D5).
4. Still-unchanged behaviors (code-read confirm against lines): roll i-frames early-exit (:1601),
   shield block chips the ALREADY-REDUCED amount (guard-break math normal), dagger-guard past-window
   full reduced damage via step 4, alive/exits (:1600). No double mitigation anywhere (MD appears in
   exactly ONE application site; `grep -n "magicDefense()" prototype/js/game.js prototype/js/player.js`
   → game.js hit(s) at the coven call site only; player.js ZERO).
PASS iff 1-4.

### V8 — A8: game.js insertion + one-hit pattern
1. game.js: new array state init near :32 sibling of `firebolts: []`; enemy-bolt update loop placed
   AFTER the firebolts loop (:3014-3021), same keep-alive shape (`b.alive && b.update(dt) → keep.push`).
2. Dead-player handling documented (either explicit alive guard before the circle test, or reliance on
   resolveIncomingHit returning false so the bolt continues) — MUST be stated in the build note; in
   both cases a bolt NEVER damages twice (spent flag set on hit regardless of route).
3. computeSockets (:2789-2795) still reads game.firebolts only — enemy bolts do NOT register light
   sockets (consistent with ED-3).
PASS iff init + loop placement present, one-hit provable from the read, and the note exists.

### V9 — A9: art law (grep-assert)
1. `grep -n "0x4fd8c8" prototype/js/CONFIG.js prototype/js/spells.js` → CONFIG enemySpell row + bolt
   material(s); cyan family ONLY.
2. `grep -n "char-09-coven-wizard" prototype/js/CONFIG.js` → §7 comment block present (also carry:
   "ONE cyan accent", "no red", the magicDefense-ONCE-at-call-site line — all four greps hit).
3. No red/orange accent in new code: `git diff <BASE>..HEAD -- prototype/js/CONFIG.js prototype/js/spells.js
   prototype/js/enemy.js prototype/js/game.js | grep "^+" | grep -i "0xff7722\\|0xff0000\\|0xcc0000\\|0xff3333"`
   → ZERO hits (0xff7722 must remain firebolt-only, pre-existing lines).
4. Build note names the char-09 anchor. Elf-body placeholder robe palette = covered by expected
   deviation ED-1 note (accent law applies to bolt + glow; no red/orange added).
PASS iff 1-4.

### V10 — A12: regionC clearance (independent recomputation; Devbot REPORTS, Testerbot RE-RUNS)
Check set (re-grep line numbers at gate time):
- 12 CC-C16b bandit camp guard rows (CONFIG.js 588-599); 10 CC-C6 camp rows (615-631);
- 4 banditCampfire props (1057-1060) — camp props;
- ALL 64 wolfPacks waypoints (CONFIG.enemy.wolfPacks, 8 packs × 8, 1980-2000) AND all regionC wolf
  enemy rows (pack-slot spawns, 576-587 + 600-611);
- den door `interactAt {x:-163.4, z:-202.6}` (1254).
Rule: 2D distance √(dx²+dz²) from EACH coven row to EVERY set member > 25.0 m.
Testerbot reference values (computed 2026-11-06 from spec coords):
- coven1 (−118.4, −238.2): min = **38.4 m** (sw-pack loop waypoint 5 [−112.5,−276.1]); den door 57.4 m.
- coven2 (−99.2, −249.1): min = **30.1 m** (same waypoint); den door 79.3 m.
→ Spec coords CLEAR as-is. If Devbot adjusted coords, re-run the sweep; also assert adjusted coords
stay ≤ 274.5 m from C center (0,0) (CC-C3 playable-disc contract; rim ≈278.5) and inside regionC ground.
Devbot's build note must print the per-row min distances and the nearest foe/set member for each.
PASS iff Testerbot's independent recomputation confirms every min > 25.0 and Devbot's report matches
within rounding.

### V11 — A10 + A10b: build + commit hygiene
1. `python3 tools/build_v8.py` from `/tmp/wh-worldfeat` → exits 0, no tracebacks.
2. `grep -c coven prototype/builds/v8-playable.html` → ≥ 4 (CONFIG row + enemySpell block + enemy
   branch + spells class all inlined). 0 = FAIL (A10). Also confirm the build inlined the CURRENT
   sources (build timestamp fresh).
3. `git -C /tmp/wh-worldfeat log -1 --format='%an <%ae>|%s'` → author identity CaptainPickard; message
   carries the gate line `spec -> valspec -> build -> validate -> commit`.
4. NO-GIT: `git -C /tmp/wh-worldfeat rev-parse origin/feat/world-visuals 2>/dev/null` (if the ref
   exists) — Devbot's sha must NOT be reachable from the remote ref; `git status -sb` shows the local
   branch ahead only. Devbot pushed = BLOCKING (D6).
PASS iff 1-4.

### NE — Numeric equality tables (spec number == CONFIG number)

NE-1 A1 coven row: hpMax 60 · moveSpeed 3.4 · chaseSpeed 4.6 · attackDamage 0 · attackRange 0 ·
attackCooldown 0 · sightRadius 20 · leashRadius 40 · staggerTime 0.45 · radius 0.7 ·
aggroPingInterval 0.2 · attackPhase windup 0.55 / active 0.12 / recover 0.85 / hitArcDeg 50 /
trackDegPerSec 180.

NE-2 covenBolt row: kind 'projectile' · focusCost 0 · damage 14 · speed 16 · hitRadius 0.8 ·
maxRange 22 · castWindup 0.55 · castCooldown 2.6 · schoolColor 0x4fd8c8 · name 'Coven Bolt' ·
glyph 'CB' · light {0x4fd8c8, 6.0, 9, 2, 8} · projectileLight {0x4fd8c8, 2.0, 6, 2, 10}.
Cross-equalities: enemySpell.castWindup == attackPhase.windup == 0.55; castCooldown 2.6 ≥ windup+recover 1.4.

NE-3 derived constants: bolt-vs-player circle = 0.8 + 0.7 (**existing** player.radius) = **1.5 m**;
bolt lifetime = 22/16 = **1.375 s**; MD v1: WH_LEVEL.magicDefense() = 0 (no item carries
stats.magicDefense — itemStats registry at 3219 is label-only) → reduced = round(14 × 1) = **14**;
kill_coven 30 ≈ 0.5 × hpMax 60 (matches the ~0.5 law: bandit 35/70, ghoul 25/45, wolf 20/38).
NE-4 enemySpell.home: `grep -n "enemySpell" prototype/js/CONFIG.js` → top-level sibling of `spell:`,
NOT nested inside it; `grep -n "covenBolt" prototype/js/CONFIG.js` → only in enemySpell block;
CONFIG.spell contains firebolt (+radiance) only — `git diff` shows zero changed lines inside CONFIG.spell.

### R1 — Regression sweep (A11 file-set law)
Expected touched set (exactly): `prototype/js/CONFIG.js`, `prototype/js/enemy.js`,
`prototype/js/spells.js`, `prototype/js/game.js`, `prototype/js/assets.js`, and optionally
`prototype/builds/v8-playable.html`. Everything else EMPTY-diff:
`git diff <BASE>..HEAD --stat`. MUST be EMPTY: `prototype/js/player.js` (the amendment!), `leveling.js`,
`anim.js`, `light.js`, `npc.js`, and any vendor file. Within touched files: pre-existing blocks byte-
identical (diff shows additions only, except where the coven branch interleaves in enemy.js update —
still zero CHANGED pre-existing lines).

---

## 4. Expected deviations (Devbot MAY record; Testerbot PASSES them)

- **ED-1** covenBody = `elf-dawn-refuser-male.rigged.glb` (sanctioned §1.2 fallback; the preferred
  human-female-caster.rigged.glb does not exist on disk — verified). Placeholder robe palette noted.
- **ED-2** BODY_PNG pngs row OMITTED for covenBody (no suitable existing png; rspec/ dir does not
  exist); body renders raw-texture.
- **ED-3** NO pooled projectile light consumed for coven bolts (covenBolt.projectileLight CONFIG
  numbers present but inert; CONFIG.playerLight pool untouched). light.js unchanged.
- **ED-4** Census corrections C1-C5 recorded as notes (player.radius exists=0.7 and is reused; body/png
  tables live in assets.js; regionC array end = CC-C6 Charlie row, coven rows land at indices 50/51;
  CHARACTERS covenBody: 6 added per C5).
- **ED-5** Benign `missing WH_*_Melee / WH_Attack_High / WH_Hit_Large_L … falling back` anim warns
  (5 per coven body instance) — inherent to the bandit variant over the elf's universal 6-clip set.
- **ED-6** Melee active-window choice (a) or (b) in V5.5 — documented, both acceptable.

## 5. BLOCKING deviations (any one → FAIL, remediation card, re-gate)

- **D1** CONFIG.player.radius changed 0.7→0.8, or a duplicate radius key, (melee-reach/prop-push regression).
- **D2** bodies row pointing at a nonexistent glb, or ANY pngs row pointing at a nonexistent file
  (fetch-fail → stand-in body, grey, clipless).
- **D3** covenBolt routed through WH_SPELLS.spawn / read from CONFIG.spell (spawn returns null ⇒ bolt
  dead on arrival; player registry polluted).
- **D4** coven bolts borrowing the player firebolt light pool, or any edit to light.js / pool sizing.
- **D5** resolveIncomingHit or any of player.js modified; magicDefense applied anywhere but the game.js
  bolt call site (or applied twice); attacker object granted enterStagger (parry-open).
- **D6** Devbot pushed to a remote (NO-GIT), or commit identity/gate line missing.
- **D7** regionC append-law violated: reorder/insert/delete/modify of any row 0-49; coven rows not at
  array end; save-state index corruption.
- **D8** kill_coven absent, wrong value (≠30), or NEW award code instead of the 'kill_' + type path.
- **D9** coven melee harm nonzero anywhere, or coven excluded from stagger, or stagger does not cancel
  an in-flight cast.
- **D10** CHARACTERS row absent for covenBody (no clip capture ⇒ no animations + shared skeleton among
  instances) UNLESS Devbot documents and Testerbot verifies an equivalent clip-capture + SkeletonUtils
  clone path.
- **D11** Wisdom/skill multiplier applied to coven bolt damage (must read CONFIG damage as-is).
- **D12** Red/orange accent introduced in coven visuals; bolt color not 0x4fd8c8 family.
- **D13** Build fails, or build marker absent (`grep coven prototype/builds/v8-playable.html` = 0).

---

## 6. Gate step 4 verdict rubric (Testerbot runs, in order)

Setup: locate Devbot's commit(s), set `<BASE>`; `git -C /tmp/wh-worldfeat status -sb` clean-or-noted.
NO harness runs; NO headless browser; NO code modification by Testerbot (findings → verdict text only).

1. `git diff <BASE>..HEAD --stat` → file set == §R1 allowed set; player.js/leveling.js/anim.js/light.js EMPTY. [feeds D1/D5/D13]
2. CONFIG sweep: §NE-1 row grep-assert; §NE-2 row grep-assert; §NE-4 placement greps; kill_coven grep (V4). [feeds V1, D8, D12]
3. assets.js sweep: MANIFEST path + `test -f` the glb; BODY_PNG omission; CHARACTERS `covenBody: 6`; elf clip count re-parse (expect 6). [feeds V2, D2, D10]
4. Append-only: the three-step V3 (row-diff zeros + prefix property + visual hunk sweep). [feeds D7]
5. enemy.js branch code-read V5 (all six behaviors; build-note statement for V5.5). [feeds D9]
6. spells.js class read V6 (+ PointLight grep = 0). [feeds D3, D4, D12]
7. game.js call-site read V7 + insertion read V8 (MD exactly once; parry-safety; wisdom-mult absence; spent/hitFlash; dead-player note). [feeds D5, D11]
8. Clearance: Testerbot independently re-computes §V10 over the full check set; compares to Devbot's reported table. [feeds A12]
9. Art greps V9 (cyan family; §7 block; no red/orange additions). [feeds D12]
10. Build: `python3 tools/build_v8.py` (exit 0) + `grep -c coven prototype/builds/v8-playable.html` ≥ 4. [feeds D13]
11. Commit hygiene `git log -1 --format='%an <%ae>|%s'` (CaptainPickard + gate line) + no-push check. [feeds D6]
12. Adjudicate every Devbot-recorded deviation against §4 (allowed) / §5 (blocking); zero-vs-list rule:
    unrecorded discovery of a blocking item also fails.

**PASS** = every check green AND zero blocking deviations AND all deviations accounted per §4.
**FAIL** = any blocking deviation, any numeric mismatch in §NE, or missing build marker. Verdict text
lists check-by-check PASS/FAIL, the deviation adjudication table, and (on FAIL) the precise remediation
card for IO to issue. Nicko's playtest then remains the final acceptance bar — this spec NEVER
substitutes for it.
