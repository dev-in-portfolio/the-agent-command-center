#!/usr/bin/env python3
# MVP49_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP49_NO_REAL_COMMAND_EXECUTION_CHECK
# MVP49_NO_REAL_ACTION_EXECUTION_CHECK
# MVP49_NO_AUTONOMOUS_EXECUTION_CHECK
# MVP49_NO_EXTERNAL_API_MUTATION_CHECK
# MVP49_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP49_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP49_NO_QUEUE_WORKER_PROCESSING_CHECK
# MVP49_NO_AUTOMATIC_DISPATCH_CHECK
# MVP49_NO_SCHEDULED_EXECUTION_CHECK
# MVP49_NO_RETRY_EXECUTION_CHECK
# MVP49_NO_PUBLIC_WRITES_CHECK
# MVP49_NO_DATABASE_WRITES_CHECK
# MVP49_NO_SUPABASE_WRITES_CHECK
# MVP49_NO_AUDIT_EVENT_WRITES_CHECK
# MVP49_NO_REQUEST_STATUS_MUTATION_CHECK
# MVP49_NO_APPROVAL_EXECUTION_CHECK
# MVP49_NO_AUTOMATION_CHECK
# MVP49_NO_SERVICE_ROLE_CHECK
# MVP49_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP49_NO_TOKEN_INPUT_CHECK
# MVP49_NO_BROWSER_PERSISTENCE_CHECK
# MVP49_NO_MIGRATION_APPLY_CHECK
# MVP49_HUMAN_APPROVED_INTERNAL_EXECUTION_EXPORT_ARTIFACTS_CHECK

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
        "14_backend/product_runtime/ui_models/human_approved_internal_execution_model.json",
        "14_backend/product_runtime/ui_models/operator_attestation_schema_model.json",
        "14_backend/product_runtime/ui_models/execution_eligibility_gate_model.json",
        "14_backend/product_runtime/ui_models/approval_execution_binding_model.json",
        "14_backend/product_runtime/ui_models/pre_execution_lock_checklist_model.json",
        "14_backend/product_runtime/ui_models/execution_result_receipt_schema_model.json",
        "14_backend/product_runtime/ui_models/rollback_handoff_packet_model.json",
        "14_backend/product_runtime/ui_models/post_execution_verification_checklist_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp49_human_approved_internal_execution_report.md",
        "09_exports/mvp_product_track/mvp49_operator_attestation_schema_report.md",
        "09_exports/mvp_product_track/mvp49_execution_eligibility_gate_report.md",
        "09_exports/mvp_product_track/mvp49_approval_execution_binding_report.md",
        "09_exports/mvp_product_track/mvp49_pre_execution_lock_checklist_report.md",
        "09_exports/mvp_product_track/mvp49_execution_result_receipt_schema_report.md",
        "09_exports/mvp_product_track/mvp49_rollback_handoff_packet_report.md",
        "09_exports/mvp_product_track/mvp49_post_execution_verification_checklist_report.md",
        "09_exports/mvp_product_track/mvp49_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp49_next_product_step_report.md",
        "09_exports/mvp_product_track/mvp49_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp49_acceptance_report.md",
        "09_exports/mvp_product_track/mvp49_validator_wall_review.md",
        "09_exports/mvp_product_track/mvp49_validation_stewardship_report.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp49_human_approved_internal_execution.md",
        "09_exports/release_package/mvp49_operator_attestation_schema.md",
        "09_exports/release_package/mvp49_execution_eligibility_gate.md",
        "09_exports/release_package/mvp49_approval_execution_binding.md",
        "09_exports/release_package/mvp49_pre_execution_lock_checklist.md",
        "09_exports/release_package/mvp49_execution_result_receipt_schema.md",
        "09_exports/release_package/mvp49_rollback_handoff_packet.md",
        "09_exports/release_package/mvp49_post_execution_verification_checklist.md",
        "09_exports/release_package/mvp49_human_approved_internal_execution_manifest.json",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")

    manifest = ROOT / "09_exports/release_package/mvp49_human_approved_internal_execution_manifest.json"
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
            "MVP-49",
            "HUMAN APPROVED INTERNAL EXECUTION",
            "OPERATOR ATTESTATION SCHEMA",
            "EXECUTION ELIGIBILITY GATE",
            "APPROVAL EXECUTION BINDING",
            "PRE EXECUTION LOCK CHECKLIST",
            "EXECUTION RESULT RECEIPT SCHEMA",
            "ROLLBACK HANDOFF PACKET",
            "POST EXECUTION VERIFICATION CHECKLIST",
            "HUMAN EXECUTION READINESS ONLY",
            "SCHEMA READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL COMMAND EXECUTION",
            "NO REAL ACTION EXECUTION",
            "NO AUTONOMOUS EXECUTION",
            "NO EXTERNAL API MUTATION",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PR CONTROLS",
            "NO QUEUE WORKER PROCESSING",
            "NO AUTOMATIC DISPATCH",
            "NO SCHEDULED EXECUTION",
            "NO RETRY EXECUTION",
            "NO PUBLIC WRITES",
            "NO DATABASE WRITES",
            "NO SUPABASE WRITES",
            "NO AUDIT EVENT WRITES",
            "NO REQUEST STATUS MUTATION",
            "NO APPROVAL EXECUTION",
            "AUTOMATION DISABLED",
            "SERVICE ROLE NOT USED",
            "SERVICE ROLE NOT IN BROWSER",
            "NO TOKEN INPUT",
            "NO BROWSER PERSISTENCE",
            "NO MIGRATION APPLY",
            "NEXT_STEP_BUILD_MONITORING_ROLLBACK_INCIDENT_CONSOLE",
            "NOT_READY_FOR_REAL_AUTOMATION"
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")

    acc_report = ROOT / "09_exports/mvp_product_track/mvp49_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "HUMAN_APPROVED_INTERNAL_EXECUTION_READY",
            "PASS_WITH_HUMAN_EXECUTION_READINESS_ONLY"
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")

    model_json = ROOT / "14_backend/product_runtime/ui_models/human_approved_internal_execution_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("human_approved_internal_execution_ready") == True, "expected true")
        check(data.get("human_execution_readiness_only") == True, "expected true")
        check(data.get("schema_readiness_only") == True, "expected true")
        check(data.get("real_command_execution_enabled") == False, "expected false")
        check(data.get("real_action_execution_enabled") == False, "expected false")
        check(data.get("autonomous_execution_enabled") == False, "expected false")
        check(data.get("external_api_mutation_enabled") == False, "expected false")
        check(data.get("github_mutation_enabled") == False, "expected false")
        check(data.get("netlify_mutation_enabled") == False, "expected false")
        check(data.get("deploy_controls_enabled") == False, "expected false")
        check(data.get("merge_controls_enabled") == False, "expected false")
        check(data.get("push_controls_enabled") == False, "expected false")
        check(data.get("pr_controls_enabled") == False, "expected false")
        check(data.get("queue_worker_processing_enabled") == False, "expected false")
        check(data.get("automatic_dispatch_enabled") == False, "expected false")
        check(data.get("scheduled_execution_enabled") == False, "expected false")
        check(data.get("retry_execution_enabled") == False, "expected false")
        check(data.get("public_write_enabled") == False, "expected false")
        check(data.get("database_write_enabled") == False, "expected false")
        check(data.get("supabase_write_enabled") == False, "expected false")
        check(data.get("audit_event_write_enabled") == False, "expected false")
        check(data.get("request_status_mutation_enabled") == False, "expected false")
        check(data.get("approval_execution_enabled") == False, "expected false")
        check(data.get("automation_enabled") == False, "expected false")

    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(not any(f.endswith(".js") for f in added_functions), "no new function files added")

    if FAILURES:
        print("MVP49_HUMAN_APPROVED_INTERNAL_EXECUTION_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)

    print("MVP49_HUMAN_APPROVED_INTERNAL_EXECUTION_VALIDATION_PASS")

if __name__ == "__main__":
    main()
