-- MVP-61 5,000-agent department-gated runtime corps.
-- 5,000 is a cap, not an automatic activation.
-- Department-gated activation is required.
-- Raw fleet activation is blocked.
-- Full 47,979-agent activation remains blocked.

create extension if not exists pgcrypto;

create or replace function runtime_corps_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists runtime_corps_limits (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

create trigger runtime_corps_limits_touch_updated_at
before update on runtime_corps_limits
for each row execute function runtime_corps_touch_updated_at();

create table if not exists runtime_corps_cohorts (
  cohort_id uuid primary key default gen_random_uuid(),
  cohort_name text not null,
  department_id text not null references runtime_departments(department_id) on delete cascade,
  requested_agent_count integer not null,
  activated_agent_count integer not null default 0,
  cohort_status text not null default 'requested',
  actor text,
  reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp61_5000_agent_department_gated_runtime_corps',
  constraint runtime_corps_cohorts_status_check check (cohort_status in ('requested', 'approved', 'active', 'partially_active', 'deactivated', 'denied', 'blocked')),
  constraint runtime_corps_cohorts_requested_check check (requested_agent_count >= 0 and requested_agent_count <= 500),
  constraint runtime_corps_cohorts_active_check check (activated_agent_count >= 0 and activated_agent_count <= requested_agent_count)
);

create trigger runtime_corps_cohorts_touch_updated_at
before update on runtime_corps_cohorts
for each row execute function runtime_corps_touch_updated_at();

create index if not exists runtime_corps_cohorts_department_id_idx on runtime_corps_cohorts (department_id);
create index if not exists runtime_corps_cohorts_status_idx on runtime_corps_cohorts (cohort_status);
create index if not exists runtime_corps_cohorts_created_at_idx on runtime_corps_cohorts (created_at desc);

create table if not exists runtime_corps_cohort_chunks (
  chunk_id uuid primary key default gen_random_uuid(),
  cohort_id uuid not null references runtime_corps_cohorts(cohort_id) on delete cascade,
  department_id text not null references runtime_departments(department_id) on delete cascade,
  chunk_index integer not null,
  requested_agent_count integer not null,
  activated_agent_count integer not null default 0,
  chunk_status text not null default 'requested',
  actor text,
  reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp61_5000_agent_department_gated_runtime_corps',
  constraint runtime_corps_cohort_chunks_status_check check (chunk_status in ('requested', 'active', 'deactivated', 'blocked')),
  constraint runtime_corps_cohort_chunks_requested_check check (requested_agent_count >= 0 and requested_agent_count <= 250),
  constraint runtime_corps_cohort_chunks_active_check check (activated_agent_count >= 0 and activated_agent_count <= requested_agent_count),
  constraint runtime_corps_cohort_chunks_index_check check (chunk_index >= 1)
);

create trigger runtime_corps_cohort_chunks_touch_updated_at
before update on runtime_corps_cohort_chunks
for each row execute function runtime_corps_touch_updated_at();

create index if not exists runtime_corps_cohort_chunks_cohort_id_idx on runtime_corps_cohort_chunks (cohort_id);
create index if not exists runtime_corps_cohort_chunks_department_id_idx on runtime_corps_cohort_chunks (department_id);
create index if not exists runtime_corps_cohort_chunks_created_at_idx on runtime_corps_cohort_chunks (created_at desc);

create table if not exists runtime_corps_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  department_id text references runtime_departments(department_id) on delete cascade,
  cohort_id uuid references runtime_corps_cohorts(cohort_id) on delete set null,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp61_5000_agent_department_gated_runtime_corps'
);

create index if not exists runtime_corps_events_department_id_idx on runtime_corps_events (department_id);
create index if not exists runtime_corps_events_cohort_id_idx on runtime_corps_events (cohort_id);
create index if not exists runtime_corps_events_created_at_idx on runtime_corps_events (created_at desc);

create table if not exists runtime_corps_rollups (
  rollup_id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  total_registered_agents integer not null default 47979,
  total_departments integer not null default 1777,
  global_live_agent_cap integer not null default 5000,
  current_live_runtime_agents integer not null default 0,
  approved_department_gates integer not null default 0,
  active_department_gates integer not null default 0,
  active_cohorts integer not null default 0,
  full_47979_activation_blocked boolean not null default true,
  command_execution_enabled boolean not null default false,
  deploy_execution_enabled boolean not null default false,
  rollback_execution_enabled boolean not null default false,
  alert_sending_enabled boolean not null default false,
  source text not null default 'mvp61_5000_agent_department_gated_runtime_corps'
);

