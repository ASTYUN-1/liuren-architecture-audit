"""细粒度经验检索入口；自动校对原文并更新运行索引，不修改原始经验。"""
import argparse
import json
from pathlib import Path
from experience_retrieval import ROOT, ensure_index, retrieve, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', '--search', default='')
    parser.add_argument('--category', action='append', default=[])
    parser.add_argument('--kind', default='')
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--all-terms', action='store_true')
    parser.add_argument('--include-suspended', action='store_true', help='Explicit review only; suspended rules cannot be adopted')
    parser.add_argument('--exclude-source', action='append', default=[])
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit 必须大于 0')
    index = ensure_index(refresh=args.refresh)
    result = index['status'] if args.status else retrieve(
        index, args.query, args.category, args.kind, args.limit, args.exclude_source, args.all_terms,
        include_suspended=args.include_suspended)
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n' if args.json or args.status else render(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding='utf-8')
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
