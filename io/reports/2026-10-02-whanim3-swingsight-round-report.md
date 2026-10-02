# whanim3 round report — swing sight (B1 sword orientation, B2 texture intake, B3 build)

Date: 2026-10-02. Author: IO. Gate: IO spec -> Testerbot valspec -> Devbot
build -> Testerbot independent validation -> IO commit.

## What shipped

- **B1 (player.js setWeapon):** longsword now mounts on the skinned R_Hand
  socket with a measured orientation — the blade axis (mesh +Y) leads
  THROUGH the swing with the tip forward. Pre-build frozen baseline:
  axisDot min −0.60 / mean −0.51 (pommel-first), sdHilt > sdTip.
  Post-build: axisDot min +0.5164 / mean +0.6381, tipLeads=True, idle
  carry 17.6° off-vertical (within ±30° of the 26.3° baseline).
- **B2 (assets.js loadOne):** GLTFLoader now constructed with a
  LoadingManager URL-modifier that rewrites embedded-texture blob: URLs
  to data: URIs on fetch failure (one-time Map cache). On the WebUI
  /playtest/ route (enforced CSP), pre-build showed 153 blob-connect
  violations + 2/2 materials with map=NULL (white mannequins). Post-build:
  cspErrors=0, map width 2048, zero stand-ins.
- **B3:** prototype/builds/v7-playable.html rebuilt — 2,416,462 bytes,
  byte-identical scratch rebuild, CharacterAnim ×11 + intake hook present,
  smoke boots + attack fires with zero page errors.
- Vendored loader files, CONFIG.js, game.js, moveset.js, anim.js, enemy.js,
  GLB assets: UNTOUCHED (verified by the harness AC6 census: drift=[]).

## Gate record

1. **IO spec:** io/specs/devbot-spec-whanim3-swingsight.md (ACs 1-6 with
   measured precision anchors from live probes).
2. **Testerbot valspec + harness:** io/specs/testerbot-spec-whanim3-
   swingsight.md + tests/wh_whanim3_validation.py (sha d4ac53c01842),
   frozen pre-build baseline: AC1 FAIL (pommel-first), AC2 PASS
   verify-only (axe CORRECT -> enemy.js closed), AC3 FAIL (153 CSP
   violations, maps NULL), AC4 PASS (18/18+18/18+v2+v3), AC5 FAIL (stale
   build, 0 CharacterAnim), AC6 PASS.
3. **Devbot build:** B1/B2/B3 implemented per spec; interim run flipped
   AC1/AC3/AC5. One cross-round adjudication during the build:
   ds1's A1-4/A3-4 weapon-pose probes read `weaponPivot` — a rigid
   stand-in-only structure since whanim2 (rigged bodies mount weapons on
   the R_Hand socket). Proven harness artifact (14/18 non-weapon ACs
   green, socket euler probe 0.00→2.76 rad healthy). Fixed as IO-owned
   harness re-target, logged as amendments **D4+D5** in
   io/specs/devbot-spec-combat-ds1.md (D4: socket-first readers +
   body-space euler metric, bars unchanged; D5: actFrac bar retired —
   starved by the 2-sim-frame active window — replaced by the swing-arc
   witness ≥ 1.0 rad; measured 2.741).
4. **Floors on the final tree:** ds1 18/18 (0 crashes), weave 18/18
   (regress=True), v2 PASS, v3 PASS.
5. **Testerbot independent validation:** deleg_0d3a109c (one full harness
   pass 982s + 2 own-tool spot-verifications: blade-axis +0.5030 min at
   strike on 8791; cspErrors=0 + map 2048 on 8787). Verdict: AC1-AC5
   PASS independently measured; AC6 FAIL on a bookkeeping conflict (the
   frozen allow-list predates the D4+D5 amendment files; zero hard
   violations, zero game defects). Adjudicated per the standing law
   (harness edits are IO's): allow-list amended (A3IO note in the
   valspec section 10); AC6 re-run alone: `changed=56 drift=[]
   hardViolations=[]` = PASS.
6. **Final verdict on record: PASS AC1-AC6.**

## Frozen shas at commit

| File | sha256 (12) |
|---|---|
| prototype/js/player.js | f0dd8902a4cc |
| prototype/js/assets.js | d1477c45b244 |
| prototype/builds/v7-playable.html | 864d0d5bb294 |
| tests/wh_whanim3_validation.py | d4ac53c01842 |
| tests/wh_combat_ds1_validation.py | 089f2e085649 |

## What Nicko sees after deploy

On the rail-button /playtest/ route: characters render TEXTURED (dark
cloak, silver sword — no more grey blocks) because embedded textures
survive the enforced CSP; the swing is a real skeletal slash with the
blade tip leading (no more hilt-first). The single-file build artifact
finally matches dev. Note: a hard-refresh is still worth doing on his
long-lived tab (the rail route serves no-store but a stuck tab can hold
its own session cache).

## Amendment log (this round's spec files)

- ds1 spec: D4+D5 (2026-10-02, socket-first readers + arc witness).
- whanim3 valspec: A1 (AC2 verify-only resolution), A2 (strike-band
  window), A3IO (AC6 allow-list + adjudication note).