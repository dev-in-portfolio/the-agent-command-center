-- MVP-64 Full-Fleet Load Test, Failure Simulation, and Recovery Drill Migration

CREATE TABLE IF NOT EXISTS runtime_fleet_load_tests (
    load_test_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name text NOT NULL,
    test_status text NOT NULL DEFAULT 'planned',
    target_stage_cap integer NOT NULL DEFAULT 47979,
    simulated_agent_count integer NOT NULL DEFAULT 0,
    simulated_department_count integer NOT NULL DEFAULT 0,
    simulated_cohort_count integer NOT NULL DEFAULT 0,
    started_by text,
    started_at timestamptz,
    paused_at timestamptz,
    completed_at timestamptz,
    failure_count integer NOT NULL DEFAULT 0,
    recovery_count integer NOT NULL DEFAULT 0,
    circuit_breaker_triggered boolean NOT NULL DEFAULT false,
    safe_state_restored boolean NOT NULL DEFAULT false,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp64_full_fleet_load_test_failure_recovery',
    CONSTRAINT valid_test_status CHECK (test_status IN ('planned', 'running', 'paused', 'completed', 'failed', 'blocked', 'safe_state_restored')),
    CONSTRAINT valid_target_cap CHECK (target_stage_cap <= 47979),
    CONSTRAINT valid_simulated_cap CHECK (simulated_agent_count <= 47979)
);

CREATE TABLE IF NOT EXISTS runtime_fleet_failure_scenarios (
    scenario_id text PRIMARY KEY,
    scenario_name text NOT NULL,
    scenario_type text NOT NULL,
    risk_level text NOT NULL DEFAULT 'medium',
    enabled boolean NOT NULL DEFAULT true,
    requires_circuit_breaker boolean NOT NULL DEFAULT false,
    description text,
    expected_safe_response text,
    source text NOT NULL DEFAULT 'mvp64_full_fleet_load_test_failure_recovery'
);

INSERT INTO runtime_fleet_failure_scenarios (scenario_id, scenario_name, scenario_type, requires_circuit_breaker, description, expected_safe_response) VALUES
    ('heartbeat_drop', 'Agent Heartbeat Drop', 'timeout', false, 'Simulates a loss of agent heartbeats across a department.', 'Flag agents as unresponsive.'),
    ('department_gate_mismatch', 'Department Gate Mismatch', 'auth', false, 'Simulates a request from an unapproved department.', 'Reject request.'),
    ('cohort_over_cap_attempt', 'Cohort Over-Cap Attempt', 'limit', false, 'Simulates activating more agents than allowed.', 'Reject request.'),
    ('stage_unlock_failure', 'Stage Unlock Failure', 'state', false, 'Simulates attempting to unlock out of sequence.', 'Reject request.'),
    ('circuit_breaker_trigger', 'Circuit Breaker Trigger', 'safety', true, 'Simulates a critical condition requiring full breaker.', 'Pause operations.'),
    ('recovery_safe_state', 'Recovery Safe State Verification', 'audit', false, 'Simulates verifying safe state.', 'Confirm safe state.'),
    ('audit_gap_detection', 'Audit Gap Detection', 'audit', false, 'Simulates a failure to write audit logs.', 'Reject request.'),
    ('readiness_rollup_degraded', 'Readiness Rollup Degraded', 'health', false, 'Simulates a degraded readiness rollup.', 'Flag system state.'),
    ('continual_harness_degraded', 'Continual Harness Degraded', 'health', false, 'Simulates a degraded supervisor harness.', 'Flag supervisor state.'),
    ('raw_activate_all_attempt_blocked', 'Raw Activate-All Attempt Blocked', 'security', false, 'Simulates an attempt to bypass staged activation.', 'Reject request.')
ON CONFLICT (scenario_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS runtime_fleet_recovery_drills (
    drill_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    load_test_id uuid REFERENCES runtime_fleet_load_tests(load_test_id) ON DELETE CASCADE,
    drill_name text NOT NULL,
    drill_status text NOT NULL DEFAULT 'planned',
    failure_scenario_id text REFERENCES runtime_fleet_failure_scenarios(scenario_id) ON DELETE SET NULL,
    recovery_action text NOT NULL,
    verified_safe_state boolean NOT NULL DEFAULT false,
    verified_audit_events boolean NOT NULL DEFAULT false,
    verified_circuit_breaker boolean NOT NULL DEFAULT false,
    verified_no_execution boolean NOT NULL DEFAULT false,
    actor text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp64_full_fleet_load_test_failure_recovery',
    CONSTRAINT valid_drill_status CHECK (drill_status IN ('planned', 'running', 'verified', 'failed', 'blocked'))
);

CREATE TABLE IF NOT EXISTS runtime_fleet_load_test_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    load_test_id uuid REFERENCES runtime_fleet_load_tests(load_test_id) ON DELETE CASCADE,
    drill_id uuid REFERENCES runtime_fleet_recovery_drills(drill_id) ON DELETE SET NULL,
    scenario_id text REFERENCES runtime_fleet_failure_scenarios(scenario_id) ON DELETE SET NULL,
    actor text,
    event_type text NOT NULL,
    event_summary text NOT NULL,
    event_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    source text NOT NULL DEFAULT 'mvp64_full_fleet_load_test_failure_recovery'
);

