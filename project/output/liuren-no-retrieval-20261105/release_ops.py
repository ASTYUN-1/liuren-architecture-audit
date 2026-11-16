"""Verify, activate and restore a no-library-retrieval experiment byte-exactly."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import itertools
import json
import os
import re
import sys
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAND=HERE/'candidate'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def j(path):return json.loads(path.read_text('utf-8-sig'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
def safe(base,rel):
    path=(base/rel).resolve()
    assert not Path(rel).is_absolute() and '..' not in Path(rel).parts and path.is_relative_to(base.resolve())
    return path
def hashes(base,values):
    for rel,digest in values.items():
        p=safe(base,rel)
        assert p.is_file() and not p.is_symlink() and sha(p.read_bytes())==digest,str(p)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify(live=False):
    plan=j(HERE/'switch-plan.json');base=ROOT if live else CAND
    package=base/plan['runtime'];old=ROOT/plan['previousRuntime']
    m=j(package/'manifest.json');om=j(old/'manifest.json')
    hashes(ROOT,plan['oldRuntimeHashes']);hashes(package,plan['newRuntimeFiles']);hashes(package,m['files'])
    assert m['version']==sha(json.dumps(m['files'],sort_keys=True).encode())==plan['methodVersion']
    pointer=j(base/'.opencode/liuren-active.json')
    assert pointer['release']==m['release']==plan['release']
    assert pointer['methodVersion']==m['version'] and pointer['experiment']==m['experiment']==plan['experiment']
    for row in plan['externalFiles']:
        assert sha((CAND/row['path']).read_bytes())==row['after']
        p=ROOT/row['path'];digest=row['after' if live else 'before']
        assert (sha(p.read_bytes()) if p.exists() else None)==digest,row['path']
    for field in ['modules','required','conditional','domains','procedureFiles']:
        assert m[field]==om[field],field
    route=j(package/'reading-route.json');previous=j(old/'reading-route.json')
    assert route['conditional']==previous['conditional'] and route['legacyCoverage']==previous['legacyCoverage']
    assert [[s['id'],s['required']] for s in route['stages']]==[[s['id'],s['required']] for s in previous['stages']]
    # Byte equality of every professional module except explicitly affected workflow instructions.
    altered={'evidence','adjudication','report','workflow-contract'}
    unchanged=[]
    loader=load('variant_methods',ROOT/'tools/load-liuren-methods.py')
    for key,item in m['modules'].items():
        loader.content(package,m,key)
        if key not in altered:
            assert (package/item['file']).read_bytes()==(old/item['file']).read_bytes(),key
            unchanged.append(key)
    assert len(m['modules'])==59 and len(unchanged)==55 and len(m['required'])==14 and len(m['domains'])==16
    for rel in ['references/shensha-policy.json']:
        a=j(package/rel);b=j(old/rel);a.pop('release');b.pop('release');assert a==b
    # All old files not explicitly listed as changed must have identical bytes.
    changed={r['path'] for r in plan['packageChanges']}|{'manifest.json'}
    for rel in om['files']:
        if rel not in changed:assert (package/rel).read_bytes()==(old/rel).read_bytes(),rel
    newroutes=copy.deepcopy(m);newroutes['readingRoute']=route
    oldroutes=copy.deepcopy(om);oldroutes['readingRoute']=previous
    combinations=0
    conditions=list(route['conditional'])
    for flags in itertools.product((False,True),repeat=len(conditions)):
        selected=[k for k,f in zip(conditions,flags) if f]
        assert loader.plan(newroutes,['exam'],extras=selected)==loader.plan(oldroutes,['exam'],extras=selected)
        combinations+=1
    for domain,timing,nianming in itertools.product(m['domains'],(False,True),(False,True)):
        assert loader.plan(newroutes,[domain],timing=timing,nianming=nianming)==loader.plan(oldroutes,[domain],timing=timing,nianming=nianming)
    for name in pointer['activeSkillNames']:
        p=base/'.opencode/skills/liuren'/name/'SKILL.md'
        assert sha(p.read_bytes())==pointer['files']['liuren/'+name+'/SKILL.md']
        text=p.read_text('utf-8');match=re.match(r'^---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---',text)
        assert match and match[1]==name and len(match[2])<=1024
    assert (base/'.opencode/skills/liuren/daliuren/SKILL.md').read_bytes()==(package/'entry.md').read_bytes()
    config=j(base/'opencode.json')
    original=j((HERE/'before/opencode.json') if live else ROOT/'opencode.json')
    # No permissions other than the intended case, experience/cache native reads change.
    expected=json.loads(json.dumps(original,ensure_ascii=False).replace(plan['previousRelease'],plan['release']))
    old_agent=expected['agent']['liuren'];new_agent=config['agent']['liuren']
    old_agent['description']=new_agent['description'];old_agent['prompt']=new_agent['prompt']
    expected_read=old_agent['permission']['read']
    for key in expected_read:
        if any(t in key for t in ['案例项目库','经验日志','tmp/liuren-materials','tmp\\liuren-materials']):expected_read[key]='deny'
    for name in ['案例项目库','经验日志']:expected_read[name+'/*']='deny'
    assert config==expected
    assert '双路复核' not in new_agent['prompt'] and '分别检索案例与经验' not in new_agent['prompt']
    assert '原书' in new_agent['prompt'] and '14必查' in new_agent['prompt']
    contract=j(package/'loader-contract.json')
    for rel,digest in contract['sourceHashes'].items():
        path=base/rel if (CAND/rel).is_file() else ROOT/rel
        assert sha(path.read_bytes())==digest,rel
    # Isolated guard check uses candidate implementation with real loader contract.
    # Two unchanged support files are staged only for this check, never activated.
    if not live:
        for rel in ['tools/load-liuren-methods.py','docs/本机六壬直接排盘.md']:
            path=CAND/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/rel).read_bytes())
    sys.path.insert(0,str(base/'tools'))
    sys.modules.pop('liuren_retrieval_policy',None)
    scope_module=load('variant_scope',base/'tools/liuren_material_scope.py')
    scope=scope_module.MaterialScope(base)
    assert scope.no_case_experience
    assert 'cases' not in scope.describe()['libraries'] and 'experience' not in scope.describe()['libraries']
    denied=0
    for library in ['cases','experience']:
        try:scope.scan(library,'考试')
        except ValueError as exc:assert 'LIUREN_EXPERIMENT_NO_RETRIEVAL' in str(exc);denied+=1
        else:raise AssertionError('library scan not denied')
    for relative in ['案例项目库/example.md','经验日志/example.md']:
        assert not scope.permitted(base/relative);denied+=1
    refs=j(package/'source-read-map.json')
    blocked_aliases=0
    for alias,item in refs['aliases'].items():
        if any(part in {'经验日志','案例项目库'} for part in Path(item['path']).parts):
            assert not scope.permitted(base/item['path']);blocked_aliases+=1
            # A rejected snapshot must never be read even for a hash check.
            blocked_path=(base/item['path']).resolve()
            original_read=Path.read_bytes
            def guarded_read(path):
                assert path.resolve()!=blocked_path,'excluded original was opened before denial'
                return original_read(path)
            with patch.object(Path,'read_bytes',guarded_read):
                try:scope.read(alias,1,1)
                except ValueError as exc:assert 'LIUREN_EXPERIMENT_NO_RETRIEVAL' in str(exc)
                else:raise AssertionError('historical alias allowed')
    assert blocked_aliases==2
    helper=load('variant_policy',base/'tools/liuren_retrieval_policy.py')
    assert helper.case_experience_disabled(base)
    if not live:assert not helper.case_experience_disabled(ROOT), 'baseline behavior changed'
    for code in ['tools/liuren_retrieval_policy.py','tools/liuren_material_scope.py','tools/liuren-local-read.py']:
        compile((base/code).read_text('utf-8'),str(base/code),'exec')
    result=dict(ok=True,release=plan['release'],phase='active' if live else 'candidate',
        methodVersion=m['version'],modules=59,professionalModulesByteUnchanged=55,required=14,domains=16,
        routeCombinationsSameAsBaseline=combinations,domainPlansSameAsBaseline=64,disabledScanAndRootChecks=denied,
        excludedHistoricalExperienceAliases=blocked_aliases,oldRuntimeUnchanged=True,
        calculationPolicyUnchanged=True,configDiffLimitedToExperiment=True,modelCalls=0,predictiveValidationCount=0)
    save(HERE/('active-verification.json' if live else 'candidate-verification.json'),result)
    return result

def atomic(path,raw):
    temp=path.with_name(path.name+'.no-retrieval-switch.tmp')
    assert not temp.exists()
    with temp.open('xb') as f:f.write(raw)
    os.replace(temp,path)
def apply():
    verify();plan=j(HERE/'switch-plan.json');backup=HERE/'before';target=ROOT/plan['runtime']
    assert not backup.exists() and not target.exists()
    backup.mkdir()
    for row in plan['externalFiles']:
        if row['before'] is not None:
            p=backup/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/row['path']).read_bytes())
    target.mkdir(parents=True)
    for rel in plan['newRuntimeFiles']:
        p=safe(target,rel);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((CAND/plan['runtime']/rel).read_bytes())
    hashes(target,plan['newRuntimeFiles'])
    rows=sorted(plan['externalFiles'],key=lambda r:r['path']=='.opencode/liuren-active.json')
    changed=[]
    try:
        for row in rows:
            dest=safe(ROOT,row['path'])
            assert (sha(dest.read_bytes()) if dest.exists() else None)==row['before']
            atomic(dest,(CAND/row['path']).read_bytes());changed.append(row)
        result=verify(True)
    except BaseException:
        for row in reversed(changed):
            dest=ROOT/row['path']
            if row['before'] is None:dest.unlink()
            else:atomic(dest,(backup/row['path']).read_bytes())
        raise
    result.update(activated=True,previousRelease=plan['previousRelease'],externalFiles=len(rows),pointerWrittenLast=True)
    save(HERE/'activation-receipt.json',result);return result

def rollback(perform=False):
    plan=j(HERE/'switch-plan.json')
    hashes(ROOT,plan['oldRuntimeHashes'])
    for row in plan['externalFiles']:
        assert sha((ROOT/row['path']).read_bytes())==row['after']
        if row['before'] is not None:assert sha((HERE/'before'/row['path']).read_bytes())==row['before']
    if perform:
        rows=sorted(plan['externalFiles'],key=lambda r:r['path']=='.opencode/liuren-active.json')
        for row in rows:
            if row['before'] is None:(ROOT/row['path']).unlink()
            else:atomic(ROOT/row['path'],(HERE/'before'/row['path']).read_bytes())
    result=dict(rollbackReady=True,performed=perform,targetRelease=plan['previousRelease'],bothRuntimesRetained=True)
    save(HERE/('rollback-receipt.json' if perform else 'rollback-check.json'),result);return result

def enable_existing():
    """Re-enable the already built variant after a checked baseline rollback."""
    plan=j(HERE/'switch-plan.json')
    pointer=j(ROOT/'.opencode/liuren-active.json')
    if pointer['release']==plan['release']:return verify(True)
    assert pointer['release']==plan['previousRelease'],'unexpected active release; do not overwrite later work'
    verify(False)
    hashes(ROOT/plan['runtime'],plan['newRuntimeFiles'])
    changed=[]
    try:
        for row in sorted(plan['externalFiles'],key=lambda r:r['path']=='.opencode/liuren-active.json'):
            dest=ROOT/row['path']
            assert (sha(dest.read_bytes()) if dest.exists() else None)==row['before']
            atomic(dest,(CAND/row['path']).read_bytes());changed.append(row)
        result=verify(True)
    except BaseException:
        for row in reversed(changed):
            if row['before'] is None:(ROOT/row['path']).unlink()
            else:atomic(ROOT/row['path'],(HERE/'before'/row['path']).read_bytes())
        raise
    save(HERE/'reenable-receipt.json',result);return result

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    commands={'verify':verify,'apply':apply,'verify-live':lambda:verify(True),'rollback-check':rollback,'rollback':lambda:rollback(True),'enable':enable_existing}
    print(json.dumps(commands[sys.argv[1]](),ensure_ascii=False))
