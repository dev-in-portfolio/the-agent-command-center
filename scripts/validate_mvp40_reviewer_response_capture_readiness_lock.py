# MVP40_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

import json, os, sys, re

# MVP40_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP40_NO_PUBLIC_ENDPOINT_CHECK
# MVP40_NO_PUBLIC_RESPONSE_SUBMISSION_CHECK
# MVP40_NO_REVIEWER_RESPONSE_WRITES_CHECK
# MVP40_NO_RESPONSE_CAPTURE_ENABLED_CHECK
# MVP40_NO_RESPONSE_PERSISTENCE_ENABLED_CHECK
# MVP40_NO_EMAIL_SENDING_CHECK
# MVP40_NO_REVIEWER_CONTACT_CHECK
# MVP40_NO_AUTOMATED_OUTREACH_CHECK
# MVP40_NO_LIVE_WRITES_CHECK
# MVP40_NO_PUBLIC_WRITES_CHECK
# MVP40_NO_TOKEN_INPUT_CHECK
# MVP40_NO_SECRETS_EXPOSED_CHECK
# MVP40_NO_SERVICE_ROLE_CHECK
# MVP40_NO_BROWSER_PERSISTENCE_CHECK
# MVP40_NO_DIRECT_SUPABASE_CHECK
# MVP40_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK
# MVP40_REVIEWER_RESPONSE_CAPTURE_READINESS_EXPORT_ARTIFACTS_CHECK
# MVP40_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

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

# MVP40_NO_DEPLOYMENT_CHECK
# MVP40_NO_RELEASE_EXECUTION_CHECK
# MVP40_NO_AUTOMATIC_RELEASE_APPROVAL_CHECK
# MVP40_NO_LIVE_WRITES_CHECK
# MVP40_NO_PUBLIC_WRITES_CHECK
def check_safety_flag(data, key, label):
    if data is None:
        return
    val = data.get(key)
    if val is True:
        fail(f"{label}: {key} is enabled (should be false)")
    elif val is None:
        fail(f"{label}: {key} is missing")

# MVP40_NO_TOKEN_INPUT_CHECK
# MVP40_NO_SECRETS_EXPOSED_CHECK
# MVP40_NO_SERVICE_ROLE_CHECK
def check_safety_flags(data, label, keys):
    for k in keys:
        check_safety_flag(data, k, label)

MODEL_SAFETY_KEYS = [
    "public_endpoint_enabled", "public_response_submission_enabled",
    "reviewer_response_write_enabled", "response_capture_enabled",
    "response_persistence_enabled", "email_sending_enabled",
    "reviewer_contact_enabled", "automated_outreach_enabled",
    "contact_automation_enabled", "live_write_enabled", "public_write_enabled",
    "token_input_enabled", "secrets_exposed", "service_role_used",
    "browser_direct_supabase_calls", "browser_persistence_enabled",
    "automation_enabled", "deploy_controls_enabled", "launch_automation_enabled",
    "update_enabled", "delete_enabled", "approve_enabled", "execute_enabled",
    "deploy_merge_push_controls_enabled"
]

print("MVP-40 Reviewer Response Capture Readiness Lock Validator")
print()

# Phase 1 — Model files
print("Phase 1 — Model Files")
models = {
    "reviewer_response_capture_readiness_lock_model.json": "Reviewer response capture readiness lock",
    "reviewer_response_schema_proposal_model.json": "Reviewer response schema proposal",
    "capture_safety_requirements_model.json": "Capture safety requirements",
    "operator_response_review_queue_readiness_model.json": "Operator response review queue readiness",
    "response_to_feedback_mapping_readiness_model.json": "Response-to-feedback mapping readiness",
    "response_triage_readiness_rules_model.json": "Response triage readiness rules",
    "future_capture_implementation_checklist_model.json": "Future capture implementation checklist",
}

for fname, label in models.items():
    path = f"14_backend/product_runtime/ui_models/{fname}"
    data = load_json(path, label)
    if data:
        print(f"  [OK] {label} model")
        check_safety_flags(data, label, MODEL_SAFETY_KEYS)

