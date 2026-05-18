#!/usr/bin/env python3
# MVP41_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

import json, os, sys, re

# MVP41_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP41_NO_PUBLIC_ENDPOINT_CHECK
# MVP41_NO_LIVE_INTAKE_CHECK
# MVP41_NO_PUBLIC_RESPONSE_SUBMISSION_CHECK
# MVP41_NO_REVIEWER_RESPONSE_WRITES_CHECK
# MVP41_NO_RESPONSE_CAPTURE_ENABLED_CHECK
# MVP41_NO_RESPONSE_PERSISTENCE_ENABLED_CHECK
# MVP41_NO_AUTOMATIC_IMPORT_CHECK
# MVP41_NO_EMAIL_SENDING_CHECK
# MVP41_NO_REVIEWER_CONTACT_CHECK
# MVP41_NO_AUTOMATED_OUTREACH_CHECK
# MVP41_NO_LIVE_WRITES_CHECK
# MVP41_NO_PUBLIC_WRITES_CHECK
# MVP41_NO_TOKEN_INPUT_CHECK
# MVP41_NO_SECRETS_EXPOSED_CHECK
# MVP41_NO_SERVICE_ROLE_CHECK
# MVP41_NO_BROWSER_PERSISTENCE_CHECK
# MVP41_NO_DIRECT_SUPABASE_CHECK
# MVP41_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK
# MVP41_CONTROLLED_REVIEWER_RESPONSE_INTAKE_EXPORT_ARTIFACTS_CHECK
# MVP41_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print(f"  [FAIL] {msg}")


def check_file(path, label):
    full = os.path.join(REPO, path)
    if not os.path.isfile(full):
        fail(f"{label}: missing {path}")
        return None
    return full


def load_json(path, label):
    full = check_file(path, label)
    if full is None:
        return None
    try:
        with open(full) as f:
            return json.load(f)
    except Exception as e:
        fail(f"{label}: invalid JSON - {e}")
        return None

MODEL_FALSE_KEYS = [
    "public_endpoint_enabled", "live_intake_enabled", "public_response_submission_enabled",
    "reviewer_response_write_enabled", "response_capture_enabled", "response_persistence_enabled",
    "automatic_import_enabled", "email_sending_enabled", "reviewer_contact_enabled",
    "automated_outreach_enabled", "contact_automation_enabled", "live_write_enabled",
    "public_write_enabled", "token_input_enabled", "secrets_exposed", "service_role_used",
    "browser_direct_supabase_calls", "browser_persistence_enabled", "automation_enabled",
    "deploy_controls_enabled", "launch_automation_enabled", "update_enabled",
    "delete_enabled", "approve_enabled", "execute_enabled", "deploy_merge_push_controls_enabled",
]
MODEL_TRUE_KEYS = ["operator_review_only", "blueprint_only", "future_implementation_only"]
MODEL_READY_MAP = {
    "controlled_reviewer_response_intake_blueprint_model.json": "controlled_reviewer_response_intake_blueprint_ready",
    "intake_route_design_proposal_model.json": "intake_route_design_proposal_ready",
    "manual_reviewer_response_import_path_model.json": "manual_reviewer_response_import_path_ready",
    "operator_approval_gate_blueprint_model.json": "operator_approval_gate_blueprint_ready",
    "reviewer_response_validation_rules_model.json": "reviewer_response_validation_rules_ready",
    "response_normalization_mapping_blueprint_model.json": "response_normalization_mapping_blueprint_ready",
    "controlled_intake_implementation_checklist_model.json": "controlled_intake_implementation_checklist_ready",
}

print("MVP-41 Controlled Reviewer Response Intake Blueprint Validator")
print()

print("Phase 1 — Model Files")
models = {
    "controlled_reviewer_response_intake_blueprint_model.json": "Controlled reviewer response intake blueprint",
    "intake_route_design_proposal_model.json": "Intake route design proposal",
    "manual_reviewer_response_import_path_model.json": "Manual reviewer response import path",
    "operator_approval_gate_blueprint_model.json": "Operator approval gate blueprint",
    "reviewer_response_validation_rules_model.json": "Reviewer response validation rules",
    "response_normalization_mapping_blueprint_model.json": "Response normalization mapping blueprint",
    "controlled_intake_implementation_checklist_model.json": "Controlled intake implementation checklist",
}
for fname, label in models.items():
    data = load_json(f"14_backend/product_runtime/ui_models/{fname}", label)
    if data:
        print(f"  [OK] {label} model")
        for key in MODEL_TRUE_KEYS:
            if data.get(key) is not True:
                fail(f"{label}: {key} is not true")
        ready_key = MODEL_READY_MAP[fname]
        if data.get(ready_key) is not True:
            fail(f"{label}: {ready_key} is not true")
        for key in MODEL_FALSE_KEYS:
            if data.get(key) is True:
                fail(f"{label}: {key} is enabled (should be false)")
            elif key not in data:
                fail(f"{label}: {key} is missing")

