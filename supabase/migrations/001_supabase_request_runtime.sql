-- Supabase / Postgres request runtime scaffold
-- MVP-3 only: schema scaffold, no automatic application.
-- RLS required before production writes.
-- auth.uid() binding required for write paths.
-- service role never exposed to browser code.
-- migrations must be reviewed and applied manually.

create table if not exists app_users (
  id uuid primary key,
  email text,
  role_name text not null default 'viewer',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists app_roles (
  id uuid primary key,
  role_name text not null unique,
  permissions jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create table if not exists requests (
  id uuid primary key,
  actor_id uuid references app_users(id),
  actor_role text not null default 'viewer',
  title text not null,
  intent text not null,
  requested_action text not null,
  lifecycle_state text not null default 'request_received',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists request_lifecycle_events (
  id uuid primary key,
  request_id uuid not null references requests(id) on delete cascade,
  lifecycle_state text not null,
  event_type text not null,
  details text not null default '',
  created_at timestamptz not null default now()
);
create table if not exists approvals (
  id uuid primary key,
  request_id uuid not null references requests(id) on delete cascade,
  approver_id uuid references app_users(id),
  approver_role text not null default 'approver',
  approval_state text not null,
  approval_scope text not null default 'request_review',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists audit_events (
  id uuid primary key,
  request_id uuid references requests(id) on delete cascade,
  actor_id uuid references app_users(id),
  actor_role text not null default 'viewer',
  event_type text not null,
  summary text not null default '',
  created_at timestamptz not null default now()
);
create table if not exists dry_run_results (
  id uuid primary key,
  request_id uuid not null references requests(id) on delete cascade,
  risk_classification text not null default 'low',
  dry_run_state text not null default 'blocked_before_execution',
  evidence jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create table if not exists no_go_flags (
  id uuid primary key,
  request_id uuid not null references requests(id) on delete cascade,
  flag_name text not null,
  flag_reason text not null default '',
  created_at timestamptz not null default now()
);
comment on table app_users is 'RLS required before production writes.';
comment on table requests is 'auth.uid() binding required for future write paths.';
comment on table approvals is 'Service role never exposed to browser code.';
comment on table audit_events is 'Production migrations are not auto-applied.';
