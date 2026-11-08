# CC-ED1 'East Wolfpack Den Site' — Testerbot INDEPENDENT VALIDATION REPORT
Gate step 4 · 2026-11-06 · Worktree /tmp/wh-worldfeat @ feat/world-visuals (HEAD fd286d5; tracked diff = this round only)
Validator: Testerbot (independent; build note NOT trusted — every claim re-derived)
Law: io/specs/cc-ed1-east-wolfpack-den-valspec.md; Round spec: io/specs/cc-ed1-east-wolfpack-den-spec.md (11 props + 4 nodes, CONFIG-only round; gather.js seat = landed CC-WD1 baseline)

## Verdict table (V-0..V-12)

| class | scope | result |
|---|---|---|
| V-0 | baseline recording, censuses, shas | PASS |
| V-1 | build + bundle marker ledger (≥ 4 contributors) | PASS |
| V-2 | CONFIG diff purity + positional/banner law | PASS |
| V-3 | gather.js diff EMPTY | PASS |
| V-4 | node --check 7 files | PASS |
| V-5 | asset/type legality | PASS |
| V-6 | wolfPacks sha + censuses | PASS |
| V-7 | file-set law + save.js + scratch-sha + NO-GIT | PASS |
| V-8 | clearance_ed1.py re-run (G-1..G-7) | PASS |
| V-9 | preseat_probe.js re-run + landed-CONFIG cross-check | PASS |
| V-10 | art law (neutrals + two-anchor banner) | PASS |
| V-11 | build note completeness + process law | PASS |
| V-12 | adjudication rubric | PASS |

**VERDICT: PASS — 13/13 classes, 0 blocking deviations, 0 adjudications needed, 1 non-blocking note (N-1).**

---

## V-0 Baseline recording — PASS
- HEAD fd286d5 extraction via `git show`: CONFIG.js sha256 → **5b064ce4b5f9cf1c6d6e2cadfa26a3ae48eb7413a955dcfe0060bac9ce6431e6** (3618 lines) == V-0 pin AND == the build note's baseline sha; gather.js HEAD sha → **492d6337061244362be39809d1f71dc5a5cb306a6a32e5394c6e9a766fbbf6ea** (== V-0 pin); HEAD bundle 108,039 lines with `east_hollow_den` = **0** (marker isNew this round) and `west_hollow_den` = 17.
- Working tree: CONFIG 3648 (+30), bundle 108,069 (+30), sha post **e493a04ed8b2ebea1058490844b996aa4e993bd57ff8a4c84394ced646b69706** (== note §2). Diff vs HEAD = exactly this round (bundle +30/CONFIG +30, no third surface).
- Baseline censuses reproduced at HEAD: `'east'` 6, `id: 'east'` 2, `type: 'wolf'` 28, `packId` 30, `type: 'bonePile'` 8, `west_hollow_den` 17, `banditCampfire` 21-whole-file (fires census unchanged post-round: 21↔21) — == valspec V-0/N-2 exactly.
- wolfPacks block at HEAD = 2190–2210 (`wolfPacks: [` at 2190, `],` at 2210); post-edit block sha **2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd** — byte-identical (V-6).
- Valspec doc-integrity (context flag: repaired after mid-write death): structurally complete — V-0..V-12, deviation tables ED-1..ED-10 + B1..B12, N-1..N-6 all readable; no truncation found. Its V-0 prose self-corrects the wolf census (28, not 30; N-2/C6). Live tree adjudicated as truth; **no doc defect found** (the only oddity: blank line + stray "1b-ter" numbering in §V-7 — cosmetic only).

## V-1 Build + bundle marker ledger — PASS
- `python3 tools/build_v8.py` → exit 0, `wrote .../v8-playable.html 3339134 bytes` (== build note §7). **Rebuild was byte-stable** (cmp pre/post rebuild → identical), so the delivered bundle IS the CONFIG-derived artifact; post-rebuild `git diff --stat` still exactly 30+30/2 files.
- `grep -c east_hollow_den` → CONFIG.js **17**, bundle **17** (≥ 6; ≤ 20 WD1-style band). Row-comment parity 17/17 CONFIG↔bundle (N-4 law).
- Per-hit distribution ( Testerbot re-derived, not pasted): 17 hits over **17 distinct lines**, NO line carries more than **1** hit (both files). Contributors ≥ 4: props banner 1166/88337, 3+3+3 larder/mouth/rim prop-row comments, 4 node-row comments, nodes banner 1197/88368 — **6 distinct contributor kinds**, max-per-row 1 ≤ 3. B2 anti-bloat holds with margin. Bundle grep line numbers (88337…88376) match the note's ledger.

