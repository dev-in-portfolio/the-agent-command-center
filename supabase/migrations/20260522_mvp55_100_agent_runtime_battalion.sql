-- MVP-55 100-agent runtime battalion.
-- This migration defines persistence only. It does not enable command execution, deploy execution, rollback execution, alert sending, or arbitrary activation beyond the approved 100-agent battalion.
-- Approved battalion IDs: mvp55_battalion_agent_001 through mvp55_battalion_agent_100.
-- Lane set: intake_lane, validation_lane, audit_lane, approval_lane, dry_run_lane, monitoring_lane, safety_lane, registry_lane, review_lane, reporting_lane.

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

create table if not exists runtime_battalion_lanes (
  lane_key text primary key,
  lane_name text not null,
  lane_order integer not null unique,
  lane_description text not null default '',
  allowed_task text not null default 'send heartbeat and create readiness note only',
  status text not null default 'inactive',
  kill_switch_visible boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_battalion_lanes_status_check
    check (status in ('inactive', 'active', 'mixed', 'disabled'))
);

create table if not exists runtime_battalion_agents (
  agent_id text primary key,
  agent_name text not null,
  lane_key text not null references runtime_battalion_lanes(lane_key) on delete cascade,
  lane_position integer not null,
  allowed_task text not null default 'send heartbeat and create readiness note only',
  execution_permissions text not null default 'none',
  external_api_permissions text not null default 'none',
  database_write_permissions text not null default 'audit_event_only',
  status text not null default 'inactive',
  is_supervised_test_agent boolean not null default true,
  kill_switch_visible boolean not null default true,
  last_heartbeat_at timestamptz,
  last_readiness_note_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_battalion_agents_status_check
    check (status in ('inactive', 'active', 'deactivated', 'blocked', 'disabled')),
  constraint runtime_battalion_agents_lane_position_check
    check (lane_position between 1 and 10),
  constraint runtime_battalion_agents_lane_position_unique
    unique (lane_key, lane_position)
);

create table if not exists runtime_battalion_activation_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_battalion_lanes(lane_key) on delete cascade,
  agent_id text references runtime_battalion_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp55_100_agent_runtime_battalion'
);

create table if not exists battalion_heartbeat_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_battalion_lanes(lane_key) on delete cascade,
  agent_id text references runtime_battalion_agents(agent_id) on delete cascade,
  actor text,
  scope text not null default 'battalion',
  heartbeat_status text not null default 'healthy',
  heartbeat_note text,
  event_type text not null default 'BATTALION_HEARTBEAT',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp55_100_agent_runtime_battalion'
);

create table if not exists battalion_readiness_notes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_battalion_lanes(lane_key) on delete cascade,
  agent_id text references runtime_battalion_agents(agent_id) on delete cascade,
  actor text,
  scope text not null default 'battalion',
  note_title text not null,
  note_body text not null,
  readiness_level text not null default 'green',
  event_type text not null default 'BATTALION_READINESS_NOTE_CREATED',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp55_100_agent_runtime_battalion'
);

create table if not exists runtime_battalion_audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_battalion_lanes(lane_key) on delete cascade,
  agent_id text references runtime_battalion_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp55_100_agent_runtime_battalion'
);

create index if not exists runtime_battalion_agents_lane_key_idx on runtime_battalion_agents (lane_key);
create index if not exists runtime_battalion_agents_status_idx on runtime_battalion_agents (status);
create index if not exists runtime_battalion_activation_events_created_at_idx on runtime_battalion_activation_events (created_at desc);
create index if not exists runtime_battalion_activation_events_lane_key_idx on runtime_battalion_activation_events (lane_key);
create index if not exists battalion_heartbeat_events_created_at_idx on battalion_heartbeat_events (created_at desc);
create index if not exists battalion_heartbeat_events_lane_key_idx on battalion_heartbeat_events (lane_key);
create index if not exists battalion_readiness_notes_created_at_idx on battalion_readiness_notes (created_at desc);
create index if not exists battalion_readiness_notes_lane_key_idx on battalion_readiness_notes (lane_key);
create index if not exists runtime_battalion_audit_events_created_at_idx on runtime_battalion_audit_events (created_at desc);
create index if not exists runtime_battalion_audit_events_lane_key_idx on runtime_battalion_audit_events (lane_key);

