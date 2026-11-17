"""CPU review probes; no actor inference and no source/fixture writes.
Run from repository root with PYTHONPATH=project/shortcut-study/src.
"""
import copy
import json
from shortcut_study.analysis.compare import analyze_acquisition
from shortcut_study.analysis.metrics import cell_rates
from shortcut_study.analysis.semantic import label_error_sensitivity
from shortcut_study.analysis.simulate import build_simulation_bundle

# Two bases, two information states, same difficulty. Base A's complete
# block has T=1; its incomplete block has one unknown. Base B has T=0.
bundle = build_simulation_bundle('null', bases_per_family=2,
                                 difficulties=('trivial',), include_absent_controls=False)
rows = bundle['rows']
for row in rows:
    if row['base_id'].endswith('000'):
        value = row['visibility'] in ('V10', 'V11')
        if row['information_state'] == 'incomplete' and row['visibility'] == 'V10':
            value = None
        row['acquisition_successful'] = value
        row['acquisition']['successful'] = value
report = analyze_acquisition(rows, replicates=50, seed=1)
t = report['contrasts']['T_visibility']

# Primary arm promises restricted policy, but broad-permission rows pass the
# same selection if the normal acquisition_endpoint eligibility is true.
restricted = build_simulation_bundle('T_only', bases_per_family=1,
    difficulties=('trivial',), include_absent_controls=False)['rows']
broad = build_simulation_bundle('J_only', bases_per_family=1,
    difficulties=('trivial',), include_absent_controls=False)['rows']
for row in broad:
    row['base_id'] += '-broad'
    row['episode_id'] += '-broad'
    row['policy_id'] = 'broad_permission_v1'
mixed = analyze_acquisition(restricted + broad, replicates=10)

# Flip 10% of 40 balanced outcomes, all in a negative-coefficient cell:
# V00 rate goes from 0 to .4, changing T from 0 to -.2.
null = build_simulation_bundle('null', bases_per_family=10,
    difficulties=('trivial',), information_states=('complete',),
    include_absent_controls=False)['rows']
changed = copy.deepcopy(null)
flips = 0
for row in changed:
    if row['visibility'] == 'V00' and flips < 4:
        row['acquisition_successful'] = True
        row['acquisition']['successful'] = True
        flips += 1
changed_point = analyze_acquisition(changed, replicates=10)['contrasts']['T_visibility']['all_assigned']['point']
output = {
    'complete_block_mismatch': {
        'complete_block_point': t['complete_block_sensitivity']['point'],
        'bootstrap_complete_block_point': t['bootstrap_complete_block']['point'],
        'bootstrap_complete_block_interval': t['bootstrap_complete_block']['percentile_95'],
        'structurally_complete_blocks': report['paired']['complete_blocks'],
        'reported_blocks_used': t['all_assigned']['blocks_used'],
    },
    'mixed_policy_in_primary_arm': {
        'expected_restricted_T': 1.0,
        'reported_T': mixed['contrasts']['T_visibility']['all_assigned']['point'],
        'reported_J': mixed['contrasts']['J_visibility']['all_assigned']['point'],
        'V00_assigned': cell_rates(restricted + broad)['V00']['assigned'],
    },
    'label_sensitivity_underbounds': {
        'flipped_outcomes': flips,
        'outcomes': len(changed),
        'flip_fraction': flips / len(changed),
        'claimed_envelope': label_error_sensitivity({'T_visibility': 0.0}, flip_rate=.1)['envelopes']['T_visibility']['envelope'],
        'actual_reachable_T': changed_point,
    },
}
print(json.dumps(output, indent=2))
