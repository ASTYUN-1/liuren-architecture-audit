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

10版计算工具参数：calendar与expression已由原生工具schema展开；直接查询、computation_requests及裁决返回calculations使用同一字段约定。calendar必须给start/end、timezone="Asia/Shanghai"及day_boundary="civil-midnight"或"zi-hour"，后者是字符串。00:00换日选civil-midnight；23:00换日选zi-hour，口径须明确。不要用midnight、00:00或对象，也不要改成start_date/end_date。

如报参数错误，按字段路径与合法值更正一次；仍失败就记录具体计算缺口并保留已知判断，不继续猜格式，不手算公历冒充程序结果。正确计算也不代表应期轮次已被裁定。例子日期只示范结构，实际范围依本问确定。

最小日期调用：{"action":"calendar","calendar":{"start":"2024-01-15","end":"2024-02-05","timezone":"Asia/Shanghai","day_boundary":"civil-midnight"}}。
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
pointer['computeInterface']={'schema':'liuren-compute-interface-v1','release':NEW,'calendarSchema':'explicit native object with required timezone and day_boundary enum','expressionSchema':'native recursive AST','samePacketSchema':True,'modelCallsAdded':0,'externalModelValidation':False}
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
dump(RUN/'compute-interface-revision.json',{'release':NEW,'parent':OLD,'scope':'local-opencode','observedFailures':3,'cause':'calendar and calculation request schemas used unknown; errors omitted legal day_boundary values','engineAlgorithmModified':False,'methodBodiesChanged':False,'independentPredictiveValidationCount':0})
manifest=obj(RUN/'manifest.json');manifest.update(release=NEW,parentRelease=OLD,authoringSource=pointer['authoringSource'],revisionFile='compute-interface-revision.json',computeInterface=pointer['computeInterface'])
manifest['files']={p.relative_to(RUN).as_posix():sha(p) for p in sorted(RUN.rglob('*')) if p.is_file() and p.name!='manifest.json'}
manifest['version']=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest();dump(RUN/'manifest.json',manifest)
pointer['methodVersion']=manifest['version'];dump(LIVE/'.opencode/liuren-active.json',pointer)
dump(OUT/'candidate-manifest.json',{'release':NEW,'live':{p.relative_to(LIVE).as_posix():sha(p) for p in LIVE.rglob('*') if p.is_file()},'runtime':manifest['files'],'methodVersion':manifest['version']})
print(json.dumps({'release':NEW,'runtimeFiles':len(manifest['files']),'liveFiles':len(before['live']),'newFiles':len(before['newFiles'])}))
