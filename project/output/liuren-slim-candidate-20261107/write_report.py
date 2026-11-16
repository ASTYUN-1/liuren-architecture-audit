from build_candidate import ROOT, OUT, BASE, HOST, C, NEW, load, sha, write, dump
import re
import json

def main():
    v=load(OUT/'verification.json');native=load(OUT/'integration-verification.json')
    measurements=v['measurements'];m=load(C/'manifest.json')
    rows=[]
    for name in ['共用必读','考试','疾病','财务与应期']:
        item=measurements[name]
        rows.append(f"| {name} | {item['before']['chars']:,} | {item['after']['chars']:,} | {item['charsReductionPercent']}% | {item['before']['pages']} → {item['after']['pages']} |")
    report=f'''# 六壬 Skill 精简候选说明

候选：`{NEW}`；基线：`20261106-performance-25`。本次已经实际改写入口、共用方法、神煞取用、读取路由和主/裁决提示，不只是提出建议。**候选未激活，原活动25版及113项基线文件未改。**

核心任务保持为：利用可信程序盘，理解原问，依专法取用，综合关键对象在课传中的有效作用，处理最强反证并逐问交付结论与条件。

## 精简结果

固定必读由14项合为8项：positioning、liqi、structure、void、shensha-use、movement、adjudication、report。三段阅读安排服务于同一主线，不重复分析。

**原问与可信盘 → 依问取用 → 综合作用与反证 → 独立裁决 → 核对并交付。**

| 实际路由中的方法正文 | 原版字符 | 候选字符 | 减少 | 读取页数 |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

入口、主prompt和自动instructions合计：{measurements['入口加主prompt加自动instructions']['beforeChars']:,} → {measurements['入口加主prompt加自动instructions']['afterChars']:,}字符。裁决prompt：{measurements['裁决prompt']['beforeChars']:,} → {measurements['裁决prompt']['afterChars']:,}字符，E01—E22关键依据全文保留。以上为静态原文字符与7,600字节分页结果，**不是实测token、推理耗时或加速比例**。AGENTS的候选文件仅说明隔离验证边界，不将它的缩短计为专业提示优化收益，也不拟用它覆盖原项目的通用开发指引。

## 实际改动

- **程序结果直接用。** 模型不重排天地盘、四课三传，不复算固定神煞公式，不逐课比旧引擎或记录已决定的起法异说。保留读取采用状态及天盘所属支、地盘坐处、乘将；缺参/停用不作判断依据。只有具体异常才处理受影响项。
- **神煞核算法与取用分开。** 原engine-shensha-output、shensha-focus、shensha-use三份必读合成一份，保留32项应用边界及按占类深化。模型仍浏览程序全量状态与位置，识别切题作用；取消机械32项核算法台账，不把神煞永远压为背景。
- **合并共同分析。** 分类/定位合入positioning，关系/理气与八煞九宝的独有条件合入liqi，材料核证与交接合入adjudication。空亡、结构和动态保留独有规则，不再以I/E/B、反例和执行步骤多次复述相同条件。
- **专项只删共用套话。** 16专项中独有段落与未决路径逐段原样保留；天神/天将辞义页的共同“适用、边界、待辨”只保留首次。风险页保留四类风险及重要例外，取消重复扫描指令。
- **历史资料退出日常执行。** 固定公式、星级、旧引擎差异、修订史留在冻结基线与证据资料；旧参考页改为取用补充/维护入口。来源与证据文件不为减小目录而删除。知识提取、案例维护仍有独立规程，共同边界合并到procedures/common.md，不进入普通研判。
- **接续协议只留当前版。** 主入口和自动说明去掉21/23/24/25累积补丁；固定output-v2/application等旧输出约束退出候选说明，保留自由报告、文件/hash/全量读取、task_result领取、report门禁、deliver及一次有据补核。裁决模型和high设置未改。

## 为准确性保留的内容

关键类神自身、与课传及彼此的关系；五气/十二气/六亲参照；作用是否有效、能否取得、制救到达与作用范围；空墓变质、直接阴神、动态、年命、结构位次、最强反证；具体占类和时间/数量专法条件均仍有入口。

空亡生扶与实现、财通专/类不现、旺鬼作用交叉边界等，属于尚未裁明的断法差异。它们与“程序公式已经确定”不同，本次仍保留具体条件和未决路径，不把删掉说明当成已经解决。完整技术报告继续保留决定性依据、来源、反证、条件和所问精度，不因提示词短而压缩成一句吉凶。

## 验证结果与范围

结构/加载检查{len(v['checks'])}项通过，实际工具模拟交接{len(native['checks'])}项通过：

- 当前manifest、hash与reading-route一致，全部59个登记ID可读取；默认8项、16专项、13触发分支可达。
- 真实CLI逐页读出的全文与回执一致；旧6模块不再被准备门禁要求，缺一项只补一项；交付前report门禁仍生效。
- 7份专业材料完整装入裁决文件，自动定位/专项按同源原段去重；未问时间/数量不自动加任务，实际tasks可装入完整应期/取数。
- 模拟裁决文件完整分页读取，非空自由正文提交、领取、重启恢复和deliver后原文相同。**报告正文是合成传输文本，没有调用模型或作预测。**
- 程序源码副本及8个排盘引擎文件字节未改；神煞policy仅更新release元数据，规则其余值相同；同一程序课盘的全部神煞位置/采用状态相同。
- 16专项的{next(c['detail']['paragraphs'] for c in v['checks'] if c['check']=='专项独有段落及未决路径原样保留')}个独有段落保留，裁决E01—E22依据全文及模型/high配置未改。原活动基线113项hash全部不变。

skill-creator的quick_validate已尝试运行，系统与捆绑Python均缺PyYAML，未取得该检查的通过结果；入口frontmatter的等价结构检查单独记录在skill-validation.json，不把它冒充官方脚本通过。该依赖问题不影响以上实际本地加载与工具交接检查。

尚未进行同模型旧/新成对行为比较或未曝光样本预测验证，不能保证准确率不下降；减少输入也不能直接换算为提速比例。主要待观察风险是模型注意力变化：取消逐项台账后是否漏掉切题神煞、合并后是否忽略重要反证或专法例外。

## 文件与复查

- [候选入口](candidate/.opencode/skills/liuren/daliuren/SKILL.md)
- [神煞取用](candidate/runtime/liuren/{NEW}/references/shensha-use.md)
- [综合作用方法](candidate/runtime/liuren/{NEW}/methods/liqi.md)
- [读取路由](candidate/runtime/liuren/{NEW}/reading-route.json)
- [规则保留与迁移对照](规则保留与迁移对照.md)
- [结构验证](verification.json)、[实际工具交接验证](integration-verification.json)

复查命令从原项目根运行：

```powershell
python -X utf8 output/liuren-slim-candidate-20261107/verify_candidate.py
node output/liuren-slim-candidate-20261107/integration_check.mjs
```

候选位于`output/liuren-slim-candidate-20261107/candidate`，仅为可加载/交接验证环境，不是完整OpenCode项目副本；书库、索引及完整宿主依赖未复制。集成检查仅从原宿主解析既有工具schema依赖，没有复制或修改依赖。不可直接把候选AGENTS或整个目录覆盖原项目。正式启用须另建发布包并同步入口、配置、manifest及文件hash；本轮无需回滚，原活动指针未切换。
'''
    write(OUT/'精简说明.md',report)
    mapping='''# 规则保留与迁移对照

这是候选编辑对照，不是专业等价或预测效果证明。具体原段保留位置、原字节hash和删除的共用段见候选runtime/migration.json；冻结25版仍为原文追溯源。

| 原模块/规则族 | 新位置 | 保留的判别条件 | 删除或退出日常的内容 |
|---|---|---|---|
| class-mapping + positioning | methods/positioning.md | 原问目标/阶段/期限；事件当事对象；考试考生、疾病患者；其他专类对待轴；九系统职责；类不现分路；同用互换；来意法范围 | 重复总纲、单独身份核验、程序角色绑定补丁、历史编号解释 |
| relations的盘位与关系范围 | methods/liqi.md“位置与关系范围” | 干/寄宫/上神/阴神不同坐标；四课与三传、发用与支、干上支上、关键类神与彼此关系；六亲参照；占时先锋；日上近事与类神三传分层 | 全盘重抄、按模块重复矩阵、程序坐标手算 |
| liqi通用作用链 | methods/liqi.md | 月令与坐处、施受方向、内外战完整链、五气/十二气/六亲参照、生合刑冲、暗鬼、取与、救制三种范围、改变依据后的重评、运筹与判断区别 | 重复长总纲、同一条主线的多次收尾、接口尾段 |
| 八煞九宝 | methods/liqi.md“查漏范围”及两表 | 17项对象/关系及独有边界；三奇/旬奇、旬仪/六仪、废非一颗新煞、月破与破碎、生扶/长生/月生气、德化鬼等 | 独立再跑一轮、每项结果台账、古籍名单差异介绍 |
| void | methods/void.md | 空的对象与层次；生扶空亡三条真实冲突路径；凶将空的张力；新久病与病程；阶段空；脱上脱/脱空等专法入口 | 追溯沿革默认阅读、坐标算法核验 |
| structure | methods/structure.md | 九宗门与附加课格身份、毕法关系层、位次；不备/幼度厄/合局/回环/顾祖/无禄/八专/铸印/病玄胎/墓、七项毕法结构；解离等喜忌和救制例外 | 起传算法分歧和血煞校勘、I/E/B重复、原例果应评议多次复述 |
| movement | methods/movement.md | 七类有路关系；直接阴神有限展开；年命引动；旬丁；驿马三怕、归支、首尾、魁罡、旺火空仍动、罗网空、马墓空、出行干支轴、周遍回归、败气、逆行及中末空 | 重复步骤和反例清单；每课记录天马/驿马旧例勘误；自动编事件链 |
| engine-shensha-output + shensha-focus + shensha-use | references/shensha-use.md | 程序状态准入、天盘所属/地盘坐处/乘将、全量结果浏览；32项各自作用边界和占类深化；直接取类/组合、生克制救、近名不互代 | 模型复核38条起法、核旧引擎、逐项公式台账、已解决异法和新增/校正标签 |
| shensha-meanings / other-meanings | 原路径 | 基本义、取用范围、条件、出处和整理身份 | 已修正引擎仍需保留冲突等陈旧指令，重复起法复核 |
| daliuren-shensha / blade-methods | 原路径缩短；固定表由程序使用 | 旧通表独有组合线索、二刃取用身份及不重复计证 | 旧星级、手算公式、逐盘贵人起例检查；异法原件在基线留存 |
| shen-symbols / jiang-symbols | 原路径 | 24项独有辞义、复合条件、例外与来源 | 同页相同适用/边界/待辨段只保留首次 |
| 16 domains | 原路径 | 全部独有段落、来源ID、取用/结果/程度/时间专法及未决路径 | 每页重复共同总纲和历史尾段 |
| evidence + adjudication | methods/adjudication.md | 中性材料、未知与争点、真实缺口查原书；task_basis；归档引用；全文装配；文件交接；自由报告；领取交付；一次有据补核 | 多处完整接口表、旧输出字段、版本补丁、回执简短时整轮重派 |
| report | methods/report.md | 完整技术报告所需信息、关键关系、最强反证、逐问精度、应期/取数记录、来源和依赖；事实/覆盖/一致性核查 | 十栏固定模板、32项全通过台账、重复接口和再裁一轮 |
| risk | details/risk.md | 丁/虎/勾/空不同风险；白虎神将分层；财煞组合和应聘类不现例外；阴神虎与发用位置差异 | I/E/B重复、速断当终审、一般验证警句多次复述 |
| shensha-tradition | details/shensha-tradition.md | 明确研究时保留季煞思辨的来源身份，不能生成新煞 | 普通研判再跑32项/推演起法 |
| timing / quantity / quantity-sources / nianming | 原文件不改，触发路由保留 | 时间节点、轮次与精度；数法数表/算式/修正/量级/单位；正常年命/行年 | 不为完整性自动增加任务，不因同一算法已算过再复算 |
| procedures两维护入口 | procedures/common.md + 原两页 | 查询/维护分流、连续精读、来源分层、附加卡/审查、引用hash、复盘反馈及实际写入验证 | 每页重复版本来历和共同说明；不纳入日常占断 |
| 主入口/自动instructions/裁决prompt | 候选.opencode与opencode.json | 目标、路线、范围、现行工具协议；裁决模型/high及E01—E22全文 | 21/23/24/25累积补丁、旧14文件与11次跳转印象、固定输出字段要求 |

旧6个模块ID作为兼容别名指向新正文，默认route不选它们；原路径的短页仅提示合并，避免继续执行旧重复流程。历史证据映射标为继承证据，不用旧映射宣称候选内容等价。

没有替研究材料作新的古法统一，也没有改变盘式算法、采用表规则、模型或思考级别。专业条件是否足够醒目、模型是否实际运用正确，仍需真实行为对照检查。
'''
    write(OUT/'规则保留与迁移对照.md',mapping)
    # Lightweight exact frontmatter validation using the available YAML parser in the host Node runtime.
    # Its result is written by validate_skill_entry.mjs, not assumed here.
    print(str(OUT/'精简说明.md'))

if __name__=='__main__':main()