print()
print("Phase 2 — Release Package Export Artifacts")
exports = {
    "mvp41_controlled_reviewer_response_intake_blueprint.md": "Controlled reviewer response intake blueprint",
    "mvp41_intake_route_design_proposal.md": "Intake route design proposal",
    "mvp41_manual_reviewer_response_import_path.md": "Manual reviewer response import path",
    "mvp41_operator_approval_gate_blueprint.md": "Operator approval gate blueprint",
    "mvp41_reviewer_response_validation_rules.md": "Reviewer response validation rules",
    "mvp41_response_normalization_mapping_blueprint.md": "Response normalization mapping blueprint",
    "mvp41_controlled_intake_implementation_checklist.md": "Controlled intake implementation checklist",
    "mvp41_controlled_reviewer_response_intake_manifest.json": "Controlled reviewer response intake manifest",
}
for fname, label in exports.items():
    path = f"09_exports/release_package/{fname}"
    check_file(path, label)
    if fname.endswith('.json'):
        load_json(path, label)
    else:
        print(f"  [OK] {label}")

print()
print("Phase 3 — Dashboard Model")
model_file = "13_web_dashboard/dist/mvp41_controlled_reviewer_response_intake_blueprint_model.json"
data = load_json(model_file, "Dashboard model")
if data:
    for key in [
        "controlled_reviewer_response_intake_blueprint_ready",
        "intake_route_design_proposal_ready",
        "manual_reviewer_response_import_path_ready",
        "operator_approval_gate_blueprint_ready",
        "reviewer_response_validation_rules_ready",
        "response_normalization_mapping_blueprint_ready",
        "controlled_intake_implementation_checklist_ready",
    ]:
        if data.get(key) is not True:
            fail(f"Dashboard model: {key} is not true")
    for key in MODEL_TRUE_KEYS:
        if data.get(key) is not True:
            fail(f"Dashboard model: {key} is not true")
    for key in MODEL_FALSE_KEYS:
        if data.get(key) is True:
            fail(f"Dashboard model: {key} is enabled (should be false)")
        elif key not in data:
            fail(f"Dashboard model: {key} is missing")

print()
print("Phase 4 — Dashboard HTML")
dashboard_html = os.path.join(REPO, "13_web_dashboard/dist/index.html")
if os.path.isfile(dashboard_html):
    with open(dashboard_html) as f:
        html = f.read()
    marker_start = html.find('data-mvp41-controlled-reviewer-response-intake-blueprint')
    marker_end = html.find('</details>', marker_start + 100) if marker_start > 0 else -1
    if marker_start > 0 and marker_end > 0:
        mvp41_html = html[marker_start:marker_end]
    else:
        fail("Dashboard HTML missing MVP-41 section data attribute")
        mvp41_html = ""
    markers = [
        ("MVP-41", "MVP-41 section"),
        ("CONTROLLED REVIEWER RESPONSE INTAKE BLUEPRINT", "Blueprint label"),
        ("INTAKE ROUTE DESIGN PROPOSAL", "Route design label"),
        ("MANUAL REVIEWER RESPONSE IMPORT PATH", "Manual import label"),
        ("OPERATOR APPROVAL GATE BLUEPRINT", "Approval gate label"),
        ("REVIEWER RESPONSE VALIDATION RULES", "Validation rules label"),
        ("RESPONSE NORMALIZATION MAPPING BLUEPRINT", "Normalization mapping label"),
        ("CONTROLLED INTAKE IMPLEMENTATION CHECKLIST", "Implementation checklist label"),
        ("OPERATOR REVIEW ONLY", "Operator review label"),
        ("BLUEPRINT ONLY", "Blueprint only label"),
        ("FUTURE IMPLEMENTATION ONLY", "Future implementation label"),
        ("NO PUBLIC ENDPOINT", "No public endpoint label"),
        ("NO LIVE INTAKE", "No live intake label"),
        ("NO PUBLIC RESPONSE SUBMISSION", "No public response submission label"),
        ("NO REVIEWER RESPONSE WRITES", "No reviewer response writes label"),
        ("NO RESPONSE CAPTURE ENABLED", "No response capture enabled label"),
        ("NO RESPONSE PERSISTENCE ENABLED", "No response persistence enabled label"),
        ("NO AUTOMATIC IMPORT", "No automatic import label"),
        ("NO EMAIL SENDING", "No email label"),
        ("NO REVIEWER CONTACT", "No contact label"),
        ("NO AUTOMATED OUTREACH", "No outreach label"),
        ("NO LIVE WRITES", "No live writes label"),
        ("NO PUBLIC WRITES", "No public writes label"),
        ("NO TOKEN INPUT", "No token label"),
        ("NO SECRETS EXPOSED", "No secrets label"),
        ("SERVICE ROLE NOT USED", "No service role label"),
        ("UPDATE DELETE EXECUTE BLOCKED", "No update/delete label"),
        ("AUTOMATION STILL DISABLED", "No automation label"),
        ("NEXT_STEP_BUILD_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN", "Next step label"),
        ("NOT_READY_FOR_REAL_AUTOMATION", "Not ready label"),
    ]
    for marker, label in markers:
        if marker not in mvp41_html:
            fail(f"Dashboard HTML MVP-41 section missing: {label} ({marker})")
        else:
            print(f"  [OK] Dashboard HTML MVP-41 section contains {label}")
