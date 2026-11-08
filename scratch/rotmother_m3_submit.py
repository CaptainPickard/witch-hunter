"""Meshy image-to-3d M3: ref_v6, should_remesh FALSE (raw poly output)."""
import json, subprocess

KEY = open('/home/hermeswebui/.hermes/profiles/io/secrets/meshy_key').read().strip()
REF = 'https://raw.githubusercontent.com/CaptainPickard/witch-hunter/feat/world-visuals/scratch/rotmother-qa2/ref_v6_34.png'
payload = {
    'image_url': REF,
    'ai_model': 'meshy-5',
    'topology': 'triangle',
    'should_remesh': False,
}
out = subprocess.run(
    ['curl', '-s', '-X', 'POST', 'https://api.meshy.ai/openapi/v1/image-to-3d',
     '-H', f'Authorization: Bearer {KEY}',
     '-H', 'Content-Type: application/json',
     '-d', json.dumps(payload)],
    capture_output=True, text=True, timeout=120)
print('HTTP body:', out.stdout[:400])