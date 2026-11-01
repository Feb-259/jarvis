# JARVIS --- Project Handoff for GitHub Copilot

Updated: 2026-10-28. Language: Vietnamese.

> For the latest verified implementation status and test results, read
> `PROJECT_PROGRESS.md` first. For the agreed V1 scope, sprint tasks, and
> acceptance criteria, read `SPRINT_PLAN.md`. This handoff contains
> longer-term project context and may include historical notes; always
> verify the actual workspace before acting.
>
> Copilot: inspect the actual workspace before editing. Some changes
> below were proposed in chat but have not been confirmed as applied. Do
> not assume the repo matches this document exactly.

## 1. Product goal

JARVIS is a personal AI assistant inspired by Iron Man's J.A.R.V.I.S.
Long-term direction: voice-first assistant (microphone → speech-to-text
→ LLM → text-to-speech), expandable tools/actions, with explicit user
approval before consequential actions. Build a working MVP
incrementally; do not over-engineer or rebuild from scratch.

## 2. Key decisions

-   LLM runs locally on the user's Windows PC for now; this superseded
    an earlier cloud-first idea.
-   Runtime: Ollama. Model successfully downloaded and run:
    `qwen2.5:3b`.
-   Ollama API: `http://localhost:11434`.
-   Model metadata: Qwen2 family, about 3.1B parameters, `Q4_K_M`,
    download about 1.93 GB, metadata context length 32768.
-   `curl.exe http://localhost:11434/api/tags` returned the model
    successfully. `ollama run qwen2.5:3b` generated Vietnamese text.
-   Provider-agnostic architecture is required: isolate Ollama behind
    `LLMProvider` adapter so local models/runtimes/cloud providers can
    be switched without rewriting assistant logic.
-   PC: Windows, 16 GB RAM, 1 TB storage, NVIDIA GTX 1660 Super with 6
    GB VRAM. GPU is recognized. Start with small models and measure
    performance; no hardware upgrade is planned now.
-   Existing stack: Python \>=3.11, FastAPI, Uvicorn, Pydantic v2,
    Pydantic Settings, pytest, httpx, Ruff. PostgreSQL is in
    configuration/planned architecture; do not assume it is connected or
    used by runtime.
-   Do not add dependencies/technologies without explaining why first.

## 3. Repository

Repo path: `D:\GIT\JARVIS`

Known structure (verify actual workspace):

``` text
JARVIS/
├── README.md
├── .env.example
├── pyproject.toml
├── docker-compose.yml
├── migrations/001_initial.sql
├── src/jarvis_api/
│   ├── __init__.py
│   ├── config.py
│   ├── schemas.py
│   ├── assistant.py
│   ├── main.py
│   └── llm/
│       ├── __init__.py
│       ├── base.py
│       ├── mock.py
│       └── providers/
│           ├── __init__.py
│           └── ollama.py
└── tests/
    ├── test_policy.py
    └── test_api.py
```

Possible stray root-level prototype files (`main.py`, `assistant.py`,
`config.py`, `jarvis.py`) were mentioned before. The application package
is under `src/jarvis_api/`; do not confuse root prototypes with package
files.

## 4. Existing interface

`src/jarvis_api/llm/base.py` as shared by user:

``` python
from typing import Protocol

class LLMProvider(Protocol):
    @property
    def name(self) -> str: ...

    async def generate_reply(self, message: str) -> str: ...
```

Keep this contract stable unless a concrete reason requires changing it.

`src/jarvis_api/llm/mock.py` as shared by user:

``` python
class MockLLMProvider:
    @property
    def name(self) -> str:
        return "mock"

    async def generate_reply(self, message: str) -> str:
        # Deterministic placeholder: replace with a real provider adapter in Milestone 2.
        return (
            "J.A.R.V.I.S. core is online. I received your message: "
            f"{message[:500]}. Real model integration is not configured yet."
        )
```

Keep MockLLMProvider for deterministic tests and environments without
Ollama.

## 5. Config and integration status

`src/jarvis_api/config.py` last shared by user, before a proposed
update:

``` python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "JARVIS"
    environment: str = "development"
    database_url: str = "postgresql://jarvis:jarvis_dev_only@localhost:5432/jarvis"
    llm_provider: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

The following config fields were proposed but user has not confirmed
applying them: - `ollama_model: str = "qwen2.5:3b"` -
`ollama_base_url: str = "http://localhost:11434"` -
`ollama_timeout: float = 120.0`

The user said they created `src/jarvis_api/llm/providers/__init__.py`
and `ollama.py`. The following adapter code was proposed; verify actual
file before editing:

``` python
import httpx

