"""Reviewed 46–60 as complete source cases; no inferred historical time or chart values."""
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
S='书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
raw=(R/S).read_bytes(); lines=raw.decode('utf-8-sig').splitlines(); sha=hashlib.sha256(raw).hexdigest()
def ref(a,b):
 return dict(path=S,line_start=a,line_end=b,quote='\n'.join(lines[a-1:b]),sha256=sha,role='原书断语')
specs=[
 (46,454,464,'应秀才占前程：妻家生计与晚年禄','事业占','原载断语与结果混合','亦得此课不等于何秀才同事件；月将不同是爱圅判断而非已知参数。原文年命失载，末申勾陈与前盘螣蛇异文保留。'),
 (47,465,476,'徐将仕占前程：涉三渊与历任子息','事业占','原载断语与结果混合','原断历事三授与叙事后续多任、四十五六界限、妻与继子分项保留。末行未署名补论不得全部归为邵氏解释。'),
 (48,477,487,'徐教授占前程：月将贵人、举荐与妻子分问','事业占','原载断语与结果混合','中传亥月将不论空亡但少迟，是此作者本案取舍；原载四妻之数与妻名叙事勿自行补齐缺位。原题正月与析理十月死气差异待校。'),
 (49,488,496,'杨秀才占前程：斫轮不成转水碓生计','事业占','原载断语与结果混合','斫轮虚名与改业生计有原载解释；七十二寿数只有算法未给明确寿终结果，不能与店屋和水碓反馈一同标验。'),
 (50,497,506,'应秀才占前程：铸印走范、坠轩与日支限制','事业占','原载断语与结果混合','若非己卯日不可言死的作者限定必须保留。性格和家庭诸断未逐项反馈，原载坠轿死亡不自动证实全部性格归因。'),
 (51,507,516,'叶助教占前程：赴任、父丧与卯辰巳数','事业占','未载明确反馈','原载十五、十六七与二十三年各有断句及算法，不拼成已验年表；无独立结果仍保留完整方法材料。'),
 (52,517,527,'伊秀才占科试：幕贵出向日贵与年命拱扶','学业占','原载断语与结果混合','原文明确占试则吉，并非出户课在所有问事皆吉；行年长生学堂、命与贵人的组合完整保存。'),
 (53,528,539,'应寺簿占前程：上书、贵多与家庭指责','事业占','原载断语与结果混合','上书十条是叙事，窜贬有若非指明的反事实；宠妾不孝为作者归因，不以道德指责代现实核验。末未署名段丁/丙、申/辛异文保留。'),
 (54,540,549,'马知丞占升迁：登三天不过关','事业占','未载明确反馈','马知丞/宋冯丞异名照录；无独立升迁或母病结果，仍保留子日关与末空的作者解释。'),
 (55,550,560,'赵将仕占武试：虚禄与改文取科甲','学业占','原载断语与结果混合','原题武试、文官科第及赴任是不同目标；二甲二十一名未在反馈段再次逐项确认，改岳庙读书是实际行动后结果。'),
 (56,561,571,'邹大官人占弓马：有马有箭无弓','学业占','原载断语与结果混合','试不中与虚官衔有叙事；黄马伤人、新衣污秽等警告未见实际反馈，不算全部命中，也不删整段作答。'),
 (57,572,582,'龚县尉占前程：兼职增禄与升转区别','事业占','原载断语与结果混合','原题年龄十二九疑讹照录；兼职不等于升转，原载余言皆验是笼统主张，不能拆成每项已有独立记录。'),
 (58,583,592,'郭巡辖占赴任：正任未得与权摄食禄','事业占','原载断语与结果混合','题头郭与反馈邓异名保留；当年十一月上任后又次年八月始到任，按原载权摄/正任阶段分别保存不改写。'),
 (59,593,602,'徐学士占前程：父子恩泽与救制阶段','事业占','未载明确反馈','整段邵先生曰及析曰中含未来年份和事件，未见另署独立结果；保留原作者断语，不冒充新核反馈。'),
 (60,603,612,'谢省元占省试：传出脱气、虚名与行年支持','学业占','原载断语与结果混合','更五次不遂与后叙五甲不是同一个量；五次、五甲及病亡叙事分别保留，造化前定为原作者信念。'),
]
records=[]
for n,a,b,title,cat,feedback,note in specs:
 records.append(dict(schema='liuren-book-case-v1',id=f'BK26-SHAO-{n:03}',title=title,book_title='六壬断案（本地邵彦和案例集）',category=cat,
  source_case_identity=f'book:{S}:L{a}-L{b}',review_state='source_checked',completeness='complete',
  boundary_note=f'逐字审读{a}–{b}及下一案标题，完整保存现存课式、原断、析理、反馈与后注；不补未载时间和身份。',
  question='本轮据原题概括：'+title.split('：')[0],authors=['邵彦和（按原文署名）','爱圅或其他编注者（具体按正文）'],
  source_refs=[ref(a,b)],missing_fields=['未单列明确结果'] if feedback=='未载明确反馈' else [],feedback_status=feedback,
  method_rule_ids=[],same_event_ids=[],chart_fields={},chart_status='原课式完整留存，尚未引擎复算',
  notes=[note,'完整是原文收录口径，不是全案断语皆验；未增加独立验证次数。'],logic_stages=['问事目标','作用关系','条件与阶段'],original_categories=['武试/弓马' if n in (55,56) else '科试/省试' if n in (52,60) else '前程/任职']))
