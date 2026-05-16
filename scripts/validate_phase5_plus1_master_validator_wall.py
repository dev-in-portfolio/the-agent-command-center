#!/usr/bin/env python3
"""Phase 5 + Original +1 + Original +1B master validator wall."""

from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
STATIC = ROOT / "13_web_dashboard" / "static"
PHASE5 = ROOT / "09_exports" / "interface_phase_5"
PLUS1 = ROOT / "09_exports" / "original_plus1"

errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def file_contains(path, text):
    return path.exists() and text in path.read_text(encoding="utf-8", errors="replace")


def js_safety_check(path):
    if not path.exists():
        errors.append(f"Missing JS file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in [
        "localStorage", "sessionStorage", "document.cookie", "indexedDB", "IndexedDB", "caches.", "serviceWorker",
        "WebSocket", "EventSource", "sendBeacon", "eval(", "Function(", "import(", "Blob", "URL.createObjectURL", "FileReader",
    ]:
        check(token not in text, f"dashboard.js contains forbidden token: {token}")
    for method in ['method: "POST"', "method:'POST'", 'method: "PUT"', "method:'PUT'", 'method: "PATCH"', "method:'PATCH'", 'method: "DELETE"', "method:'DELETE'"]:
        check(method not in text, f"dashboard.js contains forbidden HTTP method: {method}")
    allowed_fetches = {
        "./original_plus2c_audit_log_model.json",
        "./original_plus2d_approval_gate_model.json",
        "./original_plus2e_dry_run_engine_model.json",
        "/api/audit-log-status",
        "/api/approval-gate-status",
        "/api/dry-run-status",
        "/api/health",
        "/api/status",
        "/api/backend-manifest",
        "/api/auth-status",
        "/api/role-matrix",
        "/api/request-storage-status",
        "./status_snapshot.json",
        "./phase4d_identity_schema.json",
        "./phase4d_action_schema.json",
        "./phase4d_audit_schema.json",
        "./phase4d_approval_schema.json",
        "./phase4d_risk_model.json",
        "./original_plus1b_contract_schemas.json",
        "./original_plus1c_readiness_qa_model.json",
        "./original_plus1d_backend_boundary_model.json",
        "./original_plus1e_backend_build_tickets.json",
        "./original_plus2a_auth_foundation_model.json",
        "./original_plus2b_request_storage_model.json",
        "./mvp7_real_authenticated_reads_model.json",
        "./mvp8_controlled_request_create_model.json",
        "./mvp9_request_detail_lifecycle_model.json",
        "./mvp10_operator_workspace_model.json",
        "/api/request-read-smoke-status",
        "/api/request-write-smoke-status",
    }
    for target in re.findall(r'fetch\(["\']([^"\']+)["\']', text):
        check(target in allowed_fetches, f"dashboard.js unauthorized fetch: {target}")


