# CC-EN1 CONSOLIDATED BUILD CARD (Devbot finisher round, 2026-11-08 wake 47)

You are the Devbot finisher for round CC-EN1 (Wilderness Encounter Tables V1,
doc 51 Sec 2.1 -> regionB darkwood_edge). A predecessor child died mid-build on
provider timeouts. Its artifacts are PARTIALLY on disk. This card is the whole
contract: read THIS + the spec amendment section named in it. Do not re-derive
anything here; every fact below was verified by IO this wake against the live
tree.

## 0. Worktree + pinned baseline (VERIFIED this wake, do not re-verify)

Worktree: /tmp/wh-worldfeat, branch feat/world-visuals, HEAD 45c0299 (clean,
nothing staged). Valspec §0 pins hold byte-exact: CONFIG.js
20ec2045b3d77ab4..., game.js c6e5f74f319c82..., region-manager.js
c7e31520775b2e..., index.html cca80541825d13... (sha256 prefixes).

Valspec of record: io/specs/cc-en1-valspec.md (V-1..V-11). IO spec of record:
io/specs/cc-en1-spec.md — its §6 IO AMENDMENTS EN1-1..EN1-9 supersede
contradicting spec text (esp. EN1-4 pending keys, EN1-5 spawn spacing, EN1-6
predicate p6). You may read spec §6 + valspec §0/V-3/V-5/V-8 if needed; this
card carries everything else.

## 1. What the dead child left (triaged by IO — trust this)

DONE: prototype/js/encounters.js EXISTS (323 lines) with correct: state init,
dist2/deg2rad, fireRows(), nightTable(), pickSeat() complete with p1..p9
(predicate p6 already in EN1-6 final form at its line 124), gates() g1..g8,
toast() helper with debugMute, tick() idle/warn/live FSM with refund laws,
window.WH_ENCOUNTERS surface (init/tick/state/pickSeat). KEEP ALL OF IT.

BROKEN (fix these, this file must pass node --check):
a) spawnParty() lines ~177-195 is a stub: comment block OK, but line `step:
   members.length - (members.length % ? 0 : 0) });` is a syntax error and the
   loop returns 0 without spawning. REPLACE the whole function body per §3.
b) rollRow() lines ~148-153 is dead code containing a Math.random() call that
   VIOLATES the RNG law (sites must be only pickSeat / spawnPartybearing /
   tick-roll). DELETE rollRow() entirely (tick owns the roll).

MISSING ENTIRELY (you add):
c) CONFIG.encounters block in prototype/js/CONFIG.js (§2).
d) game.js 2 hook lines + index.html 1 tag (§4).
e) Post-build probe smokes + bundle build (§5).

## 2. CONFIG.encounters block — ADD to prototype/js/CONFIG.js

Location: as a NEW top-level sibling AFTER the `raid:` block ends and BEFORE
`hazards: {` (raid block ends at line ~2811; insert between them at 2-space
indent). The block below is the FULL literal — transcribe exactly (note the
string concatenation style matches the file; you may keep or flatten it, but
every key/value/comment pair must land):

