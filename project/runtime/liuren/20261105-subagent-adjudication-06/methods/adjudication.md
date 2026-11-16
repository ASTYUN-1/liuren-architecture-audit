# 文件式独立裁决接口

主智能体不形成暂定或最终主判。前两阶段、必要专法和evidence资料核证照旧。

1. 调用liuren_adjudication_packet，packet参数直接传中性对象（不是JSON字符串），字段见[契约](../references/adjudicator-contract.md)。工具校验后写到output/liuren-adjudication-requests/的独立文件；不需要bash、write或手工转义。只保存当前裁决材料，不是案例归档或经验入库。
2. 调用task，subagent_type=liuren-adjudicator，description=大六壬独立裁决，prompt原样使用工具返回的task_prompt（仅协议标记、绝对路径和SHA256三行）。不提供task_id、不传background:true，不再将长JSON塞进task prompt。
3. 子智能体通过liuren_adjudication_read逐页读取该文件，按原有书据独立裁决。只有这项工具获准，无任意read、两库检索、MCP、写文件或再次委派能力。每页有页号，必须读全；不读全或文件被改动时返回不能通过验收。
4. 返回completed且契约通过才按report完整交付。主智能体核事实和引用，不自行折中改判。needs_input补具体资料，保存新文件并新建裁决；同材料不重复问。工具或模型失败明确未完成，不由主智能体补判。同任务最多一次有具体修正的重试，仍失败报告缺口。

输入仍禁止主判、排名、权重、已知答案和旧裁决。取用候选及观察按盘位／稳定ID排列，保留正反依据。程序只自动重命名与固定书据冲突的E编号并同步结构化引用，不改变正文事实或专业结论。实体branch可写日干、明确寄宫或组合；盘面十二宫仍须单地支，不能为了过格式把日干换成别的对象。

模型仍deepseek/deepseek-flash、high思考、65,536共享输出额度，slim 2.2.18注册，原生task调用；固定书据条件摘要及关键短引保留。不调用案例／经验库，完整原书仍可追溯。文件交接避免调用参数二次转义，不代表减少模型实际阅读量或已提高预测准确率。
