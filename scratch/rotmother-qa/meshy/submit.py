import json, sys, urllib.request, urllib.error
key = open('/home/hermeswebui/.hermes/profiles/io/secrets/meshy_key').read().strip()
body = json.load(open(sys.argv[1]))
req = urllib.request.Request('https://api.meshy.ai/openapi/v2/text-to-3d', data=json.dumps(body).encode(),
    headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'}, method='POST')
try:
    r = urllib.request.urlopen(req, timeout=60); print(r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP', e.code, repr(e.read().decode()))
