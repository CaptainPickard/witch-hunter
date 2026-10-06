#!/usr/bin/env python3
"""Atomic release-dir refresh for the 8793 playtest surface.

Pattern: /tmp/wh-playtest-share/releases/<sha>/ are full git checkouts
(never touched while serving). /tmp/wh-playtest-share/current is a symlink
-> releases/<sha>. A refresh builds the NEW sha's release dir, then flips
the symlink with a single rename(2) INSIDE the share. Serving never sees a
half-written tree.

The wh-playtest-8793 container binds /tmp/wh-playtest-share:/srv:ro.

Disk law (2026-10-06): every release is a full checkout (~4-6GB incl.
artifact .git blobs). Releases accumulate at ~5GB per publish; only the
current one is sacred. flip() auto-prunes every OTHER release after a
successful flip (keeps disk flat forever). Pass --keep-old to disable
pruning entirely.
"""
import subprocess, os, sys, json

SHARE = '/tmp/wh-playtest-share'
RELEASES = os.path.join(SHARE, 'releases')
CURRENT = os.path.join(SHARE, 'current')   # symlink inside the share
REPO = 'https://github.com/CaptainPickard/witch-hunter.git'
BRANCH = 'feat/world-visuals'


def sh(cmd, **kw):
    return subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, **kw)


def current_release_sha():
    target = os.path.realpath(CURRENT)
    if os.path.isdir(target):
        r = sh(f"git -C {target} rev-parse HEAD")
        return r.stdout.strip()
    return None


def release_for(sha):
    sha = (sha or '').strip()
    if not sha or '/' in sha or sha in ('.', '..') or sha.startswith('-'):
        print('BAD_SHA', repr(sha))
        return None, False
    d = os.path.join(RELEASES, sha)
    if os.path.isdir(os.path.join(d, '.git')) or os.path.isdir(os.path.join(d, 'prototype')):
        return d, True
    r = sh(f"git clone --quiet --no-checkout --filter=blob:none --sparse {REPO} {d} && "
           f"rm -f {d}/.git/index.lock && "
           f"git -C {d} sparse-checkout set prototype art-direction && "
           f"git -C {d} fetch --quiet origin {BRANCH} && git -C {d} checkout --quiet --detach {sha}")
    if r.returncode != 0:
        print('CLONE_ERR', r.stderr[-400:])
        return None, False
    return d, False


def prune_old_releases(keep_sha, dry_run=False):
    """After a successful flip, every release dir except keep_sha is
    disposable (each is ~4-6GB and re-creatable from GitHub). Removes them;
    returns the list of removed/pending dir names."""
    removed = []
    if not os.path.isdir(RELEASES):
        return removed
    for name in sorted(os.listdir(RELEASES)):
        if name == keep_sha:
            continue
        d = os.path.join(RELEASES, name)
        if os.path.isdir(d):
            removed.append(name)
    if dry_run:
        return [f'DRY {x}' for x in removed]
    for name in list(removed):
        sh(f"rm -rf {os.path.join(RELEASES, name)}")
    return removed


def flip(sha, keep_old=False, dry_run=False):
    d, existed = release_for(sha)
    if not d:
        return False
    if not dry_run:
        tmp = CURRENT + '.tmp'
        if os.path.lexists(tmp):
            os.remove(tmp)
        # RELATIVE target (fix 2026-10-06): an absolute /tmp/... target resolves
        # on the host but NOT inside the wh-playtest-8793 container bind
        # (dangling /srv symlink = 404 mass). releases/<sha> is stable forever.
        os.symlink(os.path.join('releases', sha), tmp)
        os.rename(tmp, CURRENT)          # atomic flip
    pruned = None if keep_old else prune_old_releases(sha, dry_run=dry_run)
    print(json.dumps({'flipped_to': sha, 'release_dir': d,
                      'reused_existing_release': existed,
                      'pruned': pruned, 'dry_run': dry_run}))
    return True


if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    keep_old = '--keep-old' in args
    dry_run = '--dry-run' in args
    args = [a for a in args if not a.startswith('--')]
    sha = args[0] if args else None
    if not sha:
        print('BAD_SHA', repr(sha), '- pass the release sha explicitly')
        sys.exit(2)
    if sha == 'HEAD':
        sha = current_release_sha()
    if not sha or set(sha.lower()) - set('0123456789abcdef') or len(sha) < 7:
        print('BAD_SHA', repr(sha), '- pass the release sha explicitly')
        sys.exit(2)
    ok = flip(sha, keep_old=keep_old, dry_run=dry_run)
    sys.exit(0 if ok else 1)