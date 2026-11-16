from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
B=load(OUT/'before.json');p=load(ROOT/'.opencode/liuren-active.json')
OLD=B['release'];NEW='20261106-tool-continuation-23';source=OUT.relative_to(ROOT).as_posix()
assert p['release']==OLD
for rel,h in B['runtimeFiles'].items():assert sha(ROOT/B['runtime']/rel)==h,rel
C=ROOT/'runtime/liuren'/NEW;assert not C.exists();shutil.copytree(ROOT/B['runtime'],C)
guide='工具回执按当前阶段给出可执行next_call：领取后缺report先用liuren_materials读取，读取回执再指向deliver；已读不重读，不移除交付前校验。课盘程序事实用liuren_compute，完整引擎神煞用liuren_materials(action=shensha,path=archive.path)，不为读取归档而改用通用read。'
for rel in ['AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md']+[f.relative_to(ROOT).as_posix() for f in (ROOT/'.opencode/skills/liuren').rglob('SKILL.md')]:
    f=ROOT/rel;t=f.read_text('utf-8-sig').replace(OLD,NEW)
    if rel in ['AGENTS.md','docs/本机六壬高效执行.md']:t+='\n\n23版工具接续：'+guide+'\n'
    f.write_text(t,'utf-8')
config=load(ROOT/'opencode.json')
config=json.loads(json.dumps(config,ensure_ascii=False).replace(OLD,NEW))
config['agent']['liuren']['prompt']+=' '+guide
dump(ROOT/'opencode.json',config)
shutil.copyfile(ROOT/'.opencode/skills/liuren/daliuren/SKILL.md',C/'entry.md')
for rel in ['methods/workflow-contract.md','references/deterministic-tools.md']:
    f=C/rel;t=f.read_text('utf-8-sig').replace(OLD,NEW)
    if rel.endswith('deterministic-tools.md'):
        t=t.replace('随后liuren_adjudication_result(action="deliver",task_id=同ID)','按回执next_call先补缺读report，再liuren_adjudication_result(action="deliver",task_id=同ID)')
    f.write_text(t+'\n\n23版工具接续：'+guide+'\n','utf-8')
policy=load(C/'references/shensha-policy.json');policy['release']=NEW;dump(C/'references/shensha-policy.json',policy)
p.update(release=NEW,previousRelease=OLD,runtime=C.relative_to(ROOT).as_posix(),backup=source+'/before',authoringSource=source)
p['toolUsage'].update(continuation='state-aware claim/read/report/deliver next_call',archiveAccess='compute chart or materials shensha; tools use current session directory',professionalRulesChanged=False)
p['computeInterface'].update(release=NEW,transportEvidence=source+'/current-wire.json',transportValidation='real DeepSeek desktop run; inspect evidence before claiming success')
p['bookRetrieval']['compatibleMethodRelease']=NEW
for group in [p['workflowImplementation'],p['bookRetrieval']['files']]:
    for rel in group:group[rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
loader=load(C/'loader-contract.json');loader.update(release=NEW,parentRelease=OLD,authoringSource=source,toolUsage=p['toolUsage'])
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(C/'loader-contract.json',loader)
m=load(C/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=source,computeInterface=p['computeInterface'],toolUsage=p['toolUsage'])
pres=load(C/m['preservationFile']);pres['release']=NEW
for row in pres['modules']:
    rel=row['active_file']
    if sha(C/rel)!=sha(ROOT/B['runtime']/rel):
        if row.get('current_revision'):row.setdefault('revision_history',[]).append(row['current_revision'])
        row['current_revision']={'authoring_source':p['runtime']+'/'+rel,'sha256':sha(C/rel),'previous_active_source':B['runtime']+'/'+rel,'previous_active_sha256':sha(ROOT/B['runtime']/rel),'summary':'修正工具接续提示；未改专业规则。'}
dump(C/m['preservationFile'],pres)
m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(C/'manifest.json',m);p['methodVersion']=m['version']
tmp=ROOT/'.opencode/liuren-active.json.continuation-installing';assert not tmp.exists();dump(tmp,p);tmp.replace(ROOT/'.opencode/liuren-active.json')
for rel,h in B['runtimeFiles'].items():assert sha(ROOT/B['runtime']/rel)==h,rel
dump(OUT/'activation.json',{'release':NEW,'previousRelease':OLD,'oldRuntimeUnchanged':True,'professionalRulesChanged':False,'realModelVerification':'pending'})
print(NEW)
