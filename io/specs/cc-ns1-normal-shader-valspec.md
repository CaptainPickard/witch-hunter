# CC-NS1 VALSPEC — Testerbot validation spec (normal-shader round, 80 GLBs)

Written by Testerbot valspec child (independent validator, pre-build dispatch
review round). 2026-11-08. Validates the Devbot build of round CC-NS1 against
IO spec of record `io/specs/cc-ns1-normal-shader-spec.md`.

Roles: **IO** owns specs/gates/commits (sole git gatekeeper, identity
CaptainPickard <pickard.nicko@gmail.com>). **Devbot** builds D1–D4 in the
worktree. **Testerbot** (reader of this file) validates the build
independently against this spec and writes the verdict. Testerbot does NOT
fix code; a FAIL verdict bounces the round to IO.

Baseline commit: **`9c0fd6c`** (full: `9c0fd6c6f34dfb314b4bf4211f424283c5f25794`,
"build: v8 stamp 4c667d9 (CC-PFG1 open-air phase-fog rows G/H)", 2026-11-08
06:55:39 +0000). All "pristine"/"baseline" reads in this spec mean
`git show 9c0fd6c:<path>` — never trust the worktree copy of an engine file
for comparison. GLB reads MAY use the worktree because the build itself is
what's being validated, except where noted (V-1, V-3, V-4, V-9, V-10
law-recompute pins read pristine via `git show`).

Census of record: `io/specs/cc-ns1-normal-census.json`, frozen 2026-11-08
07:33:10Z, **census file sha256 =
`fed269cd26e414345e310fb87ce6aca33d9692a1e51febc983ddcb0548607f6a`**,
80 files × (sha256, byteSize, primAttribs, posCount, posOffAbs,
posAccMinMaxPresent, idxCompType, texcoordAccIndex, imageBufferViews, mats,
hasNORMAL=false). The census stores each file's WHOLE-file sha256 (not the
texture-window sha); texture-window integrity is verified by replaying the
census imageBufferViews byte-offsets (V-3) and re-deriving them post-build.

Law script of record (the algorithm, reference-only): 
`art-direction/3d/add_normals.py` — sha256
`23c0ebb3610d5023c61dc69935c43ff00ee60dff1c71cfdc5f3de788b030d7d5`.
Law summary (what all normal checks enforce): weld at 1e-4 (cKDTree
query_pairs + union-find, canonical rep = first input index per cluster) →
per-vertex AREA-WEIGHTED normals (np.add.at of raw per-face crosses;
degenerate faces contribute zero vectors) → normalize (guard: |n|<1e-12
forces written normal = [0,0,0]/|1| → literal zero-vector) → un-weld to
original vertex order → float32 NORMAL accessor appended (VEC3, 5126,
min/max written), attribute order POSITION, NORMAL, TEXCOORD_0.

Deliverables under test: D1 `art-direction/3d/add_normals_v2.py` (new batch
tool), D2 the 80 census GLBs rewritten in place, D3
`io/specs/cc-ns1-postbuild-census.json`, D4 `scratch/cc-ns1-impl-notes.md`.
Every check below runs from repo root `/tmp/wh-worldfeat` (paths relative to
root; the tree lives in a git worktree of
github.com/CaptainPickard/witch-hunter, branch feat/world-visuals).

Content-anchor law: commands pin file content by anchor strings, never line
numbers — anchors are stable across unrelated edits above them.

---

## V-1 — Census replay at baseline (pristine crown proof)

What: re-derive the census itself from pristine `9c0fd6c` bytes and diff
against the frozen file. Proves the baseline is what was frozen (no
pre-build drift).

Commands:

```python3
# scratch/cc-ns1-v1-census-replay.py (stdlib only)
import json, struct, subprocess, hashlib, sys, os
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
def glb(path_bytes):
    d=path_bytes
    if d[:4]!=b'glTF': return None
    jl,_=struct.unpack_from('<II',d,12)
    g=json.loads(d[20:20+jl].decode())
    binoff=20+jl+8
    return g,binoff
def row(rel):
    data=subprocess.run(['git','show',BASE+':'+rel],capture_output=True).stdout
    r=glb(data)
    if r is None: return {'error':'not-glb'}
    g,binoff=r
    acc=g['accessors']; bvs=g['bufferViews']
    prim=g['meshes'][0]['primitives'][0]; attrs=prim['attributes']
    pos=acc[attrs['POSITION']]; posbv=bvs[pos['bufferView']]
    pos_off=binoff+posbv.get('byteOffset',0)+pos.get('byteOffset',0)
    idxc=prim.get('indices'); ia=acc[idxc] if idxc is not None else None
    imgs=[]
    for img in g.get('images',[]):
        bv=bvs[img['bufferView']]
        imgs.append([bv['byteOffset'],bv['byteLength']])
    return { 'sha256': hashlib.sha256(data).hexdigest(),
             'byteSize': len(data),
             'primAttribs': list(attrs.keys()),
             'hasNORMAL': 'NORMAL' in attrs,
             'posCount': pos['count'],
             'posOffAbs': pos_off,
             'posAccMinMaxPresent': ('min' in pos and 'max' in pos),
             'idxCompType': ia['componentType'] if ia else None,
             'texcoordAccIndex': attrs.get('TEXCOORD_0'),
             'imageBufferViews': imgs,
             'mats': len(g.get('materials',[])) }
bad=[]
rows={}
skip=0
tracked=set(subprocess.run(['git','ls-files','art-direction/3d/assets'],
    capture_output=True,text=True,cwd='.').stdout.split())
tracked=sorted(p for p in tracked if p.endswith('.glb'))
for p in tracked:
    r=row(p)
    if r and r.get('error'): continue
    if r and not r['hasNORMAL']:
        rel=os.path.relpath(p,'.')
        rows[rel]=r
# compare
assert len(rows)==cens['totalNoNormal']==80, (len(rows),cens['totalNoNormal'])
for rel,r in rows.items():
    c=cens['files'].get(rel)
    if c is None: bad.append((rel,'missing-in-census')); continue
    for key in r:
        if c.get(key)!=r[key]:
            bad.append((rel,key,c.get(key),r[key]))
for rel in cens['files']:
    if rel not in rows: bad.append((rel,'extra-in-census'))
print('V-1 replay bad rows:',len(bad))
for b in bad[:10]: print('  ',b)
print('V-1 census file sha256:',
      hashlib.sha256(open('io/specs/cc-ns1-normal-census.json','rb').read()).hexdigest())
sys.exit(1 if bad else 0)
```

