"""C136–149, preserving the second original 141 as event 1411."""
from pathlib import Path
import runpy,json
specs=[
(136,'买店不免争之外，巳4戌5九年与七年后叙',
 '己亥子财临干、辰库宅，巳玄店修费，末卯鬼虎破戌库。',
 '旧136已保先财利后争与改买不消争；原朴析补4+5=9年，与第七年分赎不相同，不能因为果如先生言就消除期差。',
 ['初巳玄修费倍常，中戌巳火库为前期财利。','末卯鬼破库使财不可永，租改买仍争已在旧卡。','朴析巳4戌5合9，后叙第7年取赎，数期分别保留。'],
 [('财利与租改买仍争',['阶段','条件取舍'],True,'旧136已完整覆盖，先3年大发与后争不互相抵销。'),('九年与第七年',['数量','反馈差异'],False,'4+5=9有明法，第7年争有明叙，未把预测9改成7或把果如概括变精确应期。')],
 ['QUANTITY-OPERATIONS'],[]),
(137,'独足酉兑泽合船水利陆阻，倍利只保宽粒度反馈',
 '商人己未独足酉六合，酉兑泽、独足无足；酉将亥时原题。',
 '水陆判断与127附张姓共有酉兑泽合船、独足不利陆核心，原加倍得利与果应只保原粒度；两案将时不同不并事件。',
 ['酉兑泽与六合舡为水路利，独足无足为陆路不利。','果应笼统，未记实际利润倍数和路线，不能作独立营业账目。'],
 [('水利陆阻',['类神','问事目标'],False,'与127附只做同条件水陆核心比较，姓名/将时原异不认同一事件。'),('加倍得利果应',['数量','反馈粒度'],False,'倍数未明算法；和127附十倍不统一成同一收益幅度。')],
 ['DYNAMIC','CLASS-SYMBOL'],[]),
(138,'进屋先核罗网害与子蛇绝生，不见斫轮即宜居',
 '庚子卯酉互网，支受干制、宅天空害、太阴宅母，末子蛇落空。',
 '同124婚盘另问进屋，原以互罗网年凑、宅害和末蛇绝生不利居住；不能挪婚成结论给房产，末不断绝生原留未硬编事件。',
 ['支受干制畜产不生、宅天空害与幼小扰大。','太阴宅母不明、行年凑卯酉天网地罗。','末子蛇绝生循环为不可居，未载实际入居后果。'],
 [('斫轮与进屋争扰',['问事目标','条件取舍'],False,'课名不足宜居，罗网宅害有原据；124同盘婚成不等这里可居。'),('畜小宅母和末子蛇',['子问','反馈缺口'],False,'分对象保原断，无后实际入住、病伤或畜不育记录。')],
 ['HUMAN-HOUSE','VOID-EXCEPTIONS'],[]),
(140,'日辰夹店终得但反复赎争，原丙年句未定',
 '戊寅辰巳午三传被日辰夹定；亥卯未生人可成，日辰抛离再赎。',
 '原日辰夹定取终得店、抛离再赎并官事风险，生年亥卯未是明限定；三年主赎及丙年四五六年句疑，不凑唯一应期。',
 ['夹定三传占店终得，原限定亥卯未生人方成。','被买断后原主来赎、抛离再赎，后官事不一与屋无气死人多属风险原说。','却发目不至丙年四五六年的原句不明，无后叙解释。'],
 [('终得与原主再赎',['条件限制','阶段'],False,'既可得又可赎争不矛盾地分阶段；亥卯未生人限定照存。'),('三年及丙年疑句、屋死多',['应期','文本缺口'],False,'没有明确逐数算法和后叙，原不清句待外源，屋无气因果不作本轮现实确认。')],
 ['SUBQUESTION','TEXTUAL'],['原却发目不至丙年四五六年句待善本校读']),
(141,'三鬼原称仍能因财合库得财，命年在课限鬼兆',
 '丁酉申财六合日上，酉宅戌蛇六害，亥子丑进；申命财、命年俱课。',
 '原称三传皆鬼却仍以日财、神将合的间接合、末财库和命财限为少阻可得；末丑子爻与三鬼原称不默改，不能变成见鬼一律拒财。',
 ['六合卯与戌合、蛇巳与申合，是作者按神将本家间接合。','末见财库、本命财且命年传课为喜兆非鬼兆。','原三鬼称与丑子爻盘字并存，未替源补财库金水映射。'],
 [('再三得财与少阻',['取舍','作用链'],False,'财、合、末库与命年构成原反转条件，三鬼不是孤立通则。'),('神将间接合与原三鬼口径',['作者口径','文本核对'],False,'保卯戌/巳申两个合的来源坐标；末丑何以统称鬼原未释，待外源不自动纠盘。')],
 ['VOID-EXCEPTIONS','TEXTUAL'],['原三传皆鬼与末丑子爻的口径未释，保原待核']),
(1411,'反复薄财用命德制鬼和甲己化土，得日两说',
 '甲寅反吟寅申寅无明财，己巳命，寅德蛇制申、甲己化土；戊寅/甲戌得日。',
 '原无财仍从生年己与甲化土、命德及蛇制申论薄财，行年财临得日；首戊寅与后甲戌日期并列不择一，不改成已有实际得款反馈。',
 ['反吟争夺薄财，寅作己命德与蛇制申鬼为原限制。','甲日己年甲己化土为原化气取财。','原首戊寅日、后行年财临甲戌日得，未解释两期是阶段或异文。'],
 [('无财化气薄财',['命年','取舍'],False,'原明确论化气，不从日干常财五行硬补原盘未见的财支。'),('戊寅或甲戌得日',['应期','异文'],False,'两得日原断并存，没有实得日后叙，不用一日删除另一日。')],
 ['TEXTUAL','DOCUMENT-TIMING'],['戊寅/甲戌得财日两说待外源，不作唯一应期']),
(142,'空勾虚扰与末虎动众，向三阳课名不能保证店兴',
 '丙戌未勾空日、子宅后翳，中寅玄财物偷耗，末辰虎动众。',
 '原按空勾虚扰、后宅翳、寅玄偷财和辰虎动众解释店不兴终止；向三阳向高终不可止句与前后店止文字张力保留，不以课名改写实际歇店。',
 ['未勾空扰为虚账隔皮亲追索，子后翳不兴。','中寅玄为子偷财，末辰虎为打斗动众。','后姨夫诉70贯和子斗收钱不明致歇分时段；终不可止原句待校。'],
 [('开店虚账亲扰与不兴',['人物关系','作用链'],False,'隔皮亲人是姨夫的原后叙，官追70贯非盘内数法。'),('子财动众与终歇',['课传发展','反馈'],False,'寅玄/辰虎原据存；源向高终不可止与店止不擅调成一致。')],
 ['HUMAN-HOUSE','TEXTUAL'],['源终不可止句与先后歇店叙的语义待外源']),
(143,'日脱身兼职劳而生贵恩回补，举荐内绛帐按末生学堂',
 '甲申巳常双女生日脱，申官龙加双女；亥雀官长、寅后临亥学堂天门。',
 '原巳常双女和官临双女取兼职劳费，亥后生甲寅与申官龙转为劳中加俸升迁；寅长生学堂天门后恩对应内绛帐，不以脱气便只损。',
 ['甲生巳火脱为费力，常职巳双女与初申官加双女皆兼。','亥雀举荐官长，末寅后临亥天门长生同生甲寅为回补恩。','寅亥学堂内天门为王宫教授，不能只见天门推所有人同职。'],
 [('兼职劳费及加俸升迁',['施受关系','救制'],False,'先保甲生巳费力，再看亥后生扶与申龙官，不省回补条件。'),('列荐引见内绛帐',['职务取象','阶段'],False,'朱雀荐、天后恩、末学堂天门各原理由，后宫教授为本事件原叙。')],
 ['HUMAN-HOUSE','CLASS-SYMBOL'],[]),
(144,'同课年命异断外，彩帛坏色到十月染皂只保本',
 '甲申巳常衣帛红紫，行年丙添巳双脱；寅后改色虎斑，中亥丁水十月皂色。',
 '旧144保存官商年命异用；补存常衣帛火红紫、双巳蚀甲、寅后改色虎斑与亥十月变动皂色的行业细象。旁店仿染无效与汪十月不折本是不同结果。',
 ['太常衣帛、日年赤火为红紫，两个巳蚀甲使败色费余得不足。','寅天后改色，寅虎斑点，中亥水只宜暗青黑绿。','亥旬丁变、后水皂，亥十月才翻腾保本；寅亥生扶不能回写先前未亏滞半年。'],
 [('彩帛坏色与双脱',['行业取象','作用链'],False,'已染红紫为问时已知背景，开包见斑才原后发现，不把全部包装成未知预测。'),('十月染皂不折本',['行动条件','应期'],False,'旁人仿暗色不效/汪十月成保本同时存；保本不等利润倍增。'),('官商同课异年命',['对象','年命'],True,'复用旧144已有寅命官长生/未命虚诞、行年官与盗气区别，不合事件。')],
 ['CLASS-SYMBOL','HUMAN-HOUSE'],[]),
(146,'同课中命引生与本命自墓不同，五十四行年闭口',
 '与145癸未稼穑同课，丙辰命自来墓身；54年未上戌闭口九月。',
 '原己未命中传引生/末旬首化财与丙辰命添墓对比解释财旺或短久，行年未上戌闭口取54九月；未载实际死亡叙，不以原问对答当卒期验证。',
 ['己未命中传得本命自墓引生、旬首甲克未戌克癸为原化财理。','丙辰命辰墓来身添墓，失去前人相同转换条件。','54未年上戌闭口为9月积块疼气塞胀蛊原断，没有独立后叙。'],
 [('145发财而此案短久',['命年','条件对照'],False,'同月将日时不意味着同年命同事件，不借刘判官35万结果支持本案。'),('54岁9月闭口疾终',['行年','反馈缺口'],False,'九月戌与年未上戌闭口明示，具体病终只是原预测，不当现实病案验证。')],
 ['HUMAN-HOUSE','TEXTUAL'],[]),
(147,'先官后克之外，30岁官旺与卯6任、未死败守土虚',
 '丁酉亥命官贵发、曲直生丁；丙辰年辰上申生亥官，卯6；末未勾临卯死败。',
 '旧147已保存先官次克与木局救病，补存30丙辰申生亥官、卯6任及末未勾守土拘死败不能赴；六任是职次不是六种不同独立验证。',
 ['30丙辰辰见申生亥官有气取及第。','木局救丁病不死旧卡覆盖，不能因此漏终身残病。','卯生丁数6为六任；未勾守土死卯丁败卯，被留不能赴。'],
 [('30及第与病后吉',['年期','阶段'],True,'旧147核心充分，补记丙辰申生官细理由，不变更原卡限定。'),('六任与守土有名无实',['数量','作用链'],False,'卯6有原理由，未勾死败有原不赴理由；40余日病安为叙无明40算法。')],
 ['QUANTITY-OPERATIONS','HUMAN-HOUSE'],[]),
(148,'同官过数转鬼绝与命添水，32数和宅左墓另断',
 '丁酉同147课，49年过官，亥4未8=32；未受克不能制水，卯截路空，申命上子。',
 '原以年龄官星过数、未不能制水与命添子水把官转鬼绝，32由4×8但40外 cutoff未给独立算法；墓前左老阴据丑墓太阴方位，现实断龙致破家只是原因果。',
 ['前22取官与今49过官是原时间条件，不把同亥官贵一律等效。','亥4未8=32，后称40外无力，辛亥鬼旺且命子杀破禄为52终。','酉日丑墓在前，西看北为左、太阴老阴人，掘龙脉家破只保原说。'],
 [('同课49过官变鬼绝',['年龄条件','取舍'],False,'不把32中举/40后无力概括为人人过32就无官，原自身数字范围保留。'),('辛亥52终与命添水',['行年','反馈'],False,'辛亥死有原叙，命申上子杀破禄为52原解释，水杀不当独立准确率。'),('宅前左老阴墓与家破',['方位','原载因果'],False,'原方位坐标西看北左保留，龙脉破家因果未核，不以同课差异认证该机制。')],
 ['HUMAN-HOUSE','QUANTITY-OPERATIONS'],[]),
]
comparisons={136:('财库先利后末鬼破、租改买仍争','巳4戌5合9与第7年取赎期差，保朴析作者层次','QUANTITY-OPERATIONS'),
144:('官/商年命职业不同使同课异断，生扶只保本','衣帛常赤双巳脱、后改色虎斑、亥丁十月皂色及旁仿无效','CLASS-SYMBOL'),
147:('先官次克再木局救病，后守土虚另限','30丙辰申生亥官、卯6职次与末未勾死败细坐标','HUMAN-HOUSE')}
folder=Path(__file__).resolve().parent
runpy.run_path(str(folder/'build_shao_c061_075.py'),init_globals={'BATCH_SPECS':specs,'BATCH_COMPARISONS':comparisons,
 'BATCH_SCOPE':'已审01–149（含118/127附及重复141）和11个优先案；未全书审完或同条件去重完成。'})
