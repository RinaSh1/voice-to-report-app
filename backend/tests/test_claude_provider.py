from types import SimpleNamespace

import pytest

from app.llm.base import LLMError
from app.llm.claude import MODEL, ClaudeProvider


class FakeMessages:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


def fake_client(text='{"ok": true}', stop_reason="end_turn"):
    response = SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])
    return SimpleNamespace(messages=FakeMessages(response))


def test_sends_schema_as_structured_output_and_parses_json():
    client = fake_client()
    result = ClaudeProvider(client).generate_json("prompt", {"type": "object"})

    assert result == {"ok": True}
    assert client.messages.kwargs["model"] == MODEL
    assert client.messages.kwargs["output_config"]["format"] == {"type": "json_schema", "schema": {"type": "object"}}


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_unusable_stop_reasons_raise(stop_reason):
    with pytest.raises(LLMError):
        ClaudeProvider(fake_client(stop_reason=stop_reason)).generate_json("prompt", {})
