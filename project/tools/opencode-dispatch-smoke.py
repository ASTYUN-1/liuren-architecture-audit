"""Verify local OpenCode dispatch with DeepSeek only; no case/library writes."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess

PROJECT = Path(__file__).resolve().parents[1]


def config():
    deny = {k: 'deny' for k in ['*', 'task', 'background_task', 'call_omo_agent', 'bash', 'edit', 'write', 'read', 'skill', 'webfetch', 'websearch']}
    return {
        'model': 'deepseek/deepseek-flash',
        'small_model': 'deepseek/deepseek-flash',
        'default_agent': 'batch-main',
        'enabled_providers': ['deepseek'],
        'plugin': [], 'share': 'disabled',
        'permission': deny,
        'agent': {'batch-main': {
            'mode': 'primary', 'model': 'deepseek/deepseek-flash',
            'description': 'DeepSeek-only dispatch verification',
            'permission': deny,
        }},
        'skills': {'paths': [str(PROJECT / '.opencode/skills')]},
        'mcp': {name: {'enabled': False} for name in [
            'memory', 'sequential-thinking', 'chrome-devtools', 'context7',
            'filesystem', 'scrapling', 'windows-mcp', 'aoci',
        ]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Send two smoke prompts and one follow-up to configured DeepSeek')
    args = parser.parse_args()
    if not args.execute:
        parser.print_help()
        return
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    out = PROJECT / 'output' / ('opencode-dispatch-smoke-' + stamp)
    out.mkdir(parents=True, exist_ok=False)
    cfg = config()
    (out / 'runtime-policy.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    env = dict(os.environ, OPENCODE_CONFIG_CONTENT=json.dumps(cfg),
               OPENCODE_DISABLE_PROJECT_CONFIG='true', OPENCODE_DISABLE_AUTOUPDATE='true')
    evidence = {'scope': 'dispatch-smoke-only', 'directory': str(PROJECT), 'turns': [], 'sessions': []}

    def save():
        (out / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')

    def turn(label, prompt, session=None):
        command = ['opencode', 'run', '--pure', '--model', 'deepseek/deepseek-flash',
                   '--agent', 'batch-main', '--format', 'json']
        command += ['--session', session] if session else ['--title', '批量分发联调-' + label + '-' + stamp]
        command += [prompt]
        record = {'label': label, 'status': 'running', 'prompt': prompt, 'session_id': session}
        evidence['turns'].append(record)
        save()
        print('START ' + label, flush=True)
        try:
            with (out / (label + '.jsonl')).open('w', encoding='utf-8') as log:
                result = subprocess.run(command, cwd=PROJECT, env=env, stdout=log,
                                        stderr=subprocess.PIPE, text=True, encoding='utf-8',
                                        errors='replace', timeout=150)
            record['returncode'] = result.returncode
            events = []
            for line in (out / (label + '.jsonl')).read_text(encoding='utf-8').splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            record['session_id'] = next((v['sessionID'] for v in events if v.get('sessionID')), session)
            record['text'] = '\n'.join(v.get('part', {}).get('text', '') for v in events if v.get('type') == 'text')
            record['tool_names'] = [v.get('part', {}).get('tool') for v in events if v.get('type') == 'tool_use']
            record['error_types'] = [v.get('error', {}).get('name', 'error') for v in events if v.get('type') == 'error']
            record['status'] = 'completed' if result.returncode == 0 and record['text'] and not record['error_types'] else 'error'
            if result.returncode:
                (out / (label + '.stderr.txt')).write_text(result.stderr, encoding='utf-8')
        except subprocess.TimeoutExpired:
            record['status'] = 'timeout'
        save()
        print(json.dumps(record, ensure_ascii=False), flush=True)
        return record

    first = turn('A', '这是本机任务分发联调，不进行案例分析。禁止调用任何工具、子智能体、后台任务或其他模型。请仅回复 ACK-A-731。')
    second = turn('B', '这是第二条独立任务分发联调。禁止调用任何工具、子智能体、后台任务或其他模型。请仅回复 ACK-B-842。')
    if first['status'] == 'completed' and first.get('session_id'):
        turn('A-followup', '仍禁止调用任何工具、子智能体或后台任务。请先原样写出你上一轮回复的确认码，再单独一行回复 FOLLOWUP-OK。', first['session_id'])
    for r in [first, second]:
        if not r.get('session_id'):
            continue
        export = subprocess.run(['opencode', '--pure', 'export', r['session_id']], cwd=PROJECT,
                                env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
        try:
            data = json.loads(export.stdout)
            info = data.get('info', {})
            messages = data.get('messages', [])
            assistants = [m['info'] for m in messages if m.get('info', {}).get('role') == 'assistant']
            tools = [p.get('tool') for m in messages for p in m.get('parts', []) if p.get('type') == 'tool']
            evidence['sessions'].append({'id': info.get('id'), 'title': info.get('title'),
                'directory': info.get('directory'), 'parentID': info.get('parentID'),
                'assistant_turns': [{'providerID': m.get('providerID'), 'modelID': m.get('modelID'),
                                     'finish': m.get('finish'), 'completed': m.get('time', {}).get('completed')} for m in assistants],
                'tool_calls': tools})
        except json.JSONDecodeError:
            evidence['sessions'].append({'id': r['session_id'], 'export_failed': True})
        save()
    print('EVIDENCE ' + str(out / 'evidence.json'), flush=True)
    print(json.dumps(evidence['sessions'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
