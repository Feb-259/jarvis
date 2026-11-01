from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from jarvis_api.assistant import AssistantService
from jarvis_api.config import Settings, settings
from jarvis_api.llm.base import LLMProvider, LLMProviderError
from jarvis_api.llm.factory import create_llm_provider
from jarvis_api.postgres import PostgresConversationStore
from jarvis_api.schemas import ChatRequest, ChatResponse
from jarvis_api.storage import ConversationPersistenceError, ConversationStore


def create_app(
    config: Settings = settings,
    provider: LLMProvider | None = None,
    store: ConversationStore | None = None,
) -> FastAPI:
    selected_provider = provider or create_llm_provider(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        selected_store = store
        owns_store = selected_store is None
        if selected_store is None:
            selected_store = await PostgresConversationStore.connect(config.database_url)
        app.state.assistant = AssistantService(selected_provider, selected_store)
        try:
            yield
        finally:
            if owns_store:
                await selected_store.close()

    app = FastAPI(title=config.app_name, version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": config.environment}

    @app.post("/v1/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
        try:
            return await http_request.app.state.assistant.chat(
                request.message,
                request.conversation_id,
            )
        except LLMProviderError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ConversationPersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Conversation storage is unavailable.",
            ) from exc

    return app


app = create_app()
