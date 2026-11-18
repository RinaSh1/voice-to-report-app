from datetime import date

import pytest

from app.nlp import clean, extract_hints, resolve_date

TODAY = date(2026, 11, 18)  # a Wednesday


def test_clean_trims_and_collapses_spaces():
    assert clean("  Room   3 \n second floor  ") == "Room 3 second floor"


@pytest.mark.parametrize(
    ("text", "language", "expected"),
    [
        ("tomorrow", "en", date(2026, 11, 19)),
        ("Friday", "en", date(2026, 11, 20)),
        ("morgen", "de", date(2026, 11, 19)),
        ("Freitag", "de", date(2026, 11, 20)),
    ],
)
def test_relative_dates_become_real_dates(text, language, expected):
    assert resolve_date(text, language, TODAY) == expected


def test_english_hints():
    hints = extract_hints(
        "Room 3 on the second floor, there's a crack in the wall. Fix it by Friday. Order two new panels.",
        "en",
        TODAY,
    )
    assert hints.locations == ["Room 3", "second floor"]
    assert hints.numbers == ["two"]  # "3" belongs to the room, so it is not a quantity
    assert [(d.text, d.iso) for d in hints.dates] == [("Friday", "2026-11-20")]


def test_german_hints():
    hints = extract_hints("Im Raum 12 im 2. Stock ist die Steckdose kaputt. Bitte bis Freitag reparieren.", "de", TODAY)
    assert hints.locations == ["Raum 12", "2. Stock"]
    assert [d.iso for d in hints.dates] == ["2026-11-20"]


def test_no_hints_in_a_plain_sentence():
    hints = extract_hints("The wall is cracked.", "en", TODAY)
    assert hints.locations == [] and hints.numbers == [] and hints.dates == []
