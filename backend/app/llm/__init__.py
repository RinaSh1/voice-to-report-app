"""Pick the LLM provider from the LLM_PROVIDER environment variable (default: claude)."""

import os

from app.llm.base import LLMError, LLMProvider

__all__ = ["LLMError", "LLMProvider", "get_provider"]


def get_provider() -> LLMProvider:
    name = os.getenv("LLM_PROVIDER", "claude").lower()
    if name == "claude":
        from app.llm.claude import ClaudeProvider

        return ClaudeProvider()
    if name == "ollama":
        from app.llm.ollama import OllamaProvider

        return OllamaProvider()
    raise ValueError(f"Unknown LLM_PROVIDER '{name}'. Use 'claude' or 'ollama'.")
