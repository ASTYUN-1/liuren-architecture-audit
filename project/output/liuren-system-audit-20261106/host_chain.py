"""Real OpenCode + installed slim; scripted synthetic responses on loopback only."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,os,subprocess,threading,time,tempfile,hashlib,shutil,traceback
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
base=OUT/'host-probe';base.mkdir(exist_ok=True)
project=Path(tempfile.mkdtemp(prefix='liuren-host-audit-'))
fixture=read(OUT/'synthetic-fixture.json');pointer=read(OUT/'candidate-active.json');manifest=read(OUT/'candidate-runtime/manifest.json')
shutil.copytree(OUT/'candidate-runtime',project/pointer['runtime'])
shutil.copytree(ROOT/'tools',project/'tools',ignore=shutil.ignore_patterns('tests','__pycache__'))
for rel in ['排盘工具魔改/js/lunar.js','docs/本机六壬直接排盘.md']:
 dst=project/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
(project/'.opencode').mkdir(exist_ok=True);(project/'.opencode/liuren-active.json').write_text(json.dumps(pointer,ensure_ascii=False),encoding='utf-8')
slim=read(ROOT/'.opencode/oh-my-opencode-slim.jsonc');slim['disabled_mcps']=['context7','gh_grep'];slim['multiplexer']={'enabled':False}
(project/'.opencode/oh-my-opencode-slim.jsonc').write_text(json.dumps(slim,ensure_ascii=False),encoding='utf-8')
wrapper=base/'wrapper.ts'
slimfile=Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim/dist/index.js'
wrapper.write_text('''import original from %s;
import materials from %s;
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import path from 'node:path';
const run=promisify(execFile);
export default async ctx=>{const hooks=await original(ctx);return {...hooks,tool:{...hooks.tool,liuren_materials:{...materials,async execute(args,context){const r=await run('python',['-X','utf8',path.join(ctx.directory,'tools/liuren-materials.py'),'--request',JSON.stringify({...args,_context_key:context.sessionID})],{cwd:ctx.directory,encoding:'utf8',windowsHide:true,timeout:15000,maxBuffer:4*1024*1024});return r.stdout;}}}};};
'''%(json.dumps((ROOT/'.opencode/plugins/liuren-adjudication.ts').as_uri()),json.dumps((ROOT/'.opencode/tools/liuren_materials.ts').as_uri())),encoding='utf-8')
state={'main':0,'child':0,'call':0,'child_pages':0,'receipt':None,'finished':False};events=[];failures=[]
def call(name,args):
 state['call']+=1
 return {'id':'audit_call_'+str(state['call']),'type':'function','function':{'name':name,'arguments':json.dumps(args,ensure_ascii=False)}}
def tool_results(messages):return [m for m in messages if m.get('role')=='tool']
def content(m):
 v=m.get('content','');return v if isinstance(v,str) else '\n'.join(x.get('text','') for x in v if isinstance(x,dict))
def result(messages):
 text=content(tool_results(messages)[-1]);
 try:return json.loads(text)
 except ValueError:
  a=text.find('{');b=text.rfind('}');
  if a<0:raise ValueError('Non-JSON tool result: '+text[:3000])
  return json.loads(text[a:b+1])
def response(payload):
 messages=payload['messages'];system='\n'.join(content(m) for m in messages if m.get('role')=='system')
 child='LOCAL_LIUREN_MAIN_TEST' not in system
 names=[x['function']['name'] for x in payload.get('tools',[])]
 if not names and 'LIUREN_ADJUDICATION_FILE_V1' not in json.dumps(messages,ensure_ascii=False):return None,'Local synthetic integration'
 events.append({'who':'child' if child else 'main','stage':state['child' if child else 'main'],'tools':names,'model':payload.get('model'),'reasoning_effort':payload.get('reasoning_effort')})
 if child:
  users=[content(m) for m in messages if m.get('role')=='user'];ref=next(t for t in users if 'LIUREN_ADJUDICATION_FILE_V1' in t)
  # The hook passes exactly three lines; wrappers may surround them.
  lines=ref[ref.index('LIUREN_ADJUDICATION_FILE_V1'):].splitlines();args={'file_path':lines[1].strip(),'sha256':lines[2].strip(),'page':1}
  if not tool_results(messages):return [call('liuren_adjudication_read',args)],None
  value=result(messages)
  if value.get('schema')=='liuren-adjudication-file-page-v1':
   state['child_pages']+=1
   if value['page']<value['pages']:args['page']=value['page']+1;return [call('liuren_adjudication_read',args)],None
   return [call('liuren_adjudication_submit',{'result':fixture['result']})],None
  assert value.get('contractChecked') is True,value
  return None,json.dumps(value,ensure_ascii=False)
 stage=state['main'];state['main']+=1
 if stage==0:return [call('liuren_materials',{'action':'method','module':m}) for m in [x for x in manifest['required'] if x!='report']+['finance']],None
 if stage==1:
  assert all('LIUREN_METHOD_BEGIN' in content(x) for x in tool_results(messages))
  return [call('liuren_adjudication_packet',{'packet':fixture['packet']})],None
 if stage==2:
  value=result(messages);assert value.get('task_prompt'),value
  return [call('task',{'description':'大六壬合成全链验证','subagent_type':'liuren-adjudicator','prompt':value['task_prompt'],'background':False})],None
 if stage==3:
  value=result(messages);assert value.get('schema')=='liuren-adjudication-receipt-v1' and value.get('status')=='completed',value
  state['receipt']=value;return [call('task_result',{'task_id':value['task_id']})],None
 if stage==4:
  value=result(messages);assert value.get('task_id')==state['receipt']['task_id'] and value.get('contractChecked') is True,value
  return [call('liuren_materials',{'action':'method','module':'report'})],None
 if stage==5:return [call('liuren_adjudication_result',{'task_id':state['receipt']['task_id'],'action':'deliver'})],None
 value=result(messages);assert value.get('schema')=='liuren-delivery-v1',value
 assert '辛巳' in value['report_markdown'] and '计算值：48' in value['report_markdown']
 (OUT/'host-report.md').write_text(value['report_markdown'],encoding='utf-8');state['finished']=True
 return None,'LOCAL_CHAIN_COMPLETED: '+value['report_ref']['sha256']
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  raw=json.dumps({'object':'list','data':[{'id':'deepseek-flash','object':'model','owned_by':'local'}]}).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_POST(self):
  try:
   payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));calls,text=response(payload)
   delta={'role':'assistant',**({'tool_calls':[{**c,'index':i} for i,c in enumerate(calls)]} if calls else {'content':text})}
   chunk={'id':'local-host-audit','object':'chat.completion.chunk','created':int(time.time()),'model':'deepseek-flash','choices':[{'index':0,'delta':delta,'finish_reason':None}]}
   done={**chunk,'choices':[{'index':0,'delta':{},'finish_reason':'tool_calls' if calls else 'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}}
   raw=('data: '+json.dumps(chunk,ensure_ascii=False)+'\n\ndata: '+json.dumps(done)+'\n\ndata: [DONE]\n\n').encode()
   self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  except Exception as e:
   failures.append(traceback.format_exc());raw=json.dumps({'error':{'message':str(e),'type':'audit_failed'}}).encode();self.send_response(400);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
slimfile=Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim/dist/index.js'
config={'enabled_providers':['deepseek'],'provider':{'deepseek':{'npm':'@ai-sdk/openai-compatible','name':'Local synthetic provider','options':{'baseURL':'http://127.0.0.1:'+str(server.server_port)+'/v1','apiKey':'[REDACTED_CREDENTIAL]'},'models':{'deepseek-flash':{'name':'Synthetic test','tool_call':True,'limit':{'context':262144,'output':65536}}}}},'model':'deepseek/deepseek-flash','small_model':'deepseek/deepseek-flash','plugin':[slimfile.as_uri(),wrapper.as_uri()],'agent':{'liuren':{'mode':'primary','prompt':'LOCAL_LIUREN_MAIN_TEST. Execute the scripted synthetic integration calls.','permission':{'*':'deny','liuren_materials':'allow','liuren_adjudication_packet':'allow','task':{'*':'deny','liuren-adjudicator':'allow'},'task_result':'allow','liuren_adjudication_result':'allow'}}}}
config['plugin']=[slimfile.as_uri()]
auto=base/'config/opencode/plugins';auto.mkdir(parents=True,exist_ok=True);shutil.copyfile(wrapper,auto/'liuren-audit.ts')
if (auto/'slim-audit.ts').exists():(auto/'slim-audit.ts').unlink()
env=os.environ.copy()
for k in list(env):
 if k.startswith('OPENCODE_') or k in ['OPENAI_API_KEY','ANTHROPIC_API_KEY','DEEPSEEK_API_KEY']:env.pop(k)
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
 (base/name).mkdir(exist_ok=True);env[key]=str(base/name)
env['OPENCODE_CONFIG_DIR']=str(base/'config/opencode');env['OPENCODE_CONFIG_CONTENT']=json.dumps(config)
env['OPENCODE_LOG_DIR']=str(base/'logs')
for key in ['OPENCODE_DISABLE_PROJECT_CONFIG','OPENCODE_DISABLE_MODELS_FETCH','OPENCODE_DISABLE_AUTOUPDATE','OPENCODE_DISABLE_DEFAULT_PLUGINS','OPENCODE_DISABLE_CLAUDE_CODE','OPENCODE_DISABLE_LSP_DOWNLOAD']:env[key]='true'
exe=Path.home()/'scoop/apps/opencode/current/opencode.exe'
try:
 proc=subprocess.run([str(exe),'--print-logs','--log-level','DEBUG','run','--dir',str(project),'--model','deepseek/deepseek-flash','--agent','liuren','--format','json',fixture['question']],env=env,cwd=project,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=55)
 code=proc.returncode;output=proc.stdout
except subprocess.TimeoutExpired as e:
 code=-1;output=e.stdout.decode('utf-8','replace') if isinstance(e.stdout,bytes) else e.stdout or ''
finally:server.shutdown();server.server_close()
(OUT/'host-cli.log').write_text(output,encoding='utf-8')
summary={'exitCode':code,'finished':state['finished'],'events':events,'failures':failures,'state':state,'loopbackOnly':True,'realModelCalled':False,'slimFile':str(slimfile),'slimSha256':hashlib.sha256(slimfile.read_bytes()).hexdigest(),'project':str(project),'implementationSha256':{rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in ['.opencode/plugins/liuren-adjudication.ts','tools/liuren-flow-control.mjs','tools/liuren-adjudication-output.mjs','tools/liuren-adjudication-schema.mjs','tools/liuren-deterministic-io.mjs','.opencode/oh-my-opencode-slim.jsonc']}}
summary['candidateRuntimeSha256']={f.relative_to(OUT/'candidate-runtime').as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in (OUT/'candidate-runtime').rglob('*') if f.is_file()}
summary['fixtureSha256']=hashlib.sha256((OUT/'synthetic-fixture.json').read_bytes()).hexdigest()
summary['childModelAndHighVerified']=all(e['model']=='deepseek-flash' and e['reasoning_effort']=='high' for e in events if e['who']=='child') and any(e['who']=='child' for e in events)
(OUT/'host-chain.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exitCode':code,'finished':summary['finished'],'requests':len(events),'childPages':state['child_pages'],'failures':failures[-1:]},ensure_ascii=False))
