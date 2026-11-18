"""The LLM interface. Every provider (Claude, Ollama, ...) works the same way,
so the rest of the app never needs to know which one is used."""

from typing import Any, Protocol


class LLMError(Exception):
    """The provider could not answer (network, auth, refusal, cut-off output...)."""


class LLMProvider(Protocol):
    name: str

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Send the prompt and return JSON that follows `schema`."""
        ...
