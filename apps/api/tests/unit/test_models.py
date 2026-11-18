import pytest
from pydantic import ValidationError

from app.schemas.report import Report

COMPLETE = {
    "location": "2nd floor, room 3",
    "issue": "Crack in the wall next to the window",
    "category": "Damage",
    "priority": "High",
    "due_date": "2026-11-20",
    "assigned_trade": "Plasterer",
    "summary": "Crack in wall next to window in room 3, fix by Friday.",
    "language": "en",
}


def test_complete_report_has_nothing_missing():
    assert Report(**COMPLETE).missing_fields == []


def test_fields_that_were_not_said_are_listed_as_missing():
    report = Report(**{**COMPLETE, "priority": None, "assigned_trade": None})
    assert report.missing_fields == ["priority", "assigned_trade"]


def test_missing_fields_are_part_of_the_json():
    assert "missing_fields" in Report(**COMPLETE).model_dump()


@pytest.mark.parametrize(
    ("field", "bad_value"), [("priority", "Urgent"), ("category", "Plumbing"), ("due_date", "Friday")]
)
def test_invalid_values_are_rejected(field, bad_value):
    with pytest.raises(ValidationError):
        Report(**{**COMPLETE, field: bad_value})
