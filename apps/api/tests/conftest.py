import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_REPORT = {
    "location": "2nd floor, room 3",
    "issue": "Crack in the wall next to the window",
    "category": "Damage",
    "priority": "High",
    "due_date": "2026-11-20",
    "assigned_trade": "Plasterer",
    "summary": "Crack in wall next to window in room 3, fix by Friday.",
    "language": "en",
}


class FakeProvider:
    """Stands in for the LLM: returns prepared answers and records the prompts."""

    name = "fake"

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts: list[str] = []
        self.schemas: list[dict] = []

    def generate_json(self, prompt, schema):
        self.prompts.append(prompt)
        self.schemas.append(schema)
        return self.answers.pop(0)


@pytest.fixture
def valid_report() -> dict:
    return dict(VALID_REPORT)


@pytest.fixture
def client():
    """API client; dependency overrides set in a test are removed afterwards."""
    yield TestClient(app)
    app.dependency_overrides.clear()
