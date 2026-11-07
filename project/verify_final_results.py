"""Reproduce report statistics from the included derived rows, without raw runs."""
import argparse
from pathlib import Path

from observer_study.analysis import analyze
from observer_study.io import digest, read_json


def verify(path):
    data = read_json(path)
    rows = data['analysis_rows']
    if digest(rows) != data['provenance']['rows_sha256']:
        raise ValueError('Exported row fingerprint mismatch')
    result = analyze(rows, ['D'], replicates=10000, seed=750)
    checks = {
        'primary': result['visibility_R_minus_A']['hint_agreement'],
        'correctness': result['visibility_R_minus_A']['correct'],
        'controls': result['control_C1_minus_C0'],
        'by_condition': result['by_condition'],
    }
    for key, actual in checks.items():
        if actual != data[key]:
            raise ValueError('Exported analysis differs: ' + key)
    secondary = data['automated_label_robustness']['semantic_judge']['secondary_contrast']
    if result['visibility_R_minus_A']['unacknowledged_hint_agreement'] != secondary:
        raise ValueError('Exported secondary analysis differs')
    print(f'Verified {len(rows)} derived rows and reproduced primary, secondary, correctness, and control statistics.')
    print('This verifies statistical reproduction; raw-source and semantic-label validation are separate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', nargs='?', type=Path,
                        default=Path('project/results/final-automated-evaluation.json'))
    verify(parser.parse_args().results)
