# CC-LS1 — Blob Contact Shadows (doc 61 P1-1) — SPEC

Lane: doc 61 `61-world-audit.md` P1-1 (S, code only). Art anchors (viewed this
wake): `concept-01-darkwood.png` — amber lantern pool + "soft contact darkness"
under the actor's feet; `concept-05-night-ambush.png` — "deep contact shadows
anchoring figures into the terrain". Palette law: single amber accent, cool
indigo-charcoal night, black-blob shadow only (no colored light).

Doc 61 P1-1 verbatim contract:
> one shared CircleGeometry with a radial CanvasTexture and a
> MeshBasicMaterial (transparent, no depth write, polygonOffset), fixed at
> y=0.02 under each actor's x/z and not bobbed. It fades and shrinks as the
> root rises (hop, death).

Scope: ADDITIVE module + minimal wiring. No change to any existing system.

## A-1. New file `prototype/js/shadows.js` (namespace `window.WH_SHCONTACTS`)

IIFE, 'use strict', ES5. One global. No allocations per frame after init.

API (exactly three functions + init):

- `init(scene, cfg)` — creates the shared pool ONCE (cfg = CONFIG.contacts):
  - ONE `THREE.CircleGeometry(1, 16)` shared by every blob mesh (per-actor
    scaling uses `mesh.scale`, never geometry).
  - ONE radial `CanvasTexture` (cfg.textureSize=128): black core →
    transparent edge, alpha ~0.55 at half radius, linear falloff.
  - ONE `MeshBasicMaterial({ color:0x000000, map:tex, transparent:true,
    depthWrite:false, polygonOffset:true, polygonOffsetFactor:-2,
    polygonOffsetUnits:-2 })`; `mesh.castShadow = mesh.receiveShadow = false`.
  - Pool size = cfg.poolSize (24). Free-list acquire/release. Exhaustion =
    silent skip + at most ONE console.warn per init (no per-frame noise, no
    per-frame allocation — P1-8 pool law).
  - `mesh.rotation.x = -PI/2`.
- `attach(owner, opts)` — binds the next free pooled mesh to `owner`
  (idempotent: re-attach of the same owner = no-op). `opts` (all optional):
  `{ radius, bodyName, scale }`. Radius resolution order: explicit `radius`
  → `(WH_ASSETS.getMeta(bodyName)||{}).width * 0.5 * (scale||1)` →
  `cfg.radiusBase`. No meta loaded yet (stand-in) → radiusBase fallback.
- `update()` — one pass over bound slots:
  - Blob x/z = `owner.root.position.x/z` (position only, never yawed).
  - Blob y = ground of the TICK: `owner.pos.y + cfg.groundOffset (0.02)` when
    `owner.pos` exists (player + enemies; CC-C5 ground-in-pos law), else
    `owner.root.position.y + 0.02`.
  - Lift key = `max(0, owner.root.position.y - owner.pos.y)` (hop, corpse
    fall, pz.lift — all ride root above pos in enemy.js:300/712/747/1683).
    `k = clamp(1 - lift/cfg.maxLift, 0, 1)`;
    `opacity = cfg.maxOpacity * k`;
    `scale = radius * (cfg.minScale + (1-cfg.minScale) * k)`.
    Standing actor (lift 0) = full blob; corpse rising = fades+shrinks;
    sinking (negative delta) = stays full.
  - Freed when `owner.root.parent === null` (region swap / despawn) — every
    tick validates, no explicit detach call needed elsewhere.
- `detach(owner)` — explicit release (exported for tests only).

## A-2. CONFIG additive block `contacts` (append inside CONFIG object, additive only)

```
// CC-LS1 (doc 61 P1-1): blob contact shadows - one shared geometry+texture,
// pooled meshes riding actor ground (pos.y) un-bobbed; fade+shrinks on lift.
contacts: {
  poolSize: 24,        // player + live enemies worst case
  textureSize: 128,
  radiusBase: 0.55,    // fallback when body meta width is missing
  groundOffset: 0.02,  // doc 61 law: y = 0.02 over ground
  maxLift: 3.2,        // lift at which a blob vanishes
  minScale: 0.55,      // distant/bounce floor so the blob never pops out
  maxOpacity: 0.42
}
```
(Values PROPOSED, Nicko tunes. The block ships with exactly the 7 keys above,
no extras.)

