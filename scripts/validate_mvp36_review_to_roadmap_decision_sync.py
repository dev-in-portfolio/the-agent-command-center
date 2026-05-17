#!/usr/bin/env python3
# MVP36_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

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
    "review_to_roadmap_decision_sync_model.json",
    "external_signal_priority_mapping_model.json",
    "roadmap_update_recommendation_model.json",
    "review_signal_request_draft_model.json",
    "decision_sync_audit_packet_model.json",
    "operator_roadmap_sync_review_model.json",
]
for name in MODEL_NAMES:
    path = MODELS / name
    check(path.exists(), f"missing model: {name}")
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        check(data.get("mvp") == "36", f"{name}: mvp != 36")
        posture = data.get("posture", {})
        for field in ["automatic_roadmap_updates_enabled", "automatic_request_creation_enabled",
                       "live_write_enabled", "public_write_enabled", "token_input_enabled",
                       "secrets_exposed", "service_role_used", "browser_direct_supabase_calls",
                       "browser_persistence_enabled", "email_sending_enabled",
                       "automated_outreach_enabled", "automation_enabled",
                       "deploy_controls_enabled", "launch_automation_enabled",
                       "update_enabled", "delete_enabled", "approve_enabled", "execute_enabled",
                       "deploy_merge_push_controls_enabled"]:
            val = posture.get(field)
            check(val is False, f"{name}: posture.{field} is {val!r}, expected False")

dist_model = DIST / "mvp36_review_to_roadmap_decision_sync_model.json"
check(dist_model.exists(), "missing dist model")
if dist_model.exists():
    data = json.loads(dist_model.read_text(encoding="utf-8", errors="replace"))
    check(data.get("mvp") == "36", "dist model: mvp != 36")

# MVP36_NO_AUTOMATIC_ROADMAP_UPDATES_CHECK
# MVP36_NO_AUTOMATIC_REQUEST_CREATION_CHECK
# MVP36_NO_LIVE_WRITES_CHECK
# MVP36_NO_PUBLIC_WRITES_CHECK
# MVP36_NO_TOKEN_INPUT_CHECK
# MVP36_NO_SECRETS_EXPOSED_CHECK
# MVP36_NO_SERVICE_ROLE_CHECK
# MVP36_NO_DEPLOY_CONTROLS_CHECK
# MVP36_NO_LAUNCH_AUTOMATION_CHECK
# MVP36_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK

# -- Reports --
report_checks = [
    ("mvp36_review_to_roadmap_decision_sync_report.md", "REVIEW_TO_ROADMAP_DECISION_SYNC_READY"),
    ("mvp36_external_signal_priority_mapping_report.md", "EXTERNAL_SIGNAL_PRIORITY_MAP_READY"),
    ("mvp36_roadmap_update_recommendation_report.md", "ROADMAP_UPDATE_RECOMMENDATIONS_READY"),
    ("mvp36_review_signal_request_draft_report.md", "REVIEW_SIGNAL_REQUEST_DRAFTS_READY"),
    ("mvp36_decision_sync_audit_packet_report.md", "DECISION_SYNC_AUDIT_PACKET_READY"),
    ("mvp36_operator_roadmap_sync_review_report.md", "OPERATOR_ROADMAP_SYNC_REVIEW_READY"),
    ("mvp36_security_boundary_report.md", "SECURITY_BOUNDARY_INTACT"),
    ("mvp36_next_product_step_report.md", "NEXT_STEP_BUILD_RELEASE_CANDIDATE_DECISION_LOG_AND_HANDOFF"),
    ("mvp36_validator_quality_report.md", "PASS_WITH_OPERATOR_REVIEW_ONLY_SYNC"),
    ("mvp36_acceptance_report.md", "REVIEW_TO_ROADMAP_DECISION_SYNC_READY"),
    ("mvp36_validator_wall_review.md", "MVP-36 Wall Coverage Added"),
]
for filename, marker in report_checks:
    path = REPORTS / filename
    check(path.exists(), f"missing report: {filename}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {filename} ({marker})")

# -- MVP36_REVIEW_TO_ROADMAP_EXPORT_ARTIFACTS_CHECK --
export_paths = [
    EXPORTS / "mvp36_review_to_roadmap_decision_sync.md",
    EXPORTS / "mvp36_external_signal_priority_map.md",
    EXPORTS / "mvp36_roadmap_update_recommendations.md",
    EXPORTS / "mvp36_review_signal_request_drafts.md",
    EXPORTS / "mvp36_decision_sync_audit_packet.md",
    EXPORTS / "mvp36_operator_roadmap_sync_review_packet.md",
    EXPORTS / "mvp36_review_to_roadmap_copy_bank.md",
    EXPORTS / "mvp36_review_to_roadmap_decision_manifest.json",
]
for fpath in export_paths:
    check(fpath.exists(), f"missing export: {fpath.name}")

