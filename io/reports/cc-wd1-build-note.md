# CC-WD1 BUILD NOTE — West Wolfpack Den Site (doc 41 Family 1)

Round: CC-WD1 · 2026-11-06 · Builder: IO (inline; prior wake died pre-build-note)
Art anchor: art-direction/concepts/concept-05-night-ambush.png (viewed + absorbed:
indigo/charcoal base, moonlit cold rim light, den dressing = bone/bare-earth
neutrals; warm amber stays on the hunter — no new warm accents landed).

## Provenance of this build

Code (CONFIG props/nodes + the gather.js seat) was landed by a prior wake that
died before build/validation/commit. This wake (continuity-law diagnosis,
third consecutive mid-flight wake death): verified the layout against spec
Amendment A-1 (site (-194,-451)), remediated the inherited probes, folded the
gather.js seat into the valspec's EXACTLY-2-lines law (disclosed below), and
ran every valspec V-class. Testerbot validation follows as gate step 4.

## Diff stats (exact)

    git diff --stat
     prototype/js/CONFIG.js  | 31 ++++++++++++++++++++++
     prototype/js/gather.js  |  4 +++---
     2 files changed, 33 insertions(+), 3 deletions(-)

CONFIG.js: pure-add, 0 deletion lines, ONE hunk (props rows + banner + new
regionC nodes key are adjacent in regionC). 11 new prop rows + 8 banner lines +
nodes banner + 4 node rows + nodes-array close = +31.
gather.js: EXACTLY 2 deleted + 2 added lines, 2 hunks, pre-images verbatim:
  - `    holder.position.set(x, 0, z);` (makeNode ~line 60)
  - `    node.mesh.position.set(pick.x, 0, pick.z);` (reshuffle ~line 146)
Each replaced by the spec §3.3 sanctioned one-line seat form:
  holder.position.set(x, window.WH_GROUND && window.WH_GROUND.has(regionId) ?
  window.WH_GROUND.heightAt(regionId, x, z) : 0, z);
(reshuffle reads node.regionId / pick.x / pick.z). has()-guard REQUIRED and
present at both call sites; zero behavioral change for regionA/B pools (N-3).

## Deviations (numbered, disclosed)

- **ED-9 (IO inheritance deviation)**: the pre-death wake originally landed the
  gather.js seat as a 3-line wrapped ternary + 2 comments (4 add/2 del). IO
  folded it inline (PRIMARY law 4: <20 lines, no logic change, disclosed) to
  the valspec-pinned exactly-2-lines shape pre-validation. Semantics identical:
  same has() guard, same regionId sources, marker bob untouched.
- **ED-10 (window law)**: valspec V-6.1 pins a sed sha window (2159,2179) that
  predates A-1 (+31 CONFIG lines shift the block to 2190-2210). The LAW (block
  sha256 = 2e2afb60...) holds at the true post-A-1 window:
  `sed -n '2190,2210p' prototype/js/CONFIG.js | sha256sum` =
  2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd (exact).
- Remediations to the inherited scratch tools (disclosed, untracked scripts):
  clearance.py — case-insensitive treeRe (deadTree never matched the old
  case-sensitive class set; G-6a silently checked nothing tree-related);
  self-match exclusion (round's own marker-tagged rows were poisoning
  G-5a at 0.00); G-1/G-3/G-7 switched to the A-1 12-row union law; G-2
  props-governed per A-1's 25.96 derivation + NEW explicit G-2n
  nodes-vs-waypoints >= 20 (mouth node (-198.5,-441) to waypoint (-190,-420)
  = 22.66 m — reported, not discovered).
  seat_probe.js — REWRITTEN: stale probe still tested the RESCINDED
  (-255,-410) site; now probes the 15 amended-site rows via the V-9 sanctioned
  pattern (vendor three.classic + real WH_GROUND.heightAt/slopeTan APIs).

## Bundle marker ledger (V-1)

    grep -c west_hollow_den prototype/builds/v8-playable.html  →  17
    grep -n west_hollow_den prototype/builds/v8-playable.html  →  lines
    88316..88345: 2 banner comments (props-block + nodes-block) + 11 prop-row
    comments + 4 node-row comments = 2 + 15 distinct source contributors,
    ONE hit per row, ZERO rows carrying > 1 hit. Baseline 0 (V-0). Build:
    python3 tools/build_v8.py → exit 0 (final bundle: 3,336,413 bytes).

