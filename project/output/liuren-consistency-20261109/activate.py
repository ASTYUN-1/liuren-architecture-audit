"""Publish local consistency checks. Frozen runtimes and existing runs are retained."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
NEW='20261109-consistency-39'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
before=load(OUT/'before.json')
pointer=load(ROOT/'.opencode/liuren-active.json')
OLD=pointer['release']
assert OLD=='20261109-deepseek-child-38'
assert all(sha(ROOT/rel)==h for rel,h in before['frozen'].items())
runtime=ROOT/'runtime/liuren'/NEW
assert not runtime.exists()
shutil.copytree(ROOT/pointer['runtime'],runtime)
note=('39版一致性核对：新任务保留原问与input_review来源身份；子报告附简短audit，登记关键作用、最强反证与真实计算覆盖。'
      '局部补算不能冒充综合结果。主智能体read核对后用review登记事实身份、职责阶段、计算范围、反证、逐问约束五项；'
      '有具体原句和绑定证据才用原子会话recheck一次，保留前后报告，未解决缺口显式交付，不另派或自行改判。'
      '程序不选类神、不裁成败、不设分数阈值，正文仍自由表达。专业方法与模型选择沿用38版；网站未发布。'
      '接口见docs/本机六壬一致性核对-39.md。')
for rel in ['references/judgment-core.md','methods/adjudication.md','references/deterministic-tools.md','methods/report.md']:
    p=runtime/rel
    assert p.exists(),rel
    p.write_text(p.read_text('utf-8')+'\n\n## 第39版执行核对\n\n'+note+'\n',encoding='utf-8')
guide=runtime/'references/consistency-audit.md'
guide.write_bytes((ROOT/'docs/本机六壬一致性核对-39.md').read_bytes())

cfg=load(ROOT/'opencode.json')
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW).replace('runtime\\liuren\\'+OLD,'runtime\\liuren\\'+NEW))
cfg['agent']['liuren']['prompt']+='\n'+note+'\nreview参数须含当前report_sha256和五项checks；每项check/status(checked或unresolved)/report_quote/basis。recheck findings每项附check/report_quote/evidence_refs/evidence/request。'
write(ROOT/'opencode.json',cfg)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')
child=slim['agents']['liuren-adjudicator']
child['permission']['liuren_adjudication_audit']='allow'
child['prompt']+='\n\n## 第39版一致性附件\n'+note+'\n新任务以绑定核心consistency_guide和工具schema填写audit。可liuren_adjudication_audit先取receipts或check。submit同时给result正文和audit；成功只回回执。若收到LIUREN_CONSISTENCY_RECHECK_V1，仅补具体证据缺口并再次submit，不从头重裁；可以有依据地保留原判，未知阶段不得包装成用户事实。'
write(ROOT/'.opencode/oh-my-opencode-slim.jsonc',slim)
for rel in ['AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬稳定运行指南.md','integrations/codex/daliuren-codex/references/host.md']:
    p=ROOT/rel;t=p.read_text('utf-8')
    if rel in ['README.md','目录总索引.md']:
        t=t.replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
    p.write_text(t+'\n\n'+note+'\n',encoding='utf-8')

policy={'schema':'liuren-consistency-audit-v1','enabled':True,'maxRechecks':1,'guide':'docs/本机六壬一致性核对-39.md','scope':'local-opencode-and-codex','professionalContentChecked':False,'predictiveValidationCount':0}
pointer.update(release=NEW,runtime=runtime.relative_to(ROOT).as_posix(),previousRelease=OLD,backup='output/liuren-consistency-20261109/before',authoringSource='output/liuren-consistency-20261109',consistencyAudit=policy)
pointer['workflowImplementation']['tools/liuren-consistency-audit.mjs']=sha(ROOT/'tools/liuren-consistency-audit.mjs')
pointer['adjudication']['consistencyAudit']=policy
pointer['flowControl']['submissionPolicy']='free report plus compact evidence attachment for new runs; main delivery review; one same-child recheck'
for name in ['manifest.json','loader-contract.json']:
    data=load(runtime/name)
    data.update(release=NEW,parentRelease=OLD,authoringSource='output/liuren-consistency-20261109',consistencyAudit=policy,adjudication=pointer['adjudication'])
    if 'bookRetrieval' in data:data['bookRetrieval']['compatibleMethodRelease']=NEW
    if name=='loader-contract.json':
        data['sourceHashes']['tools/liuren-consistency-audit.mjs']=sha(ROOT/'tools/liuren-consistency-audit.mjs')
        data['sourceHashes']={rel:sha(ROOT/rel) for rel in data['sourceHashes']}
    else:
        data['modules']['consistency-audit']={'file':'references/consistency-audit.md','required':False,'requires':[],'trigger':'39版输入来源、报告附件与交付核对接口缺口'}
        data['files']['references/consistency-audit.md']=sha(guide)
    write(runtime/name,data)
for name in ['references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
    data=load(runtime/name);data['release']=NEW;write(runtime/name,data)
manifest=load(runtime/'manifest.json')
manifest['files']={rel:sha(runtime/rel) for rel in manifest['files']}
manifest['version']=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest()
write(runtime/'manifest.json',manifest)
pointer['methodVersion']=manifest['version']
pointer['workflowImplementation']={rel:sha(ROOT/rel) for rel in pointer['workflowImplementation']}
pointer['bookRetrieval']['compatibleMethodRelease']=NEW
write(ROOT/'.opencode/liuren-active.json',pointer)
assert all(sha(ROOT/rel)==h for rel,h in before['frozen'].items())
write(OUT/'integrity.json',{'frozen38Unchanged':True,'newRelease':NEW,'modelsUnchanged':True,'calculationAlgorithmsUnchanged':True,'predictiveValidationCount':0})
print('Activated',NEW,'for new local tasks; restart OpenCode')
