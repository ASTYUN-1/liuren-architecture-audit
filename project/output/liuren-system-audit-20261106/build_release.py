from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];C=OUT/'candidate-runtime'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
B=read(OUT/'before-manifest.json');p=read(OUT/'before/.opencode/liuren-active.json');NEW=B['newRelease'];source=OUT.relative_to(ROOT).as_posix()
for rel,digest in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==digest,rel
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json']
cfg=read(ROOT/'.opencode/oh-my-opencode-slim.jsonc');a=cfg['agents']['liuren-adjudicator']
a['description']='大六壬关键类神独立裁决；接受当前中性文件路径凭据，逐页读取后提交结构化裁决。'
a['orchestratorPrompt']='仅在大六壬准备到可裁决后，先packet保存中性input-v2，再将task_prompt文件凭据原样给本任务；不传长JSON，不接开发或闲聊。'
a['prompt']=a['prompt'].replace('12版使用liuren_adjudication_submit','当前使用liuren_adjudication_submit')
dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',cfg)
shutil.copyfile(ROOT/'.opencode/skills/liuren/daliuren/SKILL.md',C/'entry.md')
q=C/'references/adjudicator-contract.md';t=q.read_text(encoding='utf-8-sig').replace('# 12版裁决交接契约','# 当前裁决交接契约').replace('13版结果交接：','结果交接：');q.write_text(t,encoding='utf-8')
policy=read(C/'references/shensha-policy.json');policy['release']=NEW;dump(C/'references/shensha-policy.json',policy)
newfile='tools/liuren-adjudication-schema.mjs'
loader=read(C/'loader-contract.json');loader.update(release=NEW,parentRelease=p['release'],authoringSource=source,adjudication=p['adjudication'])
loader['sourceHashes'][newfile]=sha(ROOT/newfile)
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(C/'loader-contract.json',loader)
m=read(C/'manifest.json');m.update(release=NEW,parentRelease=p['release'],authoringSource=source,status='active',adjudication=p['adjudication'])
preservation=read(C/m['preservationFile']);preservation['release']=NEW
for row in preservation['modules']:
 rel=row['active_file'];current=sha(C/rel);revision=row.get('current_revision')
 if (revision and revision.get('sha256')!=current) or (not revision and row['original_sha256']!=current):
  if revision:row.setdefault('revision_history',[]).append(revision)
  row['current_revision']={'authoring_source':source+'/candidate-runtime/'+rel,'sha256':current,'previous_active_source':B['parentRuntime']+'/'+rel,'previous_active_sha256':sha(ROOT/B['parentRuntime']/rel),'summary':'登记当前正文与17版继承关系；本轮实质修订、接口整理及空白变化见审查说明，不等于逐条专业回源。'}
dump(C/m['preservationFile'],preservation)
m['computeInterface'].update(release=NEW,transportEvidence=source+'/current-wire.json')
m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(C/'manifest.json',m)
p.update(release=NEW,previousRelease=B['parentRelease'],runtime='runtime/liuren/'+NEW,methodVersion=m['version'],backup=source+'/before',authoringSource=source)
p['computeInterface'].update(release=NEW,transportEvidence=source+'/current-wire.json');p['bookRetrieval']['compatibleMethodRelease']=NEW
p['workflowImplementation'][newfile]=sha(ROOT/newfile)
for rel in p['workflowImplementation']:p['workflowImplementation'][rel]=sha(ROOT/rel)
for rel in p['bookRetrieval']['files']:p['bookRetrieval']['files'][rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
dump(OUT/'candidate-active.json',p)
changed={rel:sha(ROOT/rel) for rel,digest in B['live'].items() if (ROOT/rel).is_file() and sha(ROOT/rel)!=digest}
changed[newfile]=sha(ROOT/newfile)
dump(OUT/'candidate-manifest.json',{'release':NEW,'runtime':{f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file()},'live':changed,'activeSha256':sha(OUT/'candidate-active.json')})
print(json.dumps({'release':NEW,'changedLiveFiles':len(changed),'runtimeFiles':len(m['files'])+1}))
