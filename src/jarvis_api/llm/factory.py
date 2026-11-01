from jarvis_api.config import Settings
from jarvis_api.llm.base import LLMProvider
from jarvis_api.llm.mock import MockLLMProvider
from jarvis_api.llm.providers.ollama import OllamaProvider


def create_llm_provider(config: Settings) -> LLMProvider:
    provider = config.llm_provider.strip().lower()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "ollama":
        return OllamaProvider(
            model=config.ollama_model,
            base_url=config.ollama_base_url,
            timeout=config.ollama_timeout,
        )
    raise ValueError(
        f"Unsupported LLM_PROVIDER '{config.llm_provider}'. Choose 'mock' or 'ollama'."
    )
