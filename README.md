# J.A.R.V.I.S. MVP — Milestone 1

A small, testable foundation for a hybrid personal AI assistant.

For the latest verified project status, next steps, and update history, see
[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md).
The V1 sprint scope, daily tasks, and completion criteria are tracked in
[SPRINT_PLAN.md](SPRINT_PLAN.md).

## Scope
- FastAPI health and chat endpoints
- Provider-agnostic LLM interface with deterministic mock and local Ollama providers
- Tool/action policy boundary with approval required for consequential actions
- PostgreSQL schema for conversations, messages, approval requests, and audit events
- Unit tests for action policy

The API persists successful chat turns and supplies up to the 20 most recent messages from that conversation as context to the model. It does not yet execute actions. It deliberately does **not** execute arbitrary shell commands, access private files, or connect to a real cloud LLM.

## Architecture
`Client -> FastAPI -> AssistantService -> LLMProvider`
`AssistantService -> ActionPolicy -> (deny | require approval | allow)`
The mock provider is the default. Set `LLM_PROVIDER=ollama` to use the local Ollama adapter. Successful user/assistant turns are stored in PostgreSQL; when an existing `conversation_id` is supplied, up to 20 recent messages are loaded and sent to the provider as context.

## Run locally
Requires Python 3.11+ and Docker Compose.

1. Create an environment file:
   ```bash
   cp .env.example .env
   ```
2. Start PostgreSQL:
   ```bash
   docker compose up -d postgres
   ```
3. Create a virtual environment and install:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # Linux/macOS: source .venv/bin/activate
   pip install -e ".[dev]"
   ```
4. Apply the initial schema:
   ```bash
   psql "$DATABASE_URL" -f migrations/001_initial.sql
   ```
   If `psql` is unavailable, use your preferred PostgreSQL client with the same SQL file.
5. Run the API:
   ```bash
   uvicorn jarvis_api.main:app --reload
   ```
6. Check `http://127.0.0.1:8000/health` and open `http://127.0.0.1:8000/docs`.

## Use local Ollama
Install and start Ollama, then download the configured model:
```bash
ollama pull qwen2.5:3b
```

In `.env`, set:
```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120
```

Restart the API after changing `.env`. Use `LLM_PROVIDER=mock` to switch back to the deterministic mock provider. Ollama must be running and the selected model must be available locally.

## Conversation persistence
The API stores each successful user/assistant turn in PostgreSQL. `conversation_id` must be a UUID; omit it to start a new conversation, or pass the returned ID to append another turn. For an existing conversation, the latest 20 messages are loaded in chronological order and sent to the model as context. If PostgreSQL is unavailable or the initial schema has not been applied, chat requests return HTTP 503 rather than silently dropping the conversation.

## Example chat request
```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, JARVIS"}'
```

## Security baseline
- Bind to localhost for development.
- Do not expose the API directly to the public internet.
- Do not put API keys in source control.
- Do not add generic shell/file execution tools.
- Any consequential tool must be registered with a strict schema and policy classification.
- Approval must be enforced by application code, not by an LLM prompt.
- Before production use, add authentication, request limits, secrets management, structured logging, and migrations tooling.

## Next milestone
Add a short-lived approval workflow with one harmless example tool, then add voice I/O as a separate client. See [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) for the latest verified status.
