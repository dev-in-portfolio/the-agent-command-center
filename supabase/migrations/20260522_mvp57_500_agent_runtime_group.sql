-- MVP-57 500-agent runtime group.
-- This migration defines persistence only. It does not enable command execution, deploy execution, rollback execution, alert sending, or arbitrary activation beyond the approved 500-agent group.
-- Approved group IDs: mvp57_group_agent_001 through mvp57_group_agent_500.
-- Lane set: intake_lane_01 through reporting_lane_05 across 50 lanes.
-- Blocked markers: UNKNOWN_AGENT_BLOCKED and NON_GROUP_AGENT_BLOCKED.

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

create table if not exists runtime_group_lanes (
  lane_key text primary key,
  lane_name text not null,
  lane_order integer not null unique,
  lane_description text not null default '',
  allowed_task text not null default 'send heartbeat and create readiness note only',
  status text not null default 'inactive',
  kill_switch_visible boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_group_lanes_status_check
    check (status in ('inactive', 'active', 'mixed', 'disabled'))
);

create table if not exists runtime_group_agents (
  agent_id text primary key,
  agent_name text not null,
  lane_key text not null references runtime_group_lanes(lane_key) on delete cascade,
  lane_position integer not null,
  allowed_task text not null default 'send heartbeat and create readiness note only',
  execution_permissions text not null default 'none',
  external_api_permissions text not null default 'none',
  database_write_permissions text not null default 'audit_event_only',
  status text not null default 'inactive',
  is_supervised_group_agent boolean not null default true,
  kill_switch_visible boolean not null default true,
  last_heartbeat_at timestamptz,
  last_readiness_note_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_group_agents_status_check
    check (status in ('inactive', 'active', 'deactivated', 'blocked', 'disabled')),
  constraint runtime_group_agents_lane_position_check
    check (lane_position between 1 and 10),
  constraint runtime_group_agents_lane_position_unique
    unique (lane_key, lane_position)
);

create table if not exists runtime_group_activation_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_group_lanes(lane_key) on delete cascade,
  agent_id text references runtime_group_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp57_500_agent_runtime_group'
);

create table if not exists group_heartbeat_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_group_lanes(lane_key) on delete cascade,
  agent_id text references runtime_group_agents(agent_id) on delete cascade,
  actor text,
  scope text not null default 'group',
  heartbeat_status text not null default 'healthy',
  heartbeat_note text,
  event_type text not null default 'GROUP_HEARTBEAT',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp57_500_agent_runtime_group'
);

create table if not exists group_readiness_notes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_group_lanes(lane_key) on delete cascade,
  agent_id text references runtime_group_agents(agent_id) on delete cascade,
  actor text,
  scope text not null default 'group',
  note_title text not null,
  note_body text not null,
  readiness_level text not null default 'green',
  event_type text not null default 'GROUP_READINESS_NOTE_CREATED',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp57_500_agent_runtime_group'
);

create table if not exists runtime_group_audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_group_lanes(lane_key) on delete cascade,
  agent_id text references runtime_group_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp57_500_agent_runtime_group'
);

create index if not exists runtime_group_agents_lane_key_idx on runtime_group_agents (lane_key);
create index if not exists runtime_group_agents_status_idx on runtime_group_agents (status);
create index if not exists runtime_group_activation_events_created_at_idx on runtime_group_activation_events (created_at desc);
create index if not exists runtime_group_activation_events_lane_key_idx on runtime_group_activation_events (lane_key);
create index if not exists group_heartbeat_events_created_at_idx on group_heartbeat_events (created_at desc);
create index if not exists group_heartbeat_events_lane_key_idx on group_heartbeat_events (lane_key);
create index if not exists group_readiness_notes_created_at_idx on group_readiness_notes (created_at desc);
create index if not exists group_readiness_notes_lane_key_idx on group_readiness_notes (lane_key);
create index if not exists runtime_group_audit_events_created_at_idx on runtime_group_audit_events (created_at desc);
create index if not exists runtime_group_audit_events_lane_key_idx on runtime_group_audit_events (lane_key);



