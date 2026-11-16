import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import liuren_retrieval_policy as retrieval_policy
spec = importlib.util.spec_from_file_location('local_read', TOOLS / 'liuren-local-read.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class LocalReadTests(unittest.TestCase):
    def test_batches_reconstruct_every_selected_module_without_abridgement(self):
        runtime, manifest = reader.loader.active()
        batches = reader.method_batches(runtime, manifest, ['lost-person-object'], timing=True)
        self.assertTrue(all(1 <= len(group) <= 3 for group in batches))
        rows = [row for group in batches for row in group]
        expected = reader.loader.plan(manifest, ['lost-person-object'], timing=True)
        self.assertEqual(list(dict.fromkeys(row['module'] for row in rows)), expected)
        self.assertNotIn('shensha-use', expected)
        explicit = reader.method_batches(runtime, manifest, ['lost-person-object'], conditions=['shensha-use'])
        self.assertIn('shensha-use', {row['module'] for group in explicit for row in group})
        self.assertFalse(set(manifest.get('moduleAliases', {})).intersection(expected))
        for key in expected:
            _, text, digest = reader.loader.content(runtime, manifest, key)
            pieces = [row for row in rows if row['module'] == key]
            self.assertEqual(''.join(row['text'] for row in pieces), text)
            self.assertEqual([row['page'] for row in pieces], list(range(1, len(pieces) + 1)))
            for row in pieces:
                self.assertEqual(row['fileSha256'], digest)
                self.assertEqual(row['pageSha256'], reader.loader.sha(row['text'].encode()))
                self.assertNotIn('archive/previous-package', row['file'])

    def test_condition_routes_remain_intact_and_invalid_conditions_are_rejected(self):
        runtime, manifest = reader.loader.active()
        batches = reader.method_batches(runtime, manifest, ['lost-person-object'], conditions=['risk'], nianming=True)
        keys = {r['module'] for group in batches for r in group}
        self.assertTrue({'risk', 'nianming'}.issubset(keys))
        with self.assertRaisesRegex(ValueError, 'unknown condition'):
            reader.method_batches(runtime, manifest, conditions=['nonexistent'])

    def test_parallel_search_keeps_both_original_results_and_unmodified_renderers(self):
        import case_retrieval as cases
        import experience_retrieval as experience
        policy = {'research_overlay': {'overlayFingerprint': 'synthetic-policy'}}
        case_result = {'index_status': policy, 'results': [{'id': 'case1', 'conditions': ['original condition']} ]}
        exp_result = {'index_status': policy, 'results': [{'id': 'exp1', 'review': 'original limitation'}]}
        with patch.object(retrieval_policy, 'require_case_experience', return_value=None), \
             patch.object(cases, 'ensure_index', return_value='case-index'), \
             patch.object(experience, 'ensure_index', return_value='experience-index'), \
             patch.object(cases, 'retrieve', return_value=case_result) as case_call, \
             patch.object(experience, 'retrieve', return_value=exp_result) as exp_call, \
             patch.object(cases, 'render', return_value='case1 original condition\n') as cr, \
             patch.object(experience, 'render', return_value='exp1 original limitation\n') as er:
            result, text = reader.parallel_search('藏匿', '方位', '失物占', limit=8)
        case_call.assert_called_once_with('case-index', '藏匿', {'占类': '失物占'}, 8)
        exp_call.assert_called_once_with('experience-index', '方位', ['失物占'], limit=8)
        self.assertIs(result['cases'], case_result)
        self.assertIs(result['experience'], exp_result)
        cr.assert_called_once_with(case_result)
        er.assert_called_once_with(exp_result)
        self.assertIn('original condition', text)
        self.assertIn('original limitation', text)
        self.assertIn('不代表读过原文', text)

    def test_failure_in_either_search_is_not_silently_treated_as_no_candidates(self):
        import case_retrieval as cases
        import experience_retrieval as experience
        with patch.object(retrieval_policy, 'require_case_experience', return_value=None), \
             patch.object(cases, 'ensure_index', side_effect=ValueError('bad source')), \
             patch.object(experience, 'ensure_index', return_value={}), \
             patch.object(experience, 'retrieve', return_value={}):
            with self.assertRaisesRegex(ValueError, 'bad source'):
                reader.parallel_search('失物', '失物', '失物占')

    def test_current_entry_blocks_both_libraries_before_retrieval(self):
        import case_retrieval as cases
        import experience_retrieval as experience
        with patch.object(cases, 'retrieve') as cr, patch.object(experience, 'retrieve') as er:
            with self.assertRaisesRegex(ValueError, 'LIUREN_EXPERIMENT_NO_RETRIEVAL'):
                reader.parallel_search('synthetic', 'synthetic', '失物占')
        cr.assert_not_called()
        er.assert_not_called()


if __name__ == '__main__':
    unittest.main()
