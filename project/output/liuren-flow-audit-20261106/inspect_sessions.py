from pathlib import Path
import sqlite3,json,datetime
OUT=Path(__file__).resolve().parent
db=Path.home()/'.local/share/opencode/opencode.db'
c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
sessions=c.execute('select id,parent_id,title,time_created,time_updated from session where directory like ? order by time_updated desc limit 12',('%六壬八字测算%',)).fetchall()
def stamp(v):return datetime.datetime.fromtimestamp(v/1000,datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
print('SESSIONS')
for sid,parent,title,start,end in sessions:print(json.dumps({'id':sid,'parent':parent,'title':title,'start':stamp(start),'updated':stamp(end)},ensure_ascii=False))
latest=next(s for s in sessions if not s[1]);root=latest[0]
related=c.execute('select id,parent_id,title,time_created,time_updated from session where id=? or parent_id=? order by time_created',(root,root)).fetchall()
events=[]
for sid,parent,title,start,end in related:
 for pid,mid,created,updated,raw in c.execute('select id,message_id,time_created,time_updated,data from part where session_id=? order by time_created',(sid,)):
  p=json.loads(raw)
  if p.get('type')=='tool':
   st=p.get('state',{});tool=p.get('tool');request=st.get('input',{})
   # Keep only routing/validation arguments, not raw chart, question, or book text.
   inp=request if tool in ['task','task_result'] else {k:request[k] for k in ['action','module','page','file_path','sha256','batch'] if k in request}
   if tool=='liuren_adjudication_packet':
    packet=request.get('packet',{});inp={'request_id':packet.get('request_id'),'questions':[{k:q.get(k) for k in ['id','tasks']} for q in packet.get('questions',[])],'entities':len(packet.get('entities',[])),'method_materials':len(packet.get('method_materials',[]))}
   output=st.get('output','');error=st.get('error')
   events.append({'session':sid,'parent':parent,'part_id':pid,'message_id':mid,'time':stamp(created),'updated':stamp(updated),'tool':tool,'status':st.get('status'),'input':inp,'output_length':len(output),'output_excerpt':output[:1800] if tool in ['task','task_result','liuren_adjudication_packet'] else output[:180] if error else '', 'error':error,'metadata':st.get('metadata')})
events.sort(key=lambda e:e['time'])
(OUT/'tool-timeline.json').write_text(json.dumps({'root':root,'sessions':[{'id':s[0],'parent':s[1],'title':s[2]} for s in related],'events':events},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('TIMELINE',root,len(events))
for event in events:print(json.dumps(event,ensure_ascii=False))
