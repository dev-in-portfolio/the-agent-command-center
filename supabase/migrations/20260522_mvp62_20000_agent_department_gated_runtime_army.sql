-- MVP-62 20,000-agent department-gated runtime army.
-- 20,000 is a cap, not an automatic activation.
-- Department-gated activation is required.
-- Staged unlocks are required.
-- Circuit breakers pause further activation.
-- Raw fleet activation is blocked.
-- Full 47,979-agent activation remains blocked.
-- Stage caps: 5,000, 10,000, 15,000, and 20,000 agents.

create extension if not exists pgcrypto;

create or replace function runtime_army_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists runtime_army_limits (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

create table if not exists runtime_army_stages (
  stage_id text primary key,
  stage_name text not null,
  stage_cap integer not null,
  stage_status text not null default 'locked',
  unlocked_by text,
  unlocked_at timestamptz,
  safety_check_status text not null default 'not_checked',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp62_20000_agent_department_gated_runtime_army',
  constraint runtime_army_stages_status_check check (stage_status in ('locked', 'unlocked', 'active', 'paused', 'blocked', 'disabled')),
  constraint runtime_army_stages_safety_check_status_check check (safety_check_status in ('not_checked', 'passed', 'failed', 'blocked')),
  constraint runtime_army_stages_cap_check check (stage_cap >= 0)
);

drop trigger if exists runtime_army_stages_touch_updated_at on runtime_army_stages;
create trigger runtime_army_stages_touch_updated_at
before update on runtime_army_stages
for each row execute function runtime_army_touch_updated_at();

insert into runtime_army_stages (
  stage_id,
  stage_name,
  stage_cap,
  stage_status,
  safety_check_status,
  source
) values
  ('stage_1_5000', 'Stage 1', 5000, 'unlocked', 'passed', 'mvp62_20000_agent_department_gated_runtime_army'),
  ('stage_2_10000', 'Stage 2', 10000, 'locked', 'not_checked', 'mvp62_20000_agent_department_gated_runtime_army'),
  ('stage_3_15000', 'Stage 3', 15000, 'locked', 'not_checked', 'mvp62_20000_agent_department_gated_runtime_army'),
  ('stage_4_20000', 'Stage 4', 20000, 'locked', 'not_checked', 'mvp62_20000_agent_department_gated_runtime_army')
on conflict (stage_id) do update set
  stage_name = excluded.stage_name,
  stage_cap = excluded.stage_cap,
  stage_status = excluded.stage_status,
  safety_check_status = excluded.safety_check_status,
  source = excluded.source,
  updated_at = now();

create table if not exists runtime_army_cohorts (
  cohort_id uuid primary key default gen_random_uuid(),
  cohort_name text not null,
  department_id text references runtime_departments(department_id) on delete cascade,
  stage_id text references runtime_army_stages(stage_id) on delete set null,
  requested_agent_count integer not null,
  activated_agent_count integer not null default 0,
  cohort_status text not null default 'requested',
  actor text,
  reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp62_20000_agent_department_gated_runtime_army',
  constraint runtime_army_cohorts_status_check check (cohort_status in ('requested', 'approved', 'active', 'partially_active', 'deactivated', 'denied', 'blocked', 'circuit_breaker_paused')),
  constraint runtime_army_cohorts_requested_check check (requested_agent_count >= 0 and requested_agent_count <= 1000),
  constraint runtime_army_cohorts_active_check check (activated_agent_count >= 0 and activated_agent_count <= requested_agent_count)
);

drop trigger if exists runtime_army_cohorts_touch_updated_at on runtime_army_cohorts;
create trigger runtime_army_cohorts_touch_updated_at
before update on runtime_army_cohorts
for each row execute function runtime_army_touch_updated_at();

create index if not exists runtime_army_cohorts_department_id_idx on runtime_army_cohorts (department_id);
create index if not exists runtime_army_cohorts_stage_id_idx on runtime_army_cohorts (stage_id);
create index if not exists runtime_army_cohorts_status_idx on runtime_army_cohorts (cohort_status);
create index if not exists runtime_army_cohorts_created_at_idx on runtime_army_cohorts (created_at desc);

create table if not exists runtime_army_circuit_breakers (
  breaker_id uuid primary key default gen_random_uuid(),
  breaker_name text not null unique,
  breaker_status text not null default 'clear',
  trigger_reason text,
  triggered_by text,
  triggered_at timestamptz,
  cleared_by text,
  cleared_at timestamptz,
  affected_stage_id text,
  affected_department_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp62_20000_agent_department_gated_runtime_army',
  constraint runtime_army_circuit_breakers_status_check check (breaker_status in ('clear', 'triggered', 'paused', 'cleared', 'disabled'))
);

drop trigger if exists runtime_army_circuit_breakers_touch_updated_at on runtime_army_circuit_breakers;
create trigger runtime_army_circuit_breakers_touch_updated_at
before update on runtime_army_circuit_breakers
for each row execute function runtime_army_touch_updated_at();

create index if not exists runtime_army_circuit_breakers_status_idx on runtime_army_circuit_breakers (breaker_status);
create index if not exists runtime_army_circuit_breakers_created_at_idx on runtime_army_circuit_breakers (created_at desc);

create table if not exists runtime_army_health_rollups (
  rollup_id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  total_registered_agents integer not null default 47979,
  total_departments integer not null default 1777,
  global_live_agent_cap integer not null default 20000,
  current_live_runtime_agents integer not null default 0,
  current_stage_cap integer not null default 5000,
  unlocked_stages integer not null default 1,
  active_department_gates integer not null default 0,
  active_cohorts integer not null default 0,
  heartbeat_count integer not null default 0,
  readiness_note_count integer not null default 0,
  circuit_breaker_status text not null default 'clear',
  full_47979_activation_blocked boolean not null default true,
  command_execution_enabled boolean not null default false,
  deploy_execution_enabled boolean not null default false,
  rollback_execution_enabled boolean not null default false,
  alert_sending_enabled boolean not null default false,
  source text not null default 'mvp62_20000_agent_department_gated_runtime_army'
);

create index if not exists runtime_army_health_rollups_created_at_idx on runtime_army_health_rollups (created_at desc);

create table if not exists runtime_army_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  department_id text references runtime_departments(department_id) on delete cascade,
  cohort_id uuid references runtime_army_cohorts(cohort_id) on delete set null,
  stage_id text references runtime_army_stages(stage_id) on delete set null,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp62_20000_agent_department_gated_runtime_army'
);

