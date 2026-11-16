from pathlib import Path
import json,hashlib,shutil
root=Path.cwd();out=root/'output/liuren-receipt-fix-20261106';before=json.loads((out/'before-manifest.json').read_text('utf8'));candidate=out/'candidate-runtime';new=before['newRelease'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for rel,d in before['runtime'].items():assert sha(root/before['parentRuntime']/rel)==d,rel
p=candidate/'loader-contract.json';v=read(p);v.update(release=new,parentRelease=before['parentRelease'],authoringSource='output/liuren-receipt-fix-20261106');v['flowControl']['visibleResultTransport']='receipt-with-task-id';v['flowControl']['ownedResultDiscovery']=True
for rel in v['sourceHashes']:v['sourceHashes'][rel]=sha(root/rel)
dump(p,v)
dump(candidate/'receipt-handoff-revision.json',{'release':new,'parentRelease':before['parentRelease'],'problem':'successful report replaced visible receipt and hid task_id in metadata','changes':['task and task_result return a small visible receipt with task_id and next_call','result locate searches only current parent; never guesses request_id or UUID','read and deliver preserve task_id and original adjudication','scope, models, professional rules and library exclusions retained'],'realFailureSession':'ses_e50b30172ffezjWWKjx2zDLh4n','predictiveValidation':False})
m=read(candidate/'manifest.json');m.update(release=new,parentRelease=before['parentRelease'],authoringSource='output/liuren-receipt-fix-20261106',status='active');m['flowControl']=v['flowControl'];m['computeInterface'].update(release=new,transportEvidence='output/liuren-receipt-fix-20261106/current-wire.json');m['adjudication']['outputTransport']='structured-submit-and-visible-receipt'
m['files']={p.relative_to(candidate).as_posix():sha(p) for p in candidate.rglob('*') if p.is_file() and p.name!='manifest.json'};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(candidate/'manifest.json',m)
pointer=read(out/'before/.opencode/liuren-active.json');pointer.update(release=new,previousRelease=before['parentRelease'],runtime='runtime/liuren/'+new,methodVersion=m['version'],backup='output/liuren-receipt-fix-20261106/before',authoringSource='output/liuren-receipt-fix-20261106');pointer['flowControl']={'enabled':True,**v['flowControl']};pointer['adjudication']=m['adjudication'];pointer['computeInterface']=m['computeInterface'];pointer['bookRetrieval']['compatibleMethodRelease']=new
for group in ['workflowImplementation']:
 for rel in pointer[group]:pointer[group][rel]=sha(root/rel)
for rel in pointer['bookRetrieval']['files']:pointer['bookRetrieval']['files'][rel]=sha(root/rel)
for rel in pointer['files']:pointer['files'][rel]=sha(root/'.opencode/skills'/rel)
dump(out/'candidate-active.json',pointer)
assert (candidate/'entry.md').read_bytes()==(root/pointer['entry']).read_bytes()
assert read(root/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt']==(candidate/'references/adjudicator-prompt.md').read_text('utf8')
wire=read(out/'current-wire.json');assert wire['exitCode']==0
for rel,d in wire['implementationSha256'].items():assert sha(root/rel)==d,rel
log=(out/'candidate-tests.log').read_text('utf-8-sig');assert all(s in log for s in ['tests 161','pass 161','fail 0'])
cm={'release':new,'runtime':{p.relative_to(candidate).as_posix():sha(p) for p in candidate.rglob('*') if p.is_file()},'live':{r:sha(root/r) for r in before['live'] if r!='.opencode/liuren-active.json'},'activeSha256':sha(out/'candidate-active.json')};dump(out/'candidate-manifest.json',cm)
dump(out/'candidate-checks.json',{'status':'passed','release':new,'tests':161,'candidateManifestSha256':sha(out/'candidate-manifest.json'),'testLogSha256':sha(out/'candidate-tests.log'),'wireCaptureSha256':sha(out/'current-wire.json'),'realCaseRecoveredWithoutModel':read(out/'real-recovery.json')['replayed_result_equal']})
# Reuse the established pointer-last installer, with an isolated backup and candidate manifest.
shutil.copyfile(root/'output/liuren-flow-repair-20261106/activate.py',out/'activate.py')
print(json.dumps({'candidate':new,'tests':161,'runtimeFiles':len(cm['runtime'])},ensure_ascii=False))
