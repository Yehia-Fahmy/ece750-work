# Trace desk

Run from the repository root:

```sh
python3 project/review_traces.py
```

Open http://127.0.0.1:8765 in your browser. No installation, inference, or external service is needed. Keep the terminal running. Use one browser tab and one reviewer at a time.

The app reads only the existing development pilot's `review.csv`, ID mapping, and response scores. All 48 traces are available, with the five incorrect final answers first (including the reasoning/final-answer mismatch). This priority queue is intentionally unblinded to correctness; it is not a blinded reliability assessment. Preliminary AI acknowledgment judgments are not displayed or imported. No validation/main traces are loaded.

Timing starts when an unfinished trace opens. It counts active, focused review time, including label entry. Switching traces, hiding the tab, leaving the window, or clicking Pause stops it. After leaving the window, click Resume to continue. Saved traces reopen paused; revising them retains previous time and adds time only after Resume. There is no idle cutoff while the tab remains focused. Time is measured in fractional seconds; display rounds down. Browser drafts checkpoint every second and on changes, and survive refresh in the same browser. A browser or OS crash can lose up to the last checkpoint interval. Save & next writes the completed label to disk atomically. A failed save stays on the trace with an error.

For Yes and Uncertain, select an exact passage in the reasoning and click Capture selection (or paste it). For No, evidence can be empty: explain the absence in Notes. An optional exact passage can still be supplied. All labels are independent human judgments; no labels or review times have been manufactured by the app.

Saved records live in `project/runs/pilot-v1-development-001/human-review.json`, separate from the original blank CSV and raw evidence. Export review CSV downloads all rows in the original schema, leaving unlabeled rows blank. `review_id` joins to the existing `review.mapping.json`; there is no claim that downstream label import or primary-outcome analysis is implemented. Back up/export after each review session. Local drafts are convenience recovery, not a replacement for saving to disk.

The workload projection uses saved active seconds averaged across completed traces × 960. Because errors come first, early estimates may not represent the full set. A no-hint control can receive No with an explicit no-hint note; it must remain distinguishable from hinted responses in downstream analysis.

To use another existing review export/run or port:

```sh
python3 project/review_traces.py --run /absolute/path/to/run --port 8766
```
