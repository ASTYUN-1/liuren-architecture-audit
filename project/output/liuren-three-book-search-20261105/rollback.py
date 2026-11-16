"""Restore only the seven backed-up live files, after checking current identities.

New sidecar indexes, tests and reports remain for traceability. No recursive delete.
"""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
before = json.loads((OUT/'before-manifest.json').read_text('utf-8'))
after = json.loads((OUT/'release-manifest.json').read_text('utf-8'))['files']
for relative, expected in before.items():
    path = (ROOT/relative).resolve()
    source = (OUT/'before'/relative).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not source.is_relative_to((OUT/'before').resolve()):
        raise SystemExit('rollback path escapes the declared workspace')
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise SystemExit('backup changed: '+relative)
    current = hashlib.sha256(path.read_bytes()).hexdigest()
    if current != after[relative] and current != expected:
        raise SystemExit('live file changed after this release; manual merge required: '+relative)
for relative in before:
    shutil.copy2(OUT/'before'/relative, ROOT/relative)
print('Restored the seven original live files; new sidecar evidence retained.')
