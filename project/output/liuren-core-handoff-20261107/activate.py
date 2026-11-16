from pathlib import Path
import copy,hashlib,json,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];old='20261107-slim-30';new='20261107-slim-31';R=ROOT/'runtime/liuren'/new
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
def write(rel,text):(ROOT/rel).write_text(text,encoding='utf-8',newline='')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']==old
m=load(R/'manifest.json');c=load(R/'loader-contract.json');route=load(R/'reading-route.json')
details=['positioning','liqi','structure','void','shensha-use','movement']
triggers={id:'共用规范不足以确认影响本问的'+label+'条件或反证时定点查阅' for id,label in zip(details,['取用','有效作用','结构','空亡','神煞义项','动态'])}
for id in details:m['modules'][id]['required']=False;m['modules'][id]['trigger']=triggers[id];m['conditional'][id]=triggers[id]
m['modules']['judgment-core']={'file':'references/judgment-core.md','required':True,'requires':[],'trigger':'主智能体与裁决者共用的简明规范，原方法按具体缺口查'}
m['required']=['judgment-core','adjudication','report']
route['labels']['judgment-core']='共用判断规范';route['stages']=[{'id':1,'title':'原问、完整盘与本问专项','required':['judgment-core'],'action':'先读共用规范和本问domain，详细方法按具体缺口查'},{'id':2,'title':'必要补核与核心交接','required':[],'action':'条件不清、反证冲突或摘要不足才定点查方法/原书，不整库通读'},{'id':3,'title':'独立裁决与交付','required':['adjudication','report'],'action':'核心必读、来源按需，返回核对后忠实交付；report在交付前读'}]
for id,trigger in triggers.items():route['conditional'][id]={'stage':2,'trigger':trigger,'selectWith':'--condition '+id,'beforeRequired':'adjudication'}
for row in route['conditional'].values():
 if row.get('beforeRequired') in details:row['beforeRequired']='judgment-core'
