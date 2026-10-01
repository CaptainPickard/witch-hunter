# ------------------------------------------------- server + page plumbing ----
def _identity_ok(port):
    """Served tree must BE the R2 worktree: CONFIG.js carries lightPool +
    ambientIntensity 0 (post-relight signature). Status 200 alone is NOT
    identity (an alien server on 8792 serves a stale pre-R2 prototype)."""
    try:
        with urllib.request.urlopen(
                "http://localhost:%d/js/CONFIG.js" % port, timeout=2.0) as r:
            src = r.read()
        return b"lightPool" in src and b"ambientIntensity: 0" in src
    except Exception:
        return False


def start_server():
    """External-reuse ONLY with content identity; else spawn own server on an
    EPHEMERAL port and repoint BASE_ROOT/PORT module globals."""
    global BASE_ROOT, PORT
    try:
        with urllib.request.urlopen(BASE_ROOT, timeout=1.0) as r:
            if r.status == 200 and _identity_ok(PORT):
                return None  # external server already up AND is our tree
    except Exception:
        pass
    # ephemeral port pick (bind-close race acceptable; poll confirms)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    newport = sock.getsockname()[1]
    sock.close()
    proc = None
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py", str(newport)],
            cwd=os.path.join(REPO_ROOT, "prototype"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        print("[diag] server spawn failed %r" % e)
    deadline = time.time() + 15.0
    while time.time() < deadline:
        if proc is None or proc.poll() is not None:
            break
        try:
            if _identity_ok(newport):
                BASE_ROOT = "http://localhost:%d/" % newport
                PORT = newport
                print("[diag] spawned own server on port %d" % newport)
                return proc
        except Exception:
            pass
        time.sleep(0.3)
    print("[diag] server poll never came up with R2 content")
    return proc


def stop_server(proc):
    if proc is None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


INIT_SCRIPT = """window.__R2_BOOT_PROBE = {done:false};
(function(){ function probe(){ if(window.__R2_BOOT_PROBE.done) return;
  if(window.WH_GAME && window.WH_GAME.scene && window.WH_GAME.lightPool){
    var pls=[], sps=[];
    window.WH_GAME.scene.traverse(function(o){
      if(o.isPointLight) pls.push(o.uuid);
      if(o.isSprite) sps.push(o.uuid); });
    var am=0, hemi=0, dir=0;
    window.WH_GAME.scene.traverse(function(o){
      if(o.isAmbientLight) am++;
      if(o.isHemisphereLight) hemi++;
      if(o.isDirectionalLight) dir++; });
    window.__R2_BOOT_PROBE = {done:true, pointLightUuids:pls, spriteUuids:sps,
      ambient:am, hemi:hemi, dir:dir,
      poolLen:window.WH_GAME.lightPool.length,
      programs:(window.WH_GAME.renderer && window.WH_GAME.renderer.info)
        ? window.WH_GAME.renderer.info.programs.length : null}; }
}
window.__r2probeLoop = function(){ probe(); requestAnimationFrame(window.__r2probeLoop); };
window.__r2probeLoop(); })();"""

READY_JS = ("(function(){try{return typeof window.WH_DEBUG==='object' && "
            "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
            "!!window.WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()")


def new_page(browser, console_errors, page_errors, responses):
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("console", lambda m: console_errors.append(m.text)
            if m.type == "error" else None)
    page.on("response", lambda r: responses.append({"url": r.url, "s": r.status})
            if r.status >= 400 else None)
    page.add_init_script(INIT_SCRIPT)
    return page


def load_index(page):
    page.goto(BASE_ROOT, wait_until="load", timeout=30000)
    deadline = time.time() + 20.0
    while time.time() < deadline:
        try:
            if page.evaluate(READY_JS):
                page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        page.wait_for_timeout(250)
    print("[diag] WH_DEBUG never ready")
    return False