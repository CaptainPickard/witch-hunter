#!/usr/bin/env python3
"""Astrabot torch-asset Meshy helper (2026-10-05). SERIAL ONLY.
Thin wrapper over scratch/tree_meshy.py (same serial submit+wait+dl chain)
with this mission's own credit floor and log. Key from env only, never logged.

  torch_meshy.py balance | t2i <out.png> <prompt...> | i23d <ref.png> <out.glb> [tri]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tree_meshy as tm

START_BALANCE = 1444   # balance at mission start (after the 10-03 tree run)
CAP = 60               # 1-2 refs + up to 3 mesh attempts
tm.FLOOR = START_BALANCE - CAP
tm.LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'torch_meshy_log.jsonl')

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'balance':
        print(tm.balance())
    elif cmd == 't2i':
        tm.t2i(sys.argv[2], ' '.join(sys.argv[3:]))
    elif cmd == 'i23d':
        tm.i23d(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 15000)
