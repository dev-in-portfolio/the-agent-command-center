-- MVP-56 250-agent runtime company.
-- This migration defines persistence only. It does not enable command execution, deploy execution, rollback execution, alert sending, or arbitrary activation beyond the approved 250-agent company.
-- Approved company IDs: mvp56_company_agent_001 through mvp56_company_agent_250.
-- Lane set: intake_lane_01 through command_center_lane_01 across 25 lanes.

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

create table if not exists runtime_company_lanes (
  lane_key text primary key,
  lane_name text not null,
  lane_order integer not null unique,
  lane_description text not null default '',
  allowed_task text not null default 'send heartbeat and create readiness note only',
  status text not null default 'inactive',
  kill_switch_visible boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_company_lanes_status_check
    check (status in ('inactive', 'active', 'mixed', 'disabled'))
);

create table if not exists runtime_company_agents (
  agent_id text primary key,
  agent_name text not null,
  lane_key text not null references runtime_company_lanes(lane_key) on delete cascade,
  lane_position integer not null,
  allowed_task text not null default 'send heartbeat and create readiness note only',
  execution_permissions text not null default 'none',
  external_api_permissions text not null default 'none',
  database_write_permissions text not null default 'audit_event_only',
  status text not null default 'inactive',
  is_supervised_company_agent boolean not null default true,
  kill_switch_visible boolean not null default true,
  last_heartbeat_at timestamptz,
  last_readiness_note_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_company_agents_status_check
    check (status in ('inactive', 'active', 'deactivated', 'blocked', 'disabled')),
  constraint runtime_company_agents_lane_position_check
    check (lane_position between 1 and 10),
  constraint runtime_company_agents_lane_position_unique
    unique (lane_key, lane_position)
);

create table if not exists runtime_company_activation_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_company_lanes(lane_key) on delete cascade,
  agent_id text references runtime_company_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp56_250_agent_runtime_company'
);

create table if not exists company_heartbeat_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_company_lanes(lane_key) on delete cascade,
  agent_id text references runtime_company_agents(agent_id) on delete cascade,
  actor text,
  scope text not null default 'company',
  heartbeat_status text not null default 'healthy',
  heartbeat_note text,
  event_type text not null default 'COMPANY_HEARTBEAT',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp56_250_agent_runtime_company'
);

create table if not exists company_readiness_notes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_company_lanes(lane_key) on delete cascade,
  agent_id text references runtime_company_agents(agent_id) on delete cascade,
  actor text,
  scope text not null default 'company',
  note_title text not null,
  note_body text not null,
  readiness_level text not null default 'green',
  event_type text not null default 'COMPANY_READINESS_NOTE_CREATED',
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp56_250_agent_runtime_company'
);

create table if not exists runtime_company_audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  lane_key text references runtime_company_lanes(lane_key) on delete cascade,
  agent_id text references runtime_company_agents(agent_id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp56_250_agent_runtime_company'
);

create index if not exists runtime_company_agents_lane_key_idx on runtime_company_agents (lane_key);
create index if not exists runtime_company_agents_status_idx on runtime_company_agents (status);
create index if not exists runtime_company_activation_events_created_at_idx on runtime_company_activation_events (created_at desc);
create index if not exists runtime_company_activation_events_lane_key_idx on runtime_company_activation_events (lane_key);
create index if not exists company_heartbeat_events_created_at_idx on company_heartbeat_events (created_at desc);
create index if not exists company_heartbeat_events_lane_key_idx on company_heartbeat_events (lane_key);
create index if not exists company_readiness_notes_created_at_idx on company_readiness_notes (created_at desc);
create index if not exists company_readiness_notes_lane_key_idx on company_readiness_notes (lane_key);
create index if not exists runtime_company_audit_events_created_at_idx on runtime_company_audit_events (created_at desc);
create index if not exists runtime_company_audit_events_lane_key_idx on runtime_company_audit_events (lane_key);

