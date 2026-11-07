"""Fresh validation selection must not consume reserved main items or duplicates."""
import tempfile
import unittest
from pathlib import Path

from project.prepare_fresh_evaluation import select_fresh, synthetic_bundle
from observer_study.io import digest, file_digest, write_json
from observer_study.acknowledgment import validate_bundle


class FreshEvaluationTests(unittest.TestCase):
    def test_reserved_duplicate_text_is_excluded_and_selection_stable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            questions = ['Reserved', 'New one', 'New two']
            write_json(root / 'task.json', {'examples': [
                {'input': q + '\n(A) First\n(B) Second', 'target': '(B)'} for q in questions]})
            write_json(root / 'source.json', {'revision': 'rev', 'files': {'task': {
                'sha256': file_digest(root / 'task.json')}}})
            # Different reserved ID but identical text must still be excluded.
            reserved = {'items': [{'item_id': 'different:0000', 'question_sha256': digest(
                'Reserved\n(A) First\n(B) Second')}]}
            config = {'dataset_revision': 'rev', 'tasks': ['task'], 'seed': 0}
            result = select_fresh(config, reserved, root)
            self.assertEqual(result, select_fresh(config, reserved, root))
            self.assertNotEqual(result['items'][0]['source_index'], 0)
            self.assertEqual(result['selection_audit']['task']['eligible_unreserved'], 2)
            self.assertEqual(result['items'][0]['split'], 'pilot_validation')

    def test_reference_is_separate_and_balanced(self):
        bundle, references = synthetic_bundle()
        validate_bundle(bundle)
        self.assertEqual(len(bundle['entries']), 6)
        self.assertTrue(all('expected_label' not in e for e in bundle['entries']))
        self.assertEqual(sorted(c['expected_label'] for c in references['cases']),
                         ['no', 'no', 'uncertain', 'uncertain', 'yes', 'yes'])
