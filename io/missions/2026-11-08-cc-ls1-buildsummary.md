# CC-LS1 Contact Shadows — Devbot Build Summary (2026-11-08)

Unit: CC-LS1 blob contact shadows (doc 61 P1-1) — one additive module + wiring
in the feat/world-visuals worktree (parent ab61c2c). NO-GIT honored (no add,
commit, push, or config by this child).

## Build (deterministic tool law: python3 tools/build_v8.py)

- RUN 1: exit 0 → `prototype/builds/v8-playable.html` 3,569,695 bytes
- RUN 2: exit 0 → byte-identical to RUN 1
- RUN 3 (re-verify): identical again
- sha256 (x3 identical): `913c68cc6309b750768e77fd0ee8e7f8d5c97bd4f2b0bdb7d4767f2b29c0d7d7`
- pre-work bundle was `a747988a7a5b969a97272375f46420000ace364e2f9c08617b6600d3546f8d14`

## What landed (additive-only diff: 24 added lines, 1 comma-only line edit)

| File | Change |
|---|---|
| `prototype/js/shadows.js` | NEW (187 lines) — IIFE, 'use strict', ES5, global `window.WH_SHCONTACTS`; `init/attach/update/detach` only; one CircleGeometry(1,16) + one radial CanvasTexture(128, black core, ~0.55 @ half radius, linear falloff) + one MeshBasicMaterial(transparent, depthWrite false, polygonOffset −2/−2, cast/receiveShadow false, rotation.x −π/2); poolSize 24, free-list acquire, idempotent attach, exhaust = silent + one warn max, free on parent-null each tick, lift/fade law k=clamp(1−lift/3.2), opacity 0.42*k, scale radius*(0.55+0.45k), y=ground+0.02 |
| `prototype/js/CONFIG.js` | `contacts` block appended (7 keys exactly: poolSize 24, textureSize 128, radiusBase 0.55, groundOffset 0.02, maxLift 3.2, minScale 0.55, maxOpacity 0.42). Sole touched line elsewhere: `rankToastSeconds: 1.6` → `rankToastSeconds: 1.6,` (comma for the append; value unchanged) |
| `prototype/index.html` | 1 line: `<script src="js/shadows.js"></script>` immediately before game.js (order law A-3) |
| `prototype/js/game.js` | 3 tagged `// CC-LS1:` sites (8 added lines): init after the R2 light-pool boot region (~:193), player attach after `game.player.setBody(pBody)` (:2583→:2587 `{ bodyName: 'playerBody' }`), per-frame `update()` next to `game.playerLight.update` (:3262→:3269) |
| `prototype/js/region-manager.js` | 1 tagged site (3 lines): per-enemy attach directly after `enemy.setBody(eBody)` (:1926→:1929) with in-scope `{ bodyName: bodyName, scale: eScale }` — census per valspec D4 (`var bodyName` :1916, `var eScale` :1920) |

## Laws audit

- Byte-sacred (journal/bestiary/save/wolf-debug/ambush/hazards .js + style.css):
  ZERO edits (git diff over each = empty).
- game.js tagged sites = 3 (marker census), region-manager = 1, no other logic
  touched; no existing CONFIG row edited (single comma-only tail edit disclosed).
- Additive diff = 24 insertions / 1 modified line, all accounted above.

## Marker census (bundle v8-playable.html)

- CC-LS1: **7** (law ≥6 PASS; shadows.js module ×2 + CONFIG ×1 + game ×3 +
  region-manager ×1)
- Prior floors (valspec D2/D3): CC-WB2 = 7 (≥7 PASS), CC-H6 = 5 (≥5 PASS),
  lastchancel = 8 (≥8 PASS), CC-AE1 = 6 (≥6 PASS), QJR-2 = 9 (≥8 PASS),
  WH_AFF = 26 (≥25 PASS), QJR-4 = 36 hits (intact)

## Static validation run in-lane (node-only; no harness, no browser)

- `node --check` PASS on shadows/CONFIG/game/region-manager (and all six
  byte-sacred files: untouched, still parse).
