from pathlib import Path
import json,hashlib,shutil,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
B=read(OUT/'before-manifest.json')
for rel in ['README.md','目录总索引.md']:
 p=ROOT/rel
 if rel not in B['live']:
  dst=OUT/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
  B['live'][rel]=hashlib.sha256(p.read_bytes()).hexdigest()
 t=p.read_text(encoding='utf-8-sig').replace(B['parentRelease'],B['newRelease'])
 for label in ['09版：','09版程序事实与专法交接：','13版结果交接：']:
  t=re.sub(r'\n\n'+re.escape(label)+r'[^\n]*','',t)
 p.write_text(t.rstrip()+'\n',encoding='utf-8')
(OUT/'before-manifest.json').write_text(json.dumps(B,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'审查说明.md').write_text('''# 本机大六壬体系审查与18版修复

本轮核查当前入口、59个模块的登记与装载关系、三阶段/14必查/16专项覆盖、原生工具参数、文件式主子交接、裁决恢复和完整报告。工程闭环采用纯合成资料；没有调用真实外部模型，没有发送实际案例，也没有修改网站。18版以前的冻结runtime逐文件核对，原样保留。

## 查出的问题和处理

| 问题 | 已做修复与范围 |
|---|---|
| 主模式原生read仍只放行07版runtime | 改为仅放行18版；不开放全部历史版本 |
| 活动工具已为input/output-v2，loader登记仍为v1 | 统一活动指针、manifest和loader契约；文件协议v1继续承担路径凭据，不与业务v2混同 |
| 自动注入说明同时允许/禁止两库，并有关闭委派的旧措辞 | 统一为无案例/经验库、允许指定裁决task的当前范围 |
| Skill、主提示和多代补丁重复交接规定 | 主Skill保留专业路线；详细操作集中到高效执行与adjudication方法，精简过时09/12/13/16/17接口补丁 |
| packet原生边界与实际校验不一致 | 共享ID、文本及数组边界；明确task_basis；request_id独立允许日期开头/UUID及128字符，不误用记录ID规则 |
| 程序已支持runtime方法全文，原生source却仍强求行号 | 当前版已登记方法可按路径/hash装全文；书籍仍保留准确行段及来源校验 |
| book_search/retrieve共用limit上限，后端才报错 | 在原生入口按action返回具体limit错误；scan仍可到100，不扩大检索 |
| 旧结果里的null/错误数组可能直接崩溃 | 返回具体字段issues；应期候选、数量值及专法必填项透出深层路径，便于原任务修字段 |
| 主子插件实例不同或重启，task收尾可能覆盖已经成功submit的结果 | 先恢复已验收结果；失败收尾不得覆盖completed/needs_input或已领取状态，保留结果hash与格式次数 |
| 维护映射仍记旧发布/旧正文hash | 更新当前正文登记及修订继承记录；保留原来源、旧修订及17版hash |
| movement/structure把特定原案概括为“动象必逃”“归支必回” | 回读北海指南问答LF152–164、319与指南注解LF2031–2037，恢复原案动象、空墓、年命、旬遍及引从等条件与不同解释身份 |
| 部分测试fixture沿用旧阶段、缺完整manifest | 修正测试输入与当前装载协议，保留原预测规则；新增跨实例恢复、完整应期数量、原生source及实际wire验证 |

17版已做过的无悬空JSON Schema引用修复，本轮重新捕获实际OpenCode出站schema确认保留；不重复算作18版新修复。

## 专业流程保留与审读范围

重点语义复核了定位、类神、关系、理气、空亡、课体结构、动态、证据、裁决、报告、应期与取数，并审读16专项的取用/条件和共同限制。没有把术理压成数字分数或吉凶词条投票，没有恢复考试/疾病程序强绑日干、亲属正则或角色表。主智能体自然理解事件、按分类专法准备；子智能体对中性材料独立裁关键效力；主智能体核事实、引用、覆盖并忠实交付，不因回执简短或主观不同意再裁。

这不是全部原书逐条穷尽回源。部分较长参考资料只核了相关选段，已有专业分歧仍保留来源身份和边界。部分正文hash变化只是空白/旧版前缀整理，不代表新增专业结论。原书原文、既有规则卡、历史案例与冻结包没有被改写。

完整timing、quantity和quantity-sources继续按问项进入裁决材料；有应期/数量任务须返回专法记录、候选轮次或数制/倍率/单位与局限。不因给占时便自动增加时间任务，也不因格式完整而强算所有数法。

## 验证证据

- final-node-tests.log：八组143项通过，包含原生接口、确定性盘面/计算、交接状态机及实际wire；additional-node-tests.log：书籍检索、课盘健康和神煞25项通过。
- Python：method-loader 6通过；material-scope 5通过、1项Windows symlink权限跳过；single-method 3通过；book-search 16通过。
- current-wire.json：真实OpenCode 1.18.29出站五个原生工具schema，无悬空引用；所测实现逐文件hash绑定。
- host-chain.json / host-cli.log / host-report.md：真实OpenCode1.18.29、已安装slim2.2.18，API仅127.0.0.1脚本响应。按当前候选方法读取、packet存档、单次task、子智能体逐页读完6页、submit、task_result、report、deliver完整跑通；实际子请求deepseek-flash/high。合成应期“辛巳”和计算值48到达正文。
- 初轮隔离测试因沙箱无法读取已安装插件而EPERM；已在获准读取的本地测试进程中验证通过。保留host-chain-first-failure.json和日志，不把测试权限问题当成生产插件缺陷。

以上证明本轮接口和工程交接可执行，不证明DeepSeek自主遵循率、真实预测准确率、实际耗时改善或所有插件联网可用。没有为此调用外部付费模型。context7/gh_grep不是本条研判链的必要工具，回环测试中明确关闭，未以其联网状态作为验收项。

## 生效、回滚和已知缺口

activate.py仅在候选hash、测试、真实宿主链和旧冻结包核对通过后发布新runtime并原子切指针。activation-receipt.json记录实际发布结果；rollback.py按本轮清单恢复mutable文件，保留18版冻结包追溯，遇后续改动拒绝覆盖。没有提交Git。

原有doctor仍报告research mechanical validation has gaps，已知指纹aaf91ad9a2a838ddf2d7ce7ae2ea7eca17c760ce939c530e844b74003f5b85ac、730条记录中645条eligible；这属于既有研究资料校验缺口，本轮不修改研究原始材料或绕过检查制造全绿。部署后另保存doctor结果。

使用18版需完全退出OpenCode后，在本目录新建liuren会话；旧会话可能保留旧工具schema与提示，不保证热加载。后续若仍失败，按具体工具字段/子会话ID和原始错误排查，不能通过清空材料或重新派整轮裁决试错。
''',encoding='utf-8')
print('docs prepared; originals backed up')
