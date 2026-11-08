#!/usr/bin/env python3
"""CC-C13a: Old King's Forest farm/ruin/tree/fence assets. SERIAL ONLY Meshy driver.

Adapted from scratch/tree_meshy.py (2026-10-03 proven round). Serial: every
command blocks until the provider returned; i23d submits are issued by the
batch runner one at a time. Credit floor: refuse any submit that would take
balance below the mission floor (300).

Commands:
  balance                          -> print balance
  t2i  <out.png> <prompt...>       -> text-to-image ref: submit+wait+dl (prints meshy CDN url)
  i23d <ref_url_or_file> <out.glb> [tri] -> image-to-3d meshy-5: submit+wait+dl
Log: scratch/treegen/old_king/old_king_meshy_log.jsonl.
"""
import sys, time, json, os, base64, urllib.request

KEY = os.environ.get('MESHY_KEY')
if not KEY:
    raise SystemExit("MESHY_KEY not set")
API = 'https://api.meshy.ai/openapi'
FLOOR = 300
MAX_TARGET = 30000
LOG = 'scratch/treegen/old_king/old_king_meshy_log.jsonl'


def req(url, data=None, method=None):
    r = urllib.request.Request(url, method=method)
    r.add_header('Authorization', f'Bearer {KEY}')
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        r.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(r, body, timeout=60) as resp:
        return json.loads(resp.read().decode())


def balance():
    return req(f'{API}/v1/balance')['balance']


def guard(cost_estimate):
    b = balance()
    if b - cost_estimate < FLOOR:
        raise SystemExit(f'CAP GUARD: balance {b}, est {cost_estimate}, floor {FLOOR}')
    return b


def log(rec):
    rec['t'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    with open(LOG, 'a') as f:
        f.write(json.dumps(rec) + '\n')


def wait(url, every=10, max_s=2400):
    for _ in range(max_s // every):
        time.sleep(every)
        d = req(url)
        if d['status'] in ('SUCCEEDED', 'FAILED'):
            return d
        print('  ', d['status'], flush=True)
    raise SystemExit('TIMEOUT waiting ' + url)


def dl(url, path):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r, open(path, 'wb') as f:
        f.write(r.read())
    return path


def t2i(out, prompt):
    b0 = guard(5)
    body = {'ai_model': 'nano-banana', 'prompt': prompt}
    outj = req(f'{API}/v1/text-to-image', body)
    tid = outj['result']
    log({'kind': 't2i', 'task_id': tid, 'out': out, 'bal_before': b0})
    d = wait(f'{API}/v1/text-to-image/{tid}')
    log({'kind': 't2i-done', 'task_id': tid, 'status': d['status']})
    if d['status'] != 'SUCCEEDED':
        raise SystemExit(f"t2i FAILED {tid}: {json.dumps(d)[:400]}")
    img_url = (d.get('image_urls') or [None])[0]
    if not img_url:
        raise SystemExit(f"t2i no image url: {json.dumps(d)[:400]}")
    dl(img_url, out)
    b1 = balance()
    log({'kind': 't2i-dl', 'out': out, 'url': img_url, 'bal_after': b1})
    print('saved', out, 'url', img_url, 'balance', b1)


def i23d(ref, out, tri, prompt=None):
    if tri > MAX_TARGET:
        raise SystemExit(f'target_polycount {tri} > cap {MAX_TARGET}')
    if ref.startswith('http'):
        url = ref
    else:
        b = open(ref, 'rb').read()
        url = f'data:image/png;base64,{base64.b64encode(b).decode()}'
    b0 = guard(15)
    body = {'ai_model': 'meshy-6-lite', 'image_url': url, 'topology': 'quad',
            'target_polycount': int(tri), 'symmetry_mode': 'auto', 'should_remesh': True}
    if prompt:
        body['prompt'] = prompt
    outj = req(f'{API}/v1/image-to-3d', body)
    tid = outj['result']
    log({'kind': 'i23d', 'task_id': tid, 'ref': ref[:64], 'out': out, 'tri': tri, 'bal_before': b0})
    d = wait(f'{API}/v1/image-to-3d/{tid}')
    log({'kind': 'i23d-done', 'task_id': tid, 'status': d['status'], 'model_urls': d.get('model_urls'), 'out': out})
    if d['status'] != 'SUCCEEDED':
        raise SystemExit(f"i23d FAILED {tid}: {json.dumps(d)[:400]}")
    r = d
    glb_url = r.get('model_urls', {}).get('glb')
    if not glb_url:
        raise SystemExit(f"i23d no glb url: {json.dumps(r)[:400]}")
    dl(glb_url, out)
    b1 = balance()
    log({'kind': 'i23d-dl', 'out': out, 'bal_after': b1})
    print('saved', out, 'balance', b1)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'balance':
        print(balance())
    elif cmd == 't2i':
        t2i(sys.argv[2], ' '.join(sys.argv[3:]))
    elif cmd == 'i23d':
        i23d(sys.argv[2], sys.argv[3], int(sys.argv[4]),
             ' '.join(sys.argv[5:]) if len(sys.argv) > 5 else None)
    else:
        raise SystemExit('unknown cmd ' + cmd)