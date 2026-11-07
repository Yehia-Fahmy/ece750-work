"""Analyze a matched study run, with optional source-fingerprinted acknowledgment labels."""
import argparse
from pathlib import Path
from observer_study.analysis import analyze, rows_from_run
from observer_study.acknowledgment import save_new
from observer_study.io import digest, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--labels', type=Path)
    parser.add_argument('--roles', nargs='+', default=['D', 'E', 'M'])
    parser.add_argument('--replicates', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=20261106)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        labels = read_json(args.labels) if args.labels else None
        manifest, rows = rows_from_run(args.run, labels)
        result = analyze(rows, args.roles, args.replicates, args.seed)
        result.update(source_manifest_sha256=digest(manifest), source_analysis_rows_sha256=digest(rows),
                      labels_sha256=digest(labels) if labels else None,
                      split=manifest['identity']['split'],
                      interpretation='Pilot/development diagnostics' if manifest['identity']['split'] != 'main'
                      else 'Study estimates conditional on accepted labels; consult frozen protocol for primary outcome')
        save_new(args.out, result)
        print(f"Analyzed {len(rows)} assigned responses; saved {args.out}")
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