class OllamaProvider:
    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return f"ollama:{self._model}"

    async def generate_reply(self, message: str) -> str:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": message}],
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
        return data["message"]["content"].strip()
```

`httpx` is currently listed in the `dev` optional dependencies in
`pyproject.toml`, not main dependencies. Since the runtime adapter uses
it, explain the reason and propose moving it into main dependencies if
the app must run without dev extras. Do not install/update packages
without explaining first.

`src/jarvis_api/main.py` last shared before proposed Ollama integration:

``` python
from fastapi import FastAPI

from jarvis_api.assistant import AssistantService
from jarvis_api.config import settings
from jarvis_api.llm.mock import MockLLMProvider
from jarvis_api.schemas import ChatRequest, ChatResponse

provider = MockLLMProvider()
assistant = AssistantService(provider)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await assistant.chat(request.message, request.conversation_id)
```

A small provider factory selecting `mock` or `ollama` via
`settings.llm_provider` was proposed, but the user has not confirmed
updating `main.py`, `.env`, or running tests after those proposed
changes. Inspect current files first and preserve unrelated changes.

Proposed `.env` values for local mode:

``` dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120
```

For mock mode: `LLM_PROVIDER=mock`. Do not commit `.env` secrets; put
safe examples in `.env.example`.

## 6. Commands and known status

Run FastAPI from repo root with `.venv` active:

``` powershell
python -m uvicorn jarvis_api.main:app --reload
```

`python -m` uses the active interpreter; `uvicorn` is the ASGI server;
`jarvis_api.main:app` points to the `app` object; `--reload` reloads on
code changes.

Known URLs when server is running: - `http://127.0.0.1:8000/health` -
`http://127.0.0.1:8000/docs`

Test command:

``` powershell
python -m pytest
```

Before Ollama integration, 6 tests passed: 2 in `tests/test_api.py`, 4
in `tests/test_policy.py`. One Starlette deprecation warning was shown
about httpx and `starlette.testclient`; tests passed. Do not change
dependencies just to silence the warning without assessing need.

Ollama commands:

``` powershell
ollama list
ollama run qwen2.5:3b
curl.exe http://localhost:11434/api/tags
```

If `ollama serve` says port `127.0.0.1:11434` is already in use, check
`ollama list` or the API; the server may already be running in the
background.

## 7. Next steps

Read `PROJECT_PROGRESS.md` for the latest verified implementation status,
test results, and immediate next step. The initial local Ollama adapter and
conversation-context retrieval have been implemented; verify the workspace
before assuming external Ollama or PostgreSQL integration has been tested.

### Later milestones

-   Implement a short-lived approval workflow with one harmless example tool.
-   Then implement a single voice-first vertical slice: STT → assistant
    API/local LLM → TTS.
-   Add real tools/actions only when needed, with human approval for
    consequential actions.
-   Never claim the model can send messages, control apps, or perform
    actions unless those tools are actually implemented and authorized.

## 8. Working preferences

-   Communicate in Vietnamese.
-   User is a Data Engineer who understands logic/system thinking but is
    still learning Python syntax/ecosystem.
-   Explain terminal commands piece by piece, including what each part
    does and where to run it.
-   Work in small, sequential steps; prioritize a working product and
    learn as needed.
-   Preserve current code, tests, and dependencies. Never rebuild from
    scratch.
-   Explain why before adding dependencies or technologies.
-   Do not assume a command succeeded; ask for output when verification
    is needed.
-   Read the actual file and inspect diffs before editing; do not
    overwrite uncommitted work.
-   Avoid overwhelming the user with many unrelated concepts or steps.

## 9. Initial prompt to paste into GitHub Copilot Chat

Open `D:\GIT\JARVIS` in VS Code and paste:

> Read `JARVIS_PROJECT_HANDOFF.md` for project context. First, inspect
> the actual workspace only: git status/diff, repository tree,
> `pyproject.toml`, `src/jarvis_api/config.py`,
> `src/jarvis_api/main.py`, `src/jarvis_api/assistant.py`,
> `src/jarvis_api/llm/base.py`, `src/jarvis_api/llm/mock.py`,
> `src/jarvis_api/llm/providers/ollama.py`, and relevant tests.
>
> Do not edit files yet. Briefly report: (1) what of Milestone 1 is
> actually implemented, (2) what is missing or differs from this
> handoff, (3) concrete risks/bugs, and (4) the smallest recommended
> next change. Wait for my approval before editing.
>
> Do not rebuild the project, do not delete `MockLLMProvider`, do not
> add dependencies without explaining why first. Keep `LLMProvider`
> provider-agnostic and use local Ollama as the initial backend. Work
> incrementally, explain Python and terminal commands in Vietnamese, run
> tests after changes, and report actual results.
