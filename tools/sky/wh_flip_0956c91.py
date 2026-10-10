#!/usr/bin/env python3
"""Re-materialize the 0956c91 release checkout (sparse dirs absent) and re-verify."""
import os, json, subprocess

R = '/tmp/wh-playtest-share/releases/0956c91'
steps = []
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    steps.append((cmd[:60], r.returncode, (r.stdout + r.stderr)[-200:]))
    return r

# the clone fetched but checkout never materialized the sparse dirs
run(f'rm -f {R}/.git/index.lock')
run(f'git -C {R} sparse-checkout set prototype art-direction')
r = run(f'git -C {R} checkout --detach 0956c91')
run(f'git -C {R} sparse-checkout reapply')
out = {}
out['v2dir'] = os.path.isdir(R + '/art-direction/textures/sky2v2')
out['v2count'] = len(os.listdir(R + '/art-direction/textures/sky2v2')) if out['v2dir'] else 0
out['proto'] = os.path.isdir(R + '/prototype/builds')
os.system('ln -sfn releases/0956c91 /tmp/wh-playtest-share/current')
out['symlink'] = os.readlink('/tmp/wh-playtest-share/current')
def curl(url):
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code} %{size_download}', '-m', '10', url],
                       capture_output=True, text=True, timeout=15)
    return r.stdout
out['bundle_http'] = curl('http://localhost:8793/prototype/builds/v8-playable.html')
out['nightA_http'] = curl('http://localhost:8793/art-direction/textures/sky2v2/sky2v2-nightA.jpg')
out['steps'] = steps
json.dump(out, open('/tmp/wh_flip_out.json', 'w'), indent=1)
print('WROTE')
print(json.dumps(out, indent=1))