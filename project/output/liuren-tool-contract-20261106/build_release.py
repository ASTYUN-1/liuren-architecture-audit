from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];C=OUT/'candidate-runtime'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
B=read(OUT/'before-manifest.json');p=read(OUT/'before/.opencode/liuren-active.json');OLD=B['parentRelease'];NEW=B['newRelease'];source=OUT.relative_to(ROOT).as_posix()
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json']
for rel,digest in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==digest,rel
for rel in ['opencode.json','.opencode/oh-my-opencode-slim.jsonc','docs/本机六壬高效执行.md','README.md','目录总索引.md']+[str(f.relative_to(ROOT)) for f in (ROOT/'.opencode/skills/liuren').rglob('SKILL.md')]:
 f=ROOT/rel;f.write_text(f.read_text('utf-8-sig').replace(OLD,NEW),'utf-8')
shutil.copyfile(ROOT/'.opencode/skills/liuren/daliuren/SKILL.md',C/'entry.md')
q=C/'references/shensha-policy.json';v=read(q);v['release']=NEW;dump(q,v)
loader=read(C/'loader-contract.json');loader.update(release=NEW,parentRelease=OLD,authoringSource=source)
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(C/'loader-contract.json',loader)
m=read(C/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=source)
if 'computeInterface' in m:m['computeInterface']['release']=NEW
pres=read(C/m['preservationFile']);pres['release']=NEW
for row in pres['modules']:
 rel=row['active_file'];digest=sha(C/rel)
 if digest!=sha(ROOT/B['parentRuntime']/rel):
  if row.get('current_revision'):row.setdefault('revision_history',[]).append(row['current_revision'])
  row['current_revision']={'authoring_source':source+'/candidate-runtime/'+rel,'sha256':digest,'previous_active_source':B['parentRuntime']+'/'+rel,'previous_active_sha256':sha(ROOT/B['parentRuntime']/rel),'summary':'仅明确工具参数、可直接交接引用及失败恢复用法；不改专业判断规则。'}
dump(C/m['preservationFile'],pres)
m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(C/'manifest.json',m)
p.update(release=NEW,previousRelease=OLD,runtime='runtime/liuren/'+NEW,methodVersion=m['version'],backup=source+'/before',authoringSource=source)
p['computeInterface']['release']=NEW;p['bookRetrieval']['compatibleMethodRelease']=NEW
for group in [p['workflowImplementation'],p['bookRetrieval']['files']]:
 for rel in group:group[rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
p['toolHandoff']={'sourcePaths':'workspace relative or scoped absolute, normalized by program','citationTransport':'method and complete book_search hits return reusable handoff','questionDomain':'required on every native packet question','modelCallsAdded':0,'guide':'docs/本机六壬高效执行.md'}
dump(OUT/'candidate-active.json',p)
dump(OUT/'candidate-manifest.json',{'release':NEW,'runtime':{f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file()},'live':{rel:sha(ROOT/rel) for rel,digest in B['live'].items() if sha(ROOT/rel)!=digest},'activeSha256':sha(OUT/'candidate-active.json')})
print(json.dumps({'release':NEW,'runtimeFiles':len(m['files'])+1}))