## V-2 CONFIG diff purity — PASS
- `grep -c "^-[^-]"` → **0** (pure-add; B1 byte-purity: zero deleted/context-rewritten lines). `^+` lines = 30. Hunks = **2** (`@@ -1163,6 +1163,27 @@` + `@@ -1173,6 +1194,15 @@`) ≤ 2.
- Positional law: props hunk inserts at 1166 immediately after `// west_hollow_den chewed earth E` tail row (1165, rubblePile (−186,−446)); nodes hunk inserts at 1197 immediately after the last WD1 node row `bonePile (−198.5,−441)` — both inside EXISTING arrays (props close, nodes close reuse the original `],` — ED-5-sanctioned context shape; no third surface; no `nodes:` key re-created).
- Row law: every new prop row is exactly `{ asset, x, z, rotY, scale }` + comment; `y:` sweep on `+` lines → **0 matches**. Node rows exactly `{ type: 'bonePile', x, z }`.
- Set law (counted from `+` lines): deadTree ×3 (206,−440 / 213,−439 / 217,−440), mossBoulder ×3 (215,−449 / 208,−452 / 217,−445), skullPile ×2 (205,−448 / 203,−446), buriedCoffin ×1 (202,−450), rubblePile ×2 (205,−443 / 202,−440) = **11**; bonePile nodes ×4 (208.5,−455 / 199.5,−446 / 220,−447.5 / 214.5,−435) = **4**. Byte-identical to spec §3.1/§3.2 verbatim rows.
- Banner law: props banner (1166–1175) and nodes banner (1197–1201) both carry literal `east_hollow_den`; props banner names `concept-05-night-ambush` AND `day-05-ambush` on one + line (V-10.2 satisfied by the props banner, the only banner required to cite).

## V-3 gather.js diff EMPTY — PASS
- `git diff prototype/js/gather.js` → empty output; `grep -c "^@"` → **0** hunks (B4 gate). `wc -l` of diff → 0 lines.
- sha256 post-build = **492d6337…fbbf6ea** == V-0 baseline pin (tamper check).
- `node --check prototype/js/gather.js` → OK. The WD1 seat lines (60/146) ride as repo baseline; zero "helpful" edits.

## V-4 Syntax gate — PASS
`for f in CONFIG.js gather.js game.js save.js region-manager.js region-defs.js assets.js; do node --check …` → **all seven OK**, exit 0.

## V-5 Asset and node-type legality — PASS
- `git diff --stat -- prototype/js/assets.js` → empty (B6).
- Key sweep of `+` lines: asset keys exactly {deadTree ×3, mossBoulder ×3, skullPile ×2, buriedCoffin ×1, rubblePile ×2}, `type:` exactly bonePile ×4. All five manifest lines re-verified: buriedCoffin assets.js **21**, deadTree **32**, mossBoulder **64**, skullPile **72**, rubblePile **99**.
- bonePile pre-exists in CONFIG.gather.nodeTypes (boneShard ×2, respawnSec 150 — pre-existing surface); zero new nodeType/item/recipe/loot rows in the diff.

