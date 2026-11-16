"""Close the in-flight B0303 ten-part audit and publish conditional families."""
import hashlib,json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'knowledge/liuren-research/20261102';OUT=ROOT/'output/liuren-book-cases-20261102'
BOOK='书籍库/北海闲人/毕法赋全解-正式整理本.md';OLD='经验日志/古籍-壬占汇选.md';ANCIENT='书籍库/现代著作/《壬占汇选》.txt'
def ref(p,a,b,role='原书断语'):
 raw=(ROOT/p).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 assert 1<=a<=b<=len(ls)
 return dict(path=p,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role=role)
def write(p,o):
 (ROOT/p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Each row is one explicitly scoped subjudgment; no other legacy entry is marked read.
ROWS=[
 (1,'德丧禄绝',1085,1087,[13,95,135,136],[(BOOK,2511,2513),(ANCIENT,229,245)],
 ['先辨所问是考试及第、已任官去留还是疾病，再定位德禄的绝、墓、空。','徐学士同一课的考试及第与后来病亡分项保存；原末评明确邵公有事后推测。'],
 ['不能把德丧仅定义为临绝地，或把德禄绝直接改成考不中。','旧摘要所引“禄临绝地，岂能食禄乎”位于古243愚按，不应整句署邵彦和。'],
 '德禄失效须按空墓绝的具体坐标和目标分断：原徐案允许考试及第而官途/寿短，成名与能否久食禄分开。',
 '修订德丧仅临绝的缺项；将243愚按与245邵断/后析拆开，保留功名、年命缓克及后述价值。'),
 (2,'权摄禄临支',1089,1091,[1,2,136],[(ANCIENT,8195,8211),(BOOK,854,864)],
 ['先定支为他人、任所、本人单位或家庭，再核禄临支与官星空实。','邓巡辖原断同时有寅龙官空、禄临支、陈姓人阻及待其去职的现实条件。'],
 ['不见禄临支即一律不正任或得他人财产。','邓案次年八月到任，原断取待陈去，不把八月改成已证明的通用填空应期。'],
 '禄临支先解释禄的归属；正任、权摄与仍能食禄须合官星及现实阻因分断。',
 '保留邓案权摄后正任的分阶段用法；撤回脱离官空、角色和现实阻因的单项充分条件。'),
 (3,'鬼临三四',1093,1095,[84],[(ANCIENT,11117,11135),(BOOK,3465,3494)],
 ['三四皆鬼须核两个支课位置、所问和空实救制。','徐秋试案原断另有真闭口、四土壅塞和病阻；不得考试是因病不能入场。'],
 ['古11135“鬼临三四所以多灾，不得考试”为愚按，不是11131邵断的逐字因果概括。','单见一鬼、不同年旬空实，不复制全见结论。'],
 '保存鬼临三四的全见风险结构，并把考试不利、病不能赴试及空救分开；徐案后按不能覆盖原断的多条件。',
 '修正将编者愚按整体归邵及将不能赴试压成考不中；原多条件及疾病反馈仍有参照价值。'),
 (4,'两蛇夹墓',1097,1099,[68],[(ANCIENT,615,629),(BOOK,2879,2901)],
 ['两蛇夹墓依本法核日干寄宫、本墓与腾蛇的神将坐标。','何三公丙寅案另列干支带墓、四课子鬼、死神戌蛇及宅内旧冢的连续论证。'],
 ['何盘干上戌蛇与丙寄巳符合夹墓坐标，可归同结构；同结构不等于同事件，不能省略支墓与四课鬼链。','掘墓、七年丧五人是原后述；亡祟致病是原作者解释，未独立核因果。'],
 '何宅与第五十三法共享丙寄巳、戌墓乘蛇的夹墓结构，可在此条件下归并；何宅另保留四课鬼回日上、死神与宅冢链，墓地发现与疾病归因分层。',
 '旧摘要“蛇覆墓神”须补齐巳戌神将坐标；核何盘可归同结构，但何三公与毕法乙亥腹块案不得混案，保留额外条件。'),
 (5,'人宅皆死',1101,1103,[96],[(ANCIENT,7117,7131),(BOOK,4006,4028)],
 ['人宅分别核干死气和支死气，不把干之死地机械复制给支。','许州原问是战时可居否，郭御青引毕法后随督师北回，城破属原后述。'],
 ['不从战时城池一案推出任何住所逢此即不能住。','原郭判断、北海月煞/十二长生解释和既知病案不是同一事件或同一验证。'],
 '皆死先核参照层，再按住居安全、战局或重症等目标解释衰弱；原城破后述只支持原案叙事覆盖范围。',
 '保留郭引法与避险过程，收窄跨情境不可居和必然死亡的泛化。'),
 (6,'三传递克',1105,1107,[9,10,11,106],[(ANCIENT,6237,6257),(BOOK,2154,2187)],
 ['递克须逐传核方向，另核发用是否受地盘克及官职类神。','仕宦的参劾、求财的串克得财与内战各有成立条件；丙申伏吟末寅反生日干丙。'],
 ['不能把末克干写成所有递克的必要定义；旧所举丙申案并不符合这一条件。','不把仕宦参劾扩成所有占类受欺，亦不因月将一案无效即删除各占类例外。'],
 '递克共同动作是辨连续施受方向，最终克干与否决定分支及轻重；官占再合空禄、伏吟马与年命来读去留。',
 '直接修正旧定义末克干与所举丙申案不相容；保留陈断两人差异及郑命地网加重。'),
 (7,'合中犯煞',1109,1111,[101],[(BOOK,4223,4263),(ANCIENT,2947,2963)],
 ['先核三传三合局的中神，再看干支上神与中神刑冲害。','同见吉类、犯煞神空及冲去煞时，分别写过程障碍和最终结果。'],
 ['“三合局中任意藏刑冲克害”过宽，不能替代本法中神与干支上神坐标。','不能从合中犯煞直接认定现实人物有害心；郭/陈及后按的解释归属依各原段。'],
 '合中犯煞把外表和合与具体阻碍并列；是否妨碍终局，需比较类神、衰旺、空实与去煞阶段。',
 '用本法4225的中神定义替代宽泛藏克害，并保留犯煞不必推翻全局诸吉的分支。'),
 (8,'干神归支',1113,1115,[25,36,106,107],[(BOOK,1199,1211),(BOOK,2615,2615),(BOOK,4402,4408),(ANCIENT,437,445)],
 ['干神归支是日干寄宫之天盘支加日支，并非干上神再加支。','定干为本人/行人、支为家/任所后，另核生克墓、马丁、空实与所求动向。'],
 ['不将干神归支与干传支或两方上神互传混为同一坐标。','乙丑进京案须连同干支墓、无二马、中末空；富贵课刚日干上马等另有动例外。'],
 '归支先描述人归何处及主客方向；宜静、会来、任所可得与住不长分别取题，不以一条静象包办行动结论。',
 '直接修正旧“干上神临支”坐标误写；保存原乙丑北行不成而南京起官的分事结论。'),
 (9,'年命填空',1117,1119,[112],[(ANCIENT,4227,4241),(ANCIENT,5879,5893),(ANCIENT,4835,4835)],
 ['必须分本命支自身为空、某神临本命、行年填某空以及月建/出旬填实。','填实后再问填的是官财救神还是鬼煞，不先假定其吉凶方向。'],
 ['古4241编者明确反驳“未临本命便填空”，并列郭事后改释与不同作者解释。','郭5893行年辰填空仍兼印化煞并闻官音；4835本命可填仍因中传落空判不中，不支持填空必凶减或一概不以空论。'],
 '年命填空保留为有争论的局部效力判断：先核究竟哪个支、哪一层实，再合目标、其余空陷与救制，不作万能解空。',
 '旧“郭补注行年填实则凶减”未给确定同源出处；现补可定位原例说明，并保留编者反对郭命上填空的原文。'),
 (10,'制鬼良医',1121,1123,[82],[(ANCIENT,4475,4491),(BOOK,3392,3422)],
 ['先固定当前忧患，再定位实际能制该鬼的救神及空实、乘将和发用。','郭戊子病案原说木鬼得时贪荣不克；愚按另说申酉制寅为病愈关键，两说并存。'],
 ['4491“制鬼之位乃良医”为愚按质疑郭未引，不应作为郭原断逐字归因。','该例没有把申酉明确记成医生住址方位，不能由能制鬼直接承诺实际医生或疗效。'],
 '制鬼良医可按病、盗、讼分别映射能解当前忧患的角色；救神要能实际作用。郭案病愈两种解释并列，不据已知愈证明任一因果。',
 '修正旧归郭与方位化的增写；保留申酉制木、得时贪荣的竞争解释及初八渐愈原后述。'),
]
limits=['本批仅续审B0303十子判断；不表示其他旧条目已审。','原断/原后述/编者按/北海解释分层，旧源与旧案例未改。','已读答案属开发暴露，独立效果验证0；source_checked只表示引文与语义核对。']
audits=[];rules=[]
for n,title,a,b,linked,spans,conds,excs,conclusion,finding in ROWS:
 rid=f'LR26-LEGACY-BIFA-{n:03}';aid=f'LA26-LEGACY-BIFA-{n:03}'
 ev=[ref(OLD,a,b,'旧AI归纳')]+[ref(*s) for s in spans]
 rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=f'毕法旧摘要修订：{title}',categories=['通用'],claim_origin='本轮归纳',review_state='source_checked',status='candidate',conditions=conds,exclusions=excs,conclusion=conclusion,reasoning_steps=[finding,'逐句将旧IF/THEN与当前原文结构、作者归属及原载后述对照。','保留原作可取的施受方向、对象和过程；未核的充分性不增为定律。'],alternatives=['不同对象、坐标、空实、救制或时段保留独立条件分支，不能仅以同名并成同一案。'],evidence_refs=ev,support_case_ids=[],counterexample_case_ids=[],legacy_entry_ids=['B0303'],relations=[dict(type='修订',target_id='B0303',reason=f'仅修订第{n}子项{title}，不替换其他子项。')]+[dict(type='依赖',target_id=f'LR26-BOOK-BIFA-{k:03}',reason='来源卡保留原文完整条件；本卡跨旧摘要归并，只修本子项。') for k in linked],limitations=limits,independent_validation_count=0,legacy_subentry_number=n))
 audits.append(dict(schema='liuren-audit-v1',id=aid,title=f'B0303第{n}项：{title}',target_entry_ids=['B0303'],target_case_paths=[],disposition='revise',finding=finding,reasoning=conds+excs,evidence_refs=ev,replacement_rule_ids=[rid],limitations=limits,review_state='source_checked',independent_validation_count=0,subjudgment_scope=dict(number=n,line_start=a,line_end=b,only_this_subjudgment=True),reference_value=[conclusion],action_scope=f'仅B0303第{n}子判断的旧AI定义/归因；不否定原案其他论证。',evidence_axes=dict(source_text_checked=True,prediction_effect_independently_validated=False,feedback_scope='原来源记载及其明示缺口；未独立核现实结果。')))
