import asyncio
from playwright.async_api import async_playwright

URL = "file:///workspace/witch-hunter/art-direction/3d/arsenal-viewer.html"
OUT = "/workspace/witch-hunter/art-direction/3d/shots"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        pg.on("console", lambda m: print("console:", m.type, m.text[:200]))
        pg.on("pageerror", lambda e: print("pageerror:", str(e)[:200]))
        await pg.goto(URL)
        await pg.wait_for_timeout(20000)
        # select body
        await pg.select_option("#selBody", "human-hunter-male")
        await pg.wait_for_timeout(6000)
        await pg.screenshot(path=f"{OUT}/arsenal-default.png")
        # close-up camera
        await pg.evaluate("camera.position.set(0,1.3,3.2); controls.target.set(0,1.0,0);")
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f"{OUT}/arsenal-closeup.png")
        # sanity: ids present, stat text
        ids = await pg.evaluate("[['selBody','selHead','selChest','selRH','selLH','btnHead','btnChest','btnRH','btnLH','btnRot','btnRaw','stat','err','leftPanel','rightPanel']].every(a=>a.every(i=>!!document.getElementById(i))) ? 'ALL_IDS_OK' : 'MISSING_ID'")
        print("ids:", ids)
        print("stat:", await pg.text_content("#stat"))
        print("err:", repr(await pg.text_content("#err")))
        await b.close()

asyncio.run(main())