import copy
import unittest
from observer_study.experiment import schedule
from observer_study.io import digest

class ConditionSelectionTests(unittest.TestCase):
    def test_subset_preserves_payload_and_seed(self):
        config = {'seed': 0, 'generation': {}, 'model': {'alias':'test'}}
        item = {'item_id':'task:0','split':'main','question':'Q','wrong_hint':'B'}
        prepared = {'config_sha256':digest(config),'items':[item]}
        full = {r['condition']:r for r in schedule(config,prepared,'main')}
        reduced = {**config,'conditions':['C0','C1','D-R','D-A']}
        prepared['config_sha256'] = digest(reduced)
        actual = schedule(reduced,prepared,'main')
        self.assertEqual(len(actual),4)
        for row in actual:
            self.assertEqual(row,full[row['condition']])
        for invalid in ([], ['C1','C1'], ['bad'], 'C1', [None]):
            reduced['conditions'] = invalid
            prepared['config_sha256'] = digest(reduced)
            with self.assertRaises(ValueError):
                schedule(reduced,prepared,'main')