Expected output: `V-1 replay bad rows: 0` and exit code 0, plus the census
sha256 which must equal the pinned value in the preamble.

FAIL: any nonzero `bad rows` count, or count of census files ≠ 80, or the
printed census sha256 ≠ pinned `fed269cd26e414345e310fb87ce6aca33d9692a1e51fe
bc983ddcb0548607f6a` (threshold: any diff at all = FAIL).

Note: this check is independent of the Devbot build (it re-derives from
pristine bytes) and must PASS in both the pre-build state AND the post-build
state (the GLBs in the worktree are irrelevant because reads go through
`git show 9c0fd6c:`).

## V-2 — Post-build census: all 80 carry NORMAL, law-shaped

What: rebuild the same census table against the WORKTREE GLBs (post-build)
and assert every file now passes law-shape checks (attribute inserted per
add_normals.py law).

Commands: same script as V-1 but reading the worktree file directly
(replace the `subprocess.run(['git','show',...])` with
`data=open(rel,'rb').read()`), then run:

```python3
# scratch/cc-ns1-v2-postbuild.py (stdlib + numpy ok, run from repo root)
import json, struct, hashlib, os, sys
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
FAILS=[]
for rel, c in sorted(cens['files'].items()):
    d=open(rel,'rb').read()
    if d[:4]!=b'glTF': FAILS.append((rel,'not-glb')); continue
    jl,_=struct.unpack_from('<II',d,12)
    g=json.loads(d[20:20+jl].decode())
    binoff=20+jl+8
    if len(g['meshes'])!=1 or len(g['meshes'][0]['primitives'])!=1:
        FAILS.append((rel,'mesh/prim count changed')); continue
    prim=g['meshes'][0]['primitives'][0]
    attrs=prim['attributes']
    if 'NORMAL' not in attrs:
        FAILS.append((rel,'NORMAL missing')); continue
    n=attrs['NORMAL']
    na=g['accessors'][n]
    if na['type']!='VEC3' or na['componentType']!=5126:
        FAILS.append((rel,'NORMAL not VEC3/5126',na['type'],na['componentType']))
    if na['count']!=c['posCount']:
        FAILS.append((rel,'NORMAL count mismatch',na['count'],c['posCount']))
    if 'min' not in na or 'max' not in na:
        FAILS.append((rel,'NORMAL min/max missing'))
    else:
        mn=na['min']; mx=na['max']
        for v in mn+mx:
            if v<-1.0-1e-3 or v>1.0+1e-3:
                FAILS.append((rel,'NORMAL bound window not ~[-1,1]',mn,mx)); break
    # order check: POSITION, NORMAL, TEXCOORD_0 (TANGENT/COLOR_0 after if present)
    keys=list(attrs.keys())
    if keys[:3]!=['POSITION','NORMAL','TEXCOORD_0'][:len(keys)]:
        # files with no TEXCOORD_0 (nomat) become [POSITION, NORMAL]
        nomat=(keys==['POSITION','NORMAL'])
        if not nomat: FAILS.append((rel,'attr order not POSITION,NORMAL,TEXCOORD_0',keys))
    # index compType unchanged
    ia=g['accessors'][prim['indices']]
    if ia['componentType']!=c['idxCompType']:
        FAILS.append((rel,'idxCompType changed',ia['componentType']))
    # posCount unchanged
    pos=g['accessors'][attrs['POSITION']]
    if pos['count']!=c['posCount']:
        FAILS.append((rel,'posCount changed')); continue
    if not ('min' in pos and 'max' in pos):
        FAILS.append((rel,'pos min/max dropped'))
print('V-2 postbuild FAILS:',len(FAILS))
for f in FAILS[:10]: print('  ',f)
sys.exit(1 if FAILS else 0)
```

Expected: `V-2 postbuild FAILS: 0`, exit 0. Additionally the count of files
with NORMAL in worktree = 80 (implied by no FAILS).

FAIL: any nonzero FAILS list, any count mismatch, any NORMAL not
VEC3/5126/min-max present, any attr-order deviation beyond the nomat
exception (`[POSITION, NORMAL]`), or NORMAL present on a file where the
census had it already (0 such files in census, but assert none: if the
census `totalNoNormal` grows from 0 the build is out of scope).

## V-3 — Texture-window integrity per file vs frozen census

What: re-derive each file's image bufferView byte-range from the POST-build
glb JSON (offsets will shift because the JSON chunk grows), extract those
bytes, sha256 them, and compare to the SHA256 OF THE SAME WINDOW re-derived
from PRISTINE bytes (`git show 9c0fd6c:<rel>`). Also assert window lengths
are identical. This proves texture bytes did not move in content even
though buffer layout shifted.

Commands:

```python3
# scratch/cc-ns1-v3-texture-window.py (stdlib only, run from repo root)
import json, struct, hashlib, subprocess, sys
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
def glb(path_bytes):
    jl,_=struct.unpack_from('<II',path_bytes,12)
    g=json.loads(path_bytes[20:20+jl].decode())
    binoff=20+jl+8
    return g,binoff
FAILS=[]
for rel,c in sorted(cens['files'].items()):
    d0=subprocess.run(['git','show',BASE+':'+rel],capture_output=True).stdout
    d1=open(rel,'rb').read()
    g0,b0=glb(d0)
    g1,b1=glb(d1)
    w0=[]; w1=[]
    for img in g0.get('images',[]):
        bv0=g0['bufferViews'][img['bufferView']]
        w0.append(d0[b0+bv0['byteOffset']:b0+bv0['byteOffset']+bv0['byteLength']])
    for img in g1.get('images',[]):
        bv1=g1['bufferViews'][img['bufferView']]
        w1.append(d1[b1+bv1['byteOffset']:b1+bv1['byteOffset']+bv1['byteLength']])
    if len(w0)!=len(w1): FAILS.append((rel,'image count changed')); continue
    for i,(a,b) in enumerate(zip(w0,w1)):
        if hashlib.sha256(a).hexdigest()!=hashlib.sha256(b).hexdigest():
            FAILS.append((rel,'image %d window hash differs'%i))
        if len(a)!=len(b):
            FAILS.append((rel,'image %d window length changed'%i,len(a),len(b)))
    # also assert the census's own window byte-lengths still match (count check)
    if len(w0)!=len(c['imageBufferViews']):
        FAILS.append((rel,'census imageBufferViews length mismatch'))
print('V-3 texture-window FAILS:',len(FAILS))
for f in FAILS[:10]: print('  ',f)
sys.exit(1 if FAILS else 0)
```

Expected: `V-3 texture-window FAILS: 0` (80/80 files × 1 image each for 75
files; the 5 nomat files have 0 image windows and trivially pass — they are
counted in the PASS set as long as nothing fails).

FAIL: any nonzero FAILS count; any image window length change; any window
hash mismatch.

## V-4 — Geometry integrity per file (positions, indices, topology)

What: per file, assert (a) POSITION accessor byte count, count, min/max are
identical to pristine (re-derived, not from census — the census does NOT
store min/max values, only a presence bool); (b) index accessor componentType
= 5125 unchanged; (c) face count identical (indices count); (d) whole-file
byteSize grew EXACTLY by the appended NORMAL accessor cost (normal accessor
payload = 12 × posCount bytes + a new bufferView entry) — this catches any
accidental geometry re-write.

Commands:

```python3
# scratch/cc-ns1-v4-geometry.py (stdlib + numpy, run from repo root)
import json, struct, hashlib, subprocess, sys
import numpy as np
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
def glb(b):
    jl,_=struct.unpack_from('<II',b,12)
    g=json.loads(b[20:20+jl].decode())
    binoff=20+jl+8
    return g,binoff
FAILS=[]
for rel,c in sorted(cens['files'].items()):
    d0=subprocess.run(['git','show',BASE+':'+rel],capture_output=True).stdout
    d1=open(rel,'rb').read()
    g0,b0=glb(d0); g1,b1=glb(d1)
    p0=g0['meshes'][0]['primitives'][0]; p1=g1['meshes'][0]['primitives'][0]
    if len(g0['meshes'][0]['primitives'])!=len(g1['meshes'][0]['primitives']):
        FAILS.append((rel,'prim count changed')); continue
    a0=g0['accessors'][p0['attributes']['POSITION']]
    a1=g1['accessors'][p1['attributes']['POSITION']]
    if a0['count']!=a1['count'] or a0['min']!=a1['min'] or a0['max']!=a1['max']:
        FAILS.append((rel,'POSITION count/min/max drifted'))
    if a0['componentType']!=a1['componentType']:
        FAILS.append((rel,'POSITION compType changed'))
    # index accessor
    ia0=g0['accessors'][p0['indices']]
    ia1=g1['accessors'][p1['indices']]
    if ia0['componentType']!=ia1['componentType'] or ia0['count']!=ia1['count']:
        FAILS.append((rel,'index compType/count changed'))
    # byteSize equality: only expected to differ by NORMAL payload + accessor/view json
    dv=len(d1)-len(d0)
    payload=12*c['posCount']
    # JSON grows too; assert dv >= payload (no shrink) and sane bounds
    if dv < payload or dv > payload + 4096:
        FAILS.append((rel,'byteSize delta suspicious',dv,payload))
print('V-4 geometry FAILS:',len(FAILS))
for f in FAILS[:10]: print('  ',f)
sys.exit(1 if FAILS else 0)
```

Notes: the `dv > payload` allowance is because the JSON chunk grows by the
appended accessor + bufferView text + padding (typically < 400 bytes/file).
The threshold `dv > payload + 4096` FAILs anything growing far more.

Expected: `V-4 geometry FAILS: 0`. All 80 files: index compType 5125, index
count unchanged, POSITION accessor min/max equal.

FAIL: any POSITION min/max differs; any index compType/count differs; any
`dv` outside `payload … payload+4096`.

## V-5 — Determinism: script re-run on a copy is byte-identical

Sample (pinned): one file per family (smallest each, sorted names) plus the
3 smallest overall:

