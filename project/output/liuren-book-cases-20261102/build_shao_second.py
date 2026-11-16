"""Explicitly reviewed Shao 11–20. Retains textual conflicts and unknown authors."""
import build_shao_batch as base
import json
from pathlib import Path

ROOT=base.ROOT
ref=base.ref
rows=[
 (11,107,116,'童保仪占宅：极阴、宅上与归计取数','丁','丑亥酉','丑(勾陈)','重审,不备,间传,极阴,寡宿,赘婿','原载断语与结果混合',['盘中申位天将写丑，疑转录误字，未校原图；现存整段原样保存。','卯酉六数、巳亥四数是原载取数，不见阴数统一减半的说明。']),
 (12,117,127,'郑宣义占宅：三个巳的财绝取舍与后注争议','癸','酉丑巳','酉(天空)','涉害,从革','原载断语与结果混合',['附论两种解释作者未明，爱圅另指出两店与末传定位分歧。','不能把先生附论、一人论与爱圅意见拼作邵氏同一判断。']),
 (13,128,137,'王德卿占宅：原断寿数与弟子、编者解释冲突','壬','亥子卯','亥(天空)','伏吟,励德,三奇,杜传','原载断语与结果混合',['原断二十六年、结果十六年，数字冲突不能修成全验。','原文明确质疑四亥乘四为弟子增辞；行年墓太岁说以或、毋乃表示推测。']),
 (14,138,147,'童得松占宅：迁居后的结果与德丧解释分歧','壬','巳亥巳','巳(太阴)','反吟,元胎,励德,斩关','原载断语与结果混合',['邵氏析理称亥德闭口，爱圅称亥德临绝；两说保留。','迁店后户宁祸解属于采取行动后的结果，不写成原未迁情景实际发生。']),
 (15,148,157,'徐八公占宅：极阴后转迎阳与家业变化','癸','未巳卯','未(太阴)','遥克,蒿矢,间传,不备','原载断语与结果混合',['极日极阴与后续迎阳并载，不可截成六阴相继必败。','作者取妻妾、子女身份及寿数均属原载解释，非本轮独立认证。']),
 (16,158,167,'刘将仕占宅：财局耗损、沟渠与家计','戊','辰申子','辰(玄武)','元首,润下,励德,六仪','原载断语与结果混合',['己酉年五月另注六月朔未交小暑，月序口径按原文保留。','财局、盗神、家人费用等不同解释不合并为所有财局皆失财。']),
 (17,168,177,'何丞务占宅：人多欲出与宅克人区别','戊','巳戌卯','巳(太常)','重审,铸印,斩关','原载断语与结果混合',['年命有丁巳五十三与古本丁未六十二异文，不能任选一版冒称唯一。','十三年争讼与后仍兴旺可以共存，分结果层次。']),
 (18,178,190,'任太公占宅：牛与田、马与屋的条件选择','丙','酉巳丑','酉(太阴)','弹射,从革','未载明确反馈',['本案五条原断未附明确现实结果，方法照样保留。','原文用*遮蔽一字，保留缺字符；不影响主要取象关系但不可补字。']),
 (19,191,200,'王解元占宅：长生救制与各项结果分开','癸','申亥寅','申(六合)','重审,元胎,六仪,斩关','原载断语与结果混合',['原断进人口与析理退人口有文字张力，原样保留。','胎产、风湿等为历史占验语言，不转换成诊疗建议。']),
 (20,201,210,'何宣义占宅：家计、妾财与妇人子问','癸','未申酉','未(勾陈)','遥克,蒿矢,连茹','原载断语与结果混合',['年命丁丑三十三与辛丑六十九异文，保留两版。','原断终死妾手未获此段明确结果支持，不能由妾盗财顺带认证死亡判断。']),
]
records=[]
for n,a,b,title,day,trans,use,types,feedback,notes in rows:
 records.append(dict(schema='liuren-book-case-v1',id=f'BK26-SHAO-{n:03}',title=title,book_title='六壬断案（本地邵彦和案例集）',category='家宅占',source_case_identity=f'book:{base.SOURCE}:L{a}-L{b}',review_state='source_checked',completeness='complete',boundary_note=f'已逐字读本案{a}–{b}行及相邻标题；包含现存全盘、全断、全析、附论和编者异议，未截去后注。完整指现存原案文本收全，内部异文另列。',question='本轮据题概括：'+title.split('：')[0],authors=['邵彦和（原载署名）','爱圅/未署名后注（按原文逐处区分）'],source_refs=[ref(a,b)],missing_fields=['未单列明确现实结果'] if n==18 else [],feedback_status=feedback,method_rule_ids=[],same_event_ids=[],chart_fields={'日干':day,'三传':trans,'发用':use,'课体':types},chart_status='按原载文字登记，未重排；异文与字符疑点见notes',notes=notes+['全案原载方法与结果可参照；方法开发暴露，独立验证0。'],logic_stages=['子问拆分','条件分支','结果核对']))

