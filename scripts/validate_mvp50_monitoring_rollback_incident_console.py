#!/usr/bin/env python3
# MVP50_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP50_NO_REAL_MONITORING_DAEMON_CHECK
# MVP50_NO_BACKGROUND_WORKER_CHECK
# MVP50_NO_ALERT_SENDING_CHECK
# MVP50_NO_INCIDENT_NOTIFICATION_SENDING_CHECK
# MVP50_NO_INCIDENT_MUTATION_CHECK
# MVP50_NO_REAL_ROLLBACK_EXECUTION_CHECK
# MVP50_NO_ROLLBACK_MUTATION_CHECK
# MVP50_NO_EXTERNAL_API_MUTATION_CHECK
# MVP50_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP50_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP50_NO_AUTONOMOUS_EXECUTION_CHECK
# MVP50_NO_REAL_COMMAND_ACTION_EXECUTION_CHECK
# MVP50_NO_QUEUE_WORKER_PROCESSING_CHECK
# MVP50_NO_APPROVAL_EXECUTION_CHECK
# MVP50_NO_PUBLIC_DATABASE_SUPABASE_WRITES_CHECK
# MVP50_NO_AUDIT_EVENT_WRITES_CHECK
# MVP50_NO_REQUEST_STATUS_MUTATION_CHECK
# MVP50_NO_AUTOMATION_CHECK
# MVP50_NO_SERVICE_ROLE_CHECK
# MVP50_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP50_NO_TOKEN_INPUT_CHECK
# MVP50_NO_BROWSER_PERSISTENCE_CHECK
# MVP50_NO_MIGRATION_APPLY_CHECK
# MVP50_MONITORING_ROLLBACK_INCIDENT_CONSOLE_EXPORT_ARTIFACTS_CHECK
# MVP50_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validation_helpers_control_scan import scan_text_for_dangerous_controls

FAILURES = []

def fail(message: str) -> None:
    FAILURES.append(message)
    print(f"  [FAIL] {message}")

def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def scan_text(path: Path, text: str) -> None:
    findings = scan_text_for_dangerous_controls(str(path.relative_to(ROOT)), text)
    if findings:
        fail(f"{path.relative_to(ROOT)}: {findings}")

