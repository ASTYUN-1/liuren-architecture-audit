from pathlib import Path
import hashlib,json,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']=='20261106-tool-continuation-23'
files=['.opencode/liuren-active.json','.opencode/plugins/liuren-adjudication.ts','.opencode/tools/liuren_materials.ts','.opencode/oh-my-opencode-slim.jsonc','opencode.json','AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','tools/liuren-adjudication-files.mjs','tools/liuren-deterministic-io.mjs','tools/liuren-adjudication-contract.mjs','tools/liuren-adjudication-schema.mjs','tools/liuren-flow-control.mjs','tools/liuren-materials.py','tools/tests/liuren-adjudication-plugin.test.mjs','tools/tests/liuren-flow-control.test.mjs','tools/tests/liuren-deterministic.test.mjs','tools/tests/liuren-materials-transport.test.mjs','tools/tests/liuren-wire-schema.test.mjs']
files += [f.relative_to(ROOT).as_posix() for f in (ROOT/'.opencode/skills/liuren').rglob('SKILL.md')]
assert not (OUT/'before').exists()
for rel in files:
 d=OUT/'before'/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,d)
v={'release':p['release'],'runtime':p['runtime'],'live':{r:sha(ROOT/r) for r in files},'runtimeFiles':{f.relative_to(ROOT/p['runtime']).as_posix():sha(f) for f in (ROOT/p['runtime']).rglob('*') if f.is_file()}}
(OUT/'before.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf-8')
print('Baseline files and immutable runtime backed up')
