from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
LIVE=OUT/'candidate-live';RUN=OUT/'candidate-runtime'
OLD='20261106-workflow-boundaries-08';NEW='20261106-deterministic-foundation-09'
def read(p):return p.read_text('utf-8-sig')
def write(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='\n')
def dump(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads(read(OUT/'before-manifest.json'))
# Rebuild from the immutable parent, so repeated candidate generation is identical.
# Copy only its registered files; never alter the frozen parent or remove a tree.
for rel in before['runtime']:
 dst=RUN/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(ROOT/before['parentRuntime']/rel,dst)
before['newFiles']=list(dict.fromkeys(before['newFiles']+['tools/tests/liuren-deterministic.test.mjs']))
dump(OUT/'before-manifest.json',before)
for rel in [*before['live'],*before['newFiles']]:
 dst=LIVE/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
def effective(rel):return LIVE/rel if (LIVE/rel).is_file() else ROOT/rel

guide='''# 确定性事实、专法计算与交接：09版

程序负责定位、查表、关系枚举、日期和算式、连续引文及交接校验；模型负责取用、适用条件、作用效力和结果。不得把表中关系直接当成已发生作用或成败，计算通过不证明预测有效。经验库、案例库仍关闭。

## 读取与复用

liuren_chart已保留完整facts并增加program_facts，提供干支上阴、关键节点状态和关系；同盘先用返回结果，不再手算或重复读原JSON。engine_inventory.references指回同一chart.facts，原growth、seasonal_strength、nobleman、chart_types、userinfo/declared_life等不丢弃，也不重复塞全文。纠正神煞只采用shensha_resolution，不能因原标签仍保留就采用未登记项。旧userinfo年龄/年命未独立核验，禁止用它自动替代已核年命。

程序每个支节点同时给天盘该支的落宫/乘将、地盘同名宫的上神/乘将、直接阴神；不要把这三者混为同一位置。干阳干阴、支阳支阴来自四课/寄宫校对。D_B0至D_B11为支事实，D_S0至D_S9为干事实，可用于basis_ids。其他query关系ID只作导航，引用时回到参与的D_B/D_S与原法材料。

需要新增节点或具体计算时用liuren_compute。主智能体的chart/lookup/life传原archive={path,sha256}；裁决者不传archive，自动限定当前文件盘。action=chart可用symbols限定支/干；lookup需subject，可给reference/place/profile（four-seasons或quarter-earth）；calendar与quantity无需再次读取课盘。只用当前获准资料，source仅主智能体可用。

## 状态口径

五气同时提供four-seasons（四时分组）与quarter-earth（辰未戌丑土旺）条件表，并保留引擎原值；有分歧时根据实际原法说明采用口径，不能自动选更有利者、计为两票或合成分数。类神自身十二气按当前已采用的木亥、火寅、金巳、水土申五行顺行口径；引擎growth.day_stem另有阴干逆行，保留作异口径材料，不能自动替换。某字为墓、死、长生，不自动推出报废、死亡或存活。六亲默认对日干；lookup可明确其他reference，解释不得偷偷换参照。

life仅接受明确sex、age整数、age_basis="虚岁-已核"，可带用户已给birth_pillar。按references/nianming.md男一岁丙寅顺数、女一岁壬申逆数；程序不从本命猜出生年、年龄或年界。不接出生推命、大运、小限、飞限。

## 交接输入

沿用input/output-v2和文件协议v1，09版自动增加deterministic。它由packet工具生成，不手写。chart继续优先archive。每个questions成员新增tasks数组，按原问声明outcome/timing/quantity，可兼有；分清子问，不因未问数量而自动加数量任务。

entities的position省略或写"@program"，程序填写双方坐标；branch只填单个干支、纯支组合或辛（寄宫戌）这种明示格式。现实对象与候选取用写referent/mapping_basis，不能塞入branch或程序坐标。observations保留解释，但verification只能用method_interpretation/unverified；chart_checked归程序，手写会报错。

method_materials优先使用liuren_compute action=source返回的id/title/source_path/line_start/line_end/line_mode/sha256，quote可省略。source需连续行段；universal对应三书检索splitlines行号，lf只适用于明确LF口径的记录，二者不能混。手写quote须逐行相符；程序补齐所选段落，不允许省略号拼接冒充原文。段落完整不等于已涵盖章节全部条件，语义仍核上下文。

tasks含timing会自动装入完整timing；含quantity装完整quantity与quantity-sources，IDs为M_AUTO_TIMING/M_AUTO_QUANTITY/M_AUTO_NUMBERS。主智能体不再抄全文或只抄数表交接。总材料最多40条（含自动项）、总输入10万字符，超出明确报错，不静默删减。已读同版正文仍复用，不要求为自动装配再调用一次method。

可选computation_requests保存准备阶段已有计算，格式[{"id":"C_dates","action":"calendar","calendar":{...}}]或[{"id":"C_number","action":"quantity","expression":{...}}]；工具重算后装入deterministic.calculations。原问事实、盘面事实、候选取象、推断与真实反馈仍分开；不传倾向或已知答案。

## 日期与算式

calendar明确start/end（公历日期）、timezone="Asia/Shanghai"、day_boundary="civil-midnight"或"zi-hour"，可给branches或完整pillars过滤；日内可给hour/minute。默认每日午时取样，offset_days=0为start，round_for_branch按过滤范围内同支编号。每次1至732天，超过报错，不截断。它调用固定hash的原引擎lunar.js，列全范围内竞争轮次，不选择应期，也不改原课旬空、天将与课传。起算点、含不含当日和阶段由模型明确，不能把巳日读成四天后。

quantity采用有界表达式，不执行代码。查数节点{"table":"branch","symbol":"丑"}，支持branch/stem/sheng/cheng；常数节点{"value":6}；运算节点{"op":"multiply","args":[...]}，另有add/subtract/divide。没有统一天将数表，不猜腾蛇数；用原法常数时须带来源。十进位、折半、量级与单位需有依据，程序只算提交的式子，不能把原数48自动变480元。小数用有理数计算，并返回exact_fraction。

## 裁决返回与取向义务

entity_checks仍给id/referent/branch/mapping_review/limits，position、five_qi、twelve_states、site_yin、shenjiang、fact_refs由程序回填，裁决者省略；如自行填写而不符会拒绝。relation_checks的computed_relations同理由程序生成。模型写的是validity、reason、effect_scope；被逐问结论用作决定性或反证的关系，另给application={object,mechanism,stage,goal_effect,alternative_resolution}，说明作用于谁、怎么起作用、过程/结果哪一层、怎样关联目标、为何不取最强另一解释。不要为每个无关节点填长表。

问及应期/数量时，完成裁决须输出special_methods，一项对应一个question_id+kind。共同字段：question_id、kind（timing/quantity）、status（completed/unresolved）、target、basis_ids（方法来源ID）、calculation_ids、alternatives、limits、record。未定写具体缺口，不自动折中或降档。确需新资料而整体返回needs_input时，可暂不填尚未完成的专法记录，missing_inputs须给具体缺项。

timing.record包含event/stage/scale/start/count_rule/trigger/selected_method/round_comparison；completed须有candidates数组，每项date/day/event与所引用calendar计算相符。quantity.record包含object/position/number_table/operation/adjustments/magnitude/unit/precision；completed另给数值value，与引用quantity计算相符。只有干支候选、月份/年份/窗口而未完成公历转换时允许unresolved，保留已有判断及具体转换缺口，不把缺换算改为成败不明。

需要新算时，裁决者可用liuren_compute；最终calculations只交请求[{id:"C_...",action:"calendar",calendar:{...}}]或quantity+expression，程序重新计算，不交手写result。special_methods引用同ID。没有新增计算可填[]并引用输入已有计算。不得把主智能体、程序、子智能体各算一套作为三份独立证据。

主智能体核回传事实、问项/争点/专法覆盖和解释有没有越过依据，复用裁决及special_methods写完整技术报告，应期和数量各保留择法、条件、竞争候选/轮次或量级、算式与单位；不另发明决定性理由、不为谨慎折中改判。发现具体错误或必要新材料才按既有一次补核重裁规则处理。
'''
write(RUN/'references/deterministic-tools.md',guide)
policy={'schema':'liuren-deterministic-policy-v1','release':NEW,'implementation':'tools/liuren-deterministic.mjs',
 'growth':{'profile':'element-forward-water-earth','start':{'木':'亥','火':'寅','土':'申','金':'巳','水':'申'},'basis':['E02','E05'],'notEquivalent':'engine growth.day_stem'},
 'seasonalProfiles':['four-seasons','quarter-earth'],'seasonalSelection':'explicit source-conditioned; not automatically adjudicated',
 'kinReference':'day stem by default; arbitrary reference explicit','relations':'existence and direction only; no efficacy or transformation',
 'lifeRule':'references/nianming.md; verified nominal age required',
 'numberSource':'references/quantity-sources.md; branch/stem/sheng/cheng only; no guessed general table',
 'independentPredictiveValidationCount':0}
dump(RUN/'references/deterministic-policy.json',policy)
for rel in ['entry.md','reading-route.json','loader-contract.json']:
 write(RUN/rel,read(RUN/rel).replace(OLD,NEW))
entry=read(RUN/'entry.md')
trip='本版交接采用input/output-v2（focus_issues、scope_review、issue_resolutions），文件协议仍为v1。'
while trip+trip in entry:entry=entry.replace(trip+trip,trip)
entry+='\n\n09版程序事实与专法交接：先复用liuren_chart的program_facts；必要时liuren_compute按关键节点查。packet每问声明tasks，位置省略或@program，解释不用chart_checked；来源按行段/hash自动装配。应期取数全文随tasks自动进入裁决文件，返回检查special_methods。完整接口见references/deterministic-tools.md；程序不裁吉凶，原专业方法、无两库与主子分工保留。\n'
write(RUN/'entry.md',entry)
for rel in ['methods/adjudication.md','methods/relations.md','methods/liqi.md','methods/timing.md','methods/quantity.md','methods/report.md','methods/evidence.md']:
 p=RUN/rel
 if p.exists():write(p,read(p)+'\n\n09版确定性工作与交接按[程序事实接口](../references/deterministic-tools.md)执行。位置/阴神/查表/算式由程序给出，关系效力仍核原法；应期与数量任务保留完整专法记录，正文不得被简短结论替代。\n')
contract=RUN/'references/adjudicator-contract.md'
write(contract,'# 09版文件交接契约\n\n输入输出沿用v2、文件封装沿用v1。09版条件字段、计算记录和程序回填见[唯一详细接口](deterministic-tools.md)。\n\n输入保留schema/request_id/questions/chart/facts/entities/observations/method_materials/focus_issues/unknowns；每问新增tasks，可选computation_requests。deterministic由工具生成。\n\n输出保留schema/request_id/status/scope_review/entity_checks/relation_checks/issue_resolutions/answers/source_conflicts/missing_inputs，另给special_methods/calculations；实体程序字段及computed_relations省略由程序填，不手抄。\n\n模型仍DeepSeek V4.1 Flash、high，slim注册独立新task，完整读完当前文件；没有倾向、排序或已知答案。同材料不重裁，具体错误/新材料才按主方法一次补核重试。返回必须通过事实与结构校验，未定保持具体精度和条件，不自动降档。程序校验不证明术理或预测效果。\n')
prompt=read(RUN/'references/adjudicator-prompt.md')
prompt=prompt.replace('你只有liuren_adjudication_read用于读取当前获准材料文件，不能读其他文件。','你用liuren_adjudication_read读取当前获准材料文件，可用liuren_compute查询绑定盘和日期/算式，不得另读来源文件。')
prompt=prompt.replace('状态字段用简要完整的依据摘要，不要求穷举每个象义。','程序状态字段按09版省略，由程序回填；效力判断给必要摘要，不穷举无关象义。')
prompt=prompt.replace('## 裁决依据','''## 09版程序事实及专法返回（必须执行）

packet.deterministic为程序计算；D_B0-11/D_S0-9可作依据，engine_inventory.references回指完整盘原字段。位置、日阴/支阴/直接阴神、旬空、查表和关系无需手算；发现可靠原盘输入矛盾才要求补核。季令four-seasons/quarter-earth为不同条件口径，按原法说明采用，不能选有利者；原growth.day_stem另有逆行口径，类神自身五行十二气不混用。原始神煞标签不等于采用，按adopted_shensha及其状态。

entity_checks只写id/referent/branch/mapping_review/limits；省略position/five_qi/twelve_states/site_yin/shenjiang/fact_refs，由程序回填，写错会拒绝。relation_checks省略computed_relations。决定性及反证关系须附application={object,mechanism,stage,goal_effect,alternative_resolution}，核实整物/部件/功能、过程/完成、作用于目标还是障碍，不能把波折直接升为失败，也不能预定凶象总作修复解释。

按deterministic.special_requirements逐项输出special_methods，详见当前材料中的完整timing/quantity/quantity-sources。公共字段question_id/kind/status/target/basis_ids/calculation_ids/alternatives/limits/record。status=completed或unresolved，未定给具体缺口。timing.record字段event/stage/scale/start/count_rule/trigger/selected_method/round_comparison；completed再给candidates:[{date,day,event}]，须匹配引用的calendar。quantity.record字段object/position/number_table/operation/adjustments/magnitude/unit/precision；completed再给value，须匹配quantity计算。没有相关任务special_methods=[]。不能只回一句日期或金额替代专法，也不机械跑遍所有方法。

需要时liuren_compute action=calendar明确calendar={start,end,timezone:"Asia/Shanghai",day_boundary:"civil-midnight"或"zi-hour",branches:[...]}; 枚举限定范围全部竞争轮次，不改原局。action=quantity传expression：{value:6}、{table:"branch",symbol:"丑"}或{op:"multiply",args:[...]}，运算另有add/subtract/divide，数表仅branch/stem/sheng/cheng；无统一天将表，不猜数字。action=chart可symbols定点查询，lookup可明确subject/reference/place/profile，绑定盘自动取得，不传archive。

最终calculations只给请求列表[{id:"C_dates",action:"calendar",calendar:{...}}]或[{id:"C_num",action:"quantity",expression:{...}}]，程序重算并装入结果；special_methods用calculation_ids引用同ID或输入已有deterministic.calculations ID。不得手写计算result；无新增计算填[]。本版应期精细公历候选与数值完成须有实际计算，只有支日或条件未定可unresolved保留已知部分。所选方法、轮次、倍率和单位由你说明依据，程序不替代选择。

## 裁决依据''',1)
# Replace the legacy output example itself, rather than leaving contradictory hand-copy fields.
marker='```json\n';start=prompt.index(marker)+len(marker);end=prompt.index('\n```',start)
example=json.loads(prompt[start:end])
for item in example['entity_checks']:
 for key in ['position','five_qi','twelve_states','site_yin','shenjiang']:item.pop(key,None)
example['relation_checks'][0]['application']={'object':'作用对象及层级','mechanism':'作用机制与条件','stage':'阶段','goal_effect':'对问事目标的作用','alternative_resolution':'最强另一解释的处理'}
example['special_methods']=[];example['calculations']=[]
prompt=prompt[:start]+json.dumps(example,ensure_ascii=False,indent=2)+prompt[end:]
prompt=prompt.replace('依据ID只能使用固定书据 E01–E22 或输入事实、观察、方法材料的ID。','依据ID可使用固定书据 E01–E22、输入事实/观察/方法材料或程序D_B/D_S事实ID。')
prompt+='\n\n整体返回needs_input时，可暂不填尚未完成的special_methods，不为过结构检查编造专法；missing_inputs仍须指明必须补充的资料。\n'
write(RUN/'references/adjudicator-prompt.md',prompt)
cfg=json.loads(read(LIVE/'opencode.json'))
cfg['agent']['liuren']['permission']['liuren_compute']='allow'
cfg['agent']['liuren']['prompt']+=' 09版复用liuren_chart.program_facts，不手算或重抄坐标。liuren_compute提供绑定盘查表、日期轮次、算式和连续来源；每问tasks声明outcome/timing/quantity，entities.position省略或@program，observations不自标chart_checked。packet按tasks自动装入应期/数量全文；来源传行段/hash。完整操作见当前runtime references/deterministic-tools.md。裁决者回传special_methods供完整报告，应期取数保留择法与条件、轮次、算式/量级/单位。'
# Retain permissions and other settings, update only current release paths.
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace(OLD,NEW))
dump(LIVE/'opencode.json',cfg)
slim=json.loads(read(LIVE/'.opencode/oh-my-opencode-slim.jsonc'))
slim['agents']['liuren-adjudicator']['prompt']=prompt
slim['agents']['liuren-adjudicator']['permission']['liuren_compute']='allow'
dump(LIVE/'.opencode/oh-my-opencode-slim.jsonc',slim)
for name in ['daliuren','liuren-cases','liuren-extract']:
 p=LIVE/'.opencode/skills/liuren'/name/'SKILL.md'
 write(p,entry if name=='daliuren' else read(p).replace(OLD,NEW)+'\n\n研判转daliuren后按09版程序事实接口执行；知识维护仍需独立授权，不因程序计算恢复两库预测调用。\n')