lookup={int(r['id'].rsplit('-',1)[1]):r for r in records}
definitions=[
 (11,[11,15],'极阴与迎阳须看所归位置，不能把阴性标签写成统一败局',
  ['童保仪原文六阴相继并传归阴方绝地；徐八公原文同称极日极阴，但解释转向东南为迎阳。'],
  '比较两案时保留阴阳结构之后所归位置、人物背景与神将差异；原作者并未把六阴相继一概解释为同一结局。',
  ['童案用宅上卯与末酉同六数，另言巳亥四数。','徐案讲从北至西转东南、贵人太阴等，随后描述家业转好。'],
  ['两案不同日辰、传位、背景，并非只改变一条件的对照试验。','旧摘要阴数可取半未由本批两案获得原文依据，不反推其在其他书处一定不存在。'],['B0123'],[(114,115),(155,156)]),
 (12,[12],'同支多位置：三店财绝解释分歧须逐作者并列',
  ['郑宣义案日上、支上、末传皆巳，原载两店兴一店败。'],
  '同一个巳在不同位置的取财或绝神存在原书不同解释，应保留各作者分支和编者疑问，不能择结果后拼成唯一邵氏规则。',
  ['原析理先以三处巳取三店。','附论把支上末传作财、日上作绝；另一人从店受癸克解释。','爱圅明确两论不知作者，另推干支二店/末传一店，使用似、欤而非定论。'],
  ['结果两兴一败不自动验证其中任何一种位置分配。'],[],[(124,126)]),
 (13,[13],'寿数相矛盾时保留原断与结果，后人推测不可回填成初判',
  ['王德卿案原断二十六年，原载结果十六年，析理随后批评四亥乘四说。'],
  '分别保存初判数字、叙事结果、弟子增辞与编者假说；本段不能为通用旺气倍进或太岁行年定死期提供已验证充分条件。',
  ['先对照二十六与十六，不擅自校成相同。','保留“此非先生意”批语，不能截引被批评的乘数当原作者公认法。','后面的太岁行年解释有或、毋乃，继续标后人推测。'],
  ['允许方法参照和继续校本；这里只限制强认证，不宣告所有年命/太岁方法无用。'],['B0134'],[(135,136)]),
 (14,[14],'迁居后转安：干预后的结果与原情景凶断分别记',
  ['童得松案先有德丧神消等凶断，末载迁店居住后户宁祸解。'],
  '把迁居这一动作、动作后的结果与未迁时的风险判断分开保存；不将未发生凶事写成凶事已验，也不据此否定全部风险定位。',
  ['原文记录壬德亥闭口，编者另以临绝解释。','随后记录童闻方迁居与户宁，原断和行动后结果不处于同一条件。'],
  ['没有不迁时的独立现实对照，不能证明迁居的因果效果。'],[],[(145,146)]),
 (17,[17],'宅不纳人与宅克人区别：迁出原因、争讼与后兴分层',
  ['何丞务原文日往加辰、人多宅狭，明确说非宅克人是人多欲自出。'],
  '区分空间拥挤主动迁出与住宅克人，并保留以后争讼与人财仍旺两种可共存结果。',
  ['原断明确否定的是宅克人这个归因，不否定需要迁出。','十三年争讼另以太阴卯、行年太岁等关系说明。','争讼后仍兴旺，不合并为全好或全坏。'],
  ['年命异文未校，十三年细推只作本案原载。'],[],[(175,176)]),
 (18,[18],'牛田、马屋同象取舍：原作者结合生息、空亡、天马与阶段',
  ['任太公春季丙戌占宅，原文主动问何以言牛不言田、言马不言屋。'],
  '保存原作者用生息、空亡、天马和所处阶段选择具体物象的条件；同一丑、午不能脱离场景直接等同固定物品。',
  ['春丙火相气相生，原文以生息之物取牛。','午空亡且正月天马在午，原文取马不取屋。','末传丑另说阶段至秋冬而取山地，原书明确区分同支不同阶段。'],
  ['这是本案作者取舍过程；没有结果记录，不补五项全中。'],['B0148'],[(185,189)]),
 (19,[19,20],'家宅多子问逐项判验：险中得全与未反馈的强断各归其位',
  ['王解元案胎几堕而得全、子感风后无事与田遭水患并列；何宣义案妾盗财有叙事而终死妾手未有对应结局。'],
  '按子问保存风险、救制及最终结果；部分结果得到原载支持时，不顺带认证全案其他强断。',
  ['王案保留申六合长生的救制解释与原载母胎保全。','同案田坏、病后无事、族人道士劝和分别登记。','何案妾盗财与终死妾手是不同结论，结果覆盖到哪里就记录到哪里。'],
  ['没有独立现实调查；本轮只是对原书不同语句与反馈范围的整理。'],[],[(198,199),(208,209)]),
]
rules=[]
for n,case_ns,title,conditions,conclusion,steps,exclusions,old,ranges in definitions:
 rid=f'LR26-BOOK-SHAO-{n:03}'
 case_refs=[dict(lookup[k]['source_refs'][0],case_id=lookup[k]['source_case_identity']) for k in case_ns]
 # Cross-case interpretive comparisons are explicitly candidate, not an authored universal rule.
 derived=n in (11,13,14,19)
 rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=title,categories=['家宅占'],claim_origin='本轮归纳' if derived else '原文明示',review_state='source_checked',status='candidate' if derived else 'source_method',conditions=conditions,exclusions=exclusions,conclusion=conclusion,reasoning_steps=steps,alternatives=['作者、弟子与编者意见不相同处并列保留，不据单案反馈强制统一。'],evidence_refs=[ref(a,b,'原载方法/结果及后注，身份按正文分层') for a,b in ranges],source_case_refs=case_refs,source_case_ids=[x['case_id'] for x in case_refs],support_case_ids=[lookup[k]['id'] for k in case_ns]+[x['case_id'] for x in case_refs],counterexample_case_ids=[],legacy_entry_ids=old,relations=[dict(type='条件分支',target_id=x,reason='补足原案角色、条件及作者身份；不新增独立事件。') for x in old],reference_value=['保留真人原载论法及可核对的取舍，限制过度归纳而不否定整案。'],limitations=['已读原载结果，方法开发暴露；独立效果验证0。','完整性指原载整案收全，不等于文本所有说法相互一致。'],independent_validation_count=0,method_type='条件比较与边界' if derived else '原载判断方法',logic_stages=['目标与子问','条件分支','反证与反馈覆盖']))
 for k in case_ns:lookup[k]['method_rule_ids'].append(rid)
