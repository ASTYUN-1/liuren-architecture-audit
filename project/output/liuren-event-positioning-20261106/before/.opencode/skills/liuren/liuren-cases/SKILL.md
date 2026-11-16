---
name: liuren-cases
description: 案例查询、反馈复盘与维护；能力与授权边界须先核对。
---
# 案例查询、反馈复盘与维护

当前无两库对照研判不调用此入口的检索/回读；另行维护须独立任务办理，不能作为本次判断资料。
版本 `20261106-receipt-handoff-13`。
只读查询可通过liuren_materials双路检索与原档回读；用户要求反馈归档、改案或经验维护时，转有本轮写入授权的Build模式。普通只读liuren权限不支持维护写入。
读取当前两规程之一：`runtime/liuren/20261106-receipt-handoff-13/procedures/liuren-cases.md`（使用liuren_materials action=read可连续补读），或`python -B -X utf8 tools/load-liuren-procedure.py plan liuren-cases`再按part/page读取。当前正文是本轮已接受的迁移规程，旧规程只保留在历史基线，不承担现行命令。声明的CLI签名及写能力分别验收，未实际执行的维护写入不能标完成。


研判转daliuren后按09版程序事实接口执行；知识维护仍需独立授权，不因程序计算恢复两库预测调用。


13版结果交接：task及task_result向主智能体返回可见receipt-v1回执，task_id必须是该回执中的子会话ID；request_id、文件UUID和hash都不是task_id。不要从隐藏metadata找ID，不重复返回完整结构化报告。先按回执next_call调用task_result，再读report并调用liuren_adjudication_result(action="deliver",task_id=回执.task_id)。如旧任务的ID丢失，先liuren_adjudication_result(action="locate")；仅当前主会话恰有一份已保存裁决时自动定位，多份则返回候选并明确选择，不猜编号。格式失败只修字段，不重裁；需要核具体依据才action="read"获取完整结构化报告。子任务最终只回成功回执是正常交接，不是最终用户报告。
