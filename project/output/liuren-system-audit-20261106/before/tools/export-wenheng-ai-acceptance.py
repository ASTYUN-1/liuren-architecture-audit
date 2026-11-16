"""Export only the known synthetic AI acceptance conversation, without charts/secrets."""
import json
import re
import shlex
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
remote_script = '''
import json
from pathlib import Path
p=Path('/var/lib/wenheng/acceptance/ai-api')
initial=json.loads((p/'initial.json').read_text())
followup=json.loads((p/'followup.json').read_text())
summary=json.loads((p/'summary.json').read_text())
if not summary.get('ok') or not summary.get('syntheticOnly'):
    raise RuntimeError('Successful synthetic acceptance required')
print(json.dumps({
 'question':initial['chart']['input']['question'],
 'participants':initial['chart']['input']['participants'],
 'report':{k:initial['report'][k] for k in ['title','summary','content','warnings']},
 'answer':followup['answer'],
 'summary':{k:summary[k] for k in ['model','elapsedMs','chartRetained','initialUsage','followupUsage']}
},ensure_ascii=False))
'''
command = [
    'ssh.exe', '-F', 'NUL', '-i', str(Path.home()/'.ssh/old-server-control'),
    '-p', '22223', '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
    '-o', 'ConnectTimeout=12', '-o', 'StrictHostKeyChecking=yes',
    '-o', f'UserKnownHostsFile={Path.home()}/Documents/OldServerControl/linux_known_hosts',
    'slope@192.168.100.8', 'sudo -u wenheng python3 -c '+shlex.quote(remote_script),
]
result = subprocess.run(command, capture_output=True, check=True)
data = json.loads(result.stdout.decode('utf-8'))
verifier = (root/'web/deploy/verify-live-ai.mts').read_text(encoding='utf-8')
question_match = re.search(r'question:"(仍是同一件复合的事[^"\n]+)"', verifier)
if not question_match:
    raise RuntimeError('Follow-up source question missing')
followup_question = question_match.group(1)
s = data['summary']
initial_cost = s['initialUsage']['costCny']
followup_cost = s['followupUsage']['costCny']
people = '\n'.join(
    f"- {p['role']}：{'女' if p['gender']=='female' else '男'}，公历出生年份 {p['birthYear']}。"
    for p in data['participants']
)
warnings = '\n'.join('- '+w for w in data['report']['warnings'])
text = f'''# 问衡 AI 主报告与追问完整记录

导出日期：2026-10-15。此记录使用虚构人物和合成问题，来自刚才的真实 DeepSeek API 验收，不是客户档案。仅导出提问、公开报告、追问回答及运行概况，不包含完整盘面、内部思考或密钥。

## 原始提问

{data['question']}

## 人物资料

{people}

## 首次报告

**{data['report']['title']}**

{data['report']['summary']}

{data['report']['content']}

### 报告附注

{warnings}

---

## 追问原文

{followup_question}

## 追问回答

{data['answer']}

---

## 运行概况

- 模型：DeepSeek 官方 API，{s['model']}，高思考模式。
- 首次报告：{s['initialUsage']['requests']} 次模型请求，{s['initialUsage']['toolCalls']} 次工具调用，完成 {len(s['initialUsage']['completedStages'])} 个必做技能步骤。
- 追问：{s['followupUsage']['requests']} 次模型请求，{s['followupUsage']['toolCalls']} 次工具调用，完成 {len(s['followupUsage']['completedStages'])} 个必做技能步骤。
- 两次合计耗时：约 {s['elapsedMs']/1000:.0f} 秒；已核对追问沿用原盘。
- 程序估算费用：首次 ¥{initial_cost:.4f}，追问 ¥{followup_cost:.4f}，合计 ¥{initial_cost+followup_cost:.4f}。以供应商实际账单为准，不含此前失败的调试调用。
- 追问原文取自本轮验收脚本；正文取自该轮成功生成的报告文件。此记录用于查看实际输出，不构成预测准确性证明。
'''
destination = root/'output/问衡AI验收档案-20261015/主报告与追问完整记录.md'
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(text, encoding='utf-8-sig')
assert data['report']['content'] in text and data['answer'] in text
assert followup_question in text and data['question'] in text
assert 'DEEPSEEK_API_KEY' not in text and 'reasoning_content' not in text
print(json.dumps({'path':str(destination),'characters':len(text),'initialCharacters':len(data['report']['content']),'followupCharacters':len(data['answer'])},ensure_ascii=False))
