# Reduced main-study runbook

**Final status:** [report complete](report/final-report.pdf), with [automated verification and reproduction instructions](report/README.md). The [completion plan](completion-plan.md) supersedes the historical human-review completion requirement below. The frozen protocol is preserved; acknowledgment findings remain exploratory. Collection and original analysis commands below describe the retained study, not a request to rerun it.

The [frozen protocol](main-protocol-v1.md) selects 60 reserved questions and four conditions (240 responses), with wrong-hint agreement primary and acknowledgment-dependent outcomes secondary. The exact freeze and source archive are under `runs/main-reduced-v1-freeze/`; its tracked hash inventory is [results/main-reduced-v1-freeze.json](results/main-reduced-v1-freeze.json). Do not rewrite these files to incorporate later edits.

From the repository root, run tests with `PYTHONPATH=project/src python3 -m unittest discover -s project/tests -q`.

Collection was launched with:

```sh
python3 project/serve_local.py --config project/configs/main-reduced-v1.json
PYTHONPATH=project/src python3 -m observer_study run --config project/configs/main-reduced-v1.json --items project/data/items-main-reduced-v1.json --split main --out project/runs/main-reduced-v1-001
```

The active server may have been launched using the pilot config: its model/runtime/context are identical, while request sampling and exact prompts come from the main runner. Preflight verifies identity and rendered prompts. GPU/socket access may require execution outside the sandbox.

To resume an interrupted run, use the same command with `--resume`, under the same frozen source/configuration and endpoint. Do not rerun completed or interrupted attempts, or choose a new run to replace unfavorable outcomes. `runs/main-reduced-v1-001-collection.log` records progress. Keep original raw responses.

After completion:

```sh
PYTHONPATH=project/src python3 -m observer_study summarize project/runs/main-reduced-v1-001 --out project/results/main-reduced-v1-001-summary.json
PYTHONPATH=project/src python3 project/analyze_study.py project/runs/main-reduced-v1-001 --roles D --replicates 10000 --seed 750 --out project/results/main-reduced-v1-001-analysis.json
PYTHONPATH=project/src python3 -m observer_study export-review project/runs/main-reduced-v1-001 --out project/runs/main-reduced-v1-001/review.csv
```

The initial analysis does not invent acknowledgment labels: unreviewed labels remain unknown and the secondary endpoint has bounds. Human review CSV stays blank until the researcher supplies labels. The pilot exporter remains pilot-only. The separate postcollection `prepare_main_judging.py` verifies the complete run against the frozen snapshot and exports main packets without changing frozen source. There are 179 eligible single-trace packets at `runs/main-reduced-v1-001/numbered-judging-v1/agents/`; 60 no-hint controls and one incomplete trace are excluded from judging. The export initially created no labels. The subsequent authorized judging pass completed all 179 packets: 177 yes, 2 no, zero eligible uncertain/missing judgments, and all evidence checks passed. The incomplete trace remains unresolved. See the [judging report](results/main-reduced-v1-001-judging-report.md), [aggregate results](results/main-reduced-v1-001-acknowledgment.json), and [analysis with automated labels](results/main-reduced-v1-001-labeled-analysis.json). Human validation remains outstanding. Raw prompts, runtime outputs, plans, ledgers and merged labels are preserved under the numbered-judging directory; earlier reports and the human review CSV remain intact.

The constructed fresh evaluation can be recreated with `project/prepare_fresh_evaluation.py --out NEW_DIRECTORY` under `PYTHONPATH=project/src`. It preserves separate references and produces three disjoint natural items. Use `prepare_judge_agents.py prepare` for one-trace numbered packets, then isolated workers. `report_fresh_evaluation.py` merges new outputs and assesses the fixed gates; use `PYTHONPATH=project/src:.` and a directory with no prior `*-merged` reports. Re-running these now is replication, not another untouched test of a revised method.

No separate API bill or measured human coding time is available. Automated judgments are not human validation. See [analysis-methods.md](analysis-methods.md) for estimands and limitations.
