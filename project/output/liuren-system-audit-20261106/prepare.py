from pathlib import Path
import json, hashlib, shutil
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'before-manifest.json').exists()
p = json.loads((ROOT/'.opencode/liuren-active.json').read_text(encoding='utf-8-sig'))
files = []
for rel in ['tools', '.opencode/plugins', '.opencode/tools', '.opencode/skills/liuren']:
    files += [f for f in (ROOT/rel).rglob('*') if f.is_file() and '__pycache__' not in f.parts and 'node_modules' not in f.parts]
files += [ROOT/f for f in ['opencode.json','.opencode/liuren-active.json','.opencode/oh-my-opencode-slim.jsonc','AGENTS.md']]
files += list((ROOT/'docs').glob('本机*.md'))
live = {}
for f in sorted(set(files)):
    rel=f.relative_to(ROOT).as_posix(); dest=OUT/'before'/rel
    dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,dest); live[rel]=sha(f)
runtime={f.relative_to(ROOT/p['runtime']).as_posix():sha(f) for f in (ROOT/p['runtime']).rglob('*') if f.is_file()}
shutil.copytree(ROOT/p['runtime'],OUT/'candidate-runtime')
(OUT/'before-manifest.json').write_text(json.dumps({'parentRelease':p['release'],'parentRuntime':p['runtime'],'newRelease':'20261106-system-audit-18','live':live,'runtime':runtime},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'backedUp':len(live),'frozenRuntimeFiles':len(runtime)}))
