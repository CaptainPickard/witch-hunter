from pathlib import Path

p = Path('/workspace/witch-hunter/tests/wh_combat_ds1_validation.py')
txt = p.read_text()
print('total lines:', len(txt.split('\n')))
print('_wrap_pi occurrences:', txt.count('_wrap_pi'))
print('wrap_pi( occurrences:', txt.count('wrap_pi('))
print('double-RAF gate present:', 'if (window.__IO_SAMPLER_RAF) return;' in txt)