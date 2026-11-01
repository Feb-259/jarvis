from typing import Protocol
from uuid import UUID

from jarvis_api.llm.base import ChatMessage


class ConversationPersistenceError(RuntimeError):
    """Raised when conversation data cannot be read or saved."""


class ConversationStore(Protocol):
    async def get_history(
        self,
        conversation_id: UUID,
        limit: int,
    ) -> list[ChatMessage]: ...

    async def save_turn(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
        provider: str,
    ) -> None: ...
