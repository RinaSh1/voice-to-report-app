"""Claude provider. Structured outputs make the API itself return JSON that follows the schema.

Credentials are resolved by the SDK (`ant auth login` profile or ANTHROPIC_API_KEY).
"""

import json
from typing import Any

import anthropic

from app.core.errors import LLMError


class ClaudeProvider:
    name = "claude"

    def __init__(self, model: str, client: anthropic.Anthropic | None = None) -> None:
        self._model = model
        self._client = client or anthropic.Anthropic()

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
                output_config={
                    "effort": "low",  # short extraction task
                    "format": {"type": "json_schema", "schema": schema},
                },
            )
        except anthropic.AuthenticationError as error:
            raise LLMError("The language model rejected the credentials.") from error
        except anthropic.RateLimitError as error:
            raise LLMError("The language model is busy. Please try again in a moment.") from error
        except anthropic.APIStatusError as error:
            raise LLMError(f"Language model error ({error.status_code}).") from error
        except anthropic.APIConnectionError as error:
            raise LLMError("Could not reach the language model.") from error

        if response.stop_reason == "refusal":
            raise LLMError("The language model declined to process this note.")
        if response.stop_reason == "max_tokens":
            raise LLMError("The language model's answer was cut off.")

        text = next((block.text for block in response.content if block.type == "text"), "")
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            raise LLMError("The language model did not return JSON.") from error
