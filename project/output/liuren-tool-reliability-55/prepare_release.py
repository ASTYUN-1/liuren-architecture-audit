"""Preserve the active release and implementation before local interface repairs."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((R/'.opencode/liuren-active.json').read_text('utf-8-sig'))
assert p['release']=='20261112-analysis-routing-54'
assert not (O/'before.json').exists()
files=set(p['workflowImplementation'])|set(json.loads((R/p['runtime']/'loader-contract.json').read_text('utf8'))['sourceHashes'])
files.update(['.opencode/liuren-active.json','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬稳定运行指南.md'])
for f in sorted(files):
 d=O/'before'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,d)
frozen={str(f.relative_to(R)).replace('\\','/'):sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}
(O/'before.json').write_text(json.dumps({'release':p['release'],'runtime':p['runtime'],'files':{f:sha(R/f) for f in sorted(files)},'frozen':frozen},ensure_ascii=False,indent=2)+'\n','utf8')
shutil.copytree(R/p['runtime'],R/'runtime/liuren/20261114-tool-reliability-55')
print('Prepared 55; active pointer unchanged; frozen 54 preserved')
