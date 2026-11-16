"""Restore backed-up entrypoints only; refuse to overwrite subsequent changes."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rollback(directory=HERE, apply=False):
    directory = Path(directory)
    manifest = json.loads((directory / 'entrypoints.json').read_text('utf-8'))
    root = Path(manifest['root'])
    pending = []
    for row in manifest['files']:
        relative = Path(row['path'])
        current = (root / relative).resolve()
        backup = (directory / 'backup' / relative).resolve()
        if not current.is_relative_to(root.resolve()) or not backup.is_relative_to((directory / 'backup').resolve()):
            raise ValueError('回滚清单路径越界')
        original = backup.read_bytes()
        if digest(original) != row['before_sha256']:
            raise ValueError('备份哈希不符：' + row['path'])
        now = digest(current.read_bytes())
        if now not in {row['after_sha256'], row['before_sha256']}:
            raise ValueError('入口存在后续改动，停止回滚：' + row['path'])
        pending.append((current, original))
    if apply:
        for current, data in pending:
            current.write_bytes(data)
    return {'mode': 'applied' if apply else 'preview', 'verified_entrypoints': len(pending),
            'new_tools_and_evidence_retained': True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true')
    print(json.dumps(rollback(apply=p.parse_args().apply), ensure_ascii=False))
