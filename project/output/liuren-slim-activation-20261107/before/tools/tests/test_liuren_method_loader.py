"""Integrity tests for paged reading, dependency ordering, and stale content rejection."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'load-liuren-methods.py'
spec = importlib.util.spec_from_file_location('liuren_method_loader', SCRIPT)
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class MethodLoaderTests(unittest.TestCase):
    def test_local_operation_override_is_pinned_and_cannot_replace_other_methods(self):
        with tempfile.TemporaryDirectory(prefix='liuren-local-override-') as directory:
            root = Path(directory)
            runtime = root / 'runtime/test'
            runtime.mkdir(parents=True)
            (root / '.opencode').mkdir()
            (root / 'docs').mkdir()
            old = b'original immutable operation'
            (runtime / 'paipan.md').write_bytes(old)
            files = {'paipan.md': loader.sha(old)}
            manifest = dict(release='test', files=files,
                modules={'daliuren-paipan': dict(file='paipan.md')},
                version=loader.sha(json.dumps(files, sort_keys=True).encode()))
            (runtime / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            new = '本机一次排盘，保留原引擎。\n'.encode('utf-8')
            doc = root / 'docs/direct.md'
            doc.write_bytes(new)
            override = dict(file='docs/direct.md', sha256=loader.sha(new), version='direct-test')
            pointer = dict(runtime='runtime/test', release='test', methodVersion=manifest['version'],
                           localModuleOverrides={'daliuren-paipan': override})
            ptr = root / '.opencode/liuren-active.json'
            ptr.write_text(json.dumps(pointer), encoding='utf-8')
            base, checked = loader.active(root)
            self.assertEqual(loader.content(base, checked, 'daliuren-paipan')[1], new.decode())
            self.assertEqual((runtime / 'paipan.md').read_bytes(), old)
            doc.write_bytes(new + b'tampered')
            with self.assertRaisesRegex(ValueError, 'override hash'):
                loader.content(base, checked, 'daliuren-paipan')
            with self.assertRaisesRegex(ValueError, 'override hash/path'):
                loader.active(root)
            doc.write_bytes(new)
            pointer['localModuleOverrides'] = {'liqi': override}
            ptr.write_text(json.dumps(pointer), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'unsupported local module override'):
                loader.active(root)
            pointer['localModuleOverrides'] = {'daliuren-paipan': dict(override, file='../outside.md')}
            ptr.write_text(json.dumps(pointer), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'override hash/path'):
                loader.active(root)

    def test_cli_receipts_match_raw_windows_stdout_without_normalization(self):
        root = SCRIPT.parents[1]
        commands = [
            (SCRIPT, ['read', 'positioning', '--page', '1'], False),
            (SCRIPT, ['read', 'liqi', '--page', '1'], False),
            (SCRIPT, ['read', 'liqi', '--page', '2'], False),
            (root / 'tools/load-liuren-procedure.py',
             ['read', 'liuren-cases', '--part', 'P000', '--page', '1'], True),
        ]
        for script, args, procedure in commands:
            with self.subTest(script=script.name, args=args):
                # Do not use text=True or encoding=: either masks Windows CRLF translation.
                proc = subprocess.run([sys.executable, str(script), *args], cwd=root,
                                      capture_output=True, timeout=15)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                meta, text = loader.parse_page_output(proc.stdout, procedure)
                self.assertEqual(loader.sha(text.encode('utf-8')), meta['pageSha256'])
                self.assertNotIn(b'\r', proc.stdout)
                with self.assertRaises(ValueError):
                    loader.parse_page_output(proc.stdout.replace(b'\n', b'\r\n'), procedure)

    def test_year_life_and_conditional_routes_obey_workflow_stages(self):
        root = SCRIPT.parents[1]
        # Test a coherent frozen release, not an old manifest plus mutable authoring routes.
        _, manifest = loader.active(root)
        route = manifest['readingRoute']
        manifest['readingRoute'] = route
        manifest['required'] = [key for phase in route['stages'] for key in phase['required']]
        steps = loader.plan_steps(manifest, ['illness'], timing=True, nianming=True)
        keys = [item['id'] for item in steps]
        self.assertEqual(keys[0], 'nianming')
        self.assertEqual(steps[0]['stage'], 1)
        self.assertIn('engine-shensha-output', keys)
        self.assertLess(keys.index('engine-shensha-output'), keys.index('shensha-focus'))
        self.assertLess(keys.index('illness'), keys.index('relations'))
        self.assertEqual(steps[keys.index('timing')]['stage'], route['conditional']['timing']['stage'])
        self.assertEqual(keys[-1], 'report')
        self.assertEqual(keys, loader.plan(manifest, ['illness'], True, ['nianming']))
        base = loader.plan(manifest, ['illness'])
        self.assertNotIn('nianming', base)
        self.assertNotIn('timing', base)
        for key, condition in route['conditional'].items():
            steps = loader.plan_steps(manifest, ['illness'], extras=[key, key])
            selected = [item for item in steps if item['id'] == key]
            self.assertEqual(selected, [dict(id=key, stage=condition['stage'])])
        self.assertEqual(loader.plan(manifest, extras=['bifa'])[-1], 'report')
        with self.assertRaises(ValueError):
            loader.plan(manifest, extras=['missing-module'])

    def test_pages_preserve_all_chinese_and_long_lines(self):
        original = ('定位：患者、代问者不能混淆。\n' + '甲🙂乙' * 4000 + '\n````\n尾页\n')
        pages = loader.page_text(original)
        self.assertGreater(len(pages), 2)
        self.assertEqual(''.join(pages), original)
        self.assertTrue(all(len(p.encode('utf-8')) <= loader.PAGE_BYTES for p in pages))

    def test_route_has_domains_before_judgment_and_time_before_report(self):
        manifest = dict(required=['positioning', 'evidence', 'relations', 'adjudication', 'report'],
            modules={k: dict(requires=[]) for k in ['positioning', 'evidence', 'relations', 'adjudication', 'report', 'illness', 'timing']})
        route = loader.plan(manifest, ['illness'], True)
        self.assertLess(route.index('illness'), route.index('relations'))
        self.assertLess(route.index('timing'), route.index('report'))
        self.assertEqual(len(route), len(set(route)))
        manifest['modules']['relations']['requires'] = ['evidence']
        self.assertEqual(loader.plan(manifest, ['illness'], True), route)
        manifest['modules']['evidence']['requires'] = ['relations']
        with self.assertRaises(ValueError):
            loader.plan(manifest)

    def test_changed_file_and_active_pointer_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='liuren-loader-') as directory:
            root = Path(directory)
            runtime = root / 'runtime/test'
            runtime.mkdir(parents=True)
            (root / '.opencode').mkdir()
            raw = '日干代表本事件患者。\r\n代问身份另列。\r\n'.encode('utf-8')
            (runtime / 'positioning.md').write_bytes(raw)
            files = {'positioning.md': loader.sha(raw)}
            route = dict(stages=[dict(id=2, required=['positioning'])], conditional={}, domains=[])
            route_raw = json.dumps(route).encode('utf-8')
            (runtime / 'reading-route.json').write_bytes(route_raw)
            files['reading-route.json'] = loader.sha(route_raw)
            manifest = dict(release='test', files=files, modules={'positioning': dict(file='positioning.md')},
                required=['positioning'], conditional={}, domains=[], routingFile='reading-route.json',
                version=loader.sha(json.dumps(files, sort_keys=True).encode()))
            (runtime / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            pointer = dict(runtime='runtime/test', release='test', methodVersion=manifest['version'])
            (root / '.opencode/liuren-active.json').write_text(json.dumps(pointer), encoding='utf-8')
            base, checked = loader.active(root)
            self.assertEqual(loader.content(base, checked, 'positioning')[1], raw.decode().replace('\r\n', '\n'))
            manifest['conditional']['nianming'] = 'undeclared condition'
            (runtime / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'manifest and reading route disagree'):
                loader.active(root)
            manifest['conditional'] = {}
            (runtime / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            (runtime / 'reading-route.json').write_bytes(route_raw + b' ')
            with self.assertRaisesRegex(ValueError, 'reading route hash mismatch'):
                loader.active(root)
            (runtime / 'reading-route.json').write_bytes(route_raw)
            (runtime / 'positioning.md').write_text('tampered', encoding='utf-8')
            with self.assertRaises(ValueError):
                loader.content(base, checked, 'positioning')
            pointer['methodVersion'] = 'stale'
            (root / '.opencode/liuren-active.json').write_text(json.dumps(pointer), encoding='utf-8')
            with self.assertRaises(ValueError):
                loader.active(root)


if __name__ == '__main__':
    unittest.main()
