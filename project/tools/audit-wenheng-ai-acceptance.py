"""Read-only audit of the explicit synthetic acceptance files and skill digests."""
import hashlib
import json
import shlex
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
code='''
import hashlib,json
from pathlib import Path
base=Path('/var/lib/wenheng/acceptance/ai-api')
summary=json.loads((base/'summary.json').read_text())
assert summary.get('syntheticOnly') and summary.get('ok')
skills=Path('/opt/wenheng/resources/.opencode/skills')
digests={str(p.relative_to(skills)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in skills.rglob('*.md')}
records={}
for name in ['initial','followup']:
 r=json.loads((base/(name+'.json')).read_text())
 records[name]={'facts':r['chart']['facts'],'normalized':r['chart']['normalized'],'evidence':r['evidence'],'usage':r['usage']}
print(json.dumps({'digests':digests,'records':records},ensure_ascii=False))
'''
result=subprocess.run(['ssh.exe','-F','NUL','-i',str(Path.home()/'.ssh/old-server-control'),'-p','22223','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','ConnectTimeout=12','-o','StrictHostKeyChecking=yes','-o',f'UserKnownHostsFile={Path.home()}/Documents/OldServerControl/linux_known_hosts','slope@192.168.100.8','sudo -u wenheng python3 -c '+shlex.quote(code)],capture_output=True,check=True)
data=json.loads(result.stdout.decode('utf-8'))
local_skills=root/'.opencode/skills'
local={str(p.relative_to(local_skills)).replace('\\','/'):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in local_skills.rglob('*.md')}
remote=data['digests']
comparison={'localCount':len(local),'serverCount':len(remote),'identical':sorted(k for k,v in remote.items() if local.get(k)==v),'different':sorted(k for k,v in remote.items() if k in local and local[k]!=v),'localOnly':sorted(set(local)-set(remote)),'serverOnly':sorted(set(remote)-set(local))}
data['comparison']=comparison
out=root/'web/test-results/ai-rule-audit'
out.mkdir(parents=True,exist_ok=True)
(out/'synthetic-evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'comparison':{**comparison,'identicalCount':len(comparison['identical']),'identical':'omitted'},'records':{k:{'normalized':v['normalized'],'factKeys':list(v['facts']),'usage':v['usage'],'evidence':v['evidence']} for k,v in data['records'].items()}},ensure_ascii=False,indent=2))
