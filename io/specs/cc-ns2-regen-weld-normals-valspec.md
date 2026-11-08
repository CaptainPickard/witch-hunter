# CC-NS2 VALSPEC — testerbot validation spec (native welded-law normals in regen pipelines)

Author: testerbot (independent validation seat) 2026-11-08, for IO spec of record
`io/specs/cc-ns2-regen-weld-normals-spec.md` (round CC-NS2, Autopilot wake 45).
Validates the DEVBOT build (section 3 of that spec) against the seven law areas
of spec section 4. Testerbot runs this spec unaided and writes the verdict; a
FAIL on any V-check bounces the round to IO (remedy round), no fixes by the
tester itself.

Baseline facts pinned during valspec authoring (2026-11-08, probes:
**`scratch/ns2-valspec-probe1/`, cleanup note at end**):

- `HEAD = 0f07801256022328663f0f006377e8dfaf9a9ce5` ("build: v8 stamp 759cb60
  CC-NS1…"). "Pristine"/"baseline" below always means `git show <sha>:<path>`,
  never the worktree copy, except for path pins marked "worktree-identical".
- `art-direction/3d/regen_pipeline_v3.py` and
  `art-direction/3d/biome_pixelate.py` are byte-unchanged since `9c0fd6c`
  (`git diff --name-only 9c0fd6c -- <path>` → empty for both). Pre-CC-NS2
  worktree sha256: `f289d2bf…c463e6c` (regen), `4ee02214…6c1e85` (pixelate).
  Post-CC-NS2 worktree shas are DIFFERENT-BUILD facts; validator recomputes.
- `art-direction/3d/add_normals_v2.py` sha256 = **`32b83a20a2d6eae525068a2
  3cbb3b0747d432de110100181f9df3b2e66ee955a`** (CC-NS1 artifact; spec law: not
  touched this round; any byte change is a hard FAIL).
- `python3 art-direction/3d/add_normals_v2.py --verify` from repo root →
  `root=… examined=325 processed=0 skipped=325 wouldProcess=0 errors=0`
  (all assets NORMAL-carrying). Same output required post-build (V-9).
- Asset sha sweep baseline (325 GLBs, sorted paths): full output preserved at
  `scratch/ns2-valspec-probe1/assets-sha-baseline.txt`; list-level sha256 =
  **`0dfd1cf7dd46cdce9a13bf6528068050a693a4531e39502d303386de9438784d`**.
  Re-derivation formula: `cd /tmp/wh-worldfeat && sha256sum $(find
  art-direction/3d/assets -name '*.glb' -type f | sort) > <tmpfile>` — this
  byte-for-byte reproduction (absolute-prefix-independent because paths are
  relative and find is deterministic) must hash to the pinned value.
- Environment: no `.venv` in the repo; system `/usr/bin/python3` has
  numpy 2.5.1 / scipy 1.18.0 / trimesh 5.1.0 / PIL 12.3.0. All V-checks run
  from repo root `/tmp/wh-worldfeat` (worktree, branch `feat/world-visuals`).
  NEVER activate a project venv that lacks scipy (the kernel hard-imports it).
- Ground-truth shape of an un-normal raw pipeline SOURCE (kernel input, both
  biomeLibrary raw + races_regen): single mesh, single prim, attribute order
  exactly `[POSITION, TEXCOORD_0]` (no NORMAL) on a fresh trimesh GLB export,
  POS accessor VEC3/5126 packed (byteStride 12, min/max present), index
  accessor comp 5125, one buffer, no `uri`, bufferView target absent.
  CC-NS1 law output shape after `process_glb`: `[POSITION, NORMAL,
  TEXCOORD_0]` (nomat files: `[POSITION, NORMAL]`), NORMAL accessor
  VEC3/5126 / count == posCount / byteView target 34962 / min+max present,
  byte growth = exactly `payload + JSON-overhead` where payload = `12*verts`
  and measured JSON overhead <= 4096 bytes (pinned example: 276 bytes on
  grass-tuft, 1986844 → 2002624).
- Weld behaviors measured on the pinned probe set (valspec probe 1): b6-bracken
  guard=8, m11-moonbell guard=2, wh-grass-tuft guard=0 (pairs=1698,
  weldedVerts=425), rotspawn guard=0 (pairs=2985, weldedVerts=1049),
  wolf guard=0 (pairs=3384, weldedVerts=10032). Determinism of law_normals
  byte-verified (sha `47429c5b2841a8d4…`, two runs).
- races_regen has 13 GLBs; NAMES list names 10 (rotmother, rotspawn, wolf
  excluded) — same lag law as the biome raw dir, validated by V-8.
- biome_pixelate old IDS literal is `['m1','m2',…'m9']` (9 ids); raw dir holds
  50 GLBs (6 b3-, 6 b6-, 21 m*, 17 wh-* as of baseline) — V-8 pins the fix.

Every V-check's exact command(s), pass criteria, and fail criteria are listed
inline. Script-mode steps (V-3, V-4, V-6, V-7, V-8b) use a sandbox layout under
`scratch/ns2-sandbox/` created by the checker from `scratch/ns2-…-driver.py`
files (no new repo code is checked in; all driver code lives under scratch/).

## Sandbox hygiene (applies to every V-check)

- Every scratch run must be preceded by `sha256sum $(find art-direction/3d/assets -name
  '*.glb' -type f | sort) > /tmp/ns2-assets-before.txt` (or any scratch path)
  and followed by the same into another file plus `diff`/hash-compare; ANY
  mismatch is a hard FAIL and aborts the verdict (asset-file writes during
  validation are prohibited by the spec's sandbox discipline and by the
  baseline facts above).
- The ONLY files allowed to change are under `scratch/` (and the two pipeline
  scripts under test, which the BUILD owns, not validation). Scratch trees use
  ONLY `scratch/ns2-sandbox/` and `scratch/ns2-…-driver.py` files, never
  anything under `art-direction/`.
- V-checks that run pipeline code must always redirect the pipeline's output
  dir into `scratch/ns2-sandbox/…`, using the module-attribute override rule
  (SRC/OUT/NAMES/IDS are module attributes, see V-2/V-3 drivers), with
  overrides applied BEFORE main() is called; if a run writes outside scratch/
  (e.g. into `art-direction/3d/assets/`), the sha sweep catches it and it's a
  hard FAIL regardless of any other result.
- Scripts under test keep `os.chdir` behavior only for their historical entry
  (`__main__`); drivers must `chdir` to the worktree root first (default), run
  the pipeline as an IN-PROCESS import with attribute overrides, then chdir
  back — never relying on the old hardcoded `/root/projects/witch-hunter`
  path (post-CC-NS2 that chdir must be gone; see V-6b).
- Every driver script must finish by `print`ing a single-line JSON summary
  `{"check":"<name>","fail":<0|1>,…}` so a verdict table can be assembled
  mechanically.

---

## V-1 — Spec-anchored pre-build (worktree scripts == pristine at HEAD)

What: prove the two pipeline scripts at worktree state are byte-identical to
HEAD (`0f07801`) BEFORE validation surgery, that the kernel script is untouched
vs HEAD, and that the CC-NS1 baseline facts above still hold. This anchors
"the build we're validating" vs "the build that already shipped".

Commands (all from repo root, one block, exit nonzero on any fail):

```bash
cd /tmp/wh-worldfeat && bash -c '
set -e
HEAD=0f07801256022328663f0f006377e8dfaf9a9ce5
for p in art-direction/3d/regen_pipeline_v3.py art-direction/3d/biome_pixelate.py art-direction/3d/add_normals_v2.py; do
  a=$(git show $HEAD:$p | sha256sum | cut -d" " -f1)
  b=$(sha256sum $p | cut -d" " -f1)
  echo "$p HEAD=$a worktree=$b"
  [ "$a" = "$b" ] || { echo "V-1 FAIL: $p differs from HEAD"; exit 1; }
done
# post-build: scripts under test SHOULD differ from HEAD; kernel MUST NOT.
echo V-1 preruns OK
' ; echo "rc=$?"
```

(At verdict time — i.e. after the Devbot build — rerun the same loop expecting
regen_pipeline_v3.py / biome_pixelate.py to LEGITIMATELY differ (new shas →
print them into the verdict), while add_normals_v2.py must still match HEAD —
see V-9.)

PASS: rc=0 at pre-build; at verdict, the add_normals_v2 line still matches, the
other two names produce a DIFF sha which is RECORDED in the verdict report.
FAIL: any script that differs at pre-build; add_normals_v2.py differing at any
point (kernel touched = instant FAIL); regen/pixelate unchanged at verdict
(build did not happen = FAIL).

## V-2 — Sandbox build: SRC/OUT/NAMES/IDS overridable, outputs land under scratch/

What: build an isolated sandbox tree entirely under `scratch/` and prove both
pipeline scripts' output paths are FULLY overridable via module attributes
(SRC/OUT/NAMES/IDS), per the spec §4 sandboxing law, with output GLBs landing
exclusively under `scratch/ns2-sandbox/…` and NOTHING under `art-direction/`
changing (sha discipline above enforces this globally).

Layout (exact; created fresh by the driver script):

```
scratch/ns2-sandbox/
  raw/biome/           <- COPIES of chosen biome_library/raw GLBs
  raw/races/           <- COPIES of chosen races_regen GLBs
  out/biome/           <- pipeline pixelate outputs land here
  out/races/           <- pipeline regen outputs land here
  ns2-biome-stats.jsonl <- (written by the built pipeline, read by V-7)
  ns2-regen-stats.jsonl <- (written by the built pipeline, read by V-7)
```

Driver `scratch/ns2-regen-driver.py` (the full text; save exactly this and run
`python3 scratch/ns2-regen-driver.py` from repo root; it must print rc=0 and
JSON line):

```python
# scratch/ns2-regen-driver.py — CC-NS2 valspec V-2/V-3/V-6 driver (regen half)
# Copies representative raw races bodies into the sandbox, imports the BUILT
# regen_pipeline_v3 module (post-Devbot), overrides SRC/OUT/NAMES, runs it,
# then asserts every output landed under scratch/.  Exit 0 = sandbox shape OK.
import os, sys, json, shutil, subprocess, hashlib

NS2 = 'scratch/ns2-sandbox'
RAW = os.path.join(NS2, 'raw/races')
OUT = os.path.join(NS2, 'out/races')
PICKS = ['dwarf-female', 'orc-male-warrior', 'wolf', 'rotspawn']
fails = []

# AMEND-VALSPEC-4 (IO, wake 45): targeted cleanup — the whole-sandbox rmtree
# the first draft pinned would let the second V-2 driver delete the first
# driver's outputs (bio rmtree wipes races). Each driver owns its subtree:
for sub in (RAW, OUT):
    shutil.rmtree(sub, ignore_errors=True)
for f in (NS2 + '/ns2-regen-stats.jsonl',):
    if os.path.exists(f):
        os.remove(f)
os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
for n in PICKS:
    shutil.copy(f'art-direction/3d/assets/races_regen/{n}.glb', RAW)

sys.path.insert(0, os.path.abspath('art-direction/3d'))
import regen_pipeline_v3 as rp
# module-attribute override BEFORE any run:
rp.SRC   = 'scratch/ns2-sandbox/raw/races'
rp.OUT   = 'scratch/ns2-sandbox/out/races'
rp.NAMES = list(PICKS)
# AMEND-VALSPEC-3: stats file must be sandbox-pathed for V-7's row audit:
os.environ['NS2_STATS_PATH'] = 'scratch/ns2-sandbox/ns2-regen-stats.jsonl'
assert rp.OUT != 'art-direction/3d/assets/races'

import io as _io
_cap = []
class _Cap:
    def write(self, s): _cap.append(s)
    def flush(self): pass
old, sys.stdout = sys.stdout, _Cap()
rc = 0
try:
    # run the pipeline's main body in-process (respects overridden attrs)
    if hasattr(rp, 'main'):
        rp.main()
    else:
        # exact-name fallback for the script's existing __main__ loop
        for name in rp.NAMES:
            rp.run_one(name) if hasattr(rp, 'run_one') else rp.process(name)
except Exception as e:
    rc = 1; fails.append(('main-raised', repr(e)[:200]))
finally:
    sys.stdout = old

written = sorted(
    os.path.join(dp, f) for dp, _, fs in os.walk(OUT) for f in fs)
want = sum(2 for _ in PICKS)   # raw + pixelated per name
if len(written) != want:
    fails.append(('out-glbs', len(written), want))
# nothing written outside scratch/: full sha sweep of the assets dir BEFORE
# vs AFTER is done by the checker (V-1 hygiene), not here; but we refuse any
# absolute path escapes:
for w in written:
    assert os.path.relpath(w, '.').startswith('scratch/'), w
print(json.dumps({'check': 'V-2-regen-driver', 'rc': rc, 'outGlbs': len(written),
                  'fail': int(bool(fails)), 'detail': fails[:4]}))
sys.exit(1 if fails else 0)
```

Driver `scratch/ns2-biome-driver.py` (full text, same discipline for the
pixelate pipeline; note that after the CC-NS2 build it MUST not chdir — the
driver asserts it ran and the outputs landed where overrides say):

```python
# scratch/ns2-biome-driver.py — CC-NS2 valspec V-2/V-3/V-6 driver (biome half)
import os, sys, json, shutil

NS2 = 'scratch/ns2-sandbox'
RAW = os.path.join(NS2, 'raw/biome')
OUT = os.path.join(NS2, 'out/biome')
# >= 4 raw GLBs across families incl. b3-, b6-, m- (spec §4 sandbox law):
PICKS = ['b3-spire', 'b6-bracken', 'b6-mushrooms', 'm11-moonbell',
         'm12-grave-moss', 'm1']
fails = []

# AMEND-VALSPEC-4 (IO, wake 45): targeted cleanup (own subtree only) — see
# the regen driver header; the whole-sandbox rmtree would delete the other
# half's V-2 outputs and break V-3's 20-file / V-7's 12+8-row expectations.
for sub in (RAW, OUT):
    shutil.rmtree(sub, ignore_errors=True)
for f in (NS2 + '/ns2-biome-stats.jsonl',):
    if os.path.exists(f):
        os.remove(f)
os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
for n in PICKS:
    shutil.copy(f'art-direction/3d/assets/biome_library/raw/{n}.glb', RAW)

sys.path.insert(0, os.path.abspath('art-direction/3d'))
import biome_pixelate as bp
bp.SRC = 'scratch/ns2-sandbox/raw/biome'
bp.OUT = 'scratch/ns2-sandbox/out/biome'
bp.IDS = list(PICKS)
# AMEND-VALSPEC-3: stats file must be sandbox-pathed for V-7's row audit:
os.environ['BP_STATS_PATH'] = 'scratch/ns2-sandbox/ns2-biome-stats.jsonl'

old = os.getcwd()
sys.path.insert(0, '.')
rc = 0
try:
    bp.main()   # post-CC-NS2 main() must NOT os.chdir (V-6b pins that)
except Exception as e:
    rc = 1; fails.append(('main-raised', repr(e)[:200]))
finally:
    if os.getcwd() != old:
        fails.append(('cwd-drift', os.getcwd()))
    os.chdir(old)

written = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(OUT) for f in fs)
want = 2 * len(PICKS)
if len(written) != want:
    fails.append(('out-glbs', len(written), want))
for w in written:
    if not os.path.relpath(w, '.').startswith('scratch/'):
        fails.append(('escape', w))
print(json.dumps({'check': 'V-2-biome-driver', 'rc': rc, 'outGlbs': len(written),
                  'fail': int(bool(fails)), 'detail': fails[:4]}))
sys.exit(1 if fails else 0)
```

Commands for this V:

```bash
cd /tmp/wh-worldfeat
sha256sum $(find art-direction/3d/assets -name '*.glb' -type f | sort) > scratch/ns2-valspec-probe1/v2-sha-before.txt
python3 scratch/ns2-regen-driver.py ; A=$?
python3 scratch/ns2-biome-driver.py ; B=$?
sha256sum $(find art-direction/3d/assets -name '*.glb' -type f | sort) > scratch/ns2-valspec-probe1/v2-sha-after.txt
diff scratch/ns2-valspec-probe1/v2-sha-before.txt scratch/ns2-valspec-probe1/v2-sha-after.txt && echo 'sha sweep clean'
echo "rcs=$A/$B"
```

PASS: A=0, B=0, both JSON lines show `"fail":0` and `outGlbs` == 2 × picks,
and the sha sweep reports clean (no diff). FAIL: any nonzero rc / `fail:1`;
outputs outside scratch/; sha sweep mismatch (hard FAIL, stops everything).

## V-3 — Kernel-law equivalence: pipeline output NORMAL == fresh law computation

What: for every sandbox GLB produced in V-2 (raw + pixelated, body + prop),
re-parse the file bytes, extract POSITION + indices, re-derive normals via the
pristine `add_normals_v2.law_normals`, and assert they are BYTE-EQUAL to the
NORMAL payload written in the file (plus shape law: VEC3/5126, count == pos
count, target 34962, min/max inside [-1½-1e-3, 1+1e-3]). This is the spec's
"kernel-equivalence re-derivation" area.

Driver `scratch/ns2-kernel-eq.py` (full text):

```python
# scratch/ns2-kernel-eq.py — CC-NS2 valspec V-3: independent law re-derivation
# and byte-compare against every NORMAL payload written in the V-2 sandbox
# outputs. Uses only the PRISTINE kernel (never the pipeline's import).
import os, sys, json, glob, struct
import numpy as np
sys.path.insert(0, os.path.abspath('art-direction/3d'))
import add_normals_v2 as k        # pristine kernel (HEAD-identical, V-9)

def law_norms_from_file(path):
    """Return (normals, meta) re-derived by the kernel's own law routine,
    straight from the file's POSITION/indices."""
    data = open(path, 'rb').read()
    g, boff, _ = k.parse_glb(data)
    prim = g['meshes'][0]['primitives'][0]
    acc, bvs = g['accessors'], g['bufferViews']
    pa = acc[prim['attributes']['POSITION']]
    pbv = bvs[pa['bufferView']]
    poff = boff + pbv.get('byteOffset', 0) + pa.get('byteOffset', 0)
    verts = np.frombuffer(data, dtype='<f4', count=3*pa['count'],
                          offset=poff).reshape(pa['count'], 3).astype(np.float32)
    ia = acc[prim['indices']]
    ibv = bvs[ia['bufferView']]
    ioff = boff + ibv.get('byteOffset', 0) + ia.get('byteOffset', 0)
    dt = '<u4' if ia['componentType'] == 5125 else '<u2'
    faces = np.frombuffer(data, dtype=dt, count=ia['count'],
                          offset=ioff).astype(np.int64).reshape(-1, 3)
    return k.law_normals(verts, faces), data, g, prim, boff

fails = []
targets = sorted(glob.glob('scratch/ns2-sandbox/out/**/*.glb', recursive=True))
assert targets, 'no sandbox outputs found — run V-2 first'
for p in targets:
    (vnorm, nv, wc, pairs, guard), data, g, prim, boff = law_norms_from_file(p)
    na = g['accessors'][prim['attributes']['NORMAL']]
    nbv = g['bufferViews'][na['bufferView']]
    is_races = '/out/races/' in p.replace('\\', '/')
    # AMEND-VALSPEC-5 (IO, wake 45): (a) the bounds window was written
    # `win - tol <= v` — wrong sign for a [-1,1] payload (lower bound must be
    # NEGATIVE); (b) the shipped-payload slice lacked the binary-chunk offset
    # `boff`; (c) POST-CC-NS1 the biome half's NORMAL bufferView is written by
    # the lawful trimesh roundtrip, which never emits `target` (that key was a
    # kernel-appender trait) — target stays REQUIRED for races (raw append)
    # and OPTIONAL for biome (roundtrip), under AMEND-4's split discipline.
    ok_shape = (na['type'] == 'VEC3' and na['componentType'] == 5126
                and na['count'] == nv
                and (nbv.get('target') == 34962 if is_races else True)
                and 'min' in na and 'max' in na)
    if is_races:
        win = 1e-3   # kernel ±1e-3 min/max window (races = raw append)
    else:
        win = 1e-6   # AMEND-4: biome float32 re-pack tolerance
    mn, mx = na.get('min', [0]) , na.get('max', [0])
    ok_bounds = all(-1.0 - win <= v <= 1.0 + win
                    for v in list(mn) + list(mx))
    nbo = boff + nbv.get('byteOffset', 0)
    shipped = np.frombuffer(data, dtype='<f4', count=na['count']*3,
                            offset=nbo).reshape(-1, 3).astype(np.float32)
    if is_races:
        ok_bytes = shipped.tobytes() == vnorm.astype(np.float32).tobytes()
    else:
        ok_bytes = bool(np.abs(shipped - vnorm.astype(np.float32)).max() <= win)
    tag = os.path.relpath(p, 'scratch/ns2-sandbox/out')
    if not (ok_shape and ok_bounds and ok_bytes):
        fails.append((tag, ok_shape, ok_bounds, ok_bytes,
                      wc, pairs, guard))
    print(f'{tag:40} verts={nv} welded={wc} pairs={pairs} guard={guard} '
          f'shape={ok_shape} bounds={ok_bounds} bytes={ok_bytes}')
print(json.dumps({'check': 'V-3', 'n': len(targets), 'fail': int(bool(fails)),
                  'detail': fails[:6]}))
sys.exit(1 if fails else 0)
```

Command: `python3 scratch/ns2-kernel-eq.py` (from repo root).

PASS: exit 0, `n` == number of V-2 outputs (8 race + 12 biome = 20; the
authoring count said 24 — arithmetic slip, corrected by IO, wake 45), every
line shows `shape=True bounds=True bytes=True`. **AMEND-4 (IO ruling, wake
45):** `bytes=True` means byte-equality (zero tolerance) for every file
under `out/races/`, and float32-valued equality with tolerance
`np.abs(delta).max() <= 1e-6` for files under `out/biome/`. Reason:
post-CC-NS1 the raw biome SOURCE files already carry NORMAL, so the built
biome pipeline lawfully seeds trimesh's vertex_normals with the law payload
to survive its own export roundtrip; trimesh re-packs the floats and flips
the last bit on ~0.25% of rows (measured max delta 5.96e-08 on m1.glb;
geometry and normal direction exact, 8/8 zero-vector rows preserved). The
regen half stays byte-exact (the v3 export appends the law payload raw
after trimesh's export; proven byte-exact on rotspawn during authoring —
print the proof sha in the verdict). FAIL: any shape/bounds false; any
|races| byte divergence; any |biome| delta > 1e-6; min/max outside
[-1.0-1e-6, 1.0+1e-6] in the biome half (the CC-NS1 ±1e-3 min/max window
remains the regen-half convention).

## V-4 — Fresh-kernel regression cross-check (pipeline vs add_normals_v2.process_glb)

What: prove the pipeline's shipped NORMAL payload is byte-identical to what
`add_normals_v2.process_glb` itself produces on the same input. Sandbox each
raw SOURCE into a "second sandbox", run the kernel directly on a fresh copy,
and then also — because the pipeline may produce a different POSITION byte
layout than trimesh export — do the comparison through the SAME law
re-derivation path already used in V-3 (this isolates "same geometry → same
normals" independent of JSON layout). Spec §4 wording is satisfied when the
NORMAL accessors' re-derived law payload AND min/max float values are equal
between the two files.

Driver `scratch/ns2-regression.py` (full text):

```python
# scratch/ns2-regression.py — CC-NS2 valspec V-4: build one raw races body +
# one biome prop twice (pipeline output / fresh kernel process_glb run on same
# input bytes), then assert NORMAL accessor equality by law re-derivation.
import os, sys, json, shutil, struct, hashlib, tempfile
import numpy as np
sys.path.insert(0, os.path.abspath('art-direction/3d'))
import add_normals_v2 as k

PICKS = [('art-direction/3d/assets/races_regen/wolf.glb',      'sand-a'),
         ('art-direction/3d/assets/races_regen/rotspawn.glb',  'sand-b'),
         ('art-direction/3d/assets/biome_library/raw/wh-grass-tuft.glb', 'sand-c'),
         ('art-direction/3d/assets/biome_library/raw/b6-mushrooms.glb',  'sand-d')]

def pipeline_output_for(src, tag):
    """Run the BUILT pipeline in its sandbox on ONE file and return the raw
    (not pixelated) output path."""
    NS2 = 'scratch/ns2-sandbox'
    if 'races_regen' in src:
        rawd, outd = f'{NS2}/raw/races', f'{NS2}/out/races'
        sys.path.insert(0, os.path.abspath('art-direction/3d'))
        import regen_pipeline_v3 as rp
        rp.SRC, rp.OUT = rawd, outd
        name = os.path.basename(src)[:-4]
        rp.NAMES = [name]
        rp.main()
        return os.path.join(outd, name + '.glb')
    else:
        rawd, outd = f'{NS2}/raw/biome', f'{NS2}/out/biome'
        sys.path.insert(0, os.path.abspath('art-direction/3d'))
        import biome_pixelate as bp
        bp.SRC, bp.OUT = rawd, outd
        name = os.path.basename(src)[:-4]
        bp.IDS = [name]
        bp.main()
        return os.path.join(outd, name + '.glb')

def kernel_output_for(src, tag):
    """AMEND-5: direct kernel run is impossible post-CC-NS1 (sources carry
    NORMAL; process_glb refuses). Return the SOURCE copy itself — its
    law SIGNATURE is the reference the pipeline output is compared against."""
    d = os.path.join('scratch/ns2-sandbox', 'kernel-regress', tag)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'in.glb')
    shutil.copy(src, p)
    return p

def law_signature(path):
    data = open(path, 'rb').read()
    g, boff, _ = k.parse_glb(data)
    prim = g['meshes'][0]['primitives'][0]
    acc, bvs = g['accessors'], g['bufferViews']
    pa = acc[prim['attributes']['POSITION']]
    pbv = bvs[pa['bufferView']]
    poff = boff + pbv.get('byteOffset', 0) + pa.get('byteOffset', 0)
    verts = np.frombuffer(data, dtype='<f4', count=3*pa['count'],
                          offset=poff).reshape(pa['count'], 3).astype(np.float32)
    ia = acc[prim['indices']]
    ibv = bvs[ia['bufferView']]
    ioff = boff + ibv.get('byteOffset', 0) + ia.get('byteOffset', 0)
    dt = '<u4' if ia['componentType'] == 5125 else '<u2'
    faces = np.frombuffer(data, dtype=dt, count=ia['count'],
                          offset=ioff).astype(np.int64).reshape(-1, 3)
    na = acc[prim['attributes']['NORMAL']]
    nbv = bvs[na['bufferView']]
    noff = boff + nbv.get('byteOffset', 0) + na.get('byteOffset', 0)
    shipped = data[noff:noff + na['count']*12]
    vnorm, nv, wc, pairs, guard = k.law_normals(verts, faces)
    return {'sha': hashlib.sha256(shipped).hexdigest(),
            'lawSha': hashlib.sha256(vnorm.tobytes()).hexdigest(),
            'min': na['min'], 'max': na['max'], 'count': na['count'],
            'weld': (wc, pairs, guard), 'data': shipped,
            'law': vnorm.tobytes()}

fails = []
for src, tag in PICKS:
    # AMEND-VALSPEC-6 (IO, wake 45): each pick copies its own raw into the
    # sandbox (V-2's picks do not include wh-grass-tuft; never assume primed).
    if 'races_regen' in src:
        shutil.copy(src, 'scratch/ns2-sandbox/raw/races/')
    else:
        shutil.copy(src, 'scratch/ns2-sandbox/raw/biome/')
    po = pipeline_output_for(src, tag)
    ko = kernel_output_for(src, tag)
    a, b = law_signature(po), law_signature(ko)
    if 'races_regen' in src:
        # AMEND-5 (final): the pipeline's payload must BE the law payload of
        # its own geometry (raw append ⇒ bit-exact), and the source's
        # geometry must re-derive the SAME law payload (lawSha) with the
        # same weld tuple — nothing was lost or altered by the pipeline.
        same = a['sha'] == a['lawSha'] and a['count'] == b['count']
    else:
        # biome: trimesh roundtrip re-pack, <=1e-6 (AMEND-4)
        adat = np.frombuffer(a['data'], dtype='<f4').reshape(-1, 3)
        ldat = np.frombuffer(a['law'], dtype='<f4').reshape(-1, 3)
        same = a['count'] == b['count'] and bool(np.abs(adat - ldat).max() <= 1e-6)
    same_law = a['lawSha'] == b['lawSha']
    weld_ok = a['weld'] == b['weld']
    tag2 = os.path.basename(src)
    print(f'{tag2:24} payload==law: {same}  src-law==out-law: {same_law}  weld: {weld_ok}')
    if not (same and same_law and weld_ok):
        fails.append((tag2, 'payload-is-law', same, 'law-equal', same_law, 'weld', weld_ok))
print(json.dumps({'check': 'V-4', 'n': len(PICKS), 'fail': int(bool(fails)),
                  'detail': fails[:4]}))
sys.exit(1 if fails else 0)
```

Command: `python3 scratch/ns2-regression.py` (from repo root; reruns V-2's
sandbox single-file slices — acceptable re-runs because all outputs stay under
scratch/ and the sha sweep is enforced around each driver, see section "Sandbox
hygiene").

PASS (operative reading per **AMEND-5 final + AMEND-VALSPEC-6, IO wake 45**):
exit 0; every line shows `payload==law: True  src-law==out-law: True  weld:
True`. Post-CC-NS1 the DIRECT kernel reference run is impossible (sources
carry pre-round normals; `process_glb` refuses them), and the SOURCE's
shipped payload is not a usable reference (the pipeline's job is REPLACING
it). The operative equivalence: (1) the pipeline's shipped payload equals
the LAW payload re-derived from the output's own geometry (byte-exact for
races; ≤1e-6 for biome's trimesh roundtrip); (2) SOURCE geometry re-derives
the SAME lawSha and weld tuple as the output (nothing altered);
(3) min/max window checks live in V-3, dropped here. Each pick self-copies
into the sandbox raw dir (AMEND-VALSPEC-6). FAIL: any false line.

## V-5 — Pipeline-lag law (IDS derived from directory, not the stale m1..m9 list)

What: pin the spec §2.3 lag: pre-build, `biome_pixelate.IDS` is a hardcoded
9-item list while the raw dir holds 50 GLBs; post-CC-NS2, IDS derivation from
`os.listdir(SRC)` inside `main()` must process at least one raw GLB whose id
is NOT in the old list (e.g. `b6-bracken`, `m12-grave-moss`), and the old
literal must be GONE (module-level list replaced by the derived assignment,
inside main(), per spec §3.3b).

Commands (two-part, from repo root):

```bash
# Part 1 (static, any time pre- or post-build; post-build is the decisive one):
cd /tmp/wh-worldfeat
python3 - <<'EOF'
import sys, os
sys.path.insert(0, os.path.abspath('art-direction/3d'))
import biome_pixelate as bp
fails = []
# (i) the stale literal must be gone from the module SOURCE:
src = open(bp.__file__.rstrip('c'), 'rb').read().decode()
literal_present = ("IDS = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']" in src)
if literal_present:
    fails.append('stale IDS literal still present in module source')
# (ii) an os.listdir-derived IDS exists in source:
if 'os.listdir(SRC)' not in src:
    fails.append('IDS not derived via os.listdir(SRC)')
# (iii) at import time the module attribute is at least assignable:
bp.IDS = ['b6-bracken']
print(json.dumps({'check': 'V-5-static', 'fail': len(fails), 'detail': fails}))
sys.exit(1 if fails else 0)
EOF
echo "static rc=$?"
```

```python
# Part 2 (behavioral; needs the BUILT pipeline). Add to the END of
# scratch/ns2-biome-driver.py (V-2) — the sandbox PICKS already INCLUDE
# b6-bracken and m12-grave-moss, which are NOT in the old m1..m9 list.
# After the bp.main() call in that driver, this snippet must be appended
# (it is included in the shipped driver text above):
extra = [n for n in PICKS if n not in
         ('m1','m2','m3','m4','m5','m6','m7','m8','m9')]
have = {os.path.basename(w) for w in written}
lag_ok = all(n + '.glb' in have and n + '-pixelated.glb' in have for n in extra)
if not lag_ok:
    fails.append(('lag-law', extra))
print(json.dumps({'check': 'V-5-lag', 'extraIds': extra, 'fail': int(not lag_ok)}))
```

PASS: static rc=0 AND the V-2 biome driver's output JSON carries
`V-5-lag fail:0` with `extraIds` including at least `b6-bracken` and
`m12-grave-moss`. FAIL: stale literal still in source; listdir derivation
absent; any non-listed id missing from outputs.

## V-6 — Fallback RuntimeError law (no un-welded output ever written)

Two sub-checks. Both rely on the spec §3.2/§3.3 rule that when the kernel
cannot import, the pipeline must LOUDLY FAIL instead of writing un-welded
normals.

### V-6a — regen_pipeline_v3.export() raises RuntimeError when kernel unavailable

Command (from repo root; simulates the import failure WITHOUT touching any
repo file — the module under test is imported fresh with its `add_normals_v2`
path blocked):

```bash
cd /tmp/wh-worldfeat && python3 - <<'EOF'
import sys, os, json, struct, hashlib, types, importlib
# 1) build a fake "no-kernel" world: stub add_normals_v2 out of the path,
#    then import the pipeline module fresh.
sys.path.insert(0, os.path.abspath('art-direction/3d'))
sys.modules['add_normals_v2'] = None   # forces "import add_normals_v2" ImportError
import regen_pipeline_v3 as rp
importlib.reload(rp)                   # re-run the CC-NS2 shared import block
fails = []
if getattr(rp, '_NS2_WELD', True) is not False:
    fails.append('_NS2_WELD not False under stubbed kernel import')
# 2) exercise export() on a tiny in-memory geometry and demand RuntimeError
import numpy as np, io, trimesh
verts = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
faces = np.array([[0,1,2]], dtype=np.int64)
uv = np.zeros((3,2), dtype=np.float32)
from PIL import Image
img = Image.new('RGB', (4,4))
mat = trimesh.visual.material.PBRMaterial()
raised = None
try:
    rp.export('scratch/ns2-sandbox/out/v6a-out.glb', verts, faces, uv, mat, img)
except RuntimeError as e:
    raised = str(e)
except Exception as e:
    raised = ('WRONG-EXC', type(e).__name__, str(e))
if not (raised and str(raised).find('CC-NS2') >= 0 and str(raised).find('refuses') >= 0):
    fails.append(('regen-fallback', repr(raised)))
if os.path.exists('scratch/ns2-sandbox/out/v6a-out.glb'):
    fails.append(('regen-fallback-wrote-anyway', 'output file exists'))
print(json.dumps({'check': 'V-6a', 'fail': int(bool(fails)), 'detail': fails[:4]}))
sys.exit(1 if fails else 0)
EOF
```

PASS: exit 0; `_NS2_WELD` is False in the stubbed module; export() raised
RuntimeError whose text contains `CC-NS2` and `refuses`; NO output file was
written. FAIL: any other exception type, no exception, message missing the
law markers, or a file landing at the would-be path.

### V-6b — biome_pixelate._ns2_ensure_normal raises before any non-law write &
the old `os.chdir` is gone

Commands (two blocks from repo root):

```bash
# (i) static chdir check (the spec §3.3c law):
python3 - <<'EOF'
import sys, os
sys.path.insert(0, os.path.abspath('art-direction/3d'))
import biome_pixelate as bp
src = open(bp.__file__.rstrip('c'), 'rb').read().decode()
bad = ("os.chdir('/root/projects/witch-hunter')" in src)
print(json.dumps({'check': 'V-6b-chdir', 'fail': int(bad)}))
sys.exit(1 if bad else 0)
EOF
echo "chdir rc=$?"

# (ii) behavior: stub the kernel, import the BUILT biome module, call the
# helper on a THROWAWAY copy in scratch, expect RuntimeError and ZERO writes
# (pre-write mtime+sha capture).
python3 - <<'EOF'
import sys, os, json, shutil, hashlib, time
sys.path.insert(0, os.path.abspath('art-direction/3d'))
sys.modules['add_normals_v2'] = None
import biome_pixelate as bp      # post-CC-NS2 version with the shared blocks
import importlib; importlib.reload(bp)
fails = []
if getattr(bp, '_NS2_WELD', True) is not False:
    fails.append('_NS2_WELD not False under stubbed import')
os.makedirs('scratch/ns2-sandbox/out/v6b', exist_ok=True)
tgt = 'scratch/ns2-sandbox/out/v6b/copy.glb'
shutil.copy('art-direction/3d/assets/biome_library/raw/m11-moonbell.glb', tgt)
before = (os.path.getsize(tgt), hashlib.sha256(open(tgt,'rb').read()).hexdigest())
raised = None
try:
    bp._ns2_ensure_normal(tgt)
except RuntimeError as e:
    raised = str(e)
except Exception as e:
    raised = ('WRONG-EXC', type(e).__name__, str(e))
after = (os.path.getsize(tgt), hashlib.sha256(open(tgt,'rb').read()).hexdigest())
if not (raised and 'refusing' in str(raised)):
    fails.append(('ensure-normal-fallback', repr(raised)))
if before != after:
    fails.append(('wrote-despite-fallback',))
print(json.dumps({'check': 'V-6b-helper', 'fail': int(bool(fails)), 'detail': fails[:4]}))
sys.exit(1 if fails else 0)
EOF
echo "helper rc=$?"
```

PASS: both rc=0; the helper raises RuntimeError containing `refusing`; file
byte-identical before/after (size+sha equal); no os.chdir to a hardcoded path
in the module source. FAIL: any nonzero rc, wrong exception type, any byte
change in the throwaway copy, chdir line still present.

## V-7 — Stats law: both JSONL files exist post-run, ns2Weld true, sums consistent

What: after the V-2 sandbox runs, the two JSONL files the CC-NS2 spec mandates
must exist, be append-only rows, each row carrying `ns2Weld: true`, and the
summed per-file counts must reconcile with the number of sandbox GLBs
(biome: 2 outputs per id × ids; races: same) plus sensible geometry totals
(verts ≥ weldedVerts per row family; verts sum ≥ 12*4 minimum; no negative
counts; weldPairs ≥ 0).

Command (from repo root, needs V-2 run first):

```bash
cd /tmp/wh-worldfeat && python3 - <<'EOF'
import json, os, glob
fails = []
def audit(path, want_rows, name):
    if not os.path.exists(path):
        fails.append((name, 'missing', path)); return 0, 0
    rows = [json.loads(l) for l in open(path) if l.strip()]
    if len(rows) != want_rows:
        fails.append((name, 'row-count', len(rows), want_rows))
    nw = 0; verts = 0; welded = 0
    for r in rows:
        if r.get('ns2Weld') is not True:
            fails.append((name, 'ns2Weld not true', r.get('ns2Weld')))
        if 'ts' not in r or 'source' not in r:
            fails.append((name, 'missing ts/source'))
        for key in ('verts','weldedVerts','weldPairs','guardZero'):
            if key not in r or r[key] < 0:
                fails.append((name, 'bad-stat', key, r.get(key)))
        nw += r.get('weldPairs', 0); verts += r.get('verts', 0)
        welded += r.get('weldedVerts', 0)
    if welded > verts:
        fails.append((name, 'summed weldedVerts > summed verts'))
    return len(rows), verts

# biome: 2 rows per sandbox id (raw + pixelated), PICKS len 6 ⇒ 12 rows.
nb, vb = audit('scratch/ns2-sandbox/ns2-biome-stats.jsonl', 12, 'biome')
# races: 2 rows per sandbox name, PICKS len 4 ⇒ 8 rows.
nr, vr = audit('scratch/ns2-sandbox/ns2-regen-stats.jsonl', 8, 'regen')
print(json.dumps({'check': 'V-7', 'biomeRows': nb, 'regenRows': nr,
                  'biomeVertsSum': vb, 'regenVertsSum': vr,
                  'fail': int(bool(fails)), 'detail': fails[:5]}))
sys.exit(1 if fails else 0)
EOF
echo "stats rc=$?"
```

PASS: rc=0; row counts exactly 12 and 8 (these numbers are the sandbox PICKS
constants in the V-2 drivers — if a rerun changes PICKS, update the row-count
assertion to `2 × len(PICKS)` and re-pin in the verdict note); every row
`ns2Weld: true`; sums sane. FAIL: any missing file, wrong row count,
`ns2Weld` false, negative/garbage stat, summed weldeds exceeding verts.

## V-8 — Determinism: two identical pipeline runs produce byte-identical GLBs

Command (from repo root; needs V-2 run first to know the sandbox tree is
primed; this check re-runs ONE id's full export twice into different OUT
dirs and byte-compares):

```bash
cd /tmp/wh-worldfeat && python3 - <<'EOF'
import sys, os, json, shutil, hashlib
sys.path.insert(0, os.path.abspath('art-direction/3d'))
import biome_pixelate as bp

fails = []
base = 'scratch/ns2-sandbox'
# fresh sandbox for determinism (independent tree):
shutil.rmtree(base + '-det', ignore_errors=True)
os.makedirs(base + '-det/raw', exist_ok=True)
os.makedirs(base + '-det/outA', exist_ok=True)
os.makedirs(base + '-det/outB', exist_ok=True)
shutil.copy('art-direction/3d/assets/biome_library/raw/b3-spire.glb',
            base + '-det/raw/b3-spire.glb')

outs = []
for od in ('outA', 'outB'):
    bp.SRC = base + '-det/raw'
    bp.OUT = base + '-det/' + od
    bp.IDS = ['b3-spire']
    bp.main()          # twice, same inputs, different OUT dirs
    outs.append(os.path.join(bp.OUT, 'b3-spire.glb'))
    # NOTE: raw glb checked; pixelated is deterministic by construction but
    # the LAW wants one file proven; we pin the RAW (kernel path) — the
    # pixelated variant's same law applies via _ns2_ensure_normal.
h = [hashlib.sha256(open(p,'rb').read()).hexdigest() for p in outs]
same = h[0] == h[1]
print('determinism raw glb:', same, h[0][:16])
if not same:
    fails.append(('raw-determinism', h))
# and the pixelated twin, same law:
outsA = os.path.join(base + '-det/outA', 'b3-spire-pixelated.glb')
outsB = os.path.join(base + '-det/outB', 'b3-spire-pixelated.glb')
hA = hashlib.sha256(open(outsA,'rb').read()).hexdigest()
hB = hashlib.sha256(open(outsB,'rb').read()).hexdigest()
same_p = hA == hB
print('determinism pixelated glb:', same_p, hA[:16])
if not same_p:
    fails.append(('pix-determinism', hA, hB))
print(json.dumps({'check': 'V-8', 'fail': int(bool(fails)), 'detail': fails[:3]}))
shutil.rmtree(base + '-det', ignore_errors=True)
sys.exit(1 if fails else 0)
EOF
echo "det rc=$?"
```

PASS: rc=0; both raw and pixelated runs byte-identical across the two runs
(sha equality, zero tolerance). FAIL: any hash divergence; any sandbox escape
(sha sweep before/after the whole V-run, see hygiene — the determinism
driver itself must also leave assets untouched).

## V-9 — Post-build census: add_normals_v2 --verify still 0 processed; kernel sha unchanged

Command (from repo root):

```bash
cd /tmp/wh-worldfeat
python3 art-direction/3d/add_normals_v2.py --verify
# also confirm the kernel file is byte-identical to HEAD (the CC-NS1 artifact):
git show 0f07801256022328663f0f006377e8dfaf9a9ce5:art-direction/3d/add_normals_v2.py | sha256sum
sha256sum art-direction/3d/add_normals_v2.py
```

PASS: verify output exactly `root=… examined=325 processed=0 skipped=325
wouldProcess=0 errors=0` (all 325 assets already NORMAL-carrying; the CC-NS2
build must NOT have touched any asset); both kernel sha lines equal
`32b83a20a2d6eae525068a23cbb3b0747d432de110100181f9df3b2e66ee955a`. FAIL:
ANY processed/errored/skipped-mismatch; any kernel sha drift.

## V-10 — Repo-wide sha sweep + scratch-tree hygiene (verdict-stage)

What: end-to-end proof that validation (and the Devbot build) wrote outside
only the legal set: two pipeline scripts (M), this valspec + the IO spec under
`io/specs/` (untracked new), `scratch/**` (untracked new), and NOTHING under
`art-direction/3d/assets/`. Command:

```bash
cd /tmp/wh-worldfeat
sha256sum $(find art-direction/3d/assets -name '*.glb' -type f | sort) > scratch/ns2-valspec-probe1/v10-sha-after.txt
diff scratch/ns2-valspec-probe1/assets-sha-baseline.txt scratch/ns2-valspec-probe1/v10-sha-after.txt && echo 'assets sha IDENTICAL vs pre-round baseline'
sha256sum scratch/ns2-valspec-probe1/assets-sha-baseline.txt | cut -d' ' -f1   # must equal 0dfd1cf7…4d above
git status --porcelain
```

PASS: assets diff empty; baseline-list sha equal to the pinned
`0dfd1cf7…9438784d`; `git status --porcelain` shows ONLY: `M/M? lines` for
`art-direction/3d/regen_pipeline_v3.py` and `art-direction/3d/biome_pixelate.py`,
untracked `io/specs/cc-ns2-regen-weld-normals-spec.md`, untracked
`io/specs/cc-ns2-regen-weld-normals-valspec.md`, untracked
`scratch/cc-ns1-normal-batch-log.json` (pre-existing scratch), untracked
`scratch/ns2-valspec-probe1/` (authoring probes), untracked
`scratch/ns2-…-driver.py` files, untracked `scratch/ns2-sandbox/` tree, AND
NOTHING ELSE. FAIL: any changed/added file outside that set; any asset sha
drift; anything staged (git diff --cached --name-only must be empty).

## V-11 — Verdict-stage checklist (summary of what each PASS must record)

The verdict file (Testerbot writes it; NOT part of this spec) must assemble:

- V-1..V-10 one line each: PASS/FAIL + the printed JSON `detail` field.
- Post-build script shas for regen_pipeline_v3.py and biome_pixelate.py and
  the unchanged kernel sha (V-1/V-9 numbers).
- The pinned constants rechecked at verdict time and, if PICKS change, the
  updated row counts (V-7).
- The sandbox trees' cleanup state (all V-2/V-4/V-8 outputs stay under
  `scratch/`; the verdict stage re-asserts `scratch/ns2-sandbox` gets
  REMOVED only by the final validation cleanup script, as the spec says IO
  cleans it post-commit — validator must leave the tree intact for audit).

## Cleanup note (valspec-authoring probes; validator's own scratch too)

Authoring probes live in `scratch/ns2-valspec-probe1/` (probe1.py..probe4.py
+ the two pinned baseline files). They are pure-read plus BytesIO-only
in-memory work, plus the tiny throwaway bytes the probes wrote and already
deleted inside their own runs; the whole directory is safe to remove at
round end. The verdict stage's OWN scratch (ns2-sandbox/, drivers,
v2/v10 sha files /tmp copies) must be left for IO's post-commit cleanup
per spec §5. NOTHING outside `scratch/` and the two pipeline scripts
Devbot edits was written or modified by these probes (assets sha sweep
diff proved empty, `art-direction/3d/add_normals_v2.py` untouched).

---

## AMB — ambiguities / deviations IO may want to rule on

- AMB-1: The spec's `V-10` regression note says the FRESH `process_glb` run is
  on "an identical input copy in a second sandbox" — this valspec's V-4
  compares pipeline output against a DIRECT kernel run on a byte-identical
  INPUT (geometry/indices equality, not whole-file equality). Whole-file
  equality is impossible because the pipeline's JSON chunk differs from the
  kernel's; this interpretation preserves the law intent (normals equal for
  a given geometry) and should be recorded in the verdict as the operative
  reading. No remedy expected.
- AMB-2: The spec's `regen_pipeline_v3` sandbox PICKS list includes bodies
  `wolf` and `rotspawn` which are NOT in the NAMES list — that is
  intentional (module-attrs override NAMES, making the listing-lag law
  verifiable for races too, mirroring §2.5), and is allowed because the
  pipeline's contract is module-attribute-driven in the sandbox.
- AMB-3: For races bodies sourced fresh from `races_regen` raw files
  (post-CC-NS1 state: ALL assets were NORMAL-carriers per the CC-NS1 census
  325-file verify), the input to the pipeline has NORMAL present. The build's
  `regen_pipeline_v3.export()` in CC-NS2 spec §3.2 unconditionally computes
  and attaches NORMAL (it does not consult existing NORMAL). If that's the
  intended post-build behavior, V-3's file-shape check naturally covers it
  (count must equal POSITION count) — no change needed on the validation
  side; flagged only so the verdict documents the source-of-truth chain
  (trimesh strips NORMAL on re-export, per probes: exported attrs are
  `[POSITION, TEXCOORD_0]` pre-kernel).
