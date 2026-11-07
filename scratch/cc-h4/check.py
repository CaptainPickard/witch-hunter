import re
F = '/tmp/wh-worldfeat/io/specs/cc-h4-scar-reader-valspec.md'
t = open(F).read()
lines = t.count('\n')
vitems = re.findall(r'^- \*\*(V-\d+)\*\*', t, re.M)
nitems = re.findall(r'^- \*\*(N-\d+)\*\*', t, re.M)
ambs = re.findall(r'^- \*\*(AMB-\d+)\*\*', t, re.M)
print('lines:', lines)
print('V:', vitems)
print('N:', nitems)
print('AMB:', ambs)
print('V count:', len(vitems), '| N count:', len(nitems), '| AMB count:', len(ambs))
