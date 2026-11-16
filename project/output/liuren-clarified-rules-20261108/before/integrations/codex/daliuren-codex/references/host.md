# 宿主操作

命令均从 `C:\Users\QLMa_\Documents\六壬八字测算` 执行。将请求写为 UTF-8 JSON，再运行：

```text
node tools/liuren-codex.mjs --request 请求文件.json
```

不把长 JSON 嵌入 shell 命令，不手工改写程序生成的核心/哈希/回执。

## 方法、原书、盘与计算

- `{"action":"materials","request":{"action":"method","modules":["judgment-core","adjudication","recruitment"]}}`：输出带来源/hash/handoff的当前方法，最多4个模块。占类从status返回的domains选择；不要为无关问题读recruitment。
- `{"action":"materials","request":{"action":"book_search","queries":["具体争点"],"limit":4,"max_chars":14000}}`：仅原有三书，返回连续原文及精确handoff。需要其他连续原文时使用原有受限资料工具或明确项目内原书路径，保留身份，不使用案例/经验库。
- `node tools/liuren-resolved-chart.mjs --input 起课输入.json`：与OpenCode原生盘相同的修正导出。例如输入 `{"datetime":"2026-09-03T05:47","timezone":"Asia/Shanghai","declared_life":[{"birth_pillar":"辛未","sex":"男"}],"label":"求职"}`。这里只是输入示例，不包含判断或结果。
- 计算：`{"action":"compute","run":"实际run绝对路径","request":{"action":"lookup","lookup":{"subject":"申","place":"午","reference":"庚"}}}`。calendar/quantity/life等沿用原schema，按需读当前 `references/deterministic-tools.md`，程序不裁吉凶。

## 保存交接

请求形状如下。尖括号内容是说明，按原问填写，不把说明当真实事件；空数组允许保留，entities至少一项。

```json
{
  "action": "packet",
  "original_question": "<用户原问逐字，包括全部选项；不得掺入主智能体预测>",
  "packet": {
    "schema": "liuren-adjudication-input-v2",
    "request_id": "<唯一ASCII字母数字下划线连字符ID>",
    "chart": {"source": "liuren_chart可信归档", "archive": {"path": "<程序原样返回的绝对路径>", "sha256": "<原样hash>", "raw_sha256": "<原样hash>"}},
    "questions": [{"id":"Q_1","domain":"<status域ID>","text":"<原子问>","subject":"<实际对象>","stage":"<实际阶段>","deadline":"<实际期限或未给>","success_criteria":"<原问成功标准>","alternatives":["<真实分支>"],"tasks":["outcome"],"task_basis":[{"task":"outcome","origin":"user_requested","request_quote":"<逐字子问>","reason":"<简短理由>"}]}],
    "facts": [],
    "entities": [{"id":"S_person","branch":"<合法干支>","referent":"<实际对象>","question_ids":["Q_1"],"mapping_basis":"<候选定位理由>"}],
    "observations": [],
    "focus_issues": [],
    "method_materials": [],
    "method_modules": [],
    "unknowns": []
  }
}
```

observations每项为 `{id,entity_ids,kind,statement,reference,source,verification}`，kind为 `five_qi/twelve_states/relation/void/shenjiang/shensha/structure/movement/special_method`，verification为`method_interpretation/unverified`。focus_issues为 `{id,question_ids,entity_ids,observation_ids,question}`。method_materials直接使用方法/书检索返回的handoff，method_modules仅确需备查的现行ID。程序专有position、deterministic等不自己填写。完整schema见现有 `tools/liuren-adjudication-contract.mjs`。

返回spawn是给**原生子智能体工具的参数**，不是shell命令；无OpenCode task调用。返回的run在 `output/codex-liuren/codex-UUID/`，专业packet由原工具保存在 `output/liuren-adjudication-requests/`。不修改或复用历史OpenCode会话状态。

## 子智能体操作

每次JSON请求都使用同一个run：

```json
{"action":"role","run":"<实际run>"}
{"action":"read","run":"<实际run>","page":1,"page_count":1}
{"action":"read","run":"<实际run>","module":"void","page":1,"page_count":1}
{"action":"read","run":"<实际run>","material_id":"E04","page":1,"page_count":1}
{"action":"submit","run":"<实际run>","report_file":"<实际run>/report-draft.md"}
```

核心和所采用的参考段分别按next_request读全；参考总清单不要求全读。角色正文保留原工具名，role.host_mapping解释如何映射到桥接action，专业正文不改写。

主智能体：spawn返回后 `{"action":"bind","run":"<实际run>","agent_id":"<原生返回ID>"}`，等待原子智能体结束，再 `{"action":"result","run":"<实际run>"}` 取完整body。主智能体的事实/引用核对不等于重新裁决。没有receipt不凭“已完成”字样推断报告已存。

桥接使用共享文件系统，读取回执只记录文字输出，不是OpenCode插件的会话权限隔离，也不能认证是谁阅读或证明语义理解。原生spawn调用及其返回才是指定模型与独立子任务的可核对执行证据。不要声称达到另一宿主完全相同的强制隔离。

已确认判断口径以活动judgment-core的U01—U11为准。主智能体准备时不将已定规则重列为两说，真实缺口才列C编号及所缺条件；子智能体依同版规则独立查漏裁决，不能从旧摘录任选反向口径。返回核对包含U口径一致性；发现具体违规，逐字定位报告及U编号，附绑定规则证据，沿宿主一次补核协议处理，不由主智能体自行折中改判。
