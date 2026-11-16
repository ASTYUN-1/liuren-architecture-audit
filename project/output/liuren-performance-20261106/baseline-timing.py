"""Read-only first-answer timing from the unchanged original session."""
from pathlib import Path
import json, sqlite3, collections
OUT=Path(__file__).resolve().parent
db=sqlite3.connect((Path.home()/'.local/share/opencode/opencode.db').as_uri()+'?mode=ro',uri=True)
selection=json.loads((OUT/'real-run/selection.json').read_text('utf-8-sig'))
sid=selection['source_session_id']
messages=[]
for mid,raw,created in db.execute('select id,data,time_created from message where session_id=? order by time_created',(sid,)):
    v=json.loads(raw)
    parts=[json.loads(x[0]) for x in db.execute('select data from part where message_id=? order by time_created',(mid,))]
    messages.append({'id':mid,'info':v,'created':created,'parts':parts})
start=next(m for m in messages if m['info'].get('role')=='user')
end=next(m for m in messages if m['created']>=start['created'] and m['info'].get('role')=='assistant' and m['info'].get('finish')=='stop')
finish=end['info'].get('time',{}).get('completed')
assert finish
children=[x[0] for x in db.execute('select id from session where parent_id=?',(sid,))]
calls=[]
for task in [sid,*children]:
    for raw,created in db.execute('select data,time_created from part where session_id=? order by time_created',(task,)):
        v=json.loads(raw)
        if start['created']<=created<=finish and v.get('type')=='tool':
            calls.append({'task_id':task,'tool':v.get('tool'),'status':v.get('state',{}).get('status'),
                          'time':v.get('state',{}).get('time')})
result={'source_session_id':sid,'firstUserTimeMs':start['created'],'firstAnswerCompletedMs':finish,
        'elapsedSeconds':(finish-start['created'])/1000,'toolCalls':len(calls),
        'statusCounts':dict(collections.Counter(c['status'] for c in calls)),
        'toolCounts':dict(collections.Counter(c['tool'] for c in calls)), 'calls':calls}
(OUT/'baseline-timing.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['calls','toolCounts']},ensure_ascii=False))
