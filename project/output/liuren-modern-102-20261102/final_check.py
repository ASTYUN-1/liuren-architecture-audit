"""Final bounded E3 validation and human-readable consolidated report."""
import json,hashlib,sys,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;BASE=R/'knowledge/liuren-research/20261102'
sys.stdout.reconfigure(encoding='utf8');sys.path.insert(0,str(R/'tools'))
import liuren_knowledge_workbench as w
import experience_retrieval as er
import case_retrieval as cr
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reviews=read(BASE/'method-reviews/modern.json');dims=read(O/'method-dimensions.json');summary=read(O/'consolidation-summary.json');dispatch=read(O/'dispatch.json');baseline={x['case_id']:x for x in read(O/'baseline-modern-reviews.json')};reg={x['id']:x for x in read(BASE/'book-cases/modern.json')}
by={x['case_id']:x for x in reviews};subs=[s for x in reviews for s in x['subjudgments']]
errors=[];reference_count=0;cache={}
def checkrefs(x):
 global reference_count
 if isinstance(x,dict):
  if all(k in x for k in ['path','line_start','line_end','sha256','quote']):
   p=x['path']
   if p not in cache:
    raw=(R/p).read_bytes();cache[p]=(hashlib.sha256(raw).hexdigest(),raw.decode('utf-8-sig').splitlines())
   digest,ls=cache[p];reference_count+=1
   if digest!=x['sha256'] or '\n'.join(ls[x['line_start']-1:x['line_end']])!=x['quote']:errors.append('引用：'+p+':'+str(x['line_start']))
  for v in x.values():checkrefs(v)
 elif isinstance(x,list):
  for v in x:checkrefs(v)
assert len(by)==102 and set(by)==set(dispatch['complete_case_ids'])
assert len({s['id'] for s in subs})==len(subs)
preserved=[i for i in dispatch['reuse_completed_case_ids'] if by[i]==baseline[i]];assert len(preserved)==12
assert read(O/'C/preserved-106-review.json')==baseline['BK26-MODERN-106']
assert sha(R/'书籍库/现代著作/当代壬占汇选第五版.md')=='dbc35765d7e92fc92b94febcffda00dfb563b99cea93fe851b2ea936b6b7da2e'
assert sha(BASE/'book-cases/modern.json')=='52b649b464684dcbe38541102db88e48d0f8042428f938f434abaf8a5f539a5f'
v=w.validated_records(R)
allrules={x['id']:x for x in v['rules']};owned={i for i in allrules if i.startswith(('LR26-M102A-','LR26-M102AT-','LR26-M102B-','LR26-M102C-','LR26-M102N-'))}
assert len(owned)==155
for s in subs:
 if not s.get('disposition'):errors.append('未处置：'+s['id'])
 for rid in s.get('rule_ids',[]):
  if rid not in allrules:errors.append('不存在规则：'+rid)
checkrefs(reviews)
for p in [BASE/'rules'/('modern-102-'+g+'.json') for g in ['a','a-tail','b','c','consolidated']]:checkrefs(read(p))
for p in [O/'A/author-segments.json',O/'A-tail/author-segments.json',O/'B/author-segments.json',O/'C/author-segments.json']:
 if p.exists():checkrefs(read(p))