write('knowledge/liuren-research/20261102/audits/legacy-bifa-continuation.json',audits)
write('knowledge/liuren-research/20261102/rules/legacy-bifa-continuation.json',rules)
tax=json.loads((OUT/'bifa_method_taxonomy.json').read_text(encoding='utf-8'))
families=[]
for g in tax['families']:
 f=dict(g,legacy_entry_ids=['B0303'] if any(x in g['rule_ids'] for m in tax['legacy_mappings'] for x in m['current_rule_ids']) else [],merge_type='共同动作归并，条件分支保持',unresolved=['原文术理与效果未独立验证；本族不同结构不能互换。','未发现可安全删除的完全同条件重复卡，原卡与来源映射全保留。'])
 f['source_mapping_preserved']=True;families.append(f)
for n,g in enumerate(tax['normalization_groups'],1):
 ids=g['rule_ids'];byid={r['id']:r for r in json.loads((BASE/'rules/book-bifa.json').read_text(encoding='utf-8'))}
 families.append(dict(id=f'BF26-NORMAL-{n:02}',title=g['common_label']+'：条件归并',rule_ids=ids,legacy_entry_ids=['B0303'] if any(i in ids for m in tax['legacy_mappings'] for i in m['current_rule_ids']) else [],merge_type='同一分析动作归并，异条件分支保持',common_method=g['preserved_difference'],preserved_branches=[dict(rule_id=i,conditions=byid[i]['conditions'],exclusions=byid[i]['exclusions'],conclusion=byid[i]['conclusion']) for i in ids],unresolved=['归并分析步骤，未认定成立条件等效，不删除或覆盖来源卡。'],independent_validation_count=0,source_mapping_preserved=True))
