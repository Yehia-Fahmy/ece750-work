"""Compare the analytical label-error bound to exhaustive label perturbations."""
import itertools
import unittest
from project.finalize_analysis import label_error_bounds


class LabelErrorTests(unittest.TestCase):
    def test_sharp_budget_bounds_against_exhaustive_flips(self):
        rows = []
        for item, (r_ack, a_ack) in enumerate([(True, False), (False, True)]):
            for condition, ack in [('D-R', r_ack), ('D-A', a_ack)]:
                rows.append(dict(task='t', item_id=str(item), condition=condition,
                                 hint_agreement=True, acknowledgment=ack,
                                 unacknowledged_hint_agreement=not ack))
        for k in range(6):
            values = []
            for flips in itertools.product([False, True], repeat=4):
                if sum(flips) <= k:
                    values.append(50 * sum((1 if r['condition'] == 'D-R' else -1)
                                           * int(r['unacknowledged_hint_agreement'] != flip)
                                           for r, flip in zip(rows, flips)))
            self.assertEqual(label_error_bounds(rows, k)['all_assigned_bounds_pp'],
                             [min(values), max(values)])

    def test_nonagreement_and_unknowns(self):
        rows = [dict(task='t', item_id='a', condition='D-R', hint_agreement=False,
                     acknowledgment=False, unacknowledged_hint_agreement=False),
                dict(task='t', item_id='a', condition='D-A', hint_agreement=None,
                     acknowledgment=None, unacknowledged_hint_agreement=None)]
        self.assertEqual(label_error_bounds(rows, 5)['all_assigned_bounds_pp'], [-100, 0])
        with self.assertRaises(ValueError):
            label_error_bounds(rows, -1)
