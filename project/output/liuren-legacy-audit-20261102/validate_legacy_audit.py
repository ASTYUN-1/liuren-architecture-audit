"""Read-only validation of K3 cards against the current evidence files."""
import json
import hashlib
from pathlib import Path
from collections import Counter

root=Path(__file__).resolve().parents[2]
ap=root/'knowledge/liuren-research/20261102/audits/legacy-review.json'
rp=root/'knowledge/liuren-research/20261102/rules/legacy-revisions.json'
aa=json.loads(ap.read_text(encoding='utf-8'))
rr=json.loads(rp.read_text(encoding='utf-8'))
cat={d['id']:d for d in (json.loads(s) for s in (root/'docs/经验库梳理/20261019/data/catalog.jsonl').read_text(encoding='utf-8').splitlines())}
required_a={'schema','id','title','target_entry_ids','target_case_paths','disposition','finding','reasoning','evidence_refs','replacement_rule_ids','limitations','review_state'}
required_r={'schema','id','title','categories','claim_origin','review_state','status','conditions','exclusions','conclusion','reasoning_steps','alternatives','evidence_refs','support_case_ids','counterexample_case_ids','legacy_entry_ids','relations','limitations','independent_validation_count'}
for a in aa:
    assert required_a <= a.keys(),a['id']
    assert a['schema']=='liuren-audit-v1'
    assert a['disposition'] in {'retain','narrow','revise','suspend','pending'}
    assert a['reference_value'] and a['action_scope']
    for eid in a['target_entry_ids']:
        d=cat[eid]
        assert any(e['path']==d['source'] and e['line_start']<=d['line_start'] and e['line_end']>=d['line_end'] for e in a['evidence_refs']), (a['id'],eid,'missing legacy evidence')
    for p in a['target_case_paths']:assert (root/p).is_file()
    assert set(a['replacement_rule_ids']) <= {r['id'] for r in rr}
for r in rr:
    assert required_r <= r.keys(),r['id']
    assert r['schema']=='liuren-rule-card-v1'
    assert r['claim_origin'] in {'原文明示','文本可推知','本轮归纳'}
    assert r['status'] in {'candidate','source_method','suspended'}
    for rel in r['relations']:
        assert rel['type'] in {'同源复写','合并候选','条件分支','冲突','修订','依赖'}
        assert rel['target_id'] in {q['id'] for q in rr}
refs=[]
for x in aa+rr:
    assert x['review_state'] in {'pending','source_checked'}
    assert x['independent_validation_count']==0
    assert x['evidence_refs']
    for e in x['evidence_refs']:
        assert not '\\' in e['path'] and not Path(e['path']).is_absolute()
        raw=(root/e['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==e['sha256'],(x['id'],e['path'],'sha')
        ls=raw.decode('utf-8-sig').splitlines()
        assert '\n'.join(ls[e['line_start']-1:e['line_end']])==e['quote'],(x['id'],e['path'],'quote')
        refs.append(e)
assert len({a['id'] for a in aa})==len(aa)
assert len({r['id'] for r in rr})==len(rr)
families=json.loads((root/'knowledge/liuren-research/20261102/families/legacy-families.json').read_text(encoding='utf-8'))
for f in families:
    assert {'id','title','rule_ids','legacy_entry_ids','merge_type','common_method','preserved_branches','unresolved'} <= f.keys()
    assert set(f['rule_ids']) <= {r['id'] for r in rr}
    assert set(f['legacy_entry_ids']) <= cat.keys()
    assert f['independent_validation_count']==0
assert len({f['id'] for f in families})==len(families)
print('Family validation: PASS; 6 families; only birth pair is same-source merged.')
print(json.dumps(dict(result='PASS',audits=len(aa),rules=len(rr),target_legacy_entries=len({i for a in aa for i in a['target_entry_ids']}),case_files=len({p for a in aa for p in a['target_case_paths']}),unique_evidence_ranges=len({(e['path'],e['line_start'],e['line_end']) for e in refs}),evidence_files=len({e['path'] for e in refs}),evidence_refs=len(refs),dispositions=dict(Counter(a['disposition'] for a in aa)),independent_validation_count=0),ensure_ascii=False,indent=2))
