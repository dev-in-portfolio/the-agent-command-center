#!/usr/bin/env python3
"""Validate the MVP-55 100-agent runtime battalion pass."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp55_100_agent_runtime_battalion.sql",
    ROOT / "netlify" / "functions" / "_shared" / "runtime_battalion_helpers.js",
    ROOT / "netlify" / "functions" / "list-runtime-battalion.js",
    ROOT / "netlify" / "functions" / "activate-runtime-battalion.js",
    ROOT / "netlify" / "functions" / "deactivate-runtime-battalion.js",
    ROOT / "netlify" / "functions" / "activate-agent-lane.js",
    ROOT / "netlify" / "functions" / "deactivate-agent-lane.js",
    ROOT / "netlify" / "functions" / "battalion-heartbeat.js",
    ROOT / "netlify" / "functions" / "create-battalion-readiness-note.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-battalion.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-battalion.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp55_100_agent_runtime_battalion_report.md",
]

migration_required = [
    "runtime_battalion_lanes",
    "runtime_battalion_agents",
    "runtime_battalion_activation_events",
    "battalion_heartbeat_events",
    "battalion_readiness_notes",
    "runtime_battalion_audit_events",
    "runtime_battalion_size",
    "max_activation_batch_size",
    "mvp55_battalion_agent_001",
    "mvp55_battalion_agent_100",
    "intake_lane",
    "reporting_lane",
    "activate_all is blocked",
    "batch_size exceeds 100",
    "BATTALION_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENT_BLOCKED",
    "BATTALION_HEARTBEAT",
    "BATTALION_READINESS_NOTE_CREATED",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_battalion_agents",
    "runtime_battalion_lanes",
    "runtime_battalion_activation_events",
    "battalion_heartbeat_events",
    "battalion_readiness_notes",
    "runtime_battalion_audit_events",
    "runtime_battalion_activate_agents",
    "runtime_battalion_deactivate_agents",
    "runtime_battalion_activate_lane",
    "runtime_battalion_deactivate_lane",
    "runtime_battalion_record_heartbeat",
    "runtime_battalion_create_readiness_note",
    "activate_all",
    "batch_size exceeds 100",
    "UNKNOWN_AGENT_BLOCKED",
    "BATTALION_ACTIVATION_BLOCKED",
    "BATTALION_DEACTIVATION_BLOCKED",
    "BATTALION_HEARTBEAT",
    "BATTALION_READINESS_NOTE_CREATED",
]

ui_required = [
    "100-Agent Runtime Battalion",
    "MVP-55 100-Agent Runtime Battalion",
    "Runtime battalion size: 100",
    "Live runtime agents enabled: 0–100",
    "Activation beyond 100: blocked",
    "Full 47,979 activation: blocked",
    "Activate full 100-agent battalion",
    "Deactivate full battalion",
    "Activate one lane",
    "Deactivate one lane",
    "Activate individual agent",
    "Deactivate individual agent",
    "Send battalion heartbeat",
    "Create readiness note",
    "Lane Roster",
    "Lane health",
    "Heartbeat count",
    "Readiness note count",
    "Audit Timeline",
    "Kill switch",
    "Total registered agents: 47,979",
    "Open 100-Agent Runtime Battalion",
]

report_required = [
    "MVP55_100_AGENT_RUNTIME_BATTALION_COMPLETE",
    "ONE_HUNDRED_APPROVED_AGENTS_CREATED",
    "TEN_AGENT_LANES_CREATED",
    "MAX_BATCH_SIZE_100",
    "FULL_47979_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENTS_BLOCKED",
    "NON_BATTALION_AGENTS_BLOCKED",
    "HEARTBEAT_FUNCTION_ADDED",
    "READINESS_NOTE_FUNCTION_ADDED",
    "LANE_ACTIVATION_ADDED",
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
    "/.netlify/functions/list-runtime-battalion",
    "/.netlify/functions/activate-runtime-battalion",
    "/.netlify/functions/deactivate-runtime-battalion",
    "/.netlify/functions/activate-agent-lane",
    "/.netlify/functions/deactivate-agent-lane",
    "/.netlify/functions/battalion-heartbeat",
    "/.netlify/functions/create-battalion-readiness-note",
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
    print("MVP55_100_AGENT_RUNTIME_BATTALION_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


prereq = subprocess.run(
    ["python3", str(ROOT / "scripts" / "validate_mvp54_ten_agent_runtime_squad.py")],
    capture_output=True,
    text=True,
)
require(
    prereq.returncode == 0 and "MVP54_TEN_AGENT_RUNTIME_SQUAD_VALIDATION_PASS" in prereq.stdout,
    "MVP-54 prerequisite validator did not pass.",
)

for path in required_files:
    require(path.exists(), f"Missing required file: {path.relative_to(ROOT)}")

migration_text = read(required_files[0])
for needle in migration_required:
    require(needle in migration_text, f"Migration missing required string: {needle}")

function_text = "\n".join(read(path) for path in required_files[1:9])
for needle in function_required:
    require(needle in function_text, f"Function layer missing required string: {needle}")

ui_text = read(required_files[9]) + "\n" + read(required_files[10]) + "\n" + read(required_files[11]) + "\n" + read(required_files[12])
for needle in ui_required:
    require(needle in ui_text, f"Runtime battalion UI missing required string: {needle}")

page_text = read(required_files[9])
require('<header class="demo-topbar collapsible-topbar" data-collapsible-menu>' in page_text, "Runtime battalion page missing collapsible menu header.")
require('data-action="toggle-menu"' in page_text, "Runtime battalion page missing toggle menu button.")
require('aria-expanded="false"' in page_text, "Runtime battalion page missing collapsed aria state.")
require('data-menu-panel' in page_text, "Runtime battalion page missing menu panel.")
require('hidden' in page_text, "Runtime battalion page missing hidden menu panel marker.")
require("<nav class=\"nav-links\"" not in page_text, "Runtime battalion page still contains an always-visible nav row.")
require("100-Agent Runtime Battalion" in page_text, "Runtime battalion breadcrumb/title missing.")
require("Demo Hub" in page_text, "Runtime battalion breadcrumb missing Demo Hub.")
require("Runtime Battalion" in page_text or "100-Agent Runtime Battalion" in page_text, "Runtime battalion breadcrumb missing current page label.")

report_text = read(required_files[13])
for needle in report_required:
    require(needle in report_text, f"Report missing required marker: {needle}")

js_text = read(required_files[10])
for needle in browser_js_required:
    require(needle in js_text, f"Browser JS missing required endpoint: {needle}")
for needle in browser_js_forbidden:
    require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

require("activate_all" in function_text, "Server-side functions should explicitly block activate_all.")
require("batch_size exceeds 100" in function_text or "> 100" in function_text, "Server-side functions should explicitly block batch sizes above 100.")
require("UNKNOWN_AGENT_BLOCKED" in function_text, "Server-side functions should block unknown agent IDs.")
require("BATTALION_ACTIVATION_BLOCKED" in function_text, "Server-side functions should block battalion activation overreach.")
require("BATTALION_DEACTIVATION_BLOCKED" in function_text, "Server-side functions should block battalion deactivation overreach.")
require("BATTALION_HEARTBEAT" in function_text, "Heartbeat audit event missing.")
require("BATTALION_READINESS_NOTE_CREATED" in function_text, "Readiness note audit event missing.")

print("MVP55_100_AGENT_RUNTIME_BATTALION_VALIDATION_PASS")
