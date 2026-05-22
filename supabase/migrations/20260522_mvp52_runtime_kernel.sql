-- MVP-52 runtime kernel persistence only.
-- This migration defines persistence only. It does not enable command execution.

create extension if not exists pgcrypto;

create table if not exists runtime_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  requester_name text,
  requester_email text,
  request_title text not null,
  request_type text not null,
  request_body text,
  risk_level text not null default 'unclassified',
  status text not null default 'submitted',
  dry_run_summary jsonb not null default '{}'::jsonb,
  execution_enabled boolean not null default false,
  runtime_activation_id text,
  source text not null default 'mvp52_runtime_kernel',
  constraint runtime_requests_status_check
    check (status in ('submitted', 'classified', 'dry_run_ready', 'pending_approval', 'approved', 'denied', 'blocked', 'archived')),
  constraint runtime_requests_risk_level_check
    check (risk_level in ('low', 'medium', 'high', 'critical', 'blocked', 'unclassified'))
);

create table if not exists runtime_audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  request_id uuid references runtime_requests(id) on delete cascade,
  actor text,
  event_type text not null,
  event_summary text not null,
  event_payload jsonb not null default '{}'::jsonb,
  source text not null default 'mvp52_runtime_kernel'
);

create table if not exists runtime_approval_queue (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  request_id uuid references runtime_requests(id) on delete cascade,
  approval_status text not null default 'pending',
  approver_name text,
  approver_email text,
  decision_reason text,
  decision_at timestamptz,
  required_level text not null default 'human_review',
  source text not null default 'mvp52_runtime_kernel',
  constraint runtime_approval_queue_status_check
    check (approval_status in ('pending', 'approved', 'denied', 'blocked'))
);

