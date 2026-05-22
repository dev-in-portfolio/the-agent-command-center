-- MVP-54 ten-agent runtime squad.
-- This migration defines persistence only. It does not enable command execution, deploy execution, rollback execution, alert sending, or mass activation.

create extension if not exists pgcrypto;

create table if not exists runtime_kernel_config (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

create or replace function runtime_kernel_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists runtime_squad_agents (
  agent_id text primary key,
  agent_name text not null,
  allowed_task text not null default 'create heartbeat and readiness note only',
  execution_permissions text not null default 'none',
  external_api_permissions text not null default 'none',
  database_write_permissions text not null default 'audit_event_only',
  status text not null default 'inactive',
  activation_mode text not null default 'supervised_ten_agent_squad',
  is_supervised_test_agent boolean not null default true,
  kill_switch_visible boolean not null default true,
  squad_position integer not null,
  last_heartbeat_at timestamptz,
  last_readiness_note_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_squad_agents_status_check
    check (status in ('inactive', 'active', 'deactivated', 'blocked', 'disabled')),
  constraint runtime_squad_agents_position_check
    check (squad_position between 1 and 10),
  constraint runtime_squad_agents_position_unique
    unique (squad_position)
);

create table if not exists runtime_squad_audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  agent_id text references runtime_squad_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp54_ten_agent_runtime_squad'
);

create table if not exists agent_heartbeat_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  agent_id text not null references runtime_squad_agents(agent_id) on delete cascade,
  actor text,
  heartbeat_status text not null default 'healthy',
  heartbeat_note text,
  event_type text not null default 'AGENT_HEARTBEAT',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp54_ten_agent_runtime_squad'
);

create table if not exists agent_readiness_notes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  agent_id text not null references runtime_squad_agents(agent_id) on delete cascade,
  actor text,
  note_title text not null,
  note_body text not null,
  readiness_level text not null default 'green',
  event_type text not null default 'READINESS_NOTE_CREATED',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp54_ten_agent_runtime_squad'
);

create index if not exists runtime_squad_agents_status_idx on runtime_squad_agents (status);
create index if not exists runtime_squad_agents_position_idx on runtime_squad_agents (squad_position);
create index if not exists runtime_squad_audit_events_created_at_idx on runtime_squad_audit_events (created_at desc);
create index if not exists runtime_squad_audit_events_agent_id_idx on runtime_squad_audit_events (agent_id);
create index if not exists agent_heartbeat_events_created_at_idx on agent_heartbeat_events (created_at desc);
create index if not exists agent_heartbeat_events_agent_id_idx on agent_heartbeat_events (agent_id);
create index if not exists agent_readiness_notes_created_at_idx on agent_readiness_notes (created_at desc);
create index if not exists agent_readiness_notes_agent_id_idx on agent_readiness_notes (agent_id);

insert into runtime_kernel_config (key, value)
values
  ('runtime_squad_size', '10'::jsonb),
  ('max_activation_batch_size', '10'::jsonb),
  ('live_runtime_agents_enabled', '0'::jsonb),
  ('mass_activation_blocked', 'true'::jsonb),
  ('full_47979_activation_blocked', 'true'::jsonb),
  ('total_registered_agents', '47979'::jsonb),
  ('runtime_activation_started', 'false'::jsonb),
  ('command_execution_enabled', 'false'::jsonb),
  ('deploy_execution_enabled', 'false'::jsonb),
  ('rollback_execution_enabled', 'false'::jsonb),
  ('alert_sending_enabled', 'false'::jsonb),
  ('kill_switch_visible', 'true'::jsonb),
  ('activation_mode', '"supervised_ten_agent_squad"'::jsonb)
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

