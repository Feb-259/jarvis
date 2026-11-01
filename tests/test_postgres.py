import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4

from jarvis_api.postgres import PostgresConversationStore


class FakeConnection:
    def __init__(self) -> None:
        self.executions: list[tuple[str, tuple[object, ...]]] = []
        self.fetches: list[tuple[str, tuple[object, ...]]] = []
        self.transaction_count = 0
        self.rows: list[dict[str, str]] = []

    @asynccontextmanager
    async def transaction(self):
        self.transaction_count += 1
        yield

    async def execute(self, query: str, *args: object) -> None:
        self.executions.append((query, args))

    async def fetch(self, query: str, *args: object) -> list[dict[str, str]]:
        self.fetches.append((query, args))
        return self.rows


class FakePool:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def acquire(self):
        pool = self

        class Acquisition:
            async def __aenter__(self):
                return pool.connection

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        return Acquisition()


def test_postgres_store_saves_user_and_assistant_messages_in_one_transaction():
    connection = FakeConnection()
    store = PostgresConversationStore(FakePool(connection))
    conversation_id = uuid4()

    asyncio.run(
        store.save_turn(
            conversation_id=conversation_id,
            user_message="Hello",
            assistant_message="Hi",
            provider="mock",
        )
    )

    assert connection.transaction_count == 1
    assert len(connection.executions) == 3
    assert "INSERT INTO conversations" in connection.executions[0][0]
    assert connection.executions[0][1] == (conversation_id,)
    assert "INSERT INTO messages" in connection.executions[1][0]
    assert connection.executions[1][1] == (conversation_id, "Hello")
    assert "INSERT INTO messages" in connection.executions[2][0]
    assert connection.executions[2][1] == (conversation_id, "Hi", "mock")


def test_postgres_store_loads_limited_history_in_chronological_order():
    connection = FakeConnection()
    connection.rows = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
    ]
    store = PostgresConversationStore(FakePool(connection))
    conversation_id = uuid4()

    history = asyncio.run(store.get_history(conversation_id, limit=20))

    assert history == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
    ]
    query, args = connection.fetches[0]
    assert "ORDER BY created_at DESC, id DESC" in query
    assert "ORDER BY created_at ASC, id ASC" in query
    assert args == (conversation_id, 20)
