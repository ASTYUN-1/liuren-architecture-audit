import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('controller', Path(__file__).parents[1] / 'opencode-case-continue.py')
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


class FiniteWavePauseTests(unittest.TestCase):
    def test_finishes_recovered_wave_and_one_more_then_persists_pause(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            controller.batch.save_json(source / 'queue.json', {
                'dispatch_paused': False, 'pause_after_finished_wave_count': 9,
                'pause_after_wave_reason': '第47至51案完成后中场整理'})
            state = {'finished_waves': [f'wave-{i}' for i in range(1, 8)], 'active_wave': 'wave-8'}
            self.assertFalse(controller.pause_at_wave_boundary(source, state))
            state['finished_waves'].append('wave-8')
            self.assertFalse(controller.pause_at_wave_boundary(source, state))
            state['active_wave'] = 'wave-9'
            self.assertFalse(controller.pause_at_wave_boundary(source, state))
            state['finished_waves'].append('wave-9')
            self.assertTrue(controller.pause_at_wave_boundary(source, state))
            self.assertTrue(controller.batch.read_json(source / 'queue.json')['dispatch_paused'])
            self.assertEqual(state['state'], 'paused_after_completed_wave')
            self.assertTrue(controller.pause_at_wave_boundary(source, state))

    def test_never_interrupts_an_unfinished_wave(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            controller.batch.save_json(source / 'queue.json', {'pause_after_finished_wave_count': 1})
            state = {'finished_waves': ['wave-1'], 'active_wave': 'wave-2'}
            self.assertFalse(controller.pause_at_wave_boundary(source, state))


if __name__ == '__main__':
    unittest.main()
