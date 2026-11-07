"""Selection provenance survives Unicode, repeated passages and partial returns."""
import json
from pathlib import Path
import tempfile
import unittest

from observer_study.io import digest, read_json, write_json
from observer_study.numbered_evidence import passages, numbered_record, materialize
from project.prepare_judge_agents import prepare, merge
from test_acknowledgment import fixture


class NumberedEvidenceTests(unittest.TestCase):
    def test_lossless_unicode_and_repeated_passage(self):
        text = '  Café says A.\nThe suggestion is A.\nThe suggestion is A.\n\n'
        parts = passages(text)
        self.assertEqual(''.join(p['text'] for p in parts), text)
        for p in parts:
            self.assertEqual(text[p['start']:p['end']], p['text'])
            self.assertEqual(digest(p['text']), p['text_sha256'])
        self.assertEqual(passages(text), parts)
        self.assertEqual(passages(''), [])

    def test_selector_rejects_invalid_and_preserves_selected_offset(self):
        record = {'passages': passages('Same. Same.'), 'reasoning_sha256': digest('Same. Same.')}
        for ids in ([0], [999], [True], ['1'], [1, 1], None):
            with self.assertRaises(ValueError):
                materialize({'verdict': {'label': 'yes', 'evidence_passage_ids': ids,
                                         'explanation': 'A reference.'}}, record)
        output = materialize({'verdict': {'label': 'uncertain', 'evidence_passage_ids': [2],
                                         'explanation': 'Ambiguous.'}}, record)
        self.assertEqual(output['verdict']['evidence'], [' Same.'])
        self.assertEqual(output['selected_evidence'][0]['start'], 5)
        self.assertEqual(output['verdict']['label'], 'uncertain')

    def test_single_trace_merge_and_missing_labels(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            directory = root / 'agents'
            index = prepare(bundle, directory)
            self.assertEqual(len(index['packets']), index['eligible'])
            packet = read_json(directory / 'packets/packet-001.json')
            self.assertEqual(len(packet['records']), 1)
            record = packet['records'][0]
            self.assertNotIn('baseline', record)
            state = json.loads(record['messages'][1]['content'])
            self.assertEqual(''.join(p['text'] for p in record['passages']), state['reasoning'])
            response = {k: packet[k] for k in ('packet_id', 'packet_sha256', 'bundle_sha256')}
            response.update(judge={'provider': 'test', 'model': 'test', 'settings': {}}, results=[{
                'review_id': record['review_id'], 'input_sha256': record['input_sha256'],
                'verdict': {'label': 'uncertain', 'evidence_passage_ids': [1], 'explanation': 'Unclear reference.'}}])
            write_json(directory / 'outputs/packet-001.json', response)
            report = merge(bundle, directory, root / 'merged')
            self.assertEqual(report['coordination']['missing_records'], 2)
            row = next(r for r in report['rows'] if r['review_id'] == record['review_id'])
            self.assertEqual(row['label'], 'uncertain')
            self.assertEqual(row['evidence_spans'], [record['passages'][0]])
            saved = read_json(root / 'merged/judgments.json')['results'][0]
            self.assertEqual(saved['verdict']['evidence'], [record['passages'][0]['text']])
            self.assertEqual(saved['verdict']['label'], 'uncertain')
