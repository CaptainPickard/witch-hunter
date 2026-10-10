#!/usr/bin/env python3
"""Print the exact string constants of selected code objects from the frozen pyc
(no inline python here; use write_file + terminal per working discipline)."""
import dis, marshal, types

PYC = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
WANT = {"SAMPLER_JS", "ac_a1_1", "ac_a1_2", "ac_a4_4", "main", "player_state", "enemy_ref"}

def walk(co, out):
    for c in co.co_consts:
        if hasattr(c, "co_code"):
            walk(c, out)
    out.append(co)

def main():
    with open(PYC, "rb") as f:
        f.read(16)
        top = marshal.load(f)
    objs = []
    walk(top, objs)
    for co in objs:
        if co.co_name in WANT:
            print("=" * 20, co.co_name, "=" * 20)
            for c in co.co_consts:
                if isinstance(c, str) and not c.startswith("C:\\") and len(c) > 12:
                    print("--- const (len=%d) ---" % len(c))
                    print(c)

main()