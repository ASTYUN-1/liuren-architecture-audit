from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
B=load(OUT/'before-manifest.json');p=load(ROOT/'.opencode/liuren-active.json')
OLD=B['parentRelease'];NEW='20261106-workflow-22';source=OUT.relative_to(ROOT).as_posix()
assert p['release']==OLD
for rel,h in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==h,rel
C=OUT/'candidate-runtime'
if not C.exists():shutil.copytree(ROOT/B['parentRuntime'],C)
for rel in ['AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md']+[str(f.relative_to(ROOT)) for f in (ROOT/'.opencode/skills/liuren').rglob('SKILL.md')]:
 f=ROOT/rel;t=f.read_text('utf-8-sig').replace(OLD,NEW)
 if rel.endswith('daliuren/SKILL.md') and 'liuren_tool_help' not in t:
  t+='\n参数不明先liuren_tool_help的packet/compute；保存前可用workflow带domains查询missing及可复制next_calls，只补缺项。id全局唯一：Q_/F_/S_/O_/I_分开；handoff的M_/B_原样保留。神煞观察kind=shensha不等于有效采用；计算life也要archive。packet及reader成功按next_call继续，不重拼字段、不重派已有结果。\n'
 if rel=='AGENTS.md' and '21版工具自说明' not in t:
  t+='\n21版工具自说明：参数不明先liuren_tool_help(topic=packet/compute)，保存前可用topic=workflow带domains查缺读及next_calls，只补缺项。id须全局唯一，事实F_、争点I_分开；神煞观察可用shensha，计算life也需课盘archive。packet/reader/成功回执按next_call接续。完整读取、来源/hash、自由报告及无两库边界保留；旧会话需重启加载新工具。\n'
 f.write_text(t,'utf-8')
config=load(ROOT/'opencode.json');agent=config['agent']['liuren'];agent['permission']['liuren_tool_help']='allow'
if 'liuren_tool_help' not in agent['prompt']:agent['prompt']+=' 参数不明先liuren_tool_help(topic=packet/compute)，保存前可用workflow带domains查missing，只补缺读；按程序next_call接续。记录id全局唯一，事实F_和争点I_分开。'
# Keep read permissions bound to the new active runtime, preserving deny rules.
config=json.loads(json.dumps(config,ensure_ascii=False).replace(OLD,NEW));dump(ROOT/'opencode.json',config)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');a=slim['agents']['liuren-adjudicator'];a['permission']['liuren_tool_help']='allow'
a['description']='大六壬关键类神独立裁决；按文件页回执next_call读完材料，提交自由正文报告。'
if 'remaining_pages' not in a['prompt']:a['prompt']+='\n工具接续：reader返回remaining_pages和next_call；逐次原样调用next_call，剩余为空后独立裁决再submit正文或自由对象。compute参数不明用liuren_tool_help(topic="compute")，只查接口；不另取材料或改变任务范围。\n'
dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',slim)
shutil.copyfile(ROOT/'.opencode/skills/liuren/daliuren/SKILL.md',C/'entry.md')
for rel in ['methods/adjudication.md','methods/workflow-contract.md','references/deterministic-tools.md']:
 f=C/rel;t=f.read_text('utf-8-sig')
 if '21版工具自说明' not in t:t+='\n\n21版工具自说明：liuren_tool_help(topic=packet/compute)返回当前实际schema；workflow带domains返回就绪缺项及next_calls。仅补缺读，不替代方法全文。记录id全局唯一，事实F_、争点I_分开；神煞观察kind可为shensha，不升级为程序事实。主智能体compute的chart/lookup/life均须原样带archive。packet/reader成功按next_call继续；剩余页为空后才提交自由正文，不设固定专业输出字段。\n'
 f.write_text(t.replace(OLD,NEW),'utf-8')
for rel in ['methods/adjudication.md','references/adjudicator-contract.md','references/deterministic-tools.md']:
 f=C/rel;t=f.read_text('utf-8-sig')
 t+='\n自由报告的具体错误补核：retry_context.error_path对正文用$，reason引述具体错误原句；对自由JSON用真实字段JSON Pointer，不限制旧entity_checks等字段。仍须真实新增材料、已领取原任务、最多一次补核，不为格式重裁。\n'
 f.write_text(t,'utf-8')
policy=load(C/'references/shensha-policy.json');policy['release']=NEW;dump(C/'references/shensha-policy.json',policy)
p.update(release=NEW,previousRelease=OLD,runtime='runtime/liuren/'+NEW,backup=source+'/before',authoringSource=source)
p['computeInterface'].update(release=NEW,transportValidation='installed desktop host chain; see bound evidence, synthetic responses',transportEvidence=source+'/host-chain.json')
p['bookRetrieval']['compatibleMethodRelease']=NEW
p['toolUsage']={'helpTool':'liuren_tool_help','actualSchema':True,'readiness':'query current method receipts by domains','packetPreflight':'execute parses native schema and aggregates duplicate IDs','continuation':'packet and reader next_call','professionalRulesChanged':False,'predictiveValidationCount':0}
for group in [p['workflowImplementation'],p['bookRetrieval']['files']]:
 for rel in group:group[rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
loader=load(C/'loader-contract.json');loader.update(release=NEW,parentRelease=OLD,authoringSource=source,adjudication=p['adjudication'],toolUsage=p['toolUsage'])
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(C/'loader-contract.json',loader)
m=load(C/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=source,adjudication=p['adjudication'],computeInterface=p['computeInterface'],toolUsage=p['toolUsage'])
pres=load(C/m['preservationFile']);pres['release']=NEW
for row in pres['modules']:
 rel=row['active_file']
 if sha(C/rel)!=sha(ROOT/B['parentRuntime']/rel):
  if row.get('current_revision'):row.setdefault('revision_history',[]).append(row['current_revision'])
  row['current_revision']={'authoring_source':source+'/candidate-runtime/'+rel,'sha256':sha(C/rel),'previous_active_source':B['parentRuntime']+'/'+rel,'previous_active_sha256':sha(ROOT/B['parentRuntime']/rel),'summary':'工具自说明、参数校验与next_call接续；不改专业判断规则。'}
dump(C/m['preservationFile'],pres)
m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(C/'manifest.json',m);p['methodVersion']=m['version']
dump(OUT/'candidate-active.json',p)
dump(OUT/'candidate-manifest.json',{'release':NEW,'runtime':{f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file()},'live':{rel:sha(ROOT/rel) for rel in B['live']},'activeSha256':sha(OUT/'candidate-active.json')})
print(json.dumps({'release':NEW,'files':len(m['files']),'oldRuntimeUnchanged':True}))
