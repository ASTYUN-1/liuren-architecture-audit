"""Replace obsolete wording/path assumptions with exact content/provenance checks."""
from pathlib import Path
import hashlib
import json
import shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text('utf-8'))
activation=load(OUT/'activation.json')
updates={}
rel='tools/tests/liuren-materials-transport.test.mjs'
text=(ROOT/rel).read_text('utf-8')
text=text.replace("  assert.ok(text.includes('有路扫描'));","  const root=path.resolve(import.meta.dirname,'../..');\n  const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));\n  const manifest=JSON.parse(await fs.readFile(path.join(root,pointer.runtime,'manifest.json'),'utf8'));\n  const relative=manifest.modules.movement.file;\n  const expected=(await fs.readFile(path.join(root,pointer.runtime,relative),'utf8')).replaceAll('\\r\\n','\\n');\n  assert.equal(meta.fileSha256,manifest.files[relative]);\n  assert.ok(text.includes('\\n'+expected+'\\nLIUREN_METHOD_END '));")
updates[rel]=text
rel='tools/tests/liuren-wire-schema.test.mjs'
text=(ROOT/rel).read_text('utf-8').replace("const current=pointer.toolUsage?JSON.parse(await readFile(path.join(ROOT,pointer.authoringSource,'current-wire.json'),'utf8')):fixed;","// A method release can retain an unchanged tool implementation and its original capture.\n const evidence=pointer.computeInterface?.transportEvidence;\n const current=evidence?JSON.parse(await readFile(path.join(ROOT,evidence),'utf8')):fixed;")
updates[rel]=text
for rel,text in updates.items():
    assert rel not in activation['before'],'Already amended.'
    activation['before'][rel]=sha(ROOT/rel)
    p=OUT/'before'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
    (ROOT/rel).write_text(text,encoding='utf-8',newline='')
    activation['after'][rel]=sha(ROOT/rel)
(OUT/'activation.json').write_text(json.dumps(activation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'before-sha256.json').write_text(json.dumps(activation['before'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