```python3
# scratch/cc-ns1-v5-determinism.py (stdlib only, run from repo root)
# Sample = {smallest per family} ∪ {3 smallest overall}. Computed fresh
# (deterministic, never hand-listed) so the census can amend without editing
# this spec.
import json, subprocess, hashlib, os, shutil, sys, tempfile
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
files=cens['files']
fam={}
for k,v in files.items():
    fam.setdefault(k.split('/')[3],[]).append((v['byteSize'],k))
reps={}
for f,lst in fam.items():
    lst.sort()
    reps[f]=lst[0][1]
smallest3=[k for _,k in sorted((v['byteSize'],k) for k,v in files.items())[:3]]
sample=sorted(set(list(reps.values())+smallest3))
print('V-5 sample n =',len(sample))
for s in sample: print('  ',s)
FAILS=[]
tmp=tempfile.mkdtemp(prefix='ccns1-det-')
for rel in sample:
    # baseline copy (pristine)
    b=subprocess.run(['git','show',BASE+':'+rel],capture_output=True).stdout
    p0=os.path.join(tmp,'base.glb')
    open(p0,'wb').write(b)
    out0=os.path.join(tmp,'out0.glb')
    out1=os.path.join(tmp,'out1.glb')
    # TWO independent runs of the builder on the SAME pristine input
    for dst in (out0,out1):
        if os.path.exists(dst): os.remove(dst)
        shutil.copy(p0,dst)
        rc=subprocess.run([sys.executable,'art-direction/3d/add_normals_v2.py',dst],
            capture_output=True,text=True,
            env={**os.environ,'PYTHONHASHSEED':'0'}).returncode
        if rc!=0: FAILS.append((rel,'builder rc',rc))
    h0=hashlib.sha256(open(out0,'rb').read()).hexdigest()
    h1=hashlib.sha256(open(out1,'rb').read()).hexdigest()
    if h0!=h1:
        FAILS.append((rel,'two-run hashes differ'))
    # ALSO: byte-equality vs the worktree's actual post-build file
    h_wt=hashlib.sha256(open(rel,'rb').read()).hexdigest()
    if h0!=h_wt:
        FAILS.append((rel,'determinism run hash != worktree build hash',
                      h0,h_wt))
print('V-5 determinism FAILS:',len(FAILS))
for f in FAILS[:10]: print('  ',f)
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if FAILS else 0)
```

Expected: sample n = exactly 7. The union is:
- family reps (smallest per family): `art-direction/3d/assets/armor/tower-
  shield-pixelated.glb`, `.../church-kit/church-archway-pixelated.glb`,
  `.../graveyard/gravestone-obelisk-pixelated.glb`,
  `.../weapons/longsword-pixelated.glb`,
  `.../biome_library/wh-bush-snare.glb`,
  `.../old_king/ok-fence-corner-v2-pixelated.glb`
- 3 smallest overall: `.../biome_library/wh-bush-snare.glb`,
  `.../old_king/ok-fence-corner-v2-pixelated.glb`,
  `.../old_king/ok-fence-corner-v3-pixelated.glb`
(wh-bush-snare and ok-fence-corner-v2 appear in both lists; union = 7
files). PASS = all 7: two builder runs byte-identical to each other AND to
the shipped worktree build.

The expected PASS value is: for each sampled file, the two runs have
IDENTICAL sha256 AND the first run hash equals the hash of the shipped
worktree file (a mismatch = nondeterminism relative to what actually
shipped, or a file got processed differently in the batch).

FAIL: any sha mismatch between the two runs on the same input; any sha
mismatch between a run and the shipped build (threshold 0 tolerance);
any sample file missing from the worktree.

## V-6 — Idempotent `--verify`: 0 processed, 0 written

What: re-run the builder in verify mode over the post-build worktree. It
must detect NORMAL present everywhere and process/write NOTHING.

Commands:

```python3
# scratch/cc-ns1-v6-verify.py (stdlib only, run from repo root)
import subprocess, hashlib, json, sys, os, glob
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
paths=sorted(cens['files'])
pre={p: (os.path.getsize(p), hashlib.sha256(open(p,'rb').read()).hexdigest())
     for p in paths}
rc=subprocess.run([sys.executable,'art-direction/3d/add_normals_v2.py',
                   '--verify'],capture_output=True,text=True)
print('rc=',rc.returncode)
print('stdout tail:'); print(rc.stdout[-2000:])
if rc.stderr: print('stderr:'); print(rc.stderr[-2000:])
post={p: (os.path.getsize(p), hashlib.sha256(open(p,'rb').read()).hexdigest())
      for p in paths}
diffs=[p for p in paths if post[p]!=pre[p]]
print('files byte-changed by --verify:',len(diffs))
for d in diffs[:10]: print('  ',d)
sys.exit(1 if (diffs or rc.returncode!=0) else 0)
```

Expected: exit 0; report claims `processed = 0` (exact phrase may vary —
the number must equal 0); every file byte-identical before/after
(`files byte-changed = 0`).

FAIL: any file byte-change post-run (threshold 0); any report claiming
processed > 0; nonzero exit from --verify itself; the builder re-encoding
or appending anything (indicated by hash changes).

## V-7 — Scope floor: only the allowed tree was touched

What: `git status --porcelain` in the worktree shows no changes outside the
allowed set. The ALLOWED set is enumerated below (exact-match on path
prefixes); anything else fails.

Commands:

```python3
# scratch/cc-ns1-v7-scope.py (stdlib only, run from repo root)
import subprocess, sys, json, os
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
census_paths=set(cens['files'])
ALLOWED_MODIFIED=set(census_paths)                            # the 80 GLBs
ALLOWED_NEW={ 'art-direction/3d/add_normals_v2.py',
              'io/specs/cc-ns1-normal-shader-spec.md',        # IO spec
              'io/specs/cc-ns1-normal-census.json',           # census
              'io/specs/cc-ns1-normal-shader-valspec.md',     # this file
              'io/specs/cc-ns1-postbuild-census.json',        # D3
              'scratch/cc-ns1_census.py',                     # pre-existing untracked
}
ALLOWED_PREFIXES=('scratch/',)   # scratch is never committed but Devbot
                                 # touches it legitimately
st=subprocess.run(['git','status','--porcelain'],capture_output=True,text=True).stdout
FAILS=[]
for line in st.splitlines():
    if not line.strip(): continue
    xy,path=line[:2].strip(),line[3:].strip()
    # untracked dirs like '?? scratch/foo/' — expand
    if path.endswith('/'):
        # directory: everything under it must be prefix-allowed AND untracked
        if not path.startswith(ALLOWED_PREFIXES):
            FAILS.append(('unexpected dir',xy,path))
        continue
    if xy=='??':
        if path not in ALLOWED_NEW and not path.startswith(ALLOWED_PREFIXES):
            FAILS.append(('unexpected new file',path))
    elif xy=='M ' or xy==' M' or xy=='MM':
        if path not in ALLOWED_MODIFIED:
            FAILS.append(('unexpected modified file',xy,path))
    elif xy=='A ':
        if path not in ALLOWED_NEW:
            FAILS.append(('unexpected added file',path))
    else:
        FAILS.append(('unexpected status',xy,path))
print('V-7 scope FAILS:',len(FAILS))
for f in FAILS[:12]: print('  ',f)
# Also: all 80 GLBs are at least Modified
mods=set()
for line in st.splitlines():
    if line.strip():
        xy,path=line[:2].strip(),line[3:].strip()
        mods.add(path)
missing=[p for p in census_paths if p not in mods]
print('V-7 GLBs not marked modified:',len(missing))
for m in missing[:10]: print('  ',m)
# Scratch gate (repo law): NOTHING under scratch/ or io/ may be committed
staged=subprocess.run(['git','diff','--cached','--name-only'],
    capture_output=True,text=True).stdout.split()
print('STAGED FILES:',staged)
sys.exit(1 if (FAILS or missing or staged) else 0)
```

