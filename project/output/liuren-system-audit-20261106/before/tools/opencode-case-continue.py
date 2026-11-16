"""Continue the existing queue in small waves, without semantic review or subagents."""
import argparse
from collections import Counter
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wave', PROJECT / 'tools/opencode-case-wave.py')
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)
batch = wave.batch


def now():
    return dt.datetime.now().isoformat(timespec='seconds')


def workflow_check(run):
    """Check persisted process facts; model conclusions are not independently reviewed."""
    queue = batch.read_json(run / 'queue.json')
    if queue.get('review_mode') != 'workflow_only' or queue.get('content_review_waived_by_user') is not True:
        raise ValueError('未授权仅流程检查模式')
    job = queue['jobs'][0]
    if job['state'] != 'complete_pending_review' or (run / 'dispatcher.lock').exists():
        raise ValueError('分析尚未完成，不能准备归档')
    directory = run / 'cases' / job['alias']
    first, review = [batch.read_json(directory / (p + '.json')) for p in ['first', 'review']]
    for phase, data, schema in [('first', first, 'case-first-v1'), ('review', review, 'case-review-v1')]:
        if data.get('schema') != schema or data.get('task_alias') != job['alias']:
            raise ValueError('阶段结构或案例编号不一致')
        # Native exports validate the actual directory, provider, tools and skill delivery.
        native = batch.read_json(directory / (phase + '.session.json'))
        if Path(native['info']['directory']).resolve() != PROJECT.resolve():
            raise ValueError('原生会话工作目录不一致')
        batch.inspect_export(native)
    if batch.digest((directory / 'first.response.txt').read_bytes()) != job['initial_response_sha256']:
        raise ValueError('冻结的初判发生变化')
    if batch.digest(Path(job['source_file']).read_bytes()) != job['case_sha256']:
        raise ValueError('初级来源发生变化')
    source_chart = batch.read_json(Path(job['chart_file']))
    public = batch.read_json(run / 'public-inputs' / (job['alias'] + '.json'))
    if not source_chart['usable_for_batch_analysis'] or public['facts'] != source_chart['facts']:
        raise ValueError('盘面不再可用或输入facts不一致')
    if any(c.get('status') != '未验证从疑' or c.get('independent_validation_increment') != 0
           for c in review.get('experience_candidates', [])):
        raise ValueError('候选经验状态非法')
    category = first.get('zhanlei')
    if not category:
        header = review.get('case_archive_markdown', '').splitlines()[0:1]
        found = re.search(r'占类\s*=\s*([^|>\r\n]+)', header[0] if header else '')
        category = found.group(1).strip() if found else None
    mapping = {'考试占': '学业占', '交易占': '财运占', '疾病占': '健康占', '灾厄占': '健康占',
               '宅门占': '家宅占', '比赛占': '事业占', '胎产占': '感情占', '行人占': '出行占'}
    category = mapping.get(category, category)
    allowed = ['事业占', '财运占', '感情占', '学业占', '健康占', '出行占', '失物占',
               '官讼占', '家宅占', '天时占', '射覆占', '杂事占', '来意占']
    if category not in allowed:
        raise ValueError('模型缺少有效占类，不能确定归档目录')
    verdicts = [c.get('verdict') for c in review.get('dimension_checks', [])]
    feedback = '未载'
    if (job['feedback_status'] == '有明确标注反馈'
            and review['feedback_assessment']['kind'] == 'explicit_result'):
        if not verdicts or any(v not in ['correct', 'wrong', 'partial', 'unverifiable'] for v in verdicts):
            raise ValueError('逐问判验结构不完整')
        if all(v == 'correct' for v in verdicts):
            feedback = '验'
        elif all(v == 'wrong' for v in verdicts):
            feedback = '未验'
        elif any(v != 'unverifiable' for v in verdicts):
            feedback = '部分应验'
    record = {'mode': 'workflow_only', 'checked_at': now(), 'checks_passed': True,
              'semantic_review_performed': False, 'zhanlei': category, 'archive_feedback': feedback,
              'feedback_classification_source': 'DeepSeek复盘自报，未经独立核验',
              'first_json_sha256': batch.digest((directory / 'first.json').read_bytes()),
              'review_json_sha256': batch.digest((directory / 'review.json').read_bytes()),
              'notes': ['用户明确要求只走流程，不做内容审核；此记录不是Codex内容批准。',
                        '占类与逐问判验由DeepSeek给出，脚本只做格式映射，不确认术理或命中。',
                        '保留冻结初判及全部会话，疑似经验未验证从疑、验证增量0。']}
    batch.save_json(directory / 'workflow-check.json', record)
    return record


