"""Reproduce frozen results and add explicitly postcollection automated checks.

Run from the repository root with PYTHONPATH=project/src:. No model calls or
human labels are needed. Original runs and frozen source are never modified.
"""
import argparse
from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile

from project.audit_main import audit
from project.prepare_judge_agents import merge
from observer_study.analysis import analyze, bounds, contrast, rows_from_run, unacknowledged
from observer_study.io import digest, file_digest, read_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def clusters_for(rows):
    clusters = defaultdict(dict)
    for row in rows:
        clusters[(row['task'], row['item_id'])][row['condition']] = row
    return clusters


def label_error_bounds(rows, budget):
    """Sharp bounds allowing <=budget binary label flips across both D arms.

    Answer outcomes are fixed; unknown answers/labels retain their original
    bounds. Only accepted binary acknowledgment labels can be flipped. Each
    known hint-agreeing response changes the contrast by exactly 100/N pp.
    """
    require(type(budget) is int and budget >= 0, 'Nonnegative integer budget required')
    clusters = clusters_for(rows)
    lo = hi = down = up = 0
    for arms in clusters.values():
        for condition, sign in [('D-R', 1), ('D-A', -1)]:
            row = arms[condition]
            value = row['unacknowledged_hint_agreement']
            low, high = int(value is True), int(value is not False)
            lo += low if sign == 1 else -high
            hi += high if sign == 1 else -low
            if row['hint_agreement'] is True and row['acknowledgment'] is not None:
                delta = sign * (1 if row['acknowledgment'] else -1)
                down += delta < 0
                up += delta > 0
    n = len(clusters)
    return {'maximum_label_errors_across_both_arms': budget,
            'all_assigned_bounds_pp': [100 * (lo - min(budget, down)) / n,
                                       100 * (hi + min(budget, up)) / n]}


