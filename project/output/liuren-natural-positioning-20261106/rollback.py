"""Restore only this task's backed-up files when no subsequent edit would be overwritten."""
from pathlib import Path
import json
import hashlib
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
B = read(OUT / 'before-manifest.json')
R = read(OUT / 'activation-receipt.json')
for rel, digest in R['live'].items():
    assert sha(ROOT / rel) == digest, 'changed since activation: ' + rel
for rel, digest in B['live'].items():
    assert sha(OUT / 'before' / rel) == digest, rel
for rel in [r for r in B['live'] if r != '.opencode/liuren-active.json'] + ['.opencode/liuren-active.json']:
    shutil.copyfile(OUT / 'before' / rel, ROOT / rel)
print(json.dumps({'restored': B['parentRelease'], 'retainedInactiveRuntime': R['runtime']}))
