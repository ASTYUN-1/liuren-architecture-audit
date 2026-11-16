"""Run independent native OpenCode sessions with bounded concurrency and isolated state."""
import argparse
import contextlib
import copy
import datetime as dt
import importlib.util
import json
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('batch', PROJECT / 'tools/opencode-case-batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


def prepare(source, wave, count, review_mode='all'):
    if wave.exists():
        raise ValueError('批次目录已存在，不覆盖')
    queue = batch.read_json(source / 'queue.json')
    if queue.get('dispatch_paused'):
        raise ValueError('用户已暂停后续批次，不建立新批次')
    if review_mode == 'workflow_only' and queue.get('content_review_waived_by_user') is not True:
        raise ValueError('用户未授权免内容审核')
    pending = [j for j in queue['jobs'] if j['state'] == 'pending'][:count]
    if not pending:
        raise ValueError('没有待执行案例')
    wave.mkdir(parents=True)
    manifest = {'created_at': dt.datetime.now().isoformat(), 'source_run': str(source),
                'concurrency': 2, 'review_mode': review_mode, 'archive_mode': 'serial_after_wave',
                'jobs': []}
    # Snapshot hashes apply to this entire wave: no archives until all first analyses finish.
    snapshot = []
    for name in ['.opencode/skills', '案例项目库', '经验日志', '书籍库', 'books']:
        for p in (PROJECT / name).rglob('*'):
            if p.is_file():
                snapshot.append({'file': str(p.relative_to(PROJECT)), 'sha256': batch.digest(p.read_bytes())})
    batch.save_json(wave / 'knowledge-snapshot.json', snapshot)
    for original in pending:
        job = copy.deepcopy(original)
        run = wave / 'jobs' / job['alias']
        for folder in ['public-inputs', 'private', 'cases']:
            (run / folder).mkdir(parents=True)
        for folder in ['public-inputs', 'private']:
            shutil.copyfile(source / folder / (job['alias'] + '.json'), run / folder / (job['alias'] + '.json'))
        (run / 'runtime-instructions.md').write_text(batch.INSTRUCTIONS, encoding='utf-8')
        local = {'schema': queue['schema'], 'created_at': manifest['created_at'], 'model': batch.MODEL,
                 'workspace': str(PROJECT), 'run': str(run), 'authorized_case_ids': [job['case_id']],
                 'authorization': '用户同意2会话并行、前5案逐案审核、串行归档，禁止子智能体。', 'jobs': [job]}
        if review_mode == 'workflow_only':
            local.update(review_mode=review_mode, content_review_waived_by_user=True,
                         authorization='用户要求持续批处理，只走流程、不做内容审核；2个独立主会话，禁止子智能体，串行归档。')
        batch.save_json(run / 'queue.json', local)
        manifest['jobs'].append({'alias': job['alias'], 'case_id': job['case_id'], 'run': str(run), 'state': 'pending'})
    queue['authorized_case_ids'] = [j['case_id'] for j in queue['jobs']]
    queue['approval_gate'] = ('用户明确免除内容审核；保留结构、模型、工具、冻结、归档和未验证状态检查。'
                              if review_mode == 'workflow_only' else
                              '用户已同意批量方案；前5案逐案审核，之后普通案约20%抽查，疑似经验与异常全审。')
    queue['active_wave'] = str(wave)
    batch.save_json(source / 'queue.json', queue)
    batch.save_json(wave / 'wave.json', manifest)
    print(json.dumps({'prepared': len(pending), 'concurrency': 2, 'wave': str(wave)}, ensure_ascii=False))


def sync(wave, quiet=False):
    manifest = batch.read_json(wave / 'wave.json')
    source = Path(manifest['source_run'])
    master = batch.read_json(source / 'queue.json')
    for row in manifest['jobs']:
        job = batch.read_json(Path(row['run']) / 'queue.json')['jobs'][0]
        row.update(state=job['state'], session_id=job.get('session_id'), error=job.get('error'))
        for i, old in enumerate(master['jobs']):
            if old['case_id'] == job['case_id']:
                master['jobs'][i] = dict(job, execution_run=row['run'])
                break
    batch.save_json(source / 'queue.json', master)
    batch.save_json(wave / 'wave.json', manifest)
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            batch.status(source)
    else:
        batch.status(source)
    policy = ('仅流程检查，不做内容审核' if manifest.get('review_mode') == 'workflow_only' else '逐案审核')
    lines = ['# OpenCode批次进度', '', f'2个独立会话并行；{policy}；共享档案串行写入。', '',
             '| 任务 | 来源 | 状态 | 会话 |', '| --- | --- | --- | --- |']
    lines += [f'| {r["alias"]} | {r["case_id"]} | {batch.state_label(r["state"])} | {r.get("session_id") or ""} |' for r in manifest['jobs']]
    (wave / '进度.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return manifest


def run_wave(wave):
    manifest = batch.read_json(wave / 'wave.json')
    lock = wave / 'wave.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    running = {}
    waiting = [r for r in manifest['jobs'] if batch.read_json(Path(r['run']) / 'queue.json')['jobs'][0]['state'] == 'pending']
    failure = False
    try:
        while waiting or running:
            owned = {row['alias'] for _, row, _ in running.values()}
            external = sum(batch.read_json(Path(row['run']) / 'queue.json')['jobs'][0]['state'] in
                           ['first_running', 'first_saved', 'review_running']
                           for row in manifest['jobs'] if row['alias'] not in owned)
            while waiting and len(running) + external < 2 and not failure:
                row = waiting.pop(0)
                log = (wave / (row['alias'] + '.worker.log')).open('a', encoding='utf-8')
                command = [sys.executable, '-X', 'utf8', str(PROJECT / 'tools/opencode-case-batch.py'),
                           'run', '--run', row['run'], '--limit', '1']
                child = subprocess.Popen(command, cwd=PROJECT, stdout=log, stderr=subprocess.STDOUT,
                                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                running[child.pid] = (child, row, log)
                print('START', row['alias'], 'worker_pid', child.pid, flush=True)
            for pid, (child, row, log) in list(running.items()):
                if child.poll() is None:
                    continue
                log.close(); del running[pid]
                state = batch.read_json(Path(row['run']) / 'queue.json')['jobs'][0]['state']
                print('STOP', row['alias'], state, flush=True)
                if child.returncode or state != 'complete_pending_review':
                    failure = True
            sync(wave, quiet=True)
            if failure and not running:
                break
            if running:
                time.sleep(5)
    finally:
        lock.unlink(missing_ok=True)
        sync(wave)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'sync'])
    parser.add_argument('--wave', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--review-mode', choices=['all', 'workflow_only'], default='all')
    args = parser.parse_args()
    wave = args.wave.resolve()
    if args.command == 'prepare':
        prepare(args.source.resolve(), wave, args.count, args.review_mode)
    elif args.command == 'run':
        run_wave(wave)
    else:
        sync(wave)
