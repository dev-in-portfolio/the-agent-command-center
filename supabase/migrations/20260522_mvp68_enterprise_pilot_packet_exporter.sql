-- MVP-68 Enterprise Pilot Packet Exporter Migration

CREATE TABLE IF NOT EXISTS enterprise_pilot_packets (
    packet_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    packet_status text NOT NULL DEFAULT 'generated',
    packet_title text NOT NULL DEFAULT 'The Agent Command Center Enterprise Pilot Packet',
    packet_version text NOT NULL DEFAULT 'MVP-68',
    total_registered_agents integer NOT NULL DEFAULT 47979,
    total_departments integer NOT NULL DEFAULT 1777,
    total_units integer NOT NULL DEFAULT 5331,
    total_families integer NOT NULL DEFAULT 175,
    full_fleet_cap integer NOT NULL DEFAULT 47979,
    current_live_runtime_agents integer NOT NULL DEFAULT 0,
    pilot_runtime_permission_granted boolean NOT NULL DEFAULT false,
    command_execution_enabled boolean NOT NULL DEFAULT false,
    deploy_execution_enabled boolean NOT NULL DEFAULT false,
    rollback_execution_enabled boolean NOT NULL DEFAULT false,
    alert_sending_enabled boolean NOT NULL DEFAULT false,
    arbitrary_shell_execution_enabled boolean NOT NULL DEFAULT false,
    external_alert_sending_enabled boolean NOT NULL DEFAULT false,
    generated_by text,
    source text NOT NULL DEFAULT 'mvp68_enterprise_pilot_packet_exporter',
    CONSTRAINT valid_packet_status CHECK (packet_status IN ('generated', 'reviewed', 'needs_changes', 'approved_for_review', 'archived'))
);

CREATE TABLE IF NOT EXISTS enterprise_pilot_packet_sections (
    section_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_id uuid REFERENCES enterprise_pilot_packets(packet_id) ON DELETE CASCADE,
    section_key text NOT NULL,
    section_title text NOT NULL,
    section_body text NOT NULL,
    section_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    sort_order integer NOT NULL DEFAULT 0,
    source text NOT NULL DEFAULT 'mvp68_enterprise_pilot_packet_exporter'
);

