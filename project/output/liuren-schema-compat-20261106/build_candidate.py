from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
LIVE=OUT/'candidate-live';RUN=OUT/'candidate-runtime'
def read(p):return p.read_text('utf-8-sig')
def obj(p):return json.loads(read(p))
def write(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='\n')
def dump(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=obj(OUT/'before-manifest.json');OLD=before['parentRelease'];NEW=before['newRelease']
for rel in before['runtime']:
 dst=RUN/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/before['parentRuntime']/rel,dst)
for rel in [*before['live'],*before['newFiles']]:
 dst=LIVE/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
def old(rel):return read(OUT/'before'/rel)
def effective(rel):return LIVE/rel if (LIVE/rel).is_file() else ROOT/rel
notice='''

11版工具注册兼容修复：OpenCode 1.18.29转换工具参数时不保留根部$defs，发布给模型的算式节点因此改为不含$ref的定义。节点格式和既有计算请求不变，args成员仍按value/table/op三类节点嵌套，由执行程序逐层严格检查。calendar的必填字段和换日枚举保持明确；不恢复无结构的整个expression或calendar，不放松算式、日期与裁决结果核验。

本机OpenCode经回环模拟接口已验证实际发送的三个工具定义均无引用依赖；这只证明工具注册与请求兼容，不代表真实外部模型推断效果。主子分工、文件交接和应期取数专法义务继续执行。
'''
write(RUN/'entry.md',read(RUN/'entry.md').replace(OLD,NEW)+notice)
write(RUN/'references/deterministic-tools.md',read(RUN/'references/deterministic-tools.md')+notice)
prompt=read(RUN/'references/adjudicator-prompt.md')+notice
write(RUN/'references/adjudicator-prompt.md',prompt)
for name in ['daliuren','liuren-cases','liuren-extract']:
 rel='.opencode/skills/liuren/'+name+'/SKILL.md'
 write(LIVE/rel,read(RUN/'entry.md') if name=='daliuren' else old(rel).replace(OLD,NEW))
for rel in ['README.md','AGENTS.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机六壬高效执行.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬资料检索范围.md']:
 write(LIVE/rel,old(rel).replace(OLD,NEW)+(notice if rel=='docs/本机六壬高效执行.md' else ''))
cfg=json.loads(old('opencode.json').replace(OLD,NEW));cfg['agent']['liuren']['prompt']+=notice
dump(LIVE/'opencode.json',cfg)
slim=json.loads(old('.opencode/oh-my-opencode-slim.jsonc'));slim['agents']['liuren-adjudicator']['prompt']=prompt
dump(LIVE/'.opencode/oh-my-opencode-slim.jsonc',slim)
pointer=json.loads(old('.opencode/liuren-active.json'))
pointer.update(release=NEW,runtime='runtime/liuren/'+NEW,previousRelease=OLD,backup=OUT.relative_to(ROOT).as_posix()+'/before',authoringSource=OUT.relative_to(ROOT).as_posix())
pointer['computeInterface'].update(release=NEW,expressionSchema='reference-free published nodes; strict recursive execution validation',publishedReferences=0,transportValidation='OpenCode 1.18.29 to loopback-only mock API; no real model',transportEvidence=OUT.relative_to(ROOT).as_posix()+'/fixed-wire.json')
pointer['workflowImplementation']['tools/liuren-compute-schema.mjs']=sha(LIVE/'tools/liuren-compute-schema.mjs')
for rel in pointer['workflowImplementation']:pointer['workflowImplementation'][rel]=sha(effective(rel))
for key in pointer['files']:pointer['files'][key]=sha(LIVE/'.opencode/skills'/key)
retrieval=pointer['bookRetrieval'];retrieval['compatibleMethodRelease']=NEW
for rel in retrieval['files']:retrieval['files'][rel]=sha(effective(rel))
loader=obj(RUN/'loader-contract.json');loader.update(release=NEW,authoringSource=pointer['authoringSource'],computeInterface=pointer['computeInterface'])
for rel in [*loader['sourceHashes'],*pointer['workflowImplementation']]:loader['sourceHashes'][rel]=sha(effective(rel))
dump(RUN/'loader-contract.json',loader)
for rel in ['reading-route.json']:
 write(RUN/rel,read(RUN/rel).replace(OLD,NEW))
sp=obj(RUN/'references/shensha-policy.json');sp['release']=NEW;dump(RUN/'references/shensha-policy.json',sp)
dump(RUN/'schema-compat-revision.json',{'release':NEW,'parent':OLD,'scope':'local-opencode','cause':'recursive schema refs survived while root $defs was lost in OpenCode outbound tool conversion','fix':'reference-free wire contract; recursive runtime validation retained','realCliTransportVerified':True,'realModelCalled':False,'engineAlgorithmModified':False,'methodBodiesChanged':False,'independentPredictiveValidationCount':0})
manifest=obj(RUN/'manifest.json');manifest.update(release=NEW,parentRelease=OLD,authoringSource=pointer['authoringSource'],revisionFile='schema-compat-revision.json',computeInterface=pointer['computeInterface'])
manifest['files']={p.relative_to(RUN).as_posix():sha(p) for p in sorted(RUN.rglob('*')) if p.is_file() and p.name!='manifest.json'}
manifest['version']=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest();dump(RUN/'manifest.json',manifest)
pointer['methodVersion']=manifest['version'];dump(LIVE/'.opencode/liuren-active.json',pointer)
dump(OUT/'candidate-manifest.json',{'release':NEW,'live':{p.relative_to(LIVE).as_posix():sha(p) for p in LIVE.rglob('*') if p.is_file()},'runtime':manifest['files'],'methodVersion':manifest['version']})
print(json.dumps({'release':NEW,'runtimeFiles':len(manifest['files']),'liveFiles':len(before['live']),'newFiles':len(before['newFiles'])}))
