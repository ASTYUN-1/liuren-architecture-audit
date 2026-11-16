"""Prepare reviewable B5 requests; this script never executes an engine."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BOOK='书籍库/北海闲人/毕法赋全解-正式整理本.md'
TRANS='课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md'
ENGINE='docs/六壬知识整理-20261102/引擎古例参考源/古例全文.md'
OBJECT='docs/六壬知识整理-20261102/引擎古例参考源/古例原始对象.json'

def ref(path,a,b,role='原书断语'):
    raw=(ROOT/path).read_bytes();lines=raw.decode('utf-8-sig').splitlines()
    return {'path':path,'line_start':a,'line_end':b,'quote':'\n'.join(lines[a-1:b]),'sha256':hashlib.sha256(raw).hexdigest(),'role':role}

def condition(field,value,refs,**extra):
    return {'field':field,'expected':value,'evidence_refs':refs,'extraction_review_state':'source_checked',**extra}

def request(n,year,month,day,hour,general,evidence,sources,constraints,notes,engine_index=None):
    r={'schema':'liuren-book-reconstruction-request-v1','id':f'RC26-BIFA-{n:03}','case_id':f'BK26-BIFA-{n:03}',
       'input':{'mode':'manual-pillars','pillars':{'year':year,'month_branch':month,'day':day,'hour_branch':hour},'month_general':general,'label':f'书案毕法{n:03}标准复原'},
       'input_evidence':evidence,'input_sources':sources,'constraints':constraints,
       'settings_review':{'state':'candidate_not_originally_declared','guiren':'原书未明确完整贵人法；采用引擎默认/随附设置时须另列为计算约定。','zhouye':'原书时支明确而昼夜取法未明载；自动昼夜属计算设置，不当原文事实。','shehai':'原书未明载涉害取法；原书课体与传序仅作对照，不按反馈选参数。'},
       'notes':notes+['只复原结构，不以反馈选盘，不把结构吻合当效果验证。','原转录残图身份保留；标准输出和语义核对前不改complete。']}
    if engine_index is not None:
        r['engine_reference']={'index':engine_index,'sha256':hashlib.sha256((ROOT/OBJECT).read_bytes()).hexdigest(),'same_event_review_state':'source_checked','same_event_reason':'占年、月、日、时、问题对象、原陈断及后续均可对读；字词异文并存，不统一史实。','match_evidence':evidence}
    p=ROOT/f'output/liuren-book-cases-20261102/bifa-reconstruction-request-{n:03}.json'
    p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

request(1,'甲申','戌','丙子','戌','卯',
    [ref(BOOK,876,884),ref(TRANS,1035,1045)],
    {'pillars.year':'正式876原载甲申年','pillars.month_branch':'正式876原载戌月','pillars.day':'正式876丙子日','pillars.hour_branch':'正式876戌时','month_general':'正式876卯将'},
    [condition('transmission_sequence','巳戌卯',[ref(TRANS,1037,1037)]),
     condition('transmissions.0.tianjiang','太常',[ref(TRANS,1037,1037),ref(BOOK,880,880)]),
     condition('transmissions.1.tianjiang','腾蛇',[ref(TRANS,1037,1037)]),
     condition('transmissions.2.tianjiang','天空',[ref(TRANS,1037,1037),ref(BOOK,878,878)]),
     condition('lessons.2.tianpan','巳',[ref(BOOK,880,880)])],
    ['主会先前结果reconstruction-result-bifa-001.json已有三传巳常戌蛇卯空。本请求转标准归档及约定核查，不是重复独立验证。'])
request(2,'丁丑','申','戊辰','巳','午',
    [ref(BOOK,902,906),ref(BOOK,1151,1155),ref('书籍库/现代著作/《壬占汇选》.txt',823,831),ref(ENGINE,10287,10326,'后人注解')],
    {'pillars.year':'正式902丁丑','pillars.month_branch':'引擎原对象GuAnLi2[257].sizhu.mz=申；古文七月原样保留，后人输入不冒称北海逐字字段','pillars.day':'正式902戊辰日','pillars.hour_branch':'正式902丁巳时','month_general':'正式906末午月将；古汇选823明确午将巳时；古例问句10294同'},
    [condition('transmission_sequence','寅午午',[ref(TRANS,1069,1069),ref(TRANS,1367,1367)]),
     condition('transmissions.0.tianjiang','腾蛇',[ref(TRANS,1069,1069),ref(BOOK,906,906)]),
     condition('transmissions.2.tianjiang','青龙',[ref(TRANS,1069,1069),ref(BOOK,906,906)])],
    ['同事件另登记BK26-ANCIENT-017；蔡凤阳/熙阳、北京中府/汉中府、戊寅正月/六月入相等异文并存。','引擎原对象Date/Time=2000-01-01/01:01是显示占位，不作真实占时。'],engine_index=257)
request(3,'戊寅','辰','丙寅','卯','戌',
    [ref(BOOK,2189,2195),ref(TRANS,2563,2571),ref(ENGINE,7207,7246,'后人注解')],
    {'pillars.year':'正式2189戊寅','pillars.month_branch':'引擎古例GuAnLi2[180].sizhu.mz=辰，后人输入；原载三月保留','pillars.day':'正式2189丙寅日','pillars.hour_branch':'正式2189辛卯时','month_general':'引擎古例问句7214明确戌将，北海本段未直接载将；同事件交叉补充'},
    [condition('heaven_earth.10.tian','巳',[ref(BOOK,2193,2193)]),
     condition('heaven_earth.7.tian','寅',[ref(BOOK,2193,2193)]),
     condition('transmission_sequence','未子寅',[ref(TRANS,2565,2565)],source_conflict_note='转录同一行六亲列未寅子，正式2195讲解递克到子；此expected只保存主列残文，预期可能冲突，不能自动据此判引擎错误或改写原文。')],
    ['三传原转录主列未子寅，与六亲行及递克讲解未寅子矛盾；本请求故意保留对照，不预选一个序列宣告原载已完整。','引擎对象虽同案，仍是后人输入与转引，不能单凭其断语/结局认证算法。'],engine_index=180)

print(json.dumps({'requests':3,'engine_executed':False,'case_completeness_changed':False},ensure_ascii=False))
