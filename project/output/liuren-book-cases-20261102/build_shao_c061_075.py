"""Manually read C61–75 subjudgments and their precise source branches."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
B = R / 'knowledge/liuren-research/20261102'
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
cases = load(B / 'book-cases/shao.json')
reviews = load(B / 'method-reviews/shao.json')
cards = load(B / 'rules/book-shao-c-review.json')
old = load(B / 'rules/book-shao.json')
family = load(B / 'families/book-shao.json')
audit_path = R / 'output/liuren-book-cases-20261102/shao-c-condition-dedup-audit.json'
audit = load(audit_path)

# n, title, exact conditions, conclusion, source reasoning, subjudgments (title, stages, old?, note), families, external gaps
specs = globals().get('BATCH_SPECS') or [
(61, '辛生二水的泄象、幕贵科第与寿数疑算分开',
 '辛巳日亥玄临辛、亥子二水；午官临厨幕贵，寅贵加丑；末申空天空。',
 '原以一金生二水取虚泄病象，以官临厨/幕贵论监试与寅贵加丑论癸丑及第；末空限享用。申7未8与减半的原式不能直接得35，不补算法。',
 ['亥玄临辛且一金生二水为原肾泄取象；具体病因非本轮医学核证。', '官星临厨入天厨、官作幕贵取当年高中，寅贵加丑取癸丑及第。', '末申空天空是得官徒空；原申7未8空亡减半，与35及癸亥年出生校议不强行凑合。'],
 [('遗泄、病月与四月安', ['取象','医学原载'], False, '原述亥玄与金生二水；二三月/四月未给逐月算法，不由后病叙反补。'), ('监试高中与癸丑及第', ['应期','考试层级'], False, '当年发举、癸丑及第分别对应两级，幕贵官厨与寅贵加丑各存。'), ('得官不享与35寿数', ['数量','异文'], False, '原仅列申7未8与减半，未明确加乘及减半作用对象，无法直接闭合35；本轮不预设算法，出生戊子/己丑校议和癸亥35亦待外源。')],
 ['HUMAN-HOUSE','DOCUMENT-TIMING','QUANTITY-OPERATIONS'], ['申7未8减半与35寿数未闭合，出生年及卒年年龄校议待外源']),
(62, '同课异人外，亥命脱干、六阴与男女占别的原条件',
 '辛巳同61课，亥临辛、午勾鬼入宅、支干自刑、末同类申空；孙丁亥命为爱圅补议。',
 '原从面前脱气、宅午贵鬼和六阴论前程与病损，另述女占吉/未娶男克；爱圅以亥本命脱干解释较甚，只是后注不能当独立验证。',
 ['亥加辛脱气，宅午贵作鬼、支干自刑与六阴为原不久链。', '连茹喜进忌空，末同类空扩及诸孙为原判断，不把各孙当独立样本。', '男女/未娶的原对比和爱圅亥命解释分别署层次。'],
 [('前程不显、虚泄及四年后亡', ['关系链','应期'], False, '脱气/鬼/六阴有明据，四年本句无独立取数法；壬子十二月死为历史后叙。'), ('女占吉与未娶男克、诸孙丧', ['对象取舍','空亡'], False, '保留作者性别婚否条件和同类末空，不能把此例作现代医学或所有子孙结局规则。'), ('与61同课而异断', ['作者层次','年命'], True, '复用旧062，丁亥孙命、戊申占年是爱圅年龄校议，原人物事件仍分开。')],
 ['HUMAN-HOUSE','TEXTUAL'], []),
(63, '旧政反复导致赴任迟，未8终任丧归另问',
 '癸丑日未丑未反吟，戊申占年未为旧政；十二月建丑又加旧上，满盘鬼。',
 '作者以旧政重见及月建加旧解释迟赴；已三年到第六年赴的叙述不等于原文明示乘二算法。八年终任另据未8、丑墓田及常未。',
 ['先询旧任已三年，原断第六年方赴，未提供三乘二通则。', '戊申年未旧政，初末日辰与丑月建往来旧人，不能速。', '满盘鬼、丑墓田、未常加之与未8取八年丧归。'],
 [('旧任三年及第六年才赴', ['迟速','应期'], False, '旧政反复和月建有推据，6年算法未明，不能写成反吟一律加倍。'), ('终此任、八年丧归', ['数量','终局'], False, '未8用于八年，满盘鬼及墓田常未是原终局解释；和6年到任不同节点。')],
 ['DOCUMENT-TIMING','QUANTITY-OPERATIONS'], []),
(64, '墓空渐通之外，考试妻宫医误按位置分判',
 '甲申日干支墓，未旬空；初贵六害、偏堂太阴；行年申为医而作蛇鬼，本命木与墓叙存疑。',
 '旧064保墓空局部解阻；补存初贵六害不利考试、太阴与妻宫加子、行年医蛇鬼的医误风险，不以墓空免除所有凶。',
 ['未墓空只论本身渐脱，原仍另论初传贵六害。', '偏堂太阴、妻宫及加子主无子的原分问照存。', '行年申医作蛇鬼为医误解释；九年卒/庚申亡与本命是木的用语待校，未统一为确定时间链。'],
 [('本身墓空渐通', ['空亡','解阻范围'], True, '旧064已保局部解阻，不当整案吉。'), ('考试、妻与子息', ['子问','取象'], False, '贵六害与太阴是原考试不利，妻宫加子主无子原解释但不造更多子息算法。'), ('医误、病叙和卒期', ['医象','文本核对'], False, '行年申医蛇鬼与当年误诊近死可对应；原各疾病和卒期叙述保留张力，不能把近死改写成当年死。')],
 ['HUMAN-HOUSE','TEXTUAL'], ['九年而卒/庚申亡的衔接、本命是木与题干辛未的解释待外源']),
(65, '宅受身克兼脱去无正居，蛇虎限官与水边曹职',
 '丙申支申加干受丙克，宅上亥又得申生；寅末虎，亥生寅再生丙。',
 '不只用赘婿课名：宅加日受克且宅去生亥为无正居；寅申迁转被蛇虎挠使官程止知录，寅曹职与亥寅生链另取水边州府。',
 ['支就干受克而申又生亥，原论寺观、外处或妻家，无正宅。', '传见蛇虎为丧服原断，四丧后叙不反补固定4的取数。', '末寅曹职、寅生于亥与丙生于寅为原水边州府解释；迁转寅申受蛇虎挠限官。'],
 [('无正宅及赘婿居妻家', ['人宅','施受关系'], False, '课名与具体宅受克、宅脱去同存，居所几个可能不合并成唯一事实。'), ('蛇虎丧服与四丧', ['取象','数量缺据'], False, '蛇虎丧象有明据，四丧只有后叙无明4算法。'), ('水边州府曹职和迁转止', ['职务取象','取舍'], False, '寅曹与亥寅丙生链对水边知录，迁转寅申受蛇虎限，不扩大所有蛇虎都止官。')],
 ['HUMAN-HOUSE','CLASS-SYMBOL'], []),
(66, '父墓虎蚁、午妻目与屋转田园的原作用链',
 '壬寅日午临日、丑午害，申父临墓虎；亥克午、酉宅败破碎。',
 '原把父墓白虎、午妻目亥绝、丑田园午屋及水土克制分为不同子链；病眼、屋转田园、酒败与启坟后叙分范围，不认证坟致病的现实因果。',
 ['申父在墓守虎为白蚁，左虚/偏室未见各自完整推据。', '午为目为妻、火绝亥且武壬皆亥夹午，取亥年妻目不利。', '丑午害，丑田园午屋、水克午坏屋、土克水成田园；卯年另水死卯且卯上戌鬼。', '宅酉壬败又破碎，原取男女酒败；历史后叙不等同医学或伦理因果证据。'],
 [('偏室、妻宫和眼疾', ['子问','应期'], False, '偏室无正位有原断但无单独推链，午妻目与亥绝夹克有明解释。'), ('父坟蚁与兄弟不肯迁', ['取象','行动反馈'], False, '申父墓虎为原蚁象；未迁与后启见蚁保留行动时序，不能当迁坟改善已验。'), ('九年屋转田园', ['关系链','应期'], False, '屋/田园、水土作用及卯年理由存明据，九年不另编通用算法。'), ('男女酒败与戊午亡', ['原载因果','终局'], False, '酉败破碎解释酒败；戊午本人亡是后叙，无另给寿数法。')],
 ['HUMAN-HOUSE','CLASS-SYMBOL'], []),
(67, '科名分层之外，铜铁坑冶船场按传位分职',
 '壬寅日申生壬学堂，初巳贵德空而玄滞；三传巳寅亥。',
 '复用旧067生扶与贵空的科名分层，补存申金铜铁、巳加申坑冶、亥江湖临寅为未成船之修造场；不将未成寅木与卯成船混为词典同义。',
 ['干支受生及寅生巳贵德使仍得职，贵空玄滞限发解不及第。', '申金为铜铁，巳加申为坑冶。', '江湖亥临寅；寅木未成船、卯已成船，故论船场修造而非仅船行。'],
 [('发解、不能及第而终得职', ['考试层级','空亡'], True, '旧067已经覆盖，壬子发解为后析/后叙时间，不能笼统称所有考试皆中。'), ('三任铜铁坑冶船场', ['职务取象','位置'], False, '按申金、巳加申、亥临寅分别取职，寅/卯未成已成比较是原明条件。')],
 ['CLASS-SYMBOL'], []),
(68, '藏丁取舍之外，鬼生三午刃与宅合的官宅风险',
 '戊午日寅鬼生中末及宅午刃天鬼；未合午，亥月建合寅，天空空屋。',
 '原官问迁改与宅眷死亡分开，以寅鬼生三午刃、月建合寅来生宅、未午合论宅患，未藏丁非旬丁仍复用旧卡；三人后叙不变固定人数算法。',
 ['卯寅鬼生午刃天鬼，中末相重；支未午合连宅眷。', '十月亥合寅来生宅，未中丁主动和天空空屋为原官宅链。', '病死三人与米仓罢职是各结果，米仓具体物象无另明推法。'],
 [('官任责罚与罢去', ['官任','反馈范围'], False, '迁改/责罚原断与米仓败露罢职后叙存，不反补米仓神象。'), ('宅眷三亡及鬼生刃', ['作用链','数量边界'], False, '寅生三午、未合午、亥月建与天空空屋有明据；三午不编三人通则。'), ('未中丁非旬丁', ['作者口径','取舍'], True, '复用旧068，不改变引擎旬丁口径。')],
 ['HUMAN-HOUSE','SUBQUESTION'], []),
(69, '败逼墓再墓日与宅克，阻服回避及九年分节点',
 '丙子日巳戌卯；败卯克戌墓，戌墓丙，丙巳奔宅子受克；巳4戌5合9。',
 '原按败墓逼身与去住不容论阻服回避，再以宅巳4与日戌5相加九年；母卯先墓、己身后及属不同时间对象，不把九年称成功出头已验。',
 ['卯败逼戌墓再墓丙，丙巳入子宅受克，是去住不容。', '宅巳4、日戌5合9；九年后卯败木棺入墓为原终局。', '卯母先入墓而后及身；题十一月卯将戌时与爱圅寅将酉时校议分开。'],
 [('阻服、回避与去住不容', ['作用链','阶段'], False, '当年母死、再任因妹丈回避与观职后病死各阶段留存。'), ('九年数、母先身后', ['数量','应期'], False, '4+5=9明示，不将端坐九年方出头误成九年获升；后文原断数尽及死同读。'), ('月将占月异议', ['异文','作者层次'], False, '卯将戌时与寅将酉时差均5位，同盘不证明两日期同真；不替源选一。')],
 ['HUMAN-HOUSE','QUANTITY-OPERATIONS','TEXTUAL'], ['十一月与将时校议未获外源定本，原盘与后议并存']),
(70, '曲直从墓返旺生，前后妻与继兄子分别取象',
 '乙卯未卯亥曲直，从墓到旺到长生；贵生身、亥子生乙卯；未财虎与末亥后禄。',
 '原把墓传旺生用于由微至显和寿，天门木局持台用于侍从；未财虎前妻与亥后长生禄后妻、父子同类合继兄子分对象，寿近90与87后叙分精度。',
 ['贵生身且木局助，从未墓经卯旺到亥生为渐荣与寿。', '亥天门木局持台取侍郎，不另造职级普适表。', '同类父子六合取纳兄子；未财空墓虎前妻，后天后长生临日禄取后妻财旺，爱圅另以阴卯克未析前妻。'],
 [('由穷至显、侍从与寿', ['课传发展','数量精度'], False, '近九十是约数，87原载不能当精确90；无明87算法。'), ('前妻先丧、后妻财旺', ['对象区分','作者层次'], False, '未财虎/卯克与亥天后长生临禄是前后妻不同条件，保留邵析与爱圅析层次。'), ('继兄弟子及后来子丧', ['子息','反馈范围'], False, '原同类父子六合解释纳兄子；乙卯丧子是后叙，不能称所有子息逐项已有明推法。')],
 ['HUMAN-HOUSE','CLASS-SYMBOL'], []),
(71, '退归长生可朝职，末退空亡才主晚降',
 '乙卯退茹丑子亥；卯禄向亥长生，亥卯生旺相连；朱雀仪神、子紫微亥远穹。',
 '不以退茹一律衰：原先取禄归长生、近天门及宫象论在朝八座，后以退入空亡限晚年谪降；中末不空五府为原反事实，未达五府不等于无朝官。',
 ['卯禄归亥长生、亥卯一带生旺与朱雀仪神为前段科名朝官。', '中末若不空才五府，是明确反事实限定。', '近天门、子紫微亥远穹取八座；退空亡取晚降无正宅，不能倒用成全程皆无官。'],
 [('来年再举、亥年高甲', ['应期','考试'], False, '原断与35再解37登第对读；具体亥年算法未逐项明示，不补数法。'), ('在朝八座与五府反事实', ['取象','条件反事实'], False, '宫象与长生生旺为朝职，中末不空五府保反事实，八座官职名称不是人数8。'), ('晚降与无正宅', ['阶段','空亡'], False, '退空限后段，后载因秦桧一言罢；无正宅仅原断无明确后叙。')],
 ['DYNAMIC','VOID-EXCEPTIONS','CLASS-SYMBOL'], []),
(72, '德神不作怪之外，催官、阻服、争分与寿54原乘法',
 '辛酉从革巳丑酉；午官临日巳官初应，旬丁蛇巳为辛德；午9酉6。',
 '官日相应为催官，辛藏戌取庚戌及第；三传金局另论兄弟争，无子爻为子不得力；午9乘酉6得54，原五十三卒不能改成54已验。',
 ['午官临日、初巳助官为催官，辛藏戌取庚戌及第；阻服赴任不同阶段。', '金日金局取兄弟争、无子爻取子不得力；不得力不等于无子。', '旬丁蛇巳为德不作怪复用旧072；午9酉6乘54，原53结果差一保留。'],
 [('催官及第、阻服和赴任', ['作用链','应期'], False, '庚戌及第与壬子乙卯服、庚申赴任分别留；不以官星一吉覆盖后灾。'), ('兄弟争分及子不得力', ['子问','范围'], False, '金局兄弟争与无子爻不得力有原推；后有三子不可写无子，争四次无明4算法。'), ('旬丁蛇德不作怪', ['德神','取舍'], True, '原卡072已经覆盖，不补怪异真实性。'), ('寿54与实际53', ['数量','反馈差异'], False, '午9×酉6=54明示；原文五十三者又算54的句内张力存，不强改年龄制度。')],
 ['SUBQUESTION','QUANTITY-OPERATIONS'], []),
(73, '临终范围之外，学堂发解、猿迷原象与入妻家分链',
 '丁巳伏吟巳申寅；末寅学堂受行年卯扶，巳临官空；申妻玄光怪，丁巳俱生寅。',
 '旧073专保不见子息的临终范围；补存学堂与行年扶的解举、初临官空的声誉、申玄的原猿迷象、丁巳俱生寅归妻家。怪异和治疗叙不当现实病因证明。',
 ['末寅学堂、行年卯扶为来年解，初临官天空为声誉。', '中申妻玄与光怪、申猿武贼为原猿迷解释。', '日一丁巳两丁皆生寅、宅妻为移居妻家解释；四年期无明取数。', '不及第与后戊辰及第两阶段保原，不强归成永不及第；临终不见子息旧073已限范围。'],
 [('次年发解、不及第与后来及第', ['考试层级','阶段'], False, '原末寅学堂行年卯扶支持发解；前不及第和后合科第在同段，不替原书编明确哪一次省试失败。'), ('妻猿迷与治愈叙', ['原取象','反馈身份'], False, '保存申玄光怪猿武贼取象与邻人治愈原叙，不能当猿迷因果独立验证。'), ('四年移妻家合居', ['人宅','数量缺据'], False, '丁巳生寅宅妻为归妻家链；四年未明公式，妻家独子亡是后叙。'), ('七月亡、子息不在及喜事', ['临终范围','反馈粒度'], True, '复用旧073，已有二子秋试后扶丧，不能写无子；七月卒期无明算法。')],
 ['HUMAN-HOUSE','CLASS-SYMBOL','DOCUMENT-TIMING'], []),
(74, '退传顾祖与命财生鬼，归家争产不是升转',
 '庚辰午辰寅退传顾祖，命寅财末入宅；午龙加申退鳞，寅生午克庚；行年夜贵昼天空闭口。',
 '原在升迁问事里以日传降支、顾祖命入宅判断差出经乡争产；寅既财又命生午鬼，自己参与争财为作者归因，贵闭口不宜告是原建议，实际再次上诉被罢下狱分开。',
 ['日上起退支，末寅本命马入宅取差出经过乡里。', '午龙退鳞损身；中辰不归午，末寅命财反生午克庚，构成因财自扰。', '命寅财蛇挠与未眷天空争解释族产争；行年夜贵废职、昼天空闭口为官未可告。'],
 [('赴乡差出与升迁问', ['动向','条件取舍'], False, '问升而课降回家，不能见官龙便升；本命马是本人经过。'), ('族人房产争及罢狱', ['关系链','行动反馈'], False, '财命生鬼、蛇与眷属争为原方法；实际分未半再告后罢狱，不当既定人品裁决。'), ('文书十一月及贵闭口', ['文书','取舍'], False, '十一月文书下为叙事无明月法；贵闭口无用与不宜告有原据，不将后下狱补作时间算法。')],
 ['DYNAMIC','HUMAN-HOUSE','DOCUMENT-TIMING'], []),
(75, '乱首受财到仆犯主，墓形建议与实际经过分开',
 '壬辰日亥加辰自取乱首，午财后临壬、丑鬼加午；申父玄入丑墓，午亥自刑。',
 '原以财上鬼及下犯上解释受财被仆挟、妻仆与本人遇害；父墓玄武不垂头的地形叙和迁墓建议独立保留，未实施迁墓的效果不称验证。',
 ['午财丑鬼加财，亥加辰乱首、天空仆犯主为受财挟制链。', '午临壬天后及午亥自刑，是原妻仆与仆伤解释。', '申父玄入丑墓，长生玄不垂头拒尸与原地形丈数并存；迁墓能保命仅原建议。'],
 [('官中受财与仆挟制', ['关系链','行动结果'], False, '二千贯受财、仆每挟20千为历史叙，数字不是本盘取数量法。'), ('妻被仆及戊午仆刺', ['子问','应期边界'], False, '财鬼/午亥刑/下犯上有明据，戊午期未给完整算法，不以见午便唯一推出。'), ('父墓拒尸与速迁建议', ['地形原载','救制建议'], False, '原70余丈葬60丈前余10丈描述保留；未载迁墓，不能把后刺死当迁墓有效证据。')],
 ['HUMAN-HOUSE','SUBQUESTION'], []),
]

new_ids = set()
for number, title, condition, conclusion, reasoning, subs, names, gaps in specs:
    cid = f'BK26-SHAO-{number:03}'
    rid = f'LR26-BOOK-SHAO-C{number:03}'
    oid = f'LR26-BOOK-SHAO-{number:03}'
    case = next(x for x in cases if x['id'] == cid)
    ref = dict(case['source_refs'][0])
    stages = list(dict.fromkeys(s for _, tags, _, _ in subs for s in tags))
    source_case_ref = dict(ref, case_id=case['source_case_identity'])
    card = dict(schema='liuren-rule-card-v1', id=rid, title=title, categories=[case['category']],
        claim_origin='原文明示', review_state='source_checked', status='source_method',
        conditions=[condition], conclusion=conclusion, reasoning_steps=reasoning,
        exclusions=gaps or ['本案不同目标与时段不互相抵消；没有明推据的数字/应期不补造算法。'],
        alternatives=['同盘、同课名或同数字不足以认定同一事件或同一方法；保留原作者与后注取舍。'],
        evidence_refs=[ref], source_case_refs=[source_case_ref], source_case_ids=[case['source_case_identity']],
        support_case_ids=[cid, case['source_case_identity']], counterexample_case_ids=[], legacy_entry_ids=[],
        relations=[], limitations=['历史原载、作者因果与行动建议分开；独立验证为0，原医学或神怪解释不作为本轮现实因果证明。'],
        independent_validation_count=0, logic_stages=stages)
    cards = [x for x in cards if x['id'] != rid] + [card]
    new_ids.add(rid)
    judgments = [dict(id=cid+f'-Q{i:02}', judgment=title_, disposition='linked_existing' if existing else 'linked_supplemental_source_branches',
        rule_ids=[oid if existing else rid], method_note=note, evidence_refs=[ref], category_tags=[case['category']],
        judgment_stage_tags=tags, independent_validation_count=0) for i, (title_, tags, existing, note) in enumerate(subs,1)]
    review = dict(schema='liuren-book-method-review-v1', case_id=cid, review_state='source_checked',
        source_case_identity=case['source_case_identity'], source_refs=[{k:v for k,v in ref.items() if k!='quote'}],
        all_subjudgments_dispositioned=True, source_disposition_complete=True, method_extraction_complete=not bool(gaps),
        subjudgments=judgments, remaining_actions=gaps,
        review_note='逐问保原方法、无明推据项、原后叙和作者层次；同盘异人/同字多目标不并。')
    if gaps:
        review['external_gap_review'] = dict(checked_source_scope='整案题干、原断、先生析与爱圅校议已对读；连续证据见source_refs。',
            available_methods_preserved=[rid]+([oid] if any(s[2] for s in subs) else []), unresolved_actions=gaps,
            status='处置已明确，疑算/异文尚未恢复')
    reviews = [x for x in reviews if x['case_id']!=cid] + [review]
    for name in names:
        fam = next(x for x in family if x['id']=='LF26-SHAO-'+name)
        if rid not in fam['rule_ids']: fam['rule_ids'].append(rid)
        fam['preserved_branches'] = [x for x in fam['preserved_branches'] if x['rule_id']!=rid] + [dict(rule_id=rid, conditions=[condition], source_method=conclusion)]
        fam['canonical_rule']['source_rule_map'] = [x for x in fam['canonical_rule']['source_rule_map'] if x['source_rule_id']!=rid] + [dict(source_rule_id=rid, canonical_family_id=fam['id'], disposition=conclusion)]

# Concrete old/new comparisons: core object, position and purpose differ as stated.
comparisons = globals().get('BATCH_COMPARISONS', {
62: ('同课异人及爱圅丁亥命校议边界', '亥脱干/宅鬼六阴的病损链及女占男克/末同类空分问', 'TEXTUAL'),
64: ('墓空只解本身墓滞而非整案皆吉', '初贵六害、太阴、妻宫及行年申医蛇鬼的具体子链；病卒异文待校', 'HUMAN-HOUSE'),
67: ('长生扶身与贵空玄滞区分发解/及第/得职', '申铜铁、巳加申坑冶、亥临寅未成船场按传位业务取象', 'CLASS-SYMBOL'),
68: ('未支藏丁非旬丁的原作者口径', '寅鬼生重午刃、亥月合寅及未午合连宅眷，米仓具体象未明', 'HUMAN-HOUSE'),
72: ('巳旬丁蛇因辛德而不作怪', '午巳催官/辛藏戌、金局争分、无子爻不得力及9×6=54寿差', 'SUBQUESTION'),
73: ('传无子爻只在临终不在场语境，非一生无子', '学堂卯扶发解、申玄猿迷原象、丁巳生寅入妻家另链', 'HUMAN-HOUSE'),
})
for n,(core, added, name) in comparisons.items():
    oid=f'LR26-BOOK-SHAO-{n:03}'; rid=f'LR26-BOOK-SHAO-C{n:03}'
    old_card=next(x for x in old if x['id']==oid)
    fam=next(x for x in family if x['id']=='LF26-SHAO-'+name)
    if oid not in fam['rule_ids']: fam['rule_ids'].append(oid)
    fam['preserved_branches']=[x for x in fam['preserved_branches'] if x['rule_id']!=oid]+[dict(rule_id=oid,conditions=old_card['conditions'],source_method=core)]
    fam['canonical_rule']['source_rule_map']=[x for x in fam['canonical_rule']['source_rule_map'] if x['source_rule_id']!=oid]+[dict(source_rule_id=oid,canonical_family_id=fam['id'],disposition=core)]
    pair=[oid,rid]
    audit['pair_comparisons']=[x for x in audit['pair_comparisons'] if x['source_rule_ids']!=pair]+[dict(source_rule_ids=pair,
        comparison_dimensions=['问事对象','必要位置与作用','推理环节','反馈范围'],shared_scope='同一原事件原文，不增加支持样本',
        distinct_source_methods={oid:core,rid:added},disposition='旧卡已覆盖限定原则，补卡保存未载具体子链；重叠核心复用旧卡，不当完全同义删除',
        canonical_family_ids=[x['id'] for x in family if rid in x['rule_ids'] or oid in x['rule_ids']])]
audit['reviewed_case_ids']=[x['case_id'] for x in reviews]
audit['new_rule_family_maps']=[dict(rule_id=x['id'],family_ids=[f['id'] for f in family if x['id'] in f['rule_ids']]) for x in cards]
audit['remaining']=globals().get('BATCH_SCOPE', '已审01–75及11个优先案；未逐223案和全部卡同条件比较，不作全书去重完成声明。')
save(B/'rules/book-shao-c-review.json',cards)
save(B/'method-reviews/shao.json',reviews)
save(B/'families/book-shao.json',family)
save(audit_path,audit)
print(dict(batch_cases=len(specs),batch_subjudgments=sum(len(s[5]) for s in specs),new_cards=len(new_ids),reviewed=len(reviews),subjudgments=sum(len(x['subjudgments']) for x in reviews),supplemental_cards=len(cards)))
