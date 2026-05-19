#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "13_web_dashboard" / "dist" / "demo"
REPORT = ROOT / "09_exports" / "mvp_product_track" / "premium_demo_experience_after_mvp50_report.md"
INDEX = ROOT / "13_web_dashboard" / "dist" / "index.html"
VALIDATOR_NAME = "PREMIUM_DEMO_EXPERIENCE_AFTER_MVP50_VALIDATION_PASS"

required_files = [
    "index.html",
    "presentation.html",
    "system-story.html",
    "system-scale.html",
    "agent-hierarchy.html",
    "operating-model.html",
    "validator-safety-map.html",
    "safety-boundaries.html",
    "technical-appendix.html",
    "objections.html",
    "review.html",
    "demo-package.json",
    "assets/demo.css",
    "assets/demo.js",
]

required_source_docs = [
    ROOT / "09_exports" / "stakeholder_presentation_after_mvp50" / "system_story.md",
    ROOT / "09_exports" / "stakeholder_presentation_after_mvp50" / "system_scale_inventory.md",
    ROOT / "09_exports" / "stakeholder_presentation_after_mvp50" / "agent_department_hierarchy.md",
    ROOT / "09_exports" / "stakeholder_presentation_after_mvp50" / "command_center_operating_model.md",
    ROOT / "09_exports" / "stakeholder_presentation_after_mvp50" / "validator_and_safety_gate_map.md",
]

required_report_markers = [
    "PREMIUM_DEMO_EXPERIENCE_AFTER_MVP50_COMPLETE",
    "MARKDOWN_ONLY_DEMO_REPLACED_WITH_PREMIUM_BROWSER_DEMO",
    "PREMIUM_DEMO_HUB_CREATED_UNDER_DIST",
    "PREMIUM_DEMO_LINK_ADDED_TO_MAIN_DASHBOARD",
    "SYSTEM_STORY_INCLUDED",
    "SYSTEM_SCALE_INCLUDED",
    "AGENT_DEPARTMENT_HIERARCHY_INCLUDED",
    "COMMAND_CENTER_OPERATING_MODEL_INCLUDED",
    "VALIDATOR_SAFETY_GATE_MAP_INCLUDED",
    "STAKEHOLDER_PRESENTATION_RENDERED_AS_HTML",
    "OBJECTION_RESPONSES_RENDERED_AS_HTML",
    "REVIEW_SCORECARD_RENDERED_AS_HTML",
    "SYSTEM_SCALE_DISCOVERY_COMPLETED",
    "NO_UNVERIFIED_AGENT_COUNT_CLAIMED",
    "NO_UNVERIFIED_DEPARTMENT_COUNT_CLAIMED",
    "PRODUCTION_VERIFIED_THROUGH_MVP50",
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
    "SYSTEM_STORY_INCLUDED_IN_DEMO_PACKAGE",
    "SYSTEM_SCALE_INCLUDED_IN_DEMO_PACKAGE",
    "AGENT_DEPARTMENT_HIERARCHY_INCLUDED_IN_DEMO_PACKAGE",
    "COMMAND_CENTER_OPERATING_MODEL_INCLUDED_IN_DEMO_PACKAGE",
    "VALIDATOR_SAFETY_GATE_MAP_INCLUDED_IN_DEMO_PACKAGE",
    "SYSTEM_STORY_VIEWABLE_IN_DEMO_HUB",
    "SYSTEM_SCALE_VIEWABLE_IN_DEMO_HUB",
    "AGENT_HIERARCHY_VIEWABLE_IN_DEMO_HUB",
    "OPERATING_MODEL_VIEWABLE_IN_DEMO_HUB",
    "VALIDATOR_SAFETY_MAP_VIEWABLE_IN_DEMO_HUB",
]

failures = []

for rel in required_files:
    if not (DEMO / rel).is_file():
        failures.append(f"MISSING_FILE: 13_web_dashboard/dist/demo/{rel}")

for doc in required_source_docs:
    if not doc.is_file():
        failures.append(f"MISSING_SOURCE_DOC: {doc.relative_to(ROOT)}")

try:
    package = json.loads((DEMO / "demo-package.json").read_text(encoding="utf-8"))
    if package.get("runtime_activation_started") is not False:
        failures.append("DEMO_PACKAGE_RUNTIME_NOT_FALSE")
    if package.get("production_verified_through") != "MVP-50":
        failures.append("DEMO_PACKAGE_NOT_MVP50")
