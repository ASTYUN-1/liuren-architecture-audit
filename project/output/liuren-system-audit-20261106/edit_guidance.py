from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;C=OUT/'candidate-runtime'
def put(p,t):p.write_text(t.strip()+'\n',encoding='utf-8')
protocol='''## 当前工具交接与恢复

每问声明domain、tasks和逐项task_basis：原问明确要求用user_requested及逐字request_quote，必要附属任务用necessary并说明理由。只给占时不等于问应期，不为完整性自加应期、金额。程序保存原问；事件理解及取用由模型依分类专法完成，不做亲属称谓推断或日干角色锁定。

先复用liuren_chart.program_facts。必要时liuren_compute定点查坐标、阴神、状态、日期或算式；程序给关系，不替模型裁效力。chart优先原样引用排盘返回的archive.path/sha256；无归档才复制完整facts含内层schema。实体branch只放干支、纯支组合或戊（寄宫巳），说明放mapping_basis；position省略或@program。观察verification只用method_interpretation/unverified。

method_materials的当前runtime方法可只给ID、标题、路径及已知hash，由程序核manifest装全文；书籍用准确行段、line_mode与hash，quote可省略。应期/取数全文随tasks自动进入裁决文件，不再抄全文。材料总数最多40条（含自动项）、扩展后输入20万字符、文件70万UTF-8字节；超限指出实际值，不静默删减。准备阶段缺哪个必查/专项只补哪个，report在交付前读。

1. liuren_adjudication_packet保存中性材料。focus_issues引用已有观察列实质争点，不传倾向/排序，不凑正反；无争点填[]。报错按具体字段改，不删空材料、换ID或归档hash做探针。
2. 返回task_prompt原样交task(subagent_type="liuren-adjudicator")；不填task_id，不用background:true，不塞长上下文。裁决者逐页读完当前绑定文件，正常研判取用、查漏与关键效力，不另跑身份核验。模型deepseek/deepseek-flash、高思考，由oh-my-opencode-slim注册。
3. 裁决者liuren_adjudication_submit提交output-v2；程序字段省略。应期候选在record.candidates，数值在record.value；special_methods.basis_ids仅方法来源ID，fact_ids放盘面/观察。格式报错在当前子任务只修所指字段，合计最多三次提交；不重判。成功后末消息只回receipt-v1，这是交接回执。
4. 主智能体按可见回执的子会话task_id调用task_result领取/确认。request_id、文件UUID、hash都不是task_id；不用task取结果。ID丢失用liuren_adjudication_result(action="locate")，多份时明确选择。需核具体问题才action="read"读完整结果；失败可action="repair"做无歧义格式恢复，不重新派整轮。
5. completed且验收通过，读report后liuren_adjudication_result(action="deliver",task_id=该子会话ID)，取得绑定结果hash的完整report_markdown。主智能体核事实、引用、问项/争点覆盖及正文一致性，复用裁决理由，可调排版，不添决定性理由、不折中改判。needs_input/invalid_output不交付为已完成。

只有needs_input或原报告的具体事实/引用错误，且有真实新增材料，才用retry_context引用前task_id一次补核；具体错误给error_path。主观不同意、显示格式问题、回执简短均不是重裁理由。仍失败保留具体缺口，不由主智能体代裁。已验收结果不会被宿主收尾错误覆盖；重启后仍核归属和hash。

input/output-v2及文件v1并用，各有职责，不是版本冲突。全部专业方法、原书查证、最强反证、正常年命/行年保留；案例库、经验库及其旧缓存不介入。工程检查不证明专业理解或预测效果。详细字段见当前references/deterministic-tools.md。'''
put(OUT/'execution-protocol.md',protocol)
# Keep the professional route and conditional table, remove accumulated release patches.
p=ROOT/'.opencode/skills/liuren/daliuren/SKILL.md';t=p.read_text(encoding='utf-8-sig')
t=t.split('\n09版程序事实与专法交接：')[0]
t=t.replace('20261106-packet-diagnostics-17','20261106-system-audit-18').replace('按12版一次补核','按当前协议一次补核')
t=t.replace('description: 本机大六壬单事与分类研判；课势定侧重、察类循气、制化裁决；保留14项必查与按问16专项。','description: 用于本机大六壬问事、代问、分类占断和同卦追问；可靠程序盘、14项必查、16专项、中性文件交接独立裁决及完整技术报告。')
# Detailed transport lives in one auto-injected guide and the adjudication method.
t=t.split('\n本版交接采用input/output-v2')[0]
put(p,t+'\n\n工具交接及失败恢复按自动加载的《本机六壬高效执行》当前协议；字段查当前references/deterministic-tools.md。协议采用input/output-v2、文件v1。收到成功回执后领取并交付，不将回执当最终报告，也不重复派裁决。')
p=ROOT/'docs/本机六壬高效执行.md';t=p.read_text(encoding='utf-8-sig').split('\n09版：')[0]
t=t.replace('20261106-packet-diagnostics-17','20261106-system-audit-18').replace('兼容上述08方法包','与当前活动方法包配套')
put(p,t+'\n\n'+protocol)
p=ROOT/'docs/本机六壬完整研判流程.md';t=p.read_text(encoding='utf-8-sig').split('\n09版：')[0]
put(p,t+'\n\n当前参数、回执领取和失败恢复统一见[高效执行](本机六壬高效执行.md)；不另按旧版补丁扩展阶段。事件对象依分类专法自然理解，不另设角色表或程序身份门禁。')
put(ROOT/'docs/本机六壬资料检索范围.md','''# 本机六壬研判的资料范围

普通研判使用liuren主模式，开发、排障和知识维护使用Build。当前为无案例/经验库对照：不调用两库原档、快照、索引检索或旧缓存，不从维护入口绕取；原书、当前方法及其内置书例保留。

| 资料 | 当前研判范围 |
|---|---|
| 当前方法 | 活动指针所指包中登记的methods/domains/references/details及入口；不含archive |
| 原书 | 书籍库/、books/，以相关原段及必要上下文为单位 |
| 研究来源 | knowledge/liuren-research/、资料来源/qq-homework-20261018/中获准原文，保留条件和来源身份 |
| 操作说明 | tools/liuren_material_scope.py的OPERATION_FILES逐文件白名单，不扫描整个docs |
| 案例、经验 | 当前研判禁用，另行授权维护须切Build |

工具使用：method按module读当前全文，同版同上下文真实已读复用；retrieve和cases/experience扫描禁用。查《壬归》《理法简易》《天一群笔记》争点优先book_search：query或最多4项queries，book=RG/LF/TY可限定，默认总结果4、总原文14000字符，limit为1..12。完整返回的原段不用再read；passage_complete=false按continuation补读，相关前提/例外未全时按context补上下文。需要目录才book_outline；其他书用scan/library=books（limit上限100）及read。检索排序不裁理论主次，未命中不证明书中没有，不为凑次数查书。

read或原生read仅读获准原档；PDF/图片可在获准目录用原生read。liuren_chart排盘归档，liuren_compute提供确定性计算，shensha用于复核已有归档。旧methods批次接口仅兼容审计。裁决用slim的task专门委派liuren-adjudicator，结果用task_result及liuren_adjudication_result领取，具体按[当前执行协议](本机六壬高效执行.md)。

liuren默认拒绝任意Shell、全项目grep/glob/list及开发工具；task只允许本裁决者。原生read只开放当前运行包及明确资料路径，不开放整个runtime或docs。此为工具范围约束，不宣称操作系统安全沙箱。网站、APK、部署、历史output、旧运行包、archive、依赖和缓存不进入普通研判检索；缺源如实记缺口，切Build维护范围。

重启OpenCode后在本目录新建会话，选择liuren并加载daliuren；旧会话不保证热加载。默认入口为daliuren/liuren-cases/liuren-extract，知识维护与本次研判分任务。source-read-map只供已登记历史引文的逐文件hash回读，不开放旧包或output扫描。''')
put(C/'methods/adjudication.md','# 文件式独立裁决、提交与恢复\n\n主智能体准备到可裁决，裁决者对完整盘查漏、裁关键作用；主智能体核事实与覆盖并忠实交付，不重新权衡。对事件自然理解并依分类专法取用，必要依据记录在实体与观察；程序仅路由分类与计算，不绑定人物。\n\n'+protocol+'\n\n真实定位/作用/答案修正须有具体证据，不能用格式修复换取用。专法与全部专业义务保留，未定维度保留条件和精度；不自动降档，也不为反折中强断极端。不输出私下推理草稿。原始、修复、验收、领取和交付记录分存output/liuren-flow-state。')
# Reference pages keep their actual field documentation, remove duplicated operational tails.
p=C/'references/deterministic-tools.md';t=p.read_text(encoding='utf-8-sig').split('## 当前执行与恢复')[0]
t=t.replace('：12版','：当前接口').replace('09版自动增加','程序自动增加').replace('source需连续行段','当前runtime方法可只给路径及已知hash；书籍source需连续行段').replace('按12版一次有据补核','按adjudication一次有据补核')
put(p,t+'\n\n执行、回执和失败恢复统一见methods/adjudication.md。')
p=C/'methods/report.md';t=p.read_text(encoding='utf-8-sig').split('## 12版交付')[0]
t=t.replace('12版程序核','程序核').replace('定位表中每个承担结论的角色','分析中每个承担结论的对象').replace('- 事件主体和代问者是否被混淆？父母/子孙是身份象、病象还是扶损节点？所有生克说明是否仍使用同一参照？','- 如出现具体取用错误，须说明受影响作用；正常报告沿用原事件语境和专法，不另设逐人身份核验。')
put(p,t+'\n\n交付路径统一按adjudication：可见回执→task_result领取→读report→result deliver。完整正文沿用已验收结果，不能由回执简短推断子任务未完成。')
for p in C.rglob('*.md'):
 t=p.read_text(encoding='utf-8-sig').replace('09版确定性工作与交接按','确定性工作与交接按')
 put(p,t)
