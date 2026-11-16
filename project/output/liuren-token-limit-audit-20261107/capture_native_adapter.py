"""Capture safe request fields using installed adapter and local synthetic API only."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,os,socket,subprocess,threading,time,urllib.request,urllib.parse
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];captured=[]
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  p=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  captured.append({k:p[k] for k in ['model','max_tokens','max_completion_tokens','max_output_tokens','reasoning_effort','thinking','stream'] if k in p})
  chunk={'id':'local-adapter-probe','object':'chat.completion.chunk','created':1,'model':'deepseek-flash','choices':[{'index':0,'delta':{'role':'assistant','content':'LOCAL_SYNTHETIC_OK'},'finish_reason':None}]}
  end={**chunk,'choices':[{'index':0,'delta':{},'finish_reason':'stop'}],'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}}
  raw=('data: '+json.dumps(chunk)+'\n\ndata: '+json.dumps(end)+'\n\ndata: [DONE]\n\n').encode()
  self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
relay=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=relay.serve_forever,daemon=True).start()
override={'snapshot':False,'provider':{'deepseek':{'options':{'baseURL':f'http://127.0.0.1:{relay.server_port}/v1','apiKey':'[REDACTED_CREDENTIAL]'}}},'mcp':{k:{'enabled':False} for k in ['memory','sequential-thinking','chrome-devtools','context7','filesystem','scrapling','windows-mcp','aoci','gh_grep']}}
env=os.environ.copy();env.update(ELECTRON_RUN_AS_NODE='1',OPENCODE_DISABLE_AUTOUPDATE='true',OPENCODE_DISABLE_MODELS_FETCH='true',OPENCODE_DISABLE_LSP_DOWNLOAD='true',OPENCODE_CONFIG_CONTENT=json.dumps(override))
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close();base=f'http://127.0.0.1:{port}';q='?directory='+urllib.parse.quote(str(ROOT))
def api(path,body=None):
 req=urllib.request.Request(base+path+q,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=45) as r:raw=r.read();return json.loads(raw) if raw else None
log=(OUT/'adapter-probe.log').open('w',encoding='utf-8');server=None;result={'externalModelCalls':0,'configFilesChanged':False}
try:
 server=subprocess.Popen([str(Path.home()/'AppData/Local/Programs/@opencode-aidesktop/OpenCode.exe'),str(ROOT/'output/liuren-stalled-child-repair-20261107/desktop-server.mjs'),str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 for _ in range(100):
  try:urllib.request.urlopen(base+'/global/health',timeout=.4).close();break
  except Exception:time.sleep(.15)
 providers=api('/config/providers');provider=next(p for p in providers['providers'] if p['id']=='deepseek');model=provider['models']['deepseek-flash']
 result['modelMetadata']={k:model.get(k) for k in ['id','api','limit','variants']};result['providerNpm']=provider.get('npm')
 cfg=api('/config');result['configuredNpm']=cfg.get('provider',{}).get('deepseek',{}).get('npm')
 # Verify loopback override before starting any prompt; do not print endpoint or secrets.
 endpoint=cfg.get('provider',{}).get('deepseek',{}).get('options',{}).get('baseURL','')
 assert endpoint==f'http://127.0.0.1:{relay.server_port}/v1','Loopback override absent'
 session=api('/session',{'title':'本地模型适配层额度核查（合成响应）'});result['sessionID']=session['id']
 api('/session/'+session['id']+'/prompt_async',{'agent':'liuren-adjudicator','model':{'providerID':'deepseek','modelID':'deepseek-flash'},'parts':[{'type':'text','text':'Local synthetic adapter request check. Reply OK.'}]})
 for _ in range(120):
  if captured:break
  time.sleep(.25)
 result['capturedRequests']=captured;result['passed']=bool(captured) and all(not any(k in p for k in ['max_tokens','max_completion_tokens','max_output_tokens']) for p in captured)
except Exception as e:result['errorType']=type(e).__name__;result['error']=str(e)[:200]
finally:
 if server:server.terminate();server.wait(timeout=10)
 log.close();relay.shutdown();relay.server_close()
(OUT/'native-adapter-capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(result,ensure_ascii=False))
