#!/usr/bin/env python3
"""Static server for the Witch Hunter prototype.

Serves the whole witch-hunter repo root so that:
  - /            -> prototype/index.html
  - /js/...      -> prototype/js/...
  - /vendor/...  -> prototype/vendor/...
  - /art-direction/... -> GLB assets (absolute asset URLs work from any page)

Run: python3 server.py   (port 8791, bind 0.0.0.0)
"""
import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
PORT = 8791

# / maps to prototype/ so the page URL is simply http://host:8791/
PROTO_SUBPATH = "prototype"


class WHHandler(SimpleHTTPRequestHandler):
    translate_path = None  # set below; keeps linters quiet about attribute origin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        # Strip query/fragment, split, remap '' -> prototype/
        path = path.split("?", 1)[0].split("#", 1)[0]
        parts = [p for p in path.split("/") if p not in ("", ".")]
        if not parts:
            parts = ["index.html"]
        if parts[0] == PROTO_SUBPATH:
            parts = parts[1:]
        if not parts:
            parts = ["index.html"]
        elif parts[0] in ("index.html", "style.css", "js", "vendor", "builds", "README.md", "server.py"):
            parts = [PROTO_SUBPATH] + parts
        return os.path.join(ROOT, *parts)

    def guess_type(self, path):
        base = super().guess_type(path)
        if path.endswith(".glb"):
            return "model/gltf-binary"
        if path.endswith(".js") and base in ("text/plain", "application/octet-stream", None):
            return "text/javascript"
        return base

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    server = ThreadingHTTPServer(("0.0.0.0", port), WHHandler)
    print("Serving %s at http://0.0.0.0:%d/ (prototype entry)" % (ROOT, port))
    server.serve_forever()


if __name__ == "__main__":
    main()