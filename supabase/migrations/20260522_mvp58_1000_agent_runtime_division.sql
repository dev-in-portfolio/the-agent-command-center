-- MVP-58 1,000-agent runtime division.
-- This migration defines persistence only. It does not enable command execution, deploy execution, rollback execution, alert sending, or arbitrary activation beyond the approved 1,000-agent division.
-- Approved division IDs: mvp58_division_agent_0001 through mvp58_division_agent_1000.
-- Subdivisions: intake_subdivision through reporting_subdivision across 10 subdivisions.
-- Lanes: intake_lane_001 through reporting_lane_010 across 100 lanes.
-- Blocked markers: UNKNOWN_AGENT_BLOCKED, NON_DIVISION_AGENT_BLOCKED, full 47,979 activation is blocked, and activate_all is blocked.

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

create table if not exists runtime_division_subdivisions (
  subdivision_key text primary key,
  subdivision_name text not null,
  subdivision_order integer not null unique,
  subdivision_description text not null default '',
  allowed_task text not null default 'send heartbeat and create readiness note only',
  status text not null default 'inactive',
  kill_switch_visible boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_division_subdivisions_status_check
    check (status in ('inactive', 'active', 'mixed', 'disabled'))
);

create table if not exists runtime_division_lanes (
  lane_key text primary key,
  lane_name text not null,
  lane_order integer not null unique,
  subdivision_key text not null references runtime_division_subdivisions(subdivision_key) on delete cascade,
  lane_index integer not null,
  lane_description text not null default '',
  allowed_task text not null default 'send heartbeat and create readiness note only',
  status text not null default 'inactive',
  kill_switch_visible boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_division_lanes_status_check
    check (status in ('inactive', 'active', 'mixed', 'disabled')),
  constraint runtime_division_lanes_lane_index_check
    check (lane_index between 1 and 10),
  constraint runtime_division_lanes_subdivision_lane_unique
    unique (subdivision_key, lane_index)
);

create table if not exists runtime_division_agents (
  agent_id text primary key,
  agent_name text not null,
  subdivision_key text not null references runtime_division_subdivisions(subdivision_key) on delete cascade,
  lane_key text not null references runtime_division_lanes(lane_key) on delete cascade,
  subdivision_position integer not null,
  lane_position integer not null,
  allowed_task text not null default 'send heartbeat and create readiness note only',
  execution_permissions text not null default 'none',
  external_api_permissions text not null default 'none',
  database_write_permissions text not null default 'audit_event_only',
  status text not null default 'inactive',
  is_supervised_division_agent boolean not null default true,
  kill_switch_visible boolean not null default true,
  last_heartbeat_at timestamptz,
  last_readiness_note_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_division_agents_status_check
    check (status in ('inactive', 'active', 'deactivated', 'blocked', 'disabled')),
  constraint runtime_division_agents_subdivision_position_check
    check (subdivision_position between 1 and 100),
  constraint runtime_division_agents_lane_position_check
    check (lane_position between 1 and 10),
  constraint runtime_division_agents_lane_position_unique
    unique (lane_key, lane_position)
);

create table if not exists runtime_division_activation_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  subdivision_key text references runtime_division_subdivisions(subdivision_key) on delete cascade,
  lane_key text references runtime_division_lanes(lane_key) on delete cascade,
  agent_id text references runtime_division_agents(agent_id) on delete cascade,
  chunk_number integer not null default 1,
  chunk_size integer not null default 0,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp58_1000_agent_runtime_division'
);

create table if not exists division_heartbeat_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  subdivision_key text references runtime_division_subdivisions(subdivision_key) on delete cascade,
  lane_key text references runtime_division_lanes(lane_key) on delete cascade,
  agent_id text references runtime_division_agents(agent_id) on delete cascade,
  scope text not null default 'division',
  heartbeat_status text not null default 'healthy',
  heartbeat_note text,
  target_agent_count integer not null default 0,
  event_type text not null default 'DIVISION_HEARTBEAT',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp58_1000_agent_runtime_division'
);

create table if not exists division_readiness_notes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  subdivision_key text references runtime_division_subdivisions(subdivision_key) on delete cascade,
  lane_key text references runtime_division_lanes(lane_key) on delete cascade,
  agent_id text references runtime_division_agents(agent_id) on delete cascade,
  scope text not null default 'division',
  note_title text not null,
  note_body text not null,
  readiness_level text not null default 'green',
  target_agent_count integer not null default 0,
  event_type text not null default 'DIVISION_READINESS_NOTE_CREATED',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp58_1000_agent_runtime_division'
);

