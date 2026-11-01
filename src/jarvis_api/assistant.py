import uuid

from jarvis_api.llm.base import LLMProvider
from jarvis_api.schemas import ChatResponse
from jarvis_api.storage import ConversationStore

CONTEXT_MESSAGE_LIMIT = 20


class AssistantService:
    def __init__(self, provider: LLMProvider, store: ConversationStore) -> None:
        self._provider = provider
        self._store = store

    async def chat(
        self,
        message: str,
        conversation_id: uuid.UUID | None = None,
    ) -> ChatResponse:
        resolved_id = conversation_id or uuid.uuid4()
        history = await self._store.get_history(
            conversation_id=resolved_id,
            limit=CONTEXT_MESSAGE_LIMIT,
        )
        reply = await self._provider.generate_reply(message, history)
        await self._store.save_turn(
            conversation_id=resolved_id,
            user_message=message,
            assistant_message=reply,
            provider=self._provider.name,
        )
        return ChatResponse(
            conversation_id=str(resolved_id),
            reply=reply,
            provider=self._provider.name,
        )
