"""Behavioral regression checks for freshness, provenance and retrieval boundaries."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import experience_retrieval as retrieval


class ExperienceRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = '经验日志/古籍-测试.md'
        self.path = self.root / self.source
        self.path.parent.mkdir()
        self.path.write_text('# 测试\n## 甲\n铸印占病，须辨救神。\n## 乙\n反吟问考试，留意例外。\n', encoding='utf-8')
        self.catalog = dict(sources=[dict(path=self.source, sha256=hashlib.sha256(self.path.read_bytes()).hexdigest())],
                            entries=[self.entry('A', 3, '铸印占病，须辨救神。', '铸印救神'),
                                     self.entry('B', 5, '反吟问考试，留意例外。', '考试反吟')], relations=[])
        self.write_catalog()

    def entry(self, key, line, quote, title):
        return dict(id=key, source=self.source, line_start=line, line_end=line,
                    title=title, summary=title, source_excerpt=quote, categories=['健康占', '学业占'],
                    kind='技巧', verification='书籍提取未核原典', method_tags=[], caveat='需核原典',
                    case_refs=[], independent_validation_increment=0)

    def write_catalog(self):
        path = self.root / retrieval.SNAPSHOT
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.catalog, ensure_ascii=False), encoding='utf-8')

    def test_multiple_rules_in_one_file_are_separately_retrievable(self):
        found = retrieval.retrieve(retrieval.ensure_index(self.root), '考试')
        self.assertEqual([r['entry']['id'] for r in found['results']], ['B'])

    def test_category_alias_and_variant_spelling(self):
        found = retrieval.retrieve(retrieval.ensure_index(self.root), '返吟', ['考试占'])
        self.assertEqual(found['results'][0]['entry']['id'], 'B')

    def test_any_term_and_all_terms_have_distinct_behavior(self):
        index = retrieval.ensure_index(self.root)
        self.assertEqual(len(retrieval.retrieve(index, '铸印 考试')['results']), 2)
        self.assertEqual(len(retrieval.retrieve(index, '铸印 考试', match_all=True)['results']), 0)

    def test_append_automatically_enters_as_unreviewed(self):
        retrieval.ensure_index(self.root)
        with self.path.open('a', encoding='utf-8') as out:
            out.write('## 新方法\n独有新词：冲空取期，反馈验。\n')
        found = retrieval.retrieve(retrieval.ensure_index(self.root), '独有新词')
        self.assertTrue(found['results'])
        e = found['results'][0]['entry']
        self.assertEqual(e['verification'], '未整理待核')
        self.assertEqual(e['independent_validation_increment'], 0)

    def test_modified_quote_never_reuses_old_rule_or_line(self):
        retrieval.ensure_index(self.root)
        self.path.write_text(self.path.read_text(encoding='utf-8').replace('铸印占病，须辨救神。', '修订词：铸印不能一概而论。'), encoding='utf-8')
        index = retrieval.ensure_index(self.root)
        self.assertNotIn('A', [e['id'] for e in index['entries']])
        self.assertEqual(index['status']['stale_annotations'][0]['id'], 'A')
        result = retrieval.retrieve(index, '修订词')['results'][0]['entry']
        self.assertEqual(result['verification'], '未整理待核')

    def test_prepend_relocates_quote_but_flags_changed_context(self):
        self.path.write_text('新增前言\n' + self.path.read_text(encoding='utf-8'), encoding='utf-8')
        result = retrieval.retrieve(retrieval.ensure_index(self.root), '考试')['results'][0]['entry']
        self.assertEqual(result['id'], 'B')
        self.assertEqual(result['line_start'], 6)
        self.assertIn('需复核', result['annotation_status'])

    def test_deleted_source_disappears_and_is_reported(self):
        retrieval.ensure_index(self.root)
        self.path.unlink()
        index = retrieval.ensure_index(self.root)
        self.assertFalse(index['entries'])
        self.assertEqual(index['status']['missing_sources'], [self.source])

    def test_same_source_groups_retain_distinct_method_summaries(self):
        self.catalog['relations'] = [dict(id='R1', type='同源复写', members=['A', 'B'], reason='同案转引')]
        self.write_catalog()
        result = retrieval.retrieve(retrieval.ensure_index(self.root), '铸印 考试')
        self.assertEqual(result['total_matching_units'], 2)
        self.assertEqual(result['total_source_groups'], 1)
        group = result['results'][0]
        self.assertEqual(len(group['also_matched_entries']), 1)
        self.assertEqual(group['entry']['independent_validation_increment'], 0)

    def test_similar_and_conflicting_rules_are_not_collapsed(self):
        self.catalog['relations'] = [dict(id='R1', type='冲突待核', members=['A', 'B'], reason='需辨条件')]
        self.write_catalog()
        result = retrieval.retrieve(retrieval.ensure_index(self.root), '铸印 考试')
        self.assertEqual(result['total_source_groups'], 2)
        self.assertTrue(result['results'][0]['related'])

    def test_exclusion_covers_rewrites_and_associated_case(self):
        self.catalog['entries'][0]['case_refs'] = ['案例项目库/健康占/case-1-已知同案.md']
        self.catalog['relations'] = [dict(id='R1', type='同源复写', members=['A', 'B'], reason='同案转引')]
        self.write_catalog()
        result = retrieval.retrieve(retrieval.ensure_index(self.root), '考试', exclude=['case-1-已知同案'])
        self.assertFalse(result['results'])

    def test_new_file_is_searchable_even_before_category_is_assigned(self):
        retrieval.ensure_index(self.root)
        (self.path.parent / '新文件.md').write_text('# 新增\n未分类独有词，应保留从疑。\n', encoding='utf-8')
        result = retrieval.retrieve(retrieval.ensure_index(self.root), '未分类独有词', ['失物占'])
        self.assertTrue(result['results'])
        self.assertEqual(result['results'][0]['entry']['kind'], '原文片段')

    def test_packet_preserves_blind_boundary_and_does_not_mutate_public_input(self):
        cases = self.root / '案例项目库/健康占'
        cases.mkdir(parents=True)
        (cases / 'case-1-已知同案.md').write_text('来源ID=raw-current', encoding='utf-8')
        self.catalog['entries'][0]['case_refs'] = ['案例项目库/健康占/case-1-已知同案.md']
        self.write_catalog()
        public = dict(question='考试如何', facts=dict(chart_types=['铸印']))
        before = copy.deepcopy(public)
        packet = retrieval.evidence_packet(public, 'raw-current', self.root)
        ids = [r['entry']['id'] for r in packet['results']]
        self.assertNotIn('A', ids)
        self.assertIn('B', ids)
        self.assertEqual(public, before)

    def test_long_relationship_question_keeps_issue_methods_before_cross_domain_chart_hits(self):
        index = retrieval.ensure_index(self.root)
        a, b = index['entries']
        a.update(title='元首闭口妻病', categories=['健康占'], summary='元首 闭口', source_excerpt='元首 闭口')
        b.update(title='复合主动联系与出轨审查', categories=['感情占'],
                 summary='真心与出轨分别核对', source_excerpt='感情原文')
        before = copy.deepcopy(index)
        public = dict(question='男方对女方的感情是否真心，是否有与其他女性暧昧或出轨的倾向',
                      facts=dict(chart_types=['元首', '闭口']), domains=['relationship'])
        packet = retrieval.evidence_packet(public, root=self.root, index=index, budget=None)
        self.assertEqual(packet['results'][0]['entry']['id'], 'B')
        self.assertIn('出轨', packet['results'][0]['matched_terms'])
        self.assertIn('A', [row['entry']['id'] for row in packet['results']])  # comparison still available
        self.assertEqual(index, before)

    def test_local_packet_preserves_large_in_domain_candidate_instead_of_dropping_it(self):
        index = retrieval.ensure_index(self.root)
        index['entries'][0].update(categories=['感情占'], title='复合联系',
                                 conditions=['完整条件' * 4000])
        packet = retrieval.evidence_packet(dict(question='复合联系', facts={}, domains=['relationship']),
                                           root=self.root, index=index, budget=None)
        self.assertEqual(packet['results'][0]['entry']['conditions'], ['完整条件' * 4000])
        self.assertEqual(packet['omitted_by_packet_budget'], 0)
        self.assertIsNone(packet['coverage']['packet_budget'])

    def test_pregnancy_is_not_a_relationship_category_alias(self):
        index = retrieval.ensure_index(self.root)
        index['entries'][0].update(categories=['胎产占'], title='元首胎产', summary='元首')
        index['entries'][1].update(categories=['感情占'], title='元首感情', summary='元首')
        result = retrieval.retrieve(index, '元首', categories=['感情占'])
        self.assertEqual([row['entry']['id'] for row in result['results']], ['B'])


class BatchIntegrationTests(unittest.TestCase):
    @staticmethod
    def load_batch():
        spec = importlib.util.spec_from_file_location('case_batch_test', TOOLS / 'opencode-case-batch.py')
        batch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(batch)
        return batch

    def test_original_tool_and_read_boundaries_are_preserved(self):
        batch = self.load_batch()
        root = TOOLS.parent
        config = batch.runtime_config(root, root / 'output/offline-test-run')
        self.assertEqual(config['permission']['task'], 'deny')
        self.assertEqual(config['permission']['bash'], 'deny')
        self.assertEqual(config['permission']['read']['*'], 'deny')
        self.assertFalse(any('/private/' in k for k, v in config['permission']['read'].items() if v == 'allow'))
        self.assertTrue(Path(config['instructions'][-1]).is_file())

    def test_review_query_is_never_written_to_public_inputs(self):
        batch = self.load_batch()
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'public-inputs').mkdir()
            (run / 'cases/case-0001').mkdir(parents=True)
            (run / 'public-inputs/case-0001.json').write_text(json.dumps(dict(
                question='考试', facts=dict(chart_types=['蒿矢']))), encoding='utf-8')
            (run / 'cases/case-0001/review.json').write_text(json.dumps(dict(
                experience_candidates=[dict(condition='揭示反馈后的独有查询词')])), encoding='utf-8')
            job = dict(alias='case-0001', case_id='raw-nonexistent', attempts=[])
            batch.retrieval_prompt(run, job, 'first', '初判', TOOLS.parent)
            public_before = {p.name: p.read_bytes() for p in (run / 'public-inputs').iterdir()}
            result = batch.retrieval_prompt(run, job, 'archive', '归档', TOOLS.parent)
            public_after = {p.name: p.read_bytes() for p in (run / 'public-inputs').iterdir()}
            self.assertEqual(public_before, public_after)
            self.assertIn('揭示反馈后的独有查询词', result)
            self.assertTrue((run / 'cases/case-0001/archive-1.experience-retrieval.json').exists())

    def test_archive_reuses_saved_result_with_same_retrieval_context(self):
        spec = importlib.util.spec_from_file_location('retrieval_archive_test', TOOLS / 'archive-opencode-case.py')
        archive = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(archive)
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            directory = run / 'cases/case-0001'
            directory.mkdir(parents=True)
            (run / 'public-inputs').mkdir()
            (run / 'queue.json').write_text(json.dumps(dict(workspace=str(TOOLS.parent))), encoding='utf-8')
            (run / 'public-inputs/case-0001.json').write_text(json.dumps(dict(
                question='考试', facts=dict(chart_types=['蒿矢']))), encoding='utf-8')
            job = dict(alias='case-0001', case_id='raw-nonexistent', attempts=[dict(phase='archive')])
            prompt = archive.batch.reference_policy_prompt(archive.batch.retrieval_prompt(
                run, job, 'archive', '归档请求', TOOLS.parent, persist=False))
            (directory / 'archive-1.prompt.txt').write_text(prompt, encoding='utf-8')
            plan = dict(schema='case-archive-v1', task_alias='case-0001')
            for name in ['archive.json', 'archive.response.txt']:
                (directory / name).write_text(json.dumps(plan), encoding='utf-8')
            events = [dict(part=dict(tool='skill', state=dict(status='completed', input=dict(name=name))))
                      for name in ['liuren-cases', 'liuren-extract']]
            (directory / 'archive-1.jsonl').write_text('\n'.join(json.dumps(e) for e in events), encoding='utf-8')
            with patch.object(archive.batch, 'invoke', side_effect=AssertionError('不应重复调用模型')):
                self.assertEqual(archive.invoke_archive(run, job, '归档请求'), plan)


if __name__ == '__main__':
    unittest.main()
