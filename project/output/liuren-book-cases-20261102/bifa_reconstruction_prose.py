"""Additional immutable branches using explicit prose / legible six-kin rows."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/liuren-book-cases-20261102'
cases=json.loads((ROOT/'knowledge/liuren-research/20261102/book-cases/bifa.json').read_text(encoding='utf-8'))
for n,old,suffix,conditions,note in [
 (6,'reconstruction-request-bifa-006-main.json','AUDIT',[(f'transmissions.{i}.tianjiang',v) for i,v in enumerate(['六合','太常','腾蛇'])],'正式1054明确戌巳子；转录1237六亲行父戌合、鬼巳常、孙子蛇可读。保留主残子巳戌，不覆盖MAIN。'),
 (110,'bifa-reconstruction-request-110-audit.json','PROSE',[('lessons.0.tianpan','辰'),('lessons.0.tianjiang','勾陈'),('lessons.2.tianpan','辰'),('lessons.2.tianjiang','勾陈')],'正式491明确天罡加干支又乘勾陈；原AUDIT仅三传、尚有全结构不等价候选，新增明文约束不按当选反馈取设置。'),
 (32,'bifa-reconstruction-request-032-audit.json','PROSE',[(f'transmissions.{i}.tianjiang',v) for i,v in enumerate(['六合','勾陈','青龙'])],'转录2859明载财辰六、子巳勾、子午龙；正文2861又明载辰加卯六合、巳加辰勾陈，不按宅败后果挑盘。'),
 (131,'bifa-reconstruction-request-131-audit.json','FORMAL',[('transmission_sequence','卯戌巳')]+[(f'transmissions.{i}.tianjiang',v) for i,v in enumerate(['玄武','朱雀','白虎'])],'正式1068/1074明确卯玄、中戌印朱、末巳生气虎；此分支保存正文观察，AUDIT原残卯申巳/卯六继续保留。'),
]:
 req=json.loads((OUT/old).read_text(encoding='utf-8'));c=next(c for c in cases if c['id']==f'BK26-BIFA-{n:03}')
 req['id']=f'RC26-BIFA-{n:03}-{suffix}'
 evidence=c['source_refs'][:2]
 req['input_evidence']=evidence
 if suffix=='FORMAL':req['constraints']=[]
 req['constraints'] += [dict(field=f,expected=v,evidence_refs=evidence,extraction_review_state='source_checked') for f,v in conditions]
 req['notes'] += [note]
 p=OUT/f'bifa-reconstruction-request-{n:03}-{suffix.lower()}.json'
 if p.exists():assert json.loads(p.read_text(encoding='utf-8'))==req
 else:p.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 a=subprocess.run([str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),'tools/liuren_book_reconstruction.mjs','--request',p.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 print(a.stdout,flush=True);assert a.returncode in {0,2}
