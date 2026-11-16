"""Publish reviewed basic Bifa to both local hosts; preserve frozen 41 bytes."""
from pathlib import Path
import json,hashlib,shutil,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
OLD='20261111-book-logic-41';NEW='20261111-basic-bifa-42'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
encode=lambda x:(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
pointer=load(ROOT/'.opencode/liuren-active.json');assert pointer['release']==OLD
base=ROOT/pointer['runtime'];runtime=ROOT/'runtime/liuren'/NEW
assert not runtime.exists() and not (OUT/'before.json').exists()
m=load(base/'manifest.json');assert all(sha(base/f)==h for f,h in m['files'].items())
frozen={p.relative_to(ROOT).as_posix():sha(p) for p in base.rglob('*') if p.is_file()}
early=['tools/liuren-chart-view.mjs','tools/liuren-core-handoff.mjs']
paths=['.opencode/liuren-active.json','opencode.json','.opencode/oh-my-opencode-slim.jsonc',
 'README.md','目录总索引.md','AGENTS.md','docs/本机六壬高效执行.md',
 'integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md',
 '.opencode/skills/liuren/daliuren/SKILL.md',*early]
for rel in paths:
 dest=OUT/'before'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 data=(ROOT/rel).read_bytes()
 if rel in early:
  text=data.decode('utf-8')
  if rel==early[0]:
   text=text.replace("import {scanBasicBifa} from './liuren-bifa-basic.mjs';\n",'').replace(' view.bifa_conditions=scanBasicBifa(view);\n','')
  else:
   text=text.replace("import {BASIC_BIFA_RULES_SHA256,loadedBasicBifaSha256} from './liuren-bifa-basic.mjs';\n",'')
   a=text.index(" const bifaFile='references/bifa-basic-evidence.json';");b=text.index(' const core=',a);text=text[:a]+text[b:]
   a=text.index('  if(/^BF-[DB]');b=text.index('  if(/^E',a);text=text[:a]+text[b:]
  # apply_patch preserved the original file's LF byte convention.
  data=text.encode('utf-8')
  if hashlib.sha256(data).hexdigest()!=pointer['workflowImplementation'][rel]:
   data=text.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
  assert hashlib.sha256(data).hexdigest()==pointer['workflowImplementation'][rel],rel
 dest.write_bytes(data)
for rel,h in pointer['workflowImplementation'].items():assert sha(OUT/'before'/rel if rel in early else ROOT/rel)==h,rel
(OUT/'before.json').write_bytes(encode({'release':OLD,'files':{f:sha(OUT/'before'/f) for f in paths},'frozen':frozen}))
shutil.copytree(base,runtime)
evidence='references/bifa-basic-evidence.json';shutil.copyfile(ROOT/'tools/liuren-bifa-basic-rules.json',runtime/evidence)
bundle=load(runtime/evidence)
rules=bundle['rules'];laws=sorted({r['law_number'] for r in rules})
guide='''# 基本毕法自动匹配（42版）

正式完整盘与裁决核心的 chart.bifa_conditions 自动提供已核结构。扫描独立于原引擎标签；使用实际选定的昼贵/夜贵天将，不把两模式候选混用。

采用32种结构，覆盖百法中的25法。每个新盘均检查全部32种；未匹配不硬填，未采用法及偏僻旁格不等于不存在。此范围不是百法全部正变类格已核完。

matches给出法号、结构、每项成立条件、实际坐标、课传位置、旬遁及旬空/坐空。evidence给连续书证及原书SHA；用material_id（如BF-D22）查本任务绑定原文，或module=bifa-basic-evidence查总证据。基本说明用module=bifa-basic。

结构成立与效力分层：空亡不删除结构，旺衰、墓败、真假、制救及时间依U01—U11综合；课传全阴不直接等于失败，生链不自动等于举荐，虎鬼不自动等于凶灾。同一支的财丁/财马、同一虎鬼及上下皆合的包含关系不重复计票。不凭题名补上缺失条件。

第22法按用户指定《大全》：上下皆合主格=两上六合并干寄宫与日支六合；上下俱合类格=各自纵向六合；只有两上合单独标记。不得混入北海同名横向定义。

递生/递克按北海先报告三传关系，另给终点与日干的关系及daquan_complete_chain。《大全》正格还要求终点生干/克干；标false时不得声称《大全》正格全成立。第27只取传脱旁例，不能改称传财化鬼。第47分贵人普通入狱、临身、入宅；第51须戌加亥且发用；第52原文不要求入传。第83须合局中神与干上或支上六合，任意三合局不算。第61墓虎取本段五行墓，不改通用天干十二长生。

未给年命，不扫描依赖年命的旁格。时间、贵人起法与天将坐标来自可信盘，不靠毕法标签反推。原始引擎毕法仅留独立审计，不加入matches。旧速查表用于检索，不作为已核条件表。

| 结构ID | 法 | 基本结构 | 已采用条件 |
| --- | ---: | --- | --- |
'''+''.join(f"| {r['id']} | {r['law_number']:02d} | {r['name']} | {r['definition']} |\n" for r in rules)
(runtime/'references/bifa-basic.md').write_text(guide,encoding='utf-8')
core='''## 第42版：基本毕法自动交接

完整盘中的 **bifa_conditions** 已按本盘实际昼夜扫描32种已核基本结构（涉及25法），独立于原引擎标签。主、子智能体均可直接读取matches中的成立条件、实际坐标、空亡及书证索引；无需手抄原引擎毕法。它们是结构关系，**不是吉凶判辞已成立**。依本问类神、气态、作用、制救和阶段选用；包含、重叠结构不重复计票。不自动采用未核旁格；未列出不等于其余百法不存在。决定性使用而条件不清时查bifa-basic或按BF-D/B编号查本任务连续书证。

第22法依用户指定《大全》，上下俱合为各自纵向六合。递生/递克另核终点到日干，daquan_complete_chain=false不能叫《大全》完整正格。第47普通贵入狱不补成临身例外；第51须戌加亥发用；第83须局中神与干/支上六合。旬空、坐空仍保留关系，效力另依U08/U10；不得以标题或匹配数量决定成败。本版不求收齐偏僻类格，不声称百法语义或预测已全面验收。
'''
def append(rel,text):
 p=runtime/rel;p.write_text(p.read_text('utf-8')+'\n\n'+text+'\n',encoding='utf-8')
p=runtime/'references/judgment-core.md';text=p.read_text('utf-8');head,rest=text.split('\n',1);p.write_text(head+'\n\n'+core+'\n'+rest,encoding='utf-8')
append('references/bifa.md','42版：本表仅作历史速查候选，自动采用以bifa_conditions及bifa-basic逐项条件为准。首尾相见的基本条件是干支上分见旬首旬尾，不是笼统“初末夹拱”；交接不会搬用本表一句话判辞。')
append('methods/adjudication.md','42版：完整核心chart.bifa_conditions自动交已核基本结构；依占类、位置、空实气态和制救挑选，不按标题定成败或重复计票。未核的原引擎标签不作为成格事实。条件不足按BF-D/B编号查绑定原文，说明见bifa-basic。')
append('methods/structure.md','42版：自动基本毕法在chart.bifa_conditions；仅32种结构、25法，未列出不是百法不存在。结构效力按共同方法判断，未核旁格暂不自动采用。详见bifa-basic。')
short='42版本机基本毕法（20261111-basic-bifa-42）：任意新盘自动独立核32种基本结构（涉及25法），按实际昼夜，成立条件、位置、空亡和连续书证随完整盘进入裁决核心bifa_conditions。第22依《大全》；标题不裁成败，未核偏僻旁格暂停。只限本机OpenCode/Codex新任务，重启OpenCode加载；旧盘/旧任务及模型不改，网站未发布。详见docs/基本毕法自动交接-42.md。'
pending={}
for rel in paths:
 if rel in early:continue
 if rel in ['.opencode/liuren-active.json','opencode.json','.opencode/oh-my-opencode-slim.jsonc']:continue
 text=(ROOT/rel).read_text('utf-8')
 if rel in ['README.md','目录总索引.md']:text=text.replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 pending[rel]=(text+'\n\n'+short+'\n').encode('utf-8')
cfg=load(ROOT/'opencode.json');models={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW).replace('runtime\\liuren\\'+OLD,'runtime\\liuren\\'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt']
assert models=={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()};pending['opencode.json']=encode(cfg)
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt'];pending['.opencode/oh-my-opencode-slim.jsonc']=encode(slim)
current_sha=lambda rel:hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(ROOT/rel)
contract={'id':'basic-bifa-42','structures':32,'representedLaws':25,'sourceSpans':27,'evidence':evidence,
 'actualModeOnly':True,'nativeLabelsTrusted':False,'coreField':'chart.bifa_conditions','all100LawsComplete':False,
 'scope':'local-opencode-and-codex','predictiveValidationCount':0}
pointer.update(release=NEW,runtime=runtime.relative_to(ROOT).as_posix(),previousRelease=OLD,backup='output/liuren-basic-bifa-20261111/before',authoringSource='output/liuren-basic-bifa-20261111',basicBifaIntegration=contract)
pointer['bookRetrieval']['compatibleMethodRelease']=NEW
pointer['files']={rel:current_sha('.opencode/skills/'+rel) for rel in pointer['files']}
mods={'bifa-basic':('references/bifa-basic.md','自动基本毕法条件、采用范围、层级和例外需解释'),
 'bifa-basic-evidence':(evidence,'毕法基本结构决定性使用需查连续原文或源身份')}
for name in ['manifest.json','loader-contract.json']:
 d=load(runtime/name);d.update(release=NEW,parentRelease=OLD,basicBifaIntegration=contract,authoringSource='output/liuren-basic-bifa-20261111')
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if name=='manifest.json':
  for id,(file,trigger) in mods.items():d['modules'][id]={'file':file,'required':False,'requires':[],'trigger':trigger};d['files'][file]=sha(runtime/file)
 else:d['sourceHashes']={rel:current_sha(rel) for rel in [*d['sourceHashes'],'tools/liuren-bifa-basic.mjs','tools/liuren-bifa-basic-rules.json']}
 (runtime/name).write_bytes(encode(d))
for name in ['references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='references/confirmed-policy-register.json':d['basicBifaIntegration']=contract
 if name=='reading-route.json':
  for id,(file,trigger) in mods.items():d['labels'][id]=trigger;d['conditional'][id]={'stage':2,'trigger':trigger,'selectWith':'--condition '+id,'beforeRequired':'adjudication'}
 (runtime/name).write_bytes(encode(d))
m=load(runtime/'manifest.json');route=load(runtime/'reading-route.json');m['required']=[id for stage in route['stages'] for id in stage['required']];m['conditional']={id:item['trigger'] for id,item in route['conditional'].items()}
m['files']={rel:sha(runtime/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(runtime/'manifest.json').write_bytes(encode(m))
pointer['methodVersion']=m['version'];pointer['workflowImplementation']={rel:current_sha(rel) for rel in [*pointer['workflowImplementation'],'tools/liuren-bifa-basic.mjs','tools/liuren-bifa-basic-rules.json']}
pending['.opencode/liuren-active.json']=encode(pointer)
for rel in sorted(pending,key=lambda rel:rel=='.opencode/liuren-active.json'):
 target=ROOT/rel;temp=target.with_name(target.name+'.bifa42.tmp')
 with temp.open('xb') as h:h.write(pending[rel])
 os.replace(temp,target)
assert all(sha(ROOT/f)==h for f,h in frozen.items())
(OUT/'after.json').write_bytes(encode({'release':NEW,'files':{f:sha(ROOT/f) for f in paths},'rules_sha256':sha(ROOT/'tools/liuren-bifa-basic-rules.json'),'old_runtime_unchanged':True}))
print('Activated',NEW,'; frozen 41 unchanged; restart OpenCode for new tasks')
