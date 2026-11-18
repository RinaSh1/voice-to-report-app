"""Transcript -> structured report.

    clean text -> spaCy hints + real dates -> LLM (JSON schema) -> Pydantic check -> Report

LLMs can make mistakes, so the answer is always validated. If it is invalid,
we retry once and tell the LLM what was wrong.
"""

import json
from datetime import date
from typing import Any

from pydantic import ValidationError

from app.llm import LLMProvider
from app.models import Language, Report
from app.nlp import Hints, clean, extract_hints

INSTRUCTIONS = """You turn a voice note from a construction site into a structured site report.

Rules:
- Use only what the worker said. If something was not said, use null. Never guess.
- priority: only if the worker said it, or said "urgent", "asap", "dringend" (= High). Otherwise null.
- due_date: use the dates in the hints (already converted to YYYY-MM-DD). Otherwise null.
- category: Damage (something broken/cracked/leaking), Safety (danger to people), Material (order or delivery), Task (work to do), Other.
- Write issue and summary in English, even if the note is in German. Fix obvious speech-to-text mistakes (e.g. "crock in the wall" -> "crack in the wall").
- language: the language the worker spoke."""


class ReportError(Exception):
    """The LLM did not produce a valid report, even after one retry."""


def report_schema() -> dict[str, Any]:
    """The JSON schema the LLM must follow. Structured outputs need additionalProperties: false."""
    schema = Report.model_json_schema()
    _close_objects(schema)
    return schema


def _close_objects(node: Any) -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            node["additionalProperties"] = False
        for value in node.values():
            _close_objects(value)
    elif isinstance(node, list):
        for item in node:
            _close_objects(item)


def build_prompt(transcript: str, language: Language, hints: Hints, today: date) -> str:
    return (
        f"{INSTRUCTIONS}\n\n"
        f"Today is {today.strftime('%A')}, {today.isoformat()}.\n"
        f"Spoken language: {language}\n"
        f"Hints found by spaCy (may be incomplete): {hints.model_dump_json()}\n\n"
        f"<transcript>\n{transcript}\n</transcript>"
    )


def generate_report(transcript: str, language: Language, provider: LLMProvider, today: date) -> Report:
    text = clean(transcript)
    hints = extract_hints(text, language, today)
    prompt = build_prompt(text, language, hints, today)
    schema = report_schema()

    data = provider.generate_json(prompt, schema)
    try:
        return Report.model_validate(data)
    except ValidationError as error:
        # Retry once, and show the LLM exactly what was wrong.
        retry_prompt = (
            f"{prompt}\n\nYour previous answer was invalid:\n{json.dumps(data)}\n"
            f"Validation errors:\n{error}\nReturn corrected JSON."
        )
        data = provider.generate_json(retry_prompt, schema)
        try:
            return Report.model_validate(data)
        except ValidationError as second_error:
            raise ReportError("The AI returned an invalid report twice. Please try again.") from second_error
