import subprocess

r = subprocess.run(
    ['python3', 'tests/wh_combat_ds1_validation.py'],
    capture_output=True, text=True,
    cwd='/workspace/witch-hunter')
for line in r.stdout.split('\n'):
    if line.startswith('AC-') or 'SMOKE' in line or 'ZERO' in line:
        print(line)
print('EXIT:', r.returncode)