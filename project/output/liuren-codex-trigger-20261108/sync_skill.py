"""Sync the authorized trigger wording, with exact prior hashes and backups."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[2]
evidence = Path(__file__).resolve().parent
source = root / 'integrations/codex/daliuren-codex'
target = Path.home() / '.codex/skills/daliuren-codex'
before = json.loads((evidence / 'before-hashes.json').read_text(encoding='utf-8'))
digest = lambda b: hashlib.sha256(b).hexdigest()

for relative, expected in before.items():
    src, dst = source / relative, target / relative
    if src.is_symlink() or dst.is_symlink() or dst.resolve() != dst:
        raise ValueError('Linked path rejected: ' + relative)
    if digest(dst.read_bytes()) not in (expected, digest(src.read_bytes())):
        raise ValueError('Installed file changed independently: ' + relative)

changes = {}
for relative, expected in before.items():
    src, dst = source / relative, target / relative
    current, wanted = dst.read_bytes(), src.read_bytes()
    backup = evidence / 'before' / relative
    if digest(current) == expected and not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(current)
    if current != wanted:
        dst.write_bytes(wanted)
    if digest(dst.read_bytes()) != digest(wanted):
        raise ValueError('Post-write mismatch: ' + relative)
    changes[relative] = {'before': expected, 'after': digest(wanted)}

result = {'keyword': '使用大六壬进行测算', 'target': str(target), 'verified': True,
          'files': changes, 'rollback': 'Restore the matching files from before/ after checking installed hashes against after.'}
(evidence / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
