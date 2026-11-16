# 当前裁决交接契约

交接报错按具体字段修正，保留facts、observations、focus_issues和unknowns；不通过删空材料、换request_id、换归档hash或反复probe来定位。request_id允许日期开头或UUID。当前runtime方法只需路径及已知hash即可装入完整正文；书籍范围错误会指出材料ID、路径和合法行界。输入容量按程序扩展后的完整盘、方法和计算共20万字符检查，文件上限70万UTF-8字节；超限明确报出实际值，不静默删减。

每问domain用于当前分类占读取及完整正文交接；actor_entity_id为旧交接兼容字段，可省略。程序不判断谁是当事人，不强绑考试/疾病日干，也不锁定输出对象。裁决者依原问和专法正常研判，具体取用错误才纠正，不额外新增主体核验阶段或调用。

输入沿用v2，输出自由，文件封装v1。原生工具schema与程序执行是同一套字段约定，详细接口见deterministic-tools.md。

输入：schema/request_id/questions/chart/facts/entities/observations/method_materials/focus_issues/unknowns。每问tasks必填；task_basis每项含task、origin（user_requested或necessary）、reason，user_requested另给原问逐字request_quote。input_origin与deterministic由程序生成，不手写。仅需有据重裁时给retry_context={previous_task_id,reason,error_path?}。不传初判、权重、排名或已知答案。

报告已保存为completed，主智能体读report后用结果工具deliver取得与已采纳结果hash绑定的完整技术正文。只改排版，不添加决定性理由。needs_input按明确缺项补资料；具体事实/引用错误注明原记录字段路径；确有新材料才一次独立补核。格式失败、同样顾虑或不喜欢结果均不得重新派裁决。

结果交接：task及task_result向主智能体返回可见receipt-v1回执，task_id必须是该回执中的子会话ID；request_id、文件UUID和hash都不是task_id。不要从隐藏metadata找ID，不重复返回原始裁决报告。先按回执next_call调用task_result，再读report并调用liuren_adjudication_result(action="deliver",task_id=回执.task_id)。如旧任务的ID丢失，先liuren_adjudication_result(action="locate")；仅当前主会话恰有一份已保存裁决时自动定位，多份则返回候选并明确选择，不猜编号。格式失败只修字段，不重裁；需要核具体依据才action="read"获取原始裁决报告。子任务最终只回成功回执是正常交接，不是最终用户报告。


## 报告传输边界（本版）

裁决报告采用灵活表达：liuren_adjudication_submit({result: 报告正文字符串或自由JSON对象})。无需output-v2、固定分析字段或application五项表；程序不补写、不删改、不以缺字段拒收。依据、关键作用、反证、条件题、应期取数按实际问题说明，条件未满足可自然说明不答。需要补资料时可提交对象并标status="needs_input"、说明缺项。成功后末消息返回工具回执；主智能体用task_result领取，read查看原报告，读report后deliver领取原样报告与hash。只有非空、可保存、容量及任务归属/文件完整读取等传输检查；contractChecked仅兼容旧回执，validationScope="transport-only"、professionalContentChecked=false明确不作专业验收。不得为格式差异重派裁决。

自由报告的具体错误补核：retry_context.error_path对正文用$，reason引述具体错误原句；对自由JSON用真实字段JSON Pointer，不限制旧entity_checks等字段。仍须真实新增材料、已领取原任务、最多一次补核，不为格式重裁。