insert into runtime_squad_agents (
  agent_id,
  agent_name,
  allowed_task,
  execution_permissions,
  external_api_permissions,
  database_write_permissions,
  status,
  activation_mode,
  is_supervised_test_agent,
  kill_switch_visible,
  squad_position
)
values
  ('mvp54_runtime_squad_agent_001', 'Runtime Squad Agent 001', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 1),
  ('mvp54_runtime_squad_agent_002', 'Runtime Squad Agent 002', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 2),
  ('mvp54_runtime_squad_agent_003', 'Runtime Squad Agent 003', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 3),
  ('mvp54_runtime_squad_agent_004', 'Runtime Squad Agent 004', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 4),
  ('mvp54_runtime_squad_agent_005', 'Runtime Squad Agent 005', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 5),
  ('mvp54_runtime_squad_agent_006', 'Runtime Squad Agent 006', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 6),
  ('mvp54_runtime_squad_agent_007', 'Runtime Squad Agent 007', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 7),
  ('mvp54_runtime_squad_agent_008', 'Runtime Squad Agent 008', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 8),
  ('mvp54_runtime_squad_agent_009', 'Runtime Squad Agent 009', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 9),
  ('mvp54_runtime_squad_agent_010', 'Runtime Squad Agent 010', 'create heartbeat and readiness note only', 'none', 'none', 'audit_event_only', 'inactive', 'supervised_ten_agent_squad', true, true, 10)
on conflict (agent_id) do update
set agent_name = excluded.agent_name,
    allowed_task = excluded.allowed_task,
    execution_permissions = excluded.execution_permissions,
    external_api_permissions = excluded.external_api_permissions,
    database_write_permissions = excluded.database_write_permissions,
    activation_mode = excluded.activation_mode,
    is_supervised_test_agent = excluded.is_supervised_test_agent,
    kill_switch_visible = excluded.kill_switch_visible,
    squad_position = excluded.squad_position,
    updated_at = now();

drop trigger if exists runtime_squad_agents_touch_updated_at on runtime_squad_agents;
create trigger runtime_squad_agents_touch_updated_at
before update on runtime_squad_agents
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_squad_agents enable row level security;
alter table if exists runtime_squad_audit_events enable row level security;
alter table if exists agent_heartbeat_events enable row level security;
alter table if exists agent_readiness_notes enable row level security;

create or replace function runtime_squad_activate_agents(
  p_agent_ids text[],
  p_actor text,
  p_reason text default null,
  p_batch_size integer default null,
  p_activate_all boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_requested_ids text[];
  v_unknown_ids text[];
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_reason text := nullif(btrim(p_reason), '');
  v_limit integer := 10;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_activated_agents jsonb := '[]'::jsonb;
  v_audit_events jsonb := '[]'::jsonb;
  v_active_count integer := 0;
  v_audit runtime_squad_audit_events%rowtype;
begin
  select coalesce(array_agg(distinct trimmed order by trimmed), '{}'::text[])
  into v_requested_ids
  from (
    select nullif(btrim(item), '') as trimmed
    from unnest(coalesce(p_agent_ids, '{}'::text[])) item
  ) input
  where trimmed is not null;

  if v_effective_batch_size = 0 then
    v_effective_batch_size := coalesce(array_length(v_requested_ids, 1), 0);
  end if;

  if p_activate_all is true then
    v_blocked_reason := 'activate_all is blocked';
  elsif v_effective_batch_size > v_limit then
    v_blocked_reason := 'batch_size exceeds 10';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved squad agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      v_actor,
      'SQUAD_ACTIVATION_BLOCKED',
      'Squad activation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'mass_activation_blocked', true,
        'full_47979_activation_blocked', true
      ),
      'mvp54_ten_agent_runtime_squad'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'SQUAD_ACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_squad_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      v_actor,
      'UNKNOWN_AGENT_BLOCKED',
      'Unknown runtime squad agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 10-agent squad may be activated.'
      ),
      'mvp54_ten_agent_runtime_squad'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 10-agent squad may be activated.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with activated as (
    update runtime_squad_agents
    set status = 'active',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(activated)), '[]'::jsonb) into v_activated_agents
  from activated;

  with audit_rows as (
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      agent_id,
      v_actor,
      'SQUAD_AGENT_ACTIVATED',
      'Controlled runtime squad agent activated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_ten_agent_squad',
        'max_activation_batch_size', v_limit,
        'mass_activation_blocked', true,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp54_ten_agent_runtime_squad'
    from runtime_squad_agents
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(audit_rows)), '[]'::jsonb) into v_audit_events
  from audit_rows;

  select count(*) into v_active_count
  from runtime_squad_agents
  where status = 'active';

  update runtime_kernel_config
  set value = to_jsonb(v_active_count),
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_activated_agents,
    'audit_events', v_audit_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_squad_size', 10,
      'live_runtime_agents_enabled', v_active_count,
      'max_activation_batch_size', 10,
      'mass_activation_blocked', true,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'activation_mode', 'supervised_ten_agent_squad'
    )
  );
