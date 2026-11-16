"""Create local release30; leave frozen release29 byte-for-byte intact."""
from pathlib import Path
import copy,hashlib,json,os,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
def replace(rel,old,new):
 p=ROOT/rel;s=p.read_text('utf-8');assert s.count(old)==1,(rel,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='')
old='20261107-slim-29';new='20261107-slim-30';cap=393216
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']==old
source=ROOT/p['runtime'];target=ROOT/'runtime/liuren'/new;assert not target.exists()
backup=OUT/'before-output-budget';assert not backup.exists()
rels=['.opencode/liuren-active.json','.opencode/plugins/liuren-adjudication.ts','tools/liuren-preflight.py','docs/本机六壬稳定运行指南.md','docs/本机六壬高效执行.md','README.md','目录总索引.md','AGENTS.md']
for rel in rels:
 dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
before={rel:sha(ROOT/rel) for rel in rels};frozen={f.relative_to(source).as_posix():sha(f) for f in source.rglob('*') if f.is_file()}
dump(OUT/'output-budget-before.json',{'files':before,'frozen29':frozen})
shutil.copytree(source,target)
replace('.opencode/plugins/liuren-adjudication.ts','provider_default_output_budget:true,','provider_default_output_budget:false,explicit_output_budget:true,requested_max_output_tokens:393216,')
replace('.opencode/plugins/liuren-adjudication.ts',"      // Omit the request budget, including the host's inherited 32k default.\n      // The provider still enforces its own model/context limits.\n      output.maxOutputTokens=undefined;", "      // DeepSeek high defaults to 64K when omitted; request the supported 384K maximum.\n      // This is a generation ceiling, not a required output length. Keep high reasoning.\n      output.maxOutputTokens=393216;")
replace('tools/liuren-preflight.py',"  record('no client token cap','maxOutputTokens' not in pointer.get('adjudication',{}))", "  budget=pointer.get('adjudication',{}).get('maxOutputTokens')\n  record('explicit adjudicator output budget',budget==393216,budget)")
replace('docs/本机六壬稳定运行指南.md','裁决请求省略客户端输出额度，服务端仍会执行自身规则。','30版裁决请求显式申请max_tokens=393216，避免省略参数时回落到服务端64K默认额度。这是生成上限，不要求用满；仍受接口及上下文规则约束。')
replace('docs/本机六壬稳定运行指南.md','在本项目目录选择 **liuren**。一次启动检查：','在本项目目录选择 **liuren**。以下启动检查为可选排障命令，正常提问无需每次运行：')
guide='30版：裁决请求显式申请max_tokens=393216，保持deepseek-flash/high；省略参数会采用服务端64K默认值，不能取消额度。重启后workflow须features.explicit_output_budget=true、requested_max_output_tokens=393216且execution_health.ready=true。task_result无公开末消息时，用liuren_adjudication_result(action="read",task_id=原子会话ID)领取已存结果或失败。仅完整读完且finish=length、无公开报告时，按next_call在同一子会话recover一次；不新建裁决、不把reasoning转成正文。仍无正文则明确未完成，不循环领取/重派。'
rel='docs/本机六壬高效执行.md';s=(ROOT/rel).read_text('utf-8');s=s.replace('活动方法为'+old,'活动方法为'+new);lines=s.splitlines();lines=[guide if line.startswith('28版：') else line for line in lines];(ROOT/rel).write_text('\n'.join(lines)+'\n','utf-8')
rel='README.md';s=(ROOT/rel).read_text('utf-8');s=s.replace('指向 `'+old+'`','指向 `'+new+'`');s+='\n本机30版显式申请裁决生成额度393,216 tokens，保持deepseek-flash/high，修正省略参数回落服务端64K默认值的问题。重启后新请求生效；实际长裁决仍待验证。说明见[额度修改说明](output/liuren-token-limit-audit-20261107/修改说明.md)。\n';(ROOT/rel).write_text(s,'utf-8')
replace('目录总索引.md','runtime/liuren/'+old+'/','runtime/liuren/'+new+'/')
rel='AGENTS.md';s=(ROOT/rel).read_text('utf-8');s+='\n\n30版额度修正：本机裁决显式请求max_tokens=393216，模型deepseek/deepseek-flash与high保留。此前省略客户端额度会回落DeepSeek high默认64K，不能再以provider_default_output_budget=true作为当前要求。workflow须execution_health.ready=true、features.explicit_output_budget=true且requested_max_output_tokens=393216。只扩大生成额度，不改变专业方法或交接链；重启OpenCode加载。\n';(ROOT/rel).write_text(s,'utf-8')
# Only transport guidance and release metadata differ inside the new runtime.
r=target/'references/deterministic-tools.md';lines=r.read_text('utf-8').splitlines();assert sum(l.startswith('28版：') for l in lines)==1;r.write_text('\n'.join(guide if l.startswith('28版：') else l for l in lines)+'\n','utf-8')
policy=load(target/'references/shensha-policy.json');assert policy['release']==old;policy['release']=new;dump(target/'references/shensha-policy.json',policy)
m=load(target/'manifest.json');c=load(target/'loader-contract.json')
for d in [p,m,c]:
 d['release']=new;d['authoringSource']=OUT.relative_to(ROOT).as_posix()
 if 'parentRelease' in d:d['parentRelease']=old
 d['adjudication'].update(maxOutputTokens=cap,outputBudgetPolicy='explicit-supported-maximum; avoid-provider-default-64K')
 d['outputRecovery'].update(noClientTokenCap=False,explicitMaxOutputTokens=cap,validation='request budget change; real long adjudication pending',evidence=OUT.relative_to(ROOT).as_posix()+'/native-adapter-capture-30.json')
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=new
 if 'computeInterface' in d:d['computeInterface']['release']=new
p.update(runtime=target.relative_to(ROOT).as_posix(),previousRelease=old,backup=backup.relative_to(ROOT).as_posix())
c['sourceHashes']={rel:sha(ROOT/rel) for rel in c['sourceHashes']};dump(target/'loader-contract.json',c)
m['files']={rel:sha(target/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(target/'manifest.json',m)
p['methodVersion']=m['version'];p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']};p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
temp=ROOT/'.opencode/liuren-active.output30.tmp';dump(temp,p);os.replace(temp,ROOT/'.opencode/liuren-active.json')
assert all(sha(source/rel)==value for rel,value in frozen.items())
for hashes,base in [(m['files'],target),(c['sourceHashes'],ROOT),(p['workflowImplementation'],ROOT),(p['bookRetrieval']['files'],ROOT)]:assert all(sha(base/rel)==value for rel,value in hashes.items())
changed=[rel for rel,value in frozen.items() if sha(target/rel)!=value]
assert set(changed)=={'manifest.json','loader-contract.json','references/deterministic-tools.md','references/shensha-policy.json'},changed
dump(OUT/'output-budget-activation.json',{'release':new,'previousRelease':old,'maxOutputTokens':cap,'model':p['adjudication']['model'],'reasoningEffort':'high','localOnly':True,'websiteChanged':False,'before':before,'after':{rel:sha(ROOT/rel) for rel in rels},'frozen29Intact':True,'runtimeChanges':changed,'methodBodiesUnchanged':True})
print('Activated local30; budget393216/high; hashes consistent; frozen29 intact')
