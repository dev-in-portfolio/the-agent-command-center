-- MVP-53 runtime agent activation controller.
-- This migration defines persistence only. It does not enable mass activation or command execution.

create extension if not exists pgcrypto;

create table if not exists runtime_agents (
  agent_id text primary key,
  agent_name text not null,
  allowed_task text not null,
  execution_permissions text not null default 'none',
  external_api_permissions text not null default 'none',
  database_write_permissions text not null default 'audit_event_only',
  status text not null default 'inactive',
  activation_mode text not null default 'supervised_single_agent_test',
  is_supervised_test_agent boolean not null default false,
  kill_switch_visible boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_agents_status_check
    check (status in ('inactive', 'active', 'deactivated', 'blocked', 'disabled'))
);

create table if not exists agent_activation_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  agent_id text not null references runtime_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp53_runtime_agent_activation_controller'
);

create index if not exists runtime_agents_status_idx on runtime_agents (status);
create index if not exists agent_activation_events_created_at_idx on agent_activation_events (created_at desc);
create index if not exists agent_activation_events_agent_id_idx on agent_activation_events (agent_id);

insert into runtime_kernel_config (key, value)
values
  ('mass_activation_blocked', 'true'::jsonb),
  ('max_activation_batch_size', '1'::jsonb),
  ('kill_switch_visible', 'true'::jsonb),
  ('activation_mode', '"supervised_single_agent_test"'::jsonb),
  ('supervised_test_agent_id', '"mvp53_supervised_test_agent_001"'::jsonb),
  ('total_registered_agents', '47979'::jsonb),
  ('live_runtime_agents_enabled', '0'::jsonb)
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

insert into runtime_agents (
  agent_id,
  agent_name,
  allowed_task,
  execution_permissions,
  external_api_permissions,
  database_write_permissions,
  status,
  activation_mode,
  is_supervised_test_agent,
  kill_switch_visible
)
values (
  'mvp53_supervised_test_agent_001',
  'Supervised Test Agent 001',
  'create audit-only readiness note',
  'none',
  'none',
  'audit_event_only',
  'inactive',
  'supervised_single_agent_test',
  true,
  true
)
on conflict (agent_id) do update
set agent_name = excluded.agent_name,
    allowed_task = excluded.allowed_task,
    execution_permissions = excluded.execution_permissions,
    external_api_permissions = excluded.external_api_permissions,
    database_write_permissions = excluded.database_write_permissions,
    activation_mode = excluded.activation_mode,
    is_supervised_test_agent = excluded.is_supervised_test_agent,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

drop trigger if exists runtime_agents_touch_updated_at on runtime_agents;
create trigger runtime_agents_touch_updated_at
before update on runtime_agents
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_agents enable row level security;
alter table if exists agent_activation_events enable row level security;

create or replace function runtime_agent_activation_activate(
  p_agent_id text,
  p_actor text,
  p_reason text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent runtime_agents%rowtype;
  v_event agent_activation_events%rowtype;
  v_requested_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_reason text := nullif(btrim(p_reason), '');
  v_allowed_agent_id text := 'mvp53_supervised_test_agent_001';
begin
  if v_requested_agent_id is null then
    raise exception 'INVALID_PAYLOAD';
  end if;

  if v_requested_agent_id <> v_allowed_agent_id then
    insert into agent_activation_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      v_allowed_agent_id,
      v_actor,
      'ACTIVATION_BLOCKED',
      'Mass activation attempt blocked',
      jsonb_build_object(
        'requested_agent_id', v_requested_agent_id,
        'mass_activation_blocked', true,
        'max_activation_batch_size', 1,
        'reason', 'Only the supervised test agent may be activated.',
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp53_runtime_agent_activation_controller'
    )
    returning * into v_event;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'ACTIVATION_BLOCKED',
      'reason', 'Only the supervised test agent may be activated.',
      'agent', null,
      'event', to_jsonb(v_event)
    );
  end if;

  select * into v_agent
  from runtime_agents
  where agent_id = v_allowed_agent_id
  for update;

  if not found then
    insert into runtime_agents (
      agent_id,
      agent_name,
      allowed_task,
      execution_permissions,
      external_api_permissions,
      database_write_permissions,
      status,
      activation_mode,
      is_supervised_test_agent,
      kill_switch_visible
    )
    values (
      v_allowed_agent_id,
      'Supervised Test Agent 001',
      'create audit-only readiness note',
      'none',
      'none',
      'audit_event_only',
      'inactive',
      'supervised_single_agent_test',
      true,
      true
    )
    returning * into v_agent;
  end if;

  update runtime_agents
  set status = 'active'
  where agent_id = v_allowed_agent_id
  returning * into v_agent;

  update runtime_kernel_config
  set value = '1'::jsonb,
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  insert into agent_activation_events (
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_allowed_agent_id,
    v_actor,
    'AGENT_ACTIVATED',
    'Supervised test agent activated',
    jsonb_build_object(
      'reason', v_reason,
      'activation_mode', 'supervised_single_agent_test',
      'max_activation_batch_size', 1,
      'mass_activation_blocked', true,
      'live_runtime_agents_enabled', 1,
      'execution_permissions', 'none',
      'external_api_permissions', 'none',
      'database_write_permissions', 'audit_event_only'
    ),
    'mvp53_runtime_agent_activation_controller'
  )
  returning * into v_event;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agent', to_jsonb(v_agent),
    'event', to_jsonb(v_event),
    'backend_status', jsonb_build_object(
      'live_runtime_agents_enabled', 1,
      'mass_activation_blocked', true,
      'max_activation_batch_size', 1,
      'activation_mode', 'supervised_single_agent_test',
      'kill_switch_visible', true,
      'supervised_test_agent_id', v_allowed_agent_id
    )
  );
