from pathlib import Path
import hashlib, json, shutil
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json'); assert p['release']=='20261115-trial-decision-60'
assert not (O/'before.json').exists()
c=load(R/p['runtime']/'loader-contract.json')
files=set(p['workflowImplementation'])|set(c['sourceHashes'])|{'.opencode/liuren-active.json','opencode.json','README.md','目录总索引.md','tools/tests/liuren-class-selection-trial.test.mjs','tools/tests/liuren-trial-decision.test.mjs'}
files.update('.opencode/skills/'+f for f in p['files'])
for f in files:
 dst=O/'before'/f; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(R/f,dst)
new=['tools/tests/liuren-trial-month-initial.test.mjs']
b={'release':p['release'],'files':{f:sha(R/f) for f in sorted(files)},'new_files':new,'frozen':{f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}}
(O/'before.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n','utf8')
shutil.copytree(R/p['runtime'],R/'runtime/liuren/20261115-trial-decision-61')
print('Saved 60 baseline; created separate 61 staging directory')
