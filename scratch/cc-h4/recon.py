import os
root = '/tmp/wh-worldfeat'
bl = os.path.join(root, 'scratch/cc-h4/baseline')
print('BASELINE:', sorted(os.listdir(bl)) if os.path.isdir(bl) else 'MISSING')
print('HEAD:', open(os.path.join(bl, 'HEAD.txt')).read().strip() if os.path.isfile(os.path.join(bl, 'HEAD.txt')) else 'NA')
print('PRISTINE:', open(os.path.join(bl, 'git_status_pristine.txt')).read().strip()[:200] if os.path.isfile(os.path.join(bl, 'git_status_pristine.txt')) else 'NA')
shaf = os.path.join(bl, 'source_sha256.txt')
print('SHA head:')
print(open(shaf).read()[:600] if os.path.isfile(shaf) else 'NA')
print('SPECS:', sorted(os.listdir(os.path.join(root, 'io/specs'))) if os.path.isdir(os.path.join(root, 'io/specs')) else 'MISSING')

skip = {'node_modules', '.git', 'dist', 'build', 'vendor'}
targets = {'enemy.js', 'CONFIG.js', 'game.js', 'region-manager.js', 'assets.js'}
hits = {}
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in skip]
    for f in fn:
        if f in targets and f not in hits:
            hits[f] = os.path.join(dp, f)
print('FILES:', hits)

def win(path, a, b):
    if not path:
        return 'FILE NOT FOUND'
    lines = open(path, errors='replace').read().splitlines()
    a = max(1, a); b = min(b, len(lines))
    return '\n'.join(f'{i}|{lines[i-1]}' for i in range(a, b + 1))

e = hits.get('enemy.js'); c = hits.get('CONFIG.js'); a = hits.get('assets.js')
for label, args in [
    ('LAIR_STATE/lairFlag 1228-1236', (e, 1228, 1236)),
    ('lairOnDeath 1296-1306', (e, 1296, 1306)),
    ('capture/restoreLairs 1672-1694', (e, 1672, 1694)),
    ('buildSlamCue/slamCueShow 1596-1612', (e, 1596, 1612)),
    ('lairSockets 1696-1714', (e, 1696, 1714)),
    ('regionJ 2108-2126', (c, 2108, 2126)),
    ('rotmother/rotspawn 2860-2902', (c, 2860, 2902)),
    ('registries 2915-2926', (c, 2915, 2926)),
    ('deeds 4366-4374', (c, 4366, 4374)),
    ('xpSources 4396-4406', (c, 4396, 4406)),
    ('rotmotherBody 155-164', (a, 155, 164)),
    ('CHARACTERS 238-248', (a, 238, 248)),
]:
    print('\n== ' + label + ' ==')
    print(win(*args))
