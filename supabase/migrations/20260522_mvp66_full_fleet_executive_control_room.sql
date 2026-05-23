-- MVP-66 Full-Fleet Executive Control Room Migration

CREATE TABLE IF NOT EXISTS runtime_executive_control_room_snapshots (
    snapshot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    selected_mode text NOT NULL DEFAULT 'executive',
    total_registered_agents integer NOT NULL DEFAULT 47979,
    total_departments integer NOT NULL DEFAULT 1777,
    total_units integer NOT NULL DEFAULT 5331,
    total_families integer NOT NULL DEFAULT 175,
    full_fleet_cap integer NOT NULL DEFAULT 47979,
    current_live_runtime_agents integer NOT NULL DEFAULT 0,
    current_stage_cap integer NOT NULL DEFAULT 0,
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
    enterprise_readiness_status text NOT NULL DEFAULT 'review_ready',
    overall_status text NOT NULL DEFAULT 'review_ready',
    recommended_next_step text,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    source text NOT NULL DEFAULT 'mvp66_full_fleet_executive_control_room',
    CONSTRAINT valid_mode CHECK (selected_mode IN ('executive', 'operator', 'security_risk', 'technical', 'investor_recruiter', 'skeptical_reviewer')),
    CONSTRAINT valid_live_agents CHECK (current_live_runtime_agents >= 0 AND current_live_runtime_agents <= 47979),
    CONSTRAINT valid_enterprise_status CHECK (enterprise_readiness_status IN ('review_ready', 'pilot_ready', 'needs_review', 'blocked', 'unknown')),
    CONSTRAINT valid_overall_status CHECK (overall_status IN ('review_ready', 'healthy', 'degraded', 'paused', 'blocked', 'safe_state', 'review_required', 'unknown'))
);

CREATE TABLE IF NOT EXISTS runtime_executive_control_room_notes (
    note_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id uuid REFERENCES runtime_executive_control_room_snapshots(snapshot_id) ON DELETE SET NULL,
    reviewer_mode text NOT NULL DEFAULT 'executive',
    note_type text NOT NULL DEFAULT 'review_note',
    note_body text NOT NULL,
    actor text,
    source text NOT NULL DEFAULT 'mvp66_full_fleet_executive_control_room'
);

CREATE TABLE IF NOT EXISTS runtime_executive_review_questions (
    question_id text PRIMARY KEY,
    reviewer_mode text NOT NULL,
    question_text text NOT NULL,
    why_it_matters text,
    sort_order integer NOT NULL DEFAULT 0,
    enabled boolean NOT NULL DEFAULT true,
    source text NOT NULL DEFAULT 'mvp66_full_fleet_executive_control_room'
);

INSERT INTO runtime_executive_review_questions (question_id, reviewer_mode, question_text, why_it_matters, sort_order) VALUES
    ('exec_1', 'executive', 'What business problem does this solve?', 'Focuses review on ROI.', 1),
    ('exec_2', 'executive', 'What is ready for review today?', 'Clarifies scope.', 2),
    ('exec_3', 'executive', 'What is still intentionally disabled?', 'Sets safety expectations.', 3),
    ('exec_4', 'executive', 'What decision is being requested?', 'Drives the meeting forward.', 4),
    
    ('op_1', 'operator', 'What is currently live?', 'Operational awareness.', 1),
    ('op_2', 'operator', 'What is paused or blocked?', 'Issue isolation.', 2),
    ('op_3', 'operator', 'What should be checked first?', 'Prioritization.', 3),
    ('op_4', 'operator', 'What is the next safe operational action?', 'Guides the operator.', 4),
    
    ('sec_1', 'security_risk', 'What execution paths are disabled?', 'Proves non-destructive state.', 1),
    ('sec_2', 'security_risk', 'Where are the circuit breakers?', 'Identifies safety nets.', 2),
    ('sec_3', 'security_risk', 'What audit proof exists?', 'Ensures traceability.', 3),
    ('sec_4', 'security_risk', 'Can any page run commands, deploys, rollbacks, or alerts?', 'Verifies safety boundary.', 4),
    
    ('tech_1', 'technical', 'What tables, functions, and validators exist?', 'System architecture.', 1),
    ('tech_2', 'technical', 'How does data flow through the control plane?', 'Data integrity.', 2),
    ('tech_3', 'technical', 'What are the backend dependencies?', 'System coupling.', 3),
    ('tech_4', 'technical', 'Where are the safety gates enforced?', 'Implementation details.', 4),
    
    ('inv_1', 'investor_recruiter', 'What does this prove the builder can do?', 'Capability demonstration.', 1),
    ('inv_2', 'investor_recruiter', 'What is the scale of the system?', 'Scope of ambition.', 2),
    ('inv_3', 'investor_recruiter', 'What is the product story?', 'Market positioning.', 3),
    ('inv_4', 'investor_recruiter', 'What would a pilot look like?', 'Path to traction.', 4),
    
    ('skep_1', 'skeptical_reviewer', 'What sounds too big?', 'Directly addresses skepticism.', 1),
    ('skep_2', 'skeptical_reviewer', 'What is real versus simulated?', 'Transparency on state.', 2),
    ('skep_3', 'skeptical_reviewer', 'What would need proof before trusting this?', 'Requirements for trust.', 3),
    ('skep_4', 'skeptical_reviewer', 'Where could the system fail?', 'Honest risk assessment.', 4)
ON CONFLICT (question_id) DO NOTHING;


