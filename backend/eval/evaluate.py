"""Evaluation: how accurate is the pipeline? Runs 10 sample notes through the real
pipeline and prints the accuracy per field. This is a simple version of what AI teams
do before changing a prompt or a model.

Run from the backend folder (uses the real LLM, costs about 1 cent with Claude Haiku):
    python -m eval.evaluate
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from app.llm import get_provider
from app.models import Report
from app.report_service import generate_report

SAMPLES = Path(__file__).with_name("samples.json")
FIELDS = ["location", "issue", "category", "priority", "due_date", "assigned_trade"]


def field_ok(expected: Any, actual: Any) -> bool:
    """null must stay null (never guess). Keyword lists must all appear (a|b = either). Everything else must match exactly."""
    if expected is None:
        return actual is None
    if actual is None:
        return False
    if isinstance(expected, list):
        # "second|2nd" means either word is fine.
        text = str(actual).lower()
        return all(any(option in text for option in keyword.lower().split("|")) for keyword in expected)
    return str(expected) == str(actual)


def score(expected: dict[str, Any], report: Report) -> dict[str, bool]:
    data = report.model_dump(mode="json")
    return {field: field_ok(expected[field], data[field]) for field in FIELDS}


def main() -> None:
    config = json.loads(SAMPLES.read_text())
    today = date.fromisoformat(config["today"])
    provider = get_provider()
    totals = {field: 0 for field in FIELDS}
    samples = config["samples"]

    for number, sample in enumerate(samples, start=1):
        report = generate_report(sample["transcript"], sample["language"], provider, today)
        result = score(sample["expected"], report)
        for field, ok in result.items():
            totals[field] += ok
        wrong = [f"{field}={getattr(report, field)!r}" for field, ok in result.items() if not ok]
        print(f"{number:2}. {'OK ' if not wrong else 'ERR'} {sample['transcript'][:55]:55} {', '.join(wrong)}")

    print(f"\nAccuracy per field ({len(samples)} samples, provider: {provider.name})")
    for field in FIELDS:
        print(f"  {field:15} {totals[field] / len(samples):6.0%}")
    overall = sum(totals.values()) / (len(samples) * len(FIELDS))
    print(f"  {'overall':15} {overall:6.0%}")


if __name__ == "__main__":
    main()
