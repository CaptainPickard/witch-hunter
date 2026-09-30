"""Generate npm lock v3 from registry metadata without running Node/npm on this VPS.

This build-time helper is not part of the e2e execution path. Regenerate on a
Node-enabled machine with `npm install --package-lock-only` if npm rejects it.
"""
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from semantic_version import Version, NpmSpec

root = Path(__file__).resolve().parent
pkg = json.loads((root / 'package.json').read_text())
meta_cache = {}

def metadata(name):
    if name not in meta_cache:
        with urlopen('https://registry.npmjs.org/' + quote(name, safe=''), timeout=45) as response:
            meta_cache[name] = json.load(response)
    return meta_cache[name]

def satisfy(version, spec):
    if spec.startswith(('npm:', 'file:', 'git:', 'http:', 'workspace:')):
        raise ValueError((version, spec))
    if spec in ('*', 'latest'):
        return True
    try:
        return Version.coerce(version) in NpmSpec(spec)
    except ValueError:
        return version == spec

def choose(name, spec):
    versions = metadata(name)['versions']
    matches = [v for v in versions if '-' not in v and satisfy(v, spec)]
    if not matches:
        raise ValueError((name, spec))
    return max(matches, key=Version.coerce)

packages = {'': {
    'name': pkg['name'], 'version': pkg['version'],
    'dependencies': pkg['dependencies'], 'devDependencies': pkg['devDependencies'],
    'engines': pkg['engines'],
}}
queue = [(name, spec, '', name in pkg['devDependencies']) for group in ('dependencies', 'devDependencies') for name, spec in pkg[group].items()]
while queue:
    name, spec, parent, dev = queue.pop(0)
    path = 'node_modules/' + name
    if path in packages and satisfy(packages[path]['version'], spec):
        if not dev:
            packages[path].pop('dev', None)
        continue
    if path in packages:
        path = parent + '/node_modules/' + name
        if path in packages and satisfy(packages[path]['version'], spec):
            if not dev:
                packages[path].pop('dev', None)
            continue
    version = choose(name, spec)
    info = metadata(name)['versions'][version]
    record = {
        'version': version,
        'resolved': info['dist']['tarball'],
        'integrity': info['dist']['integrity'],
    }
    if info.get('dependencies'):
        record['dependencies'] = info['dependencies']
    if info.get('optionalDependencies'):
        record['optionalDependencies'] = info['optionalDependencies']
    if info.get('peerDependencies'):
        record['peerDependencies'] = info['peerDependencies']
    if info.get('peerDependenciesMeta'):
        record['peerDependenciesMeta'] = info['peerDependenciesMeta']
    if info.get('bin'):
        record['bin'] = info['bin']
    if info.get('engines'):
        record['engines'] = info['engines']
    if info.get('os'):
        record['os'] = info['os']
    if info.get('cpu'):
        record['cpu'] = info['cpu']
    if dev:
        record['dev'] = True
    packages[path] = record
    print(path, version, flush=True)
    for dependency, required in info.get('dependencies', {}).items():
        queue.append((dependency, required, path, dev))
    for dependency, required in info.get('optionalDependencies', {}).items():
        queue.append((dependency, required, path, dev))
lock = {'name': pkg['name'], 'version': pkg['version'], 'lockfileVersion': 3, 'requires': True, 'packages': dict(sorted(packages.items()))}
(root / 'package-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
print('package count', len(packages))
