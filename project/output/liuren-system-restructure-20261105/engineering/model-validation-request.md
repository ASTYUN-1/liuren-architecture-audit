# 一次最小模型验证申请（等待用户明确授权）

当前没有执行这次外发；模型请求0。既有默认路由已从原全局配置只读确认：`conpera/gpt-6.1-sol`，接收端为 `https://code.conpera.ai/v1`。hostname/path已经去除任何账户、密钥和查询串；该接收端连通性尚未实测。本申请不要求新增认证，不复制凭据、不换provider。运行时仅引用原 `C:/Users/QLMa_/.config/opencode/opencode.jsonc`，仍以它原来的模型选项为准。

此前尝试在自动审批阶段被拒，进程未启动。原因是没有具体授权把候选Skill/方法正文发送给该Conpera接收方。详见 `model-validation-auto-review-rejection.json`。没有重试、换provider或换传输绕过。

## 准备好的具体内容

- 待验证候选：`C:\Users\QLMa_\Documents\六壬八字测算\output\liuren-system-restructure-20261105\candidate\integrated-final31-05`；methodVersion `542b7ebbff6e5213f25b3fa3195ff0686dabe2c0092722e3ae21e44b4dcb92b3`。
- 独立验证工作区：`C:\Users\QLMa_\Documents\六壬八字测算\output\liuren-system-restructure-20261105\engineering\model-validation-workspace`。该工作区只放三个指定Skill、两个候选说明和唯一窄资料工具。
- 精确用户prompt、两份instructions、三份Skill全文、void模块实际完整返回、指定void条件页实际返回，共8个文件，已准备 `18869` 字节；清单 `model-validation-payload/manifest.json`，SHA256 `86738e80c4d8c53573078065c03f8185cf1cc935903dac175f25fa54a883aed0`。每个文件均有字节数与SHA256，可逐份检查。
- 具体内容：候选AGENTS.md、docs/候选执行说明.md；daliuren/liuren-cases/liuren-extract三个Skill；`method void`；`read runtime/liuren/20261105-restructure-E0-candidate/references/void-method-conditions.md start=1 count=100`。**不另发送D01审查卡或liqi模块；void正文包含纠正后的空亡条款。不发送案例、经验、客户资料、真实个案或私有答案。**
- OpenCode 1.18.29仍会自动构建其原生系统/模型指令、当前日期/平台/工作目录等环境元数据、三Skill目录元信息及工具名称/描述/schema、调用消息与包装。内置customize-opencode等可能出现在技能元信息中，但权限禁止加载。上述原生内容不是本地8文件的字节统计，无法在模型初始化前声称已经取得完整最终wire payload。仅两个列出的候选instructions显式加载；禁父项目自动配置、外部skills、Claude兼容和外部/默认插件，隔离XDG数据/状态/缓存；不引用项目父AGENTS、案例/经验目录或服务连接资料。需按实际事件保留到底收到哪些内容，不能把prompt单独当全量输入。

## 强制调用边界与本地预检

仅允许skill加载这三个名字，以及窄`liuren_materials`两种精确请求。窄工具只返回已hash固定的上述两份快照，不能读其他源文件；材料快照变更即拒绝。read只认列出路径及固定起行/数量；路径可用等价正/反斜杠。模型无bash/native read/edit、chart、shensha、retrieve、scan、维护或任务委派权限，也没有其他业务工具。

`model-validation-allowlist-tests.json`：8项本地预检通过，包含两次允许返回hash一致，retrieve/shensha/其他module/案例路径/越界路径/未批准行区间全部拒绝。这是工具白名单，不只依赖prompt。独立验证工具不替换候选普通资料工具；此次成功也只证明这个更窄加载途径。

`model-validation-boundary-manifest.json`另固定13个验证工具/配置/runner/既有OpenCode可执行文件的hash，SHA256 `0bd5f5e2a35decd991a33b28830816a348a763f173fec723158104c56fb6f950`。待授权runner须同时核对payload清单和此边界清单及明确的人类授权记录；任一内容变化即不启动。8文件payload没有因为本申请措辞修订而改变。runner的正常结束、短超时和4096字节模拟超限3项本地测试已通过（`bounded-runner-local-tests.json`），实际批准后仍用65秒/1MiB上限，尚0模型请求。

## 一次执行及通过标准

用户明确授权后仅运行一次，最长65秒，stdout+stderr总量上限1MiB，最终自然语言要求不超过200字；不自动重试、切provider或提高权限。达到时间/输出上限就结束并保留已有事件。输出上限是本地捕获界限，不承诺供应方token费用上限。

通过须观察到三个Skill实际加载；void完整正文与条件页实际工具返回及版本/hash一致；最后简短确认实际接收、三阶段身份及效果未验证。只有发现/工具返回/最后确认全部可核，才标这次最小加载通过。初始化超时、认证或网络错误、有工具越界尝试或正文截断均如实记未通过，不能当实际预测效果或完整占断验收。无论此检查结果怎样，本申请均不包含active切换。
