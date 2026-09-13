#!/usr/bin/env python3
"""S7: build a card billboard page from a card's atlas frames.

Replicates the proven card01 pattern (orbit drag, idle toggle, atlases,
findings) parametrized per card. All images embedded as data URIs.
Pure ASCII text.

Usage:
  python3 build_billboard.py --dir sprites/orc-male --prefix orc-m \
    --title "Card 01 - Orc, Male" --sub "..." --mood "..." \
    --concept concept.png --out card01-billboard.html \
    --findings findings.json
"""
import sys, os, json, base64, io, argparse
from PIL import Image

ORDER = [('back', 'view-back'), ('3/4 rear L', 'view-3q-rear'),
         ('side L', 'view-side'), ('3/4 front L', 'view-3q-front'),
         ('front', 'view-front'), ('3/4 front R', 'view-3q-front-right'),
         ('side R', 'view-side-right'), ('3/4 rear R', 'view-3q-rear-right')]

CSS = """
:root { --ink:#08090D; --gold:#C9A227; --bone:#D6D2C4; --ash:#8D93A3; --line:#2A3142; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:Georgia, serif; color:var(--bone); background:var(--ink);
  background-image:radial-gradient(ellipse at 50% 0%, #10131C, #08090D 70%);
  line-height:1.6; font-size:17px; padding:40px 24px 90px; }
body::after { content:''; position:fixed; inset:0; pointer-events:none;
  background-image:repeating-conic-gradient(rgba(255,255,255,0.012) 0% 25%, transparent 0% 50%);
  background-size:3px 3px; mix-blend-mode:overlay; }
.wrap { max-width:1100px; margin:0 auto; }
h1 { font-size:46px; text-align:center; text-shadow:0 0 18px rgba(201,162,39,0.3); margin:10px 0 4px; }
.sub { text-align:center; color:var(--ash); font-size:12px; letter-spacing:0.3em; text-transform:uppercase; margin-bottom:30px; }
.panel { border:1px solid var(--line); background:linear-gradient(180deg,#0E1119,#0A0C12);
  box-shadow:inset 0 0 60px rgba(0,0,0,0.55); padding:26px 30px; margin:22px 0; position:relative; }
.panel::before, .panel::after { content:''; position:absolute; left:8px; right:8px; height:10px;
  border-top:1px solid #8A741F; border-bottom:1px solid var(--line); }
.panel::before { top:5px; } .panel::after { bottom:5px; }
h2 { font-variant:small-caps; letter-spacing:0.35em; color:var(--gold); font-weight:normal; font-size:17px; text-align:center; margin:8px 0 16px; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:22px; align-items:center; }
@media (max-width:880px) { .grid2 { grid-template-columns:1fr; } }
.frame { border:1px solid #3D4759; padding:6px; background:#05060A; }
.frame img { display:block; width:100%; height:auto; }
.stage { position:relative; height:440px; border:1px solid #3D4759; background:#05060A; overflow:hidden; touch-action:none; }
.stage .ground { position:absolute; left:0; right:0; bottom:0; height:120px;
  background:linear-gradient(180deg, transparent, rgba(20,24,34,0.9)); }
.stage .fog { position:absolute; inset:0;
  background:radial-gradient(ellipse at 50% 80%, rgba(70,88,110,0.25), transparent 60%); }
#sprite { position:absolute; left:50%; bottom:26px; width:250px; transform:translateX(-50%);
  filter:drop-shadow(0 14px 18px rgba(0,0,0,0.7)); }
.ctl { text-align:center; margin-top:14px; }
button { background:#0D1017; color:var(--gold); border:1px solid #3D4759; padding:8px 18px;
  font-family:inherit; font-size:14px; cursor:pointer; margin:0 6px; }
button:hover { border-color:var(--gold); }
.readout { text-align:center; color:var(--ash); font-size:13px; margin-top:10px; }
.notes li { color:#9AA0B0; font-size:14.5px; margin:7px 0 7px 18px; }
.mood { text-align:center; color:#B9BDC9; max-width:760px; margin:0 auto; }
.lbl { color:#6E7484; font-size:12px; letter-spacing:0.25em; text-transform:uppercase; text-align:center; margin:6px 0 12px; }
"""