end;
$$;

create or replace function runtime_squad_deactivate_agents(
  p_agent_ids text[],
  p_actor text,
  p_reason text default null,
  p_batch_size integer default null,
  p_activate_all boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_requested_ids text[];
  v_unknown_ids text[];
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_reason text := nullif(btrim(p_reason), '');
  v_limit integer := 10;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_deactivated_agents jsonb := '[]'::jsonb;
  v_audit_events jsonb := '[]'::jsonb;
  v_active_count integer := 0;
  v_audit runtime_squad_audit_events%rowtype;
begin
  select coalesce(array_agg(distinct trimmed order by trimmed), '{}'::text[])
  into v_requested_ids
  from (
    select nullif(btrim(item), '') as trimmed
    from unnest(coalesce(p_agent_ids, '{}'::text[])) item
  ) input
  where trimmed is not null;

  if v_effective_batch_size = 0 then
    v_effective_batch_size := coalesce(array_length(v_requested_ids, 1), 0);
  end if;

  if p_activate_all is true then
    v_blocked_reason := 'activate_all is blocked';
  elsif v_effective_batch_size > v_limit then
    v_blocked_reason := 'batch_size exceeds 10';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved squad agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      v_actor,
      'SQUAD_DEACTIVATION_BLOCKED',
      'Squad deactivation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'mass_activation_blocked', true,
        'full_47979_activation_blocked', true
      ),
      'mvp54_ten_agent_runtime_squad'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'SQUAD_DEACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_squad_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      v_actor,
      'UNKNOWN_AGENT_BLOCKED',
      'Unknown runtime squad agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 10-agent squad may be managed.'
      ),
      'mvp54_ten_agent_runtime_squad'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 10-agent squad may be managed.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with deactivated as (
    update runtime_squad_agents
    set status = 'deactivated',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(deactivated)), '[]'::jsonb) into v_deactivated_agents
  from deactivated;

  with audit_rows as (
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      agent_id,
      v_actor,
      'SQUAD_AGENT_DEACTIVATED',
      'Controlled runtime squad agent deactivated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_ten_agent_squad',
        'max_activation_batch_size', v_limit,
        'mass_activation_blocked', true,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp54_ten_agent_runtime_squad'
    from runtime_squad_agents
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(audit_rows)), '[]'::jsonb) into v_audit_events
  from audit_rows;

  select count(*) into v_active_count
  from runtime_squad_agents
  where status = 'active';

  update runtime_kernel_config
  set value = to_jsonb(v_active_count),
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_deactivated_agents,
    'audit_events', v_audit_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_squad_size', 10,
      'live_runtime_agents_enabled', v_active_count,
      'max_activation_batch_size', 10,
      'mass_activation_blocked', true,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'activation_mode', 'supervised_ten_agent_squad'
    )
  );
end;
$$;

