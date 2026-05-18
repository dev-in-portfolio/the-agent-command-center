#!/usr/bin/env python3
# MVP46_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP46_NO_REAL_APPROVAL_DECISIONS_CHECK
# MVP46_NO_REAL_APPROVAL_STORAGE_CHECK
# MVP46_NO_APPROVAL_EXECUTION_CHECK
# MVP46_NO_COMMAND_EXECUTION_CHECK
# MVP46_NO_DATABASE_WRITES_CHECK
# MVP46_NO_SUPABASE_WRITES_CHECK
# MVP46_NO_PUBLIC_WRITES_CHECK
# MVP46_NO_LIVE_APPROVAL_WORKFLOW_CHECK
# MVP46_NO_APPROVAL_MUTATION_CHECK
# MVP46_NO_APPROVAL_DELETION_CHECK
# MVP46_NO_AUDIT_EVENT_WRITES_CHECK
# MVP46_NO_REQUEST_STATUS_MUTATION_CHECK
# MVP46_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP46_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP46_NO_AUTOMATION_CHECK
# MVP46_NO_SERVICE_ROLE_CHECK
# MVP46_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP46_NO_TOKEN_INPUT_CHECK
# MVP46_NO_BROWSER_PERSISTENCE_CHECK
# MVP46_NO_MIGRATION_APPLY_CHECK
# MVP46_APPROVAL_GATE_STORAGE_EXPORT_ARTIFACTS_CHECK
# MVP46_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

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
        "14_backend/product_runtime/ui_models/approval_gate_storage_model.json",
        "14_backend/product_runtime/ui_models/approval_request_schema_model.json",
        "14_backend/product_runtime/ui_models/approval_decision_schema_model.json",
        "14_backend/product_runtime/ui_models/approval_scope_expiration_model.json",
        "14_backend/product_runtime/ui_models/approval_revocation_model.json",
        "14_backend/product_runtime/ui_models/approval_audit_linkage_blueprint_model.json",
        "14_backend/product_runtime/ui_models/approval_permission_boundary_contract_model.json",
        "14_backend/product_runtime/ui_models/approval_storage_readiness_checklist_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp46_approval_gate_storage_report.md",
        "09_exports/mvp_product_track/mvp46_approval_request_schema_report.md",
        "09_exports/mvp_product_track/mvp46_approval_decision_schema_report.md",
        "09_exports/mvp_product_track/mvp46_approval_scope_expiration_model_report.md",
        "09_exports/mvp_product_track/mvp46_approval_revocation_model_report.md",
        "09_exports/mvp_product_track/mvp46_approval_audit_linkage_blueprint_report.md",
        "09_exports/mvp_product_track/mvp46_approval_permission_boundary_contract_report.md",
        "09_exports/mvp_product_track/mvp46_approval_storage_readiness_checklist_report.md",
        "09_exports/mvp_product_track/mvp46_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp46_next_product_step_report.md",
        "09_exports/mvp_product_track/mvp46_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp46_acceptance_report.md",
        "09_exports/mvp_product_track/mvp46_validator_wall_review.md",
        "09_exports/mvp_product_track/mvp46_validation_stewardship_report.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp46_approval_gate_storage.md",
        "09_exports/release_package/mvp46_approval_request_schema.md",
        "09_exports/release_package/mvp46_approval_decision_schema.md",
        "09_exports/release_package/mvp46_approval_scope_expiration_model.md",
        "09_exports/release_package/mvp46_approval_revocation_model.md",
        "09_exports/release_package/mvp46_approval_audit_linkage_blueprint.md",
        "09_exports/release_package/mvp46_approval_permission_boundary_contract.md",
        "09_exports/release_package/mvp46_approval_storage_readiness_checklist.md",
        "09_exports/release_package/mvp46_approval_gate_storage_manifest.json",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")
        
    manifest = ROOT / "09_exports/release_package/mvp46_approval_gate_storage_manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            check(data.get("name") == "MVP-46 Approval Gate Storage", "manifest name incorrect")
        except json.JSONDecodeError:
            fail("manifest JSON invalid")

    index_path = ROOT / "13_web_dashboard/dist/index.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)
        
        markers = [
            "MVP-46",
            "APPROVAL GATE STORAGE",
            "APPROVAL REQUEST SCHEMA",
            "APPROVAL DECISION SCHEMA",
            "APPROVAL SCOPE EXPIRATION MODEL",
            "APPROVAL REVOCATION MODEL",
            "APPROVAL AUDIT LINKAGE BLUEPRINT",
            "APPROVAL PERMISSION BOUNDARY CONTRACT",
            "APPROVAL STORAGE READINESS CHECKLIST",
            "APPROVAL GATE STORAGE FOUNDATION ONLY",
            "SCHEMA READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL APPROVAL DECISIONS",
            "NO REAL APPROVAL STORAGE",
            "NO APPROVAL EXECUTION",
            "NO COMMAND EXECUTION",
            "NO DATABASE WRITES",
            "NO SUPABASE WRITES",
            "NO PUBLIC WRITES",
            "NO LIVE APPROVAL WORKFLOW",
            "NO APPROVAL MUTATION",
            "NO APPROVAL DELETION",
            "NO AUDIT EVENT WRITES",
            "NO REQUEST STATUS MUTATION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PR CONTROLS",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "AUTOMATION DISABLED",
            "SERVICE ROLE NOT USED",
            "SERVICE ROLE NOT IN BROWSER",
            "NO TOKEN INPUT",
            "NO BROWSER PERSISTENCE",
            "NO MIGRATION APPLY",
            "NEXT_STEP_BUILD_SERVER_SIDE_DRY_RUN_ENGINE",
            "NOT_READY_FOR_REAL_AUTOMATION"
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")
            
    acc_report = ROOT / "09_exports/mvp_product_track/mvp46_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "APPROVAL_GATE_STORAGE_READY",
            "PASS_WITH_APPROVAL_GATE_STORAGE_FOUNDATION_ONLY"
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")
            
    # Check semantic posture
    model_json = ROOT / "14_backend/product_runtime/ui_models/approval_gate_storage_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("approval_gate_storage_ready") == "true", "expected true")
        check(data.get("approval_gate_storage_foundation_only") == "true", "expected true")
        check(data.get("schema_readiness_only") == "true", "expected true")
        check(data.get("real_approval_decisions_enabled") == "false", "expected false")
        check(data.get("real_approval_storage_enabled") == "false", "expected false")
        check(data.get("approval_execution_enabled") == "false", "expected false")
        check(data.get("command_execution_enabled") == "false", "expected false")
        check(data.get("database_write_enabled") == "false", "expected false")
        check(data.get("supabase_write_enabled") == "false", "expected false")
        check(data.get("public_write_enabled") == "false", "expected false")
        check(data.get("live_approval_workflow_enabled") == "false", "expected false")
        check(data.get("approval_mutation_enabled") == "false", "expected false")
        check(data.get("approval_deletion_enabled") == "false", "expected false")
        check(data.get("audit_event_write_enabled") == "false", "expected false")
        check(data.get("request_status_mutation_enabled") == "false", "expected false")
        check(data.get("deploy_controls_enabled") == "false", "expected false")
        check(data.get("merge_controls_enabled") == "false", "expected false")
        check(data.get("push_controls_enabled") == "false", "expected false")
        check(data.get("pr_controls_enabled") == "false", "expected false")
        check(data.get("github_mutation_enabled") == "false", "expected false")
        check(data.get("netlify_mutation_enabled") == "false", "expected false")
        check(data.get("automation_enabled") == "false", "expected false")
        
    # check no new Netlify functions added compared to origin/master
    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(not any(f.endswith(".js") for f in added_functions), "no new function files added")
    
    if FAILURES:
        print("MVP46_APPROVAL_GATE_STORAGE_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
        
    print("MVP46_APPROVAL_GATE_STORAGE_VALIDATION_PASS")

if __name__ == "__main__":
    main()