# MVP40_REVIEWER_RESPONSE_CAPTURE_READINESS_EXPORT_ARTIFACTS_CHECK
print()
print("Phase 2 — Release Package Export Artifacts")
exports = {
    "mvp40_reviewer_response_capture_readiness_lock.md": "Capture readiness lock",
    "mvp40_reviewer_response_schema_proposal.md": "Response schema proposal",
    "mvp40_capture_safety_requirements.md": "Capture safety requirements",
    "mvp40_operator_response_review_queue_readiness.md": "Operator review queue readiness",
    "mvp40_response_to_feedback_mapping_readiness.md": "Response-to-feedback mapping readiness",
    "mvp40_response_triage_readiness_rules.md": "Response triage readiness rules",
    "mvp40_future_capture_implementation_checklist.md": "Future capture implementation checklist",
    "mvp40_reviewer_response_capture_readiness_manifest.json": "Capture readiness manifest",
}

for fname, label in exports.items():
    path = f"09_exports/release_package/{fname}"
    check_file(path, label)
    if fname.endswith(".json"):
        load_json(path, label)
    else:
        print(f"  [OK] {label}")

# Phase 3 — Dashboard model
print()
print("Phase 3 — Dashboard Model")
model_file = "13_web_dashboard/dist/mvp40_reviewer_response_capture_readiness_lock_model.json"
data = load_json(model_file, "Dashboard model")
if data:
    check_safety_flags(data, "Dashboard model", MODEL_SAFETY_KEYS)
    rd = data.get("reviewer_response_capture_readiness_lock_ready")
    if rd is not True:
        fail("Dashboard model: reviewer_response_capture_readiness_lock_ready is not true")

# Phase 4 — Dashboard HTML
print()
print("Phase 4 — Dashboard HTML")
dashboard_html = os.path.join(REPO, "13_web_dashboard/dist/index.html")
if os.path.isfile(dashboard_html):
    with open(dashboard_html) as f:
        html = f.read()
    # Extract MVP-40 section for targeted checks (multi-line callout format)
    mvp40_start = html.find('data-mvp40-reviewer-response-capture-readiness-lock')
    mvp40_end = html.find('</details>', mvp40_start + 100) if mvp40_start > 0 else -1
    if mvp40_start > 0 and mvp40_end > 0:
        mvp40_html = html[mvp40_start:mvp40_end]
    else:
        fail("Dashboard HTML missing MVP-40 section data attribute")
        mvp40_html = ""
    markers = [
        ("MVP-40", "MVP-40 section"),
        ("REVIEWER RESPONSE CAPTURE READINESS LOCK", "Capture readiness lock label"),
        ("REVIEWER RESPONSE SCHEMA PROPOSAL", "Schema proposal label"),
        ("CAPTURE SAFETY REQUIREMENTS", "Safety requirements label"),
        ("OPERATOR RESPONSE REVIEW QUEUE READINESS", "Review queue readiness label"),
        ("RESPONSE TO FEEDBACK MAPPING READINESS", "Mapping readiness label"),
        ("RESPONSE TRIAGE READINESS RULES", "Triage readiness rules label"),
        ("FUTURE CAPTURE IMPLEMENTATION CHECKLIST", "Implementation checklist label"),
        ("OPERATOR REVIEW ONLY", "Operator review label"),
        ("READINESS ONLY", "Readiness only label"),
        ("FUTURE IMPLEMENTATION ONLY", "Future implementation label"),
        ("NO PUBLIC ENDPOINT", "No public endpoint label"),
        ("NO PUBLIC RESPONSE SUBMISSION", "No public response submission label"),
        ("NO REVIEWER RESPONSE WRITES", "No reviewer response writes label"),
        ("NO RESPONSE CAPTURE ENABLED", "No response capture enabled label"),
        ("NO RESPONSE PERSISTENCE ENABLED", "No response persistence enabled label"),
        ("NO EMAIL SENDING", "No email label"),
        ("NO REVIEWER CONTACT", "No contact label"),
        ("NO AUTOMATED OUTREACH", "No outreach label"),
        ("NO LIVE WRITES", "No live writes label"),
        ("NO PUBLIC WRITES", "No public writes label"),
        ("NO TOKEN INPUT", "No token label"),
        ("SERVICE ROLE NOT USED", "No service role label"),
        ("UPDATE DELETE EXECUTE BLOCKED", "No update/delete label"),
        ("AUTOMATION STILL DISABLED", "No automation label"),
        ("NOT_READY_FOR_REAL_AUTOMATION", "Not ready label"),
        ("NEXT_STEP_BUILD_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT", "Next step label"),
    ]
    for marker, label in markers:
        if marker not in mvp40_html:
            fail(f"Dashboard HTML MVP-40 section missing: {label} ({marker})")
        else:
            print(f"  [OK] Dashboard HTML MVP-40 section contains {label}")

