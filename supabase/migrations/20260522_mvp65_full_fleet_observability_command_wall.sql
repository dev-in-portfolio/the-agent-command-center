-- MVP-65 Full-Fleet Observability Command Wall Migration

CREATE TABLE IF NOT EXISTS runtime_observability_snapshots (
    snapshot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    total_registered_agents integer NOT NULL DEFAULT 47979,
    total_departments integer NOT NULL DEFAULT 1777,
    total_units integer NOT NULL DEFAULT 5331,
    total_families integer NOT NULL DEFAULT 175,
    full_fleet_cap integer NOT NULL DEFAULT 47979,
    current_live_runtime_agents integer NOT NULL DEFAULT 0,
    current_stage_cap integer NOT NULL DEFAULT 0,
    unlocked_stages integer NOT NULL DEFAULT 0,
    approved_department_gates integer NOT NULL DEFAULT 0,
    active_department_gates integer NOT NULL DEFAULT 0,
    blocked_department_gates integer NOT NULL DEFAULT 0,
    active_cohorts integer NOT NULL DEFAULT 0,
    active_circuit_breakers integer NOT NULL DEFAULT 0,
    continual_harness_status text NOT NULL DEFAULT 'unknown',
    load_test_status text NOT NULL DEFAULT 'unknown',
    recovery_drill_status text NOT NULL DEFAULT 'unknown',
    safe_state_status text NOT NULL DEFAULT 'unknown',
    audit_status text NOT NULL DEFAULT 'unknown',
    overall_status text NOT NULL DEFAULT 'unknown',
    recommended_action text,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    source text NOT NULL DEFAULT 'mvp65_full_fleet_observability_command_wall',
    CONSTRAINT valid_live_agents CHECK (current_live_runtime_agents >= 0 AND current_live_runtime_agents <= 47979),
    CONSTRAINT valid_overall_status CHECK (overall_status IN ('unknown', 'healthy', 'degraded', 'paused', 'blocked', 'safe_state', 'review_required'))
);

CREATE TABLE IF NOT EXISTS runtime_observability_events (
    event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id uuid REFERENCES runtime_observability_snapshots(snapshot_id) ON DELETE SET NULL,
    event_type text NOT NULL,
    event_summary text NOT NULL,
    event_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    actor text,
    source text NOT NULL DEFAULT 'mvp65_full_fleet_observability_command_wall'
);

CREATE TABLE IF NOT EXISTS runtime_observability_notes (
    note_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id uuid REFERENCES runtime_observability_snapshots(snapshot_id) ON DELETE SET NULL,
    note_type text NOT NULL DEFAULT 'operator_note',
    note_body text NOT NULL,
    actor text,
    source text NOT NULL DEFAULT 'mvp65_full_fleet_observability_command_wall'
);

CREATE TABLE IF NOT EXISTS runtime_observability_state_flags (
    flag_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_key text NOT NULL,
    flag_status text NOT NULL DEFAULT 'clear',
    flag_summary text,
    severity text NOT NULL DEFAULT 'info',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    source text NOT NULL DEFAULT 'mvp65_full_fleet_observability_command_wall',
    CONSTRAINT valid_flag_status CHECK (flag_status IN ('clear', 'watch', 'warning', 'blocked', 'paused', 'resolved')),
    CONSTRAINT valid_flag_severity CHECK (severity IN ('info', 'low', 'medium', 'high', 'critical'))
);

