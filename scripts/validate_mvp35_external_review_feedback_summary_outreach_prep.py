#!/usr/bin/env python3
# MVP35_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

from pathlib import Path
import json
import sys
import re

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
REPORTS = ROOT / "09_exports" / "mvp_product_track"
EXPORTS = ROOT / "09_exports" / "release_package"
MODELS = ROOT / "14_backend" / "product_runtime" / "ui_models"

errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def file_contains(path, text):
    return path.exists() and text in path.read_text(encoding="utf-8", errors="replace")

# -- Model existence --
MODEL_NAMES = [
    "external_review_feedback_summary_model.json",
    "reviewer_response_matrix_model.json",
    "outreach_prep_workspace_model.json",
    "follow_up_response_packet_model.json",
    "external_reviewer_reply_guide_model.json",
    "operator_review_follow_up_decision_model.json",
]
for name in MODEL_NAMES:
    path = MODELS / name
    check(path.exists(), f"missing model: {name}")
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        check(data.get("mvp") == "35", f"{name}: mvp != 35")
        posture = data.get("posture", {})
        for field in ["email_sending_enabled", "automated_outreach_enabled", "contact_automation_enabled",
                       "public_write_enabled", "token_input_enabled", "secrets_exposed",
                       "service_role_used", "browser_direct_supabase_calls", "browser_persistence_enabled",
                       "automation_enabled", "deploy_controls_enabled", "launch_automation_enabled",
                       "update_enabled", "delete_enabled", "approve_enabled", "execute_enabled",
                       "deploy_merge_push_controls_enabled"]:
            val = posture.get(field)
            check(val is False, f"{name}: posture.{field} is {val!r}, expected False")

dist_model = DIST / "mvp35_external_review_feedback_summary_outreach_prep_model.json"
check(dist_model.exists(), "missing dist model")
if dist_model.exists():
    data = json.loads(dist_model.read_text(encoding="utf-8", errors="replace"))
    check(data.get("mvp") == "35", "dist model: mvp != 35")

# MVP35_NO_EMAIL_SENDING_CHECK
# MVP35_NO_AUTOMATED_OUTREACH_CHECK
# MVP35_NO_CONTACT_AUTOMATION_CHECK

# -- Reports --
report_checks = [
    ("mvp35_external_review_feedback_summary_report.md", "EXTERNAL_REVIEW_FEEDBACK_SUMMARY_READY"),
    ("mvp35_reviewer_response_matrix_report.md", "REVIEWER_RESPONSE_MATRIX_READY"),
    ("mvp35_outreach_prep_workspace_report.md", "OUTREACH_PREP_WORKSPACE_READY"),
    ("mvp35_follow_up_response_packet_report.md", "FOLLOW_UP_RESPONSE_PACKET_READY"),
    ("mvp35_external_reviewer_reply_guide_report.md", "EXTERNAL_REVIEWER_REPLY_GUIDE_READY"),
    ("mvp35_operator_follow_up_decision_report.md", "OPERATOR_FOLLOW_UP_DECISION_READY"),
    ("mvp35_security_boundary_report.md", "SECURITY_BOUNDARY_INTACT"),
    ("mvp35_next_product_step_report.md", "NEXT_STEP_BUILD_REVIEW_TO_ROADMAP_DECISION_SYNC"),
    ("mvp35_validator_quality_report.md", "PASS_WITH_COPY_ONLY_OUTREACH_PREP"),
    ("mvp35_acceptance_report.md", "EXTERNAL_REVIEW_FEEDBACK_SUMMARY_OUTREACH_PREP_READY"),
    ("mvp35_validator_wall_review.md", "MVP-35 Wall Coverage Added"),
]
for filename, marker in report_checks:
    path = REPORTS / filename
    check(path.exists(), f"missing report: {filename}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {filename} ({marker})")

# -- MVP35_EXTERNAL_REVIEW_EXPORT_ARTIFACTS_CHECK --
export_paths = [
    EXPORTS / "mvp35_external_review_feedback_summary.md",
    EXPORTS / "mvp35_reviewer_response_matrix.md",
    EXPORTS / "mvp35_feedback_themes_questions_objections.md",
    EXPORTS / "mvp35_outreach_prep_draft_workspace.md",
    EXPORTS / "mvp35_follow_up_response_packet.md",
    EXPORTS / "mvp35_external_reviewer_reply_guide.md",
    EXPORTS / "mvp35_operator_follow_up_decision_packet.md",
    EXPORTS / "mvp35_outreach_prep_copy_bank.md",
    EXPORTS / "mvp35_external_review_feedback_manifest.json",
]
for fpath in export_paths:
    check(fpath.exists(), f"missing export: {fpath.name}")

# Check manifest
manifest_path = EXPORTS / "mvp35_external_review_feedback_manifest.json"
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        check(False, f"manifest invalid: {e}")
        manifest = {}
    check(isinstance(manifest, dict), "manifest not object")
    check(manifest.get("mvp") == "35", "manifest mvp != 35")
    exports_list = manifest.get("exports", [])
    check(len(exports_list) > 0, "manifest empty")
    for exp in exports_list:
        exp_path = EXPORTS / exp
        check(exp_path.exists(), f"manifest export missing: {exp}")

