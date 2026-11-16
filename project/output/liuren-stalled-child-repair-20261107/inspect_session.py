"""Read only the reported OpenCode parent/child; never print private reasoning."""
from pathlib import Path
import json,sqlite3
OUT=Path(__file__).resolve().parent
db=Path.home()/'.local/share/opencode/opencode.db'
c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
c.row_factory=sqlite3.Row
for table in ['session','message','part']:
 print(table,[(r['name'],r['type']) for r in c.execute('pragma table_info('+table+')')])
for sid in ['ses_e4b999f8effeAr6j14Vl1trT5o','ses_e4b9625cbffeIf9qaGy6975XwL']:
 session=c.execute('select * from session where id=?',(sid,)).fetchone()
 if session:print('SESSION',{k:session[k] for k in session.keys() if k in ['id','parent_id','directory','title','time_created','time_updated']})
 messages=c.execute('select * from message where session_id=? order by time_created',(sid,)).fetchall()
 summary=[]
 for message in messages:
  data=json.loads(message['data']);parts=[]
  for row in c.execute('select * from part where message_id=? order by time_created',(message['id'],)):
   p=json.loads(row['data']);item={k:p[k] for k in ['type','tool','callID'] if k in p}
   if p.get('type')=='reasoning':item['chars']=len(p.get('text',''))
   elif p.get('type')=='text':item.update(chars=len(p.get('text','')),preview=p.get('text','')[:400])
   elif p.get('type')=='tool':
    state=p.get('state',{});item.update(status=state.get('status'),input=state.get('input'),error=state.get('error'),outputChars=len(str(state.get('output',''))),outputPreview=str(state.get('output',''))[:400])
   elif p.get('type')=='step-finish':item.update(reason=p.get('reason'),tokens=p.get('tokens'))
   parts.append(item)
  summary.append({'message_id':message['id'],'role':data.get('role'),'agent':data.get('agent'),'model':data.get('modelID'),'finish':data.get('finish'),'error':data.get('error'),'tokens':data.get('tokens'),'parts':parts})
 (OUT/(sid+'-summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('MESSAGES',sid,len(summary))
 for item in summary:
  print(json.dumps({**{k:v for k,v in item.items() if k!='parts'},'parts':[{k:v for k,v in p.items() if k not in ['input','outputPreview','preview']} for p in item['parts']]},ensure_ascii=False))
