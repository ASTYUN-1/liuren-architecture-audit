"""Exercise real tool transport and exact method delivery, not prediction quality."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('single_method_loader', ROOT/'tools/load-liuren-methods.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


def request(data):
    return subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'tools/liuren-materials.py'),
                           '--request', json.dumps(data)], cwd=ROOT, capture_output=True, timeout=20)


class SingleMethodTests(unittest.TestCase):
    def test_one_complete_module_without_other_methods_plan_or_pages(self):
        runtime, manifest = loader.active()
        for key in ['class-mapping', 'relationship', 'liqi', 'void', 'movement', 'shensha-focus']:
            with self.subTest(module=key):
                run = request(dict(action='method', module=key))
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertNotIn(b'\r', run.stdout)
                first, rest = run.stdout.decode('utf-8').split('\n', 1)
                self.assertTrue(first.startswith('LIUREN_METHOD_BEGIN '))
                meta = json.loads(first.split(' ', 1)[1])
                body, end = rest.rsplit('\nLIUREN_METHOD_END ', 1)
                end = json.loads(end.strip())
                _, expected, digest = loader.content(runtime, manifest, key)
                self.assertEqual(body, expected)
                self.assertEqual(meta['fileSha256'], digest)
                self.assertEqual(meta['textSha256'], loader.sha(body.encode('utf-8')))
                self.assertEqual(end, dict(module=key, textSha256=meta['textSha256']))
                self.assertTrue(meta['completeModule'])
                self.assertEqual(meta['handoff'], dict(id='M_'+key, title=manifest['modules'][key].get('title', key), source_path=Path(meta['file']).relative_to(ROOT).as_posix(), sha256=digest))
                self.assertEqual(meta['requires'], manifest['modules'][key].get('requires', []))
                self.assertEqual(meta['release'], manifest['release'])
                self.assertNotIn('LIUREN_READING_PLAN', run.stdout.decode('utf-8'))

    def test_missing_unknown_and_path_selectors_do_not_return_unrelated_data(self):
        for value in [None, '', '../../opencode.json', 'not-a-module', ['liqi']]:
            with self.subTest(value=value):
                run = request(dict(action='method', module=value))
                self.assertEqual(run.returncode, 2)
                self.assertFalse(run.stdout)
                self.assertIn(b'LIUREN_MATERIAL_ERROR', run.stderr)

    def test_old_token_only_followup_cannot_silently_switch_to_default_plan(self):
        run = request(dict(action='methods', domains=['relationship'], timing=True, batch=1,
                           _context_key='regression-session'))
        self.assertEqual(run.returncode, 0, run.stderr)
        plan = json.loads(run.stdout.decode('utf-8').split('\n', 1)[0].split(' ', 1)[1])
        bad = request(dict(action='methods', plan_id=plan['plan_id'], batch=2,
                           _context_key='regression-session'))
        self.assertEqual(bad.returncode, 2)
        self.assertFalse(bad.stdout)
        self.assertIn('不恢复路由', bad.stderr.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
