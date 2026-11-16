"""New immutable input branches with same-event explicit month general."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
for n,year,month,day,hour,jiang,seq,gens,a,b in [
 (40,'甲申','巳','乙未','未','申','酉戌亥',['玄武','太阴','天后'],6041,6057),
 (81,'癸未','寅','己亥','未','亥','未亥卯',['青龙','腾蛇','玄武'],6825,6841),
]:
 c=next(c for c in cases if c['id']==f'BK26-BIFA-{n:03}')
 p='书籍库/现代著作/《壬占汇选》.txt';raw=(ROOT/p).read_bytes();ls=raw.decode('utf-8-sig').splitlines()
 e=dict(path=p,line_start=a,line_end=b,quote='\n'.join(ls[a-1:b]),sha256=hashlib.sha256(raw).hexdigest(),role='原书断语',dependency_type='same_event_parallel_source',same_event=True)
 ev=c['source_refs'][:2]+[e]
 cons=[dict(field='transmission_sequence',expected=seq,evidence_refs=ev,extraction_review_state='source_checked')]
 cons += [dict(field=f'transmissions.{i}.tianjiang',expected=v,evidence_refs=ev,extraction_review_state='source_checked') for i,v in enumerate(gens)]
 req=dict(schema='liuren-book-reconstruction-request-v1',id=f'RC26-BIFA-{n:03}-CROSSSOURCE',case_id=c['id'],input=dict(mode='manual-pillars',pillars=dict(year=year,month_branch=month,day=day,hour_branch=hour),month_general=jiang),input_evidence=ev,
 input_sources={'pillars.year':f'两书同案题头{year}年。','pillars.month_branch':f'原农历月份映射为{month}，不猜公历。','pillars.day':f'两书同案题头{day}日。','pillars.hour_branch':f'两书同案题头{hour}时。','month_general':f'古汇选{a}同案明确{jiang}将；毕法本段未直载，作为跨源补证输入，非毕法逐字原文。'},constraints=cons,settings_mode='enumerate_unverified',max_candidates=8,original_source_condition='毕法残盘保留，月将由已核同事件古汇选补证。',notes=['同案以题、时间、姓名与连续断后述对齐，不从结果选盘。','原书历史后叙、课名分歧及原贵人昼夜法未核独立保留，selected_candidate_id须null。'])
 dest=OUT/f'bifa-reconstruction-request-{n:03}-crosssource.json'
 if dest.exists():assert json.loads(dest.read_text(encoding='utf-8'))==req
 else:dest.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 run=subprocess.run([str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),'tools/liuren_book_reconstruction.mjs','--request',dest.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 print(run.stdout,flush=True);assert run.returncode in {0,2},run.stderr
