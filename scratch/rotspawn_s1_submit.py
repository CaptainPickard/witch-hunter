"""Meshy image-to-3d submit for the Rot Spawn ref (attempt S1, ~2000 polys)."""
import json, subprocess, sys

KEY = open('/home/hermeswebui/.hermes/profiles/io/secrets/meshy_key').read().strip()
REF = sys.argv[1] if len(sys.argv) > 1 else 'https://raw.githubusercontent.com/CaptainPickard/witch-hunter/feat/world-visuals/scratch/rotmother-qa2/spawn_ref_c1.png'
POLY = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
payload = {
    'image_url': REF,
    'ai_model': 'meshy-5',
    'target_polycount': POLY,
    'topology': 'triangle',
    'should_remesh': True,
}
out = subprocess.run(
    ['curl', '-s', '-X', 'POST', 'https://api.meshy.ai/openapi/v1/image-to-3d',
     '-H', f'Authorization: Bearer {KEY}',
     '-H', 'Content-Type: application/json',
     '-d', json.dumps(payload)],
    capture_output=True, text=True, timeout=120)
print('HTTP body:', out.stdout[:400])