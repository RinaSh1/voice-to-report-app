"""The interface every language-model provider implements."""

from typing import Any, Protocol


class LLMProvider(Protocol):
    name: str

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Send the prompt and return JSON that follows `schema`. Raises LLMError on failure."""
        ...
