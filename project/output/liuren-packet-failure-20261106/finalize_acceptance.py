"""Check installed bytes and record local evidence without editing active implementation."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
B = read(OUT / 'before-manifest.json')
C = read(OUT / 'candidate-manifest.json')
R = read(OUT / 'activation-receipt.json')
P = read(ROOT / '.opencode/liuren-active.json')
assert P['release'] == R['release'] == C['release'] == '20261106-packet-diagnostics-17'
assert P['methodVersion'] == read(ROOT / P['runtime'] / 'manifest.json')['version']
assert sha(ROOT / '.opencode/liuren-active.json') == C['activeSha256']
checks = {}
for name, base, entries in [
    ('live', ROOT, R['live']), ('candidateLive', ROOT, C['live']),
    ('runtime', ROOT / P['runtime'], R['runtimeFiles']),
    ('candidateRuntime', OUT / 'candidate-runtime', C['runtime']),
    ('parentRuntimeUnchanged', ROOT / B['parentRuntime'], B['runtime']),
    ('backups', OUT / 'before', B['live']),
    ('activeImplementations', ROOT, P['workflowImplementation'])]:
    mismatches = [rel for rel, digest in entries.items() if sha(base / rel) != digest]
    assert not mismatches, (name, mismatches)
    checks[name] = {'count': len(entries), 'mismatches': []}
runtime = ROOT / P['runtime']
assert (runtime / 'entry.md').read_bytes() == (ROOT / P['entry']).read_bytes()
slim = read(ROOT / '.opencode/oh-my-opencode-slim.jsonc')
assert slim['agents']['liuren-adjudicator']['prompt'] == (runtime / 'references/adjudicator-prompt.md').read_text('utf-8')
assert P['eventPositioning']['semanticRoleChecks'] is False
assert P['eventPositioning']['actorReferenceRequired'] is False
assert 'actorAsDayStem' not in P['eventPositioning']
for name in ['preflight-tests.log', 'acceptance-tests.log']:
    text = (OUT / name).read_text('utf-8-sig')
    assert 'tests 137' in text and 'pass 137' in text and 'fail 0' in text
single = (OUT / 'single-method-tests.log').read_text('utf-8-sig')
assert 'Ran 3 tests' in single and 'OK' in single
wire = read(OUT / 'current-wire.json')
assert wire['exitCode'] == 0 and not wire['realModelCalled'] and wire['loopbackOnlyProvider']
for rel, digest in wire['implementationSha256'].items():
    assert sha(ROOT / rel) == digest
doctor = read(OUT / 'doctor.json')
parent_doctor = read(ROOT / 'output/liuren-natural-positioning-20261106/doctor.json')
assert doctor['errors'] == parent_doctor['errors'] == ['research mechanical validation has gaps']
fingerprint = 'aaf91ad9a2a838ddf2d7ce7ae2ea7eca17c760ce939c530e844b74003f5b85ac'
assert fingerprint in json.dumps(doctor) and fingerprint in json.dumps(parent_doctor)
checks.update(entryMatchesSkill=True, adjudicatorPromptMatches=True, doctorBaselineErrorUnchanged=True)
replay = read(OUT / 'observed-replay.json')
assert len(replay['records']) == 8 and all(r['ok'] and r['nativeSchemaAndToolExecuted'] and r['methodCoveragePassed'] for r in replay['records'])
for rel, digest in replay['implementationSha256'].items():
    assert sha(ROOT / rel) == digest, rel
checks['observedOriginalNativeReplaysPassed'] = 8

evidence = ['activation-receipt.json', 'candidate-manifest.json', 'preflight-tests.log', 'acceptance-tests.log',
            'single-method-tests.log', 'doctor.json', 'current-wire.json', 'revision.json', '故障核查与修复说明.md', 'observed-replay.json']
result = {'release': P['release'], 'runtime': P['runtime'], 'checks': checks,
          'nodeTests': {'passed': 137, 'failed': 0}, 'singleMethodTests': {'passed': 3, 'failed': 0},
          'semanticRoleChecks': False, 'extraModelCallsAdded': 0,
          'externalModelCalled': False, 'predictiveValidationCount': 0,
          'globalDoctorOk': doctor['ok'], 'skillQuickValidate': 'not-rerun-missing-PyYAML',
          'restartOpenCodeRequired': True, 'evidenceSha256': {rel: sha(OUT / rel) for rel in evidence}}
(OUT / 'acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'release': P['release'], 'integrityChecksPassed': True, 'nodeTestsPassed': 137,
                  'singleMethodTestsPassed': 3, 'globalDoctorOk': doctor['ok']}))
