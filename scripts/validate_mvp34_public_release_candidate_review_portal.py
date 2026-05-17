#!/usr/bin/env python3
# MVP34_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

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
model_paths = [
    MODELS / "public_release_candidate_review_portal_model.json",
    MODELS / "external_reviewer_path_model.json",
    MODELS / "investor_recruiter_review_room_model.json",
    MODELS / "public_safe_pitch_packet_view_model.json",
    MODELS / "release_candidate_review_instruction_model.json",
    DIST / "mvp34_public_release_candidate_review_portal_model.json",
]
for p in model_paths:
    check(p.exists(), f"missing model: {p.name}")

# MVP34_NO_WHOLE_FILE_SAFETY_LABEL_SKIP — each model checked individually

REQUIRED_FALSE_FIELDS = [
    "public_write_enabled",
    "token_input_enabled",
    "secrets_exposed",
    "service_role_used",
    "browser_direct_supabase_calls",
    "browser_persistence_enabled",
    "email_sending_enabled",
    "automation_enabled",
    "deploy_controls_enabled",
    "launch_automation_enabled",
    "update_enabled",
    "delete_enabled",
    "approve_enabled",
    "execute_enabled",
    "deploy_merge_push_controls_enabled",
]

for model_path in model_paths:
    if not model_path.exists():
        continue
    data = json.loads(model_path.read_text(encoding="utf-8", errors="replace"))
    check(isinstance(data, dict), f"{model_path.name}: not a JSON object")
    check(data.get("mvp") == "34", f"{model_path.name}: mvp != 34")

    posture = data.get("posture")
    check(isinstance(posture, dict), f"{model_path.name}: posture missing or not an object")
    if not isinstance(posture, dict):
        continue

    # MVP34_NO_PUBLIC_WRITES_CHECK
    # MVP34_NO_TOKEN_INPUT_CHECK
    # MVP34_NO_SECRETS_CHECK
    for field in REQUIRED_FALSE_FIELDS:
        val = posture.get(field)
        check(val is False, f"{model_path.name}: posture.{field} is {val!r}, expected False")

# -- Reports --
report_checks = [
    ("mvp34_public_release_candidate_review_portal_report.md", "PUBLIC_RELEASE_CANDIDATE_REVIEW_PORTAL_READY"),
    ("mvp34_investor_recruiter_review_room_report.md", "INVESTOR_RECRUITER_REVIEW_ROOM_READY"),
    ("mvp34_external_reviewer_paths_report.md", "EXTERNAL_REVIEWER_PATHS_READY"),
    ("mvp34_public_safe_pitch_packet_report.md", "PUBLIC_SAFE_PITCH_PACKET_READY"),
    ("mvp34_release_candidate_artifact_index_report.md", "RELEASE_CANDIDATE_ARTIFACT_INDEX_READY"),
    ("mvp34_review_instruction_packet_report.md", "EXTERNAL_REVIEW_INSTRUCTIONS_READY"),
    ("mvp34_security_boundary_report.md", "SECURITY_BOUNDARY_INTACT"),
    ("mvp34_next_product_step_report.md", "NEXT_STEP_BUILD_EXTERNAL_REVIEW_FEEDBACK_SUMMARY_AND_OUTREACH_PREP"),
    ("mvp34_validator_quality_report.md", "PASS_WITH_PUBLIC_SAFE_REVIEW_ROOM"),
    ("mvp34_acceptance_report.md", "PUBLIC_RELEASE_CANDIDATE_REVIEW_PORTAL_READY"),
    ("mvp34_validator_wall_review.md", "MVP-34 Wall Coverage Added"),
]
for filename, marker in report_checks:
    path = REPORTS / filename
    check(path.exists(), f"missing report: {filename}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {filename} ({marker})")

# -- MVP34_PUBLIC_RELEASE_EXPORT_ARTIFACTS_CHECK --
export_paths = [
    EXPORTS / "mvp34_public_release_candidate_review_portal.md",
    EXPORTS / "mvp34_investor_review_path.md",
    EXPORTS / "mvp34_recruiter_review_path.md",
    EXPORTS / "mvp34_founder_operator_review_path.md",
    EXPORTS / "mvp34_public_safe_pitch_packet.md",
    EXPORTS / "mvp34_release_candidate_artifact_index.md",
    EXPORTS / "mvp34_public_safe_demo_script.md",
    EXPORTS / "mvp34_review_questions_prep_guide.md",
    EXPORTS / "mvp34_external_review_instruction_packet.md",
    EXPORTS / "mvp34_public_release_candidate_manifest.json",
]
for fpath in export_paths:
    check(fpath.exists(), f"missing release export: {fpath.name}")

# Check manifest
manifest_path = EXPORTS / "mvp34_public_release_candidate_manifest.json"
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        check(False, f"manifest invalid JSON: {e}")
        manifest = {}
    check(isinstance(manifest, dict), "manifest not object")
    check(manifest.get("mvp") == "34", "manifest mvp != 34")
    exports_list = manifest.get("exports", [])
    check(len(exports_list) > 0, "manifest empty exports")
    for exp in exports_list:
        exp_path = EXPORTS / exp
        check(exp_path.exists(), f"manifest export missing: {exp}")
    manifest_str = json.dumps(manifest).lower()
    for bad in ["ghp_", "gho_", "supabase_service_role", "service_role_key"]:
        if bad in manifest_str:
            check(False, f"manifest contains {bad}")

