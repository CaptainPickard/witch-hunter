

# ------------------------------------------------------------ AC-P5 --------
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# real-assignment law (R2 part10): key-ish word '=' >=8 class chars.
ASSIGN_RE = re.compile(r"(api[_-]?key|apikey|secret|password|token)"
                       r"\s*=\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
MESHY_RE = re.compile(r"msy_[A-Za-z0-9]{8}")
GAME_WINDOWS = [(29, 41), (940, 947)]     # setupRenderer(+helper) / resize
CONFIG_WINDOW = (7, 14)
CONFIG_KEEP = ["outputColorSpaceSRGB: true,", "toneMappingName: 'Neutral',",
               "toneMappingExposure: 1.15,", "maxPixelRatio: 2,",
               "shadowMapEnabled: false"]
CSS_ADD = ["  image-rendering: pixelated;", "  image-rendering: crisp-edges;"]


def hunks(path):
    """[(old_start, old_len, added[], removed[])] vs BASE_COMMIT."""
    out = []
    for ln in git("diff", "-U0", BASE_COMMIT, "--", path).splitlines():
        m = HUNK_RE.match(ln)
        if m:
            ol = int(m.group(2)) if m.group(2) is not None else 1
            out.append([int(m.group(1)), ol, [], []])
        elif out and ln.startswith("+") and not ln.startswith("+++"):
            out[-1][2].append(ln[1:])
        elif out and ln.startswith("-") and not ln.startswith("---"):
            out[-1][3].append(ln[1:])
    return out


def _within(h, windows):
    lo = h[0]
    hi = h[0] + max(h[1], 1) - 1
    return any(a <= lo and hi <= b for a, b in windows)


def style_hunk_exact():
    hs = hunks("prototype/style.css")
    if len(hs) != 1 or hs[0][3] or hs[0][2] != CSS_ADD:
        return False, "hunks=%s" % hs
    src = open(os.path.join(REPO_ROOT, "prototype/style.css")).read()
    m = re.search(r"#wh-canvas\s*\{([^}]*)\}", src)
    body = m.group(1) if m else ""
    ok = (CSS_ADD[0] in body and CSS_ADD[1] in body
          and body.index(CSS_ADD[0]) < body.index(CSS_ADD[1]))
    return ok, "insert@old%d inRule=%s" % (hs[0][0], ok)


def changed_paths():
    dirty = []
    for line in git("status", "--porcelain", "--untracked-files=all"
                    ).splitlines():
        p = line[3:].strip().strip('"')     # R1 A8 leading-3-char strip
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        dirty.append(p)
    committed = [p for p in git("diff", "--name-only", BASE_COMMIT, "HEAD",
                                "--", "prototype", "tests").splitlines() if p]
    gate_docs = [p for p in git("diff", "--name-only", BASE_COMMIT, "HEAD"
                                ).splitlines() if p and p not in committed]
    return dirty, committed, gate_docs


def secrets_scan():
    """git diff vs base (tracked) + content of untracked new files."""
    txt = git("diff", BASE_COMMIT)
    for p in git("ls-files", "--others", "--exclude-standard").splitlines():
        try:
            with open(os.path.join(REPO_ROOT, p), errors="replace") as f:
                txt += f.read()
        except Exception:
            pass
    return (len(MESHY_RE.findall(txt)) + len(ASSIGN_RE.findall(txt)))


def v7_rebuild_clean(browser):
    """A8: rebuild on a temp copy; load result; 0 console/page errors."""
    root = tmp_tree(src_prototype=os.path.join(REPO_ROOT, "prototype"))
    proc = None
    try:
        b = subprocess.run([sys.executable, "tools/build_v7.py"], cwd=root,
                           capture_output=True, text=True, timeout=180)
        if b.returncode != 0:
            return False, "build rc=%d %s" % (b.returncode, b.stderr[-200:])
        proc, base = spawn_server(root)
        if not base:
            return False, "temp server failed"
        errs = {"console": [], "page": [], "resp": []}
        ctx, pg = new_page(browser, errs)
        try:
            ready = load_index(pg, base, "builds/v7-playable.html")
        finally:
            ctx.close()
        ok = ready and not errs["console"] and not errs["page"]
        return ok, "ready=%s consoleErr=%d pageErr=%d" % (
            ready, len(errs["console"]), len(errs["page"]))
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)