create index if not exists runtime_corps_rollups_created_at_idx on runtime_corps_rollups (created_at desc);

create or replace function runtime_corps_current_live_count()
returns integer
language sql
stable
as $$
  select
    coalesce((select sum(currently_active_agents) from department_runtime_gates), 0)::integer
    +
    coalesce((select sum(activated_agent_count) from runtime_corps_cohorts where cohort_status in ('active', 'partially_active')), 0)::integer;
$$;

create or replace function runtime_corps_sync_state(p_live_count integer)
returns void
language plpgsql
as $$
declare
  v_live_count integer := coalesce(p_live_count, 0);
  v_total_departments integer;
  v_approved_department_gates integer;
  v_active_department_gates integer;
  v_active_cohorts integer;
begin
  select count(*) into v_total_departments from runtime_departments;
  select count(*) into v_approved_department_gates from department_runtime_gates where gate_status in ('approved', 'active');
  select count(*) into v_active_department_gates from department_runtime_gates where gate_status = 'active';
  select count(*) into v_active_cohorts from runtime_corps_cohorts where cohort_status in ('active', 'partially_active');

  insert into runtime_corps_limits (key, value) values
    ('mvp61_global_live_agent_cap', to_jsonb(5000)),
    ('max_department_activation_cap', to_jsonb(250)),
    ('max_cohort_activation_size', to_jsonb(500)),
    ('max_operation_chunk_size', to_jsonb(250)),
    ('full_47979_activation_blocked', to_jsonb(true)),
    ('department_gated_activation_required', to_jsonb(true)),
    ('command_execution_enabled', to_jsonb(false)),
    ('deploy_execution_enabled', to_jsonb(false)),
    ('rollback_execution_enabled', to_jsonb(false)),
    ('alert_sending_enabled', to_jsonb(false)),
    ('current_live_runtime_agents', to_jsonb(v_live_count))
  on conflict (key) do update set
    value = excluded.value,
    updated_at = now();

  insert into runtime_kernel_config (key, value) values
    ('mvp61_department_gated_runtime_corps_ready', to_jsonb(true)),
    ('mvp61_global_live_agent_cap', to_jsonb(5000)),
    ('max_cohort_activation_size', to_jsonb(500)),
    ('max_operation_chunk_size', to_jsonb(250)),
    ('department_gated_activation_required', to_jsonb(true)),
    ('full_47979_activation_blocked', to_jsonb(true)),
    ('command_execution_enabled', to_jsonb(false)),
    ('deploy_execution_enabled', to_jsonb(false)),
    ('rollback_execution_enabled', to_jsonb(false)),
    ('alert_sending_enabled', to_jsonb(false)),
    ('live_runtime_agents_enabled', to_jsonb(v_live_count)),
    ('total_registered_agents', to_jsonb(47979)),
    ('total_departments', to_jsonb(coalesce(v_total_departments, 1777)))
  on conflict (key) do update set
    value = excluded.value,
    updated_at = now();

  insert into runtime_corps_rollups (
    total_registered_agents,
    total_departments,
    global_live_agent_cap,
    current_live_runtime_agents,
    approved_department_gates,
    active_department_gates,
    active_cohorts,
    full_47979_activation_blocked,
    command_execution_enabled,
    deploy_execution_enabled,
    rollback_execution_enabled,
    alert_sending_enabled,
    source
  ) values (
    47979,
    coalesce(v_total_departments, 1777),
    5000,
    v_live_count,
    coalesce(v_approved_department_gates, 0),
    coalesce(v_active_department_gates, 0),
    coalesce(v_active_cohorts, 0),
    true,
    false,
    false,
    false,
    false,
    'mvp61_5000_agent_department_gated_runtime_corps'
  );
end;
$$;

