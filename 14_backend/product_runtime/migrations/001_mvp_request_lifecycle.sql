-- MVP-1 request lifecycle runtime migration scaffold.
-- This file is intentionally scaffold-only and must not be executed in this phase.

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    role_id TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    role_name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    title TEXT NOT NULL,
    intent TEXT NOT NULL,
    requested_action TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS request_lifecycle_events (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    event_type TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    approval_state TEXT NOT NULL,
    approval_reason TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_category TEXT NOT NULL,
    event_hash TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

CREATE TABLE IF NOT EXISTS dry_run_results (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    dry_run_plan_id TEXT NOT NULL,
    result_state TEXT NOT NULL,
    blocked_before_execution INTEGER NOT NULL DEFAULT 1,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

CREATE TABLE IF NOT EXISTS no_go_flags (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    flag_name TEXT NOT NULL,
    flag_reason TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);
