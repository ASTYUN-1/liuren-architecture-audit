"""Verify, atomically activate, and restore this bounded local release."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAND=HERE/'candidate'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def j(path):return json.loads(path.read_text('utf-8-sig'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
def safe(base,rel):
    p=(base/rel).resolve();assert p.is_relative_to(base.resolve()) and '..' not in Path(rel).parts and not Path(rel).is_absolute();return p
def hashes(base,items):
    for rel,digest in items.items():assert sha(safe(base,rel).read_bytes())==digest,rel
def verify(live=False):
    plan=j(HERE/'switch-plan.json');base=ROOT if live else CAND
    hashes(ROOT,plan['oldRuntimeHashes'])
    runtime=base/plan['runtime'];m=j(runtime/'manifest.json');pointer=j(base/'.opencode/liuren-active.json')
    hashes(runtime,plan['newRuntimeFiles']);hashes(runtime,m['files'])
    assert m['version']==pointer['methodVersion']==sha(json.dumps(m['files'],sort_keys=True).encode())
    assert m['release']==pointer['release']==plan['release']
    assert m['adjudication']==pointer['adjudication']==plan['adjudication']
    assert pointer['experiment']['disableCaseExperience'] is True
    assert j(runtime/'references/shensha-policy.json')['release']==plan['release']
    route=j(runtime/'reading-route.json')
    assert m['required']==[x for stage in route['stages'] for x in stage['required']]
    assert route['stages'][2]['required']==['evidence','adjudication','report']
    old=ROOT/plan['previousRuntime'];om=j(old/'manifest.json')
    same=[]
    for key,item in m['modules'].items():
        if key not in {'adjudication','evidence','report','workflow-contract'}:
            assert (runtime/item['file']).read_bytes()==(old/item['file']).read_bytes(),key;same.append(key)
    assert len(same)==55 and len(m['modules'])==59 and len(m['required'])==14
    assert m['domains']==om['domains'] and len(m['domains'])==16
    a=j(runtime/'references/shensha-policy.json');b=j(old/'references/shensha-policy.json');a.pop('release');b.pop('release');assert a==b
    for row in plan['externalFiles']:
        assert sha((CAND/row['path']).read_bytes())==row['after'],row['path']
        dest=ROOT/row['path'];expected=row['after' if live else 'before']
        assert (sha(dest.read_bytes()) if dest.exists() else None)==expected,row['path']
    for name in pointer['activeSkillNames']:
        assert sha((base/f'.opencode/skills/liuren/{name}/SKILL.md').read_bytes())==pointer['files'][f'liuren/{name}/SKILL.md']
    assert (base/'.opencode/skills/liuren/daliuren/SKILL.md').read_bytes()==(runtime/'entry.md').read_bytes()
    contract=j(runtime/'loader-contract.json')
    for rel,digest in contract['sourceHashes'].items():
        p=base/rel if (CAND/rel).is_file() else ROOT/rel
        assert sha(p.read_bytes())==digest,rel
    config=j(base/'opencode.json');original=j(HERE/plan.get('backup','before')/'opencode.json') if live else j(ROOT/'opencode.json')
    inherited=json.loads(json.dumps(original,ensure_ascii=False).replace(plan['previousRelease'],plan['release']))
    agent=inherited['agent']['liuren'];new=config['agent']['liuren']
    agent['prompt']=new['prompt'];agent['description']=new['description'];agent['permission']['task']={'*':'deny','liuren-adjudicator':'allow'}
    agent['permission']['liuren_adjudication_packet']='allow'
    assert config==inherited,'unrelated OpenCode config changed'
    slim=j(base/'.opencode/oh-my-opencode-slim.jsonc');judge=slim['agents']['liuren-adjudicator']
    assert len(slim['agents'])==1 and judge['model']==plan['adjudication']['model'] and judge['variant']=='high'
    assert judge['options']['reasoningEffort']=='high' and judge['permission']['*']=='deny'
    # Both the loader and scope guards must work against the constructed state.
    spec=importlib.util.spec_from_file_location('release_method_loader',ROOT/'tools/load-liuren-methods.py');loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
    rr,mm=loader.active(base)
    for key in mm['modules']:loader.content(rr,mm,key)
    assert loader.plan(mm,['exam']).index('evidence')<loader.plan(mm,['exam']).index('adjudication')
    result={'ok':True,'phase':'active' if live else 'candidate','release':plan['release'],'modules':59,'professionalModulesByteUnchanged':55,'required':14,'domains':16,'oldRuntimeUnchanged':True,'calculationPolicyUnchanged':True,'unrelatedConfigUnchanged':True,'model':judge['model'],'variant':'high','predictiveValidationCount':0}
    save(HERE/('active-verification.json' if live else 'candidate-verification.json'),result)
    return result
def atomic(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.adjudicator-switch.tmp');assert not temp.exists()
    with temp.open('xb') as f:f.write(raw)
    os.replace(temp,path)
def apply():
    verify();plan=j(HERE/'switch-plan.json');backup=HERE/plan.get('backup','before');target=ROOT/plan['runtime']
    assert not backup.exists() and not target.exists();backup.mkdir()
    for row in plan['externalFiles']:
        if row['before'] is not None:
            dest=backup/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/row['path']).read_bytes())
    for rel in plan['newRuntimeFiles']:
        p=safe(target,rel);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((CAND/plan['runtime']/rel).read_bytes())
    hashes(target,plan['newRuntimeFiles']);changed=[]
    try:
        for row in sorted(plan['externalFiles'],key=lambda x:x['path']=='.opencode/liuren-active.json'):
            dest=safe(ROOT,row['path']);assert (sha(dest.read_bytes()) if dest.exists() else None)==row['before']
            atomic(dest,(CAND/row['path']).read_bytes());changed.append(row)
        result=verify(True)
    except BaseException:
        for row in reversed(changed):
            dest=ROOT/row['path']
            if row['before'] is None:dest.unlink()
            else:atomic(dest,(backup/row['path']).read_bytes())
        raise
    result.update(activated=True,previousRelease=plan['previousRelease'],pointerWrittenLast=True)
    save(HERE/'activation-receipt.json',result);return result
def rollback(perform=False):
    plan=j(HERE/'switch-plan.json');hashes(ROOT,plan['oldRuntimeHashes'])
    for row in plan['externalFiles']:
        assert sha((ROOT/row['path']).read_bytes())==row['after'],row['path']
        if row['before'] is not None:assert sha((HERE/plan.get('backup','before')/row['path']).read_bytes())==row['before']
    if perform:
        for row in sorted(plan['externalFiles'],key=lambda x:x['path']=='.opencode/liuren-active.json'):
            dest=ROOT/row['path']
            if row['before'] is None:dest.unlink()
            else:atomic(dest,(HERE/plan.get('backup','before')/row['path']).read_bytes())
    result={'rollbackReady':True,'performed':perform,'targetRelease':plan['previousRelease'],'frozenRuntimesRetained':True}
    save(HERE/('rollback-receipt.json' if perform else 'rollback-check.json'),result);return result
if __name__=='__main__':
    commands={'verify':verify,'apply':apply,'verify-live':lambda:verify(True),'rollback-check':rollback,'rollback':lambda:rollback(True)}
    print(json.dumps(commands[sys.argv[1]](),ensure_ascii=False))
