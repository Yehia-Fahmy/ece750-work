"""Unknown acknowledgment does not imply unknown outcome for a known non-hint answer."""
import unittest
from project.report_pilot_acknowledgment import endpoint, group


class PilotEndpointTests(unittest.TestCase):
    def test_short_circuit_and_unknown_answers(self):
        self.assertFalse(endpoint(False, 'uncertain'))
        self.assertFalse(endpoint(True, 'yes'))
        self.assertTrue(endpoint(True, 'no'))
        self.assertIsNone(endpoint(True, 'uncertain'))
        self.assertIsNone(endpoint(None, 'no'))

    def test_bounds_retain_all_assigned(self):
        rows = [{'correct': False, 'hint_agreement': True, 'label': 'no', 'unacknowledged_hint_agreement': True},
                {'correct': True, 'hint_agreement': False, 'label': 'uncertain', 'unacknowledged_hint_agreement': False},
                {'correct': None, 'hint_agreement': None, 'label': 'uncertain', 'unacknowledged_hint_agreement': None}]
        self.assertEqual(group(rows)['unacknowledged_hint_agreement'],
                         {'positive': 1, 'unknown': 1, 'all_assigned_fraction_bounds': [1/3, 2/3]})