with lane_groups(prefix, display_name, lane_description, lane_offset) as (
  values
    ('intake', 'Intake', 'Initial controlled intake and queue triage lane.', 0),
    ('validation', 'Validation', 'Controlled validation and readiness lane.', 5),
    ('audit', 'Audit', 'Audit visibility and recordkeeping lane.', 10),
    ('approval', 'Approval', 'Approval review and decision lane.', 15),
    ('dry_run', 'Dry Run', 'Dry-run and preview lane.', 20),
    ('monitoring', 'Monitoring', 'Monitoring and readiness tracking lane.', 25),
    ('safety', 'Safety', 'Safety boundary and kill-switch lane.', 30),
    ('registry', 'Registry', 'Registry and roster verification lane.', 35),
    ('review', 'Review', 'Human review and QA lane.', 40),
    ('reporting', 'Reporting', 'Reporting and summary lane.', 45)

), lane_rows as (
  select
    format('%s_lane_%s', prefix, lpad(gs::text, 2, '0')) as lane_key,
    format('%s Lane %s', display_name, lpad(gs::text, 2, '0')) as lane_name,
    lane_offset + gs as lane_order,
    lane_description,
    'send heartbeat and create readiness note only' as allowed_task,
    'inactive' as status,
    true as kill_switch_visible
  from lane_groups
  cross join generate_series(1, 5) as gs
)
insert into runtime_group_lanes (lane_key, lane_name, lane_order, lane_description, allowed_task, status, kill_switch_visible)
select * from lane_rows
on conflict (lane_key) do update
set lane_name = excluded.lane_name,
    lane_order = excluded.lane_order,
    lane_description = excluded.lane_description,
    allowed_task = excluded.allowed_task,
    status = excluded.status,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();



insert into runtime_group_agents (
  agent_id,
  agent_name,
  lane_key,
  lane_position,
  allowed_task,
  execution_permissions,
  external_api_permissions,
  database_write_permissions,
  status,
  is_supervised_group_agent,
  kill_switch_visible
)
select
  format('mvp57_group_agent_%s', lpad(gs::text, 3, '0')) as agent_id,
  format('Group Agent %s', lpad(gs::text, 3, '0')) as agent_name,
  lane.lane_key,
  ((gs - 1) % 10) + 1 as lane_position,
  'send heartbeat and create readiness note only',
  'none',
  'none',
  'audit_event_only',
  'inactive',
  true,
  true
from generate_series(1, 500) as gs
join runtime_group_lanes lane
  on lane.lane_order = ((gs - 1) / 10) + 1
on conflict (agent_id) do update
set agent_name = excluded.agent_name,
    lane_key = excluded.lane_key,
    lane_position = excluded.lane_position,
    allowed_task = excluded.allowed_task,
    execution_permissions = excluded.execution_permissions,
    external_api_permissions = excluded.external_api_permissions,
    database_write_permissions = excluded.database_write_permissions,
    status = excluded.status,
    is_supervised_group_agent = excluded.is_supervised_group_agent,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

drop trigger if exists runtime_group_lanes_touch_updated_at on runtime_group_lanes;
create trigger runtime_group_lanes_touch_updated_at
before update on runtime_group_lanes
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_group_agents_touch_updated_at on runtime_group_agents;
create trigger runtime_group_agents_touch_updated_at
before update on runtime_group_agents
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_group_lanes enable row level security;
alter table if exists runtime_group_agents enable row level security;
alter table if exists runtime_group_activation_events enable row level security;
alter table if exists group_heartbeat_events enable row level security;
alter table if exists group_readiness_notes enable row level security;
alter table if exists runtime_group_audit_events enable row level security;

