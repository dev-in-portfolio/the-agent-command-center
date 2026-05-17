# MVP39_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

import json, os, sys, re

# MVP39_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP39_PACKAGE_NOT_SENT_CHECK
# MVP39_NO_EMAIL_SENDING_CHECK
# MVP39_NO_REVIEWER_CONTACT_CHECK
# MVP39_NO_AUTOMATED_OUTREACH_CHECK
# MVP39_NO_DEPLOYMENT_CHECK
# MVP39_NO_RELEASE_EXECUTION_CHECK
# MVP39_NO_LIVE_WRITES_CHECK
# MVP39_NO_PUBLIC_WRITES_CHECK
# MVP39_NO_TOKEN_INPUT_CHECK
# MVP39_NO_SECRETS_EXPOSED_CHECK
# MVP39_NO_SERVICE_ROLE_CHECK
# MVP39_NO_BROWSER_PERSISTENCE_CHECK
# MVP39_NO_DIRECT_SUPABASE_CHECK
# MVP39_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK
# MVP39_EXTERNAL_DEMO_REVIEW_SHARE_EXPORT_ARTIFACTS_CHECK
# MVP39_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

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

# MVP39_NO_DEPLOYMENT_CHECK
# MVP39_NO_RELEASE_EXECUTION_CHECK
# MVP39_NO_AUTOMATIC_RELEASE_APPROVAL_CHECK
# MVP39_NO_LIVE_WRITES_CHECK
# MVP39_NO_PUBLIC_WRITES_CHECK
def check_safety_flag(data, key, label):
    if data is None:
        return
    val = data.get(key)
    if val is True:
        fail(f"{label}: {key} is enabled (should be false)")
    elif val is None:
        fail(f"{label}: {key} is missing")

# MVP39_NO_TOKEN_INPUT_CHECK
# MVP39_NO_SECRETS_EXPOSED_CHECK
# MVP39_NO_SERVICE_ROLE_CHECK
def check_safety_flags(data, label, keys):
    for k in keys:
        check_safety_flag(data, k, label)

MODEL_SAFETY_KEYS = [
    "deployment_enabled", "release_execution_enabled", "automatic_release_approval_enabled",
    "live_write_enabled", "public_write_enabled", "token_input_enabled",
    "secrets_exposed", "service_role_used", "browser_direct_supabase_calls",
    "browser_persistence_enabled", "automation_enabled", "update_enabled",
    "delete_enabled", "approve_enabled", "execute_enabled",
    "deploy_merge_push_controls_enabled", "email_sending_enabled",
    "reviewer_contact_enabled", "automated_outreach_enabled",
    "contact_automation_enabled", "launch_automation_enabled",
    "deploy_controls_enabled"
]

# MVP39_PACKAGE_NOT_SENT_CHECK
PACKAGE_SENT_KEYS = ["package_sent"]

print("MVP-39 External Demo Review Share Package Lock Validator")
print()

# Phase 1 — Model files
print("Phase 1 — Model Files")
models = {
    "external_demo_review_share_package_lock_model.json": "External share package lock",
    "share_safe_package_index_model.json": "Share-safe package index",
    "role_based_external_reviewer_packet_model.json": "Role-based reviewer packet",
    "copy_only_share_instruction_model.json": "Copy-only share instruction",
    "reviewer_safe_demo_walkthrough_model.json": "Reviewer-safe demo walkthrough",
    "share_readiness_validation_packet_model.json": "Share-readiness validation packet",
}

for fname, label in models.items():
    path = f"14_backend/product_runtime/ui_models/{fname}"
    data = load_json(path, label)
    if data:
        print(f"  [OK] {label} model")
        check_safety_flags(data, label, MODEL_SAFETY_KEYS)
        check_safety_flags(data, label, PACKAGE_SENT_KEYS)