lookup[16]['notes'].append('本批完整归档原作者财局方法，尚未另抽新规则；后续同类比较时处理，不强凑一案一条。')

for record in records:
 text='\n'.join(x['quote'] for x in record['source_refs'])
 unquoted={k:v for k,v in record['chart_fields'].items() if v not in text}
 record['chart_fields']={k:v for k,v in record['chart_fields'].items() if v in text}
 if unquoted:record['notes'].append('负责人按盘栏结构摘录（未逐字连续定位，不入META）：'+json.dumps(unquoted,ensure_ascii=False))
for path,batch in [('knowledge/liuren-research/20261102/book-cases/shao.json',records),('knowledge/liuren-research/20261102/rules/book-shao.json',rules)]:
 existing=json.loads((ROOT/path).read_text(encoding='utf-8'))
 merged={x['id']:x for x in existing};merged.update({x['id']:x for x in batch});base.write(path,list(merged.values()))

def other_ref(path,a,b):
 data=(ROOT/path).read_bytes();ls=data.decode('utf-8-sig').splitlines()
 import hashlib
 return dict(path=path,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(data).hexdigest(),role='旧AI归纳')
audits=[]
for number,old,case_ns,replacement,finding,a,b in [
 (1,'B0123',[11,15],'LR26-BOOK-SHAO-011','旧摘要将两案概括成极阴阴数可取半；本批所列原案只明列宅上卯、末酉六数及巳亥四数，并以迎阳另论徐案转好，未见统一减半依据。只限缩这条无原文支持的通则，保留宅上/末传取数与转向比较。',33,57),
 (2,'B0134',[13],'LR26-BOOK-SHAO-013','旧摘要把原文明示受质疑的四亥数法与或/毋乃的编者猜测整理成普遍数理和死期规则；原断二十六年、原载十六年本身有差异。暂停把该王案当统一倍进或太岁行年定死期的验证依据，其他两案未在本批审查。',364,385)]:
 audits.append(dict(schema='liuren-audit-v1',id=f'LA26-BOOK-SHAO-{number:03}',title='断案原文对读：'+old,target_entry_ids=[old],target_case_paths=[],disposition='narrow',finding=finding,reasoning=['对读旧摘要与其所引原案完整文本，区分原断、叙事结果与编者推测。','本轮不否定所有数理方法，只限制当前证据无法支持的强推广。'],evidence_refs=[other_ref('经验日志/古籍-六壬断案-补丁.md',a,b)]+[lookup[k]['source_refs'][0] for k in case_ns],replacement_rule_ids=[replacement],limitations=['只审本批明列子案，未审同条目其他来源；独立效果验证0。'],review_state='source_checked',reference_value=['原书宅上/归计门、阴阳转向或年命太岁的观察仍有参照价值，按条件与作者身份使用。'],action_scope='仅处理finding明示的摘要推广及该子案验证身份，不撤销整条目所有方法或原作者其他判断。'))
base.write('knowledge/liuren-research/20261102/audits/book-shao-review.json',audits)
print(json.dumps({'second_batch_complete':len(records),'new_methods':len(rules),'targeted_audits':len(audits)},ensure_ascii=False))

from refresh_shao_coverage import refresh
refresh(ROOT)
