"""Recovery routes with stop conditions; cannot convert an unresolved gap to a fact."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
RELATIONS={8,13,14,34,36,40,41,42,43,46,60,71,72,73,76,78,79,80,81,82,86,88,90,99,106,115,116,118,122,123,124}
def run():
 cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
 review=json.loads((OUT/'bifa_reconstruction_review.json').read_text(encoding='utf-8'))
 rows=[]
 for c in cases:
  rs=[r for r in review['reviews'] if r['case_id']==c['id']];n=int(c['id'][-3:])
  if c['completeness']=='complete':route='restored_full_structure';why='现存题干、全断及后注齐，已获全facts实质等价的完整引擎结构；来源冲突、缺反馈独立记录。';action='不重复计算；只有新增来源或引擎变动才重新核。'
  elif rs and not any(r['matching_candidate_ids'] for r in rs):route='engine_source_conflict';why='明文/关系候选已实跑，与原残盘或序列不符，原请求结果不可覆盖。';action='停止同输入重算；只在新增扫描、同案文本或明确另一原载分支后另存请求。'
  elif n in RELATIONS:route='relation_constrained_candidates';why='原载有年/月、日、时与残盘或课名关系，但月将未直载；关系可约束候选，尚须实际生成并语义审核。';action='先查同案原书明确月将；无明文时允许显式关系候选，不以反馈选择，不能将候选值冒充原载。'
  else:route='cross_source_missing_inputs';why='仍缺年月、日支、将时、有效月将残字或更多盘位；已有局部关系不等于完整输入。';action='定向查同案另载及引擎随附古例；本地无明文则终止该缺口，不随机补年份月份或照后果反推。'
  rows.append(dict(case_id=c['id'],title=c['title'],completeness=c['completeness'],route=route,reason=why,next_action=action,source_refs=c['source_refs'][:2],source_missing_fields=c.get('original_source_missing_fields',c['missing_fields']),same_event_ids=c['same_event_ids'],engine_results=[r['result_id'] for r in rs],engine_input_notes=[v for v in c['notes'] if v.startswith('排盘引擎复原输入摘记：')],independent_validation_count=0))
 counts=dict(Counter(r['route'] for r in rows))
 obj=dict(schema='bifa-fragment-recovery-routes-v1',case_count=len(cases),counts=counts,
  explicit_input_pending_count=0,true_missing_narrative_count=0,
  zero_count_explanation='本轮明参、3个伏吟关系候选及040/081同源明载月将补证均已实际执行；当前131案可读题断后注均已收集，无仍缺整段正文的未登记案。缺原图/缺参不伪称整段缺文。58/59的乙日须先由有来源历法换算核日支；94戊将非法不能擅改为戌将。',
  restored_relation_candidates=['BK26-BIFA-004','BK26-BIFA-012'],failed_relation_candidate='BK26-BIFA-017',entries=rows,
  limits=[f'关系候选{counts.get("relation_constrained_candidates",0)}案尚未全部实跑，不把路由清单当复原完成。','跨源缺参类含原载本就简引的案例；没有证据的原图存在不自行断言。','同一输入无新证据不反复计算，不按反馈挑设置。'],independent_validation_count=0)
 (OUT/'bifa_fragment_routes.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(cases=len(cases),routes=counts),ensure_ascii=False))
if __name__=='__main__':run()
