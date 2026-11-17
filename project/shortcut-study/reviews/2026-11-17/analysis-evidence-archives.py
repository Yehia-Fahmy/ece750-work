"""Verify retained evidence without changing raw archives or running inference."""
import hashlib
import json
from collections import Counter
from pathlib import Path

results = []
for name in ('g2-held-out-20261116', 'g2-held-out-20261116-catalog-v2',
             'g1-long-pilots-20261116', 'native-qualification-tab01-v6-16cell'):
    archive = Path('project/runs/shortcut-study') / name
    evidence = json.loads((Path('project/shortcut-study/results/qualification') / (name + '.json')).read_text())
    manifest = json.loads((archive / 'manifest.json').read_text())
    mismatches = []
    for relative, expected in manifest['artifact_sha256'].items():
        path = archive / relative
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            mismatches.append(relative)
    anchors = []
    def inspect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in ('hashes', 'sha256') and isinstance(child, dict):
                    for relative, expected in child.items():
                        path = archive / relative
                        if isinstance(expected, str) and len(expected) == 64 and path.is_file():
                            anchors.append({'path': relative, 'matches': hashlib.sha256(path.read_bytes()).hexdigest() == expected})
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    inspect(evidence)
    assignments = json.loads((archive / 'schedule.json').read_text())['assignments']
    rows = {a['episode_id']: json.loads((archive / a['episode_id'] / 'scored.json').read_text()) for a in assignments}
    counts = Counter(r['integrity']['terminal_status'] for r in rows.values())
    easy = [a for a in assignments if a['intended_difficulty'] == 'trivial' and a['information_state'] == 'complete' and not a['shortcut_available']]
    complete = [rows[a['episode_id']] for a in assignments if a['information_state'] == 'complete']
    complete_completed = [r for r in complete if r['integrity']['terminal_status'] == 'completed']
    results.append({
        'run': name,
        'manifest_entries': len(manifest['artifact_sha256']),
        'manifest_mismatches': mismatches,
        'tracked_hash_anchors': anchors,
        'assigned': len(assignments),
        'scored': len(rows),
        'terminal_counts': dict(counts),
        'easy_successes': sum(rows[a['episode_id']]['task_result']['authorized_success'] is True for a in easy),
        'easy_assigned': len(easy),
        'complete_assigned': len(complete),
        'complete_completed': len(complete_completed),
        'complete_completed_parseable': sum(r['task_result']['answer_valid'] is True for r in complete_completed),
        'complete_assigned_answer_valid': sum(r['task_result']['answer_valid'] is True for r in complete),
    })
print(json.dumps(results, indent=2))
