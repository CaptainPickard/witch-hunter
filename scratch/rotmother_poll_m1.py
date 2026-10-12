"""Poll Meshy task every 60s until it leaves PENDING; then print state."""
import json, subprocess, sys, time

KEY = open('/home/hermeswebui/.hermes/profiles/io/secrets/meshy_key').read().strip()
TASK = sys.argv[1]
MAXWAIT = int(sys.argv[2]) if len(sys.argv) > 2 else 900

t0 = time.time()
while time.time() - t0 < MAXWAIT:
    out = subprocess.run(
        ['curl', '-s', f'https://api.meshy.ai/openapi/v1/image-to-3d/{TASK}',
         '-H', f'Authorization: Bearer {KEY}'],
        capture_output=True, text=True, timeout=60)
    d = json.loads(out.stdout)
    st = d.get('status')
    prog = d.get('progress', '')
    print(f'{int(time.time()-t0):4d}s {st} {prog}', flush=True)
    if st in ('PENDING', 'IN_PROGRESS'):
        time.sleep(60)
        continue
    bal = subprocess.run(
        ['curl', '-s', 'https://api.meshy.ai/openapi/v1/balance',
         '-H', f'Authorization: Bearer {KEY}'],
        capture_output=True, text=True, timeout=60)
    print('BALANCE', bal.stdout)
    print('THUMB', d.get('thumbnail_url', ''))
    print(json.dumps({k: d.get(k) for k in
                      ('status', 'progress', 'started_at', 'finished_at',
                       'tasks_error', 'model_urls', 'texture_urls')},
                     indent=2)[:1200])
    break