def progress(run, state):
    queue = batch.read_json(Path(state['source']) / 'queue.json')
    counts = dict(Counter(j['state'] for j in queue['jobs']))
    state.update(updated_at=now(), counts=counts)
    batch.save_json(run / 'controller.json', state)
    write_progress(run, state)


def write_progress(run, state, filename='进度.md'):
    """Read-only presentation of queue data; also usable by the live Chinese view."""
    queue = batch.read_json(Path(state['source']) / 'queue.json')
    counts = dict(Counter(j['state'] for j in queue['jobs']))
    rows = ['# OpenCode持续批处理进度', '', f'更新时间：{state["updated_at"]}', '',
            f'控制器状态：{batch.state_label(state["state"])}；当前阶段：{batch.phase_label(state.get("phase", ""))}',
            'DeepSeek Flash；每批5案、2个独立主会话并行；归档串行；禁止子智能体和重新排盘。',
            '**仅流程检查，未做内容审核；归档不代表判断正确或经验已验证。**', '',
            '队列状态：' + batch.counts_label(counts), '',
            f'当前批次：`{state.get("active_wave", "")}`',
            f'已结束批次：{len(state.get("finished_waves", []))}', '',
            '## 当前任务', '', '| 任务 | 原案例 | 状态 | 会话 |', '| --- | --- | --- | --- |']
    if queue.get('pause_target_aliases'):
        aliases = queue['pause_target_aliases']
        rows[4:4] = [f'本轮终点：{aliases[0]}～{aliases[-1]}；完成后自动暂停，等待中场整理。', '']
    active = state.get('active_wave')
    if active and (Path(active) / 'wave.json').exists():
        for row in batch.read_json(Path(active) / 'wave.json')['jobs']:
            job = batch.read_json(Path(row['run']) / 'queue.json')['jobs'][0]
            rows.append(f'| {job["alias"]} | {job["case_id"]} | {batch.state_label(job["state"], job)} | {job.get("session_id") or ""} |')
    rows += ['', '## 运行异常（如有）', '']
    rows += [f'- {e["alias"]} / {batch.phase_label(e["phase"])}：{e["error"]}' for e in state.get('errors', [])]
    rows += ['', '状态说明：独立分析中＝尚未揭示反馈；反馈复盘中＝正在对照反馈；'
             '复盘完成，待归档＝等待写入案例库、经验库及索引；已归档＝双库已写入并核对；'
             '异常暂缓，待重试＝本案暂时跳过，其他案例继续。', '',
             '暂停方式：在本控制目录创建 STOP 文件；当前小批次结束后停止新批次。']
    (run / filename).write_text('\n'.join(rows) + '\n', encoding='utf-8')


