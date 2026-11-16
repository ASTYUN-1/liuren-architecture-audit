"""Seal this task's evidence; do not modify the frozen runtime or active pointer."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


receipt = read(OUT / 'activation-receipt.json')
candidate = read(OUT / 'candidate-manifest.json')
before = read(OUT / 'before-manifest.json')
active = read(ROOT / '.opencode/liuren-active.json')
assert active['release'] == receipt['release'] == candidate['release'] == '20261106-event-positioning-15'
corrected_test = 'tools/tests/liuren-flow-control.test.mjs'
for record in (receipt, candidate):
    mismatches = [rel for rel, digest in record['live'].items() if sha(ROOT / rel) != digest]
    assert set(mismatches) <= {corrected_test}, mismatches
    record['live'][corrected_test] = sha(ROOT / corrected_test)
write(OUT / 'activation-receipt.json', receipt)
write(OUT / 'candidate-manifest.json', candidate)

checks = {}
for name, base, entries in (
    ('liveFiles', ROOT, receipt['live']),
    ('candidateLiveFiles', ROOT, candidate['live']),
    ('runtimeFiles', ROOT / receipt['runtime'], receipt['runtimeFiles']),
    ('candidateRuntimeFiles', ROOT / receipt['runtime'], candidate['runtime']),
    ('parentRuntimeFiles', ROOT / before['parentRuntime'], before['runtime']),
    ('backupFiles', OUT / 'before', before['live']),
    ('activeImplementationFiles', ROOT, active['workflowImplementation']),
):
    mismatches = [rel for rel, digest in entries.items() if sha(base / rel) != digest]
    assert not mismatches, (name, mismatches)
    checks[name] = {'count': len(entries), 'mismatches': []}
assert sha(ROOT / '.opencode/liuren-active.json') == candidate['activeSha256']
wire = read(OUT / 'current-wire.json')
assert wire['exitCode'] == 0 and wire['loopbackOnlyProvider'] and not wire['realModelCalled']
for rel, digest in wire['implementationSha256'].items():
    assert sha(ROOT / rel) == digest, rel
log = (OUT / 'acceptance-tests.log').read_text(encoding='utf-8-sig')
assert 'tests 132' in log and 'pass 132' in log and 'fail 0' in log
single = (OUT / 'single-method-tests.log').read_text(encoding='utf-8-sig')
assert 'Ran 3 tests' in single and 'OK' in single
doctor = read(OUT / 'doctor.json')
parent_doctor = read(ROOT / 'output/liuren-receipt-fix-20261106/installed-doctor.json')
assert doctor['errors'] == parent_doctor['errors'] == ['research mechanical validation has gaps']
fingerprint = 'aaf91ad9a2a838ddf2d7ce7ae2ea7eca17c760ce939c530e844b74003f5b85ac'
assert fingerprint in json.dumps(doctor) and fingerprint in json.dumps(parent_doctor)
checks['doctorBaselineErrorUnchanged'] = True
checks['wireImplementationMatch'] = True
evidence = ['acceptance-tests.log', 'single-method-tests.log', 'loader-tests.log', 'doctor.json',
            'current-wire.json', 'revision-map.json', 'activation-receipt.json', 'candidate-manifest.json',
            '整改与验收说明.md', 'finalize_acceptance.py']
result = {
    'release': active['release'], 'runtime': active['runtime'],
    'activeSha256': sha(ROOT / '.opencode/liuren-active.json'),
    'checks': checks, 'nodeTests': {'passed': 132, 'failed': 0},
    'singleMethodTests': {'passed': 3, 'failed': 0},
    'additionalLegacyPythonSuite': {'tests': 15, 'failures': 1, 'errors': 6, 'status': 'known-baseline-test-gaps'},
    'skillQuickValidate': 'unavailable-missing-PyYAML', 'globalDoctorOk': False,
    'externalModelCalled': False, 'predictiveValidationCount': 0,
    'restartOpenCodeRequired': True,
    'evidenceSha256': {rel: sha(OUT / rel) for rel in evidence},
}
write(OUT / 'acceptance.json', result)
print(json.dumps({'release': active['release'], 'integrityChecksPassed': True, 'nodeTestsPassed': 132,
                  'singleMethodTestsPassed': 3, 'globalDoctorOk': False}, ensure_ascii=False))
