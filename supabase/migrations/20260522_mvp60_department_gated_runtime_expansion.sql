-- MVP-60 department-gated runtime expansion.
-- Department approval is not command execution.
-- Activation means supervised runtime capacity only.
-- Full 47,979-agent activation remains blocked.
-- full 47,979-agent activation remains blocked.

create extension if not exists pgcrypto;

create or replace function department_runtime_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists department_runtime_gates (
  gate_id uuid primary key default gen_random_uuid(),
  department_id text not null references runtime_departments(department_id) on delete cascade,
  gate_status text not null default 'closed',
  activation_cap integer not null default 0,
  currently_active_agents integer not null default 0,
  approval_required boolean not null default true,
  approved_by text,
  approved_at timestamptz,
  blocked_reason text,
  command_execution_enabled boolean not null default false,
  deploy_execution_enabled boolean not null default false,
  rollback_execution_enabled boolean not null default false,
  alert_sending_enabled boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp60_department_gated_runtime_expansion',
  constraint department_runtime_gates_status_check check (gate_status in ('closed', 'pending_review', 'approved', 'active', 'blocked', 'disabled')),
  constraint department_runtime_gates_cap_check check (activation_cap >= 0 and activation_cap <= 250),
  constraint department_runtime_gates_active_check check (currently_active_agents >= 0 and currently_active_agents <= activation_cap),
  constraint department_runtime_gates_department_unique unique (department_id)
);

create trigger department_runtime_gates_touch_updated_at
before update on department_runtime_gates
for each row execute function department_runtime_touch_updated_at();

create index if not exists department_runtime_gates_department_id_idx on department_runtime_gates (department_id);
create index if not exists department_runtime_gates_status_idx on department_runtime_gates (gate_status);

create table if not exists department_runtime_activations (
  activation_id uuid primary key default gen_random_uuid(),
  department_id text not null references runtime_departments(department_id) on delete cascade,
  gate_id uuid references department_runtime_gates(gate_id) on delete set null,
  requested_agent_count integer not null,
  activated_agent_count integer not null default 0,
  activation_status text not null default 'requested',
  actor text,
  reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null default 'mvp60_department_gated_runtime_expansion',
  constraint department_runtime_activations_status_check check (activation_status in ('requested', 'approved', 'active', 'partially_active', 'deactivated', 'denied', 'blocked')),
  constraint department_runtime_activations_requested_check check (requested_agent_count >= 0 and requested_agent_count <= 250),
  constraint department_runtime_activations_active_check check (activated_agent_count >= 0 and activated_agent_count <= requested_agent_count)
);

create trigger department_runtime_activations_touch_updated_at
before update on department_runtime_activations
for each row execute function department_runtime_touch_updated_at();

create index if not exists department_runtime_activations_department_id_idx on department_runtime_activations (department_id);
create index if not exists department_runtime_activations_created_at_idx on department_runtime_activations (created_at desc);

create table if not exists department_runtime_gate_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  department_id text references runtime_departments(department_id) on delete cascade,
  gate_id uuid references department_runtime_gates(gate_id) on delete set null,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp60_department_gated_runtime_expansion'
);

create index if not exists department_runtime_gate_events_department_id_idx on department_runtime_gate_events (department_id);
create index if not exists department_runtime_gate_events_created_at_idx on department_runtime_gate_events (created_at desc);
create index if not exists department_runtime_gate_events_gate_id_idx on department_runtime_gate_events (gate_id);

