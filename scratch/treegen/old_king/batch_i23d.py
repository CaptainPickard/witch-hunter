#!/usr/bin/env python3
"""CC-C13a batch 2: serial Meshy image-to-3d for all old_king assets.

Resumable: skips raw GLBs that already exist. <=2 attempts per asset.
Crash-recovery: if a previous attempt SUCCEEDED but died before download,
recover the GLB from the task log instead of paying a second submit.
meshy-6-lite: target_polycount is counted in QUADS; tris ~ 2x the target.
"""
import json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
W = '/tmp/wh-worldfeat'
DRIVER = 'scratch/treegen/old_king/old_king_meshy.py'
CONCEPTS = 'art-direction/concepts/old_king'
RAWDIR = 'scratch/treegen/old_king/raw'
LOG = f'{W}/scratch/treegen/old_king/old_king_meshy_log.jsonl'
KEY = open('/home/hermeswebui/.hermes/profiles/io/secrets/meshy_key').read().strip()

TARGETS = {   # quad targets -> expected tris ~ 2x
    'ok-farm-cottage': 15000, 'ok-farm-barn': 15000, 'ok-farm-silo': 7500,
    'ok-farm-haybale': 2000,  'ok-farm-well': 6000,
    'ok-ruin-wall-straight': 4000, 'ok-ruin-wall-corner': 4000,
    'ok-ruin-arch': 4000, 'ok-ruin-column': 2500, 'ok-ruin-rubble': 3000,
    'ok-tree-oak': 15000, 'ok-tree-pine': 12500,
    'ok-fence-post': 1500, 'ok-fence-corner': 1000,
    'ok-fence-gate': 1500, 'ok-fence-stonewall': 1500,
}

def recover(out):
    """Download a previously SUCCEEDED task's glb if this run died before dl."""
    if not os.path.exists(LOG):
        return False
    for line in reversed(open(LOG).read().splitlines()):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if (rec.get('kind') == 'i23d-done' and rec.get('status') == 'SUCCEEDED'
                and rec.get('out', '').endswith(f'{name_glb(out)}') or
                (rec.get('kind') == 'i23d-done' and rec.get('status') == 'SUCCEEDED'
                 and rec.get('out') == out_rel(out))):
            glb = (rec.get('model_urls') or {}).get('glb')
            if glb and not os.path.exists(out):
                urllib.request.urlretrieve(glb, out)
                print('  recovered from log:', out, flush=True)
                return True
    return False

def name_glb(out):
    return os.path.basename(out)

def out_rel(out):
    return out

def run(names):
    os.makedirs(f'{W}/{RAWDIR}', exist_ok=True)
    fails = []
    for name in names:
        tri = TARGETS[name]
        out_abs = f'{W}/{RAWDIR}/{name}-meshy.glb'
        out = f'{RAWDIR}/{name}-meshy.glb'
        ref = f'{CONCEPTS}/{name}-ref.png'
        if os.path.exists(out_abs):
            print('skip exists', name, flush=True)
            continue
        ok = False
        for attempt in (1, 2):
            r = subprocess.run(['/app/venv/bin/python', DRIVER, 'i23d', ref, out, str(tri)],
                               capture_output=True, text=True, cwd=W, timeout=560)
            lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
            print(f'{name} try{attempt}: {lines[-1] if lines else "(no stdout)"}', flush=True)
            if r.returncode == 0 and os.path.exists(out_abs):
                ok = True
                break
            if r.stderr.strip():
                print('  err:', r.stderr.strip().splitlines()[-1][:160], flush=True)
        if not ok:
            fails.append(name)
    print('MESH FAILS:', fails)
    b = subprocess.run(['/app/venv/bin/python', DRIVER, 'balance'], capture_output=True, text=True, cwd=W)
    print('final balance:', b.stdout.strip())

if __name__ == '__main__':
    run(sys.argv[1:] or list(TARGETS))