base=folder.parents[1]/'knowledge/liuren-research/20261102'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cases=read(base/'book-cases/shao.json');reviews=read(base/'method-reviews/shao.json');families=read(base/'families/book-shao.json');audit=read(folder/'shao-c-condition-dedup-audit.json')
reuse={139:[('还本与再索息分先后',['目标','阶段'],'原139已保财绝与长生对应两阶段、当场然只证已知背景。'),('四年后癸丑息讼',['应期','反馈范围'],'丑上朱雀鬼惹动为原癸丑期解释，四年相隔保原，原卡已有后诉风险与索息分问。')],
145:[('官闭口不迁与财化鬼转治生',['目标分断','命年'],'旧145已完整保本命中未、旬末末首及化财原条件；没有这些不能迁同盘146。'),('经商12年发至35万',['行动反馈','数量缺据'],'归家治生为采纳建议后的结果，3千本金/12年/35万均后数字无明盘算法，不作未经干预对照。')],
149:[('反吟凶难后财雀争成',['取舍','阶段'],'旧149已保初难后成组合，不截单句必难。'),('两家丧、过房子闹与丁丑成',['子问','文本边界'],'旧卡已分三人争/丁丑成/两家丧，乙巳子与巳中丙戌二姓原句不清；无唯一丁丑择日算法。')]}
for n,subs in reuse.items():
 case=next(x for x in cases if x['id']==f'BK26-SHAO-{n:03}');ref=case['source_refs'][0];rid=f'LR26-BOOK-SHAO-{n:03}'
 gap=['巳中丙戌二姓过房子的原句待校；不强释或改藏干'] if n==149 else []
 rv=dict(schema='liuren-book-method-review-v1',case_id=case['id'],review_state='source_checked',source_case_identity=case['source_case_identity'],source_refs=[{k:v for k,v in ref.items() if k!='quote'}],all_subjudgments_dispositioned=True,source_disposition_complete=True,method_extraction_complete=not bool(gap),remaining_actions=gap,
  subjudgments=[dict(id=case['id']+f'-Q{i:02}',judgment=t,disposition='linked_existing',rule_ids=[rid],method_note=note,evidence_refs=[ref],category_tags=[case['category']],judgment_stage_tags=tags,independent_validation_count=0) for i,(t,tags,note) in enumerate(subs,1)],review_note='可用方法复用原卡，未明数法单列不强新增。')
 if gap:rv['external_gap_review']=dict(checked_source_scope='本案整段含原断后叙',available_methods_preserved=[rid],unresolved_actions=gap,status='处置明确，原疑句未恢复')
 reviews=[x for x in reviews if x['case_id']!=case['id']]+[rv]
 fam=next(x for x in families if x['id']=='LF26-SHAO-SUBQUESTION');oc=next(x for x in read(base/'rules/book-shao.json') if x['id']==rid)
 if rid not in fam['rule_ids']:fam['rule_ids'].append(rid)
 meaning='；'.join(s[2] for s in subs);fam['preserved_branches']=[x for x in fam['preserved_branches'] if x['rule_id']!=rid]+[dict(rule_id=rid,conditions=oc['conditions'],source_method=meaning)]
 fam['canonical_rule']['source_rule_map']=[x for x in fam['canonical_rule']['source_rule_map'] if x['source_rule_id']!=rid]+[dict(source_rule_id=rid,canonical_family_id=fam['id'],disposition=meaning)]
 audit['existing_card_reuse_decisions']=[x for x in audit.get('existing_card_reuse_decisions',[]) if x['case_id']!=case['id']]+[dict(case_id=case['id'],rule_id=rid,reason=meaning)]
pair=['LR26-BOOK-SHAO-C1271','LR26-BOOK-SHAO-C137']
audit['pair_comparisons']=[x for x in audit['pair_comparisons'] if x['source_rule_ids']!=pair]+[dict(source_rule_ids=pair,comparison_dimensions=['问事远行','酉独足六合','水陆结论','收益幅度/反馈'],shared_scope='两例有相同水陆取象核心，未核同一事件',distinct_source_methods={pair[0]:'原十倍预测无后叙、巳将卯时',pair[1]:'原加倍及笼统果应、酉将亥时'},disposition='规范合并水陆比较核心，收益数与证据身份保留分支，不删除源卡、不并事件',canonical_family_ids=['LF26-SHAO-DYNAMIC','LF26-SHAO-CLASS-SYMBOL'])]
audit['reviewed_case_ids']=[x['case_id'] for x in reviews]
write(base/'method-reviews/shao.json',reviews);write(base/'families/book-shao.json',families);write(folder/'shao-c-condition-dedup-audit.json',audit)
print({'reviewed':len(reviews),'subjudgments':sum(len(x['subjudgments']) for x in reviews),'batch_subjudgments':sum(len(x[5]) for x in specs)+sum(len(x) for x in reuse.values())})
