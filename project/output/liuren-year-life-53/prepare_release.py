"""Create a new local release and byte-preserving rollback before editing."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261112-consistency-52'
assert not (O/'before.json').exists(),'Preparation is one-time only'
files=set(p['workflowImplementation'])|set(load(R/p['runtime']/'loader-contract.json')['sourceHashes'])
files.update(['.opencode/liuren-active.json','README.md','AGENTS.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机六壬直接排盘.md','tools/liuren-direct/chart.mjs','tools/liuren-chart-view.mjs','tools/liuren-bifa-basic.mjs'])
files.update(str(f.relative_to(R)).replace('\\','/') for f in (R/'.opencode/skills/liuren').rglob('*.md'))
files.update(str(f.relative_to(R)).replace('\\','/') for f in (R/'tools/tests').glob('*.test.mjs'))
for f in sorted(files):
 dst=O/'before'/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,dst)
b={'release':p['release'],'runtime':p['runtime'],'files':{f:sha(R/f) for f in sorted(files)},'frozen':{str(f.relative_to(R)).replace('\\','/'):sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}}
(O/'before.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n','utf8')
new='20261112-year-life-53';T=R/'runtime/liuren'/new;shutil.copytree(R/p['runtime'],T)
m=load(T/'manifest.json');m.update(release=new,parentRelease=p['release']);(T/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
p.update(release=new,previousRelease=p['release'],runtime='runtime/liuren/'+new,backup='output/liuren-year-life-53/before')
(R/'.opencode/liuren-active.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf8')
print('Prepared',new,'backups',len(files),'parent files',len(b['frozen']))
