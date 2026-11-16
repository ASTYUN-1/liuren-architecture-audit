"""Register manually read cases 31–45; retain all original text and conflicting claims."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'
raw = (ROOT / SOURCE).read_bytes()
lines = raw.decode('utf-8-sig').splitlines()
digest = hashlib.sha256(raw).hexdigest()

def ref(a, b):
    return dict(path=SOURCE, line_start=a, line_end=b, quote='\n'.join(lines[a-1:b]), sha256=digest, role='原书断语')

specs = [
 (31,310,318,'郭德占宅：人宅旺神与运用限制','家宅占','未载明确反馈','原文只给断语，仍保留守分与运用的条件比较；取债之子为原作者措辞，不作本轮道德评价。'),
 (32,319,328,'叶助教占宅：水沟壅塞与分项病断','家宅占','原载断语与结果混合','保留爱圅正月节异议；原书水路与疾病解释原样存档，原载各症反馈不可外推为已证实医学因果。'),
 (33,329,338,'童三十四公占宅：阴阳角色与子孙财库','家宅占','原载断语与结果混合','老阴老阳、少女、子息、财库分别定位；文字音公及子亡顺序不擅改，原载多人结果逐项保留。'),
 (34,339,348,'汪四六公占宅：财局反生日上鬼','家宅占','原载断语与结果混合','财局经未土反克水日的作用链有明文；雷嗔木等传统叙事照录，未据结果证实所有木材来历。'),
 (35,349,358,'伊伯廷占宅：长生空亡与先凶后吉条件','家宅占','原载断语与结果混合','析理死亡于甲寅与叙事入狱几死并不相同；迁居后的变化另列，不能抹成甲寅死亡已验。'),
 (36,359,367,'某占宅：蛇虎加门与两代重丧','家宅占','原载断语与结果混合','原文组合有门户位置、刑、时令死气等条件，保留整案而不另增蛇虎必死的泛化规则。'),
 (37,368,376,'时生占宅基：逼山近水与宅基水坏','家宅占','原载断语与结果混合','原题时生等信息不全，完整指现存课式和全部断析已收；不得编出出生年或将缺题头当未载整案。'),
 (38,377,386,'某占宅：四正加临的死败与家事断语','家宅占','原载断语与结果混合','原文强语及家事叙事完整保存，单案不升级成所有四正相加非死即败的通则。'),
 (39,387,395,'某占宅：损齿与新修厨灶','家宅占','原载反馈','同一巳分别用于口与炉灶，原断损一牙与原载姐妹缺口齿粒度不同；未逐项核新砖，不能全断等同全验。'),
 (40,396,404,'郑三公占坟地：山形、家事与酉数','家宅占','原载断语与结果混合','保留坟地原占类；六年再加三年为酉增一半的本案数法，未说明普适增加条件，不并入无条件乘数法。'),
 (41,405,414,'徐承务占坟地：空穴、交易障碍与子孙贵人','家宅占','原载断语与结果混合','当前不能葬、付钱后可葬、后人仕进分阶段；析理巳加辰作贵与课式贵卯有文字冲突待核，不代原书修盘。'),
 (42,415,423,'刘秘教占宅：争产分居与诸项身体断语','家宅占','原载断语与结果混合','明确结果为拆宅分居；妇人病状、自身脾泄及太阴少妇管家未见逐项独立反馈。'),
 (43,424,432,'郭仲起占宅：本命墓身与迁居后未验凶期','家宅占','原载断语与结果混合','次年迁居是原载行动；料想其凶可免是推测而非已经反馈免灾。八全加八半十二有式无通用选择条件。'),
 (44,435,443,'应贡元占前程：魁杜天门在六仪三奇下的改判','事业占','原载断语与结果混合','原作者不作阻隔论及具体组合保留；阴德与神明为作者解释，不由成功叙事独立认证，亨集类别标题不混入43。'),
 (45,444,453,'何秀才占应试：父子分问、名次与丧妻异说','学业占','原载断语与结果混合','父不能入试和子中二十八名为明确原载，丧妻及寿阻未在此段给同等结果；邵析、爱圅异说、末段未署名补论均保留。'),
]
records = []
for n,a,b,title,category,feedback,note in specs:
    records.append(dict(schema='liuren-book-case-v1', id=f'BK26-SHAO-{n:03}', title=title,
        book_title='六壬断案（本地邵彦和案例集）', category=category,
        source_case_identity=f'book:{SOURCE}:L{a}-L{b}', review_state='source_checked', completeness='complete',
        boundary_note=f'实际通读{a}–{b}行及相邻标题，现存课式、断语、结果叙述与所有后注完整保存；完整不代表每一子断都有反馈。',
        question='本轮据原题概括：'+title.split('：')[0],
        authors=['邵彦和（依原载署名）','爱圅或其他编注者（具体以正文署名为准）'],
        source_refs=[ref(a,b)], missing_fields=['未载独立结果段'] if n==31 else [],
        feedback_status=feedback, method_rule_ids=[], same_event_ids=[], chart_fields={},
        chart_status='保留原文课式；本批尚未调用引擎复算',
        notes=[note,'原载内容用于方法开发，不增加独立验证次数。'],
        logic_stages=['占问对象','作用关系','反馈范围'],
        original_categories=['坟地'] if n in (40,41) else (['应试'] if n==45 else [category])))
by_n={int(r['id'].rsplit('-',1)[1]):r for r in records}
definitions=[
 (34,'财局须继续追踪所生对象：水日火局生未土反克日',
  ['汪四六公案水日、炎上火局，日上未土承火局之生并克水日。'],
  '按原文先识财局，再追踪财的下游作用；本案财生鬼，原作者将其落实为眷属婚嫁攀亲耗费，不能只因火是财便判得财。',
  ['原文先复述人皆曰财。','再指出火生日上未土、未土反克水。','最后把眷属婚嫁使用太过作为本案落事。'],
  ['缺少财生日上克身之神的关系时，不能照搬财化鬼。','本案家事落点不能只凭同一五行链复制到所有求财课。'],346,346),
 (35,'合与长生的救解须能承接：长生空亡时不成立原拟转吉',
  ['伊伯廷丙午日宅占，原文先以子丑合、末寅长生拟先凶后吉，继而指出寅空亡不能引进。'],
  '保存原作者先提出救解链、再核空亡否决该救解的判断过程；有合或长生名称不足单独判吉。',
  ['子克丙是起始不利。','作者提出丑寅引鬼为生的可能。','寅空亡使该接续不成立，遂称见生不生。'],
  ['甲寅死亡的析理强语与原载几死有差异；不能计为死亡预测已验。','未证明所有长生空亡皆无救，限定此原案所述作用链。'],356,357),
 (39,'同支按子问取象：巳作口与炉灶分别核搭配及旺相',
  ['正月己巳日宅占，申乘勾加巳，原作者同时给出损齿与新修灶两项断语。'],
  '同一巳的口与炉灶象分属不同子问：损齿用申骨牙、勾损折、传破，修灶用巳炉灶及旺相；不要把一字多象混成无条件枚举。',
  ['损齿链保存巳口、申骨牙、勾损折与传破。','另以巳为炉灶，旺相主新修。','原载分别回应姐妹缺口齿及灶新修，新砖没有同样明确回应。'],
  ['反馈细节不等于每个取象元素均获独立因果证明。'],394,394),
 (41,'子孙脱气与子孙贵人须随所问对象及所乘神将分辨',
  ['徐承务问坟地，原文癸见卯并明确以卯为子孙贵人；同时有空穴与交易障碍。'],
  '本案作者明确不把卯统一读作脱气，而取子孙贵人；应将当前能否买葬与后代目标分开，不因空穴或脱气一词全盘定凶。',
  ['空墓先用于穴位与未能下葬的现实障碍。','原载以付钱处理买山关系后才葬。','卯为子孙作贵人，不为脱气，是作者明示取舍。'],
  ['析理巳加辰作贵与课式有差异，须保留待核，不能把此处不一致用于改写贵人排法。','本案后人仕进叙事不构成坟地导致仕进的独立验证。'],412,413),
 (43,'取数原式与免灾推测分开：八全加八半并无通用减半准则',
  ['郭仲起案原文未八数、两个八年，先八全用后八半用，得十二年；次年已迁居。'],
  '保存十二年的原式供数法比较，同时标明作者未给为何后八减半的通用条件；迁居后的免灾仅被写作料想，不能当十二年凶期命中或免灾已验。',
  ['定位未为本命墓身及宅井的作者关系。','忠实保留八加四的原式。','按原文把实际迁居和料想免凶分层。'],
  ['单案数值可算不等于应期选择依据已完整。','不和春木旺土死折半等其他条件直接合并成统一算法。'],431,432),
 (45,'父子应试分对象，丧妻强断保留白虎限定及后注分歧',
  ['何秀才占应试，原作者按日上亥子孙夺庚气区分父与子，又另以财虎等论妻。'],
  '父的受脱与子的得第是不同对象；原文对丧妻另明说非白虎乘之不可此断，爱圅丧吊与行年墓解释须单列而非拼成邵氏原链。',
  ['父临场病阻与子二十八名分别记录。','原文名次亥四申七相乘保存为本案算法。','丧妻段把合长生、脱上逢脱、白虎限定及爱圅异议分开。'],
  ['本段没有丧妻独立结果；原载强判断仍可作方法参照，不能标为已验。','非白虎不可此断是作者本段限制，不是凡见财虎必丧妻。'],451,453),
]
rules=[]
for n,title,conditions,conclusion,steps,exclusions,a,b in definitions:
    r=by_n[n]; rid=f'LR26-BOOK-SHAO-{n:03}';r['method_rule_ids']=[rid]
    cr=dict(r['source_refs'][0],case_id=r['source_case_identity'])
    rules.append(dict(schema='liuren-rule-card-v1',id=rid,title=title,categories=[r['category']],
        claim_origin='本轮归纳' if n in (39,43,45) else '原文明示',review_state='source_checked',
        status='candidate' if n in (39,43,45) else 'source_method',conditions=conditions,
        exclusions=exclusions,conclusion=conclusion,reasoning_steps=steps,
        alternatives=['原书主张、后注、结果及本轮限定分层；未由单例排除其他解释。'],
        evidence_refs=[ref(a,b)],source_case_refs=[cr],source_case_ids=[cr['case_id']],
        support_case_ids=[r['id'],cr['case_id']],counterexample_case_ids=[],legacy_entry_ids=[],relations=[],
        limitations=['已读原载结果，不是盲测。','引用校验仅证明定位，独立验证为0。'],
        independent_validation_count=0,logic_stages=['对象定位','关系链','适用条件','结果分项']))
for relative,batch in [('knowledge/liuren-research/20261102/book-cases/shao.json',records),('knowledge/liuren-research/20261102/rules/book-shao.json',rules)]:
    target=ROOT/relative
    merged={x['id']:x for x in json.loads(target.read_text(encoding='utf-8'))}
    merged.update({x['id']:x for x in batch})
    target.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=ROOT/'output/liuren-book-cases-20261102/shao-candidates.json'
data=json.loads(inventory.read_text(encoding='utf-8'))
data['reviewed_case_ids']=[x['id'] for x in json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/shao.json').read_text(encoding='utf-8'))]
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_cases':len(records),'new_methods':len(rules),'read_range':[310,453]},ensure_ascii=False))

from refresh_shao_coverage import refresh
refresh(ROOT)
