"""Read B3 outputs independently and verify source bytes, exact spans and links."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/liuren-book-cases-20261102'
BASE=ROOT/'knowledge/liuren-research/20261102'
CASES=json.loads((BASE/'book-cases/bifa.json').read_text(encoding='utf-8'))
RULES=json.loads((BASE/'rules/book-bifa.json').read_text(encoding='utf-8'))
QUEUE=json.loads((OUT/'bifa_candidate_queue.json').read_text(encoding='utf-8'))
COVER=json.loads((OUT/'bifa_coverage.json').read_text(encoding='utf-8'))
ROLES={'原书断语','原载反馈','原载作答','后人注解','旧AI归纳','本轮解释'}
required_c={'schema','id','title','book_title','category','source_case_identity','review_state','completeness','boundary_note','question','authors','source_refs','missing_fields','feedback_status','method_rule_ids','same_event_ids','notes'}
required_r={'schema','id','title','categories','claim_origin','review_state','status','conditions','exclusions','conclusion','reasoning_steps','alternatives','evidence_refs','support_case_ids','counterexample_case_ids','legacy_entry_ids','relations','limitations','independent_validation_count'}
cache={};refs=[]

def verify_ref(e,owner):
    assert {'path','line_start','line_end','quote','sha256','role'} <= e.keys(),owner
    p=PurePosixPath(e['path']);assert not p.is_absolute() and '..' not in p.parts and '\\' not in e['path'],owner
    real=(ROOT/str(p)).resolve();assert real.is_relative_to(ROOT.resolve()),owner
    if str(p) not in cache:
        raw=real.read_bytes();cache[str(p)]=(hashlib.sha256(raw).hexdigest(),raw.decode('utf-8-sig').splitlines())
    sha,lines=cache[str(p)];a,b=e['line_start'],e['line_end']
    assert type(a) is int and type(b) is int and 1<=a<=b<=len(lines),(owner,'range')
    assert e['sha256']==sha,(owner,'sha')
    assert e['quote']=='\n'.join(lines[a-1:b]),(owner,'quote')
    assert e['role'] in ROLES,(owner,'role')
    refs.append((owner,e))

case_ids={c['id'] for c in CASES};rule_ids={r['id'] for r in RULES}
all_case_ids={c['id'] for p in (BASE/'book-cases').glob('*.json') for c in json.loads(p.read_text(encoding='utf-8'))}
assert len(case_ids)==len(CASES) and len(rule_ids)==len(RULES)
case_identities={i for c in CASES for i in [c['source_case_identity']]+c.get('additional_source_case_identities',[])}
assert len(case_identities)==sum(1+len(c.get('additional_source_case_identities',[])) for c in CASES)
for c in CASES:
    assert required_c<=c.keys(),c['id'];assert c['schema']=='liuren-book-case-v1'
    assert c['review_state']=='source_checked' and c['completeness'] in {'fragment','complete'},c['id']
    assert c['independent_validation_count']==0
    assert c['source_refs'] and c['boundary_note'] and c['missing_fields']
    for e in c['source_refs']:verify_ref(e,c['id'])
    e=c['source_refs'][0]
    assert c['source_case_identity']==f"book:{e['path']}:L{e['line_start']}-L{e['line_end']}"
    assert set(c['method_rule_ids'])<=rule_ids
    assert set(c['same_event_ids'])<=all_case_ids
    text='\n'.join(e['quote'] for e in c['source_refs'])
    for value in c.get('chart_fields',{}).values():assert value in text,(c['id'],'nonliteral chart field')
    assert any(n.startswith('排盘引擎复原输入摘记：') for n in c['notes'])
    assert c['source_recovery']['engine_reconstruction_status'] in {'inputs_recorded_pending_engine','candidate_checked_pending_standard_archive','equivalent_structure_reviewed','source_order_conflict_reviewed'}
    assert any('课盘' in e['quote'] and '错乱' in e['quote'] for e in c['source_refs']) or c['source_recovery'].get('original_chart_presence')=='not_stated',c['id']
    if c['completeness']=='complete':
        assert c['reconstruction_refs']
    for rid in c['method_rule_ids']:
        r=next(r for r in RULES if r['id']==rid)
        assert c['id'] in r['support_case_ids'] and c['source_case_identity'] in r['support_case_ids'],(c['id'],rid,'reverse link')
for r in RULES:
    assert required_r<=r.keys(),r['id'];assert r['schema']=='liuren-rule-card-v1'
    assert r['review_state']=='source_checked' and r['status']=='source_method'
    assert r['claim_origin'] in {'原文明示','文本可推知','本轮归纳'}
    assert r['independent_validation_count']==0 and r['method_type'] and r['logic_stages']
    assert r['conditions'] and r['exclusions'] and r['reasoning_steps'] and r['conclusion'] and r['alternatives']
    assert set(r['support_case_ids'])<=case_ids|case_identities
    for e in r['evidence_refs']:verify_ref(e,r['id'])
    for rel in r['relations']:
        assert rel['type'] in {'同源复写','合并候选','条件分支','冲突','修订','依赖'} and rel['target_id'] in rule_ids
for cue in QUEUE['cues']:
    assert cue['review_state']=='pending' and cue['scan_only'] and cue['boundary_status']=='not_inferred_by_scanner'
    assert set(cue['registered_case_ids'])<=case_ids
    verify_ref(cue['source_ref'],cue['id'])
for e in QUEUE['transcript_damage_cues']:
    assert e['review_state']=='pending' and e['scan_only'];verify_ref(e,'transcript-damage-cue')
assert set(n for s in QUEUE['sections'] for n in s['law_numbers'])==set(range(1,101))
assert COVER['substantive_review']['law_numbers']==list(range(1,101))
assert COVER['substantive_review']['law_count']==100
assert COVER['registered_cases']==len(CASES) and COVER['method_cards']==len(RULES)
assert COVER['complete']==sum(c['completeness']=='complete' for c in CASES)
assert COVER['fragment']==sum(c['completeness']=='fragment' for c in CASES)
# Exercise the independent owning validator as well, filtering this owner's records.
spec=importlib.util.spec_from_file_location('book_case_validator',ROOT/'tools/liuren_book_cases.py')
owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
b1=owner.validated_cases(ROOT)
mappings=owner.provenance(ROOT,b1)
assert 'BK26-BIFA-002' not in owner.expand_identities({'BK26-BIFA-001'},mappings),'Common context must not merge separate BIFA events'
for c in CASES:
    for e in c['source_refs']:
        if (e['path'],e['line_start'],e['line_end']) in {
            ('书籍库/北海闲人/毕法赋全解-正式整理本.md',6,12),
            ('课程写作/整理本/毕法赋全解/校勘记录.md',15,21),
            ('书籍库/北海闲人/毕法赋全解-正式整理本.md',1485,1491)}:
            assert e.get('same_event') is False and e.get('dependency_type')=='borrowed_context'
bifa_checks=[c for c in b1['checks'] if c['id'] in case_ids]
assert len(bifa_checks)==len(CASES)
blocked=[c for c in bifa_checks if c['mechanical_state']!='pass']
for c in CASES:
    if c['completeness']=='fragment':assert not list((ROOT/'案例项目库').glob(f"*/case-book-{c['id']}.md")),'Fragment cases must not be imported'
core=[e for who,e in refs if who in case_ids|rule_ids]
result={'schema':'bifa-validation-v1','result':'PASS' if not blocked else 'BLOCKED_OWNING_VALIDATOR','core_source_and_schema_checks':'PASS','cases':len(CASES),'complete':sum(c['completeness']=='complete' for c in CASES),'fragment':sum(c['completeness']=='fragment' for c in CASES),'rules':len(RULES),'owning_validator_pass':len(bifa_checks)-len(blocked),'owning_validator_blocked':blocked,'eligible_for_import':sum(c['eligible_for_import'] for c in bifa_checks),'core_evidence_refs':len(core),'core_unique_evidence_ranges':len({(e['path'],e['line_start'],e['line_end']) for e in core}),'all_refs_including_scan_cues':len(refs),'evidence_files':len(cache),'same_event_cross_law_count':len(COVER['same_event_cross_law_registers']),'substantive_laws':COVER['substantive_review']['law_count'],'mechanical_law_scan':100,'engine_reconstruction':{'complete_ids':[c['id'] for c in CASES if c['completeness']=='complete'],'conflict_ids':[c['id'] for c in CASES if c['source_recovery']['engine_reconstruction_status']=='source_order_conflict_reviewed']},'independent_validation_count':0,'limits':['机械核对不证明预测准确。','完整案以原载全文加独立完整复原结构保存；原图残损及设置标签未唯一确认仍明示；冲突案保留不符。','全书124条程序线索不是124案，也不等于全书精读。']}
(OUT/'bifa_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if blocked:raise SystemExit(2)




