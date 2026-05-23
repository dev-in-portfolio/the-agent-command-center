-- Continual Harness v5.0.0 operator mode.
-- Operator Mode is powerful, but not free range.
-- Arbitrary shell commands, arbitrary SQL, deploys, rollbacks, alerts,
-- and full fleet activation remain blocked.

create extension if not exists pgcrypto;

create or replace function continual_harness_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists continual_harness_sessions (
  session_id uuid primary key default gen_random_uuid(),
  component_name text not null default 'Continual Harness',
  component_version text not null default 'v5.0.0',
  mode text not null default 'operator_mode',
  status text not null default 'active',
  active_run_plan_id uuid,
  current_scope text,
  current_operation text,
  autostart_enabled boolean not null default true,
  operator_mode_enabled boolean not null default true,
  arbitrary_command_execution_enabled boolean not null default false,
  deploy_execution_enabled boolean not null default false,
  rollback_execution_enabled boolean not null default false,
  alert_sending_enabled boolean not null default false,
  started_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  stopped_at timestamptz,
  stopped_reason text,
  source text not null default 'continual_harness_operator_mode',
  constraint continual_harness_sessions_status_check check (status in ('active', 'paused', 'stopped', 'blocked', 'initialized')),
  constraint continual_harness_sessions_mode_check check (mode in ('operator_mode', 'autostart', 'manual')),
  constraint continual_harness_sessions_flags_check check (
    arbitrary_command_execution_enabled = false and
    deploy_execution_enabled = false and
    rollback_execution_enabled = false and
    alert_sending_enabled = false
  )
);

create unique index if not exists continual_harness_sessions_component_version_idx
  on continual_harness_sessions (component_name, component_version);

create trigger continual_harness_sessions_touch_updated_at
before update on continual_harness_sessions
for each row execute function continual_harness_touch_updated_at();

insert into continual_harness_sessions (
  component_name,
  component_version,
  mode,
  status,
  autostart_enabled,
  operator_mode_enabled,
  arbitrary_command_execution_enabled,
  deploy_execution_enabled,
  rollback_execution_enabled,
  alert_sending_enabled,
  source
) values (
  'Continual Harness',
  'v5.0.0',
  'operator_mode',
  'active',
  true,
  true,
  false,
  false,
  false,
  false,
  'continual_harness_operator_mode'
)
on conflict (component_name, component_version) do update set
  mode = excluded.mode,
  status = excluded.status,
  autostart_enabled = excluded.autostart_enabled,
  operator_mode_enabled = excluded.operator_mode_enabled,
  arbitrary_command_execution_enabled = excluded.arbitrary_command_execution_enabled,
  deploy_execution_enabled = excluded.deploy_execution_enabled,
  rollback_execution_enabled = excluded.rollback_execution_enabled,
  alert_sending_enabled = excluded.alert_sending_enabled,
  updated_at = now();

create table if not exists continual_harness_permissions (
  permission_id uuid primary key default gen_random_uuid(),
  scope text not null unique,
  status text not null default 'disabled',
  risk_level text not null default 'medium',
  approval_required boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'continual_harness_operator_mode',
  constraint continual_harness_permissions_status_check check (status in ('enabled', 'disabled', 'blocked'))
);

create trigger continual_harness_permissions_touch_updated_at
before update on continual_harness_permissions
for each row execute function continual_harness_touch_updated_at();

create table if not exists continual_harness_run_plans (
  run_plan_id uuid primary key default gen_random_uuid(),
  title text not null,
  requested_scope text not null,
  requested_operation text not null,
  plan_body jsonb not null default '{}'::jsonb,
  validation_status text not null default 'pending',
  approval_status text not null default 'pending',
  execution_status text not null default 'not_started',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'continual_harness_operator_mode',
  constraint continual_harness_run_plans_validation_check check (validation_status in ('pending', 'passed', 'failed', 'blocked')),
  constraint continual_harness_run_plans_approval_check check (approval_status in ('pending', 'approved', 'denied', 'not_required')),
  constraint continual_harness_run_plans_execution_check check (execution_status in ('not_started', 'completed', 'failed', 'blocked'))
);

create index if not exists continual_harness_run_plans_scope_idx on continual_harness_run_plans (requested_scope);
create index if not exists continual_harness_run_plans_operation_idx on continual_harness_run_plans (requested_operation);
create index if not exists continual_harness_run_plans_created_at_idx on continual_harness_run_plans (created_at desc);

create trigger continual_harness_run_plans_touch_updated_at
before update on continual_harness_run_plans
for each row execute function continual_harness_touch_updated_at();

create table if not exists continual_harness_allowlisted_operations (
  operation_id text primary key,
  display_name text not null,
  scope text not null,
  enabled boolean not null default false,
  risk_level text not null,
  dry_run_required boolean not null default true,
  approval_required boolean not null default true,
  command_execution_enabled boolean not null default false,
  deploy_execution_enabled boolean not null default false,
  rollback_execution_enabled boolean not null default false,
  alert_sending_enabled boolean not null default false,
  created_at timestamptz not null default now(),
  source text not null default 'continual_harness_operator_mode',
  constraint continual_harness_allowlisted_operations_flags_check check (
    command_execution_enabled = false and
    deploy_execution_enabled = false and
    rollback_execution_enabled = false and
    alert_sending_enabled = false
  )
);

create table if not exists continual_harness_readiness_notes (
  note_id uuid primary key default gen_random_uuid(),
  run_plan_id uuid references continual_harness_run_plans(run_plan_id) on delete set null,
  note_type text not null default 'readiness_note',
  note_body text not null,
  actor text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'continual_harness_operator_mode'
);

