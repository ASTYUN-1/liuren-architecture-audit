"""Prepare new source-bound requests without touching immutable requests 001–003."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/liuren-book-cases-20261102'
BOOK='书籍库/北海闲人/毕法赋全解-正式整理本.md'
TRANS='课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md'
def ref(path,a,b):
    raw=(ROOT/path).read_bytes();lines=raw.decode('utf-8-sig').splitlines()
    return dict(path=path,line_start=a,line_end=b,quote='\n'.join(lines[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role='原书断语')
specs=[
 (5,'丙戌','巳','丁未','戌','酉',(810,812),(953,959),'卯午午',['天空','六合','六合']),
 (10,'甲申','申','丙寅','寅','午',(1281,1285),(1513,1519),'酉丑巳',['贵人','太常','勾陈']),
 (11,'乙酉','未','壬辰','巳','未',(1301,1305),(1535,1541),'申戌子',['六合','青龙','白虎']),
 (15,'丙戌','未','壬寅','申','未',(1598,1618),(1857,1879),'子亥戌',['青龙','天空','白虎']),
 (18,'乙酉','未','壬戌','巳','未',(1746,1750),(2041,2047),'亥子丑',['天空','白虎','太常']),
 (20,'戊申','寅','辛卯','未','子',(2057,2067),(2405,2417),'卯申丑',['玄武','朱雀','白虎']),
]
for n,year,month,day,hour,general,br,tr,sequence,generals in specs:
    evidence=[ref(BOOK,*br),ref(TRANS,*tr)]
    if n==20:evidence.append(ref('书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt',48,57))
    constraints=[dict(field='transmission_sequence',expected=sequence,evidence_refs=evidence,extraction_review_state='source_checked')]
    constraints += [dict(field=f'transmissions.{i}.tianjiang',expected=v,evidence_refs=evidence,extraction_review_state='source_checked') for i,v in enumerate(generals)]
    request=dict(schema='liuren-book-reconstruction-request-v1',id=f'RC26-BIFA-{n:03}',case_id=f'BK26-BIFA-{n:03}',
        input=dict(mode='manual-pillars',pillars=dict(year=year,month_branch=month,day=day,hour_branch=hour),month_general=general,label=f'毕法{n:03}有据参数复原'),
        input_evidence=evidence,input_sources={'pillars.year':f'正式{br[0]}原载干支年{year}',
        'pillars.month_branch':('正式2057原载正月，按月建寅记入；这是农历月序映射，不声称确定古公历日。' if n==20 else f'正式{br[0]}原载{month}月；保留原年/月字段，非据结果猜补'),
        'pillars.day':f'正式{br[0]}原载{day}日','pillars.hour_branch':f'正式{br[0]}原载{hour}时','month_general':f'正式{br[0]}原载{general}将'},
        constraints=constraints,settings_review=dict(state='candidate_not_originally_declared',guiren='原书未明完整贵人法，不强选。',zhouye='占时原载，昼夜取法未明，保留设置候选。',shehai='原书未明涉害设置；不按结局选传序。'),
        notes=['全部按明确题干和残盘关系，不以反馈择设置；原图残损身份保留。','核全部facts实质等价和连续全文后再判完整性；缺实际反馈单独标注，不冒作已验。'])
    p=OUT/f'bifa-reconstruction-request-{n:03}.json'
    if p.exists():
        assert json.loads(p.read_text(encoding='utf-8-sig'))==request, f'{p.name} immutable request conflict'
    else:p.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_requests':[s[0] for s in specs],'engine_executed':False},ensure_ascii=False))