create table if not exists runtime_kernel_config (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

insert into runtime_kernel_config (key, value)
values
  ('runtime_activation_started', 'false'::jsonb),
  ('live_runtime_agents_enabled', '0'::jsonb),
  ('command_execution_enabled', 'false'::jsonb),
  ('automation_enabled', 'false'::jsonb),
  ('rollback_execution_enabled', 'false'::jsonb),
  ('alert_sending_enabled', 'false'::jsonb)
on conflict (key) do update
set value = excluded.value,
    updated_at = now();

create index if not exists runtime_requests_created_at_idx on runtime_requests (created_at desc);
create index if not exists runtime_requests_status_idx on runtime_requests (status);
create index if not exists runtime_requests_request_type_idx on runtime_requests (request_type);
create index if not exists runtime_audit_events_created_at_idx on runtime_audit_events (created_at desc);
create index if not exists runtime_audit_events_request_id_idx on runtime_audit_events (request_id);
create index if not exists runtime_approval_queue_created_at_idx on runtime_approval_queue (created_at desc);
create index if not exists runtime_approval_queue_request_id_idx on runtime_approval_queue (request_id);

create or replace function runtime_kernel_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists runtime_requests_touch_updated_at on runtime_requests;
create trigger runtime_requests_touch_updated_at
before update on runtime_requests
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_approval_queue_touch_updated_at on runtime_approval_queue;
create trigger runtime_approval_queue_touch_updated_at
before update on runtime_approval_queue
for each row execute function runtime_kernel_touch_updated_at();

drop trigger if exists runtime_kernel_config_touch_updated_at on runtime_kernel_config;
create trigger runtime_kernel_config_touch_updated_at
before update on runtime_kernel_config
for each row execute function runtime_kernel_touch_updated_at();

alter table if exists runtime_requests enable row level security;
alter table if exists runtime_audit_events enable row level security;
alter table if exists runtime_approval_queue enable row level security;
alter table if exists runtime_kernel_config enable row level security;

create or replace function runtime_kernel_submit_request(
  p_requester_name text,
  p_requester_email text,
  p_request_title text,
  p_request_type text,
  p_request_body text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_request runtime_requests%rowtype;
  v_approval runtime_approval_queue%rowtype;
  v_submit_event runtime_audit_events%rowtype;
  v_risk_event runtime_audit_events%rowtype;
  v_followup_event runtime_audit_events%rowtype;
  v_risk_level text := 'unclassified';
  v_blocked boolean := false;
  v_block_reason text := '';
  v_dry_run jsonb := '{}'::jsonb;
begin
  if coalesce(btrim(p_request_title), '') = '' then
    raise exception 'INVALID_PAYLOAD';
  end if;

  if coalesce(btrim(p_request_type), '') = '' then
    raise exception 'INVALID_PAYLOAD';
  end if;

  insert into runtime_requests (
    requester_name,
    requester_email,
    request_title,
    request_type,
    request_body,
    risk_level,
    status,
    dry_run_summary,
    execution_enabled,
    runtime_activation_id,
    source
  )
  values (
    nullif(btrim(p_requester_name), ''),
    nullif(btrim(p_requester_email), ''),
    btrim(p_request_title),
    btrim(p_request_type),
    p_request_body,
    'unclassified',
    'submitted',
    '{}'::jsonb,
    false,
    null,
    'mvp52_runtime_kernel'
  )
  returning * into v_request;

  insert into runtime_audit_events (
    request_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_request.id,
    coalesce(nullif(btrim(p_requester_name), ''), nullif(btrim(p_requester_email), ''), 'anonymous'),
    'REQUEST_SUBMITTED',
    'Runtime request submitted',
    jsonb_build_object(
      'request_title', p_request_title,
      'request_type', p_request_type,
      'source', 'mvp52_runtime_kernel'
    ),
    'mvp52_runtime_kernel'
  )
  returning * into v_submit_event;

  if p_request_type in ('content_review', 'stakeholder_report') then
    v_risk_level := 'low';
  elsif p_request_type in ('deploy_request', 'rollback_request') then
    v_risk_level := 'high';
  elsif p_request_type in ('supabase_write', 'alert_send', 'command_execution') then
    v_risk_level := 'blocked';
    v_blocked := true;
    v_block_reason := case p_request_type
      when 'supabase_write' then 'Supabase writes are blocked in MVP-52.'
      when 'alert_send' then 'Alert sending is blocked in MVP-52.'
      when 'command_execution' then 'Command execution is blocked in MVP-52.'
      else 'This request type is blocked in MVP-52.'
    end;
  else
    v_risk_level := 'medium';
  end if;

  v_dry_run := jsonb_build_object(
    'request_type', p_request_type,
    'risk_level', v_risk_level,
    'blocked', v_blocked,
    'approval_required', not v_blocked,
    'execution_enabled', false,
    'expected_changes', case
      when v_blocked then jsonb_build_array('No execution will occur.')
      when v_risk_level = 'low' then jsonb_build_array('Persist request metadata.', 'Record an approval queue item.')
      when v_risk_level = 'high' then jsonb_build_array('Persist request metadata.', 'Create a human approval queue item.', 'Record risk escalation.')
      else jsonb_build_array('Persist request metadata.', 'Classify the request for human review.')
    end,
    'affected_systems', jsonb_build_array('runtime_requests', 'runtime_audit_events', 'runtime_approval_queue'),
    'notes', case
      when v_blocked then v_block_reason
      else 'Approval is not execution. MVP-52 never executes the requested action.'
    end,
    'source', 'mvp52_runtime_kernel'
  );

  update runtime_requests
  set risk_level = v_risk_level,
      status = case when v_blocked then 'blocked' else 'dry_run_ready' end,
      dry_run_summary = v_dry_run,
      execution_enabled = false
  where id = v_request.id
  returning * into v_request;

  insert into runtime_audit_events (
    request_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_request.id,
    coalesce(nullif(btrim(p_requester_name), ''), nullif(btrim(p_requester_email), ''), 'anonymous'),
    'RISK_CLASSIFIED',
    'Runtime request risk classified',
    jsonb_build_object(
      'risk_level', v_risk_level,
      'blocked', v_blocked,
      'dry_run_summary', v_dry_run
    ),
    'mvp52_runtime_kernel'
  )
  returning * into v_risk_event;

  if v_blocked then
    update runtime_requests
    set status = 'blocked',
        execution_enabled = false
    where id = v_request.id
    returning * into v_request;

    insert into runtime_audit_events (
      request_id,
      actor,
      event_type,
      event_summary,
      event_payload,
      source
    )
    values (
      v_request.id,
      coalesce(nullif(btrim(p_requester_name), ''), nullif(btrim(p_requester_email), ''), 'anonymous'),
      'REQUEST_BLOCKED',
      'Runtime request blocked before queue creation',
      jsonb_build_object(
        'reason', v_block_reason,
        'risk_level', v_risk_level,
        'execution_enabled', false
      ),
      'mvp52_runtime_kernel'
    )
    returning * into v_followup_event;

    return jsonb_build_object(
      'ok', true,
      'blocked', true,
      'request', to_jsonb(v_request),
      'approval_queue', null,
      'audit_events', jsonb_build_array(
        to_jsonb(v_submit_event),
        to_jsonb(v_risk_event),
        to_jsonb(v_followup_event)
      ),
      'dry_run_summary', v_dry_run
    );
  end if;

  update runtime_requests
  set status = 'pending_approval',
      execution_enabled = false
  where id = v_request.id
  returning * into v_request;

  insert into runtime_approval_queue (
    request_id,
    approval_status,
    approver_name,
    approver_email,
    decision_reason,
    decision_at,
    required_level,
    source
  )
  values (
    v_request.id,
    'pending',
    null,
    null,
    null,
    null,
    'human_review',
    'mvp52_runtime_kernel'
  )
  returning * into v_approval;

  insert into runtime_audit_events (
    request_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_request.id,
    coalesce(nullif(btrim(p_requester_name), ''), nullif(btrim(p_requester_email), ''), 'anonymous'),
    'APPROVAL_QUEUE_CREATED',
    'Approval queue item created',
    jsonb_build_object(
      'approval_status', 'pending',
      'required_level', 'human_review'
    ),
    'mvp52_runtime_kernel'
  )
  returning * into v_followup_event;

  return jsonb_build_object(
    'ok', true,
    'blocked', false,
    'request', to_jsonb(v_request),
    'approval_queue', to_jsonb(v_approval),
    'audit_events', jsonb_build_array(
      to_jsonb(v_submit_event),
      to_jsonb(v_risk_event),
      to_jsonb(v_followup_event)
    ),
    'dry_run_summary', v_dry_run
  );
end;
$$;

create or replace function runtime_kernel_decide_request(
  p_request_id uuid,
  p_decision text,
  p_approver_name text,
  p_approver_email text,
  p_decision_reason text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_request runtime_requests%rowtype;
  v_approval runtime_approval_queue%rowtype;
  v_audit runtime_audit_events%rowtype;
  v_event_type text;
begin
  if p_request_id is null then
    raise exception 'INVALID_PAYLOAD';
  end if;

  if p_decision not in ('approved', 'denied') then
    raise exception 'INVALID_PAYLOAD';
  end if;

  select * into v_request
  from runtime_requests
  where id = p_request_id
  for update;

  if not found then
    raise exception 'REQUEST_NOT_FOUND';
  end if;

  if v_request.status = 'blocked' then
    raise exception 'BLOCKED_REQUEST_CANNOT_BE_APPROVED';
  end if;

  if v_request.execution_enabled then
    raise exception 'EXECUTION_MUST_REMAIN_FALSE';
  end if;

  select * into v_approval
  from runtime_approval_queue
  where request_id = p_request_id
  order by created_at desc
  limit 1
  for update;

  if not found then
    raise exception 'APPROVAL_QUEUE_MISSING';
  end if;

  if v_approval.approval_status <> 'pending' then
    raise exception 'APPROVAL_ALREADY_DECIDED';
  end if;

  update runtime_approval_queue
  set approval_status = p_decision,
      approver_name = nullif(btrim(p_approver_name), ''),
      approver_email = nullif(btrim(p_approver_email), ''),
      decision_reason = nullif(btrim(p_decision_reason), ''),
      decision_at = now()
  where id = v_approval.id
  returning * into v_approval;

  update runtime_requests
  set status = p_decision,
      execution_enabled = false
  where id = p_request_id
  returning * into v_request;

  v_event_type := case
    when p_decision = 'approved' then 'APPROVAL_APPROVED'
    else 'APPROVAL_DENIED'
  end;

  insert into runtime_audit_events (
    request_id,
    actor,
    event_type,
    event_summary,
    event_payload,
    source
  )
  values (
    v_request.id,
    coalesce(nullif(btrim(p_approver_name), ''), nullif(btrim(p_approver_email), ''), 'approver'),
    v_event_type,
    case
      when p_decision = 'approved' then 'Runtime request approved'
      else 'Runtime request denied'
    end,
    jsonb_build_object(
      'decision', p_decision,
      'decision_reason', nullif(btrim(p_decision_reason), ''),
      'execution_enabled', false
    ),
    'mvp52_runtime_kernel'
  )
  returning * into v_audit;

  return jsonb_build_object(
    'ok', true,
    'request', to_jsonb(v_request),
    'approval_queue', to_jsonb(v_approval),
    'audit_event', to_jsonb(v_audit)
  );
end;
$$;

comment on function runtime_kernel_submit_request(text, text, text, text, text) is
  'MVP-52 runtime kernel request intake only. It persists requests, audit events, and approval queue items. It does not enable command execution.';

comment on function runtime_kernel_decide_request(uuid, text, text, text, text) is
  'MVP-52 runtime kernel approval decision only. It updates approval status and request status. It does not enable command execution.';
