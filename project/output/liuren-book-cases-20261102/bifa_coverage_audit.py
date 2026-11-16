"""Second-pass whole-book reconciliation, with explicit non-case dispositions."""
import json,hashlib
from pathlib import Path
from bifa_scan import REVIEWED,TRANS_READ,BOOK,TRANS
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
def ref(p,a,b):
 raw=(ROOT/p).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 return dict(path=p,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role='原书断语')
def run():
 cues=json.loads((OUT/'bifa_candidate_queue.json').read_text(encoding='utf-8'))['cues']
 cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
 decisions={194:'引干正格教学例式，无具体人事或结果。',198:'引支正格教学例式，无具体人事或结果。',207:'重用194的贵人引从示意，不另造事件。',213:'两贵引从扩格例式，非现实反馈。',413:'盘珠课成立条件例式，虽有年月日将时但无具体人事。',612:'催官使者教学演示，未给具体人事或反馈。',682:'六阳演示盘，非现实叙事。',686:'六阴演示盘，非现实叙事。',870:'禄归支教学例式，下面分占类泛解。',1039:'后接经典课例的引入标题，不是另案。',1884:'家宅灾祸的泛论，没有具体事件。',2279:'一叶知秋与扩大边界的方法泛论。',2358:'六亲和旬将组合的教学假设。',4388:'乘的两层定义与位置举例。',4394:'墓及迷糊、交通事故的通用象意，未述亲验事件。',4607:'起例讨论的通用日课比较；后接另例已登记。',4798:'所问婚姻与非占现类的边界泛论。',4806:'所筮不入按占类分看课传或类象的泛论。'}
 unmatched={x['source_ref']['line_start'] for x in cues if not x['registered_case_ids']}
 assert unmatched==set(decisions),(unmatched-set(decisions),set(decisions)-unmatched)
 adjudications=[dict(cue_id=x['id'],source_ref=x['source_ref'],disposition='registered_case_or_reprint' if x['registered_case_ids'] else ('teaching_form' if x['source_ref']['line_start'] in {194,198,207,213,413,612,682,686,870,2358} else 'definition_or_general_discussion'),case_ids=x['registered_case_ids'],review_state='source_checked',reason='已人工复核对应登记的主案/跨法重引边界，线索数不等于案例数。' if x['registered_case_ids'] else decisions[x['source_ref']['line_start']]) for x in cues]
 tls=(ROOT/TRANS).read_text(encoding='utf-8-sig').splitlines()
 gaps=[dict(line_number=i,text=l) for i,l in enumerate(tls,1) if i>=125 and l.strip() and not any(a<=i<=b for a,b in TRANS_READ)]
 assert all(x['text']=='---' or x['text'].startswith(('说明：','第一批','第二批','第三批','第四批','第五批','第六批','第七批','第八批','第九批','第十批','第十一批','第十二批','## ')) for x in gaps)
 versions=[
  ('整案删节',124,[(TRANS,913,921),(BOOK,774,778)],'孙鲁山仅转录存整案，正式邻案刘汉式只作删节边界，不作孙源。'),
  ('长例压缩',93,[(TRANS,5359,5369),(BOOK,4582,4590)],'柳书游两时、父与乡试完整题干及原反馈依转录保全，正式概要不能代全案。'),
  ('教学引文删节',None,[(TRANS,831,833)],'二十四间传原判辞仅转录保留，归教学文本，不造现实案例。'),
  ('坐标编辑',130,[(TRANS,1447,1455),(BOOK,1223,1229)],'干土/干上未常整理为土象/支上未常，两版不静默统一。'),
  ('盘序异文',6,[(TRANS,1235,1255),(BOOK,1040,1058)],'主残子巳戌与六亲戌巳子及正式正文不同；完整引擎结构与冲突分轴保存。'),
 ]
 obj=dict(schema='bifa-whole-book-coverage-audit-v1',review_state='source_checked',scope='正式本前言及100法与转录全文实质段二次核对；不宣告原扫描已复原。',
  formal_front_matter_refs=[ref(BOOK,1,12),ref(BOOK,14,116)],preface_refs=[ref(BOOK,120,178),ref(TRANS,125,189)],transcript_front_matter_refs=[ref(TRANS,1,123)],
  formal_law_ranges=[dict(law=n,line_start=a,line_end=b) for n,(a,b) in sorted(REVIEWED.items())],
  transcript_substantive_ranges=TRANS_READ,remaining_transcript_gaps=dict(meaning='均已读为分批说明、目录标题或分隔符；不存在仍未读的实质断案段。',entries=gaps),
  cue_adjudications=adjudications,mechanical_cue_count=len(cues),unmatched_cues_manually_adjudicated=len(unmatched),registered_case_count=len(cases),
  audit_added_cases=[f'BK26-BIFA-{n:03}' for n in range(125,132)],audit_added_cross_law_reprints=[f'BK26-BIFA-{n:03}' for n in [71,73,76]],
  version_boundaries=[dict(kind=k,case_id=f'BK26-BIFA-{n:03}' if n else None,source_refs=[ref(p,a,b) for p,a,b in spans],note=note) for k,n,spans,note in versions],
  limits=['全文初读/二审覆盖不等于所有原图已经补齐。','124条日期问占线索与131案分属不同统计口径。','教学例式及未列课盘的见闻不造真实案例；同案跨法重引只计一个事件。','132以后的新发现仍可追加；本轮覆盖审计不是对未获得原扫描的穷尽保证。'],independent_validation_count=0)
 (OUT/'bifa_coverage_audit.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(cases=len(cases),adjudicated_cues=len(cues),noncase_cues=len(unmatched),unread_substantive_transcript_lines=0),ensure_ascii=False))
if __name__=='__main__':run()
