#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def _collect_forbidden_flags(text):
    required_lines = [
        "Live auth implemented: false",
        "Database implemented: false",
        "Real queue storage implemented: false",
        "Action execution implemented: false",
        "Command execution added: false",
        "GitHub API calls added: false",
        "Netlify API calls added: false",
        "External API calls added: false",
        "Browser external fetches added: false",
        "Secrets added: false",
        "Tokens added: false",
        "Environment variables read: false",
        "GitHub mutation added: false",
        "Netlify mutation added: false",
        "Deploy controls added: false",
        "Merge controls added: false",
        "Push controls added: false",
        "PR controls added: false"
    ]
    for line in required_lines:
        if line not in text:
            _fail(f"Missing required safety line: {line}")


def main():
    required_docs = [
        "14_backend/phase_4d_identity_selection_recommendation.md",
        "14_backend/phase_4d_role_permission_implementation_contract.md",
        "14_backend/phase_4d_action_request_queue_schema.md",
        "14_backend/phase_4d_audit_event_schema.md",
        "14_backend/phase_4d_human_approval_schema.md",
        "14_backend/phase_4d_risk_classification_model.md",
        "14_backend/phase_4d_request_only_endpoint_contract.md",
        "14_backend/phase_4d_disabled_dashboard_ui_contract.md",
        "14_backend/phase_4d_execution_boundary_contract.md",
        "14_backend/phase_4d_phase_4e_handoff_contract.md",
    ]
    required_reports = [
        "09_exports/backend_phase_4/backend_phase_4d_strategic_build_acceptance_report.md",
        "09_exports/backend_phase_4/backend_phase_4d_identity_selection_report.md",
        "09_exports/backend_phase_4/backend_phase_4d_action_schema_report.md",
        "09_exports/backend_phase_4/backend_phase_4d_audit_schema_report.md",
        "09_exports/backend_phase_4/backend_phase_4d_disabled_ui_report.md",
        "09_exports/backend_phase_4/backend_phase_4d_execution_boundary_report.md",
        "09_exports/backend_phase_4/backend_phase_4e_handoff_readiness_report.md",
    ]
    required_schemas = [
        "14_backend/schemas/phase4d_identity_schema.json",
        "14_backend/schemas/phase4d_action_schema.json",
        "14_backend/schemas/phase4d_audit_schema.json",
        "14_backend/schemas/phase4d_approval_schema.json",
        "14_backend/schemas/phase4d_risk_model.json",
    ]
    for rel in required_docs + required_reports + required_schemas:
        if not (ROOT / rel).exists():
            _fail(f"Required file missing: {rel}")

    for rel in required_docs:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "Planning only" not in text and "planning only" not in text.lower():
            _fail(f"Planning-only disclaimer missing: {rel}")

    acceptance = (ROOT / "09_exports/backend_phase_4/backend_phase_4d_strategic_build_acceptance_report.md").read_text(encoding="utf-8")
    if "PASS_WITH_HIGH_CONFIDENCE" not in acceptance:
        _fail("Acceptance report missing PASS_WITH_HIGH_CONFIDENCE")
    _collect_forbidden_flags(acceptance)

    boundary = (ROOT / "14_backend/phase_4d_execution_boundary_contract.md").read_text(encoding="utf-8")
    _collect_forbidden_flags(boundary)
    if "Netlify functions modified: false" not in boundary:
        _fail("Execution boundary contract missing Netlify functions invariant")

    identity_payload = json.loads((ROOT / "14_backend/schemas/phase4d_identity_schema.json").read_text(encoding="utf-8"))
    if identity_payload.get("schema_id") != "phase4d_identity_schema_v1":
        _fail("Identity schema id mismatch")

    print("BACKEND_PHASE_4D_STRATEGIC_BUILD_VALIDATION_PASS")


if __name__ == "__main__":
    main()
