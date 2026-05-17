#!/usr/bin/env python3
# MVP33_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

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
    MODELS / "product_launch_readiness_console_model.json",
    MODELS / "release_candidate_scorecard_model.json",
    MODELS / "final_pitch_packet_builder_model.json",
    MODELS / "stakeholder_pitch_variant_model.json",
    MODELS / "operator_launch_decision_panel_model.json",
    DIST / "mvp33_product_launch_readiness_final_pitch_packet_model.json",
]
for p in model_paths:
    check(p.exists(), f"missing model: {p.name}")

# MVP33_NO_WHOLE_FILE_SAFETY_LABEL_SKIP — each model checked individually, no whole-file skip

REQUIRED_TRUE_FIELDS = [
    "safe_launch_review_only",
    "no_fake_launch_status",
    "no_deploy_controls",
    "no_launch_automation",
]

REQUIRED_FALSE_FIELDS = [
    "service_role_used",
    "browser_direct_supabase_calls",
    "browser_persistence_enabled",
    "email_sending_enabled",
    "automation_enabled",
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
    check(data.get("mvp") == "33", f"{model_path.name}: mvp != 33")

    posture = data.get("posture")
    check(isinstance(posture, dict), f"{model_path.name}: posture missing or not an object")
    if not isinstance(posture, dict):
        continue

    # MVP33_NO_FAKE_LAUNCH_STATUS_CHECK
    for field in REQUIRED_TRUE_FIELDS:
        val = posture.get(field)
        check(val is True, f"{model_path.name}: posture.{field} is {val!r}, expected True")

    for field in REQUIRED_FALSE_FIELDS:
        val = posture.get(field)
        check(val is False, f"{model_path.name}: posture.{field} is {val!r}, expected False")

# -- Reports --
report_checks = [
    ("mvp33_product_launch_readiness_console_report.md", "PRODUCT_LAUNCH_READINESS_CONSOLE_READY"),
    ("mvp33_final_pitch_packet_report.md", "FINAL_PITCH_PACKET_READY"),
    ("mvp33_release_candidate_scorecard_report.md", "RELEASE_CANDIDATE_SCORECARD_READY"),
    ("mvp33_stakeholder_pitch_variants_report.md", "STAKEHOLDER_PITCH_VARIANTS_READY"),
    ("mvp33_operator_launch_decision_panel_report.md", "OPERATOR_LAUNCH_DECISION_PANEL_READY"),
    ("mvp33_safety_readiness_one_pager_report.md", "SAFETY_READINESS_ONE_PAGER_READY"),
    ("mvp33_security_boundary_report.md", "SECURITY_BOUNDARY_INTACT"),
    ("mvp33_next_product_step_report.md", "NEXT_STEP_REVIEW_FINAL_PITCH_PACKET_AND_PREPARE_RELEASE_CANDIDATE"),
    ("mvp33_validator_quality_report.md", "PASS_WITH_SAFE_LAUNCH_REVIEW_ONLY"),
    ("mvp33_acceptance_report.md", "PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET_READY"),
    ("mvp33_validator_wall_review.md", "MVP-33 Wall Coverage Added"),
]
for filename, marker in report_checks:
    path = REPORTS / filename
    check(path.exists(), f"missing report: {filename}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {filename} ({marker})")

# -- Release exports --
export_paths = [
    EXPORTS / "mvp33_final_pitch_packet.md",
    EXPORTS / "mvp33_launch_readiness_console_summary.md",
    EXPORTS / "mvp33_release_candidate_scorecard.md",
    EXPORTS / "mvp33_founder_pitch_variant.md",
    EXPORTS / "mvp33_recruiter_pitch_variant.md",
    EXPORTS / "mvp33_technical_reviewer_pitch_variant.md",
    EXPORTS / "mvp33_operator_demo_script.md",
    EXPORTS / "mvp33_safety_readiness_one_pager.md",
    EXPORTS / "mvp33_final_launch_review_packet.md",
    EXPORTS / "mvp33_final_pitch_manifest.json",
]
for fpath in export_paths:
    check(fpath.exists(), f"missing release export: {fpath.name}")

# MVP33_FINAL_PITCH_EXPORT_ARTIFACTS_CHECK
# MVP33_NO_DEPLOY_CONTROLS_CHECK
# MVP33_NO_LAUNCH_AUTOMATION_CHECK
# MVP33_NO_EMAIL_OR_OUTREACH_CHECK
DANGEROUS_EXPORT_CLAIMS = [
    "deployed",
    "launch automation enabled",
    "production launch complete",
    "emails sent",
    "outreach sent",
    "reviewer approved automatically",
    "fake live launch result",
    "service role is used",
    "deploy controls enabled",
]

ALLOWED_EXPORT_TERMS = [
    "launch review",
    "launch readiness",
    "final pitch",
    "not ready for real automation",
    "safe launch review only",
    "no fake launch status",
    "no deploy controls",
    "no launch automation",
]

for fpath in export_paths:
    if not fpath.exists():
        continue
    text = fpath.read_text(encoding="utf-8", errors="replace")
    for claim in DANGEROUS_EXPORT_CLAIMS:
        if claim in text.lower():
            check(False, f"{fpath.name} contains dangerous claim: '{claim}'")

# -- Manifest checks --
manifest_path = EXPORTS / "mvp33_final_pitch_manifest.json"
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        check(False, f"mvp33_final_pitch_manifest.json: invalid JSON ({e})")
        manifest = {}
    check(isinstance(manifest, dict), "mvp33_final_pitch_manifest.json: not a JSON object")
    check(manifest.get("mvp") == "33", "mvp33_final_pitch_manifest.json: mvp != 33")
    exports_list = manifest.get("exports", [])
    check(len(exports_list) > 0, "mvp33_final_pitch_manifest.json: empty exports list")
    for exp in exports_list:
        exp_path = ROOT / exp
        check(exp_path.exists(), f"mvp33_final_pitch_manifest.json: referenced export does not exist: {exp}")
    manifest_text = json.dumps(manifest).lower()
    for claim in DANGEROUS_EXPORT_CLAIMS:
        if claim in manifest_text:
            check(False, f"mvp33_final_pitch_manifest.json contains dangerous claim: '{claim}'")
    # Check no secrets/tokens/env in manifest (field names like service_role_used and _id are posture, not secrets)
    manifest_str = json.dumps(manifest)
    for suspect in ["ghp_", "gho_", "supabase_service_role", "service_role_key", "api_key=", "password=", "token="]:
        if suspect in manifest_str.lower():
            check(False, f"mvp33_final_pitch_manifest.json may contain secret: {suspect}")

# -- Dashboard markers --
for html_path in [DIST / "index.html", DIST / "print.html"]:
    check(html_path.exists(), f"missing {html_path.name}")
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        check("MVP-33" in html, f"{html_path.name} missing MVP-33")
        check("PRODUCT LAUNCH READINESS CONSOLE" in html, f"{html_path.name} missing PRODUCT LAUNCH READINESS CONSOLE")
        check("RELEASE CANDIDATE SCORECARD" in html, f"{html_path.name} missing RELEASE CANDIDATE SCORECARD")
        check("STAKEHOLDER PITCH VARIANTS" in html, f"{html_path.name} missing STAKEHOLDER PITCH VARIANTS")
        check("OPERATOR LAUNCH DECISION PANEL" in html, f"{html_path.name} missing OPERATOR LAUNCH DECISION PANEL")
        check("SAFE LAUNCH REVIEW ONLY" in html, f"{html_path.name} missing SAFE LAUNCH REVIEW ONLY")
        check("NO FAKE LAUNCH STATUS" in html, f"{html_path.name} missing NO FAKE LAUNCH STATUS")
        check("NO DEPLOY CONTROLS" in html, f"{html_path.name} missing NO DEPLOY CONTROLS")
        check("NOT_READY_FOR_REAL_AUTOMATION" in html, f"{html_path.name} missing NOT_READY_FOR_REAL_AUTOMATION")
        check("NEXT_STEP_REVIEW_FINAL_PITCH_PACKET_AND_PREPARE_RELEASE_CANDIDATE" in html, f"{html_path.name} missing next step marker")

# -- Dashboard runtime safety --
# MVP33_NO_DIRECT_SUPABASE_CHECK
# MVP33_NO_BROWSER_PERSISTENCE_CHECK
DANGEROUS_RUNTIME_PATTERNS = [
    'localStorage.setItem',
    'localStorage.getItem',
    'sessionStorage.setItem',
    'sessionStorage.getItem',
    'document.cookie =',
    'indexedDB.open',
    'createClient(',
    'supabase.createClient',
    'api.github.com',
    'api.netlify.com',
    'child_process',
    'execSync',
    'spawn(',
    'subprocess',
    'os.system',
]

for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for pattern in DANGEROUS_RUNTIME_PATTERNS:
            if pattern in text:
                check(False, f"{js_path.name} contains dangerous pattern: {pattern}")

# Also check for supabase.co fetch patterns in JS
SUPABASE_URL_PATTERNS = [
    'fetch("https://',
    "fetch('https://",
    'fetch(`https://',
    'axios.get("https://',
    "axios.get('https://",
    'axios.post("https://',
    "axios.post('https://",
    'XMLHttpRequest',
]
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for pattern in SUPABASE_URL_PATTERNS:
            if pattern in text:
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if pattern in line and "supabase.co" in line:
                        check(False, f"{js_path.name}:{i+1} direct supabase.co URL: {line.strip()[:80]}")

# -- Forbidden buttons/labels --
# MVP33_NO_FAKE_LAUNCH_STATUS_CHECK (additional)
FORBIDDEN_CONTROLS = [
    "Deploy",
    "Merge",
    "Push",
    "Create PR",
    "Launch",
    "Publish",
    "Execute",
    "Approve",
    "Apply Migration",
    "Enable Writes",
    "Send Email",
    "Email Reviewer",
    "Start Outreach",
    "Automate Launch",
    "Mark Launch Ready Automatically",
    "Save to Database",
    "Submit to Backend",
    "Submit to Supabase",
]

ALLOWED_BUTTON_PREFIXES = ["copy ", "load ", "phase ", "original +", "submit feedback packet manually"]

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
                break

# Also check JS for forbidden ID patterns
FORBIDDEN_BUTTON_IDS = [
    "mvp33-deploy",
    "mvp33-merge",
    "mvp33-push",
    "mvp33-create-pr",
    "mvp33-launch",
    "mvp33-publish",
    "mvp33-execute",
    "mvp33-approve",
    "mvp33-apply-migration",
    "mvp33-enable-writes",
    "mvp33-send-email",
    "mvp33-email-reviewer",
    "mvp33-start-outreach",
    "mvp33-automate-launch",
    "mvp33-mark-launch-ready",
    "mvp33-save-to-database",
    "mvp33-submit-to-backend",
    "mvp33-submit-to-supabase",
]
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for btn_id in FORBIDDEN_BUTTON_IDS:
            check(btn_id not in text, f"{js_path.name} contains forbidden button id: {btn_id}")

# -- JS init and copy bindings --
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        check("initMvp33" in text, f"{js_path.name} missing initMvp33")
        check("mvp33-copy-launch-readiness-console" in text, f"{js_path.name} missing copy button binding")
        check("mvp33-copy-scorecard" in text, f"{js_path.name} missing scorecard copy binding")
        check("mvp33-copy-pitch-packet" in text, f"{js_path.name} missing pitch packet copy binding")
        check("mvp33-copy-pitch-variants" in text, f"{js_path.name} missing pitch variants copy binding")
        check("mvp33-copy-decision-panel" in text, f"{js_path.name} missing decision panel copy binding")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("MVP33_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET_VALIDATION_PASS")
