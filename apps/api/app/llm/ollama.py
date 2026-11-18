"""Ollama provider: free and local. Requires a running Ollama with the configured model pulled."""

import json
from typing import Any

import httpx

from app.core.errors import LLMError


class OllamaProvider:
    name = "ollama"

    def __init__(self, url: str, model: str) -> None:
        self._url = url
        self._model = model

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(
                f"{self._url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "format": schema,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return json.loads(response.json()["message"]["content"])
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as error:
            raise LLMError(f"Ollama failed ({error}). Is it running with model {self._model}?") from error
