"""Publish local-only output-budget and stalled-result repair, preserving release 27."""
from pathlib import Path
import copy,hashlib,json,os,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
OLD='20261107-slim-27';NEW='20261107-slim-28'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,t):p.write_text(t,encoding='utf-8',newline='')
def dump(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']==OLD
runtime=ROOT/'runtime/liuren'/NEW;assert not runtime.exists()
shutil.copytree(ROOT/p['runtime'],runtime)
note='28版：裁决请求不再传max_tokens/maxOutputTokens，取消项目65536覆盖及宿主继承额度；服务端仍有模型/上下文上限，high保留。task_result无公开末消息时，用liuren_adjudication_result(action="read",task_id=原子会话ID)领取已存结果或失败。仅完整读完且finish=length、无公开报告时，按next_call用recover在同一子会话续写提交一次；不新建裁决、不把reasoning转成正文。仍无正文则明确未完成，不循环领取/重派。重启本机OpenCode后，workflow的features.provider_default_output_budget与bounded_same_session_recovery均须为true。'
for rel in ['opencode.json','AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md']:
 t=(ROOT/rel).read_text('utf-8-sig').replace(OLD,NEW)
 if rel in ['AGENTS.md','docs/本机六壬高效执行.md']:t+='\n'+note+'\n'
 if rel=='README.md':t+='\n本机28版取消项目裁决输出额度，增加原子会话正文恢复；说明见[本次修复](output/liuren-stalled-child-repair-20261107/修复说明.md)。网站未发布。\n'
 write(ROOT/rel,t)
guide=runtime/'references/deterministic-tools.md';write(guide,guide.read_text('utf-8')+'\n'+note+'\n')
policy=load(runtime/'references/shensha-policy.json');policy['release']=NEW;dump(runtime/'references/shensha-policy.json',policy)
m=load(runtime/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix())
m['adjudication']={**p['adjudication'],**m['adjudication']}
m['flowControl']={**p['flowControl'],**m['flowControl']}
m['adjudication'].pop('maxOutputTokens',None);m['adjudication']['outputBudgetPolicy']='omit-client-output-budget; provider-enforces-model-limits'
m['flowControl']['sameSessionReportRecovery']='once; only fully-read empty report after finish=length; no re-adjudication'
m['outputRecovery']={'scope':'local-opencode','noClientTokenCap':True,'highRetained':True,'sameChildOnly':True,'maxContinuations':1,'privateReasoningUsedAsReport':False,'validation':'pending current host checks','evidence':OUT.relative_to(ROOT).as_posix()+'/validation-summary.json'}
contract=load(runtime/'loader-contract.json');contract.update(release=NEW,parentRelease=OLD,authoringSource=m['authoringSource'])
for k in ['adjudication','flowControl','outputRecovery']:contract[k]=copy.deepcopy(m[k])
contract['sourceHashes']={rel:sha(ROOT/rel) for rel in contract['sourceHashes']};dump(runtime/'loader-contract.json',contract)
m['files']={f.relative_to(runtime).as_posix():sha(f) for f in runtime.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(runtime/'manifest.json',m)
p.update(release=NEW,runtime='runtime/liuren/'+NEW,methodVersion=m['version'],previousRelease=OLD,backup=(OUT/'before-fix').relative_to(ROOT).as_posix(),authoringSource=m['authoringSource'])
for k in ['adjudication','flowControl','outputRecovery']:p[k]=copy.deepcopy(m[k])
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['compatibleMethodRelease']=NEW;p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
tmp=ROOT/'.opencode/liuren-active.slim28.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
before={f.relative_to(OUT/'before-fix').as_posix():sha(f) for f in (OUT/'before-fix').rglob('*') if f.is_file()}
dump(OUT/'local-fix.json',{'release':NEW,'previousRelease':OLD,'websiteChanged':False,'before':before,'after':{rel:sha(ROOT/rel) for rel in before}})
print(NEW)
