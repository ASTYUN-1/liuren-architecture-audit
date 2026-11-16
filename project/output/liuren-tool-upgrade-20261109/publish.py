"""Publish the local tool layer; preserve the former frozen runtime byte-for-byte."""
from pathlib import Path
import json,hashlib,shutil,os,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
OLD='20261109-palace-strength-34';NEW='20261109-deterministic-tools-35'
R=ROOT/'runtime/liuren'/NEW;BASE=ROOT/'runtime/liuren'/OLD
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def dump(p,d):write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
before=load(OUT/'before.json')
assert all(sha(BASE/rel)==digest for rel,digest in before['frozen'].items()),'frozen34 changed'
p=load(ROOT/'.opencode/liuren-active.json')
refresh='--refresh' in sys.argv
assert p['release']==(NEW if refresh else OLD)
policy='''## 35版确定性工具层（主、子共同执行）

AI依原书取用、选法和裁决，工具提供确定性计算，不自动选择应期或裁成败。月令五气、十二气、空亡位置与综合旺衰分数分别保留，不能用分数重写原始状态。

取数先用liuren_compute(action="methods",methods={kind:"quantity"})查具名方法和必填条件，再用action="quantity"及quantity_method调用；expression仍兼容但不与具名方法混用、不无据叠加倍率。工具读取盘面和本法数表，不能凭量级候选或base-only基础数冒充最终数量。方法适用性、单位及量级依据由AI确定；程序数值直接采信，不重复手算。首批CY501-use-ground、WY244-month为明确分支，WY67-shenjiang-base、WY242-generated-base仅基础步。

calendar复用排盘引擎历法，支持节气/节月/旬界/日界准确时刻、值冲合筛选及日内采样；日柱与时干共用所选00:00/23:00日界。出原旬与旬名重复分开，关系事实不等同已经填实或冲开。evaluation将指定日历时间交给单宫/明确取用关系的旺衰计算，原盘坐标及原日干不变，不自动选择最高分日期为应期。

空亡系数和现行直接作用范围保持34版；evaluation默认original保留原空亡，仅按评价节月更新五气；evaluation-xun-research是新旬替换的明确研究情景，不是已经定案的出旬/冲实算法，不能按结果切换政策。三合、半合、三会数值继续暂缓。

需要辨物态时先methods(kind="imagery")查适用原段，再以imagery返回材质、新旧、阶段、空实等条件候选；没有匹配不等于无物或失败，射覆专法不直接推广成人事成败。专业报告仍自由撰写，不增固定裁决字段。详细参数见deterministic-tools；默认盘不附整套数法、判辞和审计。
'''
short='35版确定性工具层：工具只查盘、查表、计算和枚举时间，AI依原法取用、选法与裁决。取数/取象先methods查方法，按quantity_method/imagery调用；evaluation接日历与旺衰，不裁应期。空亡系数沿用34版，三合等数值暂缓。主、子共读judgment-core；详见deterministic-tools。'
newtools=['tools/liuren-calendar-v2.mjs','tools/liuren-method-tools.mjs','tools/liuren-method-registry.json','tools/liuren-time-evaluation.mjs']
if not refresh:
 assert not R.exists(),'candidate exists; do not overwrite'
 shutil.copytree(BASE,R)
 for rel in ['references/judgment-core.md','references/confirmed-judgment-policy.md','references/adjudicator-prompt.md']:
  f=R/rel;write(f,f.read_text('utf-8')+'\n\n'+policy)
 guide=(ROOT/'docs/确定性工具使用说明-35.md').read_text('utf-8')
 for rel in ['references/deterministic-tools.md','methods/quantity.md','methods/timing.md']:
  f=R/rel;write(f,f.read_text('utf-8')+'\n\n'+(guide if rel.endswith('deterministic-tools.md') else policy))
 for rel in ['.opencode/skills/liuren/daliuren/SKILL.md','integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md']:
  f=ROOT/rel;write(f,f.read_text('utf-8')+'\n\n'+short+'\n')
 cfg=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');cfg['agents']['liuren-adjudicator']['prompt']=(R/'references/adjudicator-prompt.md').read_text('utf-8');dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',cfg)
 cfg=load(ROOT/'opencode.json');cfg['agent']['liuren']['prompt']+='\n'+short;dump(ROOT/'opencode.json',json.loads(json.dumps(cfg,ensure_ascii=False).replace(OLD,NEW)))
 for rel in ['AGENTS.md','README.md','目录总索引.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/Codex大六壬工作流.md']:
  f=ROOT/rel;s=f.read_text('utf-8').replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
  write(f,s+'\n\n35版本机工具升级（'+NEW+'）：'+short+' 使用说明见docs/确定性工具使用说明-35.md；回滚见output/liuren-tool-upgrade-20261109/rollback.py。\n')
 for rel in ['references/shensha-policy.json','reading-route.json','references/confirmed-policy-register.json']:
  f=R/rel;d=load(f);d['release']=NEW;dump(f,d)
 p.update(release=NEW,runtime=R.relative_to(ROOT).as_posix(),previousRelease=OLD,backup=(OUT/'before').relative_to(ROOT).as_posix(),authoringSource=OUT.relative_to(ROOT).as_posix())
 p['computeInterface'].update(release=NEW,methodQuantity=True,conditionalImagery=True,timeEvaluation=True,calendarBoundaries=True)
 p['deterministicToolUpgrade']={'release':NEW,'source':'docs/确定性工具使用说明-35.md','voidCoefficientsChanged':False,'groupNumericEffects':False,'predictiveValidationCount':0,'scope':'local-opencode-and-codex'}
 for rel in newtools:p['workflowImplementation'][rel]=sha(ROOT/rel)
