"""Actual project and automatic local tool/plugin discovery; no composition wrapper."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,os,socket,subprocess,threading,time,traceback,urllib.request
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
base=OUT/'autoload-host';base.mkdir(exist_ok=True)
state={'step':0,'finished':False};events=[];errors=[]
required=['skill','read','liuren_chart','liuren_materials','liuren_compute','liuren_tool_help','liuren_adjudication_packet','liuren_adjudication_result','task','task_result']
def response(payload):
 names=[t['function']['name'] for t in payload.get('tools',[])]
 if not names:return None,'Local registration check'
 assert set(required).issubset(names),('Missing auto-discovered tools',set(required)-set(names))
 events.append({'tools':names})
 stage=state['step'];state['step']+=1
 def call(name,args):return {'id':f'autoload_{stage}_{name}','type':'function','function':{'name':name,'arguments':json.dumps(args,ensure_ascii=False)}}
 results=[m for m in payload['messages'] if m.get('role')=='tool']
 if stage==0:return [call('skill',{'name':'daliuren'}),call('liuren_tool_help',{'topic':'workflow','domains':['exam']})],None
 if stage==1:
  content='\n'.join(str(m.get('content')) for m in results)
  assert 'archive_metadata_passthrough' in content and '大六壬占事' in content
  return [call('liuren_materials',{'action':'method','module':'positioning'}),call('liuren_compute',{'action':'calendar','calendar':{'start':'2026-11-03','end':'2026-11-03','timezone':'Asia/Shanghai','day_boundary':'civil-midnight'}}),call('read',{'filePath':(ROOT/'runtime/liuren'/load(ROOT/'.opencode/liuren-active.json')['release']/'methods/positioning.md').as_posix()})],None
 content='\n'.join(str(m.get('content')) for m in results)
 assert 'LIUREN_METHOD_BEGIN' in content and '辛巳' in content
 assert '<file' in content or '<path>' in content or '原问、对象与取用' in content
 state['finished']=True
 return None,'LOCAL_AUTOLOAD_VERIFIED'
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  raw=b'{"object":"list","data":[]}';self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_POST(self):
  try:
   p=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));calls,text=response(p)
   delta={'role':'assistant',**({'tool_calls':[{**c,'index':i} for i,c in enumerate(calls)]} if calls else {'content':text})}
   v={'id':'local-autoload','object':'chat.completion.chunk','created':int(time.time()),'model':'deepseek-flash','choices':[{'index':0,'delta':delta,'finish_reason':None}]}
   done={**v,'choices':[{'index':0,'delta':{},'finish_reason':'tool_calls' if calls else 'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}}
   raw=('data: '+json.dumps(v,ensure_ascii=False)+'\n\ndata: '+json.dumps(done)+'\n\ndata: [DONE]\n\n').encode()
   self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  except Exception as e:
   errors.append(traceback.format_exc());raw=json.dumps({'error':{'message':str(e)}}).encode();self.send_response(400);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
relay=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=relay.serve_forever,daemon=True).start()
config=load(ROOT/'opencode.json')
slim=Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim/dist/index.js'
config['plugin']=[slim.as_uri(),(ROOT/'.opencode/plugins/liuren-adjudication.ts').as_uri()]
config['enabled_providers']=['deepseek'];config['provider']={'deepseek':{'npm':'@ai-sdk/openai-compatible','name':'Local registration verifier','options':{'baseURL':f'http://127.0.0.1:{relay.server_port}/v1','apiKey':'local-only'},'models':{'deepseek-flash':{'name':'Local scripted model','tool_call':True,'limit':{'context':262144,'output':65536}}}}}
config.update(model='deepseek/deepseek-flash',small_model='deepseek/deepseek-flash',snapshot=False)
env=os.environ.copy()
for key in list(env):
 if key.startswith('OPENCODE_') or key in ['OPENAI_API_KEY','ANTHROPIC_API_KEY','DEEPSEEK_API_KEY']:env.pop(key)
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
 (base/name).mkdir(exist_ok=True);env[key]=str(base/name)
cfg=base/'config/opencode/opencode.json';cfg.parent.mkdir(exist_ok=True);cfg.write_text(json.dumps(config,ensure_ascii=False),'utf-8')
env.update(OPENCODE_CONFIG=str(cfg),OPENCODE_CONFIG_DIR=str(cfg.parent),OPENCODE_LOG_DIR=str(base/'logs'))
for key in ['OPENCODE_DISABLE_MODELS_FETCH','OPENCODE_DISABLE_AUTOUPDATE','OPENCODE_DISABLE_CLAUDE_CODE','OPENCODE_DISABLE_LSP_DOWNLOAD']:env[key]='true'
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close();url=f'http://127.0.0.1:{port}'
desktop=Path.home()/'AppData/Local/Programs/@opencode-aidesktop/OpenCode.exe'
log=(OUT/'autoload-server.log').open('w',encoding='utf-8');server=None;output='';code=-1
try:
 server=subprocess.Popen([str(desktop),str(OUT/'desktop-server.mjs'),str(port)],cwd=ROOT,env={**env,'ELECTRON_RUN_AS_NODE':'1'},stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 for _ in range(100):
  try:urllib.request.urlopen(url+'/global/health',timeout=1).close();break
  except Exception:time.sleep(.15)
 proc=subprocess.run([str(Path.home()/'scoop/apps/opencode/current/opencode.exe'),'run','--attach',url,'--dir',str(ROOT),'--model','deepseek/deepseek-flash','--agent','liuren','--format','json','仅做本机工具注册与调用检查，不作专业占断，不修改网站。'],cwd=ROOT,env=env,capture_output=True,encoding='utf-8',timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
 code=proc.returncode;output=proc.stdout+proc.stderr
except Exception:errors.append(traceback.format_exc())
finally:
 if server is not None:server.terminate();server.wait(timeout=10)
 log.close();relay.shutdown();relay.server_close()
(OUT/'autoload-cli.jsonl').write_text(output,'utf-8')
parts=[json.loads(line)['part'] for line in output.splitlines() if line.startswith('{') and json.loads(line).get('type')=='tool_use']
tool_errors=[{'tool':p['tool'],'error':p['state'].get('error')} for p in parts if p['state']['status']!='completed']
result={'exitCode':code,'finished':state['finished'],'events':events,'errors':errors,'toolErrors':tool_errors,'actualProject':str(ROOT),'automaticProjectDiscovery':True,'toolCompositionWrapper':False,'permissionsChanged':False,'snapshotDisabledForSmokeOnly':True,'externalModelCalls':0,'websiteChanged':False}
(OUT/'autoload-smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='events'},ensure_ascii=False));raise SystemExit(0 if state['finished'] and not errors and not tool_errors else 1)