create index if not exists continual_harness_readiness_notes_created_at_idx on continual_harness_readiness_notes (created_at desc);
create index if not exists continual_harness_readiness_notes_run_plan_id_idx on continual_harness_readiness_notes (run_plan_id);

create trigger continual_harness_readiness_notes_touch_updated_at
before update on continual_harness_readiness_notes
for each row execute function continual_harness_touch_updated_at();

create table if not exists continual_harness_operator_events (
  event_id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  run_plan_id uuid references continual_harness_run_plans(run_plan_id) on delete set null,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'continual_harness_operator_mode'
);

create index if not exists continual_harness_operator_events_created_at_idx on continual_harness_operator_events (created_at desc);
create index if not exists continual_harness_operator_events_run_plan_id_idx on continual_harness_operator_events (run_plan_id);

insert into continual_harness_permissions (scope, status, risk_level, approval_required) values
  ('harness:read_status', 'enabled', 'low', true),
  ('harness:create_run_plan', 'enabled', 'medium', true),
  ('harness:validate_run_plan', 'enabled', 'medium', true),
  ('harness:write_audit_event', 'enabled', 'low', true),
  ('harness:create_readiness_note', 'enabled', 'low', true),
  ('harness:update_harness_session', 'enabled', 'medium', true),
  ('harness:run_allowlisted_check', 'enabled', 'low', true),
  ('harness:run_allowlisted_validator', 'enabled', 'medium', true),
  ('harness:request_department_gate_review', 'enabled', 'medium', true),
  ('harness:request_runtime_cohort_activation', 'enabled', 'high', true),
  ('harness:request_runtime_cohort_deactivation', 'enabled', 'high', true),
  ('harness:export_report', 'enabled', 'low', true),
  ('shell:execute', 'blocked', 'critical', true),
  ('sql:arbitrary', 'blocked', 'critical', true),
  ('deploy:execute', 'blocked', 'critical', true),
  ('rollback:execute', 'blocked', 'critical', true),
  ('alerts:send', 'blocked', 'critical', true),
  ('agents:activate_all', 'blocked', 'critical', true),
  ('agents:activate_47979', 'blocked', 'critical', true),
  ('external_api:mutate', 'blocked', 'critical', true),
  ('secrets:read', 'blocked', 'critical', true),
  ('env:read', 'blocked', 'critical', true),
  ('files:unrestricted_write', 'blocked', 'critical', true)
on conflict (scope) do update set
  status = excluded.status,
  risk_level = excluded.risk_level,
  approval_required = excluded.approval_required,
  updated_at = now();

insert into continual_harness_allowlisted_operations (
  operation_id,
  display_name,
  scope,
  enabled,
  risk_level,
  dry_run_required,
  approval_required,
  command_execution_enabled,
  deploy_execution_enabled,
  rollback_execution_enabled,
  alert_sending_enabled,
  source
) values
  ('run_mvp_validators', 'Run MVP Validators', 'harness:run_allowlisted_validator', true, 'medium', true, true, false, false, false, false, 'continual_harness_operator_mode'),
  ('create_readiness_note', 'Create Readiness Note', 'harness:create_readiness_note', true, 'low', true, true, false, false, false, false, 'continual_harness_operator_mode'),
  ('create_audit_event', 'Create Audit Event', 'harness:write_audit_event', true, 'low', true, true, false, false, false, false, 'continual_harness_operator_mode'),
  ('export_status_report', 'Export Status Report', 'harness:export_report', true, 'low', true, true, false, false, false, false, 'continual_harness_operator_mode'),
  ('request_department_gate_review', 'Request Department Gate Review', 'harness:request_department_gate_review', true, 'medium', true, true, false, false, false, false, 'continual_harness_operator_mode'),
  ('request_runtime_rollup', 'Request Runtime Rollup', 'harness:run_allowlisted_check', true, 'low', true, true, false, false, false, false, 'continual_harness_operator_mode'),
  ('request_harness_stop', 'Request Harness Stop', 'harness:update_harness_session', true, 'low', true, true, false, false, false, false, 'continual_harness_operator_mode')
on conflict (operation_id) do update set
  display_name = excluded.display_name,
  scope = excluded.scope,
  enabled = excluded.enabled,
  risk_level = excluded.risk_level,
  dry_run_required = excluded.dry_run_required,
  approval_required = excluded.approval_required,
  command_execution_enabled = excluded.command_execution_enabled,
  deploy_execution_enabled = excluded.deploy_execution_enabled,
  rollback_execution_enabled = excluded.rollback_execution_enabled,
  alert_sending_enabled = excluded.alert_sending_enabled;

insert into runtime_kernel_config (key, value) values
  ('continual_harness_operator_mode_ready', to_jsonb(true)),
  ('continual_harness_v5_incorporated', to_jsonb(true)),
  ('continual_harness_v5_autostart_enabled', to_jsonb(true)),
  ('continual_harness_v5_operator_mode_enabled', to_jsonb(true)),
  ('continual_harness_v5_persistent_daemon_enabled', to_jsonb(false)),
  ('continual_harness_v5_arbitrary_command_execution_enabled', to_jsonb(false)),
  ('continual_harness_v5_deploy_execution_enabled', to_jsonb(false)),
  ('continual_harness_v5_rollback_execution_enabled', to_jsonb(false)),
  ('continual_harness_v5_alert_sending_enabled', to_jsonb(false)),
  ('continual_harness_v5_command_center_takeover_enabled', to_jsonb(false))
on conflict (key) do update set
  value = excluded.value,
  updated_at = now();

alter table continual_harness_sessions enable row level security;
alter table continual_harness_permissions enable row level security;
alter table continual_harness_run_plans enable row level security;
alter table continual_harness_allowlisted_operations enable row level security;
alter table continual_harness_readiness_notes enable row level security;
alter table continual_harness_operator_events enable row level security;
