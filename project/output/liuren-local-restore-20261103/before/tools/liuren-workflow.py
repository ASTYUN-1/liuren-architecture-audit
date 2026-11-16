"""Unified local Liuren entry: prepare -> read -> check."""
import argparse
import json
import sys
from pathlib import Path
import liuren_workflow as workflow


def main():
    sys.stdout.reconfigure(encoding='utf-8', newline='')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Read-only runtime, knowledge, local dependency and fixed-chart checks')
    p = sub.add_parser('prepare')
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('read')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--id', required=True)
    p.add_argument('--page', type=int)
    p.add_argument('--part', default='record', help='record, source, evidence:N or source_case:N; all are bounded pages')
    p.add_argument('--review', action='store_true', help='Audit suspended material; never grants adoption or bypasses same-case exclusion')
    p = sub.add_parser('check')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--record', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'doctor': result = workflow.doctor()
        elif args.command == 'prepare': result = workflow.prepare(workflow.load(args.input), args.out)
        elif args.command == 'read': result = workflow.read(args.run, args.id, page=args.page, review=args.review, part=args.part)
        else: result = workflow.check(args.run, workflow.load(args.record))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('ok') is False else 0
    except (ValueError, KeyError) as error:
        print(json.dumps(dict(ok=False, error=str(error)), ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
