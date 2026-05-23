#!/usr/bin/env python3
"""Validate the MVP-53 runtime agent activation controller hardening pass."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp53_runtime_agent_activation_controller.sql",
    ROOT / "netlify" / "functions" / "activate-agent.js",
    ROOT / "netlify" / "functions" / "deactivate-agent.js",
    ROOT / "netlify" / "functions" / "list-runtime-agents.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-agent-control.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-agent-control.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp53_runtime_agent_activation_controller_report.md",
]

migration_required = [
    "runtime_agents",
    "agent_activation_events",
    "mvp53_supervised_test_agent_001",
    "Supervised Test Agent 001",
    "live_runtime_agents_enabled",
    "max_activation_batch_size",
    "mass_activation_blocked",
    "kill_switch_visible",
    "execution_permissions",
    "external_api_permissions",
    "database_write_permissions",
    "audit_event_only",
    "supervised_single_agent_test",
    "inactive",
    "runtime_kernel_config",
    "runtime_kernel_touch_updated_at",
    "create table if not exists runtime_kernel_config",
    "create or replace function runtime_kernel_touch_updated_at",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_agents",
    "agent_activation_events",
    "live_runtime_agents_enabled",
    "mass_activation_blocked",
    "max_activation_batch_size",
    "mvp53_supervised_test_agent_001",
    "AGENT_ACTIVATED",
    "AGENT_DEACTIVATED",
    "ACTIVATION_BLOCKED",
    "DEACTIVATION_BLOCKED",
    "Runtime agent controller backend is not configured.",
]

ui_required = [
    "Runtime Agent Control",
    "MVP-53 Runtime Agent Activation Controller",
    "Supervised single-agent test",
    "Live runtime agents enabled: 0",
    "Total registered agents: 47,979",
    "Mass activation: blocked",
    "Activation mode: supervised single-agent test",
    "Kill switch visible",
    "Audit Timeline",
    "Current Agent Status",
    "Activate supervised test agent",
    "Deactivate supervised test agent",
    "No activate-all route",
    "batch size = 1",
    "mvp53_supervised_test_agent_001",
    "Supervised Test Agent 001",
    "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.",
    "Home",
    "Demo Hub",
]

report_required = [
    "MVP53_RUNTIME_AGENT_ACTIVATION_CONTROLLER_COMPLETE",
    "REAL_RUNTIME_AGENT_CONTROL_PAGE_ADDED",
    "REAL_BACKEND_FUNCTIONS_ADDED",
    "SUPABASE_RUNTIME_AGENTS_TABLE_ADDED",
    "SUPABASE_AGENT_ACTIVATION_EVENTS_TABLE_ADDED",
    "SUPERVISED_TEST_AGENT_ADDED",
    "ONE_AGENT_ONLY_ENFORCED",
    "MAX_ACTIVATION_BATCH_SIZE_ONE",
    "MASS_ACTIVATION_BLOCKED",
    "ACTIVATE_ALL_ROUTE_NOT_ADDED",
    "KILL_SWITCH_VISIBLE",
    "ACTIVATION_AUDIT_EVENTS_ADDED",
    "DEACTIVATION_AUDIT_EVENTS_ADDED",
    "SERVICE_ROLE_SERVER_SIDE_ONLY",
    "NO_SERVICE_ROLE_IN_BROWSER",
    "NO_COMMAND_EXECUTION_ADDED",
    "NO_DEPLOY_EXECUTION_ADDED",
    "NO_ROLLBACK_EXECUTION_ADDED",
    "NO_ALERT_SENDING_ADDED",
    "NO_ARBITRARY_SQL_ENDPOINT_ADDED",
    "NO_ARBITRARY_COMMAND_ENDPOINT_ADDED",
    "LIVE_RUNTIME_AGENTS_LIMITED_TO_SUPERVISED_TEST_AGENT",
    "TOTAL_REGISTERED_AGENTS_REMAINS_47979",
]

js_required = [
    "/.netlify/functions/list-runtime-agents",
    "/.netlify/functions/activate-agent",
    "/.netlify/functions/deactivate-agent",
]

forbidden_browser = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "child_process",
    "exec(",
    "spawn(",
    "eval(",
    "new Function",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "indexedDB",
    "WebSocket",
]

forbidden_runtime_control = [
    "activateAll",
    "batch_size: 47979",
    "execution_enabled true",
    "command_execution_enabled true",
    "deploy_execution_enabled true",
    "rollback_execution_enabled true",
    "alert_sending_enabled true",
    "execution_enabled false",
    "command_execution enabled",
    "deploy execution enabled",
    "rollback execution enabled",
    "alert sending enabled",
]


def fail(message: str) -> None:
    print("MVP53_RUNTIME_AGENT_ACTIVATION_CONTROLLER_VALIDATION_FAIL")
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

function_text = "\n".join(read(path) for path in required_files[1:4])
for needle in function_required:
    require(needle in function_text, f"Function layer missing required string: {needle}")

report_text = read(required_files[8])
for needle in report_required:
    require(needle in report_text, f"Report missing required marker: {needle}")

page_text = read(required_files[4])
page_text_forbidden_scan = page_text.replace("No activate-all route", "")

page_required = [
    '<header class="demo-topbar collapsible-topbar" data-collapsible-menu>',
    'data-action="toggle-menu"',
    'aria-expanded="false"',
    'data-menu-panel',
    'hidden',
    'Runtime Agent Control',
    'Home',
    'Demo Hub',
    'Runtime Kernel',
    'Runtime Foundation',
    'Simulator',
    'Agent Registry',
    'Safety Boundaries',
    'Legal / Copyright',
]
for needle in page_required:
    require(needle in page_text, f"Runtime Agent Control page missing required string: {needle}")

require("<nav class=\"nav-links\"" not in page_text, "Runtime Agent Control page still contains an always-visible nav row.")

breadcrumb_match = re.search(r'<nav class="breadcrumb"[^>]*>(.*?)</nav>', page_text, re.S)
require(breadcrumb_match is not None, "Runtime Agent Control page missing breadcrumb block.")
breadcrumb_block = breadcrumb_match.group(1)
require("Runtime Agent Control" in breadcrumb_block, "Breadcrumb does not include Runtime Agent Control.")
require("Demo Hub" in breadcrumb_block, "Breadcrumb does not include Demo Hub.")
require(breadcrumb_block.rfind("Runtime Agent Control") > breadcrumb_block.rfind("Demo Hub"), "Breadcrumb does not end with Runtime Agent Control.")

js_text = read(required_files[5])
for needle in js_required:
    require(needle in js_text, f"Browser JS missing required fetch target: {needle}")
for needle in forbidden_browser:
    require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

runtime_control_scan = "\n".join([page_text_forbidden_scan, js_text, function_text])
for needle in [
    "activate-all",
    "activateAll",
    "batch_size: 47979",
    "execution_enabled true",
    "command_execution_enabled true",
    "deploy_execution_enabled true",
    "rollback_execution_enabled true",
    "alert_sending_enabled true",
]:
    require(needle not in runtime_control_scan, f"Forbidden runtime control string present: {needle}")

print("MVP53_RUNTIME_AGENT_ACTIVATION_CONTROLLER_VALIDATION_PASS")