create table if not exists department_runtime_global_limits (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

create trigger department_runtime_global_limits_touch_updated_at
before update on department_runtime_global_limits
for each row execute function department_runtime_touch_updated_at();

create or replace function department_runtime_current_live_count()
returns integer
language sql
stable
as $$
  select coalesce(sum(currently_active_agents), 0)::integer
  from department_runtime_gates;
$$;

create or replace function department_runtime_sync_limits(p_live_count integer)
returns void
language plpgsql
as $$
begin
  insert into department_runtime_global_limits (key, value) values
    ('mvp60_global_live_agent_cap', to_jsonb(2500)),
    ('max_department_activation_cap', to_jsonb(250)),
    ('full_47979_activation_blocked', to_jsonb(true)),
    ('department_gated_expansion_enabled', to_jsonb(true)),
    ('command_execution_enabled', to_jsonb(false)),
    ('deploy_execution_enabled', to_jsonb(false)),
    ('rollback_execution_enabled', to_jsonb(false)),
    ('alert_sending_enabled', to_jsonb(false)),
    ('current_live_runtime_agents', to_jsonb(coalesce(p_live_count, 0)))
  on conflict (key) do update set
    value = excluded.value,
    updated_at = now();

  insert into runtime_kernel_config (key, value) values
    ('mvp60_department_gated_runtime_ready', to_jsonb(true)),
    ('mvp60_global_live_agent_cap', to_jsonb(2500)),
    ('max_department_activation_cap', to_jsonb(250)),
    ('full_47979_activation_blocked', to_jsonb(true)),
    ('department_gated_expansion_enabled', to_jsonb(true)),
    ('command_execution_enabled', to_jsonb(false)),
    ('deploy_execution_enabled', to_jsonb(false)),
    ('rollback_execution_enabled', to_jsonb(false)),
    ('alert_sending_enabled', to_jsonb(false)),
    ('live_runtime_agents_enabled', to_jsonb(coalesce(p_live_count, 0)))
  on conflict (key) do update set
    value = excluded.value,
    updated_at = now();
end;
$$;

create or replace function approve_department_runtime_gate(
  p_department_id text,
  p_activation_cap integer,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  dept record;
  existing_gate record;
  lane_count integer;
  reason_text text := btrim(coalesce(p_reason, ''));
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  live_count integer;
  gate_row record;
  event_row record;
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  if dept.runtime_status <> 'eligible_for_supervised_runtime' or not coalesce(dept.activation_eligible, false) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_ELIGIBLE', 'message', 'Department must be eligible_for_supervised_runtime and activation_eligible=true.');
  end if;

  select count(*) into lane_count
  from runtime_department_lane_assignments
  where department_id = p_department_id;

  if lane_count = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_LANE_MISSING', 'message', 'Department must have a mapped runtime lane.');
  end if;

  if length(reason_text) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'READINESS_NOTE_REQUIRED', 'message', 'Department approval requires an audit-ready readiness note.');
  end if;

  if p_activation_cap is null or p_activation_cap < 1 or p_activation_cap > 250 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'ACTIVATION_CAP_OUT_OF_RANGE', 'message', 'activation_cap must be between 1 and 250.');
  end if;

  select * into existing_gate
  from department_runtime_gates
  where department_id = p_department_id
  limit 1;

  if found and coalesce(existing_gate.currently_active_agents, 0) > p_activation_cap then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'ACTIVE_AGENTS_EXCEED_CAP', 'message', 'Current active agents exceed the requested activation cap.');
  end if;

  insert into department_runtime_gates (
    department_id,
    gate_status,
    activation_cap,
    currently_active_agents,
    approval_required,
    approved_by,
    approved_at,
    blocked_reason,
    command_execution_enabled,
    deploy_execution_enabled,
    rollback_execution_enabled,
    alert_sending_enabled,
    source
  ) values (
    p_department_id,
    'approved',
    p_activation_cap,
    coalesce(existing_gate.currently_active_agents, 0),
    true,
    actor_text,
    now(),
    null,
    false,
    false,
    false,
    false,
    'mvp60_department_gated_runtime_expansion'
  )
  on conflict (department_id) do update set
    gate_status = 'approved',
    activation_cap = excluded.activation_cap,
    currently_active_agents = least(department_runtime_gates.currently_active_agents, excluded.activation_cap),
    approval_required = true,
    approved_by = excluded.approved_by,
    approved_at = excluded.approved_at,
    blocked_reason = null,
    command_execution_enabled = false,
    deploy_execution_enabled = false,
    rollback_execution_enabled = false,
    alert_sending_enabled = false,
    source = excluded.source,
    updated_at = now()
  returning * into gate_row;

  insert into department_runtime_gate_events (
    department_id,
    gate_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    gate_row.gate_id,
    actor_text,
    'DEPARTMENT_GATE_APPROVED',
    format('Department %s gate approved with cap %s.', p_department_id, p_activation_cap),
    jsonb_build_object(
      'department_id', p_department_id,
      'activation_cap', p_activation_cap,
      'gate_status', gate_row.gate_status,
      'readiness_note', reason_text
    ),
    'mvp60_department_gated_runtime_expansion'
  )
  returning * into event_row;

  live_count := department_runtime_current_live_count();
  perform department_runtime_sync_limits(live_count);

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'gate', to_jsonb(gate_row),
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', live_count,
    'global_live_agent_cap', 2500,
    'max_department_activation_cap', 250
  );
end;
$$;

