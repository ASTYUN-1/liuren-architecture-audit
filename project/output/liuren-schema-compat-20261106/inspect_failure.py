from pathlib import Path
import json,sqlite3,re
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
db=Path.home()/'.local/share/opencode/opencode.db';c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
sessions=c.execute('select id from session where directory like ? order by time_updated desc limit 3',('%六壬八字测算%',)).fetchall()
records=[]
for (sid,) in sessions:
 for (raw,) in c.execute("select data from message where session_id=? and json_type(data,'$.error') is not null order by time_created desc limit 3",(sid,)):
  e=json.loads(raw).get('error');serialized=json.dumps(e,ensure_ascii=False)
  # Preserve only the concrete schema message; do not export provider bodies/headers.
  needle="Invalid schema for function"
  match=re.search(r"Invalid schema for function '[^']+': Pointer '[^']+' does not exist(?: \(request_id: [A-Za-z0-9-]+\))?",serialized)
  if match:records.append({'session_id':sid,'error_excerpt':match.group()})
(OUT/'observed-schema-errors.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
