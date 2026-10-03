

# ------------------------------------------------- server + page plumbing ----
def _served_config(base):
    with urllib.request.urlopen(base.rstrip("/") + "/js/CONFIG.js",
                                timeout=2.0) as r:
        return r.read()


def _identity_ok(base):
    """Law 5 + R3 signature + A1 byte equality: the served CONFIG.js must
    carry lightPool, ambientIntensity 0, internalResDiv AND equal the
    worktree's prototype/js/CONFIG.js byte-for-byte."""
    if (":%d" % FORBIDDEN_PORT) in base:
        return False            # never touch the landed-work server
    try:
        src = _served_config(base)
        with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js"),
                  "rb") as f:
            mine = f.read()
        return (b"lightPool" in src and b"ambientIntensity: 0" in src
                and b"internalResDiv" in src and src == mine)
    except Exception:
        return False


def _free_port():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    p = sock.getsockname()[1]
    sock.close()
    return p


def spawn_server(root, port=0, ident=None):
    """Spawn <root>/prototype/server.py on port (0 = ephemeral); poll until
    ident(base) (default: HTTP 200). Returns (proc, base) or (proc, None)."""
    port = port or _free_port()
    if port == FORBIDDEN_PORT:
        port = _free_port()
    base = "http://localhost:%d/" % port
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py", str(port)],
            cwd=os.path.join(root, "prototype"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        print("[diag] server spawn failed %r" % e)
        return None, None
    deadline = time.time() + 15.0
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        try:
            if ident is not None:
                if ident(base):
                    return proc, base
            else:
                with urllib.request.urlopen(base, timeout=1.0) as r:
                    if r.status == 200:
                        return proc, base
        except Exception:
            pass
        time.sleep(0.3)
    print("[diag] server on %d never came up" % port)
    return proc, None


def start_server():
    """Reuse WH_BASE_ROOT only with full identity (A1); else self-spawn
    from REPO_ROOT on WH_W3_PORT / ephemeral. Returns (proc, how)."""
    global BASE_ROOT, PORT
    if BASE_ROOT and _identity_ok(BASE_ROOT):
        return None, "reused %s" % BASE_ROOT
    refused = BASE_ROOT or "none"
    proc, base = spawn_server(REPO_ROOT, PORT, ident=_identity_ok)
    if base:
        BASE_ROOT = base
        PORT = int(base.rsplit(":", 1)[1].strip("/"))
        return proc, "reuse-refused(%s) self-spawn port %d" % (refused, PORT)
    return proc, "self-spawn FAILED"


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


READY_JS = ("(function(){try{return typeof window.WH_DEBUG==='object' && "
            "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
            "!!window.WH_DEBUG.getPlayerPosition() && !!window.WH_GAME && "
            "!!window.WH_GAME.renderer;}catch(e){return false;}})()")

FRAMES_JS = ("function(n){return new Promise(function(res){var k=n;"
             "function f(){if(--k<=0)res(true);else requestAnimationFrame(f);}"
             "requestAnimationFrame(f);});}")


def wait_frames(page, n):
    """Wall-generous rAF wait (law 1: SwiftShader 1-3fps)."""
    page.evaluate(FRAMES_JS, n)


def new_page(ctx_owner, errs, dsf=1):
    """errs = {'console':[], 'page':[], 'resp':[]}. Returns (ctx, page)."""
    ctx = ctx_owner.new_context(viewport={"width": VIEW_W, "height": VIEW_H},
                                device_scale_factor=dsf)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errs["page"].append(str(e)))
    page.on("console", lambda m: errs["console"].append(m.text)
            if m.type == "error" else None)
    page.on("response", lambda r: errs["resp"].append(
        {"url": r.url, "s": r.status}) if r.status >= 400 else None)
    return ctx, page


def load_index(page, base=None, path=""):
    page.goto((base or BASE_ROOT) + path, wait_until="load", timeout=60000)
    deadline = time.time() + 40.0
    while time.time() < deadline:
        try:
            if page.evaluate(READY_JS):
                page.wait_for_timeout(1500)
                wait_frames(page, 6)     # law 3: camera settle at spawn
                return True
        except Exception:
            pass
        page.wait_for_timeout(250)
    print("[diag] WH_DEBUG never ready")
    return False
