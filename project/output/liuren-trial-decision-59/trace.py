from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
old=R/'runtime/liuren/20261115-strength-meaning-58'
run=R/'output/opencode-strength-meaning-20261115-five-04-deepseek'
def lines_at(p,terms):
 return [{'line':n,'text':s.strip()} for n,s in enumerate(p.read_text('utf8').splitlines(),1) if any(x in s for x in terms)]
calls=[]
for line in (run/'trial-02.jsonl').read_text('utf8').splitlines():
 e=json.loads(line)
 if e.get('type')=='tool_use':
  t=e['part'];args=t.get('state',{}).get('input',{})
  if t['tool']=='liuren_materials':calls.append({'tool':t['tool'],'input':args})
report=(run/'trial-02-report.md').read_text('utf8')
data={'scope':'58版真实会话中可见的输入与取舍；不声称读取模型内部思维或证明预训练因果',
 'session':'ses_e22c1afe3ffeOgkcj92qB28X9h','actual_material_calls':calls,
 'sources':[
 {'path':str((old/'references/class-selection-trial.md').relative_to(R)),'influence':lines_at(old/'references/class-selection-trial.md',['4. 取类','5. 对决定','6. 核双方'])},
 {'path':str((old/'domains/exam.md').relative_to(R)),'influence':lines_at(old/'domains/exam.md',['沿共用主线','综合主线依judgment-core'])},
 {'path':'tools/liuren-palace-strength.mjs','influence':lines_at(R/'tools/liuren-palace-strength.mjs',['directedEffect(e.type','semantic_role_validated:false','event_verdict_supported:false'])}],
 'observed_report_fragments':[s for s in report.splitlines() if any(x in s for x in ['日干被旺申','克制的力度明显比不上','并不等于侵害更大','倾向：偏凶'])],
 'diagnosis':'规则不是缺读；旧执行顺序先比较克制和制救数值，新喜旺恶衰仅作解释附注。工具本身不识别本题作用性质、又暴露扣分，形成可重现的冲突入口。专项本身并没有一句直接命令鬼旺必害，不能把全部错误归给某一原句。',
 'changes':'59版重写短答判断顺序；主调用专项改读具来源的分类摘录；短答排盘/补算加程序生成的局部解释与禁止推导；不改原始数值、完整专项、完整核心或最终自动判分。'}
(O/'source-trace.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
print('Saved source trace with actual clinical calls')
