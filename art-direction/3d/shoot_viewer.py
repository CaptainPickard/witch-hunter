#!/usr/bin/env python3
"""Playwright screenshots of arsenal-viewer.html: default cam, close cam, raw texture."""
import sys, time, base64, json
from playwright.sync_api import sync_playwright

def shoot(page, out, cam=None, raw=False, wait_ms=1200):
    if raw:
        page.click("#btnRaw")
        time.sleep(0.8)
    if cam:
        page.evaluate("""() => {
            window.__ioFix = true;
            const c = arguments; // not used
        }""")
    page.screenshot(path=out)
    return out

def main(base, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    cookie = open("/tmp/cookieval.txt").read().strip()  # bare session value
    kv = ["hermes_session", cookie]
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
        ctx = b.new_context(viewport={"width": 1280, "height": 800})
        ctx.add_cookies([{"name": kv[0], "value": kv[1], "url": base}])
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
        pg.goto(base + "/art-3d-viewer", wait_until="load", timeout=120000)
        # wait for asset select to be populated (polling; CSP blocks string eval)
        for _ in range(120):
            n = pg.evaluate("document.getElementById('selBody') ? document.getElementById('selBody').options.length : 0")
            if n > 1:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("selBody never populated")
        # select human-hunter-male
        pg.select_option("#selBody", "human-hunter-male")
        time.sleep(2.5)  # let GLB parse + first frames render
        pg.screenshot(path=f"{outdir}/before_default_cam.png")
        # close camera: OrbitControls owns position; set via its target and re-look
        pg.evaluate("""() => {
            autoRot = false;
            document.getElementById('btnRot').textContent = 'rotation OFF';
            controls.target.set(0, 1.0, 0);
            camera.position.set(0, 1.3, 3.2);
            controls.update();
        }""")
        time.sleep(1.0)
        pg.screenshot(path=f"{outdir}/before_close_cam.png")
        # raw texture mode
        pg.click("#btnRaw")
        time.sleep(1.5)
        pg.screenshot(path=f"{outdir}/before_raw_mode.png")
        # back to pixelated
        pg.click("#btnRaw")
        time.sleep(1.0)
        print("JS errors:", json.dumps(errors[:10], indent=1))
        print("done")
        b.close()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8787",
         sys.argv[2] if len(sys.argv) > 2 else "/tmp/viewer_shots_before")