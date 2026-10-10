"""IO harness-fix script (run via terminal): dedupe stacked samplers in
tests/wh_combat_ds1_validation.py and normalize them to instant-resolve
window-buffer rAF samplers. Logs every change it makes."""
import hashlib
import pathlib
import re

P = pathlib.Path('/workspace/witch-hunter/tests/wh_combat_ds1_validation.py')
t = P.read_text()
orig_len = len(t)
orig_sha = hashlib.sha256(t.encode()).hexdigest()[:12]

changes = []

# 1. Remove the stale double-RAF gate (promise-era leftover) if present.
stale_gate = '          if (window.__IO_A34_RAF) return;\n'
if stale_gate in t:
    t = t.replace(stale_gate, '')
    changes.append('removed stale gate')

# 2. Collapse any duplicate run_sampler definitions: keep the LAST one.
defs = [m.start() for m in re.finditer(r'def run_sampler\(', t)]
if len(defs) > 1:
    first_start = t.rfind('\n', 0, defs[0]) + 1
    # first block ends where drain_sampler or a comment/def at col 0 begins
    m_end = re.search(r'\n(?=def drain_sampler|def wait_for_stage|def fresh|# ---)', t[defs[0] + 12:])
    first_end = defs[0] + 12 + m_end.start() + 1 if m_end else len(t)
    t = t[:first_start] + t[first_start + (m_end.start() if m_end else 0):]
    changes.append('collapsed duplicate run_sampler defs')

P.write_text(t)
print('orig_len:', orig_len, 'orig_sha:', orig_sha)
print('changes:', changes)
print('new_sha:', hashlib.sha256(P.read_bytes()).hexdigest()[:12])