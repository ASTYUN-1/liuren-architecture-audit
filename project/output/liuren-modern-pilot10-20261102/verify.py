"""Bounded acceptance checks for E2 artifacts and the authorized E1 derived sync."""
from pathlib import Path
import json,sys,hashlib,collections,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import experience_retrieval as er
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
obs=read(OUT/'subjudgments.json');segs=read(OUT/'author-segments.json');cases=read(OUT/'case-manifest.json')
rulespath=ROOT/'knowledge/liuren-research/20261102/rules/modern-pilot10.json';rules=read(rulespath)
family_path=ROOT/'knowledge/liuren-research/20261102/families/modern-pilot10.json';families=read(family_path)
reviews=read(ROOT/'knowledge/liuren-research/20261102/method-reviews/modern.json')
old=read(OUT/'preserved-method-reviews.json');oldids={x['case_id'] for x in old}
assert [r for r in reviews if r['case_id'] in oldids]==old
assert oldids=={'BK26-MODERN-105','BK26-MODERN-106','BK26-MODERN-107'}
expected={f'BK26-MODERN-{n:03}' for n in [31,42,44,73,74,75,77,82,87,96]}
assert {c['case_id'] for c in cases}==expected and all(c['completeness']=='complete' for c in cases)
assert {r['case_id'] for r in reviews if r['case_id'] not in oldids}==expected
assert {o['case_id'] for o in obs}==expected
assert {x for r in rules for x in r['source_case_ids']}==expected
assert len(obs)==156 and len(segs)==107 and len(rules)==31 and len(families)==5
assert all(o['rule_ids'] or o['disposition']=='no_new_rule' for o in obs)
assert next(o for o in obs if o['judgment']=='问有无哥哥')['feedback_state']=='答复否定（询问）'
assert not any(o['utterance_type']=='询问' and o['feedback_state']=='原载反证' for o in obs)
# Exact contiguous evidence checks, including all source-case spans and selected legacy units.
cache={};checks=0
def check(r):
 global checks
 p=ROOT/r['path']
 if str(p) not in cache:
  raw=p.read_bytes();cache[str(p)]=(sha(p),raw.decode('utf-8-sig').splitlines())
 digest,lines=cache[str(p)]
 assert digest==r['sha256'],r
 assert '\n'.join(lines[r['line_start']-1:r['line_end']])==r['quote'],r
 checks+=1
for x in cases:
 for r in x['source_refs']:check(r)
for x in segs+obs+rules:
 for r in x['evidence_refs']+x.get('feedback_refs',[]):check(r)
comps=read(OUT/'substantive-comparisons.json');legacy={x['id']:x for c in comps for x in c['legacy_snapshots']}
legacy_proofs=[]
for x in legacy.values():
 raw=(ROOT/x['source']).read_bytes();lines=raw.decode('utf-8-sig').splitlines()
 assert '\n'.join(lines[x['line_start']-1:x['line_end']])==x['source_excerpt']
 legacy_proofs.append(dict(id=x['id'],path=x['source'],line_start=x['line_start'],line_end=x['line_end'],sha256=hashlib.sha256(raw).hexdigest(),excerpt_sha256=hashlib.sha256(x['source_excerpt'].encode()).hexdigest()))
dump(OUT/'compared-legacy-evidence-check.json',legacy_proofs)
baseline=read(OUT/'e1-before-sync-manifest.json')['input_sha256']
registry='knowledge/liuren-research/20261102/book-cases/modern.json'
assert sha(ROOT/registry)==baseline[registry]
source='书籍库/现代著作/当代壬占汇选第五版.md'
assert sha(ROOT/source)==cases[0]['source_refs'][0]['sha256']
# Actual retrieval loads the same dynamic overlay as search-experience.py.
idx=er.ensure_index(root=ROOT)
summary=idx['status']['research_overlay'];issues=idx['status']['research_issues']
assert summary['mechanical_valid'] and not issues and idx['status']['research_rule_entries']==461
assert summary['record_count']==492 and summary['eligible_count']==492 and summary['explicit_rule_family_count']==43
dump(OUT/'overlay-validation.json',dict(summary=summary,issues=issues,eligible_rule_ids=[x['id'] for x in idx['entries'] if x['id'].startswith('LR26-')],note='当前动态加载即逐证据校验；精简保存概要，非预测验证。'))
queries=[(31,'艺术家走失链','031-STEPS'),(42,'已签工程担保单','042-FAIL'),(44,'交车合而多冲','044-PROCESS'),(73,'禅外流云消化链','073-DIGEST'),(74,'雨田升象并聚','074-SIGNS'),(75,'青山相亲定位','075-ROLE-A'),(77,'误食救制分支','077-RESCUE'),(82,'冤酒案填空说','082-VOID-YES'),(87,'中考取分','087-NUMBER'),(96,'银行资格原过关链','096-PASS')]
hits=[]
for n,q,key in queries:
 result=er.retrieve(idx,q,kind='审读规则',limit=3)
 wanted='LR26-MP10-'+key;ids=[x['entry']['id'] for x in result['results']]
 assert wanted in ids,(q,ids)
 hits.append(dict(case_id=f'BK26-MODERN-{n:03}',query=q,expected_rule_id=wanted,result_ids=ids,passed=True))
