"""Reproduce key report numbers from tracked main stats JSON (clean-checkout)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATS_DEFAULT = ROOT / "results" / "main" / "main-s0-tab-v0-20261118-stats.json"
REPORT_DEFAULT = HERE / "final-report.md"


def pct(rate: float) -> str:
    return f"{100 * rate:.1f}%"


def check(cond: bool, msg: str, failures: list[str]) -> None:
    if not cond:
        failures.append(msg)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats", type=Path, default=STATS_DEFAULT)
    parser.add_argument("--report", type=Path, default=REPORT_DEFAULT)
    args = parser.parse_args()
    stats = json.loads(args.stats.read_text())
    text = args.report.read_text()
    failures: list[str] = []

    check(stats.get("submission_authorized") is False, "stats.submission_authorized must be false", failures)
    check(stats["assigned"] == 320, "assigned != 320", failures)
    check(stats["completed"] == 318, "completed != 318", failures)
    check(abs(stats["completion_rate"] - 0.99375) < 1e-12, "completion_rate mismatch", failures)
    check(stats["sampling"]["temperature"] == 0.2, "temperature != 0.2", failures)
    check(stats["semantic_scope"] == "withdrawn_behavioral_only", "semantic_scope mismatch", failures)
    check(stats["terminal_counts"]["model_format_failure"] == 2, "format failures != 2", failures)

    info = stats["key_contrasts_among_completed"]["information_state_authorized"]
    check(info["complete"]["authorized"] == 51 and info["complete"]["n"] == 158, "complete authorized mismatch", failures)
    check(info["incomplete"]["authorized"] == 8 and info["incomplete"]["n"] == 160, "incomplete authorized mismatch", failures)
    check(abs(info["delta_complete_minus_incomplete"] - 0.2727848101265823) < 1e-12, "delta mismatch", failures)

    acq = stats["key_contrasts_among_completed"]["shortcut_acquisition_successful"]
    check(acq["sc_present"]["count"] == 0 and acq["sc_absent"]["count"] == 0, "acquisition.successful not zero", failures)

    easy = stats["easy_no_shortcut"]
    check(easy["authorized"] == 28 and easy["n"] == 80, "easy no-shortcut mismatch", failures)

    # Report prose must carry the headline figures.
    for needle in [
        "318/320",
        "32.3%",
        "5.0%",
        "+27.3",
        "submission_authorized=false",
        "acquisition.successful",
        "T=0.2",
    ]:
        check(needle in text, f"report missing required token: {needle}", failures)

    # Guard against accidental S4 "0 main" claim in the final report body.
    if re.search(r"\b0\b main factorial", text, flags=re.I):
        failures.append("final report still claims 0 main factorial (stale S4 language)")

    if failures:
        print("VERIFY FAIL:")
        for f in failures:
            print(" -", f)
        return 1
    print("VERIFY OK: report numbers match tracked stats; submission_authorized=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