```js
  // CC-EN1 (io/specs/cc-en1-spec.md): wilderness encounter tables (doc 51
  // Sec 2.1). Values PROPOSED, Nicko tunes. Consumed by js/encounters.js only.
  encounters: {
    enabled: true,
    director: {
      regionId: 'darkwood_edge',
      checkSec: 20,
      triggerChance: 0.25,
      cooldownSec: 180,
      partiesPerNightMax: 2,
      warnSec: 2.0,
      warnLine: 'Eyes open in the murk of the Darkwood.',
      nightTable: 'darkwood_edge',        // which biome table the roll reads
      seatMinPlayerDistM: 14,
      seatMinPropM: 3.0,
      seatMaxSlopeTan: 0.45,
      nearFireExclusionM: 50,
      spawnSpacingM: 2.2,                 // lateral spacing between party members
      boundaryBandM: 6,                   // keep seats >= this off the z=-25 plane
      nodeM: 2.5,                         // gather-node clearance (CONFIG.scatter.clear.nodeM = 2.5)
      enemyRowM: 5,                       // static-roster spawn clearance (placement.enemyM = 5)
      spawnBandR: [0.2, 0.72]             // seat radial band = fraction of playable radius
    },
    biomes: {
      darkwood_edge: {
        note: 'doc 51 Sec 2.1 darkwood mapping. Live-kit rows only; rows naming '
            + 'not-yet-built sites are notes, not compositions.',
        // EN1-4: pending keys F2/F4/F6/F7 carry the full family story.
        pending: {
          'F2-tainted-glade-wailcaster': 'gravebound caster pool awaits its kit (doc 51 1.4)',
          'F4-road-life': 'road life already rolls via CC-AE1 on regionC; the darkwood '
              + 'side stays a live note until a smuggler chassis exists (doc 51 1.4 F4)',
          'F6-riches': 'claim-jumpers deferred - no kit row composes them yet (doc 51 Sec 2.1 F6)',
          'F7-wanderers': 'one-off hand-authored wanderers deferred - no kit (doc 51 Sec 2.1 F7)'
        },
        day: [   // DATA ONLY this round (the director never rolls day)
          { family: 3, label: 'wayfinding bandits', comp: [{ type: 'bandit', n: 2 }], tier: 'T1' }
        ],
        night: [
          { family: 1, label: 'lair-edge wolf pack', comp: [{ type: 'wolf', n: 2 }, { type: 'wolf', n: 1 }], tier: 'T1-T2' },
          { family: 2, label: 'bound thrall watch', comp: [{ type: 'bandit', n: 2 }], tier: 'T2',
            note: 'thrall seats = bandit chassis per doc 51 1.4 humanoid-grammar law' },
          { family: 3, label: 'roadless wayfinding', comp: [{ type: 'bandit', n: 1 }], tier: 'T1' },
          { family: 5, label: 'grave ghouls', comp: [{ type: 'ghoul', n: 1 }, { type: 'ghoul', n: 2 }], tier: 'T2',
            note: 'disturbance-spawn only at C; in B the graveyard edge stands in (keepOut chapel is NOT a spawn site)' },
          { family: 8, label: 'war-scar looters', comp: [{ type: 'bandit', n: 2 }, { type: 'bandit', n: 1 }], tier: 'T2-T3' }
        ],
        weights: [0, 0.28, 0.12, 0.15, 0.25, 0.2]   // index 0 = unused slot (1-based family feel)
      },
      forest_of_the_old_king: {
        note: 'doc 51 Sec 2.1 as LIVE in regionC: night road life already rolls via '
            + 'CC-AE1 (js/ambush.js CONFIG.raid = F4 night). These rows are the '
            + 'table record of that live behavior + the F1/F5 rows AE1 explicitly '
            + 'avoids (den mouths, notch arcs). No second director.',
        // EN1-4: regionC pending keys F1/F6/F7.
        pending: {
          'F1-lair-pair': 'dens are authored C sites; the den-mouth day pair stays site data (doc 41 F1)',
          'F6-riches': 'claim-jumpers deferred - no kit row composes them yet (doc 51 Sec 2.1 F6)',
          'F7-wanderers': 'one-off hand-authored wanderers deferred - no kit (doc 51 Sec 2.1 F7)'
        },
        night: [
          { family: 4, label: 'night roads (LIVE via AE1)', comp: [{ type: 'bandit', n: 2 }, { type: 'wolf', n: 1 }], tier: 'T1-T2', live: 'cc-ae1' }
        ]
      }
    }
  },
```

(NOTE the trailing comma after the block's closing brace: raid block ends `},`
and hazards follows — keep valid object-literal syntax when inserting between.)

## 3. encounters.js — REPLACE spawnParty() with the EN1-5-compliant body

Delete rollRow() (dead, stray RNG). Replace spawnParty(seat, row) body keeping
its signature. Contract (AE1 grammar verbatim + EN1-5 spacing law):

