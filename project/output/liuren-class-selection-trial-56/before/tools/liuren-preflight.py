"""Local execution readiness; research-library health is reported separately."""
from pathlib import Path
import argparse,fnmatch,hashlib,json,shutil,subprocess,sys,urllib.parse,urllib.request
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads(path.read_text('utf-8-sig'))
def check(root=ROOT,host_url=None,full_doctor=False):
 required=[];optional=[]
 def record(name,ok,detail=None):required.append({'name':name,'ok':bool(ok),**({'detail':detail} if detail is not None else {})})
 try:
  pointer=load(root/'.opencode/liuren-active.json');runtime=root/pointer['runtime'];manifest=load(runtime/'manifest.json');contract=load(runtime/'loader-contract.json')
  record('active release',pointer['release']==manifest['release']==contract['release'] and pointer['methodVersion']==manifest['version'],pointer['release'])
  record('manifest identity',hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest()==manifest['version'])
  for name,base,values in [('runtime files',runtime,manifest['files']),('loaded implementation sources',root,contract['sourceHashes']),('active tool sources',root,pointer['workflowImplementation']),('skill entries',root/'.opencode/skills',pointer['files'])]:
   mismatches=[]
   for rel,expected in values.items():
    path=base/rel
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:mismatches.append(rel)
   record(name,not mismatches,mismatches)
  overrides=[]
  for key,item in pointer.get('localModuleOverrides',{}).items():
   path=(root/item['file']).resolve()
   if key!='daliuren-paipan' or key not in manifest['modules'] or not path.is_relative_to(root.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:overrides.append(key)
  record('local operation overrides',not overrides,overrides)
  mismatches=[f for f,h in pointer.get('bookRetrieval',{}).get('files',{}).items() if not (root/f).is_file() or hashlib.sha256((root/f).read_bytes()).hexdigest()!=h]
  record('active book retrieval files',not mismatches,mismatches)
  config=load(root/'opencode.json');slim=load(root/'.opencode/oh-my-opencode-slim.jsonc')
  record('default liuren agent',config.get('default_agent')=='liuren')
  permissions=config['agent']['liuren']['permission']
  tools=['liuren_chart','liuren_materials','liuren_tool_help','liuren_compute','liuren_adjudication_packet','liuren_adjudication_result','task_result']
  record('main tool permissions',all(permissions.get(t)=='allow' for t in tools) and permissions.get('task',{}).get('liuren-adjudicator')=='allow')
  read_rules=permissions.get('read',{});missing_read=[]
  candidates=[(runtime/rel).as_posix() for rel in ['methods/positioning.md','domains/finance.md','references/judgment-core.md','details/risk.md','procedures/common.md','entry.md']]+[(root/rel).as_posix() for rel in ['README.md','目录总索引.md']]
  for candidate in candidates:
   decision='deny'
   for pattern,value in read_rules.items():
    if fnmatch.fnmatchcase(candidate,pattern):decision=value
   if decision!='allow':missing_read.append(candidate)
  record('active runtime read permissions',not missing_read,missing_read)
  adjudicator=slim['agents']['liuren-adjudicator'];p=adjudicator['permission']
  model='deepseek/deepseek-flash'
  record('primary model independently configured',bool(config['agent']['liuren'].get('model') or config.get('model')))
  record('adjudicator model and tools',adjudicator['model']==model==pointer['adjudication']['model'] and adjudicator['variant']=='high' and all(p.get(t)=='allow' for t in ['liuren_adjudication_read','liuren_adjudication_submit','liuren_compute','liuren_tool_help']))
  record('compact handoff enabled',pointer.get('compactHandoff',{}).get('enabled') is True)
  record('durable flow enabled',pointer.get('flowControl',{}).get('enabled') is True)
  if pointer.get('consistencyAudit',{}).get('enabled'):
   record('consistency audit child permission',p.get('liuren_adjudication_audit')=='allow')
   record('consistency audit implementation and bounded review','tools/liuren-consistency-audit.mjs' in pointer['workflowImplementation'] and pointer['consistencyAudit'].get('maxRechecks')==1)
  budget=pointer.get('adjudication',{}).get('maxOutputTokens')
  record('explicit DeepSeek adjudicator output budget',budget==393216,budget)
  package=Path.home()/'.cache/opencode/packages/oh-my-opencode-slim/node_modules/oh-my-opencode-slim/package.json'
  expected=pointer['adjudication']['installedPluginVersion'];installed=load(package)['version'] if package.is_file() else None
  record('pinned slim plugin',installed==expected and 'oh-my-opencode-slim@'+expected in config.get('plugin',[]),{'expected':expected,'installed':installed})
  record('project SDK dependency',(root/'.opencode/node_modules/@opencode-ai/plugin/package.json').is_file())
  for executable in ['python','node']:record(executable+' executable',bool(shutil.which(executable)))
  policy=load(runtime/'references/shensha-policy.json');record('adopted shensha release',policy['release']==pointer['release'])
  retrieval=pointer.get('bookRetrieval',{})
  record('book index',bool(retrieval.get('index')) and (root/retrieval['index']).is_file())
 except (OSError,ValueError,KeyError) as error:record('configuration readable',False,type(error).__name__+': '+str(error))
 if host_url:
  parsed=urllib.parse.urlsplit(host_url)
  if parsed.scheme!='http' or parsed.hostname not in ['127.0.0.1','localhost','::1'] or parsed.username or parsed.password:raise ValueError('host-url必须是无凭据的本机HTTP回环地址')
  query='?directory='+urllib.parse.quote(str(root))
  for endpoint in ['/global/health','/agent','/experimental/tool/ids','/mcp']:
   try:
    with urllib.request.urlopen(host_url.rstrip('/')+endpoint+query,timeout=45) as response:value=json.load(response)
    if endpoint=='/agent':record('live adjudicator registration',any(a.get('name')=='liuren-adjudicator' for a in value))
    elif endpoint=='/experimental/tool/ids':record('live workflow tools',all(t in value for t in ['liuren_chart','liuren_materials','liuren_tool_help','liuren_compute','liuren_adjudication_packet','liuren_adjudication_read','liuren_adjudication_submit','liuren_adjudication_result','task','task_result']+(['liuren_adjudication_audit'] if pointer.get('consistencyAudit',{}).get('enabled') else [])))
    elif endpoint=='/mcp':optional.extend({'name':'MCP '+k,'ok':v.get('status')=='connected','status':v.get('status')} for k,v in value.items())
    else:record('live desktop host',value.get('healthy',False))
   except Exception as error:(optional if endpoint=='/mcp' else required).append({'name':'live '+endpoint,'ok':False,'errorType':type(error).__name__})
 if full_doctor:
  from liuren_workflow import doctor
  result=doctor(root);optional.append({'name':'full historical/research doctor','ok':result['ok'],'errors':result['errors']})
 return {'schema':'liuren-local-preflight-v1','ready':all(r['ok'] for r in required),'required':required,'auxiliary':optional,'modelCalls':0,'servicesStarted':0,'scope':'本机执行与加载；辅助MCP/研究库单列，不证明专业或预测效果','next':'重启后首次在liuren调用liuren_tool_help(topic=workflow,domains=[本问占类])，确认execution_health.ready；其后按next_call执行。'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--host-url');parser.add_argument('--doctor',action='store_true');parser.add_argument('--json',action='store_true');args=parser.parse_args();value=check(host_url=args.host_url,full_doctor=args.doctor)
 if args.json:print(json.dumps(value,ensure_ascii=False,indent=2))
 else:
  print('本机六壬执行检查：'+('通过' if value['ready'] else '未通过'))
  for item in value['required']:print(('OK   ' if item['ok'] else 'FAIL ')+item['name']+((': '+json.dumps(item['detail'],ensure_ascii=False)) if item.get('detail') else ''))
  for item in value['auxiliary']:print(('AUX OK   ' if item['ok'] else 'AUX WARN ')+item['name'])
  print(value['next'])
 return 0 if value['ready'] else 1
if __name__=='__main__':raise SystemExit(main())
