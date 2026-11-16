from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
d=json.loads((OUT/'inventory.json').read_text('utf-8'))
core={
'class-mapping':('按占类确定取用系统','与positioning合并；只留共同取用原则，细法留专项'),
'positioning':('固定原问、事件对象和成功标准','保留核心；合并重复代问说明和通用定位步骤'),
'relations':('把对象落实到盘位与作用方向','算位定义交程序；有关对象关系并入核心分析'),
'liqi':('判断力量、作用、取与及制救是否有效','保留主干；去掉内部重复总纲，细例转按需参考'),
'structure':('解释课传结构对本问的作用','保留结构判断；起传算法异法、旧例勘误退出默认正文'),
'void':('判断空亡作用于谁及怎样影响实现','保留实质条件；空位直接用程序，未定断法不可当已选法删去'),
'movement':('判断变化、通路及直接阴神作用','共同阴神/关系规则并入主干；马/行程细法按事触发'),
'evidence':('保证材料可用、关键缺口和反证被识别','压成一次交接检查；不重复盘面运算或全套分析'),
'adjudication':('交接可靠材料并由独立裁决者给出判断','留最短成功路线；参数帮助和恢复规则移工具自说明'),
'report':('完整回答原问并给出可复核依据','保留结论/依据/反证/条件/必要时数；读取台账等程序生成附录'),
'timing':('有时间任务时选择应期方法及候选','保留短总则；将行人、病占等专法分支按问加载'),
'quantity':('有数值任务时确定数法、量级和精度','保留；实际运算归程序，不重复六环与交付说明'),
'shenjiang-use':('在取用需要时解释神将同用与互换','保留独有条件；通用理气与代问提醒上收'),
'workflow-contract':('可选prepare/read/check工程审计','退出日常研判；删旧版补丁叠加，仅维护入口可见'),
'risk':('解释旬丁/虎/勾/空的切题风险','共同效力/制救并入主干；独有条文按神将及事件触发'),
'shensha-tradition':('保存传统神煞解释和季煞推演','推演与来源批评转研究资料；不设额外日常执行阶段')}
refs={
'adjudication-method-conditions':'特定制救/多年财运的独有条件；按需保留，不作普遍前置',
'adjudicator-book-basis':'固定书据的执行摘要；按通用/专项拆分，独立裁决者必须能获得所需知识',
'adjudicator-book-evidence':'固定书据连续引文和hash；保留证据，默认不要求模型全读全部原段',
'adjudicator-contract':'交接契约；与adjudication/工具帮助单源维护，删除重复page_count说明',
'adjudicator-prompt':'含旧output-v2/application等要求；退出可误读的活动参考，按实际配置统一生成',
'bashajiubao':'覆盖关系与状态的查漏表；并入理气/结构/神煞规则，不再独立重复审一轮',
'beihai-extend-sop':'维护规程；移维护入口，纠正旧八字发现分组等过期说明',
'bifa':'毕法检索知识；按本盘结构或具体争点读取对应条，不整表重复研判',
'blade-methods':'两刃旧表、差异与考据；执行只留当前程序身份和取义条件，其余研究保留',
'case-retrieval-v2':'案例查询/归档的旧规程；只接维护/明确查询入口，不进普通占断',
'core-revision-provenance':'核心修订历史；维护/追溯使用，退出日常正文',
'daliuren-paipan':'转向实际排盘操作页；以工具说明为入口，保留必要输入边界',
'daliuren-shensha':'含旧起法/旧星级的速查；执行义项合并当前字典，其余退出日常检索',
'deterministic-policy':'程序采用的确定性状态口径；程序保留，向模型只传已采用口径与结果',
'deterministic-tools':'程序接口说明；去掉旧版叠加及旧报告字段，以工具schema为单一接口来源',
'engine-shensha-output':'读取程序结果的契约；压为短说明，删除每课查起法及旧引擎比较任务',
'event-positioning-policy':'程序分类路由与边界；程序保留，不转化为额外人物核验任务',
'experience-retrieval-v2':'旧经验检索规程；维护/查询入口使用',
'expert-adjudication':'疑难取舍导航；按真实争点用，不加载全部研究包',
'expert-adjudication-cases':'已曝光的断例对照；研究/开发参考，普通无两库流程不额外扩读',
'expert-adjudication-excerpts':'研究用连续原文；保留来源，仅有具体缺口时读有关段',
'expert-adjudication-sources':'研究来源定位与hash；程序和维护使用，不作日常指令',
'jiang-symbols':'十二天将职能；保留独有义项与条件，去24条共用样板，按项取得',
'keti-quanbiao':'课体定义/取义字典；已确定构成由程序给出，按命中课体取有关义项',
'kundun':'困顿等结构解释；按触发条件读取，保留专法，去通用步骤重复',
'liqi-examples':'解释易混边界的正反例；核心留一条原则，复杂例按需查看',
'liqi-source-map':'理气连续引文映射；保留来源，程序/维护校验',
'liqi-sources':'理气来源与真实分歧；已选口径移研究，未选且影响结论者保留必要条件',
'mapping-provenance':'旧ID、合并与未决来源；追溯使用，普通任务不为旧I/B跳转',
'nianming':'本命/行年的输入和采用；计算表/口诀移程序资料，年龄年界未知仍须保留限制',
'quantity-sources':'数表/数法条件；固定数表归程序，所选算法、倍率、量级条件必须保留',
'rule-semantics':'防止不充分条件反推的共同语义规则；核心保留短则，重复实例按需',
'shen-symbols':'十二支候选义；保留具体义和差别，共同适用/待辨模板只写一次',
'shensha-authority-conflicts':'已选择起法的异法史；移研究入口，日常不重记差异',
'shensha-authority-evidence':'神煞起法证据；保留原文与hash，程序/维护使用',
'shensha-authority-review':'起法复核工作记录；维护使用，不作每课必读',
'shensha-engine-index':'172名原引擎名称索引；只在名称无法识别的维护任务使用，执行优先当前可采用字典',
'shensha-field-meanings':'旧字段到词义的核对；编译为稳定ID/别名映射，移除每课源码追查',
'shensha-focus':'32项覆盖与使用范围；程序覆盖保留，起法/新增历史删出模型正文，作用条件并入字典',
'shensha-meaning-source-map':'神煞释义原文映射；保留证据，按需回源',
'shensha-meaning-sources':'释义连续原文；按具体语义缺口取得，不整包阅读',
'shensha-meanings':'常用32项作用知识；与focus/use合成一套按项可读的取用字典',
'shensha-other-meanings':'补充作用知识；只返回已采用且当前涉及的义项，保留必要组合条件',
'shensha-policy-evidence':'固定表对应的证据映射；程序/维护保留',
'shensha-policy':'38条固定规则及22个停用名称；保持程序执行，不要求模型重算或逐盘择法',
'shensha-source-map':'神煞来源映射；程序/维护保留',
'shensha-sources':'神煞出处和异法；退出默认研判，真实释义缺口按需读',
'shensha-use':'保留切题/对象/状态/制救/组合知识；删除重复起法验证，成为唯一短取用规则',
'void-method-conditions':'特殊空亡方法的具体条件；按触发保留，不能压成空即无力'}
domain_overrides={
'finance':'分收付双方、经营/财物/到账；保留通专及类不现的真实未决条件，研究批次记录退出',
'recruitment':'保留职位取用、类不现与录用链；组织共用C07等不重复抄，旧空亡分歧不可伪装已选',
'promotion-salary':'保留升/加/迁判据；同一C07/C08/C09/C15用共享规则引用，保留本域触发条件',
'interpersonal':'保留请求/等待的动静定位和助力是否落实；共用事业/音信规则按有关部分读取',
'relationship':'保留传统婚配对待轴、阶段、变法及专门三传角色；公共限制合并，批次核读记录转维护',
'pregnancy':'保留孕/产、母/子、方式/安危差别；土胎未决不可当固定排盘问题删掉，性别/产期按原问触发',
'exam':'保留考生、试卷/评分/学校/通知的阶段分工；数值/应期只在所问时触发',
'illness':'保留患者/病神/医救三方和暴久/阶段；共同制救方法引用主干，医学事实与推断不混',
'lost-person-object':'保留物/人/盗/赃差异与方位锚点；盗捕细法不连带加载兵占',
'classical-conflict':'拆兵事攻守与盗逃；按本问只取一支，不能让失物触发整份兵占材料',
'home':'保留人宅、具体构件与损害作用；不以整体安全替代具体进水等问项',
'travel':'保留成行/抵达/办事/音信区别；行人应期细则可归此分支，非时间题不加载',
'weather':'保留季候、类寻与晴雨条件；天气与宅/农受损按各子问分别触发',
'agriculture':'保留人/田/作物/收成及蚕畜渔猎细分；按实际对象切片，丝绵真实异文暂留缺口',
'period-outlook':'仅综合时运触发；保留分维判断，不让单事自动扩成五维',
'long-period':'仅长期占事触发；复用共同判断，不另载出生运限与研究历史'}
lines=['# 83份文件的核心作用与处置建议','',
'本表逐文件清点用途与运行角色，提出候选处置；不表示逐条术理已回原书验收。未更改任何活动文件。字数按UTF-8解码、换行归一后计；精简对象是日常模型输入和重复任务，证据原件保留。','',
'| 文件 | 字符 | 核心作用/建议 |','|---|---:|---|']
for r in d['files']:
    folder,stem=r['file'].split('/'); key=Path(stem).stem
    if folder=='domains': desc='专项取用与判断：'+domain_overrides[key]
    elif folder=='procedures': desc='知识/案例维护流程：与日常占断分开；共同保存/来源/复盘约定只维护一份，不因本轮精简删除维护能力'
    elif folder in ('methods','details'): desc='；'.join(core[key])
    else: desc=refs[key]
    lines.append(f"| `{r['file']}` | {r['chars']:,} | {desc} |")
(OUT/'逐文件核心作用与处置建议.md').write_text('\n'.join(lines)+'\n','utf-8')
print('Wrote',len(d['files']),'file dispositions')
