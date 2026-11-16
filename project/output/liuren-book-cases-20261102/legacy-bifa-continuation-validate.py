"""Read-only owning workbench verification; only write this batch's results."""
import hashlib,json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
sys.path.insert(0,str(ROOT/'tools'))
import liuren_knowledge_workbench as wb
r=wb.build(ROOT)
ids={f'{p}26-LEGACY-BIFA-{n:03}' for p in ['LA','LR'] for n in range(1,11)}
checks=[c for c in r['validation']['records'] if c['id'] in ids]
assert len(checks)==20
assert all(c['mechanical_state']=='pass' and c['eligible_for_search'] for c in checks),checks
families=[f for f in r['families'] if f.get('_record_file','').endswith('/legacy-bifa-continuation.json')]
assert len(families)==20
assert not any(c['mechanical_state']!='pass' or c['semantic_review_state']!='source_checked' for f in families for c in f['linked_card_states'])
book_rules={x for f in families for x in f['rule_ids'] if x.startswith('LR26-BOOK-BIFA-')}
assert len(book_rules)==139
queries={}
for query in ['干神归支','制鬼良医','三传递克','年命填空']:
 result=wb.search(r,query,30)
 text=json.dumps(result,ensure_ascii=False)
 queries[query]=dict(has_continuation_rule='LR26-LEGACY-BIFA-' in text,has_conditional_families='BF26-' in text)
 assert all(queries[query].values()),(query,queries[query])
owned=['knowledge/liuren-research/20261102/'+folder+'/legacy-bifa-continuation.json' for folder in ['audits','rules','families']]
o=dict(schema='legacy-bifa-continuation-validation-v1',result='PASS',owning_record_checks=checks,owning_record_count=20,canonical_family_count=20,source_method_cards_covered=len(book_rules),legacy_entries_reviewed=['B0303'],subjudgment_count=10,search_checks=queries,artifact_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in owned},global_validation_valid=r['validation']['valid'],independent_validation_count=0,limits=['仅说明引文/结构校验及检索可见，不证明预测准确。','全局其他代理产物若仍在途，以工具负责人最终统一索引结果为准。'])
(OUT/'legacy-bifa-continuation-validation.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:o[k] for k in ['result','owning_record_count','canonical_family_count','source_method_cards_covered','search_checks','global_validation_valid']},ensure_ascii=False))
