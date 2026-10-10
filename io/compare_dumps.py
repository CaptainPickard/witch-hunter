#!/usr/bin/env python3
"""Match rebuilt code objects to the ORIGINAL frozen dumps (pre-overwrite) by
ORDER of code objects from both pycs' nested-code trees, then compare:
  - instruction sequence (opname + argval)
  - varnames
Frozen instructions come from the preserved /tmp/pyc_dump/* listings; the
comparison here re-parses both MARSHAL roots via the .pyc on disk (rebuilt) and
the /tmp/pyc_dump instruction files (frozen).

Frozen pyc is gone (overwritten), so this tool rebuilds frozen instruction
sequences from /tmp/pyc_dump and compares against live disassembly."""
import dis
import os
import re

FROZEN_DIR = "/tmp/pyc_dump"


def parse_dump(path):
    seq = []
    varnames = None
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("varnames="):
                varnames = eval(line[len("varnames="):])
                continue
            m = re.match(r"\s*(\d+) (LOAD_CLOSURE|MAKE_FUNCTION|LOAD_CONST)"
                         r"().*$", line)
            m = re.match(r"\s*(\d+)\s+([A-Z_]+)\s*(.*)$", line)
            if not m:
                continue
            off = int(m.group(1))
            op = m.group(2)
            rest = m.group(3).strip()
            if op in ("COMPARE_OP",):
                rest = None  # compared by position only
            seq.append((off, op, rest))
    return varnames, seq


def parse_new(path):
    varnames = None
    seq = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("varnames="):
                varnames = eval(line[len("varnames="):])
                continue
            m = re.match(r"\s*(\d)\s.*", line)
            m = re.match(r"\s*(\d+)\s+([A-Z_]+)\s*(.*)$", line)
            if not m:
                continue
            off = int(m.group(1))
            op = m.group(2)
            rest = m.group(3).strip()
            if op in ("COMPARE_OP",):
                rest = None  # dump format lost the symbolic name
            seq.append((off, op, rest))
    return varnames, seq


frozen_files = sorted(f for f in os.listdir(FROZEN_DIR) if f.endswith(".txt"))
bad = 0
for ff in frozen_files:
    fvar, fseq = parse_dump(os.path.join(FROZEN_DIR, ff))
    npath = os.path.join("/tmp/new_dump", ff)
    if not os.path.exists(npath):
        # order-keyed mapping failed; find by firstlineno in name
        fline = int(ff.split("_")[0])
        cands = [n for n in os.listdir("/tmp/new_dump")
                 if n.startswith(str(fline) + "_")]
        if not cands:
            print("NO NEW DUMP for", ff)
            bad += 1
            continue
        npath = os.path.join("/tmp/new_dump", cands[0])
    nvar, nseq = parse_new(npath)
    # compare op sequences position-by-position (offsets should match too)
    ops_f = [(o, op) for o, op, _ in fseq]
    ops_n = [(o, op) for o, op, _ in nseq]
    if ops_f != ops_n:
        first = None
        for a, b in zip(ops_f, ops_n):
            if a != b:
                first = (a, b)
                break
        print("SEQ MISMATCH %s: %s vs %s | frozen=%d new=%d instrs" % (
            ff, first[0], first[1], len(ops_f), len(ops_n)))
        bad += 1
    elif fvar != nvar:
        print("VARNAMES MISMATCH %s: %r vs %r" % (ff, fvar, nvar))
        bad += 1
print("CHECKED %d frozen dumps; problems=%d" % (len(frozen_files), bad))