import asyncio
import json

import httpx
import pytest

from jarvis_api.config import Settings
from jarvis_api.llm.base import LLMProviderError
from jarvis_api.llm.factory import create_llm_provider
from jarvis_api.llm.mock import MockLLMProvider
from jarvis_api.llm.providers.ollama import OllamaProvider


def test_ollama_provider_sends_chat_request_and_returns_content():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "http://ollama.test/api/chat"
        assert json.loads(request.content) == {
            "model": "qwen2.5:3b",
            "messages": [{"role": "user", "content": "Xin chào"}],
            "stream": False,
        }
        return httpx.Response(
            200,
            json={"message": {"content": "  Xin chào!  "}},
        )

    provider = OllamaProvider(
        model="qwen2.5:3b",
        base_url="http://ollama.test/",
        transport=httpx.MockTransport(handler),
    )

    assert asyncio.run(provider.generate_reply("Xin chào")) == "Xin chào!"


def test_ollama_provider_includes_history_before_current_message():
    history = [
        {"role": "user", "content": "Tôi tên là An"},
        {"role": "assistant", "content": "Chào An"},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["messages"] == [
            *history,
            {"role": "user", "content": "Bạn nhớ tên tôi không?"},
        ]
        return httpx.Response(200, json={"message": {"content": "An"}})

    provider = OllamaProvider(transport=httpx.MockTransport(handler))

    reply = asyncio.run(
        provider.generate_reply("Bạn nhớ tên tôi không?", history)
    )

    assert reply == "An"


def test_ollama_provider_reports_http_errors():
    provider = OllamaProvider(
        transport=httpx.MockTransport(lambda request: httpx.Response(500))
    )

    with pytest.raises(LLMProviderError, match="HTTP 500"):
        asyncio.run(provider.generate_reply("Hello"))


def test_ollama_provider_reports_connection_errors():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = OllamaProvider(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMProviderError, match="Could not connect to Ollama"):
        asyncio.run(provider.generate_reply("Hello"))


@pytest.mark.parametrize(
    "payload",
    [
        {"unexpected": "shape"},
        {"message": {"content": ""}},
        [],
    ],
)
def test_ollama_provider_reports_invalid_responses(payload):
    provider = OllamaProvider(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload)
        )
    )

    with pytest.raises(LLMProviderError):
        asyncio.run(provider.generate_reply("Hello"))


def test_factory_selects_mock_provider():
    provider = create_llm_provider(Settings(llm_provider="mock"))

    assert isinstance(provider, MockLLMProvider)


def test_factory_selects_configured_ollama_provider():
    provider = create_llm_provider(
        Settings(
            llm_provider="ollama",
            ollama_model="custom-model",
            ollama_base_url="http://ollama.test",
            ollama_timeout=15,
        )
    )

    assert isinstance(provider, OllamaProvider)
    assert provider.name == "ollama:custom-model"


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Choose 'mock' or 'ollama'"):
        create_llm_provider(Settings(llm_provider="unknown"))
