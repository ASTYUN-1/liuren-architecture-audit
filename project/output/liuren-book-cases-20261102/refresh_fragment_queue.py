import json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];reg=[]
for p in (R/'knowledge/liuren-research/20261102/book-cases').glob('*.json'):reg.extend(json.loads(p.read_text(encoding='utf8')))
ready=set('BIFA-006 BIFA-009 BIFA-019 BIFA-021 BIFA-022 BIFA-025 BIFA-026 BIFA-028 BIFA-029 BIFA-030 BIFA-031 BIFA-032 BIFA-037 BIFA-038 BIFA-039 BIFA-048 BIFA-051 BIFA-052 BIFA-054 BIFA-056 MODERN-027 MODERN-028'.split())
textgap=set('ANCIENT-005 ANCIENT-006 ANCIENT-101 ANCIENT-211 SHAO-003'.split())
missing=set('ANCIENT-102 ANCIENT-115 ANCIENT-116 ANCIENT-117 ANCIENT-213 BIFA-004 BIFA-008 BIFA-012 BIFA-013 BIFA-014 BIFA-016 BIFA-017 BIFA-023 BIFA-024 BIFA-027 BIFA-033 BIFA-034 BIFA-035 BIFA-036 BIFA-040 BIFA-041 BIFA-042 BIFA-043'.split())
othergap={'MODERN-010','MODERN-047'}
items=[]
for r in reg:
 if r['completeness']!='fragment':continue
 k=r['id'].removeprefix('BK26-');rc=r.get('reconstruction_refs',[])
 if rc:state='existing_reconstruction_owner_review';action='已有结果和全raw，负责人复核facts、原文及登记两轴；不自动complete。'
 elif k in ready:state='explicit_inputs_ready';action='明载输入可另制来源绑定请求；须逐案核年月映射/盘式约束和异文，枚举未核设置。'
 elif k in textgap:state='text_loss_not_recoverable_by_chart';action='缺关键文字，盘式不能还原；检索同源善本，不由反馈补写。'
 elif k in othergap:state='nonchart_evidence_gap';action='缺原断/奇门转课等证据，单排六壬不能恢复。'
 elif k in missing:state='missing_explicit_inputs';action='缺将/完整日支/第二盘日期等；完整missing_fields照存，找同源不反推唯一盘。'
 elif k=='BIFA-007':state='conflicting_explicit_inputs';action='后文补己巳辛酉亥将卯时，但三月/巳月冲突；将来分输入组保存，不按原追赃失验选月份。'
 else:state='pending_input_review';action='新登记尚未逐条核输入，不能仅由chart_fields机械判断一定缺参或可补。'
 results=list((R/'output/liuren-book-cases-20261102/reconstructions').glob('RC26-'+k+'*.json'))
 items.append({'case_id':r['id'],'title':r['title'],'state':state,'next_action':action,'chart_fields':r.get('chart_fields',{}),'missing_fields':r['missing_fields'],'source_case_identity':r['source_case_identity'],'source_refs':[{k:v for k,v in x.items() if k!='quote'} for x in r['source_refs']],'reconstruction_refs':rc,'available_result_paths':[x.relative_to(R).as_posix() for x in results],'independent_validation_count':0})
q={'schema':'liuren-book-fragment-reconstruction-queue-v1','scope':'阶段停止时的当前登记快照；未核输入保留pending，后续授权接续时可运行本脚本刷新','summary':dict(collections.Counter(x['state'] for x in items)),'case_count':len(items),'complete':False,'items':items}
(R/'output/liuren-book-cases-20261102/fragment-reconstruction-queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'count':len(items),'summary':q['summary']},ensure_ascii=False))
