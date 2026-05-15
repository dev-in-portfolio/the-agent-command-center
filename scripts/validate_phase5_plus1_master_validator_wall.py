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
    "netlify/functions/backend-manifest.js",
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
