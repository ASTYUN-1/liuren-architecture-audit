"""Stage the new release without modifying the frozen parent or active pointer."""
from pathlib import Path
import hashlib, json, shutil
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json')
assert p['release']=='20261112-year-life-53'
assert not (O/'before.json').exists(), 'One-time preparation'
files=set(p['workflowImplementation'])|set(load(R/p['runtime']/'loader-contract.json')['sourceHashes'])
files.update(['.opencode/liuren-active.json','README.md','AGENTS.md','目录总索引.md',
 'docs/本机六壬完整研判流程.md','docs/Codex大六壬工作流.md',
 'integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md'])
files.update(str(f.relative_to(R)).replace('\\','/') for folder in ['tools/tests','.opencode/skills/liuren'] for f in (R/folder).rglob('*') if f.is_file())
for f in sorted(files):
 dst=O/'before'/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,dst)
frozen={str(f.relative_to(R)).replace('\\','/'):sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}
installed=Path.home()/'.codex/skills/daliuren-codex'
for rel in ['SKILL.md','references/host.md']:
 dst=O/'installed-skill-before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(installed/rel,dst)
(O/'before.json').write_text(json.dumps({'release':p['release'],'runtime':p['runtime'],
 'files':{f:sha(R/f) for f in sorted(files)},'frozen':frozen},ensure_ascii=False,indent=2)+'\n','utf8')
T=R/'runtime/liuren/20261112-analysis-routing-54'
shutil.copytree(R/p['runtime'],T)
print('Staged',T,'backed up',len(files),'files; active unchanged')