-- Update configuration
UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp65_observability_command_wall_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp65_observability_command_wall_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'observability_status_only';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('observability_status_only', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'external_alert_sending_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('external_alert_sending_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

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

CREATE OR REPLACE FUNCTION create_full_fleet_observability_snapshot(
  p_actor text DEFAULT 'system_observer'
) RETURNS uuid AS $$
DECLARE
  v_snapshot_id uuid;
  v_live_agents integer := 0;
  v_unlocked_stages integer := 0;
  v_current_stage_cap integer := 0;
  v_active_cohorts integer := 0;
  v_active_circuit_breakers integer := 0;
  v_load_test_status text := 'unknown';
  v_overall_status text := 'healthy';
  v_safe_state_status text := 'unknown';
BEGIN
  -- Safely gather metrics if tables exist (simplified for robust execution)
  BEGIN
    SELECT COALESCE(SUM(activated_agent_count), 0), COUNT(cohort_id) 
    INTO v_live_agents, v_active_cohorts 
    FROM runtime_fleet_cohorts WHERE cohort_status = 'active';
  EXCEPTION WHEN undefined_table THEN END;

  BEGIN
    SELECT COUNT(stage_id), COALESCE(MAX(stage_cap), 0) 
    INTO v_unlocked_stages, v_current_stage_cap 
    FROM runtime_fleet_stages WHERE stage_status = 'unlocked';
  EXCEPTION WHEN undefined_table THEN END;

  BEGIN
    SELECT COUNT(breaker_id) INTO v_active_circuit_breakers 
    FROM runtime_fleet_circuit_breakers WHERE breaker_status = 'triggered';
    IF v_active_circuit_breakers > 0 THEN
      v_overall_status := 'paused';
    END IF;
  EXCEPTION WHEN undefined_table THEN END;

  BEGIN
    SELECT test_status, CASE WHEN safe_state_restored THEN 'restored' ELSE 'not_restored' END
    INTO v_load_test_status, v_safe_state_status
    FROM runtime_fleet_load_tests ORDER BY created_at DESC LIMIT 1;
  EXCEPTION WHEN undefined_table THEN END;

  INSERT INTO runtime_observability_snapshots (
    current_live_runtime_agents,
    current_stage_cap,
    unlocked_stages,
    active_cohorts,
    active_circuit_breakers,
    load_test_status,
    safe_state_status,
    overall_status,
    recommended_action
  ) VALUES (
    v_live_agents,
    v_current_stage_cap,
    v_unlocked_stages,
    v_active_cohorts,
    v_active_circuit_breakers,
    v_load_test_status,
    v_safe_state_status,
    v_overall_status,
    CASE WHEN v_active_circuit_breakers > 0 THEN 'Review circuit breaker triggers' ELSE 'Monitor normal operations' END
  ) RETURNING snapshot_id INTO v_snapshot_id;

  INSERT INTO runtime_observability_events (snapshot_id, event_type, event_summary, actor)
  VALUES (v_snapshot_id, 'snapshot_created', 'Created full-fleet observability snapshot', p_actor);

  RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_observability_note(
  p_snapshot_id uuid,
  p_note_body text,
  p_actor text,
  p_note_type text DEFAULT 'operator_note'
) RETURNS uuid AS $$
DECLARE
  v_note_id uuid;
BEGIN
  INSERT INTO runtime_observability_notes (snapshot_id, note_type, note_body, actor)
  VALUES (p_snapshot_id, p_note_type, p_note_body, p_actor)
  RETURNING note_id INTO v_note_id;

  INSERT INTO runtime_observability_events (snapshot_id, event_type, event_summary, event_payload, actor)
  VALUES (p_snapshot_id, 'note_created', 'Created observability note', jsonb_build_object('note_type', p_note_type, 'note_body', p_note_body), p_actor);

  RETURN v_note_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION export_observability_report(
  p_snapshot_id uuid,
  p_actor text DEFAULT 'operator'
) RETURNS jsonb AS $$
DECLARE
  v_snapshot record;
  v_notes jsonb;
  v_flags jsonb;
  v_events jsonb;
BEGIN
  SELECT * INTO v_snapshot FROM runtime_observability_snapshots WHERE snapshot_id = p_snapshot_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Snapshot % does not exist', p_snapshot_id;
  END IF;

  SELECT jsonb_agg(n) INTO v_notes FROM runtime_observability_notes n WHERE snapshot_id = p_snapshot_id;
  SELECT jsonb_agg(f) INTO v_flags FROM runtime_observability_state_flags f;
  SELECT jsonb_agg(e) INTO v_events FROM runtime_observability_events e WHERE snapshot_id = p_snapshot_id;

  RETURN jsonb_build_object(
    'snapshot', to_jsonb(v_snapshot),
    'notes', v_notes,
    'flags', v_flags,
    'events', v_events,
    'exported_by', p_actor,
    'exported_at', now()
  );
END;
$$ LANGUAGE plpgsql;
