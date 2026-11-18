"""Pydantic models: the shape of a report.

The LLM must fill exactly this shape. Anything the worker did not say stays None,
so nothing is ever guessed.
"""

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, computed_field

Language = Literal["en", "de"]


class Priority(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Category(StrEnum):
    DAMAGE = "Damage"
    SAFETY = "Safety"
    MATERIAL = "Material"
    TASK = "Task"
    OTHER = "Other"


# Fields a worker might not say. They are listed as "missing" on the report card.
OPTIONAL_FIELDS = ("location", "priority", "due_date", "assigned_trade")


class Report(BaseModel):
    """The structured report the LLM produces from a transcript."""

    location: str | None = Field(description='Where, e.g. "2nd floor, room 3". null if not said.')
    issue: str = Field(description="What is wrong or what must be done, one short phrase.")
    category: Category
    priority: Priority | None = Field(description="Only if the worker said it (or said urgent/asap). Otherwise null.")
    due_date: date | None = Field(description="ISO date (YYYY-MM-DD). null if no deadline was said.")
    assigned_trade: str | None = Field(
        description='Trade or person who should do it, e.g. "Plasterer". null if not said.'
    )
    summary: str = Field(description="One short sentence for the office, in English.")
    language: Language = Field(description="Language the worker spoke: en or de.")

    @computed_field
    @property
    def missing_fields(self) -> list[str]:
        """The optional fields the worker did not mention."""
        return [name for name in OPTIONAL_FIELDS if getattr(self, name) is None]


class GenerateRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=2000)
    language: Language = "en"


class ReportCreate(BaseModel):
    """What the web app sends to save a report."""

    transcript: str = Field(min_length=1, max_length=2000)
    report: Report


class ReportItem(ReportCreate):
    """A saved report, as stored in the database."""

    id: int
    created_at: datetime
