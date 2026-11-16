"""Restore only this update's backed-up files, refusing later unrelated edits."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
O = Path(__file__).resolve().parent
load = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before, after = load(O / 'before.json'), load(O / 'after.json')
for rel, expected in after['files'].items():
    assert sha(R / rel) == expected, 'Later edits exist: ' + rel
for rel, expected in before['files'].items():
    assert sha(O / 'before' / rel) == expected
for rel in sorted(before['files'], key=lambda s: s == '.opencode/liuren-active.json'):
    shutil.copyfile(O / 'before' / rel, R / rel)
print('Restored', before['release'], '; new reading artifacts retained inactive; no runtime deleted')