dump(O/'workbench-check.json',dict(summary=v['summary'],issues=v['issues'],owned_eligible_count=len(owned)))
assert not v['issues'],v['issues'][:2]
ei=er.ensure_index(R,refresh=False);ci=cr.ensure_index(R,refresh=False)
ei_by={x['id']:x for x in ei['entries']};ci_by={x.get('book_case_id',x['id']):x for x in ci['cases']}
assert not (owned-set(ei_by))
assert not (set(by)-set(ci_by))
experience_specs=[('中标 利润',['LR26-M102C-069-PROFIT','LR26-M102N-TARGET-STAGE']),('面试 试岗',['LR26-M102A-028-OFFER']),('裁员 签约 离职',['LR26-M102AT-033-TIMING']),('月建 填空',['LR26-M102N-VOID-OBJECT','LR26-MP10-082-VOID-YES','LR26-MP10-082-VOID-NO']),('已孕 男女 产日',['LR26-M102N-PREGNANCY-QUESTION','LR26-M102AT-034-SEX']),('补偿 折半',['LR26-M102C-104-COMPENSATION']),('背包 乘车卡',['LR26-M102C-088-CARD']),('羊 西北',['LR26-M102B-038-SHEEP']),('手术 清醒',['LR26-M102C-090-SURGERY']),('复合 两天',['LR26-M102B-067-RECONCILE']),('代问 角色 施受',['LR26-M102N-ROLE-ACTION']),('刑期 运算 单位',['LR26-M102N-QUANTITY-UNIT','LR26-M102B-059-SENTENCE']),('救制 存活 恢复',['LR26-M102N-RESCUE-ENDPOINT']),('空间 层级 类神',['LR26-M102N-LOST-COORDINATE'])]
experience_specs += [('成败 目标 阶段',['LR26-M102N-TARGET-STAGE']),('代占 主体 施受',['LR26-M102N-ROLE-ACTION']),('空实 填实 对象',['LR26-M102N-VOID-OBJECT']),('胎产 已孕 性别',['LR26-M102N-PREGNANCY-QUESTION']),('失物 空间 类神',['LR26-M102N-LOST-COORDINATE']),('病占 存活 稳定',['LR26-M102N-RESCUE-ENDPOINT']),('数断 运算 单位',['LR26-M102N-QUANTITY-UNIT'])]
searchchecks=[]
for query,expect in experience_specs:
 result=er.retrieve(ei,query=query,limit=8);ids=[x['entry']['id'] for x in result['results']]
 searchchecks.append(dict(query=query,result_ids=ids,expected_any=expect,passed=bool(set(ids)&set(expect)),canonical_entry_ids=[i for i in ids if i.startswith('LR26-M102N-')]))
case_specs=[('打桩工程 中标 利润','BK26-MODERN-069'),('脑出血 手术','BK26-MODERN-090'),('乘车卡 背包','BK26-MODERN-088'),('已经怀孕 胎儿性别','BK26-MODERN-034'),('裁员 财务 业务','BK26-MODERN-033'),('妹妹 离家','BK26-MODERN-051')]
casechecks=[]
for query,expected in case_specs:
 result=cr.retrieve(ci,query=query,limit=8);ids=[x['case'].get('book_case_id',x['case']['id']) for x in result['results']];casechecks.append(dict(query=query,result_ids=ids,expected=expected,passed=expected in ids))
peer=read(O/'C/independent-peer-review.json')
dump(O/'retrieval-checks.json',dict(experience_index_status=ei['status'],case_index_status=ci['status'],owned_rule_id_presence=dict(expected=155,present=len(owned&set(ei_by))),case_id_presence=dict(expected=102,present=len(set(by)&set(ci_by))),experience_queries=searchchecks,case_queries=casechecks,ranking_is_not_accuracy=True,independent_validation_count=0))
if any(not x['passed'] for x in searchchecks+casechecks):errors.append('存在自然语言检索预期未达，见retrieval-checks.json')
result=dict(schema='liuren-modern-102-final-acceptance-v1',result='PASS' if not errors else 'NEEDS_REVIEW',counts=summary,coverage=dict(exact_cases=102,reused_12_objects_unchanged=len(preserved),all_subjudgments_dispositioned=all(x['all_subjudgments_dispositioned'] for x in reviews),new90_reviews_with_separate_restoration_axis=sum('method_derivation_restoration_complete' in x for x in reviews if x['case_id'] not in preserved),method_dimension_side_table_cases=len(dims),original_106_partial_preserved=True,source_and_registry_unchanged=True),reference_checks=reference_count,reference_errors=errors,workbench=v['summary'],experience_queries_passed=sum(x['passed'] for x in searchchecks),experience_query_count=len(searchchecks),case_queries_passed=sum(x['passed'] for x in casechecks),case_query_count=len(casechecks),all_owned_rules_indexed=155,all_modern_cases_indexed=102,peer_review=dict(path='output/liuren-modern-102-20261102/C/independent-peer-review.json',scope='4来源卡/23子判断的有界独立语义抽查；不冒充全库精度或独立效力验证',issue_id='IPR-C-001',resolution='051反馈措辞已按5693/5704/5779分轴修正，builder与派生文件均已同步，复核关闭'),independent_validation_count=0)
paths=[BASE/'method-reviews/modern.json',O/'method-dimensions.json',O/'rule-destination-map.json',O/'semantic-classification.json',O/'substantive-consolidation.json',O/'retrieval-checks.json',O/'C/independent-peer-review.json',BASE/'rules/modern-102-consolidated.json',BASE/'families/modern-102-consolidated.json',R/'output/liuren-experience-organization-20261102/classification.json',R/'output/liuren-experience-organization-20261102/manifest.json',R/'output/liuren-knowledge-20261102/validation.json']
result['hashes']={p.relative_to(R).as_posix():sha(p) for p in paths}
dump(O/'acceptance.json',result)
lines=['# 当代壬占汇选102例经验整理','',f'既有102个完整案全部有处置：12个原完成对象原样复用，本轮90案拆出1062个子判断；合计1225个子判断。新增148张来源方法分支卡，另建7个有条件、有步骤的规范核对入口。它们归一共同操作，未认定整卡预测公式等价；源卡删除0，独立验证0。','',f'全部处置与原法推导恢复分轴：本轮{summary["method_restoration_counts"].get("false",0)}案保留明示理由缺口，{summary["method_restoration_counts"].get("true",0)}案本轴未见已登记缺口；复用12案的恢复轴未重评，标unknown，不能倒推为无缺口。盘文冲突与未访后续另见逐案记录。','', '## 本轮实际工作量','', '|组别|案|子判断|来源卡|','|---|---:|---:|---:|']
for g,d in summary['groups'].items():lines.append(f'|{g}|{d["cases"]}|{d["subjudgments"]}|{d["source_cards"]}|')
lines+=['','## 规范入口及成员去向','',f'39张本轮来源卡进入以下7个共同操作入口；109张保留独立来源分支。本轮逐卡比较记录在`substantive-consolidation.json`，148卡全量去向在`rule-destination-map.json`，每个入口列成立条件、执行步骤与各成员具体差异。独立分支不是漏处理，亦不借同名/同结果强并。','']
for x in read(BASE/'rules/modern-102-consolidated.json'):
 lines+=['### '+x['title'],'',x['conclusion'],'','适用条件：'+'；'.join(x['conditions']),'','执行：'+' → '.join(x['reasoning_steps']),'','|来源分支|保留差异与反馈范围|','|---|---|']
 for b in x['branch_selector']:lines.append('|'+b['rule_id']+'|'+b['substantive_difference'].replace('|','｜')+'|')
 lines+=['','旧卡比较：'+'、'.join(i for i in x['member_rule_ids'] if not i.startswith(('LR26-M102A-','LR26-M102AT-','LR26-M102B-','LR26-M102C-'))),'']
