"""Direct CDP driver for Mixamo automation (browser-harness daemon is down)."""
import json, urllib.request, websocket, time

CDP = "http://127.0.0.1:9222"

def _tabs():
    req = urllib.request.Request(CDP + "/json", headers={"User-Agent": "io-agent/1.0"})
    tabs = json.loads(urllib.request.urlopen(req, timeout=10).read())
    return [t for t in tabs if t.get("type") == "page"]

def get_tab(create_if_none=True, url="about:blank"):
    tabs = _tabs()
    if not tabs:
        if not create_if_none:
            raise RuntimeError("no page tabs")
        urllib.request.urlopen(CDP + "/json/new?url=" + urllib.parse.quote(url), timeout=10).read()
        time.sleep(1.5)
        tabs = _tabs()
    return tabs[0]

class Page:
    def __init__(self, tab):
        self.tab = tab
        self.ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        self._id = 0

    def send(self, method, **params):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        deadline = time.time() + 60
        while time.time() < deadline:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"]))
                return msg.get("result", {})
        raise TimeoutError(method)

    def eval_js(self, expr, await_promise=False):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True,
                      awaitPromise=await_promise, userGesture=True)
        val = r.get("result", {})
        if val.get("subtype") == "error":
            raise RuntimeError("JS: " + val.get("description", "err"))
        return val.get("value")

    def goto(self, url, wait=3.0):
        self.send("Page.navigate", url=url)
        time.sleep(wait)

    def url(self): return self.eval_js("location.href")
    def title(self): return self.eval_js("document.title")