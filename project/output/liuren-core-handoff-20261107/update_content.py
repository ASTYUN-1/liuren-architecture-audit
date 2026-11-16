from pathlib import Path
import json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];R=ROOT/'runtime/liuren/20261107-slim-31'
def write(rel,text):(ROOT/rel).write_text(text,encoding='utf-8',newline='')
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def replace(rel,a,b):
 p=ROOT/rel;s=p.read_text('utf-8');assert a in s,(rel,a);p.write_text(s.replace(a,b),encoding='utf-8',newline='')
skill='''---
name: daliuren
description: 使用可信程序课盘完成大六壬占事研判，核心交接、按需查证、独立裁决并完整交付。
---

# 大六壬占事

主线：原问与可信盘→依问取用及有效作用→核心交接→独立裁决→核对交付。

1. 理解实际事件、对象、阶段、期限、成功标准及条件分支；取得或复用liuren_chart的archive。读judgment-core及本问domain，依简明规范综合取用、完整课传、气态、空墓、神将、神煞、动态及最强反证。固定排盘/神煞起法直接用程序；初势不冻结成败。
2. 详细通用方法和原书按具体疑点查，不再固定通读原8模块。决定性规则条件不清、反证冲突或摘要不足时，查相应模块/连续原段。应期、数量、年命按实际需要；只给占时或比较迟速不自动要求整套应期取数。原方法全文保留可查，同版同上下文已读复用，不统一无关异说。
3. 读adjudication后准备中性材料：facts仅补现实事实或来源身份，不重复整盘；entities写候选取用与简短理由；observations仅留影响本问且程序表未表达的必要观察；focus_issues只列真实未决处，无则[]。method_modules只列确需备查的模块，原书交精确handoff，不复制章节。程序生成完整盘与核心、来源索引；参考正文另存，不作为裁决必读。
4. packet返回task_prompt原样交新task，裁决者按next_call读完核心，必要时用同一reader的material_id/module定点读原文，可从完整盘补漏。参考不是强制阅读清单。主智能体返回只核事实、引用、问项覆盖和一致性，不重新权衡折中；读report后按回执领取完整正文。

准备必读judgment-core、adjudication及本问domain；report在交付前读。详细positioning/liqi/structure/void/shensha-use/movement及其他专项均保留，按真实缺口触发。16占类沿用当前manifest；时间任务查timing，数量查quantity，数表缺口查quantity-sources，采用年命查nianming。

保留占类专法对待轴、完整盘查漏、有效制救与最强反证；类象按对象、位置、气态和条件参与结果，不凭名象数票。普通研判不检索案例/经验库、旧缓存或现实反馈；知识维护另走liuren-cases/liuren-extract。正常年命/行年保留，出生推命及运限退出占事。

参数不明查liuren_tool_help；成功按next_call接续。工具契约liuren-tools-31，workflow须execution_health.ready及features.core_handoff/on_demand_sources为true。工程校验不证明专业或预测效果。
'''
write('.opencode/skills/liuren/daliuren/SKILL.md',skill);(R/'entry.md').write_text(skill,'utf-8')
adjudication='''# 核心交接与独立裁决

准备到可裁决即可：可靠盘、原问、候选取用、必要观察及真实未决处；不先写完整裁决，不为交接穷举矛盾。facts仅补现实事实和来源身份，不复述程序盘；observations避免重复程序状态。focus_issues保持中性，不限定裁决者查漏范围，无真实争点填[]。

主智能体读judgment-core及本问domain；详细通用方法、原书只按真实缺口查。method_modules列确需备查的ID，method_materials交精确来源handoff，quote可省略。程序保留完整引用及hash，单独保存完整存档；裁决入口仅传核心和索引。固定起法直接使用，原书摘要不能当作已核全文。

每问domain/tasks/task_basis依原问，user_requested附逐字request_quote，必要附属任务说明理由。只给占时不增加应期，迟速对比不自动加载完整定期法。课盘传liuren_chart原样archive，不手抄盘。branch仅干支或合法组合，理由放mapping_basis；verification仅method_interpretation/unverified。

1. packet保存后task_prompt原样给新task(subagent_type="liuren-adjudicator")；不传长JSON、旧task_id或background。
2. 裁决者reader默认读核心，首次page=1,page_count=4，按next_call读完核心。完整盘用于查漏，候选可纠正；有具体疑点时reader带material_id读原书，或module读详细方法，用原file_path/sha256。参考可分页，若采用某段为关键依据须理解完整所选段的条件；不遍历来源索引。只核核心传输，不要求所有参考读完。
3. 独立裁关键效力、制救、最强反证及逐问答案；submit完整Markdown正文或自由JSON，缺必要资料可needs_input。无固定专业字段。格式错误只修对应字段或同一正文，最多三次，不重新裁决。成功末消息只回回执。
4. 主智能体按回执task_id调用task_result，读report后result deliver取绑定hash的完整正文；只核事实/引用/覆盖/一致性，忠实交付，不重判。ID丢失先locate，不猜编号；格式故障repair。仅具体事实/引用错误或needs_input且补真实新材料，才按retry_context一次补核。

仅核心完整读取仍无正文且finish=length时，按next_call在原子会话recover一次；不重派，不用reasoning代正文。旧协议文件保持旧读取规则及领取能力。详细接口见references/deterministic-tools.md。
'''
(R/'methods/adjudication.md').write_text(adjudication,'utf-8')
slimPath=ROOT/'.opencode/oh-my-opencode-slim.jsonc';slim=json.loads(slimPath.read_text('utf-8'));agent=slim['agents']['liuren-adjudicator']
old=agent['prompt'];tail=old[old.index('## 裁决依据'):]
agent['prompt']='''# 大六壬独立裁决者

依据原问、完整程序盘、judgment-core及本问domain独立裁关键作用和结果。主智能体候选可纠正，争点不是封闭范围；从完整盘查漏。固定程序排盘/神煞直接用，不重起算法，不统一无关异说，不读案例/经验库、其他任务或现实反馈。

liuren_adjudication_read首次page=1,page_count=4，默认读取本任务核心；依next_call读完核心。references仅为按需索引，不须逐项打开。摘要不足以确认决定性规则条件、反证冲突或发现新关键问题时，用同一工具material_id读绑定原书材料/E01—E22，或module读版本固定的详细方法；每次沿用task给出的file_path/sha256，不使用通用read或自行编路径。原文若分多页，采用前读全所选段，保留适用条件及例外。工程只核核心传输，不为完成参考清单而扩大阅读。

程序表覆盖全部十二支与十干。表列图例说明参照，不能把主智能体facts/observations当程序确认。需要新对象状态或日期算式可liuren_compute；不手算日期，不编数值。原书查证经reader完成，compute只查询计算。每个关键作用说明对象位置、双方状态、通路、结果环节和最强反证；真实缺口保留具体条件/精度，不自动降档，不反复同材自辩。

提交liuren_adjudication_submit({result:完整Markdown正文字符串或自由JSON对象})，保留取用、关键作用、反证、逐问答案及实际来源；无固定分析字段。缺必要资料可needs_input。格式错只修对应字段或转同一正文，最多三次，不重新全盘权衡。成功末消息只回工具回执，由主智能体领取交付。

'''+tail
agent['description']='大六壬独立裁决：核心必读，完整盘查漏，原书及详细方法按需查证，自由正文交付。';dump(slimPath,slim)
cfgPath=ROOT/'opencode.json';cfg=json.loads(cfgPath.read_text('utf-8'));cfg['agent']['liuren']['prompt']='本机大六壬占事：加载当前daliuren，先读judgment-core及本问domain，详细方法和原书按具体缺口查。可信程序盘→按问取用及有效作用→核心交接→独立裁决→核对交付。准备阶段读adjudication，facts不复述整盘，observations只放必要观察，不先完成裁决；原书交精确handoff备查。裁决者读完整核心，参考按material_id/module查证，不把来源索引当必读清单。返回只核事实/引用/问项覆盖/一致性，读report后忠实交付。普通研判不调用案例/经验库或旧缓存；正常年命/行年保留，时间数量按实际tasks。参数不明查tool_help，按next_call；开发排障切Build。';dump(cfgPath,cfg)
rel='.opencode/plugins/liuren-adjudication.ts'
replace(rel,"tool_contract:'liuren-tools-25'","tool_contract:'liuren-tools-31'")
replace(rel,'features:{full_page_batch:4,','features:{core_handoff:pointer.compactHandoff?.enabled===true,on_demand_sources:pointer.compactHandoff?.enabled===true,full_page_batch:4,')
replace(rel,"'裁决者依read.next_call逐页读完，再submit正文或自由对象'","'裁决者依read.next_call读完核心，原书material_id/详细方法module按需查，再submit正文或自由对象'")
replace(rel,'原书及其他精确来源','原书及其他精确来源') if False else None
replace(rel,'应期取数全文由tasks自动装入。','应期取数由tasks选入参考索引，不强制裁决者读完整章。')
replace(rel,'已实际读完的当前方法模块ID，如liqi、void、promotion-salary；程序按当前manifest装配全文和hash，无需逐条手写路径。','确需备查的当前方法模块ID，如liqi、void、promotion-salary；程序归档全文/hash，核心只列索引，不要求全读。')
replace(rel,'先读完本次材料；成功回小回执','先读完核心，参考按需查证；成功回小回执')
replace(rel,'workflow返回当前版本、缺读模块和下一步','workflow返回当前版本、准备核心/专项的缺读项和下一步')
replace(rel,'所有必需方法和分类全文真实读完后保存。','准备阶段judgment-core、adjudication及本问domain读完后保存；详细方法/原书按具体缺口查。')
replace(rel,'已随裁决提示加载的固定书据不重抄。','固定书据及详细方法不重抄；核心附索引，原文按需查。')
replace(rel,"read:'限定本任务文件/hash/页码'","read:'核心必读；绑定来源ID/module按需查，校验本任务文件/hash/页码'")
replace('tools/liuren-preflight.py',"  record('durable flow enabled'", "  record('compact handoff enabled',pointer.get('compactHandoff',{}).get('enabled') is True)\n  record('durable flow enabled'")
# Legacy protocol regression harness deliberately remains legacy; new protocol has separate tests.
replace('tools/tests/liuren-flow-control.test.mjs','const pointer={...active,flowControl:', 'const pointer={...active,compactHandoff:{enabled:false},flowControl:')
replace('tools/tests/liuren-flow-control.test.mjs',"missing:['exam','shensha-use']","missing:['exam','judgment-core']")
replace('tools/tests/liuren-flow-control.test.mjs',"['exam','shensha-use']","['exam','judgment-core']")
replace('tools/tests/liuren-flow-control.test.mjs',"missing:['shensha-use']","missing:['judgment-core']")
replace('tools/tests/liuren-flow-control.test.mjs','MISSING_METHODS.*shensha-use','MISSING_METHODS.*judgment-core')
print('Updated core guide, skill, main/adjudicator prompts and protocol descriptions; activation pending')
