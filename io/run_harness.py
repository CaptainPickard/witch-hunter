"""Run the combat-ds1 validation harness and print the per-AC profile."""
import subprocess
r = subprocess.run(
    ['python3', 'tests/wh_combat_ds1_validation.py'],
    capture_output=True, text=True, cwd='/workspace/witch-hunter')
for ln in r.stdout.split('\n'):
    if ln.startswith('AC-') or 'SMOKE' in ln or 'ZERO' in ln:
        print(ln)
print('exit:', r.returncode)