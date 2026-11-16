"""E3 consolidation: preserves source branches and unifies only specified operations."""
import json,hashlib,collections,sys,copy
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;BASE=R/'knowledge/liuren-research/20261102'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dispatch=read(O/'dispatch.json');registry={x['id']:x for x in read(BASE/'book-cases/modern.json')}
baseline=read(O/'baseline-modern-reviews.json');baseline_by={x['case_id']:x for x in baseline}
groups={g:read(O/g/'method-reviews.json') for g in ['A','A-tail','B','C']}
assert len(groups['A'])==27 and len(groups['A-tail'])==3 and len(groups['B'])==30 and len(groups['C'])==30
reviews=[copy.deepcopy(baseline_by[i]) for i in dispatch['reuse_completed_case_ids']]
dimensions=[]
for x in reviews:
 dimensions.append(dict(case_id=x['case_id'],disposition_coverage_complete=x['all_subjudgments_dispositioned'],method_derivation_restoration_complete=None,source_derivation_gap=None,source_derivation_gaps=[],restoration_assessment_state='复用对象原样保留；旧处置完成不证明原法逐项无缺口，本轴未重新评定',unresolved_method_questions=x.get('unresolved_method_questions',[]),independent_validation_count=0))
for g,items in groups.items():
 for original in items:
  x=copy.deepcopy(original)
  gaps=x.get('source_derivation_gaps',[])
  complete=x.get('method_derivation_restoration_complete',x.get('method_restoration_complete'))
  if complete is None:
   gaps=[dict(subjudgment_id=s['id'],author=s.get('author'),phase=s.get('phase'),judgment=s['judgment'],reason='原文缺少该判断明示理由，不由后注倒补') for s in x['subjudgments'] if not s.get('reasoning_steps') and s.get('utterance_type') in ['判断','原载判断']]
   complete=not gaps
  x['method_derivation_restoration_complete']=complete;x['source_derivation_gap']=bool(gaps);x['source_derivation_gaps']=gaps
  x['completion_semantics']='现存子判断均已处置；理由恢复完整性、盘文一致性、反馈覆盖和独立验证分别记录，不表示预测效力。'
  reviews.append(x)
  dimensions.append(dict(case_id=x['case_id'],group=g,disposition_coverage_complete=x['all_subjudgments_dispositioned'],method_derivation_restoration_complete=complete,source_derivation_gap=bool(gaps),source_derivation_gaps=gaps,chart_or_text_conflicts=x.get('chart_or_text_conflicts',[]),unobserved_followup_or_outcome_limits=x.get('unobserved_followup_or_outcome_limits',[]),review_note=x.get('review_note',''),independent_validation_count=0))
reviews.sort(key=lambda x:x['case_id']);dimensions.sort(key=lambda x:x['case_id'])
assert len(reviews)==102 and {x['case_id'] for x in reviews}==set(dispatch['complete_case_ids'])
assert all(x['all_subjudgments_dispositioned'] and x['method_extraction_complete'] for x in reviews)
for x in reviews:
 if x['case_id'] in dispatch['reuse_completed_case_ids']:assert x==baseline_by[x['case_id']]
dump(BASE/'method-reviews/modern.json',reviews);dump(O/'method-dimensions.json',dimensions)
allcards={x['id']:x for p in (BASE/'rules').glob('*.json') if p.name!='modern-102-consolidated.json' for x in read(p)}
source_ids={x['id'] for p in [BASE/'rules'/('modern-102-'+g+'.json') for g in ['a','a-tail','b','c']] for x in read(p)}

