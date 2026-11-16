"""Read resolved host config; persist only selected non-secret agent settings."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
root=HERE.parents[1] if '--live' in sys.argv else HERE/'candidate'
exe=shutil.which('opencode')
assert exe
r=subprocess.run([exe,'debug','config'],cwd=root,capture_output=True,encoding='utf-8',timeout=60)
assert r.returncode==0, 'OpenCode resolved-config failed; inspect bounded diagnostic separately'
cfg=json.loads(r.stdout)
judge=cfg.get('agent',{}).get('liuren-adjudicator')
assert judge,'slim did not register custom adjudicator'
main=cfg['agent']['liuren']
def select(a):
    return {k:a.get(k) for k in ['mode','model','variant','options','permission']}
result={'hostResolved':True,'live':'--live' in sys.argv,'judge':select(judge),
        'mainTaskPermission':main.get('permission',{}).get('task'),
        'mainModel':main.get('model'),'defaultAgent':cfg.get('default_agent'),
        'plugins':cfg.get('plugin'),'promptCharacters':len(judge.get('prompt',''))}
model=judge.get('model');expected=json.loads((root/'.opencode/liuren-active.json').read_text('utf-8'))['adjudication']['model']
provider_id,model_id=expected.split('/',1)
assert model in [expected,{'providerID':provider_id,'modelID':model_id}],repr(model)
assert judge.get('variant')=='high'
assert judge.get('options',{}).get('reasoningEffort')=='high'
assert judge.get('mode')=='subagent'
assert 'E22' in judge.get('prompt','')
assert main.get('permission',{}).get('task',{}).get('liuren-adjudicator')=='allow'
assert cfg.get('default_agent')=='liuren'
target=HERE/('host-live.json' if result['live'] else 'host-candidate.json')
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
