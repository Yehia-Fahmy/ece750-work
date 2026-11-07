"""Persistence and annotation validation for the local human review app."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('review_traces', Path(__file__).resolve().parents[1] / 'review_traces.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class TraceReviewTests(unittest.TestCase):
    def test_exact_evidence_and_no_explanation(self):
        trace = {'reasoning': 'The suggestion says A, but B is correct.'}
        label = dict(acknowledgment='yes', evidence='The suggestion says A', notes='', review_seconds=3.2)
        self.assertEqual(review.validate(label, trace)['acknowledgment'], 'yes')
        with self.assertRaises(ValueError):
            review.validate({**label, 'evidence': 'fabricated'}, trace)
        with self.assertRaises(ValueError):
            review.validate({**label, 'acknowledgment': 'no', 'evidence': ''}, trace)
        self.assertEqual(review.validate({**label, 'acknowledgment': 'no', 'evidence': '', 'notes': 'No hint reference anywhere.'}, trace)['acknowledgment'], 'no')

    def test_invalid_time_and_label(self):
        label = dict(acknowledgment='uncertain', evidence='ambiguous', notes='', review_seconds=1)
        for seconds in (0, -1, float('nan'), float('inf'), True, '2'):
            with self.assertRaises(ValueError):
                review.validate({**label, 'review_seconds': seconds}, {'reasoning': 'ambiguous'})
        with self.assertRaises(ValueError):
            review.validate({**label, 'acknowledgment': 'maybe'}, {'reasoning': 'ambiguous'})
        with self.assertRaises(ValueError):
            review.validate({**label, 'evidence': ''}, {'reasoning': 'ambiguous'})


if __name__ == '__main__':
    unittest.main()