else:
    fail("Missing dashboard index.html")

print()
print("Phase 5 — Acceptance Report")
accept = os.path.join(REPO, "09_exports/mvp_product_track/mvp41_acceptance_report.md")
if os.path.isfile(accept):
    with open(accept) as f:
        text = f.read()
    markers = [
        "CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT_READY",
        "PASS_WITH_BLUEPRINT_ONLY_CONTROLLED_INTAKE",
        "INTAKE_ROUTE_DESIGN_PROPOSAL_READY",
        "MANUAL_REVIEWER_RESPONSE_IMPORT_PATH_READY",
        "OPERATOR_APPROVAL_GATE_BLUEPRINT_READY",
        "REVIEWER_RESPONSE_VALIDATION_RULES_READY",
        "RESPONSE_NORMALIZATION_MAPPING_BLUEPRINT_READY",
        "CONTROLLED_INTAKE_IMPLEMENTATION_CHECKLIST_READY",
        "OPERATOR_REVIEW_ONLY",
        "BLUEPRINT_ONLY",
        "FUTURE_IMPLEMENTATION_ONLY",
        "NO_PUBLIC_ENDPOINT",
        "NO_LIVE_INTAKE",
        "NO_PUBLIC_RESPONSE_SUBMISSION",
        "NO_REVIEWER_RESPONSE_WRITES",
        "NO_RESPONSE_CAPTURE_ENABLED",
        "NO_RESPONSE_PERSISTENCE_ENABLED",
        "NO_AUTOMATIC_IMPORT",
        "NO_EMAIL_SENDING",
        "NO_REVIEWER_CONTACT",
        "NO_AUTOMATED_OUTREACH",
        "NO_LIVE_WRITES",
        "NO_PUBLIC_WRITES",
        "NO_TOKEN_INPUT",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN",
    ]
    for m in markers:
        if m not in text:
            fail(f"Acceptance report missing marker: {m}")
        else:
            print(f"  [OK] Acceptance report contains {m}")
else:
    fail("Acceptance report missing")

print()
print("Phase 6 — MVP-41 Product Reports")
reports = [
    "mvp41_controlled_reviewer_response_intake_blueprint_report.md",
    "mvp41_intake_route_design_proposal_report.md",
    "mvp41_manual_reviewer_response_import_path_report.md",
    "mvp41_operator_approval_gate_blueprint_report.md",
    "mvp41_reviewer_response_validation_rules_report.md",
    "mvp41_response_normalization_mapping_blueprint_report.md",
    "mvp41_controlled_intake_implementation_checklist_report.md",
    "mvp41_security_boundary_report.md",
    "mvp41_next_product_step_report.md",
    "mvp41_validator_quality_report.md",
    "mvp41_validator_wall_review.md",
]
for r in reports:
    check_file(f"09_exports/mvp_product_track/{r}", r)
print()

if FAILURES:
    print(f"FAILURES: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  {f}")
    sys.exit(1)

print("MVP41_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT_VALIDATION_PASS")
