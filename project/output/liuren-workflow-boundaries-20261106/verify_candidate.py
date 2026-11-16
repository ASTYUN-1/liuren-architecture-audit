"""Preservation and loader checks without activating candidate configuration."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RUN = OUT / 'candidate-runtime'
LIVE = OUT / 'candidate-live'
STAGE = OUT / 'validation-root'
before = json.loads((OUT / 'before-manifest.json').read_text('utf-8'))
pointer = json.loads((LIVE / '.opencode/liuren-active.json').read_text('utf-8'))
old = ROOT / before['parentRuntime']
checks = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name, value):
    if not value:
        raise AssertionError(name)
    checks.append(name)


def load(path):
    return json.loads(path.read_text('utf-8-sig'))


check('active files unchanged before activation', all(sha(ROOT / p) == h for p, h in before['live'].items()))
check('all 93 parent runtime files unchanged', all(sha(old / p) == h for p, h in before['runtime'].items()))
old_route, new_route = load(old / 'reading-route.json'), load(RUN / 'reading-route.json')
for key in ['domains', 'conditional', 'legacyCoverage']:
    check('unchanged route ' + key, old_route[key] == new_route[key])
check('same 14 required modules', [s['required'] for s in old_route['stages']] == [s['required'] for s in new_route['stages']])
op, np = load(old / 'references/shensha-policy.json'), load(RUN / 'references/shensha-policy.json')
op.pop('release'); np.pop('release')
check('policy rules unchanged except release identity', op == np)
check('fixed E01-E22 evidence bytes unchanged', sha(old / 'references/adjudicator-book-evidence.json') == sha(RUN / 'references/adjudicator-book-evidence.json'))
marker = '# 固定书据：条件摘要与关键短引'
check('fixed book-basis prompt suffix unchanged', (old / 'references/adjudicator-prompt.md').read_bytes().split(marker.encode())[1] == (RUN / 'references/adjudicator-prompt.md').read_bytes().split(marker.encode())[1])
changed = {p for p in before['runtime'] if sha(RUN / p) != before['runtime'][p]}
expected = {'entry.md', 'reading-route.json', 'loader-contract.json', 'integration-map.json', 'manifest.json',
            'methods/liqi.md', 'methods/evidence.md', 'methods/adjudication.md', 'methods/report.md',
            'references/adjudicator-contract.md', 'references/adjudicator-prompt.md', 'references/shensha-policy.json'}
check('only intended runtime files changed', changed == expected)
check('liqi original professional body preserved', (old / 'methods/liqi.md').read_text('utf-8').split('\n', 1)[1] in (RUN / 'methods/liqi.md').read_text('utf-8'))
check('report original professional body preserved', (old / 'methods/report.md').read_text('utf-8').split('\n', 1)[1] in (RUN / 'methods/report.md').read_text('utf-8'))
for relative in ['opencode.json', '.opencode/oh-my-opencode-slim.jsonc']:
    before_config = load(OUT / 'before' / relative)
    after_config = load(LIVE / relative)
    path = ('agent', 'liuren') if relative == 'opencode.json' else ('agents', 'liuren-adjudicator')
    before_config[path[0]][path[1]].pop('prompt')
    after_config[path[0]][path[1]].pop('prompt')
    check('model/permissions/options unchanged: ' + relative, before_config == after_config)
check('canonical adjudicator prompt matches configured prompt', load(LIVE / '.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt'] == (RUN / 'references/adjudicator-prompt.md').read_text('utf-8'))
check('live daliuren equals candidate entry bytes', (LIVE / '.opencode/skills/liuren/daliuren/SKILL.md').read_bytes() == (RUN / 'entry.md').read_bytes())
for p, h in pointer['bookRetrieval']['files'].items():
    target = LIVE / p if (LIVE / p).exists() else ROOT / p
    check('book integration hash: ' + p, sha(target) == h)
for p in ['knowledge/liuren-book-index/20261105/catalog.json', 'knowledge/liuren-book-index/20261105/index.sqlite3',
          'tools/liuren_book_search.py', 'tools/liuren-materials.py', '.opencode/tools/liuren_materials.ts']:
    check('three-book implementation/index unchanged: ' + p, pointer['bookRetrieval']['files'][p] == load(OUT / 'before/.opencode/liuren-active.json')['bookRetrieval']['files'][p])
manifest = load(RUN / 'manifest.json')
check('runtime manifest covers all candidate files', set(manifest['files']) == {p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file() and p.name != 'manifest.json'})
check('runtime manifest file hashes', all(sha(RUN / p) == h for p, h in manifest['files'].items()))
loader = load(RUN / 'loader-contract.json')
check('source hashes describe candidate installation', all(sha(LIVE / p if (LIVE / p).exists() else ROOT / p) == h for p, h in loader['sourceHashes'].items()))
check('current local-read bytes registered', pointer['workflowImplementation']['tools/liuren-local-read.py'] == sha(ROOT / 'tools/liuren-local-read.py'))

# Isolated root consumed by the actual production loader; no active pointer change.
STAGE.mkdir(exist_ok=True)
shutil.copytree(RUN, STAGE / pointer['runtime'], dirs_exist_ok=True)
(STAGE / '.opencode').mkdir(exist_ok=True)
(STAGE / '.opencode/liuren-active.json').write_bytes((LIVE / '.opencode/liuren-active.json').read_bytes())
for item in pointer.get('localModuleOverrides', {}).values():
    target = STAGE / item['file'];target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / item['file'], target)
spec = importlib.util.spec_from_file_location('loader', ROOT / 'tools/load-liuren-methods.py')
module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
runtime, active_manifest = module.active(STAGE)
plan = module.plan(active_manifest)
check('actual production loader accepts isolated v08', active_manifest['release'] == pointer['release'] and len(plan) == 14)
for key in active_manifest['modules']:
    module.content(runtime, active_manifest, key)
check('all method modules load with correct hashes', True)
for key in pointer['files']:
    check('skill hash: ' + key, sha(LIVE / '.opencode/skills' / key) == pointer['files'][key])
report = {'status': 'passed', 'checks': checks, 'count': len(checks), 'release': pointer['release'],
          'changedRuntimeFiles': sorted(changed), 'newRuntimeFiles': ['workflow-boundaries-revision.json'],
          'predictiveValidation': False, 'realModelInvocation': False}
(OUT / 'candidate-preservation-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': report['status'], 'checks': len(checks), 'release': pointer['release']}, ensure_ascii=False))
