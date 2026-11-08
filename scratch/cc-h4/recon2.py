import hashlib, os
root = '/tmp/wh-worldfeat'
js = os.path.join(root, 'prototype/js')

def win(fn, a, b):
    lines = open(os.path.join(js, fn), errors='replace').read().splitlines()
    a = max(1, a); b = min(b, len(lines))
    return '\n'.join(f'{i}|{lines[i-1]}' for i in range(a, b + 1))

print('== region-manager.js 1905-1912 ==\n' + win('region-manager.js', 1905, 1912))
print('\n== game.js 2653-2693 ==\n' + win('game.js', 2653, 2693))

cfg = open(os.path.join(js, 'CONFIG.js'), errors='replace').read().splitlines()
print('\n== CONFIG greps ==')
for pat in ["boss-slam", "regionJ: {", "type: 'ghoul'", "spire-root", "WH_ENEMY_TYPES", "lairs", "rotLair", "scarreader", "kill_rotmother", "kill_rotspawn"]:
    hits = [(i + 1, ln.strip()[:110]) for i, ln in enumerate(cfg) if pat in ln]
    print(f"-- '{pat}': {len(hits)}")
    for i, ln in hits[:14]:
        print(f'   {i}|{ln}')

print('\n== regionJ continuation 2127-2190 ==')
print(win('CONFIG.js', 2127, 2190))

print('\n== live sha vs baseline ==')
bl = os.path.join(root, 'scratch/cc-h4/baseline')
shas = {}
for ln in open(os.path.join(bl, 'source_sha256.txt')):
    h, p = ln.split()
    shas[p] = h
for p, h in shas.items():
    fp = os.path.join(root, p)
    live = hashlib.sha256(open(fp, 'rb').read()).hexdigest() if os.path.exists(fp) else 'MISSING'
    print(f'{p}: {"MATCH" if live == h else "MISMATCH live=" + live[:12] + " base=" + h[:12]}')