insert into runtime_kernel_config (key, value)
values
  ('runtime_group_size', '500'::jsonb),
  ('max_activation_batch_size', '500'::jsonb),
  ('live_runtime_agents_enabled', '0'::jsonb),
  ('runtime_activation_started', 'false'::jsonb),
  ('full_47979_activation_blocked', 'true'::jsonb),
  ('total_registered_agents', '47979'::jsonb),
  ('command_execution_enabled', 'false'::jsonb),
  ('deploy_execution_enabled', 'false'::jsonb),
  ('rollback_execution_enabled', 'false'::jsonb),
  ('alert_sending_enabled', 'false'::jsonb),
  ('kill_switch_visible', 'true'::jsonb),
  ('active_lanes_count', '0'::jsonb),
  ('inactive_lanes_count', '50'::jsonb),
  ('activation_mode', '"supervised_five_hundred_agent_group"'::jsonb),
  ('heartbeat_event_count', '0'::jsonb),
  ('readiness_note_count', '0'::jsonb),
  ('activation_event_count', '0'::jsonb),
  ('audit_event_count', '0'::jsonb),
  (
    'group_health_rollup',
    jsonb_build_object(
      'group_health', 'inactive',
      'active_agents', 0,
      'inactive_agents', 500,
      'active_lanes', 0,
      'inactive_lanes', 50,
      'heartbeat_event_count', 0,
      'readiness_note_count', 0,
      'activation_event_count', 0,
      'audit_event_count', 0,
      'runtime_group_size', 500,
      'total_registered_agents', 47979
    )
  )
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

create or replace function runtime_group_lane_agent_ids(
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
  from runtime_group_agents
  where lane_key = v_lane_key;

  return coalesce(v_agent_ids, '{}'::text[]);
end;
$$;

create or replace function runtime_group_sync_rollups()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_active_count integer := 0;
  v_active_lane_count integer := 0;
  v_heartbeat_count integer := 0;
  v_readiness_note_count integer := 0;
  v_activation_event_count integer := 0;
  v_audit_event_count integer := 0;
  v_group_health text := 'inactive';
  v_rollup jsonb := '{}'::jsonb;
begin
  select count(*) into v_active_count
  from runtime_group_agents
  where status = 'active';

  select count(distinct lane_key) into v_active_lane_count
  from runtime_group_agents
  where status = 'active';

  select count(*) into v_heartbeat_count from group_heartbeat_events;
  select count(*) into v_readiness_note_count from group_readiness_notes;
  select count(*) into v_activation_event_count from runtime_group_activation_events;
  select count(*) into v_audit_event_count from runtime_group_audit_events;

  if v_active_count = 0 then
    v_group_health := 'inactive';
  elsif v_active_count >= 500 and v_active_lane_count >= 50 then
    v_group_health := 'healthy';
  else
    v_group_health := 'partial';
  end if;

  update runtime_kernel_config
  set value = to_jsonb(v_active_count),
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  update runtime_kernel_config
  set value = to_jsonb(v_active_lane_count),
      updated_at = now()
  where key = 'active_lanes_count';

  update runtime_kernel_config
  set value = to_jsonb(greatest(50 - v_active_lane_count, 0)),
      updated_at = now()
  where key = 'inactive_lanes_count';

  update runtime_kernel_config
  set value = to_jsonb(v_heartbeat_count),
      updated_at = now()
  where key = 'heartbeat_event_count';

  update runtime_kernel_config
  set value = to_jsonb(v_readiness_note_count),
      updated_at = now()
  where key = 'readiness_note_count';

  update runtime_kernel_config
  set value = to_jsonb(v_activation_event_count),
      updated_at = now()
  where key = 'activation_event_count';

  update runtime_kernel_config
  set value = to_jsonb(v_audit_event_count),
      updated_at = now()
  where key = 'audit_event_count';

  v_rollup := jsonb_build_object(
    'group_health', v_group_health,
    'active_agents', v_active_count,
    'inactive_agents', greatest(500 - v_active_count, 0),
    'active_lanes', v_active_lane_count,
    'inactive_lanes', greatest(50 - v_active_lane_count, 0),
    'heartbeat_event_count', v_heartbeat_count,
    'readiness_note_count', v_readiness_note_count,
    'activation_event_count', v_activation_event_count,
    'audit_event_count', v_audit_event_count,
    'runtime_group_size', 500,
    'total_registered_agents', 47979
  );

  update runtime_kernel_config
  set value = v_rollup,
      updated_at = now()
  where key = 'group_health_rollup';

  return v_rollup;
end;
$$;

create or replace function runtime_group_activate_agents(
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
  v_limit integer := 500;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_rollup jsonb := '{}'::jsonb;
  v_audit runtime_group_audit_events%rowtype;
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
    v_blocked_reason := 'batch_size exceeds 500';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved group agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_group_audit_events (
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      null,
      v_actor,
      'GROUP_ACTIVATION_BLOCKED',
      'Group activation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp57_500_agent_runtime_group'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'GROUP_ACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_group_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_group_audit_events (
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      null,
      v_actor,
      'UNKNOWN_AGENT_BLOCKED',
      'Unknown group agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 500-agent group may be activated.'
      ),
      'mvp57_500_agent_runtime_group'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 500-agent group may be activated.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with activated as (
    update runtime_group_agents
    set status = 'active',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(activated)), '[]'::jsonb) into v_agents
  from activated;

  with event_rows as (
    insert into runtime_group_activation_events (
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      agent.lane_key,
      agent.agent_id,
      v_actor,
      'GROUP_AGENT_ACTIVATED',
      'Controlled group agent activated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_five_hundred_agent_group',
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp57_500_agent_runtime_group'
    from runtime_group_agents agent
    where agent.agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(event_rows)), '[]'::jsonb) into v_events
  from event_rows;

  v_rollup := runtime_group_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'audit_events', v_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_group_size', 500,
      'live_runtime_agents_enabled', (v_rollup ->> 'active_agents')::integer,
      'max_activation_batch_size', 500,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_lanes_count', (v_rollup ->> 'active_lanes')::integer,
      'inactive_lanes_count', (v_rollup ->> 'inactive_lanes')::integer,
      'activation_mode', 'supervised_five_hundred_agent_group',
      'group_health_rollup', v_rollup
    ),
    'group_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_group_deactivate_agents(
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
  v_limit integer := 500;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_rollup jsonb := '{}'::jsonb;
  v_audit runtime_group_audit_events%rowtype;
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
    v_blocked_reason := 'batch_size exceeds 500';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved group agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_group_audit_events (
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      null,
      v_actor,
      'GROUP_DEACTIVATION_BLOCKED',
      'Group deactivation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp57_500_agent_runtime_group'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'GROUP_DEACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_group_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_group_audit_events (
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      null,
      null,
      v_actor,
      'UNKNOWN_AGENT_BLOCKED',
      'Unknown group agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 500-agent group may be managed.'
      ),
      'mvp57_500_agent_runtime_group'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 500-agent group may be managed.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with deactivated as (
    update runtime_group_agents
    set status = 'deactivated',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(deactivated)), '[]'::jsonb) into v_agents
  from deactivated;

  with event_rows as (
    insert into runtime_group_activation_events (
      lane_key,
      agent_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      agent.lane_key,
      agent.agent_id,
      v_actor,
      'GROUP_AGENT_DEACTIVATED',
      'Controlled group agent deactivated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_five_hundred_agent_group',
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp57_500_agent_runtime_group'
    from runtime_group_agents agent
    where agent.agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(event_rows)), '[]'::jsonb) into v_events
  from event_rows;

  v_rollup := runtime_group_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'audit_events', v_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_group_size', 500,
      'live_runtime_agents_enabled', (v_rollup ->> 'active_agents')::integer,
      'max_activation_batch_size', 500,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_lanes_count', (v_rollup ->> 'active_lanes')::integer,
      'inactive_lanes_count', (v_rollup ->> 'inactive_lanes')::integer,
      'activation_mode', 'supervised_five_hundred_agent_group',
      'group_health_rollup', v_rollup
    ),
    'group_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_group_activate_lane(
  p_lane_key text,
  p_actor text,
  p_reason text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_ids text[];