- stubbed-env pool probes (scratch/cc-ls1-probe.js, scratch/cc-ls1-texture-probe.js):
  pool built once (double-init idempotent), one geometry/one texture/one
  material across the pool, exhaustion → null + exactly 1 warn, idempotent
  re-attach returns same slot, free-on-parent-null + detach, lift rows
  0/0.8/3.2 → k 1/0.75/0 (opacity 0.42 → 0.315 → 0; scale 1.0 → 0.6725×r →
  0.55×r floor), blob y = pos.y + 0.02, x/z track root, texture alpha ≈
  0.55 at half radius, black core RGB 0/0/0.

## Deviations / disclosures

1. Spec preflight sha mismatch (disclosed, non-blocking): valspec D-rule froze
   `f38909c1…`; on-disk spec hashes `6199f3bc…` in every encoding variant tried
   (raw/CRLF/strip-ws/UTF-16/CP1252/NBSP-tails). Per the same D-rule ("if the
   spec changed, abort and re-read it") I re-read the spec from disk: its
   content already carries the D1–D5 rulings inline (V-4 "valspec D1" note, V-6
   floor table), so the drift is the spec amendment itself; the task brief
   endorsed this exact on-disk spec. Proceeded on the on-disk text.
2. D1 ruling (lift row 3.2 → k=0) and D2/D3 floors re-measured post-build: all
   PASS (table above).
3. D4: landed attach site census used as ruled — `bodyName` (string, :1916) +
   `eScale` (:1920); tag placed exactly after `enemy.setBody(eBody)`.
4. Build tool emits the deterministic HEAD-anchored stamp (author-time law) —
   three runs byte-identical, exit 0 each.

Queued for Testerbot: full V-1…V-7 validation gate (this lane ran only the
static subset allowed: node --check + scripted stub probes).

## REPAIR (2026-11-08, Devbot dispatch on Testerbot FAIL 36/40 — V-1.2 blocking)

Testerbot verdict `io/missions/2026-11-08-cc-ls1-verdict.md`: the `contacts`
block had landed NESTED inside `window.WH_CONFIG.leveling` (CONFIG.js ~5120)
instead of at CONFIG top level → `WH_CONFIG.contacts` undefined → boot
`WH_SHCONTACTS.init(scene, CFG.contacts)` throws TypeError at `cfg.textureSize`.

Repair applied (CONFIG.js only; no other source touched):

1. Relocated the `contacts` block OUT of `leveling` to CONFIG top level: the
   2-line CC-LS1 comment + `window.WH_CONFIG.contacts = { …7 keys… };` now
   sits immediately after the `leveling` object's closing `};`, as a sibling
   assignment in the file's existing `window.WH_CONFIG.X =` idiom (same
   7 keys, same values, same comments — relocation only).
2. `rankToastSeconds: 1.6` restored commaLESS as `leveling`'s last line,
   byte-restoring the parent band.
3. Verification: `node --check CONFIG.js` PASS; probe
   `scratch/cc-ls1-fix-probe.js` (vm stub load of the REAL CONFIG.js) prints
   `WH_CONFIG.contacts.poolSize === 24: true` (value 24) and
   `LEVELING.RANKTOASTSECONDS IS NUMBER: true 1.6` → V-1.2 REPAIR PROBE: PASS.
   Leveling band (opener 5005 → closer) round-trips BYTE-EQUIVALENT vs parent
   ab61c2c (band sha256 both `061ccc26cf…bbba798d0c`-identical). Diff vs
   parent is now pure additive: CONFIG.js 11 insertions / 0 deletions.
4. Rebuild: `python3 tools/build_v8.py` RUN 1 exit 0, RUN 2 exit 0, bundles
   BYTE-IDENTICAL (3,569,695 bytes). New sha256 (x2 identical):
   `c5cfead212d0133602419ba146c7fae6efe1cc6e9ce76b34656ff4f2b8b80354`
   (old landed sha `913c68cc…0d7d7` superseded by the relocation).
   CC-LS1 markers in the rebuilt bundle = **7** (floor ≥6 PASS; the count is
   unchanged — the CONFIG comment lines moved with the block).
   Bundle spot-check: embedded CONFIG carries the top-level form
   `window.WH_CONFIG.contacts = {` (1 hit, at the CONFIG embed region,
   after leveling's `};`, no `contacts:` token between the two openers),
   and `rankToastSeconds: 1.6` commaless.

NO-GIT honored. Touched: prototype/js/CONFIG.js, the rebuilt
prototype/builds/v8-playable.html, scratch/cc-ls1-fix-probe.js, this summary.