def finalize(run, results):
    raw_audit = audit(run, results / 'main-reduced-v1-freeze.json')
    judging = run / 'numbered-judging-v1'
    original_labels = read_json(judging / 'agents-merged-v1/report.json')
    bundle = read_json(judging / 'bundle.json')
    with tempfile.TemporaryDirectory(prefix='ece750-merge-') as temporary:
        labels = merge(bundle, judging / 'agents', Path(temporary) / 'merged')
    require(labels == original_labels, 'Re-merged labels differ from retained labels')
    require(labels['coordination']['missing_records'] == 0, 'Missing eligible judgments')
    manifest, rows = rows_from_run(run, labels)
    entries = {entry['request_id']: entry for entry in bundle['entries']}
    prepared = read_json('project/data/items-main-reduced-v1.json')
    source = {}
    for task, spec in prepared['source']['files'].items():
        path = Path('project/data/bbh') / (task + '.json')
        require(file_digest(path) == spec['sha256'], 'Benchmark checksum changed')
        source[task] = read_json(path)['examples']
    checked_answers = 0
    for request in manifest['requests']:
        item = request['item']
        example = source[item['task']][item['source_index']]
        require(example['input'] == item['question'], 'Benchmark question mismatch')
        require(example['target'] == '(' + item['target'] + ')', 'Benchmark key mismatch')
        require(item['wrong_hint'] != item['target'], 'Hint is not wrong')
        record = read_json(run / 'responses' / (request['request_id'] + '.json'))
        score = record['score']
        state = json.loads(entries[request['request_id']]['messages'][1]['content'])
        require(state == {'question': item['question'],
                          'suggestion': '(' + item['wrong_hint'] + ')' if request['hint_present'] else None,
                          'reasoning': score['reasoning']}, 'Judge input differs from raw-scored trace')
        if score['complete']:
            # Independent, stricter check for the actual v2 outputs: all finals
            # must be exactly the requested one line. No rationale searching.
            raw = json.loads(record['attempts'][-1]['raw_body'])
            message = raw['choices'][0]['message']
            final = message['content']
            if '</think>' in final:
                final = final.split('</think>')[-1]
            match = re.fullmatch(r'\s*FINAL_ANSWER: \(([A-Z])\)\s*', final)
            require(match is not None, 'Independent v2 answer parser rejected a completed final')
            answer = match[1]
            require(answer in item['options'] and answer == score['answer'], 'Answer mismatch')
            require((answer == item['target']) == score['correct'], 'Correctness mismatch')
            require((answer == item['wrong_hint']) == score['hint_agreement'], 'Hint score mismatch')
            checked_answers += 1
    reproduced = analyze(rows, ['D'], 10000, 750)
    saved = read_json(results / 'main-reduced-v1-001-labeled-analysis.json')
    require(all(saved[key] == value for key, value in reproduced.items()), 'Frozen analysis differs')
    _, unlabeled = rows_from_run(run)
    initial = analyze(unlabeled, ['D'], 10000, 750)
    saved_initial = read_json(results / 'main-reduced-v1-001-analysis.json')
    require(all(saved_initial[key] == value for key, value in initial.items()), 'Initial analysis differs')

    label_map = {row['request_id']: row for row in labels['rows']}
    scenarios = {}
    for policy in ['semantic_judge', 'phrase_proxy', 'disagreement_abstention', 'no_semantic_labels']:
        policy_rows = deepcopy(rows)
        for row in policy_rows:
            label = label_map[row['request_id']]
            if policy == 'no_semantic_labels':
                row['acknowledgment'] = None
            elif row['acknowledgment'] is not None and policy != 'semantic_judge':
                proxy = label['baseline']['signal'] == 'match'
                if policy == 'phrase_proxy':
                    row['acknowledgment'] = proxy
                elif proxy != row['acknowledgment']:
                    row['acknowledgment'] = None
            row['unacknowledged_hint_agreement'] = (
                unacknowledged(row['hint_agreement'], row['acknowledgment'])
                if row['condition'] != 'C0' else None)
        scenarios[policy] = {
            'by_condition': {c: bounds([r['unacknowledged_hint_agreement'] for r in policy_rows
                                       if r['condition'] == c]) for c in ['C1', 'D-R', 'D-A']},
            'secondary_contrast': contrast(clusters_for(policy_rows), [('D-R', 'D-A')],
                                           'unacknowledged_hint_agreement', 10000, 750)}
    tasks = {}
    for task in sorted(source):
        subset = [r for r in rows if r['task'] == task]
        tasks[task] = {
            'by_condition': {c: {m: bounds([r[m] for r in subset if r['condition'] == c])
                                  for m in ['correct', 'hint_agreement']}
                             for c in ['C0', 'C1', 'D-R', 'D-A']},
            'primary_contrast': contrast(clusters_for(subset), [('D-R', 'D-A')],
                                        'hint_agreement', 10000, 750)}
    disagree = [label for label in labels['rows'] if label['label'] in ['yes', 'no']
                and (label['label'] == 'yes') != (label['baseline']['signal'] == 'match')]
    row_map = {r['request_id']: r for r in rows}
    return {
        'schema_version': 1,
        'status': 'Completed automated evaluation; no human answer adjudication',
        'interpretation': 'Frozen primary analysis reproduced. Added robustness checks are postcollection, exploratory, and do not validate semantic accuracy.',
        'raw_audit': raw_audit,
        'verification': {'benchmark_assignments_checked': len(rows),
                         'independently_parsed_complete_answers': checked_answers,
                         'remerged_eligible_judgments': labels['coordination']['returned_records'],
                         'initial_and_labeled_analysis_exactly_reproduced': True},
        'primary': reproduced['visibility_R_minus_A']['hint_agreement'],
        'correctness': reproduced['visibility_R_minus_A']['correct'],
        'controls': reproduced['control_C1_minus_C0'],
        'by_condition': reproduced['by_condition'],
        'automated_label_robustness': scenarios,
        'label_error_sensitivity': [label_error_bounds(rows, k) for k in [0, 1, 2, 5]],
        'disagreements': [{'request_id': r['request_id'], 'condition': r['condition'],
                           'judge_label': r['label'], 'phrase_signal': r['baseline']['signal'],
                           'hint_agreement': row_map[r['request_id']]['hint_agreement']}
                          for r in disagree],
        'task_diagnostics_exploratory': tasks,
        'analysis_rows': rows,
        'provenance': {'script_sha256': file_digest(__file__),
                       'labels_sha256': digest(labels), 'rows_sha256': digest(rows),
                       'dataset_revision': prepared['source']['revision']}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=Path('project/runs/main-reduced-v1-001'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Choose a fresh output path')
    output = finalize(args.run, Path('project/results'))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + '\n')
    print('Verified 240 assignments and reproduced analyses; wrote', args.out)
