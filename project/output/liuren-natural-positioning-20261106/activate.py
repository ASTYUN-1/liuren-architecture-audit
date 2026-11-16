"""Install a fresh frozen runtime and switch only after the local checks passed."""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
B = read(OUT / 'before-manifest.json')
C = read(OUT / 'candidate-manifest.json')
p = read(OUT / 'candidate-active.json')
log = (OUT / 'preflight-tests.log').read_text(encoding='utf-8-sig')
assert 'pass 132' in log and 'fail 0' in log
assert sha(ROOT / '.opencode/liuren-active.json') == B['live']['.opencode/liuren-active.json']
assert sha(OUT / 'candidate-active.json') == C['activeSha256']
for base, entries in [(ROOT, C['live']), (ROOT / B['parentRuntime'], B['runtime']), (OUT / 'candidate-runtime', C['runtime'])]:
    for rel, digest in entries.items():
        assert sha(base / rel) == digest, rel
manifest = read(OUT / 'candidate-runtime/manifest.json')
assert manifest['release'] == p['release'] and manifest['version'] == p['methodVersion']
assert read(OUT / 'candidate-runtime' / manifest['shenshaPolicyFile'])['release'] == p['release']
assert p['eventPositioning']['semanticRoleChecks'] is False and p['eventPositioning']['actorReferenceRequired'] is False
wire = read(OUT / 'current-wire.json')
assert wire['exitCode'] == 0 and wire['realModelCalled'] is False and wire['loopbackOnlyProvider']
for rel, digest in wire['implementationSha256'].items():
    assert sha(ROOT / rel) == digest, rel
dest = (ROOT / p['runtime']).resolve()
assert dest.is_relative_to((ROOT / 'runtime/liuren').resolve()) and not dest.exists()
shutil.copytree(OUT / 'candidate-runtime', dest)
for rel, digest in C['runtime'].items():
    assert sha(dest / rel) == digest, rel
tmp = ROOT / '.opencode/liuren-active.json.natural-installing'
assert not tmp.exists()
shutil.copyfile(OUT / 'candidate-active.json', tmp)
tmp.replace(ROOT / '.opencode/liuren-active.json')
receipt = {'release': p['release'], 'previousRelease': B['parentRelease'], 'runtime': p['runtime'],
           'methodVersion': p['methodVersion'], 'runtimeFiles': C['runtime'],
           'live': {**C['live'], '.opencode/liuren-active.json': sha(ROOT / '.opencode/liuren-active.json')},
           'testLogSha256': sha(OUT / 'preflight-tests.log'), 'externalModelCalled': False,
           'websiteChanged': False, 'restartOpenCodeRequired': True}
(OUT / 'activation-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'active': p['release'], 'runtimeFiles': len(C['runtime'])}))
