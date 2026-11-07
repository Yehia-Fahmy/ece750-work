"""External workers must not see labels or silently replace another assignment."""
from pathlib import Path
import tempfile
import unittest

from project.prepare_judge_agents import prepare, merge
from observer_study.io import read_json, write_json
from test_acknowledgment import fixture, verdict


class AgentPacketTests(unittest.TestCase):
    def test_blinding_and_partial_merge(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            directory = root / 'agents'
            index = prepare(bundle, directory, 2)
            self.assertEqual(index['eligible'], 3)
            self.assertEqual(len(index['packets']), 2)
            packet = read_json(directory / 'packets/packet-001.json')
            self.assertEqual(set(packet['records'][0]), {'review_id', 'input_sha256', 'messages'})
            response = {k: packet[k] for k in ('packet_id', 'packet_sha256', 'bundle_sha256')}
            response.update(judge={'provider': 'test', 'model': 'cheap-v1', 'settings': {'reasoning_effort': 'low'}},
                            results=[{k: packet['records'][0][k] for k in ('review_id', 'input_sha256')}])
            response['results'][0]['verdict'] = verdict('uncertain')
            write_json(directory / 'outputs/packet-001.json', response)
            report = merge(bundle, directory, root / 'merged')
            self.assertEqual(report['coordination']['missing_records'], 2)
            self.assertEqual(report['coordination']['missing_packets'], ['packet-002'])
            self.assertEqual(report['overall']['unresolved'], 4)  # includes incomplete source trace
            saved = read_json(root / 'merged/judgments.json')
            self.assertEqual(saved['results'][0]['agent_judge']['model'], 'cheap-v1')
            with self.assertRaises(FileExistsError): merge(bundle, directory, root / 'merged')

    def test_foreign_record_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            directory = root / 'agents'
            prepare(bundle, directory, 1)
            packet = read_json(directory / 'packets/packet-001.json')
            foreign = read_json(directory / 'packets/packet-002.json')['records'][0]
            response = {k: packet[k] for k in ('packet_id', 'packet_sha256', 'bundle_sha256')}
            response.update(judge={'provider': 'test', 'model': 'test', 'settings': {}}, results=[{
                'review_id': foreign['review_id'], 'input_sha256': foreign['input_sha256'], 'verdict': verdict('no')}])
            write_json(directory / 'outputs/packet-001.json', response)
            with self.assertRaisesRegex(ValueError, 'unassigned'): merge(bundle, directory, root / 'merged')

    def test_tampered_packet_and_guide_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = fixture(root)
            directory = root / 'agents'
            prepare(bundle, directory)
            path = directory / 'packets/packet-001.json'
            packet = read_json(path)
            packet['records'][0]['messages'] = []
            write_json(path, packet)
            with self.assertRaisesRegex(ValueError, 'fingerprint'): merge(bundle, directory, root / 'merged')
            (directory / 'worker.md').write_text('Changed rubric')
            with self.assertRaisesRegex(ValueError, 'instructions changed'): merge(bundle, directory, root / 'merged')
