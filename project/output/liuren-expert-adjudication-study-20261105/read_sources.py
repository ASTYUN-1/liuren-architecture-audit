"""Read bounded local passages without changing sources or active rules.

LF labels match rg. Formal splitlines coordinates are also supplied.
Retrieval is not a semantic-review or predictive-validation declaration.
"""
from pathlib import Path
import argparse
import bisect
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = {
    'BHQA': ('书籍库/北海闲人/北海闲人大六壬指南问答〔完全版〕.txt', 'utf-8'),
    'BHT': ('书籍库/北海闲人/北海闲人，特训班讲义.txt', 'gb18030'),
    'BHL': ('书籍库/北海闲人/理法简易.txt', 'utf-8'),
    'TY': ('书籍库/现代著作/献给六壬天一群的六壬笔记-2023年.txt', 'utf-8'),
    'ZN': ('书籍库/经典古籍/明代/六壬指南-明-陈公献.txt', 'utf-8'),
    'ZNZ': ('书籍库/经典古籍/明代/六壬指南注解-明-陈公献.txt', 'utf-8'),
    'DA': ('书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt', 'utf-8'),
    'RG': ('书籍库/经典古籍/佚名/壬归.txt', 'utf-8'),
    'CY': ('书籍库/经典古籍/清代/六壬粹言-清-刘赤江.txt', 'utf-8'),
}

def passage(key, start, end):
    relative, encoding = SOURCES[key]
    raw = (ROOT / relative).read_bytes()
    original = raw.decode(encoding)
    normalized = original.replace('\r\n', '\n')
    lines = normalized.split('\n')
    if not 1 <= start <= end <= len(lines):
        raise ValueError((key, start, end, len(lines)))
    offsets = []
    pos = 0
    for piece in original.splitlines(keepends=True):
        offsets.append(pos)
        pos += len(piece)
    lf_raw = original.split('\n')
    a = sum(len(x) + 1 for x in lf_raw[:start-1])
    b = a + len('\n'.join(lf_raw[start-1:end]))
    return dict(source=key, path=relative, encoding=encoding,
                sha256=hashlib.sha256(raw).hexdigest(), lf_start=start,
                lf_end=end, formal_start=bisect.bisect_right(offsets, a),
                formal_end=bisect.bisect_right(offsets, max(a, b-1)),
                quote='\n'.join(lines[start-1:end]))

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('source', choices=SOURCES)
    p.add_argument('spans', nargs='+', help='LF start:end')
    args = p.parse_args()
    for span in args.spans:
        start, end = map(int, span.split(':'))
        row = passage(args.source, start, end)
        print(json.dumps({k:v for k,v in row.items() if k != 'quote'}, ensure_ascii=False))
        for n, line in enumerate(row['quote'].split('\n'), start):
            print(f'{n}: {line}')
