#!/usr/bin/env python3
"""Applier for orders 3 + asset wiring (plan: /workspace/forest_plan2.txt).

Manifest: m16/m17/m18/m19 wired under their logical names (livingOak,
witchwoodTree, deadTree, youngAsh). Region A: order-2 forest replaced by
ring/alley/rim/dead plan, enemies +8, path lanterns trimmed to z>32 span,
dirtPath zTo=32, sink y for oak/ash. Region B: original species restored at
the cf82f1f positions with healthy assets."""
import re

WT = '/tmp/wh-worldfeat'

def section(name):
    txt = open('/workspace/forest_plan2.txt').read()
    m = re.search(r'# === %s (\d+) ===\n(.*?)(?=\n# ===|\Z)' % name, txt, re.S)
    n = int(m.group(1)); body = m.group(2).strip()
    lines = [l for l in body.split('\n') if l.strip()]
    assert len(lines) == n, (name, n, len(lines))
    return lines

ring = section('ring'); alley = section('alley'); rim = section('rim')
dead = section('dead'); enemies = section('enemies')
assert len(ring) == 46 and len(enemies) == 8

# sink map (local units from Astrabot report): oak 0.16, ash 0.10
SINK = {'livingOak': 0.16, 'youngAsh': 0.10}

def with_sink(line_txt):
    m = re.search(r"asset: '(\w+)'.*scale: ([\d.]+)", line_txt)
    asset, sc = m.group(1), float(m.group(2))
    if asset in SINK:
        return line_txt.rstrip(',').rstrip(' }') , sc  # unused
    return None, None

def add_y(line_txt):
    m = re.search(r"asset: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: ([\d.]+)", line_txt)
    asset, x, z, rot, sc = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4), float(m.group(5))
    y = SINK.get(asset, 0.0) * sc
    ytxt = ', y: %.2f' % y
    return "      { asset: '%s', x: %.2f, y: %.2f, z: %.2f, rotY: %s, scale: %.2f }," % (
        asset, x, y, z, rot, sc)

forest_block = ('      // order 3 forest (10-03): ring around graveyard (outside),\n'
                '      // path alley, rim fill, dead accents - mixed healthy species\n'
                + '\n'.join(add_y(l) for l in ring + alley + rim + dead) + '\n')

# ---- CONFIG.js ----
cfg_path = WT + '/prototype/js/CONFIG.js'
cfg = open(cfg_path).read()

# 1. remove every order-2 yew line in region A (asset yewTree in regionA span)
ra_start = cfg.index("regionA: {")
rb_start = cfg.index("regionB: {")
ra = cfg[ra_start:rb_start]
yew_re = re.compile(r"^      \{ asset: 'yewTree',[^\n]*\},\n", re.M)
ra_before = len(yew_re.findall(ra))
ra = yew_re.sub('', ra)
# canon pre-forest yew at (29.4, 1.3) predates order 2; restore it once
# (ring/rims cleared 5m around it, so the plan keeps it)
canon_yew = "      { asset: 'yewTree', x: 29.4, z: 1.3, rotY: 3.03, scale: 6.5 },\n"
i_anchor = ra.index("      { asset: 'lanternPost', x: -2, z: 30,")
ra = ra[:i_anchor] + canon_yew + ra[i_anchor:]
print('regionA yew lines removed:', ra_before - 1, '(+1 canon restored)')
assert ra_before == 103, ra_before

# 2. insert forest block after the LAST lanternPost line of region A (the (-2,30)/ (4,-2) area)
last_lant = [m for m in re.finditer(r"^      \{ asset: 'lanternPost',[^\n]*\},\n", ra, re.M)][-1]
ra = ra[:last_lant.end()] + forest_block + ra[last_lant.end():]

# 3. remove path lanterns past the new path end (z 20, 8, -5, -16.5 entries)
for zval in ('20.0', '8.0', '-5.0', '-16.5'):
    pat = re.compile(r"^      \{ asset: 'lanternPost', x: -?[\d.]+, z: %s,[^\n]*\},\n" % re.escape(zval), re.M)
    ra, n = pat.subn('', ra)
    assert n == 1, (zval, n)

