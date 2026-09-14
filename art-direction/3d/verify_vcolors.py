#!/usr/bin/env python3
"""Live-route verification of the vertex-color render: 3 bodies, screenshots."""
import asyncio, json, subprocess, urllib.request
from playwright.async_api import async_playwright

BODIES = ["human-hunter-male", "orc-male-warrior", "vampire-male-noble"]

async def main():
    pw = subprocess.run(['bash', '-c',
        "grep -r 'WEBUI_PASS\\|HERMES_PASS' /workspace/hermes-webui/.env /root/.env 2>/dev/null | head -1 | cut -d= -f2"],
        capture_output=True, text=True).stdout.strip()
    data = json.dumps({'password': pw}).encode()
    req = urllib.request.Request('http://localhost:8787/api/auth/login', data=data,
                                 headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    cookie = resp.headers.get('Set-Cookie', '').split(';')[0]

    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await b.new_context(viewport={"width": 1440, "height": 900})
        await ctx.add_cookies([{"name": cookie.split('=')[0],
                                "value": cookie.split('=', 1)[1],
                                "url": "http://localhost:8787"}])
        pg = await ctx.new_page()
        await pg.goto("http://localhost:8787/art-3d-viewer")
        await pg.wait_for_timeout(20000)
        for name in BODIES:
            await pg.evaluate("""(nm) => {
                const s = document.getElementById('selBody');
                const opt = [...s.options].find(o => o.value.includes(nm));
                s.value = opt.value; s.dispatchEvent(new Event('change', {bubbles: true}));
            }""", name)
            await pg.wait_for_timeout(6000)
            await pg.evaluate("() => { autoRot = false; if(body) body.rotation.y = 0; }")
            await pg.evaluate("() => { camera.position.set(0, 1.3, 3.2); controls.target.set(0, 1.0, 0); }")
            await pg.wait_for_timeout(1000)
            info = await pg.evaluate("""() => {
                let m = null;
                scene.traverse(o => { if (o.isMesh && o.geometry && o.geometry.attributes.position && o.geometry.attributes.position.count > 1000) m = m || o; });
                if (!m) return 'no-mesh';
                return JSON.stringify({vcolors: !!m.geometry.attributes.color, hasMap: !!m.material.map,
                                       vertexColors: m.material.vertexColors, tris: m.geometry.index.count / 3});
            }""")
            await pg.screenshot(path=f"/tmp/vc_{name}.png")
            print(name, info)
        await b.close()

import asyncio
asyncio.run(main())