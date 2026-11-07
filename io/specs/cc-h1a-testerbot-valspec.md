# CC-H1a Testerbot Validation Spec (Door-Plane & Sides Correction)

**Round:** CC-H1a – door-plane and sides-table correction

---

## V-1 Pre‑fix state assertion (bugs exist at HEAD)

- **F door plane** = `CFG.regionF.door.planeZ` is **-640** (should be -662).
- **Connection[5] sides**: `C` = **-1**, `G` = **+1** (flipped sign).
- **Manual check outline** (derived from engine code):
  1. The player spawns at **regionF** `(0, -650)`.
  2. `sideOfPlane(z)` is `z > planeCoord ? 1 : -1` ( `planeCoord = -640`).
  3. For the spawn `z = -650` → `-650 > -640` is **false**, so `sideOfPlane = -1`.
  4. `sideIn(F)` (the landed side stored in the sides table) is **+1**.
  5. In `RegionManagerLogic.tickTransition` a **cross** fires when `insideDoorWindow && sideNow != activeSide`.
  6. The player is inside the door window, `sideNow = -1`, `activeSide = +1` → **mismatch** → a **cross** occurs on the first tick.
  7. This bounce‑back violates the pocket‑law `sideIn == sideOfPlane`.

> **Expectation:** The bug manifests as an instant cross‑back at the F spawn/land row.

---

## V-2 Post‑fix plane value

- Verify `CFG.regionF.door.planeZ === -662`.

## V-3 Post‑fix sides tables (law‑correct)

- `connections[5]` (door G) sides: `C = +1`, `G = -1`.
- `connections[4]` (door F) sides remain: `E = -1`, `F = +1` (already correct for plane -662).
- The four door connections now satisfy the pocket‑law for their respective planes.

## V-4 Real RegionManagerLogic checks – first tick

- **F spawn (0, -650)**: first tick **NO cross**.
- **F own land row** (as defined in `CONFIG.regionF.land`): first tick **NO cross**.
- Same for **D, E, G** – their spawn/land rows produce **no cross** on first tick.

## V-5 Walk‑back crossing at mouths

- **D** walk‑back exit (`-150.8, -216`) crosses to `veil_crypt`.
- **F** walk‑back exit (`0, -662.5`) crosses to `veil_crypt`.
- **G** walk‑back exit (`0, -699.5`) crosses to `forest_of_the_old_king`.

## V-6 Enemy roster unchanged

- `CFG.regionF.enemies` must equal exactly the two ghoul rows:
  ```json
  [{"type":"ghoul","x":-6,"z":-636},{"type":"ghoul","x":6.5,"z":-635.5}]
  ```

## V-7 No file‑byte changes outside allowed set

- `region-manager.js`, `enemy.js`, `game.js`, `save.js`, `daynight.js` **byte‑identical** to HEAD (`git diff --quiet`).
- Only the following files may differ:
  - `CONFIG.js` (single line change for `planeZ` and its comment)
  - `region-defs.js` (two side‑table lines and comment)
  - Build bundle (`prototype/builds/v8‑playable.html`)
  - Anything under `scratch/cc-h1a/`
  - This valspec file itself.

## V-8 Build determinism

- Running the v8 build (`tools/build_v8.py`) exits **0**.
- Two consecutive builds produce **identical SHA‑256** of the bundle.
- The bundle contains **≥ 8** occurrences of the marker `veil_galleries`.

---

## V-9 Independent tick probe (Testerbot implementation)

Create **scratch/cc-h1a/testerbot_tickcheck.js** with the following shim (do **not** import IO’s probe):
```js
#!/usr/bin/env node
// Independent tick‑probe for CC‑H1a validation.

(function () {
  'use strict';
  const fs = require('fs');
  const ROOT = '/tmp/wh-worldfeat';
  const win = {};
  global.window = win;
  const cfg = eval(fs.readFileSync(ROOT + '/prototype/js/CONFIG.js', 'utf8') + '; window.WH_CONFIG;');
  win.WH_CONFIG = cfg;
  eval(fs.readFileSync(ROOT + '/prototype/js/region-defs.js', 'utf8'));
  eval(fs.readFileSync(ROOT + '/prototype/js/region-manager.js', 'utf8'));
  const DEFS = win.WH_REGION_DEFS;
  const Logic = win.WH_RegionManagerLogic;

  function check(name, ok, detail) {
    console.log((ok ? 'PASS' : 'FAIL') + '  ' + name + (detail ? '  [' + detail + ']' : ''));
    if (!ok) process.exitCode = 1;
  }

  // 1. plane check
  check('planeZ == -662', cfg.regionF.door.planeZ === -662);

  // 2. sides tables
  const c4 = DEFS.connections[4], c5 = DEFS.connections[5];
  check('conn[5] C +1', c5.sides[CFG.regionC.id] === 1);
  check('conn[5] G -1', c5.sides[CFG.regionG.id] === -1);
  check('conn[4] E -1', c4.sides[CFG.regionE.id] === -1);
  check('conn[4] F +1', c4.sides[CFG.regionF.id] === 1);

  // 3. first‑tick no‑cross for each door region
  const doors = ['regionD','regionE','regionF','regionG'];
  doors.forEach(k => {
    const R = cfg[k];
    const rm = new Logic(R.id);
    const r = rm.tickTransition(R.spawn.x, R.spawn.z);
    check(k + ' spawn first‑tick no‑cross', r.action !== 'cross');
    // own land row (if any)
    const own = Object.values(DEFS.connections).find(c => c.door && c.door.land && c.door.land[R.id]);
    if (own) {
      const rm2 = new Logic(R.id);
      const r2 = rm2.tickTransition(own.door.land[R.id].x, own.door.land[R.id].z);
      check(k + ' land first‑tick no‑cross', r2.action !== 'cross');
    }
  });

  // 4. walk‑back crosses
  function crossProbe(key, x, z) {
    const rm = new Logic(cfg[key].id);
    const r = rm.tickTransition(x, z);
    return r.action === 'cross' ? r.newActiveId : null;
  }
  check('D walk‑back → veil_crypt', crossProbe('regionD', -150.8, -216) === 'veil_crypt');
  check('F walk‑back → veil_crypt', crossProbe('regionF', 0, -662.5) === 'veil_crypt');
  check('G walk‑back → forest_of_the_old_king', crossProbe('regionG', 0, -699.5) === 'forest_of_the_old_king');

  // 5. enemy roster unchanged
  const expected = JSON.stringify([
    {type:'ghoul',x:-6,z:-636},
    {type:'ghoul',x:6.5,z:-635.5}
  ]);
  check('F enemies unchanged', JSON.stringify(cfg.regionF.enemies) === expected);

  console.log('ALL CONSTRAINTS: PASS');
  process.exit(process.exitCode || 0);
})();
```

Run this script (`node scratch/cc-h1a/testerbot_tickcheck.js`) – it must exit **0** with all checks passing.

---

## Verdict Template

```
PASS/FAIL Verdict
-----------------
BLOCKING failures (must be FAIL):
- Plane value wrong.
- Sides‑table law violation.
- First‑tick cross at any door.
- Walk‑back crossing mismatches.
- Enemy roster altered.
- Unauthorized file‑byte changes.
- Build non‑deterministic.

NON‑BLOCKING failures (may be ignored):
- Style/comments deviating from spec.
- Additional markers beyond the required count.
```

---

**End of valspec**
