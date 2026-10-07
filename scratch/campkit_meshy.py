#!/usr/bin/env python3
"""Campkit-asset Meshy helper (2026-10-07). SERIAL ONLY. Clone of
scratch/torch_meshy.py / tree_meshy.py chain, self-contained. Mission floor
per dispatch addendum: START_BALANCE=1107, FLOOR=1087 (cap 20 credits).
Key from env only, never logged, never written to a file.

  campkit_meshy.py balance | t2i <out.png> <prompt...> | i23d <ref.png> <out.glb> [tri]
Log: scratch/campkitgen/campkit_meshy_log.jsonl (task ids, statuses, balance).
"""
import sys, os, json, time, base64, urllib.request, urllib.error

KEY = os.environ.get('MESHY_KEY') or sys.exit('MESHY_KEY not set')
API = 'https://api.meshy.ai/openapi'
START_BALANCE = 1107   # balance at dispatch (measured 2026-10-07 03:05 UTC)
CAP = 20               # ~3cr ref + 15cr mesh, ZERO headroom for re-rolls
FLOOR = START_BALANCE - CAP
MAX_TARGET = 22000     # addendum: target_polycount 15000-22000
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campkitgen', 'campkit_meshy_log.jsonl')


def req(url, data=None):
    r = urllib.request.Request(url)
    r.add_header('Authorization', f'Bearer {KEY}')
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        r.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(r, body, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code}: {e.read().decode()[:500]}')


def balance():
    return req(f'{API}/v1/balance')['balance']


def log(rec):
    rec['t'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, 'a') as f:
        f.write(json.dumps(rec) + '\n')


def guard(cost_estimate):
    b = balance()
    if b - cost_estimate < FLOOR:
        raise SystemExit(f'CAP GUARD: balance {b}, est cost {cost_estimate}, floor {FLOOR} -> refusing submit')
    return b


def wait(url, every=10, max_s=1800):
    t0 = time.time()
    while True:
        s = req(url)
        st = s.get('status')
        if st in ('SUCCEEDED', 'FAILED', 'CANCELED') or time.time() - t0 > max_s:
            return s
        print(f'  {st} {s.get("progress")}%', flush=True)
        time.sleep(every)


def dl(url, path):
    with urllib.request.urlopen(url, timeout=300) as r, open(path, 'wb') as f:
        f.write(r.read())


def t2i(out, prompt):
    b0 = guard(10)
    tid = req(f'{API}/v1/text-to-image', {'ai_model': 'nano-banana', 'prompt': prompt})['result']
    print('task_id', tid, flush=True)
    log({'kind': 't2i', 'task_id': tid, 'out': out, 'prompt': prompt, 'bal_before': b0})
    s = wait(f'{API}/v1/text-to-image/{tid}')
    b1 = balance()
    log({'kind': 't2i-done', 'task_id': tid, 'status': s.get('status'), 'bal_after': b1,
         'err': s.get('task_error')})
    if s.get('status') != 'SUCCEEDED':
        raise SystemExit(f'{tid} {s.get("status")} {s.get("task_error")}')
    dl(s['image_urls'][0], out)
    print('saved', out, 'credits', b0 - b1, 'balance', b1)


def i23d(ref, out, tri):
    if int(tri) > MAX_TARGET or int(tri) < 15000:
        raise SystemExit(f'target_polycount {tri} outside mission band 15000-22000')
    b0 = guard(15)   # observed meshy-5 image-to-3d cost: 15 on 60+/60+ calls in the logs
    uri = 'data:image/png;base64,' + base64.b64encode(open(ref, 'rb').read()).decode()
    body = {'ai_model': 'meshy-5', 'image_url': uri, 'topology': 'quad',
            'target_polycount': int(tri), 'symmetry_mode': 'auto', 'should_remesh': True}
    tid = req(f'{API}/v1/image-to-3d', body)['result']
    print('task_id', tid, flush=True)
    log({'kind': 'i23d', 'task_id': tid, 'ref': ref, 'out': out, 'tri': int(tri), 'bal_before': b0})
    s = wait(f'{API}/v1/image-to-3d/{tid}')
    b1 = balance()
    log({'kind': 'i23d-done', 'task_id': tid, 'status': s.get('status'), 'bal_after': b1,
         'err': s.get('task_error')})
    if s.get('status') != 'SUCCEEDED':
        raise SystemExit(f'{tid} {s.get("status")} {s.get("task_error")}')
    dl(s['model_urls']['glb'], out)
    print('saved', out, 'credits', b0 - b1, 'balance', b1)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'balance':
        print(balance())
    elif cmd == 't2i':
        t2i(sys.argv[2], ' '.join(sys.argv[3:]))
    elif cmd == 'i23d':
        i23d(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 15000)