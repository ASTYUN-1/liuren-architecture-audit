from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
OLD='20261106-workflow-boundaries-08'
NEW='20261106-deterministic-foundation-09'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
paths=['tools/liuren-adjudication-contract.mjs','tools/liuren-adjudication-files.mjs',
 '.opencode/plugins/liuren-adjudication.ts','.opencode/oh-my-opencode-slim.jsonc',
 'opencode.json','.opencode/liuren-active.json','README.md','AGENTS.md','目录总索引.md',
 'docs/本机六壬完整研判流程.md','docs/本机六壬高效执行.md','docs/本机OpenCode完整输出规则.md',
 'docs/本机六壬资料检索范围.md',
 *['.opencode/skills/liuren/'+n+'/SKILL.md' for n in ['daliuren','liuren-cases','liuren-extract']]]
if (OUT/'before-manifest.json').exists(): raise SystemExit('Backup already exists; do not overwrite')
p=json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8-sig'))
assert p['release']==OLD
for rel in paths:
 dst=OUT/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
source=ROOT/p['runtime'];dest=OUT/'candidate-runtime'
shutil.copytree(source,dest)
before={'parentRelease':OLD,'newRelease':NEW,'parentRuntime':p['runtime'],
 'live':{r:sha(ROOT/r) for r in paths},
 'runtime':{r.relative_to(source).as_posix():sha(r) for r in source.rglob('*') if r.is_file()},
 'newFiles':['tools/liuren-deterministic.mjs','tools/liuren-deterministic-io.mjs','tools/liuren-deterministic-calendar.mjs']}
(OUT/'before-manifest.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Backed up',len(paths),'live files and retained',len(before['runtime']),'runtime files')