by_n={int(x['id'].rsplit('-',1)[1]):x for x in records}
other_source='书籍库/现代著作/《壬占汇选》.txt'
other_raw=(R/other_source).read_bytes();other_lines=other_raw.decode('utf-8-sig').splitlines()
by_n[58]['source_refs'].append(dict(path=other_source,line_start=8195,line_end=8212,quote='\n'.join(other_lines[8194:8212]),sha256=hashlib.sha256(other_raw).hexdigest(),role='原书断语',same_event=True))
by_n[58]['notes'].append('已实际对读古汇选8195–8212：同将时、课式、任职经过与断语，题头邓巡辖而本书题头郭；作为同事件版本保留，不增独立次数。')
defs=[
 (46,'初期受脱与后段引生分开：妻家起业不等于功名得成',461,463,
  ['应秀才案日上亥及初传均被作者论脱气，初妻财寅引中巳长生，再引末申本身禄。'],
  '本案妻财把后段引回生路，故原作者分早年功名不成、后由妻子起家与晚年享福；不把先脱气固化为终身全凶。',
  ['原断功名不可得而生计末年可成。','析理逐传追踪妻宫、长生、本身与禄。','爱圅禄重于财为后注观点，保留身份。'],
  ['年命已逸、月将未知，不拿45何秀才案参数直接当本案实参。']),
 (48,'月将与生扶改变空亡取舍：原作者在不同对象上分别处理',484,486,
  ['徐教授案中传亥为月将乘贵，原作者说不论空亡但时少迟；巳虽天空而在寅受生。'],
  '保留此案对月将贵人及受生炉象的具体取舍，用以对照不能只见空字即一概取消作用；妻子与官任仍分对象判断。',
  ['中传亥月将用于举荐与官程，作者只保留少迟。','末寅生身与天门用于后段官程。','巳受寅生使原作者不称空炉。'],
  ['月将永不空并未在本轮跨案验证；不把本案取舍升级为引擎硬规则。','正月/十月死气文本差异尚待校。']),
 (49,'课体条件失败后按剩余结构改落生计：斫轮转水碓',495,496,
  ['杨秀才案作者以卯空朽木、戌落空无模范否定仕进用途，保留轮磨之象用于生计。'],
  '先核斫轮的材料、模范及传末条件，再决定其在科名上不成而在店业水碓可用；不能见斫轮名称直接断功名成就。',
  ['卯空与戌落空使作者称徒有斫轮虚名。','临店业转改业求生计，并据同一轮磨象论水碓。','原载权教授虚名和分店屋、水碓生计分别回应。'],
  ['寿七十二仅见数法，不计为本案明确结果。']),
 (50,'铸印乘轩还须核走范破模，强断死亡另有己卯日限定',504,505,
  ['应秀才己卯日，巳玄武加子被作者称走范，卯虎加戌称破模坠轩。'],
  '课名不能代替内部条件核查；原作者由巳卯将神、加临及日支作层层限定，并明说若非己卯日不可言死。',
  ['原课名铸印乘轩与具体结构有冲突。','作者检查上火下水玄武、卯虎与戌的位置后改判。','末句另加日支限定，必须随强断一同保存。'],
  ['该原案限制不是其他日绝无死亡的反向通则。','原载性格与家事断语未获同等逐项结果确认。']),
 (55,'武职虚禄不等于所有功名皆无：改文需另核文象与行动',557,559,
  ['赵将仕问武试，申禄空、太常不入传；末巳乘朱雀又是长生学堂官星。'],
  '原作者先判武职不成，再据文象提出岳庙读书取科甲；失败目标与转向目标分别论，实际读书是后续条件的一部分。',
  ['申禄空用于否定原武职目标。','青龙入庙、朱雀学堂等用于新方向。','不能赴广南后改岳庙、邀友读书与随后科第按时间顺序留存。'],
  ['结果同时包含行动改变，不当作未干预情景已被验证。']),
 (58,'官空与禄合分目标：正任、权摄食禄及后来到任分别判断',590,592,
  ['郭巡辖案寅官龙空、巳禄临支与申合，原文区分正任与权摄。'],
  '官位暂不可得与仍有食禄可以并存；原作者以官空、禄支合及阻碍人物离任区别阶段，不由官空直接推永远无职无收入。',
  ['寅龙不空即赴任，是作者反事实比较。','本盘官空而禄在支合，转为权摄食禄。','陈姓退去后方得正任，原载经过权公使酒税的中间阶段。'],
  ['郭/邓姓名差异原样保存；不凭推测补同一人的确定身份。','官星空亡在其他职业问题的适用条件未由此案完全给出。']),
]
rules=[]
for n,title,a,b,conditions,conclusion,steps,exclusions in defs:
 r=by_n[n];rid=f'LR26-BOOK-SHAO-{n:03}';r['method_rule_ids']=[rid];cr=dict(r['source_refs'][0],case_id=r['source_case_identity'])
 rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=title,categories=[r['category']],claim_origin='原文明示',review_state='source_checked',status='source_method',
  conditions=conditions,conclusion=conclusion,reasoning_steps=steps,exclusions=exclusions,alternatives=['当前仅保存原作者实际取舍，其他解释及迁移边界未被独立排除。'],
  evidence_refs=[ref(a,b)],source_case_refs=[cr],source_case_ids=[cr['case_id']],support_case_ids=[r['id'],cr['case_id']],counterexample_case_ids=[],legacy_entry_ids=[],relations=[],
  limitations=['已读原载结果，独立验证为0。','本案角色、位置、旺衰与时段须随方法一起阅读。'],independent_validation_count=0,logic_stages=['目标区分','关系链','条件检查','阶段变化']))
for rule in rules:
 if rule['id']=='LR26-BOOK-SHAO-058':
  rule['legacy_entry_ids']=['B0252']
  rule['relations']=[dict(type='修订',target_id='B0252',reason='保留原载官空与禄合分目标；原书未见旧卡额外填空或冲空之月应期。')]
for relative,batch in [('book-cases/shao.json',records),('rules/book-shao.json',rules)]:
 p=R/'knowledge/liuren-research/20261102'/relative;d={x['id']:x for x in json.loads(p.read_text(encoding='utf-8'))};d.update({x['id']:x for x in batch});p.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'output/liuren-book-cases-20261102/shao-candidates.json';d=json.loads(p.read_text(encoding='utf-8'));d['reviewed_case_ids']=[x['id'] for x in json.loads((R/'knowledge/liuren-research/20261102/book-cases/shao.json').read_text(encoding='utf-8'))];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_cases':15,'new_methods':6,'read_range':[454,612]},ensure_ascii=False))

from refresh_shao_coverage import refresh
refresh(R)