# The ten concrete revisions are also navigable from the appropriate mature family.
membership={1:['OFFICE','VOID'],2:['OFFICE','ROLE'],3:['GHOST'],4:['TOMB'],5:['TOMB'],6:['CHAIN'],7:['RELATION'],8:['MOTION','ROLE'],9:['VOID'],10:['GHOST']}
for n,keys in membership.items():
 r=rules[n-1]
 for key in keys:
  f=next(f for f in families if f['id']==f'BF26-{key}')
  f['rule_ids'].append(r['id']);f['preserved_branches'].append(dict(rule_id=r['id'],legacy_entry_ids=['B0303'],conditions=r['conditions'],exclusions=r['exclusions'],conclusion=r['conclusion']))
  f['legacy_entry_ids']=sorted(set(f['legacy_entry_ids']+['B0303']))
write('knowledge/liuren-research/20261102/families/legacy-bifa-continuation.json',families)
report=['# 旧经验续审：毕法及相关','', '2026-11-02。按用户收束要求，只完成已在途B0303十子项与现有139卡的条件归并，随后停止。','',
 '新增10张审查卡、10张候选修订卡；审查的旧条目为1条（B0303）中的10子判断，不是10个新增独立案例。12个方法族与8个近义组已接原families协议，保留来源卡完整条件、排除和结论；无可安全认作完全同条件重复的卡，故未删除来源卡。','',
 '## 逐子判断','', '|子项|明确修订|保留可用方法|','|---|---|---|']