# Correct a source-case conjunction that had become a universal two-marker rule.
p=C/'methods/movement.md';t=p.read_text(encoding='utf-8')
t=t.replace('本命河魁+驿马临行年双动象叠加则断必逃','问答录六的丽天僧例结合河魁临卯命、驿马临行年及既知缠扰背景断相携而逃之意，不抽成“双动象必逃”通则')
t=t.replace('断必能解脱而去','原例断解脱而去；仍须核本问确受何种罗网、空的是何物及其他制约，不将原例结论推广为任意辰戌逢空必脱')
t=t.replace('末传归支则必回一次','原例兼有一旬周遍、自干发用、末传为支神及六合，再断回归；单独末传归支不保证现实必回')
put(p,t+'\n\n本轮回源：北海《指南问答》LF152–164、319；《指南注解》LF2031–2037。后者对同例另举河魁旬空、马坐墓及本命丁马/引从条件，保留两种解释，不合并计票。其他动象原文未在本轮逐例穷尽回源。')
p=C/'methods/structure.md';t=p.read_text(encoding='utf-8').replace('末传归支必回来一次','问答录六原例兼自干发用、末支及六合而断回归，不把末传归支单项扩成必回通则')
put(p,t)
# Prompt is a short entry to the already injected protocol, not another copy of it.
p=ROOT/'opencode.json';cfg=json.loads(p.read_text(encoding='utf-8-sig'))
cfg['agent']['liuren']['prompt']='''本机大六壬占事：先加载当前daliuren，按三宏阶段、14必查与实际问项选择16专项，依自动加载的《本机六壬高效执行》当前协议执行。主智能体理解事件、依分类专法取用，准备可靠盘和中性材料；裁决者独立定关键效力与结论；主智能体核事实、引用、覆盖并忠实交付，不再折中改判。代问者不自动作当事人，不设角色表或程序人物锁定。理气贯穿、因问定侧重，阶段1不冻结成败，切题类象按完整条件使用。复用程序facts及同版已读方法，按真实缺口查书，不先全读。无案例库/经验库/旧缓存，仍保留原书、全部专业方法、最强反证及正常年命/行年。只做大六壬占事，出生推命、大运、小限、飞限退出。收到receipt按next_call领取结果，读report后deliver完整技术正文；回执简短不重派，格式问题不重裁。排障、开发和知识维护另用Build。'''
permissions=cfg['agent']['liuren']['permission']['read']
cfg['agent']['liuren']['permission']['read']={k.replace('20261105-subagent-adjudication-07','20261106-system-audit-18'):v for k,v in permissions.items()}
put(p,json.dumps(cfg,ensure_ascii=False,indent=2))
