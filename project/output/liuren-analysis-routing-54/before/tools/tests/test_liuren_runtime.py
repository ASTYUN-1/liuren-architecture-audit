import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from liuren_runtime import ROOT, SOURCE, build, verify, sha, content_version


class RuntimeTest(unittest.TestCase):
    def test_reproducible_and_paragraph_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a', Path(d) / 'b'
            ma, mb = build(a), build(b)
            self.assertEqual(ma['version'], mb['version'])
            self.assertEqual(ma['files'], mb['files'])
            self.assertGreater(verify(a)['paragraphs'], 2000)
            with self.assertRaises(ValueError):
                build(a)

    def test_tamper_missing_and_unbound_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'candidate'; build(p)
            f = p / '.opencode/skills/daliuren/refs/runtime/core.md'
            raw = f.read_bytes(); f.write_bytes(raw + b'changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                verify(p)
            f.write_bytes(raw); f.unlink()
            with self.assertRaisesRegex(ValueError, 'unbound or missing'):
                verify(p)
            f.write_bytes(raw); (p / 'extra.md').write_text('unbound')
            with self.assertRaisesRegex(ValueError, 'unbound or missing'):
                verify(p)
            (p / 'extra.md').unlink()
            m = json.loads((p / 'liuren-runtime.json').read_text('utf-8')); m['required'] = []
            (p / 'liuren-runtime.json').write_text(json.dumps(m), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'metadata binding'):
                verify(p)

    def test_protected_outputs_and_mode_separation(self):
        for p in [ROOT, ROOT / '.opencode/skills/candidate', SOURCE / 'candidate']:
            with self.assertRaises(ValueError):
                build(p)
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'structural', Path(d) / 'enhanced'
            self.assertNotEqual(build(a, 'structural')['version'], build(b)['version'])
            self.assertEqual((a / '.opencode/skills/daliuren/refs/runtime/core.md').read_bytes(), (SOURCE / 'sources/structural-core.md').read_bytes())

    def test_deleted_mapping_is_rejected_even_when_rehashed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'candidate'; m = build(p)
            name = '.opencode/skills/daliuren/refs/runtime/migration-map.json'
            rows = json.loads((p / name).read_text('utf-8')); rows.pop()
            (p / name).write_text(json.dumps(rows, ensure_ascii=False), encoding='utf-8')
            m['files'][name] = sha((p / name).read_bytes()); m['version'] = content_version(m['files'], m['mode'])
            (p / 'liuren-runtime.json').write_text(json.dumps(m), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'coverage incomplete'):
                verify(p)


if __name__ == '__main__':
    unittest.main()
