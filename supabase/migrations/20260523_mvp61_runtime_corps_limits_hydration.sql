-- MVP-61 runtime corps limits hydration.
-- This migration restores the missing runtime_corps_limits table and seeds the
-- live corps limit keys so the corps endpoints no longer report a partial backend.

create table if not exists runtime_corps_limits (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

drop trigger if exists runtime_corps_limits_touch_updated_at on runtime_corps_limits;
create trigger runtime_corps_limits_touch_updated_at
before update on runtime_corps_limits
for each row execute function runtime_corps_touch_updated_at();

insert into runtime_corps_limits (key, value) values
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
  ('current_live_runtime_agents', to_jsonb(0))
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
  ('alert_sending_enabled', to_jsonb(false))
on conflict (key) do update set
  value = excluded.value,
  updated_at = now();
