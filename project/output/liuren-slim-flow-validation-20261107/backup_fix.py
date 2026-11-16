from pathlib import Path
import hashlib,json,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
files=['tools/liuren-compute-schema.mjs','tools/liuren-adjudication-files.mjs','.opencode/plugins/liuren-adjudication.ts','tools/tests/liuren-adjudication-plugin.test.mjs','tools/tests/liuren-compute-interface.test.mjs','opencode.json','.opencode/liuren-active.json','AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md']
assert not (OUT/'before-fix-sha256.json').exists()
hashes={}
for rel in files:
 p=ROOT/rel;dest=OUT/'before-fix'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);hashes[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'before-fix-sha256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
