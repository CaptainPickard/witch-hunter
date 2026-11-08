# Asset pipeline report — io/missions/2026-10-11-asset-pipeline.md

Baseline a32d5f6eb707bb5da9b4545d4ce900261d0d3123, branch feat/world-visuals.
No harness, no browser, no game runs (standing law). IO verifies on the real
phone after the flip. Builder lane: Claude Code print mode.

## 0. Root cause (as the brief states it, confirmed in the code)

Every asset fetched in parallel, a fixed 20 s abort per asset, ~90 MB per
boot, and a mobile pipe of ~1-8 MB/s. `preloadAll()` (assets.js, a32d5f6)
fired `loadOne` for all 50 manifest names at once. Each one raced a flat
`CONFIG.assets.timeoutMs` (20000). On a ~1 MB/s shared link, 50 streams each
get about 20 KB/s, so a 6.4 MB body needs minutes. A "timeout" also did NOT
abort the fetch. The zombie download kept using the pipe while its retry
started a second copy, which made the next timeout more likely. Any client
slower than about 4.5 MB/s aggregate could not boot. Parsing and serving were
both fine.

The test sim (section 4, case 3) reproduces this. The legacy settings (all
parallel, flat 20 s) on a simulated 1 MB/s shared link give 13 stand-ins,
including playerBody, cemeteryGate, yewTree, livingOak, youngAsh and bramble.
That matches Nicko's screenshots. The new settings on the same link give
0 stand-ins and 0 retries, and the boot barrier opens at 55.8 s.

Size note: the 50 manifest GLBs in this worktree add up to **52.4 MB**
(measured with fs.stat). The brief's ~90 MB is IO's per-boot figure. The
difference may be the body atlases, sky panoramas, the 3.1 MB page and the
CSP probe, but I did not re-measure IO's number.

## 1. Per-unit summary

**P1 — prioritized, capped, timeout-scaled loader (prototype/js/assets.js + CONFIG.assets)**
- New CONFIG.assets rows:
  - `assetTimeoutMsPerMb: 6000`, `assetTimeoutMinMs: 20000`, `assetTimeoutMaxMs: 120000`
  - `criticalPoolSize: 4`, `streamPoolSize: 6`
  - `stallLineAfterMs: 8000`
  - `bootCritical: [46 names]` (section 2)
  - `timeoutMs` stays, but only daynight.js sky textures use it now. Its comment says so.
- a. **Two-phase manifest.** `CRITICAL` holds the bootCritical names in CONFIG
  order. Unknown names are dropped with a warn and duplicates are ignored.
  `DEFERRED` is every other manifest name.
- b. **Pools.** `runPool(names, size, run)` keeps at most `size` loads in
  flight, started in list order. Criticals run through a pool of 4. When every
  critical has settled, the deferred names run through a pool of 6. A pool slot
  is held through retries and backoff, so each slot is one fetch at a time.
- c. **Size-scaled timeout.** `timeoutForBytes(b) = round(clamp(6000 x b/1e6, 20000, 120000))`.
  - MB means 1e6 bytes (decimal), the brief's "6.4 MB".
  - The deadline runs from attempt start. It is re-armed as the size becomes
    known: the size inherited from an earlier attempt, else Content-Length when
    headers land, else the bytes received so far. Before any size is known it
    is the 20 s minimum.
  - The deadline covers fetch plus parse, like the old flat timeout.
  - On expiry the fetch is **aborted** with an AbortController (new).
  - To get Content-Length, chunk progress and abort, the GLB bytes are now
    streamed with `fetch` + `ReadableStream`. They are then handed to
    `WHGLTFLoader.parse(buffer, dir, ...)`. `GLTFLoader.load` keeps its
    FileLoader private, so it offers no progress total and no abort.
  - Embedded-image plugin, URL modifier, prepTemplate, groundAlign and
    swapBodyMap are unchanged.
- d. **Retry law unchanged.** 1 + bodyRetryCount (2) attempts, linear backoff
  750 ms x attempt#, and parse errors do not retry. Retries inherit the scaled
  timeout through `knownBytes[name]`, which the first attempt learned.
