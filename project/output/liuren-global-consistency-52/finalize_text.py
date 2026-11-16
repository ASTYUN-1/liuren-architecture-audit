"""One-shot cleanup after detecting unmarked legacy project instructions."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
p=R/'AGENTS.md';raw=p.read_bytes();marker=b'--- project-doc ---'
old=(O/'before/AGENTS.md').read_bytes()
assert old.startswith('# 本地大六壬工作区接手指引'.encode()) and marker not in old
assert raw.startswith(old) and raw.count(marker)==1
# The actual workspace file contains only project instructions. Personal/global
# instructions were injected separately and are not stored or edited here.
p.write_bytes(raw[raw.index(marker)+len(marker):].lstrip(b'\r\n'))
b=json.loads((O/'before.json').read_text('utf8'))
b['agent_prefix_detection']={'original_project_only':True,'personal_prefix_bytes':0,
 'note':'Original file has no project-doc separator and begins with the project heading; former agent_prefix_sha256 hashed the entire project file, not a personal prefix.'}
(O/'before.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=R/'runtime/liuren/20261112-consistency-52/references/deterministic-tools.md';s=p.read_text('utf8')
a=s.index('38版OpenCode模型对照：');z=s.index('## 单宫旺衰',a)
s=s[:a]+'''宿主启动、额度和同会话恢复只按`methods/adjudication.md`及活动配置；OpenCode首次检查execution_health.ready。核心与参考读取分工按judgment-core，不在本接口重复版本补丁。

'''+s[z:]
s=s.replace('## 单宫旺衰与取用后补算（34版，主、子共同执行）','## 单宫旺衰与取用后补算')
s=s.replace('详细参数及调用例见`deterministic-tools`','详细参数及调用例见下文')
s=s.replace('# 35版确定性工具使用说明','## 按需确定性方法')
s=s.replace('| WY242-generated-base |', '| LF3329-class-ground | 《理法简易》3329选定类神与坐处；旺仅基础数、相相乘、休相加、囚死相加折半 | target、season_profile、basis |\n| WY242-generated-base |')
s=s.replace('上述旺衰读取月令五气，不用综合指数改写原文条件。','上述方法依各自原段读取气态；CY501与LF3329核坐处五气，WY242核月令五气，不用综合指数改写原文条件。')
s=s.replace('旧expression查表算式保持兼容，但不能与quantity_method同次混用，也不自动叠到另一个数法结果上。','quantity的expression、quantity_method、quantity_adjustment三选一；最终数量兑现字段和真实回执绑定查quantity-correction。已用气态的具名法不得再套实验倍率。')
a=s.index('## 第39版执行核对');z=s.index('## 49版旺衰工具的按需核查',a)
s=s[:a]+s[z:]
s=s.replace('## 49版旺衰工具的按需核查','## 旺衰工具的按需核查')
s=s.replace('新方法只在35版新绑定任务使用；历史任务沿原版，若发现旧任务需要新工具应另建明确的新任务绑定，不混用旧回执。','任务只使用绑定版本已具备的方法，历史任务沿原版；旧任务确需新工具时另建明确的新任务，不混用旧回执。')
a=s.index('51版旺衰取数：')
s=s[:a]+'旺衰与数量的结合依judgment-core及quantity-correction：同范围without_void、source/experimental分路、空减不重复、量级独立、最终回执绑定。这里不另复制完整专业规则。\n'
p.write_text(s,encoding='utf8')
print('Removed legacy project preamble and consolidated interface documentation')
