"""Restore the six pre-upgrade entrypoints; keep source data and new artifacts intact."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='执行恢复；默认仅检查')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    root = folder.parents[1]
    manifest = json.loads((folder / 'backup-manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        current = root / item['path']
        backup = folder / 'backup' / item['path']
        if hashlib.sha256(backup.read_bytes()).hexdigest() != item['sha256_before']:
            raise SystemExit('备份校验失败：' + item['path'])
        actual = hashlib.sha256(current.read_bytes()).hexdigest()
        if actual not in {item['sha256_before'], item['sha256_after']}:
            raise SystemExit('切换后文件又有改动，停止自动覆盖：' + item['path'])
    if args.apply:
        for item in manifest['files']:
            shutil.copy2(folder / 'backup' / item['path'], root / item['path'])
        print('已恢复切换前六个入口文件；原始经验、案例和新索引文件均保留。')
    else:
        print('备份与当前文件校验通过，可以回滚；本次未执行恢复。')


if __name__ == '__main__':
    main()
