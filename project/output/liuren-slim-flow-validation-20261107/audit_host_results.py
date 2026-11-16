"""Inspect every actual host tool state, not just the scripted model's final text."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
rows=[json.loads(line) for line in (OUT/'host-cli.jsonl').read_text('utf-8').splitlines() if line.startswith('{')]
parts=[r['part'] for r in rows if r.get('type')=='tool_use']
errors=[{'tool':p['tool'],'error':p['state'].get('error')} for p in parts if p['state']['status']!='completed']
assert not errors,errors
computed=[]
for p in parts:
 if p['tool']=='liuren_compute':computed.append({'input':p['state']['input'],'output':json.loads(p['state']['output'])})
actions={p['input']['action']:p['output'] for p in computed}
assert set(actions)=={'chart','quantity','life','lookup','source'},actions.keys()
assert actions['quantity']['value']==48
assert actions['life']['xingnian']=='壬子'
assert actions['lookup']['growth']=='临官' and actions['lookup']['kin']=='子孙'
assert '竞争轮次' in actions['source']['quote']
methods=[p for p in parts if p['tool']=='liuren_materials' and p['state']['input']['action']=='method']
assert all(p['state'].get('metadata',{}).get('truncated') is not True for p in methods)
help_part=next(p for p in parts if p['tool']=='liuren_tool_help')
assert json.loads(help_part['state']['output'])['features']['archive_metadata_passthrough'] is True
host=json.loads((OUT/'host-chain.json').read_text('utf-8'))
assert host['finished'] and not host['failures'] and host['childModelAndHighVerified']
summary={'passed':True,'mainToolCalls':len(parts),'registeredAndExecuted':sorted({p['tool'] for p in parts}),'computeActionsVerified':list(actions),'childCalendarViaBoundChart':True,'childModelAndHighVerified':host['childModelAndHighVerified'],'requests':len(host['events']),'childPages':host['state']['childPages'],'childReadCalls':host['state']['childReadCalls'],'errors':errors,'externalModelCalls':0}
(OUT/'host-results-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
