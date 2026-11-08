import os
root = '/tmp/wh-worldfeat'
js = os.path.join(root, 'prototype/js')

def grep(fn, pats, ctx=0):
    lines = open(os.path.join(js, fn), errors='replace').read().splitlines()
    for pat in pats:
        for i, ln in enumerate(lines):
            if pat in ln:
                for k in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
                    print(f'{fn}:{k+1}|{lines[k]}')
                print('   ---')

print('== lairNest def =='); grep('enemy.js', ['lairNest = function', 'function lairNest'])
print('\n== nest.letter / nest =='); grep('enemy.js', ['.nest =', 'letter:'])
print('\n== WH_ENEMY_TYPES across js ==')
for fn in os.listdir(js):
    p = os.path.join(js, fn)
    if not os.path.isfile(p):
        continue
    t = open(p, errors='replace').read()
    if 'WH_ENEMY_TYPES' in t:
        for i, ln in enumerate(t.splitlines()):
            if 'WH_ENEMY_TYPES' in ln:
                print(f'{fn}:{i+1}|{ln.strip()[:130]}')
print('\n== regionD lairs row 1378-1392 ==')
lines = open(os.path.join(js, 'CONFIG.js'), errors='replace').read().splitlines()
for i in range(1377, 1392):
    print(f'{i+1}|{lines[i]}')
print('\n== regionD rotLair 1250-1290 ==')
for i in range(1249, 1290):
    print(f'{i+1}|{lines[i]}')
print('\n== enemy.js flagPrefix / prefix mentions =='); grep('enemy.js', ['flagPrefix', 'prefix'])
