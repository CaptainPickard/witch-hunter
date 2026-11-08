#!/usr/bin/env python3
"""Build builds/v8-playable.html: inline style.css + vendor + js from prototype sources.
Usage: python3 tools/build_v8.py  (run from repo root). No node required.
"""
import re, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root
P = ROOT / 'prototype'
OUT = P / 'builds' / 'v8-playable.html'

index = (P / 'index.html').read_text()

# 1. head style: replace <link rel=stylesheet> (or keep existing inline) with style.css content
style = (P / 'style.css').read_text()
html = index
# remove any stylesheet link tags
html = re.sub(r'<link[^>]*stylesheet[^>]*>', '', html)
# inject style right after <head> open block (before </head>)
html = html.replace('</head>', '<style>\n' + style + '\n</style>\n</head>')

# 2. replace each <script src="..."></script> with inline content, in order
def inline_js(match):
    src = match.group(1)
    path = P / src
    content = path.read_text()
    return '<script>\n' + content + '\n</script>'

html = re.sub(r'<script src="([^"]+)"></script>', inline_js, html)

# 3. title
html = html.replace('<title>Witch Hunter</title>', '<title>Witch Hunter v9 - EPR1 Combat</title>')
html = re.sub(r'<title>.*?</title>', '<title>Witch Hunter v9 - EPR1 Combat</title>', html, count=1, flags=re.S)
# Build stamp: tab title carries date + HEAD sha so a stale browser cache is
# instantly visible (Nicko sweep fix 2026-11-06). Disclosed inline: no-logic tool change.
try:
    import subprocess as _sp
    from datetime import datetime as _dt, timezone as _tz
    _head = _sp.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=str(ROOT),
                    capture_output=True, text=True, timeout=10).stdout.strip()
    # DETERMINISTIC-BUILD LAW (2026-11-06): stamp from the HEAD commit's
    # author time, not wall clock — rebuilds of the same HEAD are
    # byte-identical, which keep coherence guards and release flips stable.
    _r2 = _sp.run(['git', 'show', '-s', '--format=%cI', 'HEAD'], cwd=str(ROOT),
                  capture_output=True, text=True, timeout=10)
    _stamp = _dt.fromisoformat((_r2.stdout or '').strip()).astimezone(_tz.utc).strftime('%m-%d %H:%MZ')
    html = html.replace('<title>Witch Hunter v9 - EPR1 Combat</title>',
                        f'<title>Witch Hunter v9 - EPR1 Combat (build {_stamp} {_head})</title>', 1)
except Exception:
    pass

OUT.write_text(html)
print('wrote', OUT, OUT.stat().st_size, 'bytes')
