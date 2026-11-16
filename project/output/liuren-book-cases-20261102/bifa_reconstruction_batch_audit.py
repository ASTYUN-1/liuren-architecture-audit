"""Run BIFA's source-bound reconstructions through the shared real engine."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/liuren-book-cases-20261102'
cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
specs=[
 (38,'庚辰','辰','壬辰','亥','戌','戌酉申',['白虎','天空','青龙']),
 (39,'戊申','寅','丙戌','未','子','申卯午',['六合',None,'青龙']),
 (48,'己酉','戌','癸亥','辰','卯','戌酉申',['白虎','太常','玄武']),
 (51,'戊申','丑','庚辰','子','子','申寅巳',['天后','青龙','朱雀']),
 (52,'丙戌','巳','甲辰','戌','酉','子亥戌',['白虎','太常','玄武']),
 (54,'丙戌','未','庚子','戌','未','午卯子',['腾蛇','勾陈','白虎']),
 (56,'戊申','未','戊辰','酉','未','丑亥酉',['天空','太常','太阴']),
 (103,'己酉','寅','辛巳','酉','子','申亥寅',['天空','玄武','贵人']),
 (107,'丙戌','未','己酉','巳','未','丑卯巳',['天后','玄武','白虎']),
 (110,'壬午','子','己未','巳','寅','亥辰辰',[]),
 (112,'乙酉','子','戊辰','申','寅','巳亥巳',['太常','朱雀','太常']),
 (117,'乙酉','午','丙寅','申','申','巳申寅',['勾陈','腾蛇','白虎']),
 (119,'戊申','未','丁巳','酉','未','亥酉丑',[]),
 (120,'乙酉','丑','丁亥','酉','亥','酉亥丑',['贵人','太阴','太常']),
 (121,'癸未','辰','戊午','辰','戌','午子午',['白虎','腾蛇','白虎']),
 (125,'甲申','酉','癸卯','午','巳','丑子亥',['勾陈','青龙','天空']),
 (126,'甲子','卯','甲子','辰','子','戌午寅',['六合','白虎','天后']),
 (129,'乙酉','巳','戊午','卯','申','辰酉寅',['玄武','勾陈','天后']),
 (130,'庚辰','亥','丙子','申','卯','子未寅',['腾蛇','太常','六合']),
 (21,'丙戌','辰','戊子','申','酉','戌酉申',['玄武','太常','白虎']),
 (26,'丙戌','未','乙卯','亥','午','午丑申',['太阴','青龙','贵人']),
 (29,'丙戌','未','癸丑','戌','午','巳丑酉',['太阴','朱雀','天空']),
 (31,'丙戌','午','庚辰','戌','申','午辰寅',['腾蛇','六合','青龙']),
 (32,'己酉','未','甲寅','午','未','辰巳午',[]),
 (37,'丁丑','巳','甲子','巳','申','申亥寅',['青龙','朱雀','天后']),
 (57,'乙酉','寅','丁亥','未','亥','未卯亥',[]),
 (61,'丙戌','未','戊申','未','未','巳申寅',['勾陈','白虎','腾蛇']),
 (62,'庚辰','寅','辛巳','子','子','巳申寅',['六合','天空','贵人']),
 (69,'戊申','巳','甲申','丑','申','戌子寅',['六合','太阴','青龙']),
 (70,'甲申','寅','己亥','午','亥','巳戌卯',['白虎','朱雀','玄武']),
 (77,'戊申','亥','壬子','卯','卯','亥子卯',['天空','青龙','朱雀']),
 (85,'戊申','戌','壬寅','酉','辰','午丑申',['玄武','朱雀','白虎']),
 (91,'丙戌','未','甲寅','申','午','戌申午',['玄武','白虎','青龙']),
 (95,'丙戌','寅','戊辰','酉','子','亥寅巳',['勾陈','白虎','太阴']),
 (96,'乙酉','戌','戊寅','辰','辰','巳申寅',['勾陈','白虎','腾蛇']),
 (97,'己酉','亥','己亥','酉','寅','巳戌卯',['玄武','朱雀','白虎']),
 (100,'癸未','巳','癸未','午','酉','辰未戌',['天后','朱雀','青龙']),
 (102,'甲申','戌','辛巳','卯','未','午寅戌',['贵人','勾陈','太常']),
 (131,'庚午','子','己丑','未','寅','卯申巳',[]),
 (114,'癸酉','申','辛卯','寅','午','未卯亥',[]),
 (74,'丙戌','卯','甲寅','午','戌','申午午',['青龙','白虎','白虎']),
 (93,'戊午','酉','庚戌','子','辰','辰申子',[None,None,'青龙']),
]
for n,y,m,d,h,g,seq,gens in specs:
 c=next(c for c in cases if c['id']==f'BK26-BIFA-{n:03}')
 evidence=c['source_refs'][:2]
 constraints=[dict(field='transmission_sequence',expected=seq,evidence_refs=evidence,extraction_review_state='source_checked')]
 constraints += [dict(field=f'transmissions.{i}.tianjiang',expected=v,evidence_refs=evidence,extraction_review_state='source_checked') for i,v in enumerate(gens) if v]
 req=dict(schema='liuren-book-reconstruction-request-v1',id=f'RC26-BIFA-{n:03}-AUDIT',case_id=c['id'],
  input=dict(mode='manual-pillars',pillars=dict(year=y,month_branch=m,day=d,hour_branch=h),month_general=g),
  input_evidence=evidence,
  input_sources={'pillars.year':f'主源题干明载{y}年。','pillars.month_branch':f'原载月序或月支映射为{m}；正月寅、六月未、九月戌、十二月丑，不转古公历日。',
  'pillars.day':f'题干或同案正文明确{d}日；056正文戊辰干支，未由结果猜日。','pillars.hour_branch':f'原载{h}时。','month_general':f'原载{g}将。'},
  constraints=constraints,settings_mode='enumerate_unverified',max_candidates=8,
  original_source_condition='原转录残损身份不变；冲突列只核其所列，不据反馈改源或选设置。',
  notes=['B3执行真实引擎；原始题干、残盘与后注分层，selected保持null。','039/119有主传与六亲序冲突，本请求保留主列，不删除反例。','缺失原始设置和年命不补；完整性待全facts与语义审查。'])
 p=OUT/f'bifa-reconstruction-request-{n:03}-audit.json'
 if p.exists():assert json.loads(p.read_text(encoding='utf-8'))==req
 else:p.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result=subprocess.run([str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),'tools/liuren_book_reconstruction.mjs','--request',p.relative_to(ROOT).as_posix()],cwd=ROOT,text=True,encoding='utf-8',capture_output=True)
 print(result.stdout.strip(),flush=True)
 if result.stderr:print(result.stderr,flush=True)
 assert result.returncode in {0,2}