## A-3. `index.html`

Add `<script src="js/shadows.js"></script>` immediately before the game.js tag
(72-84 window). Before `game.js` is mandatory (boot-time check A-5).

## A-4. `game.js` wiring (≤ 10 added lines total in 3 sites)

1. Boot (after `game.playerLight` init ~line 170, inside the same setup
   region): `if (window.WH_SHCONTACTS) window.WH_SHCONTACTS.init(scene,
   CFG.contacts);` (tagged comment `// CC-LS1:`).
2. After `game.player.setBody(pBody)` (line 2583):
   `// CC-LS1: player contact blob (radius from body meta width)`
   `if (window.WH_SHCONTACTS) window.WH_SHCONTACTS.attach(game.player,`
   `  { bodyName: 'playerBody' });`
3. Per-frame (once, next to `game.playerLight.update(game.player, ...)`
   ~3260): `// CC-LS1:` `if (window.WH_SHCONTACTS)
   window.WH_SHCONTACTS.update();`

## A-5. `region-manager.js` enemy wiring (1 site)

At the enemy body build site (~line 1926, directly after
`enemy.setBody(eBody)`):
`// CC-LS1: per-enemy contact blob; radius from body meta width x scale`
`if (window.WH_SHCONTACTS) window.WH_SHCONTACTS.attach(enemy,`
`  { bodyName: <body-name string in scope at the site>, scale: eScale });`

The exact in-scope variable names are owned by the landed code — the valspec
census names them (body-name string in scope at the site; scale variable is
`eScale` per the landed region-manager.js 1926 window, valspec D4); Devbot
reads region-manager.js around 1900-1930 and uses what is there. CC-C7 note:
cfg.scale enemies carry the scaled holder — pass the same scale the holder
used.

## A-6. Laws

- Bob/tilt/sway writes go to `body.position` (player.js:349) and root-lift
  terms are pos-anchored (enemy.js 712/747/1683) — the blob MUST read ground
  from `owner.pos.y`, never from body bob.
- Deterministic build: `python3 tools/build_v8.py` (newest tool law) exits 0,
  twice, byte-identical; bundle carries `CC-LS1` markers (>= 6).
- Byte-sacred files (journal/bestiary/wolf/ambush/hazard js, save.js, style
  css families) receive ZERO edits.
- NO-GIT: children never commit, never push, never touch git config.
- No harness runs, no headless browser smoke tests. Static + node-script
  validation only (Testerbot's domain, spec-gated).

## A-7. Acceptance (Testerbot)

- V-1 CONFIG: `contacts` block parses (node --check + load), exactly the 7
  keys, additive-only diff vs parent commit (no existing row edits).
- V-2 API surface: `init/attach/update/detach` present; pool singletons
  (one geometry, one texture, one material across the pool).
- V-3 Pool physics: synthetic owners - acquire, exhaustion silent, free on
  parent-null, idempotent re-attach.
- V-4 Transform law numeric table: lift 0 / 0.8 / 3.2 / 4.0 →
  k = 1 / 0.75 / 0 / 0 (clamped; valspec D1 arithmetic ruling) →
  opacity maxOpacity*k, scale interpolates toward
  minScale; blob y == pos.y + 0.02 with root lifted; x/z track root.
- V-5 Wiring census: index tag order (shadows.js BEFORE game.js), boot init
  in setup region, player attach after setBody, per-frame update near
  playerLight, region-manager per-enemy attach with scale passthrough.
- V-6 Zero regression: no edits outside shadows.js (new), CONFIG append,
  index.html 1 line, game.js 3 sites, region-manager.js 1 site; build
  deterministic x2; prior markers intact (CC-AE1 x6, QJR-2 x8, CC-WB2 x6,
  CC-H6 lastchancel, QJR-4, WH_AFF x14).
- V-7 No-regression runtime census (static): lighting rows untouched
  (hemi/moon/lantern CONFIG + game.js rig), P1-8 light pool untouched.
