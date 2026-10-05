#!/usr/bin/env python3
"""assets.js structural fix: the union duplicated a fragment of old dev
loadOne inside what became loadAttempt. Re-cut into intended shape:

A) module scope: embeddedDataUris map (BEFORE both loader functions)
B) loadAttempt: new attempt-factory WITHOUT loader internals; the factory
   builds loader per attempt and applies the CSP plugin registration,
   then does load with done/timer race (dev's logic) resolving {ok,gltf}
C) loadOne: feat's retry/settle/progress wrapper (unchanged)
"""
p = '/workspace/witch-hunter/prototype/js/assets.js'
src = open(p).read()

# 1) Remove the WRONG embedded machinery currently fused in loadOne (lines
#    with the whole old-union loadOne): everything from
#    "  // The manager modifier is synchronous" to the line just before
#    "  // One load attempt, racing"
a = src.index("  // The manager modifier is synchronous; populate it before the parser starts")
b = src.index("  // One load attempt, racing the per-attempt timeout.")
src = src[:a] + src[b:]

# 2) The machinery, re-indented at module scope, INSERTED before loadAttempt:
machinery = '''  // CSP-safe embedded-texture intake (whanim3, 8f777bb): the manager
  // modifier is synchronous; populate it before the parser starts resolving
  // texture URLs. GLB image bufferViews are converted only once.
  var embeddedDataUris = new Map();
  var imageUrls = [];

  function registerEmbeddedImagePlugin(loader, mgr) {
    // CSP forbids even an attempted fetch(blob:) on enforced origins. Read
    // the RESPONSE POLICY, not the route name, before choosing the path.
    if (!registerEmbeddedImagePlugin.blobPolicy) {
      registerEmbeddedImagePlugin.blobPolicy =
        fetch(document.baseURI, { credentials: 'same-origin' })
          .then(function (response) {
            var csp = response.headers.get('content-security-policy');
            if (!csp) return true;
            var match = csp.match(/(?:^|;)\\s*connect-src\\s+([^;]+)/i);
            return !match || /(?:^|\\s)blob:(?:\\s|$)/i.test(match[1]);
          }).catch(function (err) {
            console.warn('[WH assets] cannot inspect CSP; using FileReader for embedded images:', err);
            return false;
          });
    }
    function asDataUri(blob) {
      return new Promise(function (accept, reject) {
        var reader = new FileReader();
        reader.onload = function () { accept(reader.result); };
        reader.onerror = function () { reject(reader.error || new Error('image FileReader failed')); };
        reader.readAsDataURL(blob);
      });
    }
    function releaseAll() {
      imageUrls.forEach(function (u) {
        URL.revokeObjectURL(u);
        embeddedDataUris.delete(u);
      });
      imageUrls.length = 0;
    }
    mgr.setURLModifier(function (resourceUrl) {
      return resourceUrl.indexOf('blob:') === 0 && embeddedDataUris.has(resourceUrl) ?
        embeddedDataUris.get(resourceUrl) : resourceUrl;
    });
    loader.register(function (parser) {
      return {
        name: 'WH_embedded_image_data',
        beforeRoot: function () {
          var sources = parser.json.images || [];
          return registerEmbeddedImagePlugin.blobPolicy.then(function (canFetchBlob) {
            // ImageBitmapLoader decodes via fetch(data:), also forbidden by
            // connect-src on CSP origins. ImageLoader uses img-src instead.
            if (!canFetchBlob) parser.textureLoader = new THREE.TextureLoader(mgr);
            return Promise.all(sources.map(function (source) {
              if (source.bufferView === undefined || !/^image\\//.test(source.mimeType || '')) {
                return Promise.resolve();
              }
              return parser.getDependency('bufferView', source.bufferView).then(function (bytes) {
                var blob = new Blob([bytes], { type: source.mimeType });
                var imageUrl = URL.createObjectURL(blob);
                imageUrls.push(imageUrl);
                var conversion = canFetchBlob ?
                  fetch(imageUrl).then(function (response) {
                    if (!response.ok) throw new Error('image fetch status ' + response.status);
                    return response.blob();
                  }).then(asDataUri).catch(function () { return asDataUri(blob); }) :
                  asDataUri(blob);
                return conversion.then(function (dataUri) {
                  embeddedDataUris.set(imageUrl, dataUri);
                  source.uri = imageUrl;
                  delete source.bufferView;
                });
              });
            }));
          }).catch(function (err) {
            releaseAll();
            throw err;
          });
        },
        afterRoot: function () { releaseAll(); }
      };
    });
  }

'''
anchor = "  // One load attempt, racing the per-attempt timeout."
assert src.count(anchor) == 1
src = src.replace(anchor, machinery + anchor, 1)

open(p, 'w').write(src)
print("machinery hoisted to module scope")

# 3) loadAttempt: strip the manager/loader lines (the factory that CALLS it
#    owns loader creation and plugin registration).
bad_head = """  function loadAttempt(name, url) {
    return new Promise(function (resolve) {
      var mgr = new THREE.LoadingManager();
      var loader = new window.WHGLTFLoader(mgr);
      var settled = false;"""
good_head = """  function loadAttempt(name, url) {
    return new Promise(function (resolve) {
      var settled = false;"""
assert bad_head in src, "loadAttempt head anchor missing"
src = src.replace(bad_head, good_head, 1)

# 4) insert loader creation + plugin registration inside the timer callback
#    position (before loader.load), using the timeoutMs guard
old_load = """  function loadAttempt(name, url) {
    return new Promise(function (resolve) {
      var settled = false;
      var timer = setTimeout(function () {"""
new_load = """  function loadAttempt(name, url) {
    return new Promise(function (resolve) {
      var settled = false;
      var mgr = new THREE.LoadingManager();
      var loader = new window.WHGLTFLoader(mgr);
      registerEmbeddedImagePlugin(loader, mgr);
      var timer = setTimeout(function () {"""
assert old_load in src, "timer anchor missing"
src = src.replace(old_load, new_load, 1)
open(p, 'w').write(src)
print("loadAttempt restructured")
# sanity
import re
assert 'registerEmbeddedImagePlugin' in src
assert src.count('function loadOne') == 1
print("OK")