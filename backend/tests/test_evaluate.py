import json

from app.models import Report
from eval.evaluate import FIELDS, SAMPLES, field_ok, score


def test_null_must_stay_null():
    assert field_ok(None, None)
    assert not field_ok(None, "Plumber")  # a guessed value is wrong


def test_keywords_must_all_appear_case_insensitive():
    assert field_ok(["crack", "wall"], "Crack in the WALL")
    assert not field_ok(["crack", "wall"], "Crack in the floor")


def test_keyword_alternatives():
    assert field_ok(["second|2nd"], "2nd floor, stairs")


def test_exact_values():
    assert field_ok("High", "High")
    assert not field_ok("2026-11-20", "2026-11-21")


def test_score_checks_every_field(valid_report):
    expected = {"location": ["room 3"], "issue": ["crack"], "category": "Damage",
                "priority": "High", "due_date": "2026-11-20", "assigned_trade": ["plaster"]}
    report = Report(**{**valid_report, "location": "Room 3, 2nd floor"})
    assert score(expected, report) == dict.fromkeys(FIELDS, True)


def test_sample_file_has_ten_valid_samples():
    samples = json.loads(SAMPLES.read_text())["samples"]
    assert len(samples) == 10
    for sample in samples:
        assert sample["language"] in {"en", "de"}
        assert set(sample["expected"]) == set(FIELDS)
