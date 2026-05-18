#!/usr/bin/env python3
# MVP43_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP43_NO_REAL_LOGIN_ENABLED_CHECK
# MVP43_NO_TOKEN_INPUT_CHECK
# MVP43_NO_BROWSER_TOKEN_PERSISTENCE_CHECK
# MVP43_NO_LOCAL_STORAGE_TOKEN_CHECK
# MVP43_NO_SESSION_STORAGE_TOKEN_CHECK
# MVP43_NO_COOKIE_TOKEN_CHECK
# MVP43_NO_SERVICE_ROLE_CHECK
# MVP43_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP43_NO_BACKEND_WRITES_CHECK
# MVP43_NO_PUBLIC_WRITES_CHECK
# MVP43_NO_LIVE_INTAKE_CHECK
# MVP43_NO_REVIEWER_RESPONSE_WRITES_CHECK
# MVP43_NO_COMMAND_EXECUTION_CHECK
# MVP43_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP43_NO_GITHUB_MUTATION_CHECK
# MVP43_NO_NETLIFY_MUTATION_CHECK
# MVP43_NO_SUPABASE_WRITES_CHECK
# MVP43_NO_APPROVAL_EXECUTION_CHECK
# MVP43_NO_AUTOMATION_CHECK
# MVP43_OPERATIONAL_AUTH_FOUNDATION_EXPORT_ARTIFACTS_CHECK
# MVP43_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

import json
import os
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
        "14_backend/product_runtime/ui_models/operational_auth_foundation_model.json",
        "14_backend/product_runtime/ui_models/operator_identity_model.json",
        "14_backend/product_runtime/ui_models/role_permission_matrix_model.json",
        "14_backend/product_runtime/ui_models/session_validation_blueprint_model.json",
        "14_backend/product_runtime/ui_models/auth_boundary_contract_model.json",
        "14_backend/product_runtime/ui_models/server_side_auth_verification_plan_model.json",
        "14_backend/product_runtime/ui_models/browser_auth_safety_posture_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp43_operational_auth_foundation_report.md",
        "09_exports/mvp_product_track/mvp43_operator_identity_model_report.md",
        "09_exports/mvp_product_track/mvp43_role_permission_matrix_report.md",
        "09_exports/mvp_product_track/mvp43_session_validation_blueprint_report.md",
        "09_exports/mvp_product_track/mvp43_auth_boundary_contract_report.md",
        "09_exports/mvp_product_track/mvp43_server_side_auth_verification_plan_report.md",
        "09_exports/mvp_product_track/mvp43_browser_auth_safety_posture_report.md",
        "09_exports/mvp_product_track/mvp43_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp43_next_product_step_report.md",
        "09_exports/mvp_product_track/mvp43_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp43_acceptance_report.md",
        "09_exports/mvp_product_track/mvp43_validator_wall_review.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp43_operational_auth_foundation.md",
        "09_exports/release_package/mvp43_operator_identity_model.md",
        "09_exports/release_package/mvp43_role_permission_matrix.md",
        "09_exports/release_package/mvp43_session_validation_blueprint.md",
        "09_exports/release_package/mvp43_auth_boundary_contract.md",
        "09_exports/release_package/mvp43_server_side_auth_verification_plan.md",
        "09_exports/release_package/mvp43_browser_auth_safety_posture.md",
        "09_exports/release_package/mvp43_operational_auth_foundation_manifest.json",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")
        
    manifest = ROOT / "09_exports/release_package/mvp43_operational_auth_foundation_manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            check(data.get("name") == "MVP-43 Operational Auth Foundation", "manifest name incorrect")
        except json.JSONDecodeError:
            fail("manifest JSON invalid")

    index_path = ROOT / "13_web_dashboard/dist/index.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)
        
        markers = [
            "MVP-43",
            "OPERATIONAL AUTH FOUNDATION",
            "OPERATOR IDENTITY MODEL",
            "ROLE PERMISSION MATRIX",
            "SESSION VALIDATION BLUEPRINT",
            "AUTH BOUNDARY CONTRACT",
            "SERVER SIDE AUTH VERIFICATION PLAN",
            "BROWSER AUTH SAFETY POSTURE",
            "AUTH FOUNDATION ONLY",
            "READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL LOGIN ENABLED",
            "NO TOKEN INPUT",
            "NO BROWSER TOKEN PERSISTENCE",
            "NO LOCAL STORAGE TOKEN",
            "NO SESSION STORAGE TOKEN",
            "NO COOKIE TOKEN",
            "SERVICE ROLE NOT USED",
            "SERVICE ROLE NOT IN BROWSER",
            "NO BACKEND WRITES",
            "NO PUBLIC WRITES",
            "NO LIVE INTAKE",
            "NO REVIEWER RESPONSE WRITES",
            "NO COMMAND EXECUTION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PR CONTROLS",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "NO SUPABASE WRITES",
            "NO APPROVAL EXECUTION",
            "AUTOMATION DISABLED",
            "NEXT_STEP_BUILD_PERSISTENT_REQUEST_STORAGE_FOUNDATION",
            "NOT_READY_FOR_REAL_AUTOMATION"
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")
            
    acc_report = ROOT / "09_exports/mvp_product_track/mvp43_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "OPERATIONAL_AUTH_FOUNDATION_READY",
            "PASS_WITH_AUTH_FOUNDATION_ONLY"
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")
            
    # Check semantic posture
    model_json = ROOT / "14_backend/product_runtime/ui_models/operational_auth_foundation_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("operational_auth_foundation_ready") == "true", "expected true")
        check(data.get("auth_foundation_only") == "true", "expected true")
        check(data.get("readiness_only") == "true", "expected true")
        check(data.get("real_login_enabled") == "false", "expected false")
        check(data.get("token_input_enabled") == "false", "expected false")
        check(data.get("browser_token_persistence_enabled") == "false", "expected false")
        check(data.get("local_storage_token_enabled") == "false", "expected false")
        check(data.get("session_storage_token_enabled") == "false", "expected false")
        check(data.get("cookie_token_enabled") == "false", "expected false")
        check(data.get("service_role_used") == "false", "expected false")
        check(data.get("service_role_in_browser") == "false", "expected false")
        check(data.get("backend_write_enabled") == "false", "expected false")
        check(data.get("public_write_enabled") == "false", "expected false")
        check(data.get("live_intake_enabled") == "false", "expected false")
        check(data.get("reviewer_response_write_enabled") == "false", "expected false")
        check(data.get("command_execution_enabled") == "false", "expected false")
        check(data.get("deploy_controls_enabled") == "false", "expected false")
        check(data.get("merge_controls_enabled") == "false", "expected false")
        check(data.get("push_controls_enabled") == "false", "expected false")
        check(data.get("pr_controls_enabled") == "false", "expected false")
        check(data.get("github_mutation_enabled") == "false", "expected false")
        check(data.get("netlify_mutation_enabled") == "false", "expected false")
        check(data.get("supabase_write_enabled") == "false", "expected false")
        check(data.get("approval_execution_enabled") == "false", "expected false")
        check(data.get("automation_enabled") == "false", "expected false")
        
    check(not list((ROOT / "netlify/functions").glob("live_endpoint.js")), "no endpoint files added")
    
    if FAILURES:
        print("MVP43_OPERATIONAL_AUTH_FOUNDATION_VALIDATION_FAIL")
        sys.exit(1)
        
    print("MVP43_OPERATIONAL_AUTH_FOUNDATION_VALIDATION_PASS")

if __name__ == "__main__":
    main()
