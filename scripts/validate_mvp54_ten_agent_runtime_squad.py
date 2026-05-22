#!/usr/bin/env python3
"""Validate the MVP-54 ten-agent runtime squad pass."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp54_ten_agent_runtime_squad.sql",
    ROOT / "netlify" / "functions" / "_shared" / "runtime_squad_helpers.js",
    ROOT / "netlify" / "functions" / "list-runtime-squad.js",
    ROOT / "netlify" / "functions" / "activate-runtime-squad.js",
    ROOT / "netlify" / "functions" / "deactivate-runtime-squad.js",
    ROOT / "netlify" / "functions" / "agent-heartbeat.js",
    ROOT / "netlify" / "functions" / "create-readiness-note.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-squad.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-squad.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp54_ten_agent_runtime_squad_report.md",
]

migration_required = [
    "runtime_squad_agents",
    "agent_heartbeat_events",
    "agent_readiness_notes",
    "runtime_squad_audit_events",
    "runtime_squad_size",
    "max_activation_batch_size",
    "live_runtime_agents_enabled",
    "full_47979_activation_blocked",
    "mass_activation_blocked",
    "mvp54_runtime_squad_agent_001",
    "mvp54_runtime_squad_agent_010",
    "create heartbeat and readiness note only",
    "activate_all is blocked",
    "batch_size exceeds 10",
    "UNKNOWN_AGENT_BLOCKED",
    "SQUAD_ACTIVATION_BLOCKED",
    "SQUAD_DEACTIVATION_BLOCKED",
    "AGENT_HEARTBEAT",
    "READINESS_NOTE_CREATED",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_squad_agents",
    "runtime_squad_audit_events",
    "agent_heartbeat_events",
    "agent_readiness_notes",
    "runtime_squad_activate_agents",
    "runtime_squad_deactivate_agents",
    "runtime_squad_record_heartbeat",
    "runtime_squad_create_readiness_note",
    "activate_all",
    "batch_size",
    "batch_size exceeds 10",
    "UNKNOWN_AGENT_BLOCKED",
    "SQUAD_ACTIVATION_BLOCKED",
    "SQUAD_DEACTIVATION_BLOCKED",
    "AGENT_HEARTBEAT",
    "READINESS_NOTE_CREATED",
]

ui_required = [
    "10-Agent Runtime Squad",
    "MVP-54 Ten-Agent Runtime Squad",
    "Runtime squad size: 10",
    "Live runtime agents enabled: 0–10",
    "Mass activation beyond 10: blocked",
    "Full 47,979 activation: blocked",
    "Activate squad",
    "Deactivate squad",
    "Activate individual agent",
    "Deactivate individual agent",
    "Send heartbeat",
    "Create readiness note",
    "Audit Timeline",
    "Kill switch",
    "Total registered agents: 47,979",
    "Open 10-Agent Runtime Squad",
]

report_required = [
    "MVP54_TEN_AGENT_RUNTIME_SQUAD_COMPLETE",
    "TEN_APPROVED_AGENTS_CREATED",
    "MAX_BATCH_SIZE_10_ENFORCED",
    "MASS_ACTIVATION_BROKEN_OUT_BLOCKED",
    "FULL_47979_ACTIVATION_BLOCKED",
    "HEARTBEAT_TABLE_ADDED",
    "READINESS_NOTE_TABLE_ADDED",
    "AUDIT_EVENTS_TABLE_ADDED",
    "ACTIVATE_RUNTIME_SQUAD_ADDED",
    "DEACTIVATE_RUNTIME_SQUAD_ADDED",
    "AGENT_HEARTBEAT_ADDED",
    "CREATE_READINESS_NOTE_ADDED",
    "SERVICE_ROLE_SERVER_SIDE_ONLY",
    "NO_SERVICE_ROLE_IN_BROWSER",
    "NO_COMMAND_EXECUTION_ADDED",
    "NO_DEPLOY_EXECUTION_ADDED",
    "NO_ROLLBACK_EXECUTION_ADDED",
    "NO_ALERT_SENDING_ADDED",
    "NO_ARBITRARY_SQL_ENDPOINT_ADDED",
    "NO_ARBITRARY_COMMAND_ENDPOINT_ADDED",
]

browser_js_required = [
    "/.netlify/functions/list-runtime-squad",
    "/.netlify/functions/activate-runtime-squad",
    "/.netlify/functions/deactivate-runtime-squad",
    "/.netlify/functions/agent-heartbeat",
    "/.netlify/functions/create-readiness-note",
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
    print("MVP54_TEN_AGENT_RUNTIME_SQUAD_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


for path in required_files:
    require(path.exists(), f"Missing required file: {path.relative_to(ROOT)}")

migration_text = read(required_files[0])
for needle in migration_required:
    require(needle in migration_text, f"Migration missing required string: {needle}")

function_text = "\n".join(read(path) for path in required_files[1:7])
for needle in function_required:
    require(needle in function_text, f"Function layer missing required string: {needle}")

ui_text = read(required_files[7]) + "\n" + read(required_files[8]) + "\n" + read(required_files[9])
for needle in ui_required:
    require(needle in ui_text, f"Runtime squad UI missing required string: {needle}")

page_text = read(required_files[7])
require('<header class="demo-topbar collapsible-topbar" data-collapsible-menu>' in page_text, "Runtime squad page missing collapsible menu header.")
require('data-action="toggle-menu"' in page_text, "Runtime squad page missing toggle menu button.")
require('aria-expanded="false"' in page_text, "Runtime squad page missing collapsed aria state.")
require('data-menu-panel' in page_text, "Runtime squad page missing menu panel.")
require('hidden' in page_text, "Runtime squad page missing hidden menu panel marker.")
require("<nav class=\"nav-links\"" not in page_text, "Runtime squad page still contains an always-visible nav row.")
require("10-Agent Runtime Squad" in page_text, "Runtime squad breadcrumb/title missing.")
require("Demo Hub" in page_text, "Runtime squad breadcrumb missing Demo Hub.")
require("Runtime Squad" in page_text or "10-Agent Runtime Squad" in page_text, "Runtime squad breadcrumb missing current page label.")

report_text = read(required_files[10])
for needle in report_required:
    require(needle in report_text, f"Report missing required marker: {needle}")

js_text = read(required_files[8])
for needle in browser_js_required:
    require(needle in js_text, f"Browser JS missing required endpoint: {needle}")
for needle in browser_js_forbidden:
    require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

require("activate_all" in function_text, "Server-side functions should explicitly block activate_all.")
require("batch_size exceeds 10" in function_text or "> 10" in function_text, "Server-side functions should explicitly block batch sizes above 10.")
require("UNKNOWN_AGENT_BLOCKED" in function_text, "Server-side functions should block unknown agent IDs.")
require("SQUAD_ACTIVATION_BLOCKED" in function_text, "Server-side functions should block mass activation.")
require("SQUAD_DEACTIVATION_BLOCKED" in function_text, "Server-side functions should block mass deactivation.")
require("AGENT_HEARTBEAT" in function_text, "Heartbeat audit event missing.")
require("READINESS_NOTE_CREATED" in function_text, "Readiness note audit event missing.")

print("MVP54_TEN_AGENT_RUNTIME_SQUAD_VALIDATION_PASS")
