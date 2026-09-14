#!/usr/bin/env python3
"""Baseline/FX screenshots of the LIVE /art-3d-viewer route: 3 bodies, close cam, pixelated."""
import sys, time, json, os, urllib.request
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8787"
BODIES = ["human-hunter-male", "orc-male-warrior", "vampire-male-noble"]

def get_cookie():
    pw = None
    for p in ["/workspace/hermes-webui/.env", "/root/.env"]:
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("HERMES_WEBUI_PASSWORD=") or line.startswith("WEBUI_PASS="):
                    pw = line.split("=", 1)[1].strip()
                    break
        if pw: break
    req = urllib.request.Request(BASE + "/api/auth/login",
        data=json.dumps({"password": pw}).encode(), headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    setc = resp.headers.get("Set-Cookie", "")
    return setc.split(";")[0].split("=", 1)[1]

def main(outdir, tag):
    os.makedirs(outdir, exist_ok=True)
    cookie = get_cookie()
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = b.new_context(viewport={"width": 1280, "height": 800})
        ctx.add_cookies([{"name": "hermes_session", "value": cookie, "url": BASE}])
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(BASE + "/art-3d-viewer", wait_until="load", timeout=120000)
        for _ in range(120):
            n = pg.evaluate("document.getElementById('selBody') ? document.getElementById('selBody').options.length : 0")
            if n > 10: break
            time.sleep(0.5)
        else:
            raise RuntimeError("selBody never populated")
        time.sleep(3)  # asset parse settle
        for body in BODIES:
            pg.select_option("#selBody", body)
            time.sleep(6)  # body parse + frames
            pg.evaluate("""() => {
                autoRot = false;
                body.rotation.y = 0;
                controls.target.set(0, 1.0, 0);
                camera.position.set(0, 1.3, 3.2);
                controls.update();
            }""")
            time.sleep(1.0)
            info = pg.evaluate("JSON.stringify({tri: renderer.info.render.triangles, texMode: texMode, rot: body ? body.rotation.y : null})")
            pg.screenshot(path=f"{outdir}/{tag}_{body}_close.png")
            print(body, "info:", info)
        print("JS errors:", json.dumps(errors[:10]))
        b.close()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/shots", sys.argv[2] if len(sys.argv) > 2 else "base")