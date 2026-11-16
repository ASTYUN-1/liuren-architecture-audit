"""Local additive archive-interface repair; preserve the frozen 26 release."""
from pathlib import Path
import copy,hashlib,json,os,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
OLD='20261107-slim-26';NEW='20261107-slim-27'
def load(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='')
def dump(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']==OLD
runtime=ROOT/'runtime/liuren'/NEW;assert not runtime.exists()
shutil.copytree(ROOT/p['runtime'],runtime)
for rel in ['opencode.json','AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md']:
 text=(ROOT/rel).read_text('utf-8-sig').replace(OLD,NEW)
 if rel=='docs/本机六壬高效执行.md':
  text+='\n归档引用可原样使用liuren_chart.archive（含可选raw_sha256），也可只给path/sha256。新会话workflow回执须有features.archive_metadata_passthrough=true，证明已加载本次兼容修复；旧进程仅返回工具契约25并不足以证明修复已载入。\n'
 if rel=='README.md':
  text+='\n27版修复归档引用在排盘与计算/裁决工具之间的字段兼容，详见[流程复验报告](output/liuren-slim-flow-validation-20261107/流程复验报告.md)。仍仅本机生效。\n'
 write(ROOT/rel,text)
m=load(runtime/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix())
m['computeInterface'].update(release=NEW,transportValidation='pending installed desktop host synthetic full-chain check',transportEvidence=OUT.relative_to(ROOT).as_posix()+'/current-wire.json')
m['toolUsage']['archiveMetadataPassthrough']=True
m['localInterfaceRepair']={'archiveOptionalMetadata':['raw_sha256'],'rawHashVerifiedAgainstAuthenticatedFile':True,'professionalLogicChanged':False}
policy=load(runtime/'references/shensha-policy.json');policy['release']=NEW;dump(runtime/'references/shensha-policy.json',policy)
guide=(runtime/'references/deterministic-tools.md').read_text('utf-8')
guide=guide.replace('主智能体的chart/lookup/life传原archive={path,sha256}','主智能体的chart/lookup/life可原样传liuren_chart.archive（含可选raw_sha256），或只传archive={path,sha256}；可选raw_sha256与已验证文件内的原始哈希核对')
write(runtime/'references/deterministic-tools.md',guide)
contract=load(runtime/'loader-contract.json');contract.update(release=NEW,parentRelease=OLD,authoringSource=m['authoringSource'])
for k in ['computeInterface','toolUsage']:contract[k]=copy.deepcopy(m[k])
contract['sourceHashes']={rel:sha(ROOT/rel) for rel in contract['sourceHashes']};dump(runtime/'loader-contract.json',contract)
m['files']={f.relative_to(runtime).as_posix():sha(f) for f in runtime.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(runtime/'manifest.json',m)
p.update(release=NEW,runtime='runtime/liuren/'+NEW,methodVersion=m['version'],previousRelease=OLD,backup=(OUT/'before-fix').relative_to(ROOT).as_posix(),authoringSource=m['authoringSource'])
for k in ['computeInterface','toolUsage','localInterfaceRepair']:p[k]=copy.deepcopy(m[k])
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['compatibleMethodRelease']=NEW;p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
tmp=ROOT/'.opencode/liuren-active.slim27.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
before=load(OUT/'before-fix-sha256.json')
dump(OUT/'local-fix.json',{'release':NEW,'previousRelease':OLD,'websiteChanged':False,'professionalLogicChanged':False,'before':before,'after':{rel:sha(ROOT/rel) for rel in before}})
print(NEW)
