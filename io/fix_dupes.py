"""IO self-fix: surgically dedupe stacked run_sampler defs with exact spans
read from the file itself. Idempotent."""
import hashlib
import pathlib
import re

P = pathlib.Path('/workspace/witch-hunter/tests/wh_combat_ds1_validation.py')
t = P.read_text()
defs = [m.start() for m in re.finditer(r'def run_sampler\(', t)]
print('defs found:', defs)

if len(defs) == 2:
    # Old promise-sampler block: comment marker above def 0 .. line before def 1
    block1_comment = t.rfind('# D2-C window-buffer sampler (no pending promise)', 0, defs[0])
    block1_start = t.rfind('\n', 0, block1_comment) + 1
    block1_end = t.find('def drain_sampler', defs[0])
    block1_end = t.rfind('\n', 0, block1_end) + 1
    # Second block: def 1 comment to its cancel line end
    c2_marker = t.find('# D2-C window-buffer sampler (instant resolve; rows stored on window).', defs[0])
    block2_start = t.rfind('\n', 0, c2_marker) + 1
    # find end of the second block's cancel line
    m2 = t.find('window.__IO_A34_RAF=null;}', block2_start)
    block2_end = t.find('\n', m2) + 1
    # Remove first block span entirely (old promise sampler)
    t2 = t[:block1_start] + t[block1_end:]
    P.write_text(t2)
    print('REMOVED old block span', block1_start, '..', block1_end)
else:
    print('unexpected def count, no-op')

print('new sha:', hashlib.sha256(P.read_bytes()).hexdigest()[:12])