## Clearance table (V-8 — full paste)

    python3 scratch/cc-wd1/clearance.py
    PASS G-1 union-vs-wolfspawn >= 5: 22.66
    PASS G-2 props-vs-westwp >= 25: 25.96
    PASS G-2n nodes-vs-westwp >= 20: 22.66
    PASS G-3 union-vs-fires >= 20: 80.97
    PASS G-4 props-vs-roadsedge >= 30: 72.81
    PASS G-5a props-vs-preother >= 3: 202.47
    PASS G-5b props-vs-pretree >= 4: 23.15
    PASS G-5c newprops-mutual >= 2.5: 2.83
    PASS G-6a nodes-vs-tree >= 4: 4.27
    PASS G-6b nodes-vs-other >= 3: 3.61
    PASS G-6c nodes-mutual >= 6: 13.66
    PASS G-6d nodes-from-center <= 12: 10.97
    PASS G-7 union-from-Ccenter <= 262: 221.97
    INFO G-8-seen-by-seat_probe (sep script)
    RESULT: CLEARED   (exit 0)
(N-2 was pre-amendment: the A-1 site sits 222 m from C center — 40 m inside
the 262 cap; no rim-radial-outward tension exists on this site.)

## Seat probe (V-9 — full paste)

    node scratch/cc-wd1/seat_probe.js
    WH_GROUND.has(forest_of_the_old_king) = true
    PASS deadTree      (-190,-446) y=1.44 slope1m=3.1deg
    PASS deadTree      (-197,-445) y=1.59 slope1m=3.4deg
    PASS deadTree      (-201,-445) y=1.67 slope1m=4.4deg
    PASS mossBoulder   (-199,-455) y=1.34 slope1m=3.7deg
    PASS mossBoulder   (-196,-458) y=1.52 slope1m=3.0deg
    PASS mossBoulder   (-201,-451) y=1.35 slope1m=9.0deg
    PASS skullPile     (-189,-454) y=1.90 slope1m=2.9deg
    PASS skullPile     (-187,-452) y=1.82 slope1m=3.6deg
    PASS buriedCoffin  (-186,-456) y=1.98 slope1m=0.6deg
    PASS rubblePile    (-189,-449) y=1.61 slope1m=3.6deg
    PASS rubblePile    (-186,-446) y=1.46 slope1m=5.0deg
    PASS bonePile      (-192.5,-461) y=1.76 slope1m=3.3deg
    PASS bonePile      (-184,-450) y=1.89 slope1m=3.9deg
    PASS bonePile      (-204,-453.5) y=1.22 slope1m=3.8deg
    PASS bonePile      (-198.5,-441) y=1.62 slope1m=4.7deg
    G-8 SEAT: ALL 15 PASS   (exit 0)
(All inside |y| <= 26 and slope <= 31 with huge margin.)

## Syntax + legality + censuses (V-4/V-5/V-6/V-7/V-10)

- node --check x7 (CONFIG, gather, game, save, region-manager, region-defs,
  assets): ALL OK.
- assets.js diff EMPTY; new prop keys ∈ {deadTree x3, mossBoulder x3,
  skullPile x2, buriedCoffin x1, rubblePile x2} (all in the MANIFEST);
  new node keys = bonePile x4 (nodeTypes pre-existing; no new type/item/
  recipe/loot).
- wolfPacks block sha256 = 2e2afb60... (exact V-0, window 2190-2210);
  'west' census 6; type:'wolf' census 28; diff hunk-grep for
  wolfPacks/waypoint/packId prints NOTHING (banner reworded: "waypoint"
  only ever sat inside a comment; killed to keep V-6's grep zero-noise).
- save.js diff EMPTY; file-set = {CONFIG.js, gather.js, builds/v8-playable.html}
  modified + untracked {io/specs/cc-wd1-*.md, scratch/cc-wd1/, this note}.
  No staged entries, no devbot commits (NO-GIT honored).
- V-10 art grep: zero matches (no lantern/light/color/fuel rows; bonePile
  glowColor is pre-existing CONFIG 3356, not this round's).

## Post-gate slice (IO-owned after Testerbot PASS)

Build+commit+push feat/world-visuals → wh_release_flip.py → curl 200 on
http://172.16.5.1:8793/current/prototype/builds/v8-playable.html AND served
grep -c west_hollow_den >= 6 (SERVED bytes only). Nicko's playtest (WebUI
Playtest button) remains the acceptance bar.
