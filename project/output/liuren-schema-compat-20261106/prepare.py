from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if (OUT/'before-manifest.json').exists():raise SystemExit('Backup exists; do not overwrite')
pointer=json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8'));assert pointer['release']=='20261106-compute-interface-10'
prev=json.loads((ROOT/'output/liuren-compute-interface-20261106/before-manifest.json').read_text('utf-8'))
paths=[*prev['live'],*prev['newFiles']]
for r in paths:
 dst=OUT/'before'/r;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r,dst)
runtime=ROOT/pointer['runtime']
before={'parentRelease':pointer['release'],'newRelease':'20261106-schema-compat-11','parentRuntime':pointer['runtime'],
 'live':{r:sha(ROOT/r) for r in paths},'runtime':{p.relative_to(runtime).as_posix():sha(p) for p in runtime.rglob('*') if p.is_file()},'newFiles':['tools/tests/liuren-wire-schema.test.mjs']}
(OUT/'before-manifest.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'backupFiles':len(paths),'frozenFiles':len(before['runtime'])}))