```js
function spawnParty(seat, row) {
  var rm = S.game.regionManager;
  var P = S.game.player;
  var list = rm && rm.enemies ? rm.enemies[D.regionId] : null;
  if (!list) return 0;           // defensive: region rebuilt under us
  var listKey = rm.logic ? rm.logic.activeId : D.regionId;
  var home = rm.enemies[listKey] || list;   // spawn into the ACTIVE region list
  // EN1-5 spacing: ONE random bearing for the whole party (RNG site #3 of 4);
  // member m (0-based): m 0 at the seat, later members alternate sides along
  // the bearing at Math.ceil(m/2) * D.spawnSpacingM. Per-member predicate
  // re-check p2/p3/p4/p6/p7/p8; a member failing any falls back to the seat.
  var bearing = Math.random() * Math.PI * 2;    // spacing bearing (RNG site)
  var bx = Math.cos(bearing), bz = Math.sin(bearing);
  var slots = [];
  for (var c = 0; c < row.comp.length; c++) {
    for (var m = 0; m < row.comp[c].n; m++) slots.push(row.comp[c].type);
  }
  var n = 0;
  for (var i = 0; i < slots.length; i++) {
    var type = slots[i];
    var sx = seat.x, sz = seat.z;
    var off = Math.ceil(i / 2) * D.spawnSpacingM;
    var side = (i % 2 === 1) ? 1 : -1;
    var mx = (i === 0) ? seat.x : seat.x + bx * off * side;
    var mz = (i === 0) ? seat.z : seat.z + bz * off * side;
    if (i > 0 && !memberClear(mx, mz)) { mx = seat.x; mz = seat.z; }
    var e = new window.WH_Enemy(type, rm.scene, D.regionId, mx, mz);
    e.raidMember = true;         // TRANSIENT law: the dead-state guard reads it
    e.setFsm('chase');           // pre-aggro: doc 34 "detection pre-set"
    e.yaw = Math.atan2(P.pos.x - mx, P.pos.z - mz);   // face the player
    e.setBody(window.WH_Enemy.makeBody(type));
    if (e.terrainHome) e.pos.y = e.groundY();
    e.root.position.copy(e.pos);
    e.yawFrame.rotation.y = e.yaw;
    home.push(e);                // rm.enemies keyed by active regionId
    if (rm.scene && rm.scene.add) rm.scene.add(e.root);       // parent = scene
    S.party.push(e);
    n++;
  }
  return n;
}
```

memberClear(mx, mz) is a NEW pure helper (NO Math.random inside): re-runs
p2 (props >= D.seatMinPropM), p3 (fires > D.nearFireExclusionM), p4 (player
>= D.seatMinPlayerDistM), p6 (z <= CFG.boundary.z - D.boundaryBandM),
p7 (nodes >= D.nodeM), p8 (roster >= D.enemyRowM) against the same rows
pickSeat walks; returns true when all hold. (i > 0 && !memberClear -> seat
fallback keeps the EN1-5 "predicates hold per-member at the worst 5-member
case" guarantee; the bearing stays the only RNG in spacing = 4 sites total.)
AE1's spawnParty (prototype/js/ambush.js lines ~308-335) is the grammar source;
your re-write must keep those exact lines for e.* setup. Math.random total
sites in the file after your edit MUST be exactly 4 and only inside pickSeat
(2), spawnParty bearing (1), tick roll (1). Note the fallback uses slotted
type list; comp n values cap at 2 in the data (worst party = 5 members total,
per family rows).

## 4. Engine wiring (EXACTLY these lines; NOTHING else)

a) game.js line ~3077 after `if (window.WH_AMBUSH) window.WH_AMBUSH.init(game);`
   add: `      if (window.WH_ENCOUNTERS) window.WH_ENCOUNTERS.init(game);`
   (match the surrounding indent exactly)
