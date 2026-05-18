#!/usr/bin/env python3
# MVP44_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP44_NO_REAL_DATABASE_WRITES_CHECK
# MVP44_NO_SUPABASE_WRITES_CHECK
# MVP44_NO_PUBLIC_WRITES_CHECK
# MVP44_NO_LIVE_REQUEST_CREATION_CHECK
# MVP44_NO_LIVE_INTAKE_CHECK
# MVP44_NO_PUBLIC_ENDPOINT_CHECK
# MVP44_NO_MIGRATION_APPLY_CHECK
# MVP44_NO_REAL_PERSISTENCE_CHECK
# MVP44_NO_COMMAND_EXECUTION_CHECK
# MVP44_NO_APPROVAL_EXECUTION_CHECK
# MVP44_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP44_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP44_NO_AUTOMATION_CHECK
# MVP44_NO_SERVICE_ROLE_CHECK
# MVP44_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP44_NO_TOKEN_INPUT_CHECK
# MVP44_NO_BROWSER_PERSISTENCE_CHECK
# MVP44_PERSISTENT_REQUEST_STORAGE_EXPORT_ARTIFACTS_CHECK
# MVP44_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

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
        "14_backend/product_runtime/ui_models/persistent_request_storage_foundation_model.json",
        "14_backend/product_runtime/ui_models/request_storage_data_model.json",
        "14_backend/product_runtime/ui_models/request_lifecycle_state_model.json",
        "14_backend/product_runtime/ui_models/request_metadata_schema_model.json",
        "14_backend/product_runtime/ui_models/storage_boundary_contract_model.json",
        "14_backend/product_runtime/ui_models/server_side_storage_access_plan_model.json",
        "14_backend/product_runtime/ui_models/request_retrieval_readiness_plan_model.json",
        "14_backend/product_runtime/ui_models/storage_migration_blueprint_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp44_persistent_request_storage_foundation_report.md",
        "09_exports/mvp_product_track/mvp44_request_storage_data_model_report.md",
        "09_exports/mvp_product_track/mvp44_request_lifecycle_state_model_report.md",
        "09_exports/mvp_product_track/mvp44_request_metadata_schema_report.md",
        "09_exports/mvp_product_track/mvp44_storage_boundary_contract_report.md",
        "09_exports/mvp_product_track/mvp44_server_side_storage_access_plan_report.md",
        "09_exports/mvp_product_track/mvp44_request_retrieval_readiness_plan_report.md",
        "09_exports/mvp_product_track/mvp44_storage_migration_blueprint_report.md",
        "09_exports/mvp_product_track/mvp44_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp44_next_product_step_report.md",
        "09_exports/mvp_product_track/mvp44_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp44_acceptance_report.md",
        "09_exports/mvp_product_track/mvp44_validator_wall_review.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp44_persistent_request_storage_foundation.md",
        "09_exports/release_package/mvp44_request_storage_data_model.md",
        "09_exports/release_package/mvp44_request_lifecycle_state_model.md",
        "09_exports/release_package/mvp44_request_metadata_schema.md",
        "09_exports/release_package/mvp44_storage_boundary_contract.md",
        "09_exports/release_package/mvp44_server_side_storage_access_plan.md",
        "09_exports/release_package/mvp44_request_retrieval_readiness_plan.md",
        "09_exports/release_package/mvp44_storage_migration_blueprint.md",
        "09_exports/release_package/mvp44_persistent_request_storage_foundation_manifest.json",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")
        
    manifest = ROOT / "09_exports/release_package/mvp44_persistent_request_storage_foundation_manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            check(data.get("name") == "MVP-44 Persistent Request Storage Foundation", "manifest name incorrect")
        except json.JSONDecodeError:
            fail("manifest JSON invalid")

    index_path = ROOT / "13_web_dashboard/dist/index.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)
        
        markers = [
            "MVP-44",
            "PERSISTENT REQUEST STORAGE FOUNDATION",
            "REQUEST STORAGE DATA MODEL",
            "REQUEST LIFECYCLE STATE MODEL",
            "REQUEST METADATA SCHEMA",
            "STORAGE BOUNDARY CONTRACT",
            "SERVER SIDE STORAGE ACCESS PLAN",
            "REQUEST RETRIEVAL READINESS PLAN",
            "STORAGE MIGRATION BLUEPRINT",
            "STORAGE FOUNDATION ONLY",
            "SCHEMA READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL DATABASE WRITES",
            "NO SUPABASE WRITES",
            "NO PUBLIC WRITES",
            "NO LIVE REQUEST CREATION",
            "NO LIVE INTAKE",
            "NO PUBLIC ENDPOINT",
            "NO MIGRATION APPLY",
            "NO REAL PERSISTENCE",
            "NO COMMAND EXECUTION",
            "NO APPROVAL EXECUTION",
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
            "NEXT_STEP_BUILD_IMMUTABLE_AUDIT_EVENT_LEDGER",
            "NOT_READY_FOR_REAL_AUTOMATION"
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")
            
    acc_report = ROOT / "09_exports/mvp_product_track/mvp44_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "PERSISTENT_REQUEST_STORAGE_FOUNDATION_READY",
            "PASS_WITH_STORAGE_FOUNDATION_ONLY"
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")
            
    # Check semantic posture
    model_json = ROOT / "14_backend/product_runtime/ui_models/persistent_request_storage_foundation_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("persistent_request_storage_foundation_ready") == "true", "expected true")
        check(data.get("storage_foundation_only") == "true", "expected true")
        check(data.get("schema_readiness_only") == "true", "expected true")
        check(data.get("real_database_writes_enabled") == "false", "expected false")
        check(data.get("supabase_write_enabled") == "false", "expected false")
        check(data.get("public_write_enabled") == "false", "expected false")
        check(data.get("live_request_creation_enabled") == "false", "expected false")
        check(data.get("live_intake_enabled") == "false", "expected false")
        check(data.get("public_endpoint_enabled") == "false", "expected false")
        check(data.get("migration_apply_enabled") == "false", "expected false")
        check(data.get("real_persistence_enabled") == "false", "expected false")
        check(data.get("command_execution_enabled") == "false", "expected false")
        check(data.get("approval_execution_enabled") == "false", "expected false")
        check(data.get("deploy_controls_enabled") == "false", "expected false")
        check(data.get("merge_controls_enabled") == "false", "expected false")
        check(data.get("push_controls_enabled") == "false", "expected false")
        check(data.get("pr_controls_enabled") == "false", "expected false")
        check(data.get("github_mutation_enabled") == "false", "expected false")
        check(data.get("netlify_mutation_enabled") == "false", "expected false")
        check(data.get("automation_enabled") == "false", "expected false")
        
    # check no new Netlify functions added compared to origin/master
    current_functions = set(str(p.name) for p in (ROOT / "netlify/functions").glob("*.js"))
    # We'll just hardcode the known list or check if any are added in git diff
    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(not any(f.endswith(".js") for f in added_functions), "no new function files added")
    
    if FAILURES:
        print("MVP44_PERSISTENT_REQUEST_STORAGE_FOUNDATION_VALIDATION_FAIL")
        sys.exit(1)
        
    print("MVP44_PERSISTENT_REQUEST_STORAGE_FOUNDATION_VALIDATION_PASS")

if __name__ == "__main__":
    main()
