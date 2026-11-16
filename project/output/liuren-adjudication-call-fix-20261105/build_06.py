"""05 -> 06: preserve explanatory symbols, without another model call."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CAND=HERE/'candidate'
OLD='20261105-subagent-adjudication-05';NEW='20261105-subagent-adjudication-06'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def j(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def save(p,x):write(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
oldplan=j(HERE/'switch-plan.json');assert oldplan['release']==OLD
assert j(ROOT/'.opencode/liuren-active.json')['release']==OLD
save(HERE/'file-handoff-05-switch-plan.json',oldplan)
save(HERE/'file-handoff-05-smoke-host.json',j(HERE/'smoke-host.json'))
old=ROOT/'runtime/liuren'/OLD;new=CAND/'runtime/liuren'/NEW;assert not new.exists()
m=j(old/'manifest.json')
for rel in [*m['files'],'manifest.json']:
    p=new/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/rel,p)
external=[r['path'] for r in oldplan['externalFiles']]
for rel in external:write(CAND/rel,(ROOT/rel).read_text('utf-8').replace(OLD,NEW))
write(CAND/'tools/liuren-adjudication-contract.mjs',(HERE/'source/liuren-adjudication-contract.mjs').read_text('utf-8'))
write(new/'entry.md',(CAND/'.opencode/skills/liuren/daliuren/SKILL.md').read_text('utf-8'))
policy=j(new/'references/shensha-policy.json');policy['release']=NEW;save(new/'references/shensha-policy.json',policy)
pointer=j(CAND/'.opencode/liuren-active.json');pointer['previousRelease']=OLD;pointer['backup']=HERE.relative_to(ROOT).as_posix()+'/before-06'
m['release']=NEW;m['parentRelease']=OLD
loader=j(new/'loader-contract.json');loader['release']=NEW;loader['parentRelease']=OLD
for rel in ['tools/liuren-adjudication-contract.mjs','tools/liuren-adjudication-files.mjs','.opencode/plugins/liuren-adjudication.ts','.opencode/oh-my-opencode-slim.jsonc']:
    h=sha((CAND/rel).read_bytes());loader['sourceHashes'][rel]=h;pointer['workflowImplementation'][rel]=h
save(new/'loader-contract.json',loader)
m['files']={p.relative_to(new).as_posix():sha(p.read_bytes()) for p in sorted(new.rglob('*')) if p.is_file() and p.name!='manifest.json'}
m['version']=sha(json.dumps(m['files'],sort_keys=True).encode());save(new/'manifest.json',m);pointer['methodVersion']=m['version']
for name in pointer['activeSkillNames']:pointer['files'][f'liuren/{name}/SKILL.md']=sha((CAND/f'.opencode/skills/liuren/{name}/SKILL.md').read_bytes())
save(CAND/'.opencode/liuren-active.json',pointer)
save(HERE/'switch-plan.json',{'release':NEW,'previousRelease':OLD,'runtime':pointer['runtime'],'previousRuntime':'runtime/liuren/'+OLD,'backup':'before-06','methodVersion':m['version'],'oldRuntimeHashes':{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in old.rglob('*') if p.is_file()},'newRuntimeFiles':{p.relative_to(new).as_posix():sha(p.read_bytes()) for p in new.rglob('*') if p.is_file()},'externalFiles':[{'path':rel,'before':sha((ROOT/rel).read_bytes()),'after':sha((CAND/rel).read_bytes())} for rel in external],'adjudication':m['adjudication']})
print(json.dumps({'built':NEW,'modelCalls':0}))