CREATE TABLE IF NOT EXISTS enterprise_pilot_packet_exports (
    export_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_id uuid REFERENCES enterprise_pilot_packets(packet_id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    export_format text NOT NULL DEFAULT 'json',
    export_status text NOT NULL DEFAULT 'ready',
    export_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    exported_by text,
    source text NOT NULL DEFAULT 'mvp68_enterprise_pilot_packet_exporter',
    CONSTRAINT valid_export_format CHECK (export_format IN ('json', 'print_html', 'markdown')),
    CONSTRAINT valid_export_status CHECK (export_status IN ('ready', 'exported', 'failed', 'archived'))
);

CREATE TABLE IF NOT EXISTS enterprise_pilot_packet_review_notes (
    note_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_id uuid REFERENCES enterprise_pilot_packets(packet_id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    reviewer_role text,
    note_body text NOT NULL,
    actor text,
    source text NOT NULL DEFAULT 'mvp68_enterprise_pilot_packet_exporter'
);

-- Update configuration
UPDATE runtime_kernel_config SET config_value = 'true' WHERE config_key = 'mvp68_enterprise_pilot_packet_exporter_ready';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('mvp68_enterprise_pilot_packet_exporter_ready', 'true') ON CONFLICT (config_key) DO NOTHING;

UPDATE runtime_kernel_config SET config_value = 'generated' WHERE config_key = 'enterprise_pilot_packet_status';
INSERT INTO runtime_kernel_config (config_key, config_value) VALUES ('enterprise_pilot_packet_status', 'generated') ON CONFLICT (config_key) DO NOTHING;

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

CREATE OR REPLACE FUNCTION create_enterprise_pilot_packet(
  p_actor text DEFAULT 'pilot_packet_exporter'
) RETURNS uuid AS $$
DECLARE
  v_packet_id uuid;
  v_live_agents integer := 0;
BEGIN
  -- Read from existing snapshot tables if available (gracefully falling back to 0)
  BEGIN
    SELECT current_live_runtime_agents INTO v_live_agents
    FROM enterprise_pilot_snapshots ORDER BY created_at DESC LIMIT 1;
  EXCEPTION WHEN undefined_table THEN END;
  v_live_agents := COALESCE(v_live_agents, 0);

  INSERT INTO enterprise_pilot_packets (current_live_runtime_agents, generated_by)
  VALUES (v_live_agents, p_actor)
  RETURNING packet_id INTO v_packet_id;

  -- Create required sections
  INSERT INTO enterprise_pilot_packet_sections (packet_id, section_key, section_title, section_body, sort_order) VALUES
  (v_packet_id, 'executive_summary', '1. Executive Summary', 'The Agent Command Center pilot packet.', 1),
  (v_packet_id, 'system_scale', '2. System Scale', '47,979 agents across 1,777 departments.', 2),
  (v_packet_id, 'pilot_scope', '3. Pilot Scope', 'Controlled enterprise review.', 3),
  (v_packet_id, 'stakeholder_roles', '4. Stakeholder Roles', 'Roles and responsibilities for review.', 4),
  (v_packet_id, 'safety_boundaries', '5. Safety Boundaries', 'All destructive execution is disabled.', 5),
  (v_packet_id, 'runtime_permission_status', '6. Runtime Permission Status', 'Pilot runtime permission granted: false', 6),
  (v_packet_id, 'success_criteria', '7. Success Criteria', 'Required criteria for pilot success.', 7),
  (v_packet_id, 'risk_register', '8. Risk Register', 'Identified risks and mitigations.', 8),
  (v_packet_id, 'technical_readiness', '9. Technical Readiness', 'Control plane load test results and observability status.', 9),
  (v_packet_id, 'legal_copyright_nda', '10. Legal / Copyright / NDA Links', 'Review required before pilot start.', 10),
  (v_packet_id, 'go_no_go_checklist', '11. Go / No-Go Checklist', 'Final approval checklist.', 11),
  (v_packet_id, 'decision_log', '12. Decision Log', 'Historical decisions made during review.', 12),
  (v_packet_id, 'recommended_next_step', '13. Recommended Next Step', 'Approve packet or request changes.', 13);

  RETURN v_packet_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION export_enterprise_pilot_packet(
  p_packet_id uuid,
  p_export_format text DEFAULT 'json',
  p_actor text DEFAULT 'pilot_packet_exporter'
) RETURNS jsonb AS $$
DECLARE
  v_packet record;
  v_sections jsonb;
  v_notes jsonb;
  v_payload jsonb;
  v_export_id uuid;
BEGIN
  IF p_export_format NOT IN ('json', 'print_html', 'markdown') THEN
    RAISE EXCEPTION 'Invalid export format: %', p_export_format;
  END IF;

  SELECT * INTO v_packet FROM enterprise_pilot_packets WHERE packet_id = p_packet_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Packet % does not exist', p_packet_id;
  END IF;

  SELECT jsonb_agg(s ORDER BY sort_order) INTO v_sections FROM enterprise_pilot_packet_sections s WHERE packet_id = p_packet_id;
  SELECT jsonb_agg(n ORDER BY created_at) INTO v_notes FROM enterprise_pilot_packet_review_notes n WHERE packet_id = p_packet_id;

  v_payload := jsonb_build_object(
    'packet', to_jsonb(v_packet),
    'sections', v_sections,
    'review_notes', v_notes,
    'format', p_export_format,
    'exported_by', p_actor,
    'exported_at', now()
  );

  INSERT INTO enterprise_pilot_packet_exports (packet_id, export_format, export_payload, exported_by)
  VALUES (p_packet_id, p_export_format, v_payload, p_actor)
  RETURNING export_id INTO v_export_id;

  RETURN jsonb_build_object('export_id', v_export_id, 'payload', v_payload);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_pilot_packet_review_note(
  p_packet_id uuid,
  p_reviewer_role text,
  p_note_body text,
  p_actor text
) RETURNS uuid AS $$
DECLARE
  v_note_id uuid;
BEGIN
  INSERT INTO enterprise_pilot_packet_review_notes (packet_id, reviewer_role, note_body, actor)
  VALUES (p_packet_id, p_reviewer_role, p_note_body, p_actor)
  RETURNING note_id INTO v_note_id;
  RETURN v_note_id;
END;
$$ LANGUAGE plpgsql;
