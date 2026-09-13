#!/usr/bin/env python3
"""Vision QA for sprite/concept frames against the art bible register.

Sends an image (plus a QA prompt) to gemma4:31b via Ollama Cloud
(https://ollama.com/api/chat, NDJSON streaming) and prints the model's
verdict. The API key is read from the IO profile .env (OLLAMA_API_KEY)
or the OLLAMA_API_KEY environment variable; never printed.

Usage:
  python3 vision_qa.py IMAGE_PATH "QA prompt text" [--out verdict.txt]

The default QA prompt embeds the bible section 7 checklist. Pass a
custom prompt to ask a different question (turnaround checks, etc.).
"""
import sys, os, json, base64, urllib.request

DEFAULT_PROMPT = """QA this dark-fantasy character concept frame against a locked art register. This is a CHARACTER FEATURE frame: the figure is the subject and may be small-to-mid scale (not a distant establishing shot). Answer as a terse checklist, then a final verdict line "VERDICT: PASS" or "VERDICT: FAIL - reason".
1. Negative space: at least half the frame near-black, fog, or dim environment?
2. Single clear subject; no clutter of extra figures or busy scene detail?
3. EXACTLY ONE accent color family (e.g. one ember/fire/moon glow); a second warm source is a FAIL?
4. Dithering and film grain visibly present; painterly pixel-art hybrid style, never photoreal?
5. Backlit rim light on the silhouette; light sources diegetic (lantern, torch, moon, fire, glow)?
6. No text, no UI, no watermark, no pastel colors?
7. Mood: somber, ominous, quiet menace - atmospheric rather than loud poster energy?"""


def load_key():
    key = os.environ.get('OLLAMA_API_KEY')
    if key:
        return key
    env_path = '/home/hermeswebui/.hermes/profiles/io/.env'
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('OLLAMA_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise SystemExit('OLLAMA_API_KEY not found')


def qa(image_path, prompt=None, timeout=180):
    prompt = prompt or DEFAULT_PROMPT
    with open(image_path, 'rb') as fp:
        img_b64 = base64.b64encode(fp.read()).decode()
    key = load_key()
    body = json.dumps({
        'model': 'gemma4:31b',
        'messages': [{'role': 'user', 'content': prompt, 'images': [img_b64]}],
        'stream': True,
    }).encode()
    req = urllib.request.Request('https://ollama.com/api/chat', data=body,
        headers={'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + key})
    chunks = []
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for line in resp:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            c = obj.get('message', {}).get('content', '')
            if c:
                chunks.append(c)
            if obj.get('done'):
                break
    return ''.join(chunks)


if __name__ == '__main__':
    img = sys.argv[1]
    prompt = None
    if len(sys.argv) > 2 and sys.argv[2] != '--out':
        prompt = sys.argv[2]
    out = None
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    print('QA target:', img)
    verdict = qa(img, prompt)
    print(verdict)
    if out:
        with open(out, 'w') as fp:
            fp.write(verdict)
        print('saved:', out)