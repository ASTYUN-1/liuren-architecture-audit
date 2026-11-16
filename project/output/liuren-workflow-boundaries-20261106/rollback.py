"""Restore the 16 prior local files; retain both runtime packages for history."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
before = json.loads((OUT / 'before-manifest.json').read_text('utf-8'))
after = json.loads((OUT / 'activation-receipt.json').read_text('utf-8'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true', help='Validate rollback prerequisites without writing')
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Check every target before any mutation; do not overwrite later user edits.
for path, digest in after['files'].items():
    if sha(ROOT / path) != digest:
        raise ValueError('File has later changes; no rollback performed: ' + path)
for path, digest in before['live'].items():
    if sha(OUT / 'before' / path) != digest:
        raise ValueError('Backup bytes mismatch: ' + path)
for path, digest in before['runtime'].items():
    if sha(ROOT / before['parentRuntime'] / path) != digest:
        raise ValueError('Parent runtime changed: ' + path)
paths = [p for p in before['live'] if p != '.opencode/liuren-active.json'] + ['.opencode/liuren-active.json']
for path in paths:
    temporary = (ROOT / path).with_name(Path(path).name + '.workflow08-restoring')
    if temporary.exists():
        raise ValueError('Temporary file already exists: ' + str(temporary))
if args.check:
    print(json.dumps({'rollbackEligible': True, 'wouldRestore': before['parentRelease'], 'files': len(paths), 'writes': 0}, ensure_ascii=False))
    raise SystemExit(0)
for path in paths:
    target = ROOT / path
    temp = target.with_name(target.name + '.workflow08-restoring')
    if temp.exists():
        raise ValueError('Temporary file already exists: ' + str(temp))
    shutil.copyfile(OUT / 'before' / path, temp)
    temp.replace(target)
assert all(sha(ROOT / p) == h for p, h in before['live'].items())
print(json.dumps({'restored': before['parentRelease'], 'files': len(paths), 'retainedNewRuntime': after['runtime']}, ensure_ascii=False))
