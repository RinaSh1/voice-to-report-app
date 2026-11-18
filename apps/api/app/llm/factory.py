from app.core.config import Settings
from app.llm.base import LLMProvider


def create_provider(settings: Settings) -> LLMProvider:
    """Build the provider chosen in the settings."""
    if settings.llm_provider == "ollama":
        from app.llm.ollama import OllamaProvider

        return OllamaProvider(url=settings.ollama_url, model=settings.ollama_model)

    from app.llm.claude import ClaudeProvider

    return ClaudeProvider(model=settings.claude_model)