# MVP39_EXTERNAL_DEMO_REVIEW_SHARE_EXPORT_ARTIFACTS_CHECK
print()
print("Phase 2 — Release Package Export Artifacts")
exports = {
    "mvp39_external_demo_review_share_package_lock.md": "Share package lock",
    "mvp39_share_safe_package_index.md": "Share-safe package index",
    "mvp39_founder_external_reviewer_packet.md": "Founder reviewer packet",
    "mvp39_recruiter_external_reviewer_packet.md": "Recruiter reviewer packet",
    "mvp39_technical_external_reviewer_packet.md": "Technical reviewer packet",
    "mvp39_copy_only_share_instructions.md": "Copy-only share instructions",
    "mvp39_reviewer_safe_demo_walkthrough.md": "Reviewer-safe demo walkthrough",
    "mvp39_share_readiness_validation_packet.md": "Share-readiness validation packet",
    "mvp39_external_demo_review_share_manifest.json": "Share manifest",
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
model_file = "13_web_dashboard/dist/mvp39_external_demo_review_share_package_lock_model.json"
data = load_json(model_file, "Dashboard model")
if data:
    check_safety_flags(data, "Dashboard model", MODEL_SAFETY_KEYS)
    check_safety_flags(data, "Dashboard model", PACKAGE_SENT_KEYS)
    rd = data.get("external_demo_review_share_package_lock_ready")
    if rd is not True:
        fail("Dashboard model: external_demo_review_share_package_lock_ready is not true")

# Phase 4 — Dashboard HTML
print()
print("Phase 4 — Dashboard HTML")
dashboard_html = os.path.join(REPO, "13_web_dashboard/dist/index.html")
if os.path.isfile(dashboard_html):
    with open(dashboard_html) as f:
        html = f.read()
    # Extract MVP-39 section for targeted checks
    mvp39_start = html.find('data-mvp39-external-demo-review-share-package-lock')
    mvp39_end = html.find('</details>', mvp39_start + 100) if mvp39_start > 0 else -1
    if mvp39_start > 0 and mvp39_end > 0:
        mvp39_html = html[mvp39_start:mvp39_end]
    else:
        fail("Dashboard HTML missing MVP-39 section data attribute")
        mvp39_html = ""
    markers = [
        ("MVP-39", "MVP-39 section"),
        ("EXTERNAL DEMO REVIEW SHARE PACKAGE LOCK", "External demo share lock label"),
        ("SHARE SAFE PACKAGE INDEX", "Share-safe index label"),
        ("ROLE BASED EXTERNAL REVIEWER PACKETS", "Role-based packets label"),
        ("COPY ONLY SHARE INSTRUCTIONS", "Copy-only instructions label"),
        ("REVIEWER SAFE DEMO WALKTHROUGH", "Reviewer-safe walkthrough label"),
        ("SHARE READINESS VALIDATION PACKET", "Share-readiness packet label"),
        ("OPERATOR REVIEW ONLY", "Operator review label"),
        ("SHARE PACKAGE LOCKED", "Share locked label"),
        ("COPY ONLY SHARING", "Copy only label"),
        ("PACKAGE NOT SENT", "Not sent label"),
        ("NO EMAIL SENDING", "No email label"),
        ("NO REVIEWER CONTACT", "No contact label"),
        ("NO DEPLOYMENT", "No deploy label"),
        ("NO RELEASE EXECUTION", "No release label"),
        ("NO LIVE WRITES", "No live writes label"),
        ("NO PUBLIC WRITES", "No public writes label"),
        ("NO TOKEN INPUT", "No token label"),
        ("SERVICE ROLE NOT USED", "No service role label"),
        ("UPDATE DELETE EXECUTE BLOCKED", "No update/delete label"),
        ("AUTOMATION STILL DISABLED", "No automation label"),
        ("NOT_READY_FOR_REAL_AUTOMATION", "Not ready label"),
    ]
    for marker, label in markers:
        if marker not in mvp39_html:
            fail(f"Dashboard HTML MVP-39 section missing: {label} ({marker})")
        else:
            print(f"  [OK] Dashboard HTML MVP-39 section contains {label}")

    # MVP39_NO_WHOLE_FILE_SAFETY_LABEL_SKIP
    # Check that we don't just rely on file-level labels
    # Check forbidden buttons - only check buttons within the MVP-39 section
    forbidden = [
        "Send Package", "Send Email", "Email Reviewer", "Contact Reviewer",
        "Start Outreach", "Automate Outreach", "Approve Release",
        "Execute Release", "Mark Approved", "Deploy", "Merge",
        "Push", "Create PR", "Launch", "Publish", "Execute", "Approve",
        "Apply Migration", "Enable Writes", "Token", "Login",
        "Connect Supabase", "Submit", "Save", "Send",
    ]
    for btn in forbidden:
        pattern = r'<button[^>]*>[^<]*' + re.escape(btn) + r'[^<]*</button>'
        matches = re.findall(pattern, mvp39_html)
        enabled_matches = [m for m in matches if 'disabled' not in m.lower()]
        if enabled_matches:
            fail(f"Dashboard HTML MVP-39 section has enabled forbidden button: {btn}")
        else:
            print(f"  [OK] Forbidden button '{btn}' not found in MVP-39 section")

    allowed = [
        "Copy Share Package Index", "Copy Founder Reviewer Packet",
        "Copy Recruiter Reviewer Packet", "Copy Technical Reviewer Packet",
        "Copy Share Instructions", "Copy Demo Walkthrough",
        "Copy Share Readiness Packet",
    ]
    for btn in allowed:
        if btn not in mvp39_html:
            fail(f"Dashboard HTML MVP-39 section missing allowed button: {btn}")
        else:
            print(f"  [OK] Allowed button '{btn}' found in MVP-39 section")

else:
    fail("MVP39_NO_EXPORT_ARTIFACTS_CHECK: Missing dashboard index.html")

# Phase 5 — Acceptance report
print()
print("Phase 5 — Acceptance Report")
accept = os.path.join(REPO, "09_exports/mvp_product_track/mvp39_acceptance_report.md")
if os.path.isfile(accept):
    with open(accept) as f:
        text = f.read()
    markers = [
        "EXTERNAL_DEMO_REVIEW_SHARE_PACKAGE_LOCK_READY",
        "PASS_WITH_COPY_ONLY_SHARE_PACKAGE_LOCK",
        "SHARE_SAFE_PACKAGE_INDEX_READY",
        "ROLE_BASED_EXTERNAL_REVIEWER_PACKETS_READY",
        "COPY_ONLY_SHARE_INSTRUCTIONS_READY",
        "REVIEWER_SAFE_DEMO_WALKTHROUGH_READY",
        "SHARE_READINESS_VALIDATION_PACKET_READY",
        "OPERATOR_REVIEW_ONLY",
        "SHARE_PACKAGE_LOCKED",
        "COPY_ONLY_SHARING",
        "PACKAGE_NOT_SENT",
        "NO_EMAIL_SENDING",
        "NO_REVIEWER_CONTACT",
        "NO_AUTOMATED_OUTREACH",
        "NO_DEPLOYMENT",
        "NO_RELEASE_EXECUTION",
        "NO_LIVE_WRITES",
        "NO_PUBLIC_WRITES",
        "NO_TOKEN_INPUT",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_REVIEWER_RESPONSE_CAPTURE_READINESS_LOCK",
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
print("Phase 6 — MVP-39 Product Reports")
reports = [
    "mvp39_external_demo_review_share_package_lock_report.md",
    "mvp39_share_safe_package_index_report.md",
    "mvp39_role_based_external_reviewer_packet_report.md",
    "mvp39_copy_only_share_instruction_report.md",
    "mvp39_reviewer_safe_demo_walkthrough_report.md",
    "mvp39_share_readiness_validation_packet_report.md",
    "mvp39_security_boundary_report.md",
    "mvp39_next_product_step_report.md",
    "mvp39_validator_quality_report.md",
    "mvp39_validator_wall_review.md",
]
for r in reports:
    check_file(f"09_exports/mvp_product_track/{r}", r)
print()

if FAILURES:
    print(f"FAILURES: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  {f}")
    sys.exit(1)

# MVP39_NO_EMAIL_SENDING_CHECK
# MVP39_NO_REVIEWER_CONTACT_CHECK
# MVP39_NO_AUTOMATED_OUTREACH_CHECK
print("MVP39_EXTERNAL_DEMO_REVIEW_SHARE_PACKAGE_LOCK_VALIDATION_PASS")
