"""Mechanical whole-book cue queue; never promotes scanning to substantive review."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/liuren-book-cases-20261102'
BOOK='书籍库/北海闲人/毕法赋全解-正式整理本.md'
TRANS='课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md'
REVIEWED={7:(782,850),8:(854,926),9:(930,990),10:(994,1076),11:(1080,1165),12:(1169,1229),13:(1233,1255),14:(1259,1305),15:(1309,1349),16:(1353,1379),17:(1383,1413),18:(1417,1443),19:(1447,1624),20:(1628,1668),21:(1672,1750),22:(1754,1790),23:(1795,1830),24:(1795,1830),25:(1834,1923),26:(1927,1967),27:(1971,2003),28:(2007,2029),29:(2033,2067),30:(2071,2119),31:(2123,2150),32:(2154,2203),33:(2207,2225),34:(2229,2289),35:(2293,2326),36:(2330,2398),37:(2402,2461),38:(2465,2521),39:(2525,2564),40:(2568,2605),41:(2609,2619),42:(2623,2631),43:(2635,2661),44:(2665,2685),45:(2689,2699),46:(2703,2729),47:(2733,2778),48:(2782,2797),49:(2801,2817),50:(2821,2829)}
REVIEWED.update({51:(2833,2867),52:(2871,2875),53:(2879,2901),54:(2905,2933),55:(2937,2972),56:(2976,3008),57:(3012,3076),58:(3080,3112),59:(3117,3141),60:(3117,3141)})
REVIEWED.update({61:(3145,3180),62:(3184,3248),63:(3252,3274),64:(3278,3296),65:(3300,3310),66:(3314,3330),67:(3334,3388),68:(3392,3422),69:(3426,3461),70:(3465,3510)})
REVIEWED.update({71:(3514,3532),72:(3536,3567),73:(3571,3597),74:(3601,3667),75:(3671,3763),76:(3767,3806),77:(3810,3872),78:(3876,3947),79:(3951,4002),80:(4006,4028)})
REVIEWED.update({81:(4032,4068),82:(4072,4172),83:(4176,4219),84:(4223,4263),85:(4267,4328),86:(4332,4356),87:(4360,4382),88:(4386,4408),89:(4412,4446),90:(4450,4522)})
REVIEWED.update({91:(4526,4564),92:(4568,4590),93:(4594,4629),94:(4633,4691),95:(4695,4755),96:(4759,4789),97:(4794,4838),98:(4794,4838),99:(4842,4870),100:(4874,4897)})
REVIEWED.update({1:(182,358),2:(362,449),3:(453,600),4:(604,671),5:(676,778),6:(676,778)})
TRANS_READ=[(125,189),(201,693),(705,923),(925,1007),(1013,1097),(1101,1183),(1187,1277),(1291,1383),(1387,1485),(1489,1695),(1699,1885),(1889,2147),(2151,2477),(2489,2581),(2585,3021),(3033,3271),(3283,3647),(3659,4065),(4077,4685),(4697,5281),(5293,5719)]

def write(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def run():
    cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
    rules=json.loads((ROOT/'knowledge/liuren-research/20261102/rules/book-bifa.json').read_text(encoding='utf-8'))
    raw=(ROOT/BOOK).read_bytes();lines=raw.decode('utf-8-sig').splitlines();sha=hashlib.sha256(raw).hexdigest()
    anchors=[];sections=[]
    for n,line in enumerate(lines,1):
        m=re.search(r'^<a id="law-(\d{3})"></a>',line)
        if m:anchors.append((int(m[1]),n))
        if line.startswith('## 第') and anchors:
            sections.append({'law_numbers':[x for x,_ in anchors],'title':line[3:],'anchor_start':anchors[0][1],'line_start':n})
            anchors=[]
    for i,s in enumerate(sections):
        s['line_end']=sections[i+1]['anchor_start']-1 if i+1<len(sections) else len(lines)
        s['substantive_review_state']='read_in_full' if all(n in REVIEWED for n in s['law_numbers']) else 'pending'
        s['scan_state']='mechanical_cues_scanned'
    law_numbers={n for s in sections for n in s['law_numbers']}
    assert law_numbers==set(range(1,101)),sorted(law_numbers)
    cue_patterns=[('explicit_date',r'公历\d|[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]年.{0,30}月.{0,35}日'),('time_and_question',r'[子丑寅卯辰巳午未申酉戌亥]将[子丑寅卯辰巳午未申酉戌亥]时|索占|课例：|某.{0,25}占|两人一起'),('attributed_answer',r'邵先生曰|邵子曰|先生断曰')]
    queue=[]
    for s in sections:
        for n in range(s['line_start']+1,s['line_end']+1):
            line=lines[n-1]
            triggers=[name for name,p in cue_patterns if re.search(p,line)]
            if not triggers:continue
            linked=[c['id'] for c in cases if any(e['path']==BOOK and e['line_start']<=n<=e['line_end'] for e in c['source_refs'])]
            queue.append({'id':f'BIFA-CUE-L{n:04}','law_numbers':s['law_numbers'],'review_state':'pending','scan_only':True,'candidate_kind':'text_cue_not_adjudicated_case','cue_triggers':triggers,'source_ref':{'path':BOOK,'line_start':n,'line_end':n,'quote':line,'sha256':sha,'role':'原书断语'},'registered_case_ids':linked,'boundary_status':'not_inferred_by_scanner','recovery_status':'see_registered_case_notes' if linked else 'pending_chart_and_transcript_check','warning':'日期/问占/署名命中不证明真实事件、边界完整、已精读或独立案例。'})
    traw=(ROOT/TRANS).read_bytes();tls=traw.decode('utf-8-sig').splitlines();tsha=hashlib.sha256(traw).hexdigest()
    damaged=[{'path':TRANS,'line_start':n,'line_end':n,'quote':line,'sha256':tsha,'role':'原书断语','review_state':'pending','scan_only':True,'meaning':'转录残盘线索；不自动映射正式本行号或完整案边界。'} for n,line in enumerate(tls,1) if '课盘' in line and ('错乱' in line or '从略' in line)]
    queue_obj={'schema':'bifa-candidate-queue-v1','scope':'全文机械线索扫描；不等于全文精读或完整案例数','book_sha256':sha,'sections':sections,'cues':queue,'transcript_damage_cues':damaged,'registered_case_recovery':[{'id':c['id'],'completeness':c['completeness'],'source_case_identity':c['source_case_identity'],'missing_fields':c['missing_fields'],'source_recovery':c['source_recovery'],'engine_input_notes':[n for n in c['notes'] if n.startswith('排盘引擎复原输入摘记：')]} for c in cases],'scanner_limits':['启发式可能漏掉隐含案例，也可能命中通用例式或同案后注。','每条cue仍为pending；链接已有登记不令cue本身冒充已审案。','跨法重例除已确认的杨大司马外，仍须逐一核实，不按书路径归并。','缺反馈不作为排除方法价值的条件；补盘允许引擎候选与原图并行。']}
    write('bifa_candidate_queue.json',queue_obj)
    coverage={'schema':'bifa-coverage-v1','mechanical_scan':{'law_numbers':list(range(1,101)),'chapter_sections':len(sections),'cue_count':len(queue),'transcript_damage_cues':len(damaged),'status':'scan_only'},'substantive_review':{'law_numbers':sorted(REVIEWED),'law_count':len(REVIEWED),'formal_ranges':[{'path':BOOK,'line_start':a,'line_end':b,'law_number':n} for n,(a,b) in REVIEWED.items()],'transcript_read_ranges':[{'path':TRANS,'line_start':a,'line_end':b} for a,b in TRANS_READ],'cross_references_not_full_review':[],'next_unread_from_sequential_continuation':None,'pending_law_numbers':[n for n in range(1,101) if n not in REVIEWED]},'registered_cases':len(cases),'complete':sum(c['completeness']=='complete' for c in cases),'fragment':sum(c['completeness']=='fragment' for c in cases),'method_cards':len(rules),'same_event_cross_law_registers':[{'id':c['id'],'source_case_identities':[c['source_case_identity']]+c.get('additional_source_case_identities',[]),'independent_events':1,'same_event_ids':c['same_event_ids']} for c in cases if c.get('additional_source_case_identities')],'independent_validation_count':0,'status':'whole_book_substantive_and_second_pass_coverage_audited_chart_recovery_incomplete'}
    write('bifa_coverage.json',coverage)
    print(json.dumps({'sections':len(sections),'cue_count':len(queue),'transcript_damage_cues':len(damaged),'substantive_laws':len(REVIEWED),'cases':len(cases),'methods':len(rules)},ensure_ascii=False))

if __name__=='__main__':run()



