from datetime import datetime, timezone

PHASE_NAME = "Interface Phase 3"
REPO_NAME = "dev-in-portfolio/the-agent-command-center"
SOURCE_LINEAGE = "dev-in-portfolio/agent-command-center-3"
MODE_NAME = "static_local_dashboard"

ALLOWED_SOURCE_CONFIDENCE = {
    "direct_module_read",
    "report_derived",
    "file_existence_check",
    "generated_static_snapshot",
    "unknown",
}

BOUNDARY_FIELDS = [
    "official_repo_touched",
    "repo_2_touched",
    "repo_3_touched",
    "deployment_performed",
    "secrets_credentials_used",
    "command_packets_executed",
    "merge_performed",
    "push_performed",
    "pr_created",
    "network_used",
]

SECTION_META_FIELDS = [
    "source_file_path",
    "source_exists",
    "source_type",
    "source_confidence",
]

VALIDATOR_PHASES = ["phase_1", "phase_2", "phase_3_dashboard", "runtime"]


def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def section_meta(source_file_path, source_exists, source_type, source_confidence):
    return {
        "source_file_path": source_file_path,
        "source_exists": bool(source_exists),
        "source_type": source_type,
        "source_confidence": source_confidence if source_confidence in ALLOWED_SOURCE_CONFIDENCE else "unknown",
    }


def validator_command(command, purpose, expected_pass_string, recommended_run_order, post_merge_run_order, last_known_status="unknown", source_file_path="", source_exists=False, source_type="report_derived", source_confidence="unknown"):
    return {
        "command": command,
        "purpose": purpose,
        "expected_pass_string": expected_pass_string,
        "recommended_run_order": recommended_run_order,
        "post_merge_run_order": post_merge_run_order,
        "last_known_status": last_known_status,
        "source_file_path": source_file_path,
        "source_exists": bool(source_exists),
        "source_type": source_type,
        "source_confidence": source_confidence if source_confidence in ALLOWED_SOURCE_CONFIDENCE else "unknown",
        "copy_text": command,
    }


def default_snapshot():
    now = utc_now_iso()
    return {
        "dashboard_id": f"PH3-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "created_at_utc": now,
        "phase": PHASE_NAME,
        "repo": REPO_NAME,
        "source_lineage": SOURCE_LINEAGE,
        "mode": MODE_NAME,
        "phase_1_status": section_meta("11_interface/interface_action_registry.py", True, "direct_module_read", "direct_module_read"),
        "phase_2_status": section_meta("12_tui/tui_state.py", True, "direct_module_read", "direct_module_read"),
        "phase_3_status": section_meta("13_web_dashboard/build_phase3_dashboard.py", True, "generated_static_snapshot", "generated_static_snapshot"),
        "safety_status": {
            "official_repo": "LOCKED",
            "repo_2": "LOCKED",
            "repo_3": "LOCKED",
            "deployment": "DISABLED",
            "secrets": "DISABLED",
            "credentials": "DISABLED",
            "command_packet_execution": "DISABLED",
            "free_form_shell": "DISABLED",
            "merge": "DISABLED",
            "push": "DISABLED",
            "pr_creation": "DISABLED",
            "network_behavior": "DISABLED",
            "api_server": "DISABLED",
            "hosted_app": "DISABLED",
        },
        "boundary_status": {name: False for name in BOUNDARY_FIELDS},
        "action_registry_summary": {},
        "artifact_summary": {},
        "approval_ledger_summary": {},
        "branch_review_summary": {},
        "session_summary": {},
        "validator_status": {},
        "document_index": {},
        "data_freshness": {},
        "source_transparency": {},
        "recommended_next_action": "Open the local dashboard and review the source transparency panel.",
    }


