from datetime import date

import pytest

from app.core.errors import ReportGenerationError
from app.services.report_service import generate_report, report_schema
from tests.conftest import FakeProvider

TODAY = date(2026, 11, 18)
NOTE = "Room 3 on the second floor, there's a crack in the wall. Fix it by Friday, high priority. Tell the plasterer."


def test_valid_answer_becomes_a_report(valid_report):
    provider = FakeProvider(valid_report)
    report = generate_report(NOTE, "en", provider, TODAY)

    assert report.location == "2nd floor, room 3"
    assert report.missing_fields == []
    assert len(provider.prompts) == 1


def test_prompt_contains_todays_date_hints_and_transcript(valid_report):
    provider = FakeProvider(valid_report)
    generate_report(NOTE, "en", provider, TODAY)
    prompt = provider.prompts[0]

    assert "Today is Wednesday, 2026-11-18" in prompt
    assert '"iso":"2026-11-20"' in prompt  # "Friday" already converted by nlp.py
    assert "Room 3" in prompt and "<transcript>" in prompt


def test_invalid_answer_is_retried_once_with_the_error(valid_report):
    provider = FakeProvider({**valid_report, "priority": "Urgent"}, valid_report)
    report = generate_report(NOTE, "en", provider, TODAY)

    assert report.priority.value == "High"
    assert len(provider.prompts) == 2
    assert "Validation errors" in provider.prompts[1] and "priority" in provider.prompts[1]


def test_invalid_answer_twice_raises_a_clear_error(valid_report):
    bad = {**valid_report, "category": "Plumbing"}
    with pytest.raises(ReportGenerationError, match="invalid report twice"):
        generate_report(NOTE, "en", FakeProvider(bad, bad), TODAY)


def test_schema_is_closed_for_structured_outputs():
    schema = report_schema()
    assert schema["additionalProperties"] is False
    assert "missing_fields" not in schema["properties"]  # computed by us, not by the LLM
    assert set(schema["required"]) >= {"issue", "category", "summary", "location", "priority"}
