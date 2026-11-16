"""Independent B3 comparison of immutable B5 files; never selects one setting."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/liuren-book-cases-20261102'
BOOK='书籍库/北海闲人/毕法赋全解-正式整理本.md'
TRANS='课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md'

def sha(b):return hashlib.sha256(b).hexdigest()
def jhash(d):return sha(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode('utf-8'))
def differences(a,b,p=''):
    if type(a)!=type(b):return [p]
    if isinstance(a,dict):return [q for k in sorted(set(a)|set(b)) for q in differences(a.get(k),b.get(k),p+'.'+k)]
    if isinstance(a,list):return [p] if len(a)!=len(b) else [q for i,(x,y) in enumerate(zip(a,b)) for q in differences(x,y,p+'.'+str(i))]
    return [] if a==b else [p]

def verify_ref(e):
    raw=(ROOT/e['path']).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
    assert sha(raw)==e['sha256'] and '\n'.join(ls[e['line_start']-1:e['line_end']])==e['quote']

def ref(path,a,b):
    raw=(ROOT/path).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
    return {'path':path,'line_start':a,'line_end':b,'quote':'\n'.join(ls[a-1:b]),'sha256':sha(raw),'role':'原书断语'}

def actual(facts,field):
    keys=field.split('.');v=facts
    for key in keys:v=v[int(key)] if isinstance(v,list) else v[key]
    return v

def stable_facts(facts):
    d=copy.deepcopy(facts)
    for key in ['rule','requested_zhouye','actual_zhouye']:d.get('nobleman',{}).pop(key,None)
    return d

reviews=[]
specs=[(n,'',f'bifa-reconstruction-request-{n:03}.json') for n in [1,2,3,5,10,11,15,18,20]]
specs += [(n,'-MAIN',f'reconstruction-request-bifa-{n:03}-main.json') for n in [6,19,25]]
specs += [(n,'-AUDIT',f'bifa-reconstruction-request-{n:03}-audit.json') for n in [6,38,39,48,51,52,54,56,103,107,110,112,117,119,120,121,125,126,129,130]]
specs += [(110,'-PROSE','bifa-reconstruction-request-110-prose.json')]
specs += [(n,'-AUDIT',f'bifa-reconstruction-request-{n:03}-audit.json') for n in [21,26,29,31,32,37,57,61,62,69,70,77,85,91,95,96,97,100,102,131]]
specs += [(32,'-PROSE','bifa-reconstruction-request-032-prose.json'),(131,'-FORMAL','bifa-reconstruction-request-131-formal.json')]
specs += [(n,'-RELATION',f'bifa-reconstruction-request-{n:03}-relation.json') for n in [4,12,17]]
specs += [(114,'-AUDIT','bifa-reconstruction-request-114-audit.json')]
specs += [(n,'-AUDIT',f'bifa-reconstruction-request-{n:03}-audit.json') for n in [74,93]]
specs += [(n,'-CROSSSOURCE',f'bifa-reconstruction-request-{n:03}-crosssource.json') for n in [40,81]]
registry=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
for n,suffix,request_name in specs:
    rp=OUT/f'reconstructions/RC26-BIFA-{n:03}{suffix}.json';raw=rp.read_bytes();r=json.loads(raw)
    body={k:v for k,v in r.items() if k!='result_body_sha256'}
    assert jhash(body)==r['result_body_sha256'],(r['id'],'body hash')
    reqp=OUT/request_name;req=json.loads(reqp.read_text(encoding='utf-8'))
    assert jhash(req)==r['request_sha256'],(r['id'],'request hash')
    for e in req['input_evidence']:verify_ref(e)
    assert r['selected_candidate_id'] is None and not r['outcome_feedback_used_for_selection']
    for f in r['engine_fingerprint']['adapter_files']:
        assert sha((ROOT/f['path']).read_bytes())==f['sha256'],(r['id'],f['path'],'adapter drift')
    for f in r['engine_fingerprint']['original_files']:
        assert sha((ROOT/'排盘工具魔改'/f['path']).read_bytes())==f['sha256'],(r['id'],f['path'],'engine drift')
    candidates=[]
    for c in r['candidates']:
        ap=Path(c['archive']['path']).resolve();assert ap.is_relative_to(ROOT.resolve())
        ab=ap.read_bytes();assert sha(ab)==c['archive']['sha256']
        ar=json.loads(ab);assert ar['_direct']['facts']==c['facts'],(c['id'],'archive facts')
        comparisons=[]
        for q in c['comparisons']:
            for e in q['evidence_refs']:verify_ref(e)
            value=actual(c['facts'],q['field'])
            assert value==q['actual'],(c['id'],q['field'],'comparison actual')
            match=value==q['expected']
            assert match==q['match'],(c['id'],q['field'],'comparison result')
            comparisons.append({'field':q['field'],'expected':q['expected'],'actual':value,'match':match})
        assert all(q['match'] for q in comparisons)==c['all_constraints_match']
        candidates.append({'id':c['id'],'settings':c['input']['settings'],'sequence':c['facts']['transmission_sequence'],'transmission_generals':[v['tianjiang'] for v in c['facts']['transmissions']],'all_constraints_match':c['all_constraints_match'],'comparisons':comparisons,'archive_path':ap.relative_to(ROOT).as_posix(),'archive_sha256':c['archive']['sha256']})
    matching=[c for c in r['candidates'] if c['id'] in r['matching_candidate_ids']]
    diffs={c['id']:differences(matching[0]['facts'],c['facts']) for c in matching[1:]} if matching else {}
    equivalent=bool(matching) and all(stable_facts(c['facts'])==stable_facts(matching[0]['facts']) for c in matching)
    review={'case_id':r['case_id'],'result_id':r['id'],'result_path':rp.relative_to(ROOT).as_posix(),'result_sha256':sha(raw),'request_path':reqp.relative_to(ROOT).as_posix(),'request_sha256':r['request_sha256'],'result_body_sha256':r['result_body_sha256'],'original_source_condition':'original_transcript_fragment_preserved','semantic_review_state':'source_checked','engine_result_state':r['state'],'selected_candidate_id':None,'matching_candidate_ids':r['matching_candidate_ids'],'full_facts_exactly_equal':bool(matching) and all(c['facts']==matching[0]['facts'] for c in matching),'full_facts_difference_paths':diffs,'structural_facts_equal_after_excluding_setting_labels':equivalent,'excluded_setting_label_paths':['nobleman.rule','nobleman.requested_zhouye','nobleman.actual_zhouye'],'equivalent_candidate_groups':[{'candidate_ids':r['matching_candidate_ids'],'structural_facts_sha256':jhash(stable_facts(matching[0]['facts'])),'identity':'全部facts逐字段比较，只排除明确列出的设置标签；不是只比三传。'}] if equivalent else [],'candidates':candidates,'unverified_settings':r['unverified_settings'],'outcome_feedback_used_for_selection':False,'complete_changed':False,'independent_prediction_validation_count':0}
    if suffix:
        c=next(c for c in registry if c['id']==r['case_id'])
        review['review_source_refs']=c['source_refs'][:2]
        for e in review['review_source_refs']:verify_ref(e)
        eligible=equivalent and n not in {39,112,119}
        review['completeness_assessment']={'original_question_full_answer_feedback_or_explicit_absence_and_postnote_collected':True,'gap_supplied_by_full_equivalent_engine_facts':equivalent,'eligible_after_verified_appendix':eligible,'source_consistency_independent_of_completeness':True,'noncritical_missing':['原图、原贵人/昼夜/涉害标签未核；全结构实质等价组保留。','原载年命按来源保留，本轮未另算行年；没有反馈不能改成已发生。']}
        review['semantic_notes']=['已核请求/结果/全部raw及引擎指纹、全部观察对照；候选全部facts逐字段比较，仅排除所列设置标签；没有只比三传或按反馈选盘。']
        extra={
          40:['古汇选6041明确甲申五月乙未申将未时，四知姓名、兵围与渡江后述和毕法2949–2957同案；以申将跨源补证，非从事件后果猜将。','酉玄戌阴亥后、干巳龙支申常、四课巳午申酉与两版原残相符；毕法标题蒿矢及正文昴星措辞差异继续保留，不影响完整结构来源身份。'],
          81:['古汇选6825明确癸未正月己亥亥将未时，与毕法赵忻城昆弟六月钦召题断后述逐项对齐；亥将为跨源明文。','未龙亥蛇卯玄、干亥蛇支卯玄、四课亥卯卯未符合原盘及官局/皇恩天诏的原作者论证；钦召和甲申升官仅原后述，未核史实。'],
          6:['正式1054明确戌巳子，转录主列子巳戌仍留；AUDIT只补入六亲行戌合、巳常、子蛇，未覆盖无天将约束MAIN。','干上卯、支上巳、卯上戌及巳上子，与原残四课及斫轮说明相符；原寿七十二无独立寿终回访。'],
          19:['申虎巳勾寅蛇与断案同案完整盘及正文相符，北海主残申子寅仍标异文；不是以刑死结果决定三传。','干亥、支卯与四课原残及申刃等关系相容；命巳/40岁原载，本轮未新算年命，正月寅月破原句仍存疑。'],
          25:['巳勾寅蛇亥阴、干巳支亥及两方俱生互脱与正式2252/2254一致，完整断案同源盘另存。','十一年原断、二年娶妇和五年分家等后述逐项保留，不能合成一次全准反馈。'],
          38:['戌虎酉空申龙、干戌虎支卯贵及四课戌酉卯寅，与3299–3307及正式2849–2855一致。','原载天解、鬼脱生与老板出钱放人是作者解释及后述；真实警务记录未核。'],
          39:['引擎8候选均申丑午，主残申卯午不符；六亲另丑阴与部分候选相容，不能删除主列后升完整。','病块是当场应答；原断官灾/死亡没有新增现实核验，保持fragment。'],
          48:['戌虎酉常申玄、支上戌虎及干子、阴亥与原残四课一致，宅天目月厌等仍原作者分类。','进畜原有不荣为已知背景，五年怪异及迁宅为原后述，不能作墓尸致病的现实证实。'],
          51:['申后寅龙巳雀、伏吟干上申与支上辰、原残四课辰辰申申一致。','武不成/文科甲是分项与后续；申空及寅龙学堂类象仍来源解释，未核历史榜录。'],
          52:['子虎亥常戌玄、干丑空、支卯勾及寅卯子丑四课，与3907残图及正文一致。','子病手术花费与宅基争吵分开，坟墓不整致肿胀是原作者解释，不作疾病因果验证。'],
          54:['午蛇卯勾子虎、干巳雀支酉阴、四课巳寅酉午与原残一致；原文只用初鬼、忽略干支鬼的取舍保留。','卯日预约与甲辰出行得财分阶段；未由收入金额补设置。'],
          56:['丑空亥常酉阴、干卯支寅及丑加卯/酉加亥符合3498–3510与残四课。','戊辰日来自正文戊辰干支，不是根据结果倒推；两棺、女众及酒病只原断/俱验称述。'],
          103:['申空亥玄寅贵、干丑后及支申空、四课丑辰申亥符合转录379。','单引寅月建在丑前、贵登天门等位置可定位；庚戌得职和辛亥催赴任分阶段，岳父夜贵附会原作者自限保留。'],
          107:['丑后卯玄巳虎、干酉合/支亥蛇及第四课丑发用符合转录511与正文。','长期与当前空实不同尺度，离乡低薪为当场既往自述；未虚构终身追访。'],
          110:['亥辰辰与原主传相符；首轮AUDIT只约束三传而全facts不等价，不能据此硬定。','PROSE另据正式491天罡加干支又乘勾陈，加入两课辰勾约束，未用辛酉当选反馈挑盘；干辰勾/支辰勾和四课辰丑辰丑与原残相合。'],
          112:['引擎8候选均亥巳亥，与转录巳亥巳主传及将列冲突；明确题干不改，保留fragment。','丁巳命及午行年只原载；考中后述不用于选择另一日或将时。'],
          117:['巳勾申蛇寅虎、干巳支寅与伏吟及四课巳巳寅寅原残一致。','离不了与岳母挑拨均为原断，没有后来婚姻结果；保留未载反馈及人格指控身份。'],
          119:['8候选均丑亥酉，与主残亥酉丑不符，六亲列丑亥酉但将列也需另核；本批不修盘。','六阴及四课阳明仍可作方法观察，四年六年败的原断不冒充真实后述。'],
          120:['酉贵亥阴丑常、干酉支丑、四课酉亥丑卯与转录823相符；丑为月建。','正文酉加于支上发用与实算盘干上酉/支上丑有措辞冲突，完整保存且不因盘补齐删除；丑日到只原称果验。'],
          121:['午虎子蛇午虎、干亥支子、四课亥巳子午与转录849相符。','原文子午均空与戊午日旬空子丑存在冲突；保留作者说法及计算事实，不据历史政变改盘。公历3月/辰月亦保留原样。'],
          125:['丑勾子龙亥空、干子青龙支寅六合，与转录995及旺禄子龙临干说明一致。','丁巳命巳年原载不补算法；只讲吉象没有任职或成期反馈，完整性不等于预测成功。'],
          126:['戌合午虎寅后、干戌支申与转录1003一致；末寅临午的盘位可定位。','甲子题年与明年戌/后年丁亥、初六合与正文虎发用等原文冲突另轴保留；使用明载甲子不猜改年，盘可明确补足不妨完整保存。'],
          129:['辰玄酉勾寅后、干戌合、支亥朱与原残四课一致；巳落子、辰在亥位置可查。','作者明确不是末寅鬼为主，肝癌与丙子死亡为原后述，无医疗档案独核。'],
          130:['子蛇未常寅合、干子支未及四课子未未寅与转录1449一致。','正式改土象/支上未常的编辑层保留，转录干上未常与实盘不合亦不抹去；前后形势与各人病各别标原反馈。'],
          21:['明载酉将申时戊子的8候选均寅卯辰，与残行戌玄酉常申虎及正文三传会西方不合，保持fragment。','2445自称可读四课，残符号角色仍有歧义；AUDIT将戌酉申作为待比排列，并不确认该残列已经完整三传。不能凭脑血管病后述反推将时。'],
          26:['午阴丑龙申贵、干亥合支戌朱，四课亥午戌巳与转录2655一致，初生中中生末末克干关系可定位。','原断朋友合作恩多怨深与婚离象按不同对象留；没有合作后续不改成已验。'],
          29:['巳阴丑雀酉空、干支皆酉天空，四课酉巳酉巳与2739一致；败气/亚魁解释原层次保留。','原问夺冠与后述铜牌分项，非赢奖即夺冠全准。'],
          31:['午蛇辰合寅龙、干午支寅、四课午辰寅子与2831一致；仅两个匹配候选的完整facts亦已逐字段比较。','原载转让金负担和放弃为反馈，不能把未做餐馆改成经营损益实证。'],
          32:['辰巳午主序与正文相符，AUDIT无天将约束故全facts不等价；PROSE另以财辰六子巳勾子午龙及正文辰加卯六合/巳加辰勾陈比较。','PROSE干支卯雀、四课卯辰卯辰和末午龙符合转录2859；守旺与末助初财的适用差别仍保留，未核子病死亡历史档案。'],
          37:['申龙亥雀寅后、干巳常支卯阴、四课巳申卯午与3203一致。','身份、当前拘系辨雪及未来显官不久分阶段；后知钱牧斋及甲申任官只是原后述，不增加验证次数。'],
          57:['8候选均未亥卯，主残未卯亥不符，但六亲行未勾亥贵卯常与部分候选相合；不替换原主列。','重病是已知状态，五一前死亡是原载后述，当前保留fragment等候原图或跨源核序。'],
          61:['巳勾申虎寅蛇、干巳支申及伏吟四课巳巳申申符合4277残行。','战火背景与本人安危分开，只原称不忧，未查真实返程或军情。'],
          62:['巳合申空寅贵、干戌常支巳合与4283四课一致；元旦按农历正月映射寅，非猜古公历日。','母弟既往家信、乙酉妻亡为不同年份后述，五行疾病论仍原作者意见。'],
          69:['8候选均戌巳子而残主戌子寅、天将六阴龙不合；完整原输入保留，不按贬职死亡反馈倒推。','原六亲父子龙也有残误，年命/年月及太岁推断不由本次引擎唯一确定。'],
          70:['巳虎戌雀卯玄、干子贵支辰常与转录4583残行一致。','捕获贼人、官释及失赃分三项保存，原载获人不可改成赃物已回。'],
          77:['亥空子龙卯雀、干亥支子与伏吟四课亥亥子子相符。','26年原断与16年原后述为寿数失验/张力，不能以四亥事后算16抹去原失验；完整结构不表示数量准确。'],
          85:['午玄丑雀申虎、干午支酉与四课午丑酉辰原残相符。','九年屋改田园及妻病眼病、寿等多子项分记；白蚁为原后述，不证明坟墓致病。'],
          91:['戌玄申虎午龙、干子支子、阴戌，四课子戌子戌与5333原残一致。','学生既往获利是当场自述，当前能力未稳与将来收益分开，不据股利改设置。'],
          95:['亥勾寅虎巳阴、干申蛇支未贵，四课申亥未戌与5451一致。','巳月原拟与实际未月明确分开，未贵印绶为事后解释；成事不能覆盖应月错误。'],
          96:['巳勾申虎寅蛇、干巳支寅与四课巳巳寅寅、伏吟一致。','原断不会传入与后多省小疫情构成失验，后改释规模小为修订；盘补全不洗成命中。'],
          97:['巳玄戌雀卯虎、干子勾支辰常与5589残四课一致。','先发利、购店争竞、九年期和一身合眼等原断/后述分别保存，不强增寿终现实验证。'],
          100:['辰后未雀戌龙、干辰支戌、四课辰未戌丑符合5713残行及三传官局冲散的原解。','原问考副县与未入复试的原反馈分记；官鬼冲散在脱难和考试两种目标不能同断。'],
          102:['明载未将卯时辛巳的8候选均酉丑巳，与午寅戌及天将不符；钟点下午1:30又与卯时矛盾，保持fragment。','不依据已知阿拉法特死亡去改月/将/时；原戌月及后析亥月、年命原词均保留。'],
          131:['AUDIT保留转录主残卯申巳无匹配；FORMAL据1068/1074明文另列卯玄戌雀巳虎，四个全facts等价候选。','FORMAL干寅阴支申勾、四课寅酉申卯符合转录残四课；原主卯申巳/卯六及正文支子/后注申仍标来源冲突，子科甲后续未明。'],
          4:['原载伏吟且未时；4416十二支各加本位为明文关系约束，候选将未非主案直载值，真实引擎已逐核12宫皆同位。','巳勾申虎寅蛇与转录2575相符，四课巳巳寅寅；日后参劾/解任及申猴侯大司农的可能性解释仍各别保存。'],
          12:['原载伏吟酉时；以4416定义产生将酉关系候选，实际引擎12宫皆同位，辰勾酉后卯龙与1747残列吻合。','干辰支酉及四课辰辰酉酉相符，冯尔忠三处引文已齐；双胎男女生死均无实际反馈，不因补盘改为生育事实。'],
          17:['原载伏吟戌时关系候选的8盘均卯子午，原残卯卯卯且卯蛇并不相符；逐核12宫伏吟成立仍不足以恢复原残三传。','阴阳贵人和双男反馈均不用于选另一将时；戊日/戌日、龙虎/龙战及养神等异文保留fragment。'],
          114:['正式564明载午月将，实际8盘均未亥卯，与主残未卯亥不符；未蛇亥龙卯玄与残字可部分比，但不可静默改列。','原题涉害曲直、财局/木局和初中空末实等两版差异保留，不凭未年中第断语改源。'],
          74:['申龙午虎午虎、干支上午虎、四课午戌午戌与转录4669原残相符，甲寅戌将午时明载。','糖尿病和卧床为已知背景，4月14病故为原后述；补盘不能将原先已知病情当预先推得。'],
          93:['戊午八月庚戌子时由转录5359完整原题，辰月将由正式4588正文；辰申子三传及子青龙有明文。','子时第一课干子龙支寅虎，父己酉命和本人丙子命按原文保存，本轮未新算行年；未时第二课仅原载另报时，不借第一盘冒作第二全盘。','正式压缩长例、转录甲日德禄/正式庚日德禄与庚/辰生气等异文仍留；父痰火与年安、本人中式分两项，不作一次全准确验证。'],
        }
        review['semantic_notes']+=extra[n]
        if suffix=='-RELATION':review['input_identity']='relation_constrained_candidate_not_directly_stated_month_general'
        review['source_consistency']={'state':'conflict_preserved' if not matching or n in {6,19,21,39,40,57,69,77,93,95,96,102,112,119,120,121,126,130,131} else 'no_new_material_conflict','does_not_rewrite_source':True}
        if not eligible:review['completeness_assessment']['reason']='全约束无匹配或匹配候选全结构尚非实质等价；仅保存候选，当前分支不补全关键缺项。'
    elif n==1:
        review['completeness_assessment']={'original_question_full_answer_feedback_and_postnote_collected':True,'only_critical_gap_was_original_chart':True,'gap_supplied_by_full_equivalent_engine_facts':True,'eligible_after_verified_appendix':True,'noncritical_missing':['原作者具体贵人/昼夜/涉害设置标签未明，全部实质等价候选保留。']}
        review['review_source_refs']=[ref(BOOK,876,884),ref(TRANS,1035,1045)]
        review['semantic_notes']=['四个全约束吻合候选全部12宫、四课、三传、旬干纳音神煞及生旺等结构facts实质相同；具体差异路径另列，没有强选唯一设置。','巳常、戌蛇、卯空与转录1037，支上巳德禄常/中传月建/末传月将与正式878–880逐项相符；月将卯加戌时。','主案全文及884后注已收，882仍注明插入的求职泛论，不当店案反馈。盘可独立复原；完整性升级还需以标准复原身份展示，不能冒作恢复原图。']
    elif n==2:
        review['completeness_assessment']={'original_question_full_answer_feedback_and_postnote_collected':True,'only_critical_gap_was_original_chart':True,'gap_supplied_by_full_equivalent_engine_facts':True,'eligible_after_verified_appendix':True,'noncritical_missing':['未明载完整年命数值，太岁贵人居命原断尚不能独立核命位。','原始设置标签未明，但符合原载的候选完整结构等价。']}
        review['review_source_refs']=[ref(BOOK,902,906),ref(BOOK,1151,1155),ref(TRANS,1067,1073),ref(TRANS,1365,1371)]
        review['semantic_notes']=['四个全约束吻合候选的结构facts相同，设置标签差异保留，未强选唯一贵人法/涉害法。','寅蛇、午龙、午龙符合两处残盘及正式初蛇末龙、末午为月将说明；古汇选与引擎古例明确午将巳时。','原载太岁贵人居命未明载完整本命，不能由反推猜成客户年命；同案历史异文继续保留。']
    elif n==3:
        review['completeness_assessment']={'eligible_after_verified_appendix':False,'reason':'原盘主列、六亲残列与引擎三序仍须核；正文只提供部分相容佐证，不静默改源或选唯一盘。'}
        review['review_source_refs']=[ref(BOOK,2189,2195),ref(TRANS,2563,2571)]
        compatible=[c['id'] for c in r['candidates'] if [v['tianjiang'] for v in c['facts']['transmissions']][:2]==['腾蛇','太常']]
        review['prose_compatible_candidate_ids']=compatible
        review['source_order_comparison']={'transcript_primary_list':'未子寅','transcript_liuqin_print_order':'未寅子','engine_all_eight_sequences':'子未寅','formal_prose':'2193明确发用蛇、中传太常；2195说递克而到子水，未直接列未寅子为传序。'}
        review['semantic_notes']=['原始请求003保留转录主列未子寅，因此8候选全部全约束不通过；不得删除这条不符或覆盖旧请求/结果。','重新逐字读2193，发用蛇与中传太常明确；结合2565可读子蛇、未常，子蛇/未常/寅合的4候选与该段正文相容，可作结构佐证，仍未核原图。','需修正此前请求说明中正式讲解另指未寅子的过强概括：正式文只说发用蛇、中传太常与递克到子，六亲残字排列不必等于三传完整顺序。本复核保留三方，未静默改原请求。','引擎子未寅与两项天地盘坐墓关系相符，不等于原图残损已解决；保留constraint_conflict与全部设置候选，不以其子被逮结果挑盘。']
    elif n==18:
        review['completeness_assessment']={'eligible_after_verified_appendix':False,'reason':'明确原载未将巳时壬戌输入与转录三传冲突，不能由正文到达断语择盘或改将。'}
        review['review_source_refs']=[ref(BOOK,1746,1750),ref(TRANS,2041,2047)]
        review['source_order_comparison']={'transcript_primary_list':'亥子丑','transcript_generals':'亥空/子虎/丑常','engine_all_eight_sequences':'子寅辰','formal_prose':'1746明确未将巳时壬戌日；1748干神归支、乘天空、受支克，但没有直接列完整传序。'}
        review['semantic_notes']=['原载参数与残盘约束全8候选不符，原始请求/结果保持不可变并保留constraint_conflict。','子寅辰不改成亥子丑，亦不倒改原文未将或占时以凑盘；寄物是否已到未载签收反馈，不用于筛选。','附录提供独立候选以暴露冲突，不宣告原图已核或案例complete。']
    else:
        assert n in {5,10,11,15,20} and equivalent
        spans={5:((810,812),(953,959)),10:((1281,1285),(1513,1519)),11:((1301,1305),(1535,1541)),15:((1598,1618),(1857,1879)),20:((2057,2067),(2405,2417))}
        br,tr=spans[n]
        review['completeness_assessment']={'original_question_full_answer_feedback_or_explicit_absence_and_postnote_collected':True,'only_critical_gap_was_original_chart':True,'gap_supplied_by_full_equivalent_engine_facts':True,'eligible_after_verified_appendix':True,'noncritical_missing':['贵人/昼夜/涉害原始设置未明，保留全结构实质等价组。','年命与现场背景按原载保留；未载内容不补，未另计算行年。']}
        review['review_source_refs']=[ref(BOOK,*br),ref(TRANS,*tr)]
        prose={
          5:['卯空→午合→午合符合转录955，四课午/巳/午/巳与原残文及八专课体相容。','初卯在丁未旬空，原载初空乘空、中末归干支午均相符；原有1966生未反推命支/行年。'],
          10:['酉贵→丑常→巳勾符合转录1515；四课支上午为月将，与1283相符。','年/月按正式本校甲月为申月，原转录/校勘身份仍留；入住后利人/损财反馈分项，不能作因果验证。'],
          11:['申合→戌龙→子虎符合转录1537；干上丑常、初申空、中戌龙等与1303相容。','完整原断和后注已收，但未载实际调动反馈；完整性与有无结果验证分别记录。'],
          15:['子龙→亥空→戌虎符合转录1861；干上戌、支上丑及退茹与1612相符。','夹定/透关和天时类象的正文保全；灾情、路径、气象解释仍仅原书转述，无外部现实核验。'],
          20:['卯玄→申朱→丑虎与转录2407及断案完整盘相符；四课卯/申/申/丑和赘婿等课体相容。','原载命午为明确来源字段，逼煞午害丑等原作者说明可定位；本次不新算行年，不能把year_life_verified当已核客户数据。','邵案与北海本段同事件，归葬/分家/死丧分项及北海道德报应说明仍分别存身份。']}
        review['semantic_notes']=['全约束吻合候选完整facts逐字段实质相同，具体设置差异路径另列，不仅比三传，不强选唯一贵人法。']+prose[n]
    reviews.append(review)

report={'schema':'bifa-reconstruction-semantic-review-v1','result':'PASS_provenance_and_comparison_integrity','reviews':reviews,'candidate_count':sum(len(r['candidates']) for r in reviews),'archive_hashes_verified':sum(len(r['candidates']) for r in reviews),'source_condition_changed':False,'complete_changed':False,'prediction_validation_increment':0}
(OUT/'bifa_reconstruction_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':report['result'],'archive_hashes_verified':report['archive_hashes_verified'],'requests_reviewed':len(reviews),'cases_eligible':len({r['case_id'] for r in reviews if r['completeness_assessment'].get('eligible_after_verified_appendix')}),'unmatched_branches':[r['result_id'] for r in reviews if not r['matching_candidate_ids']]},ensure_ascii=False,indent=2))
