"""One minimal real-model tool call in a separately named diagnostic session."""
from pathlib import Path
import json,time,urllib.request,urllib.parse
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
host=json.loads((OUT/'live-server.json').read_text('utf-8'));url='http://127.0.0.1:'+str(host['port']);query='?directory='+urllib.parse.quote(str(ROOT))
def request(path,body=None):
 req=urllib.request.Request(url+path+query,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=15) as response:
  raw=response.read();return json.loads(raw) if raw else None
session=request('/session',{'title':'本机六壬工具诊断-20261107-独立测试'});sid=session['id']
request('/session/'+sid+'/prompt_async',{'agent':'liuren','model':{'providerID':'deepseek','modelID':'deepseek-flash'},'variant':'low','parts':[{'type':'text','text':'本条是本机开发工具冒烟测试，不是占断。只调用一次liuren_tool_help(topic="workflow",domains=["travel"])，然后只回复该工具返回的release与features。不要加载skill，不排盘，不派发task，不调用其他工具。'}]})
report={'sessionID':sid,'externalModelCalls':1,'model':'deepseek/deepseek-flash','scope':'minimal live model routing and native tool call; no professional judgment','finished':False,'toolCalls':[]}
started=time.monotonic()
while time.monotonic()-started<150:
 messages=request('/session/'+sid+'/message');assistants=[m for m in messages if m['info']['role']=='assistant']
 report['toolCalls']=[]
 for m in assistants:
  for p in m['parts']:
   if p['type']=='tool':
    state=p.get('state',{});item={'tool':p['tool'],'status':state.get('status')}
    if p['tool']=='liuren_tool_help' and state.get('status')=='completed':
     try:v=json.loads(state['output']);item.update(release=v.get('release'),features=v.get('features'))
     except ValueError:pass
    report['toolCalls'].append(item)
 if assistants:
  last=assistants[-1]['info'];report['finish']=last.get('finish');report['errorType']=last.get('error',{}).get('name') if last.get('error') else None
  if last.get('finish') not in [None,'tool-calls','unknown'] or last.get('error'):
   report['finished']=True;break
 (OUT/'live-model-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');time.sleep(1)
report['seconds']=round(time.monotonic()-started,2);report['passed']=report['finished'] and not report.get('errorType') and any(c['tool']=='liuren_tool_help' and c['status']=='completed' for c in report['toolCalls'])
if not report['finished']:request('/session/'+sid+'/abort',{})
(OUT/'live-model-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False));raise SystemExit(0 if report['passed'] else 1)
