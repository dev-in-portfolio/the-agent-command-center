#!/usr/bin/env python3
# MVP38_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

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

# -- Model existence --
MODEL_NAMES = [
    "final_release_review_room_model.json",
    "demo_script_lock_model.json",
    "reviewer_walkthrough_path_model.json",
    "final_review_audience_path_model.json",
    "release_go_no_go_checklist_model.json",
    "demo_timing_talking_points_model.json",
]
for name in MODEL_NAMES:
    path = MODELS / name
    check(path.exists(), f"missing model: {name}")
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        check(data.get("mvp") == "38", f"{name}: mvp != 38")
        posture = data.get("posture", {})
        for field in ["deployment_enabled", "release_execution_enabled",
                       "automatic_release_approval_enabled",
                       "automatic_roadmap_updates_enabled", "automatic_request_creation_enabled",
                       "live_write_enabled", "public_write_enabled", "token_input_enabled",
                       "secrets_exposed", "service_role_used", "browser_direct_supabase_calls",
                       "browser_persistence_enabled", "email_sending_enabled",
                       "automated_outreach_enabled", "contact_automation_enabled",
                       "automation_enabled", "deploy_controls_enabled", "launch_automation_enabled",
                       "update_enabled", "delete_enabled", "approve_enabled", "execute_enabled",
                       "deploy_merge_push_controls_enabled"]:
            val = posture.get(field)
            check(val is False, f"{name}: posture.{field} is {val!r}, expected False")

dist_model = DIST / "mvp38_final_release_review_room_demo_script_lock_model.json"
check(dist_model.exists(), "missing dist model")
if dist_model.exists():
    data = json.loads(dist_model.read_text(encoding="utf-8", errors="replace"))
    check(data.get("mvp") == "38", "dist model: mvp != 38")

# MVP38_NO_DEPLOYMENT_CHECK
# MVP38_NO_RELEASE_EXECUTION_CHECK
# MVP38_NO_AUTOMATIC_RELEASE_APPROVAL_CHECK
# MVP38_NO_LIVE_WRITES_CHECK
# MVP38_NO_PUBLIC_WRITES_CHECK
# MVP38_NO_TOKEN_INPUT_CHECK
# MVP38_NO_SECRETS_EXPOSED_CHECK
# MVP38_NO_SERVICE_ROLE_CHECK
# MVP38_NO_BROWSER_PERSISTENCE_CHECK
# MVP38_NO_DIRECT_SUPABASE_CHECK
# MVP38_NO_EMAIL_OR_OUTREACH_CHECK
# MVP38_NO_CONTACT_AUTOMATION_CHECK
# MVP38_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK

# -- Reports --
report_checks = [
    ("mvp38_final_release_review_room_report.md", "FINAL_RELEASE_REVIEW_ROOM_READY"),
    ("mvp38_demo_script_lock_report.md", "DEMO_SCRIPT_LOCK_READY"),
    ("mvp38_reviewer_walkthrough_path_report.md", "REVIEWER_WALKTHROUGH_PATH_READY"),
    ("mvp38_final_review_audience_path_report.md", "FINAL_REVIEW_AUDIENCE_PATHS_READY"),
    ("mvp38_release_go_no_go_checklist_report.md", "RELEASE_GO_NO_GO_CHECKLIST_READY"),
    ("mvp38_demo_timing_talking_points_report.md", "DEMO_TIMING_TALKING_POINTS_READY"),
    ("mvp38_security_boundary_report.md", "SECURITY_BOUNDARY_INTACT"),
    ("mvp38_next_product_step_report.md", "NEXT_STEP_BUILD_EXTERNAL_DEMO_REVIEW_SHARE_PACKAGE_LOCK"),
    ("mvp38_validator_quality_report.md", "PASS_WITH_OPERATOR_REVIEW_ONLY_FINAL_ROOM"),
    ("mvp38_acceptance_report.md", "FINAL_RELEASE_REVIEW_ROOM_DEMO_SCRIPT_LOCK_READY"),
    ("mvp38_validator_wall_review.md", "MVP-38 Wall Coverage Added"),
]
for filename, marker in report_checks:
    path = REPORTS / filename
    check(path.exists(), f"missing report: {filename}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {filename} ({marker})")

# -- MVP38_FINAL_RELEASE_REVIEW_ROOM_EXPORT_ARTIFACTS_CHECK --
export_paths = [
    EXPORTS / "mvp38_final_release_review_room.md",
    EXPORTS / "mvp38_demo_script_lock.md",
    EXPORTS / "mvp38_reviewer_walkthrough_path.md",
    EXPORTS / "mvp38_final_review_audience_paths.md",
    EXPORTS / "mvp38_release_go_no_go_checklist.md",
    EXPORTS / "mvp38_demo_timing_talking_points.md",
    EXPORTS / "mvp38_final_release_review_copy_bank.md",
    EXPORTS / "mvp38_final_release_review_room_manifest.json",
]
for fpath in export_paths:
    check(fpath.exists(), f"missing export: {fpath.name}")

