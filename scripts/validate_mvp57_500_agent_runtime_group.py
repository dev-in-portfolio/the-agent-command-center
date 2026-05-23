
#!/usr/bin/env python3
"""Validate the MVP-57 500-agent runtime group pass."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp57_500_agent_runtime_group.sql",
    ROOT / "netlify" / "functions" / "_shared" / "runtime_group_helpers.js",
    ROOT / "netlify" / "functions" / "list-runtime-group.js",
    ROOT / "netlify" / "functions" / "activate-runtime-group.js",
    ROOT / "netlify" / "functions" / "deactivate-runtime-group.js",
    ROOT / "netlify" / "functions" / "activate-group-lane.js",
    ROOT / "netlify" / "functions" / "deactivate-group-lane.js",
    ROOT / "netlify" / "functions" / "group-heartbeat.js",
    ROOT / "netlify" / "functions" / "create-group-readiness-note.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-group.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-group.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp57_500_agent_runtime_group_report.md",
]

migration_required = [
    "runtime_group_lanes",
    "runtime_group_agents",
    "runtime_group_activation_events",
    "group_heartbeat_events",
    "group_readiness_notes",
    "runtime_group_audit_events",
    "runtime_group_size",
    "max_activation_batch_size",
    "mvp57_group_agent_001",
    "mvp57_group_agent_500",
    "intake_lane_01",
    "reporting_lane_05",
    "activate_all is blocked",
    "batch_size exceeds 500",
    "GROUP_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENT_BLOCKED",
    "NON_GROUP_AGENT_BLOCKED",
    "GROUP_HEARTBEAT",
    "GROUP_READINESS_NOTE_CREATED",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_group_agents",
    "runtime_group_lanes",
    "runtime_group_activation_events",
    "group_heartbeat_events",
    "group_readiness_notes",
    "runtime_group_audit_events",
    "runtime_group_activate_agents",
    "runtime_group_deactivate_agents",
    "runtime_group_activate_lane",
    "runtime_group_deactivate_lane",
    "runtime_group_record_heartbeat",
    "runtime_group_create_readiness_note",
    "activate_all",
    "batch_size exceeds 500",
    "UNKNOWN_AGENT_BLOCKED",
    "NON_GROUP_AGENT_BLOCKED",
    "GROUP_ACTIVATION_BLOCKED",
    "GROUP_DEACTIVATION_BLOCKED",
    "GROUP_HEARTBEAT",
    "GROUP_READINESS_NOTE_CREATED",
]

ui_required = [
    "500-Agent Runtime Group",
    "MVP-57 500-Agent Runtime Group",
    "Runtime group size: 500",
    "Live runtime agents enabled: 0–500",
    "Activation beyond 500: blocked",
    "Full 47,979 activation: blocked",
    "Activate full 500-agent group",
    "Deactivate full group",
    "Activate one lane",
    "Deactivate one lane",
    "Activate individual agent",
    "Deactivate individual agent",
    "Send group heartbeat",
    "Send lane heartbeat",
    "Create readiness note",
    "Group health",
    "Lane health",
    "Heartbeat count",
    "Readiness note count",
    "Audit Timeline",
    "Kill switch",
    "Total registered agents: 47,979",
    "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.",
    "Open 500-Agent Runtime Group",
]

report_required = [
    "MVP57_500_AGENT_RUNTIME_GROUP_COMPLETE",
    "FIVE_HUNDRED_APPROVED_AGENTS_CREATED",
    "FIFTY_AGENT_LANES_CREATED",
    "TEN_AGENTS_PER_LANE",
    "MAX_BATCH_SIZE_500",
    "FULL_47979_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENTS_BLOCKED",
    "NON_GROUP_AGENTS_BLOCKED",
    "HEARTBEAT_FUNCTION_ADDED",
    "READINESS_NOTE_FUNCTION_ADDED",
    "LANE_ACTIVATION_ADDED",
    "GROUP_HEALTH_ROLLUP_ADDED",
    "AUDIT_EVENTS_ADDED",
    "KILL_SWITCH_VISIBLE",
    "SERVICE_ROLE_SERVER_SIDE_ONLY",
    "NO_COMMAND_EXECUTION_ADDED",
    "NO_DEPLOY_EXECUTION_ADDED",
    "NO_ROLLBACK_EXECUTION_ADDED",
    "NO_ALERT_SENDING_ADDED",
    "NO_ARBITRARY_SQL_ENDPOINT_ADDED",
    "NO_ARBITRARY_COMMAND_ENDPOINT_ADDED",
]

browser_js_required = [
    "/.netlify/functions/list-runtime-group",
    "/.netlify/functions/activate-runtime-group",
    "/.netlify/functions/deactivate-runtime-group",
    "/.netlify/functions/activate-group-lane",
    "/.netlify/functions/deactivate-group-lane",
    "/.netlify/functions/group-heartbeat",
    "/.netlify/functions/create-group-readiness-note",
]

browser_js_forbidden = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "indexedDB",
    "child_process",
    "exec(",
    "spawn(",
    "eval(",
    "new Function",
]


def fail(message: str) -> None:
    print("MVP57_500_AGENT_RUNTIME_GROUP_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


prereq = subprocess.run(
    ["python3", str(ROOT / "scripts" / "validate_mvp56_250_agent_runtime_company.py")],
    capture_output=True,
    text=True,
)
require(
    prereq.returncode == 0 and "MVP56_250_AGENT_RUNTIME_COMPANY_VALIDATION_PASS" in prereq.stdout,
    "MVP-56 prerequisite validator did not pass.",
)

for path in required_files:
    require(path.exists(), f"Missing required file: {path.relative_to(ROOT)}")

migration_text = read(required_files[0])
for needle in migration_required:
    require(needle in migration_text, f"Migration missing required string: {needle}")

function_text = "\\n".join(read(path) for path in required_files[1:9])
for needle in function_required:
    require(needle in function_text, f"Function layer missing required string: {needle}")

ui_text = read(required_files[9]) + "\\n" + read(required_files[10]) + "\\n" + read(required_files[11]) + "\\n" + read(required_files[12])
for needle in ui_required:
    require(needle in ui_text, f"Runtime group UI missing required string: {needle}")

page_text = read(required_files[9])
require('<header class="demo-topbar collapsible-topbar" data-collapsible-menu>' in page_text, "Runtime group page missing collapsible menu header.")
require('data-action="toggle-menu"' in page_text, "Runtime group page missing toggle menu button.")
require('aria-expanded="false"' in page_text, "Runtime group page missing collapsed aria state.")
require('data-menu-panel' in page_text, "Runtime group page missing menu panel.")
require('hidden' in page_text, "Runtime group page missing hidden menu panel marker.")
require('<nav class="nav-links"' not in page_text, "Runtime group page still contains an always-visible nav row.")
require("Runtime Group" in page_text, "Runtime group breadcrumb/title missing.")
require("Demo Hub" in page_text, "Runtime group breadcrumb missing Demo Hub.")
require("Home" in page_text, "Runtime group breadcrumb missing Home.")

report_text = read(required_files[13])
for needle in report_required:
    require(needle in report_text, f"Report missing required marker: {needle}")

js_text = read(required_files[10])
for needle in browser_js_required:
    require(needle in js_text, f"Browser JS missing required endpoint: {needle}")
for needle in browser_js_forbidden:
    require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

require("activate_all" in function_text, "Server-side functions should explicitly block activate_all.")
require("batch_size exceeds 500" in function_text or "> 500" in function_text, "Server-side functions should explicitly block batch sizes above 500.")
require("UNKNOWN_AGENT_BLOCKED" in function_text, "Server-side functions should block unknown agent IDs.")
require("NON_GROUP_AGENT_BLOCKED" in function_text, "Server-side functions should block non-group agent IDs.")
require("GROUP_ACTIVATION_BLOCKED" in function_text, "Server-side functions should block group activation overreach.")
require("GROUP_DEACTIVATION_BLOCKED" in function_text, "Server-side functions should block group deactivation overreach.")
require("GROUP_HEARTBEAT" in function_text, "Heartbeat audit event missing.")
require("GROUP_READINESS_NOTE_CREATED" in function_text, "Readiness note audit event missing.")

print("MVP57_500_AGENT_RUNTIME_GROUP_VALIDATION_PASS")
