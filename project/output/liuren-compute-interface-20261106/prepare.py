from pathlib import Path
import hashlib,json,shutil,sqlite3
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if (OUT/'before-manifest.json').exists():raise SystemExit('Backup exists; do not overwrite')
pointer=json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8'))
assert pointer['release']=='20261106-deterministic-foundation-09'
previous=json.loads((ROOT/'output/liuren-deterministic-foundation-20261106/before-manifest.json').read_text('utf-8'))
paths=[*previous['live'],'tools/liuren-deterministic-calendar.mjs']
for rel in paths:
 dst=OUT/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
runtime=ROOT/pointer['runtime']
dump(OUT/'before-manifest.json',{'parentRelease':pointer['release'],'newRelease':'20261106-compute-interface-10','parentRuntime':pointer['runtime'],
 'live':{r:sha(ROOT/r) for r in paths},'runtime':{p.relative_to(runtime).as_posix():sha(p) for p in runtime.rglob('*') if p.is_file()},
 'newFiles':['tools/liuren-compute-schema.mjs','tools/tests/liuren-compute-interface.test.mjs']})
# Export only tool calls relevant to this failure; no question text, chart, or reasoning.
db=Path.home()/'.local/share/opencode/opencode.db';conn=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
sid=conn.execute('select id from session where directory like ? order by time_updated desc limit 1',('%六壬八字测算%',)).fetchone()[0]
records=[]
for pid,created,raw in conn.execute("select id,time_created,data from part where session_id=? and json_extract(data,'$.tool')='liuren_compute' order by time_created",(sid,)):
 state=json.loads(raw).get('state',{});request=state.get('input',{})
 if request.get('action')=='calendar':records.append({'part_id':pid,'time_created':created,'status':state.get('status'),'input':request,'error':state.get('error')})
dump(OUT/'observed-calendar-failures.json',{'session_id':sid,'calls':records,'scope':'calendar tool arguments and errors only'})
print(json.dumps({'backedUpFiles':len(paths),'frozenRuntimeFiles':len(json.loads((OUT/'before-manifest.json').read_text('utf-8'))['runtime']),'recordedCalendarFailures':len(records)}))