CREATE TABLE IF NOT EXISTS runtime_fleet_load_test_rollups (
    rollup_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    total_registered_agents integer NOT NULL DEFAULT 47979,
    total_departments integer NOT NULL DEFAULT 1777,
    full_fleet_cap integer NOT NULL DEFAULT 47979,
    active_load_tests integer NOT NULL DEFAULT 0,
    completed_load_tests integer NOT NULL DEFAULT 0,
    simulated_failures integer NOT NULL DEFAULT 0,
    verified_recoveries integer NOT NULL DEFAULT 0,
    circuit_breaker_drills integer NOT NULL DEFAULT 0,
    safe_state_restored_count integer NOT NULL DEFAULT 0,
    audit_gap_count integer NOT NULL DEFAULT 0,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    source text NOT NULL DEFAULT 'mvp64_full_fleet_load_test_failure_recovery'
);

CREATE TABLE IF NOT EXISTS runtime_fleet_load_test_reports (
    report_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    load_test_id uuid REFERENCES runtime_fleet_load_tests(load_test_id) ON DELETE CASCADE,
    report_status text NOT NULL DEFAULT 'generated',
    report_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    generated_by text,
    generated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp64_full_fleet_load_test_failure_recovery'
);

-- Update configuration
UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp64_full_fleet_load_testing_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp64_full_fleet_load_testing_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp64_failure_simulation_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp64_failure_simulation_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp64_recovery_drill_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp64_recovery_drill_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp64_safe_state_restoration_required';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp64_safe_state_restoration_required', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = '47979' WHERE config_key = 'full_fleet_cap';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('full_fleet_cap', '47979') ON CONFLICT (config_key) DO NOTHING;


-- RPCs

CREATE OR REPLACE FUNCTION start_fleet_load_test(
  p_test_name text,
  p_simulated_agent_count integer,
  p_simulated_department_count integer,
  p_actor text,
  p_reason text
) RETURNS uuid AS $$
DECLARE
  v_load_test_id uuid;
