#!/usr/bin/env python3
"""Meshy image-to-3d driver for the Witch Hunter production run.

Usage:
  meshy_driver.py submit <ref_url> <tri_target>   -> prints task_id
  meshy_driver.py poll <task_id>                  -> prints status (+result urls when SUCCEEDED)
  meshy_driver.py wait <task_id>                  -> polls every 15s until SUCCEEDED/FAILED, prints urls
  meshy_driver.py dl <task_id> <outglb> <outpng>  -> downloads glb + thumbnail
"""
import sys, time, json, os, urllib.request

KEY = os.environ.get('MESHY_KEY', 'msy_6oKKj0yUMxMepbwqx0OHJH2p0pnUu23QE2dT')
BASE = 'https://api.meshy.ai/openapi/v1/image-to-3d'

def req(url, data=None, method=None):
    r = urllib.request.Request(url, method=method)
    r.add_header('Authorization', f'Bearer {KEY}')
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        r.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(r, body, timeout=60) as resp:
        return json.loads(resp.read().decode())

def submit(url, tri):
    body = {
        'ai_model': 'meshy-5',
        'image_url': url,
        'topology': 'quad',
        'target_polycount': int(tri),
        'symmetry_mode': 'auto',
        'should_remesh': True,
    }
    out = req(BASE, body)
    return out['result']

def status(task_id):
    return req(f'{BASE}/{task_id}')

def poll_wait(task_id, every=15, max_s=900):
    t0 = time.time()
    while time.time() - t0 < max_s:
        s = status(task_id)
        st = s.get('status')
        if st == 'SUCCEEDED':
            return s
        if st == 'FAILED':
            return s
        time.sleep(every)
    return status(task_id)

def download(url, path):
    with urllib.request.urlopen(url, timeout=120) as r, open(path, 'wb') as f:
        f.write(r.read())

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'submit':
        print(submit(sys.argv[2], sys.argv[3]))
    elif cmd == 'poll':
        print(json.dumps(status(sys.argv[2])))
    elif cmd == 'wait':
        print(json.dumps(poll_wait(sys.argv[2])))
    elif cmd == 'dl':
        s = status(sys.argv[2])
        if s.get('status') != 'SUCCEEDED':
            print('NOT_SUCCEEDED', s.get('status')); sys.exit(1)
        m = s['model_urls']
        download(m['glb'], sys.argv[3])
        if len(sys.argv) > 4 and m.get('thumbnail'):
            download(m['thumbnail'], sys.argv[4])
        print('downloaded', sys.argv[3])