from pathlib import Path
import hashlib,json,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rels=['.opencode/liuren-active.json','.opencode/plugins/liuren-adjudication.ts','.opencode/oh-my-opencode-slim.jsonc','.opencode/skills/liuren/daliuren/SKILL.md','opencode.json','tools/liuren-adjudication-files.mjs','tools/liuren-adjudication-output.mjs','tools/liuren-preflight.py','tools/tests/liuren-flow-control.test.mjs','README.md','目录总索引.md','AGENTS.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机六壬稳定运行指南.md']
backup=OUT/'before';assert not backup.exists()
for rel in rels:
 target=backup/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
old=ROOT/'runtime/liuren/20261107-slim-30';new=ROOT/'runtime/liuren/20261107-slim-31';assert not new.exists();shutil.copytree(old,new)
(OUT/'before.json').write_text(json.dumps({'files':{r:sha(ROOT/r) for r in rels},'frozen30':{f.relative_to(old).as_posix():sha(f) for f in old.rglob('*') if f.is_file()}},ensure_ascii=False,indent=2)+'\n','utf-8')
print('Backed up local sources; staged runtime31; active pointer unchanged')
