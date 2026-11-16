"""Whole-case preservation, controlled imports, source drift and event exclusions."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import liuren_book_cases as books
import case_retrieval as cases
import experience_retrieval as experience
import liuren_research_overlay as overlay
import liuren_knowledge_workbench as workbench


class BookCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = books.BOOKS['MODERN']
        self.put(self.source, '# 案甲\n某君问求财何时得？\n### 问题9：SECRET_ANSWER_TITLE\n原断曰：反吟只是反复。\n后曰未载明确反馈。\n\n# 案乙\n某君问求财是否成？\n原断曰：类神旺。\n反馈称得财，但原载身份待核。\n后注：别解。\n\n')
        self.first = self.record('001', 1, 5)
        self.second = self.record('002', 7, 11)
        self.save([self.first, self.second])

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        return target

    def record(self, number, start, end):
        data = (self.root / self.source).read_bytes()
        quote = '\n'.join(data.decode('utf-8').splitlines()[start - 1:end])
        return {'schema': 'liuren-book-case-v1', 'id': 'BK26-MODERN-' + number,
                'title': '原载求财案' + number, 'book_title': '本轮指定现代汇选', 'category': '财运占',
                'source_case_identity': f'book:{self.source}:L{start}-L{end}',
                'review_state': 'source_checked', 'completeness': 'complete',
                'boundary_note': '已经阅读上下案；本范围含此案主文与后注，下案另起。',
                'question': '求财何时得、是否能成？本轮忠实概括。', 'authors': ['原载未署名'],
                'source_refs': [{'path': self.source, 'line_start': start, 'line_end': end,
                                 'quote': quote, 'sha256': books.sha(data), 'role': '原载作答'}],
                'missing_fields': ['没有明确独立真实反馈'], 'feedback_status': '未载明确反馈',
                'method_rule_ids': [], 'same_event_ids': [], 'notes': ['无反馈仍保留方法价值']}

    def save(self, records):
        self.put(books.DIRECTORY + '/modern.json', json.dumps(records, ensure_ascii=False))

    def test_import_whole_case_idempotent_and_no_feedback_not_filtered(self):
        result = books.import_cases(self.root)
        self.assertEqual(result['active'], 2)
        self.assertEqual([x['action'] for x in result['actions']], ['created', 'created'])
        path = self.root / books.output_path(self.first)
        original = path.read_bytes()
        self.assertTrue(original.splitlines()[0].startswith(b'<!-- META:'))
        self.assertTrue(original.splitlines()[1].startswith(books.HEADER.encode('utf-8')))
        self.assertIn(self.first['source_refs'][0]['quote'], original.decode('utf-8'))
        self.assertIn('反馈=未载', original.decode('utf-8'))
        self.assertEqual([x['action'] for x in books.import_cases(self.root)['actions']], ['unchanged', 'unchanged'])
        self.assertEqual(path.read_bytes(), original)
        index = cases.ensure_index(self.root)
        self.assertEqual(len(index['cases']), 2)
        self.assertNotIn('SECRET_ANSWER_TITLE', str([u['question'] for u in index['units']]))
        self.assertTrue(all(c['evidence']['historical_verdict'] == '未载明确反馈' for c in index['cases']))

    def test_generated_original_fences_do_not_inject_fake_question_sections(self):
        data = (self.root / self.source).read_text(encoding='utf-8').splitlines()
        data[2] = '```text\n## 问题\nSECRET_RAW_RESULT\n```'
        self.put(self.source, '\n'.join(data) + '\n')
        first = self.record('001', 1, 8)
        self.save([first])
        books.import_cases(self.root)
        index = cases.ensure_index(self.root)
        self.assertNotIn('SECRET_RAW_RESULT', str([u['question'] for u in index['units']]))

    def test_meta_preserves_original_feedback_identity_without_claiming_verified(self):
        for status, label in [('原载反馈', '原载反馈（未独立核验）'), ('原载断语与结果混合', '原载断语与结果混合'),
                              ('未载明确反馈', '未载'), ('身份待核', '身份待核')]:
            with self.subTest(status=status):
                self.first['feedback_status'] = status
                self.save([self.first])
                books.import_cases(self.root)
                target = self.root / books.output_path(self.first)
                header = target.read_text(encoding='utf-8').splitlines()[0]
                self.assertIn('反馈=' + label + ' |', header)
                self.assertNotIn('反馈=验', header)
                self.assertEqual(cases.ensure_index(self.root)['cases'][0]['evidence']['historical_verdict'], status)

    def test_manual_edit_is_preserved_and_excluded_from_retrieval(self):
        books.import_cases(self.root)
        path = self.root / books.output_path(self.first)
        path.write_bytes(path.read_bytes() + b'\nHUMAN_EDIT\n')
        result = books.import_cases(self.root)
        self.assertEqual(result['actions'][0]['action'], 'conflict')
        self.assertIn(b'HUMAN_EDIT', path.read_bytes())
        index = cases.ensure_index(self.root)
        self.assertEqual(len(index['cases']), 1)
        self.assertTrue(index['status']['book_case_imports']['issues'])

    def test_managed_update_is_allowed_but_reclassification_needs_explicit_migration(self):
        books.import_cases(self.root)
        self.first['notes'].append('负责人新增已核说明')
        self.save([self.first, self.second])
        self.assertEqual(books.import_cases(self.root)['actions'][0]['action'], 'updated_managed')
        old_path = self.root / books.output_path(self.first)
        self.first['category'] = '事业占'
        self.save([self.first, self.second])
        result = books.import_cases(self.root)
        self.assertEqual(result['actions'][0]['action'], 'conflict')
        self.assertTrue(old_path.exists())
        self.assertFalse((self.root / books.output_path(self.first)).exists())
        self.assertEqual(len(cases.ensure_index(self.root)['cases']), 1)

    def test_duplicate_ids_and_untracked_files_are_not_overwritten(self):
        duplicate = copy.deepcopy(self.first)
        duplicate['title'] = '另一次登记不能复用稳定ID'
        self.save([self.first, duplicate])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])
        self.save([self.first])
        path = self.put(books.output_path(self.first), '人工此前已创建的同名文件')
        before = path.read_bytes()
        self.assertEqual(books.import_cases(self.root)['actions'][0]['action'], 'conflict')
        self.assertEqual(path.read_bytes(), before)

    def test_source_change_hides_old_generated_cases_even_with_cache(self):
        books.import_cases(self.root)
        self.assertEqual(len(cases.ensure_index(self.root)['cases']), 2)
        source = self.root / self.source
        source.write_bytes(source.read_bytes() + '后增未经复核文本'.encode('utf-8'))
        index = cases.ensure_index(self.root)
        self.assertEqual(index['cases'], [])
        self.assertEqual(books.import_cases(self.root)['active'], 0)
        self.assertTrue((self.root / books.output_path(self.first)).exists())

    def test_fragment_stays_registered_and_never_generates_library_case(self):
        self.first['completeness'] = 'fragment'
        self.save([self.first])
        result = books.validated_cases(self.root)
        self.assertEqual(len(result['valid_records']), 1)
        self.assertFalse(result['checks'][0]['eligible_for_import'])
        self.assertEqual(books.import_cases(self.root)['active'], 0)
        self.assertFalse((self.root / books.output_path(self.first)).exists())

    def test_missing_verdict_cannot_be_marked_complete(self):
        self.put(self.source, '# 原案\n断语遗失。\n')
        first = self.record('001', 1, 2)
        self.save([first])
        result = books.validated_cases(self.root)
        self.assertFalse(result['summary']['valid'])
        self.assertIn('原文明示关键内容遗失，不得标complete', result['checks'][0]['errors'])

    def test_main_identity_and_quote_integrity_are_strict(self):
        for mutation in ('hash', 'quote', 'identity', 'path'):
            with self.subTest(mutation=mutation):
                first = copy.deepcopy(self.first)
                if mutation == 'hash': first['source_refs'][0]['sha256'] = 'bad'
                elif mutation == 'quote': first['source_refs'][0]['quote'] = '只保留摘要'
                elif mutation == 'identity': first['source_case_identity'] = f'book:{self.source}:L2-L4'
                else: first['source_refs'][0]['path'] = '../.env'
                self.save([first])
                self.assertFalse(books.validated_cases(self.root)['summary']['valid'])

    def test_same_book_different_cases_stay_separate_and_exclude_by_overlap(self):
        books.import_cases(self.root)
        index = cases.ensure_index(self.root)
        self.assertEqual(cases.retrieve(index, '求财')['total_source_groups'], 2)
        found = cases.retrieve(index, '求财', exclude=[f'book:{self.source}:L2-L4'])
        self.assertEqual(found['total_source_groups'], 1)
        self.assertEqual(found['results'][0]['case']['book_case_id'], self.second['id'])
        self.assertNotIn(self.source, found['results'][0]['case']['source_ids'])

    def test_confirmed_same_event_groups_only_explicitly_linked_cases(self):
        self.second['same_event_ids'] = [self.first['id']]
        self.save([self.first, self.second])
        books.import_cases(self.root)
        index = cases.ensure_index(self.root)
        self.assertEqual(cases.retrieve(index, '求财')['total_source_groups'], 1)
        self.assertEqual(cases.retrieve(index, '求财', exclude=[self.first['id']])['results'], [])

    def test_borrowed_previous_chart_is_exclusion_dependency_but_not_same_event(self):
        previous_chart = copy.deepcopy(self.first['source_refs'][0])
        previous_chart.update(same_event=False, dependency_type='borrowed_chart')
        self.second['source_refs'].append(previous_chart)
        self.save([self.first, self.second])
        mappings = books.provenance(self.root)
        self.assertNotIn(self.second['id'], books.expand_identities([self.first['id']], mappings))
        self.assertIn(self.first['id'], books.expand_identities([self.second['id']], mappings, include_dependencies=True))
        books.import_cases(self.root)
        index = cases.ensure_index(self.root)
        self.assertEqual(cases.retrieve(index, '求财')['total_source_groups'], 2)
        self.assertEqual(cases.retrieve(index, '求财', exclude=[self.first['id']])['results'], [])

    def test_alias_overlap_ignores_shared_blank_lines(self):
        mapping = books.provenance(self.root)
        values = books.expand_identities([f'book:{self.source}:L6-L6'], mapping)
        self.assertNotIn(self.first['id'], values)
        self.assertNotIn(self.second['id'], values)

    def test_malformed_and_missing_relationships_report_issues(self):
        for key, value in {'source_refs': None, 'authors': 'string', 'method_rule_ids': ['LR26-MISSING'],
                           'same_event_ids': ['BK26-MODERN-999'], 'category': {}, 'review_state': []}.items():
            with self.subTest(key=key):
                first = copy.deepcopy(self.first)
                first[key] = value
                self.save([first])
                self.assertTrue(books.validated_cases(self.root)['issues'])

    def test_registry_removed_or_corrupt_cannot_leave_old_case_active(self):
        books.import_cases(self.root)
        self.put(books.DIRECTORY + '/modern.json', '{broken')
        self.assertEqual(cases.ensure_index(self.root)['cases'], [])

    def test_missing_key_image_blocks_complete_but_keeps_original_reference(self):
        source = self.root / self.source
        source.write_text('# 案\n问某事\n![关键盘图](assets/not-found.png)\n原断仍在。\n', encoding='utf-8')
        first = self.record('001', 1, 4)
        self.save([first])
        checked = books.validated_cases(self.root)
        self.assertFalse(checked['summary']['valid'])
        self.assertEqual(checked['checks'][0]['image_dependencies'][0]['state'], 'missing')
        first['completeness'] = 'fragment'
        self.save([first])
        self.assertTrue(books.validated_cases(self.root)['summary']['valid'])
        self.assertIn('![关键盘图]', books.render(dict(first, _registry_file='fixture.json')).decode('utf-8'))

    def test_supplemental_same_case_ref_and_source_hash_revalidated(self):
        ref = copy.deepcopy(self.second['source_refs'][0])
        self.first['source_refs'].append(ref)
        self.save([self.first])
        mappings = books.provenance(self.root)
        values = books.expand_identities([f'book:{self.source}:L8-L9'], mappings)
        self.assertIn(self.first['id'], values)

    def test_new_method_inherits_precise_book_case_exclusion(self):
        card = {'id': 'LR26-BOOK-TEST', 'title': '有限求财方法', 'claim_origin': '原文明示', 'status': 'source_method',
                'categories': ['财运占'], 'conclusion': '先辨过程反复', 'conditions': ['依原题'],
                'exclusions': ['不只凭反吟定败'], 'reasoning_steps': ['核对象'], 'alternatives': ['财旺则成'],
                'limitations': ['未独立验证'], 'support_case_ids': [f'book:{self.source}:L2-L4'],
                'counterexample_case_ids': [], 'legacy_entry_ids': [], 'relations': [],
                'evidence_refs': [self.first['source_refs'][0]], '_record_file': 'fixture.json'}
        loaded = {'rules': [card], 'audits': [], 'issues': [], 'summary': {'present': True}}
        base = {'entries': [], 'relations': [], 'status': {'entries': 0}}
        with patch.object(overlay, 'load', return_value=loaded):
            index = overlay.apply_experience(base, self.root)
        self.assertIn(self.first['id'], index['entries'][0]['case_refs'])
        self.assertNotIn(self.second['id'], index['entries'][0]['case_refs'])
        self.assertEqual(experience.retrieve(index, '求财', exclude=[self.first['id']])['results'], [])
        self.assertEqual(experience.retrieve(index, '求财', exclude=[f'book:{self.source}:L2-L4'])['results'], [])

    def test_fragment_registration_can_support_a_limited_method_card(self):
        self.first['completeness'] = 'fragment'
        self.save([self.first])
        card = {'schema': 'liuren-rule-card-v1', 'id': 'LR26-BOOK-MODERN-001',
                'title': '局部可读断语仍保留方法', 'categories': ['财运占'], 'claim_origin': '原文明示',
                'review_state': 'source_checked', 'status': 'source_method', 'conditions': ['只用尚存断语'],
                'exclusions': ['缺损盘式不补推'], 'conclusion': '保留局部方法', 'reasoning_steps': ['核原断'],
                'alternatives': ['不能由残案推出全案结局'], 'evidence_refs': [self.first['source_refs'][0]],
                'support_case_ids': [self.first['id'], self.first['source_case_identity']],
                'counterexample_case_ids': [], 'legacy_entry_ids': [], 'relations': [],
                'limitations': ['原案残缺；独立效果未验'], 'independent_validation_count': 0}
        self.put(books.BASE + '/rules/book-modern.json', json.dumps([card], ensure_ascii=False))
        self.first['method_rule_ids'] = [card['id']]
        self.save([self.first])
        result = workbench.validated_records(self.root)
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['rules'][0]['id'], card['id'])
        self.assertEqual(books.import_cases(self.root)['active'], 0)

    def test_bifa_transcript_primary_source_is_exact_and_book_scoped(self):
        for source, book, accepted in (
                (books.BIFA_TRANSCRIPT_SOURCE, 'BIFA', True),
                (books.BIFA_TRANSCRIPT_SOURCE, 'MODERN', False),
                ('课程写作/整理本/毕法赋全解/校勘记录.md', 'BIFA', False)):
            with self.subTest(source=source, book=book):
                self.source = source
                self.put(source, '孙鲁山问请告。\n原断不准退，反升。\n')
                record = self.record('099', 1, 2)
                record['id'] = 'BK26-' + book + '-099'
                self.save([record])
                self.assertEqual(books.validated_cases(self.root)['summary']['valid'], accepted)

    def test_bifa_transcript_method_reference_still_checks_identity_hash_and_quote(self):
        self.source = books.BIFA_TRANSCRIPT_SOURCE
        self.put(self.source, '孙鲁山问请告。\n原断不准退，反升。\n')
        record = self.record('099', 1, 2)
        record['id'] = 'BK26-BIFA-099'
        self.save([record])
        reference = dict(record['source_refs'][0], case_id=record['source_case_identity'])
        card = {'schema': 'liuren-rule-card-v1', 'id': 'LR26-BOOK-BIFA-099',
                'title': '转录独有案保留方法', 'categories': ['事业占'], 'claim_origin': '原文明示',
                'review_state': 'source_checked', 'status': 'source_method', 'conditions': ['请告问退'],
                'exclusions': ['独立结果未核'], 'conclusion': '保留原断分目标', 'reasoning_steps': ['核原断'],
                'alternatives': ['不由升象泛化全部目标'], 'evidence_refs': [record['source_refs'][0]],
                'source_case_refs': [reference], 'support_case_ids': [record['id']],
                'counterexample_case_ids': [], 'legacy_entry_ids': [], 'relations': [],
                'limitations': ['转录版本保留，独立效果未验'], 'independent_validation_count': 0}
        target = books.BASE + '/rules/book-bifa.json'
        self.put(target, json.dumps([card], ensure_ascii=False))
        self.assertEqual(workbench.validated_records(self.root)['issues'], [])
        for field, value in [('case_id', 'book:' + self.source + ':L1-L1'),
                             ('sha256', '0' * 64), ('quote', '替换原断')]:
            with self.subTest(field=field):
                changed = copy.deepcopy(card)
                changed['source_case_refs'][0][field] = value
                self.put(target, json.dumps([changed], ensure_ascii=False))
                self.assertTrue(workbench.validated_records(self.root)['issues'])

    def test_chart_fields_cannot_introduce_recomputed_facts(self):
        self.first['chart_fields'] = {'日干': '甲'}
        self.first['chart_fields']['三传'] = '寅午戌'
        self.save([self.first])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])

    def test_additional_event_identity_requires_an_exact_nonborrowed_source_ref(self):
        repeated = self.second['source_refs'][0]
        identity = self.second['source_case_identity']
        self.first['source_refs'].append(repeated)
        self.first['additional_source_case_identities'] = [identity]
        self.save([self.first])
        self.assertTrue(books.validated_cases(self.root)['summary']['valid'])
        repeated['same_event'] = False
        self.save([self.first])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])
        repeated.pop('same_event')
        self.first['additional_source_case_identities'] = [f'book:{self.source}:L8-L9']
        self.save([self.first])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])

    def test_original_specialized_category_and_cross_tags_preserved(self):
        self.first['category'] = '胎产占'
        self.first['subcategories'] = ['原书胎产', '健康关系']
        self.first['logic_tags'] = ['类神', '空墓状态']
        self.save([self.first])
        books.import_cases(self.root)
        index = cases.ensure_index(self.root)
        self.assertTrue((self.root / books.output_path(self.first)).exists())
        self.assertEqual(index['cases'][0]['original_category'], '胎产占')
        self.assertEqual(index['cases'][0]['classification']['logic_tags'], ['类神', '空墓状态'])
        self.assertTrue(cases.retrieve(index, fields={'占类': '胎产占'})['results'])

    def test_same_chart_as_previous_requires_a_separate_source_ref(self):
        self.put(self.source, '# 案\n课式同前\n原断内容仍在。\n前案课式原文\n')
        first = self.record('001', 1, 3)
        self.save([first])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])
        first['source_refs'].append({'path': self.source, 'line_start': 4, 'line_end': 4,
                                    'quote': '前案课式原文', 'sha256': books.sha((self.root / self.source).read_bytes()),
                                    'role': '原书断语'})
        self.save([first])
        self.assertTrue(books.validated_cases(self.root)['summary']['valid'])

    def reconstruction_fixture(self):
        rid = 'RC26-MODERN-001'
        relative = f'output/liuren-book-cases-20261102/reconstructions/{rid}.json'
        result = {'schema': 'liuren-book-reconstruction-result-v1', 'id': rid, 'case_id': self.first['id']}
        data = self.put(relative, json.dumps(result)).read_bytes()
        link = {'id': rid, 'result_path': relative, 'result_sha256': books.sha(data),
                'review_state': 'pending', 'note': '引擎候选身份，不能补写原文或自动complete。'}
        self.first['reconstruction_refs'] = [link]
        return link

    def test_reconstruction_link_is_separate_from_original_and_hash_bound(self):
        link = self.reconstruction_fixture()
        self.save([self.first])
        self.assertTrue(books.validated_cases(self.root)['summary']['valid'])
        books.import_cases(self.root)
        text = (self.root / books.output_path(self.first)).read_text(encoding='utf-8')
        self.assertIn('引擎衍生复原与人工复核（不是原书原载）', text)
        self.assertIn(link['result_path'], text)
        self.put(link['result_path'], '{}')
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])
        self.assertFalse(cases.ensure_index(self.root)['cases'])

    def test_reconstruction_review_must_explicitly_bind_case_result_and_hash(self):
        link = self.reconstruction_fixture()
        review_path = 'output/liuren-book-cases-20261102/review.json'
        review = {'case_id': self.first['id'], 'result_id': link['id'],
                  'result_path': link['result_path'], 'result_sha256': link['result_sha256'],
                  'semantic_review_state': 'source_checked'}
        data = self.put(review_path, json.dumps({'reviews': [review]})).read_bytes()
        link.update(review_state='source_checked', review_path=review_path, review_sha256=books.sha(data))
        self.save([self.first])
        with patch.object(books, 'verify_reconstruction_artifact', return_value={'ok': True, 'groups': [
                {'candidate_ids': ['RC26-MODERN-001-C01'], 'facts': {'heaven_earth': ['full-fixture-facts']}}]}) as verify:
            self.assertTrue(books.validated_cases(self.root)['summary']['valid'])
            verify.assert_called_once()
            books.import_cases(self.root)
            rendered = (self.root / books.output_path(self.first)).read_text(encoding='utf-8')
            self.assertIn('完整等价结构组1', rendered)
            self.assertIn('full-fixture-facts', rendered)
        review['case_id'] = self.second['id']
        data = self.put(review_path, json.dumps({'reviews': [review]})).read_bytes()
        link['review_sha256'] = books.sha(data)
        self.save([self.first])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])

    def test_reconstruction_raw_verifier_failure_blocks_formal_import(self):
        link = self.reconstruction_fixture()
        review = {'case_id': self.first['id'], 'result_id': link['id'],
                  'result_path': link['result_path'], 'result_sha256': link['result_sha256'],
                  'semantic_review_state': 'source_checked'}
        review_path = 'output/liuren-book-cases-20261102/review.json'
        data = self.put(review_path, json.dumps(review)).read_bytes()
        link.update(review_state='source_checked', review_path=review_path, review_sha256=books.sha(data))
        self.save([self.first])
        with patch.object(books, 'verify_reconstruction_artifact', side_effect=ValueError('raw archive changed')):
            result = books.import_cases(self.root)
        self.assertEqual(result['active'], 0)
        self.assertIn('复原链接', str(result))

    def test_reconstruction_cannot_link_a_different_case_or_an_unapproved_path(self):
        link = self.reconstruction_fixture()
        self.second['reconstruction_refs'] = [link]
        self.save([self.second])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])
        link['result_path'] = 'output/other.json'
        self.save([self.first])
        self.assertFalse(books.validated_cases(self.root)['summary']['valid'])


if __name__ == '__main__':
    unittest.main()
