from pathlib import Path
import json, hashlib, shutil
R=Path.cwd();O=R/'output/liuren-class-selection-trial-56'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((R/'.opencode/liuren-active.json').read_text('utf-8-sig'))
assert p['release']=='20261114-tool-reliability-55'
files=set(p['workflowImplementation'])|set(json.loads((R/p['runtime']/'loader-contract.json').read_text('utf8'))['sourceHashes'])
files.update(['.opencode/liuren-active.json','README.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md'])
assert not (O/'before.json').exists()
for f in files:
 d=O/'before'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,d)
(O/'before.json').write_text(json.dumps({'release':p['release'],'files':{f:sha(R/f) for f in sorted(files)},'frozen':{str(f.relative_to(R)).replace('\\','/'):sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}},ensure_ascii=False,indent=2),'utf8')
shutil.copytree(R/p['runtime'],R/'runtime/liuren/20261114-class-selection-trial-56')
print('55 preserved; created inactive 56 staging runtime')
