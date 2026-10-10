"""Empirical: bare click -> attacking? Does a click ALWAYS fail pre-teleport?"""
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
    page = b.new_page()
    page.goto("http://localhost:8791/builds/v7-playable.html")
    page.wait_for_timeout(3500)

    def click_and_read(label):
        page.mouse.click(512, 384)
        time.sleep(0.25)
        s = page.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();"
                          "return {st:(p.getAttackStage?p.getAttackStage():null),"
                          "att:!!p.attacking, yaw:p.yaw};})()")
        print(label, s)
        time.sleep(0.8)

    click_and_read("A bare (no tele):")
    page.evaluate("window.WH_DEBUG.teleportPlayer(-6,-2)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.wait_for_timeout(400)
    click_and_read("B after tele/setcam:")
    page.keyboard.press("f")
    page.wait_for_timeout(600)
    click_and_read("C after F-lock:")
    page.keyboard.press("f")     # unlock
    page.wait_for_timeout(400)
    click_and_read("D unlocked again:")
    b.close()