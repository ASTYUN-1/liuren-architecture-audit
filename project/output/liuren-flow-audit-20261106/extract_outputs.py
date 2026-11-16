from pathlib import Path
import sqlite3,json
out=Path(__file__).resolve().parent
c=sqlite3.connect((Path.home()/'.local/share/opencode/opencode.db').as_uri()+'?mode=ro',uri=True)
ids=['ses_e510981deffeBOAFqV8J25sc3z','ses_e50fb41fdffeclcwHDP3odS2Lc']
for n,sid in enumerate(ids,1):
 texts=[]
 for raw, in c.execute('select data from part where session_id=? order by time_created',(sid,)):
  p=json.loads(raw)
  if p.get('type')=='text':texts.append(p.get('text',''))
 (out/f'child-{n}-text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf8')
 for t in texts:
  start=t.find('{');end=t.rfind('}')
  try:r=json.loads(t[start:end+1])
  except Exception:continue
  if not isinstance(r,dict) or 'entity_checks' not in r:continue
  (out/f'child-{n}-output.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
  print('CHILD',n,'schema',r.get('schema'),'status',r.get('status'),'entities',json.dumps([{k:e.get(k) for k in ['id','branch']} for e in r['entity_checks']],ensure_ascii=False))
  print('FIELDS',list(r))
for raw, in c.execute('select data from part where session_id=? order by time_created',('ses_e5116f918ffehcZhxjou41x913',)):
 p=json.loads(raw)
 if p.get('type')=='tool' and p.get('tool')=='read':
  st=p.get('state',{});print('READ',json.dumps(st.get('input'),ensure_ascii=False),'ERROR',str(st.get('error'))[:240])
for f in sorted((out.parent/'liuren-adjudication-requests').glob('LR-20261106-113121-transfer-school-*.json')):
 r=json.loads(f.read_text(encoding='utf8'));print('PACKET',f.name,'keys',list(r))
