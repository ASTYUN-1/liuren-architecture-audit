"""Retrieval regressions, not tests of divination accuracy."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from liuren_book_search import BookSearch, DATA, ROOT, check


class BookSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.search = BookSearch()

    def test_all_three_sources_have_contiguous_coverage(self):
        result = check()
        self.assertTrue(result['ok'], result['errors'])
        self.assertEqual(set(result['passages']), {'RG', 'LF', 'TY'})
        self.assertFalse(result['semantic_reading_complete'])
        self.assertEqual(result['predictive_validation_count'], 0)

    def test_weak_fire_and_strong_metal_original_is_first(self):
        result = self.search.search('死火 旺金')
        first = result['hits'][0]
        self.assertEqual(first['book'], 'TY')
        self.assertLessEqual(first['start'], 207)
        self.assertGreaterEqual(first['end'], 207)
        self.assertIn('死火克不动旺金', first['text'])
        self.assertTrue(first['section_complete'])
        # Do not fill the other slots with passages matching only one term.
        self.assertTrue(all(len(h['matched_queries']['0']['literal_terms']) == 2 for h in result['hits']))

    def test_twelve_states_retains_differing_reference_frames(self):
        result = self.search.search('十二长生', limit=1)
        self.assertEqual(result['hits'][0]['book'], 'TY')
        self.assertIn('日干', result['hits'][0]['text'])
        self.assertIn('E02', [p['id'] for p in result['related_sources']])
        self.assertIn('E11', [p['id'] for p in result['related_sources']])
        self.assertTrue(all(p.get('text') for p in result['related_sources']))

    def test_ghost_query_keeps_travel_conditions_and_lay_official_exception(self):
        result = self.search.search('旺鬼', limit=1)
        texts = [h['text'] for h in result['hits']] + [h.get('text') or '' for h in result['related_sources']]
        self.assertIn('鬼禁日', '\n'.join(texts))
        self.assertIn('仕宦', '\n'.join(texts))

    def test_pdf_hardwraps_match_without_altering_quoted_text(self):
        result = self.search.search('察天 察地 看人')
        self.assertEqual(len(result['hits']), 1)
        self.assertEqual(result['hits'][0]['book'], 'LF')
        self.assertLessEqual(result['hits'][0]['start'], 2129)

    def test_batch_search_has_each_query_and_one_total_budget(self):
        result = self.search.search(queries=['死火 旺金', '神将互换', '鬼禁日'], limit=3)
        self.assertTrue(all(q['returned_hits'] for q in result['literal_query_coverage']))
        self.assertLessEqual(result['text_chars'], 14000)
        self.assertEqual(result['coverage']['books'], ['RG', 'LF', 'TY'])

    def test_book_filter_does_not_load_companion_from_unselected_book(self):
        result = self.search.search('十二长生', book='TY')
        self.assertEqual(result['coverage']['books'], ['TY'])
        self.assertEqual(result['related_sources'], [])
        self.assertTrue(all(h['book']=='TY' for h in result['hits']))

    def test_returned_text_is_exact_current_original_range(self):
        for query in ['旺鬼', '财旺 身弱', '十二长生', '神将互换']:
            result = self.search.search(query)
            for h in result['hits']:
                raw = (ROOT / h['path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), h['fileSha256'])
                lines = raw.decode(h['sourceEncoding']).splitlines()
                self.assertIsNone(h['continuation'])
                self.assertEqual(h['text'], '\n'.join(lines[h['start']-1:h['end']]))

    def test_unknown_query_reports_no_hit_and_limited_coverage(self):
        result = self.search.search('不存在的检索词XYZ987654')
        self.assertEqual(result['hits'], [])
        self.assertFalse(result['coverage']['other_books_searched'])
        self.assertFalse(result['coverage']['cases_searched'])
        self.assertFalse(result['coverage']['experience_searched'])

    def test_small_budget_marks_incomplete_range_with_continuation(self):
        result = self.search.search('十五.课体', book='TY', max_chars=2000, limit=1)
        self.assertLessEqual(result['text_chars'], 2000)
        first = result['hits'][0]
        self.assertFalse(first['passage_complete'])
        self.assertIsNotNone(first['continuation'])
        self.assertFalse(first['section_complete'])

    def test_invalid_queries_and_paths_are_not_accepted(self):
        for query in ['', '*', 'a', 'x'*201, None]:
            with self.assertRaises(ValueError):
                self.search.search(query)
        for book in ['../docs', 'cases', 'experience', 'runtime/old']:
            with self.assertRaises(ValueError):
                self.search.search('空亡', book=book)
        with self.assertRaises(ValueError):
            self.search.search('空亡', queries=['旺鬼'])

    def test_scope_callback_can_deny_an_otherwise_registered_source(self):
        with self.assertRaisesRegex(ValueError, 'outside current material scope'):
            BookSearch(permitted=lambda path: False).search('旺鬼')

    def test_read_only_search_does_not_rewrite_index(self):
        path = ROOT / DATA / 'index.sqlite3'
        before = (path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest())
        self.search.search('旺鬼')
        self.assertEqual(before, (path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()))

    def fixture(self, root):
        for rel in [DATA/'catalog.json', DATA/'index.sqlite3', *[Path(b['path']) for b in self.search.books.values()]]:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

    def test_changed_original_fails_instead_of_returning_cached_text(self):
        with tempfile.TemporaryDirectory(prefix='book-source-test-') as tmp:
            root = Path(tmp)
            self.fixture(root)
            path = root / self.search.books['TY']['path']
            path.write_bytes(path.read_bytes()+b'\nchanged')
            with self.assertRaisesRegex(ValueError, 'BOOK_SOURCE_CHANGED'):
                BookSearch(root).search('死火 旺金')

    def test_catalog_changes_require_explicit_rebuild(self):
        with tempfile.TemporaryDirectory(prefix='book-catalog-test-') as tmp:
            root = Path(tmp)
            self.fixture(root)
            path = root / DATA / 'catalog.json'
            path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError, 'BOOK_INDEX_STALE'):
                BookSearch(root).search('死火 旺金')

    def test_outlines_have_original_coordinates_and_do_not_invent_missing_volume(self):
        result = self.search.outline('LF')
        sections = result['books'][0]['sections']
        self.assertIn('卷之八', '\n'.join(s['title'] for s in sections))
        self.assertNotIn('卷之七', '\n'.join(s['title'] for s in sections))
        self.assertEqual(sections[-1]['end'], 6931)


if __name__ == '__main__':
    unittest.main()