# -- Dashboard markers --
for html_path in [DIST / "index.html", DIST / "print.html"]:
    check(html_path.exists(), f"missing {html_path.name}")
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        check("MVP-34" in html, f"{html_path.name} missing MVP-34")
        check("PUBLIC RELEASE CANDIDATE REVIEW PORTAL" in html, f"{html_path.name} missing PUBLIC RELEASE CANDIDATE REVIEW PORTAL")
        check("INVESTOR RECRUITER REVIEW ROOM" in html, f"{html_path.name} missing INVESTOR RECRUITER REVIEW ROOM")
        check("EXTERNAL REVIEWER PATHS" in html, f"{html_path.name} missing EXTERNAL REVIEWER PATHS")
        check("PUBLIC SAFE PITCH PACKET" in html, f"{html_path.name} missing PUBLIC SAFE PITCH PACKET")
        check("RELEASE CANDIDATE ARTIFACT INDEX" in html, f"{html_path.name} missing RELEASE CANDIDATE ARTIFACT INDEX")
        check("PUBLIC SAFE DEMO SCRIPT" in html, f"{html_path.name} missing PUBLIC SAFE DEMO SCRIPT")
        check("REVIEW QUESTIONS PREP GUIDE" in html, f"{html_path.name} missing REVIEW QUESTIONS PREP GUIDE")
        check("EXTERNAL REVIEW INSTRUCTIONS" in html, f"{html_path.name} missing EXTERNAL REVIEW INSTRUCTIONS")
        check("NO PUBLIC WRITES" in html, f"{html_path.name} missing NO PUBLIC WRITES")
        check("NO TOKEN INPUT" in html, f"{html_path.name} missing NO TOKEN INPUT")
        check("NO SECRETS EXPOSED" in html, f"{html_path.name} missing NO SECRETS EXPOSED")
        check("NO DEPLOY CONTROLS" in html, f"{html_path.name} missing NO DEPLOY CONTROLS")
        check("NOT_READY_FOR_REAL_AUTOMATION" in html, f"{html_path.name} missing NOT_READY_FOR_REAL_AUTOMATION")
        check("NEXT_STEP_BUILD_EXTERNAL_REVIEW_FEEDBACK_SUMMARY_AND_OUTREACH_PREP" in html, f"{html_path.name} missing next step marker")

# -- MVP34_NO_BROWSER_PERSISTENCE_CHECK --
# -- MVP34_NO_DIRECT_SUPABASE_CHECK --
DANGEROUS_RUNTIME_PATTERNS = [
    'localStorage.setItem', 'localStorage.getItem',
    'sessionStorage.setItem', 'sessionStorage.getItem',
    'document.cookie =', 'indexedDB.open',
    'createClient(', 'supabase.createClient',
    'api.github.com', 'api.netlify.com',
    'child_process', 'execSync', 'spawn(', 'subprocess', 'os.system',
]
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for pat in DANGEROUS_RUNTIME_PATTERNS:
            if pat in text:
                check(False, f"{js_path.name} contains: {pat}")
        for pat in ['fetch("https://', "fetch('https://", 'fetch(`https://']:
            if pat in text:
                for i, line in enumerate(text.splitlines()):
                    if pat in line and "supabase.co" in line:
                        check(False, f"{js_path.name}:{i+1} direct supabase URL")

# -- MVP34_NO_EMAIL_OR_OUTREACH_CHECK --
# -- MVP34_NO_DEPLOY_CONTROLS_CHECK --
# -- MVP34_NO_LAUNCH_AUTOMATION_CHECK --
FORBIDDEN_CONTROLS = [
    "Deploy", "Merge", "Push", "Create PR", "Launch", "Publish",
    "Execute", "Approve", "Apply Migration", "Enable Writes",
    "Send Email", "Email Reviewer", "Start Outreach", "Automate Review",
    "Token", "Login", "Connect Supabase",
    "Save to Database", "Submit to Backend", "Submit to Supabase",
]
ALLOWED_BUTTON_PREFIXES = ["copy ", "load ", "phase ", "original +", "submit feedback packet manually", "mvp-", "use token", "clear token"]

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
        if any(clean.startswith(ap) for ap in ALLOWED_BUTTON_PREFIXES):
            continue
        for ctrl in FORBIDDEN_CONTROLS:
            if ctrl.lower() in clean:
                check(False, f"{html_path.name} has enabled button: '{label}'")

# -- JS init and copy bindings --
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        check("initMvp34" in text, f"{js_path.name} missing initMvp34")
        for binding in [
            "mvp34-copy-portal", "mvp34-copy-investor-path",
            "mvp34-copy-recruiter-path", "mvp34-copy-founder-path",
            "mvp34-copy-pitch-packet", "mvp34-copy-artifact-index",
            "mvp34-copy-demo-script", "mvp34-copy-review-questions",
            "mvp34-copy-review-instructions",
        ]:
            check(binding in text, f"{js_path.name} missing {binding}")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("MVP34_PUBLIC_RELEASE_CANDIDATE_REVIEW_PORTAL_VALIDATION_PASS")
