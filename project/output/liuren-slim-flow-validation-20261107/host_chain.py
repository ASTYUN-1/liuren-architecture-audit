"""Installed desktop host + exact production tools/permissions; scripted loopback only.

Tests actual registration/permission/schema/execution/session transitions, not model judgment.
No credential is read and no external model endpoint is contacted.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import hashlib,json,os,shutil,socket,subprocess,threading,time,traceback,urllib.request,tempfile,uuid

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pointer=load(ROOT/'.opencode/liuren-active.json')
manifest=load(ROOT/pointer['runtime']/'manifest.json')
base=OUT/'host-data'
project=Path(tempfile.gettempdir())/('liuren-slim-host-'+uuid.uuid4().hex)
if (OUT/'host-chain.json').exists():
 previous=OUT/'attempts'/time.strftime('%Y%m%d-%H%M%S');previous.mkdir(parents=True)
 for name in ['host-chain.json','host-cli.jsonl','progress.json','server.log']:
  if (OUT/name).exists():shutil.copyfile(OUT/name,previous/name)
assert not project.exists(),'Use a fresh test directory; do not overwrite a prior run.'
project.mkdir(parents=True)
(project/'.gitignore').write_text('.opencode/node_modules/\noutput/\n排盘存档/\n','utf-8')
# Native read permissions are relative to the host's Git worktree, not cwd.
# Give the isolated fixture its own root so the unchanged relative allowlist applies.
subprocess.run([shutil.which('git'),'init','--quiet',str(project)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
for rel in [pointer['runtime'],'tools','.opencode/skills/liuren','.opencode/tools','.opencode/plugins']:
 shutil.copytree(ROOT/rel,project/rel,ignore=shutil.ignore_patterns('tests','__pycache__'))
for rel in ['AGENTS.md','README.md','目录总索引.md','docs/本机六壬直接排盘.md','docs/本机六壬完整研判流程.md','docs/本机六壬高效执行.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬资料检索范围.md']:
 dst=project/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
for row in load(ROOT/'tools/liuren-direct/legacy-engine-manifest.json')['files']:
 rel='排盘工具魔改/'+row['path'];dst=project/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
for rel in ['knowledge/liuren-book-index/20261105','书籍库/经典古籍/佚名/壬归.txt','书籍库/北海闲人/理法简易.txt','书籍库/现代著作/献给六壬天一群的六壬笔记-2023年.txt','docs/应期取数归纳-20261027']:
 src=ROOT/rel;dst=project/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if src.is_dir():shutil.copytree(src,dst)
 else:shutil.copyfile(src,dst)
(project/'.opencode/liuren-active.json').write_text(json.dumps(pointer,ensure_ascii=False),'utf-8')
# Junction uses the existing tool SDK dependency without copying or changing it.
node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([str(node),'-e',"require('fs').symlinkSync(process.argv[1],process.argv[2],'junction')",str(ROOT/'.opencode/node_modules'),str(project/'.opencode/node_modules')],check=True)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')
slim['disabled_mcps']=['context7','gh_grep'];slim['multiplexer']={'enabled':False}
(project/'.opencode/oh-my-opencode-slim.jsonc').write_text(json.dumps(slim,ensure_ascii=False),'utf-8')
slimfile=Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim/dist/index.js'
wrapper=project/'wrapper.ts'
wrapper.write_text('''import {OhMyOpenCodeLite} from %s;
import original from %s;
import materials from %s;
import chart from %s;
const server=async ctx=>{const slim=await OhMyOpenCodeLite(ctx),own=await original(ctx),hooks={...slim,...own};
for(const key of Object.keys(own))if(typeof slim[key]==='function'&&typeof own[key]==='function')hooks[key]=async(...args)=>{await slim[key](...args);return await own[key](...args);};
hooks.tool={...slim.tool,...own.tool,liuren_materials:materials,liuren_chart:chart};return hooks;};
export default {id:'liuren-slim-real-host-validation',server};
'''%(json.dumps(slimfile.as_uri()),json.dumps((project/'.opencode/plugins/liuren-adjudication.ts').as_uri()),json.dumps((project/'.opencode/tools/liuren_materials.ts').as_uri()),json.dumps((project/'.opencode/tools/liuren_chart.ts').as_uri())),'utf-8')
state={'main':0,'calls':0,'childReadCalls':0,'childPages':0,'finished':False,'archive':None,'receipt':None}
events=[];failures=[];expected=[];checks=[];wire=[]
report='# 合成流程验收正文\n\n本报告只验工具与交接，不提供预测。日期：2026-11-03辛巳；计算：8×6=48。\n来源与限制完整保留。'
question='电脑维修能否完成？何时修好？费用多少？本次仅作工具流程测试，不提供真实反馈，不验证预测。'
def content(m):
 v=m.get('content','');return v if isinstance(v,str) else '\n'.join(x.get('text','') for x in v if isinstance(x,dict))
def parsed(m):
 text=content(m)
 try:return json.loads(text)
 except ValueError:
  a=text.find('{');b=text.rfind('}')
  if a<0:raise ValueError('Expected JSON tool receipt: '+text[:1500])
  return json.loads(text[a:b+1])
def call(name,args):
 state['calls']+=1
 return {'id':'slim_native_'+str(state['calls']),'type':'function','function':{'name':name,'arguments':json.dumps(args,ensure_ascii=False)}}
def emit(calls):
 global expected
 expected=[(c['id'],c['function']['name']) for c in calls]
 return calls,None
def consume(messages):
 results={m.get('tool_call_id'):m for m in messages if m.get('role')=='tool'}
 all_values={}
 for ident,name in expected:
  assert ident in results,('Missing tool response',name)
  text=content(results[ident])
  assert not text.startswith(('Error:','Tool execution failed')), (name,text[:1500])
  all_values.setdefault(name,[]).append(results[ident])
 return {**{name:results[ident] for ident,name in expected},'_all':all_values}
def valid_schema(v):
 if isinstance(v,dict):
  assert '$ref' not in v,'Host dropped a referenced schema definition'
  for x in v.values():valid_schema(x)
 elif isinstance(v,list):
  for x in v:valid_schema(x)
def response(payload):
 messages=payload['messages'];names=[x['function']['name'] for x in payload.get('tools',[])]
 if not names:return None,'Local tool chain validation'
 child='liuren_adjudication_read' in names and 'liuren_adjudication_packet' not in names
 events.append({'who':'child' if child else 'main','stage':state['main'],'tools':names,'model':payload.get('model'),'reasoning_effort':payload.get('reasoning_effort')})
 for definition in payload.get('tools',[]):valid_schema(definition['function']['parameters'])
 if not child and not wire:wire.extend({'name':x['function']['name'],'parameters':x['function']['parameters']} for x in payload.get('tools',[]) if x['function']['name'].startswith('liuren_'))
 if child:
  assert all(n in names for n in ['liuren_adjudication_read','liuren_adjudication_submit','liuren_compute','liuren_tool_help']),names
  tools=[m for m in messages if m.get('role')=='tool']
  if not tools:
   raw=next(content(m) for m in messages if m.get('role')=='user' and 'LIUREN_ADJUDICATION_FILE_V1' in content(m))
   lines=raw[raw.index('LIUREN_ADJUDICATION_FILE_V1'):].splitlines()
   return [call('liuren_adjudication_read',{'file_path':lines[1].strip(),'sha256':lines[2].strip(),'page':1,'page_count':4})],None
  v=parsed(tools[-1])
  if v.get('schema')=='liuren-adjudication-file-page-v1':
   state['childReadCalls']+=1;state['childPages']+=v.get('page_end',v['page'])-v['page']+1
   if v.get('next_call'):return [call(v['next_call']['tool'],v['next_call']['arguments'])],None
   return [call('liuren_compute',{'action':'calendar','calendar':{'start':'2026-11-03','end':'2026-11-03','timezone':'Asia/Shanghai','day_boundary':'civil-midnight'}})],None
  if v.get('schema')=='liuren-adjudication-receipt-v1':
   assert v['status']=='completed',v
   return None,json.dumps(v,ensure_ascii=False)
  return [call('liuren_adjudication_submit',{'result':report})],None
 stage=state['main'];state['main']+=1
 required=['skill','liuren_chart','liuren_materials','liuren_tool_help','liuren_compute','liuren_adjudication_packet','task','task_result','liuren_adjudication_result','read']
 assert all(n in names for n in required),('Unavailable tools',[n for n in required if n not in names],names)
 values=consume(messages) if expected else {}
 if stage==0:return emit([call('skill',{'name':'daliuren'})])
 if stage==1:
  assert '大六壬占事' in content(values['skill'])
  checks.append('真实skill入口可加载')
  return emit([call('liuren_tool_help',{'topic':'workflow','domains':['finance']})])
 if stage==2:
  v=parsed(values['liuren_tool_help']);assert v['tool_contract']=='liuren-tools-25';assert 'shensha-use' in v['readiness']['missing']
  checks.append('工具契约及8项路由自说明正常')
  return emit([call('liuren_chart',{'datetime':'2026-10-18T13:22','label':'流程合成验收','participants':[{'sex':'女','birth_year':2001}]})])
 if stage==3:
  v=parsed(values['liuren_chart']);assert v['ok'] and v.get('program_facts') and v.get('archive'),list(v)
  state['archive']=v['archive'];state['day_stem']=v['facts']['day_stem']
  assert str(project) in state['archive']['path'],'Chart archive escaped isolated project'
  checks.append('真实排盘工具、独立Node运行时与归档正常')
  return emit([call('liuren_materials',{'action':'method','modules':['positioning','liqi','structure','void']})])
 if stage in [4,5,6]:
  assert content(values['liuren_materials']).count('LIUREN_METHOD_BEGIN ')==4,content(values['liuren_materials'])[:1500]
  if stage==4:return emit([call('liuren_materials',{'action':'method','modules':['shensha-use','movement','adjudication','finance']})])
  if stage==5:return emit([call('liuren_materials',{'action':'method','modules':['timing','quantity','quantity-sources','nianming']})])
  checks.append('三组真实全文合批及准备回执正常')
  return emit([call('liuren_tool_help',{'topic':'workflow','domains':['finance']}),call('liuren_materials',{'action':'shensha','path':state['archive']['path']})])
 if stage==7:
  assert parsed(values['liuren_tool_help'])['readiness']['ready'] is True
  assert content(values['liuren_materials'])
  checks.append('完整神煞读取与准备缺项清零')
  return emit([call('liuren_compute',{'action':'chart','archive':state['archive'],'symbols':['庚','丑']}),call('liuren_materials',{'action':'book_search','book':'LF','query':'死火克不动旺金','limit':1}),call('read',{'filePath':(project/pointer['runtime']/'methods/positioning.md').as_posix()})])
 if stage==8:
  assert '原问、对象与取用' in content(values['read'])
  assert content(values['liuren_compute']) and content(values['liuren_materials'])
  checks.append('程序计算、三书检索和原生read权限正常')
  return emit([call('liuren_compute',{'action':'quantity','expression':{'op':'multiply','args':[{'value':8},{'value':6}]}}),call('liuren_materials',{'action':'book_outline','book':'RG'}),call('liuren_compute',{'action':'life','archive':state['archive'],'life':{'age':21,'sex':'女','age_basis':'虚岁-已核'}}),call('liuren_compute',{'action':'lookup','archive':state['archive'],'lookup':{'subject':'朱雀','place':'巳','reference':'乙'}}),call('liuren_compute',{'action':'source','source':{'id':'M_NATIVE_SOURCE','title':'应期方法全文','source_path':pointer['runtime']+'/methods/timing.md'}})])
 if stage==9:
  computed=[parsed(item) for item in values['_all']['liuren_compute']]
  assert any(v.get('value')==48 for v in computed),computed
  assert any(v.get('xingnian')=='壬子' for v in computed),computed
  assert any(v.get('growth')=='临官' and v.get('kin')=='子孙' for v in computed),computed
  assert any('竞争轮次' in v.get('quote','') for v in computed),computed
  assert content(values['liuren_materials'])
  checks.append('取数、年命、查表、来源装配及原书目录分支正常')
  p={'schema':'liuren-adjudication-input-v2','request_id':'20261107-host-chain','questions':[{'id':'Q1','text':'电脑维修能否完成？何时修好？费用多少？','subject':'维修事项','domain':'finance','stage':'合成测试','deadline':'未限定','success_criteria':'只验工具传输','alternatives':[],'tasks':['outcome','timing','quantity'],'task_basis':[{'task':t,'origin':'user_requested','request_quote':q,'reason':'测试原问明确要求'} for t,q in [('outcome','能否完成'),('timing','何时修好'),('quantity','费用多少')]]}],'chart':{'source':'合成工程验收所用程序盘','archive':state['archive']},'facts':[],'entities':[{'id':'S1','question_ids':['Q1'],'referent':'测试对象','branch':state['day_stem'],'mapping_basis':'合成接口取用，不构成专业结论'}],'observations':[],'method_materials':[],'method_modules':['positioning','liqi','structure','void','shensha-use','movement','finance','timing','quantity','quantity-sources','nianming'],'focus_issues':[],'unknowns':[]}
  return emit([call('liuren_adjudication_packet',{'packet':p})])
 if stage==10:
  v=parsed(values['liuren_adjudication_packet']);assert v.get('task_prompt'),v
  checks.append('真实packet按archive及已读模块装配并保存')
  return emit([call('task',{'description':'精简流程合成验收','subagent_type':'liuren-adjudicator','prompt':v['task_prompt']})])
 if stage==11:
  v=parsed(values['task']);assert v['status']=='completed' and v['schema']=='liuren-adjudication-receipt-v1',v
  state['receipt']=v;checks.append('真实slim子会话派发、完整读页及submit成功')
  return emit([call('task_result',{'task_id':v['task_id']})])
 if stage==12:
  v=parsed(values['task_result']);assert v['task_id']==state['receipt']['task_id'];assert v['next_call']['tool']=='liuren_materials',v
  checks.append('可见子会话ID及task_result领取与next_call正常')
  return emit([call('liuren_materials',{'action':'method','module':'report'})])
 if stage==13:
  assert 'LIUREN_WORKFLOW_CONTINUATION ' in content(values['liuren_materials'])
  return emit([call('liuren_adjudication_result',{'action':'deliver','task_id':state['receipt']['task_id']})])
 v=parsed(values['liuren_adjudication_result']);assert v['report_markdown']==report,v
 checks.append('report门禁、完整deliver及原文一致正常');state['finished']=True
 (OUT/'host-report.md').write_text(v['report_markdown'],'utf-8')
 return None,'LOCAL_CHAIN_COMPLETED'

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  raw=json.dumps({'object':'list','data':[{'id':'deepseek-flash','object':'model','owned_by':'local-test'}]}).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_POST(self):
  try:
   payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));calls,text=response(payload)
   delta={'role':'assistant',**({'tool_calls':[{**c,'index':i} for i,c in enumerate(calls)]} if calls else {'content':text})}
   chunk={'id':'local-flow-check','object':'chat.completion.chunk','created':int(time.time()),'model':'deepseek-flash','choices':[{'index':0,'delta':delta,'finish_reason':None}]}
   done={**chunk,'choices':[{'index':0,'delta':{},'finish_reason':'tool_calls' if calls else 'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}}
   raw=('data: '+json.dumps(chunk,ensure_ascii=False)+'\n\ndata: '+json.dumps(done)+'\n\ndata: [DONE]\n\n').encode()
   self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  except Exception as error:
   failures.append(traceback.format_exc());raw=json.dumps({'error':{'message':str(error),'type':'local_validation_failed'}}).encode();self.send_response(400);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  finally:
   (OUT/'progress.json').write_text(json.dumps({'state':state,'checks':checks,'requests':len(events),'failures':failures},ensure_ascii=False,indent=2),'utf-8')

relay=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=relay.serve_forever,daemon=True).start()
def remap(v):
 if isinstance(v,str):return v.replace(str(ROOT),str(project)).replace(ROOT.as_posix(),project.as_posix())
 if isinstance(v,list):return [remap(x) for x in v]
 if isinstance(v,dict):return {remap(k):remap(x) for k,x in v.items()}
 return v
config=remap(load(ROOT/'opencode.json'))
config['enabled_providers']=['deepseek'];config['provider']={'deepseek':{'npm':'@ai-sdk/openai-compatible','name':'Local scripted flow validator','options':{'baseURL':'http://127.0.0.1:'+str(relay.server_port)+'/v1','apiKey':'[REDACTED_CREDENTIAL]'},'models':{'deepseek-flash':{'name':'Local synthetic responses','tool_call':True,'limit':{'context':262144,'output':65536}}}}}
config.update(model='deepseek/deepseek-flash',small_model='deepseek/deepseek-flash',plugin=[wrapper.as_uri()])
config['agent']['liuren'].update(model='deepseek/deepseek-flash')
# Production permissions and prompts remain exactly as configured; only paths/provider are remapped.
assert config['agent']['liuren']['permission']==remap(load(ROOT/'opencode.json')['agent']['liuren']['permission'])
env=os.environ.copy()
for key in list(env):
 if key.startswith('OPENCODE_') or key in ['OPENAI_API_KEY','ANTHROPIC_API_KEY','DEEPSEEK_API_KEY']:env.pop(key)
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
 (base/name).mkdir(parents=True,exist_ok=True);env[key]=str(base/name)
cfg=base/'config/opencode/opencode.json';cfg.parent.mkdir(exist_ok=True);cfg.write_text(json.dumps(config,ensure_ascii=False),'utf-8')
env.update(OPENCODE_CONFIG=str(cfg),OPENCODE_CONFIG_DIR=str(cfg.parent),OPENCODE_LOG_DIR=str(base/'logs'))
for key in ['OPENCODE_DISABLE_PROJECT_CONFIG','OPENCODE_DISABLE_MODELS_FETCH','OPENCODE_DISABLE_AUTOUPDATE','OPENCODE_DISABLE_CLAUDE_CODE','OPENCODE_DISABLE_LSP_DOWNLOAD']:env[key]='true'
desktop=Path.home()/'AppData/Local/Programs/@opencode-aidesktop/OpenCode.exe'
server_js=OUT/'desktop-server.mjs'
shutil.copyfile(ROOT/'output/liuren-handoff-audit-20261106/desktop-server.mjs',server_js)
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close();url='http://127.0.0.1:'+str(port)
log=(OUT/'server.log').open('w',encoding='utf-8');server=None;code=-1;output='';started=time.monotonic()
try:
 server=subprocess.Popen([str(desktop),str(server_js),str(port)],cwd=project,env={**env,'ELECTRON_RUN_AS_NODE':'1'},stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 for attempt in range(100):
  try:urllib.request.urlopen(url+'/global/health',timeout=1).close();break
  except Exception:time.sleep(.15)
 paths=json.load(urllib.request.urlopen(url+'/path?directory='+urllib.parse.quote(str(project)),timeout=10))
 assert Path(paths['worktree']).resolve()==project.resolve(),paths
 (OUT/'host-path.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2),'utf-8')
 proc=subprocess.run([str(Path.home()/'scoop/apps/opencode/current/opencode.exe'),'run','--attach',url,'--dir',str(project),'--model','deepseek/deepseek-flash','--agent','liuren','--format','json',question],cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
 code=proc.returncode;output=proc.stdout
except subprocess.TimeoutExpired as error:
 output=error.stdout.decode('utf-8','replace') if isinstance(error.stdout,bytes) else error.stdout or '';failures.append('Host chain exceeded 180s')
except Exception:
 failures.append(traceback.format_exc())
finally:
 if server is not None:server.terminate();server.wait(timeout=10)
 log.close();relay.shutdown();relay.server_close()
(OUT/'host-cli.jsonl').write_text(output,'utf-8')
summary={'release':pointer['release'],'exitCode':code,'finished':state['finished'],'elapsedSeconds':round(time.monotonic()-started,2),'checks':checks,'events':events,'state':state,'failures':failures,'hostKind':'installed-desktop-server','productionPermissionsPreserved':True,'productionToolsUnmodified':True,'loopbackSyntheticResponses':True,'externalModelCalls':0,'websiteChanged':False,'childModelAndHighVerified':any(e['who']=='child' for e in events) and all(e['model']=='deepseek-flash' and e['reasoning_effort']=='high' for e in events if e['who']=='child'),'implementationSha256':{rel:sha(ROOT/rel) for rel in ['.opencode/plugins/liuren-adjudication.ts','.opencode/tools/liuren_chart.ts','.opencode/tools/liuren_materials.ts','tools/liuren-flow-control.mjs','tools/liuren-deterministic-io.mjs','.opencode/oh-my-opencode-slim.jsonc','opencode.json']}}
(OUT/'host-chain.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
if state['finished'] and not failures:
 (OUT/'current-wire.json').write_text(json.dumps({'exitCode':code,'realModelCalled':False,'scope':'Actual installed desktop host outbound schema with synthetic loopback responses; tools and permissions unchanged','requests':[{'tools':wire}],'implementationSha256':{rel:sha(ROOT/rel) for rel in ['.opencode/plugins/liuren-adjudication.ts','tools/liuren-flow-control.mjs','tools/liuren-adjudication-output.mjs','tools/liuren-compute-schema.mjs','.opencode/tools/liuren_materials.ts']}},ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:summary[k] for k in ['exitCode','finished','elapsedSeconds','checks','failures']},ensure_ascii=False),flush=True)
raise SystemExit(0 if state['finished'] and not failures else 1)