route['domainAfter']='judgment-core';route['labels']['adjudication']='核心交接与独立裁决';dump(R/'reading-route.json',route)
policy=load(R/'references/shensha-policy.json');policy['release']=new;dump(R/'references/shensha-policy.json',policy)
compact={'enabled':True,'schema':'liuren-reading-core-v1','storage':'core file plus hash-bound full archive','mandatoryRead':'core only','referenceRead':'bound material_id/module on demand','fullChartRetained':True,'sourceSelection':'model; program verifies bound provenance','predictiveValidationCount':0}
for d in [p,m,c]:
 d['release']=new;d['authoringSource']=OUT.relative_to(ROOT).as_posix();d['compactHandoff']=copy.deepcopy(compact)
 if 'parentRelease' in d:d['parentRelease']=old
 if 'computeInterface' in d:d['computeInterface']['release']=new
 d['adjudication']['inputTransport']='core-with-bound-reference-archive';d['adjudication']['readerPolicy']='read complete core; scoped references on demand'
 d['toolUsage']['toolContract']='liuren-tools-31'
 d['outputRecovery']['validation']='core protocol regression and synthetic host validation; real long adjudication pending'
 d['outputRecovery']['evidence']=OUT.relative_to(ROOT).as_posix()+'/validation.json'
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=new
p.update(runtime=R.relative_to(ROOT).as_posix(),previousRelease=old,backup=(OUT/'before').relative_to(ROOT).as_posix())
# Active guides replace old mandatory-all prose. Historical evidence remains untouched.
write('docs/本机六壬高效执行.md','''# 本机六壬执行接续

当前本机31版，工具契约liuren-tools-31。只在本机生效，模型deepseek/deepseek-flash/high及显式max_tokens=393216保留。

1. 原问与可信盘：liuren_chart或复用可靠同盘archive；固定算法不重核。读judgment-core、本问domain与adjudication；原positioning/liqi/structure/void/shensha-use/movement等详细方法按具体疑点补查，不再固定8项通读。采用年命查nianming，应期/数量按原问tasks，迟速比较不自动展开完整应期。
2. 准备中性材料：facts仅补现实事实或来源身份，observations只保留必要观察，不复述程序表、不先写完整裁决。候选取用可纠正，focus_issues只列真实未决处。method_modules和原书handoff作为备查索引，不为完整性扩资料。
3. packet程序保存核心文件及hash绑定的完整存档；仅把task_prompt原样交新task，不用旧task_id或background。默认reader首次page=1,page_count=4，按next_call读完核心即可裁决。决定性条件不清、反证冲突或摘要不足，再用同一reader的material_id查原书/E01—E22，module查详细方法。文件路径/hash沿用本任务，不能任意读其他文件。
4. 来源索引不等于阅读清单。参考分页用于读全所采用段落；未打开的其他参考不阻止submit。核心仍须完整真实传输；截断回执不计读完。程序校验归属、hash及传输，不裁专业效力。
5. 裁决者submit完整正文或自由JSON，末消息只回回执。主智能体按子会话task_id领取，读report后result deliver完整交付；核事实/引用/覆盖/一致性，不再折中改判。ID丢失先locate，格式repair；具体事实/引用错误且补真实新材料才一次补核。

重启OpenCode，在本目录新建会话选liuren。首次workflow确认execution_health.ready=true及features.core_handoff/on_demand_sources=true，工具契约31；旧进程不新派发。无需每次运行命令。

已有历史任务按原文件协议领取；新协议只强制核心读取。finish=length无正文时仅原子会话recover一次，running不重派、不用reasoning代正文。完整使用与异常处理见[稳定运行指南](本机六壬稳定运行指南.md)。
''')
write('docs/本机六壬完整研判流程.md','''# 本机六壬完整研判流程

当前31版以.opencode/liuren-active.json为准。核心目的：依原问、可信完整盘和占类专法取用，裁关键有效作用及最强反证，逐问完整回答。

1. 明确实际对象、事件阶段、期限、成功标准和条件分支，取得或复用程序盘。先读judgment-core及本问domain，在同一主线中合看课传、气态、空墓、神将、神煞、动态和制救；候选不冻结结论。
2. 主智能体读adjudication，整理必要现实事实、候选取用和真实争点。详细通用方法/原书只按条件不清、反证冲突或摘要不足查；全文保留，参考不是固定待办。年命、应期、数量按实际需要触发。普通研判不调用案例库/经验库或旧缓存，不以原案反馈作本案事实。
3. 程序从可信归档装完整盘，生成紧凑核心与来源索引，并另存hash绑定完整档案。裁决者默认读完整核心；需要时用reader的material_id/module查原文，条件明确后独立裁决，不强制通读参考库。完整盘保留以独立查漏，主智能体观察可纠正。
4. 裁决者submit正文或自由JSON，主智能体核事实、引用、覆盖和一致性，读report后领取并忠实交付。具体新事实/引用错误才一次补核，格式差异不重裁。

固定排盘/神煞公式不重算；正常年命/行年和长期占事保留，出生推命及出生运限不进入占事。主智能体准备必读共用规范、交接及本问专项；report交付前读，原六项通用细则按真实疑点调用。

同卦复用可靠盘、同版资料和已核节点；新定位或有效反证回核受影响结论。不统一无关异说、不凑吉凶数票，不把工程通过当作专业或预测正确。工具接续见[高效执行](本机六壬高效执行.md)，只在本机生效。
''')
guide=ROOT/'docs/本机六壬稳定运行指南.md';text=guide.read_text('utf-8');a=text.index('## 一条完整主线');b=text.index('## 工具与MCP的分工');text=text[:a]+'''## 核心交接主线

先读judgment-core、本问domain及adjudication；详细通用方法/原书按具体疑点查。可信盘→必要取用和中性材料→packet核心文件→裁决者读核心、来源按需→submit→主智能体领取核对→读report并deliver。

新packet返回reading.view=core。主文件只含完整盘、紧凑程序表、共用规范、专项、必要候选及参考索引；全文另存绑定hash的archive。reader默认核心，参考用material_id或module，始终沿用同一file_path/sha256。参考阅读不计核心页，不要求逐条读参考。具体段落用于决定性判断前应理解完整条件。

初次workflow须tool_contract=liuren-tools-31，features.core_handoff/on_demand_sources及execution_health.ready均为true。新进程才会加载新工具；旧文件按原协议领取，不为升级重派历史裁决。工程健康检查可选，正常直接在liuren提问。

'''+text[b:];text=text.replace('完整读完、finish=length','核心完整读完、finish=length');guide.write_text(text,'utf-8')
for rel in ['README.md','目录总索引.md']:
 f=ROOT/rel;text=f.read_text('utf-8').replace('runtime/liuren/'+old+'/','runtime/liuren/'+new+'/').replace('指向 `'+old+'`','指向 `'+new+'`');
 if rel=='README.md':
  text=text.replace('共用资料8项，16占类专项及应期、数量、年命按问触发','共用judgment-core与本问专项为阅读主干，详细方法、原书及应期/数量/年命按需要触发')
  text+='\n本机31版启用核心交接与按需查证，裁决者只强制读完整核心；原书/详细方法另存可查。使用见[高效执行](docs/本机六壬高效执行.md)，验收见[新版说明](output/liuren-core-handoff-20261107/修改说明.md)。\n'
 f.write_text(text,'utf-8')
