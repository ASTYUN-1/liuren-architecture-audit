"""Explicit relation-bound input candidates; no date or feedback inference."""
import json,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
p='书籍库/北海闲人/毕法赋全解-正式整理本.md';raw=(ROOT/p).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
definition=dict(path=p,line_start=4416,line_end=4416,quote=ls[4415],sha256=hashlib.sha256(raw).hexdigest(),role='原书断语',dependency_type='borrowed_context',same_event=False)
for n,y,m,d,h,seq,gens in [(4,'癸酉','未','戊寅','未','巳申寅',['勾陈','白虎','腾蛇']),(12,'丁丑','巳','乙酉','酉','辰酉卯',['勾陈','天后','青龙']),(17,'庚辰','辰','辛卯','戌','卯卯卯',['腾蛇','腾蛇','腾蛇'])]:
 c=next(c for c in cases if c['id']==f'BK26-BIFA-{n:03}');ev=c['source_refs'][:2]+[definition]
 constraints=[dict(field='transmission_sequence',expected=seq,evidence_refs=ev[:2],extraction_review_state='source_checked')]
 constraints += [dict(field=f'transmissions.{i}.tianjiang',expected=v,evidence_refs=ev[:2],extraction_review_state='source_checked') for i,v in enumerate(gens)]
 constraints += [dict(field=f'heaven_earth.{i}.tian',expected=v,evidence_refs=ev,extraction_review_state='source_checked') for i,v in enumerate('子丑寅卯辰巳午未申酉戌亥')]
 req=dict(schema='liuren-book-reconstruction-request-v1',id=f'RC26-BIFA-{n:03}-RELATION',case_id=c['id'],input=dict(mode='manual-pillars',pillars=dict(year=y,month_branch=m,day=d,hour_branch=h),month_general=h),input_evidence=ev,
 input_sources={'pillars.year':f'本案题干明载{y}。','pillars.month_branch':f'本案农历月序映射为{m}，不换古公历。','pillars.day':f'本案明载{d}日。','pillars.hour_branch':f'本案明载{h}时。','month_general':f'本案明载伏吟而未直载月将；4416定义十二支各加本位。以将={h}为关系约束的可验证候选，非原载逐字将值。真实引擎另核全12宫相重及残传，不据反馈猜将。'},constraints=constraints,
 settings_mode='enumerate_unverified',max_candidates=8,original_source_condition='原月将未直载；这是关系约束候选而非恢复原图。',notes=['伏吟关系固定将时相同，唯一关系候选仍须真实引擎核全部12宫及残盘；不据病死/双胎后果筛。','定义引文为borrowed_context、same_event=false，不把通用定义并成同一事件。'])
 p=OUT/f'bifa-reconstruction-request-{n:03}-relation.json'
 if p.exists():assert json.loads(p.read_text(encoding='utf-8'))==req
 else:p.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 a=subprocess.run([str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),'tools/liuren_book_reconstruction.mjs','--request',p.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 print(a.stdout,flush=True);assert a.returncode in {0,2}