report_requirements = [
    (PHASE5 / "original_phase_5_final_acceptance_report.md", "PHASE_5_COMPLETE"),
    (PHASE5 / "original_phase_5_final_production_summary.md", "PRODUCTION_VISIBLE"),
    (PHASE5 / "original_phase_5e_production_verification_report.md", "PRODUCTION_VERIFIED"),
    (PLUS1 / "original_plus1_production_verification_report.md", "PRODUCTION_VERIFIED"),
    (PLUS1 / "original_plus1b_production_verification_report.md", "PRODUCTION_VERIFIED"),
    (PLUS1 / "original_plus1c_production_verification_report.md", "PRODUCTION_VERIFIED"),
    (PLUS1 / "original_plus1d_production_verification_report.md", "PRODUCTION_VERIFIED"),
    (PLUS1 / "original_plus1_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_operator_console_consolidation_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_automation_contract_layer_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_contract_schema_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_master_validator_wall_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_design_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1b_safety_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_readiness_scoring_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_contract_qa_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_no_go_decision_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_dependency_gap_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_validator_confidence_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_design_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1c_safety_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_backend_boundary_blueprint_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_real_automation_dependency_map_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_endpoint_contract_map_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_auth_permission_architecture_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_storage_audit_approval_models_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_queue_job_lifecycle_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_mutation_gateway_boundary_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_future_integration_boundary_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_secrets_rollback_rate_limit_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_design_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_safety_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (PLUS1 / "original_plus1d_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_acceptance_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_migration_readiness_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_manual_migration_review_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_authenticated_request_reads_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_request_read_adapter_contract_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_security_boundary_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp5_next_product_step_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_controlled_migration_apply_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_migration_apply_result_report.md", "PASS_WITH_NOTES"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_post_migration_verification_report.md", "PASS_WITH_NOTES"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_authenticated_reads_enablement_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_feature_flag_enablement_report.md", "PASS_WITH_NOTES"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_security_boundary_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_next_product_step_report.md", "PASS_WITH_HIGH_CONFIDENCE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_acceptance_report.md", "PASS_WITH_CONDITIONAL_LIVE_DEPENDENCY"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp6_validator_wall_review.md", "PASS_WITH_TARGETED_VALIDATION"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_acceptance_report.md", "REAL_AUTHENTICATED_SUPABASE_READS_READY"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_real_authenticated_reads_report.md", "REAL_AUTHENTICATED_READS_IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_auth_token_validation_report.md", "IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_postgrest_read_adapter_report.md", "IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_request_endpoint_actions_report.md", "IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_read_smoke_test_report.md", "PASS_WITH_TOKEN_TEST_OPTIONAL"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_security_boundary_report.md", "VERIFIED_FOR_READS"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_next_product_step_report.md", "READY_FOR_VERIFICATION"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp7_requests_endpoint_hardening_report.md", "PASS_WITH_TARGETED_HARDENING"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_acceptance_report.md", "CONTROLLED_AUTHENTICATED_REQUEST_CREATE_READY"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_controlled_request_create_report.md", "CONTROLLED_REQUEST_CREATE_WRITE_IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_payload_schema_report.md", "DEFINED_AND_ENFORCED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_write_gate_report.md", "ACTIVE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_blocked_actions_report.md", "ENFORCED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_create_smoke_test_report.md", "PASS_WITH_CREATE_SMOKE_TEST_OPTIONAL"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_security_boundary_report.md", "VERIFIED_FOR_CREATION"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_next_product_step_report.md", "READY_FOR_VERIFICATION"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp8_write_path_review_report.md", "PASS_WITH_TARGETED_REVIEW"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_acceptance_report.md", "REQUEST_DETAIL_LIFECYCLE_TIMELINE_READY"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_request_list_ui_report.md", "DEFINED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_request_detail_ui_report.md", "DEFINED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_lifecycle_timeline_report.md", "DEFINED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_create_verification_harness_report.md", "DEFINED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_security_boundary_report.md", "VERIFIED_FOR_UI_MODELS"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp9_next_product_step_report.md", "READY_FOR_WORKSPACE_UI"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_acceptance_report.md", "OPERATOR_REQUEST_WORKSPACE_UI_READY"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_api_client_report.md", "IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_create_form_report.md", "IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_next_product_step_report.md", "READY_FOR_POLISH"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_operator_workspace_ui_report.md", "OPERATOR_REQUEST_WORKSPACE_UI_READY"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_request_panels_report.md", "IMPLEMENTED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_security_boundary_report.md", "VERIFIED_FOR_WORKSPACE"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_token_handling_report.md", "MEMORY_ONLY_ENFORCED"),
    (ROOT / "09_exports" / "mvp_product_track" / "mvp10_actual_token_storage_review.md", "PASS_WITH_TARGETED_REVIEW"),
]
for path, marker in report_requirements:
    check(path.exists(), f"missing report: {path.relative_to(ROOT)}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {path.name}")

index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")
for marker in [
    "Original Phase 5A",
    "Original Phase 5B",
    "Original Phase 5C",
    "Original Phase 5D",
    "Original Phase 5E",
    "Original +1",
    "Original +1B",
    "Original +1C",
    "Original +1D",
    "BACKEND BOUNDARY BLUEPRINT",
    "REAL AUTOMATION DEPENDENCY MAP",
    "BLUEPRINT ONLY",
    "FUTURE IMPLEMENTATION ONLY",
    "READINESS SCORING",
    "CONTRACT QA",
    "NO-GO DECISION LAYER",
    "NO LIVE AUTOMATION",
    "NO EXECUTION",
    "NO MUTATION",
    "NO BACKEND WRITES",
    "READY_FOR_BACKEND_ARCHITECTURE_REVIEW_ONLY",
    "NOT_READY_FOR_REAL_AUTOMATION",
    "MIGRATION READINESS CHECK",
    "MANUAL MIGRATION REVIEW REQUIRED",
    "AUTHENTICATED REQUEST READS",
    "READS REQUIRE BEARER TOKEN",
    "ANON KEY + USER TOKEN ONLY",
    "SERVICE ROLE NOT USED FOR READS",
    "WRITES STILL DISABLED",
    "RLS REVIEW REQUIRED",
    "NO AUTOMATIC MIGRATION APPLY",
    "NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS",
    "MVP-6",
    "CONTROLLED MIGRATION APPLY",
    "SCHEMA AND RLS MIGRATION",
    "POST-MIGRATION VERIFICATION",
    "AUTHENTICATED READS ENABLEMENT",
    "REQUEST API READS ENABLED TARGET",
    "REQUEST API WRITES STILL DISABLED",
    "SERVICE ROLE NOT EXPOSED TO BROWSER",
    "WRITES REQUIRE SEPARATE REVIEW",
    "NEXT_STEP_VERIFY_AUTHENTICATED_READS_WITH_REAL_USER_TOKEN",
    "MVP-7",
    "REAL AUTHENTICATED SUPABASE READS",
    "SUPABASE AUTH TOKEN VALIDATION",
    "POSTGREST READS ENABLED",
    "ANON KEY + USER BEARER TOKEN",
    "RLS-ENFORCED REQUEST READS",
    "SERVICE ROLE NOT USED",
    "WRITES STILL DISABLED",
    "POST WRITES BLOCKED",
    "VERIFY WITH REAL USER TOKEN",
    "MVP-8",
    "CONTROLLED REQUEST CREATE WRITE",
    "CREATE ONLY",
    "AUTHENTICATED POST REQUIRED",
    "STRICT PAYLOAD VALIDATION",
    "ANON KEY + USER BEARER TOKEN",
    "RLS-ENFORCED INSERT",
    "SERVICE ROLE NOT USED",
    "UPDATE DELETE EXECUTE BLOCKED",
    "AUTOMATION STILL DISABLED",
    "VERIFY CREATE WITH REAL USER TOKEN",
    "MVP-9",
    "REQUEST LIST UI MODEL",
    "REQUEST DETAIL UI MODEL",
    "LIFECYCLE TIMELINE",
    "USER-OWNED REQUESTS ONLY",
    "RLS-ENFORCED READS",
    "CREATE VERIFICATION HARNESS",
    "UPDATE DELETE EXECUTE BLOCKED",
    "SERVICE ROLE NOT USED",
    "AUTOMATION STILL DISABLED",
    "NEXT_STEP_BUILD_OPERATOR_REQUEST_WORKSPACE_UI",
    "MVP-10",
    "OPERATOR REQUEST WORKSPACE",
    "TOKEN IN MEMORY ONLY",
    "AUTH STATUS PANEL",
    "API STATUS PANEL",
    "REQUEST LIST PANEL",
    "REQUEST DETAIL PANEL",
    "LIFECYCLE TIMELINE PANEL",
    "DRY RUN RESULTS PANEL",
    "CREATE REQUEST FORM",
    "READ AND CREATE ONLY",
    "UPDATE DELETE EXECUTE BLOCKED",
    "SERVICE ROLE NOT USED",
    "AUTOMATION STILL DISABLED",
    "NEXT_STEP_ADD_TOKEN_AWARE_FRONTEND_SESSION_AND_REQUEST_WORKFLOW_POLISH",
]:
    check(marker in index, f"index.html missing required marker: {marker}")

for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
    tag, button_label, _ = match.groups()
    clean = button_label.strip().lower()
    if clean.startswith("copy ") or clean.startswith("load ") or clean.startswith("phase ") or clean.startswith("original +"):
        continue
    if any(word in clean for word in ["deploy", "merge", "push", "execute", "submit", "save", "queue", "create pr"]):
        check(False, f"index.html has forbidden enabled button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

changed = subprocess.run(
    ["git", "diff", "--name-only", "origin/master..HEAD"],
    capture_output=True,
    text=True,
    cwd=ROOT,
).stdout.strip().splitlines()

allowed_prefixes = [
        "scripts/validate_original_plus2c",
        "scripts/validate_original_plus2b",
        "scripts/validate_original_plus2a",
        "scripts/validate_mvp2_local_durable_request_persistence.py",
        "scripts/validate_mvp2_local_durable_request_persistence_e2e.py",
        "scripts/validate_mvp3_supabase_provider_request_api.py",
        "scripts/validate_mvp3_supabase_provider_request_api_e2e.py",
        "scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "scripts/validate_mvp4_supabase_auth_rls_request_api_e2e.py",
        "scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "scripts/validate_mvp5_migration_readiness_authenticated_reads_e2e.py",
        "scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "scripts/validate_mvp6_controlled_migration_authenticated_reads_e2e.py",
        "scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "scripts/validate_mvp7_real_authenticated_supabase_reads_e2e.py",
        "scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "scripts/validate_mvp8_controlled_authenticated_request_create_e2e.py",
        "scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "scripts/validate_mvp9_request_detail_lifecycle_timeline_e2e.py",
        "scripts/validate_mvp10_operator_request_workspace_ui.py",
        "scripts/validate_mvp10_operator_request_workspace_ui_e2e.py",
        "scripts/validate_mvp11_token_aware_workspace_polish.py",
        "scripts/validate_mvp11_token_aware_workspace_polish_e2e.py",
        "13_web_dashboard/",
        "09_exports/interface_phase_5/",
        "09_exports/original_plus1/",
        "09_exports/original_plus2/",
        "09_exports/mvp_product_track/",
        ".env.example",
        ".supabase.env.local.example",
        "AGENTS.md",
        ".gitignore",
        "14_backend/auth/",
        "14_backend/request_storage/",
        "14_backend/audit_log/",
        "14_backend/approval_gate/",
    "14_backend/dry_run/",
    "14_backend/product_runtime/",
    "netlify/functions/auth-status.js",
    "netlify/functions/role-matrix.js",
    "netlify/functions/request-storage-status.js",
    "netlify/functions/audit-log-status.js",
    "netlify/functions/approval-gate-status.js",
    "netlify/functions/dry-run-status.js",
    "netlify/functions/product-runtime-status.js",
    "netlify/functions/provider-status.js",
    "netlify/functions/auth-status.js",
    "netlify/functions/requests.js",
    "netlify/functions/request-readiness-status.js",
    "netlify/functions/backend-manifest.js",
    "netlify/functions/request-read-smoke-status.js",
    "netlify/functions/request-write-smoke-status.js",
    "netlify/functions/_shared/provider_config.js",
    "netlify/functions/_shared/supabase_read_client.js",
    "netlify/functions/_shared/supabase_write_client.js",
    "netlify/functions/_shared/request_payload_validator.js",
    "netlify/functions/_shared/auth_context.js",
    "netlify/functions/_shared/models/",
    "scripts/validate_original_plus1b_operator_console_contract_layer.py",
    "scripts/validate_original_plus1b_operator_console_contract_layer_e2e.py",
    "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
    "scripts/validate_original_plus1c_readiness_scoring_contract_qa_e2e.py",
    "scripts/validate_original_plus1d_backend_boundary_blueprint.py",
    "scripts/validate_original_plus1d_backend_boundary_blueprint_e2e.py",
    "scripts/validate_original_plus1e_backend_implementation_gate.py",
    "scripts/validate_original_plus1e_backend_implementation_gate_e2e.py",
    "scripts/validate_original_plus2a_backend_auth_foundation.py",
    "scripts/validate_original_plus2a_backend_auth_foundation_e2e.py",
    "scripts/validate_original_plus2b_persistent_request_storage.py",
    "scripts/validate_original_plus2b_persistent_request_storage_e2e.py",
    "scripts/validate_original_plus2c_immutable_audit_log.py",
    "scripts/validate_original_plus2c_immutable_audit_log_e2e.py",
    "scripts/validate_original_plus2d_approval_gate_storage.py",
    "scripts/validate_original_plus2d_approval_gate_storage_e2e.py",
    "scripts/validate_original_plus2e_server_side_dry_run_engine.py",
    "scripts/validate_original_plus2e_server_side_dry_run_engine_e2e.py",
    "scripts/validate_mvp1_request_lifecycle_runtime.py",
    "scripts/validate_mvp1_request_lifecycle_runtime_e2e.py",
    "scripts/validate_phase5_plus1_master_validator_wall.py",
    "scripts/validate_backend_phase_4a_e2e.py",
    "scripts/validate_backend_phase_4b_planning.py",
    "scripts/validate_backend_phase_4c_planning.py",
    "scripts/validate_backend_phase_4d_strategic_e2e.py",
    "scripts/validate_interface_phase_3_e2e.py",
    "scripts/validate_original_phase_4_hosted_dashboard_e2e.py",
    "scripts/validate_original_phase_5a_client_side_workflow_e2e.py",
    "scripts/validate_original_phase_5a_client_side_workflow_shell.py",
    "scripts/validate_original_phase_5b_request_packet_builder.py",
    "scripts/validate_original_plus1_controlled_automation_readiness.py",
    "scripts/validate_original_plus1_controlled_automation_readiness_e2e.py",
    "scripts/validate_original_phase_5b_request_packet_builder_e2e.py",
    "scripts/validate_original_phase_5c_review_board.py",
    "scripts/validate_backend_phase_4d_disabled_ui.py",
    "scripts/validate_interface_phase_3_dashboard.py",
    "scripts/validate_original_phase_5c_review_board_e2e.py",
    "scripts/validate_original_phase_5d_handoff_composer.py",
    "scripts/validate_original_phase_5d_handoff_composer_e2e.py",
    "scripts/validate_original_phase_5e_runbook_simulator.py",
    "scripts/validate_original_phase_5e_runbook_simulator_e2e.py",
]

forbidden_prefixes = [
    "09_exports/interface_phase_1/",
    "09_exports/interface_phase_2/",
    "09_exports/interface_phase_3/",
    "09_exports/interface_phase_4/",
    "11_interface/",
    "12_tui/",
    "10_runtime/",
]

for path in changed:
    for prefix in forbidden_prefixes:
        check(not path.startswith(prefix), f"Forbidden changed path: {path}")
    check(any(path.startswith(prefix) for prefix in allowed_prefixes), f"Unexpected changed path: {path}")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("PHASE5_PLUS1_MASTER_VALIDATOR_WALL_PASS")
