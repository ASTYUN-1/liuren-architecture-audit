"""Reproducible retrieval-only comparison; never calls a model or reads private answers."""
from pathlib import Path
import json
import statistics
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'tools'))
from liuren_book_search import BookSearch, check

old = types.ModuleType('before_book_search')
old.__file__ = str(ROOT/'tools/liuren_material_scope.py')
exec(compile((OUT/'before/tools/liuren_material_scope.py').read_bytes(), old.__file__, 'exec'), old.__dict__)
baseline = old.MaterialScope(ROOT)
current = BookSearch(ROOT)
tests = [
    ('死火 旺金', 'TY', 207),
    ('十二长生', 'TY', 381),
    ('旺鬼', 'RG', 759),
    ('鬼禁日', 'RG', 759),
    ('财旺 身弱', 'RG', 299),
    ('察天 察地 看人', 'LF', 2129),
    ('阴神 翻宫', 'TY', 489),
    ('神将互换', 'TY', 479),
    ('干之寄宫空亡', 'LF', 5611),
]
rows = []
for query, book, target in tests:
    start = time.perf_counter()
    before = baseline.scan('books', query, 8)
    old_ms = (time.perf_counter()-start)*1000
    start = time.perf_counter()
    after = current.search(query)
    new_ms = (time.perf_counter()-start)*1000
    path = current.books[book]['path']
    found = [h for h in after['hits'] if h['path']==path and h['start']<=target<=h['end']]
    related = [h for h in after['related_sources'] if h['path']==path and h['start']<=target<=h['end'] and h.get('text')]
    rows.append(dict(query=query, expected=dict(book=book,line=target),
        before=dict(ms=round(old_ms,3), files_scanned=before['files_scanned'],
                    eligible_files=before['eligible_files'], errors=before['errors'],
                    hits=[dict(path=h['path'],line=h['line']) for h in before['hits']],
                    expected_line_in_locator_hits=any(h['path']==path and h['line']==target for h in before['hits'])),
        after=dict(ms=round(new_ms,3), text_chars=after['text_chars'],
                   hits=[dict(book=h['book'],start=h['start'],end=h['end'],section_complete=h['section_complete']) for h in after['hits']],
                   related_sources=[h['id'] for h in after['related_sources']],
                   expected_original_in_returned_text=bool(found or related))))
result = dict(schema='liuren-three-books-retrieval-benchmark-v1',
    checks=check(ROOT), cases=rows,
    summary=dict(queries=len(rows), original_target_returned=sum(r['after']['expected_original_in_returned_text'] for r in rows),
                 baseline_median_ms=round(statistics.median(r['before']['ms'] for r in rows),3),
                 indexed_median_ms=round(statistics.median(r['after']['ms'] for r in rows),3)),
    limitations=['Known-source development queries, not blind tests or prediction evaluation.',
                 'Baseline outputs 8 single-line locators from all books; new search returns up to 4 contextual passages from exactly three books.',
                 'Timing is local retrieval only; it does not establish total model latency or token reduction.',
                 'A target line match is a positioning check, not proof that every condition or relevant source was retrieved.'],
    model_calls=0, predictive_validation_count=0)
(OUT/'benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['summary'],ensure_ascii=False))
print(json.dumps({r['query']:r['after']['expected_original_in_returned_text'] for r in rows},ensure_ascii=False))