Expected: FAILS = 0; GLBs not marked modified = 0 (all 80 were rewritten);
STAGED FILES = [] (children NEVER commit; if anything is staged the round
fails outright regardless of which paths).

FAIL: any modified/added file outside the allowed set above (this includes
`prototype/js/**`, `prototype/index.html`, `prototype/style.css`,
`prototype/js/CONFIG.js`); any staged file at all; any of the 80 GLBs
left untouched.

Hard note: `prototype/builds/v8-playable.html` is NOT in the allowed set —
the bundle is rebuilt by IO after the verdict, and a Devbot-side bundle mod
FAILS this check. (Bundle check lives in V-11 and runs against the code
only.)

## V-8 — Engine-file zero-diff vs `9c0fd6c`

What: prove no engine/prototype file changed relative to baseline. Uses
`git diff --name-only` against the PINNED baseline sha (not HEAD), so
IO-added specs later don't pollute the check.

Commands:

```python3
# scratch/ccns1-v8-engine-diff.py (stdlib only, run from repo root)
import subprocess, sys, json
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
census_paths=set(cens['files'])
FORBIDDEN_PREFIX=('prototype/js/','prototype/index.html','prototype/style.css',
                  'prototype/vendor/','tools/','docs/planning/')
out=subprocess.run(['git','diff','--name-only',BASE],capture_output=True,text=True).stdout
changed=out.split()
FAILS=[p for p in changed if p.startswith(FORBIDDEN_PREFIX)]
print('V-8 engine-diff FAILS:',len(FAILS))
for f in FAILS[:12]: print('  ',f)
# and changed files should be ONLY census GLBs + D1 tool
allowed_extra={'art-direction/3d/add_normals_v2.py'}
allowed_extra|=census_paths   # GLBs allowed
bad=[p for p in changed if p not in allowed_extra]
print('V-8 non-GLB changed files:',len(bad))
for p in bad[:12]: print('  ',p)
# tracked-content identity re-check on engine files (belt+braces): compare
# hashes of HEAD's tracked engine files vs BASE (should be empty set)
eng=subprocess.run(['git','ls-files','prototype/js','prototype/index.html',
                    'prototype/style.css','prototype/vendor',
                    'prototype/builds/v8-playable.html','tools/'],
                   capture_output=True,text=True).stdout.split()
hash_fail=[]
for p in eng:
    d0=subprocess.run(['git','show',BASE+':'+p],capture_output=True).stdout
    d1=subprocess.run(['git','show','HEAD:'+p],capture_output=True).stdout
    import hashlib
    if hashlib.sha256(d0).hexdigest()!=hashlib.sha256(d1).hexdigest():
        hash_fail.append(p)
print('V-8 hash-diff engine files vs BASE:',len(hash_fail))
for p in hash_fail[:12]: print('  ',p)
sys.exit(1 if (FAILS or bad or hash_fail) else 0)
```

Expected: engine-diff FAILS = 0; non-GLB changed = 0; hash-diff engine files
vs BASE = 0.