- e. **Boot barrier = criticals only.** `preloadAll()` resolves when every
  bootCritical asset has settled, as loaded or as a stand-in.
  `whenAllSettled()` (new) resolves after the deferred stream phase.
  - **Late-swap: VERIFIED MISSING, ADDED.** The old `instance(name)` on an
    uncached name returned `makeStandIn(name)`. That set `failed[name]` and was
    a dead end: no code ever replaced the stand-in, because the old boot waited
    for everything. Now `instance()` on a queued or loading name hands out a
    placeholder stand-in, not marked failed, and records it in
    `pendingHolders`. When the asset lands, `lateSwap(name)` takes the stand-in
    out of that same holder, disposes it, and adds the real clone's root. The
    caller's position, rotation and scale on the holder are kept.
  - If a deferred asset fails, its handed-out stand-ins stay.
  - A late-swapped rigged body would get the mesh but not the clips. All boot
    bodies are critical, so no live caller hits this.
- Extra, same file: the CSP probe (`registerEmbeddedImagePlugin`) did
  `fetch(document.baseURI)` only to read headers. On the phone build that
  downloads the whole 3.1 MB inlined page on the boot pipe. It now cancels the
  body once the headers arrive (`response.body.cancel()`). It is the same
  request, and the CSP logic is unchanged.

