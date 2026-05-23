#!/usr/bin/env python3
"""Validate the MVP-58 1,000-agent runtime division pass."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp58_1000_agent_runtime_division.sql",
    ROOT / "netlify" / "functions" / "_shared" / "runtime_division_helpers.js",
    ROOT / "netlify" / "functions" / "list-runtime-division.js",
    ROOT / "netlify" / "functions" / "activate-runtime-division.js",
    ROOT / "netlify" / "functions" / "deactivate-runtime-division.js",
    ROOT / "netlify" / "functions" / "activate-division-subdivision.js",
    ROOT / "netlify" / "functions" / "deactivate-division-subdivision.js",
    ROOT / "netlify" / "functions" / "activate-division-lane.js",
    ROOT / "netlify" / "functions" / "deactivate-division-lane.js",
    ROOT / "netlify" / "functions" / "division-heartbeat.js",
    ROOT / "netlify" / "functions" / "create-division-readiness-note.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-division.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-division.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp58_1000_agent_runtime_division_report.md",
]

migration_required = [
    "runtime_division_subdivisions",
    "runtime_division_lanes",
    "runtime_division_agents",
    "runtime_division_activation_events",
    "division_heartbeat_events",
    "division_readiness_notes",
    "runtime_division_audit_events",
    "runtime_division_size",
    "max_activation_batch_size",
    "max_operation_chunk_size",
    "mvp58_division_agent_0001",
    "mvp58_division_agent_1000",
    "intake_subdivision",
    "reporting_subdivision",
    "intake_lane_001",
    "reporting_lane_010",
    "activate_all is blocked",
    "batch_size exceeds 1000",
    "chunk_size exceeds 100",
    "UNKNOWN_AGENT_BLOCKED",
    "NON_DIVISION_AGENT_BLOCKED",
    "DIVISION_HEARTBEAT",
    "DIVISION_READINESS_NOTE_CREATED",
    "full 47,979 activation is blocked",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_division_agents",
    "runtime_division_subdivisions",
    "runtime_division_lanes",
    "runtime_division_activation_events",
    "division_heartbeat_events",
    "division_readiness_notes",
    "runtime_division_audit_events",
    "runtime_division_activate_agents",
    "runtime_division_deactivate_agents",
    "runtime_division_record_heartbeat",
    "runtime_division_create_readiness_note",
    "activate_all",
    "batch_size exceeds 1000",
    "chunk_size exceeds 100",
    "UNKNOWN_AGENT_BLOCKED",
    "NON_DIVISION_AGENT_BLOCKED",
    "DIVISION_HEARTBEAT",
    "DIVISION_READINESS_NOTE_CREATED",
]

ui_required = [
    "Runtime Division",
    "MVP-58 1,000-Agent Runtime Division",
    "Runtime division size: 1,000",
    "Live runtime agents enabled: 0–1,000",
    "Activation beyond 1,000: blocked",
    "Full 47,979 activation: blocked",
    "Activate full 1,000-agent division",
    "Deactivate full division",
    "Activate one subdivision",
    "Deactivate one subdivision",
    "Activate one lane",
    "Deactivate one lane",
    "Activate individual agent",
    "Deactivate individual agent",
    "Send division heartbeat",
    "Send subdivision heartbeat",
    "Send lane heartbeat",
    "Create readiness note",
    "Division health",
    "Lane health",
    "Heartbeat count",
    "Readiness note count",
    "Audit timeline",
    "Kill switch",
    "Total registered agents: 47,979",
    "Backend functions or Supabase environment variables are not configured yet",
    "Open 1,000-Agent Runtime Division",
]

report_required = [
    "MVP58_1000_AGENT_RUNTIME_DIVISION_COMPLETE",
    "ONE_THOUSAND_APPROVED_AGENTS_CREATED",
    "TEN_SUBDIVISIONS_CREATED",
    "ONE_HUNDRED_AGENT_LANES_CREATED",
    "TEN_AGENTS_PER_LANE",
    "ONE_HUNDRED_AGENTS_PER_SUBDIVISION",
    "MAX_RUNTIME_SIZE_1000",
    "MAX_BATCH_SIZE_1000",
    "MAX_OPERATION_CHUNK_SIZE_100",
    "FULL_DIVISION_CHUNKING_ADDED",
    "FULL_47979_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENTS_BLOCKED",
    "NON_DIVISION_AGENTS_BLOCKED",
    "HEARTBEAT_FUNCTION_ADDED",
    "READINESS_NOTE_FUNCTION_ADDED",
    "LANE_ACTIVATION_ADDED",
    "SUBDIVISION_ACTIVATION_ADDED",
    "DIVISION_HEALTH_ROLLUP_ADDED",
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
    "/.netlify/functions/list-runtime-division",
    "/.netlify/functions/activate-runtime-division",
    "/.netlify/functions/deactivate-runtime-division",
    "/.netlify/functions/activate-division-subdivision",
    "/.netlify/functions/deactivate-division-subdivision",
    "/.netlify/functions/activate-division-lane",
    "/.netlify/functions/deactivate-division-lane",
    "/.netlify/functions/division-heartbeat",
    "/.netlify/functions/create-division-readiness-note",
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
  print("MVP58_1000_AGENT_RUNTIME_DIVISION_VALIDATION_FAIL")
  print(f"  - {message}")
  sys.exit(1)


def read(path: Path) -> str:
  return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
  if not condition:
    fail(message)


prereq = subprocess.run(
    ["python3", str(ROOT / "scripts" / "validate_mvp57_500_agent_runtime_group.py")],
    capture_output=True,
    text=True,
)
require(
    prereq.returncode == 0 and "MVP57_500_AGENT_RUNTIME_GROUP_VALIDATION_PASS" in prereq.stdout,
    "MVP-57 prerequisite validator did not pass.",
)

for path in required_files:
  require(path.exists(), f"Missing required file: {path.relative_to(ROOT)}")

migration_text = read(required_files[0])
for needle in migration_required:
  require(needle in migration_text, f"Migration missing required string: {needle}")

function_text = "\n".join(read(path) for path in required_files[1:11])
for needle in function_required:
  require(needle in function_text, f"Function layer missing required string: {needle}")

ui_text = read(required_files[11]) + "\n" + read(required_files[12]) + "\n" + read(required_files[13]) + "\n" + read(required_files[14])
for needle in ui_required:
  require(needle in ui_text, f"Runtime division UI missing required string: {needle}")

page_text = read(required_files[11])
require('<header class="demo-topbar collapsible-topbar" data-collapsible-menu>' in page_text, "Runtime division page missing collapsible menu header.")
require('data-action="toggle-menu"' in page_text, "Runtime division page missing toggle menu button.")
require('aria-expanded="false"' in page_text, "Runtime division page missing collapsed aria state.")
require('data-menu-panel' in page_text, "Runtime division page missing menu panel.")
require('hidden' in page_text, "Runtime division page missing hidden menu panel marker.")
require('<nav class="nav-links"' not in page_text, "Runtime division page still contains an always-visible nav row.")
require("Runtime Division" in page_text, "Runtime division breadcrumb/title missing.")
require("Demo Hub" in page_text, "Runtime division breadcrumb missing Demo Hub.")
require("Home" in page_text, "Runtime division breadcrumb missing Home.")

report_text = read(required_files[15])
for needle in report_required:
  require(needle in report_text, f"Report missing required marker: {needle}")

js_text = read(required_files[12])
for needle in browser_js_required:
  require(needle in js_text, f"Browser JS missing required endpoint: {needle}")
for needle in browser_js_forbidden:
  require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

require("activate_all" in function_text, "Server-side functions should explicitly block activate_all.")
require("batch_size exceeds 1000" in function_text or "> 1000" in function_text, "Server-side functions should explicitly block batch sizes above 1000.")
require("chunk_size exceeds 100" in function_text or "> 100" in function_text, "Server-side functions should explicitly block chunk sizes above 100.")
require("UNKNOWN_AGENT_BLOCKED" in function_text, "Server-side functions should block unknown agent IDs.")
require("NON_DIVISION_AGENT_BLOCKED" in function_text, "Server-side functions should block non-division agent IDs.")
require("DIVISION_HEARTBEAT" in function_text, "Heartbeat audit event missing.")
require("DIVISION_READINESS_NOTE_CREATED" in function_text, "Readiness note audit event missing.")

print("MVP58_1000_AGENT_RUNTIME_DIVISION_VALIDATION_PASS")
