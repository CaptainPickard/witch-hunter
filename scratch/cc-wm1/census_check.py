import re
src = open('prototype/js/CONFIG.js').read()
cmt = src.index('west_hollow_den')
start = src.rindex('    nodes: [', 0, cmt)
end = src.index('    ],', start)
block = src[start:end]
bone = re.findall(r"\{ type: 'bonePile', x: ([-\d.]+), z: ([-\d.]+) \}", block)
expected = [('-192.5','-461'),('-184','-450'),('-204','-453.5'),('-198.5','-441'),
            ('208.5','-455'),('199.5','-446'),('220','-447.5'),('214.5','-435')]
print("bone rows:", len(bone), "match:", sorted(bone)==sorted(expected))

# enemies census anchor
cmt2 = src.index('wolf-pack loop point')
es = src.rindex('    enemies: [', 0, cmt2); ee = src.index('    ],', es)
from collections import Counter
print("enemies:", dict(Counter(re.findall(r"type: '([a-z]+)'", src[es:ee]))))

# nodeTypes keys
s2=src.index('nodeTypes: {'); e2=src.index('\n  }\n};', s2)
print("nodeTypes keys:", re.findall(r"^    ([a-zA-Z]+):\s+\{", src[s2:e2], re.M))
print("ingredients:", re.findall(r"^  ([a-zA-Z]+):\s*\{[^}]*category:\s*'ingredient'", src, re.M))
print("file-wide bandit rows:", len(re.findall(r"\{ type: 'bandit', x:", src)))

# props count + last row
ps = src.rindex('    props: [', 0, cmt)
pe = src.index('    ],', ps)
allp = re.findall(r"\{ asset: '", src[ps:pe])
print("props rows:", len(allp))