create table if not exists runtime_division_audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  subdivision_key text references runtime_division_subdivisions(subdivision_key) on delete cascade,
  lane_key text references runtime_division_lanes(lane_key) on delete cascade,
  agent_id text references runtime_division_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp58_1000_agent_runtime_division'
);

create index if not exists runtime_division_lanes_subdivision_key_idx on runtime_division_lanes (subdivision_key);
create index if not exists runtime_division_agents_subdivision_key_idx on runtime_division_agents (subdivision_key);
create index if not exists runtime_division_agents_lane_key_idx on runtime_division_agents (lane_key);
create index if not exists runtime_division_agents_status_idx on runtime_division_agents (status);
create index if not exists runtime_division_activation_events_created_at_idx on runtime_division_activation_events (created_at desc);
create index if not exists runtime_division_activation_events_lane_key_idx on runtime_division_activation_events (lane_key);
create index if not exists division_heartbeat_events_created_at_idx on division_heartbeat_events (created_at desc);
create index if not exists division_heartbeat_events_lane_key_idx on division_heartbeat_events (lane_key);
create index if not exists division_readiness_notes_created_at_idx on division_readiness_notes (created_at desc);
create index if not exists division_readiness_notes_lane_key_idx on division_readiness_notes (lane_key);
create index if not exists runtime_division_audit_events_created_at_idx on runtime_division_audit_events (created_at desc);
create index if not exists runtime_division_audit_events_lane_key_idx on runtime_division_audit_events (lane_key);

with subdivision_groups(prefix, display_name, subdivision_description, subdivision_order) as (
  values
    ('intake', 'Intake', 'Controlled intake and triage subdivision.', 1),
    ('validation', 'Validation', 'Controlled validation and readiness subdivision.', 2),
    ('audit', 'Audit', 'Audit visibility and recordkeeping subdivision.', 3),
    ('approval', 'Approval', 'Approval review and decision subdivision.', 4),
    ('dry_run', 'Dry Run', 'Dry-run and preview subdivision.', 5),
    ('monitoring', 'Monitoring', 'Monitoring and readiness tracking subdivision.', 6),
    ('safety', 'Safety', 'Safety boundary and kill-switch subdivision.', 7),
    ('registry', 'Registry', 'Registry and roster verification subdivision.', 8),
    ('review', 'Review', 'Human review and QA subdivision.', 9),
    ('reporting', 'Reporting', 'Reporting and summary subdivision.', 10)
), subdivision_rows as (
  select
    format('%s_subdivision', prefix) as subdivision_key,
    format('%s Subdivision', display_name) as subdivision_name,
    subdivision_order,
    subdivision_description,
    'send heartbeat and create readiness note only' as allowed_task,
    'inactive' as status,
    true as kill_switch_visible
  from subdivision_groups
)
insert into runtime_division_subdivisions (
  subdivision_key,
  subdivision_name,
  subdivision_order,
  subdivision_description,
  allowed_task,
  status,
  kill_switch_visible
)
select * from subdivision_rows
on conflict (subdivision_key) do update
set subdivision_name = excluded.subdivision_name,
    subdivision_order = excluded.subdivision_order,
    subdivision_description = excluded.subdivision_description,
    allowed_task = excluded.allowed_task,
    status = excluded.status,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

with lane_groups(prefix, display_name, lane_description, subdivision_order) as (
  values
    ('intake', 'Intake', 'Controlled intake and triage lane.', 1),
    ('validation', 'Validation', 'Controlled validation and readiness lane.', 2),
    ('audit', 'Audit', 'Audit visibility and recordkeeping lane.', 3),
    ('approval', 'Approval', 'Approval review and decision lane.', 4),
    ('dry_run', 'Dry Run', 'Dry-run and preview lane.', 5),
    ('monitoring', 'Monitoring', 'Monitoring and readiness tracking lane.', 6),
    ('safety', 'Safety', 'Safety boundary and kill-switch lane.', 7),
    ('registry', 'Registry', 'Registry and roster verification lane.', 8),
    ('review', 'Review', 'Human review and QA lane.', 9),
    ('reporting', 'Reporting', 'Reporting and summary lane.', 10)
), lane_rows as (
  select
    format('%s_lane_%s', prefix, lpad(gs::text, 3, '0')) as lane_key,
    format('%s Lane %s', display_name, lpad(gs::text, 3, '0')) as lane_name,
    ((subdivision_order - 1) * 10) + gs as lane_order,
    format('%s_subdivision', prefix) as subdivision_key,
    gs as lane_index,
    lane_description,
    'send heartbeat and create readiness note only' as allowed_task,
    'inactive' as status,
    true as kill_switch_visible
  from lane_groups
  cross join generate_series(1, 10) as gs
)
insert into runtime_division_lanes (
  lane_key,
  lane_name,
  lane_order,
  subdivision_key,
  lane_index,
  lane_description,
  allowed_task,
  status,
  kill_switch_visible
)
select * from lane_rows
on conflict (lane_key) do update
set lane_name = excluded.lane_name,
    lane_order = excluded.lane_order,
    subdivision_key = excluded.subdivision_key,
    lane_index = excluded.lane_index,
    lane_description = excluded.lane_description,
    allowed_task = excluded.allowed_task,
    status = excluded.status,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

