from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Liveness check that also shows the active LLM provider."""
    return {"status": "ok", "llm_provider": settings.llm_provider}