if refresh:
 f=R/'references/deterministic-tools.md';marker='\n\n# 35版确定性工具使用说明'
 s=f.read_text('utf-8');assert marker in s
 write(f,s.split(marker,1)[0]+'\n\n'+(ROOT/'docs/确定性工具使用说明-35.md').read_text('utf-8'))
wire_path=OUT/'current-wire.json'
if wire_path.exists():
 wire=load(wire_path)
 assert wire['exitCode']==0 and wire['requests'] and wire['realModelCalled'] is False
 assert all(sha(ROOT/rel)==digest for rel,digest in wire['implementationSha256'].items())
 p['computeInterface'].update(transportEvidence=wire_path.relative_to(ROOT).as_posix(),transportValidation='fresh native OpenCode outbound schema to loopback synthetic provider; upgraded native/Codex execution covered separately')
for file in ['loader-contract.json','manifest.json']:
 d=load(R/file);d.update(release=NEW,parentRelease=OLD,authoringSource=OUT.relative_to(ROOT).as_posix())
 d['computeInterface'].update(p['computeInterface'])
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if file=='loader-contract.json':
  for rel in newtools:d['sourceHashes'][rel]=sha(ROOT/rel)
  d['sourceHashes']={rel:sha(ROOT/rel) for rel in d['sourceHashes']}
 dump(R/file,d)
m=load(R/'manifest.json');m['files']={rel:sha(R/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(R/'manifest.json',m)
p['methodVersion']=m['version'];p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
if 'bookRetrieval' in p:
 p['bookRetrieval']['compatibleMethodRelease']=NEW;p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
assert sha(ROOT/'tools/liuren-strength-profile.json')==before['strength_profile_sha256'],'strength/void parameters changed'
tmp=ROOT/'.opencode/liuren-active.tool35.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
dump(OUT/'activation.json',{'release':NEW,'previous':OLD,'methodVersion':m['version'],'frozen34Intact':True,'voidCoefficientsChanged':False,'paidModelCalls':0,'predictiveValidationCount':0})
dump(OUT/'after.json',{'files':{rel:sha(ROOT/rel) for rel in before['files']},'new_tools':{rel:sha(ROOT/rel) for rel in newtools}})
print('Refreshed' if refresh else 'Activated',NEW)
