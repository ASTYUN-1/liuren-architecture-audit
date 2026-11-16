from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
B=load(OUT/'before24.json');p=load(ROOT/'.opencode/liuren-active.json');OLD=B['release'];NEW='20261106-performance-25';source=OUT.relative_to(ROOT).as_posix()
assert p['release']==OLD
for rel,h in B['runtimeFiles'].items():assert sha(ROOT/B['runtime']/rel)==h,rel
C=ROOT/'runtime/liuren'/NEW;assert not C.exists();shutil.copytree(ROOT/B['runtime'],C)
guide='宿主tool_output上限350000字节/20000行，覆盖有界全文合批；提交时重新比对宿主实际返回的每页全文与hash，截断回执不计读完。25版提速只减少重复传输，不降低专业要求：同阶段已触发的方法可liuren_materials(action="method",modules=[1..4个模块ID])合批读全文，保留每项独立回执，不为凑批次扩大专项。14必查、切题专项、原书核证与最强反证仍须覆盖。同版已读原段复用；遇影响本问的真实缺口才续查，不为统一无关分歧循环。packet.method_modules只列已读当前模块ID，由程序装配全文及hash；method_materials保留原书handoff和其他精确来源，quote可省略。材料别名material_aliases指向同源/同版/同行段的唯一全文，保留原编号，不丢依据。裁决者首次read用page=1,page_count=4，此后严格按next_call完整读完；不摘要、不跳页。主智能体核事实/引用/覆盖/一致性，日期算式优先核对read/deliver附带的calculation_receipts，范围、时区、日界相同且无具体疑点时不重算；新缺口可补核，不重新权衡。裁决者模型及high思考保留。新会话先查workflow回执tool_contract=liuren-tools-25确认工具已重载；方法版本号不能证明进程工具已更新。'
for rel in ['AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md']+[f.relative_to(ROOT).as_posix() for f in (ROOT/'.opencode/skills/liuren').rglob('SKILL.md')]:
 f=ROOT/rel;t=f.read_text('utf-8-sig').replace(OLD,NEW)
 if rel in ['AGENTS.md','docs/本机六壬高效执行.md'] or rel.endswith('daliuren/SKILL.md'):t+='\n\n'+guide+'\n'
 f.write_text(t,'utf-8')
config=json.loads(json.dumps(load(ROOT/'opencode.json'),ensure_ascii=False).replace(OLD,NEW));config['agent']['liuren']['prompt']+=' '+guide;dump(ROOT/'opencode.json',config)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');a=slim['agents']['liuren-adjudicator'];a['prompt']+='\n25版全文合批：首次liuren_adjudication_read用page=1,page_count=4，后续原样调用next_call。每批含连续页全文，必须remaining_pages为空才裁决。material_aliases的ID引用canonical_id对应的完整原段，不是缺失材料。必要日期/取数计算保留，程序将原始计算回执交主智能体复核，勿为传输重算。\n';dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',slim)
shutil.copyfile(ROOT/'.opencode/skills/liuren/daliuren/SKILL.md',C/'entry.md')
for rel in ['methods/workflow-contract.md','references/deterministic-tools.md']:
 f=C/rel;f.write_text(f.read_text('utf-8-sig').replace(OLD,NEW)+'\n\n'+guide+'\n','utf-8')
f=C/'references/adjudicator-contract.md';f.write_text(f.read_text('utf-8-sig')+'\n\n连续全文读取可用page_count=4；material_aliases仅引用同源同段全文，保留全部专业条件，不降低high思考。\n','utf-8')
policy=load(C/'references/shensha-policy.json');policy['release']=NEW;dump(C/'references/shensha-policy.json',policy)
p.update(release=NEW,previousRelease=OLD,runtime=C.relative_to(ROOT).as_posix(),backup=source+'/before24',authoringSource=source)
p['toolUsage'].update(toolContract='liuren-tools-25',fullPageBatch=4,moduleAssembly=True,exactSourceAliases=True,calculationReceipts=True,professionalRulesChanged=False)
p['computeInterface'].update(release=NEW,transportEvidence=source+'/current-wire.json',transportValidation='pending real native-host rerun; see evidence')
p['bookRetrieval']['compatibleMethodRelease']=NEW
for group in [p['workflowImplementation'],p['bookRetrieval']['files']]:
 for rel in group:group[rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
loader=load(C/'loader-contract.json');loader.update(release=NEW,parentRelease=OLD,authoringSource=source,toolUsage=p['toolUsage'])
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(C/'loader-contract.json',loader)
m=load(C/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=source,computeInterface=p['computeInterface'],toolUsage=p['toolUsage'])
pres=load(C/m['preservationFile']);pres['release']=NEW
for row in pres['modules']:
 rel=row['active_file']
 if sha(C/rel)!=sha(ROOT/B['runtime']/rel):
  if row.get('current_revision'):row.setdefault('revision_history',[]).append(row['current_revision'])
  row['current_revision']={'authoring_source':p['runtime']+'/'+rel,'sha256':sha(C/rel),'previous_active_source':B['runtime']+'/'+rel,'previous_active_sha256':sha(ROOT/B['runtime']/rel),'summary':'提速：全文合批、去重别名、模块装配与计算回执复用；保留专业规则与高思考。'}
dump(C/m['preservationFile'],pres)
m['files']={f.relative_to(C).as_posix():sha(f) for f in C.rglob('*') if f.is_file() and f.name!='manifest.json'};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(C/'manifest.json',m);p['methodVersion']=m['version']
tmp=ROOT/'.opencode/liuren-active.json.performance-installing';assert not tmp.exists();dump(tmp,p);tmp.replace(ROOT/'.opencode/liuren-active.json')
for rel,h in B['runtimeFiles'].items():assert sha(ROOT/B['runtime']/rel)==h,rel
dump(OUT/'activation25.json',{'release':NEW,'previousRelease':OLD,'oldRuntimeUnchanged':True,'professionalRulesChanged':False,'highReasoningPreserved':True,'verification':'pending','newFiles':['.gitignore']})
print(NEW)
