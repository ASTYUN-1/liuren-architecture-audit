"""Manually read source cases 61–75. Preserve disagreements and missing feedback."""
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[2];S='书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
raw=(R/S).read_bytes();ls=raw.decode('utf-8-sig').splitlines();sha=hashlib.sha256(raw).hexdigest()
def ref(a,b):
 return dict(path=S,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=sha,role='原书断语')
specs=[
 (61,613,622,'赵公占子国子监试：科第、身体与寿数分项','学业占','戊子生与爱圅己丑生校议并存；申七未八空亡减半未能直接说明三十五的完整算法，不代作者补公式。疾病语言保留历史身份。'),
 (62,623,633,'邵二十一公占孙前程：同课不同年命','事业占','同此数不是赵子同一事件；戊申年及丁亥命是爱圅据年龄校议，不写成原题确定年月。亥本命脱干是后注对断异的解释。'),
 (63,634,643,'何知丞占赴任：旧政重复与赴任迟延','事业占','已待三年为问答中新增事实，再断六年方赴任；不可伪装不知道等待背景便完全独立断出六年。八年丧归与前者分项。'),
 (64,644,654,'陈学谕占前程：墓空渐通与其他不利并存','事业占','开头墓空渐次亨通不覆盖后文考试、疾病、妻与年命；九年而卒及庚申年亡时间张力原样保留。'),
 (65,655,664,'施主簿占前程：无正宅与知录之职','事业占','赘婿无正宅解释含支来就干受克及宅上受脱，不只课名；四丧及己巳有事反馈粒度有限。'),
 (66,665,674,'邵梓材占前程：同日异时与家宅分项','事业占','墓中白蚁与命运的因果为原作者解释，不能因后开墓叙事便全体认证；酒败、眼、妻、宅分项保留。'),
 (67,675,684,'邓省干占前程：长生受扶而贵空所限','事业占','与66同日但时不同，原文明确此课大不同；发解与及第不是一项，三任具体职务与前程级别分开。'),
 (68,685,694,'江司户占官职：鬼生刃与支藏丁','事业占','原文明确此丁是未中有丁、非旬丁；不得把原文术语混写为所有丁神同一口径。三午与三人是原叙对应未明列通用人数法。'),
 (69,695,705,'冯机宜占前程：将时异文、回避与阻服','事业占','卯将戌时原题与爱圅寅将酉时/非十一月异议并存，未按反馈挑一盘；九年端坐、两次回避和母丧分阶段。'),
 (70,706,716,'刘运干占前程：自墓传生与前后妻分别取用','事业占','标题刘与叙事钱异名原样保留；前后妻定位有邵析与爱圅补解，不拼成一个人的连续推理。近九十与八十七原载分列。'),
 (71,717,726,'郑子云占前程：生旺入朝与后段退空','事业占','三奇、禄与长生用于前段，退入空亡用于晚段，不能把中末空简化成从未得官；五府与八座为作者有条件区分。'),
 (72,727,737,'何上舍占前程：催官、德神与寿数差异','事业占','原断五十四、反馈五十三及末段六九五十四均保留，不改为完全吻合；子不得力原断空亡与补论无子爻为不同表达。'),
 (73,738,748,'童七秀才占前程：解额科第、妻家与子息在场','事业占','早段不及第与后来又合主科第须保留时间阶段；不见子息指临终在场，原文明确有二子，不能抽成终身无子。猿迷为原书叙事。'),
 (74,749,758,'陈主簿占迁擢：顾祖归宅与争产问事','事业占','升转之问要与退归本命入宅相对读；自己不是为作者评价，保留权属事件叙事，不以模型替现实案件定责。'),
 (75,759,769,'徐通判占赴任：乱首、受财及仆伤','事业占','原书受财、仆挟及伤人叙事按历史材料保存；移坟可保命是条件性建议，未迁的结果不能验证迁后必免。'),
]
records=[]
for n,a,b,title,cat,note in specs:
 records.append(dict(schema='liuren-book-case-v1',id=f'BK26-SHAO-{n:03}',title=title,book_title='六壬断案（本地邵彦和案例集）',category=cat,
  source_case_identity=f'book:{S}:L{a}-L{b}',review_state='source_checked',completeness='complete',
  boundary_note=f'逐字通读{a}–{b}行及邻案标题，现存盘式、题干、断语、后注与叙事均完整收录；不把后注校议改成原书定论。',
  question='本轮据原题概括：'+title.split('：')[0],authors=['邵彦和（依原载署名）','爱圅及其他编注者（依正文署名）'],source_refs=[ref(a,b)],missing_fields=[],
  feedback_status='原载断语与结果混合',method_rule_ids=[],same_event_ids=[],chart_fields={},chart_status='原课式保存；本批未引擎复算',
  notes=[note,'原载反馈仅覆盖原文明确子问；本轮独立验证为0。'],logic_stages=['对象与目标','作用关系','条件核查','阶段变化']))
