from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261115-strength-meaning-58'
T=R/'runtime/liuren/20261115-trial-decision-59'
assert not T.exists() and not (O/'before.json').exists()
files=set(p['workflowImplementation'])|set(load(R/p['runtime']/'loader-contract.json')['sourceHashes'])
files.update('.opencode/skills/'+f for f in p['files'])
files.update(['.opencode/liuren-active.json','README.md','目录总索引.md','tools/tests/liuren-class-selection-trial.test.mjs'])
for f in files:
 d=O/'before'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,d)
save={'release':p['release'],'files':{f:sha(R/f) for f in sorted(files)},'new_files':['tools/liuren-trial-decision.mjs','tools/tests/liuren-trial-decision.test.mjs'],'frozen':{f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}}
(O/'before.json').write_text(json.dumps(save,ensure_ascii=False,indent=2),'utf8')
shutil.copytree(R/p['runtime'],T)
print('Backed up 58; staged new 59')