# Each listed branch is selected by reading conditions and author/feedback distinctions,
# not by keyword assignment or same outcome. Canonical entries unify an operation only.
SPECS=[
 dict(key='TARGET-STAGE',title='先分目标与阶段，再匹配成败反馈',conditions=['原问含两个以上结果，或同一事件有前后阶段；必须先写明判断对象、行为和完成标准。','中标≠利润，面试≠试岗，票据≠债权，签约≠离职，浮盈≠兑现；这些目标不可互换。'],steps=['把原问拆为主体—目标—阶段—时间单位四项。','逐作者绑定其原断针对的子目标；含混入局不替作者补成中标或盈利。','分别核已知背景、原载反馈、未覆盖后续；后期失败不能倒洗前期错误。'],claim='在多目标或分阶段条件下，先固定反馈目标，再判支持/反证/未覆盖；只统一这个核对动作，各原作者成败公式继续分支。',members=[('LR26-M102A-018-PROFIT','合同未定仅人脉支出；平本/奖金/不成并存，无最终利润反馈'),('LR26-M102A-028-OFFER','现场面过后试岗败；原面试不成保反证，不借后期失败改中'),('LR26-M102A-030-WEALTH','股票浮盈回吐，初传四月只本作者应期'),('LR26-M102AT-032-PAPER','票据未找到、债人无钱两目标；不认证盗票或贵人收款'),('LR26-M102AT-033-TIMING','10月签约与11月离职；子月、夏末初秋原断不合，亥/戌为后注分期'),('LR26-M102B-056-CONFLICT','金额、次数和两盘冲突，不将一次到账改分两次'),('LR26-M102B-067-RECONCILE','两天复合而非仅联系；未来必分未访'),('LR26-M102C-069-PROFIT','实际中标亏损；不中的原断受反证，岩层非伤亡'),('LR26-M102C-071-MONEY','申日合而申时不合亥时，私人发款不受银行下班预设')],old=['LR26-LEGACY-003','LR26-BOOK-BIFA-029'],exclusions=['不把背景已知当提前发现，不把事后推导回填事前。','这里只归并反馈核对步骤，未认任何两张预测卡整卡等价。']),
 dict(key='ROLE-ACTION',title='固定代占主体与施受方向，再解释克生合冲',conditions=['代问人、当事人、对方或类神不重合，或同案各家给出相反干支定位。','主体必须按原作者原问保存；不能用同一结果倒换坐标。'],steps=['逐作者列干、支、年命、类神分别是谁。','写动作的起点终点及谁主动，区分被克、克出、生入与归支。','用反馈只核角色动作，不以找到/回来等结果证明一种坐标唯一正确。'],claim='在代占或主客争议中，先固定角色坐标与施受再读象；共享这个操作，干孩/干父母、退走/退回来等相反解释保留。',members=[('LR26-M102A-003-ROLE','干女支男相同，主动离方仍相反，不能靠换性别消冲突'),('LR26-M102B-051-ROLE','姐代问妹，角色定位与安全、找到时间分开'),('LR26-M102B-054-TEACHER','教师、学生、家长的施受不合为一个干支主体'),('LR26-M102B-060-INTERROGATE','本人黑脸未直接促供，三日后另一组联合才成；贵救原断反证'),('LR26-M102C-076-RESCUE','干问者支患者与干患者相反，手术稳定不能裁唯一取用'),('LR26-M102C-086-RETURN','学生家长自己回来，求测方努力挽回受反证；退走/退回来继续分支')],old=['LR26-MP10-031-ROLE','LR26-LEGACY-BIFA-008','LR26-BOOK-BIFA-009'],exclusions=['同案多人是同一事件，不累计支持样本。','不同递克结构、干神归支与干加支不因字似归成一法。']),
 dict(key='VOID-OBJECT',title='空实先定作用对象、位置及填实条件',conditions=['作者以旬空、旺空、月建填空或空不受克解释结果；必须记录被空的是财、鬼、救神、胎或阶段。','至少一处存在填实与不填实、空免克与空失效的不同解释。'],steps=['列空的对象、所临位置、日月旺衰和作者是否采用填实。','分别写空对伤害、救援、取财或持续性的作用方向。','同一好结果同时适配相反空法时保冲突，不选择赢家；核不同目标及反馈时间。'],claim='空实解释可归一到对象—位置—作用—填实前提的记录顺序；月建可填和不可填、空免克与旺空不空仍为冲突分支。',members=[('LR26-M102A-021-KEEP','本次打针平安；空免受克与月建旺救不是同一路线，出生未访'),('LR26-M102B-055-VOID','年命和申酉盘文有冲突；月建冲空、救应权重分存'),('LR26-M102C-071-MONEY','辰空财/戌财取法与岁填、旺空分支；拿到工资不能独证某填法'),('LR26-M102C-102-RESCUE','土墓凶与年申化鬼、末冲墓后析；原大凶反证不抹')],old=['LR26-MP10-082-VOID-YES','LR26-MP10-082-VOID-NO','LR26-BOOK-BIFA-098','LR26-BOOK-BIFA-027'],exclusions=['本入口不宣布月建填空普遍成立或不成立。','空鬼、空救、空胎的作用不同；不能只按最后平安直接等价。']),
 dict(key='PREGNANCY-QUESTION',title='胎产先定已孕状态，再分性别、胎安与产期',conditions=['原问是否孕、已孕后安危、男女或生产日期；原已知状态必须明确。','主动终止、自然流产、未孕、未持续孕和未核孕各作不同事件。'],steps=['记录是否已经检查确孕、孕期是否载明。','按作者分别列干胎、支胎、年命胎、五行胎及所用盘，不混双盘坐标。','把未孕、主动终止、胎安、性别和产日分别配反馈；只有生男不能验证亥日。','二阴包阳等同结构若给相反结论，留作者、顺逆条件与反证，不凭结果删法。'],claim='在胎产问题中可归并先定已知孕态及目标的步骤；各胎神体系、阴阳男女与顺序算法保持来源分支，既有确孕后人工终止不能当自然必流证据。',members=[('LR26-M102A-008-CHILD','求孕后来得男不证实际两次受孕或生化'),('LR26-M102A-009-PREG','后来经来与混合验棒，不证明从未孕或确诊输精管病'),('LR26-M102AT-034-SEX','同二阴包阳男女相反；生男只支持性别项，不裁为通则'),('LR26-M102AT-034-BIRTH','无产日、孕周未载，亥日和早孕条件不能称已验'),('LR26-M102B-050-PREG','确孕后主动打掉，不是自然保不住的独证'),('LR26-M102C-078-PREG','反馈未孕无流史；巳胎空与午胎绝两体系不混'),('LR26-M102C-080-PREG','已孕母亲要求终止；无孕强断受反证，盘文异保留')],old=['LR26-BOOK-BIFA-026','LR26-BOOK-BIFA-027','LR26-BOOK-BIFA-029'],exclusions=['不能以经期或文本象链代替原载医学事实的确定程度。','性别单案及同案多作者不构成准确率验证。']),
 dict(key='LOST-COORDINATE',title='失物寻人先定类神与空间层级，得否和生死另核',conditions=['问题涉及失物、失宠或失踪，作者用类神所临/干支内外/包容层级取位置。','同盘不同对象或不同年命、替代月将盘须分开。'],steps=['先存对象及作者为何取该类神；类未定不自动拿反馈地点反选。','写天盘类神、所临地盘、干支内外或容器层级，区分西北、饭店、背包等尺度。','分别核找到、找到活体、返家、方向与具体地点；水沟尸体找到不等活返。'],claim='可以归并明确类神后保坐标及空间尺度的读取动作；羊未临戌西北、公交卡包中和失人遗体属于不同条件，方向、容器、得否与生死不互证。',members=[('LR26-M102A-025-FIND','书包含证件而非只证件，家无饭店得，未时过程为反馈后连接'),('LR26-M102B-038-SHEEP','未羊临戌西北合，受惊不证狗追，具体辰午时无反馈'),('LR26-M102B-048-DOG','白狗根本未丢；黄狗只知未找，不能以错背景立白狗三传'),('LR26-M102B-068-LOSTDEAD','水沟发现尸体，不证明活返、死因或方向'),('LR26-M102C-088-CARD','背包支持而家东北红衣/更衣柜反证；卯玄、巳后多类并存'),('LR26-M102C-092-WATCH','失物追回与盗者性别分项；性别错误不由追回遮掉'),('LR26-M102C-099-DOG','未出门柴犬与双将盘，戌时色象不能合证另一盘')],old=['LR26-BOOK-ANCIENT-003','LR26-MP10-031-ROLE'],exclusions=['同盘或同课名不证明同一算法；不混B043/B048对象。','本入口不把方向近似或找到当死因鉴定。']),
 dict(key='RESCUE-ENDPOINT',title='病占救制固定作用链，并区分存活、稳定与恢复',conditions=['来源以医、德、父母、年命、冲墓或制鬼解释疾病轻重、疗效及结局。','原反馈可能仅脱险、出院、自理或半植物状态，不能自动等于彻底治愈。'],steps=['固定作者的患者、医生和病神坐标，再写救神实际作用于哪一环。','区分生干、化鬼、助鬼、冲墓及年命救应，不以同为父母/长生合一。','分别记录病位、病种、保命、清醒、自理、出院和远期；旧危断遇新反馈保反证。'],claim='救制方法可统一为实际施受链及结局层级的核对；末父化鬼、父母助鬼、冲墓、年命化鬼是不同结构，不因有救或出院归同法。',members=[('LR26-M102AT-033-PARENT','事业异领域对照：寅父母助鬼抗子孙，并非父母生干必救'),('LR26-M102B-062-DANGER','肝癌无救原断后见出院自理，须保反证；不等癌愈'),('LR26-M102C-076-RESCUE','手术后稳定、尚无法切包，不等根治；取用坐标仍冲突'),('LR26-M102C-090-SURGERY','活命但意识未复，不能笼统称手术全成功；远期未验'),('LR26-M102C-095-DEATH','医院去世支持死亡；未月辰日反证申月申日，不能换时中'),('LR26-M102C-102-RESCUE','脑栓塞不重出院反大凶；冲墓/申化鬼后析留分支')],old=['LR26-BOOK-BIFA-005','LR26-MP10-082-VOID-YES'],exclusions=['病种、医疗因果、鬼神原因及未来灾病未反馈者仍未核。','事业父母助鬼仅作施受结构对照，不据此把病占和职业吉凶等价。']),
 dict(key='QUANTITY-UNIT',title='数断保取数、运算、单位与结果口径',conditions=['来源给出金额、刑期、名次、寿限等数断；需要逐作者完整取数链和单位。','同案多个算法或同数不同事件口径须并列，不以最后近似值反选。'],steps=['写取哪支/将/地盘、基础数、相加相乘折半、单位和起算点。','把初判刑期、改判剩余、赔偿净额和总含医药额分开。','保作者未明的舍入、双算法及未反馈中间量；不凭近似命中补公式。'],claim='数断可归并为取数—运算—单位—口径四步记录；本轮未找到足够证据将不同领域的空半或加数统一为一个可执行预测公式。',members=[('LR26-M102A-007-RANK','八专顺三作者自称巧合；第三不证并列或竞争四人'),('LR26-M102B-059-SENTENCE','戌5、7+8=15、5+4空半=7、末午冲子年7四法不合一，初判15后7余分期'),('LR26-M102C-104-COMPENSATION','寅7空折3.5、亥4，实补3.2含医4.4各有误差，不改精确命中')],old=['LR26-BOOK-SHAO-C134'],exclusions=['没有明法的金额/年月名次只存结论，不造数卡。','空折半在不同位置、对象和单位下不自动等价，舍0.5不明继续缺口。'])
]
canonical=[];families=[];comparisons=[];membership=collections.defaultdict(list)
def uniqrefs(items):return list({(x['path'],x['line_start'],x['line_end'],x.get('role'),x.get('author')):x for x in items}.values())
for spec in SPECS:
 memberids=[i for i,_ in spec['members']];missing=[i for i in memberids+spec['old'] if i not in allcards];assert not missing,missing
 selected=[allcards[i] for i in memberids+spec['old']]
 rid='LR26-M102N-'+spec['key'];fid='LF26-M102N-'+spec['key']
 branches=[dict(rule_id=i,conditions=allcards[i]['conditions'],author_phase_feedback_conclusion=allcards[i]['conclusion'],substantive_difference=diff,disposition='共同核对动作归入口；预测条件/作者/反证完整保留在源卡') for i,diff in spec['members']]
 refs=uniqrefs([e for x in selected for e in x['evidence_refs']])
 # Only source-case references already exact in source cards are propagated.
 case_refs=uniqrefs([e for x in selected for e in x.get('source_case_refs',[]) if e.get('case_id')==f"book:{e.get('path')}:L{e.get('line_start')}-L{e.get('line_end')}"])
 caseids=list(dict.fromkeys(e['case_id'] for e in case_refs))
 oldunits=list(dict.fromkeys(i for x in selected for i in x.get('legacy_entry_ids',[])))
 canonical.append(dict(schema='liuren-rule-card-v1',id=rid,title=spec['title'],categories=list(dict.fromkeys(c for x in selected for c in x['categories'])),claim_origin='本轮归纳',review_state='source_checked',status='candidate',conditions=spec['conditions'],conclusion=spec['claim'],reasoning_steps=spec['steps'],exclusions=spec['exclusions'],alternatives=[x['substantive_difference'] for x in branches],limitations=['这是有源分支的规范核对入口，未增加预测定律或准确率证明。','统一共同操作，不宣称源卡整卡同义或彼此可替换；分歧、反证及未知必须沿分支返回。'],evidence_refs=refs,source_case_refs=case_refs,source_case_ids=caseids,support_case_ids=[],counterexample_case_ids=[],legacy_entry_ids=oldunits,relations=[dict(type='条件分支',target_id=i,reason='共同动作已明确，原预测条件及结论不被覆盖') for i in memberids+spec['old']],logic_stages=spec['steps'],canonical_scope='共同操作层；不是预测公式等价类',member_rule_ids=memberids+spec['old'],branch_selector=branches,independent_validation_count=0))
 families.append(dict(id=fid,title=spec['title'],rule_ids=[rid]+memberids+spec['old'],legacy_entry_ids=oldunits,merge_type='共同操作规范入口；预测条件分支保持；源卡不删',common_method='；'.join(spec['steps']),preserved_branches=branches,canonical_rule_id=rid,unresolved=spec['exclusions']+['未认定整卡预测等价；新独立验证0。'],independent_validation_count=0))
 comparisons.append(dict(id='CMP-M102N-'+spec['key'],canonical_rule_id=rid,family_id=fid,new_rule_ids=memberids,existing_rule_ids=spec['old'],shared_conditions=spec['conditions'],shared_action=spec['steps'],branch_comparisons=branches,decision='统一共同操作入口；整卡及预测公式不等价归并',predictive_equivalence_claim=False,source_card_deletion_count=0,independent_validation_count=0))
 for i in memberids+spec['old']:membership[i].append(dict(canonical_rule_id=rid,family_id=fid,scope='上述共同操作；具体分支原样保留'))