end;
$$;

create or replace function runtime_agent_activation_deactivate(
  p_agent_id text,
  p_actor text,
  p_reason text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent runtime_agents%rowtype;
  v_event agent_activation_events%rowtype;
  v_requested_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_reason text := nullif(btrim(p_reason), '');
  v_allowed_agent_id text := 'mvp53_supervised_test_agent_001';
begin
  if v_requested_agent_id is null then
    raise exception 'INVALID_PAYLOAD';
  end if;

  if v_requested_agent_id <> v_allowed_agent_id then
    insert into agent_activation_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      v_allowed_agent_id,
      v_actor,
      'DEACTIVATION_BLOCKED',
      'Mass deactivation attempt blocked',
      jsonb_build_object(
        'requested_agent_id', v_requested_agent_id,
        'mass_activation_blocked', true,
        'max_activation_batch_size', 1,
        'reason', 'Only the supervised test agent may be managed.'
      ),
      'mvp53_runtime_agent_activation_controller'
    )
    returning * into v_event;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'DEACTIVATION_BLOCKED',
      'reason', 'Only the supervised test agent may be managed.',
      'agent', null,
      'event', to_jsonb(v_event)
    );
  end if;

  select * into v_agent
  from runtime_agents
  where agent_id = v_allowed_agent_id
  for update;

  if not found then
    insert into runtime_agents (
      agent_id,
      agent_name,
      allowed_task,
      execution_permissions,
      external_api_permissions,
      database_write_permissions,
      status,
      activation_mode,
      is_supervised_test_agent,
      kill_switch_visible
    )
    values (
      v_allowed_agent_id,
      'Supervised Test Agent 001',
      'create audit-only readiness note',
      'none',
      'none',
      'audit_event_only',
      'inactive',
      'supervised_single_agent_test',
      true,
      true
    )
    returning * into v_agent;
  end if;

  update runtime_agents
  set status = 'inactive'
  where agent_id = v_allowed_agent_id
  returning * into v_agent;

  update runtime_kernel_config
  set value = '0'::jsonb,
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  insert into agent_activation_events (
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_allowed_agent_id,
    v_actor,
    'AGENT_DEACTIVATED',
    'Supervised test agent deactivated',
    jsonb_build_object(
      'reason', v_reason,
      'activation_mode', 'supervised_single_agent_test',
      'max_activation_batch_size', 1,
      'mass_activation_blocked', true,
      'live_runtime_agents_enabled', 0
    ),
    'mvp53_runtime_agent_activation_controller'
  )
  returning * into v_event;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agent', to_jsonb(v_agent),
    'event', to_jsonb(v_event),
    'backend_status', jsonb_build_object(
      'live_runtime_agents_enabled', 0,
      'mass_activation_blocked', true,
      'max_activation_batch_size', 1,
      'activation_mode', 'supervised_single_agent_test',
      'kill_switch_visible', true,
      'supervised_test_agent_id', v_allowed_agent_id
    )
  );
end;
$$;

comment on function runtime_agent_activation_activate(text, text, text) is
  'MVP-53 supervised single-agent activation only. It does not allow mass activation, command execution, deployment execution, rollback execution, or alert sending.';

comment on function runtime_agent_activation_deactivate(text, text, text) is
  'MVP-53 supervised single-agent deactivation only. It does not allow mass activation, command execution, deployment execution, rollback execution, or alert sending.';
