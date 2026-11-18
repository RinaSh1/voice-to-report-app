from fastapi.testclient import TestClient

from app.llm import LLMError, get_provider
from app.main import app
from tests.conftest import FakeProvider

client = TestClient(app)


class FailingProvider:
    name = "failing"

    def generate_json(self, prompt, schema):
        raise LLMError("Could not reach Claude.")


def use(provider):
    app.dependency_overrides[get_provider] = lambda: provider


def teardown_function():
    app.dependency_overrides.clear()


def test_generate_returns_report_with_missing_fields(valid_report):
    use(FakeProvider({**valid_report, "assigned_trade": None}))
    response = client.post("/api/reports/generate", json={"transcript": "Crack in room 3", "language": "en"})

    assert response.status_code == 200
    assert response.json()["missing_fields"] == ["assigned_trade"]


def test_empty_transcript_is_rejected():
    use(FakeProvider())
    assert client.post("/api/reports/generate", json={"transcript": ""}).status_code == 422


def test_llm_failure_gives_a_readable_502():
    use(FailingProvider())
    response = client.post("/api/reports/generate", json={"transcript": "Crack in room 3"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Could not reach Claude."