# Check manifest
manifest_path = EXPORTS / "mvp36_review_to_roadmap_decision_manifest.json"
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        check(False, f"manifest invalid: {e}")
        manifest = {}
    check(isinstance(manifest, dict), "manifest not object")
    check(manifest.get("mvp") == "36", "manifest mvp != 36")
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
        check("MVP-36" in html, f"{html_path.name} missing MVP-36")
        check("REVIEW TO ROADMAP DECISION SYNC" in html, f"{html_path.name} missing REVIEW TO ROADMAP DECISION SYNC")
        check("EXTERNAL SIGNAL PRIORITY MAP" in html, f"{html_path.name} missing EXTERNAL SIGNAL PRIORITY MAP")
        check("ROADMAP UPDATE RECOMMENDATIONS" in html, f"{html_path.name} missing ROADMAP UPDATE RECOMMENDATIONS")
        check("REVIEW SIGNAL REQUEST DRAFTS" in html, f"{html_path.name} missing REVIEW SIGNAL REQUEST DRAFTS")
        check("DECISION SYNC AUDIT PACKET" in html, f"{html_path.name} missing DECISION SYNC AUDIT PACKET")
        check("OPERATOR ROADMAP SYNC REVIEW" in html, f"{html_path.name} missing OPERATOR ROADMAP SYNC REVIEW")
        check("REVIEW TO ROADMAP COPY BANK" in html, f"{html_path.name} missing REVIEW TO ROADMAP COPY BANK")
        check("OPERATOR REVIEW ONLY" in html, f"{html_path.name} missing OPERATOR REVIEW ONLY")
        check("NO AUTOMATIC ROADMAP UPDATES" in html, f"{html_path.name} missing NO AUTOMATIC ROADMAP UPDATES")
        check("NO AUTOMATIC REQUEST CREATION" in html, f"{html_path.name} missing NO AUTOMATIC REQUEST CREATION")
        check("NO LIVE WRITES" in html, f"{html_path.name} missing NO LIVE WRITES")
        check("NO PUBLIC WRITES" in html, f"{html_path.name} missing NO PUBLIC WRITES")
        check("NO TOKEN INPUT" in html, f"{html_path.name} missing NO TOKEN INPUT")
        check("NO SECRETS EXPOSED" in html, f"{html_path.name} missing NO SECRETS EXPOSED")
        check("SERVICE ROLE NOT USED" in html, f"{html_path.name} missing SERVICE ROLE NOT USED")
        check("UPDATE DELETE EXECUTE BLOCKED" in html, f"{html_path.name} missing UPDATE DELETE EXECUTE BLOCKED")
        check("AUTOMATION STILL DISABLED" in html, f"{html_path.name} missing AUTOMATION STILL DISABLED")
        check("NEXT_STEP_BUILD_RELEASE_CANDIDATE_DECISION_LOG_AND_HANDOFF" in html, f"{html_path.name} missing next step marker")
        check("NOT_READY_FOR_REAL_AUTOMATION" in html, f"{html_path.name} missing NOT_READY_FOR_REAL_AUTOMATION")

# -- MVP36_NO_BROWSER_PERSISTENCE_CHECK --
# -- MVP36_NO_DIRECT_SUPABASE_CHECK --
DANGEROUS_PATTERNS = [
    'localStorage.setItem', 'sessionStorage.setItem',
    'document.cookie =', 'indexedDB.open',
    'createClient(', 'supabase.createClient',
    'api.github.com', 'api.netlify.com',
]
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for pat in DANGEROUS_PATTERNS:
            if pat in text:
                check(False, f"{js_path.name} contains: {pat}")

# -- Forbidden controls --
FORBIDDEN_LABELS = [
    "Submit", "Save", "Send", "Sync", "Auto Sync",
    "Send Email", "Email Reviewer",
    "Start Outreach", "Automate Outreach", "Automate Review", "Contact Reviewer",
    "Update Roadmap", "Create Request", "Create Live Request", "Apply Recommendation",
    "Deploy", "Merge", "Push", "Create PR", "Launch", "Publish",
    "Execute", "Approve", "Apply Migration", "Enable Writes",
    "Token", "Login", "Connect Supabase",
]
ALLOWED_PREFIXES = ["copy ", "load ", "phase ", "original +", "mvp-", "use token", "clear token",
                     "submit feedback packet manually"]

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
        check("initMvp36" in text, f"{js_path.name} missing initMvp36")
        for binding in [
            "mvp36-copy-decision-sync", "mvp36-copy-signal-priority",
            "mvp36-copy-roadmap-recommendations", "mvp36-copy-request-drafts",
            "mvp36-copy-audit-packet", "mvp36-copy-operator-review",
            "mvp36-copy-copy-bank",
        ]:
            check(binding in text, f"{js_path.name} missing {binding}")

# MVP36_NO_EMAIL_OR_OUTREACH_CHECK
# MVP36_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("MVP36_REVIEW_TO_ROADMAP_DECISION_SYNC_VALIDATION_PASS")
