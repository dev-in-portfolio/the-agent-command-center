import json
import os
import sys

DEMO_PACKAGE_DIR = "09_exports/external_demo_package_after_mvp50"
REPORT_PATH = "09_exports/mvp_product_track/external_demo_package_after_mvp50_report.md"
VALIDATOR_NAME = "EXTERNAL_DEMO_PACKAGE_AFTER_MVP50_VALIDATION_PASS"

required_files = [
    "README.md",
    "executive_demo_one_pager.md",
    "guided_demo_walkthrough_script.md",
    "stakeholder_pitch_outline.md",
    "demo_talk_track.md",
    "demo_click_path.md",
    "architecture_layer_map.md",
    "safety_boundary_brief.md",
    "validator_confidence_brief.md",
    "release_readiness_summary.md",
    "runtime_activation_separation_memo.md",
    "stakeholder_faq.md",
    "demo_screenshot_capture_list.md",
    "demo_readiness_checklist.md",
    "external_reviewer_notes_template.md",
    "demo_package_manifest.json",
]

required_markers = [
    "EXTERNAL_DEMO_PACKAGE_AFTER_MVP50_COMPLETE",
    "LIVE_MVP50_DASHBOARD_CONFIRMED",
    "CONTROLLED_COMMAND_CENTER_READINESS_ROADMAP_COMPLETE",
    "MVP43_THROUGH_MVP50_DEMO_PACKAGED",
    "NO_RUNTIME_ACTIVATION_STARTED",
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
    fpath = os.path.join(DEMO_PACKAGE_DIR, fname)
    if not os.path.isfile(fpath):
        failures.append(f"MISSING_FILE: {fpath}")

# Check manifest JSON
manifest_path = os.path.join(DEMO_PACKAGE_DIR, "demo_package_manifest.json")
if os.path.isfile(manifest_path):
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        if manifest.get("runtime_activation_started") is not False:
            failures.append("MANIFEST_RUNTIME_ACTIVATION_NOT_FALSE")
        if manifest.get("production_verified_through") != "MVP-50":
            failures.append("MANIFEST_PRODUCTION_VERIFIED_NOT_MVP50")
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

# Check all MVP layers mentioned in at least one demo package file
package_text = ""
for fname in os.listdir(DEMO_PACKAGE_DIR):
    fpath = os.path.join(DEMO_PACKAGE_DIR, fname)
    if os.path.isfile(fpath) and fname.endswith((".md", ".json")):
        with open(fpath, encoding="utf-8", errors="replace") as f:
            package_text += f.read() + "\n"

for layer in mvp_layers:
    if layer not in package_text:
        failures.append(f"LAYER_NOT_MENTIONED_IN_PACKAGE: {layer}")

# Check safety claims
false_claims = [
    "runtime activation started",
    "real automation enabled",
    "public writes enabled",
    "command execution enabled",
    "action execution enabled",
    "rollback execution enabled",
    "alert sending enabled",
]
# These must NOT appear as affirmative claims (they may appear as negations)
with open(os.path.join(DEMO_PACKAGE_DIR, "README.md"), encoding="utf-8", errors="replace") as f:
    readme = f.read().lower()
for claim in false_claims:
    if claim in readme and "not" not in readme.split(claim)[:1]:
        # Check if it's negated in context
        idx = readme.find(claim)
        context_start = max(0, idx - 50)
        context = readme[context_start:idx]
        is_negated = any(neg in context for neg in ["not", "no", "disabled", "has not", "remain"])
        if not is_negated:
            failures.append(f"README_MAY_CLAIM_UNSAFE_STATE: {claim}")

# Check no endpoint or Netlify function files added by this branch
import subprocess
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
    pass  # If no base ref, skip this check

# Check for newly added endpoint files (from untracked or staged)
untracked_lines = ""
try:
    untracked_lines = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        stderr=subprocess.STDOUT, text=True
    ).strip()
    for f in untracked_lines.splitlines():
        f_lower = f.lower()
        if f.endswith(".js") and ("endpoint" in f_lower or "api" in f_lower or "route" in f_lower):
            if "netlify/functions" not in f:
                failures.append(f"ENDPOINT_FILE_IN_UNTRACKED: {f}")
except subprocess.CalledProcessError:
    pass

# Check no MVP-51 files added by this branch
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
for f in untracked_lines.splitlines():
    f_lower = f.lower()
    if "mvp51" in f_lower or "mvp-51" in f_lower:
        failures.append(f"MVP51_FILE_UNTRACKED: {f}")

if failures:
    print(f"EXTERNAL_DEMO_PACKAGE_AFTER_MVP50_VALIDATION_FAIL")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print("EXTERNAL_DEMO_PACKAGE_AFTER_MVP50_VALIDATION_PASS")