by_n={int(x['id'].rsplit('-',1)[1]):x for x in records}
defs=[
 (62,'同课不等于同事件或同结论：年命解释须保留校议身份',623,631,
  ['邵二十一公孙案与前一赵子案同课；爱圅按年龄推戊申占、丁亥命，另以亥命脱干解释凶较甚。'],
  '保留同课比较所用年命与问事对象，不用盘相同直接合并两事件或迁移全部结论；本案年命补全仍标后注校议。',
  ['题头同此数而人物不同。','爱圅明确据年岁补占年及孙命。','文末课同断异因亥本命而脱干是后注解释，不归作邵氏原话。'],
  ['未用引擎或其他原本核定补入年月；不把此校议当确定排盘输入。']),
 (64,'墓空只解除对应阻碍，不等于考试及家人所有方面皆吉',651,652,
  ['陈学谕案干支皆墓，原作者先喜本身墓未空，再另论初传六害、太阴、年命及妻宫。'],
  '本案墓空渐通是局部作用，后续考试与家事仍有各自不利条件；使用时逐项追踪所解除的阻碍，不把墓空扩为全案转吉。',
  ['先定位本身墓空、渐次脱去。','再分别检查考试初传、妻宫和年命。','原载疾病与死亡时间有文字张力，未以结果一刀推翻或证明每项判断。'],
  ['只保存原作者分项方式；历史疾病解释不作为当前医学因果。']),
 (67,'长生生扶与贵空同时存在：发解、及第及职务级别分层',682,683,
  ['邓省干案日上申长生学堂，初巳贵德空，寅生巳生贵德；原作者断可发解但不能及第。'],
  '扶身与贵空分作用层次：本案并非一空便全无前程，也非得长生便科名全成；科名等级和后续实际职务分别保留。',
  ['先看干支受生与长生学堂。','再以贵空和玄滞限其科名层级。','寅生贵德与三传象另用于任职与具体业务。'],
  ['发解结果与及第是不同考试层级，不合并成笼统考中。']),
 (68,'原书丁神有支藏口径：未中丁须与旬丁区分',692,693,
  ['江司户案正文明确未中有丁，非旬丁，并在鬼生午刃与支合关系中解释。'],
  '提取方法时标清作者使用的是未支藏丁，不可误记为旬遁丁神；原文丁主动须连同本案关系使用。',
  ['原断先讲鬼生午刃与支上未合。','析理明言未中有丁、非旬丁。','丁主动与天空空屋是原作者在本案的后续解释。'],
  ['本轮不据此替换现有引擎旬丁输出，也不把三午固定成三名死者通则。']),
 (72,'旬丁乘蛇也须看德神：作者明确不作怪异解释',734,736,
  ['何上舍案巳旬丁作蛇，原作者指出辛以巳为德神，故不云怪。'],
  '保留原作者以德神限制旬丁螣蛇怪异取象的取舍；同一神将符号需要结合日干关系和问事目标。',
  ['巳既有旬丁、螣蛇身份。','原文明说不云怪者，辛以巳为德神。','官星催官与后来阻服寿数另分目标，不混入怪异解释。'],
  ['五十四断数与五十三结果不一致；不能把本案全断标为精确命中。']),
 (73,'无子爻与临终不见子息：必须按原问时间范围解读',745,747,
  ['童七秀才案原断终于奴婢之手不见子息，后载二子归秋试、奴婢办后事，子后归扶丧。'],
  '本案不见子息指临终未在场，不能由传中无子爻改写为一生无子；人物存在与阶段在场是不同子判断。',
  ['原断把临终无人子息在侧与家中后来的喜事并列。','原叙明确有二子并赴秋试。','末析传中无子爻须放回临终这一语境。'],
  ['该限定来自本案上下文，不推成所有无子爻皆指临终不在场。']),
]
rules=[]
for n,title,a,b,conditions,conclusion,steps,exclusions in defs:
 r=by_n[n];rid=f'LR26-BOOK-SHAO-{n:03}';r['method_rule_ids']=[rid];cr=dict(r['source_refs'][0],case_id=r['source_case_identity'])
 rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=title,categories=[r['category']],claim_origin='本轮归纳' if n in (62,64,73) else '原文明示',review_state='source_checked',status='candidate' if n in (62,64,73) else 'source_method',
  conditions=conditions,conclusion=conclusion,reasoning_steps=steps,exclusions=exclusions,alternatives=['原书取舍与编注异说并存；没有独立排除其他解释。'],
  evidence_refs=[ref(a,b)],source_case_refs=[cr],source_case_ids=[cr['case_id']],support_case_ids=[r['id'],cr['case_id']],counterexample_case_ids=[],legacy_entry_ids=[],relations=[],
  limitations=['原文明示与本轮归纳按claim_origin区分。','已读原载结果，独立验证为0。'],independent_validation_count=0,logic_stages=['对象边界','条件取舍','反馈粒度']))
for relative,batch in [('book-cases/shao.json',records),('rules/book-shao.json',rules)]:
 p=R/'knowledge/liuren-research/20261102'/relative;d={x['id']:x for x in json.loads(p.read_text(encoding='utf-8'))};d.update({x['id']:x for x in batch});p.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'output/liuren-book-cases-20261102/shao-candidates.json';d=json.loads(p.read_text(encoding='utf-8'));d['reviewed_case_ids']=[x['id'] for x in json.loads((R/'knowledge/liuren-research/20261102/book-cases/shao.json').read_text(encoding='utf-8'))];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_cases':15,'new_methods':6,'read_range':[613,769]},ensure_ascii=False))

from refresh_shao_coverage import refresh
refresh(R)