create or replace function block_department_runtime_gate(
  p_department_id text,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  dept record;
  existing_gate record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
  live_count integer;
  gate_row record;
  event_row record;
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  select * into existing_gate
  from department_runtime_gates
  where department_id = p_department_id
  limit 1;

  insert into department_runtime_gates (
    department_id,
    gate_status,
    activation_cap,
    currently_active_agents,
    approval_required,
    approved_by,
    approved_at,
    blocked_reason,
    command_execution_enabled,
    deploy_execution_enabled,
    rollback_execution_enabled,
    alert_sending_enabled,
    source
  ) values (
    p_department_id,
    'blocked',
    0,
    0,
    true,
    null,
    null,
    nullif(reason_text, ''),
    false,
    false,
    false,
    false,
    'mvp60_department_gated_runtime_expansion'
  )
  on conflict (department_id) do update set
    gate_status = 'blocked',
    activation_cap = 0,
    currently_active_agents = 0,
    approval_required = true,
    approved_by = null,
    approved_at = null,
    blocked_reason = nullif(reason_text, ''),
    command_execution_enabled = false,
    deploy_execution_enabled = false,
    rollback_execution_enabled = false,
    alert_sending_enabled = false,
    source = excluded.source,
    updated_at = now()
  returning * into gate_row;

  insert into department_runtime_gate_events (
    department_id,
    gate_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    gate_row.gate_id,
    actor_text,
    'DEPARTMENT_GATE_BLOCKED',
    format('Department %s gate blocked.', p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'blocked_reason', nullif(reason_text, ''),
      'previous_gate_status', coalesce(existing_gate.gate_status, 'closed')
    ),
    'mvp60_department_gated_runtime_expansion'
  )
  returning * into event_row;

  live_count := department_runtime_current_live_count();
  perform department_runtime_sync_limits(live_count);

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'gate', to_jsonb(gate_row),
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', live_count,
    'global_live_agent_cap', 2500,
    'max_department_activation_cap', 250
  );
end;
$$;

create or replace function activate_department_runtime(
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
  gate record;
  lane_count integer;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
  requested_count integer := coalesce(p_requested_agent_count, 0);
  current_live integer;
  projected_live integer;
  activation_row record;
  event_row record;
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  if dept.runtime_status <> 'eligible_for_supervised_runtime' or not coalesce(dept.activation_eligible, false) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_ELIGIBLE', 'message', 'Department must be eligible_for_supervised_runtime and activation_eligible=true.');
  end if;

  select count(*) into lane_count
  from runtime_department_lane_assignments
  where department_id = p_department_id;

  if lane_count = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_LANE_MISSING', 'message', 'Department must have a mapped runtime lane.');
  end if;

  if length(reason_text) = 0 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'READINESS_NOTE_REQUIRED', 'message', 'Department activation requires a readiness note in the request payload.');
  end if;

  if requested_count < 1 or requested_count > 250 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'REQUESTED_COUNT_OUT_OF_RANGE', 'message', 'requested_agent_count must be between 1 and 250.');
  end if;

  select * into gate
  from department_runtime_gates
  where department_id = p_department_id
  limit 1
  for update;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'GATE_NOT_APPROVED', 'message', 'Department gate must be approved before activation.');
  end if;

  if gate.gate_status not in ('approved', 'active') then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'GATE_NOT_APPROVED', 'message', 'Department gate must be approved or active.');
  end if;

  if requested_count > coalesce(gate.activation_cap, 0) then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'REQUESTED_COUNT_EXCEEDS_CAP', 'message', 'requested_agent_count exceeds the department cap.');
  end if;

  current_live := department_runtime_current_live_count();
  projected_live := current_live - coalesce(gate.currently_active_agents, 0) + requested_count;

  if projected_live > 2500 then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'GLOBAL_CAP_EXCEEDED', 'message', 'Requested activation would exceed the global MVP-60 cap of 2,500.');
  end if;

  update department_runtime_gates
  set
    gate_status = 'active',
    currently_active_agents = requested_count,
    approval_required = true,
    approved_by = coalesce(approved_by, actor_text),
    approved_at = coalesce(approved_at, now()),
    blocked_reason = blocked_reason,
    command_execution_enabled = false,
    deploy_execution_enabled = false,
    rollback_execution_enabled = false,
    alert_sending_enabled = false,
    updated_at = now()
  where gate_id = gate.gate_id
  returning * into gate;

  insert into department_runtime_activations (
    department_id,
    gate_id,
    requested_agent_count,
    activated_agent_count,
    activation_status,
    actor,
    reason,
    source
  ) values (
    p_department_id,
    gate.gate_id,
    requested_count,
    requested_count,
    case when requested_count = coalesce(gate.activation_cap, requested_count) then 'active' else 'partially_active' end,
    actor_text,
    reason_text,
    'mvp60_department_gated_runtime_expansion'
  )
  returning * into activation_row;

  insert into department_runtime_gate_events (
    department_id,
    gate_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    gate.gate_id,
    actor_text,
    'DEPARTMENT_RUNTIME_ACTIVATED',
    format('Department %s activated for %s supervised runtime agents.', p_department_id, requested_count),
    jsonb_build_object(
      'department_id', p_department_id,
      'requested_agent_count', requested_count,
      'activation_cap', gate.activation_cap,
      'readiness_note', reason_text,
      'activation_status', activation_row.activation_status
    ),
    'mvp60_department_gated_runtime_expansion'
  )
  returning * into event_row;

  perform department_runtime_sync_limits(projected_live);

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'gate', to_jsonb(gate),
    'activation', to_jsonb(activation_row),
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', projected_live,
    'global_live_agent_cap', 2500,
    'max_department_activation_cap', 250
  );
