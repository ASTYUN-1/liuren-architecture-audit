"""Build release metadata after candidate/source edits; do not switch the active pointer."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
C = OUT / 'candidate-runtime'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def dump(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


B = read(OUT / 'before-manifest.json')
NEW = B['newRelease']
policy = read(OUT / 'event-policy.json')
for rel, digest in B['runtime'].items():
    assert sha(ROOT / B['parentRuntime'] / rel) == digest, rel
assert sha(ROOT / '.opencode/liuren-active.json') == B['live']['.opencode/liuren-active.json']
source = OUT.relative_to(ROOT).as_posix()
shensha = read(C / 'references/shensha-policy.json')
shensha['release'] = NEW
dump(C / 'references/shensha-policy.json', shensha)
loader = read(C / 'loader-contract.json')
loader.update(release=NEW, parentRelease=B['parentRelease'], authoringSource=source, eventPositioning=policy)
for rel in loader['sourceHashes']:
    loader['sourceHashes'][rel] = sha(ROOT / rel)
dump(C / 'loader-contract.json', loader)
dump(C / 'natural-positioning-revision.json', read(OUT / 'revision.json'))
m = read(C / 'manifest.json')
m.update(release=NEW, parentRelease=B['parentRelease'], authoringSource=source, status='active', eventPositioning=policy)
m['computeInterface'].update(release=NEW, transportEvidence=source + '/current-wire.json')
m['files'] = {f.relative_to(C).as_posix(): sha(f) for f in C.rglob('*') if f.is_file() and f.name != 'manifest.json'}
m['version'] = hashlib.sha256(json.dumps(m['files'], sort_keys=True).encode()).hexdigest()
dump(C / 'manifest.json', m)
p = read(OUT / 'before/.opencode/liuren-active.json')
p.update(release=NEW, previousRelease=B['parentRelease'], runtime='runtime/liuren/' + NEW,
         methodVersion=m['version'], backup=source + '/before', authoringSource=source, eventPositioning=policy)
p['computeInterface'].update(release=NEW, transportEvidence=source + '/current-wire.json')
p['bookRetrieval']['compatibleMethodRelease'] = NEW
for rel in p['workflowImplementation']:
    p['workflowImplementation'][rel] = sha(ROOT / rel)
for rel in p['bookRetrieval']['files']:
    p['bookRetrieval']['files'][rel] = sha(ROOT / rel)
for rel in p['files']:
    p['files'][rel] = sha(ROOT / '.opencode/skills' / rel)
dump(OUT / 'candidate-active.json', p)
dump(OUT / 'candidate-manifest.json', {
    'release': NEW, 'runtime': {f.relative_to(C).as_posix(): sha(f) for f in C.rglob('*') if f.is_file()},
    'live': {rel: sha(ROOT / rel) for rel in B['live'] if rel != '.opencode/liuren-active.json'},
    'activeSha256': sha(OUT / 'candidate-active.json')})
print(json.dumps({'candidate': NEW, 'runtimeFiles': len(m['files']) + 1}))