dump(OUT/'search-ten-cases.json',hits)
cli=read(OUT/'search-digestion.json')
assert 'LR26-MP10-073-DIGEST' in [r['entry']['id'] for r in cli['results']]
e1=ROOT/'output/liuren-experience-organization-20261102'
classification=read(e1/'classification.json');e1manifest=read(e1/'manifest.json');e1validation=read(e1/'validation.json')
classids={x['id'] for x in classification}
assert len(classification)==1419 and len(classids)==1419
assert all(r['id'] in classids for r in rules)
assert e1manifest['counts']['mapped_rule_ids']==461 and e1validation['rule_id_coverage']=='461/461' and e1validation['result']=='PASS'
assert e1manifest['historical_e1_snapshot']['rules']==430
result=dict(result='PASS',scope='E2固定十案及授权E1派生分类同步；没有全库语义复审或预测效果验证',
 case_ids=sorted(expected),counts=dict(cases=10,complete_cases=10,author_phase_segments=107,subjudgments=156,new_source_method_cards=31,reused_topic_groups=6,new_comparison_families=5,existing_rules_compared=23,legacy_units_compared=25,existing_families_compared=4,existing_equivalent_merges=0,deletions=0,preserved_modern_reviews=3,new_modern_reviews=10),
 current_overlay=summary,evidence_checks=dict(exact_contiguous_refs=checks,unique_source_files=len(cache),selected_legacy_exact_units=len(legacy_proofs),original_modern_case_register_unchanged=True,original_book_sha256=sha(ROOT/source)),
 e1_derived_sync=dict(result='PASS',mapped_units=1419,legacy_units=958,rules=461,new_e2_rule_ids_covered=31,historical_e1_rules=430,historical_e1_mapped_units=1388,classification_semantics_changed=False),
 retrieval=dict(actual_cli='python -X utf8 tools/search-experience.py --query "禅外流云 消化" --limit 3 --json --out output/liuren-modern-pilot10-20261102/search-digestion.json',actual_cli_expected_rule_found=True,ten_case_queries=hits),
 method_questions_remain=['031干孩/父母及计时起点','075干支正反定位','077遥克轻重和救链因果','082月建填空正反说','087伏吟盘丑未互加坐标','096单处填实后修订与当次未过'],
 limits=dict(independent_validation_count=0,project_complete=False,ten_case_extraction_complete=True,no_new_cases=True,no_new_reserved_questions=True,chart_recalculation=False,external_model_calls=False,deployment=False),
 artifacts={})
dump(OUT/'final-check.json',result)
# Refresh human-readable report only after the final dynamic validation.
subprocess.run([sys.executable,'-X','utf8',str(OUT/'report.py')],cwd=ROOT,check=True,capture_output=True)
paths=[rulespath,family_path,ROOT/'knowledge/liuren-research/20261102/method-reviews/modern.json',ROOT/'docs/六壬知识整理-20261102/当代汇选十例经验试提.md',OUT/'author-segments.json',OUT/'subjudgments.json',OUT/'case-manifest.json',OUT/'substantive-comparisons.json',OUT/'final-check.json',OUT/'search-ten-cases.json',OUT/'search-digestion.json',OUT/'overlay-validation.json',e1/'organize.py',e1/'classification.json',e1/'classification.jsonl',e1/'manifest.json',e1/'validation.json',ROOT/'docs/六壬知识整理-20261102/已有经验统一整理.md']
acceptance={k:result[k] for k in ['result','scope','case_ids','counts','current_overlay','evidence_checks','e1_derived_sync','method_questions_remain','limits']}
acceptance['retrieval']=dict(actual_cli_expected_rule_found=True,ten_case_queries_passed=10,details='search-ten-cases.json / search-digestion.json')
acceptance['source_hashes']={source:sha(ROOT/source),registry:sha(ROOT/registry)}
acceptance['artifact_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
dump(OUT/'acceptance.json',acceptance)
print(json.dumps({k:acceptance[k] for k in ['result','counts','current_overlay','e1_derived_sync','retrieval']},ensure_ascii=False))