end;
$$;

create or replace function deactivate_department_runtime(
  p_department_id text,
  p_actor text,
  p_reason text
)
returns jsonb
language plpgsql
as $$
declare
  dept record;
  gate record;
  actor_text text := coalesce(nullif(btrim(coalesce(p_actor, '')), ''), 'operator');
  reason_text text := btrim(coalesce(p_reason, ''));
  current_live integer;
  projected_live integer;
  previous_active_agents integer;
  activation_row record;
  event_row record;
  next_gate_status text;
begin
  select * into dept
  from runtime_departments
  where department_id = p_department_id
  limit 1;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'DEPARTMENT_NOT_FOUND', 'message', 'Department not found.');
  end if;

  select * into gate
  from department_runtime_gates
  where department_id = p_department_id
  limit 1
  for update;

  if not found then
    return jsonb_build_object('ok', false, 'blocked', true, 'error', 'GATE_NOT_FOUND', 'message', 'Department gate not found.');
  end if;

  previous_active_agents := coalesce(gate.currently_active_agents, 0);
  next_gate_status := case
    when gate.gate_status in ('blocked', 'disabled') then gate.gate_status
    when gate.gate_status in ('pending_review', 'closed') then 'closed'
    else 'approved'
  end;

  current_live := department_runtime_current_live_count();
  projected_live := greatest(current_live - previous_active_agents, 0);

  update department_runtime_gates
  set
    gate_status = next_gate_status,
    currently_active_agents = 0,
    approval_required = true,
    approved_by = approved_by,
    approved_at = approved_at,
    blocked_reason = case when next_gate_status = 'blocked' then blocked_reason else blocked_reason end,
    command_execution_enabled = false,
    deploy_execution_enabled = false,
    rollback_execution_enabled = false,
    alert_sending_enabled = false,
    updated_at = now()
  where gate_id = gate.gate_id
  returning * into gate;

  insert into department_runtime_activations (
    department_id,
    gate_id,
    requested_agent_count,
    activated_agent_count,
    activation_status,
    actor,
    reason,
    source
  ) values (
    p_department_id,
    gate.gate_id,
    previous_active_agents,
    0,
    'deactivated',
    actor_text,
    reason_text,
    'mvp60_department_gated_runtime_expansion'
  )
  returning * into activation_row;

  insert into department_runtime_gate_events (
    department_id,
    gate_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  ) values (
    p_department_id,
    gate.gate_id,
    actor_text,
    'DEPARTMENT_RUNTIME_DEACTIVATED',
    format('Department %s deactivated.', p_department_id),
    jsonb_build_object(
      'department_id', p_department_id,
      'previous_active_agents', previous_active_agents,
      'reason', reason_text,
      'next_gate_status', next_gate_status
    ),
    'mvp60_department_gated_runtime_expansion'
  )
  returning * into event_row;

  perform department_runtime_sync_limits(projected_live);

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'gate', to_jsonb(gate),
    'activation', to_jsonb(activation_row),
    'event', to_jsonb(event_row),
    'live_runtime_agents_enabled', projected_live,
    'global_live_agent_cap', 2500,
    'max_department_activation_cap', 250
  );
end;
$$;

select department_runtime_sync_limits(department_runtime_current_live_count());
