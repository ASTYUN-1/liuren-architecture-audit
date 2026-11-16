"""Behavioral tests: question routing, source identity and blind-stage isolation."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import case_retrieval as cases


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '案例项目库').mkdir()

    def add(self, name, text):
        p = self.root / '案例项目库' / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def test_subquestions_retrieve_different_methods_but_one_event(self):
        self.add('事业占/case-001-工作.md', '''<!-- META: 占类=事业占 | 来源ID=raw-test-0001 -->
# 工作
## 问题
背景：准备换公司。Q1是否离职；Q2新工作满意吗；Q3工资多少？
## 初判
不应进入问题的SECRET_RESULT。
''')
        index = cases.ensure_index(self.root)
        self.assertEqual(len(index['units']), 3)
        result = cases.retrieve(index, '新工作是否满意')
        self.assertIn('Q2', result['results'][0]['unit']['question'])
        self.assertEqual(result['total_source_groups'], 1)
        self.assertNotIn('SECRET_RESULT', str([u['question'] for u in index['units']]))

    def test_numbered_options_are_not_invented_subquestions(self):
        self.add('财运占/case-001.md', '# 回款\n## 问题\n问多少？1.90%以上；2.70%以上；3.50%以下。\n## 反馈\n要回五万。')
        index = cases.ensure_index(self.root)
        self.assertEqual(len(index['units']), 1)
        self.assertIn('50%', index['units'][0]['question'])

    def test_inline_numbered_questions_split_without_splitting_decimals(self):
        self.add('财运占/case-001.md', '# 索赔\n## 问题\n1.能否索赔？2.何时拿到？3.多少（误差2.5万）？\n')
        index = cases.ensure_index(self.root)
        self.assertEqual(len(index['units']), 3)
        self.assertIn('2.5万', index['units'][2]['question'])

    def test_title_only_stays_explicitly_a_fallback(self):
        self.add('事业占/case-001.md', '# 明年录用\n## 分析\n结果是失败。')
        unit = cases.ensure_index(self.root)['units'][0]
        self.assertIn('标题检索入口', unit['extraction_status'])
        self.assertNotIn('失败', unit['question'])

    def test_number_spellings_and_specific_exam_names_match(self):
        self.add('考试占/case-001.md', '# 外语\n## 问题\n英语6级能不能通过？')
        self.add('考试占/case-002.md', '# 考试\n## 问题\n电工考试能否通过？')
        row = cases.retrieve(cases.ensure_index(self.root), '英语六级能过吗')['results'][0]
        self.assertTrue(row['case']['source'].endswith('case-001.md'))
        self.assertIn('考试', row['matched_goals'])

    def test_answer_headings_yield_only_questions_not_answers(self):
        self.add('事业占/case-001.md', '# 工作\n## 模范答案\n### 问题1：能录用吗？\nSECRET_ANSWER\n### 问题2：何时入职？\nSECRET_DATE\n')
        units = cases.ensure_index(self.root)['units']
        self.assertEqual(len(units), 2)
        self.assertNotIn('SECRET', str([u['question_location'] for u in units]))

    def test_native_suffix_is_not_dropped_and_known_rewrites_are_excluded(self):
        for n, sid in [(1, '0002a'), (2, '0002b'), (3, '0002a')]:
            self.add(f'官讼占/case-{n:03}.md', f'<!-- META: 来源ID=raw-source-{sid} -->\n# 索赔\n## 问题\n能否索赔？\n不同文稿{n}')
        index = cases.ensure_index(self.root)
        result = cases.retrieve(index, '索赔', exclude=['raw-source-0002a'])
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['case']['source_ids'], ['raw-source-0002b'])

    def test_same_chart_is_not_same_event(self):
        for n in range(2):
            self.add(f'事业占/case-{n:03}.md', f'<!-- META: 占类=事业占 | 课体=反吟 | 三传=卯酉卯 -->\n# 求职\n## 问题\n能否录用？\n原档{n}')
        result = cases.retrieve(cases.ensure_index(self.root), '录用')
        self.assertEqual(result['total_source_groups'], 2)

    def test_updates_relocate_quotes_and_deletions_remove_stale_sources(self):
        path = self.add('事业占/case-001.md', '# 求职\n## 问题\n能否录用？\n')
        first = cases.ensure_index(self.root)
        path.write_text('\n\n' + path.read_text('utf-8').replace('录用', '加薪'), encoding='utf-8')
        second = cases.ensure_index(self.root)
        unit = second['units'][0]
        self.assertIn('加薪', unit['question'])
        self.assertNotEqual(first['fingerprint'], second['fingerprint'])
        self.assertEqual(unit['question_location']['line_start'], 5)
        path.unlink()
        self.assertEqual(cases.ensure_index(self.root)['units'], [])

    def test_aliases_do_not_merge_equal_numbers_in_distinct_directories(self):
        self.add('疾病占/case-001.md', '<!-- META: 占类=疾病占 | 课体=铸印 -->\n# 病情')
        self.add('灾厄占/case-001.md', '<!-- META: 占类=灾厄占 | 课体=反吟 -->\n# 灾厄')
        (self.root / '案例项目库/_metadata_index.md').write_text('<!-- META: 占类=疾病占 | 编号=case-001 | 发用=卯(六合) -->\n<!-- META: 占类=灾厄占 | 编号=case-001 | 发用=午(天空) -->', encoding='utf-8')
        index = cases.ensure_index(self.root)
        self.assertFalse(index['legacy_audit']['ambiguous_rows'])
        self.assertEqual({Path(r['source']).parts[1]: r['fields']['发用'] for r in index['cases']},
                         {'疾病占': '卯(六合)', '灾厄占': '午(天空)'})

    def test_legacy_conflict_preserves_source_and_never_raises_confidence(self):
        path = self.add('事业占/case-001.md', '<!-- META: 占类=事业占 | 三传=卯酉卯 | 反馈=未载 | 经验状态=未验证从疑 -->\n# 工作')
        before = path.read_bytes()
        (self.root / '案例项目库/_metadata_index.md').write_text('<!-- META: 占类=事业占 | 编号=case-001 | 三传=子午子 | 反馈=验 -->', encoding='utf-8')
        row = cases.retrieve(cases.ensure_index(self.root), '工作')['results'][0]
        self.assertEqual(row['case']['fields']['三传'], '卯酉卯')
        self.assertIn('反馈', row['case']['legacy_conflicts'])
        self.assertEqual(row['case']['evidence']['independent_validation_increment'], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_class_god_is_not_inferred_from_technique_and_feedback_not_a_multiplier(self):
        index = cases.build_index(self.root, files={
            '案例项目库/事业占/case-001.md': '<!-- META: 占类=事业占 | 技法=朱雀 | 反馈=验 -->\n# 求职'.encode(),
            '案例项目库/事业占/case-002.md': '<!-- META: 占类=事业占 | 技法=朱雀 | 反馈=未载 -->\n# 求职'.encode()}, rows=[])
        rows = cases.retrieve(index, '求职', {'占类': '事业占', '类神': '朱雀'})['results']
        self.assertEqual(rows[0]['relevance_score'], rows[1]['relevance_score'])
        self.assertEqual(rows[0]['six_dimensions']['类神'], 0)

    def test_book_examples_do_not_borrow_another_examples_chart(self):
        self.add('一字诀玉连环注解/章.md', '<!-- META: 占类=古籍注解 -->\n# 章节\n## 假令案例\n### 假令一：甲子日\n- 三传：卯（六合）→ 酉（朱雀）→ 卯（六合）\n### 假令二：乙丑日\n- 三传：子（青龙）→ 午（白虎）→ 子（青龙）\n')
        units = cases.ensure_index(self.root)['units']
        self.assertEqual(len(units), 2)
        self.assertNotEqual(units[0]['fields']['三传'], units[1]['fields']['三传'])
        self.assertTrue(all(u['unit_kind'] == '书籍假令' for u in units))

    def test_packet_is_read_only_and_carries_common_origin_key(self):
        self.add('事业占/case-001.md', '<!-- META: 来源ID=raw-source-0001 -->\n# 求职\n## 问题\n能否录用？')
        public = {'question': '能否录用？', 'facts': {'chart_types': ['反吟']}}
        original = copy.deepcopy(public)
        packet = cases.evidence_packet(public, 'raw-other-0001', self.root)
        self.assertEqual(public, original)
        self.assertIn('案例项目库/事业占/case-001.md', packet['results'][0]['origin_keys'])
        self.assertEqual(cases.evidence_packet(public, 'raw-source-0001', self.root)['results'], [])

    def test_packet_budget_does_not_mutate_reusable_index(self):
        self.add('事业占/case-001.md', '# 工作\n## 问题\n' + '什么时候能换工作？' * 100)
        index = cases.ensure_index(self.root)
        before = copy.deepcopy(index)
        cases.compact(cases.retrieve(index, '换工作'))
        self.assertEqual(index, before)

    def test_pregnancy_and_relationship_have_distinct_category_scores(self):
        self.add('胎产占/case-001.md', '<!-- META: 占类=胎产占 -->\n# 怀孕\n## 问题\n是否怀孕？')
        self.add('感情占/case-002.md', '<!-- META: 占类=感情占 -->\n# 复合\n## 问题\n是否复合？')
        result = cases.retrieve(cases.ensure_index(self.root), fields={'占类': '感情占'})
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['case']['category'], '感情占')

    def test_unbudgeted_local_packet_does_not_drop_selected_case(self):
        self.add('感情占/case-001.md', '# 复合\n## 问题\n是否复合？\n')
        result = cases.retrieve(cases.ensure_index(self.root), '复合')
        result['results'][0]['case']['legacy_conflicts'] = {'完整原值': '重要条件' * 6000}
        packet = cases.compact(result, budget=None)
        self.assertEqual(len(packet['results']), 1)
        self.assertEqual(packet['results'][0]['case']['legacy_conflicts']['完整原值'], '重要条件' * 6000)


class BatchBoundaryTests(unittest.TestCase):
    def test_windows_compatibility_entry_accepts_omitted_question(self):
        import os
        if os.name != 'nt':
            self.skipTest('Windows PowerShell compatibility')
        result = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                 str(TOOLS / 'search-cases.ps1'), '-Scope', 'case', '-ZhanLei', '事业占', '-Top', '1'],
                                cwd=TOOLS.parent, capture_output=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('案例问题级检索', result.stdout)

    def test_later_phase_never_writes_into_first_stage_directory(self):
        batch = load('case_packet_batch', 'opencode-case-batch.py')
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'public-inputs').mkdir()
            case_dir = run / 'cases/case-0001'
            case_dir.mkdir(parents=True)
            (run / 'public-inputs/case-0001.json').write_text(json.dumps(dict(question='工作', facts={})), encoding='utf-8')
            (case_dir / 'review.json').write_text(json.dumps(dict(experience_candidates=[dict(condition='SECRET_AFTER_FEEDBACK')])), encoding='utf-8')
            job = dict(alias='case-0001', case_id='raw-current-0001', attempts=[])
            with patch.object(batch.case_retrieval, 'evidence_packet', return_value={'results': [], 'schema': cases.VERSION}), \
                 patch.object(batch.case_retrieval, 'ensure_index', return_value={'cases': []}), \
                 patch.object(batch, 'evidence_packet', side_effect=lambda *a, **kw: {'query': kw.get('extra_query', '')}):
                batch.retrieval_prompt(run, job, 'first', '初判', run)
                before = {p.name: p.read_bytes() for p in (run / 'public-inputs').iterdir()}
                result = batch.retrieval_prompt(run, job, 'archive', '归档', run)
                after = {p.name: p.read_bytes() for p in (run / 'public-inputs').iterdir()}
            self.assertEqual(before, after)
            self.assertNotIn('SECRET_AFTER_FEEDBACK', str(before))
            self.assertIn('SECRET_AFTER_FEEDBACK', result)
            self.assertTrue((case_dir / 'archive-1.case-retrieval.json').exists())

    def test_archive_cache_rollback_removes_new_cache_and_restores_old_bytes(self):
        archive = load('case_packet_archive', 'archive-opencode-case.py')
        with tempfile.TemporaryDirectory() as temp, patch.object(archive, 'PROJECT', Path(temp)):
            old = Path(temp) / archive.batch.experience_retrieval.CACHE
            old.parent.mkdir(parents=True)
            old.write_bytes(b'ORIGINAL')
            snapshot = archive.retrieval_cache_snapshot()
            new = Path(temp) / cases.CACHE
            new.parent.mkdir(parents=True)
            new.write_bytes(b'NEW')
            old.write_bytes(b'CHANGED')
            archive.restore_retrieval_caches(snapshot)
            self.assertEqual(old.read_bytes(), b'ORIGINAL')
            self.assertFalse(new.exists())


if __name__ == '__main__':
    unittest.main()
