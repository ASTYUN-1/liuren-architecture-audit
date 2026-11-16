import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('batch', Path(__file__).parents[1] / 'opencode-case-batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


class DispatchContractTests(unittest.TestCase):
    def test_blind_packet_excludes_feedback_raw_text_source_ids_and_result_titles(self):
        text = '''# 已知结果标题SECRET_TITLE
## 1. 来源与状态
- 反馈状态：有明确标注反馈
## 2. 起课信息与人物
- 人物与年命原文：辛酉男
## 3. 背景、问题与要求
能找到工作吗？
## 4. 明确标注的反馈
SECRET_FEEDBACK
## 5. 作答及其他未核验内容
SECRET_ANSWER
## 6. 待核事项
SECRET_REVIEW
## 7. 完整原文
SECRET_RAW
'''
        chart = {'facts': {'day_pillar': '甲子'}, 'source': {'case_id': 'SECRET_SOURCE'},
                 'policy': {'timezone': 'Asia/Shanghai', 'time_basis': 'civil'}, 'effective_settings': {}}
        blind, disclosed = batch.split_input(text, chart, 'case-0001')
        self.assertNotIn('SECRET', json.dumps(blind))
        self.assertEqual(blind['people_declared_in_question'], '辛酉男')
        self.assertIn('SECRET_FEEDBACK', json.dumps(disclosed))
        self.assertIn('SECRET_ANSWER', json.dumps(disclosed))

    def test_runtime_denies_delegation_write_network_and_uses_deepseek_for_small_model(self):
        config = batch.runtime_config(Path('isolated-workspace'))
        self.assertEqual(config['model'], config['small_model'])
        self.assertEqual(config['enabled_providers'], ['deepseek'])
        for tool in ['task', 'background_task', 'call_omo_agent', 'bash', 'edit', 'write', 'external_directory']:
            self.assertEqual(config['permission'][tool], 'deny')
        self.assertTrue(all(not v['enabled'] for v in config['mcp'].values()))

    def test_export_rejects_wrong_provider_and_forbidden_tools(self):
        data = {'messages': [{'info': {'role': 'assistant', 'providerID': 'minimax', 'modelID': 'x'}, 'parts': []}]}
        with self.assertRaises(ValueError):
            batch.inspect_export(data)
        data['messages'][0]['info'].update(providerID='deepseek', modelID='deepseek-flash')
        data['messages'][0]['parts'] = [{'type': 'tool', 'tool': 'task'}]
        with self.assertRaises(ValueError):
            batch.inspect_export(data)

    def test_unverified_answers_are_explicitly_disclosed_as_unverified(self):
        prompt = batch.review_prompt('case-0001', {'unverified_answers_not_ground_truth': 'SECRET_ANSWER'}, 'abc')
        self.assertIn('绝不能当现实反馈', prompt)
        self.assertIn('independent_validation_increment', prompt)
        self.assertIn('初判保持原样', prompt)

    def test_selected_assignments_are_high_quality_learning_references(self):
        prompt = batch.review_prompt('case-0001', {'unverified_answers_not_ground_truth': '精选作答'}, 'abc')
        self.assertIn('很高参考质量', prompt)
        self.assertIn('reference_comparison', prompt)
        self.assertIn('优秀作业参照提取', prompt)
        self.assertIn('unverifiable', prompt)
        self.assertNotIn('没有明确反馈不反推', prompt)
        self.assertIn('不直接增强旧规则权重', prompt)

    def test_reference_policy_does_not_duplicate_on_archive_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / 'policy.md'
            policy.write_text('优秀作业具有很高参考质量；初判仍独立。', encoding='utf-8')
            with patch.object(batch, 'REFERENCE_POLICY', policy):
                effective = batch.reference_policy_prompt('归档任务')
                self.assertEqual(effective, batch.reference_policy_prompt(effective))
                self.assertIn('很高参考质量', effective)

    def test_missing_review_skill_retries_only_review_in_the_same_session(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            job = {'alias': 'case-0007', 'session_id': 'same-native-session',
                   'initial_response_sha256': 'frozen', 'attempts': []}
            queue = {'review_mode': 'workflow_only', 'jobs': [job]}
            calls = []
            def native_attempt(run, job, phase, prompt, timeout):
                calls.append((phase, prompt, job['session_id']))
                job['attempts'].append({'phase': phase, 'state': 'running'})
                if len(calls) == 1:
                    raise ValueError('复盘未加载经验提取规则')
                return {'schema': 'case-review-v1'}
            with patch.object(batch, 'CURRENT_QUEUE', queue), patch.object(batch, 'invoke_once', side_effect=native_attempt):
                result = batch.invoke(run, job, 'review', '原复盘任务')
            self.assertEqual(result['schema'], 'case-review-v1')
            self.assertEqual([c[0] for c in calls], ['review', 'review'])
            self.assertTrue(all(c[2] == 'same-native-session' for c in calls))
            self.assertIn('liuren-extract', calls[1][1])
            self.assertIn('禁止重做初判', calls[1][1])
            self.assertEqual(job['initial_response_sha256'], 'frozen')

    def test_missing_review_skill_has_a_bounded_retry_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            job = {'alias': 'case-0007', 'attempts': []}
            queue = {'review_mode': 'workflow_only', 'jobs': [job]}
            def always_missing(*args):
                job['attempts'].append({'phase': 'review', 'state': 'running'})
                raise ValueError('复盘未加载经验提取规则')
            with patch.object(batch, 'CURRENT_QUEUE', queue), patch.object(batch, 'invoke_once', side_effect=always_missing):
                with self.assertRaisesRegex(ValueError, '复盘未加载'):
                    batch.invoke(Path(temporary), job, 'review', '复盘')
            self.assertEqual(len(job['attempts']), 3)

    def test_cli_progress_is_not_mistaken_for_final_json(self):
        text = '我先加载skills。\n' + json.dumps({'schema': 'case-first-v1', 'task_alias': 'case-0001'})
        self.assertEqual(batch.parse_result(text)['task_alias'], 'case-0001')
        with self.assertRaises(ValueError):
            batch.parse_result(text + '\n任务还未完成')

    def test_review_extra_root_brace_is_repaired_without_changing_values(self):
        head = {'schema': 'case-review-v1', 'task_alias': 'case-0014',
                'feedback_assessment': {'kind': 'explicit_result'}, 'dimension_checks': [],
                'revision_markdown': '原文保留 } , "experience_candidates": 和换行\n第二行'}
        tail = {'experience_candidates': [], 'case_archive_markdown': '案例原文', 'experience_archive_markdown': ''}
        malformed = json.dumps(head, ensure_ascii=False) + ',' + json.dumps(tail, ensure_ascii=False)[1:]
        repairs = []
        self.assertEqual(batch.parse_result(malformed, repairs), dict(head, **tail))
        self.assertEqual(len(repairs), 1)
        self.assertFalse(repairs[0]['string_values_modified'])
        with self.assertRaises(ValueError):
            batch.parse_result(malformed[:-1])

    def test_review_brace_repair_rejects_duplicate_keys_or_other_boundaries(self):
        head = {'schema': 'case-review-v1', 'task_alias': 'case-0014', 'feedback_assessment': {},
                'dimension_checks': [], 'revision_markdown': '原文'}
        duplicate = json.dumps(head) + ',"experience_candidates":[],"task_alias":"other","case_archive_markdown":"","experience_archive_markdown":""}'
        with self.assertRaises(ValueError):
            batch.parse_result(duplicate)
        head['schema'] = 'case-first-v1'
        malformed = json.dumps(head) + ',"experience_candidates":[],"case_archive_markdown":"","experience_archive_markdown":""}'
        with self.assertRaises(ValueError):
            batch.parse_result(malformed)

    def test_length_recovery_keeps_existing_blind_judgment(self):
        exported = {'messages': [{'info': {'role': 'assistant', 'finish': 'length'}}]}
        self.assertEqual(batch.last_finish(exported), 'length')
        prompt = batch.compact_first_prompt('case-0001')
        self.assertIn('尚未给你任何反馈', prompt)
        self.assertIn('首选的月份与日期须如实保留', prompt)
        self.assertIn('不重新检索', prompt)

    def test_stray_backslash_is_preserved_without_repairing_truncation(self):
        raw = r'{"schema":"case-first-v1","analysis_markdown":"原文\ n说明\n次行"}'
        value = batch.parse_result(raw)
        self.assertEqual(value['analysis_markdown'], '原文\\ n说明\n次行')
        normal = {'schema': 'case-first-v1', 'path': 'C:\\Users\\example', 'quoted': '"引号"'}
        self.assertEqual(batch.parse_result(json.dumps(normal)), normal)
        with self.assertRaises(ValueError):
            batch.parse_result(raw[:-1])

    def test_windows_temporary_sharing_violation_does_not_abort_dispatcher(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'queue.json'
            replace = batch.os.replace
            attempts = []
            def temporarily_locked(source, destination):
                attempts.append(1)
                if len(attempts) == 1:
                    raise PermissionError('simulated sharing violation')
                return replace(source, destination)
            with patch.object(batch.os, 'replace', side_effect=temporarily_locked), patch.object(batch.time, 'sleep'):
                batch.save_json(target, {'state': 'running'})
            self.assertEqual(batch.read_json(target)['state'], 'running')
            self.assertEqual(len(attempts), 2)

    def test_read_permissions_follow_parent_git_worktree_without_exposing_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            (parent / '.git').mkdir()
            project = parent / '六壬八字测算'
            project.mkdir()
            run = project / 'output/pilot'
            config = batch.runtime_config(project, run)
            read = config['permission']['read']
            self.assertEqual(read['六壬八字测算/案例项目库/*'], 'allow')
            self.assertEqual(read['六壬八字测算/output/pilot/public-inputs/*'], 'allow')
            self.assertEqual(read['*'], 'deny')
            self.assertFalse(any('private' in pattern or '初级案例资料' in pattern for pattern in read))
            self.assertEqual(config['permission']['grep'], 'deny')
            self.assertEqual(config['permission']['glob'], 'deny')


    def test_json_reader_retries_temporary_windows_permission_denial(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'wave.json'
            target.write_text('{"state":"completed"}', encoding='utf-8')
            read_text = Path.read_text
            attempts = []
            def temporarily_locked(path, *args, **kwargs):
                attempts.append(1)
                if len(attempts) == 1:
                    raise PermissionError('simulated transient Windows read lock')
                return read_text(path, *args, **kwargs)
            with patch.object(Path, 'read_text', temporarily_locked), patch.object(batch.time, 'sleep'):
                self.assertEqual(batch.read_json(target), {'state': 'completed'})
            self.assertEqual(len(attempts), 2)


if __name__ == '__main__':
    unittest.main()