dump(BASE/'rules/modern-102-consolidated.json',canonical);dump(BASE/'families/modern-102-consolidated.json',families);dump(O/'substantive-consolidation.json',comparisons)
mapping=[]
for i in sorted(source_ids):
 mapping.append(dict(source_rule_id=i,destinations=membership[i],disposition='规范入口成员，来源分支保留' if membership[i] else '单卡来源分支保留；本轮未证明与规范入口共享足够具体条件',replacement_rule_id=None,source_deleted=False,predictive_equivalence_proved=False))
dump(O/'rule-destination-map.json',mapping)
# Manual semantic classification uses already authored judgment axes, never lexical guesses.
subs=[s for x in reviews for s in x['subjudgments']];byrule=collections.defaultdict(list)
for s in subs:
 for rid in s.get('rule_ids',[]):byrule[rid].append(s)
semantic=[]
for rid in sorted(source_ids|set(membership)|{x['id'] for x in canonical}):
 ss=byrule[rid];r=allcards.get(rid) or next(x for x in canonical if x['id']==rid)
 semantic.append(dict(id=rid,review_scope='E3逐作者源卡' if rid in source_ids else '本轮共同操作规范入口' if rid.startswith('LR26-M102N-') else '仅规范比较涉及的现有卡条件与结论；不是整条旧经验重审',categories=r['categories'],source_judgment_axes=list(dict.fromkeys(s.get('axis','未分轴') for s in ss)),source_case_ids=list(dict.fromkeys(s.get('case_id') for s in ss)),subjudgment_ids=[s['id'] for s in ss],canonical_routes=membership[rid],semantic_basis='逐作者人工拆分和逐卡条件比较；非关键词标签',covers_all_claims=rid in source_ids,independent_validation_count=0))
