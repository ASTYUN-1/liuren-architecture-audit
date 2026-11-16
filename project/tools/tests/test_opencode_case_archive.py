import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('archive', Path(__file__).parents[1] / 'archive-opencode-case.py')
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class ArchiveBoundaryTests(unittest.TestCase):
    def test_unverified_experience_cannot_enter_verified_index(self):
        targets = {'case': '案例项目库/事业占/case-010-test.md', 'experience': '经验日志/test.md'}
        bodies = {'case': '<!-- META: 反馈=未验 -->\nraw-test\n',
                  'experience': '<!-- META: 反馈=未载 | 经验状态=未验证从疑 -->\nraw-test\n独立验证次数：0\n疑似链条\n待验证\n不能直接作为结论\n'}
        plan = {'files': [{'kind': kind, 'path': targets[kind], 'content': content} for kind, content in bodies.items()]}
        self.assertEqual(set(archive.validate_files(plan, targets, 'raw-test')), {'case', 'experience'})
        plan['files'][1]['content'] = bodies['experience'].replace('反馈=未载', '反馈=验')
        with self.assertRaises(ValueError):
            archive.validate_files(plan, targets, 'raw-test')

    def test_duplicate_source_is_not_appended_again(self):
        text = '| 事业占 | case-009 | old |\n<!-- META: 来源ID=raw-test -->\n'
        with self.assertRaises(ValueError):
            archive.append_case_index(text, '事业占', 'case-010', 'raw-test', '<!-- META: -->')

    def test_windows_double_carriage_return_keeps_new_meta_on_own_line(self):
        text = '| 事业占 | case-009 | old |\r\r\n\r\r\n# next\r\r\n'
        updated = archive.append_case_index(text, '事业占', 'case-010', 'raw-test', '<!-- META: 来源ID=raw-test -->')
        self.assertIn('\n<!-- META: 来源ID=raw-test -->\n', updated)
        self.assertNotIn('\r', updated)

    def test_missing_feedback_cannot_be_written_as_verified_case(self):
        targets = {'case': '案例项目库/考试占/case-001-test.md', 'experience': '经验日志/test.md'}
        plan = {'files': [
            {'kind': 'case', 'path': targets['case'], 'content': '<!-- META: 反馈=验 -->\nraw-test'},
            {'kind': 'experience', 'path': targets['experience'], 'content': '<!-- META: 反馈=未载 | 经验状态=未验证从疑 -->\nraw-test\n独立验证次数：0\n疑似链条\n待验证\n不能定论'}]}
        with self.assertRaises(ValueError):
            archive.validate_files(plan, targets, 'raw-test', case_feedback='未载')


if __name__ == '__main__':
    unittest.main()
