import json
import os
import subprocess
import sys

PRESENTATION_DIR = "09_exports/stakeholder_presentation_after_mvp50"
REPORT_PATH = "09_exports/mvp_product_track/stakeholder_presentation_after_mvp50_report.md"
VALIDATOR_NAME = "STAKEHOLDER_PRESENTATION_AFTER_MVP50_VALIDATION_PASS"

required_files = [
    "README.md",
    "presentation_outline_12_slides.md",
    "slide_by_slide_script.md",
    "presenter_notes.md",
    "screen_share_runbook.md",
    "executive_opening_statement.md",
    "plain_english_product_story.md",
    "technical_reviewer_appendix.md",
    "safety_and_non_activation_disclaimer.md",
    "demo_objection_responses.md",
    "post_demo_followup_email_template.md",
    "post_demo_review_questions.md",
    "demo_success_scorecard.md",
    "presentation_manifest.json",
]

required_markers = [
    "STAKEHOLDER_PRESENTATION_AFTER_MVP50_COMPLETE",
    "EXTERNAL_DEMO_PACKAGE_MERGED_TO_MASTER",
    "LIVE_MVP50_DASHBOARD_CONFIRMED",
    "TWELVE_SLIDE_PRESENTATION_OUTLINE_CREATED",
    "SLIDE_BY_SLIDE_SCRIPT_CREATED",
    "PRESENTER_NOTES_CREATED",
    "SCREEN_SHARE_RUNBOOK_CREATED",
    "EXECUTIVE_OPENING_STATEMENT_CREATED",
    "PLAIN_ENGLISH_PRODUCT_STORY_CREATED",
    "TECHNICAL_REVIEWER_APPENDIX_CREATED",
    "SAFETY_NON_ACTIVATION_DISCLAIMER_CREATED",
    "DEMO_OBJECTION_RESPONSES_CREATED",
    "POST_DEMO_FOLLOWUP_EMAIL_TEMPLATE_CREATED",
    "POST_DEMO_REVIEW_QUESTIONS_CREATED",
    "DEMO_SUCCESS_SCORECARD_CREATED",
    "PRESENTATION_MANIFEST_CREATED",
    "RUNTIME_ACTIVATION_NOT_STARTED",
    "NO_ENDPOINTS_ADDED",
    "NO_NETLIFY_FUNCTIONS_ADDED",
    "NO_PUBLIC_WRITES_ADDED",
    "NO_DATABASE_WRITES_ADDED",
    "NO_SUPABASE_WRITES_ADDED",
    "NO_COMMAND_EXECUTION_ADDED",
    "NO_ACTION_EXECUTION_ADDED",
    "NO_AUTOMATION_ADDED",
    "NO_MVP51_STARTED",
]

mvp_layers = [
    "MVP-43", "MVP-44", "MVP-45", "MVP-46",
    "MVP-47", "MVP-48", "MVP-49", "MVP-50",
]

failures = []

# Check all required files exist
for fname in required_files:
    fpath = os.path.join(PRESENTATION_DIR, fname)
    if not os.path.isfile(fpath):
        failures.append(f"MISSING_FILE: {fpath}")

# Check manifest JSON
manifest_path = os.path.join(PRESENTATION_DIR, "presentation_manifest.json")
if os.path.isfile(manifest_path):
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        if manifest.get("runtime_activation_started") is not False:
            failures.append("MANIFEST_RUNTIME_ACTIVATION_NOT_FALSE")
        if manifest.get("production_verified_through") != "MVP-50":
            failures.append("MANIFEST_PRODUCTION_VERIFIED_NOT_MVP50")
        if manifest.get("presentation_slide_count") != 12:
            failures.append(f"MANIFEST_SLIDE_COUNT_NOT_12: {manifest.get('presentation_slide_count')}")
        if not manifest.get("live_site"):
            failures.append("MANIFEST_MISSING_LIVE_SITE")
        for layer in mvp_layers:
            found = any(
                l.get("mvp") == layer and l.get("production_verified")
                for l in manifest.get("readiness_layers", [])
            )
            if not found:
                failures.append(f"MANIFEST_MISSING_LAYER: {layer}")
    except (json.JSONDecodeError, IOError) as e:
        failures.append(f"MANIFEST_PARSE_ERROR: {e}")
else:
    failures.append("MANIFEST_FILE_MISSING")

