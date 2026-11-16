"""Read only the identified local session; retain auditable visible evidence."""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATABASE = Path('C:/Users/QLMa_/.local/share/opencode/opencode.db')
PARENT = 'ses_e53290ff6ffezfIdZtoppZS2xc'
connection = sqlite3.connect(DATABASE.as_uri() + '?mode=ro', uri=True)
connection.execute('BEGIN')
sessions = [PARENT] + [r[0] for r in connection.execute('select id from session where parent_id=? order by time_created', (PARENT,))]
messages, tasks, packet_calls, tool_rows, tokens = [], [], [], [], {}
first_user, first_finish = None, None


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


for sid in sessions:
    aggregate = collections.Counter()
    for mid, created, raw in connection.execute('select id,time_created,data from message where session_id=? order by time_created,id', (sid,)):
        message = json.loads(raw)
        if message.get('role') == 'assistant':
            recorded = message.get('tokens', {})
            aggregate.update(assistant_requests=1, input=recorded.get('input', 0),
                             output=recorded.get('output', 0), reasoning=recorded.get('reasoning', 0),
                             cache_read=recorded.get('cache', {}).get('read', 0))
        if sid == PARENT and message.get('role') == 'user' and first_user is None:
            first_user = created
        for pid, part_raw in connection.execute('select id,data from part where message_id=? order by time_created,id', (mid,)):
            part = json.loads(part_raw)
            # Do not export private intermediate reasoning; only visible text/tools.
            if part.get('type') == 'text':
                if sid == PARENT and (message.get('role') == 'user' or message.get('finish') == 'stop'):
                    messages.append({'session_id': sid, 'message_id': mid, 'part_id': pid, 'role': message.get('role'),
                                     'time': message.get('time', {'created': created}), 'text': part.get('text', '')})
                    if message.get('role') == 'assistant' and first_finish is None:
                        first_finish = message['time']['completed']
            if part.get('type') != 'tool':
                continue
            state = part.get('state', {})
            row = {'session_id': sid, 'message_id': mid, 'part_id': pid, 'tool': part.get('tool'),
                   'call_id': part.get('callID'), 'status': state.get('status'), 'time': state.get('time'),
                   'input': state.get('input'), 'error': state.get('error')}
            if row['tool'] == 'liuren_adjudication_packet':
                row['input'] = {'request_id': state.get('input', {}).get('packet', {}).get('request_id')}
                row['output'] = state.get('output')
                packet_calls.append(row)
            elif row['tool'] == 'task':
                row['result'] = json.loads(state['output'])
                row['metadata'] = state.get('metadata')
                tasks.append(row)
            if sid == PARENT:
                tool_rows.append(row)
    tokens[sid] = dict(aggregate)

connection.close()
save('visible-conversation.json', messages)
save('adjudications.json', tasks)
save('packet-calls.json', packet_calls)
save('tool-timeline.json', tool_rows)

packet_paths = sorted((ROOT / 'output/liuren-adjudication-requests').glob('LR-20261018-screen-repair-*.json'), key=lambda p: p.stat().st_mtime)
packets = [json.loads(p.read_text('utf-8'))['packet'] for p in packet_paths]
changes = {}
for key, value in packets[0].items():
    other = packets[1][key]
    if value == other:
        continue
    if isinstance(value, list) and all(isinstance(x, dict) and 'id' in x for x in value):
        old = {x['id']: x for x in value}; new = {x['id']: x for x in other}
        changes[key] = {'beforeCount': len(old), 'afterCount': len(new),
                        'changedOrAdded': [x for id_, x in new.items() if old.get(id_) != x],
                        'removedIds': [id_ for id_ in old if id_ not in new]}
    else:
        changes[key] = {'before': value, 'after': other}
save('packet-differences.json', changes)

book_calls = [x for x in tool_rows if x['tool'] == 'liuren_materials' and x.get('input', {}).get('action') == 'book_search']
start1, end1 = tasks[0]['time']['start'], tasks[0]['time']['end']
start2, end2 = tasks[1]['time']['start'], tasks[1]['time']['end']
phases = [('preparation_to_first_task', first_user, start1), ('first_adjudication', start1, end1),
          ('correction_and_second_dispatch', end1, start2), ('second_adjudication', start2, end2),
          ('final_report_after_second_task', end2, first_finish)]
summary = {
    'title': '电脑屏幕故障维修与换新占卜', 'parentSession': PARENT, 'childSessions': sessions[1:],
    'readOnlyDatabase': str(DATABASE), 'observedMethodRelease': '20261106-workflow-boundaries-08',
    'taskCalls': len(tasks), 'packetCalls': len(packet_calls),
    'packetError': 'O10 kind=shensha; observation.kind invalid value',
    'bothTasksPassedContractAndReadAllPages': all(x['metadata']['liurenAdjudication']['contractChecked'] and x['metadata']['liurenAdjudication']['pagesRead'] == 4 for x in tasks),
    'toolCounts': dict(collections.Counter(x['tool'] for x in tool_rows)),
    'methodCalls': sum(x['tool'] == 'liuren_materials' and x.get('input', {}).get('action') == 'method' for x in tool_rows),
    'bookSearchBatches': len(book_calls), 'bookQueries': sum(len(x['input'].get('queries', [])) for x in book_calls),
    'phases': [{'name': name, 'startUTC': dt.datetime.fromtimestamp(start/1000, dt.timezone.utc).isoformat(),
                'endUTC': dt.datetime.fromtimestamp(end/1000, dt.timezone.utc).isoformat(), 'seconds': round((end-start)/1000, 3)} for name, start, end in phases],
    'totalFirstReportSeconds': round((first_finish-first_user)/1000, 3), 'tokenRecordsIncludingFollowups': tokens,
    'packetFiles': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in packet_paths],
    'currentUserClarification': '是巳日，不是他理解的4日之后',
    'currentScreenshot': {'path': 'C:/Users/QLMa_/AppData/Local/Temp/codex-clipboard-6682b60f-bc65-4bef-893d-f1ecf33a8a7b.png',
                          'reportedFinalCompletion': '11月3日酉时彻底修好',
                          'reportedProcess': '反复购屏，次品或不满意；最后专业商家提供合适屏幕',
                          'purchaseCount': 'do not resolve screenshot ambiguity without clarification'},
    'feedbackChronology': {'historicalTranscript': '四日之后，原AI解为10月25日',
                           'correctedByUser': '巳日',
                           'dayCycleCheck': '以程序盘2026-10-18乙丑为锚，11月2日庚辰、11月3日辛巳；10月21日亦为辰日，不能只见辰即固定第一轮',
                           'cost': '650元，来自会话用户反馈；截图本身未给金额'},
    'changesAppliedToWorkflow': False,
}
save('summary.json', summary)
print(json.dumps({k: summary[k] for k in ['taskCalls', 'packetCalls', 'methodCalls', 'bookSearchBatches', 'bookQueries', 'phases', 'totalFirstReportSeconds']}, ensure_ascii=False, indent=2))