create or replace function runtime_corps_activate_department_cohort(
  p_department_id text,
  p_requested_agent_count integer,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  dept record;
  gate_row record;
  lane_count integer;
  department_live_count integer;
  live_count integer;
  cohort_row record;
  event_row record;
  chunk_index integer := 1;
  chunk_size integer;
  remaining integer;
  activated_total integer := 0;
  reason_text text := btrim(coalesce(p_reason, ''));
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  select * into gate_row
  from department_runtime_gates
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_GATE_NOT_FOUND', 'message', 'Department gate not found.');
  end if;

  select count(*) into lane_count
  from runtime_department_lane_assignments
  where department_id = p_department_id;

  if lane_count = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_LANE_MISSING', 'message', 'Department must have a mapped runtime lane.');
  end if;

  if dept.runtime_status <> 'eligible_for_supervised_runtime' or not coalesce(dept.activation_eligible, false) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_ELIGIBLE', 'message', 'Department must be eligible_for_supervised_runtime and activation_eligible=true.');
  end if;

  if gate_row.gate_status not in ('approved', 'active') then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_GATE_NOT_APPROVED', 'message', 'Department gate must be approved or active.');
  end if;

  if p_requested_agent_count is null or p_requested_agent_count < 1 or p_requested_agent_count > 500 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'REQUESTED_AGENT_COUNT_OUT_OF_RANGE', 'message', 'requested_agent_count must be between 1 and 500.');
  end if;

  if p_requested_agent_count > coalesce(gate_row.activation_cap, 0) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'REQUESTED_AGENT_COUNT_EXCEEDS_DEPARTMENT_CAP', 'message', 'requested_agent_count must stay within the department cap.');
  end if;

  select coalesce(sum(activated_agent_count), 0)::integer into department_live_count
  from runtime_corps_cohorts
  where department_id = p_department_id
    and cohort_status in ('active', 'partially_active');

  if department_live_count + p_requested_agent_count > coalesce(gate_row.activation_cap, 0) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_CAP_EXCEEDED', 'message', 'Requested agents would exceed the department cap.');
  end if;

  live_count := runtime_corps_current_live_count();
  if live_count + p_requested_agent_count > 5000 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'GLOBAL_CAP_EXCEEDED', 'message', 'Requested agents would exceed the 5,000-agent global cap.');
  end if;

  insert into runtime_corps_cohorts (
    cohort_name,
    department_id,
    requested_agent_count,
    activated_agent_count,
    cohort_status,
    actor,
    reason,
    source
  ) values (
    format('%s-cohort-%s', p_department_id, to_char(clock_timestamp(), 'YYYYMMDDHH24MISSMS')),
    p_department_id,
    p_requested_agent_count,
    p_requested_agent_count,
    'active',
    actor_text,
    reason_text,
    'mvp61_5000_agent_department_gated_runtime_corps'
  )
  returning * into cohort_row;

  remaining := p_requested_agent_count;
  while remaining > 0 loop
    chunk_size := least(remaining, 250);
    insert into runtime_corps_cohort_chunks (
      cohort_id,
      department_id,
      chunk_index,
      requested_agent_count,
      activated_agent_count,
      chunk_status,
      actor,
      reason,
      source
    ) values (
      cohort_row.cohort_id,
      p_department_id,
      chunk_index,
      chunk_size,
      chunk_size,
      'active',
      actor_text,
      reason_text,
      'mvp61_5000_agent_department_gated_runtime_corps'
    );
    remaining := remaining - chunk_size;
    chunk_index := chunk_index + 1;
    activated_total := activated_total + chunk_size;
  end loop;

  insert into runtime_corps_events (
    department_id,
    cohort_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    cohort_row.cohort_id,
    actor_text,
    'RUNTIME_CORPS_COHORT_ACTIVATED',
    format('Activated %s supervised runtime agents for department %s.', p_requested_agent_count, p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'requested_agent_count', p_requested_agent_count,
      'activated_agent_count', activated_total,
      'global_live_runtime_agents_before', live_count,
      'global_live_runtime_agents_after', runtime_corps_current_live_count()
    ),
    'mvp61_5000_agent_department_gated_runtime_corps'
  )
  returning * into event_row;

  perform runtime_corps_sync_state(runtime_corps_current_live_count());

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'department_id', p_department_id,
    'gate', to_jsonb(gate_row),
    'cohort', to_jsonb(cohort_row),
    'event', to_jsonb(event_row),
    'chunk_count', chunk_index - 1,
    'live_runtime_agents_enabled', runtime_corps_current_live_count(),
    'global_live_agent_cap', 5000,
    'max_cohort_activation_size', 500,
    'max_operation_chunk_size', 250
  );
end;
$$;

