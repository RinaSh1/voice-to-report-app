from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_ok_and_shows_default_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "llm_provider": "claude"}


def test_health_shows_configured_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    assert client.get("/api/health").json()["llm_provider"] == "ollama"
