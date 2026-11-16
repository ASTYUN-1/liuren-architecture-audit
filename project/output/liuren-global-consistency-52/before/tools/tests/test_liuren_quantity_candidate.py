"""Candidate integration checks; these measure loading and provenance, not divination."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/stage-liuren-quantity-20261027.py'
spec = importlib.util.spec_from_file_location('quantity_candidate_test', SCRIPT)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
loader = candidate.pages


class QuantityCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidate.verify()
        cls.manifest = candidate.manifest_checked()

    def test_actual_cli_roundtrip_for_full_exam_timing_quantity_route(self):
        _, active = loader.active()
        script = ROOT / 'tools/load-liuren-methods.py' if active['release'] == candidate.RELEASE else SCRIPT
        proc = subprocess.run([sys.executable, '-X', 'utf8', str(script), 'plan',
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
                result = subprocess.run([sys.executable, '-X', 'utf8', str(script), 'read',
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
        candidate.dump(candidate.OUT / 'page-roundtrip.json', dict(
            release=candidate.RELEASE, moduleCount=len(plan['modules']), pageCount=len(receipts),
            bytesVerified=sum(item['bytes'] for item in receipts), pages=receipts,
            predictionTested=False))

    def test_condition_selection_is_explicit_and_live_release_matches_activation(self):
        for domain in self.manifest['domains']:
            generic = loader.plan(self.manifest, [domain])
            self.assertNotIn('quantity', generic)
            self.assertNotIn('quantity-sources', generic)
            numeric = loader.plan(self.manifest, [domain], extras=['quantity'])
            self.assertIn('quantity', numeric)
            self.assertNotIn('quantity-sources', numeric)
            self.assertEqual([key for key in numeric if key != 'quantity'], generic)
        _, active = loader.active()
        if active['release'] == candidate.PARENT:
            with self.assertRaises(ValueError):
                loader.plan(active, extras=['quantity'])
        else:
            self.assertEqual(active['release'], candidate.RELEASE)
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
            raw = path.read_bytes()
            self.assertEqual(loader.sha(raw), item['source_sha256'], item['id'])
            lines = raw.decode(item['encoding']).split('\n')
            excerpt = '\n'.join(line.rstrip('\r') for line in
                                lines[item['start_line'] - 1:item['end_line']])
            self.assertEqual(excerpt, item['excerpt'], item['id'])
        candidate.dump(candidate.OUT / 'evidence-roundtrip.json', dict(
            excerptGroups=len(rows), sourceFiles=len({item['source'] for item in rows}),
            sourceHashesAndLFExcerptsMatched=True, predictiveValidation=False))


if __name__ == '__main__':
    unittest.main()