def execute(command, log_path, run, state):
    with log_path.open('a', encoding='utf-8') as log:
        child = subprocess.Popen([sys.executable, '-X', 'utf8', *command], cwd=PROJECT,
                                 stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        state['child_pid'] = child.pid
        while child.poll() is None:
            progress(run, state)
            time.sleep(5)
        state.pop('child_pid', None)
        progress(run, state)
        return child.returncode


def defer(run, row, state, phase, error):
    local = batch.read_json(Path(row['run']) / 'queue.json')
    local['jobs'][0].update(state='deferred_runtime_error', error=str(error))
    batch.save_json(Path(row['run']) / 'queue.json', local)
    state.setdefault('errors', []).append({'alias': row['alias'], 'phase': phase, 'error': str(error), 'at': now()})
    print('DEFER', row['alias'], phase, str(error), flush=True)


def pause_at_wave_boundary(source, state):
    """Persist a user-requested finite run so restarts cannot dispatch past it."""
    master = batch.read_json(source / 'queue.json')
    boundary = master.get('pause_after_finished_wave_count')
    if boundary is None or len(state['finished_waves']) < boundary:
        return False
    active = state.get('active_wave')
    if active and active not in state['finished_waves']:
        return False
    master.update(dispatch_paused=True,
                  pause_reason=master.get('pause_after_wave_reason', '用户要求本轮完成后暂停'),
                  paused_at=now())
    batch.save_json(source / 'queue.json', master)
    state.update(state='paused_after_completed_wave', pause_reason=master['pause_reason'],
                 phase='paused', pause_boundary_reached=True)
    return True


def continue_queue(source, run):
    run.mkdir(parents=True, exist_ok=True)
    lock = PROJECT / 'output/opencode-case-continuous.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    state = {'source': str(source), 'created_at': now(), 'state': 'running', 'pid': os.getpid(),
             'review_mode': 'workflow_only', 'finished_waves': [], 'errors': []}
    if (run / 'controller.json').exists():
        state.update(batch.read_json(run / 'controller.json'))
        state.update(state='running', pid=os.getpid())
        state.pop('error', None)
        state.pop('child_pid', None)
    try:
        failures_in_a_row = 0
        while True:
            if pause_at_wave_boundary(source, state):
                break
            master = batch.read_json(source / 'queue.json')
            if master.get('dispatch_paused') or (run / 'STOP').exists():
                state['state'] = 'paused_by_user'; break
            active = state.get('active_wave')
            if active and str(active) not in state['finished_waves']:
                target = Path(active)
                if (target / 'wave.lock').exists():
                    raise ValueError('当前批次仍有运行锁，拒绝重复启动')
            else:
                if not any(j['state'] == 'pending' for j in master['jobs']):
                    state['state'] = ('completed_with_deferred_errors' if any(j['state'] != 'archived' for j in master['jobs'])
                                      else 'completed')
                    break
                target = run / f'wave-{len(state["finished_waves"]) + 1:03d}'
                wave.prepare(source, target, 5, review_mode='workflow_only')
                state['active_wave'] = str(target)
            manifest = batch.read_json(target / 'wave.json')
            state['phase'] = 'analysis_and_feedback'
            seen_terminal = set()
            while any(batch.read_json(Path(r['run']) / 'queue.json')['jobs'][0]['state'] == 'pending'
                      for r in manifest['jobs']):
                execute([str(PROJECT / 'tools/opencode-case-wave.py'), 'run', '--wave', str(target)],
                        target / 'controller-worker.log', run, state)
                for row in manifest['jobs']:
                    job = batch.read_json(Path(row['run']) / 'queue.json')['jobs'][0]
                    if job['state'] == 'error':
                        # Phase-level retries already ran in the original native session.
                        defer(run, row, state, 'analysis', job.get('error', '分析进程错误'))
                        failures_in_a_row += 1
                        seen_terminal.add(row['alias'])
                    elif job['state'] == 'complete_pending_review' and row['alias'] not in seen_terminal:
                        failures_in_a_row = 0
                        seen_terminal.add(row['alias'])
                if failures_in_a_row >= 3:
                    raise ValueError('连续3案运行失败，停止新增调用并保留断点')
            wave.sync(target, quiet=True)
            for row in manifest['jobs']:
                local = Path(row['run'])
                job = batch.read_json(local / 'queue.json')['jobs'][0]
                if job['state'] in ['archived', 'deferred_runtime_error']:
                    continue
                if job['state'] != 'complete_pending_review':
                    raise ValueError('有未结束的原生分析，禁止写入共享库：' + row['alias'])
                state.update(phase='archive:' + row['alias'])
                try:
                    workflow_check(local)
                    for attempt in range(3):
                        code = execute([str(PROJECT / 'tools/archive-opencode-case.py'), '--run', str(local),
                                        '--alias', row['alias']], target / (row['alias'] + '.archive.log'), run, state)
                        archived = batch.read_json(local / 'queue.json')['jobs'][0]
                        if code == 0 and archived['state'] == 'archived':
                            break
                        lines = (target / (row['alias'] + '.archive.log')).read_text('utf-8').splitlines()
                        message = next((line for line in reversed(lines) if line.strip()), '归档失败')
                        repairable = any(x in message for x in ['META', '反馈状态', '疑似经验缺少', '预留归档路径',
                                                               '必须提供案例和经验', '未找到完整', 'JSON', 'skill'])
                        if attempt == 2 or not repairable:
                            raise ValueError(message)
                        q = batch.read_json(local / 'queue.json')
                        q['jobs'][0]['archive_format_repair'] = message
                        batch.save_json(local / 'queue.json', q)
                except Exception as exc:
                    defer(run, row, state, 'archive', exc)
                wave.sync(target, quiet=True)
                progress(run, state)
            final = wave.sync(target, quiet=True)
            final.update(state='completed_workflow_only', completed_at=now(), semantic_review_performed=False)
            batch.save_json(target / 'wave.json', final)
            state['finished_waves'].append(str(target))
            progress(run, state)
    except Exception as exc:
        state.update(state='stopped_runtime_error', error=str(exc))
        print('CONTROLLER_STOP', str(exc), flush=True)
    finally:
        progress(run, state)
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    continue_queue(args.source.resolve(), args.run.resolve())
