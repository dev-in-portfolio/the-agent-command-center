#!/usr/bin/env python3
# MVP50_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP50_NO_REAL_MONITORING_CHECK
# MVP50_NO_REAL_ALERT_DISPATCH_CHECK
# MVP50_NO_REAL_ROLLBACK_CHECK
# MVP50_NO_REAL_INCIDENT_RESPONSE_CHECK
# MVP50_NO_EXTERNAL_API_MUTATION_CHECK
# MVP50_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP50_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP50_NO_PUBLIC_WRITES_CHECK
# MVP50_NO_DATABASE_WRITES_CHECK
# MVP50_NO_SUPABASE_WRITES_CHECK
# MVP50_NO_AUTOMATION_CHECK
# MVP50_NO_MIGRATION_APPLY_CHECK

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

    index_path = ROOT / "13_web_dashboard/dist/index.html"
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
            "NO REAL MONITORING",
            "NO REAL ALERT DISPATCH",
            "NO REAL ROLLBACK",
            "NO REAL INCIDENT RESPONSE",
            "NO EXTERNAL API MUTATION",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PUBLIC WRITES",
            "NO DATABASE WRITES",
            "NO SUPABASE WRITES",
            "AUTOMATION DISABLED",
            "NOT_READY_FOR_REAL_AUTOMATION",
            "READINESS_ROADMAP_COMPLETE_PENDING_REVIEW",
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")

    acc_report = ROOT / "09_exports/mvp_product_track/mvp50_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "READINESS_READY",
            "PASS_WITH_READINESS_ONLY",
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")

    model_json = ROOT / "14_backend/product_runtime/ui_models/monitoring_rollback_incident_console_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("schema_readiness_only") == True, "expected true")
        check(data.get("real_monitoring_enabled") == False, "expected false")
        check(data.get("real_alert_dispatch_enabled") == False, "expected false")
        check(data.get("real_metrics_collection_enabled") == False, "expected false")
        check(data.get("real_log_aggregation_enabled") == False, "expected false")
        check(data.get("autonomous_observability_enabled") == False, "expected false")
        check(data.get("external_monitoring_api_mutation_enabled") == False, "expected false")
        check(data.get("dashboard_write_enabled") == False, "expected false")
        check(data.get("health_check_execution_enabled") == False, "expected false")
        check(data.get("service_role_used") == False, "expected false")
        check(data.get("service_role_in_browser") == False, "expected false")
        check(data.get("token_input_enabled") == False, "expected false")
        check(data.get("browser_persistence_enabled") == False, "expected false")
        check(data.get("migration_apply_enabled") == False, "expected false")

    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(not any(f.endswith(".js") for f in added_functions), "no new function files added")

    if FAILURES:
        print("MVP50_MONITORING_ROLLBACK_INCIDENT_CONSOLE_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)

    print("MVP50_MONITORING_ROLLBACK_INCIDENT_CONSOLE_VALIDATION_PASS")

if __name__ == "__main__":
    main()
