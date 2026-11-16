"""Rebuild only explicitly reviewed Shao cases; candidate headings are not reviewed."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
raw = (ROOT / SOURCE).read_bytes()
lines = raw.decode('utf-8-sig').splitlines()
digest = hashlib.sha256(raw).hexdigest()

def ref(a, b, role='原书断语'):
    return dict(path=SOURCE, line_start=a, line_end=b, quote='\n'.join(lines[a-1:b]), sha256=digest, role='原书断语')

def write(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Every entry below was read with its adjoining case boundary. No inferred reconstruction.
specs = [
    (1,11,20,'韩太守占祈雪','天时占','何时有雨雪、天气如何转变及积雪深度？','己','巳戌卯','巳(玄武)','铸印,乘轩,知一,励德','原载断语与结果混合',
     ['原断说次日，析理又说当日有，时间表述张力原样保存。','原载积雪七寸不证明所有铸印课均有同样雪量。']),
    (2,21,29,'十二月戊申日占晴雨','天时占','冬月晴雨及下雪、转晴起风的变化如何？','戊','辰申子','辰(玄武)','元首,润下,励德,六仪','原载断语与结果混合',
     ['本案原文无具体年份，不补公历；春占水涨是作者对照说法，并非本案春季另一次反馈。']),
    (3,30,36,'州官占雨（原载断语遗失）','天时占','浙江旱情下占雨。','癸','丑戌未','丑(勾陈)','伏吟,乱首,励德,游子,稼穑','未载明确反馈',
     ['原文明示断语遗失；保留现存盘式，不能补断后计完整。','标题先写庚辰日又写癸丑日，时间文字冲突待核。']),
    (4,38,47,'张九翁占宅：生宅脱人与后续家计','家宅占','家宅、人身及家计后续兴衰如何？','庚','巳寅亥','巳(勾陈)','元首,元胎','原载断语与结果混合',
     ['断语与反馈并载，十一年守寡等并非所有细节均有逐项结果核对；保留反馈范围。']),
    (5,48,57,'叶助教占宅：赘婿课与尊长归葬分家','家宅占','家宅未来是否破败、门户如何变化？','辛','卯申丑','卯(玄武)','重审,励德,不备,斫轮,赘婿','原载断语与结果混合',
     ['同名叶助教其他日期课不能自动并案；本案辛卯日子将未时。','还俗僧、归葬及六年家分是本案原载判断及结果，不作为普遍确定结论。']),
    (6,58,67,'邵三翁占宅：妻为主与兄妻身份条件','家宅占','夫妻、宅地及后续年限如何？','辛','卯申丑','卯(天后)','重审,斩关,励德,不备,斫轮,乱首','未载明确反馈',
     ['原文未另给明确结果，不妨碍学习“若申不空则不可乱断”的限制。','原书“然不加申酉空亡”语句疑有讹字，不擅改；原断目下丧妻与九年相守并存，角色/阶段待核。']),
    (7,68,77,'邵秀才占宅及父母：不备取用与家产','家宅占','家宅、兄弟家产及父母状况如何？','乙','辰卯寅','辰(青龙)','不备,弹射（原断所称）','原载反馈',
     ['“后分毫不爽”是笼统原载，不等于逐子问独立核实。','末尾“此课必须仔细研读”括注作者不明，不能归给邵氏。','原载辰为勾陈与盘中辰乘青龙应分神支象义和所乘天将，不代原作者消解。']),
    (8,78,87,'邵巡检占宅：水局脱气与任职子息分问','家宅占','家宅、子息耗费及任职迁转如何？','庚','辰申子','辰(青龙)','元首,润下,不备,励德,闭口','原载断语与结果混合',
     ['长期生育与寿数描述为历史材料，不作为当前医学解释。','原文“子加申、子九申七”取六十三是本案作者数法，未提供通用乘数选择规则。']),
    (9,88,97,'任三翁占宅：婢去复归与纷扰终止','家宅占','家宅纷争及婢女离去后是否返回？','壬','子巳戌','子(白虎)','知一,退茹,斩关','原载反馈',
     ['原载“果一一如占”无逐项独立记录，保留为原书结果主张。','末空与绝乡指纷扰收束，不概括为一切事情末空皆吉。']),
    (10,98,106,'邵伯达占宅基：未有宅基另寻长生','家宅占','欲迁外居，能否求得新宅基、从何处成就？','庚','子巳戌','子(青龙)','铸印,知一,蓦越','原载断语与结果混合',
     ['求新宅基与已有家宅吉凶不同；支上空不直接推出永远无宅。','丁巳年造宅是原载结果，原文未给完整统一的推年算法。']),
]

records = []
for n,a,b,title,cat,question,day,trans,use,types,feedback,notes in specs:
    rid=f'BK26-SHAO-{n:03}'
    caseid=f'book:{SOURCE}:L{a}-L{b}'
    records.append(dict(schema='liuren-book-case-v1', id=rid, title=title, book_title='六壬断案（本地邵彦和案例集）',
        category=cat, source_case_identity=caseid, review_state='source_checked',
        completeness='fragment' if n==3 else 'complete',
        boundary_note=f'完整保留原编号{n:02}的标题、课式和现存文字至第{b}行；已阅读下案标题核边界。第03案后宅墓类别标题不归入本案。第10案原文后直接接11案，无空行亦不截断析理。',
        question='本轮据原题概括：'+question,
        authors=['邵彦和（原载“邵先生曰／先生析曰”）','编录者及未署名括注（身份按原书保留）'],
        source_refs=[ref(a,b)], missing_fields=['原文明示断语遗失','结果未载'] if n==3 else (['未单列明确结果'] if n==6 else []),
        feedback_status=feedback, method_rule_ids=[] if n==3 else [f'LR26-BOOK-SHAO-{n:03}'], same_event_ids=[],
        chart_fields={'日干':day,'三传':trans,'发用':use,'课体':types},
        chart_status='按原书课式逐字登记，未重新排盘；内部文字疑点见notes',
        notes=notes+['原书整案作为方法开发材料；原载反馈不等于本轮独立验证。'],
        logic_stages=['占问拆分','原载取用','条件核对'], method_type='原书完整案例' if n!=3 else '原书残案'))

# Source-backed observations. Their scope is this author's stated application, not universal prediction.
methods = {
 1: ('祈雪：分开风、雨、雪的阶段，并保留原断与析理的时间差',
     ['本案冬月己卯日祈雪，课传巳戌卯，原断同时给风、雨、雪与厚度。'],
     '可学习原作者把风起转寒、微雨、降雪分阶段论述；析理所用火水加临与季节条件需随案保存，不能只留下铸印必雪四字。',
     ['原断列次日巳时风、未时雨、亥时雪；叙事分别记录天气变化。','析理以巳临子、玄武、日上水、末卯白虎等组合解释，另比较春夏秋与冬。'],
     ['原断次日与析理当日文字相抵，不能统一改成今日必雪。','七寸缺明确取数步骤，不能外推雪量算法。'],['B0299'],18,19),
 2: ('冬月润下占晴雨：季节改变同一水局的事件解释',
     ['原例十二月戊申日子将申时，辰申子润下，原文连述玄武、青龙。'],
     '原作者把春季水涨与冬季大雪分开取象；可参照这一季节比较动作，不能把润下在所有季节固定为同一天气。',
     ['先据原文润下与神将水象组合。','原文明确“若春占主水涨，今冬占必有大雪”。','原载结果另列辛亥雨、丙辰雪、戊午晴风。'],
     ['原文没有展开三个应日如何计算；不能补造统一应期步骤。'],[],28,28),
 4: ('占宅：生宅与脱人可以并存，需固定施受双方',
     ['张九翁占宅例庚寅日，巳寅亥三传，原文论庚生巳、寅生亥及两者受脱。'],
     '原作者把住宅受生与本人被耗分开，并以传递与具体家事解释先兴后衰；生宅不能直接写成全家所有方面均吉。',
     ['保留原文庚与寅分别所受生、脱的关系。','末亥生宅同时脱干，原作者据此论因宅役、婚嫁等费财。','原载多项结果分别保存，不把一项费用证实为所有年限均验。'],
     ['十一年守寡与后五年分家等不同子问不可混成同一应期。'],[],45,46),
 5: ('赘婿占宅：太岁、宅、人、墓的作用链须逐层保存',
     ['叶助教辛卯日占宅，原文同时论太岁入宅、支来就干及末丑墓。'],
     '可学习原作者逐层追问谁克宅、宅归何处、墓与尊长如何联系；不以赘婿课名独断家破或还俗僧。',
     ['原断先说支来就干为干所制，再论太岁入宅克宅。','析理再引末丑临太岁、丑生申及庚辛墓丑。','僧人/尊长/分家细节与本案具体支神关系和原载结果分别记录。'],
     ['僧与还俗的象义是原书传统推断，单见申或辛不足照搬人物身份。'],[],55,56),
 6: ('兄妻身份：原作者明确以申空为限定，不将妻上同类单项定身份',
     ['邵三翁辛巳日占宅，卯取妻，申加卯乘天空，原载旬空申酉。'],
     '保留原作者“若申不空，则不可乱断”的限制；同类临妻不能脱离此案组合和限制，直接给出现实亲属关系的确定判断。',
     ['原文先以辛卯、天后论妻，再定位申同类在妻上。','另以申酉空亡及天空说明所断兄已亡、妻身份。','原作者亲自指出申不空不可照此乱断。'],
     ['该限制针对此推断，不表示申不空时现实中绝无该关系。','原文疑似讹字及未载反馈均保留，原断的不同妻子/时间阶段不明。'],[],65,66),
 7: ('邵秀才案：保留原作者不备取用争点，不从单案扩为通用排盘改写',
     ['原例乙巳日戌将亥时，原作者认为干支同见之位不能重复据以取用。'],
     '本案可学习作者先核四课与取用依据再论结果的做法；既有B0122应连读本案精确结构，不能直接改写全部排盘算法。',
     ['原文逐课解释为什么不由第四课取元首。','转以日遥克取辰，名弹射，随后才论宅与兄弟父母。'],
     ['现代计算规则与历史口径异同未在本轮复算；原载成功不能独立证明全部取用通则。','文末提醒括注身份未知，不当邵氏原话。'],['B0122'],75,76),
 8: ('占宅兼问任职：子息耗身、住宅迁移与官任应分开提取',
     ['邵巡检庚辰日占宅，原载同时含子息、迁居、前后任与寿数。'],
     '原书把金日水局脱气用于子息耗费，官任地点与迁宅另有叙述；应按子问保存依据，不能以一条水局主凶覆盖全案。',
     ['原文论日辰受脱与青龙等关系，用于子息/耗费。','任职初不合末吉、后任水陆处与住宅迁移分别保存。','十二年、六十三各有不同取数呈现，不拼成统一算法。'],
     ['术数耗气、生育与寿数语言保留历史身份，不转为当前医学因果。','算法选择依据不足，不能由一次六十三取数归纳普遍乘数法。'],[],85,86),
 9: ('家宅婢去复归：取宅阴神、合及牙人之象时保留完整关系',
     ['任三翁壬寅日占宅，原文把婢妾纷争、遣出后再归及纷扰收束分开。'],
     '原作者以宅之阴神、辰酉合与勾陈牙人解释再归；末空绝乡用于纷扰结束，应限定在此目标，不能泛称末空一律吉。',
     ['先保留原断婢去复归这一具体子问。','析理注明天盘酉阴神寅加酉、酉加辰与辰合、勾陈夹住等环节。','末空绝与甲辰乙巳停止纷扰是另一判断，分别关联。'],
     ['果一一如占没有逐日反馈细节，不能据此独立认证每个应日。'],[],95,96),
 10: ('求新宅基：支上空后另察长生，不把现无宅基等同永远求不得',
     ['邵伯达庚寅日求迁外居，原书支上空且初传青龙脱气落空，中传巳为日长生。'],
     '原作者先辨当前宅基未定，再转察中传长生所指的新宅来源；取用随求新宅这一目标展开，不能套成已有家宅安危。',
     ['日为人、辰为宅，先查支上空，区分未有宅基及暂住。','中传巳长生另论老妇人店业，原文再列方位、尊长与干仆。','原载后来买得及丁巳造宅，分别保存交易成就与建成时间。'],
     ['未载完整推年步骤，不能把丁巳建成反馈当已提取应期算法。'],[],105,106),
}
rules=[]
for record in records:
    n=int(record['id'].rsplit('-',1)[1])
    if n not in methods: continue
    title,conditions,conclusion,steps,exclusions,old,a,b=methods[n]
    source_ref=dict(record['source_refs'][0],case_id=record['source_case_identity'])
    rules.append(dict(schema='liuren-rule-card-v1', id=f'LR26-BOOK-SHAO-{n:03}', title=title,
        categories=[record['category']],claim_origin='原文明示',review_state='source_checked',status='source_method',
        conditions=conditions,exclusions=exclusions,conclusion=conclusion,reasoning_steps=steps,
        alternatives=['保存原书解释供方法参照；本轮未排除其他解释，未建立独立效果证据。'],
        evidence_refs=[ref(a,b,'原载邵氏断语及析理；其中结果叙述按原文区分')],
        source_case_refs=[source_ref],source_case_ids=[record['source_case_identity']],
        support_case_ids=[record['id'],record['source_case_identity']],counterexample_case_ids=[],legacy_entry_ids=old,
        relations=[dict(type='条件分支',target_id=x,reason='同一原书案例方法的精确条件补充；不增加独立证据。') for x in old],
        reference_value=['保存原作者实际使用的对象、位置、条件和取舍，供同类问题对照。'],
        limitations=['本批已读原载结果，属于方法开发暴露；独立验证次数为0。','原载断语与后编叙事身份照录；没有独立证据确认析理写于结果之前。'],
        independent_validation_count=0,method_type='原载判断方法',logic_stages=['目标与子问','定位施受','条件与例外']))

# This script owns the Shao files. Preserve future reviewed batches rather than truncate them.
for record in records:
    text='\n'.join(x['quote'] for x in record['source_refs'])
    unquoted={k:v for k,v in record['chart_fields'].items() if v not in text}
    record['chart_fields']={k:v for k,v in record['chart_fields'].items() if v in text}
    if unquoted:
        record['notes'].append('负责人按盘栏结构摘录（未逐字连续定位，不入META）：'+json.dumps(unquoted,ensure_ascii=False))
for rule in rules:
    if rule['id'] in {'LR26-BOOK-SHAO-001','LR26-BOOK-SHAO-007','LR26-BOOK-SHAO-008','LR26-BOOK-SHAO-009'}:
        rule['claim_origin']='本轮归纳'
        rule['status']='candidate'
for path,batch in [('knowledge/liuren-research/20261102/book-cases/shao.json',records),('knowledge/liuren-research/20261102/rules/book-shao.json',rules)]:
    existing=json.loads((ROOT/path).read_text(encoding='utf-8')) if (ROOT/path).exists() else []
    lookup={x['id']:x for x in existing}
    lookup.update({x['id']:x for x in batch})
    write(path,list(lookup.values()))

heads=[(i+1,s) for i,s in enumerate(lines) if re.match(r'^\s*\d+[）)]',s)]
write('output/liuren-book-cases-20261102/shao-candidates.json',dict(source=SOURCE,sha256=digest,
    discovery='编号标题扫描仅作候选；151缺右括号、141重复、177/218未由模式检出，需逐段核边界。',
    complete=False,reviewed_case_ids=[r['id'] for r in json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/shao.json').read_text(encoding='utf-8'))],
    candidates=[dict(line_start=a,heading=s,state='pending') for a,s in heads]))
print(json.dumps({'reviewed':len(records),'complete':sum(x['completeness']=='complete' for x in records),'fragment':1,'methods':len(rules),'candidate_headings':len(heads)},ensure_ascii=False))

from refresh_shao_coverage import refresh
refresh(ROOT)