create or replace function runtime_corps_deactivate_cohort(p_cohort_id uuid, p_actor text, p_reason text)
returns jsonb
language plpgsql
as $$
declare
  cohort_row record;
  event_row record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
begin
  select * into cohort_row
  from runtime_corps_cohorts
  where cohort_id = p_cohort_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'COHORT_NOT_FOUND', 'message', 'Cohort not found.');
  end if;

  update runtime_corps_cohort_chunks
  set chunk_status = 'deactivated',
      activated_agent_count = 0
  where cohort_id = p_cohort_id;

  update runtime_corps_cohorts
  set cohort_status = 'deactivated',
      activated_agent_count = 0,
      actor = coalesce(actor, actor_text),
      reason = coalesce(nullif(reason_text, ''), reason)
  where cohort_id = p_cohort_id
  returning * into cohort_row;

  insert into runtime_corps_events (
    department_id,
    cohort_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    cohort_row.department_id,
    cohort_row.cohort_id,
    actor_text,
    'RUNTIME_CORPS_COHORT_DEACTIVATED',
    format('Deactivated supervised runtime cohort %s for department %s.', cohort_row.cohort_id, cohort_row.department_id),
    jsonb_build_object(
      'department_id', cohort_row.department_id,
      'cohort_id', cohort_row.cohort_id,
      'reason', reason_text
    ),
    'mvp61_5000_agent_department_gated_runtime_corps'
  )
  returning * into event_row;

  perform runtime_corps_sync_state(runtime_corps_current_live_count());

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'cohort', to_jsonb(cohort_row),
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', runtime_corps_current_live_count(),
    'global_live_agent_cap', 5000
  );
end;
$$;

create or replace function runtime_corps_deactivate_department_cohorts(p_department_id text, p_actor text, p_reason text)
returns jsonb
language plpgsql
as $$
declare
  dept record;
  cohort_ids uuid[];
  active_count integer;
  updated_count integer := 0;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
  event_row record;
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  select coalesce(array_agg(cohort_id), '{}'::uuid[]), count(*)
  into cohort_ids, active_count
  from runtime_corps_cohorts
  where department_id = p_department_id
    and cohort_status in ('active', 'partially_active');

  if active_count > 0 then
    update runtime_corps_cohort_chunks
    set chunk_status = 'deactivated',
        activated_agent_count = 0
    where cohort_id = any(cohort_ids);

    update runtime_corps_cohorts
    set cohort_status = 'deactivated',
        activated_agent_count = 0,
        actor = coalesce(actor, actor_text),
        reason = coalesce(nullif(reason_text, ''), reason)
    where cohort_id = any(cohort_ids);

    updated_count := active_count;
  end if;

  insert into runtime_corps_events (
    department_id,
    cohort_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    null,
    actor_text,
    'RUNTIME_CORPS_DEPARTMENT_COHORTS_DEACTIVATED',
    format('Deactivated %s active cohort(s) for department %s.', updated_count, p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'deactivated_cohort_count', updated_count,
      'reason', reason_text
    ),
    'mvp61_5000_agent_department_gated_runtime_corps'
  )
  returning * into event_row;

  perform runtime_corps_sync_state(runtime_corps_current_live_count());

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'department_id', p_department_id,
    'deactivated_cohort_count', updated_count,
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', runtime_corps_current_live_count(),
    'global_live_agent_cap', 5000
  );
end;
$$;

create or replace function activate_runtime_corps_cohort(
  p_department_id text,
  p_requested_agent_count integer,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
begin
  return runtime_corps_activate_department_cohort(p_department_id, p_requested_agent_count, p_actor, p_reason);
end;
$$;

create or replace function deactivate_runtime_corps_cohort(
  p_cohort_id uuid,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
begin
  return runtime_corps_deactivate_cohort(p_cohort_id, p_actor, p_reason);
end;
$$;

create or replace function activate_approved_department_cohort(
  p_department_id text,
  p_requested_agent_count integer,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
begin
  return runtime_corps_activate_department_cohort(p_department_id, p_requested_agent_count, p_actor, p_reason);
end;
$$;

create or replace function deactivate_approved_department_cohort(
  p_department_id text,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
begin
  return runtime_corps_deactivate_department_cohorts(p_department_id, p_actor, p_reason);
end;
$$;

select runtime_corps_sync_state(runtime_corps_current_live_count());
