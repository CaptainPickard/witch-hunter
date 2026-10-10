#!/usr/bin/env python3
"""Probe the 8793 serving surface through the new current/ symlink path."""
import subprocess, json

out = {}
def curl(url, save=None):
    cmd = ['curl', '-s', '-o', save or '/dev/null', '-w', '%{http_code} %{time_total} %{size_download}',
           '-m', '15', url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout

code, t, size = curl('http://localhost:8793/current/prototype/js/CONFIG.js', '/tmp/cfgcheck.js').split()
out['config'] = {'code': code, 'time': t, 'bytes': size}
src = open('/tmp/cfgcheck.js', encoding='utf-8', errors='replace').read()
out['hint_line'] = next((l.strip() for l in src.splitlines() if 'Mushrooms favor' in l), 'NOT_FOUND')[:90]
out['daynight_marker'] = src.count('WH_DAYNIGHT')

for u in ['current/prototype/builds/v8-playable.html',
          'current/prototype/js/daynight.js',
          'current/art-direction/3d/assets/biome_library/m15-bandit-campfire-pixelated.glb',
          'current/art-direction/3d/assets/graveyard/gravestone-obelisk-pixelated.glb']:
    parts = curl('http://localhost:8793/' + u).split()
    out[u.split('/')[-1]] = {'code': parts[0], 'time': parts[1]}

with open('/tmp/wh_serve_probe.json', 'w') as f:
    json.dump(out, f, indent=1)
print('WROTE')