import time, os, sys

RESULT = "/tmp/delegation_result_epr1_validate.md"
VERDICT = "/workspace/wh-erparity-test/scratch/erparity/VALIDATION-VERDICT-EPR1.md"
deadline = time.time() + 5400
while time.time() < deadline:
    if os.path.exists(RESULT) and os.path.getsize(RESULT) > 50:
        time.sleep(2)
        print("RESULT FILE READY")
        print(open(RESULT).read())
        break
    time.sleep(20)
else:
    print("TIMEOUT waiting for", RESULT)
    if os.path.exists(VERDICT):
        print("VERDICT FILE EXISTS:")
        print(open(VERDICT).read()[:4000])
    sys.exit(1)