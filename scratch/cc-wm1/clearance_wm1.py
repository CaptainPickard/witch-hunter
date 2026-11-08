import math

veins = [(53, -577), (55.5, -573.5), (61, -572), (64, -575.5), (62.5, -581), (57, -584), (51.5, -581.5), (50, -574)]
squatters = [(56.5, -580.5), (61.5, -580), (59, -574.5)]
props = [
    ('mossBoulder', 54, -586), ('mossBoulder', 59, -587), ('mossBoulder', 64, -585),
    ('mossBoulder', 67, -581), ('mossBoulder', 67.5, -575), ('mossBoulder', 65, -570),
    ('mossBoulder', 60, -567), ('rubblePile', 56, -583), ('rubblePile', 60.5, -578.5),
    ('rubblePile', 53.5, -575), ('treeStump', 49.5, -578), ('treeStump', 66.5, -573),
    ('deadTree', 47, -581), ('deadTree', 68, -578),
]


def d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


nn = []
all_pairs = []
for i in range(len(veins)):
    for j in range(i + 1, len(veins)):
        dd = d(veins[i], veins[j])
        all_pairs.append(dd)
print('vein pairwise: min %.2f max %.2f' % (min(all_pairs), max(all_pairs)))
# nearest-neighbour per vein
nns = []
for i, v in enumerate(veins):
    others = [d(v, u) for j, u in enumerate(veins) if j != i]
    nns.append(min(others))
print('vein nearest-neighbor per vein: min %.2f max %.2f' % (min(nns), max(nns)))

print('\n--- vein5 variant check (63.5,-582) ---')
v5b = (63.5, -582)
veins_b = veins[:4] + [v5b] + veins[5:]
pairs_b = [d(veins_b[i], veins_b[j]) for i in range(8) for j in range(i + 1, 8)]
nns_b = []
for i, v in enumerate(veins_b):
    others = [d(v, u) for j, u in enumerate(veins_b) if j != i]
    nns_b.append(min(others))
print('pairwise min %.2f max %.2f ; nn min %.2f max %.2f' % (min(pairs_b), max(pairs_b), min(nns_b), max(nns_b)))
for s in squatters:
    print('squatter', s, '-> vein5b %.2f vs vein5old %.2f' % (d(s, v5b), d(s, (62.5, -581))))
for a, x, z in props:
    print('  prop', a, (x, z), '-> vein5b %.2f' % d((x, z), v5b))

print('\n--- squatter clearances (current table) ---')
for i, s in enumerate(squatters):
    dveins = min((d(s, v), v) for v in veins_b)
    dprops = min((d(s, (x, z)), a) for a, x, z in props)
    print('squatter%d %s: min-vein %.2f @%s  min-prop %.2f @%s' % (i + 1, s, dveins[0], dveins[1], dprops[0], dprops[1]))
print('squatter pairwise:', ['%.2f' % d(squatters[i], squatters[j]) for i in range(3) for j in range(i + 1, 3)])

print('\n--- vein vs prop/bonePile clearances (full tables) ---')
bones = [(-192.5, -461), (-184, -450), (-204, -453.5), (-198.5, -441), (208.5, -455), (199.5, -446), (220, -447.5), (214.5, -435)]
for v in veins_b:
    dp = min((d(v, (x, z)), a) for a, x, z in props)
    db = min(d(v, b) for b in bones)
    if dp[0] < 5 or db < 5:
        print('CLOSE: vein', v, 'prop %.2f @%s bone %.2f' % (dp[0], dp[1], db))
mindp = min((d(v, (x, z)), a, i) for i, v in enumerate(veins_b) for a, x, z in props)
print('tightest vein-prop: %.2f' % mindp[0], mindp[1], veins_b[mindp[2]])
minsb = min((d(s, (x, z)), i) for i, s in enumerate(squatters) for a, x, z in props)
print('tightest squatter-prop: %.2f' % minsb[0])
