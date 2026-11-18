from app.api.deps import get_llm
from app.core.errors import LLMError
from app.main import app
from tests.conftest import FakeProvider


class FailingProvider:
    name = "failing"

    def generate_json(self, prompt, schema):
        raise LLMError("Could not reach the language model.")


def test_generate_returns_report_with_missing_fields(client, valid_report):
    app.dependency_overrides[get_llm] = lambda: FakeProvider({**valid_report, "assigned_trade": None})
    response = client.post("/api/reports/generate", json={"transcript": "Crack in room 3", "language": "en"})

    assert response.status_code == 200
    assert response.json()["missing_fields"] == ["assigned_trade"]


def test_empty_transcript_is_rejected(client):
    app.dependency_overrides[get_llm] = lambda: FakeProvider()
    assert client.post("/api/reports/generate", json={"transcript": ""}).status_code == 422


def test_llm_failure_gives_a_readable_502(client):
    app.dependency_overrides[get_llm] = lambda: FailingProvider()
    response = client.post("/api/reports/generate", json={"transcript": "Crack in room 3"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Could not reach the language model."


def test_invalid_answer_twice_gives_a_502(client, valid_report):
    bad = {**valid_report, "category": "Plumbing"}
    app.dependency_overrides[get_llm] = lambda: FakeProvider(bad, bad)
    response = client.post("/api/reports/generate", json={"transcript": "Crack in room 3"})

    assert response.status_code == 502
    assert "invalid report twice" in response.json()["detail"]