def main():
    models = [
        "14_backend/product_runtime/ui_models/monitoring_rollback_incident_console_model.json",
        "14_backend/product_runtime/ui_models/monitoring_console_model.json",
        "14_backend/product_runtime/ui_models/health_signal_schema_model.json",
        "14_backend/product_runtime/ui_models/incident_record_schema_model.json",
        "14_backend/product_runtime/ui_models/rollback_plan_registry_model.json",
        "14_backend/product_runtime/ui_models/rollback_readiness_checklist_model.json",
        "14_backend/product_runtime/ui_models/operator_incident_review_packet_model.json",
        "14_backend/product_runtime/ui_models/incident_severity_escalation_matrix_model.json",
        "14_backend/product_runtime/ui_models/post_incident_audit_packet_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp50_monitoring_rollback_incident_console_report.md",
        "09_exports/mvp_product_track/mvp50_monitoring_console_report.md",
        "09_exports/mvp_product_track/mvp50_health_signal_schema_report.md",
        "09_exports/mvp_product_track/mvp50_incident_record_schema_report.md",
        "09_exports/mvp_product_track/mvp50_rollback_plan_registry_report.md",
        "09_exports/mvp_product_track/mvp50_rollback_readiness_checklist_report.md",
        "09_exports/mvp_product_track/mvp50_operator_incident_review_packet_report.md",
        "09_exports/mvp_product_track/mvp50_incident_severity_escalation_matrix_report.md",
        "09_exports/mvp_product_track/mvp50_post_incident_audit_packet_report.md",
        "09_exports/mvp_product_track/mvp50_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp50_validation_stewardship_report.md",
        "09_exports/mvp_product_track/mvp50_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp50_acceptance_report.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp50_monitoring_rollback_incident_console_manifest.json",
        "09_exports/release_package/mvp50_monitoring_rollback_incident_console.md",
        "09_exports/release_package/mvp50_monitoring_console.md",
        "09_exports/release_package/mvp50_health_signal_schema.md",
        "09_exports/release_package/mvp50_incident_record_schema.md",
        "09_exports/release_package/mvp50_rollback_plan_registry.md",
        "09_exports/release_package/mvp50_rollback_readiness_checklist.md",
        "09_exports/release_package/mvp50_operator_incident_review_packet.md",
        "09_exports/release_package/mvp50_incident_severity_escalation_matrix.md",
        "09_exports/release_package/mvp50_post_incident_audit_packet.md",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")

    manifest = ROOT / "09_exports/release_package/mvp50_monitoring_rollback_incident_console_manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            fail("manifest JSON invalid")

    index_path = ROOT / "13_web_dashboard/dist/full-audit-dashboard.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)

        markers = [
            "MVP-50",
            "MONITORING / ROLLBACK / INCIDENT CONSOLE",
            "MONITORING CONSOLE",
            "HEALTH SIGNAL SCHEMA",
            "INCIDENT RECORD SCHEMA",
            "ROLLBACK PLAN REGISTRY",
            "ROLLBACK READINESS CHECKLIST",
            "OPERATOR INCIDENT REVIEW PACKET",
            "INCIDENT SEVERITY ESCALATION MATRIX",
            "POST-INCIDENT AUDIT PACKET",
            "SCHEMA READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL MONITORING DAEMON",
            "NO BACKGROUND WORKER",
            "NO ALERT SENDING",
            "NO INCIDENT NOTIFICATION SENDING",
            "NO INCIDENT MUTATION",
            "NO REAL ROLLBACK EXECUTION",
            "NO ROLLBACK MUTATION",
            "NO EXTERNAL API MUTATION",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PR CONTROLS",
            "NO AUTONOMOUS EXECUTION",
            "NO REAL COMMAND EXECUTION",
            "NO REAL ACTION EXECUTION",
            "NO QUEUE WORKER PROCESSING",
            "NO APPROVAL EXECUTION",
            "NO PUBLIC WRITES",
            "NO DATABASE WRITES",
            "NO SUPABASE WRITES",
            "NO AUDIT EVENT WRITES",
            "NO REQUEST STATUS MUTATION",
            "AUTOMATION DISABLED",
            "SERVICE ROLE NOT USED",
            "SERVICE ROLE NOT IN BROWSER",
            "NO TOKEN INPUT",
            "NO BROWSER PERSISTENCE",
            "NO MIGRATION APPLY",
            "READINESS_ROADMAP_COMPLETE_PENDING_REVIEW",
            "NOT_READY_FOR_REAL_AUTOMATION",
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")

    acc_report = ROOT / "09_exports/mvp_product_track/mvp50_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "MONITORING_ROLLBACK_INCIDENT_CONSOLE_READY",
            "PASS_WITH_MONITORING_INCIDENT_READINESS_ONLY",
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")

    model_json = ROOT / "14_backend/product_runtime/ui_models/monitoring_rollback_incident_console_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("monitoring_rollback_incident_console_ready") == True, "expected true")
        check(data.get("monitoring_console_ready") == True, "expected true")
        check(data.get("health_signal_schema_ready") == True, "expected true")
        check(data.get("incident_record_schema_ready") == True, "expected true")
        check(data.get("rollback_plan_registry_ready") == True, "expected true")
        check(data.get("rollback_readiness_checklist_ready") == True, "expected true")
        check(data.get("operator_incident_review_packet_ready") == True, "expected true")
        check(data.get("incident_severity_escalation_matrix_ready") == True, "expected true")
        check(data.get("post_incident_audit_packet_ready") == True, "expected true")
        check(data.get("monitoring_incident_readiness_only") == True, "expected true")
        check(data.get("schema_readiness_only") == True, "expected true")
        check(data.get("review_only") == True, "expected true")
        check(data.get("future_implementation_only") == True, "expected true")
        check(data.get("real_monitoring_daemon_enabled") == False, "expected false")
        check(data.get("background_worker_enabled") == False, "expected false")
        check(data.get("alert_sending_enabled") == False, "expected false")
        check(data.get("incident_notification_sending_enabled") == False, "expected false")
        check(data.get("incident_mutation_enabled") == False, "expected false")
        check(data.get("real_rollback_execution_enabled") == False, "expected false")
        check(data.get("rollback_mutation_enabled") == False, "expected false")
        check(data.get("external_api_mutation_enabled") == False, "expected false")
        check(data.get("github_mutation_enabled") == False, "expected false")
        check(data.get("netlify_mutation_enabled") == False, "expected false")
        check(data.get("deploy_controls_enabled") == False, "expected false")
        check(data.get("merge_controls_enabled") == False, "expected false")
        check(data.get("push_controls_enabled") == False, "expected false")
        check(data.get("pr_controls_enabled") == False, "expected false")
        check(data.get("autonomous_execution_enabled") == False, "expected false")
        check(data.get("real_command_execution_enabled") == False, "expected false")
        check(data.get("real_action_execution_enabled") == False, "expected false")
        check(data.get("queue_worker_processing_enabled") == False, "expected false")
        check(data.get("approval_execution_enabled") == False, "expected false")
        check(data.get("public_write_enabled") == False, "expected false")
        check(data.get("database_write_enabled") == False, "expected false")
        check(data.get("supabase_write_enabled") == False, "expected false")
        check(data.get("audit_event_write_enabled") == False, "expected false")
        check(data.get("request_status_mutation_enabled") == False, "expected false")
        check(data.get("automation_enabled") == False, "expected false")
        check(data.get("service_role_used") == False, "expected false")
        check(data.get("service_role_in_browser") == False, "expected false")
        check(data.get("token_input_enabled") == False, "expected false")
        check(data.get("browser_persistence_enabled") == False, "expected false")
        check(data.get("migration_apply_enabled") == False, "expected false")

    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(
        not any(
            f.endswith(".js")
            and not f.startswith("netlify/functions/runtime-request-")
            and not f.startswith("netlify/functions/runtime-agent-")
            and f not in {
                "netlify/functions/activate-agent.js",
                "netlify/functions/deactivate-agent.js",
                "netlify/functions/list-runtime-agents.js",
            }
            for f in added_functions
        ),
        "no new function files added",
    )

    if FAILURES:
        print("MVP50_MONITORING_ROLLBACK_INCIDENT_CONSOLE_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)

    print("MVP50_MONITORING_ROLLBACK_INCIDENT_CONSOLE_VALIDATION_PASS")

if __name__ == "__main__":
    main()
