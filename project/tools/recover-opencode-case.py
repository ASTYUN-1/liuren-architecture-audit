"""Recover a native response after dispatcher bookkeeping failed; do not redo blind work."""
import argparse
import importlib.util
import json
from pathlib import Path
import time

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('batch', PROJECT / 'tools/opencode-case-batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


def recover(run):
    queue = batch.read_json(run / 'queue.json')
    batch.CURRENT_QUEUE = queue
    job = queue['jobs'][0]
    assert job['state'] in ['error', 'first_running'] and not (run / 'dispatcher.lock').exists()
    assert not any(a['phase'] == 'review' for a in job['attempts'])
    job['state'] = 'first_running'
    batch.save_json(run / 'queue.json', queue)
    phase = 'first'
    case_dir = run / 'cases' / job['alias']
    prefix = f'first-{sum(a["phase"] == phase for a in job["attempts"])}'
    log = case_dir / (prefix + '.jsonl')
    started = time.monotonic()
    print('WAIT_EXISTING_SESSION', job['alias'], job['session_id'], flush=True)
    while True:
        events = []
        for line in log.read_text('utf-8').splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        if events and ((events[-1].get('type') == 'step_finish' and
                        events[-1].get('part', {}).get('reason') not in ['tool-calls', 'tool_calls'])
                       or events[-1].get('type') == 'error'):
            break
        if time.monotonic() - started > 1200:
            raise TimeoutError('原生会话仍未给出完整回复，保留等待，不重复分析')
        time.sleep(2)
    prompt = (case_dir / (prefix + '.prompt.txt')).read_text('utf-8')
    try:
        batch.finalize_attempt(run, job, phase, prefix, prompt)
    except ValueError:
        exported = batch.read_json(case_dir / 'first.session.json')
        if batch.last_finish(exported) == 'length':
            batch.invoke(run, job, 'first', batch.compact_first_prompt(job['alias']))
        else:
            # Format repair remains blind. Never repair an already disclosed first.
            try:
                batch.parse_result((case_dir / 'first.response.txt').read_text('utf-8'))
            except ValueError:
                prompt = batch.compact_first_prompt(job['alias']).replace(
                    '上一条回复因输出长度上限被截断',
                    '上一条完整回复的JSON格式校验失败（value数组结尾多了双引号等语法问题）')
                batch.invoke(run, job, 'first', prompt)
            else:
                raise
    job['initial_response_sha256'] = batch.digest((case_dir / 'first.response.txt').read_bytes())
    job.update(state='first_saved', recovery='Existing native response recovered; no blind rerun')
    job.pop('error', None)
    batch.save_json(run / 'queue.json', queue)
    batch.run_jobs(run, limit=1, retry=True)


def recover_review(run):
    queue = batch.read_json(run / 'queue.json')
    batch.CURRENT_QUEUE = queue
    job = queue['jobs'][0]
    assert job['state'] == 'error' and not (run / 'dispatcher.lock').exists()
    case_dir = run / 'cases' / job['alias']
    assert batch.digest((case_dir / 'first.response.txt').read_bytes()) == job['initial_response_sha256']
    prompt = f'''继续{job['alias']}，上一份复盘JSON在revision_markdown结尾多了一个右花括号，导致语法校验失败。
    不改已冻结初判，不重新排盘、检索或加载skill，不调用子智能体，仅沿用已读资料补交完整case-review-v1 JSON，控制2500中文字以内。
    两问都无现实反馈，dimension_checks均unverifiable；原首选、备选、应期窗口与主次不能偷换。
    复盘补记日德与降低置信可以保留，但无反馈不能证明旧规则须加强、限制或改写。上份所谓limit只是旧资料的断法提醒，不是本案验证的新发现；experience_candidates请为空数组、experience_archive_markdown为空字符串，案例稿写无可采纳新增疑似链条，仅留待反馈核验记录。
    保留原有schema/task_alias/feedback_assessment/dimension_checks/revision_markdown/experience_candidates/case_archive_markdown/experience_archive_markdown字段，只返回闭合合法JSON。'''
    job['state'] = 'review_running'
    batch.save_json(run / 'queue.json', queue)
    batch.invoke(run, job, 'review', prompt)
    job.update(state='complete_pending_review', recovery='Review format repair in existing native session')
    job.pop('error', None)
    batch.save_json(run / 'queue.json', queue)


def recover_saved_review(run):
    """Reparse an already finished native review; issue no new model request."""
    queue = batch.read_json(run / 'queue.json')
    batch.CURRENT_QUEUE = queue
    job = queue['jobs'][0]
    assert job['state'] in ['error', 'deferred_runtime_error'] and not (run / 'dispatcher.lock').exists()
    case_dir = run / 'cases' / job['alias']
    first_hash = batch.digest((case_dir / 'first.response.txt').read_bytes())
    first_json_hash = batch.digest((case_dir / 'first.json').read_bytes())
    assert first_hash == job['initial_response_sha256']
    count = sum(a['phase'] == 'review' for a in job['attempts'])
    assert count and job['attempts'][-1]['phase'] == 'review'
    prefix = f'review-{count}'
    events = [json.loads(line) for line in (case_dir / (prefix + '.jsonl')).read_text('utf-8').splitlines()]
    assert events[-1].get('type') == 'step_finish' and events[-1].get('part', {}).get('reason') == 'stop'
    original = (case_dir / (prefix + '.response.txt')).read_bytes()
    # Fail before doing an export if the saved reply still cannot be parsed.
    batch.parse_result(original.decode('utf-8'))
    batch.save_json(case_dir / 'queue-before-saved-review-recovery.json', queue)
    result = batch.finalize_attempt(run, job, 'review', prefix,
                                    (case_dir / (prefix + '.prompt.txt')).read_text('utf-8'))
    assert (case_dir / (prefix + '.response.txt')).read_bytes() == original
    assert batch.digest((case_dir / 'first.response.txt').read_bytes()) == first_hash
    assert batch.digest((case_dir / 'first.json').read_bytes()) == first_json_hash
    for filename, key in [('复盘.md', 'revision_markdown'), ('案例候选稿.md', 'case_archive_markdown'),
                          ('经验候选稿.md', 'experience_archive_markdown')]:
        (case_dir / filename).write_text(result.get(key, '') + '\n', encoding='utf-8')
    job.update(state='complete_pending_review', feedback_kind=result['feedback_assessment']['kind'],
               candidate_count=len(result.get('experience_candidates', [])),
               recovery='Saved review recovered by a single syntax correction; no model call or blind rerun')
    job.pop('error', None)
    batch.save_json(run / 'queue.json', queue)
    batch.save_json(case_dir / 'saved-review-recovery.json', {
        'source_attempt': prefix, 'first_response_sha256': first_hash, 'first_json_sha256': first_json_hash,
        'review_json_sha256': batch.digest((case_dir / 'review.json').read_bytes()),
        'same_session_id': job['session_id'], 'new_model_calls': 0,
        'original_response_preserved': True, 'semantic_review_performed': False})
    print('RECOVERED_SAVED_REVIEW', job['alias'], 'new_model_calls=0', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--phase', choices=['first', 'review', 'saved-review'], default='first')
    args = parser.parse_args()
    {'first': recover, 'review': recover_review, 'saved-review': recover_saved_review}[args.phase](args.run.resolve())
