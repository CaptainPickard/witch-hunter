import time, os, sys

RESULT = "/tmp/delegation_result_epr1_valspec.md"
deadline = time.time() + 5400  # 90 min cap
while time.time() < deadline:
    if os.path.exists(RESULT) and os.path.getsize(RESULT) > 100:
        time.sleep(2)
        print("RESULT FILE READY:", RESULT)
        print(open(RESULT).read())
        sys.exit(0)
    time.sleep(20)
print("TIMEOUT waiting for", RESULT)
sys.exit(1)