for rel in ['README.md','AGENTS.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机六壬高效执行.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬资料检索范围.md']:
 p=LIVE/rel;write(p,read(p).replace(OLD,NEW)+'\n\n09版：复用liuren_chart.program_facts与liuren_compute。裁决输入每问tasks，程序生成坐标/阴神/状态，连续来源按行段/hash装配；应期取数全文自动交接，返回special_methods并完整解释。程序只计算，不裁吉凶；经验库、案例库仍不介入。完整接口见当前runtime references/deterministic-tools.md。\n')
policy_path=RUN/'references/shensha-policy.json';sp=json.loads(read(policy_path));sp['release']=NEW;dump(policy_path,sp)
pointer=json.loads(read(LIVE/'.opencode/liuren-active.json'))
pointer.update(release=NEW,runtime='runtime/liuren/'+NEW,previousRelease=OLD,backup=(OUT/'before').relative_to(ROOT).as_posix(),authoringSource=OUT.relative_to(ROOT).as_posix())
pointer['deterministicFoundation']={'enabled':True,'schema':'liuren-deterministic-v1','tool':'liuren_compute','guide':'references/deterministic-tools.md','inputExtension':'program-generated deterministic + question.tasks','specialMethodsRequired':True,'modelCallsAdded':0,'predictiveValidationCount':0}
for rel in ['tools/liuren-deterministic.mjs','tools/liuren-deterministic-io.mjs','tools/liuren-deterministic-calendar.mjs','.opencode/tools/liuren_chart.ts']:
 pointer['workflowImplementation'][rel]=sha(effective(rel))