## V-6 wolfPacks byte-purity + censuses — PASS
- Block sha (`awk '/^    wolfPacks: \[/{s=1} s{print} s&&/^    \],$/{exit}' | sha256sum`, run at the live 2190–2210 window): **2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd** — byte-exact == V-0 == WD1 baseline. (No window drift this round: the +30 shift is downstream at 2221+, so the pack block sits where V-0 pinned it.)
- `git diff CONFIG.js | grep "wolfPacks\|waypoint\|packId"` → **no output** (rc=1). The L7 east pack keeps its exact 8 waypoints, re-extracted byte-exact: [[190,-318],[214,-322],[222,-340],[220,-372],[205,-398],[178,-388],[166,-360],[192,-334]].
- Censuses post-round: `'east'` = **6** (spawn 576–579, boundary guard 779, pack row 2191), `id: 'east'` = **2**, `type: 'wolf'` = **28**, `packId` = **30** (28 in-row + 2 comment refs), `type: 'bonePile'` 8→**12** (+4, exactly this round's rows) — all match V-0/N-2 law. Zero new wolf/pack/behavior rows (B7 clean).

## V-7 File-set law + save safety + scratch purity + NO-GIT — PASS
- `git status --short`: modified = {prototype/builds/v8-playable.html, prototype/js/CONFIG.js} ONLY; untracked = {io/reports/cc-ed1-build-note.md, io/specs/cc-ed1-*.md ×2, scratch/cc-ed1/}. GO-list diffs all **0 lines**: save.js, game.js, enemy.js, region-manager.js, region-defs.js, assets.js, wh-ground.js, gather.js (B8/B10 clean; the untracked io/specs + note are gate-authorship artifacts, not build output).
- `git diff prototype/js/save.js | wc -l` → **0** (A-8).
- Scratch sha purity (V-7.1b): site_scan.py `5491151606…d7d5c1` ✓, preseat_probe.js `c73fdd357a…4ba23da6` ✓, clearance_ed1.py `68acab5b4f…eef2f2c11` ✓ — all == V-0 pins, never edited. scratch/cc-ed1/ holds ONLY the delivered three + fix_valspec.py (`4e0623dfd3……84176358` == V-0 pin, IO's own remediation tool per 1b-ter). No new scripts.
- **NO-GIT**: nothing staged (`git diff --cached` empty), zero new commits, HEAD fd286d5 sits at the WD1 gate commit; changes unstaged. Honored.

## V-8 Clearance geometry — PASS
- `python3 scratch/cc-ed1/clearance_ed1.py` (AS-IS, sha-verified) → exit 0, **13/13 PASS + INFO G-8 line, `RESULT: CLEARED` literal present**. Testerbot outputs byte-identical to the build note §4 paste (Δ = 0.00): G-1 12.03 ≥ 5 · G-2 41.77 ≥ 25 · G-2n 38.20 ≥ 20 · G-3 81.54 ≥ 20 · G-4 69.36 ≥ 30 · G-5a 176.17 ≥ 3 · G-5b 41.23 ≥ 4 · G-5c 2.83 ≥ 2.5 · G-6a 4.27 ≥ 4 · G-6b 3.04 ≥ 3 · G-6c 12.73 ≥ 6 · G-6d 10.97 ≤ 12 · G-7 234.61 ≤ 262.
- All IO §5 limits (5/25/20/20/30/3/4/2.5/4/3/6/≤12/262) appear verbatim in the script's threshold strings. NEW_TAG exclusion active (post-landing self-rows dropped; the WD1 G-5a fix behaves as P0-designed). N-5 full-file census shape expected-by-design — no adjudication needed; every margin ≥/≤ its limit with the printed values.

## V-9 Seat probe (G-8) + landed-CONFIG cross-check — PASS
- `node scratch/cc-ed1/preseat_probe.js` (AS-IS, sha-verified) → exit 0; `WH_GROUND.has('forest_of_the_old_king') = true`; **all 15 rows PASS**; final line `ED1 PRE-SPEC SEAT: ALL 15 PASS`. Values byte-identical across this Testerbot run, the note §5 paste, and V-0's reference (deterministic seeded terrain, ED-10 class): y ∈ [0.05, 1.42] (≤ 26), slope1m ∈ [2.0°, 8.8°] (≤ 31°). Largest slope: deadTree (217,−440) 8.8° — the ED-9 float-print class, ceiling holds.
- Probe harness legality (re-read source): `globalThis.window/self` shim + vendored `three.classic.js` + CONFIG.js + wh-ground.js — CORE THREE-free, deterministic, **no browser/puppeteer artifact**.
- **V-9.3 landed-CONFIG cross-check (required, performed programmatically):** landed rows parsed from the V-2 diff `+` lines (11 + 4) vs the probe's hardcoded `const rows` table (15) — **ALL 15 MATCH as exact (asset, x, z) tuples**, not merely count-matched. No mismatch → no B5.

## V-10 Art law — PASS
- Valspec-verbatim grep on `+` lines (`lantern|campfire|startLit|light:|color|0xff|0xf…|ember|torch|glowColor`) → **no output** (exit 1). No warm accent, no light/color row in the new block; `banditCampfire` census 21↔21 (nothing added).
- Anchor citation: `concept-05-night-ambush` present ×1 and `day-05-ambush` present ×1 in the props banner + lines — both anchors cited (B6 banner law).
- No new warm-accent ASSET row; the 5-key neutral kit only. The pre-existing bonePile nodeType `glowColor 0xbbbbaa` (pre-round surface) untouched — confirmed by 0-diff on nodeTypes.

## V-11 Build note + process law — PASS
- io/reports/cc-ed1-build-note.md exists and contains every required paste: git diff --stat (30/30 ×2 — the note's stat matches re-derived truth), FULL per-hit CONFIG + bundle marker ledger (17+17 with line numbers, re-verified against live greps), FULL clearance table + verbatim post-landing output, FULL probe output, node --check 7/7, shas, censuses, smart-quote byte check, ED-n list. Every load-bearing paste reproduced exactly by Testerbot.
- Scripts present + runnable + sha-pure (V-7/V-8/V-9). No harness/browser/puppeteer artifact in diff, scratch, or note. NO-GIT honored (0 staged, 0 commits, 0 pushes).
- Deviations recorded: **none encountered** (note §9 = ED-1..ED-10 reviewed explicitly as non-triggered). Testerbot's re-derivation confirms: no valspec deviation class fired. The probe's 8.8° print vs the spec's 8.7 prose is pre-adjudicated ED-9 with the 31° ceiling intact — recorded as covered, not a new deviation.

## V-12 Adjudication rubric — PASS
Ran in valspec order (V-7 file-set → V-2 → V-3/V-4 → V-5/V-6/V-7 → V-8 → V-9 → V-1/V-10/V-11 → deviation adjudication). Zero-vs-list rule: **no blocking item discovered unrecorded**. No ED-n deviation was triggered this round, so no adjudication table was needed; the sole soft item is the note-level N-1 below. Every check green, zero blocking ⇒ **PASS**.

---

## Deviations ledger (final)

Adjudications: **none required** — every valspec check passed on its own green output.

Non-blocking notes:
- **N-1 (valspec V-0 prose slope-quote, pre-covered):** the spec §2/§3.1 prose says "slope ≤ 8.7 deg"; the deterministic probe prints 8.8° for deadTree (217,−440). This is exactly valspec note C4/ED-9's adjudicated ceiling-of-degree float print, disclosed before the build and re-confirmed by this gate — not a round deviation; recorded here so the next reader doesn't re-litigate it. The 31° law ceiling holds with 22° of margin.
- **N-2 (doc hygiene, cosmetic):** the valspec's §V-7 numbering carries two `1b-ter` headings (the write-repair artifact); both clauses read complete and non-contradictory against the live tree. Recorded per the task's doc-bug instruction; no effect on any check.

## Commands run (key outputs)
1. `git status -sb/--short`, `git diff --stat`, `git log -1`, `git diff --cached` → file set per V-7; NO-GIT clean; HEAD fd286d5.
2. `git show HEAD:` extractions + sha256sum ×2 → CONFIG/gather baseline pins == V-0/note; bundle baseline 108,039 lines, marker 0.
3. `git diff CONFIG.js | counts/greps` → 0− / 30+ / 2 hunks; positional law vs CONFIG 1165/1175 anchors; `y:` none; 11+4 set byte-== spec §3.1/§3.2; banners carry marker + both anchors.
4. `git diff gather.js` → 0 lines/0 hunks; sha == pin. `node --check` ×7 → all OK.
5. assets.js diff empty; manifest grep 21/32/64/72/99.
6. wolfPacks awk-sha → 2e2afb60… (== law); diff-grep wolfPacks|waypoint|packId → empty; west/east waypoint extraction byte-exact; censuses 6/2/28/30/8→12.
7. `python3 tools/build_v8.py` → exit 0, 3,339,134 bytes; cmp pre/post rebuild byte-identical; bundle grep -c = 17; per-row distribution max 1; parity 17/17.
8. `python3 scratch/cc-ed1/clearance_ed1.py` → exit 0, 13/13 PASS, RESULT: CLEARED, == note paste.
9. `node scratch/cc-ed1/preseat_probe.js` → exit 0, 15/15 PASS, == note paste; harness source re-read (THREE-free).
10. Testerbot cross-check (new this gate): landed diff-rows ↔ probe hardcoded table → 15/15 exact tuples.
11. Scratch sha256 ×4 (site_scan/preseat_probe/clearance_ed1/fix_valspec) → all == V-0 pins.

## Final verdict

VERDICT: PASS — 13/13 classes green, 0 blocking deviations, 0 adjudications required, 2 non-blocking notes (N-1 ED-9 float print pre-covered; N-2 valspec cosmetic numbering artifact). The east wolfpack den round is ready for IO's post-gate slice (stage+commit → serve → flip → Nicko playtest).
