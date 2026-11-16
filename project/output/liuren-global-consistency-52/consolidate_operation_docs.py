"""One-shot cleanup of the live operation documents, retaining their old bytes."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
p=O/'before.json';b=json.loads(p.read_text('utf8'))
for f in ['docs/本机六壬稳定运行指南.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬直接排盘.md']:
 if f not in b['files']:
  target=O/'before'/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/f,target)
  b['files'][f]=hashlib.sha256(target.read_bytes()).hexdigest()
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=R/'docs/本机六壬稳定运行指南.md';s=p.read_text('utf8')
s=s[:s.index('\n32版历史记录')].rstrip()+'\n'
s=s.replace('当前38版仅OpenCode裁决者固定','当前仅OpenCode裁决者固定')
s=s.replace('专业条件仍以当前daliuren、方法全文及原书为准。','执行采用口径以任务绑定judgment-core与本问专项为准，详细方法及原书按需查证。历史发布记录只供追溯。')
s=s.replace('memory、sequential-thinking、chrome-devtools、context7、filesystem、scrapling、windows-mcp、gh_grep属于辅助能力；29版曾完成实际工具调用检查；31版本轮验证项目原生工具全链，辅助MCP仅记录当前加载状态。','memory、sequential-thinking、chrome-devtools、context7、filesystem、scrapling、windows-mcp、gh_grep属于辅助能力，是否可用以当前宿主实际状态为准；历史调用成功不证明当前连接有效。')
s=s.replace('补真实新材料，按retry_context允许的一次补核；格式问题或不同意结论不属于重裁依据。','保留真实缺项或补入可靠证据；已交报告有具体原句和绑定证据时，按result(action="recheck")在原子会话补核一次并保留前后报告，不用retry_context另建任务。格式问题或不同意结论不属于重裁依据。')
s+='\n现行完整主线见[本机完整研判流程](本机六壬完整研判流程.md)；已确认U01—U11直接执行，历史C编号不作为待确认清单。五项review与数量最终回执依绑定核心，不叠加历史版本补丁。\n'
p.write_text(s,encoding='utf8')
p=R/'docs/本机OpenCode完整输出规则.md';s=p.read_text('utf8');s=s[:s.index('\n40版直接作答：')].rstrip()+'\n\n直接作答、数值估计与五项review以任务绑定judgment-core、report及quantity-correction为准，不在操作入口重复版本补丁。\n';p.write_text(s,encoding='utf8')
p=R/'docs/本机六壬直接排盘.md';s=p.read_text('utf8')
s=s.replace('操作版本：`20261030-direct-01`','操作版本：`20261112-operation-52`')
s=s.replace('无需等待新工具发现，也不因此重启现有会话。用 shell 调同一后端（命令从项目根目录执行）：','OpenCode的liuren模式先检查项目目录和execution_health，工具未加载则重启宿主，不绕过其Shell权限。Codex或Build维护模式已具备Shell权限时，可从项目根目录调用同一后端：')
s=s.replace('引擎年命/行年口径尚未独立核验，不直接用作决定性判断。','此userinfo旧字段口径未独立核验，不直接用作决定性判断；不影响另以已核虚岁/年界调用life取得的可信回执。')
s=s.replace('读取[旧手册的活时报数步骤](<../runtime/liuren/20261027-quantity-02/references/daliuren-paipan.md>)并操作可用的3456页面','按当前绑定模块daliuren-paipan对应原文所保留的活时报数章节核条件；普通liuren权限内无法执行时，转Codex或Build维护模式操作可用的3456页面，明确核验后再使用')
p.write_text(s,encoding='utf8')
# The operation override is deliberately versioned outside frozen runtime.
p=R/'.opencode/liuren-active.json';data=json.loads(p.read_text('utf8'));data['localModuleOverrides']['daliuren-paipan']['version']='20261112-operation-52';p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Consolidated live operation guides and removed the retry_context instruction')
