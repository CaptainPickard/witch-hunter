#!/bin/bash
# CC-AE1 verdict-2 full regression: all v1 val_ case files in landed order,
# JSON captured per file; verdict-2 addendum runs appended by the caller.
cd /tmp/wh-worldfeat/scratch/cc-ae1-val
set -u
for f in val_A02_05_fix.js val_A07_13.js val_A14_16.js val_A17_22.js val_A24_29.js val_A30_33.js val_A30_last.js; do
  echo "=== $f"
  timeout 560 node "$f" > "tmp/reg_${f%.js}.json" 2> "tmp/reg_${f%.js}.err"
  echo "exit=$?"
done
echo "=== digest of runs"
python3 - <<'EOF'
import json, glob, os, hashlib, re
allrec = []
for f in ["val_A02_05_fix","val_A07_13","val_A14_16","val_A17_22","val_A24_29","val_A30_33","val_A30_last"]:
    path = f"tmp/reg_{f}.json"
    recs = []
    for line in open(path):
        line = line.strip()
        if line.startswith("[") or line.startswith("{"):
            try:
                data = json.loads(line)
                recs += data if isinstance(data, list) else [data]
            except Exception: pass
    seen = {}
    for r in recs:
        if isinstance(r, dict) and r.get("id","").startswith("V-A"):
            seen[r["id"]] = r  # later files override (A02/A05 fix, A30 last)
    for k in sorted(seen, key=lambda s: int(s.split("A-")[1])):
        r = seen[k]
        allrec.append(r)
        print(f"{k} {r['result']:4s} {r.get('name','')}")
print("TOTAL", len(allrec), "PASS", sum(1 for r in allrec if r["result"]=="PASS"))
json.dump(allrec, open("tmp/reg_all_records.json","w"), indent=1)
EOF
