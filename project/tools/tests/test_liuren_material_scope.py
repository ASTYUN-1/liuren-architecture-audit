import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

spec = importlib.util.spec_from_file_location('material_scope', Path(__file__).resolve().parents[1] / 'liuren_material_scope.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='liuren-scope-')
        self.root = Path(self.temp.name)
        self.write('runtime/liuren/current/methods/timing.md', '失物应期条件\n最强反证\n')
        self.write('runtime/liuren/current/source-read-map.json', json.dumps({'aliases':{}}))
        digest = hashlib.sha256((self.root/'runtime/liuren/current/methods/timing.md').read_bytes()).hexdigest()
        files = {'methods/timing.md':digest}
        version = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
        self.write('.opencode/liuren-active.json', json.dumps({'release':'current','methodVersion':version,'runtime':'runtime/liuren/current'}))
        self.write('runtime/liuren/current/manifest.json', json.dumps({'release':'current','version':version,'files':files,'modules':{'timing':{'file':'methods/timing.md'}}}))
        self.scope = module.MaterialScope(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, filename, text):
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_docs_are_exact_file_exceptions_never_a_search_library(self):
        self.write('docs/网站开发.md', '失物部署说明')
        self.write('docs/本机六壬直接排盘.md', '指定操作说明')
        self.assertFalse(self.scope.permitted('docs/网站开发.md'))
        self.assertTrue(self.scope.permitted('docs/本机六壬直接排盘.md'))
        with self.assertRaisesRegex(ValueError, 'library must'):
            self.scope.scan('docs', '失物')
        with self.assertRaisesRegex(ValueError, '超出'):
            self.scope.read('docs/网站开发.md')

    def test_scans_never_enter_development_old_runtime_or_nested_archive(self):
        self.write('书籍库/失物原书.md', '失物原文\n失物反证')
        self.write('书籍库/archive/旧稿.md', '失物旧稿')
        self.write('web/失物.md', '失物产品代码')
        self.write('runtime/liuren/old/methods/timing.md', '失物旧法')
        self.write('runtime/liuren/current/archive/previous-package/失物.md', '失物旧法')
        result = self.scope.scan('books', '失物')
        self.assertEqual({x['path'] for x in result['hits']}, {'书籍库/失物原书.md'})
        result = self.scope.scan('methods', '失物')
        self.assertEqual({x['path'] for x in result['hits']}, {'runtime/liuren/current/methods/timing.md'})
        for path in ['web/失物.md', 'runtime/liuren/old/methods/timing.md', 'runtime/liuren/current/archive/previous-package/失物.md']:
            self.assertFalse(self.scope.permitted(path))

    def test_traversal_outside_scope_is_rejected_before_read(self):
        self.write('docs/开发.md', '不可读')
        for filename in ['书籍库/../docs/开发.md', '../outside.md', 'opencode.json', 'tools/liuren-materials.py']:
            with self.assertRaisesRegex(ValueError, '超出'):
                self.scope.read(filename)

    def test_read_retains_line_numbers_and_explicit_continuation(self):
        self.write('案例项目库/失物占/原案.md', '原问\n条件\n断语\n反馈\n反例')
        result = self.scope.read('案例项目库/失物占/原案.md', 2, 2)
        self.assertEqual(result['text'], '2: 条件\n3: 断语')
        self.assertEqual(result['next_line'], 4)
        self.assertEqual(result['total_lines'], 5)

    def test_hit_limit_is_disclosed_and_never_claims_full_coverage(self):
        self.write('经验日志/失物.md', '失物一\n失物二\n失物三')
        result = self.scope.scan('experience', '失物', 1)
        self.assertEqual(len(result['hits']), 1)
        self.assertTrue(result['limit_reached'])
        self.assertFalse(result['complete'])

    def test_symlink_cannot_expand_library_to_development_or_outside_project(self):
        target = self.write('docs/开发.md', '失物无关开发')
        link = self.root / '书籍库/链接.md'
        link.parent.mkdir(exist_ok=True)
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest('platform cannot create symlink: ' + type(exc).__name__)
        self.assertFalse(self.scope.permitted(link))
        self.assertEqual(self.scope.scan('books', '失物')['hits'], [])


if __name__ == '__main__':
    unittest.main()