# Check report markers
if os.path.isfile(REPORT_PATH):
    with open(REPORT_PATH) as f:
        report_content = f.read()
    for marker in required_markers:
        if marker not in report_content:
            failures.append(f"MISSING_MARKER_IN_REPORT: {marker}")
else:
    failures.append(f"MISSING_REPORT: {REPORT_PATH}")

# Check slide outline has exactly 12 slides
outline_path = os.path.join(PRESENTATION_DIR, "presentation_outline_12_slides.md")
if os.path.isfile(outline_path):
    with open(outline_path) as f:
        outline = f.read()
    slide_count = outline.count("## Slide")
    if slide_count != 12:
        failures.append(f"SLIDE_OUTLINE_HAS_{slide_count}_SLIDES_EXPECTED_12")
else:
    failures.append("SLIDE_OUTLINE_MISSING")

# Check all 8 MVP layers mentioned
package_text = ""
for fname in os.listdir(PRESENTATION_DIR):
    fpath = os.path.join(PRESENTATION_DIR, fname)
    if os.path.isfile(fpath) and fname.endswith((".md", ".json")):
        with open(fpath, encoding="utf-8", errors="replace") as f:
            package_text += f.read() + "\n"
for layer in mvp_layers:
    if layer not in package_text:
        failures.append(f"LAYER_NOT_MENTIONED_IN_PACKAGE: {layer}")

# Check objection responses has at least 15 pairs
objections_path = os.path.join(PRESENTATION_DIR, "demo_objection_responses.md")
if os.path.isfile(objections_path):
    with open(objections_path) as f:
        objections = f.read()
    q_count = objections.count("## Q")
    a_count = objections.count("**A:**")
    if q_count < 15:
        failures.append(f"OBJECTIONS_ONLY_HAS_{q_count}_QUESTIONS_EXPECTED_15+")
else:
    failures.append("OBJECTIONS_FILE_MISSING")

# Check safety claims (must be negated in README)
false_claims = [
    "runtime activation started",
    "real automation enabled",
    "public writes enabled",
    "command execution enabled",
    "action execution enabled",
    "rollback execution enabled",
    "alert sending enabled",
]
with open(os.path.join(PRESENTATION_DIR, "README.md"), encoding="utf-8", errors="replace") as f:
    readme = f.read().lower()
for claim in false_claims:
    if claim in readme:
        idx = readme.find(claim)
        context_start = max(0, idx - 50)
        context = readme[context_start:idx]
        is_negated = any(neg in context for neg in ["not", "no", "disabled", "has not", "remain"])
        if not is_negated:
            failures.append(f"README_MAY_CLAIM_UNSAFE_STATE: {claim}")

# Check no Netlify function files or endpoint files added by this branch
base_ref = "origin/master"
try:
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", base_ref, "HEAD", "--", "netlify/functions/"],
        stderr=subprocess.STDOUT, text=True
    ).strip()
    if changed:
        for line in changed.splitlines():
            failures.append(f"NETLIFY_FUNCTION_FILE_ADDED_BY_BRANCH: {line}")
except subprocess.CalledProcessError:
    pass

try:
    changed_all = subprocess.check_output(
        ["git", "diff", "--name-only", base_ref, "HEAD"],
        stderr=subprocess.STDOUT, text=True
    ).strip()
    for f in changed_all.splitlines():
        f_lower = f.lower()
        if "mvp51" in f_lower or "mvp-51" in f_lower:
            failures.append(f"MVP51_FILE_ADDED: {f}")
except subprocess.CalledProcessError:
    pass

# Check no endpoint JS files in untracked
try:
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        stderr=subprocess.STDOUT, text=True
    ).strip()
    for f in untracked.splitlines():
        f_lower = f.lower()
        if f.endswith(".js") and ("endpoint" in f_lower or "api" in f_lower or "route" in f_lower):
            if "netlify/functions" not in f:
                failures.append(f"ENDPOINT_FILE_IN_UNTRACKED: {f}")
        if "mvp51" in f_lower or "mvp-51" in f_lower:
            failures.append(f"MVP51_FILE_UNTRACKED: {f}")
except subprocess.CalledProcessError:
    pass

if failures:
    print(f"STAKEHOLDER_PRESENTATION_AFTER_MVP50_VALIDATION_FAIL")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print("STAKEHOLDER_PRESENTATION_AFTER_MVP50_VALIDATION_PASS")
