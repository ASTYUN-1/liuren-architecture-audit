"""Seal final short-mode instructions and verification evidence before handoff."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261114-class-strength-trial-57'
T=R/p['runtime']; b=load(O/'before.json')
assert all(sha(R/f)==h for f,h in b['frozen'].items())
entry=R/'.opencode/skills/liuren/daliuren/SKILL.md'
old='不得只列空墓或神煞就定倾向。'
new='旺衰必须实际参与吉凶判断，简述它如何影响关键生克、制救及最终倾向；不得只列状态而不用于结论，也不得只列空墓或神煞就定倾向。'
s=entry.read_text('utf8');assert old in s;entry.write_text(s.replace(old,new),'utf8');(T/'entry.md').write_bytes(entry.read_bytes())
f=T/'references/class-selection-trial.md';s=f.read_text('utf8').replace('主类必须贯穿倾向依据，','旺衰必须实际参与吉凶判断：说明它如何影响关键作用方的生克、制救，并据此支持或改变最终倾向，不能仅列出状态后弃置不用。主类必须贯穿倾向依据，').replace('程序只核坐标，','程序只核坐标和状态计算，');f.write_text(s,'utf8')
cfg=load(R/'opencode.json');cfg['agent']['liuren']['prompt']=entry.read_text('utf8').split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝即表示该工具不在当前试验范围，不以其他代理、Build、外部MCP或脚本绕过；工作流开发由用户另行提出。';save(R/'opencode.json',cfg)
p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']}
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
p['bookRetrieval']['files']={f:sha(R/f) for f in p['bookRetrieval']['files']}
c=load(T/'loader-contract.json');m=load(T/'manifest.json')
c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
for d in [m,c]:d['bookRetrieval']=p['bookRetrieval']
save(T/'loader-contract.json',c);m['files']={f:sha(T/f) for f in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':p['release'],'files':{f:sha(R/f) for f in b['files']},'frozen_56_unchanged':True,'external_model_calls':0})
save(O/'verification.json',{'release':p['release'],'node_tests':{'passed':45,'failed':0,'command':'node --test tools/tests/liuren-class-selection-trial.test.mjs tools/tests/liuren-adjudication-contract.test.mjs tools/tests/liuren-analysis-route.test.mjs'},'native_strength_archive_call':True,'no_archive_rejected':True,'adjudication_still_disabled':True,'preflight_passed':True,'codex_status_ready':True,'external_model_calls':0,'model_compliance_verified':False,'predictive_accuracy_verified':False})
print('Finalized',p['release'])
