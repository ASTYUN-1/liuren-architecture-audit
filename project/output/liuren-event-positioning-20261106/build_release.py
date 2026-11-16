"""Prepare live entrypoints and a hash-bound immutable event-positioning release."""
from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];C=OUT/'candidate-runtime'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');NEW=B['newRelease'];OLD=B['parentRelease']
RULE='本版事件定位：先保留原问并确定核心事件、实际当事对象与目标，再实读相应分类占。考试日干为考生，疾病日干为患者；无论谁代问，不以代问者为日干后由六亲递推替换当事人。其他占类按事件专项对待轴，例如婚配干男支女、攻守干攻支守、产时干儿支母；四课不按人数分席。亲属异法仅留来源研究，不覆盖本机普通单事规则。每问domain必填，考试/疾病填actor_entity_id引用日干考生/患者；先核对象再裁作用。漏读专项会在packet/派发前拦截，已读同版全文复用；完整定位与分类占自动随文件交裁决者，不增加模型轮次。'
# Back up the last discovered main-agent prompt entry before touching it.
for rel in ['opencode.json']:
 if rel not in B['live']:
  f=ROOT/rel;t=OUT/'before'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,t);B['live'][rel]=sha(f)
dump(OUT/'before-manifest.json',B)
for rel in B['runtime']:assert sha(ROOT/B['parentRuntime']/rel)==B['runtime'][rel],rel
for name in ['daliuren','liuren-cases','liuren-extract']:
 f=ROOT/'.opencode/skills/liuren'/name/'SKILL.md';s=(OUT/'before/.opencode/skills/liuren'/name/'SKILL.md').read_text('utf-8').replace(OLD,NEW)
 if name=='daliuren':
  a,b=s.split('## 实际专业主线',1);s=a+RULE+'\n\n## 实际专业主线'+b
 f.write_text(s,encoding='utf-8')
 if name=='daliuren':(C/'entry.md').write_text(s,encoding='utf-8')
op=read(OUT/'before/opencode.json');op['agent']['liuren']['prompt']=RULE+'\n\n'+op['agent']['liuren']['prompt'];dump(ROOT/'opencode.json',op)
slim=read(OUT/'before/.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=(C/'references/adjudicator-prompt.md').read_text('utf-8');dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',slim)
for rel in ['README.md','目录总索引.md','AGENTS.md','docs/本机六壬完整研判流程.md','docs/本机六壬高效执行.md']:
 s=(OUT/'before'/rel).read_text('utf-8').replace(OLD,NEW)
 if rel=='AGENTS.md':s+='\n\n'+RULE+'\n'
 else:s+='\n\n'+RULE+'\n'
 (ROOT/rel).write_text(s,encoding='utf-8')
route=read(C/'reading-route.json');route['domainReadRequired']=True;route['eventRolePolicy']='references/event-positioning-policy.json';dump(C/'reading-route.json',route)
policy={'enabled':True,'schema':'liuren-event-positioning-v1','actorAsDayStem':['exam','illness'],'domainReadRequired':True,'fullDomainHandoff':True,'source':'explicit-user-instruction'}
loader=read(C/'loader-contract.json');loader.update(release=NEW,parentRelease=OLD,authoringSource='output/liuren-event-positioning-20261106',eventPositioning=policy)
loader['sourceHashes']['tools/liuren-event-positioning.mjs']=sha(ROOT/'tools/liuren-event-positioning.mjs')
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(C/'loader-contract.json',loader)
dump(C/'event-positioning-revision.json',{'release':NEW,'parentRelease':OLD,'authority':'user event-centered role policy','problems':['domain reads were not enforced by preparation coverage','exam omitted an explicit actor binding','illness allowed family-role reference switching','adjudicator received observations without automatic complete domain rules'],'changes':['event role policy in shared methods and all 16 domains','program checks domain reading, actor references and day stem for exam/illness','full positioning and selected domains accompany scoped file','completed adjudication cannot replace protected actor symbol'],'predictiveValidation':False,'externalModelCalled':False})
m=read(C/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource='output/liuren-event-positioning-20261106',status='active',eventPositioning=policy)
m['computeInterface'].update(release=NEW,transportEvidence='output/liuren-event-positioning-20261106/current-wire.json')
m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(C/'manifest.json',m)
p=read(OUT/'before/.opencode/liuren-active.json');p.update(release=NEW,previousRelease=OLD,runtime='runtime/liuren/'+NEW,methodVersion=m['version'],backup='output/liuren-event-positioning-20261106/before',authoringSource='output/liuren-event-positioning-20261106',eventPositioning=policy)
p['computeInterface'].update(release=NEW,transportEvidence='output/liuren-event-positioning-20261106/current-wire.json');p['bookRetrieval']['compatibleMethodRelease']=NEW;p['workflowImplementation']['tools/liuren-event-positioning.mjs']=sha(ROOT/'tools/liuren-event-positioning.mjs')
for rel in p['workflowImplementation']:p['workflowImplementation'][rel]=sha(ROOT/rel)
for rel in p['bookRetrieval']['files']:p['bookRetrieval']['files'][rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
dump(OUT/'candidate-active.json',p)
changed=[rel for rel in B['runtime'] if rel!='manifest.json' and sha(C/rel)!=B['runtime'][rel]]
dump(OUT/'revision-map.json',{'release':NEW,'changedRuntimeFiles':changed,'newRuntimeFiles':[f.relative_to(C).as_posix() for f in C.rglob('*') if f.is_file() and f.relative_to(C).as_posix() not in B['runtime']],'domainsReviewed':m['domains'],'newLiveFiles':['tools/liuren-event-positioning.mjs'],'unchangedHistoricalRuntime':True})
live={rel:sha(ROOT/rel) for rel in B['live'] if rel!='.opencode/liuren-active.json'};live['tools/liuren-event-positioning.mjs']=sha(ROOT/'tools/liuren-event-positioning.mjs')
dump(OUT/'candidate-manifest.json',{'release':NEW,'runtime':{f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file()},'live':live,'activeSha256':sha(OUT/'candidate-active.json')})
print(json.dumps({'candidate':NEW,'changedRuntimeFiles':len(changed),'domains':len(m['domains'])}))
