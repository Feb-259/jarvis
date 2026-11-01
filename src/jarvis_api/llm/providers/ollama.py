
from collections.abc import Sequence

import httpx

from jarvis_api.llm.base import ChatMessage, LLMProviderError


class OllamaProvider:
    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._transport = transport

    @property
    def name(self) -> str:
        return f"ollama:{self._model}"

    async def generate_reply(
        self,
        message: str,
        history: Sequence[ChatMessage] = (),
    ) -> str:
        messages = [
            {"role": item["role"], "content": item["content"]}
            for item in history
        ]
        messages.append({"role": "user", "content": message})
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json={
                        "model": self._model,
                        "messages": messages,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"Ollama returned HTTP {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Could not connect to Ollama: {exc}") from exc
        except ValueError as exc:
            raise LLMProviderError("Ollama returned invalid JSON.") from exc

        if not isinstance(data, dict):
            raise LLMProviderError("Ollama returned an unexpected response.")
        response_message = data.get("message")
        if not isinstance(response_message, dict):
            raise LLMProviderError("Ollama response is missing its message.")
        content = response_message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("Ollama response is missing message content.")
        return content.strip()