insert into runtime_division_agents (
  agent_id,
  agent_name,
  subdivision_key,
  lane_key,
  subdivision_position,
  lane_position,
  allowed_task,
  execution_permissions,
  external_api_permissions,
  database_write_permissions,
  status,
  is_supervised_division_agent,
  kill_switch_visible
)
select
  format('mvp58_division_agent_%s', lpad(gs::text, 4, '0')) as agent_id,
  format('Division Agent %s', lpad(gs::text, 4, '0')) as agent_name,
  lane.subdivision_key,
  lane.lane_key,
  ((gs - 1) % 100) + 1 as subdivision_position,
  ((gs - 1) % 10) + 1 as lane_position,
  'send heartbeat and create readiness note only',
  'none',
  'none',
  'audit_event_only',
  'inactive',
  true,
  true
from generate_series(1, 1000) as gs
join runtime_division_lanes lane
  on lane.lane_order = ((gs - 1) / 10) + 1
on conflict (agent_id) do update
set agent_name = excluded.agent_name,
    subdivision_key = excluded.subdivision_key,
    lane_key = excluded.lane_key,
    subdivision_position = excluded.subdivision_position,
    lane_position = excluded.lane_position,
    allowed_task = excluded.allowed_task,
    execution_permissions = excluded.execution_permissions,
    external_api_permissions = excluded.external_api_permissions,
    database_write_permissions = excluded.database_write_permissions,
    status = excluded.status,
    is_supervised_division_agent = excluded.is_supervised_division_agent,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

drop trigger if exists runtime_division_subdivisions_touch_updated_at on runtime_division_subdivisions;
create trigger runtime_division_subdivisions_touch_updated_at
before update on runtime_division_subdivisions
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_division_lanes_touch_updated_at on runtime_division_lanes;
create trigger runtime_division_lanes_touch_updated_at
before update on runtime_division_lanes
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_division_agents_touch_updated_at on runtime_division_agents;
create trigger runtime_division_agents_touch_updated_at
before update on runtime_division_agents
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_division_subdivisions enable row level security;
alter table if exists runtime_division_lanes enable row level security;
alter table if exists runtime_division_agents enable row level security;
alter table if exists runtime_division_activation_events enable row level security;
alter table if exists division_heartbeat_events enable row level security;
alter table if exists division_readiness_notes enable row level security;
alter table if exists runtime_division_audit_events enable row level security;

insert into runtime_kernel_config (key, value)
values
  ('division_runtime_size', '1000'::jsonb),
  ('division_max_activation_batch_size', '1000'::jsonb),
  ('division_max_operation_chunk_size', '100'::jsonb),
  ('division_live_runtime_agents_enabled', '0'::jsonb),
  ('division_runtime_activation_started', 'false'::jsonb),
  ('division_full_47979_activation_blocked', 'true'::jsonb),
  ('division_total_registered_agents', '47979'::jsonb),
  ('division_command_execution_enabled', 'false'::jsonb),
  ('division_deploy_execution_enabled', 'false'::jsonb),
  ('division_rollback_execution_enabled', 'false'::jsonb),
  ('division_alert_sending_enabled', 'false'::jsonb),
  ('division_kill_switch_visible', 'true'::jsonb),
  ('division_active_subdivisions_count', '0'::jsonb),
  ('division_inactive_subdivisions_count', '10'::jsonb),
  ('division_active_lanes_count', '0'::jsonb),
  ('division_inactive_lanes_count', '100'::jsonb),
  ('division_activation_mode', '"supervised_thousand_agent_division"'::jsonb),
  ('division_heartbeat_event_count', '0'::jsonb),
  ('division_readiness_note_count', '0'::jsonb),
  ('division_activation_event_count', '0'::jsonb),
  ('division_audit_event_count', '0'::jsonb),
  (
    'division_health_rollup',
    jsonb_build_object(
      'division_health', 'inactive',
      'active_agents', 0,
      'inactive_agents', 1000,
      'active_subdivisions', 0,
      'inactive_subdivisions', 10,
      'active_lanes', 0,
      'inactive_lanes', 100,
      'heartbeat_event_count', 0,
      'readiness_note_count', 0,
      'activation_event_count', 0,
      'audit_event_count', 0,
      'runtime_division_size', 1000,
      'total_registered_agents', 47979
    )
  )
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

