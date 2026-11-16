"""Seal the new local interface release; never overwrite frozen runtime bytes."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
b=load(O/'before.json');old=b['release'];new='20261114-tool-reliability-55';T=R/'runtime/liuren'/new
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen 54 changed'
p=load(R/'.opencode/liuren-active.json');assert p['release'] in [old,new]
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-tool-reliability-55/before',authoringSource='output/liuren-tool-reliability-55')
m=load(T/'manifest.json');c=load(T/'loader-contract.json')
m.update(release=new,parentRelease=old);c.update(release=new,parentRelease=old)
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(T/rel);d['release']=new;save(T/rel,d)
notice='工具参数不明查liuren_tool_help；topic可用workflow/packet/compute/result/read/submit/audit/chart/materials。task_basis.request_quote和user_explicit的stage_basis须直接复制原始用户消息连续原句，解释另放依据字段。result read返回evidence_catalog合法引用及review_scaffold待填写结构；review嵌套review:{report_sha256,checks}，recheck用findings。仅从合法清单取ID，不能拼路径/行号/说明。报错按具体索引修正，不读tools或插件源码，不反复猜参数；复核内容仍须实质填写。'
for cfg in ['opencode.json','.opencode/oh-my-opencode-slim.jsonc']:
 data=load(R/cfg)
 if cfg=='opencode.json':
  rules=data['agent']['liuren']['permission']['read']
  data['agent']['liuren']['permission']['read']={k.replace(old,new):v for k,v in rules.items()}
  prompt=data['agent']['liuren']['prompt']
  if notice not in prompt:data['agent']['liuren']['prompt']=prompt+'\n'+notice
 else:
  prompt=(T/'references/adjudicator-prompt.md').read_text('utf8')
  extra='\n工具接口：裁决者可查tool_help的compute/read/submit/audit。原书用本任务reader的material_id/module，具名法优先methods返回的source_read，不自行构造source路径；source转接只指向本任务已绑定书段。audit引用本任务真实ID/回执，不猜hash。\n'
  if extra.strip() not in prompt:prompt+=extra;(T/'references/adjudicator-prompt.md').write_text(prompt,'utf8')
  data['agents']['liuren-adjudicator']['prompt']=prompt
 save(R/cfg,data)
for f in ['README.md','目录总索引.md']:
 path=R/f;path.write_text(path.read_text('utf8').replace(old,new),'utf8')
policy={'release':new,'scope':'local-opencode-and-shared-transport','professionalRulesChanged':False,'modelCallsAdded':0,'predictiveValidationCount':0,'audit':'output/liuren-tool-reliability-55/修复与验收说明.md'}
for d in [p,m,c]:d['toolReliability']=policy
p['computeInterface']['transportEvidence']='output/liuren-tool-reliability-55/native-schema.json'
p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']}
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=sha(R/f)
c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
for key in ['computeInterface','bookRetrieval']:c[key]=p[key];m[key]=p[key]
save(T/'loader-contract.json',c)
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
save(T/'manifest.json',m);p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in b['files']},'frozen_54_unchanged':True,'real_model_calls':0})
print('Sealed',new,m['version'])
