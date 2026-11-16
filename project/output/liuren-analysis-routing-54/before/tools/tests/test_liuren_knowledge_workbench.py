import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import liuren_knowledge_workbench as work


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = '书籍库/现代著作/测试.md'
        self.put(self.source, '# 作者甲\n同案第一作答\n同案第二作答\n反馈未载\n')

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        return target

    def card(self, identity='LR26-TEST'):
        data = (self.root / self.source).read_bytes()
        return {'schema': 'liuren-rule-card-v1', 'id': identity, 'title': '分条件保留作答参照',
                'categories': ['通用'], 'claim_origin': '文本可推知', 'review_state': 'source_checked',
                'status': 'source_method', 'conditions': ['仅对应原题当前对象'],
                'exclusions': ['没有真实结果反馈'], 'conclusion': '保留判断方法待进一步核对',
                'reasoning_steps': ['逐条区别原作答与反馈'], 'alternatives': ['两作答可能冲突'],
                'evidence_refs': [{'path': self.source, 'line_start': 2, 'line_end': 4,
                                   'quote': '同案第一作答\n同案第二作答\n反馈未载',
                                   'sha256': work.digest(data), 'role': '原载作答'}],
                'support_case_ids': [], 'counterexample_case_ids': [], 'legacy_entry_ids': [],
                'relations': [], 'limitations': ['单案多答不等于独立验证'],
                'independent_validation_count': 0}

    def validate(self, records):
        return work.validate_records(self.root, records, [], [])

    def test_source_method_without_explicit_feedback_is_valid(self):
        result = self.validate([self.card()])
        self.assertTrue(result['valid'])
        self.assertTrue(result['records'][0]['eligible_for_search'])

    def test_hash_tamper_blocks_even_if_quote_remains(self):
        card = self.card()
        self.put(self.source, '# 作者乙\n同案第一作答\n同案第二作答\n反馈未载\n')
        result = self.validate([card])
        self.assertFalse(result['valid'])
        self.assertIn('证据:source_hash_changed', result['records'][0]['errors'])

    def test_quote_cannot_skip_middle_line(self):
        card = self.card()
        card['evidence_refs'][0]['quote'] = '同案第一作答\n反馈未载'
        result = self.validate([card])
        self.assertFalse(result['valid'])
        self.assertIn('证据:quote_mismatch_or_noncontinuous', result['records'][0]['errors'])

    def test_missing_conditions_and_bad_relationship(self):
        card = self.card()
        card['conditions'] = []
        card['relations'] = [{'type': '依赖', 'target_id': 'LR26-NOT-THERE', 'reason': '测试'}]
        result = self.validate([card])
        self.assertFalse(result['valid'])
        self.assertIn('必需非空文本数组:conditions', result['records'][0]['errors'])
        self.assertIn('关系目标不存在:LR26-NOT-THERE', result['records'][0]['errors'])

    def test_paths_and_secret_files_rejected(self):
        for value in ('../outside.md', '/etc/passwd', 'C:/secret.md', 'books/../secret.md',
                      '.env', 'books/.env', 'books/private-key.txt', 'docs/unapproved.md'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                work.safe_path(self.root, value)

    def test_symlink_redirect_cannot_read_hidden_source(self):
        target = self.put('books/real.md', 'safe')
        link = self.root / 'books' / 'link.md'
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest('Windows当前权限不允许创建symlink')
        with self.assertRaises(ValueError):
            work.read_bytes(self.root, 'books/link.md')

    def test_pending_never_upgraded_by_build_and_empty_not_complete(self):
        card = self.card()
        card['review_state'] = 'pending'
        self.put(work.OVERLAY + '/rules/one.json', json.dumps([card], ensure_ascii=False))
        result = work.build(self.root)
        self.assertEqual(result['records'][0]['review_state'], 'pending')
        self.assertFalse(result['validation']['records'][0]['eligible_for_search'])
        self.assertEqual(result['coverage']['full_source_read_count'], 0)
        self.assertFalse(result['coverage']['complete'])
        self.assertTrue(all(x['state'] == 'pending' for x in result['tasks']))

    def test_same_case_multiple_answers_not_independent_events(self):
        result = work.build(self.root)
        asset = next(a for a in result['assets'] if a['path'] == self.source)
        self.assertIsNone(asset['event_count'])
        self.assertEqual(result['coverage']['independent_validation_count'], 0)
        self.assertEqual(len(result['tasks']), 1)

    def add_batch(self):
        public = 'analysis-ready/public/case-alias.json'
        private = 'analysis-ready/private/case-alias.json'
        public_bytes = self.put(work.BATCH + '/' + public, '{"question":"问考试"}\n').read_bytes()
        self.put(work.BATCH + '/' + private, 'NEVER_OPEN_RESERVED_ANSWER')
        item = {'case_id': 'raw-qqwb20261019-0002', 'public_path': public,
                'private_path': private, 'public_sha256': work.digest(public_bytes),
                'private_sha256': 'declared-not-read', 'has_explicit_feedback': False,
                'has_assignment_reference': True, 'charts': [{}, {}]}
        self.put(work.BATCH + '/analysis_manifest.json', json.dumps(
            {'cases': [item], 'counts': {'有效有作答来源': 1, '程序盘数量': 2}}, ensure_ascii=False))
        return private

    def test_reserved_answer_never_read_or_put_into_public_task(self):
        self.add_batch()
        original = Path.read_bytes
        def guard(path):
            if '/private/' in path.as_posix():
                raise AssertionError('预留答案被打开')
            return original(path)
        with patch.object(Path, 'read_bytes', guard):
            result = work.build(self.root)
            packet = work.next_packet(self.root, result, kind='question201_public')
        self.assertEqual(len(result['public_tasks']), 1)
        self.assertEqual(result['private_tasks'][0]['state'], 'reserved')
        self.assertNotIn('NEVER_OPEN_RESERVED_ANSWER', json.dumps(packet))
        self.assertFalse(result['exposure']['cases'][0]['clean_holdout'])
        self.assertEqual(result['coverage']['question201']['source_records'], 1)

    def test_unselected_answer_evidence_rejected(self):
        private = self.add_batch()
        with self.assertRaises(ValueError):
            work.read_bytes(self.root, work.BATCH + '/' + private)

    def test_exposed_cases_need_both_selection_and_old_ledger(self):
        self.add_batch()
        self.assertEqual(work.selected_exposed_tokens(self.root), set())
        self.put(work.DEVELOPMENT, json.dumps({'excluded_from_independent_evaluation':
                                             ['raw-qqwb20261019-0002', 'raw-qqwb20261019-0009']}))
        tokens = work.selected_exposed_tokens(self.root)
        self.assertIn('case-alias', tokens)
        self.assertNotIn('raw-qqwb20261019-0009', tokens)

    def test_pending_dependency_blocks_derived_card(self):
        first = self.card('LR26-FIRST')
        first['review_state'] = 'pending'
        derived = self.card('LR26-DERIVED')
        derived['relations'] = [{'type': '依赖', 'target_id': first['id'], 'reason': '依赖取用'}]
        result = self.validate([first, derived])
        self.assertFalse(result['records'][1]['eligible_for_search'])

    def test_suspend_audit_retains_suspended_explanation(self):
        first = self.card('LR26-SUSPENDED')
        first['status'] = 'suspended'
        audit = {'schema': 'liuren-audit-v1', 'id': 'LA26-SUSPEND', 'title': '暂停错误推导',
                 'target_entry_ids': [], 'target_case_paths': [], 'disposition': 'suspend',
                 'finding': '原推导不成立', 'reasoning': ['原文条件不全'], 'evidence_refs': first['evidence_refs'],
                 'replacement_rule_ids': [first['id']], 'limitations': ['仍可追溯原错误'],
                 'review_state': 'source_checked'}
        result = self.validate([first, audit])
        self.assertTrue(result['valid'])
        self.assertTrue(result['records'][1]['eligible_for_search'])

    def test_non_dependency_conflict_does_not_invalidate_valid_card(self):
        invalid = self.card('LR26-INVALID')
        invalid['evidence_refs'][0]['sha256'] = 'tampered'
        good = self.card('LR26-GOOD')
        good['relations'] = [{'type': '冲突', 'target_id': invalid['id'], 'reason': '两法不同'}]
        result = self.validate([invalid, good])
        self.assertTrue(result['records'][1]['eligible_for_search'])
        self.assertEqual(result['records'][1]['related_status_notes'][0]['state'], 'blocked')

    def test_book_case_registry_separate_from_selected_semantic_evidence(self):
        card = self.card()
        ref = copy.deepcopy(card['evidence_refs'][0])
        ref['line_start'] = 1
        ref['quote'] = '# 作者甲\n同案第一作答\n同案第二作答\n反馈未载'
        ref['case_id'] = f'book:{self.source}:L1-L4'
        card['source_case_refs'] = [ref]
        card['support_case_ids'] = [ref['case_id']]
        self.assertTrue(self.validate([card])['valid'])
        card['source_case_refs'][0]['sha256'] = 'changed'
        self.assertFalse(self.validate([card])['valid'])

    def test_book_case_requires_matching_evidence_span(self):
        card = self.card()
        card['support_case_ids'] = [f'book:{self.source}:L2-L4']
        self.assertTrue(self.validate([card])['valid'])
        card['support_case_ids'] = [f'book:{self.source}:L1-L4']
        self.assertFalse(self.validate([card])['valid'])

    def test_invalid_audit_exposes_target_ids_not_stale_finding(self):
        card = self.card()
        self.put(work.OVERLAY + '/rules/one.json', json.dumps([card], ensure_ascii=False))
        audit = {'schema': 'liuren-audit-v1', 'id': 'LA26-TEST', 'title': '旧经验审查',
                 'target_entry_ids': ['E-MISSING'], 'target_case_paths': [], 'disposition': 'narrow',
                 'finding': '不能采用的旧结论', 'reasoning': ['条件不全'], 'evidence_refs': card['evidence_refs'],
                 'replacement_rule_ids': [], 'limitations': ['未完'], 'review_state': 'source_checked'}
        self.put(work.OVERLAY + '/audits/one.json', json.dumps([audit], ensure_ascii=False))
        result = work.validated_records(self.root)
        self.assertEqual(result['issues'][0]['target_entry_ids'], ['E-MISSING'])
        self.assertNotIn('finding', result['issues'][0])
        self.assertEqual(len(result['rules']), 1)
        self.assertEqual(result['audits'], [])

    def test_bazi_only_in_inventory_not_liuren_queue(self):
        self.put('书籍库/八字书籍/子平.txt', '八字正文')
        result = work.build(self.root)
        self.assertTrue(any(a['scope'] == 'other_tradition_inventory_only' for a in result['assets']))
        self.assertFalse(any('子平' in t['path'] for t in result['tasks']))

    def test_next_line_budget_preserves_contiguous_quote_and_resumes(self):
        result = work.build(self.root)
        task = result['tasks'][0]
        packet = work.next_packet(self.root, result, task_id=task['id'], from_line=2, max_chars=15)['packets'][0]
        self.assertEqual(packet['evidence_window']['quote'], '同案第一作答\n同案第二作答')
        self.assertEqual(packet['remaining_from_line'], 4)
        self.assertIn('--from-line 4', packet['resume_command'])

    def test_explicit_reading_progress_skips_only_declared_lines(self):
        result = work.build(self.root)
        task = result['tasks'][0]
        work.record_reading(self.root, result, path=self.source, line_start=1, line_end=2,
                            sha256=task['sha256'], outcome='no_new', note='已实际阅读，暂无新增')
        result = work.build(self.root)
        self.assertEqual(result['tasks'][0]['state'], 'partially_read_declared')
        packet = work.next_packet(self.root, result)['packets'][0]
        self.assertEqual(packet['evidence_window']['line_start'], 3)
        self.assertEqual(result['coverage']['full_source_read_count'], 0)
        work.record_reading(self.root, result, path=self.source, line_start=3, line_end=4,
                            sha256=task['sha256'], outcome='needs_review', note='读完但方法边界仍需复核')
        result = work.build(self.root)
        self.assertEqual(result['coverage']['full_source_read_count'], 1)
        self.assertEqual(result['tasks'][0]['state'], 'fully_read_declared')
        self.assertEqual(work.next_packet(self.root, result, kind='book_text')['packets'], [])
        self.assertEqual(len(work.next_packet(self.root, result, kind='review_followup')['packets']), 1)
        self.assertEqual(result['coverage']['reading_windows_fully_reviewed'], 0)

    def test_changed_source_invalidates_reading_progress_and_returns_to_queue(self):
        result = work.build(self.root)
        work.record_reading(self.root, result, path=self.source, line_start=1, line_end=4,
                            sha256=result['assets'][0]['sha256'], outcome='no_new', note='实际已读')
        self.put(self.source, '# 作者改\n同案第一作答\n同案第二作答\n反馈未载\n')
        result = work.build(self.root)
        self.assertFalse(result['validation']['valid'])
        self.assertTrue(result['reading_progress']['issues'])
        self.assertEqual(work.next_packet(self.root, result)['packets'][0]['evidence_window']['line_start'], 1)

    def test_extracted_reading_requires_real_link_and_build_preserves_progress(self):
        result = work.build(self.root)
        with self.assertRaises(ValueError):
            work.record_reading(self.root, result, path=self.source, line_start=1, line_end=4,
                                sha256=result['assets'][0]['sha256'], outcome='extracted', note='缺链接')
        self.assertFalse((self.root / work.PROGRESS).exists())
        work.record_reading(self.root, result, path=self.source, line_start=1, line_end=4,
                            sha256=result['assets'][0]['sha256'], outcome='no_new', note='实际已读')
        before = (self.root / work.PROGRESS).read_bytes()
        work.write_outputs(self.root, work.build(self.root))
        self.assertEqual((self.root / work.PROGRESS).read_bytes(), before)

    def test_malformed_arrays_fail_without_crashing(self):
        card = self.card()
        card['legacy_entry_ids'] = None
        self.assertFalse(self.validate([card])['valid'])

    def test_malformed_schema_variants_return_readable_issues(self):
        values = {'evidence_refs': 'not-an-array', 'relations': 'not-an-array',
                  'review_state': [], 'status': {}, 'claim_origin': [],
                  'support_case_ids': None, 'id': {}, 'source_case_refs': 'not-an-array'}
        for key, value in values.items():
            with self.subTest(key=key):
                card = self.card()
                card[key] = value
                self.put(work.OVERLAY + '/rules/malformed.json', json.dumps([card], ensure_ascii=False))
                result = work.validated_records(self.root)
                self.assertEqual(result['rules'], [])
                self.assertTrue(result['issues'])

    def test_families_explicit_links_and_missing_ids(self):
        card = self.card()
        self.put(work.OVERLAY + '/rules/one.json', json.dumps([card], ensure_ascii=False))
        family = {'id': 'LF26-TEST', 'title': '原文条件族', 'rule_ids': [card['id']],
                  'legacy_entry_ids': [], 'merge_type': '条件分支', 'common_method': '保留条件',
                  'preserved_branches': ['原题边界'], 'unresolved': ['待核反馈']}
        self.put(work.OVERLAY + '/families/one.json', json.dumps([family], ensure_ascii=False))
        result = work.build(self.root)
        self.assertEqual(result['coverage']['explicit_rule_family_count'], 1)
        self.assertEqual(len(work.search(result, '作答')['results'][0]['rule_families']), 1)
        family['rule_ids'] = ['LR26-MISSING']
        self.put(work.OVERLAY + '/families/one.json', json.dumps([family], ensure_ascii=False))
        result = work.validated_records(self.root)
        self.assertTrue(result['issues'])
        self.assertEqual(result['families'], [])

    def test_search_excludes_case_identity_in_evidence(self):
        self.add_batch()
        card = self.card()
        card['evidence_refs'][0]['case_id'] = 'raw-qqwb20261019-0002'
        self.put(work.OVERLAY + '/rules/one.json', json.dumps([card], ensure_ascii=False))
        result = work.build(self.root)
        self.assertEqual(len(work.search(result, '作答')['results']), 1)
        self.assertEqual(work.search(result, '作答', exclude=['raw-qqwb20261019-0002'])['results'], [])


if __name__ == '__main__':
    unittest.main()
