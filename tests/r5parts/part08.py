

# ------------------------------------------------------------ AC-PRES ------
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# real-assignment law (R2 part10): key-ish word '=' >=8 class chars.
ASSIGN_RE = re.compile(r"(api[_-]?key|apikey|secret|password|token)"
                       r"\s*=\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
MESHY_RE = re.compile(r"msy_[A-Za-z0-9]{8}")
# Sanctioned windows in BASE_COMMIT line numbers (valspec AC-PRES hunk law;
# insert windows allow +-1 for git's blank/brace-line slide ambiguity).
WINDOWS = {
    "prototype/js/CONFIG.js": [(59, 73),        # world {} (playerMargin + visual keys)
                               (86, 86),        # regionA.enemies ghoul
                               (270, 279)],     # player camera keys (C1)
    "prototype/js/region-manager.js": [
        (99, 113),                              # clampPlayer
        (116, 135),                             # clampEnemyToHomeSide + adjacent helpers
        (251, 255),                             # ground repeat :253
        (272, 276),                             # live wrapper + adjacent helpers
        (296, 298),                             # ground disc :297
        (315, 317)],                            # mist size
    "prototype/js/game.js": [(467, 478)],       # clampPlayerToBounds
    "prototype/js/player.js": [(896, 947)],     # updateCamera (C13)
}


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


def _block(src, start, end):
    i = src.find(start)
    return src[i:src.index(end, i) + len(end)] if i >= 0 else None


def classify_hunks():
    """Every hunk of every allowed proto file classified in/out of window."""
    rows, foreign = [], []
    for path, wins in WINDOWS.items():
        for h in hunks(path):
            ok = _within(h, wins)
            rows.append({"file": path.split("/")[-1], "old": [h[0], h[1]],
                         "add": len(h[2]), "rem": len(h[3]), "in": ok})
            if not ok:
                foreign.append("%s@%d,%d" % (path.split("/")[-1], h[0], h[1]))
    return rows, foreign


def player_invariants():
    """C13: wheel/mousemove/lock-on-framing bytes unchanged."""
    base = (git_blob(BASE_COMMIT, "prototype/js/player.js") or b"").decode()
    cur = open(os.path.join(REPO_ROOT, "prototype/js/player.js")).read()
    bad = []
    for start, end in (("document.addEventListener('mousemove'", "});"),
                       ("document.addEventListener('wheel'",
                        "{ passive: true });")):
        b = _block(base, start, end)
        if b is None or b != _block(cur, start, end):
            bad.append(start.split("'")[1])
    bl = base.splitlines()
    framing = "\n".join(bl[906:929]) if len(bl) >= 929 else None   # :907-929
    if not framing or framing not in cur:
        bad.append("lock-on framing :907-929")
    return bad


def config_invariants():
    base = (git_blob(BASE_COMMIT, "prototype/js/CONFIG.js") or b"").decode()
    cur = _worktree_config().decode()
    bad = []
    for k in ("regionA", "regionB"):
        if props_block(base, k) is None or props_block(base, k) != \
                props_block(cur, k):
            bad.append("%s.props" % k)
    for start in ("  renderer: {", "  lighting: {", "  lightPool: {",
                  "  assets: {"):
        if _block(base, start, "\n  }") != _block(cur, start, "\n  }"):
            bad.append(start.strip())
    return bad


def changed_paths():
    dirty = []
    for line in git("status", "--porcelain", "--untracked-files=all"
                    ).splitlines():
        p = line[3:].strip().strip('"')     # R1 A8 leading-3-char strip
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        dirty.append(p)
    committed = [p for p in git("diff", "--name-only", BASE_COMMIT, "HEAD"
                                ).splitlines() if p]
    return dirty, committed


def secrets_scan():
    """git diff vs base (tracked) + content of untracked new files."""
    txt = git("diff", BASE_COMMIT)
    for p in git("ls-files", "--others", "--exclude-standard").splitlines():
        if p.endswith(".png"):
            continue
        try:
            with open(os.path.join(REPO_ROOT, p), errors="replace") as f:
                txt += f.read()
        except Exception:
            pass
    return (len(MESHY_RE.findall(txt)) + len(ASSIGN_RE.findall(txt)))


def tmp_tree(src_prototype=None, archive_rev=None):
    """Temp repo-shaped root: prototype/ (worktree copy or git archive of
    archive_rev) + tools/build_v7.py; other top-level entries symlinked."""
    root = tempfile.mkdtemp(prefix="whr5_")
    if archive_rev:
        arc = subprocess.run(["git", "archive", archive_rev, "prototype"],
                             cwd=REPO_ROOT, capture_output=True, timeout=120)
        subprocess.run(["tar", "-x", "-C", root], input=arc.stdout,
                       capture_output=True, timeout=120)
    else:
        shutil.copytree(src_prototype, os.path.join(root, "prototype"),
                        ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(root, "tools"))
    shutil.copy(os.path.join(REPO_ROOT, "tools", "build_v7.py"),
                os.path.join(root, "tools", "build_v7.py"))
    for ent in os.listdir(REPO_ROOT):
        if ent in ("prototype", "tools", ".git"):
            continue
        os.symlink(os.path.join(REPO_ROOT, ent), os.path.join(root, ent))
    return root


def v7_rebuild_clean(browser):
    """R3 A8: rebuild on a temp copy; load result; 0 console/page errors."""
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
        errs = new_errs()
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


def unchanged_since_base(path):
    return not git("diff", "--name-only", BASE_COMMIT, "--", path).strip()


def assets_blob():
    cur = subprocess.run(["git", "hash-object", "prototype/js/assets.js"],
                         cwd=REPO_ROOT, capture_output=True, text=True,
                         timeout=30).stdout.strip()
    base = git("rev-parse", "%s:prototype/js/assets.js" % BASE_COMMIT).strip()
    return cur, base


def ac_pres(browser):
    dirty, committed = changed_paths()
    allp = sorted(set(dirty + committed))
    resid = [p for p in allp if not in_surface(p)]
    other_proto = [p for p in allp if p.startswith("prototype/")
                   and p not in PROTO_ALLOWED]
    rows, foreign = classify_hunks()
    p_bad = player_invariants()
    c_bad = config_invariants()
    a_cur, a_base = assets_blob()
    a_ok = a_cur == a_base and a_cur.startswith(ASSETS_BLOB_PREFIX)
    rig_dirty = [p for p in allp if p.startswith(RIGGED_DIR)]
    idx = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    i_ok = idx == INDEX_FREEZE_SHA256
    v_ok, v_ev = v7_rebuild_clean(browser)
    builds_dirty = [p for p in dirty if p.startswith("prototype/builds/")]
    nsec = secrets_scan()
    added = [a for p in PROTO_ALLOWED for h in hunks(p) for a in h[2]]
    free_hits = [a for a in added if re.search(r"\bfree\b", a, re.I)]
    ok = (not resid and not other_proto and not foreign and not p_bad
          and not c_bad and a_ok and not rig_dirty and i_ok and v_ok
          and not builds_dirty and nsec == 0 and not free_hits)
    ev = ("resid=%s otherProto=%s foreignHunks=%s playerInv=%s configInv=%s "
          "assetsBlob=%s(base %s) rigDirty=%s index=%s v7=%s(%s) "
          "buildsDirty=%s secretsHits=%d freeHits=%d changedSinceBase=%d "
          "hunks=%s" % (resid, other_proto, foreign, p_bad, c_bad, a_cur[:12],
                        a_base[:12], rig_dirty,
                        "freeze-ok" if i_ok else "DRIFT:" + idx[:12], v_ok,
                        v_ev, builds_dirty, nsec, len(free_hits), len(allp),
                        json.dumps(rows)))
    blockish = (resid or other_proto or foreign or rig_dirty or not a_ok
                or not i_ok or nsec)
    check("PRES", "preservation surface", ok, ev,
          verdict=None if ok else ("BLOCK" if blockish else "FAIL"))