except Exception as exc:
    failures.append(f"DEMO_PACKAGE_PARSE_ERROR: {exc}")

index_text = INDEX.read_text(encoding="utf-8", errors="replace")
if "Premium Stakeholder Demo" not in index_text:
    failures.append("MISSING_DASHBOARD_LINK_LABEL")
if "/demo/" not in index_text:
    failures.append("MISSING_DASHBOARD_DEMO_PATH")

demo_index = (DEMO / "index.html").read_text(encoding="utf-8", errors="replace")
for required in [
    "Stakeholder Demo Hub",
    "Production verified through MVP-50",
    "NOT_READY_FOR_REAL_AUTOMATION",
    "System Story",
    "System Scale",
    "Agent / Department Hierarchy",
    "Operating Model",
    "Validator and Safety Gate Map",
]:
    if required not in demo_index:
        failures.append(f"INDEX_MISSING: {required}")

presentation_text = (DEMO / "presentation.html").read_text(encoding="utf-8", errors="replace")
slide_count = presentation_text.count('<section class="slide')
if slide_count != 12:
    failures.append(f"PRESENTATION_SLIDE_COUNT_{slide_count}_EXPECTED_12")

objections_text = (DEMO / "objections.html").read_text(encoding="utf-8", errors="replace")
if objections_text.count('class="qa-item"') < 20:
    failures.append("OBJECTIONS_LT_20")

scale_text = (DEMO / "system-scale.html").read_text(encoding="utf-8", errors="replace")
if "UNKNOWN_NOT_CURRENTLY_DECLARED" not in scale_text:
    failures.append("SYSTEM_SCALE_MISSING_UNKNOWN_LABEL")
if "agent count" in scale_text.lower() and "unknown_not_currently_declared" not in scale_text.lower():
    failures.append("AGENT_COUNT_MUST_USE_UNKNOWN_LABEL")
if "department count" in scale_text.lower() and "unknown_not_currently_declared" not in scale_text.lower():
    failures.append("DEPARTMENT_COUNT_MUST_USE_UNKNOWN_LABEL")

safety_text = (DEMO / "safety-boundaries.html").read_text(encoding="utf-8", errors="replace")
for disabled in [
    "no runtime activation",
    "no command execution",
    "no action execution",
    "no public writes",
    "no database or Supabase writes",
    "no alert sending",
    "no rollback execution",
    "no incident mutation",
    "no deploy / merge / push controls in app",
    "no automation",
    "no endpoints",
    "no Netlify functions",
]:
    if disabled.lower() not in safety_text.lower():
        failures.append(f"SAFETY_MISSING: {disabled}")

report_text = REPORT.read_text(encoding="utf-8", errors="replace")
for marker in required_report_markers:
    if marker not in report_text:
        failures.append(f"REPORT_MISSING_MARKER: {marker}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "origin/master", "HEAD"],
    cwd=ROOT,
    text=True,
).splitlines()

allowed_prefixes = [
    "13_web_dashboard/dashboard_renderer.py",
    "13_web_dashboard/dist/index.html",
    "13_web_dashboard/dist/demo/",
    "09_exports/mvp_product_track/premium_demo_system_scale_discovery_report.md",
    "09_exports/mvp_product_track/premium_demo_experience_after_mvp50_report.md",
    "09_exports/mvp_product_track/live_site_demo_rendering_rescue_after_mvp50_report.md",
    "scripts/validate_premium_demo_experience_after_mvp50.py",
    "scripts/validate_live_site_demo_rendering_rescue_after_mvp50.py",
    "09_exports/stakeholder_presentation_after_mvp50/",
    "scripts/validate_phase5_plus1_master_validator_wall.py",
]

for path in changed:
    lower = path.lower()
    if "mvp51" in lower or "mvp-51" in lower:
        failures.append(f"MVP51_FILE_ADDED: {path}")
    if path.startswith(("netlify/functions/", "api/", ".env", "supabase/.temp")):
        failures.append(f"FORBIDDEN_PATH: {path}")
    if not any(path.startswith(prefix) for prefix in allowed_prefixes):
        failures.append(f"UNEXPECTED_CHANGED_PATH: {path}")

if "runtime activation" in demo_index.lower() and "not started" not in demo_index.lower():
    failures.append("UNSAFE_RUNTIME_LANGUAGE")

if failures:
    print("PREMIUM_DEMO_EXPERIENCE_AFTER_MVP50_VALIDATION_FAIL")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)

print(VALIDATOR_NAME)