def png_uri(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def jpg_uri(path, max_w=960, q=80, bg=(10, 12, 18)):
    im = Image.open(path)
    if im.mode == 'RGBA':
        flat = Image.new('RGB', im.size, bg)
        flat.paste(im, mask=im.split()[3])
        im = flat
    else:
        im = im.convert('RGB')
    if im.size[0] > max_w:
        im = im.resize((max_w, int(im.size[1] * max_w / im.size[0])), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=q)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True, help='card dir (art-direction-relative or absolute)')
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--sub', required=True)
    ap.add_argument('--mood', required=True)
    ap.add_argument('--concept', default='concept.png')
    ap.add_argument('--out', required=True)
    ap.add_argument('--findings', help='JSON file: list of finding strings')
    ap.add_argument('--flicker', default='')
    a = ap.parse_args()

    cdir = a.dir if os.path.isabs(a.dir) else os.path.join(
        '/workspace/witch-hunter/art-direction', a.dir)
    atlas = os.path.join(cdir, 'atlas')

    findings = []
    if a.findings:
        findings = json.load(open(a.findings))

    frames = []
    for label, fname in ORDER:
        still_path = os.path.join(atlas, a.prefix + '-' + fname + '.png')
        still = png_uri(still_path)
        if label == 'back':
            idle = [png_uri(os.path.join(atlas, a.prefix + '-idle-f%d.png' % i))
                    for i in range(1, 6)]
        else:
            idle = [still] * 5
        frames.append({'still': still, 'idle': idle})

    concept_uri = jpg_uri(os.path.join(cdir, a.concept))
    dir_atlas = jpg_uri(os.path.join(atlas, a.prefix + '-directions-atlas.png'), max_w=1600, q=72)
    idle_atlas = jpg_uri(os.path.join(atlas, a.prefix + '-idle-atlas.png'), max_w=1600, q=72)

    find_items = ''.join('<li>%s</li>' % f for f in findings)
    flicker_note = (' (flicker %s)' % a.flicker) if a.flicker else ''
    html = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Witch Hunter - %s</title>\n<style>%s</style></head>\n'
            '<body><div class="wrap">\n<h1>%s</h1>\n<div class="sub">%s</div>\n'
            '<p class="mood">%s</p>\n'
            '<div class="panel">\n<h2>Concept vs Sprite</h2>\n<div class="grid2">\n'
            '  <div><div class="lbl">Approved concept frame</div>\n'
            '    <div class="frame"><img src="%s"></div>\n'
            '  <div><div class="lbl">Generated sprite, live billboard (drag to orbit)</div>\n'
            '    <div class="stage">\n      <div class="fog"></div><div class="ground"></div>\n'
            '      <img id="sprite" src="%s">\n    </div>\n'
            '    <div class="ctl">\n      <button id="left">&lt; orbit</button>\n'
            '      <button id="idlebtn">idle: on</button>\n'
            '      <button id="right">orbit &gt;</button>\n    </div>\n'
            '    <div class="readout" id="readout"></div>\n  </div>\n</div>\n</div>\n'
            '<div class="panel"><h2>Directional Atlas</h2>\n<div class="frame">'
            '<img src="%s"></div>\n<div class="lbl">8 directions</div>\n</div>\n'
            '<div class="panel"><h2>Idle Atlas</h2>\n<div class="frame">'
            '<img src="%s"></div>\n<div class="lbl">5-frame breathing idle, back view%s</div>\n</div>\n'
            '<div class="panel"><h2>Card Findings</h2>\n<ul class="notes">%s</ul>\n</div>\n'
            '<div style="text-align:center;color:#565C6C;font-size:11px;letter-spacing:0.3em;'
            'text-transform:uppercase;margin-top:40px;">Witch Hunter - production run - 2026</div>\n'
            '</div>\n<script>\nconst FRAMES = %s;\n'
            'const VIEWNAMES = ["back","3/4 rear L","side L","3/4 front L","front",'
            '"3/4 front R","side R","3/4 rear R"];\n'
            'let angle = 0, idleOn = true, idleF = 0;\n'
            'const sprite = document.getElementById("sprite");\n'
            'const readout = document.getElementById("readout");\n'
            'function dirIndex(a) { return Math.round(((a %% 360) + 360) %% 360 / 45) %% 8; }\n'
            'function render() {\n'
            '  const di = dirIndex(angle);\n'
            '  sprite.src = idleOn ? FRAMES[di].idle[idleF %% 5] : FRAMES[di].still;\n'
            "  readout.textContent = 'camera: ' + Math.round(((angle%%360)+360)%%360) + "
            "' deg - view: ' + VIEWNAMES[di] + (idleOn ? ' - idle f' + (idleF%%5+1) : '');\n}\n"
            "document.getElementById('left').onclick = () => { angle -= 15; render(); };\n"
            "document.getElementById('idlebtn').onclick = function() { idleOn = !idleOn; "
            "this.textContent = 'idle: ' + (idleOn?'on':'off'); render(); };\n"
            "document.getElementById('right').onclick = () => { angle += 15; render(); };\n"
            'const stage = document.querySelector(".stage");\n'
            'let dragging = false, lastX = 0;\n'
            'stage.addEventListener("pointerdown", e => { dragging = true; lastX = e.clientX; });\n'
            'window.addEventListener("pointerup", () => dragging = false);\n'
            'window.addEventListener("pointermove", e => { if (dragging) { '
            'angle += (e.clientX-lastX)*0.6; lastX = e.clientX; render(); } });\n'
            'setInterval(() => { if (idleOn) { idleF = (idleF+1)%%5; render(); } }, 320);\n'
            'render();\n</script>\n</body></html>\n') % (
        a.title, CSS, a.title, a.sub, a.mood, concept_uri, frames[0]['idle'][0],
        dir_atlas, idle_atlas, flicker_note, find_items, json.dumps(frames))

    # sanity: pure ASCII
    non_ascii = [c for c in html if ord(c) > 127]
    assert not non_ascii, 'non-ASCII found: %r' % set(non_ascii)
    with open(os.path.join(cdir, a.out), 'w') as fp:
        fp.write(html)
    print('written:', os.path.join(cdir, a.out), os.path.getsize(os.path.join(cdir, a.out)) // 1024, 'KB')


if __name__ == '__main__':
    main()