f=ROOT/'AGENTS.md';f.write_text(f.read_text('utf-8')+'''\n\n31版当前执行规则（覆盖上方历版关于8项/14项通读和裁决全部材料必读的要求）：主智能体准备读judgment-core、adjudication及本问domain，report在交付前读。原positioning/liqi/structure/void/shensha-use/movement及全部专业方法全文保留，按真实条件缺口、反证冲突或摘要不足定点查。原书只交必要handoff备查，不复述整盘、不为交接先写完整裁决。程序保存紧凑核心与hash绑定完整存档；reader默认完整核心，参考用material_id（含固定E01—E22）或module按需查。只强制核心完整传输；参考不是待办清单，必要段落查明条件再用于决定性判断。候选取用可纠正，完整盘用于独立查漏。无两库、原书来源身份、完整自由报告及最强反证保留。工具契约liuren-tools-31，workflow须execution_health.ready=true及features.core_handoff/on_demand_sources=true。模型deepseek-flash/high、max_tokens393216不变；只在本机，重启加载，旧任务按原文件协议领取。\n''','utf-8')
# Refresh all identities only after the content has reached its final shape.
newSource='tools/liuren-core-handoff.mjs';c['sourceHashes'][newSource]=sha(ROOT/newSource);p['workflowImplementation'][newSource]=sha(ROOT/newSource)
c['sourceHashes']={rel:sha(ROOT/rel) for rel in c['sourceHashes']};dump(R/'loader-contract.json',c)
m['files']['references/judgment-core.md']=sha(R/'references/judgment-core.md');m['files']={rel:sha(R/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(R/'manifest.json',m)
p['methodVersion']=m['version'];p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']};p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']};p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
temp=ROOT/'.opencode/liuren-active.core31.tmp';dump(temp,p);os.replace(temp,ROOT/'.opencode/liuren-active.json')
before=load(OUT/'before.json');assert all(sha(ROOT/'runtime/liuren'/old/rel)==h for rel,h in before['frozen30'].items())
dump(OUT/'activation.json',{'release':new,'previousRelease':old,'localOnly':True,'websiteChanged':False,'before':before['files'],'after':{rel:sha(ROOT/rel) for rel in before['files']},'newFiles':[newSource],'frozen30Intact':True,'realModelValidation':'pending'})
print('Activated local31 with core protocol; frozen30 intact')