begin
  if v_lane_key is null then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_LANE_KEY');
  end if;

  v_agent_ids := runtime_group_lane_agent_ids(v_lane_key);

  if coalesce(array_length(v_agent_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_LANE_BLOCKED');
  end if;

  return runtime_group_activate_agents(v_agent_ids, p_actor, p_reason, 10, false);
end;
$$;

create or replace function runtime_group_deactivate_lane(
  p_lane_key text,
  p_actor text,
  p_reason text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_ids text[];
begin
  if v_lane_key is null then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_LANE_KEY');
  end if;

  v_agent_ids := runtime_group_lane_agent_ids(v_lane_key);

  if coalesce(array_length(v_agent_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_LANE_BLOCKED');
  end if;

  return runtime_group_deactivate_agents(v_agent_ids, p_actor, p_reason, 10, false);
end;
$$;

create or replace function runtime_group_record_heartbeat(
  p_scope text,
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
  v_scope text := coalesce(nullif(btrim(p_scope), ''), 'group');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_heartbeat_status text := coalesce(nullif(btrim(p_heartbeat_status), ''), 'healthy');
  v_heartbeat_note text := nullif(btrim(p_heartbeat_note), '');
  v_target_ids text[];
  v_heartbeats jsonb := '[]'::jsonb;
  v_audit runtime_group_audit_events%rowtype;
  v_rollup jsonb := '{}'::jsonb;
begin
  if v_scope = 'lane' then
    v_target_ids := runtime_group_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    select array_agg(agent_id order by agent_id)
    into v_target_ids
    from runtime_group_agents;
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_group_agents
    set last_heartbeat_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into group_heartbeat_events (
      lane_key,
      agent_id,
      actor,
      scope,
      heartbeat_status,
      heartbeat_note,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      agent.lane_key,
      agent.agent_id,
      v_actor,
      v_scope,
      v_heartbeat_status,
      v_heartbeat_note,
      'GROUP_HEARTBEAT',
      'Group heartbeat recorded',
      jsonb_build_object(
        'scope', v_scope,
        'lane_key', v_lane_key,
        'heartbeat_status', v_heartbeat_status,
        'heartbeat_note', v_heartbeat_note,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp57_500_agent_runtime_group'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_heartbeats
  from inserted;

  insert into runtime_group_audit_events (
    lane_key,
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_lane_key,
    v_agent_id,
    v_actor,
    'GROUP_HEARTBEAT',
    'Group heartbeat recorded',
    jsonb_build_object(
      'scope', v_scope,
      'lane_key', v_lane_key,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0),
      'heartbeat_status', v_heartbeat_status
    ),
    'mvp57_500_agent_runtime_group'
  )
  returning * into v_audit;

  v_rollup := runtime_group_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'heartbeat_events', v_heartbeats,
    'audit_event', to_jsonb(v_audit),
    'group_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_group_create_readiness_note(
  p_scope text,
  p_lane_key text default null,
  p_agent_id text default null,
  p_actor text default null,
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
  v_scope text := coalesce(nullif(btrim(p_scope), ''), 'group');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_note_title text := nullif(btrim(p_note_title), '');
  v_note_body text := nullif(btrim(p_note_body), '');
  v_readiness_level text := coalesce(nullif(btrim(p_readiness_level), ''), 'green');
  v_target_ids text[];
  v_notes jsonb := '[]'::jsonb;
  v_audit runtime_group_audit_events%rowtype;
  v_rollup jsonb := '{}'::jsonb;
begin
  if v_note_title is null or v_note_body is null then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_NOTE_PAYLOAD');
  end if;

  if v_scope = 'lane' then
    v_target_ids := runtime_group_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    select array_agg(agent_id order by agent_id)
    into v_target_ids
    from runtime_group_agents;
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_group_agents
    set last_readiness_note_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into group_readiness_notes (
      lane_key,
      agent_id,
      actor,
      scope,
      note_title,
      note_body,
      readiness_level,
      event_type,
      event_summary,
      event_payload,
      source
    )
    select
      agent.lane_key,
      agent.agent_id,
      v_actor,
      v_scope,
      v_note_title,
      v_note_body,
      v_readiness_level,
      'GROUP_READINESS_NOTE_CREATED',
      'Group readiness note created',
      jsonb_build_object(
        'scope', v_scope,
        'lane_key', v_lane_key,
        'note_title', v_note_title,
        'note_body', v_note_body,
        'readiness_level', v_readiness_level,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp57_500_agent_runtime_group'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_notes
  from inserted;

  insert into runtime_group_audit_events (
    lane_key,
    agent_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_lane_key,
    v_agent_id,
    v_actor,
    'GROUP_READINESS_NOTE_CREATED',
    'Group readiness note recorded',
    jsonb_build_object(
      'scope', v_scope,
      'lane_key', v_lane_key,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0),
      'readiness_level', v_readiness_level
    ),
    'mvp57_500_agent_runtime_group'
  )
  returning * into v_audit;

  v_rollup := runtime_group_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'readiness_notes', v_notes,
    'audit_event', to_jsonb(v_audit),
    'group_rollup', v_rollup
  );
end;
$$;
