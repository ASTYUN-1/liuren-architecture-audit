import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('wave', Path(__file__).parents[1] / 'opencode-case-wave.py')
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)


class WaveIsolationTests(unittest.TestCase):
    def test_workers_have_independent_state_and_only_their_own_blind_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            source = project / 'source'
            for folder in ['public-inputs', 'private']:
                (source / folder).mkdir(parents=True)
            jobs = [{'alias': f'case-{i:04d}', 'case_id': f'raw-{i}', 'state': 'pending'} for i in range(1, 7)]
            wave.batch.save_json(source / 'queue.json', {'schema': 'opencode-case-batch-v1', 'jobs': jobs})
            for job in jobs:
                for folder in ['public-inputs', 'private']:
                    wave.batch.save_json(source / folder / (job['alias'] + '.json'), {'alias': job['alias']})
            target = project / 'wave'
            with patch.object(wave, 'PROJECT', project):
                wave.prepare(source, target, 5)
            manifest = wave.batch.read_json(target / 'wave.json')
            self.assertEqual(manifest['concurrency'], 2)
            self.assertEqual(len(manifest['jobs']), 5)
            for row in manifest['jobs']:
                run = Path(row['run'])
                local = wave.batch.read_json(run / 'queue.json')
                self.assertEqual(len(local['jobs']), 1)
                self.assertEqual(local['authorized_case_ids'], [row['case_id']])
                self.assertEqual([p.name for p in (run / 'public-inputs').iterdir()], [row['alias'] + '.json'])


if __name__ == '__main__':
    unittest.main()