BEGIN
  IF p_simulated_agent_count > 47979 THEN
    RAISE EXCEPTION 'Simulated agent count cannot exceed global limit (47979)';
  END IF;

  INSERT INTO runtime_fleet_load_tests (test_name, simulated_agent_count, simulated_department_count, started_by, started_at, test_status)
  VALUES (p_test_name, p_simulated_agent_count, p_simulated_department_count, p_actor, now(), 'running')
  RETURNING load_test_id INTO v_load_test_id;

  INSERT INTO runtime_fleet_load_test_events (load_test_id, actor, event_type, event_summary, event_payload)
  VALUES (v_load_test_id, p_actor, 'load_test_started', 'Started load test: ' || p_test_name, jsonb_build_object('reason', p_reason, 'agent_count', p_simulated_agent_count));

  RETURN v_load_test_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION pause_fleet_load_test(
  p_load_test_id uuid,
  p_actor text,
  p_reason text
) RETURNS void AS $$
BEGIN
  UPDATE runtime_fleet_load_tests SET test_status = 'paused', paused_at = now() WHERE load_test_id = p_load_test_id;

  INSERT INTO runtime_fleet_load_test_events (load_test_id, actor, event_type, event_summary, event_payload)
  VALUES (p_load_test_id, p_actor, 'load_test_paused', 'Paused load test', jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION complete_fleet_load_test(
  p_load_test_id uuid,
  p_actor text,
  p_reason text
) RETURNS void AS $$
DECLARE
  v_safe_restored boolean;
BEGIN
  SELECT safe_state_restored INTO v_safe_restored FROM runtime_fleet_load_tests WHERE load_test_id = p_load_test_id;
  
  -- The requirement says: "requires safe_state_restored true or verified recovery drill". We will enforce safe_state_restored being true.
  IF NOT v_safe_restored THEN
    RAISE EXCEPTION 'Cannot complete load test without safe state restored';
  END IF;

  UPDATE runtime_fleet_load_tests SET test_status = 'completed', completed_at = now() WHERE load_test_id = p_load_test_id;

  INSERT INTO runtime_fleet_load_test_events (load_test_id, actor, event_type, event_summary, event_payload)
  VALUES (p_load_test_id, p_actor, 'load_test_completed', 'Completed load test', jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION simulate_fleet_failure(
  p_load_test_id uuid,
  p_scenario_id text,
  p_actor text,
  p_details jsonb DEFAULT '{}'::jsonb
) RETURNS void AS $$
DECLARE
  v_enabled boolean;
  v_requires_cb boolean;
BEGIN
  SELECT enabled, requires_circuit_breaker INTO v_enabled, v_requires_cb 
  FROM runtime_fleet_failure_scenarios 
  WHERE scenario_id = p_scenario_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Failure scenario % does not exist', p_scenario_id;
  END IF;

  IF NOT v_enabled THEN
    RAISE EXCEPTION 'Failure scenario % is disabled', p_scenario_id;
  END IF;

  UPDATE runtime_fleet_load_tests 
  SET failure_count = failure_count + 1,
      circuit_breaker_triggered = CASE WHEN v_requires_cb THEN true ELSE circuit_breaker_triggered END
  WHERE load_test_id = p_load_test_id;

  INSERT INTO runtime_fleet_load_test_events (load_test_id, scenario_id, actor, event_type, event_summary, event_payload)
  VALUES (p_load_test_id, p_scenario_id, p_actor, 'failure_simulated', 'Simulated failure: ' || p_scenario_id, p_details);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION trigger_recovery_drill(
  p_load_test_id uuid,
  p_scenario_id text,
  p_actor text,
  p_recovery_action text
) RETURNS uuid AS $$
DECLARE
  v_drill_id uuid;
BEGIN
  INSERT INTO runtime_fleet_recovery_drills (load_test_id, drill_name, failure_scenario_id, recovery_action, actor, drill_status)
  VALUES (p_load_test_id, 'Recovery Drill for ' || p_scenario_id, p_scenario_id, p_recovery_action, p_actor, 'running')
  RETURNING drill_id INTO v_drill_id;

  INSERT INTO runtime_fleet_load_test_events (load_test_id, drill_id, scenario_id, actor, event_type, event_summary, event_payload)
  VALUES (p_load_test_id, v_drill_id, p_scenario_id, p_actor, 'recovery_drill_started', 'Triggered recovery drill', jsonb_build_object('action', p_recovery_action));

  RETURN v_drill_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION verify_recovery_drill(
  p_drill_id uuid,
  p_actor text,
  p_reason text
) RETURNS void AS $$
DECLARE
  v_load_test_id uuid;
BEGIN
  UPDATE runtime_fleet_recovery_drills 
  SET drill_status = 'verified', 
      verified_safe_state = true, 
      verified_audit_events = true, 
      verified_circuit_breaker = true, 
      verified_no_execution = true, 
      updated_at = now()
  WHERE drill_id = p_drill_id
  RETURNING load_test_id INTO v_load_test_id;

  UPDATE runtime_fleet_load_tests 
  SET safe_state_restored = true,
      recovery_count = recovery_count + 1
  WHERE load_test_id = v_load_test_id;

  INSERT INTO runtime_fleet_load_test_events (load_test_id, drill_id, actor, event_type, event_summary, event_payload)
  VALUES (v_load_test_id, p_drill_id, p_actor, 'recovery_drill_verified', 'Verified recovery drill', jsonb_build_object('reason', p_reason));
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION export_fleet_load_test_report(
  p_load_test_id uuid,
  p_actor text
) RETURNS jsonb AS $$
DECLARE
  v_test_record record;
  v_drills jsonb;
  v_events jsonb;
  v_payload jsonb;
  v_report_id uuid;
BEGIN
  SELECT * INTO v_test_record FROM runtime_fleet_load_tests WHERE load_test_id = p_load_test_id;
  
  SELECT jsonb_agg(d) INTO v_drills FROM runtime_fleet_recovery_drills d WHERE load_test_id = p_load_test_id;
  SELECT jsonb_agg(e) INTO v_events FROM runtime_fleet_load_test_events e WHERE load_test_id = p_load_test_id;

  v_payload := jsonb_build_object(
    'load_test', to_jsonb(v_test_record),
    'drills', v_drills,
    'events', v_events
  );

  INSERT INTO runtime_fleet_load_test_reports (load_test_id, report_payload, generated_by)
  VALUES (p_load_test_id, v_payload, p_actor)
  RETURNING report_id INTO v_report_id;

  RETURN jsonb_build_object('report_id', v_report_id, 'payload', v_payload);
END;
$$ LANGUAGE plpgsql;
