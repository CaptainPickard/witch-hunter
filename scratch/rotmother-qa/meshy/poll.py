import json, sys, time, urllib.request
key = open('/home/hermeswebui/.hermes/profiles/io/secrets/meshy_key').read().strip()
tid = sys.argv[1]
while True:
    req = urllib.request.Request('https://api.meshy.ai/openapi/v2/text-to-3d/'+tid, headers={'Authorization':'Bearer '+key})
    t = json.loads(urllib.request.urlopen(req, timeout=60).read())
    print(time.strftime('%H:%M:%S'), t.get('status'), t.get('progress'), flush=True)
    if t.get('status') in ('SUCCEEDED','FAILED','CANCELED','EXPIRED'):
        json.dump(t, open(sys.argv[2],'w'), indent=1); break
    time.sleep(20)
