"""Question-level case retrieval, compatible with explicit chart feature queries."""
import argparse
import json
from pathlib import Path
from case_retrieval import ROOT, ensure_index, retrieve, render


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--query', default='')
    for flag in ['category', 'keti', 'fayong', 'sanchuan', 'rigan', 'leishen', 'feedback', 'kind']:
        p.add_argument('--' + flag, default='')
    p.add_argument('--exclude-source', action='append', default=[])
    p.add_argument('--limit', type=int, default=8)
    p.add_argument('--strict', action='store_true')
    p.add_argument('--refresh', action='store_true')
    p.add_argument('--status', action='store_true')
    p.add_argument('--audit', action='store_true')
    p.add_argument('--json', action='store_true')
    p.add_argument('--out', type=Path)
    args = p.parse_args()
    if args.limit < 1:
        p.error('--limit 必须大于0')
    index = ensure_index()
    if args.refresh:
        index = ensure_index(refresh=True)
    fields = dict(zip(['占类', '课体', '发用', '三传', '日干', '类神'],
                      [args.category, args.keti, args.fayong, args.sanchuan, args.rigan, args.leishen]))
    result = index['legacy_audit'] if args.audit else index['status'] if args.status else retrieve(
        index, args.query, fields, args.limit, args.exclude_source, args.strict, args.feedback, args.kind)
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n' if args.json or args.status or args.audit else render(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding='utf-8')
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
