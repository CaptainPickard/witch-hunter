#!/usr/bin/env python3
"""CC-C13a batch 1: serial t2i refs for old_king assets (max 2 tries each).

Usage: batch_t2i.py [name name ...]   (default: all names in ref_plan.json)
Foreground-safe: run in chunks of ~5-6 refs per call.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = '/tmp/wh-worldfeat'
plan = json.load(open(f'{HERE}/ref_plan.json'))['assets']

if __name__ == '__main__':
    names = sys.argv[1:] or list(plan)
    fails = []
    for name in names:
        prompt = plan[name]
        out = f'art-direction/concepts/old_king/{name}.png'
        if os.path.exists(f'{W}/{out}'):
            print('skip exists', name, flush=True)
            continue
        ok = False
        for attempt in (1, 2):
            r = subprocess.run(['/app/venv/bin/python', 'scratch/treegen/old_king/old_king_meshy.py',
                                't2i', out, prompt],
                               capture_output=True, text=True, cwd=W, timeout=2700)
            tail = (r.stdout.strip().splitlines() or [''])[-1]
            print(f'{name} try{attempt}: {tail}', flush=True)
            if r.returncode == 0 and os.path.exists(f'{W}/{out}'):
                ok = True
                break
            print('  stderr tail:', r.stderr.strip()[-200:], flush=True)
        if not ok:
            fails.append(name)
        b = subprocess.run(['/app/venv/bin/python', 'scratch/treegen/old_king/old_king_meshy.py',
                            'balance'], capture_output=True, text=True, cwd=W)
        print('  balance:', b.stdout.strip(), flush=True)
    print('FAILS:', fails)