CREATE TABLE IF NOT EXISTS runtime_executive_decision_log (
    decision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id uuid REFERENCES runtime_executive_control_room_snapshots(snapshot_id) ON DELETE SET NULL,
    decision_type text NOT NULL DEFAULT 'review_decision',
    decision_status text NOT NULL DEFAULT 'pending',
    decision_summary text NOT NULL,
    actor text,
    source text NOT NULL DEFAULT 'mvp66_full_fleet_executive_control_room',
    CONSTRAINT valid_decision_status CHECK (decision_status IN ('pending', 'approved_for_review', 'needs_changes', 'blocked', 'deferred', 'completed'))
);

-- Update configuration
UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp66_executive_control_room_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp66_executive_control_room_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'review_ready' WHERE config_key = 'executive_control_room_status';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('executive_control_room_status', 'review_ready') ON CONFLICT (config_key) DO NOTHING;

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

CREATE OR REPLACE FUNCTION create_executive_control_room_snapshot(
  p_mode text DEFAULT 'executive',
  p_actor text DEFAULT 'executive_viewer'
) RETURNS uuid AS $$
DECLARE
  v_snapshot_id uuid;
  v_live_agents integer := 0;
  v_unlocked_stages integer := 0;
  v_current_stage_cap integer := 0;
  v_active_cohorts integer := 0;
  v_active_circuit_breakers integer := 0;
  v_approved_gates integer := 0;
  v_active_gates integer := 0;
  v_blocked_gates integer := 0;
  v_load_test_status text := 'unknown';
  v_overall_status text := 'review_ready';
  v_safe_state_status text := 'unknown';
  v_continual_harness_status text := 'unknown';
  v_audit_status text := 'unknown';
BEGIN
  IF p_mode NOT IN ('executive', 'operator', 'security_risk', 'technical', 'investor_recruiter', 'skeptical_reviewer') THEN
    RAISE EXCEPTION 'Invalid reviewer mode: %', p_mode;
  END IF;

  -- Safely gather metrics if tables exist
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
    SELECT 
      COUNT(*) FILTER (WHERE gate_status = 'approved'),
      COUNT(*) FILTER (WHERE gate_status = 'active'),
      COUNT(*) FILTER (WHERE gate_status = 'blocked')
    INTO v_approved_gates, v_active_gates, v_blocked_gates
    FROM department_runtime_gates;
  EXCEPTION WHEN undefined_table THEN END;

  BEGIN
    SELECT COUNT(breaker_id) INTO v_active_circuit_breakers 
    FROM runtime_fleet_circuit_breakers WHERE breaker_status = 'triggered';
  EXCEPTION WHEN undefined_table THEN END;

  BEGIN
    SELECT test_status, CASE WHEN safe_state_restored THEN 'restored' ELSE 'not_restored' END
    INTO v_load_test_status, v_safe_state_status
    FROM runtime_fleet_load_tests ORDER BY created_at DESC LIMIT 1;
  EXCEPTION WHEN undefined_table THEN END;
  
  -- Assuming observability snapshot might have audit/harness info
  BEGIN
    SELECT continual_harness_status, audit_status INTO v_continual_harness_status, v_audit_status
    FROM runtime_observability_snapshots ORDER BY created_at DESC LIMIT 1;
  EXCEPTION WHEN undefined_table THEN END;

  INSERT INTO runtime_executive_control_room_snapshots (
    selected_mode,
    current_live_runtime_agents,
    current_stage_cap,
    unlocked_stages,
    approved_department_gates,
    active_department_gates,
    blocked_department_gates,
    active_cohorts,
    active_circuit_breakers,
    load_test_status,
    safe_state_status,
    continual_harness_status,
    audit_status,
    overall_status,
    recommended_next_step
  ) VALUES (
    p_mode,
    v_live_agents,
    v_current_stage_cap,
    v_unlocked_stages,
    v_approved_gates,
    v_active_gates,
    v_blocked_gates,
    v_active_cohorts,
    v_active_circuit_breakers,
    v_load_test_status,
    v_safe_state_status,
    v_continual_harness_status,
    v_audit_status,
    v_overall_status,
    'Review system state and finalize readiness.'
  ) RETURNING snapshot_id INTO v_snapshot_id;

  RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_executive_control_room_note(
  p_snapshot_id uuid,
  p_reviewer_mode text,
  p_note_body text,
  p_actor text,
  p_note_type text DEFAULT 'review_note'
) RETURNS uuid AS $$
DECLARE
  v_note_id uuid;
BEGIN
  INSERT INTO runtime_executive_control_room_notes (snapshot_id, reviewer_mode, note_type, note_body, actor)
  VALUES (p_snapshot_id, p_reviewer_mode, p_note_type, p_note_body, p_actor)
  RETURNING note_id INTO v_note_id;
  RETURN v_note_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION export_executive_control_room_report(
  p_snapshot_id uuid,
  p_actor text DEFAULT 'operator'
) RETURNS jsonb AS $$
DECLARE
  v_snapshot record;
  v_notes jsonb;
  v_decisions jsonb;
  v_questions jsonb;
BEGIN
  SELECT * INTO v_snapshot FROM runtime_executive_control_room_snapshots WHERE snapshot_id = p_snapshot_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Snapshot % does not exist', p_snapshot_id;
  END IF;

  SELECT jsonb_agg(n) INTO v_notes FROM runtime_executive_control_room_notes n WHERE snapshot_id = p_snapshot_id;
  SELECT jsonb_agg(d) INTO v_decisions FROM runtime_executive_decision_log d WHERE snapshot_id = p_snapshot_id;
  SELECT jsonb_agg(q) INTO v_questions FROM runtime_executive_review_questions q WHERE reviewer_mode = v_snapshot.selected_mode AND enabled = true;

  RETURN jsonb_build_object(
    'snapshot', to_jsonb(v_snapshot),
    'notes', v_notes,
    'decisions', v_decisions,
    'questions', v_questions,
    'exported_by', p_actor,
    'exported_at', now()
  );
END;
$$ LANGUAGE plpgsql;