# -- Dashboard markers --
for html_path in [DIST / "index.html", DIST / "print.html"]:
    check(html_path.exists(), f"missing {html_path.name}")
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        check("MVP-35" in html, f"{html_path.name} missing MVP-35")
        check("EXTERNAL REVIEW FEEDBACK SUMMARY" in html, f"{html_path.name} missing EXTERNAL REVIEW FEEDBACK SUMMARY")
        check("REVIEWER RESPONSE MATRIX" in html, f"{html_path.name} missing REVIEWER RESPONSE MATRIX")
        check("FEEDBACK THEMES" in html, f"{html_path.name} missing FEEDBACK THEMES")
        check("OUTREACH PREP WORKSPACE" in html, f"{html_path.name} missing OUTREACH PREP WORKSPACE")
        check("FOLLOW UP RESPONSE PACKET" in html, f"{html_path.name} missing FOLLOW UP RESPONSE PACKET")
        check("EXTERNAL REVIEWER REPLY GUIDE" in html, f"{html_path.name} missing EXTERNAL REVIEWER REPLY GUIDE")
        check("OPERATOR FOLLOW UP DECISION PANEL" in html, f"{html_path.name} missing OPERATOR FOLLOW UP DECISION")
        check("OUTREACH PREP COPY BANK" in html, f"{html_path.name} missing COPY BANK")
        check("COPY ONLY OUTREACH PREP" in html, f"{html_path.name} missing COPY ONLY OUTREACH PREP")
        check("NO EMAIL SENDING" in html, f"{html_path.name} missing NO EMAIL SENDING")
        check("NO AUTOMATED OUTREACH" in html, f"{html_path.name} missing NO AUTOMATED OUTREACH")
        check("NO CONTACT AUTOMATION" in html, f"{html_path.name} missing NO CONTACT AUTOMATION")
        check("NO PUBLIC WRITES" in html, f"{html_path.name} missing NO PUBLIC WRITES")
        check("NO TOKEN INPUT" in html, f"{html_path.name} missing NO TOKEN INPUT")
        check("NO SECRETS EXPOSED" in html, f"{html_path.name} missing NO SECRETS EXPOSED")
        check("SERVICE ROLE NOT USED" in html, f"{html_path.name} missing SERVICE ROLE NOT USED")
        check("UPDATE DELETE EXECUTE BLOCKED" in html, f"{html_path.name} missing UPDATE DELETE EXECUTE BLOCKED")
        check("AUTOMATION STILL DISABLED" in html, f"{html_path.name} missing AUTOMATION STILL DISABLED")
        check("NEXT_STEP_BUILD_REVIEW_TO_ROADMAP_DECISION_SYNC" in html, f"{html_path.name} missing next step marker")
        check("NOT_READY_FOR_REAL_AUTOMATION" in html, f"{html_path.name} missing NOT_READY_FOR_REAL_AUTOMATION")

# -- MVP35_NO_BROWSER_PERSISTENCE_CHECK --
# -- MVP35_NO_DIRECT_SUPABASE_CHECK --
DANGEROUS_PATTERNS = [
    'localStorage.setItem', 'sessionStorage.setItem',
    'document.cookie =', 'indexedDB.open',
    'createClient(', 'supabase.createClient',
    'api.github.com', 'api.netlify.com',
    'child_process', 'execSync', 'spawn(', 'subprocess.Popen', 'subprocess.call',
]
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for pat in DANGEROUS_PATTERNS:
            if pat in text:
                check(False, f"{js_path.name} contains: {pat}")

# -- Forbidden controls --
FORBIDDEN_LABELS = [
    "Submit", "Save", "Send", "Send Email", "Email Reviewer",
    "Start Outreach", "Automate Outreach", "Automate Review", "Contact Reviewer",
    "Deploy", "Merge", "Push", "Create PR", "Launch", "Publish",
    "Execute", "Approve", "Apply Migration", "Enable Writes",
    "Token", "Login", "Connect Supabase",
]
ALLOWED_PREFIXES = ["copy ", "load ", "phase ", "original +", "mvp-", "use token", "clear token", "submit feedback packet manually"]

for html_path in [DIST / "index.html", DIST / "print.html"]:
    if not html_path.exists():
        continue
    html = html_path.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r'<button[^>]*>([^<]+)</button>', html):
        tag = match.group(0)
        label = match.group(1).strip()
        if "disabled" in tag.lower():
            continue
        clean = label.lower()
        if any(clean.startswith(ap) for ap in ALLOWED_PREFIXES):
            continue
        for ctrl in FORBIDDEN_LABELS:
            if ctrl.lower() in clean:
                check(False, f"{html_path.name} has enabled button: '{label}'")

# -- JS init and copy bindings --
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        check("initMvp35" in text, f"{js_path.name} missing initMvp35")
        for binding in [
            "mvp35-copy-feedback-summary", "mvp35-copy-response-matrix",
            "mvp35-copy-themes", "mvp35-copy-outreach-draft",
            "mvp35-copy-response-packet", "mvp35-copy-reply-guide",
            "mvp35-copy-decision-packet", "mvp35-copy-copy-bank",
        ]:
            check(binding in text, f"{js_path.name} missing {binding}")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("MVP35_EXTERNAL_REVIEW_FEEDBACK_SUMMARY_OUTREACH_PREP_VALIDATION_PASS")