def validate_snapshot(snapshot):
    errors = []
    required_root_fields = [
        "dashboard_id",
        "created_at_utc",
        "phase",
        "repo",
        "source_lineage",
        "mode",
        "phase_1_status",
        "phase_2_status",
        "phase_3_status",
        "safety_status",
        "boundary_status",
        "action_registry_summary",
        "artifact_summary",
        "approval_ledger_summary",
        "branch_review_summary",
        "session_summary",
        "validator_status",
        "document_index",
        "data_freshness",
        "source_transparency",
        "recommended_next_action",
    ]
    for field in required_root_fields:
        if field not in snapshot:
            errors.append(f"Missing root field: {field}")

    if snapshot.get("phase") != PHASE_NAME:
        errors.append(f"phase must be {PHASE_NAME}")
    if snapshot.get("repo") != REPO_NAME:
        errors.append(f"repo must be {REPO_NAME}")
    if snapshot.get("source_lineage") != SOURCE_LINEAGE:
        errors.append(f"source_lineage must be {SOURCE_LINEAGE}")
    if snapshot.get("mode") != MODE_NAME:
        errors.append(f"mode must be {MODE_NAME}")
    if not isinstance(snapshot.get("recommended_next_action"), str):
        errors.append("recommended_next_action must be a string")

    for section_name in ["phase_1_status", "phase_2_status", "phase_3_status", "action_registry_summary", "artifact_summary", "approval_ledger_summary", "branch_review_summary", "session_summary", "validator_status", "document_index", "data_freshness", "source_transparency"]:
        section = snapshot.get(section_name)
        if not isinstance(section, dict):
            errors.append(f"{section_name} must be an object")
            continue
        for key in SECTION_META_FIELDS:
            if key not in section:
                errors.append(f"{section_name} missing {key}")
        if section.get("source_confidence") not in ALLOWED_SOURCE_CONFIDENCE:
            errors.append(f"{section_name}.source_confidence must be allowed value")

    safety_status = snapshot.get("safety_status", {})
    if not isinstance(safety_status, dict):
        errors.append("safety_status must be an object")
    else:
        expected_keys = [
            "official_repo", "repo_2", "repo_3", "deployment", "secrets", "credentials",
            "command_packet_execution", "free_form_shell", "merge", "push", "pr_creation",
            "network_behavior", "api_server", "hosted_app",
        ]
        for key in expected_keys:
            if key not in safety_status:
                errors.append(f"safety_status missing {key}")

    boundary_status = snapshot.get("boundary_status", {})
    if not isinstance(boundary_status, dict):
        errors.append("boundary_status must be an object")
    else:
        for field in BOUNDARY_FIELDS:
            if boundary_status.get(field) is not False:
                errors.append(f"boundary_status.{field} must be false")

    validator_status = snapshot.get("validator_status", {})
    if not isinstance(validator_status, dict):
        errors.append("validator_status must be an object")
    else:
        for phase in VALIDATOR_PHASES:
            if phase not in validator_status:
                errors.append(f"validator_status missing {phase}")

    document_index = snapshot.get("document_index", {})
    if isinstance(document_index, dict):
        docs = document_index.get("documents")
        if not isinstance(docs, list):
            errors.append("document_index.documents must be a list")
        else:
            for doc in docs:
                if not isinstance(doc, dict):
                    errors.append("document_index entry must be an object")
                    continue
                for key in ["document_id", "title", "path", "exists", "category", "detected_verdict", "source_confidence", "recommended_review_order"]:
                    if key not in doc:
                        errors.append(f"document_index entry missing {key}")
                if doc.get("source_confidence") not in ALLOWED_SOURCE_CONFIDENCE:
                    errors.append("document_index entry source_confidence invalid")

    source_transparency = snapshot.get("source_transparency", {})
    if isinstance(source_transparency, dict):
        sections = source_transparency.get("sections")
        if not isinstance(sections, list):
            errors.append("source_transparency.sections must be a list")
        else:
            for sec in sections:
                if not isinstance(sec, dict):
                    errors.append("source_transparency entry must be an object")
                    continue
                for key in ["section_id", "title", "source_file_path", "source_exists", "source_type", "source_confidence"]:
                    if key not in sec:
                        errors.append(f"source_transparency entry missing {key}")
                if sec.get("source_confidence") not in ALLOWED_SOURCE_CONFIDENCE:
                    errors.append("source_transparency entry source_confidence invalid")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