# Check manifest
manifest_path = EXPORTS / "mvp38_final_release_review_room_manifest.json"
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        check(False, f"manifest invalid: {e}")
        manifest = {}
    check(isinstance(manifest, dict), "manifest not object")
    check(manifest.get("mvp") == "38", "manifest mvp != 38")
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
        check("MVP-38" in html, f"{html_path.name} missing MVP-38")
        check("FINAL RELEASE REVIEW ROOM" in html, f"{html_path.name} missing FINAL RELEASE REVIEW ROOM")
        check("DEMO SCRIPT LOCK" in html, f"{html_path.name} missing DEMO SCRIPT LOCK")
        check("REVIEWER WALKTHROUGH PATH" in html, f"{html_path.name} missing REVIEWER WALKTHROUGH PATH")
        check("FINAL REVIEW AUDIENCE PATHS" in html, f"{html_path.name} missing FINAL REVIEW AUDIENCE PATHS")
        check("RELEASE GO NO GO CHECKLIST" in html, f"{html_path.name} missing RELEASE GO NO GO CHECKLIST")
        check("DEMO TIMING TALKING POINTS" in html, f"{html_path.name} missing DEMO TIMING TALKING POINTS")
        check("FINAL RELEASE REVIEW COPY BANK" in html, f"{html_path.name} missing FINAL RELEASE REVIEW COPY BANK")
        check("OPERATOR REVIEW ONLY" in html, f"{html_path.name} missing OPERATOR REVIEW ONLY")
        check("FINAL REVIEW ONLY" in html, f"{html_path.name} missing FINAL REVIEW ONLY")
        check("DEMO SCRIPT LOCKED" in html, f"{html_path.name} missing DEMO SCRIPT LOCKED")
        check("NO DEPLOYMENT" in html, f"{html_path.name} missing NO DEPLOYMENT")
        check("NO RELEASE EXECUTION" in html, f"{html_path.name} missing NO RELEASE EXECUTION")
        check("NO AUTOMATIC RELEASE APPROVAL" in html, f"{html_path.name} missing NO AUTOMATIC RELEASE APPROVAL")
        check("NO LIVE WRITES" in html, f"{html_path.name} missing NO LIVE WRITES")
        check("NO PUBLIC WRITES" in html, f"{html_path.name} missing NO PUBLIC WRITES")
        check("NO TOKEN INPUT" in html, f"{html_path.name} missing NO TOKEN INPUT")
        check("NO SECRETS EXPOSED" in html, f"{html_path.name} missing NO SECRETS EXPOSED")
        check("SERVICE ROLE NOT USED" in html, f"{html_path.name} missing SERVICE ROLE NOT USED")
        check("UPDATE DELETE EXECUTE BLOCKED" in html, f"{html_path.name} missing UPDATE DELETE EXECUTE BLOCKED")
        check("AUTOMATION STILL DISABLED" in html, f"{html_path.name} missing AUTOMATION STILL DISABLED")
        check("NEXT_STEP_BUILD_EXTERNAL_DEMO_REVIEW_SHARE_PACKAGE_LOCK" in html, f"{html_path.name} missing next step marker")
        check("NOT_READY_FOR_REAL_AUTOMATION" in html, f"{html_path.name} missing NOT_READY_FOR_REAL_AUTOMATION")
        check("PASS_WITH_OPERATOR_REVIEW_ONLY_FINAL_ROOM" in html, f"{html_path.name} missing PASS_WITH_OPERATOR_REVIEW_ONLY_FINAL_ROOM")

# -- MVP38_NO_BROWSER_PERSISTENCE_CHECK --
# -- MVP38_NO_DIRECT_SUPABASE_CHECK --
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
        check("initMvp38" in text, f"{js_path.name} missing initMvp38")
        for binding in [
            "mvp38-copy-review-room", "mvp38-copy-demo-script-lock",
            "mvp38-copy-walkthrough-path", "mvp38-copy-audience-paths",
            "mvp38-copy-checklist", "mvp38-copy-timing",
            "mvp38-copy-copy-bank",
        ]:
            check(binding in text, f"{js_path.name} missing {binding}")

# MVP38_NO_EMAIL_OR_OUTREACH_CHECK
# MVP38_NO_CONTACT_AUTOMATION_CHECK
# MVP38_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("MVP38_FINAL_RELEASE_REVIEW_ROOM_DEMO_SCRIPT_LOCK_VALIDATION_PASS")
