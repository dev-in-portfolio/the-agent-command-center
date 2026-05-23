-- MVP-67 Enterprise Pilot Room Migration

CREATE TABLE IF NOT EXISTS enterprise_pilot_snapshots (
    snapshot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    pilot_status text NOT NULL DEFAULT 'review_ready',
    pilot_scope text NOT NULL DEFAULT 'controlled_enterprise_review',
    total_registered_agents integer NOT NULL DEFAULT 47979,
    total_departments integer NOT NULL DEFAULT 1777,
    total_units integer NOT NULL DEFAULT 5331,
    total_families integer NOT NULL DEFAULT 175,
    full_fleet_cap integer NOT NULL DEFAULT 47979,
    current_live_runtime_agents integer NOT NULL DEFAULT 0,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    external_alert_sending_enabled boolean NOT NULL DEFAULT false,
    pilot_runtime_permission_granted boolean NOT NULL DEFAULT false,
    legal_review_required boolean NOT NULL DEFAULT true,
    security_review_required boolean NOT NULL DEFAULT true,
    technical_review_required boolean NOT NULL DEFAULT true,
    stakeholder_review_required boolean NOT NULL DEFAULT true,
    recommended_next_step text,
    source text NOT NULL DEFAULT 'mvp67_enterprise_pilot_room',
    CONSTRAINT valid_pilot_status CHECK (pilot_status IN ('review_ready', 'pilot_ready', 'needs_changes', 'blocked', 'deferred', 'approved_for_limited_pilot', 'completed'))
);

CREATE TABLE IF NOT EXISTS enterprise_pilot_stakeholder_roles (
    role_id text PRIMARY KEY,
    role_name text NOT NULL,
    role_description text NOT NULL,
    responsibility_summary text NOT NULL,
    required_for_go_decision boolean NOT NULL DEFAULT true,
    sort_order integer NOT NULL DEFAULT 0,
    source text NOT NULL DEFAULT 'mvp67_enterprise_pilot_room'
);

INSERT INTO enterprise_pilot_stakeholder_roles (role_id, role_name, role_description, responsibility_summary, sort_order) VALUES
    ('executive_sponsor', 'Executive Sponsor', 'Owns the pilot outcome.', 'Provides budget, strategic alignment, and final approval.', 1),
    ('technical_reviewer', 'Technical Reviewer', 'Validates architecture.', 'Confirms scalability, integrations, and codebase structure.', 2),
    ('security_risk_reviewer', 'Security / Risk Reviewer', 'Assesses vulnerabilities.', 'Validates boundaries, audit trails, and execution disabled states.', 3),
    ('legal_reviewer', 'Legal Reviewer', 'Reviews compliance.', 'Approves NDAs, IP ownership, and data privacy models.', 4),
    ('operator_reviewer', 'Operator Reviewer', 'Validates usability.', 'Confirms the control room is observable and operational.', 5),
    ('pilot_owner', 'Pilot Owner', 'Runs the pilot.', 'Drives the daily execution and manages the review checklists.', 6),
    ('decision_maker', 'Decision Maker', 'Signs off.', 'Makes the final Go/No-Go call on the limited pilot.', 7)
