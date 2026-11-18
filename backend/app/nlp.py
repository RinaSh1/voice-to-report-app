"""Classic NLP before the LLM: clean the text and find hints with spaCy.

The hints (places, numbers, dates) go to the LLM together with the transcript.
Relative dates like "Friday" or "morgen" are turned into real dates here,
because LLMs are bad at calendar maths.
"""

import re
from datetime import date, datetime
from functools import lru_cache

import dateparser
import spacy
from pydantic import BaseModel
from spacy.language import Language as SpacyModel
from spacy.matcher import Matcher

from app.models import Language

SPACY_MODELS = {"en": "en_core_web_sm", "de": "de_core_news_sm"}

# Words that start a place on a building site, followed by a number: "room 3", "Raum 12", "floor 2".
PLACE_WORDS = {
    "en": ["room", "floor", "level", "building", "apartment", "flat", "unit"],
    "de": ["raum", "zimmer", "stock", "stockwerk", "etage", "geschoss", "gebäude", "wohnung"],
}
# Ordinals before "floor": "second floor", "2nd floor", "2. Stock".
FLOOR_WORDS = {"en": ["floor", "level"], "de": ["stock", "stockwerk", "etage", "og", "obergeschoss"]}

# Words that mean a date, so we can find dates in both languages (the German model has no DATE entity).
DATE_WORDS = {
    "en": ["today", "tomorrow", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    "de": ["heute", "morgen", "übermorgen", "montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"],
}


class DateHint(BaseModel):
    text: str
    iso: str


class Hints(BaseModel):
    locations: list[str]
    numbers: list[str]
    dates: list[DateHint]


def clean(text: str) -> str:
    """Trim and collapse whitespace: '  room   3 \\n' -> 'room 3'."""
    return re.sub(r"\s+", " ", text).strip()


@lru_cache
def _model(language: Language) -> SpacyModel:
    return spacy.load(SPACY_MODELS[language])


@lru_cache
def _place_matcher(language: Language) -> Matcher:
    matcher = Matcher(_model(language).vocab)
    # "room 3", "Raum B204"
    matcher.add("PLACE", [[{"LOWER": {"IN": PLACE_WORDS[language]}}, {"TEXT": {"REGEX": r"^[A-Za-z]?\d+[A-Za-z]?$"}}]])
    # "second floor", "2nd floor", "2. Stock"
    matcher.add("FLOOR", [
        [{"TEXT": {"REGEX": r"^\d+\.$"}}, {"LOWER": {"IN": FLOOR_WORDS[language]}}],  # German "2." is one token
        [{"LOWER": {"REGEX": r"^(\d+(st|nd|rd|th)|first|second|third|fourth|fifth|ground|top)$"}},
         {"LOWER": {"IN": FLOOR_WORDS[language]}}],
        [{"LOWER": {"REGEX": r"^(erste|zweite|dritte|vierte|fünfte)[nmrs]?$"}},
         {"LOWER": {"IN": FLOOR_WORDS[language]}}],
    ])
    return matcher


def resolve_date(text: str, language: Language, today: date) -> date | None:
    """Turn 'Friday', 'tomorrow' or 'Freitag' into a real date, counted from `today`."""
    parsed = dateparser.parse(
        text,
        languages=[language],
        settings={"RELATIVE_BASE": _midday(today), "PREFER_DATES_FROM": "future"},
    )
    return parsed.date() if parsed else None


def _midday(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, 12)


def extract_hints(text: str, language: Language, today: date) -> Hints:
    """Find places, numbers and dates in the transcript."""
    doc = _model(language)(text)

    # Places: our own patterns plus spaCy's named places (e.g. a street or building name).
    spans = [doc[start:end] for _, start, end in _place_matcher(language)(doc)]
    spans += [ent for ent in doc.ents if ent.label_ in {"FAC", "GPE", "LOC"}]
    locations = _unique(span.text for span in sorted(spans, key=lambda s: s.start))

    # Numbers that are not part of a place ("3" in "room 3" is not a quantity).
    in_place = {token.i for span in spans for token in span}
    numbers = _unique(token.text for token in doc if token.like_num and token.i not in in_place)

    # Dates: spaCy DATE entities (English) plus known date words (both languages).
    date_texts = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    date_texts += [token.text for token in doc if token.lower_ in DATE_WORDS[language]]
    dates = []
    for date_text in _unique(date_texts):
        resolved = resolve_date(date_text, language, today)
        if resolved and not any(d.iso == resolved.isoformat() for d in dates):
            dates.append(DateHint(text=date_text, iso=resolved.isoformat()))

    return Hints(locations=locations, numbers=numbers, dates=dates)


def _unique(items) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen
