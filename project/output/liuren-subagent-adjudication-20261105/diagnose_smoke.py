"""Read only the synthetic test sessions; never print unrelated sessions or reasoning."""
from pathlib import Path
import json
import shutil
import subprocess
HERE=Path(__file__).resolve().parent
exe=shutil.which('opencode')
def run(args):
    p=subprocess.run([exe,*args],cwd=HERE/'candidate',capture_output=True,encoding='utf-8',timeout=50)
    assert p.returncode==0,'diagnostic CLI failed'
    return json.loads(p.stdout)
found=[{'id':json.loads((HERE/'smoke-session.json').read_text('utf-8'))['parent']}]
out=[]
for row in found[-3:]:
    data=run(['export',row['id']])
    messages=data.get('messages',[])
    selected=[]
    for m in messages:
        info=m.get('info',{})
        parts=[]
        for p in m.get('parts',[]):
            if p.get('type')=='tool':
                s=p.get('state',{})
                parts.append({'tool':p.get('tool'),'status':s.get('status'),'metadata':s.get('metadata'),'error':s.get('error'),'output':s.get('output')})
        selected.append({'role':info.get('role'),'error':info.get('error'),'partTypes':[p.get('type') for p in m.get('parts',[])],'parts':parts})
    out.append({'id':row['id'],'messages':selected})
target=HERE/'smoke-diagnostic.json';target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
