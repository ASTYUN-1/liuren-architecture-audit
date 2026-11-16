import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('archive', Path(__file__).parents[1] / 'archive-opencode-case.py')
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class WorkflowOnlyGateTests(unittest.TestCase):
    def prepare(self, root):
        for name in ['first.json', 'review.json']:
            archive.batch.save_json(root / name, {'preserved': name})
        decision = {'mode': 'workflow_only', 'semantic_review_performed': False, 'checks_passed': True,
                    'first_json_sha256': archive.batch.digest((root / 'first.json').read_bytes()),
                    'review_json_sha256': archive.batch.digest((root / 'review.json').read_bytes())}
        archive.batch.save_json(root / 'workflow-check.json', decision)
        return {'review_mode': 'workflow_only', 'content_review_waived_by_user': True}, decision

    def test_user_authorized_workflow_check_does_not_forge_semantic_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue, _ = self.prepare(root)
            result = archive.archive_gate(root, {}, queue)
            self.assertFalse(result['semantic_review_performed'])
            self.assertNotIn('reviewer', result)
            self.assertFalse((root / 'codex-review.json').exists())

    def test_no_implicit_waiver_and_no_false_claim_of_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue, decision = self.prepare(root)
            queue['content_review_waived_by_user'] = False
            with self.assertRaises(ValueError):
                archive.archive_gate(root, {}, queue)
            queue['content_review_waived_by_user'] = True
            decision['semantic_review_performed'] = True
            archive.batch.save_json(root / 'workflow-check.json', decision)
            with self.assertRaises(ValueError):
                archive.archive_gate(root, {}, queue)

    def test_frozen_artifacts_cannot_change_after_workflow_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue, _ = self.prepare(root)
            archive.batch.save_json(root / 'first.json', {'changed': True})
            with self.assertRaises(ValueError):
                archive.archive_gate(root, {}, queue)

    def test_existing_reviewed_mode_still_needs_actual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            with self.assertRaises(FileNotFoundError):
                archive.archive_gate(root, {}, {})


if __name__ == '__main__':
    unittest.main()