create index if not exists runtime_army_events_department_id_idx on runtime_army_events (department_id);
create index if not exists runtime_army_events_cohort_id_idx on runtime_army_events (cohort_id);
create index if not exists runtime_army_events_stage_id_idx on runtime_army_events (stage_id);
create index if not exists runtime_army_events_created_at_idx on runtime_army_events (created_at desc);

create or replace function runtime_army_current_live_count()
returns integer
language sql
stable
as $$
  select
    coalesce((select sum(currently_active_agents) from department_runtime_gates where gate_status = 'active'), 0)::integer
    +
    coalesce((select sum(activated_agent_count) from runtime_army_cohorts where cohort_status in ('active', 'partially_active')), 0)::integer;
$$;

create or replace function runtime_army_current_stage_cap()
returns integer
language sql
stable
as $$
  select coalesce((
    select max(stage_cap)
    from runtime_army_stages
    where stage_status in ('unlocked', 'active')
  ), 5000)::integer;
$$;

create or replace function runtime_army_current_circuit_breaker_status()
returns text
language sql
stable
as $$
  select coalesce((
    select breaker_status
    from runtime_army_circuit_breakers
    order by
      case breaker_status
        when 'triggered' then 1
        when 'paused' then 2
        when 'disabled' then 3
        when 'cleared' then 4
        else 5
      end,
      updated_at desc
    limit 1
  ), 'clear');
