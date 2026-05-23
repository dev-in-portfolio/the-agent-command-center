#!/usr/bin/env python3
"""Validate the MVP-56 250-agent runtime company pass."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp56_250_agent_runtime_company.sql",
    ROOT / "netlify" / "functions" / "_shared" / "runtime_company_helpers.js",
    ROOT / "netlify" / "functions" / "list-runtime-company.js",
    ROOT / "netlify" / "functions" / "activate-runtime-company.js",
    ROOT / "netlify" / "functions" / "deactivate-runtime-company.js",
    ROOT / "netlify" / "functions" / "activate-company-lane.js",
    ROOT / "netlify" / "functions" / "deactivate-company-lane.js",
    ROOT / "netlify" / "functions" / "company-heartbeat.js",
    ROOT / "netlify" / "functions" / "create-company-readiness-note.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-company.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-company.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp56_250_agent_runtime_company_report.md",
]

migration_required = [
    "runtime_company_lanes",
    "runtime_company_agents",
    "runtime_company_activation_events",
    "company_heartbeat_events",
    "company_readiness_notes",
    "runtime_company_audit_events",
    "runtime_company_size",
    "max_activation_batch_size",
    "mvp56_company_agent_001",
    "mvp56_company_agent_250",
    "intake_lane_01",
    "command_center_lane_01",
    "activate_all is blocked",
    "batch_size exceeds 250",
    "COMPANY_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENT_BLOCKED",
    "COMPANY_HEARTBEAT",
    "COMPANY_READINESS_NOTE_CREATED",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_company_agents",
    "runtime_company_lanes",
    "runtime_company_activation_events",
    "company_heartbeat_events",
    "company_readiness_notes",
    "runtime_company_audit_events",
    "runtime_company_activate_agents",
    "runtime_company_deactivate_agents",
    "runtime_company_activate_lane",
    "runtime_company_deactivate_lane",
    "runtime_company_record_heartbeat",
    "runtime_company_create_readiness_note",
    "activate_all",
    "batch_size exceeds 250",
    "UNKNOWN_AGENT_BLOCKED",
    "COMPANY_ACTIVATION_BLOCKED",
    "COMPANY_DEACTIVATION_BLOCKED",
    "COMPANY_HEARTBEAT",
    "COMPANY_READINESS_NOTE_CREATED",
]

ui_required = [
    "250-Agent Runtime Company",
    "MVP-56 250-Agent Runtime Company",
    "Runtime company size: 250",
    "Live runtime agents enabled: 0–250",
    "Activation beyond 250: blocked",
    "Full 47,979 activation: blocked",
    "Activate full 250-agent company",
    "Deactivate full company",
    "Activate one lane",
    "Deactivate one lane",
    "Activate individual agent",
    "Deactivate individual agent",
    "Send company heartbeat",
    "Send lane heartbeat",
    "Create readiness note",
    "Company health",
    "Lane health",
    "Heartbeat count",
    "Readiness note count",
    "Audit Timeline",
    "Kill switch",
    "Total registered agents: 47,979",
    "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.",
    "Open 250-Agent Runtime Company",
]

report_required = [
    "MVP56_250_AGENT_RUNTIME_COMPANY_COMPLETE",
    "TWO_HUNDRED_FIFTY_APPROVED_AGENTS_CREATED",
    "TWENTY_FIVE_AGENT_LANES_CREATED",
    "TEN_AGENTS_PER_LANE",
    "MAX_BATCH_SIZE_250",
    "FULL_47979_ACTIVATION_BLOCKED",
    "UNKNOWN_AGENTS_BLOCKED",
    "NON_COMPANY_AGENTS_BLOCKED",
    "HEARTBEAT_FUNCTION_ADDED",
    "READINESS_NOTE_FUNCTION_ADDED",
    "LANE_ACTIVATION_ADDED",
    "COMPANY_HEALTH_ROLLUP_ADDED",
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
    "/.netlify/functions/list-runtime-company",
    "/.netlify/functions/activate-runtime-company",
    "/.netlify/functions/deactivate-runtime-company",
    "/.netlify/functions/activate-company-lane",
    "/.netlify/functions/deactivate-company-lane",
    "/.netlify/functions/company-heartbeat",
    "/.netlify/functions/create-company-readiness-note",
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
    print("MVP56_250_AGENT_RUNTIME_COMPANY_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


prereq = subprocess.run(
    ["python3", str(ROOT / "scripts" / "validate_mvp55_100_agent_runtime_battalion.py")],
    capture_output=True,
    text=True,
)
require(
    prereq.returncode == 0 and "MVP55_100_AGENT_RUNTIME_BATTALION_VALIDATION_PASS" in prereq.stdout,
    "MVP-55 prerequisite validator did not pass.",
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
    require(needle in ui_text, f"Runtime company UI missing required string: {needle}")

page_text = read(required_files[9])
require('<header class="demo-topbar collapsible-topbar" data-collapsible-menu>' in page_text, "Runtime company page missing collapsible menu header.")
require('data-action="toggle-menu"' in page_text, "Runtime company page missing toggle menu button.")
require('aria-expanded="false"' in page_text, "Runtime company page missing collapsed aria state.")
require('data-menu-panel' in page_text, "Runtime company page missing menu panel.")
require('hidden' in page_text, "Runtime company page missing hidden menu panel marker.")
require("<nav class=\"nav-links\"" not in page_text, "Runtime company page still contains an always-visible nav row.")
require("Runtime Company" in page_text, "Runtime company breadcrumb/title missing.")
require("Demo Hub" in page_text, "Runtime company breadcrumb missing Demo Hub.")
require("Home" in page_text, "Runtime company breadcrumb missing Home.")

report_text = read(required_files[13])
for needle in report_required:
    require(needle in report_text, f"Report missing required marker: {needle}")

js_text = read(required_files[10])
for needle in browser_js_required:
    require(needle in js_text, f"Browser JS missing required endpoint: {needle}")
for needle in browser_js_forbidden:
    require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

require("activate_all" in function_text, "Server-side functions should explicitly block activate_all.")
require("batch_size exceeds 250" in function_text or "> 250" in function_text, "Server-side functions should explicitly block batch sizes above 250.")
require("UNKNOWN_AGENT_BLOCKED" in function_text, "Server-side functions should block unknown agent IDs.")
require("COMPANY_ACTIVATION_BLOCKED" in function_text, "Server-side functions should block company activation overreach.")
require("COMPANY_DEACTIVATION_BLOCKED" in function_text, "Server-side functions should block company deactivation overreach.")
require("COMPANY_HEARTBEAT" in function_text, "Heartbeat audit event missing.")
require("COMPANY_READINESS_NOTE_CREATED" in function_text, "Readiness note audit event missing.")

print("MVP56_250_AGENT_RUNTIME_COMPANY_VALIDATION_PASS")
