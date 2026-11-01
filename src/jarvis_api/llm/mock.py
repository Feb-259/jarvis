from collections.abc import Sequence

from jarvis_api.llm.base import ChatMessage


class MockLLMProvider:
    @property
    def name(self) -> str:
        return "mock"

    async def generate_reply(
        self,
        message: str,
        history: Sequence[ChatMessage] = (),
    ) -> str:
        # Deterministic placeholder: replace with a real provider adapter in Milestone 2.
        return (
            "J.A.R.V.I.S. core is online. I received your message: "
            f"{message[:500]}. Real model integration is not configured yet."
        )
