from pathlib import Path
import sqlite3,json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];dest=OUT/'real-run';assert not dest.exists();dest.mkdir()
sid='ses_e4f0a0fdbffelwKn0f8SYOFYq9'
c=sqlite3.connect((Path.home()/'.local/share/opencode/opencode.db').as_uri()+'?mode=ro',uri=True)
for mid,data in c.execute('select id,data from message where session_id=? order by time_created',(sid,)):
 if json.loads(data).get('role')=='user':
  question='\n'.join(json.loads(r[0]).get('text','') for r in c.execute('select data from part where message_id=? order by time_created',(mid,)) if json.loads(r[0]).get('type')=='text');break
chart=None
for data, in c.execute('select data from part where session_id=? order by time_created',(sid,)):
 part=json.loads(data)
 if part.get('type')=='tool' and part.get('tool')=='liuren_chart' and part.get('state',{}).get('status')=='completed':chart=json.loads(part['state']['output'])['archive'];break
assert chart and question
assert hashlib.sha256(Path(chart['path']).read_bytes()).hexdigest()==chart['sha256']
rows=c.execute('select id,data from part where session_id=? order by time_created,id',(sid,)).fetchall()
selection={'source_session_id':sid,'title':'工作调动能否成功及应期','original_question':question,'archive':chart,'originalPartsSha256':hashlib.sha256(json.dumps(rows,ensure_ascii=False).encode()).hexdigest(),'selectionReason':'same original question for performance rerun; original case already completed; no old answer or real-world feedback supplied to model'}
(dest/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),'utf-8')
prior=ROOT/'output/liuren-zero-error-20261106/real-rerun'
for name in ['collect.py','desktop-server.mjs']:shutil.copyfile(prior/name,dest/name)
t=(prior/'run.py').read_text('utf-8-sig')
start=t.index("question='这是当前工作流")
end=t.index("(OUT/'test-question.md')",start)
t=t[:start]+'''question=selection['original_question']+'\\n\\n复用原问原占时的可靠程序盘，不按现在重起。归档archive='+json.dumps(ref,ensure_ascii=False)+'。按当前大六壬完整流程完成本问并交付完整技术报告。不给现实反馈或旧答案，不读取原会话及旧检索缓存。'
'''+t[end:]
assert 'async execute(args,context)' not in t
(dest/'run.py').write_text(t,'utf-8')
print('Prepared repeat of original job-transfer question; original answers and feedback excluded')
