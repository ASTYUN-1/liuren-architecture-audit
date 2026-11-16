from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'before.json').exists()
# Preserve the small post-batch correction, restore and verify exact tested 59.
helper=R/'tools/liuren-trial-decision.mjs';tests=R/'tools/tests/liuren-trial-decision.test.mjs'
if not (O/'helper.mjs').exists():(O/'helper.mjs').write_bytes(helper.read_bytes())
if not (O/'test.mjs').exists():(O/'test.mjs').write_bytes(tests.read_bytes())
old_function="""export function withTrialChartBasis(result){
 if(!result.ok||!result.facts)return result;
 const f=result.facts;
 return {trial_judgment_policy:TRIAL_DECISION_POLICY,...result,facts:{...f,trial_judgment_policy:TRIAL_DECISION_POLICY}};
}
"""
s=(O/'helper.mjs').read_text('utf8');helper.write_bytes((s[:s.index('export function withTrialChartBasis(result){')]+old_function).encode('utf8'))
s=(O/'test.mjs').read_text('utf8');tests.write_bytes((s[:s.index("test('unselected weak and zero day ghosts")].rstrip()+'\n').encode('utf8'))
baseline=load(R/'output/liuren-trial-decision-59/after.json')
assert all(sha(R/f)==h for f,h in baseline['files'].items()),'59 restoration differs from tested bytes'
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
save(R/'output/opencode-trial-decision-20261115-five-05-deepseek/tested-release.json',baseline)
p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261115-trial-decision-59'
T=R/'runtime/liuren/20261115-trial-decision-60';assert not T.exists()
c=load(R/p['runtime']/'loader-contract.json');files=set(p['workflowImplementation'])|set(c['sourceHashes'])
files.update('.opencode/skills/'+f for f in p['files']);files.update(['.opencode/liuren-active.json','README.md','目录总索引.md','tools/tests/liuren-class-selection-trial.test.mjs','tools/tests/liuren-trial-decision.test.mjs'])
for f in files:
 d=O/'before'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,d)
save(O/'before.json',{'release':p['release'],'files':{f:sha(R/f) for f in sorted(files)},'new_files':[],'frozen':{f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}})
shutil.copytree(R/p['runtime'],T)
helper.write_bytes((O/'helper.mjs').read_bytes());tests.write_bytes((O/'test.mjs').read_bytes())
print('Tested 59 verified and preserved; staged 60 unselected-ghost correction')