lines+=['## 逐案覆盖及原法缺口','', '“无已登记缺口”只限原文理由轴；不表示盘文无争议、反馈完整或方法有效。原12对象未改，恢复轴从侧表读取。','', '|案例|主题|判断项|恢复轴|理由缺口项|来源卡|','|---|---|---:|---|---:|---:|']
for d in dims:
 x=by[d['case_id']];state='未知／未重评' if d['method_derivation_restoration_complete'] is None else '有原文理由缺口' if not d['method_derivation_restoration_complete'] else '无已登记缺口';rules={rid for s in x['subjudgments'] for rid in s.get('rule_ids',[])}
 lines.append('|'+x['case_id']+'|'+reg[x['case_id']]['title'].replace('|','｜')+'|'+str(len(x['subjudgments']))+'|'+state+'|'+str(len(d['source_derivation_gaps']))+'|'+str(len(rules))+'|')
lines+=['','## 验收与边界','',f'连续原文引用核对{reference_count}次，错误{len(errors)}；工作台{v["summary"]["eligible_count"]}/{v["summary"]["record_count"]}记录通过，阻断{len(v["issues"])}。经验检索155张本轮来源卡/规范入口全部在索引，案例检索102案全部在索引；自然语言经验查询{result["experience_queries_passed"]}/{len(searchchecks)}、案例查询{result["case_queries_passed"]}/{len(casechecks)}达到所列预期。检索顺序不是预测准确率。','', '另有4卡、23子判断有界独立语义抽查，051一处反馈措辞已核原文并修正，未解决0；不能据此宣称全库语义精度。','', '原书与登记哈希不变；106旧部分review单独保留后由本轮新审替换。五个fragment案、未拆书、题库、部署、外部API、原书与排盘算法均未扩入。','', '逐作者完整表：`当代汇选102例-A.md`、`当代汇选102例-A尾三案.md`、`当代汇选102例-B.md`、`当代汇选102例-C.md`；机器验收：`output/liuren-modern-102-20261102/acceptance.json`。','']
(R/'docs/六壬知识整理-20261102/当代汇选102例经验整理.md').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['counts','hashes']},ensure_ascii=False));assert not errors,errors
