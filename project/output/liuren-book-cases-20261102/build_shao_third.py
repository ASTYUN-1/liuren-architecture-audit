"""Reviewed original cases 21–30; no automatic heading-to-complete conversion."""
import json
import build_shao_batch as base
R=base.ROOT
data=[
 (21,211,220,'林丞务占宅：中末空时是否仍须细审','中末空且初传在干支才限缩读传；原作者明确其他初传位置不得概称不行。'),
 (22,221,230,'冯修职占宅：婢妾、母丧、拘系与火患','婢自缢日期六月十七与七月异文保留，原载各项结果分开；人物与火鬼传统解释非独立因果认证。'),
 (23,231,240,'叶油饼店占宅：极阴空亡与填实后的变化','原文空亡解灾与后填实入极阴是不同阶段；不改成极阴永远无灾或中末空一律吉。'),
 (24,241,250,'童秀才占宅：四课定位、方位异文与数法折半','西北/东北、寡居原因多种后注并列；春木旺土死而折半是本案具体取数条件，不是所有阴数自动取半。'),
 (25,251,260,'何七秀才占宅：归亲争产及诉讼终止','原载起讼至壬子十二月止，析理又以十一月水克火论宁贴，月份差异保留。'),
 (26,261,269,'某占家宅：原书怪异叙事与移灶说','整段怪异占验照录；果然未逐项说明哪些发现得到核实，括注作者未署名，不由本轮认证游尸等因果。'),
 (27,270,278,'郁氏女占宅：弹射四项断语','末句五月十五皆应属于原载笼统结果；没有各项完整析理，不补成模型自编判断链。'),
 (28,279,288,'邵三公占宅：养猪先成后败与子息费用','原断、不同年份叙事及末子玄武解释全保留；不能因原载家退尽就认证所有寿病预测。'),
 (29,289,298,'江文老占宅：独足神像与各项断语','原载只明确叙述供奉损一足神像；坏酱、蛇入宅及妻生独足儿等不自动算全部有反馈。'),
 (30,299,309,'徐大夫占宅：墓、年命与后注异议','原断母六月亡而反馈五月丁服有月份差异；母妻自身分子问，妻孕亡未见该段明确结果，爱圅解释单列。'),
]
records=[]
for n,a,b,title,note in data:
 records.append(dict(schema='liuren-book-case-v1',id=f'BK26-SHAO-{n:03}',title=title,book_title='六壬断案（本地邵彦和案例集）',category='家宅占',source_case_identity=f'book:{base.SOURCE}:L{a}-L{b}',review_state='source_checked',completeness='complete',boundary_note=f'本批逐字阅读{a}–{b}行，已核上下案标题；现存全盘、全断、全析及后注均收录，内部冲突没有删除。',question='本轮据原题概括：'+title.split('：')[0],authors=['邵彦和（原载署名）','编录者或后注作者（仅以正文署名为据）'],source_refs=[base.ref(a,b)],missing_fields=[],feedback_status='原载断语与结果混合',method_rule_ids=[],same_event_ids=[],notes=[note,'完整指本地来源全文收全，不等于逐项结果皆验或原盘已重算。','本批已读结果，仅作方法开发参照；无适合新增的方法时保留原文，不硬凑条目。'],chart_fields={},chart_status='保留原书全文课式，本批未重新排盘',logic_stages=['占问目标','原载方法','反馈覆盖']))
lookup={int(x['id'].rsplit('-',1)[1]):x for x in records}
definitions=[
 (21,'中末空不等于所有课都无传：原作者限定初传从干支起',
  ['林丞务案中末皆空，初传原在宅上；原文据此只就干支二处分断。'],
  '保留原作者对不行/无传的适用条件：初传不是从日宅上起时，仍须细审，不可泛化中末空便不看三传。',
  ['原文先定位初传宅上、中末空，才等之无传。','紧接明确“若初传不从宅与日上起，则又当细审，不得概为不行”。'],
  ['这是关于取读范围的限制，不表示中末空时现实事件必不发生。'],219,219),
 (23,'极阴得空与后来填实分阶段：解急灾不等于无长期耗损',
  ['叶油饼店案丑亥酉，甲子旬中末空；后载辛亥太岁填实亥。'],
  '原作者把眼前空亡解灾、家计仍耗与后来填实再论凶分开；可取其阶段与条件变化，不将空亡压成永久吉凶。',
  ['原断虽有灾危不至不测，同时论子孙耗财。','析理以中末空及真三奇解释当前解灾。','后说太岁填实亥，条件已变，另论母与家计。'],
  ['原文不提供独立对照；不能从该案得出所有填实都必凶。'],238,239),
 (24,'家宅取数与方位：位置、季节折半及异文须同时保留',
  ['童秀才求新宅，原书未八戌五相乘四十，再以春木旺土死折半为二十年。'],
  '本案折半有明确季节和取数位置，不能简化成所有极阴数取半；青龙宅左与方位异文也应保留原作者各自的参照层级。',
  ['原文区分家宅四课定位与坟墓天盘定位，但该括述作者未明确，不全部归邵氏。','末段列未八戌五与春木旺土死的折半条件。','西北/东北的编者校议并存，未以一种代替原文。'],
  ['该案原文没有独立逐年结果确认二十年；不能把算法算出当应期已验。','本轮只保存作者在此盘的选择，未建立统一乘除规则。'],248,249),
 (25,'争产的进入与停止：不同作用链及结果月份分别留证',
  ['何七秀才甲子日占宅，原文有关眷属归家、分灶争产及之后宁贴。'],
  '入局的刑害与收束的制破碎分阶段保存；原载十一月解释和十二月结案差异不抹平。',
  ['原文用末戌刑未、初子害未等解释归亲和起讼。','再用壬子子水克火制破碎解释收束。','叙事与析理月份不完全一致，标明待校而非改写原判。'],
  ['不要把不冲不发不刑不动从该故事直接升级为一切事件发生的必要条件。'],258,259),
]
rules=[]
for n,title,conditions,conclusion,steps,exclusions,a,b in definitions:
 r=lookup[n];rid=f'LR26-BOOK-SHAO-{n:03}';r['method_rule_ids']=[rid]
 cr=dict(r['source_refs'][0],case_id=r['source_case_identity'])
 rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=title,categories=['家宅占'],claim_origin='原文明示',review_state='source_checked',status='source_method',conditions=conditions,exclusions=exclusions,conclusion=conclusion,reasoning_steps=steps,alternatives=['同样符号在其他对象/阶段的读法可能不同，当前只保存原文所述条件。'],evidence_refs=[base.ref(a,b)],source_case_refs=[cr],source_case_ids=[cr['case_id']],support_case_ids=[r['id'],cr['case_id']],counterexample_case_ids=[],legacy_entry_ids=[],relations=[],reference_value=['原作者的限定、阶段变化与原文争议均可作为判断方法参照。'],limitations=['本批已读原载结果，独立验证0。','原书强语按原文保存，迁移范围以本卡明列条件为界。'],independent_validation_count=0,method_type='条件与取舍',logic_stages=['位置','条件限制','阶段变化']))
for path,batch in [('knowledge/liuren-research/20261102/book-cases/shao.json',records),('knowledge/liuren-research/20261102/rules/book-shao.json',rules)]:
 existing=json.loads((R/path).read_text(encoding='utf-8'));merged={x['id']:x for x in existing};merged.update({x['id']:x for x in batch});base.write(path,list(merged.values()))
print(json.dumps({'third_batch_complete':10,'new_methods':4,'read_range':[211,309]},ensure_ascii=False))

from refresh_shao_coverage import refresh
refresh(R)