insert into runtime_company_lanes (lane_key, lane_name, lane_order, lane_description, allowed_task, status, kill_switch_visible)
values
  ('intake_lane_01', 'Intake Lane 01', 1, 'Initial controlled intake and queue triage lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('intake_lane_02', 'Intake Lane 02', 2, 'Second intake and intake review lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('validation_lane_01', 'Validation Lane 01', 3, 'Controlled validation and readiness lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('validation_lane_02', 'Validation Lane 02', 4, 'Second validation and acceptance lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('audit_lane_01', 'Audit Lane 01', 5, 'Audit visibility and recordkeeping lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('audit_lane_02', 'Audit Lane 02', 6, 'Second audit and traceability lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('approval_lane_01', 'Approval Lane 01', 7, 'Approval review and decision lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('approval_lane_02', 'Approval Lane 02', 8, 'Second approval and decision lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('dry_run_lane_01', 'Dry Run Lane 01', 9, 'Dry-run and preview lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('dry_run_lane_02', 'Dry Run Lane 02', 10, 'Second dry-run and preview lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('monitoring_lane_01', 'Monitoring Lane 01', 11, 'Monitoring and readiness tracking lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('monitoring_lane_02', 'Monitoring Lane 02', 12, 'Second monitoring and readiness lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('safety_lane_01', 'Safety Lane 01', 13, 'Safety boundary and kill-switch lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('safety_lane_02', 'Safety Lane 02', 14, 'Second safety boundary lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('registry_lane_01', 'Registry Lane 01', 15, 'Registry and roster verification lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('registry_lane_02', 'Registry Lane 02', 16, 'Second registry and roster lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('review_lane_01', 'Review Lane 01', 17, 'Human review and QA lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('review_lane_02', 'Review Lane 02', 18, 'Second human review lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('reporting_lane_01', 'Reporting Lane 01', 19, 'Reporting and summary lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('reporting_lane_02', 'Reporting Lane 02', 20, 'Second reporting and summary lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('compliance_lane_01', 'Compliance Lane 01', 21, 'Compliance and controls lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('compliance_lane_02', 'Compliance Lane 02', 22, 'Second compliance and controls lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('incident_lane_01', 'Incident Lane 01', 23, 'Incident triage and escalation lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('readiness_lane_01', 'Readiness Lane 01', 24, 'Readiness and signoff lane.', 'send heartbeat and create readiness note only', 'inactive', true),
  ('command_center_lane_01', 'Command Center Lane 01', 25, 'Command center coordination lane.', 'send heartbeat and create readiness note only', 'inactive', true)
on conflict (lane_key) do update
set lane_name = excluded.lane_name,
    lane_order = excluded.lane_order,
    lane_description = excluded.lane_description,
    allowed_task = excluded.allowed_task,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

insert into runtime_company_agents (
  agent_id,
  agent_name,
  lane_key,
  lane_position,
  allowed_task,
  execution_permissions,
  external_api_permissions,
  database_write_permissions,
  status,
  is_supervised_company_agent,
  kill_switch_visible
)
select
  format('mvp56_company_agent_%s', lpad(gs::text, 3, '0')) as agent_id,
  format('Company Agent %s', lpad(gs::text, 3, '0')) as agent_name,
  lane.lane_key,
  ((gs - 1) % 10) + 1 as lane_position,
  'send heartbeat and create readiness note only',
  'none',
  'none',
  'audit_event_only',
  'inactive',
  true,
  true
from generate_series(1, 250) as gs
join runtime_company_lanes lane
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
    is_supervised_company_agent = excluded.is_supervised_company_agent,
    kill_switch_visible = excluded.kill_switch_visible,
    updated_at = now();

drop trigger if exists runtime_company_lanes_touch_updated_at on runtime_company_lanes;
create trigger runtime_company_lanes_touch_updated_at
before update on runtime_company_lanes
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_company_agents_touch_updated_at on runtime_company_agents;
create trigger runtime_company_agents_touch_updated_at
before update on runtime_company_agents
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_company_lanes enable row level security;
alter table if exists runtime_company_agents enable row level security;
alter table if exists runtime_company_activation_events enable row level security;
alter table if exists company_heartbeat_events enable row level security;
alter table if exists company_readiness_notes enable row level security;
alter table if exists runtime_company_audit_events enable row level security;

insert into runtime_kernel_config (key, value)
values
  ('runtime_company_size', '250'::jsonb),
  ('max_activation_batch_size', '250'::jsonb),
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
  ('inactive_lanes_count', '25'::jsonb),
  ('activation_mode', '"supervised_two_hundred_fifty_agent_company"'::jsonb),
  ('heartbeat_event_count', '0'::jsonb),
  ('readiness_note_count', '0'::jsonb),
  ('activation_event_count', '0'::jsonb),
  ('audit_event_count', '0'::jsonb),
  (
    'company_health_rollup',
    jsonb_build_object(
      'company_health', 'inactive',
      'active_agents', 0,
      'inactive_agents', 250,
      'active_lanes', 0,
      'inactive_lanes', 25,
      'heartbeat_event_count', 0,
      'readiness_note_count', 0,
      'activation_event_count', 0,
      'audit_event_count', 0,
      'runtime_company_size', 250,
      'total_registered_agents', 47979
    )
  )
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

create or replace function runtime_company_lane_agent_ids(
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
  from runtime_company_agents
  where lane_key = v_lane_key;

  return coalesce(v_agent_ids, '{}'::text[]);
end;
$$;

create or replace function runtime_company_sync_rollups()
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
  v_company_health text := 'inactive';
  v_rollup jsonb := '{}'::jsonb;
begin
  select count(*) into v_active_count
  from runtime_company_agents
  where status = 'active';

  select count(distinct lane_key) into v_active_lane_count
  from runtime_company_agents
  where status = 'active';

  select count(*) into v_heartbeat_count from company_heartbeat_events;
  select count(*) into v_readiness_note_count from company_readiness_notes;
  select count(*) into v_activation_event_count from runtime_company_activation_events;
  select count(*) into v_audit_event_count from runtime_company_audit_events;

  if v_active_count = 0 then
    v_company_health := 'inactive';
  elsif v_active_count >= 250 and v_active_lane_count >= 25 then
    v_company_health := 'healthy';
  else
    v_company_health := 'partial';
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
  set value = to_jsonb(greatest(25 - v_active_lane_count, 0)),
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
    'company_health', v_company_health,
    'active_agents', v_active_count,
    'inactive_agents', greatest(250 - v_active_count, 0),
    'active_lanes', v_active_lane_count,
    'inactive_lanes', greatest(25 - v_active_lane_count, 0),
    'heartbeat_event_count', v_heartbeat_count,
    'readiness_note_count', v_readiness_note_count,
    'activation_event_count', v_activation_event_count,
    'audit_event_count', v_audit_event_count,
    'runtime_company_size', 250,
    'total_registered_agents', 47979
  );

  update runtime_kernel_config
  set value = v_rollup,
      updated_at = now()
  where key = 'company_health_rollup';

  return v_rollup;
end;
$$;

create or replace function runtime_company_activate_agents(
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
  v_limit integer := 250;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_rollup jsonb := '{}'::jsonb;
  v_audit runtime_company_audit_events%rowtype;
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
    v_blocked_reason := 'batch_size exceeds 250';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved company agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_company_audit_events (
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
      'COMPANY_ACTIVATION_BLOCKED',
      'Company activation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp56_250_agent_runtime_company'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'COMPANY_ACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_company_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_company_audit_events (
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
      'Unknown company agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 250-agent company may be activated.'
      ),
      'mvp56_250_agent_runtime_company'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 250-agent company may be activated.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with activated as (
    update runtime_company_agents
    set status = 'active',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(activated)), '[]'::jsonb) into v_agents
  from activated;

  with event_rows as (
    insert into runtime_company_activation_events (
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
      'COMPANY_AGENT_ACTIVATED',
      'Controlled company agent activated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_two_hundred_fifty_agent_company',
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp56_250_agent_runtime_company'
    from runtime_company_agents agent
    where agent.agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(event_rows)), '[]'::jsonb) into v_events
  from event_rows;

  v_rollup := runtime_company_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'audit_events', v_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_company_size', 250,
      'live_runtime_agents_enabled', (v_rollup ->> 'active_agents')::integer,
      'max_activation_batch_size', 250,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_lanes_count', (v_rollup ->> 'active_lanes')::integer,
      'inactive_lanes_count', (v_rollup ->> 'inactive_lanes')::integer,
      'activation_mode', 'supervised_two_hundred_fifty_agent_company',
      'company_health_rollup', v_rollup
    ),
    'company_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_company_deactivate_agents(
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
  v_limit integer := 250;
  v_effective_batch_size integer := coalesce(p_batch_size, 0);
  v_blocked_reason text := null;
  v_agents jsonb := '[]'::jsonb;
  v_events jsonb := '[]'::jsonb;
  v_rollup jsonb := '{}'::jsonb;
  v_audit runtime_company_audit_events%rowtype;
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
    v_blocked_reason := 'batch_size exceeds 250';
  elsif coalesce(array_length(v_requested_ids, 1), 0) = 0 then
    v_blocked_reason := 'No approved company agent IDs were supplied.';
  end if;

  if v_blocked_reason is not null then
    insert into runtime_company_audit_events (
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
      'COMPANY_DEACTIVATION_BLOCKED',
      'Company deactivation request blocked',
      jsonb_build_object(
        'reason', v_blocked_reason,
        'requested_agent_ids', to_jsonb(coalesce(v_requested_ids, '{}'::text[])),
        'batch_size', v_effective_batch_size,
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true
      ),
      'mvp56_250_agent_runtime_company'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'COMPANY_DEACTIVATION_BLOCKED',
      'reason', v_blocked_reason,
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  select array_agg(agent_id order by agent_id)
  into v_unknown_ids
  from (
    select unnest(v_requested_ids) as agent_id
    except
    select agent_id from runtime_company_agents
  ) missing;

  if coalesce(array_length(v_unknown_ids, 1), 0) > 0 then
    insert into runtime_company_audit_events (
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
      'Unknown company agent IDs were rejected',
      jsonb_build_object(
        'unknown_agent_ids', to_jsonb(v_unknown_ids),
        'requested_agent_ids', to_jsonb(v_requested_ids),
        'batch_size', v_effective_batch_size,
        'reason', 'Only the approved 250-agent company may be managed.'
      ),
      'mvp56_250_agent_runtime_company'
    )
    returning * into v_audit;

    return jsonb_build_object(
      'ok', false,
      'blocked', true,
      'error', 'UNKNOWN_AGENT_BLOCKED',
      'reason', 'Only the approved 250-agent company may be managed.',
      'unknown_agent_ids', to_jsonb(v_unknown_ids),
      'audit_event', to_jsonb(v_audit)
    );
  end if;

  with deactivated as (
    update runtime_company_agents
    set status = 'deactivated',
        updated_at = now()
    where agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(deactivated)), '[]'::jsonb) into v_agents
  from deactivated;

  with event_rows as (
    insert into runtime_company_activation_events (
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
      'COMPANY_AGENT_DEACTIVATED',
      'Controlled company agent deactivated',
      jsonb_build_object(
        'reason', v_reason,
        'activation_mode', 'supervised_two_hundred_fifty_agent_company',
        'max_activation_batch_size', v_limit,
        'full_47979_activation_blocked', true,
        'execution_permissions', 'none',
        'external_api_permissions', 'none',
        'database_write_permissions', 'audit_event_only'
      ),
      'mvp56_250_agent_runtime_company'
    from runtime_company_agents agent
    where agent.agent_id = any(v_requested_ids)
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(event_rows)), '[]'::jsonb) into v_events
  from event_rows;

  v_rollup := runtime_company_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'agents', v_agents,
    'audit_events', v_events,
    'backend_status', jsonb_build_object(
      'runtime_activation_started', false,
      'runtime_company_size', 250,
      'live_runtime_agents_enabled', (v_rollup ->> 'active_agents')::integer,
      'max_activation_batch_size', 250,
      'full_47979_activation_blocked', true,
      'total_registered_agents', 47979,
      'command_execution_enabled', false,
      'deploy_execution_enabled', false,
      'rollback_execution_enabled', false,
      'alert_sending_enabled', false,
      'kill_switch_visible', true,
      'active_lanes_count', (v_rollup ->> 'active_lanes')::integer,
      'inactive_lanes_count', (v_rollup ->> 'inactive_lanes')::integer,
      'activation_mode', 'supervised_two_hundred_fifty_agent_company',
      'company_health_rollup', v_rollup
    ),
    'company_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_company_activate_lane(
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

  v_agent_ids := runtime_company_lane_agent_ids(v_lane_key);

  if coalesce(array_length(v_agent_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_LANE_BLOCKED');
  end if;

  return runtime_company_activate_agents(v_agent_ids, p_actor, p_reason, 10, false);
end;
$$;

create or replace function runtime_company_deactivate_lane(
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

  v_agent_ids := runtime_company_lane_agent_ids(v_lane_key);

  if coalesce(array_length(v_agent_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_LANE_BLOCKED');
  end if;

  return runtime_company_deactivate_agents(v_agent_ids, p_actor, p_reason, 10, false);
end;
$$;

create or replace function runtime_company_record_heartbeat(
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
  v_scope text := coalesce(nullif(btrim(p_scope), ''), 'company');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_heartbeat_status text := coalesce(nullif(btrim(p_heartbeat_status), ''), 'healthy');
  v_heartbeat_note text := nullif(btrim(p_heartbeat_note), '');
  v_target_ids text[];
  v_heartbeats jsonb := '[]'::jsonb;
  v_audit runtime_company_audit_events%rowtype;
  v_rollup jsonb := '{}'::jsonb;
begin
  if v_scope = 'lane' then
    v_target_ids := runtime_company_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    select array_agg(agent_id order by agent_id)
    into v_target_ids
    from runtime_company_agents;
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_company_agents
    set last_heartbeat_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into company_heartbeat_events (
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
      'COMPANY_HEARTBEAT',
      'Company heartbeat recorded',
      jsonb_build_object(
        'scope', v_scope,
        'lane_key', v_lane_key,
        'heartbeat_status', v_heartbeat_status,
        'heartbeat_note', v_heartbeat_note,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp56_250_agent_runtime_company'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_heartbeats
  from inserted;

  insert into runtime_company_audit_events (
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
    'COMPANY_HEARTBEAT',
    'Company heartbeat recorded',
    jsonb_build_object(
      'scope', v_scope,
      'lane_key', v_lane_key,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0),
      'heartbeat_status', v_heartbeat_status
    ),
    'mvp56_250_agent_runtime_company'
  )
  returning * into v_audit;

  v_rollup := runtime_company_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'heartbeat_events', v_heartbeats,
    'audit_event', to_jsonb(v_audit),
    'company_rollup', v_rollup
  );
end;
$$;

create or replace function runtime_company_create_readiness_note(
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
  v_scope text := coalesce(nullif(btrim(p_scope), ''), 'company');
  v_lane_key text := nullif(btrim(p_lane_key), '');
  v_agent_id text := nullif(btrim(p_agent_id), '');
  v_actor text := coalesce(nullif(btrim(p_actor), ''), 'operator');
  v_note_title text := nullif(btrim(p_note_title), '');
  v_note_body text := nullif(btrim(p_note_body), '');
  v_readiness_level text := coalesce(nullif(btrim(p_readiness_level), ''), 'green');
  v_target_ids text[];
  v_notes jsonb := '[]'::jsonb;
  v_audit runtime_company_audit_events%rowtype;
  v_rollup jsonb := '{}'::jsonb;
begin
  if v_note_title is null or v_note_body is null then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'INVALID_NOTE_PAYLOAD');
  end if;

  if v_scope = 'lane' then
    v_target_ids := runtime_company_lane_agent_ids(v_lane_key);
  elsif v_scope = 'agent' then
    v_target_ids := array_remove(array[v_agent_id], null);
  else
    select array_agg(agent_id order by agent_id)
    into v_target_ids
    from runtime_company_agents;
  end if;

  if coalesce(array_length(v_target_ids, 1), 0) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'UNKNOWN_SCOPE_OR_TARGET');
  end if;

  with updated_agents as (
    update runtime_company_agents
    set last_readiness_note_at = now(),
        updated_at = now()
    where agent_id = any(v_target_ids)
    returning *
  ),
  inserted as (
    insert into company_readiness_notes (
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
      'COMPANY_READINESS_NOTE_CREATED',
      'Company readiness note created',
      jsonb_build_object(
        'scope', v_scope,
        'lane_key', v_lane_key,
        'note_title', v_note_title,
        'note_body', v_note_body,
        'readiness_level', v_readiness_level,
        'target_agent_count', coalesce(array_length(v_target_ids, 1), 0)
      ),
      'mvp56_250_agent_runtime_company'
    from updated_agents agent
    returning *
  )
  select coalesce(jsonb_agg(to_jsonb(inserted)), '[]'::jsonb) into v_notes
  from inserted;

  insert into runtime_company_audit_events (
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
    'COMPANY_READINESS_NOTE_CREATED',
    'Company readiness note recorded',
    jsonb_build_object(
      'scope', v_scope,
      'lane_key', v_lane_key,
      'target_agent_count', coalesce(array_length(v_target_ids, 1), 0),
      'readiness_level', v_readiness_level
    ),
    'mvp56_250_agent_runtime_company'
  )
  returning * into v_audit;

  v_rollup := runtime_company_sync_rollups();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'readiness_notes', v_notes,
    'audit_event', to_jsonb(v_audit),
    'company_rollup', v_rollup
  );
end;
$$;