$$;

create or replace function runtime_army_sync_state()
returns void
language plpgsql
as $$
declare
  v_live_count integer := runtime_army_current_live_count();
  v_stage_cap integer := runtime_army_current_stage_cap();
  v_circuit_status text := runtime_army_current_circuit_breaker_status();
  v_total_departments integer;
  v_unlocked_stages integer;
  v_active_department_gates integer;
  v_active_cohorts integer;
  v_heartbeat_count integer;
  v_readiness_note_count integer;
begin
  select count(*) into v_total_departments from runtime_departments;
  select count(*) into v_unlocked_stages from runtime_army_stages where stage_status in ('unlocked', 'active');
  select count(*) into v_active_department_gates from department_runtime_gates where gate_status = 'active';
  select count(*) into v_active_cohorts from runtime_army_cohorts where cohort_status in ('active', 'partially_active');
  select count(*) into v_heartbeat_count from runtime_army_events where event_type = 'RUNTIME_ARMY_HEARTBEAT';
  select count(*) into v_readiness_note_count from runtime_army_events where event_type = 'RUNTIME_ARMY_READINESS_NOTE_CREATED';

  insert into runtime_army_limits (key, value) values
    ('mvp62_global_live_agent_cap', to_jsonb(20000)),
    ('max_department_activation_cap', to_jsonb(500)),
    ('max_cohort_activation_size', to_jsonb(1000)),
    ('max_operation_chunk_size', to_jsonb(500)),
    ('full_47979_activation_blocked', to_jsonb(true)),
    ('department_gated_activation_required', to_jsonb(true)),
    ('staged_activation_required', to_jsonb(true)),
    ('circuit_breaker_required', to_jsonb(true)),
    ('command_execution_enabled', to_jsonb(false)),
    ('deploy_execution_enabled', to_jsonb(false)),
    ('rollback_execution_enabled', to_jsonb(false)),
    ('alert_sending_enabled', to_jsonb(false)),
    ('current_live_runtime_agents', to_jsonb(v_live_count)),
    ('current_stage_cap', to_jsonb(v_stage_cap)),
    ('circuit_breaker_status', to_jsonb(v_circuit_status))
  on conflict (key) do update set
    value = excluded.value,
    updated_at = now();

  insert into runtime_kernel_config (key, value) values
    ('mvp62_department_gated_runtime_army_ready', to_jsonb(true)),
    ('mvp62_global_live_agent_cap', to_jsonb(20000)),
    ('max_cohort_activation_size', to_jsonb(1000)),
    ('max_operation_chunk_size', to_jsonb(500)),
    ('staged_activation_required', to_jsonb(true)),
    ('circuit_breaker_required', to_jsonb(true)),
    ('department_gated_activation_required', to_jsonb(true)),
    ('full_47979_activation_blocked', to_jsonb(true)),
    ('command_execution_enabled', to_jsonb(false)),
    ('deploy_execution_enabled', to_jsonb(false)),
    ('rollback_execution_enabled', to_jsonb(false)),
    ('alert_sending_enabled', to_jsonb(false)),
    ('live_runtime_agents_enabled', to_jsonb(v_live_count)),
    ('current_stage_cap', to_jsonb(v_stage_cap)),
    ('circuit_breaker_status', to_jsonb(v_circuit_status)),
    ('heartbeat_count', to_jsonb(v_heartbeat_count)),
    ('readiness_note_count', to_jsonb(v_readiness_note_count)),
    ('total_registered_agents', to_jsonb(47979)),
    ('total_departments', to_jsonb(coalesce(v_total_departments, 1777)))
  on conflict (key) do update set
    value = excluded.value,
    updated_at = now();

  insert into runtime_army_health_rollups (
    total_registered_agents,
    total_departments,
    global_live_agent_cap,
    current_live_runtime_agents,
    current_stage_cap,
    unlocked_stages,
    active_department_gates,
    active_cohorts,
    heartbeat_count,
    readiness_note_count,
    circuit_breaker_status,
    full_47979_activation_blocked,
    command_execution_enabled,
    deploy_execution_enabled,
    rollback_execution_enabled,
    alert_sending_enabled,
    source
  ) values (
    47979,
    coalesce(v_total_departments, 1777),
    20000,
    v_live_count,
    v_stage_cap,
    coalesce(v_unlocked_stages, 0),
    coalesce(v_active_department_gates, 0),
    coalesce(v_active_cohorts, 0),
    coalesce(v_heartbeat_count, 0),
    coalesce(v_readiness_note_count, 0),
    v_circuit_status,
    true,
    false,
    false,
    false,
    false,
    'mvp62_20000_agent_department_gated_runtime_army'
  );
