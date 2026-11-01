from collections.abc import Sequence
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from jarvis_api.assistant import AssistantService
from jarvis_api.llm.base import ChatMessage, LLMProviderError
from jarvis_api.llm.mock import MockLLMProvider
from jarvis_api.main import create_app
from jarvis_api.storage import ConversationPersistenceError


class FakeConversationStore:
    def __init__(self, fail: bool = False) -> None:
        self.turns: list[dict[str, object]] = []
        self.fail = fail

    async def save_turn(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
        provider: str,
    ) -> None:
        if self.fail:
            raise ConversationPersistenceError("database unavailable")
        self.turns.append(
            {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "provider": provider,
            }
        )

    async def get_history(self, conversation_id: UUID, limit: int) -> list[ChatMessage]:
        messages: list[ChatMessage] = []
        for turn in self.turns:
            if turn["conversation_id"] != conversation_id:
                continue
            messages.extend(
                [
                    {"role": "user", "content": str(turn["user_message"])},
                    {"role": "assistant", "content": str(turn["assistant_message"])},
                ]
            )
        return messages[-limit:]


@pytest.fixture
def api():
    store = FakeConversationStore()
    app = create_app(provider=MockLLMProvider(), store=store)
    with TestClient(app) as client:
        yield client, store


def test_health(api):
    client, _ = api
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_returns_mock_reply_and_persists_turn(api):
    client, store = api
    response = client.post("/v1/chat", json={"message": "Hello"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "mock"
    assert payload["conversation_id"]
    assert "received your message" in payload["reply"]
    assert len(store.turns) == 1
    assert str(store.turns[0]["conversation_id"]) == payload["conversation_id"]
    assert store.turns[0]["user_message"] == "Hello"
    assert store.turns[0]["assistant_message"] == payload["reply"]


def test_chat_appends_to_existing_conversation(api):
    client, store = api
    first = client.post("/v1/chat", json={"message": "Hello"}).json()
    second = client.post(
        "/v1/chat",
        json={
            "message": "Again",
            "conversation_id": first["conversation_id"],
        },
    ).json()

    assert second["conversation_id"] == first["conversation_id"]
    assert [turn["user_message"] for turn in store.turns] == ["Hello", "Again"]


def test_chat_sends_previous_turns_to_provider():
    store = FakeConversationStore()

    class RecordingProvider:
        def __init__(self) -> None:
            self.histories: list[list[ChatMessage]] = []

        @property
        def name(self) -> str:
            return "recording"

        async def generate_reply(
            self,
            message: str,
            history: Sequence[ChatMessage] = (),
        ) -> str:
            self.histories.append(list(history))
            return f"reply to {message}"

    provider = RecordingProvider()
    app = create_app(provider=provider, store=store)
    with TestClient(app) as client:
        first = client.post("/v1/chat", json={"message": "Hello"}).json()
        client.post(
            "/v1/chat",
            json={
                "message": "What did I say?",
                "conversation_id": first["conversation_id"],
            },
        )

    assert provider.histories == [
        [],
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "reply to Hello"},
        ],
    ]


def test_chat_rejects_non_uuid_conversation_id(api):
    client, _ = api

    response = client.post(
        "/v1/chat",
        json={"message": "Hello", "conversation_id": "not-a-uuid"},
    )

    assert response.status_code == 422


def test_chat_returns_service_unavailable_when_provider_fails(api):
    client, store = api

    class FailingProvider:
        @property
        def name(self) -> str:
            return "failing"

        async def generate_reply(
            self,
            message: str,
            history: Sequence[ChatMessage] = (),
        ) -> str:
            raise LLMProviderError("Ollama is unavailable.")

    client.app.state.assistant = AssistantService(FailingProvider(), store)

    response = client.post("/v1/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert response.json() == {"detail": "Ollama is unavailable."}
    assert store.turns == []


def test_chat_returns_service_unavailable_when_storage_fails():
    store = FakeConversationStore(fail=True)
    app = create_app(provider=MockLLMProvider(), store=store)
    with TestClient(app) as client:
        response = client.post("/v1/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert response.json() == {"detail": "Conversation storage is unavailable."}
