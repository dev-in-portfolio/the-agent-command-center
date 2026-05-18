#!/usr/bin/env python3
# MVP47_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP47_NO_REAL_COMMAND_EXECUTION_CHECK
# MVP47_NO_REAL_ACTION_EXECUTION_CHECK
# MVP47_NO_REAL_EXTERNAL_DRY_RUN_CHECK
# MVP47_NO_APPROVAL_EXECUTION_CHECK
# MVP47_NO_DATABASE_WRITES_CHECK
# MVP47_NO_SUPABASE_WRITES_CHECK
# MVP47_NO_PUBLIC_WRITES_CHECK
# MVP47_NO_LIVE_REQUEST_MUTATION_CHECK
# MVP47_NO_AUDIT_EVENT_WRITES_CHECK
# MVP47_NO_EXTERNAL_API_MUTATION_CHECK
# MVP47_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP47_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP47_NO_ACTION_QUEUE_CHECK
# MVP47_NO_AUTOMATION_CHECK
# MVP47_NO_SERVICE_ROLE_CHECK
# MVP47_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP47_NO_TOKEN_INPUT_CHECK
# MVP47_NO_BROWSER_PERSISTENCE_CHECK
# MVP47_NO_MIGRATION_APPLY_CHECK
# MVP47_SERVER_SIDE_DRY_RUN_ENGINE_EXPORT_ARTIFACTS_CHECK
# MVP47_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

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
        "14_backend/product_runtime/ui_models/server_side_dry_run_engine_model.json",
        "14_backend/product_runtime/ui_models/action_plan_input_schema_model.json",
        "14_backend/product_runtime/ui_models/preflight_validation_schema_model.json",
        "14_backend/product_runtime/ui_models/simulated_execution_result_schema_model.json",
        "14_backend/product_runtime/ui_models/risk_dependency_report_model.json",
        "14_backend/product_runtime/ui_models/rollback_preview_model.json",
        "14_backend/product_runtime/ui_models/approval_bound_dry_run_contract_model.json",
        "14_backend/product_runtime/ui_models/dry_run_evidence_packet_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp47_server_side_dry_run_engine_report.md",
        "09_exports/mvp_product_track/mvp47_action_plan_input_schema_report.md",
        "09_exports/mvp_product_track/mvp47_preflight_validation_schema_report.md",
        "09_exports/mvp_product_track/mvp47_simulated_execution_result_schema_report.md",
        "09_exports/mvp_product_track/mvp47_risk_dependency_report.md",
        "09_exports/mvp_product_track/mvp47_rollback_preview_report.md",
        "09_exports/mvp_product_track/mvp47_approval_bound_dry_run_contract_report.md",
        "09_exports/mvp_product_track/mvp47_dry_run_evidence_packet_report.md",
        "09_exports/mvp_product_track/mvp47_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp47_next_product_step_report.md",
        "09_exports/mvp_product_track/mvp47_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp47_acceptance_report.md",
        "09_exports/mvp_product_track/mvp47_validator_wall_review.md",
        "09_exports/mvp_product_track/mvp47_validation_stewardship_report.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp47_server_side_dry_run_engine.md",
        "09_exports/release_package/mvp47_action_plan_input_schema.md",
        "09_exports/release_package/mvp47_preflight_validation_schema.md",
        "09_exports/release_package/mvp47_simulated_execution_result_schema.md",
        "09_exports/release_package/mvp47_risk_dependency_report.md",
        "09_exports/release_package/mvp47_rollback_preview.md",
        "09_exports/release_package/mvp47_approval_bound_dry_run_contract.md",
        "09_exports/release_package/mvp47_dry_run_evidence_packet.md",
        "09_exports/release_package/mvp47_server_side_dry_run_engine_manifest.json",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")
        
    manifest = ROOT / "09_exports/release_package/mvp47_server_side_dry_run_engine_manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            check(data.get("name") == "MVP-47 Server-Side Dry-Run Engine", "manifest name incorrect")
        except json.JSONDecodeError:
            fail("manifest JSON invalid")

    index_path = ROOT / "13_web_dashboard/dist/index.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)
        
        markers = [
            "MVP-47",
            "SERVER SIDE DRY RUN ENGINE",
            "ACTION PLAN INPUT SCHEMA",
            "PREFLIGHT VALIDATION SCHEMA",
            "SIMULATED EXECUTION RESULT SCHEMA",
            "RISK DEPENDENCY REPORT",
            "ROLLBACK PREVIEW",
            "APPROVAL BOUND DRY RUN CONTRACT",
            "DRY RUN EVIDENCE PACKET",
            "DRY RUN ENGINE FOUNDATION ONLY",
            "SCHEMA READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL COMMAND EXECUTION",
            "NO REAL ACTION EXECUTION",
            "NO REAL EXTERNAL DRY RUN",
            "NO APPROVAL EXECUTION",
            "NO DATABASE WRITES",
            "NO SUPABASE WRITES",
            "NO PUBLIC WRITES",
            "NO LIVE REQUEST MUTATION",
            "NO AUDIT EVENT WRITES",
            "NO EXTERNAL API MUTATION",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PR CONTROLS",
            "NO ACTION QUEUE",
            "AUTOMATION DISABLED",
            "SERVICE ROLE NOT USED",
            "SERVICE ROLE NOT IN BROWSER",
            "NO TOKEN INPUT",
            "NO BROWSER PERSISTENCE",
            "NO MIGRATION APPLY",
            "NEXT_STEP_BUILD_CONTROLLED_ACTION_QUEUE",
            "NOT_READY_FOR_REAL_AUTOMATION"
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")
            
    acc_report = ROOT / "09_exports/mvp_product_track/mvp47_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "SERVER_SIDE_DRY_RUN_ENGINE_READY",
            "PASS_WITH_DRY_RUN_ENGINE_FOUNDATION_ONLY"
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")
            
    # Check semantic posture
    model_json = ROOT / "14_backend/product_runtime/ui_models/server_side_dry_run_engine_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("server_side_dry_run_engine_ready") == "true", "expected true")
        check(data.get("dry_run_engine_foundation_only") == "true", "expected true")
        check(data.get("schema_readiness_only") == "true", "expected true")
        check(data.get("real_command_execution_enabled") == "false", "expected false")
        check(data.get("real_action_execution_enabled") == "false", "expected false")
        check(data.get("real_external_dry_run_enabled") == "false", "expected false")
        check(data.get("approval_execution_enabled") == "false", "expected false")
        check(data.get("database_write_enabled") == "false", "expected false")
        check(data.get("supabase_write_enabled") == "false", "expected false")
        check(data.get("public_write_enabled") == "false", "expected false")
        check(data.get("live_request_mutation_enabled") == "false", "expected false")
        check(data.get("audit_event_write_enabled") == "false", "expected false")
        check(data.get("external_api_mutation_enabled") == "false", "expected false")
        check(data.get("github_mutation_enabled") == "false", "expected false")
        check(data.get("netlify_mutation_enabled") == "false", "expected false")
        check(data.get("deploy_controls_enabled") == "false", "expected false")
        check(data.get("merge_controls_enabled") == "false", "expected false")
        check(data.get("push_controls_enabled") == "false", "expected false")
        check(data.get("pr_controls_enabled") == "false", "expected false")
        check(data.get("action_queue_enabled") == "false", "expected false")
        check(data.get("automation_enabled") == "false", "expected false")
        
    # check no new Netlify functions added compared to origin/master
    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(not any(f.endswith(".js") for f in added_functions), "no new function files added")
    
    if FAILURES:
        print("MVP47_SERVER_SIDE_DRY_RUN_ENGINE_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
        
    print("MVP47_SERVER_SIDE_DRY_RUN_ENGINE_VALIDATION_PASS")

if __name__ == "__main__":
    main()