for row in ROWS:report.append(f'|{row[0]}. {row[1]}|{row[-1]}|{row[-2]}|')
report += ['', '## 边界与产物','', '甲子徐学士、丙寅何三公、郭戊子病案与北海同名法只按明示关系并读，不据课名造同源。第9项旧“郭补注行年填实则凶减”仍缺唯一直接出处，已标缺口，不替其拼造原引。第10项制鬼良医由愚按提出，郭原断为木鬼贪荣，两者身份与竞争解释均保留。','',
 '旧源未改。没有重开其余807条旧经验审查，也没有新增独立效果验证。未完成项留给之后明确续接。','',
 '审查：knowledge/liuren-research/20261102/audits/legacy-bifa-continuation.json。修订卡：rules/legacy-bifa-continuation.json。规范分组：families/legacy-bifa-continuation.json。校验：output/liuren-book-cases-20261102/legacy-bifa-continuation-validation.json。','',
 '规范分组为显式人工归并，检索返回共同动作及保留分支，不能把族名或机械校验通过当作术理有效性证明。统一索引/导入由工具负责人完成，以其最终结果为准。','']
(ROOT/'docs/六壬知识整理-20261102/旧经验续审-毕法及相关.md').write_text('\n'.join(report),encoding='utf-8')
print(json.dumps(dict(audits=len(audits),rules=len(rules),families=len(families),reviewed_legacy_entries=1,reviewed_subjudgments=10),ensure_ascii=False))
