# CC-NS2 Spec — Native welded-smooth normals in the regen pipelines

Round code: CC-NS2. Date: 2026-11-08 (Autopilot wake 45). Author: IO, under
Nicko's standing Autopilot order (PRIMARY.md, /root/projects/wh-hb/Git: gate law 4:
IO spec -> Testerbot validation spec -> Devbot build -> Testerbot independent
verdict -> IO commit + push, identity CaptainPickard <pickard.nicko@gmail.com>.
Children NEVER run git commit / push. All work lands in worktree
/tmp/wh-worldfeat, branch feat/world-visuals.

## 1. Why

Wake 44 (CC-NS1) welded smooth normals onto all 80 previously no-normal kit
GLBs (verdict PASS, 0 blocking; add_normals_v2.py committed). GOALS.md and
the wake-44 journal both say the same NEXT LANE: "P1-6 pipeline half
(regen_pipeline_v3 / biome_pixelate welded-path switch) DEFERRED to a later
round". That is this round: the two asset-generation pipelines must produce
CC-NS1-style WELDED smooth normals natively, so any future regen/rebake
cannot silently re-introduce the seam-crease artifact class CC-NS1 removed.

Art law anchor (viewed this wake): art-direction/concepts/
concept-08-veil-spire.png — light soaks into crevices; crevices read as
depth, not as shading bands. art-direction/concepts/day-10-hunter.png —
smooth cloth-like shading surfaces under a high-contrast key. UV-seam crease
shading is exactly what these frames forbid.

## 2. Ground truth (verified wake 45)

1. Weld-law kernel: art-direction/3d/add_normals_v2.py (committed CC-NS1,
   do NOT modify it):
   - weld_vertices(verts, tol=1e-4): cKDTree query_pairs + union-find,
     canonical rep = first input index per cluster.
   - law_normals(verts, faces): area-weighted accumulation in welded space
     (np.add.at of raw per-face crosses, degenerate faces contribute zero
     vectors), |n| < 1e-12 guards keep literal [0,0,0] rows, then un-weld
     back to original vertex order; returns (vnorm_float32, n_verts,
     weldedVerts, weldPairs, guardZero).
   - process_glb(path): full in-place law append — ONE accessor (VEC3, 5126,
     count == POSITION count, min/max written) + ONE bufferView (target
     34962), attribute order POSITION, NORMAL, TEXCOORD_0 (+ extra attrs
     preserved after), chunk layout JSON-padded-spaces / BIN-padded-zeros,
    buffers[0].byteLength updated, re-parse self-checks, single-mesh
     single-prim only, raises if NORMAL already present.
2. art-direction/3d/regen_pipeline_v3.py (races bodies): exports raw +
   pixelated body GLBs; its export() computes normals from per-face crosses
   accumulated per ORIGINAL (un-welded) vertex => seam creases under strong
   key light. No welded variant exists.
3. art-direction/3d/biome_pixelate.py (biome props): exports raw copy +
   pixelated; injects normals when missing via trimesh
   Trimesh(process=False).vertex_normals => un-welded, same artifact class.
   IDS is a hardcoded m1..m9 list but the raw dir holds 50 GLBs — the script
   lags the assets.
4. Census state right now: `python3 art-direction/3d/add_normals_v2.py
   --verify` from repo root => examined=325 processed=0 skipped=325
   wouldProcess=0 errors=0 (everything already carries NORMAL). This round
   ships pipeline code only; no asset regeneration in this round.
5. races_regen/ holds 13 GLBs; the NAMOS list in regen_pipeline_v3.py names
   10. Kernel import must not depend on list or dir contents.

## 3. Build law (Devbot)

Single deliverable: edits to the two pipeline scripts in place. add_normals_v2.py
must NOT be touched. No asset files change in this round (see section 5).

### 3.1 Shared blocks (identical in both files)

(a) Import block after the existing imports:

```python
import time

try:
    import add_normals_v2
    from add_normals_v2 import law_normals, has_normal, parse_glb
    _NS2_WELD = True
    print('CC-NS2: weld-law kernel ENABLED (add_normals_v2.law_normals)')
except ImportError as _ns2_err:
    _NS2_WELD = False
    print('CC-NS2: weld-law kernel IMPORT FAILED (%r); runs will abort' % (_ns2_err, ))
```

(b) Stats + JSONL log block:

```python
_NS2_STATS = {}


def _ns2_stats_add(d):
    for k, v in d.items():
        _NS2_STATS[k] = _NS2_STATS.get(k, 0) + v


def _ns2_log(stats_path, source):
    row = dict(_NS2_STATS)
    row["ts"] = float(time.time())
    row["source"] = source
    row["ns2Weld"] = bool(_NS2_WELD)
    with open(stats_path, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print("NS2 pipeline stats (appended %s):" % stats_path)
    print(json.dumps(row, sort_keys=True))
```

### 3.2 art-direction/3d/regen_pipeline_v3.py — deterministic diffs

In export(), REPLACE the whole "smooth normals" computation block (from the
comment `# smooth normals (lighting requirement; no visual change on unlit
texels)` down to `nv = vnorm.astype(np.float32)`) with:

```python
    # CC-NS2: normals MUST come from the weld-law kernel (add_normals_v2).
    # The former un-welded in-place add.at block was the seam-crease artifact
    # class CC-NS1 eliminated. No fallback: fail the run loudly.
    if _NS2_WELD:
        nv, ncount, _wc, _wp, _gz = law_normals(
            verts32, np.asarray(faces, dtype=np.int64))
        assert ncount == len(verts32), 'CC-NS2 vertex count drift'
    else:
        raise RuntimeError(
            'CC-NS2: weld-law kernel (add_normals_v2) unavailable; '
            'regen_pipeline_v3 refuses to ship un-welded normals')
```