FAIL: ANY diff line touching those paths (threshold 0 — every engine-
file diff is fatal per IO spec hard-constraint #1); any hash drift on those
files.

## V-9 — Loader-compat static check (no extension growth; generator preserved)

What: the runtime loader is `prototype/js/assets.js`'s `prepTemplate`
(content anchors, not lines: `function prepTemplate(group, isPixelated)`,
`obj.geometry.attributes.position && !obj.geometry.attributes.normal`,
`obj.geometry.computeVertexNormals()`). Post-build, every glb's glTF JSON
must still be parseable by a plain glTF 2.0 reader and must NOT have grown
extensions. Also: `asset.generator` must be preserved verbatim per file (the
trimesh files were generated by trimesh and the 2 meshy-scene files
(`biome_library/raw/wh-bush-snare.glb`,
`biome_library/refs/wh-bush-snare-meshy-raw.glb`) by meshy-scene — the
builder must not re-stamp the generator).

Commands:

```python3
# scratch/cc-ns1-v9-loader-compat.py (stdlib only, run from repo root)
import json, struct, subprocess, sys
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
def glb(b):
    jl,_=struct.unpack_from('<II',b,12)
    g=json.loads(b[20:20+jl].decode())
    binoff=20+jl+8
    return g,binoff
FAILS=[]
for rel,c in sorted(cens['files'].items()):
    d0=subprocess.run(['git','show',BASE+':'+rel],capture_output=True).stdout
    d1=open(rel,'rb').read()
    g0,b0=glb(d0); g1,b1=glb(d1)
    e0=g0.get('extensionsUsed',[])
    e1=g1.get('extensionsUsed',[])
    if e0!=e1:
        FAILS.append((rel,'extensionsUsed changed',e0,e1))
    r0=g0.get('extensionsRequired',[])
    r1=g1.get('extensionsRequired',[])
    if r0!=r1:
        FAILS.append((rel,'extensionsRequired changed',r0,r1))
    if g0['asset'].get('generator')!=g1['asset'].get('generator'):
        FAILS.append((rel,'asset.generator changed',
                      g0['asset'].get('generator'),g1['asset'].get('generator')))
    if g0['asset'].get('version')!='2.0' or g1['asset'].get('version')!='2.0':
        FAILS.append((rel,'asset.version not 2.0'))
    if len(g1.get('buffers',[]))!=len(g0.get('buffers',[])):
        FAILS.append((rel,'buffer count changed'))
    if 'uri' in g1['buffers'][0]:
        FAILS.append((rel,'spotted embedded buffer got a uri'))
print('V-9 FAILS:',len(FAILS))
for f in FAILS[:12]: print('  ',f)
sys.exit(1 if FAILS else 0)
```

Expected: FAILS = 0. Facts pinned now (measured pre-build, Testerbot):
extensionsUsed = `[]` (empty) on all 80; extensionsRequired = `[]`; single
binary buffer; generator = `https://github.com/mikedh/trimesh` on 78 files
and `meshy-scene` on 2 (`biome_library/raw/wh-bush-snare.glb`,
`biome_library/refs/wh-bush-snare-meshy-raw.glb`).

FAIL: ANY extension (used or required) appearing where the pristine had
none (threshold 0 — glTF-light loader here has no Draco/KHR support and any
growth breaks load); ANY generator string change; asset.version != 2.0.

## V-10 — Per-family normal histogram spot check (magnitudes ~1.0)

Sample: the 6 family representatives (smallest per family, byte-ordered
deterministic choice — same 6 as the V-5 sample). For these, run the LAW
(re-compute normals from pristine geometry exactly as `add_normals.py`
would) and compare to the file's written NORMAL, plus check magnitudes.

Commands:

```python3
# scratch/cc-ns1-v10-histogram.py (stdlib + numpy + scipy, run from repo root)
# NOTE: this is the ONE check that requires numpy/scipy. On the CC-NS1 box:
# python 3.12.3, numpy 2.5.1, scipy installed.
import json, struct, subprocess, sys
import numpy as np
from scipy.spatial import cKDTree
BASE='9c0fd6c'
cens=json.load(open('io/specs/cc-ns1-normal-census.json'))
files=cens['files']
fam={}
for k,v in files.items():
    fam.setdefault(k.split('/')[3],[]).append((v['byteSize'],k))
reps={}
for f,lst in fam.items():
    lst.sort()
    reps[f]=lst[0][1]   # smallest per family (matches V-5 sample)
def law_normals(path_bytes):
    data=path_bytes
    jl,_=struct.unpack_from('<II',data,12)
    g=json.loads(data[20:20+jl].decode())
    binoff=20+jl+8
    prim=g['meshes'][0]['primitives'][0]; acc=g['accessors']; bvs=g['bufferViews']
    posa=acc[prim['attributes']['POSITION']]; pbv=bvs[posa['bufferView']]
    poff=binoff+pbv.get('byteOffset',0)+posa.get('byteOffset',0)
    n=posa['count']
    verts=np.frombuffer(data,dtype='<f4',count=3*n,offset=poff).reshape(n,3).astype(np.float32)
    ia=acc[prim['indices']]
    ibv=bvs[ia['bufferView']]
    ioff=binoff+ibv.get('byteOffset',0)+ia.get('byteOffset',0)
    faces=np.frombuffer(data,dtype='<u4',count=ia['count'],offset=ioff).reshape(-1,3).astype(np.int64)
    t=cKDTree(verts)
    pairs=t.query_pairs(1e-4,output_type='ndarray')
    parent=list(range(n))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for a,b in pairs:
        ra,rb=find(a),find(b)
        if ra!=rb: parent[ra]=rb
    roots=np.array([find(i) for i in range(n)],dtype=np.int64)
    uniq,inv=np.unique(roots,return_inverse=True)
    canon={}
    for i,cc in enumerate(inv):
        if cc not in canon: canon[cc]=i
    rep=np.array([canon[cc] for cc in range(len(uniq))])
    wverts=verts[rep]
    wnorm=np.zeros((len(uniq),3),dtype=np.float64)
    fw=inv[faces]
    fv=wverts[fw]
    nn=np.cross(fv[:,1]-fv[:,0],fv[:,2]-fv[:,0])
    area2=np.linalg.norm(nn,axis=1); valid=area2>1e-12
    nn[valid]=nn[valid]/area2[valid,None]
    for kk in range(3):
        np.add.at(wnorm,fw[:,kk],nn)
    L=np.linalg.norm(wnorm,axis=1)
    guard=L<1e-12
    Lg=L.copy(); Lg[guard]=1.0
    return guard.sum(), len(uniq), (wnorm/Lg[:,None]).astype(np.float32), inv
FAILS=[]
for f,rel in sorted(reps.items()):
    d0=subprocess.run(['git','show',BASE+':'+rel],capture_output=True).stdout
    d1=open(rel,'rb').read()
    jl,_=struct.unpack_from('<II',d1,12)
    g=json.loads(d1[20:20+jl].decode())
    binoff=20+jl+8
    prim=g['meshes'][0]['primitives'][0]
    # read WRITTEN normal from the file
    na=g['accessors'][prim['attributes']['NORMAL']]
    nbv=g['bufferViews'][na['bufferView']]
    n_off=binoff+nbv.get('byteOffset',0)+na.get('byteOffset',0)
    written=np.frombuffer(d1,dtype='<f4',count=3*na['count'],
        offset=n_off).reshape(na['count'],3)
    # law-recompute
    gsum, wcount, wnorm_law, inv = law_normals(d0)
    exp=wnorm_law[inv].astype(np.float32)
    mag_w=np.linalg.norm(written,axis=1)
    # zero-length normals = guard rows (law writes literal [0,0,0] there)
    guard_now=(mag_w<1e-12).sum()
    nz=(mag_w>=1e-12)
    dev=np.abs(mag_w[nz]-1.0)
    # compare written vs law-expectation componentwise (exact fp32 law match)
    cmp=not (written==exp).all()   # must be bitwise equal for welded law
    print(f"family={f:<13} verts={na['count']:>7} lawGuard={gsum:>4} "
          f"writtenGuard={int(guard_now):>4} maxDevNonGuard={dev.max():.3e}"
          + (f"  LAW-MISMATCH cmp={cmp}" if cmp else ""))
    if int(guard_now)!=int(gsum): FAILS.append((f,'guard mismatch',gsum,int(guard_now)))
    if (dev>1e-6).any(): FAILS.append((f,'dev>1e-6',(dev>1e-6).sum(),float(dev.max())))
    if cmp: FAILS.append((f,'written normals != law-recompute'))
print('V-10 FAILS:',len(FAILS))
for x in FAILS: print('  ',x)
sys.exit(1 if FAILS else 0)
```

Expected on every sampled file (pinned numbers from Testerbot's pre-build
law sweep over pristine bytes, in `/tmp/ccns1_law_sweep.json`):

| family        | file (from `art-direction/3d/assets/`) | verts (posCount) | law guard-zeros | max `\|\|n\|-1\|` after law |
|---------------|----------------------------------------|-----------------:|----------------:|------------------------------|
| armor         | armor/tower-shield-pixelated.glb       |             1807 | 0 | < 6.0e-08 |
| biome_library | biome_library/wh-bush-snare.glb        |             1525 | 79 | < 6.0e-08 |
| church-kit    | church-kit/church-archway-pixelated.glb|             1942 | 0 | < 6.0e-08 |
| graveyard     | graveyard/gravestone-obelisk-pixelated.glb |         1439 | 0 | < 6.0e-08 |
| old_king      | old_king/ok-fence-corner-v2-pixelated.glb |           2398 | 1 | < 6.0e-08 |
| weapons       | weapons/longsword-pixelated.glb        |             1379 | 0 | < 6.0e-08 |

PASS definition (per family sample): (a) written NORMAL guard count ==
law-recomputed guard count; (b) all non-guard written normals satisfy
|‖n‖−1| ≤ 1e-6 (allowing float32 storage quantization; law's own float64
sweep maxes at 5.96e-08); (c) written bytes bitwise-equal the law recompute
(`written==exp` must be True). NO zero-length normals are allowed OUTSIDE
the law's guard branch — the 1e-12 guard on cancel-pair geometry
(coincident opposite-winding triangles, e.g. the 79 in wh-bush-snare, 127
in wh-bramble — measured pre-build, Testerbot sweep) legitimately writes
[0,0,0] and those ARE expected: the check's job is that the post-build file
matches the LAW, not that the mesh never zero-cancels.

FAIL (any of): written NORMAL contains a zero vector count != law guard
count; any non-guard magnitude deviates > 1e-6 from 1.0; written bytes ≠
law-recompute bytes (any of the 6 sample files).

## V-11 — Build health (no JS touched ⇒ no node --check; build_v8.py must run clean)

What: prove the bundle build is intact: (a) `tools/build_v8.py` exits 0 on
the post-round worktree; (b) the bundle's inlined `<script>` blocks
byte-match the `prototype/js/**` sources + vendor files (the 36-entry
`<script src>` list in index.html), and the `<style>` block byte-matches
`prototype/style.css` — proving no latent engine file change rode in via
the bundle; (c) `node --check` is not applicable (0 engine .js files
touched in this round per V-8; Devbot should have run it if any had —
assert the SET of touched js files is empty in the V-8 output).

Commands:

```python3
# scratch/cc-ns1-v11-buildhealth.py (stdlib + re, run from repo root)
import re, subprocess, sys, pathlib
ROOT=pathlib.Path('.')
# (a) run build_v8.py; it is deterministic (law) from HEAD commit stamp
rc=subprocess.run([sys.executable,'tools/build_v8.py'],capture_output=True,text=True)
print('build_v8 rc=',rc.returncode, rc.stdout.strip()[-120:])
if rc.returncode!=0: print('FAIL: build_v8 nonzero rc'); sys.exit(1)
# (b) bundle inline byte-match
html=(ROOT/'prototype/builds/v8-playable.html').read_text()
idx=(ROOT/'prototype/index.html').read_text()
srcs=re.findall(r'<script src="([^"]+)"></script>',idx)
FAILS=[]
pos=0
for src in srcs:
    content=(ROOT/'prototype'/src).read_text()
    marker='<script>\n'+content+'\n</script>'
    found=html.find(marker,pos)
    if found<0:
        FAILS.append(('inline-mismatch or out-of-order',src))
    else:
        pos=found+len(marker)
style=(ROOT/'prototype/style.css').read_text()
if not ('<style>\n'+style+'\n</style>') in html:
    FAILS.append(('style block mismatch',))
print('V-11 inline FAILS:',len(FAILS))
for f in FAILS[:8]: print('  ',f)
# (c) no js touched: git diff vs 9c0fd6c already proved it; re-assert here
out=subprocess.run(['git','diff','--name-only','9c0fd6c',
                    '--','prototype/js/','prototype/index.html',
                    'prototype/style.css','prototype/vendor/'],
                   capture_output=True,text=True).stdout.split()
print('V-11 js files touched vs 9c0fd6c:',len(out),out[:5])
# node --check on bundle-only inline scripts is not feasible (inline, no file);
# if V-8 is clean, skip node --check. Assert explicitly:
print('node --check skipped: no engine js touched (V-8 clean required)')
sys.exit(1 if (FAILS or out) else 0)
```

Expected: `build_v8 rc= 0`; the printed bundle path exists; inline script
FAILS = 0 (36 `<script src>` entries: 3 vendor + 33 js/*.js, all
byte-matched IN ORDER); style block inline = present; js touched vs
9c0fd6c = 0.

Bundle-commit-order note (law): the valspec validates the CODE tree; the
bundle is committed BY IO AFTER the verdict. If the worktree's
`prototype/builds/v8-playable.html` already differs from `9c0fd6c`'s bundle
only by the build-stamp title line (`<title>Witch Hunter v9 - EPR1 Combat
(build …)</title>`), that diff alone is EXPECTED (rebuild from a newer HEAD
stamps a different commit sha in the title) and does NOT fail V-11 — but
any OTHER byte difference does. Pre-build facts (measured): rebuilding at
9c0fd6c changes exactly the title line, `build 11-08 06:55Z 3192edd` →
`9c0fd6c`, and V-8's zero-diff applies to `prototype/js/**` etc. — the
bundle file itself is IO's, not Devbot's, and its ONLY permitted worktree
delta is that stamp line before IO's commit.

FAIL: nonzero build_v8 rc; any inline `<script>` byte-mismatch or ordering
break (36 entries expected); missing `<style>` inline match; any touched
js/index/style/vendor file (cross-check V-8); any bundle difference beyond
the title-stamp line.

Bundle sha facts (pinned pre-build, pristine tree): rebuilding at 9c0fd6c
from the 9c0fd6c tree writes title stamp `(...build 11-08 06:55Z 9c0fd6c)`
and the rest byte-stable (Testerbot-verified during valspec authoring).
Testerbot runs V-11 AFTER Devbot; the bundle title stamp must read
**9c0fd6c** exactly (build stamp is the HEAD commit's author time per the
2026-11-06 deterministic-build law, not wall clock): expect
`11-08 06:55Z 9c0fd6c` in the title line.

---

## IO amendment log

IO rulings 2026-11-08 (wake 44), after Devbot build + self-verification,
before Testerbot verdict run. Testerbot runs the spec AS AMENDED.

### AMEND-1 — census-pre.json into ALLOWED_NEW (V-7)
`io/specs/cc-ns1-normal-census-pre.json` is a dispatch-mandated pre-build
census COPY (byte-identical to the pinned census file, sha256
`fed269cd…07f6a` verified). ADD it to V-7's `ALLOWED_NEW` set. New PASS
language: FAILS = 0 with the allowed set being V-7's original list PLUS
`io/specs/cc-ns1-normal-census-pre.json` PLUS `io/specs/…
cc-ns1-normal-shader-spec.md`'s companions already listed.

### AMEND-2 — V-7 status parse fix
V-7's snippet line `xy,path=line[:2].strip(),line[3:].strip()` mis-parses
`git status --porcelain` XY codes ('M ' -> 'M'). REPLACED by the
intent-preserving parse: `xy = line[:2]` used verbatim (no strip) and
`path = line[3:]` (single leading space after the 2 code chars, paths never
start with a space in this tree). Comparison set for modified:
`xy in (' M','M ','MM')` -> must be in ALLOWED_MODIFIED; `xy=='??'` ->
untracked handling as written; `xy=='A '` -> allowed-new handling.

### AMEND-3 — V-10 double-inv defect: operative law is the SINGLE map
V-10's snippet reads `exp=wnorm_law[inv[inv]]` but its own prose (and the
law script `add_normals.py`: `vnorm = wnorm[inv]`) defines the law as the
SINGLE application `exp = wnorm_law[inv]`. The snippet's double
application is a transcription error. Operative law for V-10 = SINGLE map;
Devbot's bitwise single-map equality across all 6 family samples (max
‖n‖−1 = 5.96e-08, all bitwise PASS) is the accepted PASS form. The snippet
line is corrected to `exp=wnorm_law[inv].astype(np.float32)` in effect
(as already written in the shipped copy — the double-inv variant is dead
text): treat `exp=wnorm_law[inv]` as the check.

### AMEND-4 — V-10 guard-count population ruling
The V-10 guard table compares TWO DIFFERENT POPULATIONS: law guard rows
count welded CLUSTERS whose normal is zero (`guard.sum()` over clusters,
e.g. 79 on wh-bush-snare live = number of zero clusters... note: law guard
counts clusters, written zero rows count source-vertices mapped to zero
clusters; these differ by exactly the vertices welded INTO a zero cluster).
RULING: (a) guard equality check `int(guard_now)!=int(gsum)` is DEFECTIVE —
dropped. PASS = (b) magnitudes ≤1e-6 dev on non-guard rows + (c) bitwise
`written==exp` against the operative single-map law (AMEND-3). Zero-length
normals are legal ONLY where the law's own guard branch wrote them; the
bitwise check enforces exactly that. Pinned per-family clusters→written
zero-row expansions live in scratch/cc-ns1-v8v10v11.json.

### AMEND-5 — D3 postbuild census artifact defect + repair + tool note
Devbot's first D3 (`io/specs/cc-ns1-postbuild-census.json`) carried
`"files": {}` — the census script (scratch/cc-ns1_census.py) hardcodes OUT
to the pre-build path and the run pointed at the postbuild path captured a
zero-row pass (script collects only no-normal files). IO repaired D3
directly: new scratch variant `scratch/cc-ns1_postbuild_census.py`
(parameterized OUT; explicit processed/stillNoNormal/other counts) re-ran;
D3 now records processedHasNormal=80, stillNoNormal=0, otherGlbNoNormal=0,
files=80 rows. This is an IO-side tooling/artifact repair (scratch/ +
io/specs artifacts only, no GLBs, no engine files) — disclosed, in-gate.
NOTE for the verdict: V-1 and V-2 read the FROZEN pre-build census file at
`io/specs/cc-ns1-normal-census.json` (byte-stable, sha pinned fed269cd,
verified unchanged pre/post build); D3 is an artifact under audit, not a
check input.

---

## AMB: ambiguities in the IO spec (for IO ruling BEFORE Devbot dispatch)

AMB: none.
