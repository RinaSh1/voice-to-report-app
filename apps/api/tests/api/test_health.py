from app.core.config import Settings, get_settings
from app.main import app


def test_health_is_ok_and_shows_default_provider(client):
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "llm_provider": "claude"}


def test_health_shows_configured_provider(client):
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, llm_provider="ollama")
    assert client.get("/api/health").json()["llm_provider"] == "ollama"