else:
    fail("Missing dashboard index.html")

# Phase 5 — Acceptance report
print()
print("Phase 5 — Acceptance Report")
accept = os.path.join(REPO, "09_exports/mvp_product_track/mvp40_acceptance_report.md")
if os.path.isfile(accept):
    with open(accept) as f:
        text = f.read()
    markers = [
        "REVIEWER_RESPONSE_CAPTURE_READINESS_LOCK_READY",
        "PASS_WITH_READINESS_ONLY_CAPTURE_LOCK",
        "REVIEWER_RESPONSE_SCHEMA_PROPOSAL_READY",
        "CAPTURE_SAFETY_REQUIREMENTS_READY",
        "OPERATOR_RESPONSE_REVIEW_QUEUE_READINESS_READY",
        "RESPONSE_TO_FEEDBACK_MAPPING_READINESS_READY",
        "RESPONSE_TRIAGE_READINESS_RULES_READY",
        "FUTURE_CAPTURE_IMPLEMENTATION_CHECKLIST_READY",
        "OPERATOR_REVIEW_ONLY",
        "READINESS_ONLY",
        "FUTURE_IMPLEMENTATION_ONLY",
        "NO_PUBLIC_ENDPOINT",
        "NO_PUBLIC_RESPONSE_SUBMISSION",
        "NO_REVIEWER_RESPONSE_WRITES",
        "NO_RESPONSE_CAPTURE_ENABLED",
        "NO_RESPONSE_PERSISTENCE_ENABLED",
        "NO_EMAIL_SENDING",
        "NO_REVIEWER_CONTACT",
        "NO_AUTOMATED_OUTREACH",
        "NO_LIVE_WRITES",
        "NO_PUBLIC_WRITES",
        "NO_TOKEN_INPUT",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT",
    ]
    for m in markers:
        if m not in text:
            fail(f"Acceptance report missing marker: {m}")
        else:
            print(f"  [OK] Acceptance report contains {m}")
else:
    fail("Acceptance report missing")

# Phase 6 — Reports
print()
print("Phase 6 — MVP-40 Product Reports")
reports = [
    "mvp40_reviewer_response_capture_readiness_lock_report.md",
    "mvp40_reviewer_response_schema_proposal_report.md",
    "mvp40_capture_safety_requirements_report.md",
    "mvp40_operator_response_review_queue_readiness_report.md",
    "mvp40_response_to_feedback_mapping_readiness_report.md",
    "mvp40_response_triage_readiness_rules_report.md",
    "mvp40_future_capture_implementation_checklist_report.md",
    "mvp40_security_boundary_report.md",
    "mvp40_next_product_step_report.md",
    "mvp40_validator_quality_report.md",
    "mvp40_validator_wall_review.md",
]
for r in reports:
    check_file(f"09_exports/mvp_product_track/{r}", r)
print()

if FAILURES:
    print(f"FAILURES: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  {f}")
    sys.exit(1)

print("MVP40_REVIEWER_RESPONSE_CAPTURE_READINESS_LOCK_VALIDATION_PASS")
