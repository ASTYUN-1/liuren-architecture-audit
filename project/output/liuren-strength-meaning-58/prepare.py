from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261114-class-strength-trial-57'
T=R/'runtime/liuren/20261115-strength-meaning-58'
assert not (O/'before.json').exists() and not T.exists()
c=load(R/p['runtime']/'loader-contract.json')
files=set(p['workflowImplementation'])|set(c['sourceHashes'])
files.update('.opencode/skills/'+f for f in p['files'])
files.update(['.opencode/liuren-active.json','README.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md','tools/tests/liuren-class-selection-trial.test.mjs','tools/tests/liuren-palace-strength.test.mjs'])
for f in files:
 d=O/'before'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,d)
b={'release':p['release'],'files':{f:sha(R/f) for f in sorted(files)},'new_files':['tools/liuren-strength-interpretation.mjs','tools/tests/liuren-strength-interpretation.test.mjs'],'frozen':{f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}}
(O/'before.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),'utf8')
shutil.copytree(R/p['runtime'],T)
print('57 backed up; inactive 58 staging created')