b) game.js line ~3613 after `window.WH_AMBUSH.tick(dt);`
   add: `    window.WH_ENCOUNTERS.tick(dt);` (match indent)
c) index.html: after the ambush.js script tag (line 80) add
   `<script src="js/encounters.js"></script>` — the file already contains a
   comment at line 82 mentioning encounters band; leave that comment alone.
d) DO NOT touch region-manager.js (its raidMember guard already landed; V-11
   pins its sha byte-stable). DO NOT touch ANY engine file beyond game.js,
   CONFIG.js, index.html. NO git commands whatsoever (IO owns the gate).

## 5. Stage order (STRICT — code first, prose last) + budget

MAX ~30 tool calls total. No narration between calls. Skip all reads except
the exact edit regions you patch.

S1. FINISH encounters.js: delete rollRow, replace spawnParty, add memberClear.
    Immediately `node --check prototype/js/encounters.js` -> must exit 0.
S2. ADD the §2 CONFIG block (single patch anchored on the raid-block-end ->
    hazards seam). `node --check prototype/js/CONFIG.js` -> exit 0.
S3. game.js 2 lines + index.html 1 tag. `node --check prototype/js/game.js`
    -> exit 0.
S4. Smoke the pre-written Testerbot probes (they are the "existing suite"):
    mkdir -p /tmp/wh-probe-out && cd /tmp/wh-worldfeat &&
    node scratch/cc-en1-probe/probe_config_baseline.js post
    node scratch/cc-en1-probe/probe_weight_law.js
    node scratch/cc-en1-probe/probe_transient_law.js
    node scratch/cc-en1-probe/probe_gates_matrix.js
    Expected prints: census PASS lines, `WEIGHT-LAW PASS`,
    `TRANSIENT-LAW PASS`, `GATE-MATRIX PASS`. If a probe fails, FIX THE CODE
    (probes are the pinned law, not the enemy) and re-run. Do NOT edit the
    probes.
S5. `python3 tools/build_v8.py` twice; `sha256sum prototype/builds/v8-playable.html`
    after each; two shas MUST be equal. Bundle greps:
    `grep -c "CC-EN1" prototype/builds/v8-playable.html` >= 1 and
    `grep -c "window.WH_ENCOUNTERS" prototype/builds/v8-playable.html` >= 1.
S6. V-2 surface check: `git diff HEAD --stat` must show ONLY: CONFIG.js,
    game.js, index.html, builds/v8-playable.html modified + encounters.js new
    (+ the pre-existing untracked io/specs/cc-en1-*, io/reports none yet,
    scratch/cc-en1-probe/). `git diff HEAD -- prototype/js/game.js | grep -c
    "^+.*WH_ENCOUNTERS"` == 2. region-manager diff empty:
    `diff <(git show HEAD:prototype/js/region-manager.js)
    prototype/js/region-manager.js` -> empty output.
S7. Write /tmp/delegation_result_ccen1_finish.md NOW (mandatory result file):
    files changed, probe outputs verbatim, both build shas, V-2 counts, any
    deviation (extra toast site would be a deviation to name, not to hide).
S8. Only if calls remain: re-run one flaky probe for a stable transcript.

## 6. Pass line (what Testerbot will independently re-run)

V-1 node --check x3 = 0 | V-2 surface 2/1/0 + region-manager byte-stable |
V-3 census families [1,2,3,5,8] night + [3] day + pending keys F2/F4/F6/F7
(darkwood) & F1/F6/F7 (regionC), comp types in {bandit,ghoul,wolf,coven},
regionC note keeps "no second director" + cc-ae1 | V-4 weights len 6 sum 1.0
w0 0 | V-5 GATE-MATRIX PASS | V-6 TRANSIENT-LAW PASS both halves | V-7 zero
THREE constructions in encounters.js, one toast helper, debugMute respected |
V-8 exactly 4 Math.random sites in {pickSeat, spawnParty, tick roll} | V-9 two
build runs sha-equal + markers | V-10 worktree surface exactly the round's
files, nothing staged.
