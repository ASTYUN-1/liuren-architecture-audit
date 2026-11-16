"""Read-only server adapter for frozen, manifest-bound retrieval snapshots.

The server supplies bounded JSON on stdin. No paths, shell commands, index
refresh, model calls, network or writes are accepted from the model.
"""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import case_retrieval
import experience_retrieval

ROOT = Path(__file__).resolve().parents[1]


def main():
    request = json.loads(sys.stdin.read(8193))
    operation = request['operation']
    query = request.get('query', '')
    category = request.get('category', '')
    if operation not in ('cases', 'experience') or not isinstance(query, str) or len(query) > 300:
        raise ValueError('invalid_retrieval_request')
    if not isinstance(category, str) or len(category) > 20:
        raise ValueError('invalid_retrieval_category')
    bindings = json.loads((ROOT / '_retrieval/bindings.json').read_text(encoding='utf-8'))
    if operation == 'cases':
        index = json.loads((ROOT / '_retrieval/case-index.json').read_text(encoding='utf-8'))
        fields = request.get('fields', {})
        if not isinstance(fields, dict) or any(k not in ['占类','课体','发用','三传','日干','类神']
                or not isinstance(v, str) or len(v) > 400 for k,v in fields.items()):
            raise ValueError('invalid_retrieval_fields')
        # Website categories remain exact/safe-synonym only. The general local
        # engine's broader aliases must not merge pregnancy with relationships.
        safe = next((v for v in [('学业占','考试占'),('财运占','交易占'),('家宅占','宅门占'),('健康占','疾病占')]
                     if category in v), (category,))
        sources = {r['source'] for r in index['cases'] if r['fields'].get('占类') in safe}
        selected = dict(index, cases=[r for r in index['cases'] if r['source'] in sources],
            units=[u for u in index['units'] if u['source'] in sources and u['unit_kind']=='案例问题'])
        result = case_retrieval.compact(case_retrieval.retrieve(selected, query=query, fields=fields, limit=5))
        for hit in result['results']:
            hit['id'] = bindings['case_ids'][hit['case']['source']]
            hit['source'] = hit['case']['source']
            hit['meta'] = hit['case']['fields']
            hit['automaticAcceptance'] = False
            hit['total'] = hit['six_dimension_total']
    else:
        index = json.loads((ROOT / '_retrieval/experience-index.json').read_text(encoding='utf-8'))
        # Category is a ranking hint: methods remain discoverable without the
        # local engine's broad category alias changing their evidence identity.
        result = experience_retrieval.retrieve(index, query=query, limit=5, preferred_categories=[category] if category else [])
        for hit in result['results']:
            e = hit['entry']
            hit['id'] = bindings['experience_ids'][e['id']]
            hit['source'] = e['source']
            e['source_excerpt'] = e['source_excerpt'][:700]
            hit['also_matched_entries'] = hit['also_matched_entries'][:3]
            hit['also_matched_ids'] = hit['also_matched_ids'][:3]
            for related in hit['related']:
                related['read_id'] = bindings['experience_ids'][related['id']]
    result['warning'] = '候选定位不算已读。须 read_knowledge 完整读取可引用来源；相关性、作答质量与真实反馈分开，同源不重复计证。'
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('{"error":"frozen_retrieval_failed"}')
        sys.exit(1)
