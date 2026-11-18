"""Claude provider (default). Uses structured outputs: the API itself makes
sure the answer is valid JSON that follows our schema.

Auth: the SDK finds the credentials itself, from `ant auth login` or ANTHROPIC_API_KEY.
"""

import json
from typing import Any

import anthropic

from app.llm.base import LLMError

MODEL = "claude-haiku-5-5"  # fast and cheap: less than 1 cent per report


class ClaudeProvider:
    name = "claude"

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client or anthropic.Anthropic()

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.messages.create(
                model=MODEL,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
                output_config={
                    "effort": "low",  # a short extraction task does not need deep thinking
                    "format": {"type": "json_schema", "schema": schema},
                },
            )
        except anthropic.AuthenticationError as error:
            raise LLMError("Claude rejected the credentials. Run `ant auth login` or check ANTHROPIC_API_KEY.") from error
        except anthropic.RateLimitError as error:
            raise LLMError("Too many requests to Claude. Wait a moment and try again.") from error
        except anthropic.APIStatusError as error:
            raise LLMError(f"Claude API error {error.status_code}.") from error
        except anthropic.APIConnectionError as error:
            raise LLMError("Could not reach Claude. Check the internet connection.") from error

        if response.stop_reason == "refusal":
            raise LLMError("Claude declined to process this note.")
        if response.stop_reason == "max_tokens":
            raise LLMError("Claude's answer was cut off.")

        text = next((block.text for block in response.content if block.type == "text"), "")
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            raise LLMError("Claude did not return JSON.") from error