dump(O/'semantic-classification.json',semantic)
summary=dict(schema='liuren-modern-102-consolidation-v1',registered_complete_cases=102,reused_complete_cases=12,newly_reviewed_cases=90,groups={g:dict(cases=len(xs),subjudgments=sum(len(x['subjudgments']) for x in xs),source_cards=sum(i.startswith({'A':'LR26-M102A-','A-tail':'LR26-M102AT-','B':'LR26-M102B-','C':'LR26-M102C-'}[g]) for i in source_ids)) for g,xs in groups.items()},all_subjudgments=len(subs),new_subjudgments=sum(len(s['subjudgments']) for xs in groups.values() for s in xs),source_cards=len(source_ids),canonical_operation_entries=len(canonical),consolidated_families=len(families),source_cards_with_canonical_route=sum(bool(m['destinations']) for m in mapping),standalone_source_branches=sum(not m['destinations'] for m in mapping),whole_card_predictive_equivalence_merges=0,source_cards_deleted=0,method_restoration_counts=dict(collections.Counter('unknown' if d['method_derivation_restoration_complete'] is None else str(d['method_derivation_restoration_complete']).lower() for d in dimensions)),scope_exclusions=dispatch['excluded_fragment_ids'],independent_validation_count=0)
dump(O/'consolidation-summary.json',summary)
print(json.dumps(summary,ensure_ascii=False))


