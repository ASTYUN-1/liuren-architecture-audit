"""Behavior checks for reviewed evidence entering both local retrieval paths."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import experience_retrieval as experience
import case_retrieval as cases
import liuren_research_overlay as overlay


class ResearchOverlayTests(unittest.TestCase):
    def setUp(self):
        self.old = dict(id='H1', source='经验日志/旧.md', line_start=1, line_end=1,
                        source_excerpt='反吟必败，raw-qqwb20261019-0002。', summary='反吟必败',
                        title='反吟', categories=['财运占'], kind='条件规则', method_tags=[],
                        verification='来源称验', caveat='需核', case_refs=['案例项目库/交易占/case-001.md'],
                        annotation_status='旧批注', source_sha256='old', independent_validation_increment=0)
        self.base = dict(entries=[self.old], relations=[], status=dict(entries=1, curated_entries=1,
                         unreviewed_fragments=0, stale_annotations=[]))
        self.card = dict(id='LR26-A', title='反吟过程与结果分开', claim_origin='本轮归纳',
                         status='candidate', categories=['财运占'], conclusion='反吟先看反复，再辨得财条件。',
                         conditions=['问求财且课体反吟'], exclusions=['不可只凭反吟定失败'],
                         reasoning_steps=['区分过程与结果'], alternatives=['财旺而成的对照'],
                         limitations=['仅原载方法参照'], independent_validation_count=0,
                         support_case_ids=['raw-qqwb20261019-0026'], counterexample_case_ids=[],
                         legacy_entry_ids=['H1'], relations=[], _record_file='knowledge/liuren-research/20261102/rules/a.json',
                         evidence_refs=[dict(path='书籍库/测试.txt', line_start=1, line_end=1,
                                             quote='反吟主反复。', sha256='book', role='原书断语',
                                             case_id='raw-qqwb20261019-0026')])
        self.audit = dict(id='LA26-A', title='限缩旧规则', disposition='narrow', finding='只保留反复过程，不能直接推失败。',
                          reference_value='保留过程提示', target_entry_ids=['H1'],
                          target_case_paths=['案例项目库/交易占/case-001.md'],
                          replacement_rule_ids=['LR26-A'], limitations=['结果独立验证未完成'],
                          _record_file='knowledge/liuren-research/20261102/audits/a.json',
                          evidence_refs=self.card['evidence_refs'])
        self.loaded = dict(rules=[self.card], audits=[self.audit], issues=[], summary={'present': True})

    def attach(self):
        with patch.object(overlay, 'load', return_value=self.loaded):
            return overlay.apply_experience(self.base, Path('.'))

    def test_original_data_unmodified_and_repeated_attach_from_base_is_stable(self):
        before = copy.deepcopy(self.base)
        first, second = self.attach(), self.attach()
        self.assertEqual(self.base, before)
        self.assertEqual(first, second)
        self.assertEqual(len(first['entries']), 2)
        self.assertIn('历史摘录', first['entries'][0]['summary'])

    def test_conditions_and_review_are_visible_in_old_cli_renderer(self):
        found = experience.retrieve(self.attach(), '反吟')
        text = experience.render(found)
        self.assertIn('限缩适用范围', text)
        self.assertIn('不可只凭反吟定失败', text)
        self.assertIn('区分过程与结果', text)
        self.assertIn('保留价值：保留过程提示', text)
        self.assertIn('不否定整份作答', text)
        self.assertIn('原文已核对；效果未独立验证', text)

    def test_excluded_case_removes_rules_and_audits_that_reveal_it(self):
        result = experience.retrieve(self.attach(), '反吟', exclude=['raw-qqwb20261019-0026'])
        self.assertFalse(result['results'])
        result = experience.retrieve(self.attach(), '反吟', exclude=['raw-qqwb20261019-0002'])
        self.assertFalse(result['results'])

    def test_dependency_provenance_excludes_derived_rule(self):
        second = copy.deepcopy(self.card)
        second.update(id='LR26-B', legacy_entry_ids=[], support_case_ids=[],
                      relations=[dict(type='依赖', target_id='LR26-A', reason='沿用前提')],
                      evidence_refs=[dict(path='书籍库/另一.txt', line_start=2, line_end=2,
                                          quote='反吟。', sha256='x', role='原书断语')])
        self.loaded['rules'].append(second)
        found = experience.retrieve(self.attach(), '反吟', exclude=['raw-qqwb20261019-0026'])
        self.assertFalse(found['results'])

    def test_suspended_rule_is_never_rendered_as_unqualified_method(self):
        self.card['status'] = 'suspended'
        new = self.attach()['entries'][1]
        self.assertIn('暂停采用', new['summary'])
        self.assertEqual(new['independent_validation_increment'], 0)

    def test_invalid_audit_cannot_silently_restore_unqualified_old_summary(self):
        self.loaded.update(rules=[], audits=[], issues=[dict(id='LA26-A',
                           target_entry_ids=['H1'], target_case_paths=[], errors=['source_hash_changed'])])
        result = self.attach()
        self.assertIn('复核前不得', result['entries'][0]['caveat'])
        self.assertIn('失效', experience.render(experience.retrieve(result, '反吟')))

    def test_malformed_audit_file_warns_old_entries_and_keeps_packet_diagnostic(self):
        self.loaded.update(rules=[], audits=[], issues=[dict(record_file='audits/broken.json', error='invalid JSON')])
        result = self.attach()
        self.assertIn('加载缺口', result['entries'][0]['summary'])
        with patch.object(experience, 'ensure_index', return_value=result):
            packet = experience.evidence_packet(dict(question='求财', facts={'chart_types': ['反吟']}), root=Path('.'))
        self.assertEqual(packet['index_status']['research_issue_count'], 1)
        self.assertEqual(packet['index_status']['research_issues'][0]['record_file'], 'audits/broken.json')

    def test_new_rule_conditions_survive_batch_packet_compaction(self):
        with patch.object(experience, 'ensure_index', return_value=self.attach()):
            packet = experience.evidence_packet(dict(question='求财', facts={'chart_types': ['反吟']}),
                                                root=Path('.'))
        new = next(r['entry'] for r in packet['results'] if r['entry']['id'] == 'LR26-A')
        self.assertEqual(new['conditions'], self.card['conditions'])
        old = next(r['entry'] for r in packet['results'] if r['entry']['id'] == 'H1')
        self.assertEqual(old['review_notices'][0]['reference_value'], '保留过程提示')

    def test_case_overlay_preserves_reference_value_and_source_exclusion(self):
        case = dict(source='案例项目库/交易占/case-001.md', annotation_status='程序抽取',
                    origin_keys=['案例项目库/交易占/case-001.md'], mentioned_source_ids=[], source_group='case-one')
        index = {'cases': [case], 'status': {}}
        with patch.object(overlay, 'load', return_value=self.loaded):
            result = overlay.apply_cases(index, Path('.'))
        self.assertNotIn('review_notices', case)
        self.assertEqual(result['cases'][0]['review_notices'][0]['reference_value'], '保留过程提示')
        self.assertIn('raw-qqwb20261019-0026', result['cases'][0]['mentioned_source_ids'])

    def test_only_explicit_same_source_family_merges_legacy_entries(self):
        other = copy.deepcopy(self.old)
        other.update(id='H2', source='经验日志/另存.md')
        self.base['entries'].append(other)
        self.loaded['families'] = [dict(id='LF26-A', title='同案复写', merge_type='条件分支保持',
                                      rule_ids=['LR26-A'], legacy_entry_ids=['H1', 'H2'],
                                      common_method='已核同案', preserved_branches=[], unresolved=[])]
        found = experience.retrieve(self.attach(), '反吟')
        self.assertEqual(found['total_source_groups'], 3)
        self.loaded['families'][0]['merge_type'] = '同源归并'
        found = experience.retrieve(self.attach(), '反吟')
        self.assertEqual(found['total_source_groups'], 2)
        self.assertEqual(found['total_matching_units'], 3)

    def test_no_overlay_leaves_fixture_or_archived_workspace_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIs(overlay.apply_experience(self.base, Path(folder)), self.base)


if __name__ == '__main__':
    unittest.main()
