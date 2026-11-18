import pytest

from app.api.deps import get_repository
from app.db.repository import ReportRepository
from app.main import app


@pytest.fixture(autouse=True)
def repository(tmp_path):
    """Each test gets its own empty database file."""
    repository = ReportRepository(tmp_path / "test.db")
    app.dependency_overrides[get_repository] = lambda: repository
    return repository


def test_list_is_empty_at_start(client):
    assert client.get("/api/reports").json() == []


def test_saved_report_is_listed_with_id_and_time(client, valid_report):
    response = client.post("/api/reports", json={"transcript": "Crack in room 3", "report": valid_report})

    assert response.status_code == 201
    saved = response.json()
    assert saved["id"] == 1 and saved["created_at"]
    assert client.get("/api/reports").json() == [saved]


def test_list_is_newest_first(client, valid_report):
    for issue in ["first", "second"]:
        client.post("/api/reports", json={"transcript": issue, "report": {**valid_report, "issue": issue}})

    assert [item["report"]["issue"] for item in client.get("/api/reports").json()] == ["second", "first"]


def test_missing_fields_survive_saving(client, valid_report):
    client.post("/api/reports", json={"transcript": "x", "report": {**valid_report, "priority": None}})
    assert client.get("/api/reports").json()[0]["report"]["missing_fields"] == ["priority"]


def test_invalid_report_is_not_saved(client, valid_report):
    invalid = {**valid_report, "category": "Plumbing"}
    response = client.post("/api/reports", json={"transcript": "x", "report": invalid})
    assert response.status_code == 422
    assert client.get("/api/reports").json() == []