end;
$$;

create or replace function unlock_runtime_army_stage(
  p_stage_id text,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  stage_row record;
  previous_stage record;
  breaker_status text := runtime_army_current_circuit_breaker_status();
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
  event_row record;
begin
  select * into stage_row
  from runtime_army_stages
  where stage_id = p_stage_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'STAGE_NOT_FOUND', 'message', 'Stage not found.');
  end if;

  if breaker_status = 'triggered' then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'CIRCUIT_BREAKER_TRIGGERED', 'message', 'Circuit breaker must be clear before unlocking stages.');
  end if;

  if stage_row.stage_status = 'disabled' then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'STAGE_DISABLED', 'message', 'Stage is disabled.');
  end if;

  if stage_row.stage_id <> 'stage_1_5000' then
    select *
    into previous_stage
    from runtime_army_stages
    where stage_cap < stage_row.stage_cap
    order by stage_cap desc
    limit 1;

    if not found or previous_stage.stage_status not in ('unlocked', 'active') or previous_stage.safety_check_status <> 'passed' then
      return jsonb_build_object('ok', false, 'blocked', true, 'error', 'PREVIOUS_STAGE_NOT_READY', 'message', 'Previous stage must be unlocked or active and safety-check passed.');
    end if;
  end if;

  update runtime_army_stages
  set stage_status = 'unlocked',
      unlocked_by = actor_text,
      unlocked_at = coalesce(unlocked_at, now()),
      safety_check_status = 'passed'
  where stage_id = p_stage_id
  returning * into stage_row;

  insert into runtime_army_events (
    stage_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_stage_id,
    actor_text,
    'RUNTIME_ARMY_STAGE_UNLOCKED',
    format('Unlocked runtime army stage %s.', p_stage_id),
    jsonb_build_object(
      'stage_id', p_stage_id,
      'reason', reason_text,
      'stage_cap', stage_row.stage_cap
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'stage', to_jsonb(stage_row),
    'event', to_jsonb(event_row),
    'current_stage_cap', runtime_army_current_stage_cap(),
    'circuit_breaker_status', runtime_army_current_circuit_breaker_status()
  );
end;
$$;

create or replace function runtime_army_activate_department_cohort(
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
  stage_row record;
  live_count integer := runtime_army_current_live_count();
  department_live_count integer;
  stage_cap integer := runtime_army_current_stage_cap();
  breaker_status text := runtime_army_current_circuit_breaker_status();
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
  cohort_row record;
  event_row record;
  remaining integer;
  chunk_size integer;
  chunk_index integer := 1;
  activated_total integer := 0;
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

  select *
  into stage_row
  from runtime_army_stages
  where stage_status in ('unlocked', 'active')
  order by stage_cap desc
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'NO_UNLOCKED_STAGE', 'message', 'At least one stage must be unlocked before activation.');
  end if;

  if dept.runtime_status <> 'eligible_for_supervised_runtime' or not coalesce(dept.activation_eligible, false) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_ELIGIBLE', 'message', 'Department must be eligible_for_supervised_runtime and activation_eligible=true.');
  end if;

  if gate_row.gate_status not in ('approved', 'active') then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_GATE_NOT_APPROVED', 'message', 'Department gate must be approved or active.');
  end if;

  if breaker_status <> 'clear' then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'CIRCUIT_BREAKER_TRIGGERED', 'message', 'Circuit breaker must be clear before activation.');
  end if;

  if p_requested_agent_count is null or p_requested_agent_count < 1 or p_requested_agent_count > 1000 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'REQUESTED_AGENT_COUNT_OUT_OF_RANGE', 'message', 'requested_agent_count must be between 1 and 1000.');
  end if;

  if p_requested_agent_count > coalesce(gate_row.activation_cap, 0) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'REQUESTED_AGENT_COUNT_EXCEEDS_DEPARTMENT_CAP', 'message', 'requested_agent_count must stay within the department cap.');
  end if;

  select coalesce(sum(activated_agent_count), 0)::integer into department_live_count
  from runtime_army_cohorts
  where department_id = p_department_id
    and cohort_status in ('active', 'partially_active');

  if department_live_count + p_requested_agent_count > coalesce(gate_row.activation_cap, 0) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_CAP_EXCEEDED', 'message', 'Requested agents would exceed the department cap.');
  end if;

  if p_requested_agent_count > stage_cap then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'STAGE_CAP_EXCEEDED', 'message', 'Requested agents must stay within the unlocked stage cap.');
  end if;

  if live_count + p_requested_agent_count > 20000 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'GLOBAL_CAP_EXCEEDED', 'message', 'Requested agents would exceed the 20,000-agent global cap.');
  end if;

  if live_count + p_requested_agent_count > stage_cap then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'STAGE_CAP_EXCEEDED', 'message', 'Requested agents would exceed the current stage cap.');
  end if;

  insert into runtime_army_cohorts (
    cohort_name,
    department_id,
    stage_id,
    requested_agent_count,
    activated_agent_count,
    cohort_status,
    actor,
    reason,
    source
  ) values (
    format('%s-cohort-%s', p_department_id, to_char(clock_timestamp(), 'YYYYMMDDHH24MISSMS')),
    p_department_id,
    stage_row.stage_id,
    p_requested_agent_count,
    p_requested_agent_count,
    'active',
    actor_text,
    reason_text,
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into cohort_row;

  remaining := p_requested_agent_count;
  while remaining > 0 loop
    chunk_size := least(remaining, 500);
    insert into runtime_army_events (
      department_id,
      cohort_id,
      stage_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    ) values (
      p_department_id,
      cohort_row.cohort_id,
      stage_row.stage_id,
      actor_text,
      'RUNTIME_ARMY_COHORT_CHUNK_ACTIVATED',
      format('Activated %s agents in chunk %s for department %s.', chunk_size, chunk_index, p_department_id),
      jsonb_build_object(
        'department_id', p_department_id,
        'cohort_id', cohort_row.cohort_id,
        'stage_id', stage_row.stage_id,
        'chunk_index', chunk_index,
        'chunk_size', chunk_size,
        'requested_agent_count', p_requested_agent_count
      ),
      'mvp62_20000_agent_department_gated_runtime_army'
    );
    remaining := remaining - chunk_size;
    chunk_index := chunk_index + 1;
    activated_total := activated_total + chunk_size;
  end loop;

  insert into runtime_army_events (
    department_id,
    cohort_id,
    stage_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    cohort_row.cohort_id,
    stage_row.stage_id,
    actor_text,
    'RUNTIME_ARMY_COHORT_ACTIVATED',
    format('Activated %s supervised runtime agents for department %s.', p_requested_agent_count, p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'requested_agent_count', p_requested_agent_count,
      'activated_agent_count', activated_total,
      'stage_id', stage_row.stage_id,
      'global_live_runtime_agents_before', live_count,
      'global_live_runtime_agents_after', runtime_army_current_live_count()
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'department_id', p_department_id,
    'stage', to_jsonb(stage_row),
    'cohort', to_jsonb(cohort_row),
    'event', to_jsonb(event_row),
    'chunk_count', chunk_index - 1,
    'live_runtime_agents_enabled', runtime_army_current_live_count(),
    'global_live_agent_cap', 20000,
    'current_stage_cap', stage_cap,
    'max_cohort_activation_size', 1000,
    'max_operation_chunk_size', 500
  );
end;
$$;

create or replace function runtime_army_deactivate_cohort(p_cohort_id uuid, p_actor text, p_reason text)
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
  from runtime_army_cohorts
  where cohort_id = p_cohort_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'COHORT_NOT_FOUND', 'message', 'Cohort not found.');
  end if;

  update runtime_army_cohorts
  set cohort_status = 'deactivated',
      activated_agent_count = 0,
      actor = coalesce(actor, actor_text),
      reason = coalesce(nullif(reason_text, ''), reason)
  where cohort_id = p_cohort_id
  returning * into cohort_row;

  insert into runtime_army_events (
    department_id,
    cohort_id,
    stage_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    cohort_row.department_id,
    cohort_row.cohort_id,
    cohort_row.stage_id,
    actor_text,
    'RUNTIME_ARMY_COHORT_DEACTIVATED',
    format('Deactivated supervised runtime cohort %s for department %s.', cohort_row.cohort_id, cohort_row.department_id),
    jsonb_build_object(
      'department_id', cohort_row.department_id,
      'cohort_id', cohort_row.cohort_id,
      'reason', reason_text
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'cohort', to_jsonb(cohort_row),
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', runtime_army_current_live_count(),
    'global_live_agent_cap', 20000
  );
end;
$$;

create or replace function deactivate_approved_department_army_cohorts(
  p_department_id text,
  p_actor text,
  p_reason text
)
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
  from runtime_army_cohorts
  where department_id = p_department_id
    and cohort_status in ('active', 'partially_active');

  if active_count > 0 then
    update runtime_army_cohorts
    set cohort_status = 'deactivated',
        activated_agent_count = 0,
        actor = coalesce(actor, actor_text),
        reason = coalesce(nullif(reason_text, ''), reason)
    where cohort_id = any(cohort_ids);

    updated_count := active_count;
  end if;

  insert into runtime_army_events (
    department_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    actor_text,
    'RUNTIME_ARMY_DEPARTMENT_COHORTS_DEACTIVATED',
    format('Deactivated %s active cohort(s) for department %s.', updated_count, p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'deactivated_cohort_count', updated_count,
      'reason', reason_text
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'department_id', p_department_id,
    'deactivated_cohort_count', updated_count,
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', runtime_army_current_live_count(),
    'global_live_agent_cap', 20000
  );
end;
$$;

create or replace function runtime_army_trigger_circuit_breaker(
  p_breaker_name text,
  p_trigger_reason text,
  p_actor text,
  p_stage_id text default null,
  p_department_id text default null
)
returns jsonb
language plpgsql
as $$
declare
  breaker_row record;
  event_row record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_trigger_reason, ''));
begin
  insert into runtime_army_circuit_breakers (
    breaker_name,
    breaker_status,
    trigger_reason,
    triggered_by,
    triggered_at,
    affected_stage_id,
    affected_department_id,
    source
  ) values (
    coalesce(nullif(btrim(coalesce(p_breaker_name, '')), ''), 'runtime_army_global'),
    'triggered',
    reason_text,
    actor_text,
    now(),
    p_stage_id,
    p_department_id,
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  on conflict (breaker_name) do update set
    breaker_status = 'triggered',
    trigger_reason = excluded.trigger_reason,
    triggered_by = excluded.triggered_by,
    triggered_at = excluded.triggered_at,
    affected_stage_id = excluded.affected_stage_id,
    affected_department_id = excluded.affected_department_id,
    source = excluded.source
  returning * into breaker_row;

  insert into runtime_army_events (
    department_id,
    stage_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    p_stage_id,
    actor_text,
    'RUNTIME_ARMY_CIRCUIT_BREAKER_TRIGGERED',
    format('Triggered circuit breaker %s.', breaker_row.breaker_name),
    jsonb_build_object(
      'breaker_id', breaker_row.breaker_id,
      'breaker_name', breaker_row.breaker_name,
      'trigger_reason', reason_text,
      'affected_stage_id', p_stage_id,
      'affected_department_id', p_department_id
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'breaker', to_jsonb(breaker_row),
    'event', to_jsonb(event_row),
    'circuit_breaker_status', runtime_army_current_circuit_breaker_status(),
    'live_runtime_agents_enabled', runtime_army_current_live_count()
  );
end;
$$;

create or replace function runtime_army_clear_circuit_breaker(
  p_breaker_id uuid,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  breaker_row record;
  event_row record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
begin
  select * into breaker_row
  from runtime_army_circuit_breakers
  where breaker_id = p_breaker_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'BREAKER_NOT_FOUND', 'message', 'Circuit breaker not found.');
  end if;

  update runtime_army_circuit_breakers
  set breaker_status = 'cleared',
      cleared_by = actor_text,
      cleared_at = now(),
      trigger_reason = coalesce(trigger_reason, reason_text)
  where breaker_id = p_breaker_id
  returning * into breaker_row;

  insert into runtime_army_events (
    department_id,
    stage_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    breaker_row.affected_department_id,
    breaker_row.affected_stage_id,
    actor_text,
    'RUNTIME_ARMY_CIRCUIT_BREAKER_CLEARED',
    format('Cleared circuit breaker %s.', breaker_row.breaker_name),
    jsonb_build_object(
      'breaker_id', breaker_row.breaker_id,
      'breaker_name', breaker_row.breaker_name,
      'reason', reason_text
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'breaker', to_jsonb(breaker_row),
    'event', to_jsonb(event_row),
    'circuit_breaker_status', runtime_army_current_circuit_breaker_status()
  );
end;
$$;

create or replace function runtime_army_record_heartbeat(
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  event_row record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
begin
  insert into runtime_army_events (
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    actor_text,
    'RUNTIME_ARMY_HEARTBEAT',
    'Recorded runtime army heartbeat.',
    jsonb_build_object('reason', reason_text),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'event', to_jsonb(event_row),
    'heartbeat_count', (select count(*) from runtime_army_events where event_type = 'RUNTIME_ARMY_HEARTBEAT'),
    'readiness_note_count', (select count(*) from runtime_army_events where event_type = 'RUNTIME_ARMY_READINESS_NOTE_CREATED')
  );
end;
$$;

create or replace function runtime_army_create_readiness_note(
  p_department_id text,
  p_note_body text,
  p_actor text
)
returns jsonb
language plpgsql
as $$
declare
  dept record;
  event_row record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  note_text text := btrim(coalesce(p_note_body, ''));
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  insert into runtime_army_events (
    department_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    actor_text,
    'RUNTIME_ARMY_READINESS_NOTE_CREATED',
    format('Recorded readiness note for department %s.', p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'note_body', note_text,
      'note_type', 'readiness_note'
    ),
    'mvp62_20000_agent_department_gated_runtime_army'
  )
  returning * into event_row;

  perform runtime_army_sync_state();

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'department_id', p_department_id,
    'event', to_jsonb(event_row),
    'heartbeat_count', (select count(*) from runtime_army_events where event_type = 'RUNTIME_ARMY_HEARTBEAT'),
    'readiness_note_count', (select count(*) from runtime_army_events where event_type = 'RUNTIME_ARMY_READINESS_NOTE_CREATED')
  );
end;
$$;

select runtime_army_sync_state();