create or replace function runtime_division_subdivision_lane_keys(
  p_subdivision_key text
)
returns text[]
language plpgsql
security definer
set search_path = public
as $$
declare
  v_subdivision_key text := nullif(btrim(p_subdivision_key), '');
  v_lane_keys text[];
begin
  if v_subdivision_key is null then
    return '{}'::text[];
  end if;

  select array_agg(lane_key order by lane_order)
  into v_lane_keys
  from runtime_division_lanes
  where subdivision_key = v_subdivision_key;

  return coalesce(v_lane_keys, '{}'::text[]);
end;
$$;

create or replace function runtime_division_lane_agent_ids(
  p_lane_key text
)
returns text[]
language plpgsql
security definer
set search_path = public
as $$
declare
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_ids text[];
begin
  if v_lane_key is null then
    return '{}'::text[];
  end if;

  select array_agg(agent_id order by lane_position)
  into v_agent_ids
  from runtime_division_agents
  where lane_key = v_lane_key;

  return coalesce(v_agent_ids, '{}'::text[]);
end;
$$;

create or replace function runtime_division_subdivision_agent_ids(
  p_subdivision_key text
)
returns text[]
language plpgsql
security definer
set search_path = public
as $$
declare
  v_subdivision_key text := nullif(btrim(p_subdivision_key), '');
  v_agent_ids text[];
begin
  if v_subdivision_key is null then
    return '{}'::text[];
  end if;

  select array_agg(agent_id order by subdivision_position, lane_position)
  into v_agent_ids
  from runtime_division_agents
  where subdivision_key = v_subdivision_key;

  return coalesce(v_agent_ids, '{}'::text[]);
end;
$$;

create or replace function runtime_division_division_agent_ids()
returns text[]
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent_ids text[];
begin
  select array_agg(agent_id order by agent_id)
  into v_agent_ids
  from runtime_division_agents;

  return coalesce(v_agent_ids, '{}'::text[]);
end;
$$;

create or replace function runtime_division_sync_rollups()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_active_count integer := 0;
  v_active_lane_count integer := 0;
  v_active_subdivision_count integer := 0;
  v_heartbeat_count integer := 0;
  v_readiness_note_count integer := 0;
  v_activation_event_count integer := 0;
  v_audit_event_count integer := 0;
  v_division_health text := 'inactive';
  v_rollup jsonb := '{}'::jsonb;