create or replace function runtime_squad_record_heartbeat(
  p_agent_id text,
  p_actor text,
  p_heartbeat_status text default 'healthy',
  p_heartbeat_note text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent runtime_squad_agents%rowtype;
  v_heartbeat agent_heartbeat_events%rowtype;
  v_audit runtime_squad_audit_events%rowtype;
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_status text := coalesce(nullif(btrim(p_heartbeat_status), ''), 'healthy');
  v_note text := nullif(btrim(p_heartbeat_note), '');
begin
  if v_agent_id is null then
    raise exception 'INVALID_PAYLOAD';
  end if;

  select *
  into v_agent
  from runtime_squad_agents
  where agent_id = v_agent_id;

  if not found then
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      v_actor,
      'HEARTBEAT_BLOCKED',
      'Heartbeat blocked for unknown squad agent',
      jsonb_build_object('agent_id', v_agent_id, 'reason', 'Unknown agent ID.'),
      'mvp54_ten_agent_runtime_squad'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 10-agent squad may send heartbeats.',
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  update runtime_squad_agents
  set last_heartbeat_at = now(),
      updated_at = now()
  where agent_id = v_agent_id
  returning * into v_agent;

  insert into agent_heartbeat_events (
    agent_id,
    actor,
    heartbeat_status,
    heartbeat_note,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_agent_id,
    v_actor,
    v_status,
    v_note,
    'AGENT_HEARTBEAT',
    'Controlled squad heartbeat recorded',
    jsonb_build_object(
      'heartbeat_status', v_status,
      'heartbeat_note', v_note,
      'allowed_task', 'create heartbeat and readiness note only',
      'execution_permissions', 'none',
      'external_api_permissions', 'none',
      'database_write_permissions', 'audit_event_only'
    ),
    'mvp54_ten_agent_runtime_squad'
  )
  returning * into v_heartbeat;

  insert into runtime_squad_audit_events (
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_agent_id,
    v_actor,
    'AGENT_HEARTBEAT',
    'Controlled squad heartbeat recorded',
    jsonb_build_object(
      'heartbeat_status', v_status,
      'heartbeat_note', v_note,
      'last_heartbeat_at', now(),
      'allowed_task', 'create heartbeat and readiness note only'
    ),
    'mvp54_ten_agent_runtime_squad'
  )
  returning * into v_audit;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agent', to_jsonb(v_agent),
    'heartbeat', to_jsonb(v_heartbeat),
    'audit_event', to_jsonb(v_audit),
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_squad_size', 10,
      'live_runtime_agents_enabled', (
        select count(*) from runtime_squad_agents where status = 'active'
      ),
      'max_activation_batch_size', 10,
      'mass_activation_blocked', true,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'activation_mode', 'supervised_ten_agent_squad'
    )
  );
end;
$$;

create or replace function runtime_squad_create_readiness_note(
  p_agent_id text,
  p_actor text,
  p_note_title text,
  p_note_body text,
  p_readiness_level text default 'green'
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent runtime_squad_agents%rowtype;
  v_note agent_readiness_notes%rowtype;
  v_audit runtime_squad_audit_events%rowtype;
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_note_title text := nullif(btrim(p_note_title), '');
  v_note_body text := nullif(btrim(p_note_body), '');
  v_readiness_level text := coalesce(nullif(btrim(p_readiness_level), ''), 'green');
begin
  if v_agent_id is null or v_note_title is null or v_note_body is null then
    raise exception 'INVALID_PAYLOAD';
  end if;

  select *
  into v_agent
  from runtime_squad_agents
  where agent_id = v_agent_id;

  if not found then
    insert into runtime_squad_audit_events (
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      v_actor,
      'READINESS_NOTE_BLOCKED',
      'Readiness note blocked for unknown squad agent',
      jsonb_build_object('agent_id', v_agent_id, 'reason', 'Unknown agent ID.'),
      'mvp54_ten_agent_runtime_squad'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 10-agent squad may create readiness notes.',
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  update runtime_squad_agents
  set last_readiness_note_at = now(),
      updated_at = now()
  where agent_id = v_agent_id
  returning * into v_agent;

  insert into agent_readiness_notes (
    agent_id,
    actor,
    note_title,
    note_body,
    readiness_level,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_agent_id,
    v_actor,
    v_note_title,
    v_note_body,
    v_readiness_level,
    'READINESS_NOTE_CREATED',
    'Controlled squad readiness note recorded',
    jsonb_build_object(
      'readiness_level', v_readiness_level,
      'note_title', v_note_title,
      'note_body', v_note_body,
      'allowed_task', 'create heartbeat and readiness note only'
    ),
    'mvp54_ten_agent_runtime_squad'
  )
  returning * into v_note;

  insert into runtime_squad_audit_events (
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_agent_id,
    v_actor,
    'READINESS_NOTE_CREATED',
    'Controlled squad readiness note recorded',
    jsonb_build_object(
      'readiness_level', v_readiness_level,
      'note_title', v_note_title,
      'last_readiness_note_at', now(),
      'allowed_task', 'create heartbeat and readiness note only'
    ),
    'mvp54_ten_agent_runtime_squad'
  )
  returning * into v_audit;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agent', to_jsonb(v_agent),
    'readiness_note', to_jsonb(v_note),
    'audit_event', to_jsonb(v_audit),
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_squad_size', 10,
      'live_runtime_agents_enabled', (
        select count(*) from runtime_squad_agents where status = 'active'
      ),
      'max_activation_batch_size', 10,
      'mass_activation_blocked', true,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'activation_mode', 'supervised_ten_agent_squad'
    )
  );
end;
$$;
