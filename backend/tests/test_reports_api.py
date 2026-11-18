import pytest
from fastapi.testclient import TestClient

from app.db import ReportStore, get_store
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_store(tmp_path):
    """Each test gets its own empty database file."""
    store = ReportStore(tmp_path / "test.db")
    app.dependency_overrides[get_store] = lambda: store
    yield store
    app.dependency_overrides.clear()


def test_list_is_empty_at_start():
    assert client.get("/api/reports").json() == []


def test_saved_report_is_listed_with_id_and_time(valid_report):
    response = client.post("/api/reports", json={"transcript": "Crack in room 3", "report": valid_report})

    assert response.status_code == 201
    saved = response.json()
    assert saved["id"] == 1 and saved["created_at"]
    assert client.get("/api/reports").json() == [saved]


def test_list_is_newest_first(valid_report):
    for issue in ["first", "second"]:
        client.post("/api/reports", json={"transcript": issue, "report": {**valid_report, "issue": issue}})

    assert [item["report"]["issue"] for item in client.get("/api/reports").json()] == ["second", "first"]


def test_missing_fields_survive_saving(valid_report):
    client.post("/api/reports", json={"transcript": "x", "report": {**valid_report, "priority": None}})
    assert client.get("/api/reports").json()[0]["report"]["missing_fields"] == ["priority"]


def test_invalid_report_is_not_saved(valid_report):
    response = client.post("/api/reports", json={"transcript": "x", "report": {**valid_report, "category": "Plumbing"}})
    assert response.status_code == 422
    assert client.get("/api/reports").json() == []