for rel in pointer['workflowImplementation']:pointer['workflowImplementation'][rel]=sha(effective(rel))
for key in pointer['files']:
 name=key.split('/')[-2];pointer['files'][key]=sha(LIVE/'.opencode/skills/liuren'/name/'SKILL.md')
retrieval=pointer['bookRetrieval'];retrieval['compatibleMethodRelease']=NEW
for rel in retrieval['files']:retrieval['files'][rel]=sha(effective(rel))
loader=json.loads(read(RUN/'loader-contract.json'));loader.update(release=NEW,authoringSource=pointer['authoringSource'])
for rel in [*loader['sourceHashes'],*pointer['workflowImplementation']]:loader['sourceHashes'][rel]=sha(effective(rel))
loader['deterministicFoundation']=pointer['deterministicFoundation'];dump(RUN/'loader-contract.json',loader)
dump(RUN/'deterministic-foundation-revision.json',{'release':NEW,'parent':OLD,'scope':'local-opencode','sourceFactsRetained':True,'engineAlgorithmModified':False,'libraryExperimentChanged':False,'fixedBookEvidenceRetained':True,'independentPredictiveValidationCount':0})
manifest=json.loads(read(RUN/'manifest.json'));manifest.update(release=NEW,parentRelease=OLD,status='active',authoringSource=pointer['authoringSource'],revisionFile='deterministic-foundation-revision.json',deterministicFoundation=pointer['deterministicFoundation'])
manifest['files']={p.relative_to(RUN).as_posix():sha(p) for p in sorted(RUN.rglob('*')) if p.is_file() and p.name!='manifest.json'}
manifest['version']=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest();dump(RUN/'manifest.json',manifest)
pointer['methodVersion']=manifest['version'];dump(LIVE/'.opencode/liuren-active.json',pointer)
dump(OUT/'candidate-manifest.json',{'release':NEW,'live':{p.relative_to(LIVE).as_posix():sha(p) for p in LIVE.rglob('*') if p.is_file()},'runtime':manifest['files'],'methodVersion':manifest['version']})
print(json.dumps({'release':NEW,'runtimeFiles':len(manifest['files']),'liveFiles':len(before['live']),'newFiles':len(before['newFiles'])},ensure_ascii=False))