with `verts32 = verts.astype(np.float32)` computed just above the call
(one line, keeps the exact float32 dtype path the kernel used for CC-NS1).
Feed stats inside the `if _NS2_WELD:` branch AFTER unpacking the 5-tuple:

```python
        _ns2_stats_add({"verts": ncount, "faces": len(faces),
                        "weldedVerts": _wc, "weldPairs": _wp,
                        "guardZero": _gz})
```

In the append section, amend the bufferView/accessor shape to the law shape
(min/max + target):

```python
    bvs.append({'buffer': 0, 'byteOffset': start, 'byteLength': nv.nbytes,
                'target': 34962})
    accessors.append({'bufferView': len(bvs) - 1, 'componentType': 5126,
                      'count': len(nv), 'type': 'VEC3',
                      'min': [float(x) for x in nv.min(axis=0)],
                      'max': [float(x) for x in nv.max(axis=0)]})
    n_acc = len(accessors) - 1
```

In `__main__`, after the loop, before/with the V3 COMPLETE print:

```python
        _ns2_log('scratch/regen_pipeline_v3-ns2-stats.jsonl', 'regen_pipeline_v3')
    print('V3 COMPLETE')
```

(_ns2_log outside the loop.)

### 3.3 art-direction/3d/biome_pixelate.py — diffs

(a) Same shared blocks (3.1).
(b) IDS becomes raw-dir-derived inside main() (replaces the module-level
literal):

```python
IDS = sorted(fn[:-4] for fn in os.listdir(SRC) if fn.endswith('.glb'))
```

(c) The os.chdir('/root/projects/witch-hunter') line in main() is REMOVED;
scripts run from the repo root of their tree (docstring documents this).
(d) New helper (module scope), delegating the append to the kernel so the
written bytes follow the exact CC-NS1 accessor shape:

```python
def _ns2_ensure_normal(path):
    """CC-NS2: ship welded smooth normals or fail loudly. In-place."""
    g, _binoff, _blen = parse_glb(open(path, 'rb').read())
    if has_normal(g):
        return
    if not _NS2_WELD:
        raise RuntimeError(
            'CC-NS2: weld-law kernel unavailable; refusing un-welded '
            'NORMAL for %s' % path)
    row = add_normals_v2.process_glb(path)
    _ns2_stats_add({"verts": row["verts"], "faces": row["faces"],
                    "weldedVerts": row["weldedVerts"],
                    "weldPairs": row["weldPairs"],
                    "guardZero": row["guardZero"]})
    print('CC-NS2 welded NORMAL injected: %s (weldPairs %d)' % (path, row["weldPairs"]))
```

(e) export(path, mesh, tex): DELETE the entire old injection body (from
`# inject NORMAL attribute if missing (required for lighting)` through
`print('  injected normals')`) and replace with:

```python
    _ns2_ensure_normal(path)
```

(f) main(): after each raw copy export (raw_out), call `_ns2_ensure_normal(raw_out)`
AND after each pixelated export call `_ns2_ensure_normal(pix_out)`. The old
export() no longer injects normals itself; the callers own that step via the
kernel path.

(g) In `__main__`, after the loop:
`_ns2_log('scratch/biome_pixelate-ns2-stats.jsonl', 'biome_pixelate')`.

### 3.4 Non-goals / hard boundaries

- add_normals_v2.py: byte-untouched (census-verified; CC-NS1 artifact).
- No asset file under art-direction/3d/assets/ changes in this round.
- No browser, no HTML, no build stamp: playable v8 bytes stay untouched
  (0f07801 stamp); serving stays on the current release. This is a
  tool-lane round — no playtest claims.
- No git from children. No new crons. No spending.

## 4. Validation law (Testerbot valspec contract)

- Sandbox: scratch/ns2-sandbox/ — copies of representative raw assets only
  (>= 4 biome raw GLBs across families incl. b3-, b6-, m-; >= 2 races_regen
  bodies). All pipeline outputs must land under scratch/; SRC/OUT/NAMES/IDS
  are overridable module attributes. Repo sha sweep over
  art-direction/3d/assets must be IDENTICAL before/after validation.
- Kernel-equivalence: for each sandbox output GLB (raw + pixelated, body +
  prop), re-parse from file bytes: NORMAL accessor VEC3/5126 with min/max in
  [-1,1], count == POSITION count, bufferView target 34962; re-derive law
  normals from the file's float32 POSITION + indices via law_normals ->
  byte-equal to shipped accessor payload.
- Regression: at least one sandbox output cross-checked against a FRESH
  add_normals_v2.process_glb() run on an identical input copy in a second
  sandbox => NORMAL accessor payload byte-equal.
- Pipeline-lag law: IDS-derived listing actually processes a raw GLB whose
  id is NOT in the old m1..m9 list (e.g. b6-bracken).
- Fallback law: with the kernel import forced to fail (monkeypatch sys.path
  or stubbing), regen_pipeline_v3 export() raises RuntimeError (no
  un-welded output written), and biome_pixelate _ns2_ensure_normal raises
  before any non-law write.
- Stats: both JSONL files exist after a run with ns2Weld true and summed
  stats consistent with the number of injections.
- Determinism: one sandbox GLB processed twice (two runs, same input) =>
  byte-identical output GLB.
- Exit criteria: no blocking FAILs; any FAIL -> remedy round.

## 5. IO close-out

After PASS: IO commits (feat: cc-ns2 native weld-law normals in regen
pipelines) + pushes feat/world-visuals; GOALS.md task row updated; journal
entry (session-type Autopilot); scratch cleaned of sandbox copies.
