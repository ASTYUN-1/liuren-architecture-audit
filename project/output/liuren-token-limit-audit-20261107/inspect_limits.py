"""Read limit-related source and message metadata; never read reasoning text."""
from pathlib import Path
import json,re,sqlite3,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
package=Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim'
print('SLIM_VERSION',json.loads((package/'package.json').read_text('utf-8'))['version'])
terms=['maxOutputTokens','max_tokens','maxTokens','max_completion_tokens','max_output_tokens','tokenBudget','token_budget','OUTPUT_TOKEN_MAX','chat.params','promptAsync','session.prompt','MAX_OUTPUT','maxSteps']
matches=[]
for file in (package/'dist').rglob('*.js'):
 s=file.read_text('utf-8')
 for term in terms:
  found=list(re.finditer(re.escape(term),s))
  if found:print('TERM',file.relative_to(package).as_posix(),term,len(found))
  for match in found[:8]:
   value={'file':str(file),'line':s.count('\n',0,match.start())+1,'term':term,'context':s[max(0,match.start()-180):match.end()+320]};matches.append(value);print(json.dumps(value,ensure_ascii=False))
(OUT/'slim-limit-source.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2)+'\n','utf-8')
db=Path.home()/'.local/share/opencode/opencode.db';c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
sessions=c.execute('select id,parent_id,title,time_created,time_updated from session where directory=? and parent_id is not null order by time_updated desc limit 12',(str(ROOT),)).fetchall()
result=[]
for row in sessions:
 session=dict(row);messages=[]
 for m in c.execute('select id,data,time_created from message where session_id=? order by time_created',(row['id'],)):
  d=json.loads(m['data'])
  if d.get('role')!='assistant':continue
  parts={r['type']:r['n'] for r in c.execute("select json_extract(data,'$.type') as type,count(*) as n from part where message_id=? group by type",(m['id'],))}
  public_chars=c.execute("select coalesce(sum(length(json_extract(data,'$.text'))),0) from part where message_id=? and json_extract(data,'$.type')='text'",(m['id'],)).fetchone()[0]
  tools=[dict(r) for r in c.execute("select json_extract(data,'$.tool') as name,json_extract(data,'$.state.status') as status from part where message_id=? and json_extract(data,'$.type')='tool'",(m['id'],))]
  messages.append({'id':m['id'],'finish':d.get('finish'),'modelID':d.get('modelID'),'providerID':d.get('providerID'),'tokens':d.get('tokens'),'errorName':d.get('error',{}).get('name') if d.get('error') else None,'partTypes':parts,'publicTextChars':public_chars,'tools':tools})
 session['messages']=messages;result.append(session)
 print('SESSION',json.dumps(session,ensure_ascii=False))
(OUT/'recent-child-metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
