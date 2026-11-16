"""Publish the compact deterministic Bifa view without editing frozen runtime 43."""
from pathlib import Path
import json,hashlib,shutil,re,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
enc=lambda x:(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json');before=load(O/'before.json')
OLD=before['release'];NEW='20261111-compact-bifa-44'
assert p['release']==OLD=='20261111-reviewed-bifa-43'
assert all(sha(R/f)==h for f,h in before['frozen'].items())
runtime=R/'runtime/liuren'/NEW;assert not runtime.exists()
shutil.copytree(R/p['runtime'],runtime)
shutil.copyfile(R/'tools/liuren-bifa-statements.json',runtime/'references/bifa-statements.json')
short='44版本机毕法精简导出：百法固定象义、142条固定条件模板（134结构、8方法）；正式AI盘bifa_conditions只列已满足全部条件的基本结构，每项仅条目、成格、意象。同法合并保留全部子格，成格依实际昼夜与坐标生成，旬空坐空分列。详细核查和BF-B/D书证保留按需查阅。'
core='''## 第44版：毕法固定语句导出

正式盘及裁决核心的chart.bifa_conditions为数组，每项仅“条目、成格、意象”。程序按实际昼夜扫描全部已登记基本条件，以固定模板填本盘坐标；同法合并但保留全部匹配子格。成格确认的是明列结构关系，取义仍依本问类神、旺衰空实、制救与阶段，重叠关系不重复计证。

未满足全部条件的候选及方法核查不列为成格。第9、93、94、96、97、98、99、100法的方法仍按问使用；百法固定象义和全部条件模板见bifa-statements，详细采用边界见bifa-basic，连续原文按BF-B/D法号读取（第100法用BF-B100或BF-D100）。

'''
for rel in ['references/judgment-core.md','methods/adjudication.md','methods/structure.md','references/bifa.md']:
 target=runtime/rel;text=target.read_text('utf-8')
 text=re.sub(r'## 第43版：[^\n]*\n[\s\S]*?(?=\n## |\Z)','',text,count=1)
 text=re.sub(r'## 第42版：基本毕法自动交接\n[\s\S]*?(?=\n## |\Z)','',text,count=1)
 text=re.sub(r'^42版：[^\n]*bifa_conditions[^\n]*\n?','',text,flags=re.M)
 head,rest=text.split('\n',1);target.write_text(head+'\n\n'+core+rest.lstrip('\n'),encoding='utf-8')
# Keep the extensive adoption rules on demand, separate from the three-field view.
guide=runtime/'references/bifa-basic.md';g=guide.read_text('utf-8');g=g.replace('# 毕法百法基本适配（43版）','# 毕法百法基本适配（44版）')
g=g.replace('本机正式完整盘及裁决核心的chart.bifa_conditions已逐法登记100法','内部scanBasicBifa详细核查结果已逐法登记100法')
g=g.replace('## 第43版：百法基本条件与方法交接（覆盖42版的25法范围说明）','## 内部基本条件与方法核查')
guide.write_text(g.split('\n',1)[0]+'\n\n'+core+g.split('\n',1)[1],encoding='utf-8')
contract={**p['basicBifaIntegration'],'id':'compact-bifa-44','display':'matched-laws-three-fields','statementLaws':100,'statementBranches':142,'statements':'references/bifa-statements.json','templatesDeterministic':True}
pending={}
for rel in ['README.md','目录总索引.md']:
 text=(R/rel).read_text('utf-8').replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 pending[rel]=(text+'\n\n'+short+'\n').encode('utf-8')
cfg=load(R/'opencode.json');models={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt']
assert models=={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
pending['opencode.json']=enc(cfg)
slim=load(R/'.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt'];pending['.opencode/oh-my-opencode-slim.jsonc']=enc(slim)
current_sha=lambda rel:hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(R/rel)
p.update(release=NEW,runtime=runtime.relative_to(R).as_posix(),previousRelease=OLD,backup='output/liuren-bifa-compact-20261111/before',authoringSource='output/liuren-bifa-compact-20261111',basicBifaIntegration=contract)
p['bookRetrieval']['compatibleMethodRelease']=NEW
for name in ['manifest.json','loader-contract.json']:
 d=load(runtime/name);d.update(release=NEW,parentRelease=OLD,basicBifaIntegration=contract,authoringSource='output/liuren-bifa-compact-20261111')
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if name=='manifest.json':
  d['modules']['bifa-statements']={'file':'references/bifa-statements.json','required':False,'title':'百法固定象义与条件模板'}
  d['files']['references/bifa-statements.json']=sha(runtime/'references/bifa-statements.json')
 if name=='loader-contract.json':d['sourceHashes']={rel:current_sha(rel) for rel in d['sourceHashes']}
 (runtime/name).write_bytes(enc(d))
for name in ['references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='references/confirmed-policy-register.json':d['basicBifaIntegration']=contract
 (runtime/name).write_bytes(enc(d))
m=load(runtime/'manifest.json');m['files']={rel:sha(runtime/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(runtime/'manifest.json').write_bytes(enc(m))
p['methodVersion']=m['version']
p['workflowImplementation']={rel:current_sha(rel) for rel in p['workflowImplementation']}
for rel in ['tools/liuren-bifa-view.mjs','tools/liuren-bifa-statements.json']:p['workflowImplementation'][rel]=current_sha(rel)
pending['.opencode/liuren-active.json']=enc(p)
for rel in sorted(pending,key=lambda s:s=='.opencode/liuren-active.json'):
 target=R/rel;temp=target.with_name(target.name+'.bifa44.tmp');temp.write_bytes(pending[rel]);os.replace(temp,target)
assert all(sha(R/f)==h for f,h in before['frozen'].items())
(O/'after.json').write_bytes(enc({'release':NEW,'runtime':p['runtime'],'methodVersion':p['methodVersion'],'files':{f:sha(R/f) for f in before['files']},'new_files':['tools/liuren-bifa-view.mjs','tools/liuren-bifa-statements.json','tools/tests/liuren-bifa-view.test.mjs'],'frozen43_unchanged':True}))
print('Activated',NEW,'; frozen43 unchanged')
