-- Initial J.A.R.V.I.S. durable-state schema (PostgreSQL 16+)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    provider TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_created
    ON messages (conversation_id, created_at);

CREATE TABLE IF NOT EXISTS approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    action_name TEXT NOT NULL,
    action_payload JSONB NOT NULL,
    payload_sha256 TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'executed')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    decided_at TIMESTAMPTZ,
    decided_by TEXT,
    executed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_approval_requests_pending
    ON approval_requests (status, expires_at)
    WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    trace_id UUID NOT NULL DEFAULT gen_random_uuid(),
    actor TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_audit_events_created ON audit_events (created_at);
