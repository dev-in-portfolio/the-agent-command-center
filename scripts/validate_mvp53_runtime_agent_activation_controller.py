#!/usr/bin/env python3
"""Validate the MVP-53 runtime agent activation controller pass."""

from pathlib import Path
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
]

ui_required = [
    "Runtime Agent Control",
    "MVP-53 Runtime Agent Activation Controller",
    "Supervised single-agent test",
    "Live runtime agents enabled: 0",
    "Total registered agents: 47,979",
    "Mass activation: blocked",
    "Activation mode: supervised single-agent test",
    "Kill switch",
    "Audit Timeline",
    "Current Agent Status",
    "Activate supervised test agent",
    "Deactivate supervised test agent",
    "No activate-all route",
    "batch size = 1",
    "mvp53_supervised_test_agent_001",
    "Supervised Test Agent 001",
    "Backend functions or Supabase environment variables are not configured yet",
]

js_required = [
    "/.netlify/functions/list-runtime-agents",
    "/.netlify/functions/activate-agent",
    "/.netlify/functions/deactivate-agent",
]

forbidden = [
    "/activate-all",
    "activateAll",
    "batch size > 1",
    "command execution enabled",
    "deploy execution enabled",
    "rollback execution enabled",
    "alert sending enabled",
    "SUPABASE_SERVICE_ROLE_KEY",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "indexedDB",
    "WebSocket",
    "eval(",
    "new Function",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def fail(message: str) -> None:
    print("MVP53_RUNTIME_AGENT_ACTIVATION_CONTROLLER_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


for path in required_files:
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")

migration_text = read(required_files[0])
for needle in migration_required:
    if needle not in migration_text:
        fail(f"Migration missing required string: {needle}")

function_text = migration_text + "\n" + "\n".join(read(path) for path in required_files[1:4])
for needle in function_required:
    if needle not in function_text:
        fail(f"Function layer missing required string: {needle}")

ui_text = read(required_files[4]) + "\n" + read(required_files[5]) + "\n" + read(required_files[6]) + "\n" + read(required_files[7])
for needle in ui_required:
    if needle not in ui_text:
        fail(f"UI missing required string: {needle}")

for needle in js_required:
    if needle not in read(required_files[5]):
        fail(f"Browser JS missing required fetch target: {needle}")

for needle in forbidden:
    if needle in read(required_files[5]):
        fail(f"Forbidden browser JS string present: {needle}")

print("MVP53_RUNTIME_AGENT_ACTIVATION_CONTROLLER_VALIDATION_PASS")
