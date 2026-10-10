#!/usr/bin/env python3
"""Print the SAMPLER_JS module-level string constant from the frozen pyc,
byte-exact, quoted for safe embedding in the rebuild."""
import marshal, json

PYC = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
with open(PYC, "rb") as f:
    f.read(16)
    top = marshal.load(f)

for c in top.co_consts:
    if isinstance(c, str) and "(function(cfg){" in c and "__IO_SAMPLER" in c:
        with open("/tmp/sampler_js.txt", "w") as out:
            out.write(c)
        print("SAVED len=%d" % len(c))
        print(c)
        break