# 4. enemies: append 8 forest enemies before the closing bracket of enemies array
enemy_block = '\n'.join('      ' + l.strip() for l in enemies if l.strip()) + '\n'
ra = ra.replace("      { type: 'ghoul', x: 2, z: -23.5 }\n",
                "      { type: 'ghoul', x: 2, z: -23.5 },\n" + enemy_block,
                1)

# 5. dirtPath zTo -> 32.0
cfg = cfg[:ra_start] + ra + cfg[rb_start:]
cfg = cfg.replace('zTo: -23.5,                     // just past the gate mouth, before plane',
                  'zTo: 32.0,                      // order 3: ends AT the graveyard fence mouth')
cfg = cfg.replace('zFrom: 86.0,                    // south rim start (inside playable 88.5)',
                  'zFrom: 86.0,                    // south rim start (inside playable 88.5); order 3: span ends at yard fence')

# 6. region B: restore species per original 10-03 slot table (asset at cf82f1f is yewTree)
orig_B = [
 ('livingOak', 6.2, -46.4), ('witchwoodTree', -31.2, -50.3), ('livingOak', 25.2, -73.8),
 ('livingOak', -31.1, -68.7), ('witchwoodTree', 19.0, -54.7), ('witchwoodTree', -10.9, -55.8),
 ('livingOak', -22.3, -59.2), ('deadTree', 35.5, -52.1), ('witchwoodTree', -18.1, -35.6),
 ('deadTree', -9.1, -35.8), ('deadTree', 28.8, -55.3), ('deadTree', 31.4, -48.7),
 ('witchwoodTree', -29.1, -72.5), ('deadTree', -20.5, -42.5), ('livingOak', -23.0, -39.2),
 ('livingOak', 23.5, -37.4), ('deadTree', 36.4, -37.1), ('witchwoodTree', -7.4, -41.5),
 ('deadTree', -31.1, -74.8), ('livingOak', -22.9, -71.1), ('witchwoodTree', 29.8, -76.9),
 ('witchwoodTree', -28.4, -79.9), ('deadTree', -16.0, -76.7)]
rb_end = cfg.index('boundary: {')
rb = cfg[rb_start:rb_end]
swapped = 0
for asset, x, z in orig_B:
    xtxt = ('%.1f' % x) if x != int(x) else ('%.1f' % x)
    pat = re.compile(r"\{ asset: 'yewTree', x: %s, z: %s, rotY: ([\d.]+), scale: ([\d.]+) \}," % (re.escape(xtxt), re.escape('%.1f' % z)))
    m = pat.search(rb)
    if not m:
        print('WARN no rb match', asset, x, z); continue
    sc = float(m.group(2))
    y = SINK.get(asset, 0.0) * sc
    yfrag = ', y: %.2f' % y if y else ''
    repl = "{ asset: '%s'%s, x: %s, z: %s, rotY: %s, scale: %s }," % (
        asset, yfrag, xtxt, '%.1f' % z, m.group(1), m.group(2))
    rb = rb[:m.start()] + repl + rb[m.end():]
    swapped += 1
print('regionB species restored:', swapped)
assert swapped >= 20, swapped
cfg = cfg[:rb_start] + rb + cfg[rb_end:]

open(cfg_path, 'w').write(cfg)

# ---- assets.js manifest ----
am_path = WT + '/prototype/js/assets.js'
am = open(am_path).read()
anchor = "    yewTree: 'art-direction/3d/assets/biome_library/m5-pixelated.glb',\n"
new_manifest = anchor + (
    "    livingOak: 'art-direction/3d/assets/biome_library/m16-living-oak-pixelated.glb',\n"
    "    witchwoodTree: 'art-direction/3d/assets/biome_library/m17-witchwood-pixelated.glb',\n"
    "    youngAsh: 'art-direction/3d/assets/biome_library/m19-birch-pixelated.glb',\n"
    "    // m18-dead-tree lives in biome_library (Astrabot 10-03)\n"
    "    deadTree: 'art-direction/3d/assets/biome_library/m18-dead-tree-pixelated.glb',\n")
assert anchor in am
am = am.replace(anchor, new_manifest)
open(am_path, 'w').write(am)
print('manifest wired')
print('DONE')