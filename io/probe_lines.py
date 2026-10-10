"""IO diagnostic: show harness lines 1280..1320 to locate the syntax break."""
import pathlib

h = pathlib.Path('/workspace/witch-hunter/tests/wh_combat_ds1_validation.py')
t = h.read_text()
lines = t.split('\n')
for n in range(1290, min(len(lines), 1315)):
    print(n, '>', lines[n])
print('total lines:', len(lines))