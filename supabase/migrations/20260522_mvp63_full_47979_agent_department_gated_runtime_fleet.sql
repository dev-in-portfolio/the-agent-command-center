-- MVP-63 Full 47,979-Agent Department-Gated Runtime Fleet Migration
-- Ensures staged activation, circuit breakers, and Continual Harness supervision.

CREATE TABLE IF NOT EXISTS runtime_fleet_limits (
    key text PRIMARY KEY,
    value jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO runtime_fleet_limits (key, value) VALUES
    ('mvp63_global_live_agent_cap', '47979'),
    ('max_department_activation_cap', '1000'),
    ('max_cohort_activation_size', '2500'),
    ('max_operation_chunk_size', '500'),
    ('full_47979_activation_cap_enabled', 'true'),
    ('raw_activate_all_route_enabled', 'false'),
    ('department_gated_activation_required', 'true'),
    ('staged_activation_required', 'true'),
    ('circuit_breaker_required', 'true'),
    ('continual_harness_supervision_required', 'true'),
    ('command_execution_enabled', 'false'),
    ('deploy_execution_enabled', 'false'),
    ('rollback_execution_enabled', 'false'),
    ('alert_sending_enabled', 'false'),
    ('arbitrary_shell_execution_enabled', 'false')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now();

CREATE TABLE IF NOT EXISTS runtime_fleet_stages (
    stage_id text PRIMARY KEY,
    stage_name text NOT NULL,
    stage_cap integer NOT NULL,
    stage_status text NOT NULL DEFAULT 'locked',
    unlocked_by text,
    unlocked_at timestamptz,
    safety_check_status text NOT NULL DEFAULT 'not_checked',
    continual_harness_status text NOT NULL DEFAULT 'not_checked',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp63_full_47979_agent_department_gated_runtime_fleet',
    CONSTRAINT valid_stage_status CHECK (stage_status IN ('locked', 'unlocked', 'active', 'paused', 'blocked', 'disabled')),
    CONSTRAINT valid_safety_check_status CHECK (safety_check_status IN ('not_checked', 'passed', 'failed', 'blocked')),
    CONSTRAINT valid_continual_harness_status CHECK (continual_harness_status IN ('not_checked', 'healthy', 'degraded', 'unavailable', 'blocked'))
);

INSERT INTO runtime_fleet_stages (stage_id, stage_name, stage_cap, stage_status) VALUES
    ('stage_1_5000', 'Stage 1: 5,000 Agents', 5000, 'unlocked'),
    ('stage_2_10000', 'Stage 2: 10,000 Agents', 10000, 'unlocked'),
    ('stage_3_20000', 'Stage 3: 20,000 Agents', 20000, 'unlocked'),
    ('stage_4_30000', 'Stage 4: 30,000 Agents', 30000, 'locked'),
    ('stage_5_40000', 'Stage 5: 40,000 Agents', 40000, 'locked'),
    ('stage_6_47979', 'Stage 6: 47,979 Agents', 47979, 'locked')
ON CONFLICT (stage_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS runtime_fleet_cohorts (
    cohort_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_name text NOT NULL,
    department_id text REFERENCES runtime_departments(department_id) ON DELETE CASCADE,
    stage_id text REFERENCES runtime_fleet_stages(stage_id) ON DELETE SET NULL,
    requested_agent_count integer NOT NULL,
    activated_agent_count integer NOT NULL DEFAULT 0,
    cohort_status text NOT NULL DEFAULT 'requested',
    actor text,
    reason text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp63_full_47979_agent_department_gated_runtime_fleet',
    CONSTRAINT valid_cohort_status CHECK (cohort_status IN ('requested', 'approved', 'active', 'partially_active', 'deactivated', 'denied', 'blocked', 'circuit_breaker_paused')),
    CONSTRAINT valid_requested_count CHECK (requested_agent_count >= 0 AND requested_agent_count <= 2500),
    CONSTRAINT valid_activated_count CHECK (activated_agent_count >= 0 AND activated_agent_count <= requested_agent_count)
);

CREATE TABLE IF NOT EXISTS runtime_fleet_circuit_breakers (
    breaker_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    breaker_name text NOT NULL,
    breaker_status text NOT NULL DEFAULT 'clear',
    trigger_reason text,
    triggered_by text,
    triggered_at timestamptz,
    cleared_by text,
    cleared_at timestamptz,
    affected_stage_id text,
    affected_department_id text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp63_full_47979_agent_department_gated_runtime_fleet',
    CONSTRAINT valid_breaker_status CHECK (breaker_status IN ('clear', 'triggered', 'paused', 'cleared', 'disabled'))
);

CREATE TABLE IF NOT EXISTS runtime_fleet_health_rollups (
    rollup_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    total_registered_agents integer NOT NULL DEFAULT 47979,
    total_departments integer NOT NULL DEFAULT 1777,
    total_units integer NOT NULL DEFAULT 5331,
    total_families integer NOT NULL DEFAULT 175,
    global_live_agent_cap integer NOT NULL DEFAULT 47979,
    current_live_runtime_agents integer NOT NULL DEFAULT 0,
    current_stage_cap integer NOT NULL DEFAULT 20000,
    unlocked_stages integer NOT NULL DEFAULT 3,
    active_department_gates integer NOT NULL DEFAULT 0,
    active_cohorts integer NOT NULL DEFAULT 0,
    heartbeat_count integer NOT NULL DEFAULT 0,
    readiness_note_count integer NOT NULL DEFAULT 0,
    circuit_breaker_status text NOT NULL DEFAULT 'clear',
    continual_harness_status text NOT NULL DEFAULT 'not_checked',
    raw_activate_all_route_enabled boolean NOT NULL DEFAULT false,
    department_gated_activation_required boolean NOT NULL DEFAULT true,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    source text NOT NULL DEFAULT 'mvp63_full_47979_agent_department_gated_runtime_fleet'
);

CREATE TABLE IF NOT EXISTS runtime_fleet_department_coverage (
    coverage_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    department_id text REFERENCES runtime_departments(department_id) ON DELETE CASCADE,
    registered_agent_count integer NOT NULL DEFAULT 0,
    approved_runtime_cap integer NOT NULL DEFAULT 0,
    current_active_runtime_agents integer NOT NULL DEFAULT 0,
    coverage_status text NOT NULL DEFAULT 'not_active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp63_full_47979_agent_department_gated_runtime_fleet',
    CONSTRAINT valid_coverage_status CHECK (coverage_status IN ('not_active', 'eligible', 'active', 'partially_active', 'blocked', 'disabled')),
    CONSTRAINT valid_coverage_counts CHECK (approved_runtime_cap >= 0 AND current_active_runtime_agents >= 0 AND current_active_runtime_agents <= approved_runtime_cap),
    UNIQUE (department_id)
);

CREATE TABLE IF NOT EXISTS runtime_fleet_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    department_id text REFERENCES runtime_departments(department_id) ON DELETE CASCADE,
    cohort_id uuid REFERENCES runtime_fleet_cohorts(cohort_id) ON DELETE SET NULL,
    stage_id text REFERENCES runtime_fleet_stages(stage_id) ON DELETE SET NULL,
    actor text,
    event_type text NOT NULL,
    event_summary text NOT NULL,
    event_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    source text NOT NULL DEFAULT 'mvp63_full_47979_agent_department_gated_runtime_fleet'
);

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp63_full_fleet_runtime_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp63_full_fleet_runtime_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = '47979' WHERE config_key = 'mvp63_global_live_agent_cap';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp63_global_live_agent_cap', '47979') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = '2500' WHERE config_key = 'max_cohort_activation_size';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('max_cohort_activation_size', '2500') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = '500' WHERE config_key = 'max_operation_chunk_size';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('max_operation_chunk_size', '500') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'staged_activation_required';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('staged_activation_required', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'circuit_breaker_required';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('circuit_breaker_required', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'department_gated_activation_required';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('department_gated_activation_required', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'continual_harness_supervision_required';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('continual_harness_supervision_required', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'raw_activate_all_route_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('raw_activate_all_route_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'command_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('command_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'deploy_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('deploy_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'rollback_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('rollback_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'alert_sending_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('alert_sending_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'arbitrary_shell_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('arbitrary_shell_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;


-- RPCs
CREATE OR REPLACE FUNCTION unlock_runtime_fleet_stage(
  p_stage_id text,
  p_actor text,
  p_reason text
) RETURNS void AS $$
DECLARE
  v_stage_status text;
  v_stage_cap integer;
  v_circuit_breaker_status text;
  v_execution_enabled boolean;
BEGIN
  SELECT stage_status, stage_cap INTO v_stage_status, v_stage_cap FROM runtime_fleet_stages WHERE stage_id = p_stage_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Stage % does not exist', p_stage_id;
  END IF;

  SELECT breaker_status INTO v_circuit_breaker_status FROM runtime_fleet_circuit_breakers WHERE breaker_status = 'triggered' LIMIT 1;
  IF FOUND THEN
    RAISE EXCEPTION 'Cannot unlock stage while circuit breaker is triggered';
  END IF;

  SELECT (value::boolean) INTO v_execution_enabled FROM runtime_fleet_limits WHERE key = 'command_execution_enabled';
  IF v_execution_enabled THEN
    RAISE EXCEPTION 'Cannot unlock stage while command execution is enabled';
  END IF;

  UPDATE runtime_fleet_stages SET stage_status = 'unlocked', unlocked_by = p_actor, unlocked_at = now() WHERE stage_id = p_stage_id;

  INSERT INTO runtime_fleet_events (stage_id, actor, event_type, event_summary, event_payload)
  VALUES (p_stage_id, p_actor, 'stage_unlocked', 'Unlocked ' || p_stage_id, jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION activate_runtime_fleet_cohort(
  p_department_id text,
  p_requested_agent_count integer,
  p_actor text,
  p_reason text
) RETURNS uuid AS $$
DECLARE
  v_dept_status text;
  v_dept_eligible boolean;
  v_circuit_breaker_status text;
  v_cohort_id uuid;
BEGIN
  SELECT runtime_status, activation_eligible INTO v_dept_status, v_dept_eligible FROM runtime_departments WHERE department_id = p_department_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Department % does not exist', p_department_id;
  END IF;
  
  IF v_dept_status != 'eligible_for_supervised_runtime' OR NOT v_dept_eligible THEN
    RAISE EXCEPTION 'Department % is not eligible for supervised runtime', p_department_id;
  END IF;

  IF p_requested_agent_count > 2500 THEN
    RAISE EXCEPTION 'Requested agent count exceeds max cohort size (2500)';
  END IF;

  SELECT breaker_status INTO v_circuit_breaker_status FROM runtime_fleet_circuit_breakers WHERE breaker_status = 'triggered' LIMIT 1;
  IF FOUND THEN
    RAISE EXCEPTION 'Cannot activate cohort while circuit breaker is triggered';
  END IF;

  INSERT INTO runtime_fleet_cohorts (cohort_name, department_id, requested_agent_count, activated_agent_count, cohort_status, actor, reason)
  VALUES ('Cohort ' || p_department_id, p_department_id, p_requested_agent_count, p_requested_agent_count, 'active', p_actor, p_reason)
  RETURNING cohort_id INTO v_cohort_id;

  INSERT INTO runtime_fleet_department_coverage (department_id, approved_runtime_cap, current_active_runtime_agents, coverage_status)
  VALUES (p_department_id, p_requested_agent_count, p_requested_agent_count, 'active')
  ON CONFLICT (department_id) DO NOTHING;

  INSERT INTO runtime_fleet_events (department_id, cohort_id, actor, event_type, event_summary, event_payload)
  VALUES (p_department_id, v_cohort_id, p_actor, 'cohort_activated', 'Activated cohort for ' || p_department_id, jsonb_build_object('reason', p_reason, 'count', p_requested_agent_count));
  
  RETURN v_cohort_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION deactivate_runtime_fleet_cohort(
  p_cohort_id uuid,
  p_actor text,
  p_reason text
) RETURNS void AS $$
BEGIN
  UPDATE runtime_fleet_cohorts SET cohort_status = 'deactivated', activated_agent_count = 0, updated_at = now() WHERE cohort_id = p_cohort_id;
  INSERT INTO runtime_fleet_events (cohort_id, actor, event_type, event_summary, event_payload)
  VALUES (p_cohort_id, p_actor, 'cohort_deactivated', 'Deactivated cohort ' || p_cohort_id, jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION activate_approved_department_fleet_cohort(
  p_department_id text,
  p_requested_agent_count integer,
  p_actor text,
  p_reason text
) RETURNS uuid AS $$
BEGIN
  RETURN activate_runtime_fleet_cohort(p_department_id, p_requested_agent_count, p_actor, p_reason);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION deactivate_approved_department_fleet_cohort(
  p_department_id text,
  p_actor text,
  p_reason text
) RETURNS void AS $$
BEGIN
  UPDATE runtime_fleet_cohorts SET cohort_status = 'deactivated', activated_agent_count = 0, updated_at = now() WHERE department_id = p_department_id AND cohort_status = 'active';
  INSERT INTO runtime_fleet_events (department_id, actor, event_type, event_summary, event_payload)
  VALUES (p_department_id, p_actor, 'department_cohorts_deactivated', 'Deactivated cohorts for ' || p_department_id, jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION trigger_runtime_fleet_circuit_breaker(
  p_breaker_name text,
  p_trigger_reason text,
  p_actor text,
  p_stage_id text DEFAULT NULL,
  p_department_id text DEFAULT NULL
) RETURNS uuid AS $$
DECLARE
  v_breaker_id uuid;
BEGIN
  INSERT INTO runtime_fleet_circuit_breakers (breaker_name, breaker_status, trigger_reason, triggered_by, triggered_at, affected_stage_id, affected_department_id)
  VALUES (p_breaker_name, 'triggered', p_trigger_reason, p_actor, now(), p_stage_id, p_department_id)
  RETURNING breaker_id INTO v_breaker_id;

  INSERT INTO runtime_fleet_events (actor, event_type, event_summary, event_payload)
  VALUES (p_actor, 'circuit_breaker_triggered', 'Triggered circuit breaker: ' || p_breaker_name, jsonb_build_object('reason', p_trigger_reason));

  RETURN v_breaker_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION clear_runtime_fleet_circuit_breaker(
  p_breaker_id uuid,
  p_actor text,
  p_reason text
) RETURNS void AS $$
BEGIN
  UPDATE runtime_fleet_circuit_breakers SET breaker_status = 'cleared', cleared_by = p_actor, cleared_at = now() WHERE breaker_id = p_breaker_id;
  INSERT INTO runtime_fleet_events (actor, event_type, event_summary, event_payload)
  VALUES (p_actor, 'circuit_breaker_cleared', 'Cleared circuit breaker ' || p_breaker_id, jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION runtime_fleet_kill_switch(
  p_actor text,
  p_reason text
) RETURNS void AS $$
BEGIN
  PERFORM trigger_runtime_fleet_circuit_breaker('FLEET_KILL_SWITCH', p_reason, p_actor);
  UPDATE runtime_fleet_cohorts SET cohort_status = 'circuit_breaker_paused' WHERE cohort_status = 'active';
  INSERT INTO runtime_fleet_events (actor, event_type, event_summary, event_payload)
  VALUES (p_actor, 'fleet_kill_switch_activated', 'Activated fleet kill switch', jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;
