"""Build a new immutable runtime and coordinated local instructions; do not switch active."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
NEW='20261106-flow-recovery-12';OLD='20261106-schema-compat-11'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf8')
before=read(OUT/'before-manifest.json');pointer=read(OUT/'before/.opencode/liuren-active.json')
assert pointer['release']==OLD
for rel,d in before['runtime'].items():assert sha(ROOT/before['parentRuntime']/rel)==d,rel
candidate=OUT/'candidate-runtime'
if candidate.exists():raise ValueError('Candidate already exists; review edits explicitly rather than overwriting')
shutil.copytree(ROOT/before['parentRuntime'],candidate)
protocol='''
12版执行规则：主智能体准备中性材料，独立裁决者裁关键作用，主智能体忠实交付。每问tasks必填，task_basis逐项注明user_requested及原问逐字request_quote，或necessary及具体理由；只给占时不等于问应期，不为完整性默认增加应期/取数。程序保留原问并提示明确亲属标签冲突，不替代专业取用。日干不能改成寄宫支来过校验。

先按当前路由读必查与触发专项；同版同上下文已读可复用。packet保存前核准备阶段必查回执，缺哪项只补哪项。report在交付前读。来源按行段/hash交程序装配，quote可省略；不要反复手抄引文。branch只放干支/纯支组合/戊（寄宫巳），注释放mapping_basis或mapping_review；verification只用method_interpretation/unverified。

packet返回task_prompt原样交新task，不提供task_id，不用background:true，不把上下文塞入task。裁决者逐页读完紧凑文件，使用liuren_adjudication_submit提交结构化结果，末消息仅返回工具回执。格式报错只在原子任务内修对应字段，保持裁决内容不变，最多三次提交；不得重新全盘权衡。含混对象不由程序猜改。程序保留原报告、字段错误、校验产物及hash。

主智能体收到结果后先task_result(task_id=子会话ID)领取并确认，领取同样经过六壬验收；不要用task取结果。失败用liuren_adjudication_result(action=read或repair)查看具体缺口/无歧义格式修复，不能再派整轮裁决。只有needs_input，或原报告中具体事实/引用错误（retry_context.error_path），并补入真实新材料，才可retry_context引用前task_id一次补核；仍失败明示未完成。同材料重复派发由程序拦截。

completed且验收通过，读report后调用liuren_adjudication_result(action=deliver,task_id=子会话ID)，取得绑定结果hash的完整report_markdown，直接交付技术正文；可调排版，不改结论/精度/条件、不添决定性理由。它保留取用、关键作用、反证、争点、应期取数记录与来源。工程通过不证明专业或预测正确。经验库、案例库仍不介入，原书、全部专业方法和正常年命/行年保留。
'''
adjudication='''
# 文件式独立裁决、结构化提交与恢复

主智能体核原问、可靠盘、取用候选、状态关系与必要原法，准备到可裁决，以focus_issues列中性争点，不夹带初判、排序或已知答案。裁决者对照完整盘查错漏，裁关键作用与各问结论；主智能体返回后核事实和覆盖并忠实交付，不重做全盘权衡。

'''+protocol+'''

真实定位/效力/答案修正必须有具体证据；修格式不得将日干换成寄宫、将组合任意拆支。原始结果与修复记录分别保存，不用最新一份覆盖历史。已产出、已领取、已验收和已交付分别记录。状态存于output/liuren-flow-state，主子会话及文件hash绑定；重启后领取已保存结果仍核归属与hash。

input/output-v2、文件v1保持；新增task_basis、input_origin（程序生成）、retry_context。实体位置/状态和关系枚举由程序回填。应期/数量按原问声明后仍装入完整专法并要求special_methods；basis_ids只放方法来源，fact_ids放D_*、观察及事实。candidates和value均在record下。

详细字段见references/deterministic-tools.md与references/adjudicator-contract.md。未定维度保留条件和精度，不自动折中、降档，也不为反折中强断极端；不输出私下推理草稿。
'''
put(candidate/'methods/adjudication.md',adjudication)
put(candidate/'references/adjudicator-contract.md','''
# 12版裁决交接契约

输入输出沿用v2，文件封装v1。原生工具schema与程序执行是同一套字段约定，详细接口见deterministic-tools.md。

输入：schema/request_id/questions/chart/facts/entities/observations/method_materials/focus_issues/unknowns。每问tasks必填；task_basis每项含task、origin（user_requested或necessary）、reason，user_requested另给原问逐字request_quote。input_origin与deterministic由程序生成，不手写。仅需有据重裁时给retry_context={previous_task_id,reason,error_path?}。不传初判、权重、排名或已知答案。

输出不再只靠一段自由JSON传输。裁决者调用liuren_adjudication_submit(result=output-v2对象)，通过原生schema及事实/引用/专法校验后取得receipt-v1；最终消息只回该回执。结构化输出保留scope_review/entity_checks/relation_checks/issue_resolutions/answers/source_conflicts/missing_inputs/special_methods/calculations。实体只给id/referent/branch/mapping_review/limits；位置和状态由程序生成，关系computed_relations同理。

special_methods每项公共字段question_id/kind/status/target/basis_ids/fact_ids?/calculation_ids/alternatives/limits/record。basis_ids是实际方法来源ID（E01-E22或M项），fact_ids是盘面/观察/事实ID。timing的候选在record.candidates:[{date,day,event}]；quantity的完成值在record.value。日期和数值须匹配程序计算，择法、轮次、倍率、单位仍由裁决者说明依据。没有相关任务则special_methods=[]，未定给具体limits，不编造完成记录。

提交报错按issues[].path改字段，不改裁决、不重新读全包，最多三次提交。原报告保留，只有无歧义的字段移位/引用分类/不含其他干支的注释可程序归一化。出现混合对象不猜拆、不截字冒充修复。任务结束后主智能体用task_result领取，六壬插件统一验收；结果工具read/repair只读已有产物或做上述格式归一化，不调用模型。

completed且验收通过，主智能体读report后用结果工具deliver取得与已采纳结果hash绑定的完整技术正文。只改排版，不添加决定性理由。needs_input按明确缺项补资料；具体事实/引用错误注明原记录字段路径；确有新材料才一次独立补核。格式失败、同样顾虑或不喜欢结果均不得重新派裁决。
''')
det=(candidate/'references/deterministic-tools.md').read_text('utf8')
det=det.split('\n10版计算工具参数：')[0]
det=det.replace('# 确定性事实、专法计算与交接：09版','# 确定性事实、专法计算与交接：12版')
det=det.replace('basis_ids（方法来源ID）','basis_ids（方法来源ID）、fact_ids（可选盘面/观察/事实ID）')
det=det.replace('发现具体错误或必要新材料才按既有一次补核重裁规则处理。','格式失败就地修复；具体事实/引用错误或必要新资料，按12版一次有据补核规则处理。')
det=det.replace('完成裁决须输出special_methods','完成裁决须向liuren_adjudication_submit提交special_methods')
put(candidate/'references/deterministic-tools.md',det+'\n\n## 当前执行与恢复\n\n'+protocol+'\ncalendar必须明确start/end、timezone="Asia/Shanghai"、day_boundary="civil-midnight"或"zi-hour"；算式节点value/table/op保持无$ref发布、逐层严格校验。参数失败按字段修一次，仍失败保留具体计算缺口，不手算冒充程序。')
oldprompt=(candidate/'references/adjudicator-prompt.md').read_text('utf8')
head=oldprompt.split('## 输出契约')[0]
head=head.replace('完成后返回JSON','完成后用liuren_adjudication_submit提交结构化结果')
head=head.replace('公共字段question_id/kind/status/target/basis_ids/calculation_ids','公共字段question_id/kind/status/target/basis_ids/fact_ids?/calculation_ids')
head=head.replace('completed再给candidates:[{date,day,event}]','completed再给record.candidates:[{date,day,event}]')
book='# 固定书据：'+oldprompt.split('# 固定书据：',1)[1].split('\n10版计算工具参数：')[0]
submit='''
## 结构化提交和局部修复

只对packet.questions声明的tasks提交专法；不因给了占时就自加应期，不自加金额任务。12版使用liuren_adjudication_submit(result=output-v2对象)，字段直接按该工具schema填写。branch只放单干支、纯地支组合或戊（寄宫巳）；天将、临宫、旬空及解释放mapping_review。basis_ids只放E/M方法来源，D_*或观察/事实放fact_ids。timing候选只放record.candidates，quantity值只放record.value。

工具返回issues时，只改列明字段，不重做专业判断，不再读全包，不改变原结论、作用效力、应期轮次或数量择法。最多三次提交；仍失败如实留缺口，不靠换对象过校验。成功后最终消息原样返回工具给出的receipt-v1小回执，不再重复整份报告或添加Markdown。needs_input也用submit提交具体缺项，不能伪造completed。

实体程序字段及关系枚举继续省略；没有新增计算填calculations=[]。日期计算须明确start/end、timezone="Asia/Shanghai"和day_boundary="civil-midnight"或"zi-hour"。完整应期、取数、原法条件和最强反证义务保留；只修格式不意味着允许主智能体重新决定吉凶。
'''
put(candidate/'references/adjudicator-prompt.md',head+submit+'\n\n'+book)
report=(candidate/'methods/report.md').read_text('utf8')
report=report.replace('发现具体事实/引用/覆盖错误，按adjudication补材料新裁；纯展示更正不重裁。','格式问题先领取已保存产物并局部修复；具体事实/引用错误按adjudication一次有据补核，纯展示更正不重裁。')
report=report.replace('这是一套文件规程与显式产物约束，尚非 OpenCode 宿主强制门禁。加载器只能核版本、页数与文件完整性，不能证明模型实际理解或术理正确。','12版程序核必查读取、任务来源、父子归属、完整文件、结果契约、已采纳产物及交付hash，并从该结果生成完整正文；这些检查仍不能证明模型理解或术理正确。')
put(candidate/'methods/report.md',report+'\n\n## 12版交付\n\n先task_result领取/确认已有裁决，再liuren_adjudication_result(action="deliver",task_id=子会话ID)。程序生成report_markdown并绑定结果hash，保留完整结构化依据，主智能体直接交付；可调排版，不另造理由或折中改判。用户明确要简答时，可基于已通过裁决回答该问，不重新启动整轮流程。')
# Configure the actual entrypoints, keeping the three-book search and domain methods.
config=read(OUT/'before/opencode.json');old=config['agent']['liuren']['prompt']
base=old.split('依问核定位候选')[0]
search='查《壬归》'+old.split('查《壬归》',1)[1].split('09版复用',1)[0]
config['agent']['liuren']['prompt']=base+'\n\n'+protocol+'\n\n'+search+'\n复用liuren_chart.program_facts；必要时liuren_compute定点查表、日期、算式或连续来源。应期取数仍按完整专法。详细字段只读当前references/deterministic-tools.md，不猜格式。'
permission=config['agent']['liuren']['permission'];permission['task_result']='allow';permission['liuren_adjudication_result']='allow'
dump(ROOT/'opencode.json',config)
slim=read(OUT/'before/.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=(candidate/'references/adjudicator-prompt.md').read_text('utf8');slim['agents']['liuren-adjudicator']['permission']['liuren_adjudication_submit']='allow';dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',slim)
for rel in before['live']:
 if rel.endswith('SKILL.md') or rel in ['README.md','目录总索引.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬完整研判流程.md','docs/本机六壬资料检索范围.md','docs/本机六壬高效执行.md','AGENTS.md']:
  text=(OUT/'before'/rel).read_text('utf8').replace(OLD,NEW)
  if rel.endswith('daliuren/SKILL.md'):
   text=text.split('\n\n10版计算工具参数：')[0]
   text=text.replace('具体错误或新增材料才补核重裁，细节见adjudication。','格式错误不重裁；具体事实/引用错误或新材料按12版一次补核，细节见adjudication。')
  text=text.replace('缺项或错误补齐后新建独立裁决；失败明示未完成，不代裁。','格式错误只修原报告；必要新材料或具体事实/引用错误才一次补核；失败明示未完成，不代裁。')
  text=text.replace('具体错误或新增材料须补核重裁，纯排版或表述修正可直接处理。','格式错误局部修复；具体事实/引用错误或新材料按12版一次补核，纯排版更正可直接处理。')
  if rel in ['docs/本机六壬高效执行.md','.opencode/skills/liuren/daliuren/SKILL.md','AGENTS.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md']:
   text=text.split('\n\n10版计算工具参数：')[0]+'\n\n'+protocol
  put(ROOT/rel,text)
policy=read(candidate/'references/shensha-policy.json');policy['release']=NEW;dump(candidate/'references/shensha-policy.json',policy)
loader=read(candidate/'loader-contract.json');loader['release']=NEW;loader['authoringSource']='output/liuren-flow-repair-20261106'
loader['sourceHashes'].update({r:sha(ROOT/r) for r in ['tools/liuren-flow-control.mjs','tools/liuren-adjudication-output.mjs']})
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
loader['flowControl']={'schema':'liuren-flow-state-v1','durable':True,'maxAdjudications':2,'maxSubmissions':3,'resultTool':'liuren_adjudication_result','submitTool':'liuren_adjudication_submit','compactPacket':True}
dump(candidate/'loader-contract.json',loader)
m=read(candidate/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource='output/liuren-flow-repair-20261106',status='candidate')
m['flowControl']=loader['flowControl'];m['computeInterface']['release']=NEW;m['computeInterface']['transportEvidence']='output/liuren-flow-repair-20261106/current-wire.json'
m['adjudication'].update(submitTool='liuren_adjudication_submit',resultTool='liuren_adjudication_result',outputTransport='structured-submit-and-receipt')
m['files']={f.relative_to(candidate).as_posix():sha(f) for f in candidate.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(candidate/'manifest.json',m)
pointer.update(release=NEW,previousRelease=OLD,runtime='runtime/liuren/'+NEW,methodVersion=m['version'],backup='output/liuren-flow-repair-20261106/before',authoringSource='output/liuren-flow-repair-20261106')
pointer['flowControl']={'enabled':True,**loader['flowControl']};pointer['adjudication']=m['adjudication'];pointer['computeInterface']=m['computeInterface']
for rel in pointer['workflowImplementation']:pointer['workflowImplementation'][rel]=sha(ROOT/rel)
pointer['workflowImplementation'].update({r:sha(ROOT/r) for r in ['tools/liuren-flow-control.mjs','tools/liuren-adjudication-output.mjs']})
for rel in pointer['bookRetrieval']['files']:pointer['bookRetrieval']['files'][rel]=sha(ROOT/rel)
pointer['bookRetrieval']['compatibleMethodRelease']=NEW
for rel in pointer['files']:pointer['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
dump(OUT/'candidate-active.json',pointer)
dump(OUT/'candidate-manifest.json',{'release':NEW,'runtime':{f.relative_to(candidate).as_posix():sha(f) for f in candidate.rglob('*') if f.is_file()},'live':{r:sha(ROOT/r) for r in [*before['live'],*before['newFiles']] if r!='.opencode/liuren-active.json'}})
print(json.dumps({'candidate':NEW,'runtimeFiles':len(m['files']),'methodVersion':m['version']},ensure_ascii=False))
