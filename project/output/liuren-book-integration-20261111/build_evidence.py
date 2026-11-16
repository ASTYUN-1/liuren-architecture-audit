"""Capture contiguous source spans and the user's 24 selections without editing the book."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
SOURCE='书籍库/北海闲人/理法简易.txt'
p=ROOT/SOURCE;raw=p.read_bytes();lines=p.read_text('utf-8-sig').splitlines()
sha=hashlib.sha256(raw).hexdigest()
assert sha=='afd2707315061e9423d8d444e00c3e9cce497c304449be8c37bcdb0d5aa19279'
def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
ranges=[('B41-气势',3033,3137),('B41-阴神施受取数',3143,3347),('B41-理气概括',3379,3419),
 ('B41-财阴补充',3441,3467),('B41-迟速与类阴',3535,3565),('B41-年命',3783,3805),
 ('B41-类神课传',3807,3899),('B41-旺衰神将',4005,4025),('B41-相貌',4189,4219),
 ('B41-发用制救类聚动静',4895,5017),('B41-空亡全节',5467,5610),('B41-寄宫空续论',5611,5693),
 ('B41-空亡减数原载',6671,6671)]
spans=[]
for ident,a,b in ranges:
 spans.append({'id':ident,'path':SOURCE,'line_start':a,'line_end':b,'line_mode':'universal','sha256':sha,
  'quote':'\n'.join(lines[a-1:b]),'role':'北海著作：含所引古籍原文及北海解释，逐句身份需依上下文分辨','author':'北海闲人及原文明确所引作者'})
spec=[
 (1,3184,'五、发用的气势。','发用气势','book-logic','补全多维气势及按占类使用'),
 (2,3096,'虎蛇同为凶将','虎急蛇缠','book-logic','原将象页已有峻烈，补明确迟速比较'),
 (3,3294,'以上三个小节，阐述的是主象阴神','阴神方法','book-logic','连读上文与下文，分扶类/益我/原因/迟速'),
 (4,3310,'干上神代表自身状况','阳显阴藏','book-logic','用户采用推广到物、项目与承接，保留条件'),
 (5,3358,'依照财爻出现的位置来定迟速','位置迟速','book-logic','推广关键类神，保留入课传等条件'),
 (6,3380,'财的新旧，孟新，仲中，季旧','取数与旺衰','quantity-strength','新增LF具名分支、数量修正核对'),
 (7,3460,'得之难易，以干支为双方','理气推理','book-logic','分成败、难易、迟速、规模、数目、新旧'),
 (8,3510,'《壬归》一向主张','财阴推广','book-logic','类阴生类与益我分层'),
 (9,3602,'应期的断法，类神入课传','迟速与四建','book-logic','区分类现与发用参考，四建不一刀切'),
 (10,3610,'财上天官，主财之类','类神与施受者','book-logic','所求种类、背后条件、出财者及其顾虑分开'),
 (11,3846,'一般说来，命主一生','命固有年当前','nianming','补充时段职责，限制人格宿命化'),
 (12,3850,'占一般的事情，年重于命','年命职责','nianming','当前可超一年，专项不固定年胜命'),
 (13,3878,'实际上“相需并用，占法斯全。”','类神与课传','book-logic','按用户修订类不现继续找而降低显明性'),
 (14,3898,'壬课判断的主要标准是类象','天时地利与扶我','book-logic','并入类神完整条件；用户未另写该项说明'),
 (15,3940,'视类将者，吉凶在所乘神','气地与神将','book-logic','完整连续段吸取'),
 (16,3940,'视类将者，吉凶在所乘神','神将作用','book-logic','与15同源去重，减力不归零'),
 (17,4070,'六壬扶阳抑阴，喜旺忌衰','旺衰改变表现','book-logic','沿U02，并按用户意见弱化名称吉凶'),
 (18,4244,'第五节 婚姻占占相貌的方法','相貌','relationship','简要专法，稳定禀受/当前容貌'),
 (19,4970,'但如果发用能制干上之鬼','发用制四课','book-logic','明确跨课传作用与时序'),
 (20,4976,'六壬中“类聚”的力量甚大','类聚','book-logic','看共同实际作用，不计名字票数或强加倍数'),
 (21,4984,'为什么特别强调日上和支上都要','施受双方旺衰','book-logic','能给、愿给、能取及通路分开'),
 (22,5050,'这一小节谈的是动的快慢','整体气势','book-logic','快慢、大小、虚实、持续分维度'),
 (23,5026,'一小节讲的是能否成行','动与解除','book-logic','扩展转岗调动等状态转换，不只地理移动'),
 (24,5522,'三 空亡详释','空亡全节','void-class-applications','全节并寄宫续论，分类及冲突分层')]
selections=[]
for n,annotation_line,key,title,module,action in spec:
 hits=[i+1 for i,s in enumerate(lines) if key in s]
 assert len(hits)==1,(n,key,hits)
 source_line=hits[0];refs=[s['id'] for s in spans if s['line_start']<=source_line<=s['line_end']]
 # Selection 13 is an introductory sentence just before the illustrated class/structure discussion.
 assert refs,(n,source_line)
 selections.append({'selection':n,'annotation_line':annotation_line,'source_line':source_line,'source_line_mode':'universal',
  'title':title,'runtime_module':module,'integration':action,'evidence_ids':refs})
evidence={'schema':'liuren-book-annotation-evidence-v1','release':'20261111-book-logic-41','source_sha256':sha,'spans':spans,
 'selections':selections,'source_limits':'项目内电子文本，未核影印底本；全文摘录校验不替代语义判断。',
 'user_decision':{'id':'V41-01','quote':'此处先保留现行，后续由我仔细研判。','scope':'神生其将且神自空，出旬可望与出旬亦无望','effective_policy':'U08/U10 unchanged; deferred user review'},
 'reported_quantity_case':{'identity':'用户本轮口述的开发例','base':40,'strength_approximately':2.9,'requested_quantity_factor':0.5,'result':20,'unit':'分','original_chart_verified':False,'feedback_independently_verified':False},
 'independent_validation_count':0}
save(OUT/'book-annotation-evidence.json',evidence)
md=['# 24处批注：上下文摘录及接入对照','',f'原书：{SOURCE}；SHA256 `{sha}`。行号LF-U按Python通用换行计。',
 '原书含CRCRLF，编辑器/rg的LF行号可能不同；以下完整复制连续原段，并以LF-U标注每行，避免混号。','',
 '| 批注 | 主题 | 原书LF-U | 接入 |','|---|---|---|---|']
for s in selections:md.append(f"| {s['selection']} | {s['title']} | {s['source_line']} | {s['integration']} |")
for s in spans:
 md += ['',f"## {s['id']}（LF-U{s['line_start']}—{s['line_end']}）",'', '```text']
 md += [f'{i}: {lines[i-1]}' for i in range(s['line_start'],s['line_end']+1)]
 md += ['```']
(OUT/'24处批注-原文与接入对照.md').write_text('\n'.join(md)+'\n','utf-8')
# Register source-backed maintenance cards. Active execution uses the versioned runtime,
# not a search of this research library.
groups=[('气势',1,'发用气势及虎蛇迟速','B41-气势'),('阴神',3,'类神阴神与表里条件','B41-阴神施受取数'),
 ('取数',6,'类神地盘取数与数量修正职责','B41-阴神施受取数'),('理气',7,'理气分项推理与属性','B41-理气概括'),
 ('迟速',9,'关键类神位置与气态迟速','B41-迟速与类阴'),('年命',11,'命固有与年当前的职责','B41-年命'),
 ('类传',13,'类神优先与课传过程','B41-类神课传'),('神将',16,'神将减权与气地能力','B41-类神课传'),
 ('相貌',18,'婚姻容貌的稳定与当前','B41-相貌'),('制救',19,'发用作用四课及行动解除','B41-发用制救类聚动静'),
 ('空亡',24,'空亡逐类推与阶段','B41-空亡全节'),('寄宫空',24,'寄宫空与实现路径','B41-寄宫空续论')]
cards=[]
for label,n,title,eid in groups:
 s=next(s for s in spans if s['id']==eid);selection=next(x for x in selections if x['selection']==n)
 cards.append({'schema':'liuren-rule-card-v1','id':'LR26-BOOK41-'+str(n)+'-'+label,'title':title,'categories':['通用'],
  'claim_origin':'本轮归纳','review_state':'source_checked','status':'candidate',
  'conditions':['先依占类明确对象、位置、阶段与目标','具体条件见活动41版'+selection['runtime_module']+'及原连续段'],
  'exclusions':['原文强语不作无条件成败开关','跨占类推广属于用户本轮采用约定，不冒称作者逐字明示'],
  'conclusion':selection['integration'],'reasoning_steps':['分对象职责','核气地、阴神及施受','处理实际作用和最强反证','按本问分别回答'],
  'alternatives':['同对象同条件仍互斥才列矛盾；V41-01保留现行待用户研判'],
  'evidence_refs':[{'path':SOURCE,'line_start':s['line_start'],'line_end':s['line_end'],'quote':s['quote'],'sha256':sha,'role':'本轮解释','author':'整理者；连续证据内有北海及所引古籍原文'}],
  'support_case_ids':[],'counterexample_case_ids':[],'legacy_entry_ids':[],'relations':[],
  'limitations':['原书电子本未核扫描','开发案例不作独立预测验收','当前候选卡的身份不替代活动方法执行约定'],
  'independent_validation_count':0})
save(ROOT/'knowledge/liuren-research/20261102/rules/book-annotation-20261111.json',cards)
print('Captured',len(selections),'selections,',len(spans),'contiguous source spans,',len(cards),'research cards')
