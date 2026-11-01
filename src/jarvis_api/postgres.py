from uuid import UUID

import asyncpg

from jarvis_api.llm.base import ChatMessage
from jarvis_api.storage import ConversationPersistenceError


class PostgresConversationStore:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    @classmethod
    async def connect(cls, database_url: str) -> "PostgresConversationStore":
        try:
            pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
        except (asyncpg.PostgresError, OSError, TimeoutError) as exc:
            raise ConversationPersistenceError(
                "Could not connect to the conversation database."
            ) from exc
        return cls(pool)

    async def close(self) -> None:
        await self._pool.close()

    async def get_history(
        self,
        conversation_id: UUID,
        limit: int,
    ) -> list[ChatMessage]:
        try:
            async with self._pool.acquire() as connection:
                rows = await connection.fetch(
                    """
                    SELECT role, content
                    FROM (
                        SELECT id, role, content, created_at
                        FROM messages
                        WHERE conversation_id = $1
                          AND role IN ('user', 'assistant')
                        ORDER BY created_at DESC, id DESC
                        LIMIT $2
                    ) recent_messages
                    ORDER BY created_at ASC, id ASC
                    """,
                    conversation_id,
                    limit,
                )
        except (asyncpg.PostgresError, OSError, TimeoutError) as exc:
            raise ConversationPersistenceError(
                "Could not load the conversation history."
            ) from exc
        return [
            {"role": row["role"], "content": row["content"]}
            for row in rows
        ]

    async def save_turn(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
        provider: str,
    ) -> None:
        try:
            async with self._pool.acquire() as connection, connection.transaction():
                await connection.execute(
                    """
                    INSERT INTO conversations (id)
                    VALUES ($1)
                    ON CONFLICT (id) DO UPDATE SET updated_at = now()
                    """,
                    conversation_id,
                )
                await connection.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content)
                    VALUES ($1, 'user', $2)
                    """,
                    conversation_id,
                    user_message,
                )
                await connection.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, provider)
                    VALUES ($1, 'assistant', $2, $3)
                    """,
                    conversation_id,
                    assistant_message,
                    provider,
                )
        except (asyncpg.PostgresError, OSError, TimeoutError) as exc:
            raise ConversationPersistenceError(
                "Could not save the conversation turn."
            ) from exc