ON CONFLICT (role_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS enterprise_pilot_success_criteria (
    criterion_id text PRIMARY KEY,
    criterion_group text NOT NULL,
    criterion_text text NOT NULL,
    measurement_method text NOT NULL,
    required_for_success boolean NOT NULL DEFAULT true,
    status text NOT NULL DEFAULT 'pending_review',
    source text NOT NULL DEFAULT 'mvp67_enterprise_pilot_room',
    CONSTRAINT valid_status CHECK (status IN ('pending_review', 'accepted', 'needs_revision', 'blocked', 'met', 'not_met'))
);

INSERT INTO enterprise_pilot_success_criteria (criterion_id, criterion_group, criterion_text, measurement_method) VALUES
    ('clarity_1', 'clarity', 'Pilot scope is narrowly defined.', 'Documented in decision log.'),
    ('security_1', 'security', 'All destructive execution is disabled.', 'Verified via validator scripts.'),
    ('tech_1', 'technical_readiness', 'System handles control plane load testing.', 'MVP-64 load tests pass.'),
    ('ops_1', 'operational_readiness', 'Control wall provides full observability.', 'MVP-65 command wall is active.'),
    ('legal_1', 'legal_review', 'Data boundary and ownership are clear.', 'Legal review note logged.'),
    ('scope_1', 'pilot_scope', 'Pilot limits to a specific department or function.', 'Approved department gate selected.'),
    ('stake_1', 'stakeholder_confidence', 'All required roles have reviewed.', 'Decision log reflects sign-offs.')
ON CONFLICT (criterion_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS enterprise_pilot_risk_register (
    risk_id text PRIMARY KEY,
    risk_name text NOT NULL,
    risk_summary text NOT NULL,
    risk_level text NOT NULL DEFAULT 'medium',
    mitigation_summary text NOT NULL,
    owner_role text,
    status text NOT NULL DEFAULT 'open',
    source text NOT NULL DEFAULT 'mvp67_enterprise_pilot_room',
    CONSTRAINT valid_risk_level CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_risk_status CHECK (status IN ('open', 'mitigated', 'accepted', 'blocked', 'closed'))
);

INSERT INTO enterprise_pilot_risk_register (risk_id, risk_name, risk_summary, risk_level, mitigation_summary, owner_role) VALUES
    ('misunderstanding_static_vs_runtime', 'Static vs Runtime Confusion', 'Stakeholders assume agents are live.', 'medium', 'Clear UI copy enforcing zero live agents.', 'executive_sponsor'),
    ('unauthorized_activation', 'Unauthorized Activation', 'Accidental raw fleet start.', 'high', 'Raw activate-all routes removed. Circuit breakers in place.', 'technical_reviewer'),
    ('command_execution_confusion', 'Command Execution Confusion', 'Stakeholders assume UI buttons run shell scripts.', 'medium', 'Copy explicitly states command execution is disabled.', 'pilot_owner'),
    ('data_boundary_unclear', 'Data Boundary Unclear', 'Uncertainty about where agent data goes.', 'high', 'Legal review of data isolation.', 'legal_reviewer'),
    ('legal_ownership_unclear', 'Legal Ownership Unclear', 'IP or output ownership undefined.', 'high', 'Clear copyright and terms of service.', 'legal_reviewer'),
    ('security_review_incomplete', 'Security Review Incomplete', 'Moving to pilot without infosec signoff.', 'critical', 'Mandatory security checklist in decision log.', 'security_risk_reviewer'),
    ('pilot_scope_creep', 'Pilot Scope Creep', 'Pilot attempts to boil the ocean.', 'medium', 'Strict adherence to limited department gates.', 'pilot_owner'),
    ('stakeholder_confusion', 'Stakeholder Confusion', 'Disagreement on what success means.', 'medium', 'Defined success criteria and role definitions.', 'executive_sponsor')
ON CONFLICT (risk_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS enterprise_pilot_review_notes (
    note_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id uuid REFERENCES enterprise_pilot_snapshots(snapshot_id) ON DELETE SET NULL,
    reviewer_role text,
    note_type text NOT NULL DEFAULT 'review_note',
    note_body text NOT NULL,
    actor text,
    source text NOT NULL DEFAULT 'mvp67_enterprise_pilot_room'
);

CREATE TABLE IF NOT EXISTS enterprise_pilot_decision_log (
    decision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id uuid REFERENCES enterprise_pilot_snapshots(snapshot_id) ON DELETE SET NULL,
    decision_type text NOT NULL DEFAULT 'pilot_decision',
    decision_status text NOT NULL DEFAULT 'pending',
    decision_summary text NOT NULL,
    actor text,
    source text NOT NULL DEFAULT 'mvp67_enterprise_pilot_room',
    CONSTRAINT valid_log_status CHECK (decision_status IN ('pending', 'approved_for_review', 'approved_for_limited_pilot', 'needs_changes', 'blocked', 'deferred', 'rejected', 'completed'))
);

-- Update configuration
UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp67_enterprise_pilot_room_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp67_enterprise_pilot_room_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'review_ready' WHERE config_key = 'enterprise_pilot_status';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('enterprise_pilot_status', 'review_ready') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'pilot_runtime_permission_granted';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('pilot_runtime_permission_granted', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'command_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('command_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'deploy_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('deploy_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'rollback_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('rollback_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'alert_sending_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('alert_sending_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'external_alert_sending_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('external_alert_sending_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'false' WHERE config_key = 'arbitrary_shell_execution_enabled';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('arbitrary_shell_execution_enabled', 'false') ON CONFLICT (config_key) DO NOTHING;

-- RPCs

CREATE OR REPLACE FUNCTION create_enterprise_pilot_snapshot(
  p_actor text DEFAULT 'pilot_viewer'
) RETURNS uuid AS $$
DECLARE
  v_snapshot_id uuid;
  v_live_agents integer := 0;
  v_pilot_status text := 'review_ready';
BEGIN
  -- Check live agents from executive snapshots if available
  BEGIN
    SELECT current_live_runtime_agents INTO v_live_agents
    FROM runtime_executive_control_room_snapshots ORDER BY created_at DESC LIMIT 1;
  EXCEPTION WHEN undefined_table THEN END;

  -- Defaulting to 0 since we know activation isn't happening here
  v_live_agents := COALESCE(v_live_agents, 0);

  INSERT INTO enterprise_pilot_snapshots (
    pilot_status,
    current_live_runtime_agents,
    recommended_next_step
  ) VALUES (
    v_pilot_status,
    v_live_agents,
    'Review stakeholder package and log decision.'
  ) RETURNING snapshot_id INTO v_snapshot_id;

  RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_enterprise_pilot_note(
  p_snapshot_id uuid,
  p_reviewer_role text,
  p_note_body text,
  p_actor text,
  p_note_type text DEFAULT 'review_note'
) RETURNS uuid AS $$
DECLARE
  v_note_id uuid;
BEGIN
  INSERT INTO enterprise_pilot_review_notes (snapshot_id, reviewer_role, note_type, note_body, actor)
  VALUES (p_snapshot_id, p_reviewer_role, p_note_type, p_note_body, p_actor)
  RETURNING note_id INTO v_note_id;
  RETURN v_note_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_enterprise_pilot_decision(
  p_snapshot_id uuid,
  p_decision_status text,
  p_decision_summary text,
  p_actor text,
  p_decision_type text DEFAULT 'pilot_decision'
) RETURNS uuid AS $$
DECLARE
  v_decision_id uuid;
BEGIN
  INSERT INTO enterprise_pilot_decision_log (snapshot_id, decision_status, decision_summary, decision_type, actor)
  VALUES (p_snapshot_id, p_decision_status, p_decision_summary, p_decision_type, p_actor)
  RETURNING decision_id INTO v_decision_id;
  
  -- Explicitly ensuring runtime permission stays false even if approved_for_limited_pilot
  -- We don't change pilot_runtime_permission_granted here.

  RETURN v_decision_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION export_enterprise_pilot_report(
  p_snapshot_id uuid,
  p_actor text DEFAULT 'pilot_viewer'
) RETURNS jsonb AS $$
DECLARE
  v_snapshot record;
  v_roles jsonb;
  v_criteria jsonb;
  v_risks jsonb;
  v_notes jsonb;
  v_decisions jsonb;
BEGIN
  SELECT * INTO v_snapshot FROM enterprise_pilot_snapshots WHERE snapshot_id = p_snapshot_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Snapshot % does not exist', p_snapshot_id;
  END IF;

  SELECT jsonb_agg(r) INTO v_roles FROM enterprise_pilot_stakeholder_roles r;
  SELECT jsonb_agg(c) INTO v_criteria FROM enterprise_pilot_success_criteria c;
  SELECT jsonb_agg(k) INTO v_risks FROM enterprise_pilot_risk_register k;
  SELECT jsonb_agg(n) INTO v_notes FROM enterprise_pilot_review_notes n WHERE snapshot_id = p_snapshot_id;
  SELECT jsonb_agg(d) INTO v_decisions FROM enterprise_pilot_decision_log d WHERE snapshot_id = p_snapshot_id;

  RETURN jsonb_build_object(
    'snapshot', to_jsonb(v_snapshot),
    'roles', v_roles,
    'criteria', v_criteria,
    'risks', v_risks,
    'notes', v_notes,
    'decisions', v_decisions,
    'exported_by', p_actor,
    'exported_at', now()
  );
END;
$$ LANGUAGE plpgsql;