**P2 — faster second load (VERIFY only, serving untouched).** A conditional GET
returns 304 on the live share (proof in section 3). The server sends
Last-Modified and Content-Length and no Cache-Control at all, so no `no-store`
anywhere in the chain. A grep of prototype/index.html and prototype/js/*.js
found no `no-store`, `no-cache`, `cache:` fetch option, `?v=` or
`Date.now()+` URL busting. The new loader's `fetch` uses the default cache
mode, so the browser HTTP cache revalidates (or heuristically reuses) the
GLBs on a second load.

**P3 — compression: NOT built (decision).** GLBs are already binary. Gzip gains
only about 5-10% on them, and python http.server does not compress. A
compression layer would need a server or image rebuild, which is IO-owned and
out of scope. The wins come from P2 caching and P1 scheduling. No code was
written for P3.

**P4 — loading UX.**
- `bootProgressCb` now receives `bootState()`: `{done, total, loadedBytes,
  knownBytes, stall}`. `done/total` counts boot-critical assets only (46).
- It fires on every critical settle (the existing per-asset tick), on byte
  progress (throttled to 250 ms), and on a 1 s heartbeat until the barrier.
  The heartbeat keeps the elapsed clock moving even when no bytes arrive.
- game.js adds a bytes row, `#wh-boot-bytes`, under `#wh-boot-sub`. It shows
  "N.N MB received", or the plain-language stall line for the slowest critical
  that has been in flight for at least `stallLineAfterMs` (clocked from its
  first attempt): `slow link: still working, 3.0 MB of 6.4 MB, 30 s elapsed`
  (string taken from test case 7). The row is cleared at the barrier.
- Red banner: `#wh-asset-fail-note` keeps its loud styling and lists
  **failed boot-critical** assets only. Failed deferred assets go on a dim
  10 px line under it (`#wh-asset-fail-late`, "streamed stand-in: ..."). A
  deferred asset that lands late swaps in silently.
- game.js boot hook (TOUCH allows this "ONLY if the boot barrier call site
  needs the two-phase hook"): CONTINUE now waits for `whenAllSettled()`
  before `enterWorld(true)`. A save restore can `switchRegion` into region C.
  C's scatter reads the deferred `bushA`/`bushB` templates and footprints, and
  an incomplete plan builds without them. A fresh boot (NEW GAME and class
  pick) enters at the barrier.

**P5 — mechanical gate.** See sections 4-6. All edited JS passes `node
--check`. The build was regenerated from the repo root, the markers are
present, and the scheduling test gives 46/46 PASS.

**P6 — commit and push.** See section 7. FLIP-HOST-SIDE-PENDING: IO flips.

## 2. Critical-asset list (derived) + why

Derivation: I ran the pure planners `window.WH_ScatterPlan(regionA, meta)` and
`window.WH_WallPlan(meta)` (region-manager.js:1973-1974) in node, with real
moveset.js + CONFIG.js + region-defs.js + region-manager.js and a meta spy that
records every asset name they read. I added region A's `cfg.props`
(region-manager.js:1724 buildRegion), the scatter trees (`instance`, :1739),
the instanced scatter (`getTemplate`, :1387 whBuildInstanced), the wall
segments, arch, lantern and door arches (buildWorld :1487-1545), and the enemy
bodies (:1788). On top of that came the game.js boot site (game.js
preloadAll().then):
- playerBody (game.js `instance('playerBody')`)
- playerDagClips (player.js:188 setBody merges its clips)
- `setupHandMeshes` (game.js:1634), which instances **every** gear mesh in
  CONFIG.items at boot: longsword, dagger, roundShield, torch
- handAxe (enemy.js:103, bandit setBody)
- whTent / whCampkit (brief proposal). CONTINUE restores deployed kit sites,
  and camp.js `makePiece` (camp.js:74) extracts named kit nodes from the
  instance, which a stand-in cannot late-swap.

**Key finding:** the boot set is much larger than the brief's ~12-16 estimate.
`whWallPlan` sets `plan.complete = false` for any missing footprint of
**every region A AND region B prop** (region-manager.js:1172, exclusion
targets "every CONFIG prop collider of BOTH regions"). `buildWorld` then
returns null and builds no wall (:1490). `whScatterPlan` likewise needs every
region A prop footprint (:914). If any of those assets arrives late, region A
boots without its boundary wall or with a partial scatter, and the
region-manager code that would rebuild it is NOT-TOUCH. So every name those
planners read is boot-critical. Region B's build reads the same set (checked:
darkwood_edge gives the identical 37 names), so entering B never waits on a
deferred asset.

bootCritical (46, largest first so the 4-pool drains the big bodies early):
playerBody, banditBody, ghoulBody, playerDagClips, bramble, whCampkit, whTent,
yewTree, livingOak, youngAsh, cemeteryGate, torch, mossBoulder, witchwoodTree,
mourningStatue, deadTree, fallenLog, reachTreeA, lanternWaymarker, picketFence,
treeStump, b3Gate, lanternPost, youngBirch, whWallB, banditCampfire, whWallA,
reachTreeB, reachTreeC, youngDeadTree, whLanternHang, graveMound, dagger,
grassTuft, rubblePile, stoneCrossTilted, roundShield, ironFenceSection,
churchCornerButtress, gravestoneObelisk, churchPewBroken, buriedCoffin,
handAxe, churchArchway, whBushSnare, longsword.

Deferred (4, ~1.0 MB):
- bushA, bushB: region C scatter only
- banditBedroll: the camp bedroll rollback row, unreferenced at boot
- ironFenceCorner: unreferenced at boot

Consequence, stated plainly: in this build the barrier is about 51.4 of
52.4 MB. **The boot fix is the cap plus the scaled timeouts plus abort-on-timeout**,
not a smaller barrier. A smaller barrier would need region-manager to rebuild
the wall and scatter on late footprints, which is NOT-TOUCH. If the planners
are ever made late-tolerant, the bootCritical list can shrink to the brief's
proposed list with no loader change.

## 3. P2 curl 304 proof (host, `python3 /tmp/dhost.py`, workdir /tmp)

Share `current` -> `releases/a32d5f6eb707bb5da9b4545d4ce900261d0d3123`.
```
== plain HEAD  http://127.0.0.1:8793/current/prototype/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.14.8
Content-type: model/gltf-binary
Content-Length: 6451008
Last-Modified: Sun, 11 Oct 2026 02:40:19 GMT
== conditional GET  If-Modified-Since: Sun, 11 Oct 2026 02:40:19 GMT
HTTP/1.0 304 Not Modified
Server: SimpleHTTP/0.6 Python/3.14.8
== page  /current/prototype/builds/v8-playable.html
HTTP/1.0 200 OK   Content-Length: 3131439   Last-Modified: Sun, 11 Oct 2026 02:40:19 GMT   (no Cache-Control)
```
Content-Length is present on the GLBs, so the loader's size-scaled deadline
kicks in at the headers. I checked only the host loopback, not the Tailscale
proxy hop. IO's phone run will show whether that hop keeps Content-Length; if
it does not, the deadline falls back to bytes received, which test case 5
covers.

## 4. Scheduling test output (`scratch/test_loader_scheduling.js`)

Run: `/usr/local/lib/python3.12/site-packages/playwright/driver/node scratch/test_loader_scheduling.js`
(repo root). It loads the real moveset.js, CONFIG.js and assets.js into a
vm. THREE, the GLTF loader, the DOM and fetch are stubbed, and everything runs
on a virtual clock. The fetch stub is a shared-link simulator: bytes/s split
across the streams in flight, real GLB sizes, Content-Length, scripted hangs,
404s and parse errors, and AbortSignal support.
```
PASS CONFIG.assets.assetTimeoutMsPerMb = 6000  [6000]
PASS CONFIG.assets.assetTimeoutMinMs = 20000  [20000]
PASS CONFIG.assets.assetTimeoutMaxMs = 120000  [120000]
PASS CONFIG.assets.criticalPoolSize = 4 / streamPoolSize = 6  [4/6]
PASS bootCritical: every name is a manifest asset (no drops)  [46/46]
PASS bootCritical + deferred partition the manifest  [46 + 4 = 50]
PASS timeout = clamp(6000 x 0 MB, 20 s, 120 s) = 20000 ms  [20000]
PASS timeout = clamp(6000 x 1 MB, 20 s, 120 s) = 20000 ms  [20000]
PASS timeout = clamp(6000 x 3.4 MB, 20 s, 120 s) = 20400 ms  [20400]
PASS timeout = clamp(6000 x 6.4 MB, 20 s, 120 s) = 38400 ms  [38400]
PASS timeout = clamp(6000 x 6.448742 MB, 20 s, 120 s) = 38692 ms  [38692]
PASS timeout = clamp(6000 x 19.9 MB, 20 s, 120 s) = 119400 ms  [119400]
PASS timeout = clamp(6000 x 20 MB, 20 s, 120 s) = 120000 ms  [120000]
PASS timeout = clamp(6000 x 90 MB, 20 s, 120 s) = 120000 ms  [120000]
PASS criticals start in CONFIG.bootCritical order  [playerBody,banditBody,ghoulBody,playerDagClips]
PASS every critical starts before any deferred asset  [first deferred at #46]
PASS no deferred fetch starts before ALL criticals settled  [46/46 46/46 46/46 46/46]
PASS critical pool cap respected (max concurrent critical fetches <= 4)  [4]
PASS stream pool cap respected (max concurrent deferred fetches <= 6)  [4]
PASS never more than 6 GLB fetches in flight  [4]
PASS boot barrier fires once criticals settled (bootState done == total)  [46/46]
PASS boot barrier fires on criticals ONLY (deferred still in flight at barrier)  [deferred settled at barrier 0/4, barrier 55.8 s < all 57.1 s]
PASS 1 MB/s phone pipe: 0 stand-ins with capped pools + size-scaled timeouts  [0 stand-ins, 50 loaded]
PASS 1 MB/s phone pipe: no retries needed  [none]
PASS legacy config (50 parallel, flat 20 s) on the same pipe reproduces the phone stand-ins  [13 stand-ins incl. cemeteryGate,yewTree,livingOak,youngAsh,bramble]
PASS attempt 1 (6.4 MB Content-Length, stalled) aborted at clamp(6000 x 6.4) = 38400 ms  [38400]
PASS retry backoff unchanged (750 ms x attempt#)  [750]
PASS retry inherits the scaled timeout (attempt 2, no headers yet: still 38400 ms, not 20000)  [38400]
PASS timed-out fetches are aborted (signal fired per timeout)  [2]
PASS attempt 3 streaming 6.4 MB at 200 KB/s (~32 s) loads (flat 20 s would have killed it)  [attempts 3]
PASS retry law: max 3 attempts (1 + bodyRetryCount 2)  [3]
PASS no Content-Length: deadline tracks bytes received (6 MB @ 250 KB/s = 24 s loads)  [attempts 1]
PASS 404 retries then stand-in (3 attempts)  [3]
PASS parse error does NOT retry (1 attempt, stand-in)  [1]
PASS failed CRITICAL assets on the loud red line  [Asset stand-in: yewTree (parse - THREE.GLTFLoader: Unsupport]
PASS after the barrier a deferred asset is still pending  [bushA pending]
PASS instance(pending) hands out a stand-in placeholder, NOT marked failed  [standin-bushA]
PASS instance(critical) after the barrier = the real clone  [gltf-root-longsword]
PASS late arrival physically swaps the stand-in (same holder, real root)  [gltf-root-bushA]
PASS late swap keeps the caller placement transform  [5,7]
PASS late swap logged
PASS failed deferred asset keeps its stand-in, marked failed
PASS failed deferred asset NOT on the loud critical line, on the dim streamed line  [streamed stand-in: ironFenceCorner (network - fetc]
PASS progress reports bytes received for criticals  [465 updates]
PASS stall line data: slow asset loaded/total/elapsed past stallLineAfterMs  [slow link: still working, 3.0 MB of 6.4 MB, 30 s elapsed]
PASS final progress update = all criticals settled  [2/2]

phone-pipe sim (1 MB/s shared): boot barrier at 55.8 s
46 PASS, 0 FAIL
```
Exit code 0.

## 5. Scope audit — `git diff --stat a32d5f6` (before commit)

```
 prototype/builds/v8-playable.html | 407 +++++++++++++++++++++++++++++++++-----
 prototype/js/CONFIG.js            |  44 ++++-
 prototype/js/assets.js            | 324 ++++++++++++++++++++++++++----
 prototype/js/game.js              |  39 +++-
 4 files changed, 724 insertions(+), 90 deletions(-)
```
The commit also adds `scratch/test_loader_scheduling.js` and this report. The
regenerated v8-playable.html diff is exactly the 407 changed source lines.

Every touched file is on the TOUCH list:
- CONFIG.js: assets rows only.
- assets.js: the loader.
- game.js: the boot-overlay progress callback, the barrier call site
  `.then`, and the CONTINUE wait.
- v8-playable.html: regenerated.

NOT touched: server/container config, wh_release_flip.py, region-manager.js,
region-defs.js, enemy.js, player.js, camp.js, save.js, daynight.js, style.css,
GLBs, save schema, combat. No NOT-TOUCH file was touched.

## 6. node --check + markers

node --check (playwright driver node v24.21.0):
- prototype/js/assets.js: OK
- prototype/js/game.js: OK
- prototype/js/CONFIG.js: OK
- scratch/test_loader_scheduling.js: OK

`python3 tools/build_v8.py` (repo root) wrote prototype/builds/v8-playable.html,
3146429 bytes. Marker counts (`grep -o | wc -l`):
- assetTimeoutMsPerMb: 3
- bootCritical: 8
- wh-boot-bytes (bytes progress row): 1
- whenAllSettled: 5
- lateSwap: 3

## 7. Commit + push

The host-side origin tip check (`git ls-remote https://github.com/CaptainPickard/witch-hunter.git
refs/heads/feat/world-visuals` through dhost from /tmp) must equal a32d5f6
before the commit. The result and the commit sha are in the builder's final
reply and in `git log -1 -- scratch/asset_pipeline_report.md`, because this
report ships inside the commit. Push: HTTPS to origin feat/world-visuals.
**FLIP-HOST-SIDE-PENDING** (IO flips).

## 8. Deviations + reasons

1. **bootCritical is 46 names, not ~12-16.** It was derived from the real
   planners (section 2). The wall and scatter plans need every A+B prop
   footprint at boot, and region-manager is NOT-TOUCH. As a result the
   two-phase barrier saves only about 1 MB in this build. The boot fix comes
   from the 4-pool, the scaled timeouts and abort.
2. **Brief arithmetic.** "A 6.4 MB body on a 1 MB/s pipe gets ~64 s" does not
   match the locked formula: 6000 x 6.4 = 38.4 s. I implemented the locked
   formula. Sensitivity: 6000 ms/MB means each stream needs at least about
   167 KB/s. At pool 4 that is about 0.67 MB/s aggregate for the largest
   bodies. Below that, the 6.4 MB body will time out on every attempt. The
   knob is `assetTimeoutMsPerMb`.
3. **Loader now uses fetch + `loader.parse`** instead of `loader.load`. That
   was the only way to get Content-Length, byte progress and a real abort.
   Parse, the plugins and post-processing are identical.
4. **The CSP probe now cancels the page body** after reading headers (assets.js,
   in scope). Before, it downloaded the 3.1 MB page on the boot pipe.
5. **game.js CONTINUE waits for the stream phase** (about 1 MB more), so a
   restore into region C never builds its scatter without bushA/bushB. A fresh
   boot is not delayed.
6. **Bar fraction = critical settled/total** (46), not manifest/50. The bytes
   row carries the byte progress. The bar stays per-asset, as the brief
   specifies.
7. Not addressed (out of scope, noted for IO): daynight.js sky panoramas load
   on their own flat `timeoutMs` and share the pipe once the day clock runs.
   The body atlas PNGs (swapBodyMap) have no timeout and no progress. Both are
   small or happen after boot.
