import time, os, sys

# Watch smoke (ERPARITY SMOKE SUMMARY) + floor freeze (e2_floor.json)
deadline = time.time() + 2400
smoke_done = floor_done = False
while time.time() < deadline and not (smoke_done and floor_done):
    try:
        if not smoke_done:
            log = open('/tmp/erparity_smoke.log').read()
            if 'ERPARITY SMOKE SUMMARY' in log or ('AC-F' in log and 'SUMMARY' in log):
                smoke_done = True
    except FileNotFoundError:
        pass
    if not floor_done and os.path.exists('/workspace/witch-hunter/scratch/erparity/e2_floor.json'):
        floor_done = True
    if not (smoke_done and floor_done):
        time.sleep(20)

print(f"smoke_done={smoke_done} floor_done={floor_done}")
if smoke_done:
    log = open('/tmp/erparity_smoke.log').read()
    print("--- SMOKE TAIL ---")
    print(log[-3500:])
if floor_done:
    print("--- e2_floor.json ---")
    print(open('/workspace/witch-hunter/scratch/erparity/e2_floor.json').read()[:2000])