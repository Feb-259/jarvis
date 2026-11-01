from collections.abc import Sequence
from typing import Literal, Protocol, TypedDict


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot return a valid response."""


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class LLMProvider(Protocol):
    @property
    def name(self) -> str: ...

    async def generate_reply(
        self,
        message: str,
        history: Sequence[ChatMessage] = (),
    ) -> str: ...
