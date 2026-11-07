"""Prepare blinded agent packets and merge disjoint external agent judgments."""

import argparse
from pathlib import Path

from observer_study.acknowledgment import evaluate_bundle, save_new, validate_bundle
from observer_study.io import digest, file_digest, read_json
from observer_study.numbered_evidence import FORMAT, numbered_record, materialize

GUIDES = Path(__file__).resolve().parent / 'judge-agents'


def prepare(bundle, output, batch_size=1):
    validate_bundle(bundle)
    if type(batch_size) is not int or batch_size < 1:
        raise ValueError('Batch size must be a positive integer')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'packets').mkdir()
    (output / 'outputs').mkdir()
    entries = sorted((e for e in bundle['entries'] if not e['excluded_reason']), key=lambda e: e['review_id'])
    index = {'evidence_format': FORMAT if batch_size == 1 else 'legacy-quotations', 'bundle_sha256': bundle['bundle_sha256'], 'worker_guide_sha256': file_digest(GUIDES / 'worker.md'),
             'eligible': len(entries), 'batch_size': batch_size, 'packets': []}
    (output / 'worker.md').write_bytes((GUIDES / 'worker.md').read_bytes())
    (output / 'coordinator.md').write_bytes((GUIDES / 'coordinator.md').read_bytes())
    for offset in range(0, len(entries), batch_size):
        packet_id = f'packet-{offset // batch_size + 1:03d}'
        packet = {'packet_id': packet_id, 'bundle_sha256': bundle['bundle_sha256'],
                  'worker_guide_sha256': index['worker_guide_sha256'],
                  'evidence_format': index['evidence_format'],
                  'records': [numbered_record(e) if batch_size == 1 else
                              {k: e[k] for k in ('review_id', 'input_sha256', 'messages')}
                              for e in entries[offset:offset + batch_size]]}
        packet['packet_sha256'] = digest(packet)
        save_new(output / 'packets' / (packet_id + '.json'), packet)
        index['packets'].append({'packet_id': packet_id, 'packet_sha256': packet['packet_sha256']})
    save_new(output / 'index.json', index)
    return index


def merge(bundle, directory, output):
    validate_bundle(bundle)
    directory = Path(directory)
    index = read_json(directory / 'index.json')
    if index['bundle_sha256'] != bundle['bundle_sha256']:
        raise ValueError('Index belongs to a different bundle')
    if file_digest(directory / 'worker.md') != index['worker_guide_sha256']:
        raise ValueError('Worker instructions changed after export')
    numbered = index.get('evidence_format') == FORMAT
    expected = {e['review_id']: numbered_record(e) if numbered else
                {k: e[k] for k in ('review_id', 'input_sha256', 'messages')}
                for e in bundle['entries'] if not e['excluded_reason']}
    assigned, returned, workers, results, missing = set(), set(), [], [], []
    packet_ids = [p['packet_id'] for p in index['packets']]
    if len(packet_ids) != len(set(packet_ids)):
        raise ValueError('Duplicate packet ID')
    known_names = {pid + '.json' for pid in packet_ids}
    if any(p.name not in known_names for p in (directory / 'outputs').glob('*.json')):
        raise ValueError('Unknown output file; archive extra rounds outside outputs/')
    for spec in index['packets']:
        pid = spec['packet_id']
        if not isinstance(pid, str) or not pid.startswith('packet-') or not pid[7:].isdigit():
            raise ValueError('Invalid packet ID')
        packet = read_json(directory / 'packets' / (pid + '.json'))
        unhashed = dict(packet)
        claimed = unhashed.pop('packet_sha256')
        if (digest(unhashed) != claimed or claimed != spec['packet_sha256']
                or packet['packet_id'] != pid or packet['bundle_sha256'] != bundle['bundle_sha256']
                or packet['worker_guide_sha256'] != index['worker_guide_sha256']):
            raise ValueError('Packet fingerprint mismatch')
        if numbered and (packet.get('evidence_format') != FORMAT or len(packet['records']) != 1):
            raise ValueError('Numbered workflow requires exactly one trace per packet')
        owned = set()
        for record in packet['records']:
            rid = record['review_id']
            if rid in assigned or expected.get(rid) != record:
                raise ValueError('Overlapping or altered packet input')
            assigned.add(rid)
            owned.add(rid)
        path = directory / 'outputs' / (pid + '.json')
        if not path.exists():
            missing.append(pid)
            continue
        response = read_json(path)
        if any(response.get(k) != packet[k] for k in ('packet_id', 'packet_sha256', 'bundle_sha256')):
            raise ValueError('Worker output identity mismatch')
        # Check ownership before looking up evidence from another assignment.
        for result in response.get('results', []):
            if result.get('review_id') not in owned:
                raise ValueError('Worker returned an unassigned record')
        if numbered:
            response = {**response, 'results': [materialize(r, expected[r['review_id']])
                                               for r in response['results']]}
        # Existing importer validates schema, provenance, and input IDs before pooling.
        evaluate_bundle(bundle, response)
        for result in response['results']:
            rid = result['review_id']
            if rid not in owned or rid in returned:
                raise ValueError('Worker returned an unassigned or duplicate record')
            returned.add(rid)
            results.append({**result, 'agent_packet_id': pid, 'agent_judge': response.get('judge')})
        workers.append({'packet_id': pid, 'judge': response.get('judge'), 'output_sha256': file_digest(path)})
    if assigned != set(expected):
        raise ValueError('Packet assignments do not cover eligible records exactly')
    judgments = {'bundle_sha256': bundle['bundle_sha256'],
                 'judge': {'provider': 'external-agent-coordination', 'model': 'see_per_packet_provenance',
                           'settings': {'worker_guide_sha256': index['worker_guide_sha256'], 'workers': workers}},
                 'results': results}
    report = evaluate_bundle(bundle, judgments)
    input_hashes = {e['review_id']: e['input_sha256'] for e in bundle['entries']}
    for row in report['rows']:
        row['input_sha256'] = input_hashes[row['review_id']]
    if numbered:
        selected = {r['review_id']: r['selected_evidence'] for r in results}
        for row in report['rows']:
            if row['check'] == 'passed' and row['review_id'] in selected:
                row['evidence_spans'] = selected[row['review_id']]
    report['coordination'] = {'missing_packets': missing, 'eligible': len(expected),
                              'returned_records': len(returned), 'missing_records': len(expected) - len(returned)}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    save_new(output / 'judgments.json', judgments)
    save_new(output / 'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'merge'))
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--packets', type=Path)
    parser.add_argument('--batch-size', type=int, default=1)
    args = parser.parse_args()
    try:
        bundle = read_json(args.bundle)
        if args.command == 'prepare':
            result = prepare(bundle, args.out, args.batch_size)
            print(f"Prepared {len(result['packets'])} packets for {result['eligible']} eligible records")
        else:
            if args.packets is None:
                raise ValueError('--packets is required for merge')
            result = merge(bundle, args.packets, args.out)
            print(result['coordination'])
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
