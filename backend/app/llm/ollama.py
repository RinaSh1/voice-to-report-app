"""Ollama provider (optional, free and local). Needs Ollama running and a model pulled,
e.g. `ollama pull llama3.2`. Choose it with LLM_PROVIDER=ollama in .env."""

import json
import os
from typing import Any

import httpx

from app.llm.base import LLMError


class OllamaProvider:
    name = "ollama"

    def __init__(self) -> None:
        self._url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self._model = os.getenv("OLLAMA_MODEL", "llama3.2")

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(
                f"{self._url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "format": schema,  # Ollama also supports JSON-schema output
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return json.loads(response.json()["message"]["content"])
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as error:
            raise LLMError(f"Ollama failed: {error}. Is Ollama running with model {self._model}?") from error
