"""Candidate integration checks; these measure loading and provenance, not divination."""
import importlib.util
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/stage-liuren-quantity-20261027.py'
spec = importlib.util.spec_from_file_location('quantity_candidate_test', SCRIPT)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
loader = candidate.pages


class QuantityCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Frozen candidate checks must not invoke historical live activation or write old evidence.
        cls.manifest = candidate.manifest_checked()

    def test_actual_cli_roundtrip_for_full_exam_timing_quantity_route(self):
        temporary = tempfile.TemporaryDirectory(prefix='liuren-frozen-quantity-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(candidate.PACKAGE, root/'runtime/candidate')
        (root/'.opencode').mkdir()
        candidate.dump(root/'.opencode/liuren-active.json', dict(release=candidate.RELEASE,
            runtime='runtime/candidate', methodVersion=self.manifest['version']))
        script = ROOT/'tools/load-liuren-methods.py'
        command = [sys.executable, '-X', 'utf8', str(script), '--root', str(root)]
        proc = subprocess.run([*command, 'plan',
                               '--domain', 'exam', '--timing', '--nianming',
                               '--condition', 'quantity', '--condition', 'quantity-sources'],
                              cwd=ROOT, capture_output=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        plan = json.loads(proc.stdout)
        self.assertEqual(plan['release'], candidate.RELEASE)
        keys = [row['id'] for row in plan['modules']]
        self.assertEqual(keys[0], 'nianming')
        self.assertEqual(keys[-1], 'report')
        receipts = []
        for row in plan['modules']:
            expected = loader.content(candidate.PACKAGE, self.manifest, row['id'])[1]
            recovered = []
            for number in range(1, row['pages'] + 1):
                result = subprocess.run([*command, 'read',
                                         row['id'], '--page', str(number)],
                                        cwd=ROOT, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                meta, body = loader.parse_page_output(result.stdout)
                self.assertEqual(meta['release'], candidate.RELEASE)
                self.assertEqual(meta['module'], row['id'])
                self.assertEqual(meta['fileSha256'], row['sha256'])
                self.assertEqual(meta['page'], number)
                recovered.append(body)
                receipts.append(meta)
            self.assertEqual(''.join(recovered), expected)
        self.assertGreater(len(receipts),0)

    def test_frozen_and_live_quantity_routes_keep_explicit_selection(self):
        for domain in self.manifest['domains']:
            generic = loader.plan(self.manifest, [domain])
            self.assertNotIn('quantity', generic)
            self.assertNotIn('quantity-sources', generic)
            numeric = loader.plan(self.manifest, [domain], extras=['quantity'])
            self.assertIn('quantity', numeric)
            self.assertNotIn('quantity-sources', numeric)
            self.assertEqual([key for key in numeric if key != 'quantity'], generic)
        _, active = loader.active()
        selected = loader.plan(active, extras=['quantity-sources'])
        self.assertLess(selected.index('quantity'), selected.index('quantity-sources'))
        self.assertLess(selected.index('quantity-sources'), selected.index('report'))

    def test_candidate_pointer_and_content_reject_tampering(self):
        with tempfile.TemporaryDirectory(prefix='liuren-quantity-') as folder:
            root = Path(folder)
            runtime = root / 'runtime/candidate'
            runtime.mkdir(parents=True)
            (root / '.opencode').mkdir()
            for rel in ['manifest.json', 'reading-route.json', 'methods/quantity.md']:
                dest = runtime / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((candidate.PACKAGE / rel).read_bytes())
            candidate.dump(root / '.opencode/liuren-active.json', dict(
                release=candidate.RELEASE, runtime='runtime/candidate',
                methodVersion=self.manifest['version']))
            package, manifest = loader.active(root)
            loader.content(package, manifest, 'quantity')
            (runtime / 'methods/quantity.md').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'module hash mismatch'):
                loader.content(package, manifest, 'quantity')
            with (runtime / 'reading-route.json').open('ab') as handle:
                handle.write(b' ')
            with self.assertRaisesRegex(ValueError, 'reading route hash mismatch'):
                loader.active(root)

    def test_all_fifty_excerpts_still_match_actual_books(self):
        rows = json.loads((ROOT / candidate.EVIDENCE[-1]).read_text('utf-8'))
        for item in rows:
            path = ROOT / item['source']
            if path.is_file():
                raw = path.read_bytes()
            else:
                # Bazi-only books were moved by the registered 20261102 archive;
                # verify their original bytes in place, without restoring them.
                routes = json.loads((ROOT/'docs/路径路由映射.json').read_text('utf-8'))
                route = next(r for r in routes['archive_routes'] if r.get('manifest') == '归档/八字专项/manifest.json')
                archive_manifest = json.loads((ROOT/route['manifest']).read_text('utf-8'))
                entry = next(e for e in archive_manifest['entries']
                    if e['source_location'] == 'project' and e['original_path'] == item['source'].replace('\\','/'))
                self.assertEqual(entry['sha256'], item['source_sha256'])
                with zipfile.ZipFile(ROOT/route['archive']) as archive:
                    raw = archive.read(entry['archive_path'])
            self.assertEqual(loader.sha(raw), item['source_sha256'], item['id'])
            lines = raw.decode(item['encoding']).split('\n')
            excerpt = '\n'.join(line.rstrip('\r') for line in
                                lines[item['start_line'] - 1:item['end_line']])
            self.assertEqual(excerpt, item['excerpt'], item['id'])
        self.assertEqual(len(rows),50)


if __name__ == '__main__':
    unittest.main()
