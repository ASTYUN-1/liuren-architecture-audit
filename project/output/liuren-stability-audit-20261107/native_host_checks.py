"""Real global/project loading, scripted provider; MCP calls and full native workflow."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,os,socket,subprocess,threading,time,traceback,urllib.request,urllib.parse,sys,uuid
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];mode=sys.argv[1] if len(sys.argv)>1 else 'flow'
project=ROOT;pointer=json.loads((ROOT/'.opencode/liuren-active.json').read_text('utf-8'))
globals().update(OUT=OUT,ROOT=ROOT,project=project,pointer=pointer)
exec((OUT/('native_flow_length_scenario.py' if mode=='length' else 'native_flow_scenario.py')).read_text('utf-8'),globals())
flow_response=response;probe='__opencode_connectivity_'+uuid.uuid4().hex+'__';mcp_tools=[];schemas=[];child_request_checks=[]
def mcp_response(payload):
 names=[t['function']['name'] for t in payload.get('tools',[])];definitions={t['function']['name']:t['function'] for t in payload.get('tools',[])}
 if not names:return None,'Local diagnostic title'
 if state['main']==0:
  schemas.extend(definitions.values());calls=[]
  specs=[('memory','search_nodes',{'query':probe}),('sequential-thinking','sequentialthinking',{'thought':'Synthetic connectivity check only.','nextThoughtNeeded':False,'thoughtNumber':1,'totalThoughts':1}),('chrome-devtools','list_pages',{}),('context7','resolve-library-id',{'libraryName':'python','query':'Find official Python documentation; connectivity check only.'}),('filesystem','list_allowed_directories',{}),('scrapling','get',{'url':'https://example.com'}),('windows-mcp','Shell',{'command':"Write-Output 'MCP_PROBE_OK'"}),('aoci','aoci_rules',{}),('gh_grep','searchGitHub',{'query':probe})]
  for server,suffix,args in specs:
   matches=[name for name in names if name.lower().startswith(server.lower().replace('-','_')+'_') or name.lower().startswith(server.lower()+'_')]
   matched=[name for name in matches if name.lower().replace('-','_').endswith(suffix.lower().replace('-','_'))]
   if not matched and server=='scrapling':matched=[name for name in matches if name.lower().endswith(('_fetch','_get'))]
   if not matched:mcp_tools.append({'server':server,'available':False,'candidateTools':matches,'status':mcp_status.get(server)});continue
   name=matched[0];props=definitions[name]['parameters'].get('properties',{})
   if server=='aoci':
    for key in definitions[name]['parameters'].get('required',[]):
     if key in ['root','repo_root','repository','repo','repository_root','project_path','path']:args[key]=str(ROOT)
   if server=='scrapling' and 'urls' in props:args={'urls':['https://example.com']}
   args={k:v for k,v in args.items() if k in props}
   missing=[key for key in definitions[name]['parameters'].get('required',[]) if key not in args]
   if missing:mcp_tools.append({'server':server,'available':True,'tool':name,'skippedRequiredFields':missing});continue
   mcp_tools.append({'server':server,'available':True,'tool':name});calls.append(call(name,args))
  state['main']=1;return emit(calls)
 state['finished']=True;return None,'MCP_READ_ONLY_PROBES_COMPLETED'
def response(payload):
 if mode=='mcp':return mcp_response(payload)
 names=[t['function']['name'] for t in payload.get('tools',[])]
 if 'liuren_adjudication_read' in names and 'liuren_adjudication_packet' not in names:
  keys=[k for k in ['max_tokens','max_completion_tokens','max_output_tokens'] if k in payload]
  assert not keys and payload.get('reasoning_effort')=='high'
  child_request_checks.append({'model':payload.get('model'),'reasoning_effort':payload.get('reasoning_effort'),'outputBudgetKeys':keys})
 return flow_response(payload)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  raw=b'{"object":"list","data":[]}';self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_POST(self):
  try:
   payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));calls,text=response(payload)
   exhausted=text=='__LENGTH_WITH_REASONING__'
   delta={'role':'assistant',**({'tool_calls':[{**c,'index':i} for i,c in enumerate(calls)]} if calls else {'content':text})}
   if exhausted:delta={'role':'assistant','reasoning_content':'Synthetic private reasoning; never use as report.'}
   chunk={'id':'native-check','object':'chat.completion.chunk','created':int(time.time()),'model':'deepseek-flash','choices':[{'index':0,'delta':delta,'finish_reason':None}]}
   done={**chunk,'choices':[{'index':0,'delta':{},'finish_reason':'length' if exhausted else 'tool_calls' if calls else 'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}}
   raw=('data: '+json.dumps(chunk,ensure_ascii=False)+'\n\ndata: '+json.dumps(done)+'\n\ndata: [DONE]\n\n').encode()
   self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  except Exception:
   failures.append(traceback.format_exc());raw=b'{"error":{"message":"native diagnostic scenario failed"}}';self.send_response(400);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  finally:(OUT/(mode+'-progress.json')).write_text(json.dumps({'state':state,'checks':checks,'failures':failures},ensure_ascii=False,indent=2),'utf-8')
relay=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=relay.serve_forever,daemon=True).start()
override={'snapshot':False,'model':'deepseek/deepseek-flash','small_model':'deepseek/deepseek-flash','enabled_providers':['deepseek'],'provider':{'deepseek':{'npm':'@ai-sdk/openai-compatible','options':{'baseURL':f'http://127.0.0.1:{relay.server_port}/v1','apiKey':'[REDACTED_CREDENTIAL]'},'models':{'deepseek-flash':{'name':'Synthetic native diagnostic','tool_call':True,'limit':{'context':1048576,'output':393216}}}}}}
if mode=='mcp':override['agent']={'build':{'permission':{'*':'allow'}}}
env=os.environ.copy();env.update(ELECTRON_RUN_AS_NODE='1',OPENCODE_DISABLE_AUTOUPDATE='true',OPENCODE_DISABLE_MODELS_FETCH='true',OPENCODE_DISABLE_LSP_DOWNLOAD='true',OPENCODE_CONFIG_CONTENT=json.dumps(override))
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close();url=f'http://127.0.0.1:{port}';query='?directory='+urllib.parse.quote(str(ROOT))
def api(path,body=None,timeout=20):
 req=urllib.request.Request(url+path+query,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:raw=r.read();return json.loads(raw) if raw else None
exe=Path.home()/'AppData/Local/Programs/@opencode-aidesktop/OpenCode.exe';log=(OUT/(mode+'-server.log')).open('w',encoding='utf-8');server=None;tool_results=[];sid=None;started=time.monotonic()
try:
 server=subprocess.Popen([str(exe),str(ROOT/'output/liuren-stalled-child-repair-20261107/desktop-server.mjs'),str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 for _ in range(100):
  try:urllib.request.urlopen(url+'/global/health',timeout=.5).close();break
  except Exception:time.sleep(.15)
 config=api('/config',timeout=60);agents=api('/agent',timeout=60)
 mcp_status={k:v.get('status') for k,v in api('/mcp',timeout=60).items()}
 (OUT/(mode+'-loading.json')).write_text(json.dumps({'plugins':config.get('plugin'),'default_agent':config.get('default_agent'),'mcpStatus':mcp_status,'adjudicator':[{'name':a['name'],'model':a.get('model'),'variant':a.get('variant')} for a in agents if a['name']=='liuren-adjudicator'],'noCompositionWrapper':True},ensure_ascii=False,indent=2)+'\n','utf-8')
 session=api('/session',{'title':'本机稳定性诊断-'+mode+'-20261107'});sid=session['id']
 api('/session/'+sid+'/prompt_async',{'agent':'build' if mode=='mcp' else 'liuren','model':{'providerID':'deepseek','modelID':'deepseek-flash'},'parts':[{'type':'text','text':'本次只做只读MCP连通性诊断。' if mode=='mcp' else question}]})
 while time.monotonic()-started<240:
  messages=api('/session/'+sid+'/message');assistants=[m for m in messages if m['info']['role']=='assistant']
  if assistants and (assistants[-1]['info'].get('error') or assistants[-1]['info'].get('finish') not in [None,'tool-calls','unknown']):break
  time.sleep(.5)
 for m in messages:
  for part in m.get('parts',[]):
   if part['type']=='tool':
    value=part.get('state',{});output=value.get('output','');tool_results.append({'tool':part['tool'],'status':value.get('status'),'outputChars':len(output),'errorPresent':bool(value.get('error')),'textErrorPrefix':output.startswith(('Error:','Tool execution failed'))})
 if not state['finished']:failures.append('Scenario did not finish');api('/session/'+sid+'/abort',{})
except Exception:failures.append(traceback.format_exc())
finally:
 if server is not None:server.terminate();server.wait(timeout=10)
 log.close();relay.shutdown();relay.server_close()
result={'mode':mode,'sessionID':sid,'finished':state['finished'],'seconds':round(time.monotonic()-started,2),'checks':checks,'toolResults':tool_results,'mcpTools':mcp_tools,'childRequests':child_request_checks,'failures':failures,'externalModelCalls':0,'actualGlobalAndProjectConfig':True,'compositionWrapper':False,'websiteChanged':False}
result['passed']=state['finished'] and not failures and bool(tool_results) and all(t['status']=='completed' and not t['errorPresent'] and not t['textErrorPrefix'] for t in tool_results)
(OUT/(mode+'-result.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
if mode=='mcp':(OUT/'mcp-tool-schemas.json').write_text(json.dumps(schemas,ensure_ascii=False,indent=2)+'\n','utf-8')
if mode=='flow':(OUT/'current-wire.json').write_text(json.dumps({'exitCode':0 if state['finished'] and not failures else 1,'realModelCalled':False,'scope':'Native global/project plugin loading; no wrapper','requests':[{'tools':wire}],'implementationSha256':{rel:__import__('hashlib').sha256((ROOT/rel).read_bytes()).hexdigest() for rel in ['.opencode/plugins/liuren-adjudication.ts','tools/liuren-flow-control.mjs','tools/liuren-compute-schema.mjs','tools/liuren-adjudication-output.mjs','.opencode/tools/liuren_materials.ts']}},ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['passed'] else 1)
