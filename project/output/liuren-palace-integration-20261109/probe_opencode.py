"""Capture actual OpenCode HTTP tool schemas at a loopback-only synthetic API."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import argparse,json,os,subprocess,threading,time,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--label',required=True);args=parser.parse_args()
base=OUT/'probe'/args.label
for name in ['config/opencode','data','cache','state','project']:(base/name).mkdir(parents=True,exist_ok=True)
captured=[]
project=Path(tempfile.mkdtemp(prefix='liuren-wire-probe-'))
def check_refs(schema):
 errors=[]
 def walk(node):
  if isinstance(node,dict):
   ref=node.get('$ref')
   if ref:
    cur=schema
    try:
     if ref=='#':pass
     elif ref.startswith('#/'):
      for key in ref[2:].split('/'):cur=cur[key.replace('~1','/').replace('~0','~')]
     else:raise KeyError(ref)
    except (KeyError,TypeError):errors.append(ref)
   for child in node.values():walk(child)
  elif isinstance(node,list):
   for child in node:walk(child)
 walk(schema);return errors
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  raw=json.dumps({'object':'list','data':[{'id':'schema-probe','object':'model','owned_by':'local'}]}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_POST(self):
  payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
  tools=[{'name':t['function']['name'],'parameters':t['function']['parameters']} for t in payload.get('tools',[])]
  errors=[{'tool':t['name'],'missing':check_refs(t['parameters'])} for t in tools if check_refs(t['parameters'])]
  captured.append({'path':self.path,'tools':tools,'referenceErrors':errors})
  if errors:
   msg="Invalid schema for function '"+errors[0]['tool']+"': Pointer '"+errors[0]['missing'][0].lstrip('#')+"' does not exist"
   raw=json.dumps({'error':{'message':msg,'type':'invalid_request_error','code':'invalid_schema'}}).encode()
   self.send_response(400);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
  if payload.get('stream'):
   chunk={'id':'local-schema-probe','object':'chat.completion.chunk','created':int(time.time()),'model':'schema-probe','choices':[{'index':0,'delta':{'role':'assistant','content':'Local schema check passed.'},'finish_reason':None}]}
   done={**chunk,'choices':[{'index':0,'delta':{},'finish_reason':'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}}
   raw=('data: '+json.dumps(chunk)+'\n\ndata: '+json.dumps(done)+'\n\ndata: [DONE]\n\n').encode()
   self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  else:
   raw=json.dumps({'id':'local-schema-probe','object':'chat.completion','created':int(time.time()),'model':'schema-probe','choices':[{'index':0,'message':{'role':'assistant','content':'Local schema check passed.'},'finish_reason':'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}}).encode()
   self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
config={'$schema':'https://opencode.ai/config.json','enabled_providers':['local-schema'],
 'provider':{'local-schema':{'npm':'@ai-sdk/openai-compatible','name':'Local schema probe','options':{'baseURL':'http://127.0.0.1:'+str(server.server_port)+'/v1','apiKey':'[REDACTED_CREDENTIAL]'},'models':{'schema-probe':{'name':'Schema probe','tool_call':True,'limit':{'context':131072,'output':1024}}}}},
 'model':'local-schema/schema-probe','small_model':'local-schema/schema-probe','plugin':[(ROOT/'.opencode/plugins/liuren-adjudication.ts').as_uri()],
 'agent':{'liuren':{'mode':'primary','prompt':'This is a synthetic local schema check. Reply with a short acknowledgment.','permission':{'*':'deny','liuren_compute':'allow','liuren_adjudication_packet':'allow','liuren_adjudication_read':'allow'}}}}
env=os.environ.copy()
for key in list(env):
 if key.startswith('OPENCODE_') or key in ['OPENAI_API_KEY','ANTHROPIC_API_KEY','DEEPSEEK_API_KEY']:env.pop(key)
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:env[key]=str(base/name)
env['OPENCODE_CONFIG_DIR']=str(base/'config/opencode');env['OPENCODE_CONFIG_CONTENT']=json.dumps(config)
for key in ['OPENCODE_DISABLE_PROJECT_CONFIG','OPENCODE_DISABLE_MODELS_FETCH','OPENCODE_DISABLE_AUTOUPDATE','OPENCODE_DISABLE_DEFAULT_PLUGINS','OPENCODE_DISABLE_CLAUDE_CODE','OPENCODE_DISABLE_LSP_DOWNLOAD']:env[key]='true'
exe=Path.home()/'scoop/apps/opencode/current/opencode.exe'
cmd=[str(exe),'run','--dir',str(project),'--model','local-schema/schema-probe','--agent','liuren','--format','json','--title','Local synthetic schema check','Check the local tool schema only.']
try:
 proc=subprocess.run(cmd,env=env,cwd=project,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=45)
 output=proc.stdout;code=proc.returncode
except subprocess.TimeoutExpired as e:output=(e.stdout or b'').decode('utf-8','replace') if isinstance(e.stdout,bytes) else (e.stdout or '');code=-1
finally:server.shutdown();server.server_close()
(OUT/(args.label+'-cli.log')).write_text(output,encoding='utf-8')
result={'exitCode':code,'requests':captured,'loopbackOnlyProvider':True,'realModelCalled':False,
 'implementationSha256':{rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in ['tools/liuren-compute-schema.mjs','.opencode/plugins/liuren-adjudication.ts']}}
(OUT/(args.label+'-wire.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exitCode':code,'requests':len(captured),'toolNames':[t['name'] for r in captured for t in r['tools']],'referenceErrors':[e for r in captured for e in r['referenceErrors']]},ensure_ascii=False))
