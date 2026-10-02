

# ------------------------------------------------------------ AC-PRES ------
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# real-assignment law (R2 part10): key-ish word '=' >=8 class chars.
ASSIGN_RE = re.compile(r"(api[_-]?key|apikey|secret|password|token)"
                       r"\s*=\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
MESHY_RE = re.compile(r"msy_[A-Za-z0-9]{8}")
CONFIG_WINDOW = (478, 481)                  # assets {} block at cce06eb
# assets.js windows at cce06eb: header comment, adjacent-to-MANIFEST table,
# adjacent swap helper (between prepTemplate and loadOne), loadOne success.
# Insert windows allow +-1 for git's blank/brace-line slide ambiguity.
ASSETS_WINDOWS = [(6, 7), (53, 56), (151, 154), (165, 179)]
ASSETS_FROZEN_FNS = ["resolveUrl", "makeStandIn", "groundAlign",
                     "prepTemplate", "preloadAll", "instance"]


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


def config_hunks_ok():
    """Only inside assets {}; pure additions = kill-switch comment +
    `pixelatedBodies: true`; timeoutMs/standInColor lines unchanged."""
    ch = hunks("prototype/js/CONFIG.js")
    added = [a for h in ch for a in h[2]]
    removed = [r for h in ch for r in h[3]]
    base = (git_blob(BASE_COMMIT, "prototype/js/CONFIG.js") or b"").decode()
    cur = open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")).read()
    blines = base.splitlines()
    keep = [blines[i - 1] for i in (479, 480)] if len(blines) >= 480 else []
    code = [a.strip() for a in added if not a.strip().startswith("//")]
    comments = [a for a in added if a.strip().startswith("//")]
    shape = (not ch) or (code in (["pixelatedBodies: true,"],
                                  ["pixelatedBodies: true"])
                         and any(re.search(r"kill[- ]?switch", c, re.I)
                                 for c in comments))
    ok = bool(all(_within(h, [CONFIG_WINDOW]) for h in ch)
              and not removed and shape and keep
              and all(k in cur.splitlines() for k in keep)
              and "timeoutMs" in keep[0] and "standInColor" in keep[1])
    return ok, [(h[0], h[1]) for h in ch]


def _fn_src(src, name):
    i = src.find("function %s(" % name)
    if i < 0:
        return None
    j, depth = src.index("{", i), 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[i:k + 1]
    return None


def _block(src, start, end):
    i = src.find(start)
    return src[i:src.index(end, i) + len(end)] if i >= 0 else None


def assets_hunks_ok():
    ah = hunks("prototype/js/assets.js")
    base = (git_blob(BASE_COMMIT, "prototype/js/assets.js") or b"").decode()
    cur = open(os.path.join(REPO_ROOT, "prototype/js/assets.js")).read()
    frozen = {n: (_fn_src(base, n) is not None
                  and _fn_src(base, n) == _fn_src(cur, n))
              for n in ASSETS_FROZEN_FNS}
    chars = [l for l in base.splitlines() if "var CHARACTERS" in l]
    frozen["CHARACTERS"] = bool(chars) and chars[0] in cur.splitlines()
    api = "window.WH_ASSETS = {"
    frozen["WH_ASSETS"] = (_block(base, api, "};") is not None
                           and _block(base, api, "};") == _block(cur, api,
                                                                 "};"))
    newfns = [a for h in ah for a in h[2]
              if re.search(r"^\s*function\s+\w+\s*\(", a)]
    # vacuous on the pre-Devbot tree (no hunks); post-Devbot R4-1 proves
    # the swap exists, this proves where it lives
    ok = (all(_within(h, ASSETS_WINDOWS) for h in ah)
          and all(frozen.values()) and len(newfns) <= 1)
    return ok, {"hunks": [(h[0], h[1]) for h in ah],
                "frozen_bad": [k for k, v in frozen.items() if not v],
                "new_fns": [f.strip()[:40] for f in newfns]}


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


def ac_pres(browser):
    dirty, committed = changed_paths()
    allp = sorted(set(dirty + committed))
    resid = [p for p in allp if not in_surface(p)]
    forbidden = [p for p in allp if p in FORBIDDEN_PROTO]
    other_proto = [p for p in allp if p.startswith("prototype/")
                   and p not in PRES_SURFACE[:5]]
    c_ok, c_h = config_hunks_ok()
    a_ok, a_ev = assets_hunks_ok()
    glb_dirty = [p for p in allp if p.startswith(RIGGED_DIR)
                 and p.endswith(".glb")]
    png_bad = [b for b in BODIES
               if sha256_bytes(git_blob(PNG_COMMIT, PNG_PATHS[b]) or b"")
               != sha256_file(os.path.join(REPO_ROOT, PNG_PATHS[b]))]
    idx = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    i_ok = idx == INDEX_FREEZE_SHA256
    i_base = unchanged_since_base("prototype/index.html")
    v_ok, v_ev = v7_rebuild_clean(browser)
    builds_dirty = [p for p in dirty if p.startswith("prototype/builds/")]
    nsec = secrets_scan()
    added = [a for p in PRES_SURFACE[:2] for h in hunks(p) for a in h[2]]
    free_hits = [a for a in added if re.search(r"\bfree\b", a, re.I)]
    ok = (not resid and not forbidden and not other_proto and c_ok and a_ok
          and not glb_dirty and not png_bad and i_ok and i_base and v_ok
          and not builds_dirty and nsec == 0 and not free_hits)
    ev = ("resid=%s forbidden=%s otherProto=%s configHunks=%s(%s) "
          "assetsHunks=%s(%s) glbDirty=%s pngRebake=%s index=%s(identToBase="
          "%s) v7=%s(%s) buildsDirty=%s secretsHits=%d freeHits=%d "
          "changedSinceBase=%d"
          % (resid, forbidden, other_proto, c_ok, c_h, a_ok, json.dumps(a_ev),
             glb_dirty, png_bad, "freeze-ok" if i_ok else "DRIFT:" + idx[:12],
             i_base, v_ok, v_ev, builds_dirty, nsec, len(free_hits),
             len(allp)))
    blockish = forbidden or other_proto or glb_dirty or not i_ok or nsec
    check("PRES", "preservation surface", ok, ev,
          verdict=None if ok else ("BLOCK" if blockish else "FAIL"))