insert into runtime_battalion_lanes (lane_key, lane_name, lane_order, lane_description, allowed_task, status, kill_switch_visible)
values
  ('intake_lane', 'Intake Lane', 1, 'Initial controlled intake and queue triage lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('validation_lane', 'Validation Lane', 2, 'Controlled validation and readiness lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('audit_lane', 'Audit Lane', 3, 'Audit visibility and recordkeeping lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('approval_lane', 'Approval Lane', 4, 'Approval review and decision lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('dry_run_lane', 'Dry Run Lane', 5, 'Dry-run and preview lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('monitoring_lane', 'Monitoring Lane', 6, 'Monitoring and readiness tracking lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('safety_lane', 'Safety Lane', 7, 'Safety boundary and kill-switch lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('registry_lane', 'Registry Lane', 8, 'Registry and roster verification lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('review_lane', 'Review Lane', 9, 'Human review and QA lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('reporting_lane', 'Reporting Lane', 10, 'Reporting and summary lane.', 'send heartbeat and create readiness note only', 'inactive', true)
on conflict (lane_key) do update
set lane_name = excluded.lane_name,
    lane_order = excluded.lane_order,
    lane_description = excluded.lane_description,
    allowed_task = excluded.allowed_task,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

insert into runtime_battalion_agents (
  agent_id,
  agent_name,
  lane_key,
  lane_position,
  allowed_task,
  execution_permissions,
  external_api_permissions,
  database_write_permissions,
  status,
  is_supervised_test_agent,
  kill_switch_visible
)
select
  format('mvp55_battalion_agent_%s', lpad(gs::text, 3, '0')) as agent_id,
  format('Battalion Agent %s', lpad(gs::text, 3, '0')) as agent_name,
  lane.lane_key,
  ((gs - 1) % 10) + 1 as lane_position,
  'send heartbeat and create readiness note only',
  'none',
  'none',
  'audit_event_only',
  'inactive',
  true,
  true
from generate_series(1, 100) as gs
join runtime_battalion_lanes lane
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
    is_supervised_test_agent = excluded.is_supervised_test_agent,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

drop trigger if exists runtime_battalion_lanes_touch_updated_at on runtime_battalion_lanes;
create trigger runtime_battalion_lanes_touch_updated_at
before update on runtime_battalion_lanes
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_battalion_agents_touch_updated_at on runtime_battalion_agents;
create trigger runtime_battalion_agents_touch_updated_at
before update on runtime_battalion_agents
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_battalion_lanes enable row level security;
alter table if exists runtime_battalion_agents enable row level security;
alter table if exists runtime_battalion_activation_events enable row level security;
alter table if exists battalion_heartbeat_events enable row level security;
alter table if exists battalion_readiness_notes enable row level security;
alter table if exists runtime_battalion_audit_events enable row level security;

insert into runtime_kernel_config (key, value)
values
  ('runtime_battalion_size', '100'::jsonb),
  ('max_activation_batch_size', '100'::jsonb),
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
  ('inactive_lanes_count', '10'::jsonb),
  ('activation_mode', '"supervised_hundred_agent_battalion"'::jsonb)
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

create or replace function runtime_battalion_lane_agent_ids(
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
  from runtime_battalion_agents
  where lane_key = v_lane_key;

  return coalesce(v_agent_ids, '{}'::text[]);
end;
$$;

create or replace function runtime_battalion_activate_agents(
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
  v_limit integer := 100;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_active_count integer := 0;
  v_active_lane_count integer := 0;
  v_audit runtime_battalion_audit_events%rowtype;
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
    v_blocked_reason := 'batch_size exceeds 100';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved battalion agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_battalion_audit_events (
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
      'BATTALION_ACTIVATION_BLOCKED',
      'Battalion activation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp55_100_agent_runtime_battalion'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'BATTALION_ACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_battalion_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_battalion_audit_events (
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
      'Unknown battalion agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 100-agent battalion may be activated.'
      ),
      'mvp55_100_agent_runtime_battalion'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 100-agent battalion may be activated.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with activated as (
    update runtime_battalion_agents
    set status = 'active',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(activated)), '[]'::jsonb) into v_agents
  from activated;

  with event_rows as (
    insert into runtime_battalion_activation_events (
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
      'BATTALION_AGENT_ACTIVATED',
      'Controlled battalion agent activated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_hundred_agent_battalion',
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp55_100_agent_runtime_battalion'
    from runtime_battalion_agents agent
    where agent.agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(event_rows)), '[]'::jsonb) into v_events
  from event_rows;

  select count(*) into v_active_count
  from runtime_battalion_agents
  where status = 'active';

  select count(distinct lane_key) into v_active_lane_count
  from runtime_battalion_agents
  where status = 'active';

  update runtime_kernel_config
  set value = to_jsonb(v_active_count),
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  update runtime_kernel_config
  set value = to_jsonb(v_active_lane_count),
      updated_at = now()
  where key = 'active_lanes_count';

  update runtime_kernel_config
  set value = to_jsonb(greatest(10 - v_active_lane_count, 0)),
      updated_at = now()
  where key = 'inactive_lanes_count';

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'audit_events', v_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_battalion_size', 100,
      'live_runtime_agents_enabled', v_active_count,
      'max_activation_batch_size', 100,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_lanes_count', v_active_lane_count,
      'inactive_lanes_count', greatest(10 - v_active_lane_count, 0),
      'activation_mode', 'supervised_hundred_agent_battalion'
    )
  );
end;
$$;

create or replace function runtime_battalion_deactivate_agents(
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
  v_limit integer := 100;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_active_count integer := 0;
  v_active_lane_count integer := 0;
  v_audit runtime_battalion_audit_events%rowtype;
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
    v_blocked_reason := 'batch_size exceeds 100';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved battalion agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_battalion_audit_events (
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
      'BATTALION_DEACTIVATION_BLOCKED',
      'Battalion deactivation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp55_100_agent_runtime_battalion'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'BATTALION_DEACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_battalion_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_battalion_audit_events (
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
      'Unknown battalion agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 100-agent battalion may be managed.'
      ),
      'mvp55_100_agent_runtime_battalion'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 100-agent battalion may be managed.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with deactivated as (
    update runtime_battalion_agents
    set status = 'deactivated',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(deactivated)), '[]'::jsonb) into v_agents
  from deactivated;

  with event_rows as (
    insert into runtime_battalion_activation_events (
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
      'BATTALION_AGENT_DEACTIVATED',
      'Controlled battalion agent deactivated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_hundred_agent_battalion',
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp55_100_agent_runtime_battalion'
    from runtime_battalion_agents agent
    where agent.agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(event_rows)), '[]'::jsonb) into v_events
  from event_rows;

  select count(*) into v_active_count
  from runtime_battalion_agents
  where status = 'active';

  select count(distinct lane_key) into v_active_lane_count
  from runtime_battalion_agents
  where status = 'active';

  update runtime_kernel_config
  set value = to_jsonb(v_active_count),
      updated_at = now()
  where key = 'live_runtime_agents_enabled';

  update runtime_kernel_config
  set value = to_jsonb(v_active_lane_count),
      updated_at = now()
  where key = 'active_lanes_count';

  update runtime_kernel_config
  set value = to_jsonb(greatest(10 - v_active_lane_count, 0)),
      updated_at = now()
  where key = 'inactive_lanes_count';

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'audit_events', v_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_battalion_size', 100,
      'live_runtime_agents_enabled', v_active_count,
      'max_activation_batch_size', 100,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_lanes_count', v_active_lane_count,
      'inactive_lanes_count', greatest(10 - v_active_lane_count, 0),
      'activation_mode', 'supervised_hundred_agent_battalion'
    )
  );
end;
$$;

create or replace function runtime_battalion_activate_lane(
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

  v_agent_ids := runtime_battalion_lane_agent_ids(v_lane_key);

  if coalesce(array_length(v_agent_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_LANE_BLOCKED');
  end if;

  return runtime_battalion_activate_agents(v_agent_ids, p_actor, p_reason, 10, false);
end;
$$;

create or replace function runtime_battalion_deactivate_lane(
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

  v_agent_ids := runtime_battalion_lane_agent_ids(v_lane_key);

  if coalesce(array_length(v_agent_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_LANE_BLOCKED');
  end if;

  return runtime_battalion_deactivate_agents(v_agent_ids, p_actor, p_reason, 10, false);
end;
$$;

create or replace function runtime_battalion_record_heartbeat(
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
  v_scope text := coalesce(nullif(btrim(p_scope), ''), 'battalion');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_heartbeat_status text := coalesce(nullif(btrim(p_heartbeat_status), ''), 'healthy');
  v_heartbeat_note text := nullif(btrim(p_heartbeat_note), '');
  v_target_ids text[];
  v_heartbeats jsonb := '[]'::jsonb;
  v_audit runtime_battalion_audit_events%rowtype;
begin
  if v_scope = 'lane' then
    v_target_ids := runtime_battalion_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    select array_agg(agent_id order by agent_id)
    into v_target_ids
    from runtime_battalion_agents;
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_battalion_agents
    set last_heartbeat_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into battalion_heartbeat_events (
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
      'BATTALION_HEARTBEAT',
      'Battalion heartbeat recorded',
      jsonb_build_object(
        'scope', v_scope,
        'lane_key', v_lane_key,
        'heartbeat_status', v_heartbeat_status,
        'heartbeat_note', v_heartbeat_note,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp55_100_agent_runtime_battalion'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_heartbeats
  from inserted;

  insert into runtime_battalion_audit_events (
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
    'BATTALION_HEARTBEAT',
    'Battalion heartbeat recorded',
    jsonb_build_object(
      'scope', v_scope,
      'lane_key', v_lane_key,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0),
      'heartbeat_status', v_heartbeat_status
    ),
    'mvp55_100_agent_runtime_battalion'
  )
  returning * into v_audit;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'heartbeat_events', v_heartbeats,
    'audit_event', to_jsonb(v_audit)
  );
end;
$$;

create or replace function runtime_battalion_create_readiness_note(
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
  v_scope text := coalesce(nullif(btrim(p_scope), ''), 'battalion');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_note_title text := nullif(btrim(p_note_title), '');
  v_note_body text := nullif(btrim(p_note_body), '');
  v_readiness_level text := coalesce(nullif(btrim(p_readiness_level), ''), 'green');
  v_target_ids text[];
  v_notes jsonb := '[]'::jsonb;
  v_audit runtime_battalion_audit_events%rowtype;
begin
  if v_note_title is null or v_note_body is null then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_NOTE_PAYLOAD');
  end if;

  if v_scope = 'lane' then
    v_target_ids := runtime_battalion_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    select array_agg(agent_id order by agent_id)
    into v_target_ids
    from runtime_battalion_agents;
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_battalion_agents
    set last_readiness_note_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into battalion_readiness_notes (
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
      'BATTALION_READINESS_NOTE_CREATED',
      'Battalion readiness note created',
      jsonb_build_object(
        'scope', v_scope,
        'lane_key', v_lane_key,
        'note_title', v_note_title,
        'note_body', v_note_body,
        'readiness_level', v_readiness_level,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp55_100_agent_runtime_battalion'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_notes
  from inserted;

  insert into runtime_battalion_audit_events (
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
    'BATTALION_READINESS_NOTE_CREATED',
    'Battalion readiness note recorded',
    jsonb_build_object(
      'scope', v_scope,
      'lane_key', v_lane_key,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0),
      'readiness_level', v_readiness_level
    ),
    'mvp55_100_agent_runtime_battalion'
  )
  returning * into v_audit;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'readiness_notes', v_notes,
    'audit_event', to_jsonb(v_audit)
  );
end;
$$;