begin
  select count(*) into v_active_count
  from runtime_division_agents
  where status = 'active';

  select count(distinct lane_key) into v_active_lane_count
  from runtime_division_agents
  where status = 'active';

  select count(distinct subdivision_key) into v_active_subdivision_count
  from runtime_division_agents
  where status = 'active';

  select count(*) into v_heartbeat_count from division_heartbeat_events;
  select count(*) into v_readiness_note_count from division_readiness_notes;
  select count(*) into v_activation_event_count from runtime_division_activation_events;
  select count(*) into v_audit_event_count from runtime_division_audit_events;

  if v_active_count = 0 then
    v_division_health := 'inactive';
  elsif v_active_count >= 1000 and v_active_lane_count >= 100 and v_active_subdivision_count >= 10 then
    v_division_health := 'healthy';
  else
    v_division_health := 'partial';
  end if;

  insert into runtime_kernel_config (key, value)
  values ('division_live_runtime_agents_enabled', to_jsonb(v_active_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_active_subdivisions_count', to_jsonb(v_active_subdivision_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_inactive_subdivisions_count', to_jsonb(greatest(10 - v_active_subdivision_count, 0)))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_active_lanes_count', to_jsonb(v_active_lane_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_inactive_lanes_count', to_jsonb(greatest(100 - v_active_lane_count, 0)))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_heartbeat_event_count', to_jsonb(v_heartbeat_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_readiness_note_count', to_jsonb(v_readiness_note_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_activation_event_count', to_jsonb(v_activation_event_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  insert into runtime_kernel_config (key, value)
  values ('division_audit_event_count', to_jsonb(v_audit_event_count))
  on conflict (key) do update set value = excluded.value, updated_at = now();

  v_rollup := jsonb_build_object(
    'division_health', v_division_health,
    'active_agents', v_active_count,
    'inactive_agents', greatest(1000 - v_active_count, 0),
    'active_subdivisions', v_active_subdivision_count,
    'inactive_subdivisions', greatest(10 - v_active_subdivision_count, 0),
    'active_lanes', v_active_lane_count,
    'inactive_lanes', greatest(100 - v_active_lane_count, 0),
    'heartbeat_event_count', v_heartbeat_count,
    'readiness_note_count', v_readiness_note_count,
    'activation_event_count', v_activation_event_count,
    'audit_event_count', v_audit_event_count,
    'runtime_division_size', 1000,
    'total_registered_agents', 47979
  );

  insert into runtime_kernel_config (key, value)
  values ('division_health_rollup', v_rollup)
  on conflict (key) do update set value = excluded.value, updated_at = now();

  return v_rollup;
end;
$$;

create or replace function runtime_division_apply_agent_state(
  p_operation text,
  p_scope text,
  p_scope_key text default null,
  p_agent_ids text[] default null,
  p_actor text default null,
  p_reason text default null,
  p_batch_size integer default null,
  p_chunk_size integer default 100,
  p_activate_all boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_operation text := lower(coalesce(nullif(btrim(p_operation), ''), 'activate'));
  v_scope text := lower(coalesce(nullif(btrim(p_scope), ''), 'division'));
  v_scope_key text := nullif(btrim(p_scope_key), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_reason text := nullif(btrim(p_reason), '');
  v_limit integer := 1000;
  v_chunk_limit integer := 100;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_effective_chunk_size integer := coalesce(p_chunk_size, 0);
  v_requested_ids text[];
  v_scope_ids text[];
  v_unknown_ids text[];
  v_out_of_scope_ids text[];
  v_blocked_reason text := null;
  v_target_status text := case when v_operation = 'deactivate' then 'deactivated' else 'active' end;
  v_event_type text := case when v_operation = 'deactivate' then 'DIVISION_AGENT_DEACTIVATED' else 'DIVISION_AGENT_ACTIVATED' end;
  v_event_summary text := case when v_operation = 'deactivate' then 'Controlled division agent deactivated' else 'Controlled division agent activated' end;
  v_blocked_event_type text := case when v_operation = 'deactivate' then 'DIVISION_DEACTIVATION_BLOCKED' else 'DIVISION_ACTIVATION_BLOCKED' end;
  v_event_scope text := v_scope;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_audit_events jsonb := '[]'::jsonb;
  v_rollup jsonb := '{}'::jsonb;
  v_chunk_index integer := 0;
  v_chunk_start integer;
  v_chunk_end integer;
  v_chunk_ids text[];
  v_chunk_agents jsonb := '[]'::jsonb;
  v_chunk_events jsonb := '[]'::jsonb;
  v_audit runtime_division_audit_events%rowtype;
begin
  if v_operation not in ('activate', 'deactivate') then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_OPERATION');
  end if;

  select coalesce(array_agg(distinct trimmed order by trimmed), '{}'::text[])
  into v_requested_ids
  from (
    select nullif(btrim(item), '') as trimmed
    from unnest(coalesce(p_agent_ids, '{}'::text[])) item
  ) input
  where trimmed is not null;

  if v_effective_chunk_size = 0 then
    v_effective_chunk_size := 100;
  end if;

  if v_effective_batch_size = 0 then
    if array_length(v_requested_ids, 1) is not null then
      v_effective_batch_size := array_length(v_requested_ids, 1);
    elsif v_scope = 'division' then
      v_effective_batch_size := 1000;
    elsif v_scope = 'subdivision' then
      v_effective_batch_size := coalesce(array_length(runtime_division_subdivision_agent_ids(v_scope_key), 1), 0);
    elsif v_scope = 'lane' then
      v_effective_batch_size := coalesce(array_length(runtime_division_lane_agent_ids(v_scope_key), 1), 0);
    else
      v_effective_batch_size := 1;
    end if;
  end if;

  if p_activate_all is true then
    v_blocked_reason := 'activate_all is blocked';
  elsif v_effective_batch_size > v_limit then
    v_blocked_reason := 'batch_size exceeds 1000';
  elsif v_effective_chunk_size > v_chunk_limit then
    v_blocked_reason := 'chunk_size exceeds 100';
  end if;

  if v_blocked_reason is null then
    if v_scope = 'division' then
      v_scope_ids := runtime_division_division_agent_ids();
    elsif v_scope = 'subdivision' then
      v_scope_ids := runtime_division_subdivision_agent_ids(v_scope_key);
    elsif v_scope = 'lane' then
      v_scope_ids := runtime_division_lane_agent_ids(v_scope_key);
    elsif v_scope = 'agent' and array_length(v_requested_ids, 1) = 1 then
      v_scope_ids := v_requested_ids;
    else
      v_blocked_reason := 'UNKNOWN_SCOPE_OR_TARGET';
    end if;
  end if;

  if v_blocked_reason is null and v_scope in ('subdivision', 'lane') and coalesce(array_length(v_scope_ids, 1), 0) = 0 then
    v_blocked_reason := 'UNKNOWN_SCOPE_OR_TARGET';
  end if;

  if v_blocked_reason is null then
    if coalesce(array_length(v_requested_ids, 1), 0) = 0 then
      v_requested_ids := v_scope_ids;
    end if;

    select array_agg(agent_id order by agent_id)
    into v_unknown_ids
    from (
      select unnest(v_requested_ids) as agent_id
      except
      select agent_id from runtime_division_agents
    ) missing;

    if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
      v_blocked_reason := 'Only the approved 1,000-agent division may be managed.';
    end if;
  end if;

  if v_blocked_reason is null and v_scope in ('subdivision', 'lane', 'agent') then
    select array_agg(agent_id order by agent_id)
    into v_out_of_scope_ids
    from (
      select unnest(v_requested_ids) as agent_id
      except
      select unnest(coalesce(v_scope_ids, '{}'::text[]))
    ) missing_scope;

    if coalesce(array_length(v_out_of_scope_ids, 1), 0) > 0 then
      v_blocked_reason := 'NON_DIVISION_AGENT_BLOCKED';
    end if;
  end if;

  if v_blocked_reason = 'Only the approved 1,000-agent division may be managed.' then
    v_blocked_event_type := 'UNKNOWN_AGENT_BLOCKED';
  elsif v_blocked_reason = 'UNKNOWN_SCOPE_OR_TARGET' then
    v_blocked_event_type := 'UNKNOWN_AGENT_BLOCKED';
  elsif v_blocked_reason = 'NON_DIVISION_AGENT_BLOCKED' then
    v_blocked_event_type := 'NON_DIVISION_AGENT_BLOCKED';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_division_audit_events (
      subdivision_key,
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      case when v_scope = 'subdivision' then v_scope_key else null end,
      case when v_scope = 'lane' then v_scope_key else null end,
      case when v_scope = 'agent' then coalesce((v_requested_ids)[1], null) else null end,
      v_actor,
      v_blocked_event_type,
      case when v_operation = 'deactivate' then 'Division deactivation request blocked' else 'Division activation request blocked' end,
      jsonb_build_object(
        'reason', v_blocked_reason,
        'scope', v_scope,
        'scope_key', v_scope_key,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'chunk_size', v_effective_chunk_size,
        'max_activation_batch_size', v_limit,
        'max_operation_chunk_size', v_chunk_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp58_1000_agent_runtime_division'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', v_blocked_event_type,
      'reason', v_blocked_reason,
      'unknown_agent_ids', case when v_unknown_ids is null then null else to_jsonb(v_unknown_ids) end,
      'out_of_scope_agent_ids', case when v_out_of_scope_ids is null then null else to_jsonb(v_out_of_scope_ids) end,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  if v_effective_batch_size > coalesce(array_length(v_requested_ids, 1), 0) then
    v_effective_batch_size := coalesce(array_length(v_requested_ids, 1), 0);
  end if;

  if v_effective_batch_size = 0 then
    v_effective_batch_size := coalesce(array_length(v_requested_ids, 1), 0);
  end if;

  v_chunk_index := 0;
  while v_chunk_index * v_effective_chunk_size < coalesce(array_length(v_requested_ids, 1), 0) loop
    v_chunk_index := v_chunk_index + 1;
    v_chunk_start := ((v_chunk_index - 1) * v_effective_chunk_size) + 1;
    v_chunk_end := least(v_chunk_index * v_effective_chunk_size, coalesce(array_length(v_requested_ids, 1), 0));
    v_chunk_ids := v_requested_ids[v_chunk_start:v_chunk_end];

    with changed_agents as (
      update runtime_division_agents
      set status = v_target_status,
          updated_at = now()
      where agent_id = any(v_chunk_ids)
      returning *
    ),
    event_rows as (
      insert into runtime_division_activation_events (
        subdivision_key,
        lane_key,
        agent_id,
        chunk_number,
        chunk_size,
        actor,
        event_type,
        event_summary,
        event_payload,
        source
      )
      select
        agent.subdivision_key,
        agent.lane_key,
        agent.agent_id,
        v_chunk_index,
        coalesce(array_length(v_chunk_ids, 1), 0),
        v_actor,
        v_event_type,
        v_event_summary,
        jsonb_build_object(
          'scope', v_scope,
          'scope_key', v_scope_key,
          'operation', v_operation,
          'chunk_number', v_chunk_index,
          'chunk_size', coalesce(array_length(v_chunk_ids, 1), 0),
          'batch_size', v_effective_batch_size,
          'max_activation_batch_size', v_limit,
          'max_operation_chunk_size', v_chunk_limit,
          'full_47979_activation_blocked', true,
          'execution_permissions', 'none',
          'external_api_permissions', 'none',
          'database_write_permissions', 'audit_event_only'
        ),
        'mvp58_1000_agent_runtime_division'
      from changed_agents agent
      returning *
    )
    select
      coalesce((select jsonb_agg(to_jsonb(changed_agents)) from changed_agents), '[]'::jsonb),
      coalesce((select jsonb_agg(to_jsonb(event_rows)) from event_rows), '[]'::jsonb)
    into v_chunk_agents, v_chunk_events
    ;

    v_agents := v_agents || coalesce(v_chunk_agents, '[]'::jsonb);
    v_events := v_events || coalesce(v_chunk_events, '[]'::jsonb);

    insert into runtime_division_audit_events (
      subdivision_key,
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      case when v_scope = 'subdivision' then v_scope_key else null end,
      case when v_scope = 'lane' then v_scope_key else null end,
      case when v_scope = 'agent' then (v_chunk_ids)[1] else null end,
      v_actor,
      v_event_type,
      v_event_summary,
      jsonb_build_object(
        'scope', v_scope,
        'scope_key', v_scope_key,
        'operation', v_operation,
        'chunk_number', v_chunk_index,
        'chunk_size', coalesce(array_length(v_chunk_ids, 1), 0),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'max_operation_chunk_size', v_chunk_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp58_1000_agent_runtime_division'
    )
    returning * into v_audit;

    v_audit_events := v_audit_events || jsonb_build_array(to_jsonb(v_audit));
  end loop;

  v_rollup := runtime_division_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'activation_events', v_events,
    'audit_events', v_audit_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_division_size', 1000,
      'live_runtime_agents_enabled', (v_rollup ->> 'active_agents')::integer,
      'max_activation_batch_size', 1000,
      'max_operation_chunk_size', 100,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_subdivisions_count', (v_rollup ->> 'active_subdivisions')::integer,
      'inactive_subdivisions_count', (v_rollup ->> 'inactive_subdivisions')::integer,
      'active_lanes_count', (v_rollup ->> 'active_lanes')::integer,
      'inactive_lanes_count', (v_rollup ->> 'inactive_lanes')::integer,
      'activation_mode', 'supervised_thousand_agent_division',
      'division_health_rollup', v_rollup
    ),
    'division_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_division_activate_agents(
  p_agent_ids text[] default null,
  p_actor text default null,
  p_reason text default null,
  p_batch_size integer default null,
  p_chunk_size integer default 100,
  p_activate_all boolean default false,
  p_scope text default 'division',
  p_scope_key text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
begin
  return runtime_division_apply_agent_state(
    'activate',
    p_scope,
    p_scope_key,
    p_agent_ids,
    p_actor,
    p_reason,
    p_batch_size,
    p_chunk_size,
    p_activate_all
  );
end;
$$;

create or replace function runtime_division_deactivate_agents(
  p_agent_ids text[] default null,
  p_actor text default null,
  p_reason text default null,
  p_batch_size integer default null,
  p_chunk_size integer default 100,
  p_activate_all boolean default false,
  p_scope text default 'division',
  p_scope_key text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
begin
  return runtime_division_apply_agent_state(
    'deactivate',
    p_scope,
    p_scope_key,
    p_agent_ids,
    p_actor,
    p_reason,
    p_batch_size,
    p_chunk_size,
    p_activate_all
  );
end;
$$;

create or replace function runtime_division_record_heartbeat(
  p_scope text,
  p_subdivision_key text default null,
  p_lane_key text default null,
  p_agent_id text default null,
  p_actor text default null,
  p_heartbeat_status text default 'healthy',
  p_heartbeat_note text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_scope text := lower(coalesce(nullif(btrim(p_scope), ''), 'division'));
  v_subdivision_key text := nullif(btrim(p_subdivision_key), '');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_heartbeat_status text := coalesce(nullif(btrim(p_heartbeat_status), ''), 'healthy');
  v_heartbeat_note text := nullif(btrim(p_heartbeat_note), '');
  v_target_ids text[];
  v_heartbeat jsonb := '[]'::jsonb;
  v_audit runtime_division_audit_events%rowtype;
  v_rollup jsonb := '{}'::jsonb;
begin
  if v_scope = 'subdivision' then
    v_target_ids := runtime_division_subdivision_agent_ids(v_subdivision_key);
  elsif v_scope = 'lane' then
    v_target_ids := runtime_division_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    v_target_ids := runtime_division_division_agent_ids();
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_division_agents
    set last_heartbeat_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into division_heartbeat_events (
      subdivision_key,
      lane_key,
      agent_id,
      scope,
      heartbeat_status,
      heartbeat_note,
      target_agent_count,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      case when v_scope = 'subdivision' then v_subdivision_key else null end,
      case when v_scope = 'lane' then v_lane_key else null end,
      case when v_scope = 'agent' then v_agent_id else null end,
      v_scope,
      v_heartbeat_status,
      v_heartbeat_note,
      coalesce(array_length(v_target_ids, 1), 0),
      'DIVISION_HEARTBEAT',
      'Division heartbeat recorded',
      jsonb_build_object(
        'scope', v_scope,
        'subdivision_key', v_subdivision_key,
        'lane_key', v_lane_key,
        'agent_id', v_agent_id,
        'heartbeat_status', v_heartbeat_status,
        'heartbeat_note', v_heartbeat_note,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp58_1000_agent_runtime_division'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_heartbeat
  from inserted;

  insert into runtime_division_audit_events (
    subdivision_key,
    lane_key,
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    case when v_scope = 'subdivision' then v_subdivision_key else null end,
    case when v_scope = 'lane' then v_lane_key else null end,
    case when v_scope = 'agent' then v_agent_id else null end,
    v_actor,
    'DIVISION_HEARTBEAT',
    'Division heartbeat recorded',
    jsonb_build_object(
      'scope', v_scope,
      'subdivision_key', v_subdivision_key,
      'lane_key', v_lane_key,
      'agent_id', v_agent_id,
      'heartbeat_status', v_heartbeat_status,
      'heartbeat_note', v_heartbeat_note,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
    ),
    'mvp58_1000_agent_runtime_division'
  )
  returning * into v_audit;

  v_rollup := runtime_division_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'heartbeat_events', v_heartbeat,
    'audit_event', to_jsonb(v_audit),
    'division_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_division_create_readiness_note(
  p_scope text,
  p_subdivision_key text default null,
  p_lane_key text default null,
  p_agent_id text default null,
  p_actor text default null,
  p_note_title text default null,
  p_note_body text default null,
  p_readiness_level text default 'green'
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_scope text := lower(coalesce(nullif(btrim(p_scope), ''), 'division'));
  v_subdivision_key text := nullif(btrim(p_subdivision_key), '');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_note_title text := nullif(btrim(p_note_title), '');
  v_note_body text := nullif(btrim(p_note_body), '');
  v_readiness_level text := coalesce(nullif(btrim(p_readiness_level), ''), 'green');
  v_target_ids text[];
  v_notes jsonb := '[]'::jsonb;
  v_audit runtime_division_audit_events%rowtype;
  v_rollup jsonb := '{}'::jsonb;
begin
  if v_note_title is null or v_note_body is null then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_NOTE_PAYLOAD');
  end if;

  if v_scope = 'subdivision' then
    v_target_ids := runtime_division_subdivision_agent_ids(v_subdivision_key);
  elsif v_scope = 'lane' then
    v_target_ids := runtime_division_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    v_target_ids := runtime_division_division_agent_ids();
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_division_agents
    set last_readiness_note_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into division_readiness_notes (
      subdivision_key,
      lane_key,
      agent_id,
      scope,
      note_title,
      note_body,
      readiness_level,
      target_agent_count,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      case when v_scope = 'subdivision' then v_subdivision_key else null end,
      case when v_scope = 'lane' then v_lane_key else null end,
      case when v_scope = 'agent' then v_agent_id else null end,
      v_scope,
      v_note_title,
      v_note_body,
      v_readiness_level,
      coalesce(array_length(v_target_ids, 1), 0),
      'DIVISION_READINESS_NOTE_CREATED',
      'Division readiness note created',
      jsonb_build_object(
        'scope', v_scope,
        'subdivision_key', v_subdivision_key,
        'lane_key', v_lane_key,
        'agent_id', v_agent_id,
        'note_title', v_note_title,
        'note_body', v_note_body,
        'readiness_level', v_readiness_level,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp58_1000_agent_runtime_division'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_notes
  from inserted;

  insert into runtime_division_audit_events (
    subdivision_key,
    lane_key,
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    case when v_scope = 'subdivision' then v_subdivision_key else null end,
    case when v_scope = 'lane' then v_lane_key else null end,
    case when v_scope = 'agent' then v_agent_id else null end,
    v_actor,
    'DIVISION_READINESS_NOTE_CREATED',
    'Division readiness note recorded',
    jsonb_build_object(
      'scope', v_scope,
      'subdivision_key', v_subdivision_key,
      'lane_key', v_lane_key,
      'agent_id', v_agent_id,
      'note_title', v_note_title,
      'readiness_level', v_readiness_level,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
    ),
    'mvp58_1000_agent_runtime_division'
  )
  returning * into v_audit;

  v_rollup := runtime_division_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'readiness_notes', v_notes,
    'audit_event', to_jsonb(v_audit),
    'division_rollup', v_rollup
  );
end;
$$;
